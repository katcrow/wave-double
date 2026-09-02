---
title: '오늘의 후보 카드 UI'
type: 'feature'
created: '2026-09-03'
status: 'in-review'
review_loop_iteration: 0
followup_review_recommended: false
baseline_revision: 'f00bb2365282e2efa40c92e2ee931733ad0010f5'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      `/strategies/[strategy]`, `page.tsx`의 카드 그리드/빈 상태 분기, `CandidateCard`/`StrategyTagList`
      렌더링 등 이번 스토리가 추가한 인증 보호 라우트의 통합 동작에 자동화된(e2e) 테스트가 없다.
    evidence: |-
      근본 원인은 이 스토리 이전부터 있던 저장소 전반의 제약이다 -- 이 리포에는 인증된
      세션을 발급하는 테스트 픽스처가 없어(Story 1.10부터 `e2e/manual-trigger.spec.ts`,
      `e2e/home.spec.ts`가 동일하게 문서화), 보호 라우트의 렌더링은 어떤 스토리에서도
      자동화된 적이 없다(DataTrustBar/NoticeBanner도 동일). 이번 스토리가 새로 만든 결함이
      아니라 기존 제약이 새 화면에도 그대로 적용된 것이다.
    location: e2e/home.spec.ts
    severity: low
---

<intent-contract>

## Intent

**Problem:** `/`는 항상 고정 빈 상태만 보여준다(Epic 1 Never 경계). 태깅된 후보(Story 2.5)를 카드로, 전략 태그를 배지로, 수급 부분결측(Story 2.6 `supply_3day.investor_net_status`)을 단서로 노출할 화면이 없다.

**Approach:** `get_dashboard_snapshot()`이 주는 run_id로 후보·태그·D0 수급상태를 조회하는 신규 RPC `get_today_candidate_cards(p_run_id)`를 추가하고, `/`에서 태깅된 후보가 있으면 카드 그리드로, 없으면 기존 빈 상태를 그대로 렌더링한다. 태그 클릭은 신규 `/strategies/[strategy]` 자리표시자 페이지로 이동하는 보조 액션이다.

## Boundaries & Constraints

**Always:**
- 신규 마이그레이션 `infra/supabase/migrations/202609022100_create_get_today_candidate_cards.sql`에 `get_today_candidate_cards(p_run_id uuid) returns jsonb`를 `get_dashboard_snapshot()`과 동일한 `security definer stable`로 생성하고 `anon, authenticated, service_role`에 grant한다. `candidates`를 `candidate_tags(status='active')`와 INNER JOIN(태그 없는 후보 제외), `supply_3day`(해당 candidate_id/attempt_run_id의 `slot='D0'` 행)와 LEFT JOIN한다. 각 후보를 `{ candidate_id, ticker, name, strategies: string[] (A/B/C, 정렬), supply_partial_missing: boolean }`로 반환한다.
- `supply_partial_missing`은 D0 행이 존재하고 `investor_net_status`가 `pending`/`missing`일 때만 true. D0 행이 아예 없으면(Epic 4 수집 미구현 상태) false — "부분결측"은 데이터 일부가 존재할 때의 상태이지 전체 부재가 아니다.
- `apps/web/app/page.tsx`: `complete_snapshot`이 있으면 `get_today_candidate_cards(complete_snapshot.run_id)`를 추가 호출한다. 반환 배열이 비어있지 않으면 카드 그리드를 렌더링하고 기존 `.empty-state` 블록은 렌더링하지 않는다. 비어있으면(또는 `complete_snapshot`이 없으면) 기존 `.empty-state`를 그대로 유지한다(`NoticeBanner`가 이미 배치 실패를 우선 노출하므로 추가 분기 불필요).
- `apps/web/lib/candidate-cards.ts`: RPC 원시 행 배열을 카드 뷰모델로 변환하는 순수 함수 `buildCandidateCardViewModels(rows)`. 태그 배지 "+N" 접힘은 고정 임계값 상수(`MAX_VISIBLE_TAGS = 2`)로 처리하는 순수 로직으로 구현 — 반응형 폭 측정(ResizeObserver 등)은 쓰지 않는다.
- `apps/web/app/strategies/[strategy]/page.tsx` 신규: `/tracking`과 동일한 자리표시자 패턴("전략 A 설명/성과 준비 중입니다." 등, strategy 파라미터가 A/B/C가 아니면 Next `notFound()`).
- 카드/태그 문구는 관찰 가능한 표현만 사용한다(예: "전략 A · 전략 C 시그널"). "강력 매수 신호" 등 확정적 표현 금지.
- `apps/web/lib/dashboard-types.ts`에 `TodayCandidateCardRow` 타입을 추가한다.
- `apps/web/app/globals.css`에 카드 그리드/전략 태그 배지 스타일을 기존 토큰(`--color-accent`, `--color-informational` 등)과 `.runs-card` 반응형 패턴을 참고해 추가한다.

