import { NextResponse, type NextRequest } from "next/server";
import type { SupabaseClient } from "@supabase/supabase-js";
import { timingSafeEqualStrings } from "@/lib/dispatch";
import { getSupabaseServiceClient } from "@/lib/supabase-service";
import {
  decideOutboxAction,
  resolveWorkflowRef,
  shouldDeadLetterAfterDispatchFailure,
} from "@/lib/dispatch-outbox-worker";

/**
 * Story 1.10 (AD-18): pg_cron이 매 1분 `x-cron-secret` 헤더로 깨우는 server-only outbox worker.
 * `queued`를 claim해 GitHub workflow_dispatch를 호출하고(-> `accepted`), lease 만료 + receipt
 * 미도달이 시도 상한을 넘기면 `dead_letter`로 닫고 GitHub Issue를 만든다(AD-10). `queued`에서
 * dispatch 호출 자체가 반복 실패하는 행도 같은 attempts 카운터로 상한을 넘기면 `dead_letter`다
 * (무한 재시도 금지 -- 재시도/dead-letter 판단 로직 자체는 `lib/dispatch-outbox-worker.ts`의 순수
 * 함수로 추출해 단위 테스트한다). 매 tick 끝에 `reconcile_dispatch_outbox`로 `started` 행을 종결시킨다.
 *
 * GITHUB_DISPATCH_TOKEN 필요 권한: 이 워커는 이 토큰 하나로 workflow_dispatch(Actions: Read/Write)와
 * dead_letter Issue 생성(Issues: Read/Write)을 모두 호출한다 -- fine-grained PAT라면 두 권한을 모두
 * 부여해야 하며, 하나라도 빠지면 해당 호출만 조용히 실패하고 로그에만 남는다(아래 각 함수 참고).
 */
export const dynamic = "force-dynamic";

const WORKER_LEASE_SECONDS = 120;
const MAX_CLAIM = 20;
const WORKFLOW_FILE = "scheduled-batch.yml";
const WORKFLOW_REF = resolveWorkflowRef(process.env.GITHUB_DISPATCH_REF);

interface ClaimedOutboxRow {
  outbox_id: string;
  dispatch_request_id: string;
  status: "queued" | "accepted" | "started";
  lease_token: string;
  run_id: string | null;
  github_run_id: number | null;
  attempts: number;
  logical_run_key: string;
  idempotency_key: string;
}

export async function POST(request: NextRequest) {
  const expected = process.env.CRON_CALLBACK_SECRET;
  const provided = request.headers.get("x-cron-secret");
  if (!expected || !timingSafeEqualStrings(expected, provided)) {
    return NextResponse.json({ error: "UNAUTHORIZED" }, { status: 401 });
  }

  const supabase = getSupabaseServiceClient();

  const { data: claimed, error: claimError } = await supabase.rpc("claim_dispatch_outbox", {
    p_worker_lease_seconds: WORKER_LEASE_SECONDS,
    p_limit: MAX_CLAIM,
  });

  if (claimError) {
    return NextResponse.json({ error: "CLAIM_FAILED", message: claimError.message }, { status: 500 });
  }

  const rows = (claimed ?? []) as ClaimedOutboxRow[];
  const results: Array<Record<string, unknown>> = [];
  for (const row of rows) {
    results.push(await processRow(supabase, row));
  }

  const { data: reconciled, error: reconcileError } = await supabase.rpc("reconcile_dispatch_outbox");
  if (reconcileError) {
    console.error(`reconcile_dispatch_outbox failed message=${reconcileError.message}`);
  }

  return NextResponse.json({
    claimed: rows.length,
    results,
    reconciled: reconcileError ? null : reconciled,
  });
}

async function processRow(supabase: SupabaseClient, row: ClaimedOutboxRow): Promise<Record<string, unknown>> {
  const decision = decideOutboxAction(row);

  if (decision.action === "dead_letter") {
    await deadLetter(supabase, row, decision.reasonCode);
    return { outbox_id: row.outbox_id, result: "dead_letter", reason: decision.reasonCode };
  }

  if (decision.action === "dispatch") {
    const dispatchedAtMs = Date.now();
    const dispatched = await callGithubWorkflowDispatch(row);
    if (!dispatched.ok) {
      if (shouldDeadLetterAfterDispatchFailure(row.attempts)) {
        await deadLetter(supabase, row, "GITHUB_DISPATCH_FAILED");
        return { outbox_id: row.outbox_id, result: "dead_letter", reason: dispatched.message };
      }
      return { outbox_id: row.outbox_id, result: "dispatch_failed_will_retry", reason: dispatched.message };
    }

    // best-effort 상관관계: workflow_dispatch REST 호출은 204 No Content라 run id를 주지 않는다.
    // 방금 만든 run만 후보로 남을 때만(동시 dispatch가 없을 때만) github_run_id를 채운다 -- 모호하면
    // null로 남겨 대시보드/이슈에서 오배치보다 "알 수 없음"을 택한다.
    const githubRunId = await findGithubRunId(dispatchedAtMs);

    const { error } = await supabase.rpc("advance_dispatch_outbox", {
      p_outbox_id: row.outbox_id,
      p_status: "accepted",
      p_lease_token: row.lease_token,
      p_github_run_id: githubRunId,
    });
    if (error) {
      // GitHub 호출은 이미 성공했으므로 이 실패를 방치하면 행이 queued로 남아 다음 claim에서
      // 중복 dispatch를 유발한다 -- 로그에 남겨 운영자가 outbox_id로 직접 추적할 수 있게 한다.
      console.error(`advance_to_accepted failed outbox_id=${row.outbox_id} message=${error.message}`);
      return { outbox_id: row.outbox_id, result: "advance_failed", message: error.message };
    }
    return { outbox_id: row.outbox_id, result: "accepted", github_run_id: githubRunId };
  }

  if (decision.action === "await_receipt") {
    // GitHub는 dispatch를 수락했지만 workflow 첫 단계 receipt가 아직 없다(lease 만료로 재claim됨).
    // 재발송하지 않고 receipt 폴링만 재시도한다(AD-18).
    return { outbox_id: row.outbox_id, result: "awaiting_receipt" };
  }

  return { outbox_id: row.outbox_id, result: "noop", status: row.status };
}

