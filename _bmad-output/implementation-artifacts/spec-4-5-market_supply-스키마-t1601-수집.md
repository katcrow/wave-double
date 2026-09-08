---
title: 'Story 4.5: market_supply 스키마 & t1601 수집'
type: 'feature'
created: '2026-09-08'
status: 'done'
review_loop_iteration: 1
followup_review_recommended: true
baseline_revision: '7f26129837d461e1dd7f8f92234a450ed97f0409'
baseline_commit: '7f26129837d461e1dd7f8f92234a450ed97f0409'
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 현재 후보별 수급만 저장할 수 있어 장중 시장 전체 맥락을 표시할 수 없고, market stage가 발행 전제조건으로 연결되어 있지 않다.

**Approach:** `market_supply`를 attempt 계보에 귀속된 append-only 시장별 스냅샷으로 만들고, 공통 `LsClient`를 통해 t1601의 KOSPI/KOSDAQ 투자자 순매수와 t1631 프로그램 순매수를 수집한다. 시장별 오류를 격리해 부분 결과를 보존하되 두 시장이 모두 완료된 경우에만 stage 성공·발행을 허용한다.

## Boundaries & Constraints

**Always:** `market_supply` 행은 `attempt_run_id`와 `trading_day`를 가지며 시장은 KOSPI/KOSDAQ만 허용한다. 자연키는 `(attempt_run_id, market, trading_day)`로 멱등 upsert하고, 모든 수치의 유한값을 검증한다. t1601은 종목코드 없이 시장 전체를 조회하는 `/stock/investor` TR로만 호출하고, t1631은 KOSPI `gubun=1`·KOSDAQ `gubun=2`로 `/stock/program`을 호출해 프로그램 순매수를 보강한다. 성공한 시장의 행은 저장하고 실패 시장 목록과 오류를 stage 결과에 남긴다. `market_supply` stage는 close/intraday에서 tags·supply_3day 뒤 실행하며 두 시장 모두 성공할 때만 `success`로 기록한다.

**Never:** t1601을 종목별 데이터로 사용하지 않는다. 기존 migration을 수정하거나 supply_3day 행을 덮어쓰지 않는다. 전부 0인 시장 수급을 결측으로 재해석하거나 임의 재시도하지 않는다. 한 시장 실패를 숨기고 전체 stage/publish를 성공으로 보고하지 않는다. premarket에서 당일 시장 수급 stage를 호출하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | t1601의 KOSPI/KOSDAQ 투자자 값과 t1631 양 시장 값 | 두 시장 1행씩 저장, stage success | 없음 |
| ONE_MARKET_FAILURE | 한 시장 t1631 실패 또는 값 파싱 실패 | 성공 시장 행은 보존, stage partial, 실패 시장 목록 기록 | publish 차단 |
| MALFORMED_RESPONSE | 필수 block/필드 누락, 비수치, NaN/Infinity | 행을 저장하지 않음 | 구조화된 failed/partial 결과 |
| IDEMPOTENT_RETRY | 같은 attempt·시장·일자 재실행 | 동일 자연키 1행 유지, 최신 수집값으로 upsert | 기존 attempt 행은 변경하지 않음 |

</intent-contract>

## Code Map

- `apps/batch/ls_client.py:141-239` -- TR별 token bucket, bounded retry, 직렬화와 `/stock/investor`·`/stock/program` path 전달 경계.
- `apps/batch/ls_supply_provider.py:39-94`, `apps/batch/ls_program_supply_provider.py:27-94` -- LS 응답·유한 수치·날짜 파싱의 재사용 패턴.
- `apps/batch/supply_3day_repository.py:51-97` -- service-role PostgREST upsert adapter 패턴.
- `apps/batch/scheduler.py:36-50,187-222` -- tags 뒤 stage 배선, 결과 집계, publish 게이트.
- `apps/batch/__main__.py:88-135` -- CLI 의존성 주입과 closeable adapter 생성 지점.
- `packages/domain/domain/run_state.py:36-53,135-136` -- `Stage.MARKET_SUPPLY`, 필수 stage와 publish 순수 규칙.
- `packages/domain/domain/stage_registry.py:27-50` -- stage verifier 등록 구조.
- `infra/supabase/migrations/202609022000_create_supply_3day.sql` -- 합성 FK·RLS·유한값 CHECK의 기존 스키마 기준.
- `infra/supabase/migrations/202609070900_supply_3day_publish_guard.sql:44-52,279-307` -- publish/snapshot을 forward migration으로 확장할 지점.
- `docs/api/ls-openapi/03-domestic-stock/investors.md:48-89`, `program-trading.md:48-89` -- t1601/t1631 요청·응답 계약. t1601 OutBlock1/2의 KOSPI/KOSDAQ 매핑과 t1631 전체행 선택은 adapter 테스트 fixture로 고정한다.

