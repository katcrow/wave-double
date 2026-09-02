# 배포 가이드 (Vercel Hobby)

이 문서는 spec-1-11(호스팅 배포 파이프라인)의 산출물이다. wave-double 웹 앱(`apps/web`)을
Vercel Hobby에 연결·배포·검증하는 절차를 다룬다. Vercel Hobby 선택 근거는
`_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md`
의 "배포(hosting) 결정(2026-09-01)" 항목을 참고한다.

이 세션(에이전트)은 Vercel 계정 자격증명이 없어 ①~③을 실제로 실행할 수 없다. 아래는 Neo가
Vercel 대시보드에서 수행해야 하는 수동 1회 절차다.

## ① Vercel 프로젝트 생성 & GitHub 저장소 연동

1. https://vercel.com 에 로그인(또는 GitHub 계정으로 가입)한다.
2. "Add New... > Project"를 선택하고, 이 저장소(wave-double)가 있는 GitHub 계정/조직을 연결한다.
3. 저장소 목록에서 `wave-double`을 선택해 Import한다.

## ② Root Directory 및 Node 버전 확인

1. Import 설정 화면(또는 이후 Project Settings > General)에서 **Root Directory**를
   `apps/web`로 지정한다 -- 이 모노레포는 `apps/web`이 실제 Next.js 앱이다
   (`package.json`의 `workspaces` 참고).
2. **Node.js Version**이 24.x인지 확인한다(2026-09 기준 Vercel 기본값). 루트
   `package.json`의 `engines.node`(`>=24.20.0`)와 호환되는 버전을 명시적으로 선택한다.
3. Framework Preset은 Next.js로 자동 인식되어야 한다. Build Command/Output Directory는
   기본값(Next.js 표준)을 그대로 둔다.

## ③ 환경변수 전체 등록

`.env.example`(repo root)에 나열된 모든 키를 Project Settings > Environment Variables에
등록한다. `.env.local`(미버전관리, 로컬 전용)에 있는 실제 값을 그대로 옮긴다.

- 대상 환경: Production(및 필요 시 Preview)에 모두 등록한다.
- **주의**: `INTERNAL_CRON_SECRET`은 코드에서 실제로 읽지 않는 이름이다(미사용). pg_cron이
  `/api/dispatch/worker` 호출 시 검증에 실제로 쓰이는 값은 `CRON_CALLBACK_SECRET`이다. 두
  키에 같은 값을 넣어도 되지만, 실제 게이트는 `CRON_CALLBACK_SECRET`만 본다(`.env.example`
  주석 참고).
- 모든 secret은 Vercel Environment Variables에만 등록한다. 코드·로그·커밋 이력에 평문으로
  남기지 않는다(NFR1).
- Vercel은 `.env.local`을 읽지 않는다(`apps/web/next.config.ts`의 `loadRootEnvFile`은 로컬
  전용 병합기다) -- 위 목록이 Vercel에도 그대로 등록되어야 앱이 정상 동작한다.
- **Vercel의 Git Fork Protection(기본 활성화)을 끄지 말 것** -- 이 저장소는 public으로
  운영되므로(AD-11과 동일한 위험군) fork에서 올라오는 PR이 존재할 수 있다. Vercel은 기본적으로
  fork PR 배포에 대해 Git Fork Protection(수동 승인 필요)을 제공해, fork PR 빌드가 Preview
  환경변수(위에서 등록한 `SUPABASE_SERVICE_ROLE_KEY`, `GITHUB_DISPATCH_TOKEN` 등 secret 포함)에
  무단으로 접근하지 못하도록 막는다(공식 문서: vercel.com/docs/git,
  vercel.com/docs/project-configuration/security-settings). 이 설정은 Preview 환경변수를
  secret 유출 없이 안전하게 쓸 수 있게 하는 기본 방어선이므로 비활성화하지 않는다.

## ④ main 병합 시 자동 배포 확인

별도 GitHub Actions 배포 워크플로(`.github/workflows/deploy.yml` 등)를 새로 만들 필요가
없다. Vercel의 GitHub 통합은 push-to-deploy를 기본 제공하므로, ①~③이 올바르게 설정되면
`main` 브랜치에 병합되는 즉시 Vercel이 자동으로 새 프로덕션 배포를 트리거한다(Root
Directory만 정확히 설정하면 됨). 기존 `.github/workflows/{test,scheduled-batch}.yml`은 이
배포 경로와 무관한 별개 파이프라인이다(테스트 CI, 배치 스케줄링).

확인 절차: 사소한 변경을 담은 PR을 main에 병합한 뒤, Vercel 대시보드 > Deployments에
새 배포가 자동으로 나타나고 "Ready" 상태가 되는지 확인한다.

## ⑤ 배포 후 contract smoke test 실행

배포가 "Ready" 상태가 되면, 실제 배포 URL을 대상으로 smoke test를 실행한다:

```bash
SMOKE_BASE_URL=https://<실제-배포-도메인> npm run test:smoke
```