**Never:**
- 카드 전체 클릭 시 근거 패널을 여는 상호작용(Story 4.6 범위), 당일 가격/등락률 표시(AC에 없고 `candidates` 테이블에 컬럼 없음), 장중 소멸 표시(Story 2.8)는 이번 스토리에서 구현하지 않는다.
- `get_dashboard_snapshot()`, `candidates`/`candidate_tags`/`supply_3day` 기존 테이블·마이그레이션은 수정하지 않는다(신규 RPC만 추가).
- `/strategies/[strategy]`에 실제 전략 설명/성과 콘텐츠를 채우지 않는다(자리표시자만).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 태깅 후보 존재 | 활성 태그 ≥1개인 후보 N건 | N개 카드 렌더, 각 카드에 종목명·코드·전략 태그 | No error expected |
| 다중 태그 | 후보 하나가 A/B/C 중 3개 태그 | 태그 2개 표시 + `+1` | No error expected |
| 부분결측 | D0 행 존재, `investor_net_status='pending'` | 카드에 "수급 일부 미수집" 단서 표시, 목록에서 제외 안 됨 | No error expected |
| D0 데이터 없음 | 해당 후보 D0 행 미존재 | 부분결측 배지 없음(정상) | No error expected |
| 태깅 후보 0건 | `complete_snapshot` 있음, 활성 태그 0건 | 기존 `.empty-state` 그대로 표시 | No error expected |
| 배치 실패 + 후보 없음 | `latest_attempt.status='failed'`, 태깅 후보 0건 | `NoticeBanner` 실패 문구가 상단에 우선 노출, 그 아래 빈 상태 유지 | No error expected |
| 태그 클릭 | `/strategies/A` 이동 | 필터링 없이 자리표시자 페이지로 네비게이션 | No error expected |

</intent-contract>

## Code Map

- `apps/web/app/page.tsx` -- `complete_snapshot.run_id`로 신규 RPC 호출 추가, 카드/빈 상태 조건부 렌더 (lines 10-51 현재 전체가 조건 없는 empty-state).
- `apps/web/lib/trust-bar.ts` -- `deriveTrustBarState()` 참고 패턴(순수 함수 + 상태 우선순위), 새 로직 스타일 기준.
- `apps/web/lib/trust-bar.test.ts` -- `node:test` + `assert/strict` + 빌더 헬퍼 패턴, `candidate-cards.test.ts` 작성 시 그대로 따른다.
- `apps/web/lib/dashboard-types.ts` -- `DashboardSnapshot` 등 기존 타입 정의 위치, `TodayCandidateCardRow` 추가 지점.
- `infra/supabase/migrations/202609021700_add_tags_to_publish_and_snapshot.sql` -- `get_dashboard_snapshot()` 최신본(run 선택/JSON 구성 패턴), 신규 RPC가 참고할 `security definer` 구조.
- `infra/supabase/migrations/202609022000_create_supply_3day.sql` -- `supply_3day` 스키마(컬럼/`investor_net_status` 계약), 신규 RPC의 LEFT JOIN 대상.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql` 인접 `202609020000_create_dashboard_snapshot.sql:104` -- grant 패턴(`anon, authenticated, service_role`) 참고.
- `apps/web/app/globals.css:368-407` -- `.runs-card`/`.runs-card__row` 반응형 카드 패턴, 신규 카드 그리드가 참고할 구조. `:4-19` 색 토큰, `:330-344` `.skeleton-card`(미사용, 참고 가능).
- `apps/web/app/tracking/page.tsx` -- 자리표시자 페이지 패턴(`/strategies/[strategy]`가 그대로 따를 구조).
- `apps/web/components/app-shell/AppShell.tsx:7-11` -- nav 항목 목록(이번 스토리에서 `/strategies`는 추가하지 않음, 태그 클릭으로만 도달).
- `apps/web/components/dashboard/NoticeBanner.tsx`, `apps/web/components/dashboard/DataTrustBar.tsx` -- 기존 대시보드 컴포넌트 배치/공존 순서 참고.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609022100_create_get_today_candidate_cards.sql` -- `get_today_candidate_cards(p_run_id uuid)` RPC 생성 + grant -- 카드 데이터 원천.
- `apps/web/lib/dashboard-types.ts` -- `TodayCandidateCardRow` 타입 추가 -- RPC 응답 타이핑.
- `apps/web/lib/candidate-cards.ts` -- `buildCandidateCardViewModels()` 순수 함수(+N 접힘, 부분결측 배지 여부 계산) -- 렌더 로직과 뷰모델 분리.
- `apps/web/lib/candidate-cards.test.ts` -- I/O 매트릭스 전 시나리오(다중 태그 +N, 부분결측 유/무) 유닛 테스트 -- 회귀 방지.
- `apps/web/components/dashboard/StrategyTagList.tsx` -- 전략 태그 배지 목록(+N, 클릭 시 `/strategies/[strategy]` 링크) -- UX-DR7 재사용 컴포넌트.
- `apps/web/components/dashboard/CandidateCard.tsx` -- 카드 1개 렌더(종목명·코드·태그·부분결측 단서) -- UX-DR4/UX-DR16.
- `apps/web/app/page.tsx` -- RPC 호출 + 카드 그리드/빈 상태 조건부 렌더 -- 화면 통합.
- `apps/web/app/strategies/[strategy]/page.tsx` -- 자리표시자 페이지 -- 태그 클릭 네비게이션 타깃.
- `apps/web/app/globals.css` -- 카드 그리드/태그 배지 스타일 추가 -- 시각적 일관성.
- `e2e/home.spec.ts` -- 로그인 세션에서 카드 렌더/빈 상태 케이스 e2e 보강(현재 인증 리다이렉트만 검증) -- 화면 통합 검증.

