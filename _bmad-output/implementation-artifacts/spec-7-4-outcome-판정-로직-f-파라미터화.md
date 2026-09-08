---
title: 'Outcome 판정 로직 F 파라미터화 (Epic 3/6 확장)'
type: 'feature'
created: '2026-09-08'
baseline_revision: '9dfdce7e7de1e64b58128338e0ff7bd7bd207d9d'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      No SQL fixture exercises the OUTCOME_STRATEGY_RULE_NOT_FOUND branch in emit_open_command
      or guard_outcome_strategy_snapshot for any strategy letter.
    evidence: |-
      verification-gap review searched tests/sql/ for "RULE_NOT_FOUND" repo-wide and found no
      matches; the branch exists unguarded in both functions since the D/E-era migrations
      (predates Story 7.4) and this story's migration copies it verbatim for F without adding
      coverage, since it isn't new behavior introduced by this change.
    location: >-
      infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql:199,321
    severity: low
---

<intent-contract>

## Intent

**Problem:** `outcome_strategy_rules`/`emit_open_command`/관련 CHECK 제약이 A/B/C/D/E만 지원해, Story 7.2/7.3에서 태깅·계산 가능해진 전략 F의 outcome 판정(TP/SL/최대보유)이 아직 동작하지 않는다(`OUTCOME_STRATEGY_RULE_NOT_FOUND`/`INVALID_STRATEGY`로 막힘).

**Approach:** Story 6.5(D/E 파라미터화)와 동일한 forward-only 패턴으로 `outcome_strategy_rules`에 F 행(`tp_pct=3, sl_pct=4, cutoff_n=999999` sentinel)을 추가하고, `emit_open_command`의 허용 전략 목록·`outcome_events`/`candidate_outcome`의 strategy CHECK·`guard_outcome_strategy_snapshot`의 cutoff 비교 목록을 F까지 확장한다. `publish_attempt`/`rebuild_outcome_projection`은 이미 전략-비의존적이라 변경하지 않는다.

## Boundaries & Constraints

**Always:** 기존 마이그레이션은 수정하지 않고 새 forward-only migration만 추가한다(AD-14). A/B/C/D/E의 기존 rule 행·저장된 `candidate_outcome`/`outcome_events` 값은 그대로 보존한다(NFR-5, 재계산·재판정 없음). `cutoff_n`은 NOT NULL 제약(`> 0`)을 그대로 두고 "무제한"을 sentinel `999999`로 표현한다(스키마 변경 금지). `publish_attempt`의 `v_traded_days >= cutoff_n` 비교 로직은 그대로 재사용한다.

