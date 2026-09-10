---
title: 'Story 5.9: 이탈 임계값(보조) 표시'
type: 'feature'
created: '2026-09-10'
status: 'done'
baseline_revision: '35c6e4b93fb62a56248ed60afdebabffedccf04d'
baseline_commit: '35c6e4b93fb62a56248ed60afdebabffedccf04d'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** Story 5.8의 95% 신뢰구간 판정만으로는 큰 승률·PF 이탈을 빠르게 선별할 수 없다. 다만 고정 임계값이 통계적 1차 판정을 덮어쓰면 작은 표본의 잡음을 과대해석할 수 있다.

**Approach:** 5.8 CI gated view를 소비하는 신규 versioned view에서 게이트 통과 A/B/C 행의 기대 승률·PF 대비 보조 이탈 플래그를 반환한다. 승률은 절대 10%p 초과, PF는 상대 25% 초과를 경고하며, `expected_in_ci`는 그대로 1차 판정으로 보존한다.

## Boundaries & Constraints

**Always:** 5-8 view의 게이트·산식·CI 판정을 그대로 물려받는다. 기대치는 A/B/C만 사용한다(A 승률 0.6871/PF 2.0540, B 0.6895/2.0770, C 0.6600/1.8159; 상세 baseline의 4자리 값). 승률 이탈은 `abs(win_rate - expected_win_rate) > 0.10`, PF 이탈은 `abs(profit_factor - expected_profit_factor) / expected_profit_factor > 0.25`이며 정확히 경계값은 미이탈이다. 보조 플래그는 `expected_in_ci`를 대체하거나 표본 크기에 따라 우선순위를 바꾸지 않는다. migration은 forward-only이고 browser 역할 SELECT는 차단한다.

