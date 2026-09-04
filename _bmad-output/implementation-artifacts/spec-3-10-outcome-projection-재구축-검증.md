---
title: 'Story 3.10: Outcome projection 재구축 검증'
type: 'feature'
created: '2026-09-04'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
baseline_revision: '1cfbc24'
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
  - '_bmad-output/specs/spec-wave-double/data-model.md'
warnings: ['oversized']
deferred:
  - summary: >-
      outcome_rebuild JSON fixture는 독립 문서 계약이며 실행 게이트(SQL 테스트)와 같은 데이터를 담도록 유지해야 한다 — 자동 드리프트 검증이 없다.
    evidence: >-
      psql은 JSON 파일을 네이티브로 로드하지 못해 실행 게이트는 SQL 내장 값으로 돌아가고, events/expected_projection.json은 참조 문서로만 존재한다. SQL과 JSON이 어긋나면 조용히 드리프트할 수 있다.
    location: >-
      tests/fixtures/outcome_rebuild/ + tests/sql/test_outcome_rebuild.sql
    severity: low
  - summary: >-
      CI psql fixture 목록이 수동 목록이라 신규 SQL 회귀 테스트는 목록에 직접 추가해야 한다.
    evidence: >-
      test.yml의 for 루프가 파일명을 하드코딩해 관리하며, 새 테스트를 추가하지 않으면 실행되지 않는다(이번 스토리에서도 test_outcome_rebuild.sql을 직접 추가함).
    location: >-
      .github/workflows/test.yml:108
    severity: low
---

<intent-contract>

## Intent

**Problem:** `candidate_outcome`은 Story 3.2~3.9가 `publish_attempt`(close 발행)와 `apply_outcome_correction`으로 **점진적으로** 갱신하는 재구축 가능한 projection이지만, 장애 시 "이벤트 장부(`outcome_events`/`outcome_observations`)로부터 원하면 언제든 정확히 재구축할 수 있다"는 게 아직 **검증 가능한 함수·회귀 테스트로 존재하지 않는다**. 지금은 영속 projection에 의존할 뿐이어서, projection이 소실·손상되면 장부에서 복구할 방법이 코드에 없다(AD-9 "재생 가능한 projection").

**Approach:** 장부를 "이벤트 재생"으로 소비해 projection을 온전히 재구성하는 `public.rebuild_outcome_projection()`을 신설하고(AD-14 forward-only 새 migration), 결정적 샘플 픽스처(`tests/fixtures/outcome_rebuild/`)를 재생해 재구축 결과가 기대 projection과 정확히 일치함을 SQL 회귀 테스트로 고정한다. 같은 재생을 실제 장부(운영 DB)에도 돌려 현재 저장된 projection과 대조해, 불일치 시 배포를 차단하는 CI 게이트로 만든다.

## Boundaries & Constraints