**Never:** `candidate_outcome.cutoff_n`/`outcome_strategy_rules.cutoff_n`의 NOT NULL 제약을 완화하거나 NULL 허용으로 바꾸지 않는다. `emit_open_command`/`publish_attempt`/`rebuild_outcome_projection`의 A-E 판정 로직·TP 우선순위·비용 반영 방식을 바꾸지 않는다. 태깅 stage 연동(Story 7.5), UI(Story 7.6)는 이 스토리 범위가 아니다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| F_OPEN_HAPPY_PATH | close 배치, F 태그된 종목의 `emit_open_command(..., 'F')` | OPEN 성공, `tp_pct=3, sl_pct=4, cutoff_n=999999`가 event payload와 candidate_outcome에 스냅샷 | 없음 |
| F_REPLAY | 동일 (logical_run_key, ticker, F) 재호출, rule 행 일시 삭제 상태 | 저장된 snapshot을 rule lookup 없이 그대로 반환(D/E와 동일 패턴) | 없음 |
| F_TIMEOUT_NEVER_FIRES | F 포지션이 현실적 보유일수 범위 내(`v_traded_days < 999999`) | TIMEOUT 미발동, TP/SL 도달까지 계속 추적 | 없음 |
| F_SNAPSHOT_MISMATCH | 직접 INSERT/UPDATE로 F 행의 tp_pct/sl_pct/cutoff_n이 rule 테이블과 불일치 | `guard_outcome_strategy_snapshot` 트리거가 차단 | `OUTCOME_STRATEGY_SNAPSHOT_MISMATCH` |
| LEGACY_ABCDE_UNCHANGED | 기존 A-E `outcome_strategy_rules`/`candidate_outcome` 행 | migration 적용 후에도 값 그대로, 재판정 없음 | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql` (신규) -- Story 6.5(`202609051600_...sql`)·Story 7.2(`202609071000_expand_candidate_tags_strategy_check_f.sql`)와 동일한 사전조건 검증 → drop/add constraint → comment 갱신 패턴. 다음을 forward-only로 수행:
  1. `outcome_strategy_rules_strategy_check`(테이블 생성 시 인라인 check, 이름은 `pg_constraint`에서 확인 후 drop/add)를 `('A','B','C','D','E','F')`로 확장.
  2. `insert into outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n) values ('F', 3.0, 4.0, 999999) on conflict (strategy) do nothing;`
  3. `outcome_events_strategy_check`/`candidate_outcome_strategy_check`(`infra/supabase/migrations/202609051600_parameterize_outcome_strategy_rules.sql:56-61`에서 마지막 정의)를 drop/add로 `('A','B','C','D','E','F')` 확장.
  4. `emit_open_command`를 `create or replace`하되 `infra/supabase/migrations/202609052000_harden_outcome_strategy_snapshot_contract.sql:75-266`의 최신 본문을 그대로 복사하고 `p_strategy not in ('A','B','C','D','E')` 한 줄만 `('A','B','C','D','E','F')`로 변경.
  5. `guard_outcome_strategy_snapshot`을 `create or replace`하되 `infra/supabase/migrations/202609052100_preserve_legacy_outcome_snapshot_compatibility.sql:6-47`의 최신 본문을 그대로 복사하고 두 곳만 변경: `new.strategy not in ('A','B','C','D','E')` → `('A','B','C','D','E','F')`, `new.strategy in ('D','E')`(cutoff_n 비교 조건) → `('D','E','F')`.
  6. `revoke/grant execute`는 기존과 동일 유지(`emit_open_command`/`guard_outcome_strategy_snapshot`은 `service_role`만).
  7. `comment on function ...`으로 이 migration의 변경 범위(F 추가)를 기록.
- `tests/sql/test_outcome_schema.sql:63-71` -- `outcome_strategy_rules` 카운트를 5→6, F 행(`3.0, 4.0, 999999`) 값 단언 추가.
- `tests/sql/test_outcome_open_command.sql:20-38,68-101,167-175` -- fixture에 `ZZTEST9` daily_ohlcv 행 추가, D/E와 동일한 패턴으로 F의 최초 OPEN(파라미터 스냅샷 확인)·replay(rule 행 삭제 후 저장된 snapshot 반환) 테스트 추가. 172행 "미지원 전략" 테스트가 현재 `'F'`를 미지원 예시로 쓰고 있으므로, F가 지원되면서 이 테스트는 실제 미지원 코드(예: `'G'` 또는 `'X'`)로 교체해야 한다.
- `.github/workflows/test.yml:111` -- 이미 `test_outcome_schema.sql`/`test_outcome_open_command.sql`을 실행 목록에 포함하므로 CI 목록 변경 불필요(신규 migration도 `db reset` 경로로 자동 적용됨, 확인만).

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql` -- 위 Code Map 1~7 항목 구현 -- F의 outcome 판정 파라미터(TP3%/SL4%/무제한 보유)를 forward-only로 활성화한다.
- `tests/sql/test_outcome_schema.sql` -- F 행 카운트·값 단언 추가 -- rule 테이블 확장을 고정 회귀로 증명한다.
- `tests/sql/test_outcome_open_command.sql` -- F OPEN/replay 시나리오 추가, "미지원 전략" 테스트를 실제 미정의 코드로 교체 -- `emit_open_command`가 F를 정확히 지원하고 여전히 진짜 미정의 전략은 거부함을 증명한다.

