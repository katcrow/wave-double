---
title: 'Story 4.1 후속 보강: Epic 7 전략 F와 supply 계약 정합성'
type: 'chore'
created: '2026-09-08'
status: 'done'
review_loop_iteration: 0
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-retro-09-08-2026.md'
baseline_commit: '8e82160c6e5354597d94cb348cb754d250dc6079'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 7에서 전략 F가 추가된 뒤 로컬 코드는 F-only·다중 태그 후보를 supply stage까지 처리할 수 있지만, 이 경계를 직접 보장하는 회귀 테스트가 없다. 더 중요하게는 운영 Supabase에 Story 4.1의 supply 게이트와 Epic 7의 F 제약/rule migration이 없어 로컬 구현과 운영 계약이 서로 다른 상태다.

**Approach:** active `candidate_tags`를 전략명과 무관하게 distinct 후보로 수집하는 계약과, 동일 후보의 다중 전략 태그가 t1702 1콜 원칙을 깨지 않는 계약을 회귀 테스트로 고정한다. 누락된 forward-only migration을 의존 순서대로 운영 프로젝트에 적용하고, F tag·F outcome rule·supply publish gate를 rollback 가능한 명시적 fixture로 검증한다.

## Boundaries & Constraints

**Always:** Story 4.1의 후보당 t1702 1콜, trading-calendar 기반 D-2/D-1/D0 매핑, `stage_status.supply_3day='success'` 발행 게이트를 유지한다. 전략 수가 늘어도 수급 행은 candidate_id·attempt 기준으로만 생성한다. 운영 검증은 Supabase MCP에서 실제 프로젝트에 수행하고, fixture 데이터는 트랜잭션 rollback으로 남기지 않는다. migration은 로컬 파일 순서와 동일한 forward-only 순서로 적용한다.

**Never:** t1702를 전략별로 중복 호출하거나 supply schema의 attempt lineage/UNIQUE 계약을 완화하지 않는다. 기존 A~E outcome을 재계산하지 않는다. 전략 G 실험 산출물, UI 배지 검증, F OOS 재평가는 이 작업에 포함하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| F-only tag | 한 attempt에 F active tag만 존재 | tagged fetcher가 후보를 반환하고 supply stage가 t1702를 1회 호출해 3행 저장 | 누락/실패 시 해당 후보만 partial |
| Multi-tag candidate | 같은 후보에 A와 F active tag 존재 | candidate_id를 1회만 조회·수집하고 3행만 저장 | 중복 수급 행을 만들지 않음 |
| Production contract | 운영 migration 적용 후 F tag와 F rule 존재 | F tag 삽입, `(3,4,999999)` rule 조회, supply success publish gate가 모두 통과 | 각 fixture assertion 실패 시 작업 실패 |

</frozen-after-approval>

## Code Map

- `C:/dev/wave-double/apps/batch/tagged_candidate_fetcher.py` -- active tag의 candidate_id를 distinct 처리하는 supply 대상 조회; 전략명에 대한 필터가 없어 F 포함 여부의 핵심 경계다.
- `C:/dev/wave-double/apps/batch/supply_stage.py` -- 조회된 후보별 t1702 1콜과 3거래일 행 생성; 전략 태그 수와 무관한 수집 단위다.
- `C:/dev/wave-double/tests/batch/test_tagged_candidate_fetcher.py` -- active tag 조회·중복 제거 회귀 테스트.
- `C:/dev/wave-double/tests/batch/test_supply_stage.py` -- 후보별 1콜 및 3행 저장 회귀 테스트.
- `C:/dev/wave-double/tests/sql/test_supply_3day_publish_guard.sql` -- supply 성공 게이트와 attempt-scoped fixture; F-only/multi-tag 경계를 추가할 위치다.
- `C:/dev/wave-double/infra/supabase/migrations/202609070900_supply_3day_publish_guard.sql` -- Story 4.1의 publish/dashboard 계약 migration, 운영 catalog 누락을 확인했다.
- `C:/dev/wave-double/infra/supabase/migrations/202609070901_relax_supply_3day_confirmed_program_net.sql` -- t1637 병합 전 `program_net` NULL 허용 계약.
- `C:/dev/wave-double/infra/supabase/migrations/202609071000_expand_candidate_tags_strategy_check_f.sql` -- F tag CHECK 확장 migration.
- `C:/dev/wave-double/infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql` -- F outcome rule `(3,4,999999)` 및 snapshot 계약 migration.
- 운영 읽기 증거: Supabase MCP `list_migrations`는 202609052100 이후 migration이 없고, `candidate_tags_strategy_check`는 A~E, `outcome_strategy_rules`에도 F row가 없음을 반환했다.

