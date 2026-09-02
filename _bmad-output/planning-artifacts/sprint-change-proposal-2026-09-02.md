---
date: '2026-09-02'
trigger_story: '1.10 (인증 & 수동 트리거)'
scope: 'minor'
status: 'implemented'
---

# Sprint Change Proposal — 인증 방식 전환 (OTP/매직링크 → 사전 등록 슈퍼유저 + 비밀번호)

## 1. Issue Summary

**문제:** Story 1.10에서 AD-7("브라우저는 단일 운영자 세션과 읽기 권한만 가진다")에 따라 Supabase Auth email OTP/magic link 방식으로 인증을 구현했다(`이미 done`). 그러나 이 프로젝트는 Neo 1인만 사용하는 개인 운영 도구이고, 외부 회원가입 플로우가 애초에 없다. OTP/매직링크는 매번 로그인마다 이메일 왕복이 필요해 1인 운영 맥락에서 불필요한 번거로움을 만든다.

**발견 경위:** story 1.11(호스팅 배포) 완료 직후, Neo가 "OTP 로그인은 안 했으면 좋겠다. 회원가입 없이 Supabase에 슈퍼유저 하나 등록해서 쓰면 될 것 같다"고 요청.

**이슈 유형:** 원래 요구사항에 대한 오해가 아니라, 구현이 끝난 뒤 드러난 "1인 운영에 맞지 않는 선택" — 즉 실제 사용 맥락과 맞지 않는 완료된 결정의 재검토(전략적 pivot에 가까운 소규모 조정).

## 2. Impact Analysis

**Epic 영향:** Epic 1(배치 자동화 인프라 & 오늘의 후보 모집단) 하나의 스토리(1.10)만 영향받는다. Epic 자체의 목표·범위·순서에는 변화가 없다 — "브라우저는 단일 운영자 세션과 읽기 권한만 가진다"는 AD-7의 근본 취지(비인가 실행 방지, secret 비노출)는 그대로 유지되고, 오직 세션 발급 메커니즘만 바뀐다.

**Story 영향:**
- Story 1.10(done) — 인증 메커니즘 변경. AC 문구·구현 코드·spec의 Spec Change Log 갱신 필요.
- Story 1.11(done) — `docs/deployment.md`의 ⑥번 "인증 필요 화면 수동 확인" 절차가 OTP 이메일 수신을 전제로 서술돼 있어 문구 수정 필요(로직 영향 없음).
- 이후 스토리(1.12 이하, Epic 2/3/4) — 영향 없음. AD-7을 참조하는 다른 스토리는 "server-side subject allowlist가 dispatch 권한의 권위"라는 부분만 의존하며, 이는 이번 변경에서도 그대로 유지된다.

**Artifact 충돌:**
- **PRD** — OTP/매직링크를 명시한 요구사항 없음(grep 확인). 영향 없음.
- **Architecture** (`ARCHITECTURE-SPINE.md`) — AD-7 Rule 문구가 "Supabase Auth email OTP/magic link로 단일 운영자 세션만 발급한다"를 명시. 수정 필요.
- **UX** (`DESIGN.md`/`EXPERIENCE.md`) — 로그인 화면에 대한 언급 자체가 없음(story 1.10이 "새 디자인 요건 없음, 최소 기능"으로 자체 정의). 영향 없음.
- **기타(코드/테스트/문서):**
  - `apps/web/app/login/page.tsx` — OTP 요청 폼 → 이메일+비밀번호 로그인 폼으로 교체.
  - `apps/web/app/auth/callback/route.ts` — 매직 링크 PKCE 콜백. 더 이상 필요 없어 삭제.
  - `apps/web/proxy.ts` — `/auth/*` public 경로 패턴 제거(더 이상 `/auth` 하위 라우트가 없음).
  - `e2e/manual-trigger.spec.ts`, `e2e/production-smoke.spec.ts` — "매직 링크 보내기" 버튼 문구 assertion을 새 UI에 맞게 수정.
  - `docs/deployment.md`(story 1.11 산출물) — ⑥번 절차를 OTP 수신 확인에서 "Supabase 대시보드에서 슈퍼유저 계정 생성 + 비밀번호 로그인 확인"으로 수정.
  - `_bmad-output/implementation-artifacts/spec-1-10-인증-수동-트리거.md` — 이미 `done`인 spec의 `<intent-contract>`(읽기 전용 원본)는 보존하고, `## Spec Change Log`에 이번 pivot을 새 항목으로 append.
  - `_bmad-output/planning-artifacts/epics.md` — AD-7 요약(63행)과 story 1.10 AC(458행)의 OTP/매직링크 문구 수정.
  - `_bmad-output/planning-artifacts/architecture/.../ARCHITECTURE-SPINE.md` — AD-7 Rule(159행) 문구 수정.
  - Supabase 대시보드(수동, 코드 아님) — ① Authentication > Providers에서 email OTP 발급이 아닌 email+password 로그인을 쓰도록 확인, ② Authentication > Settings에서 "Allow new users to sign up" 비활성화(공개 회원가입 차단 — 이 리포는 public이므로 중요), ③ Authentication > Users에서 Neo의 슈퍼유저 계정을 직접 생성(이메일 인증 완료 상태로).

