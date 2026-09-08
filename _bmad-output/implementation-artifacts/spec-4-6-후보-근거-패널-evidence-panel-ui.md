---
title: 'Story 4.6: 후보 근거 패널(Evidence panel) UI'
type: 'feature'
created: '2026-09-08'
status: 'done'
baseline_revision: '9b84cc2a09b6295da7572a717a11f13b635dba52'
baseline_commit: '9b84cc2a09b6295da7572a717a11f13b635dba52'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 현재 후보 카드는 종목명·전략·부분결측 단서만 보여 3일치 수급을 직접 확인할 수 없다. 후보를 열었을 때 데이터의 원천과 생성 시각을 한 번 확인하고, 실제 값과 미확정/미수집 상태를 구분할 수 있어야 한다.

**Approach:** 후보 카드가 접근 가능한 토글이 되도록 확장하고, 카드에 연결된 attempt의 후보 수급 근거를 새 read RPC로 한 번 조회해 Evidence panel에 주입한다. panel은 D0, D-1, D-2 순으로 정규화해 표 형태로 표시하며, 원천·생성 시각·결측 슬롯·상태 라벨을 UI에서 일관되게 렌더링한다.

## Boundaries & Constraints

**Always:** `candidate_id`와 `attempt_run_id`로 근거를 격리한다. 활성 태그 후보만 반환하고 후보 원천 provenance(t1859/t1852/t1856)를 보존하며 없으면 "기본"으로 표시한다. D0를 위에 두고 종가·거래량·등락률·외인·기관·개인·프로그램 순매수를 제공한다. `confirmed`의 실제 0은 0으로 표시하고 `pending`은 "미확정", `missing` 또는 없는 슬롯은 "미수집"으로 표시한다. 패널 열기/닫기는 클릭과 Enter/Space로 가능하고 포커스·aria-expanded·aria-controls를 제공한다. 기존 카드·배치 실패 우선 표시·태그 링크 동작은 유지한다.

**Never:** UI에서 수급 힌트나 금융 판단을 계산하지 않는다. 기존 테이블·기존 migration·`get_dashboard_snapshot()`·`get_today_candidate_cards()` 계약을 수정하지 않는다. 실제 전략 설명, 시장 전체 패널, 반응형 날짜별 카드 전환, 힌트 배지/필터는 이 스토리에서 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 후보 1개, D0/D-1/D-2 confirmed | 카드 토글로 panel을 열고 D0부터 3행과 7개 지표를 표시 | No error expected |
| PENDING | 행의 `investor_net_status=pending` | 네 순매수 칸은 "미확정"이고 숫자 0으로 표시하지 않음 | No error expected |
| MISSING | 행이 없거나 `missing` | 해당 슬롯이 "미수집"으로 시각 구분되고 부분결측 요약이 표시됨 | No error expected |
| FALLBACK_SOURCE | provenance가 t1852/t1856 | panel 상단에 실제 원천을 명시 | No error expected |
| EMPTY_OR_RPC_ERROR | 근거 행 없음 또는 read RPC 실패 | 카드와 panel은 유지하고 panel에 데이터 없음/로드 실패 상태 표시 | 오류를 console에 기록하고 빈 데이터를 정상 데이터로 위장하지 않음 |

</intent-contract>

## Code Map

