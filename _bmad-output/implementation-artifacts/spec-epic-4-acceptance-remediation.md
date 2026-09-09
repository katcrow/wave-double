---
title: 'Epic 4 운영 수용성 반려 사유 해결'
type: 'bugfix'
created: '2026-09-09'
status: 'done'
review_loop_iteration: 0
baseline_commit: 'f9773704c9eac78452561a34bfb6a23174bac860'
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-retro-09-09-2026.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 4의 후보 근거 RPC가 미발행 attempt를 읽을 수 있고, t1702 비유한 수치가 저장 경계를 통과하며, Evidence 종가의 수정주가 기준이 불명확하다. 인증된 후보·시장 UI와 에픽별 변경 범위도 자동 증거가 없어 회고 수용 판정을 통과하지 못했다.

**Approach:** published/current-complete read 경계와 후보 거래일 조인을 forward-only migration으로 고정하고 SQL negative fixture를 추가한다. 외부 수치와 SupplyRow invariant를 강화하고, t1702 원자료 종가와 adjusted daily_ohlcv 종가를 명시적으로 분리해 Evidence에는 adjusted 종가와 adjusted 등락률만 노출한다. 결정론적 인증 UI fixture와 에픽 경로 manifest 검사를 추가해 운영 수용 증거를 반복 실행 가능하게 만든다.

## Boundaries & Constraints

**Always:** 기존 migration은 수정하지 않는다. 공개 read RPC는 published/current-complete이며 해당 stage가 success인 attempt만 반환한다. 후보 evidence slot은 후보의 trading_day와 일치해야 한다. NaN/Infinity는 adapter와 저장 dataclass 양쪽에서 거부하고 한 후보 오류가 다른 후보를 막지 않는다. Evidence 종가·등락률은 adjusted daily_ohlcv를 진실 원천으로 사용하며 원자료 누락은 안전하게 미수집으로 표시한다. 테스트 fixture는 rollback한다. 운영 Supabase 프로젝트 `qqhjeumlecaudsiqhhdu`와 저장소의 Playwright 규칙을 사용한다.

**Never:** 기존 migration을 재작성하거나 raw t1702 close를 adjusted 값으로 가장하지 않는다. 인증을 우회하는 production 경로를 추가하지 않는다. 인증 UI fixture를 운영 데이터에 의존시키지 않는다. Epic 7 파일을 Epic 4 증거에 포함하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| PUBLISHED_COMPLETE | published run, current_complete pointer, supply success, adjusted OHLCV 3일 | evidence 3행, adjusted close/등락률 반환 | 정상 |
| UNPUBLISHED_OR_PARTIAL | running/partial/non-current run with supply rows | evidence `[]` | SQL fixture가 노출을 실패 처리 |
| DAY_MISMATCH | slot date differs from candidate date | mismatched slot omitted | 안전한 missing 표시 |
| MALFORMED_NUMBER | t1702 NaN/Infinity 또는 invalid SupplyRow | 해당 후보만 partial/unprocessed | 후보 오류 집계, 전체 stage 중단 금지 |
| AUTH_UI_FIXTURE | deterministic authenticated mock session and RPC payload | cards, evidence, filter, both market tabs at desktop/mobile/200% | fixture contract failure |

</frozen-after-approval>

## Code Map

- `infra/supabase/migrations/202609081201_harden_get_candidate_evidence_attempt_scope.sql` -- 현재 evidence RPC의 보안-definer 구현. 새 migration에서 published/current-complete, supply success, candidate-day, adjusted OHLCV join을 재정의한다.
- `tests/sql/test_get_candidate_evidence.sql` -- RPC 권한·attempt 격리·slot 선택 fixture. published/partial/unpublished 및 날짜 불일치 negative case를 추가한다.
- `apps/batch/ls_supply_provider.py` -- t1702 파서. `math.isfinite` 기반 숫자 계약과 malformed row 오류 경계를 추가한다.
- `apps/batch/supply_3day_repository.py`, `apps/batch/supply_stage.py` -- 저장 행 invariant와 후보 단위 오류 격리 지점이다.
- `tests/batch/test_ls_supply_provider.py`, `tests/batch/test_supply_3day_repository.py`, `tests/batch/test_supply_stage.py` -- finite/invariant/partial 회귀망이다.
- `apps/web/components/dashboard/CandidateEvidencePanel.tsx`, `apps/web/lib/candidate-evidence-view.ts` -- adjusted 종가 기준 표시와 evidence 렌더 계약이다.
- `e2e/authenticated-dashboard.spec.ts`, `e2e/mock-supabase-server.mjs`, `e2e/start-test-web.mjs` -- 운영 인증을 우회하지 않는 결정론적 로컬 세션/RPC UI fixture다.
- `tools/check_epic_scope.py`, `.github/workflows/test.yml` -- 지정 revision과 허용 경로의 커밋·파일 범위를 검사한다.

## Tasks & Acceptance

