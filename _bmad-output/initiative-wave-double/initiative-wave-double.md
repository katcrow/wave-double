---
type: initiative
title: "개인투자자를 위한 매수후보 추천 대시보드"
sources: ["_bmad-output/initiative-wave-double/project-assessment.md", "AGENTS.md"]
companions: []
after: []
risk: high
---

# 개인투자자를 위한 매수후보 추천 대시보드

## Description

개인투자자 Neo가 매 거래일 매수후보와 근거를 한 화면에서 확인하도록 웹 대시보드(`apps/web/`), Python 배치(`apps/batch/`), 백테스트 커널(`backtest/`)을 운영한다. 기존 기록상 MVP와 v6 작업은 완료·배포되었다. 이번 트리는 기존 구현의 현재 증거와 확인된 잔여 작업을 관리하며 신규 기능을 추가하지 않는다.

## Outcome

Neo가 후보의 데이터 기준·실패 상태와 성과 계산의 근거를 확인하고 전략 M의 자금 제약을 반영한 위험 측정 결과를 재현할 수 있다.

## Requirements

- R1 (assessment 운영 신뢰성): 배포·CI·운영 스키마의 현재 기준을 확보한다. 완료 증거: 동일 배포 기준의 CI 결과와 운영 대조표에서 통과·실패·미확인을 구분할 수 있다. 기존 정상 배치 한 건의 dispatch→run→publish→후보 화면 경로를 읽기 조회와 Playwright MCP로 연결한다.
- R2 (assessment 운영 신뢰성): 자동 배치부터 화면 발행까지 수명주기를 검증한다. 완료 증거: run_id·logical_run_key·거래일로 배치와 발행 화면을 연결하고 중복 발행·실패 숨김 여부를 판정한 증거가 있다.
- R3 (assessment 운영 신뢰성): 최신 백업과 격리 복구 드릴의 증거를 확인한다. 완료 증거: 암호화 백업 식별자·격리 복원 결과·기존 workflow 기준 대비 실측 RPO/RTO와 미해결 항목이 기록되어 있다.
- R4 (assessment 후보 판단): 후보 스냅샷·카드·근거의 연결을 검증한다. 완료 증거: Playwright MCP에서 정상/빈 결과/실패/부분 상태를 확인하고 SQL 결과와 카드 순서·근거·기준시각이 일치하는 기록을 남긴다.
- R5 (assessment 후보 판단): 수급·시장확률의 기준시각과 실패 표시를 검증한다. 완료 증거: Playwright MCP로 정상/지연/누락/실패를 확인한다. 시장확률에 후보와 같은 run을 강제하지 않고 각 정보의 상태·시각을 구별한다.
- R6 (assessment 후보 판단): 로그인과 수동 실행 후 갱신 경계를 검증한다. 완료 증거: Playwright MCP로 허용/거부 접근과 수동 실행 응답·갱신을 확인한다. 운영 실행이 필요하면 통상 운영창의 단일 실행으로 제한한다.
- R7 (assessment 성과와 재현성): close 발행부터 성과 추적까지 대조한다. 완료 증거: 운영 읽기 조회·격리 fixture·Playwright MCP 증거에서 같은 후보/전략/원천의 추적 행과 발행 계보가 일치한다.
- R8 (assessment 성과와 재현성): 성과 통계와 편향 진단의 표시를 검증한다. 완료 증거: 기존 parity fixture와 Playwright MCP에서 표본 경계·기대치 없음·조회실패·0건이 구분되고 수치와 판정이 일치한다.
- R9 (assessment 성과와 재현성): 전략별 실행기와 성과 비교 계약을 명시한다. 완료 증거: L의 동시 TP/SL·수익 종가·미청산, M의 박스 하단·트레일 회귀와 계약표가 일치한다. 서로 다른 실행 결과를 동일 기준 성과로 취급하지 않는다.
- R10 (assessment 포트폴리오 잔여 작업): 포트폴리오의 가용 현금 초과 진입을 차단한다. 완료 증거: 초기자본 100·종목비중 25%·동일일 5종목·청산 전 사례에서 다섯째 진입을 거부하고 현금이 음수가 되지 않는다. 날짜 불일치·중복종목·청산일 진입 정책도 명시·검증한다.
- R11 (assessment 포트폴리오 잔여 작업): M 전용 청산 거래를 계좌 평가에 연결한다. 완료 증거: M 원본 거래의 진입·청산·비용을 보존하고 합성 계좌가 수작업 계산과 일치한다. WAVE_BACKTEST_RESULTS_DIR 지정 시 커밋 baseline은 바뀌지 않는다.
- R12 (assessment 포트폴리오 잔여 작업): 전체 유니버스에서 M의 자본곡선과 MDD를 측정한다. 완료 증거: 데이터/기간/파라미터/비용/자금조건/명령/산출물로 재실행 가능하며 중복보유·현금음수·한도위반 없이 MDD를 산출한다. 운영 채택 결정은 별도다.

