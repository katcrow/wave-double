# Epic 7 Context: 전략 확장 — 신규 후보 탐지 기법(F) 통합

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Extend the existing five-strategy candidate detection system (A/B/C/D/E) with a sixth strategy, F (각도 가속·이평선 쌍바닥 기법 — slope-acceleration + moving-average double-bottom), so that F's signals are computed and tagged OR-combined with the existing strategies on the same candidate population, and any candidate matching one or more of the six strategies is surfaced with multi-badge tagging. This is a Correct Course extension (2026-09-07) that reuses Epic 6's `candidate_tags` / `compute_abc` / `StrategyTagList` / per-strategy outcome parameterization infrastructure rather than reopening Epic 6. Sequencing matters: this epic must complete **before** Epic 4 Story 4.10 (hint badge unified filter) and Epic 5 Stories 5.6/5.12 (per-strategy view, metric comparison), otherwise those would be built on a five-strategy assumption and need rework. Within this epic, Story 7.1 (calculation logic committed to code) is a prerequisite for 7.2–7.6.

## Stories

- Story 7.1: 전략 F 계산 로직 코드화 & 백테스트 baseline 이식
- Story 7.2: `candidate_tags` 전략 제약 확장 (F)
- Story 7.3: 전략 계산 API 일반화 (AD-5 addendum 2 확장)
- Story 7.4: Outcome 판정 로직 F 파라미터화 (Epic 3/6 확장)
- Story 7.5: 후보 태깅 stage에 전략 F 반영
- Story 7.6: UI 확장 — 라벨·배지·라우트 (F)
- Story 7.7: OOS(워크포워드) 검증 — 전략 F

## Requirements & Constraints

- Strategy F must expose the same interface as A–E: daily-bar frame in, signal-ticker-set out. Entry condition: slope acceleration AND MA double-bottom neckline breakout. Exit condition: TP 3% / SL 4%, tp_first=True, no max holding period.
- Adopted params (표본 확대형/expanded-sample variant): slope_window=30, accel_window=5, min_slope_delta=0.004 (doc value 0.0045, code-reproduced value 0.004 — documented discrepancy), ma_db_window=16, cost_rate=0.0005.
- Code-reproduced backtest numbers (win rate 70.83%, PF 1.7178, 168 trades, ~2.30 trades/month) are authoritative over the source doc's numbers (73.1% / 1.92 / 182 trades / 2.8/month) — both exceed the acceptance bar (win rate > 50%, PF > 1), same pattern as D/E. (An earlier code run reported 70.10%/1.6585/194 trades before a Story 7.1 review pass fixed a double-bottom warmup-padding bug that fabricated a phantom first trough at segment restarts; the corrected numbers above are authoritative.)
- Strategy tagging must remain multi-label/OR-combined (e.g. a ticker can match both A and F simultaneously); DB tag storage, strategy calc API, and outcome judgment must all support this without breaking existing A–E behavior.
- All schema changes are forward-only expand-migrate-contract (AD-14): add/expand → backfill/dual-read → consumer cutover → contract in a later release. CI must verify clean `db reset`, N/N-1 compatibility, generated types, and SQL fixture parity.
- Historical A–E `candidate_outcome`/tagging data must remain immutable — no recomputation or re-judgment when F is added (NFR-5, past-data invariance).
- Strategy F must go through the same out-of-sample (walk-forward) validation as D/E before being trusted in production: in-sample 2020-08-03–2024-08-27, holdout 2024-08-28–2026-08-27. Until that validation completes, F's "OOS unverified" status must be tracked as an open risk (rated Medium in the 2026-09-07 correct-course proposal) and surfaced/updated once validation finishes.
- Badge/color accessibility: color alone must never be the only way strategies (or statuses) are distinguished — a text label (and, for status, icon/description) must always accompany color coding.

## Technical Decisions

- **AD-5 (shared strategy API), Addendum 2 (Epic 7):** `backtest.strategy_api.compute_abc(frame) -> StrategyResult` keeps its name for backward compatibility but its returned `StrategyResult` must now carry all six signal keys (A/B/C/D/E/F), each exposing its own signal ticker set plus its own exit parameters (TP/SL/max-holding) — extending the per-strategy exit-parameter structure Epic 6 already introduced, no new structure needed.
- New general-purpose signal helpers `_linreg_slope` and `_double_bottom_signal` (added to `backtest/indicator_opt/_signals.py` for Strategy F) must be reused by the shared prod/backtest calculation function (Story 7.3) — same reuse boundary principle as A–E: swap the data loader, never the indicator logic.
- `candidate_tags_strategy_check` constraint (currently `A|B|C|D|E` per `202609051500_finalize_candidate_tags_strategy_contract.sql`) must be expanded via forward-only migration to `A|B|C|D|E|F` without breaking existing rows/queries.
- `outcome_strategy_rules` (per-strategy TP/SL/max-holding lookup table from `202609051600_parameterize_outcome_strategy_rules.sql`) needs a new F row: `tp_pct=3, sl_pct=4`. Because both `outcome_strategy_rules.cutoff_n` and `candidate_outcome.cutoff_n` are `integer NOT NULL CHECK (cutoff_n > 0)`, "no max holding" cannot be stored as NULL. Convention: use a large sentinel integer (`999999`) to represent "unlimited" rather than altering the NOT NULL constraint. The existing `publish_attempt` comparison logic (`v_traded_days >= cutoff_n`, from Story 3.7) is reused unchanged — a sentinel this large never triggers TIMEOUT in realistic holding-period ranges.
- Golden fixture regression testing (Story 2.4/6.4 `golden_signals.json`) must add an F key, verified at the same Jaccard ≥ 0.9 threshold as A–E, with `strategy_f.py` as the reference implementation.
- `strategy_f.py` (`StrategyFParams`), the general signal helpers, and `test_strategy_f.py` (13 tests) already exist in the codebase as of the 2026-09-07 correct-course kickoff — Story 7.1's remaining scope is commit + final review only, not net-new implementation.

## UX & Interaction Patterns

- `apps/web/lib/strategy-labels.ts` (`STRATEGY_LABEL`) and `StrategyTagList.tsx` must be extended to include F alongside A–E: badges render horizontally, collapsing to a `+N` summary under narrow width.
- The `/strategies/[strategy]` route must accept an F path (rendering F's description/performance page) while continuing to 404 on undefined strategy codes.
- Badge color scheme additions for F must not rely on color alone to distinguish strategies — a text label must always accompany the color (accessibility rule also applied to batch failure/risk status elsewhere in the design).

## Cross-Story Dependencies

- Story 7.1 (F logic in code + backtest baseline) is a hard prerequisite for Stories 7.2–7.6.
- Story 7.2 (schema constraint expansion) and 7.3 (strategy API generalization) must both complete before Story 7.5 (tagging stage integration) can compute/store F tags.
- Story 7.4 (outcome rule parameterization for F) must complete before Story 7.5's tags can flow correctly into `emit_open_command` entry/exit judgment.
- Story 7.6 (UI labels/badges/routes) depends on Story 7.5 having real F-tagged data to display.
- Story 7.7 (OOS validation) may run in parallel with Story 7.5 for scheduling reasons, but its "OOS unverified" status must be tracked as an open risk until validation completes and the result is recorded.
- This entire epic is a hard prerequisite for Epic 4 Story 4.10 and Epic 5 Stories 5.6/5.12, which assume a six-strategy (not five-strategy) world.
