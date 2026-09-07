---
title: '후보 태깅 stage에 전략 D/E 반영'
type: 'feature'
created: '2026-09-07'
baseline_revision: '4bc2c98'
baseline_commit: '4bc2c98'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/spec-6-5-outcome-판정-로직-전략별-파라미터화-epic-3-확장.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `apps/batch/tags_stage.py`가 `compute_abc`의 A/B/C 시그널만 소비해, Story 6.4에서 이미 반환하는 D/E 시그널이 `candidate_tags`에 저장되지 않는다.

**Approach:** tags stage가 소비하는 전략 키 목록을 A/B/C/D/E로 확장하고, 계산 파라미터 스냅샷(`params_meta`)에 D/E 지표 파라미터를 추가한다. 저장·발행 경로(`candidate_tags` 스키마, `emit_open_command`/`publish_attempt`의 전략별 TP/SL 조회)는 Story 6.3/6.5가 이미 일반화했으므로 변경하지 않는다.

## Boundaries & Constraints

**Always:** `daily_ohlcv` → `compute_abc` → `candidate_tags` 순서와 ineligible/error 분리 집계, look-ahead 방지, `params_meta` 스냅샷 관례를 그대로 유지한다. 시그널이 발생한 모든 전략(A~E, 다중 가능)을 저장한다.

**Never:** `compute_abc`/전략 계산 로직, `candidate_tags` 스키마, `emit_open_command`/`publish_attempt`, UI를 변경하지 않는다(Story 6.3/6.4/6.5가 이미 구현·검증했고 이번 스토리 범위 밖).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 후보 종목에서 A/B/C/D/E 중 일부 시그널 발생 | 발생한 모든 전략이 다중 태그로 저장(예 A∩D) | 오류 없음 |
| ONLY_D_E | D/E만 발생, A/B/C 없음 | D/E만 태그로 저장 | 오류 없음 |
| PUBLISH_FLOW | D/E 태그가 `publish_attempt`에 전달됨 | `emit_open_command`가 `outcome_strategy_rules`에서 조회한 D/E 전용 TP/SL/cutoff를 사용 | 기존 A/B/C 계약 불변(Story 6.5 검증 완료, 회귀 없음) |

</intent-contract>

## Code Map

- `apps/batch/tags_stage.py:32` -- `_STRATEGY_KEYS = ("A", "B", "C")`. D/E 태깅 누락의 직접 원인. `("A","B","C","D","E")`로 확장.
- `apps/batch/tags_stage.py:154-158` -- `strategies` 리스트 컴프리헨션이 `_STRATEGY_KEYS`를 순회하며 `result.signals.get(key)`로 마지막-1 봉 신호를 태그로 변환. 로직 자체는 이미 전략 키 개수에 무관하게 동작(추가 분기 불필요).
- `apps/batch/tags_stage.py:263-283` (`_build_params_meta`) -- A/B/C 지표 파라미터만 스냅샷. `backtest.indicator_opt.strategy_d.STRATEGY_D_PARAMS`/`strategy_e.STRATEGY_E_PARAMS`를 추가해 재현성 스냅샷을 D/E까지 대칭으로 맞춘다.
- `backtest/strategy_api.py:22,193-273` (`compute_abc`) -- Story 6.4에서 이미 A/B/C/D/E 키의 `signals`·`params_meta`(전략별 TP/SL/max_holding)를 반환하도록 확장 완료. 변경 없음, 그대로 소비.
- `infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql` -- Story 6.3에서 `candidate_tags.strategy` CHECK를 A/B/C/D/E로 확장 완료(운영 적용 확인). 변경 없음.
- `infra/supabase/migrations/202609051600_parameterize_outcome_strategy_rules.sql`, `202609052000_harden_outcome_strategy_snapshot_contract.sql` -- Story 6.5에서 `emit_open_command`가 `outcome_strategy_rules`(A~E)를 조회해 OPEN 시점 TP/SL/cutoff를 스냅샷하도록 완료. `publish_attempt`도 `candidate_tags`의 전략값을 그대로 `emit_open_command`에 전달(하드코딩 없음). 변경 없음, 그대로 소비.
- `apps/batch/candidate_tags_repository.py:22` -- `CandidateTag.strategy` 타입 주석이 `"A" | "B" | "C"`로 낡음. `"A" | "B" | "C" | "D" | "E"`로 갱신(동작 변경 없음, 문서 정정).
- `tests/batch/test_tags_stage.py` -- 기존 A/B/C 픽스처는 `signals` dict에 D/E 키가 없어도 `.get()` 기반 로직상 영향 없음(하위호환). D/E 단독 태깅과 A∩D 다중 태깅 회귀를 신규 테스트로 추가.

## Tasks & Acceptance

