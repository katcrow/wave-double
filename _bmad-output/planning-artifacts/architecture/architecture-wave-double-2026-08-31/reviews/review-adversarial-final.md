# Adversarial Review — ARCHITECTURE-SPINE.md (wave-double V1)

**Verdict: FAIL** — Two compliant implementations can still diverge on canonical attempt selection, provenance dual-write, and fencing token semantics. All prior findings (RA-01–RA-05, v3, v4) are **NOT fully resolved**; new critical gaps introduced.

---

## Top 5 Findings

### 1. AD-15/AD-19: Canonical Attempt Selection Race (CRITICAL)
**AD-15** declares publication transaction chooses `canonical_attempt_run_id` (must be `status='success'`).  
**AD-3** says orchestrator mutates `logical_runs` and marks prior attempts `superseded`.  
**AD-19** says canonical publish transaction *deletes* prior attempt provenance rows.

**Incompatibility:**  
- **Team A (Orchestrator-publisher):** Orchestrator ends success attempt → updates `canonical_attempt_run_id` → runs AD-19 cleanup in same transaction.  
- **Team B (Observer-publisher):** Separate publisher service watches `run_attempts.status='success'` → picks max `fence_token` success → runs publication + AD-19 cleanup.

Both obey every AD. **Result:** If two success attempts exist (e.g., manual re-run after auto success), Team B may pick the *later* attempt while Team A's orchestrator already canonized the *earlier* one. Provenance deletes diverge; `bias_metrics` and `candidate_outcome` become inconsistent. No AD specifies *who* runs publication or *when* relative to orchestrator commit.

---

### 2. AD-9/AD-16/AD-19: Dual Provenance Schema with No Reconciliation Rule (CRITICAL)
**AD-9:** `candidate_outcome.source_jsonb` = `{primary_source, sources:[{source,weight}]}`.  
**AD-16:** `candidate_source_contrib(candidate_id, source, contribution_weight, contrib_run_id, restore_epoch)`.  
**AD-19:** Canonical publish upserts **single row per candidate** in `candidate_source_contrib` with aggregated `sources` JSONB.

**Incompatibility:**  
- **Team A:** Writes primary source to `outcome.source_jsonb`; detailed weights only in `candidate_source_contrib`.  
- **Team B:** Writes full composite to `candidate_source_contrib`; leaves `outcome.source_jsonb` minimal (backfill only).

Both satisfy AD letter. **Result:** AD-8 read-model metrics (which must join one or the other) will compute different win-rates/PF per source slice. No AD mandates which is authoritative or a sync trigger.

---

### 3. AD-3/AD-17/AD-19: `restore_epoch` Propagation Gap (HIGH)
**AD-17:** PITR restore increments `restore_epoch` on **all provenance tables** via migration. Metrics views filter `WHERE restore_epoch = (SELECT MAX(restore_epoch) FROM candidate_source_contrib)`.  
**AD-19:** Adds `restore_epoch` to `candidate_source_contrib` only.  
**AD-9:** `candidate_outcome.source_jsonb` has **no `restore_epoch` column**.

**Incompatibility:**  
- **Team A:** Migration adds `restore_epoch` to `candidate_outcome` (and `candidate_tags`, `bias_metrics`) per "all provenance tables".  
- **Team B:** Touches only `candidate_source_contrib` as explicitly listed in AD-19.

Both compliant. **Result:** Post-restore, metrics views joining `candidate_outcome` (epoch 0) with `candidate_source_contrib` (epoch 1) return empty or duplicated slices. AD-17's "all provenance tables" vs AD-19's explicit list is contradictory.

---

### 4. AD-6/AD-12: `truncated_count` Semantic Split (HIGH)
**AD-6:** "절단은 실패/미처리가 아닌 관측 가능한 정상 경계이며 `runs.truncated_count`에 제외 수를 기록한다" — at **screen stage** (population cap 150).  
**AD-12:** Same column records exclusions; close batch compares backtest 104 signals vs candidate signals for `bias_metrics`.

**Incompatibility:**  
- **Team A:** `truncated_count` = candidates dropped at screen due to 150-cap (deterministic).  
- **Team B:** `truncated_count` = candidates dropped at *any* stage due to budget/time (API quota, partial).

Both obey AD text. **Result:** `bias_metrics` opportunity-loss calculation diverges; Team B inflates truncation, Team A reports only screen truncation. No AD defines *which stage* owns the counter.

---

### 5. AD-3/AD-18: `dispatch_idempotency` ↔ `run_id` Lifecycle Gap (MEDIUM)
**AD-18:** Idempotency keyed by `logical_run_key`; stores `github_dispatch_id` after dispatch.  
**AD-3:** `run_id` is UUID per attempt; `logical_run_key` stable; retry increments `attempt_no`.

**Incompatibility:**  
- **Team A:** `/api/runs/dispatch` inserts `dispatch_idempotency` row → calls GitHub → on success writes `github_dispatch_id` → orchestrator later creates `run_id` and links back.  
- **Team B:** `/api/runs/dispatch` inserts row *without* `run_id` → GitHub Actions workflow creates `run_id` → workflow updates `dispatch_idempotency.run_id` on start.

If GitHub accepts dispatch but workflow crashes before DB update: Team A has orphan `run_id` (never linked); Team B has `pending` dispatch with no `run_id`. Reconciler (AD-18) handles `pending` TTL but cannot distinguish "dispatch sent, run not started" from "dispatch failed". No AD defines the hand-off protocol.

---

## Previously Reported Issues — Status

| Issue | Status | Evidence |
|-------|--------|----------|
| RA-01 (AD-3 fencing vs advisory lock) | **PARTIAL** | AD-3 now forbids advisory-lock-only stale prevention but still uses it for serialization; fence_token check not mandated in every RPC signature |
| RA-02 (AD-15 canonical selection) | **UNRESOLVED** | Finding #1 above — who/when publishes is unspecified |
| RA-03 (provenance dual-write) | **WORSENED** | AD-9 + AD-16 + AD-19 create three overlapping columns with no sync rule |
| RA-04 (restore_epoch coverage) | **UNRESOLVED** | Finding #3 — outcome table missing epoch |
| RA-05 (truncated_count ambiguity) | **UNRESOLVED** | Finding #4 — stage ownership undefined |
| v3: dispatch idempotency gap | **PARTIAL** | AD-18 adds outbox/reconciler but lifecycle hand-off undefined (Finding #5) |
| v4: snapshot publication atomicity | **RESOLVED** | AD-13 + AD-19 now explicit on delete→upsert at publish |

---

## Recommendation
Do not green-light implementation. Add three binding ADs:
1. **AD-20** — Publication Authority: "Orchestrator exclusively runs publication transaction at success attempt commit; no external publisher."
2. **AD-21** — Provenance Single Source: "`candidate_outcome.source_jsonb` is deprecated; all source slices derived from `candidate_source_contrib` only. Migration backfills and drops `source_jsonb`."
3. **AD-22** — `restore_epoch` Universal: "Every table in provenance lineage (`candidates`, `candidate_tags`, `candidate_outcome`, `bias_metrics`, `candidate_source_contrib`, `outcome_observations`) carries `restore_epoch` NOT NULL DEFAULT 0; PITR migration increments all."