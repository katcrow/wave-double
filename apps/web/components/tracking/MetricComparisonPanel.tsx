"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  formatMetricCount,
  formatMetricPercent,
  formatMetricProfitFactor,
  getMetricComparisonRow,
  getMetricExpectedVerdict,
  getMetricSampleGateLabel,
  getMetricStrategyLabel,
  getMetricThresholdMessages,
  getMetricTimeoutNotice,
  METRIC_STRATEGY_OPTIONS,
  type MetricStrategy,
  type OutcomeMetricComparisonRpcRow,
} from "@/lib/metric-comparison";
import { getStrategyLabel } from "@/lib/strategy-labels";

interface MetricComparisonPanelProps {
  rows: OutcomeMetricComparisonRpcRow[];
  fetchFailed: boolean;
  selectedStrategy: MetricStrategy;
}

function MetricBar({ observed, expected, maxValue, label, formatValue }: { observed: number | null; expected: number | null; maxValue: number; label: string; formatValue: (value: number | null) => string }) {
  const observedWidth = observed === null ? 0 : (observed / maxValue) * 100;
  const expectedWidth = expected === null ? 0 : (expected / maxValue) * 100;
  const accessibleValues = `${label} 비교 그래픽: 실전 ${formatValue(observed)}, 기대치 ${expected === null ? "없음" : formatValue(expected)}, 최대 기준 ${formatValue(maxValue)}`;
  return (
    <div className="metric-comparison__bar-group" role="img" aria-label={accessibleValues}>
      <div className="metric-comparison__bar-track" aria-hidden="true">
        <span className="metric-comparison__bar-fill metric-comparison__bar-fill--observed" style={{ width: `${observedWidth}%` }} />
        {expected !== null && <span className="metric-comparison__bar-marker" style={{ left: `${expectedWidth}%` }} />}
      </div>
      <p className="metric-comparison__bar-legend">
        <span><i className="metric-comparison__legend-swatch metric-comparison__legend-swatch--observed" />실전</span>
        {expected !== null && <span><i className="metric-comparison__legend-swatch metric-comparison__legend-swatch--expected" />기대치</span>}
      </p>
    </div>
  );
}

function MetricValue({ row }: { row: OutcomeMetricComparisonRpcRow }) {
  const expectedDefined = row.expected_win_rate !== null || row.expected_profit_factor !== null;
  const observedProfitFactor = row.profit_factor === null
    ? null
    : row.profit_factor;
  const observedProfitFactorLabel = row.profit_factor === null && row.gross_loss === null
    ? "산출 불가(음의 손익 없음)"
    : formatMetricProfitFactor(row.profit_factor);
  const profitFactorMax = Math.max(observedProfitFactor ?? 0, row.expected_profit_factor ?? 0, 1);
  return (
    <div className="metric-comparison__values">
      <div className="metric-comparison__metric">
        <div className="metric-comparison__metric-heading"><h3>승률</h3><span>실전 / 기대치</span></div>
        <p className="metric-comparison__metric-value">
          {formatMetricPercent(row.win_rate)} <span>/ {formatMetricPercent(row.expected_win_rate)}</span>
        </p>
        <MetricBar observed={row.win_rate} expected={row.expected_win_rate} maxValue={1} label="승률" formatValue={formatMetricPercent} />
      </div>
      <div className="metric-comparison__metric">
        <div className="metric-comparison__metric-heading"><h3>PF</h3><span>실전 / 기대치</span></div>
        <p className="metric-comparison__metric-value">
          {observedProfitFactorLabel} <span>/ {row.expected_profit_factor === null ? "기대치 없음" : formatMetricProfitFactor(row.expected_profit_factor)}</span>
        </p>
        <MetricBar observed={observedProfitFactor} expected={expectedDefined ? row.expected_profit_factor : null} maxValue={profitFactorMax} label="PF" formatValue={formatMetricProfitFactor} />
      </div>
    </div>
  );
}