내부적으로 `npm run test:smoke`는 `playwright test --config=playwright.smoke.config.ts`를
실행한다(`playwright.smoke.config.ts`는 `webServer`를 정의하지 않고 `SMOKE_BASE_URL`을
`baseURL`로 사용한다 -- 로컬 `next dev` 대상 검증 시에는
`SMOKE_BASE_URL=http://localhost:3000 npm run test:smoke`로 재사용할 수 있다).

**기대 결과** (`e2e/production-smoke.spec.ts`, 4개 시나리오 전부 통과):

| 시나리오 | 기대 결과 |
|---|---|
| 미인증 `/` 접속 | `/login`으로 리다이렉트 |
| 미인증 `/runs` 접속 | `/login`으로 리다이렉트 |
| `/login` 접속 | `200`, OTP 요청 폼(이메일 입력 + "매직 링크 보내기" 버튼) 렌더 |
| 시크릿 헤더 없이 `/api/dispatch/worker` 호출 | `401` (route가 살아있고 게이트가 걸림을 증명) |

이 smoke test는 인증 없이 확인 가능한 계약만 검증한다. 실제 데이터 렌더링 확인은 아래 ⑥을
따른다.

## ⑥ 인증 필요 화면 수동 확인

OTP 로그인은 실제 이메일 수신이 필요해 자동화할 수 없다. 배포 후 다음을 육안으로 확인한다:

1. 실제 배포 URL의 `/login`에서 운영자 이메일로 매직 링크를 요청한다.
2. 수신한 메일의 링크로 로그인한다.
3. `/`(오늘의 후보, Story 1.9)와 `/runs`(배치 이력, Story 1.9)가 정상 렌더링되는지 확인한다.
4. 화면에 표시되는 데이터가 Story 1.8 스냅샷 API(장중 snapshot)의 실제 값을 반영하는지
   확인한다(예: 후보 목록이 비어있지 않거나, 최근 배치 실행 이력이 보이는지).

## ⑦ Vercel 사용량 한도 80% 근접 감지 (Usage Alert)

**근거**: Vercel REST API에는 프로젝트별 사용량(대역폭/함수 호출/빌드 시간) 조회 엔드포인트가
없다(2026-09 확인: 공식 `vercel.com/docs/rest-api`에 해당 엔드포인트 없음, GitHub
`vercel/vercel` discussion #11120/#8310에서 커뮤니티도 동일하게 확인). 따라서 story 1.10의
dead-letter 알림(AD-10, GitHub Issue 생성)과 같은 커스텀 폴링+알림 패턴을 사용량 감지에
재사용할 수 없다. 이 결정은 Vercel이 향후 사용량 API를 공개하면 재검토한다.

**대신 Vercel 대시보드 내장 Usage Alert을 활성화한다**:

1. Vercel 대시보드 > (해당 프로젝트 또는 계정) > Settings > Usage(또는 Billing) > Usage
   Alerts로 이동한다.
2. 이메일 알림을 받을 대상(Neo의 이메일)이 설정되어 있는지 확인한다.
3. Hobby 플랜 한도(2026 기준 대역폭 100GB, 함수 호출 ~100K~1M, 빌드 6,000분, 함수 10초
   time-out) 근접 시 Vercel이 자동으로 이메일을 발송하도록 활성화되어 있는지 확인한다.

## ⑧ "서비스 접속 불가" vs "stale" 구분 근거

이 앱은 이미 대시보드에 데이터 "stale"(신선도 저하) 표시를 갖고 있다(Story 1.9). Vercel
인프라 레벨 한도 초과나 장애로 인한 "서비스 접속 불가"는 이 stale 표시와 별도의 신규 UI
상태가 필요 없다 -- 다음 이유로 이미 구분된다:

- **서비스 접속 불가**(Vercel Hobby 한도 초과, 배포 실패, Vercel 자체 장애 등)가 발생하면
  브라우저는 애초에 이 앱의 React 트리를 렌더링하지 못한다. 대신 Vercel이 반환하는 자체 오류
  화면(예: 함수 timeout의 504, 빌드 실패로 인한 배포 미존재, Vercel 플랫폼 장애 페이지)을
  보게 된다.
- **stale**(데이터 신선도 저하)은 앱이 정상적으로 응답하고 렌더링된 상태에서, 그 안의 데이터가
  오래됐음을 알리는 것이다(예: 배치가 지연되어 최신 스냅샷이 없는 경우).

즉 "화면 자체가 Vercel 오류 화면인가(서비스 접속 불가) vs 앱 화면 안에 stale 배지가 떠 있는가
(데이터 신선도 저하)"라는 사실 자체가 이미 두 상태를 구분해 준다. 별도의 신규 UI 상태를
추가할 필요가 없다(AC4는 문서화·확인 요건이지 신규 UI 요건이 아니다).

## 부록: 재검토 트리거

- Vercel Hobby의 비영리 제약에 걸리거나(V2 자동매매 상용화), 함수 호출/대역폭이 지속적으로
  한도에 근접하면 그때 호스팅 제공자를 재검토한다(ARCHITECTURE-SPINE.md 참고).
- Vercel이 사용량 조회 REST API를 공개하면, ⑦의 Usage Alert 방식 대신 커스텀 폴링+알림
  방식(AD-10과 유사) 도입을 재검토한다.
