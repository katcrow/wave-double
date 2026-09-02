import { NextResponse, type NextRequest } from "next/server";
import type { SupabaseClient } from "@supabase/supabase-js";
import { timingSafeEqualStrings } from "@/lib/dispatch";
import { getSupabaseServiceClient } from "@/lib/supabase-service";

/**
 * Story 1.10 (AD-18): pg_cron이 매 1분 `x-cron-secret` 헤더로 깨우는 server-only outbox worker.
 * `queued`를 claim해 GitHub workflow_dispatch를 호출하고(-> `accepted`), lease 만료 + receipt
 * 미도달이 시도 상한을 넘기면 `dead_letter`로 닫고 GitHub Issue를 만든다(AD-10). `queued`에서
 * dispatch 호출 자체가 반복 실패하는 행도 같은 attempts 카운터로 상한을 넘기면 `dead_letter`다
 * (무한 재시도 금지). 매 tick 끝에 `reconcile_dispatch_outbox`로 `started` 행을 종결시킨다.
 */
export const dynamic = "force-dynamic";

const MAX_ATTEMPTS = 5;
const WORKER_LEASE_SECONDS = 120;
const MAX_CLAIM = 20;
const WORKFLOW_FILE = "scheduled-batch.yml";
const WORKFLOW_REF = "main";

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
  if (row.attempts > MAX_ATTEMPTS) {
    await deadLetter(supabase, row, "ATTEMPTS_EXHAUSTED");
    return { outbox_id: row.outbox_id, result: "dead_letter", reason: "ATTEMPTS_EXHAUSTED" };
  }

  if (row.status === "queued") {
    const dispatched = await callGithubWorkflowDispatch(row);
    if (!dispatched.ok) {
      if (row.attempts >= MAX_ATTEMPTS) {
        await deadLetter(supabase, row, "GITHUB_DISPATCH_FAILED");
        return { outbox_id: row.outbox_id, result: "dead_letter", reason: dispatched.message };
      }
      return { outbox_id: row.outbox_id, result: "dispatch_failed_will_retry", reason: dispatched.message };
    }

    const { error } = await supabase.rpc("advance_dispatch_outbox", {
      p_outbox_id: row.outbox_id,
      p_status: "accepted",
      p_lease_token: row.lease_token,
    });
    if (error) return { outbox_id: row.outbox_id, result: "advance_failed", message: error.message };
    return { outbox_id: row.outbox_id, result: "accepted" };
  }

  if (row.status === "accepted") {
    // GitHub는 dispatch를 수락했지만 workflow 첫 단계 receipt가 아직 없다(lease 만료로 재claim됨).
    // 재발송하지 않고 receipt 폴링만 재시도한다(AD-18).
    if (row.attempts >= MAX_ATTEMPTS) {
      await deadLetter(supabase, row, "RECEIPT_TIMEOUT");
      return { outbox_id: row.outbox_id, result: "dead_letter", reason: "RECEIPT_TIMEOUT" };
    }
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

/** AD-10 알림 계약: dead_letter는 조용히 묻히지 않고 GitHub Issue를 만든다. 실패는 로그만 남긴다(secret 제외). */
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
