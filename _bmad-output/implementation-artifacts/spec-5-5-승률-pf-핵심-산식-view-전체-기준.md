---
title: 'Story 5.5: 승률·PF 핵심 산식 view(전체 기준)'
type: feature
created: '2026-09-10'
status: 'done'
baseline_revision: 'c815f8b'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: []
deferred:
  - type: 'followup'
    severity: 'low'
    finding: "database.types.ts 재생성 과정에서 스토리 5-4의 append_bias_event/get_bias_population을 포함한 운영 스키마 전체가 반영됐다 — HEAD에는 5-4가 타입 재생성을 안 해서 이전까지 빠져 있던 것이고, story 5-5 변경의 문제는 아니다. 진실한 재생성 결과이므로 그대로 두며, 후속 스토리에서 재생성 절차를 일관화한다."
  - type: 'followup'
    severity: 'low'
    finding: "parity 도구가 backtest 커널(metrics.py)을 import하지 않고 인라인 동일 산식으로 reference를 계산한다 — spec intent가 문법적으로 'metrics와 동일 산식'을 통해 양자 동등성을 증명하는 설계이고, 커널 import는 중의존도를 만들 수 있어 의도된 바다. metrics.py 산식 변경 시 이 gate가 실패하지 않는 점은 향후 커널 연동으로 강화 후보로 남긴다."
---

<intent-contract>

## Intent

**Problem:** 실전 승률·PF가 SQL view에서 계산되지 않아 Python 백테스트 값과 화면 값이 불일치할 수 있다. 현재 `candidate_outcome` 테이블에는 종결 건이 적재되어 있지만, 이를 기반으로 한 versioned read model view가 없어 AD-8 원칙(지표는 versioned SQL view/RPC에서만 계산)을 충족하지 못한다.

**Approach:** `candidate_outcome` 테이블에서 TP/SL/TIMEOUT 종결 건만 분모로 사용하는 전체 기준 SQL view `candidate_outcome_win_rate_pf`를 생성한다. 승률은 손익률 부호로 판정하고, PF는 양/음의 손익률 합으로 계산하며, 백테스트 `metrics/metrics.py:70-72,80-86`와 동일한 산식을 적용한다. Python 계산값과 SQL view 결과의 동등성은 migration gate(JSON fixture + SQL assertion + Python 기준값 파서 3중 대조)로 검증한다.

## Boundaries & Constraints

**Always:** 승률 = (return_pct > 0인 종결 건수) / (TP+SL+TIMEOUT 건수). PF = Σ(양의 return_pct) / |Σ(음의 return_pct)|. 둘 다 비용 차감 후 손익률 기준. 승패는 종결 상태가 아니라 손익률 부호로 판정(TIMEOUT이 양의 손익으로 끝나면 승). OPEN은 항상 분모에서 제외되고 별도 카운트로 노출. SUSPENDED/DELISTED는 정상 종결 3종과 구분해 별도 카운트로 노출하며 혼입 금지. return_pct=0인 종결 건은 분모에 포함되되 승/패 어느 쪽에도 세지 않는다(metrics.py와 동일). versioned SQL view는 migration으로 생성하고 create or replace로 유지한다. 동일 fixture에 대해 Python 기준값과 view 결과가 동등함을 migration gate 테스트로 검증한다. 운영 Supabase MCP로 migration 적용·fixture 검증을 진행한다.

**Never:** 기존 migration을 수정하지 않는다(AD-14 forward-only). backtest 커널을 변경하지 않는다. UI를 직접 변경하지 않는다. browser 역할(anon/authenticated)에 원자재 SELECT를 열지 않는다(공개 전이 경로는 후속 스토리). 토큰·키를 출력하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | candidate_outcome에 TP/SL/TIMEOUT 종결 건이 있는 경우 | 승률·PF가 정상 계산됨 | 없음 |
| OPEN_EXCLUDED | OPEN 상태 건이 있는 경우 | OPEN은 분모에서 제외되고 별도 카운트로 노출 | 없음 |
| SUSPENDED_DELISTED | SUSPENDED/DELISTED 상태 건이 있는 경우 | 정상 종결 3종과 구분되어 별도 카운트로 노출 | 없음 |
| WIN_BY_SIGN | TIMEOUT이 양의 손익으로 끝나는 경우 | 승으로 집계됨 | 없음 |
| ZERO_RETURN | return_pct = 0인 종결 건이 있는 경우 | 분모에는 포함, 승/패 어느 쪽에도 미집계 | 없음 |
| ALL_WIN | 손실 없이 승만 있는 경우 | profit_factor = NULL(분모 0, SQL 무한대 대응 불가) | NULL로 진실하게 표기 |
| EMPTY | settled 분모가 0인 경우 | count 0, win_rate/profit_factor NULL | NULL로 "계산 불가" 표기 |
| PYTHON_EQUALITY | 동일 fixture에 대해 Python 계산값과 view 결과 비교 | 두 값이 동일함 | 불일치 시 파서 도구 실패 |

