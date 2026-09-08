"use client";

import { useEffect, useRef } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { Market, MarketSupplyRpcRow } from "@/lib/dashboard-types";
import {
  buildMarketSupplyViewModel,
  formatMarketSupplyDate,
  formatMarketSupplyNumber,
  MARKET_OPTIONS,
  normalizeMarket,
} from "@/lib/market-supply";

interface MarketSupplyPanelProps {
  rows: MarketSupplyRpcRow[];
  fetchFailed: boolean;
}

type MarketBarStyle = React.CSSProperties & { "--market-supply-bar-width": string };

export default function MarketSupplyPanel({ rows, fetchFailed }: MarketSupplyPanelProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const rawMarket = searchParams.get("market");
  const market = normalizeMarket(rawMarket);
  const tabRefs = useRef<Partial<Record<Market, HTMLButtonElement>>>({});

  useEffect(() => {
    if (rawMarket === null || rawMarket === market) return;
    const params = new URLSearchParams(searchParams.toString());
    params.set("market", market);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [market, pathname, rawMarket, router, searchParams]);

  function selectMarket(nextMarket: (typeof MARKET_OPTIONS)[number]) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("market", nextMarket);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }

  function handleTabKeyDown(event: React.KeyboardEvent<HTMLButtonElement>, current: Market) {
    const currentIndex = MARKET_OPTIONS.indexOf(current);
    const nextIndex = event.key === "ArrowRight" || event.key === "ArrowDown"
      ? (currentIndex + 1) % MARKET_OPTIONS.length
      : event.key === "ArrowLeft" || event.key === "ArrowUp"
        ? (currentIndex - 1 + MARKET_OPTIONS.length) % MARKET_OPTIONS.length
        : event.key === "Home"
          ? 0
          : event.key === "End"
            ? MARKET_OPTIONS.length - 1
            : -1;
    if (nextIndex < 0) return;
    event.preventDefault();
    const nextMarket = MARKET_OPTIONS[nextIndex];
    selectMarket(nextMarket);
    tabRefs.current[nextMarket]?.focus();
  }

  const viewModel = buildMarketSupplyViewModel(rows, market);
  const panelId = "market-supply-panel-content";

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

      <div className="market-supply-panel__tabs" role="tablist" aria-label="시장 선택">
        {MARKET_OPTIONS.map((option) => {
          const selected = option === market;
          return (
            <button
              type="button"
              role="tab"
              key={option}
              id={`market-tab-${option}`}
              aria-selected={selected}
              aria-controls={panelId}
              tabIndex={selected ? 0 : -1}
              ref={(element) => {
                tabRefs.current[option] = element ?? undefined;
              }}
              className={selected ? "market-supply-panel__tab market-supply-panel__tab--active" : "market-supply-panel__tab"}
              onClick={() => selectMarket(option)}
              onKeyDown={(event) => handleTabKeyDown(event, option)}
            >
              {option}
            </button>
          );
        })}
      </div>

      <div
        id={panelId}
        className="market-supply-panel__content"
        role="tabpanel"
        aria-labelledby={`market-tab-${market}`}
        tabIndex={0}
      >
        {!viewModel.available || !viewModel.row ? (
          <p className="market-supply-panel__state" role={fetchFailed ? "alert" : "status"}>
            {fetchFailed ? "시장 수급을 불러오지 못했습니다." : "시장 수급을 확인할 수 없습니다."}
          </p>
        ) : (
          <>
            <div className="market-supply-panel__day-meta">
              <span>기준일 {viewModel.row.trading_day}</span>
              <span aria-hidden="true"> · </span>
              <span>수집 {formatMarketSupplyDate(viewModel.row.collected_at)}</span>
            </div>
            <div className="market-supply-panel__metrics">
              {viewModel.metrics.map((metric) => (
                <article className="market-supply-panel__metric" key={metric.key}>
                  <header className="market-supply-panel__metric-header">
                    <h3>{metric.label}</h3>
                    <span className={`market-supply-panel__direction market-supply-panel__direction--${metric.direction}`}>
                      {metric.directionLabel}
                    </span>
                  </header>
                  <p className="market-supply-panel__value">
                    {formatMarketSupplyNumber(metric.value)}<span>주</span>
                  </p>
                  <span className="market-supply-panel__bar" aria-hidden="true">
                    <span
                      className={`market-supply-panel__bar-fill market-supply-panel__bar-fill--${metric.direction}`}
                      style={{ "--market-supply-bar-width": `${metric.barWidth}%` } as MarketBarStyle}
                    />
                  </span>
                </article>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}
