# Architecture Spine Review — wave-double V1

Reviewed file: `ARCHITECTURE-SPINE.md` (updated 2026-09-01)
Reviewer stance: independent audit against the good-spine checklist (divergence coverage, AD enforceability, Deferred safety, capability coverage, dimension completeness, internal consistency).

## Verdict: PASS-WITH-NOTES

The spine is unusually disciplined for a V1 document: 21 ADs each name a concrete divergence, a mechanism that closes it (RPCs, fence tokens, partial unique indexes, append-only tables, transaction boundaries), and cross-reference each other coherently (AD-3/AD-9/AD-13/AD-15/AD-19/AD-20 form one consistent run-lifecycle story; AD-16/AD-21 form one consistent provenance story). No internal contradictions were found. One real gap and a couple of minor notes below keep this from a clean pass.

## Finding 1 (real gap) — Golden-fixture parity precondition (사후조정/배당) is not decided, deferred, or flagged as an open question

`spec-wave-double/backtest-baseline.md:98` and `api-map.md:58` both explicitly flag, with `[검증 필요]`, that the backtest kernel uses yfinance dividend-adjusted (`auto_adjust=True`) prices while the production OHLCV ingestion path uses LS `t8410`/`t8451` with a `sujung` flag whose adjustment semantics (commonly split-only in KR practice) are unconfirmed against yfinance's. The spec text says this discrepancy check is **"FR-3 골든 픽스처 회귀 대조의 선행 조건"** — i.e., it gates the very parity mechanism AD-5 relies on.

AD-5's whole purpose is "운영 수식이 백테스트와 따로 진화... 방지," and its Rule leans on golden-fixture Jaccard ≥ 0.9 as the enforcement gate. AD-5 does mention "corporate-action adjustment version 변경 시 영향 구간을 재구축한다" — but that only covers *re-processing when the adjustment version changes*, not *whether the two runtimes' adjustment methodology is equivalent in the first place*. This is exactly the kind of "implementation unit built independently" divergence the spine is supposed to fix: the LS-adapter author and the backtest-kernel author could each proceed on different adjustment assumptions and only discover the mismatch after tagging silently diverges from backtest, defeating NFR-6.

This should be either (a) resolved as a decision (e.g., "adopt LS sujung as authoritative; backtest fixture is regenerated against it" or similar), or (b) added to **Deferred** with an explicit re-verification trigger (mirroring how the ATR(14) gate and Python-stack-promotion items are handled) — e.g., "사전 실측 대조 없이 golden fixture 배포를 통과시키지 않는다." As written it is silent, which is the failure mode the checklist calls out ("a whole dimension left silent... is a finding") applied at the AD level rather than the environmental-envelope level.

## Finding 2 (minor) — AD-5 golden-fixture gate has no owner for the precondition above

Related to Finding 1: AD-5's Rule states the Jaccard gate blocks deploy, but doesn't state what happens if the *fixture itself* is suspect (i.e., built on an unverified adjustment assumption). A one-line addition tying the gate to "adjustment-parity 실측 확인 후에만 유효" would close this without a new AD.

## Finding 3 (minor) — Operational alerting is implicit, not explicit

AD-10 gives visibility (`result_code`, dashboard-visible run states) and AD-17 gives backup-failure notification ("실패를 알린다"), but there's no explicit statement of what happens when a scheduled batch fails or falls into `ORPHANED_ATTEMPT`/`NO_SNAPSHOT` outside of the dashboard being checked — i.e., is failure surfaced only by the single operator pulling `/runs`, or is there a push channel? Given this is a single-operator, free-tier hobby-scale system and the UX spec centers on a `/runs` dashboard, a pull-only model is a defensible product decision — but the spine doesn't say so explicitly, so it reads as a silent dimension rather than a decision. Recommend one sentence (either in AD-10 or Deferred) confirming "no push alerting in V1; operator polls `/runs`" so a future implementer doesn't wonder whether they're supposed to build a notification channel.

## Checklist walk-through