</intent-contract>

## Code Map

- `backtest/metrics/metrics.py:70-72,80-86` -- 승률·PF 산식 원본 (n_win=rets>0, win_rate=n_win/n_trades, PF=gross/gross_loss, to_dict 4자리 반올림)
- `backtest/engine.py:49-70` -- Trade dataclass (parity 기준값 검증용)
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- candidate_outcome DDL (status CHECK, unique(ticker,strategy,entry_date))
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql` -- guard_candidate_outcome_mutation 트리거(INSERT는 무관), version 컬럼
- `infra/supabase/migrations/202609051600_parameterize_outcome_strategy_rules.sql` -- outcome_strategy_rules(A 3/3/30 등) + snapshot guard 트리거
- `infra/supabase/migrations/202609051700_harden_outcome_strategy_snapshot_contract.sql` -- guard의 tp_pct/sl_pct/cutoff_n 검사 계약(INSERT에도 적용)
- `infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql` -- F 전략 추가(3/4/999999), guard 목록 F 확장
- `infra/supabase/migrations/202609091700_create_bias_events.sql:127-181` -- canonical view 선례 + `revoke select from public, anon, authenticated` 패턴
- `tools/check_outcome_rebuild_fixture_drift.py` -- JSON↔SQL drift 차단 gate 선례(parity 도구 골격)
- `tests/tools/test_check_outcome_rebuild_fixture_drift.py` -- 드리프트 도구 계약 테스트 선례
- `tests/sql/test_bias_close_stage.sql` -- SQL fixture 선례(begin/rollback, do $$ raise exception)
- `packages/read-model/src/database.types.ts:800-868` -- Views 섹션(신규 view 반영 대상)
- `.github/workflows/test.yml:178-209` -- sql-schema-tests 잡(마이그레이션 적용 + SQL fixture + drift gate 실행)

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609101100_create_outcome_win_rate_pf.sql` -- 전체 기준 view 생성 + comment + `revoke select on ... from public, anon, authenticated`.
- `tests/fixtures/outcome_win_rate_pf/input_cases.json` -- view 입력 candidate_outcome 행 fixture(전체 row)와 동등성 기대 산식 입력값.
- `tests/sql/test_outcome_win_rate_pf.sql` -- fixture 행을 candidate_outcome에 INSERT하고(전략 snapshot guard 통과값 사용) view 결과를 assertion 영역에 고정. begin/rollback.
- `tools/check_outcome_win_rate_pf_parity.py` -- JSON fixture 행 ↔ SQL fixture INSERT 행 ↔ SQL assertion 값 대조. Python 기준값은 backtest metrics와 동일 산식으로 JSON fixture로부터 계산한다. drift 시 ERROR.
- `tests/tools/test_check_outcome_win_rate_pf_parity.py` -- 파서 도구 계약 테스트(동기화 pass 고정 + 각 drift 종류 실패 고정).
- `.github/workflows/test.yml` -- sql-schema-tests에 parity 도구 실행 step 추가.
- `packages/read-model/src/database.types.ts` -- 운영에 적용 후 `npm run generate:read-model-types` 재생성 반영(offline lint 통과).
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 5-5 키 done 갱신.
- `tools/epic-path-manifests/epic-5.txt` -- 변경 경로 등록.

