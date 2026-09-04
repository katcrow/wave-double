# Epic 6 Context: 전략 확장 — 신규 후보 탐지 기법(D/E) 통합

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

기존 조건검색식 후보 모집단 위에서 전략 A/B/C에 전략 D(돌파3%기법)와 전략 E(익절2%_고정SL5%기법)를 추가로 계산하고, 하나라도 일치한 후보를 다중 전략 태그와 함께 일관되게 노출한다. 이를 통해 신규 전략의 기대 성과를 실제 백테스트 코드로 확인하면서 운영 태깅, 사후 outcome 판정, 전략별 화면까지 같은 계약으로 확장하고, 이후 성과 검증 에픽이 5개 전략을 대상으로 동작할 수 있게 한다.

## Stories

- Story 6.1: 전략 D(돌파3%기법) 계산 로직 코드화 및 백테스트 baseline 이식
- Story 6.2: 전략 E(익절2%_고정SL5%기법) 계산 로직 코드화 및 백테스트 baseline 이식
- Story 6.3: `candidate_tags` 전략 제약 확장
- Story 6.4: 전략 계산 API 일반화
- Story 6.5: Outcome 판정 로직 전략별 파라미터화
- Story 6.6: 후보 태깅 stage에 전략 D/E 반영
- Story 6.7: UI 확장 — 라벨·배지·라우트
- Story 6.8: OOS(워크포워드) 검증

## Requirements & Constraints

- 전략 D는 후보 A 파라미터(N=20, W=3, VMR=0.95, 장기 이동평균 240, RSI(10,6), 임계값 42/최저 30, TP 3%·SL 5%·최대보유 20거래일)를 사용한다. 진입은 고점 돌파·매집 확인·장기 하단 반전·RSI 상향 돌파의 결합이다.
- 전략 E는 SMA20×60 골든크로스, OBV 20일 이동평균 상향 돌파, ADX(14)≥20의 결합을 사용하며 TP 2%·고정 SL 5%·최대보유 30거래일·수수료 0.1%를 적용한다.
- 두 전략 모두 기존 t1859 후보 모집단에 한정해 A/B/C와 OR로 계산한다. 한 종목에 여러 전략이 매칭될 수 있고, 하나 이상의 태그가 있는 후보만 노출된다. 신규 조건검색식이나 신규 후보 원천을 추가하는 범위는 아니다.
- D baseline은 승률 83.1%, 총거래 77건, E baseline은 승률 78.2%, PF 1.34, 총거래 78건으로 기록된 값을 실제 `backtest/` 코드와 동일 데이터·기간으로 재현하거나 차이를 규명해야 한다. 각 전략의 golden fixture 회귀는 Jaccard 유사도 0.9 이상을 기준으로 하며, typed error나 기준 미달은 배포를 막는다.
- OOS/워크포워드 결과는 in-sample과 별도 기간에서 기록한다. OOS 미검증 상태로 진행할 경우 과적합 위험을 명시적으로 추적하며, 결과가 크게 열화되면 파라미터 조정 또는 전략 보류 결정을 문서화한다.

## Technical Decisions

- 운영과 백테스트는 `backtest.strategy_api.compute_abc(frame) -> StrategyResult` 하나를 계속 사용한다. 함수명은 하위호환을 위해 유지하고, 결과는 A/B/C/D/E 시그널과 전략별 TP/SL/최대보유 파라미터를 함께 제공한다. 지표 계산은 프레임워크와 분리된 공유 로직이며 입력 부족·계산 예외는 무신호로 숨기지 않고 typed error로 반환한다.
- DB 변경은 forward-only migration으로 수행한다. `candidate_tags.strategy`는 A/B/C/D/E를 허용하되 기존 A/B/C 행과 조회의 의미를 바꾸지 않고 clean reset 및 N/N-1 호환성 게이트를 통과해야 한다.
- outcome 판정은 전략별 파라미터를 행 생성 시 저장·조회한다. D/E의 TP/SL/보유일을 공통 3%/3%/30일 기본값이나 SQL 리터럴에 의존하지 않으며, 기존 A/B/C outcome은 재계산·수정하지 않는다. outcome event와 projection의 append-only/재생 가능 계약도 유지한다.
- Epic 2의 `candidate_tags`, 공유 계산 API, 다중 태그 산출물을 재사용하며 Epic 2를 재오픈하지 않는다. 시그널 계산에는 기존 일봉 이력 캐시와 데이터 기준의 차이를 전제로 한 회귀 검증을 적용한다.

## UX & Interaction Patterns

- 전략 D/E는 기존 전략과 동일한 다중 배지 패턴으로 표시한다. 태그는 텍스트 라벨을 항상 포함하고, 좁은 폭에서는 줄바꿈 대신 `+N`으로 접는다. 색상은 보조 수단이며 색상만으로 전략을 구분하지 않는다.
- 전략 설명·성과 라우트는 D/E를 허용하고 정의되지 않은 전략 코드는 계속 404 처리한다. A/B/C에 고정된 문구와 성과 전환 UI는 태깅된 전략 목록(가변 개수)과 전체 선택을 지원하도록 일반화한다.
- 성과 비교 화면은 전략별 선택을 제공하되 종결 표본 30건 미만에서는 수치 대신 표본 부족 상태를 우선 표시하고 기대치 판정을 생략한다.

## Cross-Story Dependencies

- 구현 순서는 6.1/6.2(계산·baseline) → 6.3(스키마) → 6.4(API) → 6.5(outcome) → 6.6(태깅 stage) → 6.7(UI)다. 6.8은 6.1/6.2 이후 병행할 수 있다.
- Epic 2의 완료 산출물을 기반으로 하며 재오픈하지 않는다. Epic 3의 기존 outcome 데이터는 보존하고, 전략별 판정 확장만 forward-only로 추가한다.
- Epic 6은 Epic 4의 전략 필터/힌트 배지 통합과 Epic 5의 전략별 view·metric comparison보다 먼저 완료되어야 한다. 그렇지 않으면 해당 에픽이 3전략 가정으로 구현되어 재작업이 발생한다.
