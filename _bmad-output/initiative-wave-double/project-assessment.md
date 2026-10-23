# 현재 프로젝트 조사 — 2026-10-21

## 범위와 증거 수준

사용자는 2026-10-21 기존 기능 정리 + 남은 작업·검증 티켓 작성을 선택했다. 신규 기능과 과거 완료 티켓 복원은 제외한다. 기준 커밋은 b48b74d이며 AGENTS.md와 infra/supabase/migrations/README.md의 기존 사용자 변경은 보존한다.

기존 이니셔티브에는 MVP·v6 완료·배포가 기록되어 있다. 아래는 저장소 구현과 검증 정의의 존재 근거다. 최신 CI·현재 배포·운영 DB·실제 화면 성공을 이번 조사에서 검증하지 않았다. 과거 BMAD 계획은 요구사항 권위로 복원하지 않는다.

## 구현 현황

| 기능 | 구현 근거 | 기존 검증 정의 |
|---|---|---|
| 후보·근거·태그·거래대금·소멸 후보 | apps/web/app/page.tsx, apps/batch/tags_stage.py | e2e/candidate-surface-scenarios.spec.ts, tests/sql/test_get_today_candidate_cards.sql |
| 수급·시장확률 | apps/batch/market_probability.py, apps/web/app/page.tsx | tests/batch/test_market_probability.py, apps/web/lib/market-probability.test.ts |
| 자동·수동 배치·발행 | apps/batch/__main__.py, apps/batch/scheduler.py, apps/web/lib/dispatch-outbox-worker.ts | tests/batch/test_scheduler.py, tests/sql/test_dispatch_outbox.sql, e2e/manual-trigger.spec.ts |
| 실행 이력 | apps/web/app/runs/page.tsx, apps/batch/run_state.py | tests/batch/test_run_state.py, tests/sql/test_run_lineage.sql |
| 추적·통계·편향 | apps/web/app/tracking/page.tsx | e2e/tracking.spec.ts, tests/sql/test_get_outcome_tracking_rows.sql |
| 전략 커널 | backtest/strategy_api.py, backtest/indicator_opt/ | backtest/tests/test_strategy_api.py, backtest/tests/test_params_sql_parity.py |
| CI·운영 대조 | .github/workflows/test.yml, tools/check_production_parity.py | tests/tools/test_check_production_parity.py, tests/sql/ |
| 백업·복구 | .github/workflows/backup.yml, .github/workflows/backup-restore-drill.yml | tests/sql/restore_drill_smoke.sql |

검증 파일은 조사 시 실행하지 않았으며 위 표는 통과 결과를 뜻하지 않는다.

## 운영 신뢰성

현재 SHA의 배포·CI·운영 migration/RPC/권한 동등성이 미확인이다. test.yml은 SQL fixture와 N/N-1 비교를 정의하지만 pg_cron shim을 쓰고 실제 worker cron migration을 제외하므로 운영 스케줄 증거를 대신하지 못한다. 1.1이 기준 SHA·run/day·증거 위치와 기존 정상 배치 한 건의 dispatch→run→publish→후보 화면 경로를 읽기 조회와 Playwright MCP로 확보한다.

scheduled-batch.yml은 workflow_dispatch 경로다. 자동은 pg_cron→outbox→웹 worker→GitHub dispatch→Python 배치→publish_attempt 흐름이다. logical run·lease/fence·heartbeat·운영창 검사·close 발행 경계가 구현되어 있다. 1.2는 정상·휴장·부분실패·재시도에서 발행까지 추적한다.

6시간 간격 암호화 백업과 분기 복구 드릴이 정의돼 있다. 최신 artifact 복구 가능성과 실측 RPO/RTO는 미확인이다. 1.3은 운영 원본을 덮어쓰지 않는 격리 복원 증거를 확인한다.

## 후보 판단

2.1은 complete snapshot 기준 후보·근거·거래대금·소멸 후보와 필터·정렬·실패/0건 구분을 검증한다. 2.2는 수급 힌트의 run/day 및 시장 수급·매크로·독립 시장확률의 상태·기준시각을 확인한다. 시장확률 RPC는 별도 최신 슬롯을 사용하므로 후보와 같은 run을 강제하지 않는다.

2.3은 로그인·허용 사용자·수동 실행·로그아웃·갱신 경계의 기존 계약을 확인한다. apps/web/app/strategies/[strategy]/page.tsx의 설명/성과 준비 중은 의도된 자리표시자다. 신규 콘텐츠 개발이나 기존 결함으로 확대하지 않는다.

## 성과와 재현성

3.1은 close outcome·이름 스냅샷·원천/전략 필터·재구축의 기존 계약을 조회와 격리 fixture로 검증한다. 3.2는 표본 게이트·신뢰구간·기대치·편향의 기존 SQL/JSON/Python parity와 UI 표시를 대조한다.

3.3은 실행기 계약의 소유자다. A~H/L/M은 공유 시그널 커널이고 I는 수급 기반 운영 전용 경로다. I 과거 수급 부재를 신규 백테스트 개발로 확대하지 않는다. L 전용 run_vwap_recovery는 TP-first·수익 종가 청산·미청산 거래 제외이고 해당 회귀 테스트가 있다. 공통 engine.run_backtest는 기본 SL-first·데이터 끝 강제 청산이다. docs/후보종목-태깅-조건.md의 L 설명은 전용 실행기와 부합한다. 운영 outcome 규칙과의 정합성은 미확인이다. 실행기 차이를 즉시 문서 오류나 버그로 단정하지 않고 호출 경로별로 기록한다.

## 포트폴리오 잔여 작업

4.1의 코드 근거: backtest/portfolio.py simulate_portfolio는 설명과 달리 진입 직전 가용 현금을 검사하지 않는다. 초기자본 100·position_pct=0.25·동일일 다섯 종목 진입·청산 전 조건에서 투입액 125가 가능한 코드 경로다. 코드상 결함이며 실행 재현은 아직 하지 않았다. 첫 종목 날짜만 전체 축으로 쓰고 다음 이벤트 날짜와 ==로 비교하므로 다른 종목만의 날짜에서 포인터 정체 가능성도 있다. 후자는 재현·판정 대상으로 기록하며 확정 버그로 단정하지 않는다.

4.2의 근거: docs/후보종목-태깅-조건.md에 전략 M의 현금·동시보유 한도 기반 자본곡선/MDD 미측정이 명시되어 있다. portfolio.simulate_portfolio는 공통 run_backtest로 거래를 다시 생성하므로 M 전용 박스 하단·ATR 트레일 청산을 보존하는 연결이 아니다. M 전용 거래 결과를 소비하는 경계가 필요하다. portfolio.py OUT은 results_dir 환경변수를 사용하지 않으므로 새 탐색 실행 전에 격리를 보완한다.

4.3은 위 미완 측정을 전체 유니버스에서 수행한다. 초기자본·종목비중·동시보유 한도는 미정이므로 실행 전 확정해야 한다. 비용·중복보유 금지·미청산 평가를 명시하며 전략 파라미터 변경·신규 채택·운영 매매 결정은 제외한다.