**Acceptance Criteria:**
- Given candidate_outcome에 종결(TP/SL/TIMEOUT) 건이 있는 경우, when versioned SQL view를 호출하면, then 승률 = (손익률>0 종결)/(TP+SL+TIMEOUT), PF = Σ(양)/|Σ(음)|이 비용 차감 후 손익률 기준으로 계산된다.
- Given OPEN 상태 건이 있는 경우, when 분모를 계산하면, then OPEN은 분모에서 제외되고 별도 카운트로 노출된다.
- Given SUSPENDED/DELISTED 상태 건이 있는 경우, when 분모를 계산하면, then 정상 종결 3종과 구분되어 별도 처리이며 혼입되지 않는다.
- Given 승패를 판정하는 경우, when 기준을 확인하면, then 상태가 아니라 손익률 부호로 판정된다(TIMEOUT 양수 = 승).
- Given 동일 fixture에 대해 Python 계산값과 view 결과를 비교하는 경우, when migration gate 테스트를 실행하면, then 두 값이 동일함이 검증된다.

## Spec Change Log

- 2026-09-10 step-03(Verify): Tasks 항목의 fixture 파일명을 `cases.json` → `input_cases.json`으로 일치시켰다(Design Notes의 구체 계약명을 따라 구현과 동일하게).
- 2026-09-10 step-03(Verify, Matrix Test Audit): edge-case matrix의 ZERO_RETURN/ALL_WIN/EMPTY 행이 어떤 테스트로도 SQL 레벨에서 검증되지 않음을 발견해 `tests/sql/test_outcome_win_rate_pf.sql`에 전용 시나리오 블록(각각 delete + 재구성 + view 대조)을 추가했다. parity 파서(`parse_sql_insert_rows`)는 marker 아래의 **첫 번째** candidate_outcome INSERT만 파싱하므로 해당 블록들은 parity 대상에서 자동 제외되며, 운영 Supabase 실행 시 모두 통과를 확인했다.
- 2026-09-10 step-04(Review pass): 리뷰 발견사항 반영 — (1) `compare_reference_vs_expected`가 gross_win/gross_loss를 비교하지 않던 gap을 닫아 반올림 없이 float 4자리 동등 비교 추가. (2) win_rate/profit_factor 비교를 float 동등 대신 `canonical_4dp`(round 4 고정 소수 4자리 문자열)로 정규화해 부동소수점 노이즈에 강하게 함. (3) `compute_reference`는 승/패가 없는 쪽의 gross를 SQL view의 NULL과 동일하게 None으로 반환(ALL_WIN/EMPTY edge 일관성). (4) status에 지원하지 않는 값이 섞이면 gate가 ERROR를 내도록 `VALID_STATUSES` 사전 검사 추가(오타 상태가 조용히 빠지는 drift 차단). (5) 종결 행의 return_pct 값 변경 drift를 계약 테스트로 고정. (6) Migration gate Design Note의 잔존 `cases.json` 참조를 `input_cases.json`으로 일치, "운영 준수 여부" 과잉 주장 문구 제거.

## Review Triage Log

### 2026-09-10 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0, medium 1, low 5)
- defer: 2
- dismissed:
  - 첫 번째 candidate_outcome INSERT에 의존하는 "first-match" 파싱의 취약함 — `test_sql_parsing_finds_all_insert_rows`가 `len(rows) == len(json_rows) == 9`를 고정하므로, edge 시나리오 INSERT가 main insert보다 앞으로 재배치되면 행 수 불일치로 즉시 실패한다. 청구한 결과 경로가 존재하지 않는다.
  - sprint-status.yaml 5-5 키가 diff에 없다 — 스토리 최종화(finalize) 단계의 작업으로 계획된 항목이며, 본 pass에서 `done`으로 갱신하고 `check_sprint_status.py` 통과로 검증했다.
  - ZERO_RETURN/ALL_WIN/EMPTY 시나리오가 parity gate가 아니라 SQL fixture로만 검증된다 — 의도된 설계다: 각 시나리오는 전체 테이블을 delete 후 재구성하므로 parity fixture 행과 성격이 다르고, SQL fixture가 CI sql-schema-tests에서 실행되어 회귀망 역할을 한다.
  - edge 시나리오 블록이 마지막 테이블 비우기를 안 하고 rollback에 의존 — `begin/rollback` 전부가 fixture 계약이므로(Comment 헤더) 필수 의존성이지 취약점이 아니다.
  - '0.5' vs '0.5000' 스케일 drift 미탐지 우려 — `canonical_4dp` 도입 후 양쪽이 '0.5000'으로 정규화되어 view의 canonical 4dp 출력과 의미상 일치하며, round-4 이하 자릿수 차이는 문서화된 비교 계약(4dp 동등) 범위 밖이다. 행 단위 return_pct drift는 `compare_json_sql_rows`가 별도로 잡는다.