## Tasks & Acceptance

**Execution:**
- [x] `tests/batch/test_tagged_candidate_fetcher.py` -- F-only active tag와 A/F 동일 후보 fixture를 추가해 전략명 무관 조회·distinct candidate_id를 검증한다.
- [x] `tests/batch/test_supply_stage.py` -- F-only 및 multi-tag 후보가 후보당 1회 t1702 호출·3행 저장되는 회귀를 추가한다.
- [x] `tests/sql/test_supply_3day_publish_guard.sql` -- F tag가 supply 대상에서 빠지지 않고 supply success 후 publish gate가 통과하는 fixture assertion을 추가한다.
- [x] `infra/supabase/migrations/202609070900_supply_3day_publish_guard.sql`, `202609070901_relax_supply_3day_confirmed_program_net.sql`, `202609071000_expand_candidate_tags_strategy_check_f.sql`, `202609080900_parameterize_outcome_strategy_rules_f.sql` -- 운영 Supabase MCP에 파일 순서대로 적용하고 적용 결과를 기록한다.
- [x] 운영 Supabase MCP fixture -- migration catalog, F constraint, F rule, F tag insert/duplicate rejection, supply success publish gate와 grants를 pass/fail 행으로 검증하고 rollback한다.

**Acceptance Criteria:**
- Given F-only 또는 A/F multi-tag 후보가 있는 attempt, when supply 대상 조회와 stage를 실행하면, then 후보는 정확히 1회 t1702 호출되고 3개의 `supply_3day` 행이 저장된다.
- Given 네 migration이 운영에 적용된 경우, when 운영 schema와 F fixture를 조회하면, then F constraint/rule 및 Story 4.1 supply publish gate가 로컬 migration 정의와 일치한다.
- Given supply stage가 success인 close attempt, when `publish_attempt`를 호출하면, then supply gate를 통과하고 기존 A~E outcome 호환성이 유지된다.

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass

- intent_gap: 0
- bad_spec: 0
- patch: 7
- defer: 1
- addressed:
  - F-only tagged-candidate test가 `status=eq.active`를 사용하고 `strategy` 필터를 보내지 않는지 assertion을 추가했다.
  - real `TaggedCandidateFetcher`에서 F-only 후보를 받아 supply stage가 후보당 1회 호출·3행 저장하는 연결 테스트를 추가했다.
  - F-only 및 A/F multi-tag supply 테스트가 후보별 D-2/D-1/D0 slot 소유권을 확인하도록 보강했다.
  - SQL fixture에 F constraint/rule과 service-role 전용 publish/emit grants assertion, A/F multi-tag, F TP/SL/cutoff 및 OPEN payload assertion, 정확히 5개 pass row assertion을 추가했다.
  - SQL fixture의 publish 후보를 `STORY41F`로 격리해 실종목 충돌 가능성을 줄였다.