**Acceptance Criteria:**
- Given `outcome_strategy_rules`가 A-E 5행인 경우, when 이 migration을 적용하면, then F 행(`tp_pct=3, sl_pct=4, cutoff_n=999999`)이 추가되고 기존 5행은 값이 그대로 유지된다.
- Given F 태그된 후보의 `emit_open_command(..., 'F')` 호출인 경우, when close 배치가 실행되면, then `candidate_outcome`/`outcome_events` OPEN payload에 F의 tp_pct/sl_pct/cutoff_n이 스냅샷되고 `INVALID_STRATEGY`가 발생하지 않는다.
- Given F가 sentinel `cutoff_n=999999`를 쓰는 경우, when `publish_attempt`가 `v_traded_days >= cutoff_n`을 평가하면, then 현실적 보유 기간 범위에서 TIMEOUT이 발동하지 않고 TP/SL 도달까지 계속 추적된다(코드 변경 없이 기존 비교 로직 재사용으로 검증).
- Given 기존 A/B/C/D/E `candidate_outcome`/`outcome_events` 행이 있는 경우, when 이 migration을 적용하면, then 기존 행의 값이 그대로 유지되고 재계산·재판정되지 않는다.
- Given 진짜 미정의 전략 코드(F 지원 이후의 예: `'G'`)인 경우, when `emit_open_command`를 호출하면, then 여전히 `INVALID_STRATEGY`로 거부된다.

## Design Notes

`rebuild_outcome_projection()`은 전략별 분기 없이 payload의 3개 rule 키(tp_pct/sl_pct/cutoff_n)가 모두 있으면 그대로 투영하고, 없으면 A/B/C에만 legacy 3/3/30 fallback을 적용하며 그 외(D/E/F 포함)는 `REBUILD: OPEN payload missing strategy rules` 오류로 fail-closed한다(`202609052000_harden_outcome_strategy_snapshot_contract.sql:339-349`) — F 추가에 코드 변경이 필요 없고 기존 동작이 이미 올바르다. `publish_attempt`도 `candidate_outcome`에 저장된 tp_pct/sl_pct/cutoff_n 값을 그대로 조회해 비교하므로(`202609070900_supply_3day_publish_guard.sql`) strategy 목록을 하드코딩하지 않아 변경이 필요 없다.

## Verification

**Commands:**
- `supabase db reset` (로컬) -- expected: 전체 migration이 순서대로 깨끗하게 적용됨(N/N-1 호환성 포함).
- `for f in tests/sql/test_outcome_schema.sql tests/sql/test_outcome_open_command.sql tests/sql/test_outcome_rebuild.sql; do psql ... -f "$f"; done` -- expected: 전부 통과, F 관련 신규 단언 포함.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- 없음(전부 CLI/SQL fixture로 검증 가능; UI 표면 없음).

## Review Triage Log

