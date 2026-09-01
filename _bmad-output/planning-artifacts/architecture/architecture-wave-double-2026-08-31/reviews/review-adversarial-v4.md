# Adversarial Review v4 – ARCHITECTURE-SPINE.md (wave-double V1)

**Date:** 2026-08-31
**Reviewer:** Adversarial Architect

---

## 1. Verdict
**Conditional Pass** – All prior Critical issues (RA‑01 … RA‑05) are *closed at the AD level*, and three of five v3 findings are resolved by new ADs (AD‑17/18/19). **Two latent incompatibility vectors remain** that let two conforming sub‑units diverge at runtime.

---

## 2. Construction of Two “One‑Level‑Down” Units that Obey Every AD Yet Build Incompatibly

| Unit | Description | AD‑Compliance Highlights | Divergence Point |
|------|-------------|--------------------------|------------------|
| **U‑A – Python Batch Orchestrator** | `apps/batch` written in pure Python, uses the canonical `run_attempts.fence_token` sequence, writes stage rows via the stage‑writer RPC (`upsert_stage`), publishes by setting `published_at` in the same transaction. On publish it **deletes then regenerates** `candidate_source_contrib` for the logical run (AD‑19). For composite fallbacks it inserts **multiple rows per candidate** with `contribution_weight`. | ✅ AD‑1 (port contract) <br>✅ AD‑3 (state machine, fence_token) <br>✅ AD‑5 (kernel reuse) <br>✅ AD‑9/15/16 (outcome & provenance) <br>✅ AD‑13 (atomic publish) <br>✅ AD‑17 (restore_epoch on contrib) <br>✅ AD‑18 (dispatch idempotency) <br>✅ AD‑19 (forced delete→regenerate) | **Interpretation of `candidate_outcome.source`** – U‑A writes the *primary* source (highest weight) to the scalar `source` column, but the *full* composite breakdown lives only in `candidate_source_contrib`. |
| **U‑B – TypeScript Read‑Model / Dashboard Service** | `apps/web` + `packages/read-model` built in TypeScript, consumes only the published snapshot (`current_complete_run_id`). Materialises `bias_metrics_by_source` and `candidate_outcome` views by joining `candidate_source_contrib` filtered to `MAX(restore_epoch)` (AD‑17). Expects **exactly one `candidate_source_contrib` row per candidate** in the canonical attempt. | ✅ AD‑1 (read‑model contract) <br>✅ AD‑2/8 (single source of truth) <br>✅ AD‑10 (run‑id centric observability) <br>✅ AD‑13 (reads only published run) <br>✅ AD‑16 (provenance columns present) <br>✅ AD‑17 (epoch‑filtered views) <br>✅ AD‑19 (assumes deduplicated contrib) | **Assumption on `candidate_source_contrib` cardinality** – U‑B aggregates by `source` assuming uniqueness per candidate. When U‑A produces multiple rows (composite fallback), U‑B’s `SUM(contribution_weight)` double‑counts or mis‑attributes, yielding divergent win‑rate / PF slices. |

Both units respect **every** AD as written:
* They never import each other's frameworks (AD‑1).
* They both use the same Supabase schema, migrations, and versioned views (AD‑2, AD‑14).
* They both honour the state‑machine, fence token, and publish rules (AD‑3, AD‑13, AD‑15).
* They both propagate `source` columns unchanged (AD‑16) and clean non‑canonical rows (AD‑19).
* They both epoch‑filter provenance tables (AD‑17).
* They both use the hardened dispatch idempotency path (AD‑18).

**Yet they diverge** because the spine does **not** prescribe:
1. **Whether `candidate_source_contrib` is guaranteed single‑row per candidate at publish** – AD‑19 mandates *delete→regenerate* but does not forbid the canonical attempt itself from inserting multiple rows per candidate (composite fallback). The AD text says “candidate당 단일 canonical source contrib 행만 존재함을 보장한다” but the schema and regen logic allow multiples.
2. **Whether `candidate_outcome.source` remains a scalar `TEXT`** – AD‑15 explicitly warns “outcome projection의 단일 entry_candidate_id만으로 source별 slice를 만들 수 있다는 가정을 금지한다”, yet the DDL in AD‑9/16 still defines `source TEXT NOT NULL`. Composite fallback provenance therefore cannot be expressed in the outcome row itself; it lives only in the contrib table, which U‑B assumes is already deduped.

Result: U‑A produces a **multi‑row** contribution set per candidate for composite fallbacks; U‑B reads a **single‑row** view → metrics differ, bias slices diverge, dashboards show contradictory win‑rates.

---

## 3. Status of Prior Critical Issues (RA‑01 … RA‑05)

