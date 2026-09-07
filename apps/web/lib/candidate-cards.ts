import type { TodayCandidateCardRow } from "./dashboard-types.ts";

/**
 * Design Notes: 전략은 A~E까지 가변 개수로 태깅될 수 있다(현재 최대 5종).
 * MAX_VISIBLE_TAGS를 초과하는 나머지는 태그 개수와 무관하게 "+N" 배지로 접힌다
 * (5태그 동시 존재 시 `+3`). 반응형 폭 측정(ResizeObserver 등)은 쓰지 않는 고정 임계값이다.
 */
export const MAX_VISIBLE_TAGS = 2;

export interface CandidateCardViewModel {
  candidateId: string;
  ticker: string;
  name: string | null;
  /** 렌더링용 표시 이름. name이 null이면 ticker로 대체(row.name ?? row.ticker). */
  displayName: string;
  /** 정렬된(A~E, 가변 개수) 태그 중 MAX_VISIBLE_TAGS개까지. */
  visibleStrategies: string[];
  /** visibleStrategies에서 접힌 나머지 태그 수. 0이면 "+N" 배지를 렌더링하지 않는다. */
  hiddenStrategyCount: number;
  /** true면 카드에 "수급 일부 미수집" 단서를 표시한다(카드를 목록에서 제외하지 않는다). */
  supplyPartialMissing: boolean;
  /** Story 2.8: 이전 attempt에서 active였으나 현재 attempt에서 재태깅되지 않은 전략(정렬됨, 접힘 없음). */
  vanishedStrategies: string[];
  /** true면 active 태그가 0건이고 vanished 태그만 있다(카드는 목록에서 제외되지 않고 "소멸" 배지로 표시). */
  isFullyVanished: boolean;
}

/**
 * get_today_candidate_cards() 원시 행 배열을 카드 렌더링용 뷰모델로 변환하는 순수 함수.
 * RPC가 이미 태그 없는 후보는 INNER JOIN으로 제외했고 `strategies`도
 * `array_agg(distinct t.strategy order by t.strategy)`로 정렬해 반환하므로 여기서는
 * 필터링/재정렬을 하지 않는다(SQL이 단일 정렬 출처).
 */
export function buildCandidateCardViewModels(
  rows: TodayCandidateCardRow[]
): CandidateCardViewModel[] {
  return rows.map((row) => ({
    candidateId: row.candidate_id,
    ticker: row.ticker,
    name: row.name,
    displayName: row.name ?? row.ticker,
    visibleStrategies: row.strategies.slice(0, MAX_VISIBLE_TAGS),
    hiddenStrategyCount: Math.max(0, row.strategies.length - MAX_VISIBLE_TAGS),
    supplyPartialMissing: row.supply_partial_missing,
    vanishedStrategies: row.vanished_strategies,
    isFullyVanished: row.strategies.length === 0 && row.vanished_strategies.length > 0,
  }));
}