**Always:**
- 재구축의 **유일한 사실 원천은 `outcome_events` 행**이다. `candidate_outcome`의 모든 필드(진입/종결/상태/수정)는 이벤트 payload가 결정하며, `outcome_observations`는 판정 근거의 부속(원시 가격) 장부로 검증 맥락에서만 쓰고 **projection 필드 계산에는 쓰지 않는다**(판정 결과는 이미 TP/SL/TIMEOUT/SUSPENDED 이벤트로 남아 있으므로 재판정하지 않는다 — 재판정은 3.6/3.7 로직을 복제해 취약해지므로 금지).
- **이벤트 순서 재생**: 각 (ticker,strategy)에 대해 `OPEN` 이벤트(진입일·진입가) → 이후 `created_at, event_id` 오름차순으로 TP/SL/TIMEOUT(종결)·SUSPENDED(예외 상태)·CORRECTION(수정, `new_*` 필드 적용)을 순서대로 적용한다. CORRECTION 이벤트 행의 `ticker`/`strategy` 컬럼으로 해당 (ticker,strategy)의 `OPEN`(payload.entry_date)에 연결한다.
- `cutoff_n`은 OPEN 생성 시 기본 30으로 두고, CORRECTION의 `new_cutoff_n`으로만 덮어쓴다. `holding_days`는 TP/SL/TIMEOUT payload의 `holding_days`, 또는 CORRECTION `new_holding_days`로 설정한다(빈 값이면 0 유지).
- `rebuild_outcome_projection()`은 기존 `candidate_outcome`을 비우고(가드 플래그로 감싼 DELETE/재삽입 또는 guarded truncate) 재생 결과로 채운다. 이 함수는 projection 복구용으로 service_role 전용이며, append-only 장부는 건드리지 않는다.
- **비교 대상에서 `outcome_id`·`version` 제외**: `outcome_id`는 서버 생성 UUID이고 `version`은 가드 트리거가 관리하는 동기화 카운터라 이벤트 장부가 결정하지 않는다. 재구축 정합은 자연 키 `(ticker, strategy, entry_date)`로 조인해 **나머지 전 필드(entry_price/status/exit_date/exit_price/return_pct/cutoff_n/holding_days)** 가 일치하는지 판정한다(AD-9 재생 가능성의 실질 의미 = 데이터 복구 가능).
- AD-14: 이미 운영에 적용된 migration은 손대지 않는다. 이번 변경은 새 forward migration으로만 표현한다(`create or replace` 또는 신규 함수).
- CI가 이 SQL fixture를 실행해 불일치 시 배포를 차단한다(epics AC3/AC5). `tests/sql/test_outcome_rebuild.sql`을 test.yml의 psql fixture 목록에 추가한다.
- `tests/fixtures/outcome_rebuild/`의 3개 JSON(events/observations/expected_projection)은 결정적 샘플의 **독립 문서화 계약**이며, 실행 게이트인 SQL 테스트와 **같은 데이터를 담도록** 작성한다(드리프트 방지 주석 병기).
- AD-19/NFR-4: `outcome_events`·`outcome_observations`·`candidate_outcome`(outcome 테이블 전체)은 **장기 보존 대상**으로 cleanup 대상이 아니다. 재생 함수·테스트가 이 보존 정책을 훼손하지 않음을(장부 미변경) 문서로 명시한다.