## Constraints

- AGENTS.md Policy: 한국어로 작성하며 비밀 값을 문서·응답·로그·커밋에 기록하지 않는다.
- AGENTS.md Policy: 웹 개발·E2E는 Playwright MCP, 운영 Supabase 작업은 Supabase MCP로 qqhjeumlecaudsiqhhdu에 수행한다. 연결 필요 시 .env.local을 먼저 직접 확인한다.
- AGENTS.md Conventions 및 Running: 전략 라벨·계산 커널과 회귀망을 권위로 사용한다. 탐색 결과는 results_dir 규약으로 격리하고 커밋 baseline은 보존한다.
- project-assessment.md 범위와 증거 수준: 코드·검증 정의와 실행 증거를 구분하며 과거 계획과 미실행 검사를 완료 증거로 쓰지 않는다.

## Done when

- 현재 배포·CI·운영 DB 기준과 배치 발행·복구 결과의 실측 증거가 있고 미해결 오류를 통과로 취급하지 않는다.
- 후보 화면과 접근·수동 실행의 정상/빈 결과/실패/지연 동작을 Playwright MCP로 확인한다.
- 추적·통계 및 실행기 계약을 운영 읽기 증거와 기존 회귀 기준에 대조한다.
- 포트폴리오 현금 회계를 수정하고 M 전용 청산을 보존한 계좌 자본곡선/MDD를 확정된 조건으로 재현한다.

## Boundaries

- 신규 추천 전략·자동 주문·전략 상세 콘텐츠 확장과 과거 완료 티켓 복원은 제외한다.
- Touch point: LS OpenAPI — 기존 시세·수급 원천만 소비; owner: epic-batch-reliability.
- Touch point: Supabase·GitHub Actions·웹 배포 — 기존 발행·실행 계약 검증; owner: epic-batch-reliability. 후보·성과 에픽은 확보된 기준을 소비한다.
- Touch point: 공통 시그널 커널과 labels — 기존 계산과 명칭을 소비; owner: epic-outcome-reproducibility. M 계좌 연결은 epic-portfolio-evidence가 소유한다.
- Tracer path: 현재 배포의 자동 배치→발행 run/day→후보 RPC·화면 및 추적을 연결하고 별도 M 계좌 검증으로 확장한다.
- Must not change: 운영 전략 규칙과 커밋 baseline을 증거 없이 변경하지 않는다.

## References

- assessment — _bmad-output/initiative-wave-double/project-assessment.md
- context — AGENTS.md

## Notes

- Decision: 2026-10-21 사용자 선택으로 기존 기능 정리 + 남은 작업·검증 티켓을 범위로 한다.
- Assumption: 독립 수용 결과 네 개로 나눈 4에픽·12티켓 분할과 순서는 승인 대기 초안이다.
- Open question: 4.3의 초기자본·종목비중·동시보유 한도는 측정 실행 전에 확정한다. 회계 보완과 연결은 먼저 진행할 수 있다.
- Decision: 2026-10-21 분할 제안 — 플랫폼은 구현되어 있으므로 새 scaffold 대신 1.1의 현재 배포·CI·스키마 기준 검증으로 시작한다. 승인 전 제안이다.
- Decision: 2026-10-21 분할 제안 — 기존 코드 계약을 유지하며 3.3이 실행기별 비교 계약을 소유하고 4.2가 소비한다. 새 아키텍처 스파인은 만들지 않는다. 승인 전 제안이다.
