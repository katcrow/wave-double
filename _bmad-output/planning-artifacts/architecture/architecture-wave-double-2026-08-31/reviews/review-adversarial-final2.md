# Adversarial Review (Final-2) — ARCHITECTURE-SPINE.md (wave-double V1)

**Verdict: CONDITIONAL PASS.** The reviewer-gate revision genuinely closes the prior CRITICAL gaps (canonical-selection race, dual provenance schema, `restore_epoch` propagation). Mechanism-level re-derivation, not just re-wording, confirms those fixes actually work. However, five new/residual ambiguities remain in the run/attempt state machine, dispatch idempotency, and the section/pointer vocabulary that two spec-literal implementations could resolve incompatibly. None are as severe as the prior CRITICALs; all are closable with small AD amendments.

---

## Verification of prior reviewer-gate fixes (do the mechanisms actually work?)

| Prior finding (review-adversarial-final.md) | Reviewer-gate fix (memlog) | Re-derivation in current spine text | Holds? |
|---|---|---|---|
| #1 Canonical attempt selected by two possible publishers (orchestrator vs external observer) → race | AD-20: "orchestrator만 publish_attempt RPC를 호출한다"; AD-15: only `active_attempt_run_id` + `ready_to_publish` attempt is a candidate | AD-20's RPC is a **serializable transaction that locks the logical row** and re-validates active/fence/lease before acting. Correctness comes from the DB transaction, not from process topology — even if two "orchestrator" instances raced to call the RPC concurrently, only one would win the row lock and the other would fail fence/active validation. This is a real fix, not just a naming rule. | **Yes** |
| #2 Dual provenance schema (`candidate_outcome.source_jsonb` + `candidate_source_contrib`, no sync rule) | AD-16/21: `source_jsonb` is deprecated then dropped; contrib table is sole store | Current AD-16 text: "`source_jsonb`는 필요 시 이 테이블에서 만드는 read projection이며 저장하지 않는다." Since it is never persisted, there is no second writable copy to drift — the dual-write is structurally impossible, not merely discouraged. | **Yes** |
| #3 `restore_epoch` propagation gap (paid PITR assumption inconsistent across tables) | AD-17 rewritten to drop paid PITR entirely | Current AD-17 uses `pg_dump`+age encryption+quarterly restore drill; **no `restore_epoch` column exists anywhere in the current spine**. The whole concept that caused the propagation gap was removed rather than patched, which eliminates the class of bug outright. | **Yes** |
| #4 `truncated_count` semantic split (screen-cap vs any-stage) | AD-6 rewritten: 150-cap truncation is explicitly the screen-stage boundary | AD-6 text now scopes truncation entirely to the 150-candidate selection step; AD-10 separately defines `unprocessed_count`/`truncated_count` as distinct fields with distinct meanings for other failure modes. | **Yes** |
| #5 Dispatch/`run_id` handoff protocol undefined | AD-18 rewritten around `dispatch_request`/`dispatch_outbox`, workflow-first-step receipt | Mostly fixed (single RPC creates both rows atomically), but see **Finding 2** below — a residual race remains in the receipt-check-before-resend path. | **Partially** |

So four of five prior CRITICAL/HIGH findings are cleanly closed by mechanism, and the fifth is improved but not fully closed (detailed below).

---

## New Findings

### 1. AD-3: reaper's "정책상 재개 가능한 `ready_to_publish`" is an undefined policy — two teams build different orphan-recovery behavior

AD-3's Rule text: *"heartbeat가 만료된 attempt는 reaper가 `failed` 또는 정책상 재개 가능한 `ready_to_publish`로 CAS 처리한다."*

No AD anywhere defines what "정책" (the policy) is. This is a genuine binary branch left to the implementer:

- **Team A** (conservative): reaper always CAS's an orphaned attempt to `failed`. Simple, safe, but wastes LS API budget on every crash/restart since a full retry is required (interacts with AD-6's 30-minute budget — repeated failures can starve later attempts into `RATE_LIMIT_EXHAUSTED`).
- **Team B** (optimistic): reaper inspects `stage_status`; if every AD-20 pre-publish-required stage already reports `success`, it CAS's to `ready_to_publish`, letting a later orchestrator publish an attempt whose owning worker never got to call publish itself.