### 2026-09-08 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4-layer 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 2: (high 0, medium 0, low 2)
- defer: 1
- dismissed:
  - (blind-hunter) `rebuild_outcome_projection`에 F 전용 OPEN/TP/SL 회귀 테스트가 없다는 지적 — 해당 함수는 `strategy in ('A','B','C')` 분기 외에는 전략에 무관하게 payload의 3개 rule 키(tp_pct/sl_pct/cutoff_n) 존재 여부로만 분기하며, D/E 테스트가 이미 F와 동일한 "else(non-ABC)" 분기 동작을 실증한다. F만의 고유 동작이 없어 별도 테스트가 실효가 없다.
  - (blind-hunter) sentinel `cutoff_n=999999`의 "무제한 보유" 의미론을 `publish_attempt` 대상 실행 테스트로 검증하지 않았다는 지적 — verification-gap 리뷰가 `publish_attempt`의 `v_traded_days >= tpsl_row.cutoff_n`(202609070900_supply_3day_publish_guard.sql:165) 비교가 완전히 데이터 기반이며 전략 목록을 하드코딩하지 않음을 직접 확인했다. 코드 변경이 없는 기존 로직 재사용이므로 이 스토리에서 새 실행 테스트가 필요하지 않다.
  - (blind-hunter) `999999`가 매직 넘버이고 오버플로 검토가 없다는 지적 — `cutoff_n`은 Postgres `integer`(최대 약 21억)이고 비교 대상 `v_traded_days`는 실제 거래일 카운트이므로 999999에 근접할 수 없다. 산술 연산(덧셈/곱셈) 없이 단순 비교(`>=`)만 사용해 오버플로 경로 자체가 없다.
  - (blind-hunter) `ALTER TABLE ... DROP/ADD CONSTRAINT`의 락/운영 영향 언급이 없다는 지적 — 이 migration 작성·적용 시점 기준 production `outcome_strategy_rules`/`outcome_events`/`candidate_outcome`에 실거래 데이터가 없음을 직접 조회로 확인했다(테스트 fixture만 존재, 전부 rollback으로 제거됨). 락/스캔 비용은 무시할 수준이며, 이는 Story 7.2의 동일 패턴 migration이 이미 채택한 판단이다.
  - (blind-hunter) 비-SQL 레이어(edge function/TS 타입/프론트엔드)가 A-E만 별도로 하드코딩해 F를 조용히 거부할 수 있다는 지적 — verification-gap이 `apps/web`, `apps/batch`, `packages/read-model/src/database.types.ts` 전체를 검색해 `strategy` 관련 하드코딩된 리스트가 없음을 확인했다(`database.types.ts`는 `string` 타입, `apps/batch/scheduler.py`는 `candidate_tags`에서 전략 집합을 동적으로 도출). 근거 반박됨.
  - (blind-hunter) migration 재실행 시 부분 적용 상태에서의 복구 절차 안내가 없다는 지적 — 이 프로젝트의 기존 forward-only migration 전체(예: 202609071000 등)에 이런 운영 노트가 없는 것이 확립된 관례이며, 이 스토리가 새로 도입한 격차가 아니다.
  - (blind-hunter) 테스트 파일에서 D replay 이후 rule 행 재삽입(`insert ... values ('D', ...)`)에 `on conflict`가 없어 스타일이 일관되지 않다는 지적 — 지적한 F replay 재삽입 코드는 바로 다음에 나오는 기존 D replay 재삽입 코드와 동일한 패턴(둘 다 `on conflict` 없음)이며, 각 테스트는 격리된 rollback 트랜잭션 내에서만 실행되어 재진입 위험이 없다. 새로 도입한 불일치가 아니다.
  - (blind-hunter) migration 주석이 정확한 파일명·줄 번호를 인용해 추후 stale해질 수 있다는 지적 — 이 저장소의 기존 migration·스펙 전반(예: 이 스펙 자체의 Code Map)이 동일하게 정확한 줄 번호를 인용하는 확립된 관례이며, 순수 주석이라 실행 동작에 영향이 없다.
  - (blind-hunter) `outcome_strategy_rules` 테이블 코멘트의 `publish_attempt` 비교 연산자(`>=`) 언급이 미검증 주장이라는 지적 — verification-gap이 `202609070900_supply_3day_publish_guard.sql:165`에서 정확히 `v_traded_days >= tpsl_row.cutoff_n`임을 직접 확인했다. 주장이 사실로 검증됨, 반박 아님.
  - (intent-alignment) "필요하면 e2e 테스트" 조항이 실제 존재하는 e2e 스위트(`e2e/home.spec.ts` 등) 내용을 확인하지 않고 스펙이 "UI 표면 없음"으로 자체 면제했다는 지적 — `e2e/` 디렉터리 전체를 `outcome|strategy|candidate_outcome` 키워드로 검색한 결과 매치되는 파일이 0건이었다. 스펙의 면제 판단이 실제 스위트 내용으로 사후 확인되어 근거가 성립한다.
  - (intent-alignment) sprint-status.yaml이 아직 backlog이고 커밋이 없으며 `review_loop_iteration: 0`이라는 관찰 — 사용자 지시 순서(개발→검수/보완→e2e 필요성 판단→스프린트 동기화→커밋)상 이 리뷰 패스 자체가 "검수" 단계이고 스프린트 동기화·커밋은 이 패스 완료 이후 순서이므로 예상된 상태다(결함 아님).
  - (verification-gap, Other findings) `apps/web/lib/strategy-labels.ts`가 F 라벨을 아직 매핑하지 않아 `getStrategyLabel("F")`가 `undefined`를 반환한다는 관찰 — epics.md가 UI 라벨/배지 확장을 명시적으로 Story 7.6 범위로 분리했고, 현재 컴포넌트들은 이미 `전략 ${s}` 제네릭 폴백으로 안전하게 처리한다(깨지지 않음). 이 스토리(7.4)는 DB의 outcome 판정 파라미터화만 다루며 UI 표면이 없다.
