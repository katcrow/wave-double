<!-- bmad:context -->
<!-- Verified 2026-09-16 against 95373e6. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## wave-double

개인투자자 Neo를 위한 매수후보 추천 대시보드. 실존 파이썬 백테스트 커널은 `backtest/`에 있다. MVP 1차 완료 이후 BMAD 계획 문서(에픽/스토리/아키텍처 스파인)는 더 이상 유지하지 않는다.

## Policy

- 개발·테스트(e2e 등)는 **playwright MCP**를 사용한다.
- Supabase 작업 시엔 **supabase MCP**를 사용한다.
- **Supabase는 별도 dev/staging 프로젝트 없이 운영 프로젝트(`qqhjeumlecaudsiqhhdu`, "wave-double") 하나만 쓴다.** migration 적용, RPC/SQL 실행, fixture 검증 등 모든 Supabase 작업은 이 운영 프로젝트에 바로 적용한다 — 별도 확인 없이 바로 진행할 것(Neo의 명시적 정책, 2026-09-02).
- Supabase 연결 정보(URL·키·토큰)가 필요하거나 불확실하면 항상 먼저 `.env.local`을 직접 확인한다 — gitignored라 저장소 검색만으로 "없다"고 판단하거나 사용자에게 재요청하지 않는다. 대상은 `knoucrow's Org`의 `wave-double` 프로젝트(`qqhjeumlecaudsiqhhdu`)이며, `.env.local`의 URL과 MCP 연결 대상이 이 프로젝트인지 확인한다.
- 키·토큰·비밀번호 값은 응답·로그·문서·커밋에 노출하지 않는다 — 변수명, 설정 여부, 비밀 아닌 프로젝트 참조만 기록한다.
- 프로젝트 기본 언어는 **한국어**를 사용한다.

## Where things are

- LS OpenAPI 참조: `docs/api/ls-openapi/`

## Running and verifying

- backtest 테스트는 `backtest/`에서 `uv run --with pytest pytest`로 돌린다.

## Conventions that differ from defaults

- 전략 A~F 태깅/파라미터는 `apps/web/lib/strategy-labels.ts`와 `backtest/` 커널 코드가 유일한 근거다(별도 스펙 문서 없음) — 커널 테스트가 회귀망이므로 깨뜨리지 말 것.

## Known pitfalls

- `.env.local`(gitignored)에 server-only 환경변수가 이미 문서화돼 있다 — repo 전체 grep은 이 파일을 건너뛰므로, 환경변수가 "없다"고 판단하기 전에 직접 열어 확인할 것(story 1.10 리뷰에서 이 파일을 못 보고 오판한 전례가 있다).
- `.env.local`에 미사용 `INTERNAL_CRON_SECRET`과 신규 `CRON_CALLBACK_SECRET`이 같은 용도로 이름만 다르게 공존한다 — 정리 전까지는 `CRON_CALLBACK_SECRET`이 실제 사용되는 이름이다.

<!-- /bmad:context -->