## Tasks & Acceptance

**Execution:**
- `apps/batch/ls_market_supply_provider.py`, `ls_market_program_supply_provider.py` -- t1601/t1631 요청·시장 매핑·엄격한 응답 파싱 구현 -- 외부 TR 계약을 stage에서 격리한다.
- `apps/batch/market_supply_repository.py` -- `MarketSupplyRow`와 멱등 PostgREST upsert 구현 -- attempt별 이력을 보존한다.
- `apps/batch/market_supply_stage.py` -- 두 시장 수집·부분실패 격리·stage-write 구현 -- 성공/partial/failed를 관측 가능하게 한다.
- `apps/batch/scheduler.py`, `apps/batch/__main__.py` -- close/intraday 배선과 DI, 결과 필드 추가 -- 실제 CLI 경로를 완성한다.
- `packages/domain/domain/run_state.py`, `stage_registry.py` -- market_supply를 필수 stage 및 검증 registry에 반영 -- publish 순수 규칙을 일치시킨다.
- `infra/supabase/migrations/202609081000_create_market_supply.sql`, `202609081100_harden_market_supply_data_guard.sql` -- 테이블/RLS/제약과 publish·snapshot 계약을 forward-only 확장 -- 운영 DB 권위를 반영한다.
- `tests/batch/test_ls_market_supply_provider.py`, `test_ls_market_program_supply_provider.py`, `test_market_supply_stage.py` 및 기존 배선 테스트 -- 정상·부분실패·malformed·멱등 경계 검증.
- `tests/sql/test_market_supply.sql` 및 기존 publish/snapshot fixture, `.github/workflows/test.yml` -- DB 제약·발행 게이트와 CI 실행을 검증.

**Acceptance Criteria:**
- Given 유효한 t1601/t1631 응답과 활성 attempt, when market stage가 실행되면, then KOSPI/KOSDAQ 각각의 외인·기관·개인·프로그램 순매수 1행이 해당 attempt/trading_day에 저장되고 stage가 success다.
- Given 한 시장의 조회·파싱이 실패하면, when stage가 완료되면, then 다른 시장의 행과 실패 목록이 보존되고 stage는 partial이며 publish_attempt는 거부된다.
- Given migration이 운영 프로젝트에 적용되면, when schema와 RPC를 조회하면, then market 자연키·attempt FK·유한값 CHECK·RLS와 market stage 발행 게이트가 확인되고 snapshot의 `market_supply` section이 더 이상 무조건 missing이 아니다.
- Given 같은 attempt의 동일 시장·일자를 재실행하면, when 저장하면, then 자연키 중복 없이 한 행으로 유지되고 다른 attempt의 행은 영향받지 않는다.
- Given t1601을 종목코드와 함께 사용하려는 코드가 있으면, when adapter 계약을 검토하면, then 해당 파라미터가 없고 종목별 수급 경로가 아님이 테스트로 고정된다.

## Design Notes

