---
title: '코스피·코스닥 다음 거래일 고가 돌파 확률'
type: 'feature'
created: '2026-10-21'
status: 'done'
review_loop_iteration: 0
baseline_commit: 'cda8a36ba8da35a298be1411682b169a7e7e0766'
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/specs/spec-market-index-probability/SPEC.md'
  - '{project-root}/_bmad-output/specs/spec-market-index-probability/data-and-validation.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 종가배팅 후보의 당일 진입 여부를 판단할 때 다음 거래일 지수의 장중 회복 가능성을 참고할 확률이 없다. 목표는 코스피·코스닥 각각에서 다음 공동 거래일 고가가 기준일 종가보다 높은지 추정하는 것이다.

**Approach:** 기존 후보 배치와 독립된 확률 배치가 KST 15:00~19:00에 20분마다 시장 자료를 모으고 확률을 갱신한다. 결과는 거래일별 한 행에 upsert하고 마지막 성공값을 대시보드 시장 흐름 영역에서 참고정보로 보여준다.

## Boundaries & Constraints

**Always:** 성공 라벨은 `next_trading_day.high > trading_day.close`; 같으면 실패다. 코스피 종합 `001`과 코스닥 종합 `301`을 별도 계산한다. 실행 슬롯은 15:00, 15:20, 15:40, 16:00, 16:20, 16:40, 17:00, 17:20, 17:40, 18:00, 18:20, 18:40, 19:00이다. 매 성공 계산이 같은 날짜 행을 갱신하며 실패하면 이전 성공행을 보존한다. 예측·화면은 이미 정해진 후보군을 위한 참고정보로만 동작한다. 당시에 관측할 수 없던 데이터는 feature 생성·검증에 쓰지 않는다. 외부검증이 완료되기 전은 `검증 중`으로 표시한다.

**Never:** 후보 선택·정렬·주문·자동매수를 바꾸지 않는다. 기존 후보 추천 스케줄이나 실행 파이프라인에 시장확률 작업을 결합하지 않는다. 검증되지 않은 예측을 검증된 수익 우위로 표현하지 않는다. 지수선물 일봉 결과만으로 장중 선물 feature를 배제하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 재계산 | 개장일, 필수 입력 정상 | 해당 날짜 한 행의 두 확률·목표일·모델/검증 메타를 원자적으로 갱신 | 성공시각·feature 기준시각 저장 |
| 중복/역순 실행 | 같은 슬롯 재전달 또는 이전 슬롯 늦게 도착 | 중복은 멱등 처리; 오래된 결과가 최신 성공값을 덮지 않음 | 저장 경계에서 슬롯/시각 비교 |
| 일부 API 실패 | 필수 모델 입력 누락·오류 | 새 확률을 쓰지 않고 기존 성공행 유지 | 실패 원인과 입력 품질을 배치 결과에 남김 |
| 학습자료 부족 | 시간순 검증 표본이 불충분 | `검증 중` 상태로 참고 확률 표시; 검증 완료로 주장하지 않음 | 배치는 최신 수집자료만 성공 저장 |
| 휴장/장외 지연 | 거래일이 아니거나 실행시각이 15:00~19:00 밖 | 계산/갱신 없음 | 자동 스케줄 요청은 안전하게 거부 또는 skip |

</frozen-after-approval>

## Code Map

- `packages/domain/domain/run_state.py` -- `BatchKind`, `LogicalRunKey`, slot regex. 새 확률 실행종류와 거래일·20분 슬롯의 도메인 계약을 분리 추가한다.
- `apps/batch/__main__.py`, `apps/batch/scheduler.py` -- 기존 후보 파이프라인 진입점. 새 실행종류는 후보 조회/태깅/발행을 호출하지 않도록 독립 경로를 둔다.
- `infra/supabase/migrations/202609021000_create_dispatch_outbox.sql`, `202609151600_add_auto_schedule_dispatch_cron.sql`, `202609211200_switch_intraday_start_to_08_10.sql`, `202610021000_enforce_batch_operating_window.sql`, `202610021610_tighten_batch_start_deadlines.sql` -- 예약 outbox, 슬롯 enqueue, 실제 시작시각 guard의 기존 SQL 계약. 새 forward migration에서 확률 작업만 15:00~19:00 20분 슬롯으로 확장한다.
- `.github/workflows/scheduled-batch.yml`, `apps/web/app/api/dispatch/worker/route.ts` -- outbox가 기존 workflow_dispatch로 전달되는 경계. 기존 candidate batch 입력·경로를 보존한다.
- `apps/batch/ls_market_index_provider.py`, `ls_market_supply_provider.py`, `ls_market_program_supply_provider.py`, `ls_market_macro_provider.py` -- `t1511`, `t1601`, `t1631`, `t3521` 기존 provider 재사용 후보.
- `apps/batch/market_supply_stage.py`, `apps/batch/market_supply_repository.py` -- attempt 귀속 수급 저장. 새 날짜 기본키 확률 저장소는 attempt cleanup 수명주기와 분리한다.
- `docs/api/ls-openapi/02-sector/chart.md`, `04-futures-options/market-data.md`, `04-futures-options/chart.md` -- 지수 일봉 `t8429`, 지수선물 마스터/현재가 `t8467`/`t2111`, 일봉 차트 `t8466` 계약.
- `apps/web/app/page.tsx` -- 현재 후보 대시보드 및 독립 시장수급 조회. 확률 조회는 complete snapshot 존재 여부에 종속시키지 않는다.
- `apps/web/components/dashboard/MarketSupplyPanel.tsx`, `apps/web/lib/dashboard-types.ts`, `apps/web/lib/market-supply.ts` -- 기존 시장 흐름 표시·RPC 타입·view-model 경계. 신규 확률 view를 후보 순위와 독립 표시한다.
- `packages/read-model/src/database.types.ts` -- 새 dashboard/read RPC의 typed client 계약을 갱신한다.