- addressed_findings:
  - `[low]` `[patch]` (blind-hunter + edge-case-hunter, 동일 근본원인) F rule 행 삽입이 `on conflict (strategy) do nothing`이라 이미 다른 값의 F 행이 존재하면 조용히 유지되어 3.0/4.0/999999 계약이 깨질 수 있음 — insert 직전에 기존 F 행이 있다면 값이 정확히 일치하는지 검증하는 사전조건 `do $$ ... raise exception` 블록을 추가했다. production에 단독 실행해 현재 F 행(3.0/4.0/999999)이 이 사전조건을 통과함을 확인했다.
  - `[low]` `[patch]` (blind-hunter) F의 `OUTCOME_STRATEGY_SNAPSHOT_MISMATCH` 트리거 확장(`guard_outcome_strategy_snapshot`의 cutoff_n 비교 목록이 D/E에서 D/E/F로 확장됨)이 `emit_open_command` 경로로만 간접 검증되고 직접 INSERT 위반 테스트가 없었음 — `tests/sql/test_outcome_schema.sql`에 D의 기존 직접 INSERT 위반 테스트와 동일한 패턴으로 F(`tp_pct=3, sl_pct=4, cutoff_n=1`, rule 행과 cutoff_n 불일치)의 `OUTCOME_STRATEGY_SNAPSHOT_MISMATCH` 테스트를 추가했다. production에서 재실행해 통과를 확인했다.

## Auto Run Result

Summary: `outcome_strategy_rules`/`emit_open_command`/`guard_outcome_strategy_snapshot`/`outcome_events`·`candidate_outcome`의 strategy CHECK가 A/B/C/D/E만 지원해 Story 7.2/7.3에서 태깅·계산까지 가능해진 전략 F의 outcome 판정(TP/SL/최대보유)이 아직 동작하지 않던 것을, Story 6.5(D/E 파라미터화)와 동일한 forward-only 패턴으로 F 행(`tp_pct=3, sl_pct=4, cutoff_n=999999` sentinel)을 추가하고 관련 CHECK·허용 전략 목록·snapshot 비교 목록을 F까지 확장해 해결했다. `publish_attempt`/`rebuild_outcome_projection`은 이미 전략-비의존적이라 코드 변경 없이 그대로 재사용된다.