- addressed_findings:
  - `[medium]` `[patch]` parity gate가 gross_win/gross_loss를 비교하지 않던 gap — `compare_reference_vs_expected`에 gross 필드 float 4자리 동등 비교 추가, `test_gross_win_drift_is_reported`/`test_gross_loss_drift_is_reported` 계약 테스트 추가, `test_compute_reference_matches_expected`에 gross 어설션 추가.
  - `[low]` `[patch]` win_rate/profit_factor가 float 동등으로 비교되던 것 — `canonical_4dp`(round 4 고정 소수 4자리 문자열) 도입으로 정규화 비교 전환, `test_win_pf_expected_rounding_equal_is_ok` 고정.
  - `[low]` `[patch]` ALL_WIN/EMPTY에서 Python reference의 gross_loss=0이 SQL view의 NULL과 어긋나던 latent divergence — `compute_reference`가 승/패 없는 쪽 gross를 None으로 반환하도록 수정, `test_compute_reference_all_win_gross_loss_none`/`test_compute_reference_empty_settled_none` 고정.
  - `[low]` `[patch]` 종결 행 return_pct 값 변경 drift 계약 테스트 부재 — `test_settled_row_return_pct_value_drift_is_reported` 추가.
  - `[low]` `[patch]` status 값 사전 검증 부재 — `VALID_STATUSES` + `validate_statuses` + `test_invalid_status_is_reported` 추가(오타 상태가 조용히 빠지면 gate ERROR).
  - `[low]` `[patch]` spec Design Note의 `cases.json` 잔존 참조·"운영 준수 여부" 과잉/오타 문구 ·float/문자열 모순 — 신규 파일명·실제 비교 방식(round 4 정규화 문자열/float)에 맞게 수정.

## Design Notes

### View 계약 (`candidate_outcome_win_rate_pf`)

fraction의 분모는 TP/SL/TIMEOUT settled 세트 하나로 고정한다. OPEN/SUSPENDED/DELISTED는 집계 대상이지만 분모 밖이며 각각 별도 카운트로 노출한다.

```sql
create or replace view public.candidate_outcome_win_rate_pf as
select
  count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')) as total_settled,
  count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as wins,
  count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0) as losses,
  count(*) filter (where status = 'OPEN') as open_count,
  count(*) filter (where status = 'SUSPENDED') as suspended_count,
  count(*) filter (where status = 'DELISTED') as delisted_count,
  round(
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0)::numeric
    / nullif(count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')), 0),
    4
  ) as win_rate,
  sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as gross_win,
  abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)) as gross_loss,
  round(
    sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0)
    / nullif(abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)), 0),
    4
  ) as profit_factor
from public.candidate_outcome;
```

- 반올림은 `Performance.to_dict()`의 round(win_rate,4)/round(profit_factor,4)와 동일한 4자리. ROUND(numeric,4)와 Python round(x,4)의 tie 처리는 "계산상 다를 수 있는 반올림 경계값"에 해당하며, parity gate가 사용하는 fixture 값은 tie 경계에서 멀리 잡아 그 차이를 어설션 지점에서 발생시키지 않는다.
- 미세 자릿수: numeric 나눗셈 결과는 `round(...,4)`로 고정하므로 Python float 연산과의 비교는 round 이후 값으로만 대조한다. parity 도구는 양쪽 값을 모두 round 4 처리한 뒤 **소수 4자리 정규화 문자열**(`canonical_4dp`, 예: `0.5` → `'0.5000'`)로 비교한다 — abs/rel 허용 오차 없이 동등. gross_win/gross_loss는 반올림 없이 round 4 float 동등으로 대조한다.
- gross_loss = 0(전부 승)이면 Python은 `inf`를 주지만 SQL view는 NULL로 표현한다. 이는 UI/JSON 직렬화에서 무한대를 쓰지 않기 위한 SQL 경계 결정이며, edge-case matrix에 기재한다. 동등성 gate는 손실이 있는 fixture를 사용해 이 divergence 지점을 어설션 범위 밖으로 둔다.
- settled가 0이면 win_rate/profit_factor는 NULL(계산 불가)이고 카운트는 0.
- view는 migration 소유자인 postgres로 생성되고 `guard_candidate_outcome_mutation`의 UPDATE 가드와 무관하다(읽기 전용).
- `revoke select on public.candidate_outcome_win_rate_pf from public, anon, authenticated;` — bias view 선례(202609091700:176-181)와 동일하게 browser 역할 접근을 닫고, service_role을 통한 read path는 후속 스토리(5.13/5.14 등)에서 연다. candidate_outcome 자체가 RLS deny-all이라 view 권한을 닫지 않으면 anon이 view owner(postgres, BYPASSRLS)를 통해 원자재를 읽을 수 있으므로 반드시 revoke가 필요하다.

