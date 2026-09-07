# Epic 4 Context: 후보 근거(3일치 수급) · 시장 전체 수급 · 좋은 수급 힌트

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Neo가 태깅된 각 후보의 2거래일전/1거래일전/당일 가격·수급, 시장 전체(코스피/코스닥) 수급 맥락, '좋은 수급' 힌트를 한 화면에서 확인해 5분 안에 매수 판단을 내릴 수 있게 한다. 종목별 수급(t1702+t1637 병합)과 시장 전체 수급(t1601)을 수집·저장하고, 힌트 판정을 SQL view로 단일화하며, 근거 패널·시장 패널·필터 UI로 노출한다.

## Stories

- Story 4.1: t1702 종목별 가격·수급 수집
- Story 4.2: t1637 프로그램 순매수 수집 병합
- Story 4.3: D0 당일 행 attempt별 누적 저장
- Story 4.4: 빈 수급 적재 방지 가드
- Story 4.5: `market_supply` 스키마 & t1601 수집
- Story 4.6: 후보 근거 패널(Evidence panel) UI
- Story 4.7: 근거 패널 반응형 전환
- Story 4.8: 시장 전체 수급 패널 UI
- Story 4.9: '좋은 수급' 힌트 계산 view
- Story 4.10: 힌트 배지 통합 & 필터

## Requirements & Constraints

- 태깅된 각 후보의 D-2/D-1/D0 3행(종가·거래량·등락율·외인/기관/개인/프로그램 순매수)을 표시한다. 등락율은 전일 종가 대비, 가격은 수정주가 기준이다.
- 시장 전체(코스피/코스닥) 외인/기관/개인/프로그램 순매수 집계를 별도로 표시한다.
- 프로그램+외인+기관이 모두 순매수(>0)일 때만 '좋은 수급' 힌트를 표시하며, 그 외에는 미충족 또는 판정 불가(3상태)로 구분한다. 판정은 UI가 아닌 SQL view/RPC에서 계산해야 하며, Python 계산값과 동등성을 fixture로 검증한다.
- 투자자별 순매수가 전부 0인 응답은 실제 0(순매수 없음)과 구분해 미완료로 처리·재시도한다. 최종적으로도 값이 없으면 NULL + `investor_net_status='pending'`(장중 미확정) 또는 `'missing'`(수집 실패)으로 저장하며, 화면에서 각각 "미확정"/"미수집"으로 렌더링해 0과 혼동하지 않는다. 힌트 판정은 `confirmed`+실제 0만 "미충족"으로, NULL(pending/missing)은 "판정 불가"로 구분한다.
- 결측 종목이 있으면 해당 배치를 부분실패로 기록하고 결측 목록을 남긴다.
- 처리 규모는 태깅된 후보 한정(최대 150종목), LS OpenAPI 호출은 후보당 1콜(t1702), 1콜(t1637) 기준으로 초당 1건 예산 안에서 처리한다.
- 장중 D0 행은 attempt마다 덮어쓰지 않고 누적 저장하여 하루 중 시계열(예: 09:30/10:00/10:30)을 재구성할 수 있어야 한다. 장중 이력은 보존 정책(잠정 90일)에 따라 정리 대상이 될 수 있으나 D-2/D-1 행과 종가 확정 D0 행의 보존 기준은 별도다.

## Technical Decisions