Files changed:
- `infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql` — 신규 forward-only migration. `outcome_strategy_rules_strategy_check`/`outcome_events_strategy_check`/`candidate_outcome_strategy_check`를 A-F로 확장, F 규칙 행(3.0/4.0/999999) 삽입(리뷰 패치로 사전조건 검증 추가), `emit_open_command`/`guard_outcome_strategy_snapshot`을 F 포함하도록 `create or replace`.
- `tests/sql/test_outcome_schema.sql` — `outcome_strategy_rules` 카운트 5→6·F 값 단언 추가, 리뷰 패치로 F strategy snapshot cutoff_n 불일치 직접 INSERT 테스트 추가.
- `tests/sql/test_outcome_open_command.sql` — F의 최초 OPEN(파라미터 스냅샷)·replay(rule 행 삭제 후 저장된 snapshot 반환) 테스트 추가, "미지원 전략" 테스트를 `'F'`(이제 유효)에서 `'G'`로 교체.
- `tests/sql/test_outcome_rebuild.sql` — F와 무관한 기존 결함 수정: 100014/100015 fixture의 OPEN/TP·OPEN/SL 이벤트가 동일 트랜잭션 내 동일 `now()` 타임스탬프를 공유해 재생 순서가 무작위 UUID 비교에 의존하던 비결정성을 명시적 `created_at` 지정으로 고정.
- `_bmad-output/implementation-artifacts/spec-7-4-outcome-판정-로직-f-파라미터화.md` — 신규 스펙 문서(본 파일).

Review findings breakdown (2026-09-08, 4계층 정식 리뷰 패스): patch 2건(low 2) 모두 수정 — F rule 행의 `on conflict do nothing` 사전조건 부재, F strategy snapshot cutoff_n 불일치 직접 INSERT 테스트 부재. defer 1건(low, `OUTCOME_STRATEGY_RULE_NOT_FOUND` 미검증 — D/E 시절부터 존재하던 사전 결함, 이 스토리가 새로 도입하지 않음). dismissed 11건은 위 Review Triage Log에 각각 근거와 함께 기록(rebuild/publish_attempt 관련 지적은 코드가 이미 전략-비의존적임을 직접 확인, 매직넘버·락 우려는 실측(정수 오버플로 불가능·production 테이블 비어있음)으로 반박, 비-SQL 레이어 하드코딩 우려는 전체 검색으로 반박, 스타일·주석·프로세스 순서 관련 지적은 기존 관례와 일치하거나 이 리뷰 패스 이후 순서라 예상된 상태, e2e 면제는 실제 스위트 0건 매치로 사후 확인, UI 라벨 부재는 Story 7.6 범위로 명시적으로 분리됨).

Follow-up review recommendation: false (patched low 2; score 1×2 = 2 < 5, no high severity).

Verification: production Supabase(qqhjeumlecaudsiqhhdu)에 migration을 직접 적용(로컬 CLI/Docker 미가용, [[feedback_supabase_prod_policy]] 정책에 따라 직접 적용) 후 `tests/sql/test_outcome_schema.sql`(리뷰 패치 반영 버전 포함) `tests/sql/test_outcome_open_command.sql` `tests/sql/test_outcome_rebuild.sql`(non-F 결함 수정 반영 버전 포함) 3개 fixture를 각각 전체 실행 — 모두 pass(각 fixture는 `begin;...rollback;`으로 감싸여 있어 production에 흔적을 남기지 않음). `git diff --check` — 공백 오류 없음(LF/CRLF 경고만 존재, 실제 diff 이슈 아님; 스펙 파일 말미의 빈 줄 하나는 트리밍). F rule 행 사전조건 블록은 production에 단독 실행해 현재 F 행(3.0/4.0/999999)이 통과함을 별도 확인했다. e2e/브라우저 테스트는 이 스토리 범위(순수 DB migration·SQL fixture, UI/edge function/프론트엔드 표면 없음, `e2e/` 전체 검색으로 관련 스펙 0건 확인)에 해당하지 않아 적용하지 않았다.

Residual risks: `OUTCOME_STRATEGY_RULE_NOT_FOUND` 예외 경로는 A-F 어떤 전략으로도 SQL fixture에서 검증되지 않는다(D/E 시절부터 존재하던 사전 결함, deferred 항목으로 기록). UI 라벨/배지(`apps/web/lib/strategy-labels.ts`의 F 미매핑)는 Story 7.6 범위로 이미 추적되며 현재도 제네릭 폴백으로 안전하게 동작한다. 태깅 stage 연동(Story 7.5)은 이 스토리 완료 전제 조건이었으며 이제 완료되어 후속 스토리가 F outcome 판정을 사용할 수 있다.