### Migration gate (AD-8): Python 기준값 ↔ view 동등성

`check_outcome_rebuild_fixture_drift.py`(epic-3-retro-item-17)의 drift 차단 구조를 따른다. 진실의 원천이 둘이면 조용히 갈라지는 문제를 차단하기 위해 **세 경로를 같은 값으로 묶는다**:

1. `tests/fixtures/outcome_win_rate_pf/input_cases.json` — view에 넣을 candidate_outcome 행의 유일한 데이터 원본.
2. `tests/sql/test_outcome_win_rate_pf.sql` — 같은 행을 candidate_outcome에 INSERT하고(전략 snapshot guard 통과값: 전략별 rules와 일치하는 tp_pct/sl_pct/cutoff_n, 예 A=3.0/3.0/30), 기대 승률·PF·카운트를 assertion으로 고정. `begin ... rollback`으로 상태를 남기지 않는다.
3. `tools/check_outcome_win_rate_pf_parity.py` — (a) SQL fixture의 INSERT 행과 assertion 값을 파싱하고, (b) JSON fixture를 파싱해 같은 행임을 대조하고, (c) JSON 행으로부터 Python 기준값(metrics와 동일 산식, round 4)을 계산해 SQL assertion 값과 **문자열 동등**을 요구한다. 어느 하나라도 갈라지면 ERROR.

이 구성은 "Python이 이 fixture에서 반환할 값"과 "SQL view가 이 fixture에서 반환해야 하는 값"을 gate가 동시에 단속하므로, 한쪽만 고치면 다른 쪽과의 drift로 즉시 실패한다.

### SQL INSERT 시 snapshot guard 통과

`candidate_outcome`에는 `candidate_outcome_strategy_snapshot_guard`(BEFORE INSERT, 202609051600/1700)가 있어 전략별 `outcome_strategy_rules`와 다른 tp_pct/sl_pct(및 D~F는 cutoff_n)로 INSERT하면 `OUTCOME_STRATEGY_SNAPSHOT_MISMATCH`로 거부된다. SQL fixture는 rules 상 존재하는 전략(A/B/C/D/E/F 중 전부 또는 일부)을 사용하고 각 행에 rules-matched tp_pct/sl_pct/cutoff_n을 명시한다. GRANT는 INSERT 경로에 무관(슈퍼유저 실행). unique(ticker,strategy,entry_date)와 OPEN 하나-per-ticker 제약을 지키도록 ticker·전략·날짜를 결정론적으로 잡는다.

### parity 도구 어설션

- win_rate/profit_factor는 round 4 고정 소수 4자리 정규화 문자열 비교(예: `'0.6800'`, `'2.0540'`; `canonical_4dp`). gross_win/gross_loss는 round 4 float 동등 비교.
- 카운트(total_settled/wins/losses/open/suspended/delisted)는 정수 비교.
- JSON INSERT 행과 SQL INSERT 행은 (ticker, strategy, entry_date)를 지표로 완전 일치까지 비교.
- status 값은 `VALID_STATUSES`(=TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED) 검사를 거친다 — 오타 상태가 조용히 빠지면 gate가 ERROR.

### migration gate 산출물 3중 구조(구체 계약)

`check_outcome_rebuild_fixture_drift.py`의 marker 기반 파싱 방식을 그대로 따른다. 파서는 SQL을 완전히 해석하는 대신 fixture가 지켜야 하는 형태를 전제하고, 전제가 깨지면 ERROR로 실패한다.

