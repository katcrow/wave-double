/**
 * 전략 A/B/C 표시 라벨의 단일 출처.
 * `StrategyTagList`(태그 배지)와 `/strategies/[strategy]`(자리표시자 페이지) 양쪽이 이 맵을 공유한다.
 */
export const STRATEGY_LABEL: Record<string, string> = {
  A: "전략 A",
  B: "전략 B",
  C: "전략 C",
};

/** `strategy`가 own-property로 등록된 전략 코드일 때만 라벨을 반환한다(prototype pollution 방지). */
export function getStrategyLabel(strategy: string): string | undefined {
  return Object.prototype.hasOwnProperty.call(STRATEGY_LABEL, strategy)
    ? STRATEGY_LABEL[strategy]
    : undefined;
}
