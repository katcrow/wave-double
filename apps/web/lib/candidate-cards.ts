import type { TodayCandidateCardRow } from "./dashboard-types.ts";

/**
 * Design Notes: 전략은 A/B/C 3종뿐이라 어떤 조합도 최소 지원 폭에서 한 줄에 들어간다.
 * 3태그 케이스에서만 `+1`이 나타나며, 반응형 폭 측정(ResizeObserver 등)은 쓰지 않는 고정 임계값이다.
 */
export const MAX_VISIBLE_TAGS = 2;

export interface CandidateCardViewModel {
  candidateId: string;
  ticker: string;
  name: string | null;
  /** 렌더링용 표시 이름. name이 null이면 ticker로 대체(row.name ?? row.ticker). */
  displayName: string;
  /** 정렬된(A/B/C) 태그 중 MAX_VISIBLE_TAGS개까지. */
  visibleStrategies: string[];
  /** visibleStrategies에서 접힌 나머지 태그 수. 0이면 "+N" 배지를 렌더링하지 않는다. */
  hiddenStrategyCount: number;
  /** true면 카드에 "수급 일부 미수집" 단서를 표시한다(카드를 목록에서 제외하지 않는다). */
  supplyPartialMissing: boolean;
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
  }));
}
