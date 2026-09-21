"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  formatOutcomeDate,
  formatOutcomeReturnPct,
  getOutcomeReturnTone,
  getOutcomeStatusMeta,
  getOutcomeStrategyLabel,
  getOutcomeSummary,
  normalizeOutcomeFilters,
  OUTCOME_STATUS_OPTIONS,
  OUTCOME_STRATEGY_OPTIONS,
  type OutcomeTrackingRpcRow,
} from "@/lib/outcome-tracking";
import { toneClassName } from "@/lib/value-tone";

function ReturnPct({ value, status }: { value: number | null; status: OutcomeTrackingRpcRow["status"] }) {
  return <span className={toneClassName(getOutcomeReturnTone(value))}>{formatOutcomeReturnPct(value, status)}</span>;
}

interface OutcomeTrackingPanelProps {
  rows: OutcomeTrackingRpcRow[];
  fetchFailed: boolean;
}

const TABLE_COLUMNS = ["종목", "전략", "진입일", "상태", "종결일", "손익률"];

function OutcomeStatus({ status }: { status: OutcomeTrackingRpcRow["status"] }) {
  const meta = getOutcomeStatusMeta(status);
  return (
    <span className="outcome-tracking__status-group">
      <span className={`outcome-tracking__status outcome-tracking__status--${status.toLowerCase()}`}>
        {meta.label}
      </span>
      <span className="outcome-tracking__status-description">{meta.description}</span>
    </span>
  );
}

export default function OutcomeTrackingPanel({ rows, fetchFailed }: OutcomeTrackingPanelProps) {
  const summary = getOutcomeSummary(rows);
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const filters = normalizeOutcomeFilters(new URLSearchParams(searchParams.toString()));

  function handleFilterSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const nextParams = new URLSearchParams(searchParams.toString());
    for (const key of ["status", "strategy", "ticker"]) {
      const value = String(formData.get(key) ?? "").trim();
      if (value) nextParams.set(key, value);
    }
    const query = nextParams.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return (
    <section className="outcome-tracking" aria-labelledby="outcome-tracking-heading">
      <header className="outcome-tracking__header">
        <div>
          <p className="outcome-tracking__eyebrow">사후 결과 추적</p>
          <h2 id="outcome-tracking-heading">Outcome tracking</h2>
          <p className="outcome-tracking__description">
            종결 결과와 진행 중 건을 상태 의미와 함께 확인합니다. 승률·PF는 여기서 계산하지 않습니다.
          </p>
        </div>
        {!fetchFailed && (
          <p className="outcome-tracking__summary" role="status">
            조회된 종결 {summary.settledCount}건 · 진행 중 {summary.openCount}건
            {(summary.suspendedCount > 0 || summary.delistedCount > 0) &&
              ` · 예외 ${summary.suspendedCount + summary.delistedCount}건`}
          </p>
        )}
      </header>

      {rows.length >= 500 && !fetchFailed && (
        <p className="outcome-tracking__limit-note">조회 결과는 최대 500건까지 표시됩니다.</p>
      )}

      <form key={JSON.stringify(filters)} className="outcome-tracking__filters" method="get" action="/tracking" onSubmit={handleFilterSubmit}>
        <div className="outcome-tracking__filter-field">
          <label htmlFor="outcome-status-filter">상태</label>
          <select id="outcome-status-filter" name="status" defaultValue={filters.status}>
            <option value="">전체 상태</option>
            {OUTCOME_STATUS_OPTIONS.map((status) => <option key={status} value={status}>{status}</option>)}
          </select>
        </div>
        <div className="outcome-tracking__filter-field">
          <label htmlFor="outcome-strategy-filter">전략</label>
          <select id="outcome-strategy-filter" name="strategy" defaultValue={filters.strategy}>
            <option value="">전체 전략</option>
            {OUTCOME_STRATEGY_OPTIONS.map((strategy) => (
              <option key={strategy} value={strategy}>{getOutcomeStrategyLabel(strategy)}</option>
            ))}
          </select>
        </div>
        <div className="outcome-tracking__filter-field outcome-tracking__filter-field--ticker">
          <label htmlFor="outcome-ticker-filter">Ticker</label>
          <input id="outcome-ticker-filter" name="ticker" type="search" maxLength={40} defaultValue={filters.ticker} />
        </div>
        <div className="outcome-tracking__filter-actions">
          <button type="submit">필터 적용</button>
          <a href={(() => { const params = new URLSearchParams(searchParams.toString()); ["status", "strategy", "ticker"].forEach((key) => params.delete(key)); const query = params.toString(); return query ? `${pathname}?${query}` : pathname; })()}>초기화</a>
        </div>
      </form>

      {fetchFailed ? (
        <p className="outcome-tracking__state" role="alert">Outcome 데이터를 불러오지 못했습니다</p>
      ) : rows.length === 0 ? (
        <p className="outcome-tracking__state" role="status">추적 중인 outcome이 없습니다.</p>
      ) : (
        <>
          <div className="outcome-tracking__table-wrap">
            <table className="outcome-tracking__table">
              <caption className="sr-only">추천 후보의 outcome 추적 결과</caption>
              <thead><tr>{TABLE_COLUMNS.map((column) => <th key={column} scope="col">{column}</th>)}</tr></thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.outcome_id}>
                    <th scope="row">{row.ticker}</th>
                    <td>{getOutcomeStrategyLabel(row.strategy)}</td>
                    <td><time dateTime={row.entry_date}>{formatOutcomeDate(row.entry_date)}</time></td>
                    <td><OutcomeStatus status={row.status} /></td>
                    <td>{row.exit_date ? <time dateTime={row.exit_date}>{formatOutcomeDate(row.exit_date)}</time> : "미종결"}</td>
                    <td><ReturnPct value={row.return_pct} status={row.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="outcome-tracking__cards" aria-label="Outcome 추적 카드">
            {rows.map((row) => (
              <article className="outcome-tracking__card" key={row.outcome_id}>
                <header className="outcome-tracking__card-header">
                  <div>
                    <h3>{row.ticker}</h3>
                    <p>{getOutcomeStrategyLabel(row.strategy)}</p>
                  </div>
                  <OutcomeStatus status={row.status} />
                </header>
                <dl className="outcome-tracking__card-details">
                  <div><dt>진입일</dt><dd><time dateTime={row.entry_date}>{formatOutcomeDate(row.entry_date)}</time></dd></div>
                  <div><dt>종결일</dt><dd>{row.exit_date ? <time dateTime={row.exit_date}>{formatOutcomeDate(row.exit_date)}</time> : "미종결"}</dd></div>
                  <div><dt>손익률</dt><dd><ReturnPct value={row.return_pct} status={row.status} /></dd></div>
                </dl>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