**기술적 영향:** `OPERATOR_ALLOWLIST` 기반 server-side allowlist, JWKS 서명 검증(`/api/dispatch`), CSRF, rate limit 등 AD-7의 나머지 방어선은 전혀 바뀌지 않는다 — 세션이 어떻게 발급됐는지와 무관하게 유효한 Supabase 세션이면 동일하게 검증된다. 즉 보안 경계 자체는 약화되지 않고, "OTP로 발급됐는가 vs 비밀번호로 발급됐는가"만 바뀐다.

## 3. Recommended Approach

**선택: Option 1 — Direct Adjustment.** 기존 스토리(1.10) 구현을 직접 수정하고, 영향받는 문서 3곳(epics.md, ARCHITECTURE-SPINE.md, spec-1-10)에 반영한다. 새 스토리나 새 epic을 만들 필요가 없다 — 범위가 "인증 메커니즘 교체" 하나로 국한되고, AD-7의 근본 목적(비인가 실행 방지)은 그대로 유지되기 때문이다.

**대안 검토:**
- **Option 2(Rollback)** — 검토 불필요: story 1.10을 되돌려도 문제가 해결되지 않는다(인증 자체가 없어지면 AD-7 위반). 기각.
- **Option 3(MVP 재검토)** — 검토 불필요: PRD/MVP 목표에 영향이 없다. 기각.

**근거:** 변경 범위가 좁고(로그인 화면 1개 + 콜백 라우트 1개 제거 + 문서 3곳), 기존 보안 계약(AD-7의 allowlist·JWKS·CSRF·rate limit)은 그대로 재사용되므로 효과/리스크 비율이 높다. 효과(effort): Low. 리스크: Low(핵심 인가 로직 무변경, UI 레이어만 교체).

## 4. Detailed Change Proposals

### 4.1 Architecture — `ARCHITECTURE-SPINE.md` AD-7 (line 159)

```
OLD:
V1은 외부 사용자 관리 없이 Supabase Auth email OTP/magic link로 단일 운영자 세션만 발급한다.

NEW:
V1은 외부 사용자 관리 없이 Supabase Auth 이메일/비밀번호(Supabase 대시보드에 사전 등록한
단일 슈퍼유저 계정, 공개 회원가입 비활성화)로 단일 운영자 세션만 발급한다.

Rationale: 1인 개인 운영 도구에서 매 로그인마다 이메일 왕복(OTP/매직링크)이 불필요한
마찰을 만든다. 계정이 하나뿐이고 회원가입 플로우 자체가 없으므로 비밀번호 로그인이
동일한 보안 경계(allowlist·JWKS·CSRF)를 유지하면서 더 단순하다.
```

### 4.2 Epics — `epics.md`

```
OLD (line 63, AD-7 요약):
- **AD-7 브라우저는 단일 운영자 세션과 읽기 권한만 가진다:** Supabase Auth email OTP/magic link.
  server-side subject allowlist. dispatch route는 JWKS 검증, CSRF, rate limit, idempotency.

NEW:
- **AD-7 브라우저는 단일 운영자 세션과 읽기 권한만 가진다:** Supabase Auth 이메일/비밀번호
  (사전 등록된 단일 슈퍼유저 계정, 공개 회원가입 비활성화). server-side subject allowlist.
  dispatch route는 JWKS 검증, CSRF, rate limit, idempotency.
```