| RA‑ID | Original Concern | Resolution in Current Spine | Residual Risk |
|------|------------------|-----------------------------|---------------|
| **RA‑01** | Partial publish vs last-success snapshot pointer conflict | AD‑10/13 now separate `current_complete_run_id` (success only) and `latest_partial_run_id`; AD‑13 forbids partial from moving the complete pointer. | **Resolved** – pointer contract is explicit and monotonic. |
| **RA‑02** | Dispatch idempotency could replay with different payload | AD‑18 introduces `dispatch_idempotency` with `request_hash`, UNIQUE `(logical_run_key, route_contract, request_hash)`, outbox + reconciler. | **Resolved** – dual‑write gap closed, hash‑bound replay. |
| **RA‑03** | Outcome allowed multiple OPEN rows per ticker/strategy | AD‑9 adds partial unique index `candidate_outcome_open_unique`. | **Resolved**. |
| **RA‑04** | Provenance loss when fallback replaces primary | AD‑16 mandates `source` on four tables + `candidate_source_contrib`; AD‑19 cleans superseded attempts at publish. | **Partially resolved** – schema still has scalar `source` on `candidate_outcome`; composite fallback not representable in outcome row (see §2). |
| **RA‑05** | No guaranteed RPO/RTO / backup verification | AD‑17 defines provider acceptance contract (RPO ≤1h, RTO ≤4h, PITR, restore drills, `restore_epoch` separation). | **Resolved**. |

**Bottom line:** RA‑01‑05 are **closed** architecturally, but RA‑04’s implementation‑level wiggle room (scalar `source`) is the root of Finding 1 below.

---

## 4. Status of v3 Findings

| v3 Finding | Current Spine Status | Resolved? |
|------------|----------------------|-----------|
| 1. Ambiguous `candidate_source_contrib` lifecycle (delete vs mark) | AD‑19 now **forces delete→regenerate** at canonical publish. | **Yes** – ambiguity removed. |
| 2. `source` column remains scalar | AD‑9/16 still define `candidate_outcome.source TEXT NOT NULL`. AD‑15 warns but no schema change. | **No** – still scalar. |
| 3. No explicit publish‑time deduplication rule | AD‑19 mandates delete→regenerate **for non‑canonical attempts**, but does not constrain the canonical attempt’s own contrib cardinality. | **Partially** – non‑canonical cleaned, canonical may still be multi‑row. |
| 4. `restore_epoch` only on `outcome_correction` | AD‑17 now adds `restore_epoch` to `candidate_source_contrib` and `bias_metrics`; views filter by `MAX(restore_epoch)`. | **Yes** – epoch extended to provenance tables. |
| 5. Dispatch idempotency reconciler window | AD‑18 specifies pg_cron 10 s or GH Actions 30 s; UNIQUE on `(logical_run_key, route_contract, request_hash)` prevents duplicate pending rows. | **Mostly** – small burst window remains but duplicate insert is blocked by DB unique constraint. |

---

## 5. Top Findings (2‑5)

1. **`candidate_outcome.source` is still scalar `TEXT`** – AD‑15 forbids assuming a single `entry_candidate_id` can represent a union, yet the DDL keeps a single `source` column. Composite fallbacks (multiple TRs contributing to one candidate) cannot be expressed in the outcome row; they exist only in `candidate_source_contrib`, which the read model assumes is already deduped. **This is the direct cause of the U‑A vs U‑B divergence.**

2. **No rule forcing *canonical attempt* `candidate_source_contrib` to be single‑row per candidate** – AD‑19 guarantees cleanup of *non‑canonical* attempts, but the canonical attempt may legally insert multiple rows per candidate (one per contributing source with `contribution_weight`). The spine never says “each candidate has exactly one contrib row in the canonical attempt”. U‑B’s aggregation therefore over‑counts or mis‑attributes.

3. **`candidate_source_contrib` lacks a uniqueness constraint for the canonical attempt** – The table PK is `(candidate_id, source, contrib_run_id)`. A composite fallback creates multiple rows with different `source` values for the same `candidate_id` and `contrib_run_id`. No constraint or publish‑time collapse to a single composite row exists.

4. **Dispatch reconciler still has a sub‑minute race window** – AD‑18’s pg_cron 10 s (or GH Actions 30 s) means two manual clicks within that window can both insert `pending` rows with identical `request_hash` (allowed by unique constraint) but different `sub`. Both may succeed after reconciliation, creating duplicate GitHub dispatches for the same logical run.

---

## 6. Recommendations (Actionable)

| # | Action | Owner | Target AD |
|---|--------|-------|-----------|
| 1 | Change `candidate_outcome.source` to **`source_jsonb`** (or add `source_contrib_id` FK to `candidate_source_contrib`) to capture multiple fallback contributors. Add migration + backfill. | DB / Domain | AD‑9 / AD‑15 |
| 2 | Add **publish‑time canonical deduplication** rule: orchestrator must collapse `candidate_source_contrib` to **one row per candidate** in the canonical attempt (e.g., aggregate weights into a JSONB `sources` column or a single composite row). Enforce with a partial unique index on `(contrib_run_id, candidate_id) WHERE contrib_run_id = canonical_attempt_run_id`. | Batch / DB | AD‑13 / AD‑19 |
| 3 | Document the **canonical contribution shape** in `packages/domain/run_rules.py` (e.g., `REQUIRED_CONTRIB_ROWS_PER_CANDIDATE = 1`). | Architecture | AD‑13 / AD‑16 |
| 4 | Tighten dispatch reconciler to **run on every `dispatch_idempotency` insert** via `pg_notify` + lightweight worker, eliminating the 10‑30 s window. Keep DB unique constraint as safety net. | Platform | AD‑18 |

---

## 7. File Reference
Review written to: `C:\dev\wave-double\_bmad-output\planning-artifacts\architecture\architecture-wave-double-2026-08-31\reviews\review-adversarial-v4.md`