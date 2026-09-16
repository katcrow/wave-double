/**
 * 전략 A/B/C/D/E/F/G/H/I 표시 라벨의 단일 출처.
 * `StrategyTagList`(태그 배지)와 `/strategies/[strategy]`(자리표시자 페이지) 양쪽이 이 맵을 공유한다.
 * 이름은 `docs/보조지표-최적화결과.md`(A/B/C)와 `docs/*기법_추가.md`(D/E/F), `docs/양음돌파패턴.md`(G),
 * `docs/240이평돌파_120이평우상향필터.md`(H)의 확정 전략 정의를 따르며,
 * I(음봉수급쌍끌이)는 백테스트 불가(국면 데이터 t1702 미보유)로 운영 수동 확인 전용이다.
 * `outcome_strategy_rules`의 TP%/SL%/최대보유일 조합으로 대응 문서를 식별했다.
 */
export const STRATEGY_LABEL: Record<string, string> = {
  A: "전략 A · OBV 합집합",
  B: "전략 B · 쌍바닥+주봉K",
  C: "전략 C · 3바닥 다이버전스",
  D: "전략 D · 돌파3%",
  E: "전략 E · SMA GC+OBV+ADX",
  F: "전략 F · 각도가속 쌍바닥",
  G: "전략 G · 양음돌파패턴",
  H: "전략 H · 240이평돌파",
  I: "전략 I · 음봉수급쌍끌이",
};

/** `strategy`가 own-property로 등록된 전략 코드일 때만 라벨을 반환한다(prototype pollution 방지). */
export function getStrategyLabel(strategy: string): string | undefined {
  return Object.prototype.hasOwnProperty.call(STRATEGY_LABEL, strategy)
    ? STRATEGY_LABEL[strategy]
    : undefined;
}