Both literally satisfy the AD-3 sentence — it explicitly names both target states as legal reaper outcomes and defers the choice to "policy." Because this determines whether a crashed-but-actually-finished run becomes visible data or a forced retry, it is a genuine cross-team behavioral divergence, not a cosmetic one: a batch-side team and a dashboard/ops-side team building against this spine independently would disagree about whether "orphaned lease" ever yields publishable data. **Fix:** AD-3 should state the concrete condition (e.g., "iff all AD-20 required pre-publish stages report `success`" ) rather than leaving "policy" unbound.

### 2. AD-18: receipt-check-before-resend does not close the GitHub `workflow_dispatch` acceptance-but-not-yet-started window

AD-18 Rule: *"응답 유실 시 receipt를 먼저 조회하고 확인 전에는 재발송하지 않는다."* The receipt is written by the **workflow's first step**, i.e., it can only exist once the dispatched GitHub Actions run has actually started executing.

`workflow_dispatch` is fire-and-forget: GitHub returns 204 with no run identifier, and there is a real (sometimes multi-second, occasionally much longer under GitHub Actions queue pressure) delay before the triggered run's first step executes and writes the receipt. If the outbox worker's lease expires during exactly this window (e.g., process killed right after the GitHub call returned success but before it persisted `accepted`/`started` locally), a second worker instance claims the row via `FOR UPDATE SKIP LOCKED`, queries for a receipt, **finds none yet** (because the run hasn't started), and — per the stated rule — proceeds to redispatch. This produces a genuine second GitHub Actions run for the same `logical_run_key`, not just a duplicate DB row. The `concurrency.group` at the GitHub level (AD-3) will queue or cancel the duplicate depending on `cancel-in-progress`, which the spine does not pin — but either way this is a real dispatch sent twice to an external system, spending workflow-minutes and confusing operators, which is exactly the class of bug AD-18 exists to prevent. The rule conflates "response lost" with "response received but not yet observable via receipt," and the mechanism does not distinguish them. **Fix:** either require the outbox worker to persist "GitHub call issued" as a durable fact *before* the HTTP call (so a crash after a successful call is detectable as "unknown, do not resend" rather than "retriable"), or require `cancel-in-progress: true` to be pinned so a duplicate dispatch is at least neutralized at the GitHub layer.

### 3. AD-13: "section" is shared vocabulary between `packages/read-model` and `apps/web` but its taxonomy is never fixed

AD-13's Rule: *"section 하나는 오직 하나의 `run_id`에서 읽으며 UI는 각 section의 run/time/status를 표시한다."* `get_dashboard_snapshot()` must return `available_partial_sections`/`missing_sections` keyed by section — but the spine never enumerates what a "section" *is* (per-capability: candidates/tags/supply/market/outcome? or per-UI-surface: header/table/detail?). This is the one piece of shared contract shape AD-13 claims to fix (`get_dashboard_snapshot()`'s return shape), yet its granularity is undefined.

Two independently-built teams — one owning `packages/read-model`/SQL (batch/backend side) and one owning the Next.js dashboard (web side) — could each read AD-13 literally and land on different partitions: a backend team naturally partitions by capability/stage (5+ sections matching CAP-1..7 stages), while a frontend team naturally partitions by rendered UI block (2-3 coarser sections). Since `get_dashboard_snapshot()` is the one RPC contract meant to unify both sides, an undefined section taxonomy means the function's actual return shape is not fixed by the spine at all, despite AD-13's stated purpose of preventing "row mixing across sections in one screen." **Fix:** AD-13 (or a table in Consistency Conventions) should enumerate the canonical section list once (even if just "one section per CAP-*, plus `outcome`").

### 4. AD-3/AD-9/AD-15/AD-20: `canonical_success_run_id` scope across `batch_kind` is not pinned

