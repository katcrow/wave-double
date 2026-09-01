# Adversarial Review v2 — Architecture Spine wave-double V1

**Date:** 2026-08-31  
**Reviewer:** Adversarial Agent  
**Target:** ARCHITECTURE-SPINE.md (332 lines)  
**Method:** Construct two units one level down that obey every AD yet build incompatibly.

---

## Verdict
**CONDITIONAL PASS** — The spine closes the five previously-critical holes with AD-13/15/16/17/18, but three *new* cross-AD incompatibilities remain. Each is a pair of units that individually satisfy every AD yet diverge on shared data shape, ownership, or mutation path.

---

## Top 5 Findings

### 1. RA-01 residual: `latest_partial_run_id` vs `current_complete_run_id` pointer race
**Clash:** Unit A (orchestrator) publishes a **partial close run** (screen+tagging ok, supply_3day budget-exhausted) → writes `latest_partial_run_id`. Unit B (manual re-trigger) starts *same logical key*, succeeds fully → writes `current_complete_run_id`.  
**Incompatibility:** AD-13 allows partial to update `latest_partial_run_id`; AD-15 canonical selection prefers `success` → `fence_token` max. If Unit B's attempt_no=2 gets a *lower* fence_token than Unit A's attempt_no=1 (sequence gap from crashed attempt), Unit A remains canonical → **partial outcome leak**.  
**Gap:** AD-15 canonical rule does not forbid a *failed/partial* attempt from holding the max fence_token.  
**Fix:** Tighten AD-15: `canonical_attempt_run_id` MUST be a `success` attempt; fence_token ordering only among successes.

### 2. RA-02 residual: retry winner vs provenance split across `candidate_source_contrib`
**Clash:** Unit A (close attempt 1, t1859 source) succeeds screen+tagging, fails supply_3day → partial. Unit B (close attempt 2, t1852 fallback source) succeeds all stages → success, canonical.  
**Incompatibility:** AD-16 demands source column propagates to `candidate_tags`, `candidate_outcome`, `bias_metrics`, `candidate_source_contrib`. AD-15 says only canonical attempt's candidates create outcomes. Unit B's candidates carry source=t1852; Unit A's tags (t1859) persist in `candidate_tags` because AD-2 says tags table is append-only per run_id. **Outcome provenance shows t1852, but bias_metrics still sees t1859 tags from partial attempt** → source-slice divergence.  
**Gap:** AD-16 lacks a *cleanup/obsoletion* rule for tags/outcomes from non-canonical attempts.  
**Fix:** Add AD-19: non-canonical attempt rows in `candidate_tags`, `candidate_outcome`, `bias_metrics` MUST be marked `superseded_by_run_id` or deleted by canonical publish transaction.

### 3. RA-03 residual: state storage shape — `run_stages` vs `logical_runs` dual-write window
**Clash:** Unit A (orchestrator) writes `run_stages` row for `supply_3day` (status=running). Crashes before `logical_runs.latest_partial_run_id` update. Unit B (retry) acquires advisory lock, sees no `latest_partial_run_id`, starts fresh attempt_no=2. Unit A's stale worker recovers, writes `run_stages` success for attempt_no=1.  
**Incompatibility:** AD-3 fence_token check on *stage write* prevents stale write *if* fence_token is validated. But `run_stages` PK is `(run_id, stage)` — Unit A's run_id ≠ Unit B's run_id → **no PK conflict, both rows coexist**. Logical run now has two `supply_3day` stages from different attempts, one success one running. Read model (AD-13) joins on `current_complete_run_id` → undefined which stage wins.  
**Gap:** AD-3 fence_token is per-attempt; cross-attempt stage deduplication missing.  
**Fix:** Add unique constraint `(logical_run_key, stage)` on a *canonical stage view* or require orchestrator to delete prior attempt's stage rows on retry start.

### 4. RA-04 residual: production recovery contract — PITR vs `outcome_correction` event divergence
**Clash:** Unit A (restore drill) restores PITR to 02:00, replays close batch → new `run_id`, new outcomes. Unit B (manual correction) applies `outcome_correction` event at 03:00 on *original* DB for a ticker/strategy OPEN outcome.  
**Incompatibility:** AD-17 says "영향 행 수 > 1% 또는 다일간 누적이면 restore, 그 외 correction". But the *same* logical error (bad TP price) can be corrected via event on primary *and* re-appear via restore on staging. Metrics view (AD-8) aggregates both → **double-count or contradiction**.  
**Gap:** AD-17 lacks a *namespace* or *epoch* column to distinguish restored vs corrected outcomes.  
**Fix:** Require `outcome_correction` events to carry `restore_epoch` (incremented per PITR restore); metrics views filter by max epoch.

### 5. RA-05 residual: dispatch idempotency key scope collision across sub/route
**Clash:** Unit A (user Alice) POST `/api/runs/dispatch` with `idempotency_key="close-20260831"`, route_contract="close". Unit B (user Bob) same key, same route. AD-18 PK is `(sub, route_contract, idempotency_key)` → **no collision**.  
**Incompatibility:** GitHub Actions `concurrency.group` uses `logical_run_key` (trading_day+batch_kind+final). Both dispatches trigger *same* workflow → GitHub cancels first in-progress. AD-18 outbox reconciler sees first dispatch `succeeded` (GitHub accepted), second `unknown` (cancelled). Reconciler calls GitHub API, sees cancelled → marks `failed`. **Alice gets success, Bob gets failure for identical intent** — violates "same key+same hash = replay" semantics at workflow level.  
**Gap:** AD-18 idempotency scope is per-user; GitHub concurrency is global.  
**Fix:** Extend AD-18: idempotency key MUST include `logical_run_key` (or hash thereof) so cross-user same-intent maps to same GitHub concurrency group, or document that manual dispatch is single-user per logical run.

---

## File Path
`C:\dev\wave-double\_bmad-output\planning-artifacts\architecture\architecture-wave-double-2026-08-31\reviews\review-adversarial-v2.md`