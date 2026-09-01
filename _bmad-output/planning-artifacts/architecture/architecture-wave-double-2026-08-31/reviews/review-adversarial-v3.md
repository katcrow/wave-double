# Adversarial Review v3 – ARCHITECTURE-SPINE.md (wave-double V1)

**Date:** 2026-08-31
**Reviewer:** Adversarial Architect (auto‑generated)

---

## 1. Verdict
**Conditional Pass** – All previously reported Critical issues **RA‑01 … RA‑05** are *addressed* in the current spine, but two latent incompatibility vectors remain that allow two conforming sub‑units to diverge at runtime.

---

## 2. Construction of Two “One‑Level‑Down” Units that Obey Every AD Yet Build Incompatibly

| Unit | Description | AD‑Compliance Highlights | Divergence Point |
|------|-------------|--------------------------|------------------|
| **U‑A – Python Batch Orchestrator** | `apps/batch` written in pure Python, uses the **canonical** `run_attempts.fence_token` sequence, writes stage rows via the *stage‑writer RPC* (`upsert_stage`) and publishes by setting `published_at` in the same transaction. | ✅ AD‑1 (port contract) <br>✅ AD‑3 (state machine, fence_token) <br>✅ AD‑5 (kernel reuse) <br>✅ AD‑9/15/16 (outcome & provenance) <br>✅ AD‑13 (atomic publish) <br>✅ AD‑18 (dispatch idempotency) | **Interpretation of `candidate_source_contrib`** – U‑A treats the table as *append‑only per attempt* and never deletes rows on retry; it only marks superseded attempts via `superseded_by_run_id` (AD‑19). |
| **U‑B – TypeScript Read‑Model / Dashboard Service** | `apps/web` + `packages/read-model` built in TypeScript, consumes the **published** snapshot only (`current_complete_run_id`). It materialises `bias_metrics_by_source` and `candidate_outcome` views by joining `candidate_source_contrib` **filtered to the latest `restore_epoch`** (AD‑17). | ✅ AD‑1 (read‑model contract) <br>✅ AD‑2/8 (single source of truth) <br>✅ AD‑10 (run‑id centric observability) <br>✅ AD‑13 (reads only published run) <br>✅ AD‑16 (provenance columns present) | **Assumption on `candidate_source_contrib` cardinality** – U‑B expects **exactly one row per candidate per canonical attempt** (i.e. the table is *deduped* at publish time). It therefore aggregates by `source` assuming uniqueness. |

Both units respect **every** AD as written:
* They never import each other's frameworks (AD‑1).
* They both use the same Supabase schema, migrations, and versioned views (AD‑2, AD‑14).
* They both honour the state‑machine, fence token, and publish rules (AD‑3, AD‑13, AD‑15).
* They both propagate `source` columns unchanged (AD‑16) and clean non‑canonical rows (AD‑19).

**Yet they diverge** because the spine does **not** prescribe:
1. **Whether `candidate_source_contrib` is deduplicated at publish** (AD‑19 only says *delete or mark superseded* – both actions satisfy the rule).
2. **Whether the `source` column in `candidate_outcome` is a single value or a composite (e.g., JSON array) when multiple fallbacks contributed** (AD‑15 explicitly *forbids* assuming a single `entry_candidate_id` can represent a union, but the schema still allows a single `source` text column).

Result: U‑A produces a **multi‑row** contribution set per candidate; U‑B reads a **single‑row** view → metrics differ, bias slices diverge, and downstream dashboards show contradictory win‑rates.

---

## 3. Status of Prior Critical Issues (RA‑01 … RA‑05)

