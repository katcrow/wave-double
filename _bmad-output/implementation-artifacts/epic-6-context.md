# Epic 6 Context: 전략 확장 — 신규 후보 탐지 기법(D/E) 통합

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

기존 t1859 후보 모집단에서 전략 A/B/C에 D(돌파3%기법)와 E(익절2%·고정 SL 5% 기법)를 추가로 계산하고, 매칭된 후보를 다중 전략 태그로 일관되게 제공한다. 운영 태깅과 백테스트가 동일한 계산 계약을 사용하도록 확장해 이후 outcome 및 성과 검증 화면이 다섯 전략을 처리할 수 있게 한다.

## Stories

- Story 6.1: 전략 D 계산 로직 코드화 및 백테스트 baseline 이식
- Story 6.2: 전략 E 계산 로직 코드화 및 백테스트 baseline 이식
- Story 6.3: `candidate_tags` 전략 제약 확장
- Story 6.4: 전략 계산 API 일반화
- Story 6.5: Outcome 판정 로직 전략별 파라미터화
- Story 6.6: 후보 태깅 stage에 전략 D/E 반영
- Story 6.7: UI 확장 — 라벨·배지·라우트
- Story 6.8: OOS(워크포워드) 검증

## Requirements & Constraints

- D는 N=20, W=3, VMR=0.95, 장기 이동평균 240, RSI(10,6), 임계값 42/최저 30, TP 3%·SL 5%·최대보유 20거래일을 사용한다. 진입은 고점 돌파·매집 확인·장기 하단 반전·RSI 상향 돌파의 결합이다.
- E는 SMA20×60 골든크로스, OBV 20일 이동평균 상향 돌파, ADX(14)≥20을 결합하고 TP 2%·고정 SL 5%·최대보유 30거래일·수수료 0.1%를 사용한다.
- A/B/C/D/E는 동일 후보 모집단에서 OR로 계산하며 한 종목에 여러 태그가 허용된다. 신규 조건검색식이나 후보 원천 추가는 범위가 아니다.
- D baseline(승률 83.1%, 77건)과 E baseline(승률 78.2%, PF 1.34, 78건)은 동일 데이터·기간으로 재현하거나 차이를 기록한다. 골든 픽스처의 각 전략 Jaccard 회귀 기준은 0.9 이상이며 입력 부족·계산 예외는 typed error로 드러내야 한다.
- OOS 결과는 in-sample과 별도 기간으로 기록한다. 미검증 상태로 진행하면 과적합 위험을 추적하고, 큰 열화 시 조정 또는 보류 결정을 문서화한다.

## Technical Decisions

- 하위호환을 위해 `backtest.strategy_api.compute_abc(frame) -> StrategyResult` 진입점과 함수명은 유지한다. 반환 결과는 A/B/C/D/E 시그널과 전략별 TP/SL/최대보유 파라미터를 제공하며, 공통 지표 계산 로직은 운영과 백테스트가 공유한다. 입력 부족·계산 예외는 무신호로 숨기지 않고 typed error로 반환한다.
- DB 변경은 forward-only로 수행한다. `candidate_tags.strategy`는 A/B/C/D/E를 허용하고 기존 A/B/C 행과 조회 의미를 보존하며 clean reset 및 N/N-1 호환성 검증을 통과해야 한다.
- outcome 행은 전략별 TP/SL/최대보유를 저장·조회한다. D/E를 공통 3%/3%/30일 기본값이나 SQL 리터럴로 판정하지 않으며, 기존 A/B/C outcome은 재계산·수정하지 않는다. append-only 및 재생 가능 계약을 유지한다.
- Epic 2의 `candidate_tags`, 다중 태그 산출물, 일봉 캐시를 재사용하며 Epic 2를 재오픈하지 않는다.

## UX & Interaction Patterns

- D/E도 기존과 같은 다중 배지로 표시한다. 텍스트 라벨은 항상 제공하고, 좁은 폭에서는 줄바꿈 대신 `+N`으로 접으며 색상만으로 전략을 구분하지 않는다.
- 전략 설명·성과 라우트는 D/E를 허용하고 미정의 전략 코드는 계속 404 처리한다. A/B/C 고정 문구와 전환 UI는 가변 전략 목록 및 전체 선택을 지원하도록 일반화한다.
- 성과 비교는 전략별 선택을 제공하되 종결 표본 30건 미만이면 수치 대신 표본 부족 상태를 우선 표시하고 기대치 판정을 생략한다.

## Cross-Story Dependencies

- 구현 순서는 6.1/6.2 → 6.3 → 6.4 → 6.5 → 6.6 → 6.7이다. 6.8은 6.1/6.2 이후 병행할 수 있다.
- Epic 2의 완료 산출물을 기반으로 하며 재오픈하지 않는다. Epic 3의 기존 outcome 데이터는 보존하고 전략별 판정 확장만 추가한다.
- Epic 6은 Epic 4의 전략 필터·힌트 배지 통합과 Epic 5의 전략별 view·metric comparison보다 먼저 완료되어야 한다.
