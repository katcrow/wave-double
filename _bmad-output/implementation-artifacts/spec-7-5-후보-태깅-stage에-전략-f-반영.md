---
title: '후보 태깅 stage에 전략 F 반영'
type: 'feature'
created: '2026-09-08'
baseline_revision: '9c7d705aa111b0a371aae95b53233cdb3177de7e'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/spec-6-6-후보-태깅-stage에-전략-d-e-반영.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `apps/batch/tags_stage.py`가 여전히 자체 5키 상수(`_STRATEGY_KEYS = ("A","B","C","D","E")`)만 소비해, Story 7.3에서 `compute_abc`가 이미 반환하는 F 시그널이 `candidate_tags`에 저장되지 않는다(Story 7.3/7.4 스펙에 이미 잔여 리스크로 기록된 정확히 그 gap).

**Approach:** tags stage가 소비하는 전략 키 목록을 A/B/C/D/E/F로 확장하고, `params_meta` 스냅샷에 F 지표 파라미터(`STRATEGY_F_PARAMS`)를 추가한다. 저장·발행 경로(`candidate_tags` 스키마, `emit_open_command`/`publish_attempt`의 전략별 TP/SL 조회)는 Story 7.2/7.3/7.4가 이미 일반화·완료했으므로 변경하지 않는다.

## Boundaries & Constraints

**Always:** `daily_ohlcv` → `compute_abc` → `candidate_tags` 순서와 ineligible/error 분리 집계, look-ahead 방지, `params_meta` 스냅샷 관례를 그대로 유지한다. 시그널이 발생한 모든 전략(A~F, 다중 가능)을 저장한다.

**Never:** `compute_abc`/전략 계산 로직(`backtest/strategy_api.py`), `candidate_tags` 스키마, `emit_open_command`/`publish_attempt`, `outcome_strategy_rules`, UI를 변경하지 않는다(Story 7.2/7.3/7.4가 이미 구현·검증했고 이번 스토리 범위 밖). Story 7.6(UI 라벨/배지)·7.7(OOS 검증)도 이 스토리 범위가 아니다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 후보 종목에서 A/B/C/D/E/F 중 일부 시그널 발생 | 발생한 모든 전략이 다중 태그로 저장(예 A∩F) | 오류 없음 |
| ONLY_F | F만 발생, A~E 없음 | F만 태그로 저장 | 오류 없음 |
| ALL_SIX | A/B/C/D/E/F 6개 전략 동시 발생 | 6중 태그로 저장 | 오류 없음 |
| F_SIGNAL_COMPUTE_ERROR | F 시그널 계산 중 예외 발생 | 에러로 집계되고 다른 전략(A~E)으로 오귀속되거나 조용히 누락되지 않음 | `SIGNAL_COMPUTE_ERROR` 계열 처리 |
| PUBLISH_FLOW | F 태그가 `publish_attempt`에 전달됨 | `emit_open_command`가 `outcome_strategy_rules`에서 조회한 F 전용 TP3%/SL4%/cutoff=999999를 사용 | 기존 A~E 계약 불변(Story 7.4 SQL fixture로 검증 완료, 회귀 없음) |

</intent-contract>

## Code Map