t1601 샘플은 `tjjcode_17/18/08`의 `svolume`을 외인/기관/개인 값으로 읽고, block 번호의 시장 의미는 공식 fixture로 고정한다. t1631 응답 배열의 프로그램 순매수는 문서의 합계 행 의미를 확인한 뒤 선택하며, 불명확한 행을 임의 합산하지 않는다. 시장 수급의 0은 유효한 실측값이므로 null 결측 규칙은 적용하지 않는다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch tests/domain` -- expected: all focused tests pass.
- `uv run --with pytest pytest tests/` -- expected: full Python regression passes.
- `uv run --with pytest pytest backtest/` -- expected: backtest regression passes.
- `git diff --check` -- expected: no whitespace errors.
- Supabase MCP `apply_migration` + `execute_sql` -- expected: production project schema/grants and explicit pass rows for schema, two-market insert/upsert, partial gate, snapshot, rollback residue 0.

## Review Triage Log

### 2026-09-08 review pass

- **HIGH / patched:** stage success만으로 실제 시장 행이 없는 attempt가 발행될 수 있던 경로를 forward-only `runs` trigger로 보강하고, 빈 데이터 발행 차단 fixture를 추가했다.
- **MEDIUM / patched:** t1601 한 block malformed 시 유효한 다른 시장을 보존하도록 adapter/stage를 수정하고, t1631 응답 순서에 의존하지 않으면서 합계 행을 식별하도록 파서를 보강했다.
- **MEDIUM / patched:** scheduler aggregate 결과가 partial/failed stage의 result code를 잃지 않도록 수정하고, happy path에서 시장별 저장 값·일자·attempt 귀속을 직접 검증했다.
- **LOW / patched:** 유한값 CHECK의 실제 거부 동작, premarket 시장 adapter 미호출, repository의 날짜·수치 타입 경계를 테스트에 추가했다.
- **DISMISSED:** 기본 stage verifier의 실제 행 존재 검증, dashboard UI 표시, 데이터 보존 기간은 기존 verifier/UI 범위 또는 후속 read-model 운영 계약이며 이번 story의 captured intent/acceptance에 없는 항목이다. 현재 publish 권위는 운영 RPC와 trigger, read 권위는 snapshot 함수에 둔다.

follow-up review recommendation: true (HIGH 1, MEDIUM 3, LOW 4 findings were patched in this pass; production migration and fixture were rerun after the fixes).

## Auto Run Result

- **Status:** done
- **Scope:** Story 4.5 `market_supply` schema, t1601/t1631 adapters, market stage, scheduler/CLI DI, publish/snapshot contract, domain stage registry, SQL/Python/CI tests.
- **Implementation:** `market_supply`는 `(attempt_run_id, market, trading_day)` 자연키로 upsert하고 KOSPI/KOSDAQ별 성공 행을 보존한다. t1601은 `/stock/investor`를 종목코드 없이 1회 호출하며, t1631은 시장별 `gubun`으로 호출한다. 두 시장 성공 전에는 stage/publish를 성공으로 보고하지 않는다.
- **Review repairs:** malformed block 부분 보존, t1631 합계 행 순서 독립 파싱, 실제 finite CHECK 검증, 빈 market 데이터 발행 guard, stage result code 전파와 저장값/attempt/date 경계를 보완했다.
- **Production Supabase evidence:** 운영 프로젝트에 `202609081000_create_market_supply`와 `202609081100_harden_market_supply_data_guard`를 적용했다. live catalog 결과는 `table_exists=true`, `rls_enabled=true`, `column_count=8`, `unique_key=true`, `attempt_fk=true`, `publish_guard_trigger=true`였다. SQL fixture 결과는 `attempt_scoped_upsert=pass`, `finite_value_checks=pass`, `publish_and_snapshot_contract=pass`, `schema_contract=pass`였다. `publish_attempt`/`write_stage`는 service_role 실행 권한만 있고 anon/authenticated 실행 권한이 없으며, `get_dashboard_snapshot`은 기존 anon/authenticated/service_role 조회 권한을 유지한다.
- **Verification:** focused Python 79 passed; full Python regression 456 passed; backtest 152 passed; `python -m compileall -q apps/batch packages/domain/domain` passed; `git diff --check` passed.
- **E2E:** UI 변경이 없는 batch/DB story이므로 Playwright E2E는 실행하지 않았다. 운영 DB 계약은 Supabase MCP 실DB fixture로 검증했다.
- **Residual risk:** LS 실계정 API 호출은 외부 credential과 장중 상태에 의존하므로 unit fixture로 계약을 고정했다. Supabase security advisor의 기존 `trading_calendar` RLS 경고 등 story 이전 baseline은 이번 story의 변경 대상이 아니다.