- **Divergence points for the level below**: Well covered. Batch concurrency/idempotency (AD-3, AD-18, AD-20), time semantics (AD-4), strategy-kernel parity (AD-5, modulo Finding 1), LS budget/canonicalization (AD-6), auth/secret boundary (AD-7), read-model authority (AD-8), outcome ledger (AD-9), observability vocabulary (AD-10), dev/prod data boundary (AD-11), bias/cap accounting (AD-12), snapshot publication atomicity (AD-13), migration discipline (AD-14), single-winner semantics (AD-15), provenance shape (AD-16), backup/restore (AD-17), non-canonical retention (AD-19), publish authority (AD-20), source-of-truth for source-sliced metrics (AD-21). No missing divergence point was found beyond Finding 1.
- **Enforceability of each Rule**: Each Rule names a concrete mechanism (RPC signature, index, transaction boundary, fixture gate, CAS transition) rather than a policy statement. AD-7's Rule is checked by a list of concrete verifications (JWKS claims, CSRF, rate limit, idempotency) — enforceable. AD-14's Rule is checked by CI (`db reset`, N/N-1, fixture parity) — enforceable. No Rule reduces to an unenforceable aspiration.
- **Deferred safety**: All five Deferred items either (a) have a stated default/fallback behavior for V1 (hosting: none yet, but nothing else depends on the choice before the "배포 story"; cross-TR parallelization: forbidden by default per AD-6; snapshot retention: 90-day default; ATR gate: kept as-is; Python-stack promotion: pinned exact versions in Stack table serve as the default, with a documented downgrade+spine-update path on failure), or (b) are pinned to an explicit re-trigger condition. None leaves two independently-built units free to silently diverge.
- **Named tech currency**: Out of scope per instructions (separate reviewer).
- **Spec capability coverage**: SPEC/data-model/api-map/backtest-baseline/PRD/UX sources are all reflected — cross-checked api-map.md and backtest-baseline.md directly; the one capability-relevant risk flagged in those specs that is *not* reflected in the spine is the adjustment-parity issue (Finding 1). The intraday all-zero investor-flow guard from api-map.md IS correctly reflected in AD-4 ("당일 수급이 전부 0이면 재시도 후... partial"). The TR-budget-sharing uncertainty from api-map.md IS correctly reflected in AD-6's Rule and the Deferred cross-TR-parallelization entry.
- **Dimension completeness (feature altitude)**: Deployment & environments — decided partially (GitHub Actions runner pinned, dev/prod boundary in AD-11) and explicitly deferred where undecided (Next.js hosting provider, with a resolution trigger). Infra/provider strategy — decided (Supabase as sole operational-data owner AD-2, GitHub Actions as dispatch/batch executor AD-3/18/20). Operations — backup/restore decided in detail (AD-17), observability decided (AD-10), but alerting/failure-surfacing is only implicit (Finding 3, minor). No dimension is entirely silent.
- **No AD-to-AD contradiction**: Checked the run-lifecycle cluster (AD-3/9/13/15/19/20) and the provenance cluster (AD-16/21) line by line; pointer names (`active_attempt_run_id`, `canonical_success_run_id`, `current_complete_run_id`, `latest_partial_run_id`) and state vocab (`running/ready_to_publish/published`, `partial/failed/skipped/superseded/cancelled`) are used consistently everywhere they appear. No contradiction found.

## Summary

- **Verdict**: pass-with-notes
- **Top findings**:
  1. (Real gap) The yfinance-vs-LS-`sujung` dividend-adjustment parity question, which the source specs flag as a precondition for AD-5's golden-fixture gate, is not decided, deferred, or raised as an open question anywhere in the spine.
  2. (Minor) AD-5's fixture gate should state it's contingent on that adjustment-parity check having been run.
  3. (Minor) Failure/operational alerting beyond dashboard polling is implicit, not stated as a decision.
- Everything else — divergence coverage, AD enforceability, Deferred safety, capability-map alignment, and internal AD-to-AD consistency — checks out.