**Acceptance Criteria:**
- Given Story 2.5에서 태깅된 후보가 존재하는 경우, when `/`에 접속하면, then 태그를 가진 후보만 카드로 노출되며 카드에 종목명·코드·전략 A/B/C 태그가 표시된다.
- Given 후보가 다중 태그를 가진 경우, when 렌더링하면, then 태그가 가로 나열되고 임계값 초과 시 `+N`으로 접힌다.
- Given 태그를 클릭하는 경우, when 사용자가 상호작용하면, then `/strategies/{strategy}`로 이동한다(필터링 아님).
- Given 태깅된 후보의 D0 수급 데이터가 `pending`/`missing`인 경우, when 카드를 렌더링하면, then "수급 일부 미수집" 단서가 표시되고 카드가 목록에서 제외되지 않는다.
- Given 태깅된 후보가 없는 경우, when `/`를 열면, then 기존 빈 상태 문구가 그대로 표시된다(배치 실패 시 `NoticeBanner`가 우선 노출).

## Design Notes

- `MAX_VISIBLE_TAGS = 2` 고정 임계값 근거: 전략은 A/B/C 3종뿐이라 어떤 조합도 최소 지원 폭에서 한 줄에 들어간다. 3태그 케이스에서만 `+1`이 나타나며, 이는 유닛 테스트로 검증하고 실제 화면 폭 측정 로직은 만들지 않는다.
- `supply_partial_missing`은 D0 슬롯만 본다(카드 UI 문맥이 "오늘" 상태를 다루므로) — D-2/D-1 슬롯의 결측 여부는 이번 스토리 표시 대상이 아니다.

## Verification

**Commands:**
- `cd apps/web && node --test lib/**/*.test.ts` -- expected: `candidate-cards.test.ts` 포함 전체 통과.
- `cd apps/web && npx playwright test e2e/home.spec.ts` -- expected: 기존 미인증 리다이렉트 테스트만 변경 없이 통과(카드/빈 상태 렌더링 검증은 이 e2e에 추가되지 않았고, 아래 Manual checks로 수행한다).
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):**
- 신규 migration을 Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 직접 적용 후 `get_today_candidate_cards`를 실제 `run_id`로 호출해 반환 shape과 부분결측 계산을 확인한다(단일 프로젝트, 운영 적용이 곧 검증).

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7 (high 1, medium 2, low 4)
- defer: 1 (high 0, medium 0, low 1)
- dismissed:
  - `get_today_candidate_cards`가 RPC 응답을 런타임 검증 없이 unchecked cast(`as TodayCandidateCardRow[]`)한다는 주장(blind-hunter) — 바로 위 `get_dashboard_snapshot()` 호출도 동일한 패턴(`data as DashboardSnapshot`)을 이미 쓰고 있어 이 스토리가 새로 도입한 위험이 아니다.
  - `supabase.rpc()` 호출에 try/catch가 없다는 주장(edge-case-hunter) — 같은 파일의 기존 `get_dashboard_snapshot()` 호출도 동일하게 try/catch 없이 `{data, error}` 반환값만 확인하는 확립된 패턴이라 신규 위험이 아니다.
  - `revoke execute ... from public` 후 `anon/authenticated`에 grant하는 것이 사실상 no-op이라는 주장(blind-hunter) — Postgres는 함수 생성 시 기본적으로 PUBLIC 전체에 EXECUTE를 부여하므로, revoke는 그 기본 권한을 실제로 제거하고 이후 명시된 3개 role로만 좁히는 유효한 하드닝이다. 사실과 다른 지적.
  - `+N` 배지가 숨겨진 태그명을 알려줄 방법이 없다는 주장(blind-hunter) — 스펙 Design Notes가 이미 "고정 임계값 기반 순수 함수, 반응형 폭 측정 없음"으로 범위를 명시했고, 어떤 AC도 숨김 태그 공개를 요구하지 않는다.
  - 신규 JOIN 대상(`candidate_tags`, `supply_3day`)에 대한 인덱스 안내가 없다는 주장(blind-hunter) — Story 2.5/2.6 리뷰에서 이미 확정된 관례(접근 패턴이 정해지지 않은 인덱스는 후속 스토리가 필요에 맞게 추가)와 동일.
  - `/strategies/[strategy]`에 홈으로 돌아가는 링크가 없다는 주장(blind-hunter) — `apps/web/app/layout.tsx`가 모든 페이지를 `AppShell`로 감싸고, `AppShell`의 전역 nav가 모든 라우트에서 "/"(오늘의 후보) 링크를 상시 제공한다. 사실과 다른 지적.