- `apps/batch/tags_stage.py:32` -- `_STRATEGY_KEYS = ("A", "B", "C", "D", "E")`. F 태깅 누락의 직접 원인(유일한 하드코딩 지점). `("A","B","C","D","E","F")`로 확장.
- `apps/batch/tags_stage.py:154-158` -- `strategies` 리스트 컴프리헨션이 `_STRATEGY_KEYS`를 순회하며 `result.signals.get(key)`로 마지막-1 봉 신호를 태그로 변환. 로직 자체는 전략 키 개수에 무관하게 동작(추가 분기 불필요, 변경 없음).
- `apps/batch/tags_stage.py:263-287` (`_build_params_meta`) -- A~E 지표 파라미터만 스냅샷(`strategy_d_params`/`strategy_e_params`가 각각 266-267행 import, 283-284행 dict 삽입). `from backtest.indicator_opt.strategy_f import STRATEGY_F_PARAMS`를 추가하고 `"strategy_f_params": STRATEGY_F_PARAMS.as_dict()`를 대칭으로 삽입.
- `apps/batch/tags_stage.py:1,4` -- 모듈 docstring이 "Story 2.5/6.6", "A/B/C/D/E"로 표기. Story 7.5/F 반영으로 갱신.
- `backtest/strategy_api.py:20-21,26,48,242,268` (`compute_abc`) -- Story 7.3에서 이미 A/B/C/D/E/F 6키의 `signals`·`params_meta`(전략별 TP/SL/max_holding 포함)를 반환하도록 확장 완료. 변경 없음, 그대로 소비.
- `infra/supabase/migrations/202609071000_expand_candidate_tags_strategy_check_f.sql` -- Story 7.2에서 `candidate_tags.strategy` CHECK를 A~F로 확장 완료(운영 적용 확인). 변경 없음.
- `infra/supabase/migrations/202609080900_parameterize_outcome_strategy_rules_f.sql` -- Story 7.4에서 `emit_open_command`가 `outcome_strategy_rules`(A~F)를 조회해 OPEN 시점 TP/SL/cutoff를 스냅샷하도록 완료. `publish_attempt`(`202609070900_supply_3day_publish_guard.sql:75-80`)도 `candidate_tags`의 전략값을 그대로 `emit_open_command`에 전달(하드코딩 없음, `select ... t.strategy from candidate_tags t` 완전 데이터 기반). 변경 없음, 그대로 소비.
- `apps/batch/candidate_tags_repository.py:22` -- `CandidateTag.strategy` 타입 주석이 이미 `"A" | "B" | "C" | "D" | "E" | "F"`로 Story 6.6 당시 갱신되어 있음(확인만, 변경 불필요).
- `tests/batch/test_tags_stage.py` -- 기존 A~E 픽스처는 `signals` dict에 F 키가 없어도 `.get()` 기반 로직상 영향 없음(하위호환). F 단독 태깅, A∩F 다중 태깅, 6전략 동시 발생, F `SIGNAL_COMPUTE_ERROR` 분기, `params_meta`의 `strategy_f_params` 값 동등성(`STRATEGY_F_PARAMS.as_dict()`) 회귀를 신규 테스트로 추가(Story 6.6이 D/E에 대해 추가한 5개 테스트와 동일 패턴).

## Tasks & Acceptance

**Execution:**
- `apps/batch/tags_stage.py` -- `_STRATEGY_KEYS`를 `("A","B","C","D","E","F")`로 확장하고 `_build_params_meta`에 F 지표 파라미터(`STRATEGY_F_PARAMS`) 스냅샷을 추가하며 모듈 docstring을 갱신한다 -- AC1.
- `tests/batch/test_tags_stage.py` -- F 단독 태깅, A∩F 다중 태깅, A~F 6전략 동시 발생, F `SIGNAL_COMPUTE_ERROR` 분기, `params_meta`에 `strategy_f_params` 값 동등성 검증을 추가한다 -- AC1, I/O 매트릭스 전체.

