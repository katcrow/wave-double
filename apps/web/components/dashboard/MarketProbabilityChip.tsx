import type { MarketIndexProbabilityRpcRow } from "@/lib/dashboard-types";
import { deriveMarketProbabilityChipState } from "@/lib/market-probability";

interface Props { row: MarketIndexProbabilityRpcRow | null; fetchFailed: boolean }

const LAST_SUCCESS_FORMAT = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
});

export default function MarketProbabilityChip({ row, fetchFailed }: Props) {
  const todayKst = new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Seoul" }).format(new Date());
  const state = deriveMarketProbabilityChipState(row, fetchFailed, todayKst);
  return (
    <aside className="market-probability-chip" aria-label="종가배팅 참고 확률">
      <div className="market-probability-chip__head">
        <span className="market-probability-chip__label">종가배팅 참고 · 익일 고가 돌파</span>
        <span className="market-probability-chip__badge">참고용</span>
        {state.status === "ready" && state.stale && (
          <span className="market-probability-chip__badge market-probability-chip__badge--stale">직전값</span>
        )}
        <details className="market-probability-chip__info">
          <summary aria-label="종가배팅 참고 확률 설명">ⓘ</summary>
          <p>
            오늘 종가보다 다음 거래일 고가가 높을 확률 · 장중 등락률과 과거 일봉을 비교한 실험값 · 후보 판단 참고
          </p>
        </details>
      </div>
      {state.status === "failed" ? (
        <p className="market-probability-chip__message" role="status">확률 불러오기 실패</p>
      ) : state.status === "empty" ? (
        <p className="market-probability-chip__message" role="status">확률 아직 계산 전</p>
      ) : (
        <>
          <dl className="market-probability-chip__values">
            <div><dt>코스피</dt><dd>{state.kospiPercent}</dd></div>
            <div><dt>코스닥</dt><dd>{state.kosdaqPercent}</dd></div>
          </dl>
          <p className="market-probability-chip__meta">
            {state.row.trading_day} 기준 · 목표 {state.row.target_trading_day} · 계산{" "}
            {LAST_SUCCESS_FORMAT.format(new Date(state.row.last_success_at))} ·{" "}
            {state.row.validation_status === "validated" ? "검증 완료" : "검증 중"}
          </p>
          {state.stale && (
            <p className="market-probability-chip__meta" role="status">오늘 계산값 없음 · 직전 성공값</p>
          )}
        </>
      )}
    </aside>
  );
}
