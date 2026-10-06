import type { MarketSupplyRpcRow } from "@/lib/dashboard-types";
import {
  buildMarketSupplyViewModel,
  formatMarketBreadthCount,
  formatMarketIndexChangeRate,
  formatMarketIndexPrice,
  formatMarketSupplyDate,
  formatMarketSupplyNumber,
  MARKET_OPTIONS,
} from "@/lib/market-supply";

interface MarketSupplyPanelProps {
  rows: MarketSupplyRpcRow[];
  fetchFailed: boolean;
}

type MarketBarStyle = React.CSSProperties & { "--market-supply-bar-width": string };
type BreadthSegmentStyle = React.CSSProperties & { "--market-breadth-share": string };

export default function MarketSupplyPanel({ rows, fetchFailed }: MarketSupplyPanelProps) {
  return (
    <section className="market-supply-panel" aria-labelledby="market-supply-heading">
      <header className="market-supply-panel__header">
        <div className="market-supply-panel__title-group">
          <p className="market-supply-panel__eyebrow">시장 전체 수급</p>
          <h2 id="market-supply-heading">시장 흐름</h2>
          <p className="market-supply-panel__freshness">
            장중에도 갱신될 수 있음 · 후보별 수급과 다른 시장 전용 신선도
          </p>
        </div>
        <span className="market-supply-panel__intraday-label">장중 참고</span>
      </header>

      <div className="market-supply-panel__markets">
        {MARKET_OPTIONS.map((market) => {
          const viewModel = buildMarketSupplyViewModel(rows, market);
          const headingId = `market-supply-${market}-heading`;
          return (
            <section className="market-supply-panel__market" key={market} aria-labelledby={headingId}>
              <header className="market-supply-panel__market-header">
                <h3 id={headingId}>{market}</h3>
                {viewModel.index && (
                  <p className="market-supply-panel__index">
                    <span className="market-supply-panel__index-price">
                      {formatMarketIndexPrice(viewModel.index.price)}
                    </span>
                    <span
                      className={`market-supply-panel__index-rate market-supply-panel__index-rate--${viewModel.index.direction}`}
                    >
                      {formatMarketIndexChangeRate(viewModel.index.changeRate)}
                    </span>
                  </p>
                )}
              </header>
              {viewModel.breadth && (
                <div className="market-supply-panel__breadth">
                  <span className="market-supply-panel__breadth-bar" aria-hidden="true">
                    {([
                      ["advancing", viewModel.breadth.advancingShare],
                      ["unchanged", viewModel.breadth.unchangedShare],
                      ["declining", viewModel.breadth.decliningShare],
                    ] as const).map(([kind, share]) => (
                      <span
                        key={kind}
                        className={`market-supply-panel__breadth-segment market-supply-panel__breadth-segment--${kind}`}
                        style={{ "--market-breadth-share": String(share) } as BreadthSegmentStyle}
                      />
                    ))}
                  </span>
                  <dl className="market-supply-panel__breadth-counts" aria-label="종목수">
                    <div className="market-supply-panel__breadth-count market-supply-panel__breadth-count--advancing">
                      <dt>상승</dt>
                      <dd>{formatMarketBreadthCount(viewModel.breadth.advancing)}</dd>
                    </div>
                    <div className="market-supply-panel__breadth-count market-supply-panel__breadth-count--unchanged">
                      <dt>보합</dt>
                      <dd>{formatMarketBreadthCount(viewModel.breadth.unchanged)}</dd>
                    </div>
                    <div className="market-supply-panel__breadth-count market-supply-panel__breadth-count--declining">
                      <dt>하락</dt>
                      <dd>{formatMarketBreadthCount(viewModel.breadth.declining)}</dd>
                    </div>
                  </dl>
                </div>
              )}
              {!viewModel.available || !viewModel.row ? (
                <p className="market-supply-panel__state" role={fetchFailed ? "alert" : "status"}>
                  {fetchFailed ? "시장 수급을 불러오지 못했습니다." : "시장 수급을 확인할 수 없습니다."}
                </p>
              ) : (
                <ul className="market-supply-panel__metrics">
                  {viewModel.metrics.map((metric) => (
                    <li className="market-supply-panel__metric" key={metric.key}>
                      <span className="market-supply-panel__metric-label">{metric.label}</span>
                      <span className={`market-supply-panel__direction market-supply-panel__direction--${metric.direction}`}>
                        {metric.directionLabel}
                      </span>
                      <span className="market-supply-panel__bar" aria-hidden="true">
                        <span
                          className={`market-supply-panel__bar-fill market-supply-panel__bar-fill--${metric.direction}`}
                          style={{ "--market-supply-bar-width": `${metric.barWidth}%` } as MarketBarStyle}
                        />
                      </span>
                      <span className={`market-supply-panel__value market-supply-panel__value--${metric.direction}`}>
                        {formatMarketSupplyNumber(metric.value)}<span>억원</span>
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              {viewModel.available && viewModel.row && (
                <p className="market-supply-panel__day-meta">
                  <span>기준일 {viewModel.row.trading_day}</span>
                  <span aria-hidden="true"> · </span>
                  <span>수집 {formatMarketSupplyDate(viewModel.row.collected_at)}</span>
                </p>
              )}
            </section>
          );
        })}
      </div>
    </section>
  );
}