async function deadLetter(supabase: SupabaseClient, row: ClaimedOutboxRow, reasonCode: string): Promise<void> {
  const { error } = await supabase.rpc("advance_dispatch_outbox", {
    p_outbox_id: row.outbox_id,
    p_status: "dead_letter",
    p_lease_token: row.lease_token,
  });
  if (error) {
    console.error(`dispatch_outbox dead_letter transition failed outbox_id=${row.outbox_id} message=${error.message}`);
    return;
  }
  await createDeadLetterIssue(row, reasonCode);
}

/**
 * AD-10 알림 계약: dead_letter는 조용히 묻히지 않고 GitHub Issue를 만든다. 실패는 로그만 남긴다
 * (secret 제외) -- GITHUB_DISPATCH_TOKEN에 Issues:Write 권한이 없으면 이 호출만 조용히 실패하므로,
 * 토큰 발급 시 Actions:Write와 Issues:Write를 함께 부여했는지 반드시 확인한다(모듈 상단 주석 참고).
 */
async function createDeadLetterIssue(row: ClaimedOutboxRow, reasonCode: string): Promise<void> {
  const token = process.env.GITHUB_DISPATCH_TOKEN;
  const owner = process.env.GITHUB_REPO_OWNER;
  const repo = process.env.GITHUB_REPO_NAME;
  if (!token || !owner || !repo) {
    console.error("dispatch dead_letter issue skipped: missing GitHub configuration");
    return;
  }

  try {
    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/issues`, {
      method: "POST",
      headers: {
        authorization: `Bearer ${token}`,
        accept: "application/vnd.github+json",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        title: `[dispatch] outbox dead_letter: ${row.logical_run_key}`,
        body: [
          `dispatch_request_id: ${row.dispatch_request_id}`,
          `outbox_id: ${row.outbox_id}`,
          `logical_run_key: ${row.logical_run_key}`,
          `reason: ${reasonCode}`,
          "",
          "필요 조치: GitHub Actions 실행 이력을 대조하고 수동으로 재개하세요(AD-10).",
        ].join("\n"),
        labels: ["dispatch-dead-letter"],
      }),
    });
    if (!response.ok) {
      console.error(`dispatch dead_letter issue creation failed status=${response.status}`);
    }
  } catch (error) {
    console.error(`dispatch dead_letter issue creation threw: ${error instanceof Error ? error.message : "unknown error"}`);
  }
}

async function callGithubWorkflowDispatch(row: ClaimedOutboxRow): Promise<{ ok: boolean; message?: string }> {
  const token = process.env.GITHUB_DISPATCH_TOKEN;
  const owner = process.env.GITHUB_REPO_OWNER;
  const repo = process.env.GITHUB_REPO_NAME;
  if (!token || !owner || !repo) {
    return { ok: false, message: "MISSING_GITHUB_CONFIGURATION" };
  }

  const batchKind = row.logical_run_key.split(":")[0];

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
      {
        method: "POST",
        headers: {
          authorization: `Bearer ${token}`,
          accept: "application/vnd.github+json",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          ref: WORKFLOW_REF,
          inputs: {
            batch_kind: batchKind,
            dispatch_request_id: row.dispatch_request_id,
          },
        }),
      }
    );
    if (!response.ok) {
      return { ok: false, message: `GITHUB_HTTP_${response.status}` };
    }
    return { ok: true };
  } catch (error) {
    return { ok: false, message: error instanceof Error ? error.message : "GITHUB_REQUEST_ERROR" };
  }
}

/**
 * `workflow_dispatch` REST 호출은 204 No Content라 run id를 돌려주지 않는다. dispatch 직후 실행
 * 목록을 한 번 조회해, `dispatchedAtMs` 이후 생성된 후보가 정확히 하나뿐일 때만 그 id를 채택한다
 * (동시에 여러 workflow_dispatch가 겹치면 후보가 둘 이상이 되어 모호해지므로 null을 반환한다 --
 * 틀린 상관관계보다 "알 수 없음"이 낫다). 실패해도 dispatch 자체의 성공/실패에는 영향을 주지 않는다.
 */
async function findGithubRunId(dispatchedAtMs: number): Promise<number | null> {
  const token = process.env.GITHUB_DISPATCH_TOKEN;
  const owner = process.env.GITHUB_REPO_OWNER;
  const repo = process.env.GITHUB_REPO_NAME;
  if (!token || !owner || !repo) return null;

  try {
    const response = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${WORKFLOW_FILE}/runs?event=workflow_dispatch&per_page=5`,
      {
        headers: {
          authorization: `Bearer ${token}`,
          accept: "application/vnd.github+json",
        },
      }
    );
    if (!response.ok) return null;

    const body = (await response.json()) as { workflow_runs?: Array<{ id: number; created_at: string }> };
    const runs = body.workflow_runs ?? [];
    // 약간의 시계 오차를 허용해, dispatch 직전 5초부터 생성된 실행만 후보로 삼는다.
    const candidates = runs.filter((run) => new Date(run.created_at).getTime() >= dispatchedAtMs - 5_000);
    return candidates.length === 1 ? candidates[0].id : null;
  } catch {
    return null;
  }
}