**Execution:**
- [x] evidence RPC forward migration과 SQL fixture를 구현한다.
- [x] t1702/SupplyRow finite·invariant 및 후보 단위 partial 처리를 구현한다.
- [x] adjusted OHLCV 기반 Evidence read projection과 UI 설명을 구현한다.
- [x] 인증된 deterministic Playwright smoke와 responsive/market/filter 검사를 추가한다.
- [x] per-epic scope manifest 도구와 CI 실행을 추가한다.
- [x] 운영 migration/catalog/advisor/fixture 증거와 전체 테스트를 재실행하고 Epic 4 회고·action item을 갱신한다.

**Acceptance Criteria:**
- Given non-published, non-current, partial, 또는 supply 실패 attempt, when `get_candidate_evidence`를 호출하면, then 빈 배열이고 anon/authenticated 직접 table SELECT는 계속 차단된다.
- Given candidate와 다른 trading_day의 slot, when evidence를 읽으면, then 해당 slot은 반환되지 않는다.
- Given t1702에 비유한 값이 있으면, when stage가 처리하면, then 해당 후보만 unprocessed/partial이고 정상 후보 행은 저장된다.
- Given adjusted OHLCV가 있으면, when Evidence를 렌더링하면, then 종가와 등락률은 adjusted 기준이며 화면에 기준이 명시된다.
- Given fixture 로그인 상태, when HomePage를 1280px, 375px, 200% 확대에서 열고 조작하면, then 카드 근거·복합 필터·KOSPI/KOSDAQ 탭과 URL 보존이 통과한다.
- Given Epic 4 revision/path manifest, when scope checker를 실행하면, then Epic 7 변경은 제외·보고되고 허용 경로 밖 변경은 실패한다.

## Spec Change Log

- 2026-09-09: 운영 catalog 대조에서 Epic 4 원본 migration 누락을 확인해 운영 `qqhjeumlecaudsiqhhdu`에 순서대로 적용했고, 원본 migration이 remediation 함수를 덮지 않도록 `202609091200_reapply_candidate_evidence_read_boundary`를 추가했다.
- 2026-09-09: 첫 adjusted OHLCV bar에서 raw t1702 `change_pct`로 fallback하는 경로를 제거하고, `202609091300_strict_adjusted_evidence_rate`를 운영 catalog에 적용했다. 이전 adjusted bar가 없으면 해당 evidence slot은 반환하지 않는다.

## Review Triage Log

- Independent reviewer layers: unavailable in this runtime; inline review performed against the working tree, callers, production REST/Management API evidence, and all listed verification commands.
- Kept: initial rejection findings A1-A6/B1-B3 are each covered by the implementation and verification evidence below; no unresolved consequence remains in the Epic 4 acceptance scope.
- Dismissed: Supabase advisor warnings for intentional anon/authenticated read RPC execution are not a search-path or privilege regression; the SQL fixture separately proves direct table SELECT remains revoked and RPC grants are explicit.
- Dismissed: zero candidates in the live close snapshot is valid `candidates=success` with `candidate_count=0`; it does not invalidate market-supply acceptance, which has two actual market rows and a published complete snapshot.

## Design Notes

`daily_ohlcv.close`는 t8410 `sujung=Y`로 적재되는 adjusted canonical price다. t1702는 공식 요청 스키마에 `sujung`이 없으므로 t1702의 close를 adjusted라고 주장하지 않는다. 수급·거래량은 t1702 원자료를 유지하되, Evidence read projection에서 adjusted daily bar와 adjusted 이전 bar가 모두 존재하는 날짜만 가격과 adjusted 전일 대비율을 제공한다. 어느 bar라도 없으면 해당 slot을 반환하지 않아 raw 가격·등락률을 잘못 노출하지 않는다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/ -q` -- all Python tests pass.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- backtest regression passes.
- `npm test && npm run typecheck && npm run build` -- web tests, types, build pass.
- `npm run test:e2e -- authenticated-dashboard.spec.ts` -- authenticated fixture UI checks pass.
- `python tools/check_migration_order.py && python tools/check_epic_scope.py ...` -- migration and scope contracts pass.
- production Supabase migration/catalog/advisor/fixture checks -- explicit pass rows. The
  configured Supabase MCP endpoint was bound to a different project URL, so the required
  `qqhjeumlecaudsiqhhdu` production checks used the official Supabase Management API fallback.

**Observed production evidence (2026-09-09, project `qqhjeumlecaudsiqhhdu`):**

- `close:2026-09-09` published complete run: `c6ea80aa-91fe-4468-8dc1-2d7766b0cf9d`; all stages including `market_supply` and `outcome_tracking` are `success`, `missing_sections=[]`.
- KOSPI: foreign `-1086`, institution `883`, individual `-601`, program `-1294`; KOSDAQ: foreign `5648`, institution `-153`, individual `-4905`, program `5995`. Both rows have trading day `2026-09-09` and the same collection timestamp.
- Production SQL fixtures: `story_4_6_candidate_evidence: pass`, `story_4_8_market_supply_read: pass`.
- Production migration catalog contains the eight missing Epic 4 migrations plus `202609091100_harden_candidate_evidence_read_boundary`, `202609091200_reapply_candidate_evidence_read_boundary`, and `202609091300_strict_adjusted_evidence_rate`.