## Tasks & Acceptance

**Execution:**
- [x] `packages/domain/domain/run_state.py`, `apps/web/lib/dashboard-types.ts`, `apps/web/app/api/dispatch/route.ts` -- 확률 job kind와 슬롯 유효성 계약 추가 -- 수동·예약 dispatch 경계에서 어휘를 일치시킨다.
- [x] `infra/supabase/migrations/202610211000_add_market_probability.sql` -- 날짜별 확률 테이블, upsert RPC, 읽기 RPC, outbox schedule 슬롯 및 operating-window guard 추가 -- 서비스 쓰기와 안전한 dashboard 읽기를 제공하고 기존 후보 계약을 보존한다.
- [x] `apps/batch/market_probability.py`, `apps/batch/__main__.py`, `.github/workflows/scheduled-batch.yml` -- 시장 입력 수집, 점수 산출, 메타 기록, 별도 job dispatch 구현 -- 기존 후보 파이프라인을 실행하지 않는다.
- [x] `apps/web/app/page.tsx`, `apps/web/components/dashboard/MarketProbabilityPanel.tsx`, `apps/web/lib/dashboard-types.ts` -- 코스피·코스닥 확률과 기준일·목표일·최종 성공시각·검증 상태 표시 -- 오류/미검증 상태에서도 기존 후보 화면은 정상 표시한다.

**Acceptance Criteria:**
- Given 공동 거래일이며 허용 슬롯에 입력 조회가 성공했을 때, when 확률 job이 완료되면, then 두 시장 확률은 각각 0~1 범위로 같은 `trading_day` 행에 저장되고 목표일은 다음 공동 거래일이다.
- Given 같은 날짜의 성공 행이 있을 때, when API/모델/저장 단계가 실패하면, then 기존 확률과 `last_success_at`은 변경되지 않는다.
- Given 동일 슬롯 재시도 또는 늦은 이전 슬롯 결과가 도착했을 때, when upsert하면, then 중복 행이 없고 이전 결과가 더 최신 성공값을 덮지 않는다.
- Given 확률 job을 예약 실행할 때, when workflow가 시작되면, then 후보 수집·태깅·후보 snapshot publish는 실행되지 않는다.
- Given 대시보드를 열 때, when 확률 데이터가 없거나 RPC가 실패하면, then 확률 영역은 상태를 설명하고 기존 후보·시장 수급 표시는 계속 동작한다.
- Given 모델의 시간순 외부검증이 기준모델보다 나쁘거나 표본이 부족할 때, when 확률을 표시하면, then `검증 중` 상태가 보여야 한다. 검증 기준을 통과할 때만 완료 상태로 바뀐다.
- Given 다음 거래일 index bar가 확정됐을 때, when 결과를 회고하면, then 라벨은 `next.high > base.close`이며 동일값은 실패로 집계된다.

## Design Notes

현재 live 조회는 위 TR들의 정상 응답을 확인했지만, 15:00~19:00 원천시세 신선도는 확인 전이다. `t3518` 분봉은 빈 응답이어서 제외한다. 지수선물 일봉은 2024-09 이후만 확보됐고 2026년 제한 표본에서 뚜렷한 개선이 없어 모델 기본 feature로 선반영하지 않는다. 장중 선물·수급은 실제 슬롯 수집과 point-in-time 검증 후 challenger로 채택한다. 매 시도 원천/수집시각, feature snapshot, model version, 데이터 품질을 저장해 확률을 재현할 수 있게 한다.

구현 기준 모델은 t1511의 실행 시점 지수 등락률을 과거 t8429 일봉 등락률 구간의 다음 거래일 고가 돌파율에 조건부로 매핑하고 Laplace 보정한다. 현재 quote는 장중 값이고 과거 feature는 종가 값이므로 아직 시간 정합 외부검증이 되지 않았다. 따라서 항상 `experimental`로 저장하고 화면에서 `검증 중`으로 표시한다. 수급·해외매크로·주식선물은 현재 점수에 포함하지 않으며 충분한 시계열을 모아 challenger로 평가한다.

