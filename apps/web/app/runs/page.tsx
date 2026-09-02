import type { LogicalRunRow, RunRow } from "@/lib/dashboard-types";
import { formatKstDateTime } from "@/lib/format";
import { getSupabaseBrowserClient } from "@/lib/supabase-browser";

export const dynamic = "force-dynamic";

const STATUS_LABEL: Record<string, string> = {
  running: "실행 중",
  ready_to_publish: "발행 대기",
  published: "발행 완료",
  partial: "부분성공",
  failed: "실패",
  skipped: "스킵",
  superseded: "대체됨",
  cancelled: "취소됨",
};

const TRIGGER_LABEL: Record<string, string> = {
  schedule: "자동",
  manual: "수동",
};

function stageStatusSummary(stageStatus: Record<string, string> | null | undefined): string {
  if (!stageStatus) return "-";
  return Object.entries(stageStatus)
    .map(([stage, status]) => `${stage}:${status}`)
    .join(", ");
}

export default async function RunsPage() {
  const supabase = getSupabaseBrowserClient();

  const [runsResult, logicalRunsResult] = await Promise.all([
    supabase
      .from("runs")
      .select("*")
      .order("started_at", { ascending: false })
      .limit(100),
    supabase.from("logical_runs").select("*"),
  ]);

  if (runsResult.error || logicalRunsResult.error) {
    return (
      <section aria-labelledby="runs-heading">
        <h1 id="runs-heading">배치 이력</h1>
        <p role="alert">
          배치 이력을 불러오지 못했습니다:{" "}
          {runsResult.error?.message ?? logicalRunsResult.error?.message}
        </p>
      </section>
    );
  }

  const logicalRunByKey = new Map<string, LogicalRunRow>(
    ((logicalRunsResult.data ?? []) as LogicalRunRow[]).map((row) => [
      row.logical_run_key,
      row,
    ])
  );

  const rows = (runsResult.data ?? []) as RunRow[];

  return (
    <section aria-labelledby="runs-heading">
      <header>
        <h1 id="runs-heading">배치 이력</h1>
      </header>

      {rows.length === 0 ? (
        <p>배치 실행 이력이 없습니다.</p>
      ) : (
        <>
          {/* >=768px: 표 */}
          <table className="runs-table">
            <caption className="sr-only">
              거래일·배치 종류별 자동/수동 배치 실행 이력, 시작 시각 내림차순
            </caption>
            <thead>
              <tr>
                <th scope="col">시작 시각 (KST)</th>
                <th scope="col">거래일</th>
                <th scope="col">배치 종류</th>
                <th scope="col">트리거</th>
                <th scope="col">상태</th>
                <th scope="col">단계 상태</th>
                <th scope="col">스킵 사유</th>
                <th scope="col">잘림 건수</th>
                <th scope="col">미처리 건수</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((run) => {
                const logical = logicalRunByKey.get(run.logical_run_key);
                return (
                  <tr key={run.run_id}>
                    <td>{formatKstDateTime(run.started_at)}</td>
                    <td>{logical?.trading_day ?? "-"}</td>
                    <td>{logical?.batch_kind ?? "-"}</td>
                    <td>{TRIGGER_LABEL[run.trigger] ?? run.trigger}</td>
                    <td>{STATUS_LABEL[run.status] ?? run.status}</td>
                    <td>{stageStatusSummary(run.stage_status)}</td>
                    <td>{run.skip_reason ?? "-"}</td>
                    <td>{run.truncated_count}</td>
                    <td>{run.unprocessed_count}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {/* <768px: 행 카드 */}
          <ul className="runs-card-list">
            {rows.map((run) => {
              const logical = logicalRunByKey.get(run.logical_run_key);
              return (
                <li key={run.run_id} className="runs-card">
                  <div className="runs-card__row">
                    <span className="runs-card__label">시작</span>
                    <span>{formatKstDateTime(run.started_at)}</span>
                  </div>
                  <div className="runs-card__row">
                    <span className="runs-card__label">거래일 · 배치</span>
                    <span>
                      {logical?.trading_day ?? "-"} · {logical?.batch_kind ?? "-"}
                    </span>
                  </div>
                  <div className="runs-card__row">
                    <span className="runs-card__label">트리거 · 상태</span>
                    <span>
                      {TRIGGER_LABEL[run.trigger] ?? run.trigger} ·{" "}
                      {STATUS_LABEL[run.status] ?? run.status}
                    </span>
                  </div>
                  <div className="runs-card__row">
                    <span className="runs-card__label">단계 상태</span>
                    <span>{stageStatusSummary(run.stage_status)}</span>
                  </div>
                  <div className="runs-card__row">
                    <span className="runs-card__label">스킵 사유</span>
                    <span>{run.skip_reason ?? "-"}</span>
                  </div>
                  <div className="runs-card__row">
                    <span className="runs-card__label">잘림 · 미처리</span>
                    <span>
                      {run.truncated_count} · {run.unprocessed_count}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </section>
  );
}
