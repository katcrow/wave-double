import type { MarketIndexProbabilityRpcRow } from "@/lib/dashboard-types";

interface Props { row: MarketIndexProbabilityRpcRow | null; fetchFailed: boolean }

function percent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function MarketProbabilityPanel({ row, fetchFailed }: Props) {
  const todayKst = new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Seoul" }).format(new Date());
  const stale = Boolean(row && row.trading_day !== todayKst);
  return (
    <section className="market-supply-panel" aria-labelledby="market-probability-heading">
      <header className="market-supply-panel__header">
        <div className="market-supply-panel__title-group">
          <p className="market-supply-panel__eyebrow">종가배팅 참고 확률</p>
          <h2 id="market-probability-heading">다음 거래일 지수 고가 돌파</h2>
          <p className="market-supply-panel__freshness">
            오늘 종가보다 다음 거래일 고가가 높을 확률 · 장중 등락률과 과거 일봉을 비교한 실험값 · 후보 판단 참고
          </p>
        </div>
        <span className="market-supply-panel__intraday-label">참고용</span>
      </header>
      {fetchFailed ? <p role="status">시장 확률을 불러오지 못했습니다.</p> : !row ? <p role="status">아직 계산된 시장 확률이 없습니다.</p> : (
        <>
          <dl className="market-supply-panel__markets">
            <div className="market-supply-panel__market"><dt>코스피</dt><dd>{percent(row.kospi_probability)}</dd></div>
            <div className="market-supply-panel__market"><dt>코스닥</dt><dd>{percent(row.kosdaq_probability)}</dd></div>
          </dl>
          <p className="market-supply-panel__freshness">
            {row.trading_day} 기준 · 목표 {row.target_trading_day} · 마지막 계산 {new Intl.DateTimeFormat("ko-KR", {
              timeZone: "Asia/Seoul", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
            }).format(new Date(row.last_success_at))} · {row.validation_status === "validated" ? "검증 완료" : "검증 중"}
          </p>
          {stale && <p role="status">오늘 계산된 값이 없어 직전 성공값을 표시합니다.</p>}
        </>
      )}
    </section>
  );
}