## Verification

**Commands:**
- `uv run --with pytest pytest` (cwd `backtest/`) -- expected: existing backtest regression suite remains green if model work touches shared backtest code.
- `uv run --with pytest pytest` (cwd `apps/batch/`) -- expected: probability batch/provider tests pass.
- `npm run typecheck` (cwd `apps/web/`) -- expected: dashboard RPC/view types compile.

**Manual checks:**
- Confirm the dashboard lists one same-day row after each successful slot, failure preserves prior success, and 19:00 is the final permitted slot.
- Confirm the probability panel does not depend on candidate snapshot availability and does not alter candidate order or order actions.
- Confirm live 15:00~19:00 API values and timestamps are fresh before enabling any signal using those sources.

## Review Triage Log

- **Dismiss — 이동평균 경계가 평가 구간의 미래값을 본다는 주장:** 실제 운영 점수는 `trading_day` 이전 일봉만 남긴 뒤 그 자료의 분위수 경계를 계산한다. 미래 거래일은 입력에 포함되지 않는다. 순차 외부검증은 아직 구현하지 않았으므로 이 코드를 검증 완료 모델로 간주하지 않는다.
- **Dismiss — logical run 제약 교체가 기존 슬롯을 좁힌다는 주장:** 기존 2026-09-21 migration은 intraday `:00/:10/:20/:30/:40`을 허용한다. 새 제약은 이 범위를 그대로 유지하고 market_probability 슬롯만 추가한다.
- **Dismiss — 수집시각이 원천 관측시각을 보장한다는 우려:** LS 응답에 일관된 원천시각이 없다는 제한을 feature quality 메타데이터와 화면의 실험값 문구에 기록했다. 원천시각 신선도는 검증 전까지 보장하지 않는다.
- **Patch — 슬롯 지연·역순 전달:** worker와 batch가 logical slot의 20분 유효구간을 확인하고, 저장 RPC가 낮은 슬롯의 덮어쓰기를 막는다.
- **Patch — 휴장 실행:** probability batch는 주말·알려진 KRX 휴장일에 계산·저장을 건너뛴다.
- **Patch — 이전 거래일 확률 오인:** 화면에 오늘 성공값이 없을 때 직전 성공값임을 표시한다.
- **Patch — 읽기 데이터 최소화:** dashboard RPC는 화면에 필요한 필드만 반환한다.
- **Patch — 전처리 재현성:** 성공 feature snapshot에 계산 대상이 된 과거 일봉과 결과 라벨을 저장한다.
- **Patch — dispatch worker 연결:** worker operating-window guard가 새 kind와 슬롯 지연을 허용하며, batch 완료 RPC가 candidate run 생성을 요구하지 않는다.
- **미해결 검증 제한:** 새 계산·RPC·migration에 대한 자동 테스트나 운영 적용은 이 작업에서 실행하지 않았다. 시간순 Brier/log-loss 및 calibration 평가도 아직 구현되지 않았으므로 확률은 `experimental` 상태를 유지한다.

## Suggested Review Order

**실행·계산 경계**

- 별도 batch kind가 후보 파이프라인을 우회하고 슬롯·휴장·성공 저장을 처리한다.
  [__main__.py:95](../../apps/batch/__main__.py#L95)
- 과거 라벨 기반 조건부 확률과 재현 가능한 입력 snapshot을 구성한다.
  [market_probability.py:57](../../apps/batch/market_probability.py#L57)

**영속성·예약 dispatch**

- 날짜별 단일 결과와 stale-slot fence, 읽기 계약, outbox 종료 경로를 확인한다.
  [migration.sql:101](../../infra/supabase/migrations/202610211000_add_market_probability.sql#L101)
- 20분 예약 슬롯과 기존 배치 dispatch 경계를 함께 확인한다.
  [migration.sql:257](../../infra/supabase/migrations/202610211000_add_market_probability.sql#L257)
- worker가 dispatch 지연 구간을 적용하고 늦은 이전 슬롯을 막는다.
  [dispatch-outbox-worker.ts:68](../../apps/web/lib/dispatch-outbox-worker.ts#L68)

**대시보드 표시**

- 확률 RPC가 후보 snapshot 성공 여부와 독립 호출되는지 확인한다.
  [page.tsx:36](../../apps/web/app/page.tsx#L36)
- 미검증·이전 거래일 값이 참고정보로 표시된다.
  [MarketProbabilityPanel.tsx:9](../../apps/web/components/dashboard/MarketProbabilityPanel.tsx#L9)

**지원 계약**

- 도메인·웹·batch 입력이 같은 시장 확률 슬롯을 허용한다.
  [run_state.py:18](../../packages/domain/domain/run_state.py#L18)
- Supabase RPC 타입과 workflow 입력을 맞춘다.
  [database.types.ts:1194](../../packages/read-model/src/database.types.ts#L1194)
