---
title: 'Story 5.6: 전략별 + 원천별 분리 view'
type: feature
created: '2026-09-10'
status: 'done'
baseline_revision: '1f1f960'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 5-5 승률·PF view는 전체 기준뿐이라 전략(A/B/C)별·원천(t1859/t1852/t1856)별로 분리 조회할 수 없다. 폴백 원천이 지표에 미치는 영향을 구분해 보려는 Neo의 구간이 빠져 있다.

**Approach:** candidate_outcome 행의 source를 **canonical close 발행 후보의 `candidate_source_contrib`만 join하여 결정**(AD-21)하는 versioned SQL view `candidate_outcome_win_rate_pf_by_strategy_source`를 추가한다. 전략 × **primary source** 그룹으로 split하고, primary source는 weight 내림차순 → source 우선순위(t1859>t1852>t1856)로 도출한다. 파티션은 disjoint이고 합이 5-5 전체 view와 정확히 일치한다.

## Boundaries & Constraints

**Always:**
- source 결정은 `candidate_source_contrib`만 join해 수행한다. `candidate_outcome`에 독립 source 컬럼/JSONB 사본을 두지 않는다(AD-21, epics.md:1496).
- primary source = `contribution_weight` 내림차순 → source 우선순위(t1859>t1852>t1856) 규칙(epics.md:1500).
- 승률·PF 산식·분모 규칙은 5-5와 완전 동일: TP/SL/TIMEOUT이 분모, 승패는 return_pct 부호, OPEN/SUSPENDED/DELISTED는 별도 카운트, 반올림 4자리.
- 조인 사슬: candidate_outcome(ticker,strategy,entry_date) → logical_runs(batch_kind='close', trading_day=entry_date, canonical_success_run_id NOT NULL) → candidates(trading_day, attempt_run_id=canonical) → candidate_source_contrib. candidate_tags는 join하지 않는다(전략은 candidate_outcome이 이미 보유, status='vanished' 필터링 방지).
- canonical close 후보가 없는 행(close run/후보 미존재)은 `source NULL` 그룹으로 노출한다(미수집 ≠ 실제 0). GROUP BY가 NULL 그룹을 보존한다.
- migration은 forward-only(AD-14). view는 create or replace, `revoke select on ... from public, anon, authenticated`(browser 차단, 5-5와 동일).
- 동등성: 동일 fixture에서 Python 기준값 ↔ view 결과 ↔ SQL assertion 3중 대조 migration gate(AD-8). 셀 합 = expected_overall(5-5 수치) 교차 검증 포함.
- 운영 Supabase MCP로 migration 적용 + SQL fixture 검증.