- `apps/web/app/page.tsx` -- complete snapshot의 run_id로 카드 RPC와 별도로 근거 RPC를 호출하고 candidate_id별 evidence를 카드에 전달한다. 기존 실패/빈 상태 우선순위를 유지한다.
- `apps/web/components/dashboard/CandidateCard.tsx` -- 현재 server-only 카드. client 토글과 `CandidateEvidencePanel` 연결 지점이며, 전략 링크는 토글 이벤트와 충돌하지 않아야 한다.
- `apps/web/lib/dashboard-types.ts` -- `TodayCandidateCardRow`와 snapshot 타입이 있는 위치. evidence RPC 원시 행 타입을 여기에 둔다.
- `apps/web/lib/candidate-cards.ts` -- 카드 view model 순수 변환 및 테스트 패턴. evidence는 attempt 경계를 보존한 별도 map으로 연결한다.
- `apps/web/components/dashboard/StrategyTagList.tsx` -- 카드 내부 링크를 유지해야 하는 기존 interactive child.
- `apps/web/app/globals.css` -- dark console 토큰과 카드 그리드 스타일. panel/table의 상태·반응형·포커스 스타일을 여기에 추가한다.
- `infra/supabase/migrations/202609022000_create_supply_3day.sql`, `202609011700_create_candidates.sql` -- supply 컬럼/status와 candidate provenance의 read 계약. 기존 파일은 read-only다.
- `infra/supabase/migrations/202609081200_create_get_candidate_evidence.sql` -- 새 `get_candidate_evidence(p_run_id uuid)` security-definer read RPC 및 role grant를 forward-only로 추가한다.
- `tests/sql/test_get_candidate_evidence.sql`, `.github/workflows/test.yml` -- active 후보·3행 순서·source fallback·pending/missing/null/attempt 격리 SQL 회귀를 실제 fixture로 실행한다.
- `apps/web/lib/candidate-evidence.ts` 및 테스트 -- 슬롯 정규화, 상태 라벨, 숫자/시간 표시를 순수 함수로 분리해 UI 경계를 검증한다.
- `e2e/home.spec.ts` -- 인증 세션 fixture가 가능할 때 카드 토글/키보드/태그 링크의 브라우저 검증 지점. 현재 저장소 인증 제약이면 기존 redirect와 함께 명시적으로 skip 사유를 남긴다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609081200_create_get_candidate_evidence.sql` -- 활성 후보별 provenance와 attempt-scoped supply rows를 D0 우선 JSON으로 반환하는 RPC, search_path 고정, public 실행권한 회수 및 허용 role grant를 추가한다.
- [x] `apps/web/lib/dashboard-types.ts`, `packages/read-model/src/database.types.ts` -- evidence RPC의 후보/행 타입과 함수 시그니처를 추가한다.
- [x] `apps/web/lib/candidate-evidence.ts` -- D0/D-1/D-2 정규화, missing/pending 상태와 partial 요약, 안전한 표시 포맷을 순수 함수로 구현한다.
- [x] `apps/web/components/dashboard/CandidateEvidencePanel.tsx`, `CandidateCard.tsx` -- 접근 가능한 카드 토글과 source/collected-at 단일 헤더, 부분결측 배지, 근거 표를 구현한다.
- [x] `apps/web/app/page.tsx`, `apps/web/app/globals.css` -- RPC 응답 연결, 오류/빈 데이터 경계, dark responsive panel 스타일을 통합한다.
- [x] `apps/web/lib/candidate-evidence.test.ts`, `tests/sql/test_get_candidate_evidence.sql` -- I/O matrix와 attempt/source/status/정렬 경계를 회귀 검증한다.
- [x] `e2e/home.spec.ts` -- 실행 가능한 인증 fixture에서 클릭·Enter·상태 텍스트·태그 링크를 확인하고, 불가하면 인증 보호 라우트 제약을 기록한다.

**Acceptance Criteria:**
- Given 활성 후보와 3일 근거가 존재할 때, when 카드에서 Enter 또는 클릭으로 panel을 열면, then D0/D-1/D-2 순으로 종가·거래량·등락률·외인·기관·개인·프로그램 순매수가 표시된다.
- Given panel이 열릴 때, when 상단 메타를 렌더링하면, then 원천과 데이터 생성 시각이 값별 반복 없이 한 줄에 표시된다.
- Given pending/missing 또는 없는 슬롯이 있을 때, when panel을 렌더링하면, then 각각 "미확정"/"미수집"으로 표시되고 숫자 0과 구분되며 부분결측 요약과 결측 슬롯 스타일이 보인다.
- Given t1852/t1856 fallback provenance가 있을 때, when panel을 열면, then 해당 실제 원천이 표시된다.
- Given 배치가 실패했을 때, when 홈을 렌더링하면, then 기존 실패 알림 우선순위와 후보 카드 동작이 유지된다.
- Given 다른 attempt에 같은 candidate_id의 supply가 있을 때, when 근거 RPC를 호출하면, then 요청한 `p_run_id`의 행만 반환된다.

## Spec Change Log

## Review Triage Log

- 2026-09-08: 자동 리뷰어 서브에이전트를 사용할 수 없는 런타임이라 수동 diff·경계 검토로 대체했으며, 확정된 finding은 0건이다.

## Design Notes

근거 RPC는 카드 요약 RPC를 확장하지 않고 별도로 둔다. 그래야 기존 카드 응답 계약을 보존하면서 panel이 필요한 3일 행과 provenance를 한 번에 읽고, RPC 실패가 기존 후보 목록을 가리지 않는다. 없는 슬롯은 UI에서 정규화하되 실제 confirmed 0과 혼동하지 않도록 상태를 먼저 결정한다.

## Verification

**Commands:**
- `npm test` -- expected: web 순수 함수 테스트 통과.
- `npm run typecheck` -- expected: root TypeScript 검사 통과.
- `npm run build` -- expected: Next.js production build 통과.
- `npx playwright test e2e/home.spec.ts` -- expected: 인증 가능한 범위의 redirect 또는 panel 브라우저 검증 통과; 인증 fixture가 없으면 그 사실을 결과에 기록.
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):**
- Supabase 운영 프로젝트 `qqhjeumlecaudsiqhhdu`에 migration 적용 후 실제 fixture로 RPC 반환 shape, attempt 격리, source/status/정렬 결과를 확인한다.

## Suggested Review Order

**서버 데이터 연결과 격리**

- complete snapshot의 attempt로 별도 근거 RPC를 조회하고 기존 카드 실패 경계를 보존한다.
  [page.tsx:55](../../apps/web/app/page.tsx#L55)

- active 후보만 provenance와 슬롯별 최신 행으로 반환하며 함수 search_path와 권한을 고정한다.
  [migration.sql:6](../../infra/supabase/migrations/202609081200_create_get_candidate_evidence.sql#L6)

**근거 정규화와 접근성 UI**

- 카드 헤더를 키보드 가능한 토글로 만들고 태그 링크와 근거 패널을 분리한다.
  [CandidateCard.tsx:18](../../apps/web/components/dashboard/CandidateCard.tsx#L18)

- D0/D-1/D-2 고정 순서와 confirmed/pending/missing 표시 경계를 한 곳에서 결정한다.
  [candidate-evidence.ts:74](../../apps/web/lib/candidate-evidence.ts#L74)

- 원천·생성 시각 메타와 7개 지표 표를 상태별 시각 구분과 함께 렌더링한다.
  [CandidateEvidencePanel.tsx:24](../../apps/web/components/dashboard/CandidateEvidencePanel.tsx#L24)

- 다크 콘솔 표면, 포커스 링, 결측 행, 좁은 화면의 표 overflow를 확인한다.
  [globals.css:400](../../apps/web/app/globals.css#L400)

**회귀 증거와 타입 계약**

- confirmed 0, pending/missing, fallback, 중복 슬롯, 빈 응답 정규화 회귀를 확인한다.
  [candidate-evidence.test.ts:43](../../apps/web/lib/candidate-evidence.test.ts#L43)

- 운영 프로젝트에서 active 후보, provenance, 정렬, pending, attempt 격리를 실제 fixture로 검증한다.
  [test_get_candidate_evidence.sql:1](../../tests/sql/test_get_candidate_evidence.sql#L1)

- RPC 함수 시그니처와 브라우저 인증 제약의 검증 범위를 확인한다.
  [database.types.ts:691](../../packages/read-model/src/database.types.ts#L691)
  [home.spec.ts:10](../../e2e/home.spec.ts#L10)