**Execution:**
- `apps/batch/tags_stage.py` -- `_STRATEGY_KEYS`를 `("A","B","C","D","E")`로 확장하고 `_build_params_meta`에 D/E 지표 파라미터 스냅샷을 추가한다 -- AC1.
- `apps/batch/candidate_tags_repository.py` -- `CandidateTag.strategy` 타입 주석을 D/E 포함으로 갱신한다 -- 문서 정합성.
- `tests/batch/test_tags_stage.py` -- D/E 단독 태깅, A∩D 다중 태깅, params_meta에 D/E 파라미터 포함 검증을 추가한다 -- AC1, I/O 매트릭스 전체.

**Acceptance Criteria:**
- Given Story 6.3(스키마)·6.4(계산 API)가 완료된 상태에서 Story 2.5의 tagging stage가 실행되면, when 후보 종목에 A/B/C/D/E 중 하나 이상의 시그널이 발생하면, then 발생한 모든 전략이 `candidate_tags`에 다중 태그로 저장된다(예 A∩D).
- Given Story 6.5가 완료되어 전략별 TP/SL/최대보유 조회가 가능한 상태에서, when 이 태그가 Epic 3의 `emit_open_command`(publish_attempt 경유)에 전달되면, then 진입가·TP/SL 판정에 태그된 전략의 파라미터가 정확히 적용된다(이미 Story 6.5 SQL fixture로 검증 완료, 이번 스토리는 태그 생성만 추가).

## Review Triage Log

### 2026-09-07 — 독립 리뷰 4종(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)

- intent_gap: 0
- bad_spec: 0
- patch: 5: (high 0, medium 0, low 5)
- defer: 0
- dismissed:
  - `tags_stage.py` docstring이 "Story 2.5/6.6"으로, migration 주석이 "Story 6.3"으로 D/E 확장 출처를 다르게 표기한다는 지적 — 서로 다른 계층(오케스트레이터 vs DB CHECK 제약)의 출처 주석이라 실제 모순이 아니다.
  - `compute_abc` 이름을 그대로 쓰는 docstring이 오래됐다는 지적 — Story 6.4가 하위호환을 위해 함수명을 의도적으로 보존했으므로 정확한 표기다.
  - `_build_params_meta`가 `StrategyResult.params_meta`와 파라미터를 중복 기록해 드리프트 위험이 있다는 지적 — 두 값 모두 동일한 `STRATEGY_D_PARAMS`/`STRATEGY_E_PARAMS` 싱글턴 인스턴스에서 파생되며, A/B/C도 이미 동일한 이중 스냅샷 패턴(지표 파라미터는 `_build_params_meta`, 청산 파라미터는 `strategy_api`)을 쓰고 있어 이번 diff가 새로 만든 위험이 아니다.
  - 실제 `compute_abc`를 통한 end-to-end 테스트가 없다는 지적 — 기존 A/B/C 테스트도 전부 `FakeStrategyClient`로 격리돼 있는 이 파일의 기존 관례이며, `compute_abc` 자체의 D/E 계산 정확성은 Story 6.4의 `backtest/tests/test_strategy_api.py`/golden fixture 범위다.
  - `CandidateTag.strategy`에 런타임 가드가 없다는 지적 — 기존 A/B/C 시절부터 동일한 `str` 타입이며 Postgres CHECK가 저장 시점 권위 검증을 담당하는 기존 설계로, 이번 변경이 악화시키지 않았다.
  - 전략 조합 순서·vanished 태그의 D/E 커버리지 부족 지적 — `strategies` 리스트는 `_STRATEGY_KEYS` 순서를 그대로 따르는 기존 로직(변경 없음)이고, vanished 동기화는 Python 계층에서 전략을 인지하지 않는 순수 SQL RPC 위임(`sync_vanished`)이라 이 stage의 표면이 아니다.
- addressed_findings:
  - `[low]` `[patch]` `params_meta`에 `strategy_d_params`/`strategy_e_params` 키 존재만 검증하고 값은 검증하지 않아, 내용이 바뀌거나 비어도 통과할 수 있었다 — `STRATEGY_D_PARAMS.as_dict()`/`STRATEGY_E_PARAMS.as_dict()`와의 값 동등성 assertion으로 강화.
  - `[low]` `[patch]` 전략 E 단독 발생 케이스 회귀 없음 — `test_strategy_e_only_signal_is_tagged` 추가.
  - `[low]` `[patch]` A/B/C/D/E 5개 전략 동시 발생 케이스(Story 6.3 SQL fixture의 "5중 태그"에 대응하는 Python 계층 회귀) 없음 — `test_all_five_strategies_signal_on_same_ticker` 추가.
  - `[low]` `[patch]` 전략 D/E에 특정된 `SIGNAL_COMPUTE_ERROR` 분기 회귀 없음(에러가 A/B/C로 오귀속되거나 조용히 누락될 위험) -- `test_strategy_d_signal_compute_error_counts_as_error_not_silently_dropped` 추가.
  - `[low]` `[patch]` spec 초안의 실행 결과 문구가 "신규 D/E 태깅 테스트 4건"이라 적었으나 실제로는 diff에 신규 테스트 함수 2건 + 기존 테스트 assertion 보강만 있어 서술과 diff가 불일치했다 — 위 4건 보강을 반영해 최종 테스트 함수 5건(신규)으로 정정.