| RA‑ID | Original Concern | Resolution in Current Spine | Residual Risk |
|------|------------------|-----------------------------|---------------|
| **RA‑01** | *Missing contract between batch and web for run‑state* | AD‑1, AD‑3, AD‑10, AD‑13 now define a **single canonical run pointer** and **port‑only** contract. | Low – contract exists, but **semantic ambiguity** of `candidate_source_contrib` (see §2). |
| **RA‑02** | *Idempotent dispatch could replay with different payload* | AD‑18 introduces `dispatch_idempotency` table with **request_hash** and dual‑write outbox/reconciler. | Low – solidified. |
| **RA‑03** | *Outcome table allowed multiple OPEN rows per ticker/strategy* | AD‑9 adds **partial unique index** `candidate_outcome_open_unique`. | Resolved. |
| **RA‑04** | *Provenance loss when fallback source replaces primary* | AD‑16 mandates `source` column on **four** tables and `candidate_source_contrib`; AD‑19 cleans superseded attempts. | **Partially resolved** – schema permits single `source` text; composite fallback not modelled (see §2). |
| **RA‑05** | *No guaranteed RPO/RTO / backup verification* | AD‑17 defines provider acceptance contract, PITR, restore drills, `restore_epoch` separation. | Resolved. |

**Bottom line:** RA‑01‑05 are **closed** at the architectural‑decision level, but RA‑01 and RA‑04 leave *implementation‑level* wiggle room that the adversarial units exploit.

---

## 4. Top Findings (2‑5)

1. **Ambiguous `candidate_source_contrib` lifecycle** – AD‑19 permits *delete* **or** *mark superseded*; no rule forces a *single canonical row per candidate* at publish. Leads to divergent aggregation (U‑A vs U‑B).
2. **`source` column remains scalar** – AD‑15 warns against assuming a single `entry_candidate_id` can represent a union, yet the DDL for `candidate_outcome.source` is a plain `TEXT`. Composite fallback provenance cannot be expressed without schema change.
3. **No explicit *publish‑time deduplication* rule** – The spine states “publish only on success” (AD‑13) but does not require the orchestrator to collapse `candidate_source_contrib` to one row per candidate. This is the root cause of Finding 1.
4. **`restore_epoch` only on `outcome_correction`** – AD‑17 ties epoch to corrections, but `candidate_source_contrib` and `bias_metrics` are not versioned by epoch; a PITR restore could re‑expose superseded rows unless they are also epoch‑filtered.
5. **Dispatch idempotency key scope** – AD‑18 ties `logical_run_key` to the *batch kind*; however *manual* and *scheduled* triggers for the same logical key can race because the reconciler runs only **once per minute**. A burst of manual clicks within that window could create two `pending` rows with identical `request_hash` (allowed) but different `sub` claims, both succeeding after reconciliation.

---

## 5. Recommendations (Actionable)

| # | Action | Owner | Target AD |
|---|--------|-------|-----------|
| 1 | Add **publish‑time deduplication** rule: orchestrator must `DELETE FROM candidate_source_contrib WHERE run_id <> canonical_attempt_run_id AND logical_run_key = …` before setting `published_at`. | Batch team | AD‑13 / AD‑19 |
| 2 | Change `candidate_outcome.source` to **`source_jsonb`** (or add `source_contrib_id` FK) to capture multiple fallback contributors. Add migration + backfill. | DB / Domain team | AD‑9 / AD‑15 |
| 3 | Extend `restore_epoch` column to **`candidate_source_contrib`** and **`bias_metrics`**; adjust views to filter by `MAX(restore_epoch)`. | DB team | AD‑17 |
| 4 | Tighten dispatch reconciler to **run on every `dispatch_idempotency` insert** (pg_notify / pg_cron 10 s) and enforce unique `(logical_run_key, sub, request_hash)` at DB level. | Platform team | AD‑18 |
| 5 | Document the **canonical contribution shape** in `packages/domain/run_rules.py` (e.g., `REQUIRED_CONTRIB_ROWS_PER_CANDIDATE = 1`). | Architecture | AD‑13 / AD‑16 |

---

## 6. File Reference
Review written to: `C:\dev\wave-double\_bmad-output\planning-artifacts\architecture\architecture-wave-double-2026-08-31\reviews\review-adversarial-v3.md`