- `tests/fixtures/outcome_win_rate_pf/input_cases.json` -- candidate_outcome에 넣을 행의 유일한 데이터 원본. 각 행 키: `ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct`. null 필드는 JSON null로 기술(exit_date/exit_price/return_pct).
- `tests/sql/test_outcome_win_rate_pf.sql` -- `begin`; (마커 `-- ── parity fixture setup` 아래 AC 구간) JSON과 동일한 행을 `insert into public.candidate_outcome(...) values (...)`로 삽입하고, 기대 튜플을 temp table `win_pf_expected`로 고정한 뒤 `do $$ raise exception` 블록으로 **view 조회 값 전체 필드를 튜플과 대조**한다. 모든 fixture는 `rollback`으로 끝난다.
- `tools/check_outcome_win_rate_pf_parity.py` -- (a) SQL AC 구간의 INSERT 튜플 파싱, (b) `win_pf_expected` 값 튜플 파싱, (c) JSON을 파싱해 SQL INSERT 행과 대조, (d) JSON 행으로 Python 기준값 계산(아래), (e) 기준 승률·PF·카운트·gross를 SQL 기대 튜플과 **성분 단위 소수 4자리 문자열/정수 비교**. status는 `VALID_STATUSES` 사전 검사. 갈라지면 ERROR + 0이 아닌 exit code.
- Python 기준값 산식(지표 반올림은 metrics.to_dict와 동일): settled = [status in TP/SL/TIMEOUT인 행]; total_settled=len(settled); wins=len(return_pct>0); losses=len(<0); win_rate=round(wins/total,4); gross_win=sum(+)(승 없으면 None); gross_loss=abs(sum(-))(패 없으면 None — SQL view의 NULL과 동일화); profit_factor=round(gross_win/gross_loss,4)(gross_loss>0일 때, 그 외 None). 카운트는 정수, 지표는 소수 4자리 정규화 문자열로 비교.

기대 튜플(구현이 그대로 사용할 기준값, 코스트 포함 임의 손익률로 '0.7111'이 tie 경계에서 멀다):

```
total_settled=6, wins=3, losses=3, open_count=1, suspended_count=1, delisted_count=1,
gross_win=6.4, gross_loss=9.0, win_rate='0.5000', profit_factor='0.7111'
```

AC 구간 입력 데이터(A~C 전략, rules 스냅샷 3.0/3.0/30, ticker 고유):

| ticker | strategy | entry_date | entry_price | status    | exit_date  | exit_price | return_pct |
|--------|----------|------------|-------------|-----------|------------|------------|------------|
| A0001 | A | 2098-05-01 | 1000 | TP       | 2098-05-03 | 1029       | 2.9        |
| A0002 | B | 2098-05-01 | 2000 | SL       | 2098-05-03 | 1940       | -3.0       |
| A0003 | C | 2098-05-02 | 5000 | TIMEOUT  | 2098-06-01 | 5075       | 1.5        |
| A0004 | A | 2098-05-02 | 1000 | TIMEOUT  | 2098-06-01 | 980        | -2.0       |
| A0005 | B | 2098-05-03 | 3000 | TP       | 2098-05-05 | 3060       | 2.0        |
| A0006 | C | 2098-05-03 | 4000 | SL       | 2098-05-05 | 3840       | -4.0       |
| A0007 | A | 2098-05-04 | 1000 | OPEN     | null       | null       | null       |
| A0008 | B | 2098-05-04 | 2000 | SUSPENDED| null       | null       | null       |
| A0009 | C | 2098-05-05 | 5000 | DELISTED | 2098-05-10 | 4800       | null       |

(TIMEOUT A0003이 양수=WIN_BY_SIGN, A0003/A0004로 전략 수명 차이·holding_days 포함, A0007/A0008/A0009로 OPEN/SUSPENDED/DELISTED 제외·별도 카운트 커버.)

parity 도구의 SQL 파싱 marker: AC 구간 시작 `-- ── parity fixture setup`(이 구간 안의 candidate_outcome INSERT만 대조 대상), `win_pf_expected` 튜플은 정규식 `insert into win_pf_expected values\s*\((...)\)`로 파싱. 마커가 없으면 SystemExit로 조용한 통과를 차단한다.

### read-model 타입 반영

신규 view는 `packages/read-model/src/database.types.ts` Views 섹션에 반영돼야 한다(offline `check_generated_types_drift.py`가 view 이름 존재를 요구). 운영에 migration을 적용한 뒤 `npm run generate:read-model-types`(SUPABASE_ACCESS_TOKEN 필요, `.env.local`에 존재)로 재생성해 커밋한다.

