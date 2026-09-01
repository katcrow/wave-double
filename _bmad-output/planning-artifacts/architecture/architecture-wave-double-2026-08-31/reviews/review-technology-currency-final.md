# Review: Technology Currency — ARCHITECTURE-SPINE.md Stack & Structural Seed

Reviewed against real release history as of 2026-09-01. Verdict: **discrepancies found** — one entry names a version that does not exist, one entry is stale/deprecated, others check out.

## Findings

### 1. Next.js 16.3.4 — DOES NOT EXIST (hallucinated)
Real release history: Next.js 16.3 shipped 2026-08-03; the patch chain is 16.3.1 → 16.3.2 → 16.3.3 (latest stable as of 2026-09-01). 16.3.4 has not been published; the only newer builds are 16.4.0-canary.x (pre-release, not stable). The spine should cite **16.3.3** or accept the risk of pinning an unreleased patch.

### 2. HTTPX 0.28.1 — STALE, NOT CURRENT (fails "2026-09-01 confirmed current" claim)
0.28.1 was released 2024-12-06 — roughly 21 months before the spine's stated confirmation date. It is not the current stable release; encode/httpx has continued past 0.28.x (a 1.0 dev line exists: 1.0.dev5, 2026-08-21). This entry reads like a stale/pre-cutoff value carried over rather than something re-verified for 2026-09-01, and directly contradicts the spine's own framing text ("2026-09-01 공식 지원 상태를 확인한 cold-start seed").

### 3. @supabase/ssr 0.12.5 — DOES NOT EXIST
Latest published version on npm is **0.12.4** (published ~2026-08-06, "25 days ago" relative to an 2026-08-31 lookup). 0.12.5 was not found; only pre-release candidates like 0.12.4-rc.146 exist. Likely a hallucinated patch bump. Note also the version-line inconsistency: `@supabase/supabase-js` is pinned at a high patch (2.112.4) while `@supabase/ssr` sits at a low 0.x line — this is normal for these two packages (independent versioning schemes), not itself a defect, but the specific 0.12.5 value is wrong.

### 4. Peer-consistency check: Next.js 16 / React 19.2.x — OK
Next.js 16 requires React 19.2+ in the App Router; React 19.2.8 (real release, 2026-07-21) satisfies that floor. No inconsistency here once Next.js is corrected to an actual 16.3.x patch.

### 5. Entries verified as real and current
- **Python 3.12.14** — real (released 2026-08-12); correctly a security-only legacy release per PEP 693 (3.12 is past feature freeze, still receiving fixes through 2028). Fits its stated role as a pinned interpreter version.
- **pandas 3.0.5** — real (released 2026-07-22), latest patch in the 3.0.x line (3.0.0 shipped 2026-01-21).
- **NumPy 2.5.2** — 2.5.0 confirmed real (released 2026-06-21); the specific .2 patch wasn't individually confirmed via search but the 2.5 line is current and supports Python 3.12–3.14, consistent with the Python 3.12.14 pin.
- **PyArrow 25.0.1** — real (released 2026-08-10, bugfix release following 25.0.0 on 2026-07-10).
- **Node.js 24.20.0 LTS** — real (released 2026-08-26), Node 24 ("Krypton") is in active LTS through ~April 2028. Correct fit for an LTS pin.
- **Playwright 1.62.1** — real (released 2026-07-30, patch fixing regressions in 1.62.0 from 2026-07-24).
- **GitHub Actions `ubuntu-24.04` runner** — real and current; Ubuntu 22.04 runner images are entering deprecation (starting 2026-09-17), reinforcing that 24.04 is the correct current choice, not a stale one.
- **@supabase/supabase-js 2.112.4** — real (published 2026-08-24, ~3 days before the spine's 2026-08-31 authoring date), changelog entries (auth lock warnings, postgrest codegen fixes) are consistent with an actively maintained fast-moving 2.x line.
- **TypeScript 5.9.3** — real, but note it is an older patch: released 2025-10-01, i.e. nearly a year before the spine's 2026-09-01 date. TypeScript's 5.9 line may have later patches or a newer minor (5.10/6.0) by Sep 2026 that would be more "current"; this wasn't fully cross-checked against the latest TS release and is worth a follow-up look — flagged as a **possible staleness risk**, not confirmed hallucination.

## Summary Table

| Entry | Status |
| --- | --- |
| Python 3.12.14 | Verified real, correct role (legacy security release) |
| pandas 3.0.5 | Verified real, current patch |
| NumPy 2.5.2 | Line verified real/current; exact patch not individually confirmed |
| HTTPX 0.28.1 | Real but **stale** (Dec 2024) — not current as of 2026-09-01 |
| PyArrow 25.0.1 | Verified real, current patch |
| Node.js 24.20.0 LTS | Verified real, current LTS |
| Next.js 16.3.4 | **Does not exist** — latest stable is 16.3.3 |
| React/react-dom 19.2.8 | Verified real, current, compatible with Next.js 16 |
| TypeScript 5.9.3 | Real but possibly stale (dated Oct 2025) — needs re-check against Sep 2026 latest |
| @supabase/supabase-js 2.112.4 | Verified real, current |
| @supabase/ssr 0.12.5 | **Does not exist** — latest is 0.12.4 |
| Playwright 1.62.1 | Verified real, current |
| ubuntu-24.04 runner | Verified real, current, correct choice vs. deprecating 22.04 |

## Recommendation
Update the spine table before treating it as a cold-start authority:
- Next.js: 16.3.4 → 16.3.3 (or re-verify against whatever is latest at implementation time)
- @supabase/ssr: 0.12.5 → 0.12.4
- HTTPX: re-pin to whatever is actually current in the 0.28.x/1.0.x line at implementation time, not 0.28.1
- TypeScript: spot-check for a newer 5.9.x patch or minor before lockfile generation