- addressed_findings:
  - `[high]` `[patch]` `get_today_candidate_cards`의 `group by ... s.investor_net_status`가 `investor_net_status`를 그룹핑 키에 포함해, 동일 후보의 `supply_3day` D0 슬롯 행이 attempt 내에서 2건 이상(테이블 comment가 문서화한 정상적 누적 상태) 존재하면 같은 후보가 카드 배열에 중복 노출된다(blind-hunter + verification-gap, 동일 근본원인) — `distinct on (c.candidate_id) ... order by c.candidate_id, s.trading_day desc`로 후보당 최신 D0 슬롯 한 행만 선택하도록 서브쿼리를 재작성하고, 동일 후보에 D0 슬롯 2건(다른 trading_day, 다른 investor_net_status)을 시딩해 배열에 정확히 1건만 반환됨을 검증하는 SQL 회귀 테스트를 추가했다.
  - `[medium]` `[patch]` `/strategies/[strategy]`에서 `strategy` 라우트 파라미터가 `constructor`/`toString`/`hasOwnProperty` 등이면 `STRATEGY_LABEL[strategy]`가 `Object.prototype`에서 상속된 값(함수, truthy)을 반환해 `notFound()` 분기를 우회하고, 함수를 React 자식으로 렌더링하려다 런타임 오류로 페이지가 깨진다(edge-case-hunter) — `Object.prototype.hasOwnProperty.call()`로 own-property만 조회하도록 수정했다.
  - `[medium]` `[patch]` `get_today_candidate_cards` RPC가 실패하면 조용히 빈 상태로 폴백하면서 로그를 남기지 않고, `candidateCount`(전체 후보 수, 태그 무관)가 0보다 크면 "오늘 태깅된 후보가 없습니다"와 "참고용 · 오늘 태깅 후보 N건"이 동시에 표시되어 자기모순적으로 보인다(blind-hunter + edge-case-hunter) — RPC 실패 시 `console.error`로 로깅하고, 실패 케이스에서는 참고 카운트 텍스트를 렌더링하지 않도록 분리했다.
  - `[low]` `[patch]` `STRATEGY_LABEL` 매핑이 `StrategyTagList.tsx`와 `strategies/[strategy]/page.tsx`에 그대로 중복돼 있어 라벨이 바뀌면 어긋날 수 있다(blind-hunter) — `apps/web/lib/strategy-labels.ts`로 단일 출처를 추출해 양쪽에서 import하도록 정리했다.
  - `[low]` `[patch]` SQL이 이미 `order by t.strategy`로 정렬한 배열을 `buildCandidateCardViewModels`가 클라이언트에서 다시 `.sort()`하는 중복 연산이 있었다(blind-hunter) — SQL을 단일 출처로 유지하고 클라이언트 측 재정렬을 제거했다.
  - `[low]` `[patch]` `CandidateCard`가 종목명을 순수 `span`으로 렌더링해 카드 그리드에 스크린리더가 탐색할 시맨틱 헤딩 구조가 없었다(blind-hunter) — 종목명 요소를 `h2`로 바꾸고 기존 시각 스타일은 CSS로 유지했다.
  - `[low]` `[patch]` 스펙 Verification 절이 "e2e/home.spec.ts 보강된 카드/빈 상태 케이스 통과"라고 적어 실제로는 추가되지 않은 자동화를 한 것처럼 과장했다(intent-alignment + edge-case-hunter) — Verification 절 문구를 실제 수행 범위(기존 리다이렉트 테스트만 그대로 통과, 카드/빈 상태 검증은 Manual checks로 수행)에 맞게 정정했다.