## Design Notes

`compute_abc`(6.4)·`candidate_tags` 스키마(6.3)·`emit_open_command`/`publish_attempt`(6.5)가 이미 A~E를 전략 키 개수에 무관하게 일반적으로 처리하도록 구현돼 있어, 실제 남은 gap은 `tags_stage.py`의 하드코딩된 3-전략 상수 하나였다. 계획 단계 조사에서 production Supabase가 Story 6.3~6.5의 migration(202609051200~202609052100) 중 다수를 실제로는 적용받지 못한 채(git에는 커밋/작성돼 있으나 미반영) 남아있던 것을 추가로 발견해, 이번 실행에서 순서대로 전부 재적용하고 관련 SQL fixture(`test_outcome_open_command.sql`, `test_candidate_tags.sql`, `test_outcome_rebuild.sql`)로 재검증했다(별도 커밋 `4bc2c98`).

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with httpx --with pytest pytest tests/batch tests/domain -q` -- expected: 신규 D/E 태깅 테스트 포함 전체 통과, 기존 회귀 없음.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 전략 계산 회귀 없음(compute_abc 미변경).
- `npm run typecheck` -- expected: 통과.
- `python tools/check_migration_order.py` -- expected: 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (Supabase MCP):**
- 운영 프로젝트 `qqhjeumlecaudsiqhhdu`: `candidate_tags`/`outcome_strategy_rules`/`emit_open_command` 관련 SQL fixture를 직접 실행해 전략 D/E 저장·조회·발행 경로가 명시적 PASS를 반환하는지 확인한다.

실행 결과:

- Production Supabase gap 발견 및 해소: Story 6.3~6.5의 migration 12건(`202609051200`~`202609052100`, 그중 2건은 기존에 커밋되지 않은 상태였음)이 실제로는 미적용 상태였다. 순서대로 전부 재적용(`mcp__supabase__apply_migration`)하고 커밋(`4bc2c98`)했다.
- `tests/sql/test_outcome_open_command.sql` 운영 실행 -- `pass`(D/E OPEN 파라미터 스냅샷·replay·SUSPENDED/DELISTED 재진입 가드 포함).
- `tests/sql/test_candidate_tags.sql` 운영 실행 -- 예외 없이 통과(A/B/C/D/E 5중 태그, UNIQUE/FK/RLS/CHECK 회귀 포함).
- `tests/sql/test_outcome_rebuild.sql` 운영 실행 -- `pass`(D/E 스냅샷 보존, malformed payload fail-closed 포함).
- `mcp__supabase__get_advisors(security)` -- 기존 baseline과 동일(신규 WARN/추가 EXECUTE 노출 없음).
- 독립 리뷰 4종(blind-hunter/edge-case-hunter/verification-gap/intent-alignment) 실행 -- low 5건 패치(테스트 커버리지 보강), dismissed 6건(위 Review Triage Log 참조), intent_gap·bad_spec·defer 없음.
- `uv run ... pytest tests/batch/test_tags_stage.py -q` -- 18 passed(신규 테스트 함수 5건: D/E 동시, A∩D 다중, E 단독, 5전략 동시, D 전략 SIGNAL_COMPUTE_ERROR 분기; 기존 params_meta 테스트는 값 동등성 assertion으로 보강).
- `uv run ... pytest tests/batch tests/domain -q` -- 208 passed(리뷰 패치 반영 후 재실행, 회귀 없음).
- `uv run ... pytest backtest -q` -- 131 passed(compute_abc 회귀 없음).
- `npm run typecheck` -- 통과.
- `python tools/check_migration_order.py` -- 47 files 통과.
- `git diff --check` -- 통과.
- Playwright MCP -- 이번 변경은 배치 파이썬 코드와 파라미터 스냅샷만 다루며 UI 표면이 없어 실행하지 않았다.

**추적 리뷰 권장:** patch 5건 전부 low → **권장함**(score = 1×5 = 5, 5 이상 기준 충족).

**잔여 리스크:** 없음. 발견된 유일한 실질 gap(production Supabase가 Story 6.3~6.5 migration을 일부 반영하지 못한 상태)은 이번 실행에서 전부 재적용·재검증했다.