```
OLD (line 458, Story 1.10 AC):
**Then** Supabase Auth email OTP/magic link로 단일 운영자 세션을 요구하며,
server-side subject allowlist에 없는 사용자는 dispatch 권한을 얻지 못한다(AD-7).

NEW:
**Then** Supabase Auth 이메일/비밀번호(사전 등록된 단일 슈퍼유저 계정)로 단일 운영자
세션을 요구하며, server-side subject allowlist에 없는 사용자는 dispatch 권한을
얻지 못한다(AD-7).
```

### 4.3 Spec — `spec-1-10-인증-수동-트리거.md`

`<intent-contract>`(읽기 전용 원본)는 보존한다. `## Spec Change Log`에 다음 항목을 append한다:

```
### 2026-09-02 — 인증 방식 전환 (bmad-correct-course, 코드 변경 아님)
- **트리거:** 1인 개인 운영 도구에서 OTP/매직링크 로그인의 이메일 왕복이 불필요한
  마찰이라는 Neo의 피드백. sprint-change-proposal-2026-09-02.md 참고.
- **수정 내용:** `apps/web/app/login/page.tsx`를 이메일+비밀번호 로그인 폼으로 교체,
  `apps/web/app/auth/callback/route.ts`(매직 링크 PKCE 콜백) 삭제,
  `apps/web/proxy.ts`의 `/auth/*` public 경로 패턴 제거. Supabase 대시보드에서
  공개 회원가입을 비활성화하고 Neo의 슈퍼유저 계정을 직접 생성하는 절차를
  `docs/deployment.md`에 추가. `OPERATOR_ALLOWLIST`/JWKS/CSRF/rate limit 등 AD-7의
  나머지 방어선은 무변경.
- **피한 known-bad 상태:** 인증 메커니즘 변경이 AD-7의 근본 목적(비인가 실행 방지,
  server-side allowlist 권위)을 약화시키는 것 — 세션 발급 방식만 바뀌고 그 이후의
  모든 검증(JWKS/CSRF/rate limit/allowlist)은 동일하게 유지되므로 이 위험은 없다.
- **KEEP:** `proxy.ts`의 낙관적 세션 리다이렉트 + `/api/dispatch`의 독립 JWKS 검증
  2단 방어 구조, `lib/csrf-constants.ts`/`lib/dispatch.ts` 분리, allowlist 기반 dispatch
  권한 판정 — 전부 인증 메커니즘과 무관하게 그대로 유지한다.
```

### 4.4 구현 코드 변경 (Direct Adjustment, 이 세션이 직접 구현)

- `apps/web/app/login/page.tsx` — `signInWithOtp` → `signInWithPassword({email, password})`로 교체. 성공 시 `/`로 리다이렉트. 실패 시 기존과 같은 에러 표시 패턴 유지.
- `apps/web/app/auth/callback/route.ts` — 삭제(더 이상 매직 링크 콜백이 없음).
- `apps/web/proxy.ts` — `PUBLIC_PATH_PATTERNS`에서 `/^\/auth(\/.*)?$/` 제거.
- `e2e/manual-trigger.spec.ts` — "매직 링크 보내기" → "로그인" 버튼, 비밀번호 필드 assertion 추가.
- `e2e/production-smoke.spec.ts` — 동일하게 버튼 문구 assertion 수정.
- `docs/deployment.md` ⑥ — OTP 이메일 수신 절차를 "Supabase 대시보드에서 슈퍼유저 계정 생성(이메일+비밀번호) → 공개 회원가입 비활성화 확인 → 비밀번호로 로그인" 절차로 교체.
- `.env.example`/`.env.local` — 변경 없음(같은 Supabase publishable key/URL을 그대로 씀. `OPERATOR_ALLOWLIST`에 Neo 이메일이 이미 등록돼 있어야 함, 기존과 동일).

## 5. Implementation Handoff

**Scope classification: Minor** — Developer agent(이 세션)가 직접 구현한다. 새 스토리/에픽 생성이나 PM/Architect 개입이 필요 없다.

**Deliverables:**
1. 위 4.1~4.3의 문서 3곳 편집(epics.md, ARCHITECTURE-SPINE.md, spec-1-10 Spec Change Log).
2. 4.4의 코드/테스트/docs 변경 구현 및 검증(`npm run typecheck`, `npm run test`, `npm run test:e2e`).
3. git commit(스토리 1.10 amendment로 명확히 표기).

**Success criteria:** 로그인 페이지가 이메일+비밀번호 폼을 렌더링하고, `signInWithPassword` 성공 시 세션이 발급되어 `/`로 이동한다. 기존 e2e/유닛 테스트가 새 UI 기준으로 전부 통과한다. `docs/deployment.md`가 Neo에게 Supabase 슈퍼유저 생성·공개 회원가입 비활성화 절차를 안내한다.

**Neo가 배포 후 직접 수행할 일(코드 밖):** Supabase 대시보드에서 ① Authentication > Settings > "Allow new users to sign up" 비활성화, ② Authentication > Users에서 본인 이메일+비밀번호로 계정 생성(이메일 인증 완료 상태), ③ `OPERATOR_ALLOWLIST`에 그 이메일이 등록돼 있는지 확인.

## Implementation Result (2026-09-02)

Neo 승인 후 Direct Adjustment로 즉시 구현했다.

**변경 파일:**
- `apps/web/app/login/page.tsx` — `signInWithOtp` → `signInWithPassword({email, password})`, 성공 시 `/`로 client-side 이동.
- `apps/web/app/auth/callback/route.ts` — 삭제(매직 링크 PKCE 콜백 불필요).
- `apps/web/proxy.ts` — `PUBLIC_PATH_PATTERNS`에서 `/auth/*` 패턴 제거.
- `e2e/manual-trigger.spec.ts`, `e2e/production-smoke.spec.ts` — "매직 링크 보내기" → "로그인" 버튼, 비밀번호 필드 assertion 추가.
- `docs/deployment.md` — ⑥번을 "슈퍼유저 계정 생성 & 인증 필요 화면 수동 확인"으로 교체(공개 회원가입 비활성화, Supabase Users에서 직접 계정 생성, `OPERATOR_ALLOWLIST` 포함 확인 절차 추가).
- `_bmad-output/planning-artifacts/epics.md`(AD-7 요약 63행, story 1.10 AC 458행), `ARCHITECTURE-SPINE.md`(AD-7 Rule 159행) — OTP/매직링크 → 이메일/비밀번호(사전 등록 슈퍼유저, 공개 회원가입 비활성화) 문구로 수정.
- `spec-1-10-인증-수동-트리거.md` — `<intent-contract>`는 보존, `## Spec Change Log`에 이번 전환 항목 append.

**검증:**
- `npm run typecheck`(루트) — 기존 베이스라인과 동일한 path-alias 오류만 남음(신규 오류 없음, 삭제된 콜백 라우트 관련 오류 1건 자연 소멸로 40→39줄).
- `npm run build -w apps/web` — 성공, 라우트 목록에서 `/auth/callback` 사라지고 `/login`만 남음(`.next` 캐시 삭제 후 재확인).
- `npm run test`(unit) — 47/47 통과(이번 변경과 무관한 영역, 회귀 없음 확인).
- `npm run test:e2e` — 4/4 통과(`manual-trigger.spec.ts`가 새 이메일/비밀번호 폼 assertion으로 통과).
- `SMOKE_BASE_URL=http://localhost:3000 npm run test:smoke` — 4/4 통과.
- Playwright MCP로 실제 브라우저에서 `/login` 렌더링(이메일+비밀번호+"로그인" 버튼) 확인, 잘못된 자격증명 제출 시 "Invalid login credentials" 에러가 폼에 표시되고 페이지 이동이 없음을 직접 확인.

**잔여 위험:** 실제 슈퍼유저 계정으로의 로그인 성공 경로(올바른 자격증명 → 세션 발급 → `/` 이동)는 Neo가 Supabase에 실제 계정을 만들기 전까지는 이 세션에서 끝까지 검증할 수 없다(자격증명 부재) — `docs/deployment.md` ⑥의 Manual checks로 위임.