- t1702는 `fromdt`=2거래일전 `todt`=당일 범위로 후보당 1콜 호출해 종가·등락율·거래량·외인(`tjj0016`)/기관(`tjj0018`)/개인(`tjj0008`) 순매수를 확보한다.
- 프로그램 순매수는 t1637(`gubun2=1`, 일자별, `svolume`)로 병합한다. t1636(단일 시점 스냅샷)은 3일 시계열에 부적합하므로 사용 금지.
- 시장 전체 수급은 t1601로 코스피/코스닥 외인/기관/개인을 수집하고 프로그램은 관련 TR(t1631 등)로 보강한다. t1601InBlock은 종목코드 파라미터가 없어 시장 단위 전용이며 종목별 용도로 오용하지 않는다.
- 모든 LS API 호출은 Epic 1의 공통 클라이언트(TR별 token bucket, bounded retry)를 통해서만 이뤄진다.
- supply stage(t1702 병합분)와 market stage가 각각 성공하면 stage-write RPC로 `stage_status.supply_3day`/`stage_status.market_supply`를 `success`로 기록하며, 이 시점부터 두 stage가 `publish_attempt`의 필수 stage 목록에 포함되고 `get_dashboard_snapshot()`의 해당 section이 반영된다.
- `supply_3day`/`market_supply` 스키마 자체는 Epic 2/Epic 1 쪽에서 이미 마련되어 있다(선행조건). 이 에픽의 수집 스토리는 그 스키마를 전제로 값만 채운다.
- 금융 지표(힌트 판정)의 계산 권위는 versioned SQL view/RPC이며 UI는 계산하지 않는다. 임계값은 한 곳(view/설정)에서만 유지한다.

## UX & Interaction Patterns

- Evidence panel: 카드 클릭/Enter로 확장, 거래일 최신(D0)이 위, 원천(t1859/t1852/t1856)과 데이터 생성 시각을 패널 상단에 한 번만 표시. 폴백 원천 사용 시 실제 원천을 명시.
- 부분결측 배지: 3행 중 일부만 결측인 경우 "D-2/D-1/D0 중 N행이 미수집" 형태로 패널 상단에 표시하며, 정상/결측 슬롯을 시각적으로 구분한다. 배치 실패가 더 광범위하면 실패 상태가 부분결측 배지보다 우선.
- 반응형: ≥1200px는 고정 3행 테이블, <768px는 날짜별 행 카드로 전환. 200% 확대에서 내용이 잘리지 않아야 하고, 테이블은 행/열 헤더를 제공한다.
- Market supply panel: 코스피/코스닥 탭(URL 또는 로컬 상태 보존), 방향을 숫자+막대로 표시. 종목별 수급과 다른 신선도 라벨을 사용하고, 장중에는 "장중 참고" 라벨을 고정 표시한다.
- 힌트 배지: Candidate summary card에 좋은 수급/미충족/판정 불가를 표시한다.
- 필터: 전략/수급힌트/시그널상태/원천 필터에 더해 "수급 결측 포함/제외" 옵션을 제공해 부분결측 후보를 분석에서 제외할 수 있게 한다. 필터 결과 0건이면 적용된 필터를 보여주고 일괄 초기화를 제공한다. 모든 필터는 키보드로 접근 가능해야 한다(WCAG 2.2 AA).
- Voice/tone: "판정 불가 · 장 마감 후 확정" 같은 확정 문구를 사용하고 "매수 확정"류 금융조언 표현은 금지한다.

## Cross-Story Dependencies

- 4.1/4.2/4.4(t1702+t1637 병합, 빈 수급 가드)와 4.5(t1601)는 Epic 1의 stage-write RPC, publish_attempt 필수 stage 레지스트리, LS 공통 클라이언트(Story 1.3/1.4)에 의존한다.
- `supply_3day`/`investor_net_status`(confirmed/pending/missing) 스키마는 Epic 2 Story 2.6에서 이미 정의됨 — 이 에픽은 그 계약을 전제로 값만 채운다.
- 4.9의 힌트 view는 4.1/4.2/4.4가 채운 `supply_3day` 데이터에 의존하며, 4.10의 UI 배지·필터는 4.9의 view 결과에 의존한다.
- 4.6/4.7(Evidence panel)은 4.1~4.4의 데이터와 Epic 1 Story 1.9의 카드/화면 뼈대 위에 구축된다.
- 4.8(Market supply panel)은 4.5의 `market_supply` 데이터에 의존한다.
