<!-- bmad:context -->
<!-- Verified 2026-09-02 against 2f690a2. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## wave-double

개인투자자 Neo를 위한 매수후보 추천 대시보드. 계획 문서는 `_bmad-output/`에 있고 주 계약은 `_bmad-output/specs/spec-wave-double/SPEC.md`다. 실존 파이썬 백테스트 커널은 `backtest/`에 있다.

## Policy

- 개발·테스트(e2e 등)는 **playwright MCP**를 사용한다.
- Supabase 작업 시엔 **supabase MCP**를 사용한다.
- **Supabase는 별도 dev/staging 프로젝트 없이 운영 프로젝트(`qqhjeumlecaudsiqhhdu`, "wave-double") 하나만 쓴다.** migration 적용, RPC/SQL 실행, fixture 검증 등 모든 Supabase 작업은 이 운영 프로젝트에 바로 적용한다 — 별도 확인 없이 바로 진행할 것(Neo의 명시적 정책, 2026-09-02).
- 프로젝트 기본 언어는 **한국어**를 사용한다.

## Where things are

- 상호변경 불가 규칙(AD-1~AD-20): `_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md`
- 에픽·스토리: `_bmad-output/planning-artifacts/epics.md`, 진행 상태: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- LS OpenAPI 참조: `docs/api/ls-openapi/`

## Running and verifying

- backtest 테스트는 `uv run --with pandas --with numpy --with pyarrow --with pytest pytest`로 돌린다 — pyarrow 없이 실행하면 실데이터 테스트 3개가 ImportError로 실패한다.

## Conventions that differ from defaults

- 전략 A/B/C 태깅은 `specs/spec-wave-double/backtest-baseline.md`의 룰과 일치해야 하고 `backtest/` 커널을 깨뜨리지 말 것 — 커널 테스트가 회귀망이다.
- 스토리 작업 커밋 제목과 build/review evidence에는 스토리 key를 `story <에픽>-<스토리>` 형식으로 넣는다(예: `feat(story 2-5): ...`). 키는 `_bmad-output/implementation-artifacts/sprint-status.yaml`의 스토리 key slug("2-5-후보-태깅-stage-저장")의 선두 토큰이며, 점(`story 4.2`)이나 하이픈 접미사(`story-2-5`) 등 표기 변형은 회고 `git_evidence.py`가 정규화해 자동 귀속한다.

## Known pitfalls

- `.env.local`(gitignored)에 story별 server-only 환경변수가 이미 문서화돼 있다 — repo 전체 grep은 이 파일을 건너뛰므로, 환경변수가 "없다"고 판단하기 전에 직접 열어 확인할 것(story 1.10 리뷰에서 이 파일을 못 보고 오판한 전례가 있다).
- `.env.local`에 미사용 `INTERNAL_CRON_SECRET`과 신규 `CRON_CALLBACK_SECRET`이 같은 용도로 이름만 다르게 공존한다 — 정리 전까지는 `CRON_CALLBACK_SECRET`이 실제 사용되는 이름이다.

<!-- /bmad:context -->

## Supabase 연결 정보 확인 정책

- Supabase 프로젝트·URL·인증 키·접근 토큰 등 연결 정보가 필요하거나 불확실하면 **항상 먼저 `C:\dev\wave-double\.env.local`을 직접 확인한다.** gitignored 파일이므로 일반 저장소 검색 결과만으로 설정이 없다고 판단하거나 사용자에게 다시 요청하지 않는다.
- 사용 대상은 **`knoucrow's Org`의 `wave-double` 프로젝트(`qqhjeumlecaudsiqhhdu`)**다. `.env.local`의 URL에서 프로젝트 참조를 확인하고, MCP 연결 대상도 같은 프로젝트인지 확인한다. 파일만으로 조직 소속이나 MCP 인증 완료를 확인했다고 간주하지 않는다.
- 키·토큰·비밀번호 값은 응답, 로그, 문서, 커밋에 노출하지 않는다. 확인 결과에는 변수명, 설정 여부, 비밀이 아닌 프로젝트 참조만 기록한다. `.env.local`은 커밋하지 않는다.
- `.env.local`의 애플리케이션 인증 정보와 Supabase MCP 연결 상태는 별도로 확인한다. Supabase 작업에는 위의 **Supabase MCP 사용 정책**을 계속 적용한다.