**Acceptance Criteria:**
- Given Story 7.2(스키마)·7.3(계산 API)가 완료된 상태에서 Story 2.5/6.6의 tagging stage가 실행되면, when 후보 종목에 A/B/C/D/E/F 중 하나 이상의 시그널이 발생하면, then 발생한 모든 전략이 `candidate_tags`에 다중 태그로 저장된다(예 A∩F).
- Given Story 7.4가 완료되어 전략별 TP/SL/최대보유 조회가 가능한 상태에서, when 이 태그가 Epic 3의 `emit_open_command`(publish_attempt 경유)에 전달되면, then 진입가·TP/SL 판정에 F의 청산조건(TP3%/SL4%/cutoff=999999)이 정확히 적용된다(이미 Story 7.4 SQL fixture로 검증 완료, 이번 스토리는 태그 생성만 추가).

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4계층 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 2: (high 0, medium 0, low 2)
- defer: 0
- dismissed:
  - (blind-hunter) `sprint-status.yaml`이 아직 `backlog`로 동기화되지 않았다는 지적 — 사용자 지시 순서(개발→검수/보완→e2e 필요성 판단→스프린트 동기화→커밋)상 스프린트 동기화는 이 리뷰 패스 완료 이후 순서이므로 예상된 상태다(결함 아님).
  - (blind-hunter) `test_all_five_strategies_signal_on_same_ticker`(A-E만, F 키 부재)가 `test_all_six_strategies_signal_on_same_ticker`의 부분집합이라 중복이라는 지적 — 두 테스트를 직접 확인한 결과 전자는 `signals` dict에 `"F"` 키 자체가 없는 시나리오(하위호환/`.get()` 기본값 분기)를, 후자는 6개 키 모두 존재하는 시나리오를 검증해 서로 다른 입력 형태를 다룬다. 부분집합이 아니다.
  - (blind-hunter) F 키가 `signals` dict에 아예 없을 때의 방어적 `.get()` 분기가 테스트되지 않았다는 지적 — 위와 동일 근거로 `test_all_five_strategies_signal_on_same_ticker`(변경 없이 그대로 유지, 248 passed에 포함되어 통과 확인)가 정확히 이 시나리오(F 키 부재)를 이미 검증하고 있다.
  - (blind-hunter) F가 한 종목에서 에러이고 F가 다른 종목에서 성공하는 비대칭 케이스가 없다는 지적 — `run_tags_stage`의 독스트링(`tags_stage.py:99`, "한 종목의 실패가 나머지 종목 처리를 막지 않는다")과 실제 루프 구현이 종목별로 완전히 독립적으로 처리되며 어떤 전략이 성공/실패했는지에 따라 분기하는 공유 상태가 없음을 코드로 확인했다. 기존 D 테스트(동일 비대칭 패턴, A 성공/D 에러)로 이미 이 독립성이 실증되어 있어 F 전용 반복 테스트가 실효가 없다.
  - (blind-hunter) 신규 테스트 4건이 D/E 테스트와 보일러플레이트를 다수 공유한다는 지적 — Story 6.6이 D/E 테스트를 추가할 때 이미 채택한 이 파일의 확립된 관례(전략별 유사 fixture 반복)이며 이번 diff가 새로 만든 패턴이 아니다.
  - (blind-hunter) F `SIGNAL_COMPUTE_ERROR` 테스트의 `error.strategy="F"`가 실제로는 검증되지 않는 장식적 필드라는 지적 — `run_tags_stage`의 에러 집계 로직(결과 상태/`result.error is not None` 여부만 확인)을 직접 확인한 결과 전략별 에러 귀속 자체를 하지 않는 설계이며, 이는 Story 6.6의 D 테스트도 동일하게 갖고 있던 기존 패턴이라 이번 diff가 새로 도입한 격차가 아니다.
  - (blind-hunter) `params_meta["strategy_f_params"]`이 F만 태깅된 행에 특정해 검증되지 않는다는 지적 — `_build_params_meta(batch_kind)`를 확인한 결과 이 함수는 어떤 전략이 발동했는지와 무관하게 배치당 한 번 계산된 동일한 dict를 모든 태그 행에 그대로 부착하므로, 기존 A-only 테스트의 값 동등성 검증이 F-only 시나리오에도 바이트 단위로 동일하게 적용된다.
  - (blind-hunter) PUBLISH_FLOW/AC2(F의 emit_open_command 청산조건 적용)가 diff에 새 테스트 아티팩트로 남지 않고 스펙 서술로만 기록됐다는 지적 — epic-7-context.md의 Cross-Story Dependencies("Story 7.4가 완료되어야 Story 7.5의 태그가 emit_open_command 판정에 정확히 흘러간다")가 7.4를 인에이블러로, 7.5를 태그 생성 전담으로 명시적으로 구분하고 있고, Story 6.6(D/E의 동일 구조 선례)도 이 AC를 이전 스토리(6.5) fixture 재실행만으로 충족 처리했다. 이번 세션에서도 이 스토리의 리뷰 과정에서 `tests/sql/test_outcome_open_command.sql`을 production에 직접 재실행해 F의 OPEN/replay 스냅샷(TP3%/SL4%/cutoff=999999)이 여전히 pass함을 확인했다(스펙 Verification 절에 기록). 코드 변경이 없는 경로이므로 diff 내 신규 아티팩트가 없는 것이 결함이 아니다.
  - (intent-alignment) 서술적 감사 보고 — 코드 없이 세 가지 방어 가능한 해석(R1 전체-AC, R2 좁은-범위, R3 검증-완결성)을 나열하고 diff가 R2를 구현함을 확인. epic context의 Cross-Story Dependencies 문구와 Story 6.6의 동일 구조 선례가 R2를 뒷받침하는 의도상 근거이므로 다중 해석 사이에 선택 근거가 없는 intent gap이 아니다.
  - (edge-case-hunter) 발견 없음(`[]`).
  - (verification-gap) 발견 없음("No verification gaps found.").