**Never:**
- 기존 migration 수정(AD-14 forward-only). backtest 커널·5-5 view 변경 금지.
- `candidate_outcome`에 source 컬럼/JSONB 추가 금지(AD-21).
- UI 변경 없음. browser 역할(anon/authenticated) SELECT 공개 없음.
- parity 도구는 5-5 도구/backtest 커널을 import하지 않는 self-contained 구현(이번 스토리에서 5-5 deferred low 따라간다).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 후보/기여/outcome이 존재 | 전략×source 셀별 승률·PF·카운트가 계산됨 | 없음 |
| STRATEGY_SPLIT | A/B/C 전략이 섞임 | 전략별로 동일 산식이 그룹화되어 반환됨 | 없음 |
| PRIMARY_WEIGHT | 후보에 t1859 0.3 / t1852 0.7 기여 | primary = t1852(weight 내림차순 우선) 셀로 단일 귀속 | 없음 |
| PRIMARY_TIE_PRIORITY | 후보에 t1859 0.5 / t1852 0.5 기여(tie) | primary = t1859(source 우선순위) 셀로 단일 귀속 | 없음 |
| NO_CANONICAL_NULL | canonical close 후보가 없는 outcome | source=NULL 그룹으로 노출(0과 구분) | 없음 |
| PARTITION_OVERALL_PARITY | 스토리 5-5의 동일 9개 outcome | 전체 셀 합 = 5-5 전체(6/3/3/1/1/1, gross 6.4/9.0, win_rate 0.5000, PF 0.7111) | 파티션 재구성 drift 시 gate ERROR |
| PYTHON_EQUALITY | 동일 fixture | Python 기준값 == SQL assertion(셀 단위 + 전체) | 갈라지면 도구 실패 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609101100_create_outcome_win_rate_pf.sql` -- 5-5 view 전체 계약(컬럼명·산식·revoke 패턴). 신규 view는 같은 컬럼 구조를 전략×source로 그룹화.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:5-19,182-209` -- logical_runs(batch_kind='close'만 canonical_success_run_id), publish_attempt가 canonical 설정. 조인 사슬의 첫 단.
- `infra/supabase/migrations/202609011700_create_candidates.sql:5-28` -- candidates + candidate_source_contrib(weight>0, source CHECK 3종, PK(candidate_id, attempt_run_id, source)).
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:32-53` -- candidate_outcome(unique(ticker,strategy,entry_date), FK 없음, status CHECK).
- `infra/supabase/migrations/202609051600_parameterize_outcome_strategy_rules.sql` + `202609051700_harden_outcome_strategy_snapshot_contract.sql` -- snapshot guard: SQL fixture는 전략별 rules 일치 tp_pct/sl_pct/cutoff_n 필요(A/B/C=3.0/3.0/30).
- `tools/check_outcome_win_rate_pf_parity.py` -- 5-5 parity 골격(_setup_region, canonical_4dp, validate_statuses, compare_reference_vs_expected). 신규 도구의 템플릿이되 import 금지.
- `tests/fixtures/outcome_win_rate_pf/input_cases.json` + `tests/sql/test_outcome_win_rate_pf.sql` -- 5-5 fixture 구조(신규는 후보/기여/캐치널/예상 셀을 추가 보유).
- `tests/tools/test_check_outcome_win_rate_pf_parity.py` -- parity 도구 계약 테스트 선례.
- `packages/read-model/src/database.types.ts` (5-5는 line 843) -- 신규 view 타입 반영 대상.
- `.github/workflows/test.yml:178-209` -- sql-schema-tests 잡(신규 parity step 추가).
- `tools/check_migration_order.py`, `tools/check_generated_types_drift.py`, `tools/check_sprint_status.py`, `tools/check_epic_scope.py`, `tools/epic-path-manifests/epic-5.txt`, `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 게이트/매니페스트·상태 파일.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609101200_create_outcome_win_rate_pf_by_strategy_source.sql` -- 신규 migration: view 생성(아래 설계 SQL) + comment on view/column + revoke.
- `tests/fixtures/outcome_win_rate_pf_by_strategy_source/input_cases.json` -- JSON fixture: outcomes(5-5와 동일 9건), candidates(8건), contributors(10건), canonicals(4건), expected_cells(6행), expected_overall(5-5 전체 수치).
- `tests/sql/test_outcome_win_rate_pf_by_strategy_source.sql` -- begin; logical_runs→runs→canonical update→candidates→contrib→outcome 순 INSERT(결정적 UUID), src_expected temp table 6행, do 블록 EXCEPT-diff 대조, rollback.
- `tools/check_outcome_win_rate_pf_source_parity.py` -- self-contained parity 도구: (a) SQL 부문별 INSERT/캐치널 update 파싱, (b) JSON과 대조, (c) JSON으로 Python 기준 셀·전체 계산(primary pick 규칙 복제), (d) SQL src_expected와 4dp/정수/문자열 비교, (e) 셀 합 == expected_overall 교차 검증. drift 시 ERROR.
- `tests/tools/test_check_outcome_win_rate_pf_source_parity.py` -- 계약 테스트: sync pass 고정 + drift 종류별 실패 고정(기여 행 변경, weight 변경, primary 규칙 변경, 캐치널 변경, 예상 셀 변경, outcome 행 변경).
- `.github/workflows/test.yml` -- sql-schema-tests에 parity 도구 실행 step 추가.
- `packages/read-model/src/database.types.ts` -- 운영 적용 후 `npm run generate:read-model-types` 재생성 반영.
- `tools/epic-path-manifests/epic-5.txt` -- 변경 경로 등록.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 5-6 키 done 갱신(최종화 단계).

**Acceptance Criteria:**
- Given 5-5 view가 있는 경우, when 전략(strategy) 파라미터를 추가하면, then A/B/C 각각 및 전체 승률·PF가 조회 가능하다.
- Given source 분리 조회 시, when view를 실행하면, then source는 candidate_source_contrib만 join해 결정되고 candidate_outcome에 독립 source 컬럼/JSONB가 없다(AD-21).
- Given 여러 source가 하나의 candidate에 기여한 경우, when primary source를 도출하면, then weight 내림차순 → source 우선순위(t1859>t1852>t1856) 규칙이 적용된다.
- Given canonical close 후보가 없는 outcome, when 조회하면, then source NULL 그룹으로 노출되어 미수집이 0과 구분된다.
- Given 동일 fixture, when migration gate 테스트를 실행하면, then Python 기준값이 SQL view 셀 결과와 동등하고 셀 합이 전체(5-5)와 일치한다.

## Spec Change Log

- 2026-09-10: `tests/sql/test_outcome_win_rate_pf_by_strategy_source.sql`의 `src_expected` 임시 테이블 컬럼 순서가 실제 view(`...win_rate, gross_win, gross_loss, profit_factor`)와 달리 `...gross_win, gross_loss, win_rate, profit_factor`로 선언돼 있었다. `select *` EXCEPT는 위치 기준 비교이므로 값이 논리적으로 동일해도 매 행이 불일치로 판정됐다(운영 Supabase에 실제 실행해 확인: `view-only=5 expected-only=5`). `src_expected` 컬럼 순서를 view와 일치시키고 `tools/check_outcome_win_rate_pf_source_parity.py`의 `parse_sql_cells` 하드코딩 컬럼 순서도 동일하게 맞춰 재정렬. 수정 후 SQL fixture를 운영 Supabase에서 재실행해 EXCEPT-diff 0건을 확인했다.

## Review Triage Log

### Review Findings (2026-09-10, bmad-code-review: blind-hunter + edge-case-hunter + verification-gap + acceptance-auditor)

- [x] [Review][Patch] `parse_sql_cells`가 `src_expected` 컬럼 순서를 하드코딩된 튜플로 별도 유지해 DDL과 갈라질 수 있었다(이번 세션에서 실제로 한 번 발생) [tools/check_outcome_win_rate_pf_source_parity.py] — `create temp table src_expected (...)` DDL에서 컬럼 순서를 직접 파싱하도록 수정, 재발 구조를 제거함
- [x] [Review][Patch] `compute_reference_cells`가 candidates에 없는 ticker를 참조하는 contributor 행을 조용히 건너뛰어 fixture 오타를 숨길 수 있었다 [tools/check_outcome_win_rate_pf_source_parity.py] — orphan ticker 발견 시 SystemExit로 명시 에러
- [x] [Review][Patch] `_pick_primary_source`의 우선순위 fallback(`-1`)이 SQL view의 `case ... else 2 end`(최하위 랭크)와 불일치 — 현재는 `validate_contributors`가 선행 차단해 도달 불가하지만 표현을 SQL과 일치시킴 [tools/check_outcome_win_rate_pf_source_parity.py]
- [x] [Review][Patch] `expected_overall`에 필수 필드가 빠지면 `verify_overall`에서 처리되지 않은 `KeyError`로 죽던 것을 fixture 로드 시점에 명확한 ERROR로 전환 [tools/check_outcome_win_rate_pf_source_parity.py]
- [x] [Review][Defer] `revoke select ... from public, anon, authenticated`가 실제로 anon/authenticated의 SELECT를 막는지 검증하는 자동 테스트가 없다 [infra/supabase/migrations/202609101200_create_outcome_win_rate_pf_by_strategy_source.sql] — deferred, pre-existing(5-5부터 동일한 gap)
- [x] [Review][Defer] SQL 리터럴 파서(`_extract_value_tuples`/`_split_preserving_quotes`)가 이스케이프된 따옴표(`''`)나 따옴표 안의 괄호를 처리하지 못한다 [tools/check_outcome_win_rate_pf_source_parity.py] — deferred, pre-existing(5-5 도구 템플릿에서 그대로 상속)

**Dismissed:**
- `run`/`cand` lateral에 `LIMIT 1`이 없어 팬아웃 가능성 제기 — `logical_runs.logical_run_key`(PK+shape check)와 `candidates`의 `unique(ticker, trading_day, attempt_run_id)` 제약으로 실제로는 1행 이상 매치가 구조적으로 불가능함을 확인
- `candidate_outcome.entry_date`가 `candidates.trading_day`와 어긋나면 source가 조용히 NULL로 빠진다는 지적 — FK 부재는 AD-21의 의도된 설계이며 spec의 NO_CANONICAL_NULL 시나리오가 이미 이 동작을 정의함
- canonical candidate는 있으나 `candidate_source_contrib` 행이 0개인 경우와 "canonical 자체가 없는" 경우가 같은 NULL 셀로 합쳐진다는 지적 — spec Design Notes가 "최대 1개의 primary source or NULL" 단일 버킷을 명시적으로 설계함
- SQL `case ... else 2 end`의 암묵적 최하위 버킷이 위험하다는 지적 — `candidate_source_contrib.source`에 3개 값만 허용하는 DB CHECK 제약이 있어 도달 불가능한 분기
- view에 `ORDER BY`가 없다는 지적 — 이번 diff에는 소비자가 없고(view 전용 스토리), 동등성 검증은 EXCEPT 기반 집합 비교라 순서 무관
- 이 스토리에 UI 소비 코드가 없다는 지적 — epic-5-context.md의 Cross-Story Dependencies상 원천별 필터 UI는 Story 5.14 소관으로 명시적으로 분리됨
- `verify_overall`이 overall 레벨 ALL_WIN(승만 있고 패 없음) 엣지를 fixture로 exercise하지 않는다는 지적 — 코드를 직접 읽어 `gw_cells > 0 and gl_cells > 0` 가드가 이미 올바르게 NULL 처리함을 확인, 커버리지 공백일 뿐 결함 아님
- `.github/workflows/test.yml`/`packages/read-model/src/database.types.ts`가 `epic-path-manifests/epic-5.txt`에 없다는 지적 — 두 파일 모두 5-1/5-5에서 이미 등록되어 있어 이번 diff가 새로 추가할 필요가 없었음(반증됨)

## Design Notes

### view 계약 (`candidate_outcome_win_rate_pf_by_strategy_source`)

전략×source 셀별로 5-5와 동일한 컬럼(total_settled/wins/losses/open_count/suspended_count/delisted_count/win_rate/gross_win/gross_loss/profit_factor)을 반환한다.

```sql
create or replace view public.candidate_outcome_win_rate_pf_by_strategy_source as
with resolved as (
  select co.strategy, co.status, co.return_pct, src.source
  from public.candidate_outcome co
  left join lateral (
    select lr.canonical_success_run_id, lr.trading_day
    from public.logical_runs lr
    where lr.batch_kind = 'close'
      and lr.trading_day = co.entry_date
      and lr.canonical_success_run_id is not null
  ) run on true
  left join lateral (
    select cl.candidate_id, cl.attempt_run_id
    from public.candidates cl
    where cl.trading_day = run.trading_day
      and cl.ticker = co.ticker
      and cl.attempt_run_id = run.canonical_success_run_id
  ) cand on true
  left join lateral (
    select cs.source
    from public.candidate_source_contrib cs
    where cs.candidate_id = cand.candidate_id
      and cs.attempt_run_id = cand.attempt_run_id
    order by cs.contribution_weight desc,
      case cs.source when 't1859' then 0 when 't1852' then 1 else 2 end
    limit 1
  ) src on true
),
cells as (
  select strategy, source,
    count(*) filter (where status in ('TP','SL','TIMEOUT')) as total_settled,
    count(*) filter (where status in ('TP','SL','TIMEOUT') and return_pct > 0) as wins,
    count(*) filter (where status in ('TP','SL','TIMEOUT') and return_pct < 0) as losses,
    count(*) filter (where status = 'OPEN') as open_count,
    count(*) filter (where status = 'SUSPENDED') as suspended_count,
    count(*) filter (where status = 'DELISTED') as delisted_count,
    round(count(*) filter (where status in ('TP','SL','TIMEOUT') and return_pct > 0)::numeric
      / nullif(count(*) filter (where status in ('TP','SL','TIMEOUT')), 0), 4) as win_rate,
    sum(return_pct) filter (where status in ('TP','SL','TIMEOUT') and return_pct > 0) as gross_win,
    abs(sum(return_pct) filter (where status in ('TP','SL','TIMEOUT') and return_pct < 0)) as gross_loss,
    round(sum(return_pct) filter (where status in ('TP','SL','TIMEOUT') and return_pct > 0)
      / nullif(abs(sum(return_pct) filter (where status in ('TP','SL','TIMEOUT') and return_pct < 0)), 0), 4) as profit_factor
  from resolved
  group by strategy, source
)
select * from cells;
```

- **표준 SQL 주의:** contrib lateral의 `cs.attempt_run_id`는 반드시 **candidate의 attempt_run_id**(= run.canonical_success_run_id)와 같아야 한다. candidate는 unique(candidate_id, attempt_run_id), contrib FK도 (candidate_id, attempt_run_id)이므로 `cand.candidate_id & cand.attempt_run_id` 쌍으로 조인한다(candidate_id만으로 조인하면 FK 위반이자 결과 오염).
- primary pick은 `order by contribution_weight desc, source_priority limit 1`(무거운 가중치 우선, tie면 t1859>t1852>t1856).
- **disjoint 파티션:** 각 outcome은 정확히 한 셀(candidate 결정 후 최대 1개의 primary source or NULL)에 귀속된다. 따라서 셀 합 = 5-5 전체. 전체(=전략 무관)는 5-5 view `candidate_outcome_win_rate_pf`가 이미 제공하므로 신규 view에 ROLLUP을 두지 않는다.
- OPEN/SUSPENDED/DELISTED도 후보 링크가 있으면 source가 귀속된다(전체 셀 계수 포함). canonical 링크가 없으면 source NULL 셀.
- 5-5와 동일하게 `revoke select on table ... from public, anon, authenticated;`.

### migration gate(AD-8, 5-5 구조 확장)

JSON ↔ SQL INSERT ↔ SQL assertion ↔ Python 기준값 4경로를 묶는다(drift 시 ERROR).

1. `input_cases.json` — outcomes(5-5와 동일 9건), candidates(ticker/trading_day/attempt_run_id), contributors(ticker/source/weight), canonicals(trading_day→attempt_run_id), expected_cells(6행), expected_overall(5-5 전체: settled 6/wins 3/losses 3/gross 6.4/9.0/win_rate 0.5000/PF 0.7111).
2. SQL fixture — JSON과 동일한 행을 단계적 INSERT하고 `src_expected`에 6행을 고정한 뒤 EXCEPT-diff 대조(**NULL source·gross 처리는 `is not distinct from`/EXCEPT로 정확 비교**).
3. Python 기준값 — JSON outcomes를 primary pick 규칙으로 셀에 귀속시켜 셀 단위 승률·PF·카운트·gross를 5-5와 동일 산식으로 계산하고, 셀 합이 expected_overall과 같음을 검증한다(파티션 전체 일치).
4. 도구가 SQL의 candidate.attempt_run_id와 canonicals 매핑을 대조해 "후보가 canonical close run에만 연결된다"는 조인 불변식을 Drift 단속한다.

기대 셀(구현 기준값):

```
(A,t1859): settled 2 wins 1 losses 1 open 1 gross 2.9/2.0  win_rate 0.5000  pf 1.4500
(B,t1852): settled 1 wins 0 losses 1 susp 1  gross NULL/3.0 win_rate 0.0000  pf NULL
(B,t1856): settled 1 wins 1 losses 0         gross 2.0/NULL win_rate 1.0000  pf NULL
(C,t1852): settled 1 wins 1 losses 0         gross 1.5/NULL win_rate 1.0000  pf NULL
(C,t1859): settled 1 wins 0 losses 1         gross NULL/4.0 win_rate 0.0000  pf NULL
(C,NULL) : settled 0 counts 0 delisted 1     gross NULL     win_rate NULL   pf NULL
합      : 6/3/3 + open 1 susp 1 delist 1 + gross 6.4/9.0 = 5-5 전체와 일치
```

### SQL fixture 결정적 id 및 순서

```text
logical_runs:  close:2098-05-01..04 (batch_kind 'close', canonical은 update로 설정)
runs:          10000000-0000-0000-0000-000000000001..004 (status published, trigger schedule)
canonical:     update logical_runs set canonical_success_run_id = '<run id>' where logical_run_key = 'close:<날짜>'
candidates:    00000000-0000-0000-0000-000000000001..008 (candidate_id=00..0N, attempt_run_id=해당 날짜의 run)
contributors:  10행 — A0001 t1859 1.0 / A0002 t1852 1.0 / A0003 t1852 0.7+t1859 0.3(→t1852) /
               A0004 t1859 0.5+t1852 0.5(→t1859) / A0005 t1856 1.0 / A0006 t1859 1.0 /
               A0007 t1859 1.0 / A0008 t1852 1.0