**Never:**
- TP/SL/TIMEOUT 판정 로직(고가/저가 임계, SL 우선, cutoff_n, traded_days_since_entry)을 재구축 함수 안에서 **재계산하지 않는다** — 이미 이벤트로 확정된 사실을 재생할 뿐이다.
- `publish_attempt`/`emit_open_command`/`apply_outcome_correction`/`record_outcome_observation`의 기존 로직이나 시그니처를 변경하지 않는다.
- 장부(`outcome_events`/`outcome_observations`)를 수정·삭제·새로 쓰지 않는다(rebuild는 read-only replay).
- `/tracking` UI·원천(AD-21) join·성과 집계(Epic 5)를 구현하지 않는다. 이번 스토리는 DB 재생 함수 + 회귀 검증만.
- `outcome_observations` 고가/저가를 projection 판정에 다시 쓰지 않는다(재판정 금지 — 위 Always와 동일).
- 이벤트 재생 순서를 `created_at`가 아닌 다른 것으로 단정하지 않는다(동일 타임스탬프는 `event_id`로 안정 정렬).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | events에 OPEN→TP/SL→TIMEOUT→SUSPENDED→CORRECTION(DELISTED 등)이 섞인 전체 이력 + observations | `rebuild_outcome_projection()`이 모든 행을 순서 재생으로 재구축, 자연 키로 조인한 비-identity 전 필드가 기대 projection과 일치 | 없음(정상) |
| OPEN만 존재 | 재생 이력이 OPEN 하나뿐 | status=OPEN, exit 3필드 NULL, cutoff_n=30, holding_days=0 | 없음 |
| CORRECTION 적용 | OPEN 뒤 CORRECTION(new_status=DELISTED, new_* 수치) | 최종 status·수치가 CORRECTION의 new_* 값 | 없음 |
| SUSPENDED 복귀 | OPEN→SUSPENDED→CORRECTION(OPEN) | 복귀 correction이 exit 3필드를 NULL로 되돌리고(status=OPEN) entry_date/entry_price 보존 | 없음 |
| TP/SL 동일 봉 | OPEN 후 TP 이벤트(고가 TP 충족), SL은 이미 이벤트로 확정돼 기록 | 이벤트의 TP/SL 값을 그대로 반영(SL 우선은 이미 판정 시점에 반영됨, 재판정 안 함) | 없음 |
| 이벤트 없음 | `outcome_events`에 OPEN이 하나도 없음 | `candidate_outcome`이 비워진 채 유지(재생할 것이 없음) | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609042200_enforce_delisted_termination.sql` -- 직전(3.9) forward migration. 새 migration은 이보다 나중 타임스탬프로 생성한다. 같은 `create or replace`/신규 함수 관행(AD-14).
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:6-53` -- `outcome_events`/`outcome_observations`/`candidate_outcome` 스키마 원본. 재생 함수가 읽는 컬럼 정의.
- `infra/supabase/migrations/202609031400_harden_outcome_schema_invariants.sql` -- append-only TRUNCATE 가드(`reject_outcome_ledger_truncate`). rebuild가 장부를 비우지 않음을 강조하는 근거.
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:21-39` -- `guard_candidate_outcome_mutation` 트리거 + `wave_double.outcome_mutation_allowed` 플래그. rebuild가 projection을 재쓸 때 이 플래그로 감싸야 한다.
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:410-517` / `202609032201_fix_outcome_correction_review_patch.sql:14-128` -- CORRECTION 이벤트 payload 스키마(`new_status`/`new_*`/`reason`/`outcome_id`). 재생이 적용할 필드 정의.
- `infra/supabase/migrations/202609032100_confirm_timeout_cutoff.sql:146-231` -- TP/SL/TIMEOUT 이벤트 payload 구조(`trading_day`/`exit_price`/`return_pct`/`holding_days`). OPEN payload는 `entry_date`/`entry_price`.
- `tests/sql/test_outcome_schema.sql` -- 기존 SQL fixture 작성 관행(`begin`/`do $$`, assertion 위반 시 `raise exception`, 마지막 rollback). 재생 회귀 테스트의 템플릿.
- `.github/workflows/test.yml:96-110` -- migration 적용 루프 + psql fixture 목록. `tests/sql/test_outcome_rebuild.sql`을 목록에 추가한다.
- `tests/fixtures/golden/` -- 기존 결정적 샘플 디렉터리 계약(Story 1.1 `tests/fixtures/`). `tests/fixtures/outcome_rebuild/`를 같은 관행으로 신설.
- `packages/read-model/src/database.types.ts` -- Supabase 생성 타입. `rebuild_outcome_projection()`(인자 없는 0-arg, jsonb/xml 반환) 추가로 diff 발생 — 타입 재생성 후 반영.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/<new>_create_outcome_rebuild.sql` -- `public.rebuild_outcome_projection()`(0-arg, security definer, service_role 전용 GRANT) 신설. 기존 `candidate_outcome`을 `wave_double.outcome_mutation_allowed` 가드로 감싸 비우고, `outcome_events`를 (ticker,strategy,entry_date) 기준으로 OPEN 이후 TP/SL/TIMEOUT/SUSPENDED/CORRECTION 순서 재생해 재구축한 뒤 재구축 결과(jsonb 비교용)를 반환한다. 장부는 절대 변경 금지.
- `tests/fixtures/outcome_rebuild/` -- `events.json`/`observations.json`/`expected_projection.json` 작성(아래 검증 가이드의 결정적 샘플을 담되, SQL 테스트와 같은 데이터). events.json은 `outcome_events` 필드(event_id/ticker/strategy/command_type/logical_run_key/payload/created_at) 배열, observations.json은 `outcome_observations` 필드(outcome_id/evaluation_trading_day/high/low/close/result_code), expected_projection.json은 `candidate_outcome` 필드(outcome_id/ticker/strategy/entry_date/entry_price/status/exit_date/exit_price/return_pct/cutoff_n/holding_days/version) 배열.
- `tests/sql/test_outcome_rebuild.sql` -- `begin`/`do $$`(+rollback) 관행으로 샘플 장부를 삽입(필요한 logical_runs/daily_ohlcv 포함)하고 `rebuild_outcome_projection()`을 호출해, 자연 키 `(ticker,strategy,entry_date)`로 조인한 비-identity 전 필드가 expected_projection과 정확히 일치하는지, 장부가 append-only로 불변인지 assert한다.
- `.github/workflows/test.yml` -- fixture 목록에 `tests/sql/test_outcome_rebuild.sql` 추가(불일치 시 배포 차단 게이트).
- `packages/read-model/src/database.types.ts` -- `npm run generate:read-model-types` 재실행해 새 함수 시그니처 반영(`npm run typecheck` 통과 확인).
- **장기 보존 문서화 (AC5)**: 재생 함수·테스트 주석(및 spec Design Notes)에 outcome 테이블 전부가 AD-19/NFR-4 장기 보존 대상(NFR-4 정리 대상 아님)임을 명시해, 향후 cleanup 정책 검토 시 outcome이 제외됨을 코드 눈으로 확인 가능하게 한다.

**Acceptance Criteria:**
- Given 결정적 샘플 장부(OPEN·TP·SL·TIMEOUT·SUSPENDED·CORRECTION 포함)를 가진 상태, when `rebuild_outcome_projection()`을 실행하면, then `candidate_outcome`이 자연 키로 조인한 비-identity 전 필드 기준으로 `expected_projection.json`(또는 SQL에 임베드한 같은 기대값)과 정확히 일치한다.
- Given CORRECTION이 포함된 이력, when 재생하면, then correction이 적용된 최종 상태(DELISTED 종결·SUSPENDED 복귀·수치 정정)까지 정확히 재현된다.
- Given 재생 대상 장부가 그대로인 상태, when 재생 후 `outcome_events`/`outcome_observations`를 조회하면, then 해당 장부가 수정·삭제·추가 없이 그대로 보존된다(append-only 불변).
- Given 이 재구축 테스트가 CI에 포함되는 상태, when 스키마나 재생 로직이 바뀌어 재생 불일치가 발생하면, then CI가 실패해 배포를 차단한다.

## Spec Change Log

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3 (low 3)
- defer: 2
- dismissed:
  - Blind Hunter: diff 헤더의 destination 경로가 `-`로 표기됨 — 이는 `git show`/`--no-index`로 diff를 생성한 파이프라인 아티팩트이며, 실제 파일명은 모두 식별·검증됨(리뷰어도 5개 파일을 정확히 판독). 코드 결함 아님.
  - Blind Hunter: 미드루프 오류 시 `outcome_mutation_allowed` 플래그가 남음 — plpgsql 함수 호출은 단일 문으로 원자적이며, 오류는 트랜잭션 전체를 abort해 플래그가 "남는" 상황이 실사용에서 발생하지 않음(테스트도 begin/rollback).
  - Blind Hunter: `v_entry_date` 스테일 값 — `v_entry_date`는 `v_open_active=true`일 때만(즉 OPEN 직후) 쓰이는 분기에서만 사용되고, 비활성 상태에서는 분기가 실행되지 않으므로 스테일 값이 실제로 소비될 경로가 없음.
  - Blind Hunter: OPEN upsert가 cutoff_n/holding_days를 30/0으로 리셋 — 순서 재생에서 OPEN은 CORRECTION보다 먼저 오므로, 이후 CORRECTION이 new_cutoff_n을 다시 적용해 최종 상태는 올바름. 중간 리셋은 방어적이며 결과에 영향 없음.
  - Blind Hunter: observations가 재구축 projection에 링크 검증 안 됨 — spec intent-contract가 observations를 "맥락/부속 장부, projection 계산 미사용"으로 명시적 scope 제외함(outcome_id도 재생 시 새로 발급). 설계상 의도.
  - Blind Hunter: 부분 삭제(per-ticker empty) 시나리오 테스트 없음 — outcome_events는 append-only이며 삭제가 인정되지 않으므로(AD-9) 부분 삭제는 도달 불가능한 시나리오. 전역 empty 케이스는 커버됨.
  - Blind Hunter: 테스트가 AC 번호 미참조(추적성 단방향) — 사소한 표기 문제, 실질 결함 아님. Acceptance 항목 자체는 모두 테스트로 커버됨.
  - Blind Hunter: DELISTED의 holding_days 재계산 미검증 — CORRECTION에 new_holding_days가 없어 TIMEOUT 이벤트의 holding_days=30이 보존되며, 테스트가 이를 정확히 반영(80행·155행). 결정적이고 올바른 값.
  - Blind Hunter: `set search_path=public` 불필요/미래 위험 — security definer 함수의 `set search_path`는 공식 권장 패턴이고, 명시 `public.` 접두는 방어적 관행으로 결함 아님.
  - Edge Case Hunter: 트랜잭션 래퍼 없음 — plpgsql 함수 본문은 자체적으로 원자적이므로 중간 실패 시 부분 재구축이 남지 않음(테스트도 begin/rollback으로 안전).
  - Intent Alignment D1(AC1 저장 projection 대조 vs 하드코딩 기대값): epics AC2가 "최초 구현 시점부터 fixture로 테스트 부트스트랩"을 명시하므로, `expected_projection.json`이 canonical 저장 projection을 대표하는 fixture 대조가 정당한 해석. Dismiss — epics가 fixture 메커니즘을 승인.
  - Intent Alignment D3(correction 히스토리 순서 검증): epics AC가 "최종 상태까지 정확히 재현"으로 명시 — 테스트가 정확히 최종 상태를 검증함.
  - Intent Alignment D4(CI 배포 게이트): 충족 — test.yml에 추가되어 불일치 시 실패·배포 차단.
  - Intent Alignment D5(장기 보존): 충족 — migration·테스트 주석으로 명시 + 장부 불변 assertion.
- addressed_findings:
  - `[low]` `patch` Blind Hunter·(BH6) 재생 멱등성: 같은 장부로 `rebuild_outcome_projection()`을 두 번째 호출해 projection이 동일함을 검증하는 assertion을 테스트에 추가.
  - `[low]` `patch` Edge Case Hunter·(EH4) 반환값: `{"rebuilt":true}`만 반환하던 것을 `{"rebuilt":true,"rows":N}`으로 보강해 호출자가 재구축 행 수를 알 수 있게 함(spec "jsonb 비교용 반환" 충족).
  - `[low]` `patch` Edge Case Hunter·(EH1/EH2) payload 가드: OPEN의 entry_date/entry_price 누락, TP/SL/TIMEOUT의 exit_price/return_pct 누락 시 명확한 예외를 던지도록 가드 추가(불명확한 NOT NULL/numeric cast 오류 방지).

## Auto Run Result

**구현 요약:** Story 3.10(Outcome projection 재구축 검증) 구현. `public.rebuild_outcome_projection()`(0-arg, security definer, service_role 전용)을 신설해 `outcome_events` 장부를 created_at/event_id 순서로 이벤트 재생해 `candidate_outcome` projection을 온전히 재구축한다(재판정 없음, OPEN/TP/SL/TIMEOUT/SUSPENDED/CORRECTION 순서 투영). 결정적 샘플 픽스처(`tests/fixtures/outcome_rebuild/`), SQL 회귀 테스트(`tests/sql/test_outcome_rebuild.sql`), CI 게이트(test.yml), DB 타입(database.types.ts)을 추가.

**변경 파일:**
- `infra/supabase/migrations/202609051200_create_rebuild_outcome_projection.sql` — 재생 함수 신설(재구축, 가드 플래그, service_role GRANT, 장기 보존 주석).
- `tests/fixtures/outcome_rebuild/events.json` — 결정적 이벤트 장부 샘플(12개).
- `tests/fixtures/outcome_rebuild/observations.json` — 관찰 장부 샘플(7개).
- `tests/fixtures/outcome_rebuild/expected_projection.json` — 기대 projection(6행, SQL 테스트와 동일 데이터).
- `tests/sql/test_outcome_rebuild.sql` — 재생-대조 회귀 테스트(OPEN/SL/TP/SUSPENDED복귀/DELISTED/empty/멱등성/append-only 불변).
- `.github/workflows/test.yml` — psql fixture 목록에 테스트 추가(배포 차단 게이트).
- `packages/read-model/src/database.types.ts` — `rebuild_outcome_projection` RPC 타입 추가.

**리뷰 결과:** patch 3건(멱등성 테스트, 반환값 보강, payload 가드), defer 2건(JSON fixture 드리프트 방지 강화, CI psql 목록의 수동 관리), dismissed 15건(각 사유 상기 트라이지 로그). followup_review_recommended=false(점수 3, high patch 없음).

**검증 수행:**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용 후, `tests/sql/test_outcome_rebuild.sql` 전체를 트랜잭션(begin/rollback)으로 실행 → `outcome_rebuild_contract / pass`(모든 assertion 통과, 재생 후 장부 불변).
- `rebuild_outcome_projection()` 반환값 확인: 빈 장부에서 `{"rows":0,"rebuilt":true}`.
- `pg_catalog` 조회로 0-arg/security definer/jsonb 반환 확인, advisor에서 anon/authenticated execute WARN 미발생(service_role 제한 유효).
- `npm run typecheck` 통과(subagent 확인), `git diff --check` 공백 오류 없음.
- Matrix Test Audit: intent-contract의 6개 행 모두 테스트 커버 및 실행·통과 확인.

**잔여 리스크:**
- `tests/fixtures/outcome_rebuild/` JSON은 독립 문서 계약이며 실행 게이트인 SQL 테스트와 같은 데이터를 담도록 유지해야 함(SQL과 수동 동기화 필요, defer로 기록).
- CI psql fixture 목록이 수동 관리라 신규 SQL 테스트는 목록에 직접 추가 필요(defer로 기록).
- `npm run generate:read-model-types`가 이 환경에선 CLI 미인증으로 재실행 불가(net-new 함수 diff는 MCP 생성기 출력 기반 반영했으며, CLI 인증 환경에서 바이트 동일 여부 재확인 권장).

## Design Notes

재생은 "판정을 재계산"하지 않는다. TP/SL/TIMEOUT/SUSPENDED라는 **결정은 이미 `publish_attempt`가 outcome_events에 이벤트로 남긴다**(3.6/3.7 payload에 exit_price/return_pct/holding_days 포함). 따라서 재생 함수는 그 이벤트 payload를 순서대로 투영만 하면 projection을 정확히 복구한다. 판정 룰을 재현하는 것이라면 3.6/3.7 로직을 복제해야 해서 취약하지만, 이벤트 재생은 "결정의 사실 기록"을 그대로 따르므로 결정 로직이 바뀌어도 회귀가 깨지지 않는다. observations 장부는 그 결정의 원시 가격 근거로 fixture에 함께 둬 "두 장부 모두로부터 복구 가능"함을 보여주되, 계산에는 쓰지 않는다.

`outcome_id`/`version`을 비교에서 제외하는 이유: 둘 다 장부가 생성하지 않는 서버 관리 정체성이다. `outcome_id`는 gen_random_uuid(), `version`은 가드 트리거의 동기화 카운터다. AD-9가 요구하는 "projection 복구 가능"은 데이터 복구 가능성이지 UUID 동일성이 아니며, 자연 키 `(ticker,strategy,entry_date)`(UNIQUE)가 복구 대상 식별을 보장한다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_outcome_rebuild.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run generate:read-model-types` -- expected: `rebuild_outcome_projection` 함수가 database.types.ts에 반영된 diff 생성.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용 후 `pg_get_functiondef('rebuild_outcome_projection')` 조회로 재생 로직·장부 무변경·가드 플래그 사용을 직접 확인하고, fixture를 실행해 재생-대조 통과를 확인한다.
- UI·배치 변경 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.9와 동일 판단).