- dismissed:
  - inactive/vanished tag 응답 fixture 부재 지적은 `status=eq.active` 요청 자체를 assertion하고 있어 필터 제거 시 테스트가 실패하므로 별도 응답 행이 없어도 핵심 계약이 검증된다.
  - rollback assertion이 SQL 파일 내부 select 뒤에 있다는 지적은 fixture 실행 후 별도 Supabase MCP query로 2099 fixture 5종 잔여 행 0건을 확인해 보완했다.
  - A~E 호환성 부재 지적은 동일 A/F multi-tag publish에서 A outcome 생성과 F rule snapshot을 함께 assertion하고, 전체 Python 250개 및 backtest 152개 회귀를 통과해 기각했다.
  - SQL fixture가 Python t1702를 호출하지 않는다는 지적은 계층 경계상 SQL이 LS API를 호출하지 않도록 유지하고, real fetcher→supply stage 연결을 Python 테스트로 추가해 해결했다.
- defer:
  - 컴파일된 `epic-4-context.md`의 수동 보강을 원천 planning artifact와 자동 동기화하는 문제는 agent-context/process 범위라 `deferred-work.md`에 기록했다.

## Design Notes

운영 migration 적용은 `202609070900` → `202609070901` → `202609071000` → `202609080900` 순서를 따른다. F migration은 Story 4.1 코드 변경이 아니라 Epic 7 drift 해소에 필요한 운영 전제이며, supply stage는 전략별 outcome rule을 해석하지 않고 candidate_id만 소비하므로 코드 결합을 추가하지 않는다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/batch/test_tagged_candidate_fetcher.py tests/batch/test_supply_stage.py tests/batch/test_scheduler.py -q` -- expected: 신규 회귀 포함 전부 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/ -q` -- result: `250 passed`.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- result: `152 passed`.
- `python tools/check_migration_order.py` -- expected: migration 순서 통과.
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks:**
- Supabase MCP에서 운영 migration catalog, CHECK constraint, F rule, function grants 및 rollback fixture의 pass/fail assertion을 확인한다. 결과: fixture 5건, schema/grant assertion 5건, rollback 잔여 데이터 5종 모두 `pass`.
- 운영 migration 적용 결과: 네 migration 모두 `success`; 적용 후 catalog에 네 항목이 순서대로 존재한다.
- Supabase MCP `tests/sql/test_supply_3day_publish_guard.sql` 실행 결과: `schema_and_grants`, `pending_supply_gate`, `failed_supply_gate`, `partial_supply_gate`, `f_only_publish_and_snapshot` 5개 행이 모두 `pass`.
- Supabase MCP rollback 후 별도 조회 결과: `runs`, `logical_runs`, `candidate_tags`, `supply_3day`, `daily_ohlcv` fixture 잔여 행이 모두 `0`.

## Suggested Review Order

**전략 중립 수급 수집 경계**

- F-only·A/F 후보가 전략 수가 아닌 candidate_id 기준으로 한 번씩 처리되는지 확인한다.
  [`test_supply_stage.py:141`](../../tests/batch/test_supply_stage.py#L141)

- 실제 tagged fetcher가 F-only active 후보를 supply stage로 전달하는지 확인한다.
  [`test_supply_stage.py:165`](../../tests/batch/test_supply_stage.py#L165)

- active 필터와 strategy 무관 조회가 함께 보장되는지 확인한다.
  [`test_tagged_candidate_fetcher.py:60`](../../tests/batch/test_tagged_candidate_fetcher.py#L60)

**운영 DB 계약**

- F 제약·rule·grants와 supply gate를 실제 transaction fixture가 검증하는지 확인한다.
  [`test_supply_3day_publish_guard.sql:6`](../../tests/sql/test_supply_3day_publish_guard.sql#L6)

- A/F multi-tag publish와 F TP/SL/cutoff snapshot이 함께 검증되는지 확인한다.
  [`test_supply_3day_publish_guard.sql:151`](../../tests/sql/test_supply_3day_publish_guard.sql#L151)

**추적 문서**

- 리뷰 triage와 운영 검증 결과가 보강 범위 및 잔여 process 이슈와 일치하는지 확인한다.
  [`spec-4-1-epic7-계약-보강.md:66`](spec-4-1-epic7-계약-보강.md#L66)