## Verification

**Commands:**
- `python tools/check_migration_order.py` -- migration timestamp 유일성·순서 통과.
- `python tools/check_outcome_win_rate_pf_parity.py` -- JSON↔SQL↔Python 기준값 3중 동등성 통과.
- `uv run --with pytest python -m pytest tests/tools/test_check_outcome_win_rate_pf_parity.py -q` -- 도구 계약 테스트 통과.
- `python tools/check_generated_types_drift.py` -- 신규 view가 타입 파일에 존재.
- 운영 Supabase MCP: migration 적용 후 `tests/sql/test_outcome_win_rate_pf.sql` 실행(rollback) 및 view 조회.
- `npm run generate:read-model-types` 후 `git diff --exit-code -- packages/read-model/src/database.types.ts` -- 재생성 drift 없음.

**Manual checks (if no CLI):**
- Supabase 대시보드에서 `candidate_outcome_win_rate_pf` view가 조회되고(service_role), anon/authenticated는 빈 결과 또는 권한 없음이 확인된다.

## Auto Run Result

Story key: 5-5-승률-pf-핵심-산식-view-전체-기준 / Epic 5 / build-auto (1ca16fbcda4c)

**Outcome:** diff [`review`] = true → patch → auto-fix → sprint sync → commit flows done. 계약 테스트 95개(parity 도구 17 + tools 78), 전체 `tests/tools` 95 passed. 리뷰 패치: parity gate gross/canonical-4dp/status 검증 + 계약 테스트 확장, spec Change Log·프로즈 정합. 스토리 5-5의 변화는 이 diff 하나로 완결되지 않았고, 이후 스토리 5-6(전략별·원천별 분리 view)이 다음 이터레이션.

**Build:**
- `python tools/check_outcome_win_rate_pf_parity.py` — fixture drift 없음(행 9건, total_settled=6, win_rate=0.5, profit_factor=0.7111), exit 0.
- `python tools/check_migration_order.py` — 69 files 통과, exit 0.
- `python tools/check_generated_types_drift.py` — 22 objects 통과(신규 view 포함), exit 0.
- `uv run --with pytest --with pyyaml pytest tests/tools -q` — 95 passed, exit 0.
- `python tools/check_sprint_status.py` — action item 38건(open 3, in-progress 1, done 34) 통과, exit 0.
- `python tools/check_epic_scope.py --epic 5 --range c815f8b --worktree --clean-tree` — ok:true, clean_tree:true, 변경 9경로 전부 게이트 내.

**Review run:**
- layer 향상: blind hunter 12건, edge-case hunter 3건, verification gap 1건, intent-alignment(판독 R1-R9 + D1-D5 기록).
- patch 6, defer 2. followup_review_recommended: true(3×medium 1 + low 5 = 8 ≥ 5). — gross gap 중등도 1건이 기준을 넘겼다. 근거: parity gate만으로 gross drift를 잡지 못했던 gap은 이번에 닫았고, SQL fixture의 do-블록이 동일 부분을 중복 단속하므로 실질 위험은 낮다.
- 리뷰 확정 계획: 그대로 진행. 다음 이터레이션(5-6)에서 이행 여부를 재확인한다.

**operational zap:** [Migration SUCCESS] 202609101100_create_outcome_win_rate_pf.sql 적용 + SQL fixture 테스트(rollback) 통과 + 뷰 권한·롤백 잔재 검증(anon/auth SELECT off, service_role on, 잔재 0).

**배포/배포 후 검증:**
- 운영 프로젝트(qqhjeumlecaudsiqhhdu)에 migration 적용 로드 완료. `tests/sql/test_outcome_win_rate_pf.sql`을 begin/rollback으로 실행해 ZERO_RETURN/ALL_WIN/EMPTY 시나리오를 포함한 전체 assertion 통과 확인.
- 사후 검증 쿼리에서 leftover=0, table_rows=0, view_owner=postgres, anon/auth can_select=false, service_role can_select=true 확인.
- `npm run generate:read-model-types` 후 `python tools/check_generated_types_drift.py` drift 없음(22 objects). `database.types.ts`에 `candidate_outcome_win_rate_pf` 포함(line 843).
- 커밋: `feat(story 5-5): candidate_outcome_win_rate_pf 승률·PF view + parity gate`(스토리 5-4 커밋 구조 참조).