**Never:** 5-5~5-8 view를 수정하지 않는다. D/E/F·rollup에 근거 없는 기대치를 채우지 않는다. 게이트 미통과 행에 수치·플래그를 노출하지 않는다. UI, RPC, 청산 주문, 컷오프 편향 고지는 이 스토리에서 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| WARN_WIN_RATE | A, settled >= 30, 승률 기대치와 차이 0.10 초과 | `win_rate_threshold_breached=true`, `threshold_warning=true`, CI 판정은 원본 유지 | 없음 |
| WARN_PF | B, settled >= 30, PF 상대 차이 0.25 초과 | `profit_factor_threshold_breached=true`, `threshold_warning=true` | 없음 |
| EXACT_BOUNDARY | 게이트 통과, 승률 차이 0.10 또는 PF 상대 차이 0.25 | 해당 플래그 false | 없음 |
| BELOW_GATE | settled=29 | 기대치·임계값·플래그 모두 NULL, 5-8 게이트 라벨 유지 | 없음 |
| NO_EXPECTATION | D/E/F 또는 rollup, settled >= 30 | CI는 유지하고 기대치·플래그는 NULL | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609101500_create_outcome_win_rate_pf_ci_gated.sql` -- 5-8 CI gated view; 게이트와 `expected_in_ci`의 입력 권위이며 수정 금지.
- `infra/supabase/migrations/202609101100_create_outcome_win_rate_pf.sql` -- 비용 차감 손익률 기반 승률·PF 산식의 원천.
- `C:/dev/wave-double/_bmad-output/specs/spec-wave-double/backtest-baseline.md:307-311` -- A/B/C 기대 PF 4자리 기준과 fixture 원천.
- `packages/read-model/src/database.types.ts:894-913` -- 5-8 view 생성 타입; 신규 view 타입을 인접 위치에 추가.
- `tools/check_outcome_win_rate_pf_ci_parity.py` 및 `tests/tools/test_check_outcome_win_rate_pf_ci_parity.py` -- 게이트·CI parity와 drift 검증 패턴.
- `tests/sql/test_outcome_win_rate_pf_ci_gated.sql` -- candidate_outcome rollback fixture와 5-8 view 검증 패턴.
- `tools/check_migration_order.py`, `tools/check_generated_types_drift.py`, `tools/check_production_parity.py`, `tools/epic-path-manifests/epic-5.txt` -- migration/type/parity/scope gates.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609101600_create_outcome_win_rate_pf_threshold_gated.sql` -- 5-8 view를 소비하고 기대 PF, 임계값 상수, 승률/PF 개별 플래그와 종합 보조 경고를 생성한다.
- [x] `tests/fixtures/outcome_win_rate_pf_threshold_gated/input_cases.json` -- A/B/C의 정상·초과·정확 경계, 29건 게이트 미통과, D/E/F·rollup 사례를 고정한다.
- [x] `tests/sql/test_outcome_win_rate_pf_threshold_gated.sql` -- fixture를 rollback 범위에 삽입하고 SQL 결과를 expected와 절차적으로 대조한다.
- [x] `tools/check_outcome_win_rate_pf_threshold_parity.py` -- JSON↔SQL INSERT↔Python 기준값↔SQL expected 4중 parity를 검사한다.
- [x] `tests/tools/test_check_outcome_win_rate_pf_threshold_parity.py` -- 경계 포함/초과, 게이트·기대치 NULL, CI 판정 보존 및 상수/매핑 drift를 검증한다.
- [x] `.github/workflows/test.yml` -- 신규 threshold parity gate를 schema 테스트에 연결한다.
- [x] `packages/read-model/src/database.types.ts`, `tools/epic-path-manifests/epic-5.txt` -- 생성 타입과 Epic 5 scope를 갱신한다.
- [x] `tools/production_parity_baseline.json`, `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 운영 migration 적용 후 baseline과 5-9 상태를 갱신한다.

**Acceptance Criteria:**
- Given 게이트 통과 A/B/C 행, when 승률 또는 PF가 각각 정의된 이탈 임계값을 초과하면, then 해당 개별 플래그와 `threshold_warning`이 true로 반환된다.
- Given 승률 차이가 정확히 10%p 또는 PF 상대 차이가 정확히 25%인 게이트 통과 행, when 보조 경고를 계산하면, then 해당 플래그는 false이다.
- Given 5-8의 `expected_in_ci`가 반환되는 행, when 신규 view를 조회하면, then `expected_in_ci` 값과 CI 컬럼은 변경 없이 함께 반환되고 threshold 플래그는 별도 보조 결과로 반환된다.
- Given 종결 건수가 30 미만이거나 기대치가 정의되지 않은 D/E/F·rollup 행, when 조회하면, then threshold 기대치와 플래그는 NULL이고 5-8의 게이트/CI 의미가 보존된다.
- Given 동일 fixture, when offline parity와 운영 Supabase SQL fixture를 실행하면, then Python 기준값·SQL view·expected rows가 일치하고 migration/type/scope gate가 통과한다.

## Design Notes

- view 이름은 `candidate_outcome_win_rate_pf_threshold_gated`로 고정한다. `expected_win_rate`·`expected_in_ci`는 5-8에서 전달받고 `expected_profit_factor`만 이 스토리에서 추가한다.
- 반환 컬럼은 `win_rate_threshold_pp=0.10`, `profit_factor_threshold_ratio=0.25`, `win_rate_threshold_breached`, `profit_factor_threshold_breached`, `threshold_warning`이다. 모든 비교는 게이트 통과와 A/B/C 기대치 존재를 함께 요구한다.
- `threshold_warning`은 빠른 스크리닝용 보조 신호일 뿐 95% CI 기반 `expected_in_ci`의 대체 판정이 아니다.

## Verification

**Commands:**
- `python tools/check_outcome_win_rate_pf_threshold_parity.py` -- fixture 4중 동등성 통과.
- `pytest -q tests/tools/test_check_outcome_win_rate_pf_threshold_parity.py` -- drift·경계 계약 통과.
- `python tools/check_migration_order.py` 및 `python tools/check_generated_types_drift.py` -- migration/type gate 통과.
- `python tools/check_production_parity.py` -- 운영 baseline 대비 신규 migration이 expected pending으로 확인되고 역방향 drift 없음.
- 운영 Supabase MCP로 migration 및 `tests/sql/test_outcome_win_rate_pf_threshold_gated.sql` 실행 -- SQL assertion pass와 catalog/type ACL 확인.

</intent-contract>

## Spec Change Log

## Review Triage Log

### 2026-09-10 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7: (high 1, medium 4, low 2)
- defer: 0
- dismissed:
  - E2E/브라우저 검증 부재 — 이번 스토리는 UI·RPC 소비면이 없는 read-model 계층이고, 사용자 요구도 E2E를 조건부로 요청했으며 실제 SQL/catalog 검증으로 해당 표면을 검증했다.
  - 운영 적용 증거가 diff에 없다는 주장 — diff 자체는 실행 로그를 담지 않지만 운영 Supabase MCP에서 migration 적용 성공, 명시적 SQL assertion, catalog/ACL 결과를 별도로 확인했다.
  - catalog 검사를 SQL fixture에 넣지 않았다는 주장 — fixture는 rollback 데이터 assertion 전용으로 유지하고 catalog/type/ACL은 운영 catalog 쿼리와 generated-type gate에서 확인하는 분리된 검증 경계다.
  - parity parser가 경계용 두 번째 INSERT를 무시한다는 주장 — 경계 INSERT를 `sql-only boundary fixture` marker 뒤로 분리해 parity parser가 의도한 JSON parity 영역만 읽도록 명시했다.
  - PF 0 기대치 방어가 필요하다는 주장 — 프로젝트의 고정 기대 PF는 모두 양수이며 Python helper에도 0 방어를 추가해 division-by-zero 경로를 차단했다.
  - 테스트가 E/F·상태 다양성을 모두 포함해야 한다는 주장 — E/F, TIMEOUT, zero return, OPEN/SUSPENDED/DELISTED를 계약 테스트에 추가해 해당 동작을 직접 검증했다.
- addressed_findings:
  - `[high][patch]` generated read-model 타입이 동일 view를 두 번 선언하던 문제를 제거하고 `npm run typecheck`로 확인했다.
  - `[medium][patch]` PostgreSQL view의 승률/PF 정확 경계값을 직접 검증하도록 SQL fixture와 assertion을 추가했다.
  - `[medium][patch]` 신규 view의 anon/authenticated SELECT revoke를 SQL fixture와 운영 catalog에서 assert했다.
  - `[medium][patch]` SQL fixture의 expected/view row cardinality를 EXCEPT 비교 전에 검증하도록 보강했다.
  - `[medium][patch]` parity parser의 escaped quote, 컬럼 순서, 누락 컬럼, 중복 strategy, Decimal 정밀도, gross 값 drift 검사를 보강했다.
  - `[low][patch]` 운영 최종 view comment와 migration 계약을 일치시키는 forward-only `202609101602`를 추가하고 불필요한 기대 승률 상수를 제거했다.
  - `[low][patch]` D/E/F·TIMEOUT·zero return·예외 상태 경로의 계약 테스트를 추가했다.

## Auto Run Result

**요약:** `candidate_outcome_win_rate_pf_threshold_gated`를 추가해 Story 5.8의 95% Wilson CI와 `expected_in_ci`를 보존하면서, 게이트 통과 A/B/C의 승률 10%p 초과 및 PF 25% 초과 이탈을 별도 보조 플래그와 `threshold_warning`으로 반환한다. 정확히 경계값은 경고하지 않으며 게이트 미통과·D/E/F·rollup은 기대치와 threshold 결과를 NULL로 유지한다.

**변경 파일:**
- `infra/supabase/migrations/202609101600_create_outcome_win_rate_pf_threshold_gated.sql` — 신규 threshold view, 기대 PF, 컬럼 comment, revoke.
- `infra/supabase/migrations/202609101601_harden_outcome_win_rate_pf_threshold_gated.sql` — 게이트 미통과 행의 임계값 상수/기대 PF NULL 보강.
- `infra/supabase/migrations/202609101602_finalize_outcome_win_rate_pf_threshold_comment.sql` — 운영 catalog 최종 comment와 revoke를 forward-only로 동기화.
- `tests/fixtures/outcome_win_rate_pf_threshold_gated/input_cases.json`, `tests/sql/test_outcome_win_rate_pf_threshold_gated.sql` — 119건 parity 입력, A/B 경고, C 게이트, D/rollup NULL, SQL 경계·ACL assertion.
- `tools/check_outcome_win_rate_pf_threshold_parity.py`, `tests/tools/test_check_outcome_win_rate_pf_threshold_parity.py` — JSON↔SQL↔Python parity와 경계/상태/매핑 drift 계약 테스트.
- `packages/read-model/src/database.types.ts` — 신규 view 단일 생성 타입.
- `.github/workflows/test.yml`, `tools/epic-path-manifests/epic-5.txt`, `tools/production_parity_baseline.json` — CI/scope/운영 baseline 배선.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Story 5.9 완료 상태 동기화.

**리뷰 findings:** patch 7건을 모두 적용했고, high 1·medium 4·low 2, defer 0건이다. dismissed 항목과 사유는 위 Review Triage Log에 기록했다. Follow-up review recommendation은 `true`이며 patched severity count는 high=1, medium=4, low=2, score는 high finding 존재로 계산상 7점 이상이다.

**검증 수행:**
- `python tools/check_outcome_win_rate_pf_threshold_parity.py` — 통과(입력 119건, 전체 종결 119건).
- `uv run --with pytest pytest -q tests/tools/test_check_outcome_win_rate_pf_threshold_parity.py` — 통과(10 passed).
- 기존 5.5~5.9 parity suite — 통과(80 passed).
- `npm run typecheck` — 통과.
- `python tools/check_migration_order.py` — 통과(76 files); `python tools/check_generated_types_drift.py` — 통과(26 objects); `python tools/check_production_parity.py` — 0 ERROR, 0 WARN; `git diff --check` — 통과.
- 운영 Supabase MCP 대상 `https://qqhjeumlecaudsiqhhdu.supabase.co` 확인. `202609101600`, `202609101601`, `202609101602` migration 적용 목록 확인, rollback SQL fixture가 `story 5-9 SQL fixture assertion passed`와 expected_rows=5를 반환, catalog에서 view 24컬럼·comment 존재·anon/authenticated SELECT=false 확인.
- Playwright E2E — UI 변경이 없는 데이터 계층 스토리라 대상 없음.

**잔여 위험:** threshold view는 후속 Story 5.12 UI가 소비할 수 있도록 read-model 타입과 restricted view만 제공하며, 브라우저 표시 문구/필터/E2E는 후속 UI 스토리 범위다.