outcomes:      5-5와 동일 9건(A0001..A0009). A0009(canonical 링크 없음)는 (C, NULL) 셀.
```

runs INSERT는 (run_id, logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status) 명시(lease_expires_at=now()+interval '1 hour'). FK 순서: logical_runs → runs → candidates → contrib → outcome. snapshot guard는 A/B/C rules(3.0/3.0/30) 일치 값으로 통과. 전부 `rollback`으로 끝난다.

### parity 도구 파싱 계약

- marker `-- ── parity fixture setup` 아래만 파싱. 마커 없으면 SystemExit로 조용한 통과 차단(5-5와 동일).
- 파싱 대상: logical_runs INSERT(인덱스 별도 컬럼 없음, key/trading_day만), canonical update, candidates INSERT, contributors INSERT, candidate_outcome INSERT, `insert into src_expected values` 튜플. candidate_id는 candidates INSERT에서 ticker로 매핑한다.
- 검증: source ∈ {t1859,t1852,t1856}(또는 NULL), weight > 0, outcome당 정확히 1셀 귀속, 셀 6행 == JSON expected_cells, 셀 합 == expected_overall, SQL/JSON candidate·contrib·outcome 행 완전 일치. win_rate/profit_factor는 `canonical_4dp`, gross는 round 4 float, 카운트는 정수 비교.

### read-model 타입 반영

신규 view는 `packages/read-model/src/database.types.ts` Views 섹션에 반영돼야 한다(offline `check_generated_types_drift.py`가 view 이름 존재 요구). 운영에 migration 적용 후 `npm run generate:read-model-types`(SUPABASE_ACCESS_TOKEN, `.env.local`에 존재)로 재생성해 커밋한다.

## Verification

**Commands:**
- `python tools/check_migration_order.py` -- migration timestamp 유일성·순서 통과.
- `python tools/check_outcome_win_rate_pf_source_parity.py` -- JSON↔SQL↔Python 4중 동등 + 셀-전체 교차 검증 통과.
- `uv run --with pytest python -m pytest tests/tools/test_check_outcome_win_rate_pf_source_parity.py -q` -- 도구 계약 테스트 통과.
- `python tools/check_generated_types_drift.py` -- 신규 view가 타입 파일에 존재.
- 운영 Supabase MCP: migration 적용 + `tests/sql/test_outcome_win_rate_pf_by_strategy_source.sql` 실행(rollback) + view 조회.
- `npm run generate:read-model-types` 후 `git diff --exit-code -- packages/read-model/src/database.types.ts` -- 재생성 drift 없음.

**Manual checks (if no CLI):**
- Supabase 대시보드에서 신규 view가 service_role로 조회되고(전략×source 셀 6행), anon/authenticated는 빈 결과 또는 권한 없음이 확인된다.