- addressed_findings:
  - `[low]` `[patch]` (blind-hunter) `tags_stage.py` 모듈 docstring이 전략 F가 무엇인지(각도가속·이평선 쌍바닥) 설명하지 않음 — 한 줄 설명 추가.
  - `[low]` `[patch]` (blind-hunter) `TaggedCandidate.strategies`의 예시 주석(`# ["A"], ["A", "B"], etc.`)이 5-6개 전략 공간을 반영하지 않음 — F를 포함한 예시로 갱신.

## Design Notes

`compute_abc`(7.3)·`candidate_tags` 스키마(7.2)·`emit_open_command`/`publish_attempt`(7.4)가 이미 A~F를 전략 키 개수에 무관하게 일반적으로 처리하도록 구현돼 있어, 실제 남은 gap은 `tags_stage.py`의 하드코딩된 5-전략 상수 하나뿐이다(Story 6.6이 D/E에 대해 동일 gap을 해소한 것과 정확히 같은 패턴). `apps/batch/scheduler.py`는 전략 목록을 전혀 열거하지 않으므로(투명 전달만) 변경 대상이 아니다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with httpx --with pytest pytest tests/batch tests/domain -q` -- expected: 신규 F 태깅 테스트 포함 전체 통과, 기존 회귀 없음.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 전략 계산 회귀 없음(compute_abc 미변경).
- `npm run typecheck` -- expected: 통과.
- `python tools/check_migration_order.py` -- expected: 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- 없음(전부 CLI/pytest로 검증 가능; UI 표면 없음, 이 스토리는 Python 배치 계층만 변경).

실행 결과:

- `pytest tests/batch tests/domain -q` -- 248 passed(신규 F 태깅 테스트 4건 포함).
- `pytest backtest -q` -- 152 passed(compute_abc 회귀 없음).
- `npm run typecheck` -- 통과.
- `python tools/check_migration_order.py` -- 51 files 통과.
- `git diff --check` -- 통과(공백 오류 없음).
- `tests/sql/test_outcome_open_command.sql`를 production Supabase(qqhjeumlecaudsiqhhdu)에 직접 실행(begin/rollback으로 흔적 없음) -- `pass`(PUBLISH_FLOW 매트릭스 행: F의 emit_open_command OPEN/replay가 Story 7.4 스냅샷 그대로 재확인됨, 이 스토리는 해당 경로를 변경하지 않았으므로 회귀 없음).
- 리뷰 패치 반영 후 재검증: `pytest tests/batch tests/domain -q` -- 248 passed(회귀 없음). `npm run typecheck` -- 통과. `git diff --check` -- 통과.

## Auto Run Result

Summary: `apps/batch/tags_stage.py`가 여전히 자체 5키 상수(`_STRATEGY_KEYS`)만 소비해 Story 7.3에서 이미 계산 가능해진 전략 F 시그널이 `candidate_tags`에 저장되지 않던 것을, Story 6.6이 D/E에 대해 적용한 것과 동일한 패턴으로 `_STRATEGY_KEYS`를 F까지 확장하고 `params_meta`에 F 지표 파라미터 스냅샷을 추가해 해결했다. 저장·발행 경로(`candidate_tags` 스키마, `emit_open_command`/`outcome_strategy_rules`)는 Story 7.2/7.3/7.4가 이미 완료해 변경이 필요 없었다.

Files changed:
- `apps/batch/tags_stage.py` — `_STRATEGY_KEYS`를 `("A","B","C","D","E","F")`로 확장, `_build_params_meta`에 `strategy_f_params`(`STRATEGY_F_PARAMS.as_dict()`) 추가, 모듈 docstring 및 `TaggedCandidate.strategies` 예시 주석 갱신(리뷰 패치).
- `tests/batch/test_tags_stage.py` — F 단독 태깅, A∩F 다중 태깅, A~F 6전략 동시 발생, F `SIGNAL_COMPUTE_ERROR` 분기 신규 테스트 4건 추가, 기존 `params_meta` 값 동등성 테스트에 `strategy_f_params` 단언 추가.
- `_bmad-output/implementation-artifacts/spec-7-5-후보-태깅-stage에-전략-f-반영.md` — 신규 스펙 문서(본 파일).

Review findings breakdown (2026-09-08, 4계층 병렬 리뷰 패스): patch 2건(low 2) 모두 수정 — 모듈 docstring에 F 설명 부재, `TaggedCandidate.strategies` 예시 주석이 5-6전략 공간을 반영하지 않음. dismissed 9건(위 Review Triage Log에 각각 근거와 함께 기록: sprint-status 미동기화는 이후 순서라 예상된 상태, 5전략/6전략 테스트 중복·F 키 부재 미검증·비대칭 에러 케이스·보일러플레이트 중복·에러 귀속 미검증·params_meta 미검증 지적은 모두 코드 직접 확인으로 반박됨, PUBLISH_FLOW e2e 아티팩트 부재는 epic context의 cross-story 의존성 문구와 Story 6.6 선례로 근거가 성립하고 production 재실행으로 재확인됨). intent_gap·bad_spec·defer 없음.

Follow-up review recommendation: false (patched low 2; score 1×2 = 2 < 5, no high severity).

Verification: `pytest tests/batch tests/domain -q` 248 passed(신규 F 테스트 4건 포함), `pytest backtest -q` 152 passed(compute_abc 회귀 없음), `npm run typecheck` 통과, `python tools/check_migration_order.py` 51 files 통과, `git diff --check` 통과. `tests/sql/test_outcome_open_command.sql`를 production Supabase(qqhjeumlecaudsiqhhdu)에 begin/rollback으로 직접 실행해 PUBLISH_FLOW 매트릭스 행(F OPEN/replay 스냅샷)을 재확인(pass, 흔적 없음). 리뷰 패치 2건 반영 후 전체 재검증 통과. e2e/브라우저 테스트는 이 스토리 범위(Python 배치 계층만 변경, UI/edge function/프론트엔드 표면 없음)에 해당하지 않아 적용하지 않았다.

Residual risks: 없음. 남은 유일한 실질 gap이었던 `tags_stage.py`의 하드코딩된 5-전략 상수를 이번 스토리로 해소했으며, 저장·발행 경로는 이미 완료된 선행 스토리(7.2/7.3/7.4)로 검증되어 있다. UI 배지/라벨(Story 7.6)과 OOS 검증(Story 7.7)은 이 스토리 범위 밖으로 이미 추적 중이다.