export default function MetricComparisonPanel({ rows, fetchFailed, selectedStrategy }: MetricComparisonPanelProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const row = getMetricComparisonRow(rows, selectedStrategy);

  function handleSelectionSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const nextParams = new URLSearchParams(searchParams.toString());
    const value = String(formData.get("metric_strategy") ?? "");
    if (value) nextParams.set("metric_strategy", value);
    else nextParams.delete("metric_strategy");
    const query = nextParams.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  const sampleGateLabel = row ? getMetricSampleGateLabel(row) : null;
  const thresholdMessages = row ? getMetricThresholdMessages(row) : [];
  const timeoutNotice = row ? getMetricTimeoutNotice(row) : null;

  return (
    <section className="metric-comparison" aria-labelledby="metric-comparison-heading">
      <header className="metric-comparison__header">
        <div>
          <p className="metric-comparison__eyebrow">실전 성과 대조</p>
          <h2 id="metric-comparison-heading">Metric comparison</h2>
          <p className="metric-comparison__description">
            5.10 canonical metric의 실전 성과와 백테스트 기대치를 같은 기준으로 비교합니다. 화면에서는 성과를 재계산하지 않습니다.
          </p>
        </div>
        {row && <p className="metric-comparison__scope" role="status">비교 범위: {getMetricStrategyLabel(selectedStrategy)}</p>}
      </header>

      <form key={selectedStrategy} className="metric-comparison__filters" method="get" action={pathname} onSubmit={handleSelectionSubmit}>
        <div className="metric-comparison__filter-field">
          <label htmlFor="metric-strategy-filter">성과 기준 전략</label>
          <select id="metric-strategy-filter" name="metric_strategy" defaultValue={selectedStrategy}>
            <option value="">전체 전략</option>
            {METRIC_STRATEGY_OPTIONS.map((strategy) => (
              <option key={strategy} value={strategy}>{getStrategyLabel(strategy) ?? `전략 ${strategy}`}</option>
            ))}
          </select>
        </div>
        {Array.from(searchParams.entries()).filter(([key]) => key !== "metric_strategy").map(([key, value], index) => (
          <input key={`${key}-${index}`} type="hidden" name={key} value={value} />
        ))}
        <div className="metric-comparison__filter-actions">
          <button type="submit">비교 범위 적용</button>
          <a href={(() => { const params = new URLSearchParams(searchParams.toString()); params.delete("metric_strategy"); const query = params.toString(); return query ? `${pathname}?${query}` : pathname; })()}>전체로 초기화</a>
        </div>
      </form>

      {fetchFailed ? (
        <p className="metric-comparison__state" role="alert">성과 비교 데이터를 불러오지 못했습니다</p>
      ) : !row ? (
        <p className="metric-comparison__state" role="status">선택한 범위의 metric 데이터가 없습니다.</p>
      ) : (
        <article className="metric-comparison__result" aria-label={`${getMetricStrategyLabel(selectedStrategy)} metric 비교 결과`}>
          <div className="metric-comparison__counts" role="status">
            <span>종결 <strong>{formatMetricCount(row.total_settled)}</strong></span>
            <span>진행 중 <strong>{formatMetricCount(row.open_count)}</strong></span>
            {(row.suspended_count > 0 || row.delisted_count > 0) && (
              <span>예외 <strong>{formatMetricCount(row.suspended_count + row.delisted_count)}</strong></span>
            )}
          </div>

          {sampleGateLabel ? (
            <p className="metric-comparison__gate" role="status">{sampleGateLabel}</p>
          ) : (
            <>
              <MetricValue row={row} />
              <div className="metric-comparison__judgement" role="status">
                <p><strong>{row.expected_win_rate === null ? "95% CI" : "95% CI 판정"}</strong> {row.ci_lower === null || row.ci_upper === null ? "-" : `${formatMetricPercent(row.ci_lower)} ~ ${formatMetricPercent(row.ci_upper)}`}</p>
                {row.expected_win_rate !== null && <p>{getMetricExpectedVerdict(row)}</p>}
              </div>
              {thresholdMessages.length > 0 && (
                <div className="metric-comparison__warnings" role="note">
                  <strong>보조 이탈 경고</strong>
                  <ul>{thresholdMessages.map((message) => <li key={message}>{message}</li>)}</ul>
                  <p>95% CI 판정을 대체하지 않는 보조 지표입니다.</p>
                </div>
              )}
            </>
          )}

          {row.expected_win_rate === null && row.expected_profit_factor === null && !sampleGateLabel && (
            <p className="metric-comparison__no-expectation" role="note">기대치 없음 — 이 비교 범위에는 정의된 백테스트 기대치가 없습니다.</p>
          )}
          {timeoutNotice && <p className="metric-comparison__timeout" role="note">{timeoutNotice}</p>}
        </article>
      )}
    </section>
  );
}