AD-3 defines `logical_runs.canonical_success_run_id` as a generic field alongside `current_complete_run_id`. AD-15 talks about "한 logical run의 canonical winner" generically across "AD-3/9/12/13/20." But AD-4 states outcome is confirmed **only by the close batch** ("close 배치만 outcome을 확정"), and AD-9's append-only ledger events are produced only by "AD-20의 canonical close publication." Nothing in the spine restricts *which `batch_kind`s populate `canonical_success_run_id`* versus which only ever populate `current_complete_run_id`.

- **Team A** could implement `canonical_success_run_id` as populated only for `batch_kind='close'` logical runs (since that's the only kind with an outcome/provenance concept worth calling "canonical"), leaving it `NULL` for premarket/intraday.
- **Team B** could implement it uniformly — every successfully-published attempt of every `batch_kind` gets a `canonical_success_run_id`, treating the field as a generic "the winning attempt for this logical key," since AD-15's binding list (AD-3/9/12/13/20) never says "close only."

If Team B's semantics ships, any provenance/outcome join written against the assumption "a populated `canonical_success_run_id` implies outcome events exist" (which several ADs' prose implies, e.g. AD-16/21's `*_by_source` views) would silently pick up premarket/intraday runs that have no corresponding `outcome_events`, unless every join also filters `batch_kind='close'` — a filter the spine never states as mandatory. **Fix:** AD-3 or AD-15 should state explicitly whether `canonical_success_run_id` is close-scoped or universal, and if universal, that all outcome/provenance joins must additionally filter `batch_kind='close'`.

### 5. AD-16/AD-19: whether `candidate_id` is itself attempt-scoped is implied, not stated — leaves the PK's redundancy ambiguous

AD-16's PK for `candidate_source_contrib` is `(candidate_id, attempt_run_id, source)`. AD-19 requires attempt-scoped `candidates` rows to be preserved (not overwritten) across retries, tagged by `attempt_run_id`. This only reads as fully consistent if `candidate_id` is **itself minted per-attempt** (i.e., the same ticker in two different attempts of the same logical run gets two different `candidate_id`s) — in which case `attempt_run_id` in the contrib PK is functionally redundant with `candidate_id`, which is a code smell but not a bug.

The alternative reading — a `candidate_id` that is a stable identity for "this ticker within this logical run" reused/updated across attempts — is nowhere ruled out by explicit wording (only implied by AD-19's "삭제하지 않는다" instruction, which a careless implementer could satisfy by inserting a *new* row per attempt while still treating `candidate_id` as reused-and-versioned via a separate `version`/`attempt_run_id` column pair, rather than a fresh UUID per attempt). Two teams could genuinely diverge on whether `candidate_id` is globally unique-per-attempt or a stable per-(logical_run,ticker) identity, which changes whether downstream consumers can safely use `candidate_id` alone as a join key anywhere outside the canonical view. **Fix:** state explicitly in AD-16 or AD-19 that `candidates.candidate_id` is minted fresh per attempt (never reused across `attempt_run_id`s for the same ticker).

---

## Not re-flagged (confirmed resolved, no new angle found)
- Dispatch idempotency key scoping (client-supplied key + server-computed canonical payload hash) is well-specified: same key+hash always replays regardless of which team builds the client vs. the RPC, since the hash is computed server-side.
- AD-5's same-candle TP/SL tie-break (SL priority) is now singly defined in AD-5 only, not duplicated with conflicting text elsewhere.
- `outcome_observations` identity `(outcome_id, evaluation_trading_day)` with retry returning the existing row is unambiguous and idempotent as written.

---

## Recommendation
Ship-blocking: none of the five findings rise to the severity of the prior CRITICALs (all are containable with a one-sentence AD clarification each, no schema rework required). Recommend closing Findings 1, 2, and 4 before implementation starts on AD-3/AD-18/AD-20, since those three touch the run-state machine and dispatch path that every other capability depends on; Findings 3 and 5 can be resolved during the first read-model/UI integration story without blocking cold-start.
