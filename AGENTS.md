<!-- bmad:context -->
<!-- Verified 2026-10-21 against b48b74d. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## wave-double

개인투자자 Neo를 위한 매수후보 추천 대시보드다. 웹 대시보드는 `apps/web/`, Python 배치는 `apps/batch/`, 실존 백테스트 커널은 `backtest/`에 있다. MVP 1차 완료 이후 기존 BMAD 계획 문서(에픽/스토리/아키텍처 스파인)는 더 이상 유지하지 않는다. 새 BMAD 작업의 진입점은 `_bmad-output/initiative-wave-double/initiative-wave-double.md`다.

## Policy

- 개발·테스트(e2e 등)는 playwright MCP를 사용한다.
- Supabase 작업 시엔 supabase MCP를 사용한다.
- Supabase는 별도 dev/staging 프로젝트 없이 운영 프로젝트(`qqhjeumlecaudsiqhhdu`, "wave-double") 하나만 쓴다. migration 적용, RPC/SQL 실행, fixture 검증 등 모든 Supabase 작업은 이 운영 프로젝트에 바로 적용한다 — 별도 확인 없이 바로 진행할 것.
- Supabase 연결 정보(URL·키·토큰)가 필요하거나 불확실하면 항상 먼저 `.env.local`을 직접 확인한다 — gitignored라 저장소 검색만으로 "없다"고 판단하거나 사용자에게 재요청하지 않는다. 대상은 `knoucrow's Org`의 `wave-double` 프로젝트(`qqhjeumlecaudsiqhhdu`)이며, `.env.local`의 URL과 MCP 연결 대상이 이 프로젝트인지 확인한다.
- 키·토큰·비밀번호 값은 응답·로그·문서·커밋에 노출하지 않는다 — 변수명, 설정 여부, 비밀 아닌 프로젝트 참조만 기록한다.
- 프로젝트 기본 언어는 한국어를 사용한다.

## Where things are

- 웹/Next.js 작업: `apps/web/`; 설치된 Next.js 버전 문서는 `node_modules/next/dist/docs/`
- LS OpenAPI 작업 시 `docs/api/ls-openapi/README.md`에서 해당 TR 정의서를 찾아 먼저 확인한다.
- 후보 태깅조건 작업 시 `docs/후보종목-태깅-조건.md`를 먼저 읽고, 계산 조건은 아래 커널 권위 지침에 따라 확인한다.
- Supabase migration 작성·적용 시 `infra/supabase/migrations/README.md`를 먼저 읽는다.

## Running and verifying

- backtest 테스트는 `backtest/`에서 `uv run --with pytest pytest`로 돌린다.
- 탐색 백테스트는 `WAVE_BACKTEST_RESULTS_DIR`로 산출물을 저장소 밖 또는 `backtest/results/scratch/`에 격리한다. 커밋된 `backtest/results/` baseline 증거는 옮기거나 지우지 않는다 — 경로 설정은 `backtest/results_dir.py`를 따른다.

## Conventions that differ from defaults

- 운영 전략 라벨은 `apps/web/lib/strategy-labels.ts`, 백테스트 전략 계산 키·파라미터는 `backtest/strategy_api.py`와 `backtest/indicator_opt/`를 권위로 사용한다 — 별도 스펙 문서를 우선하지 말고 `backtest/tests/` 회귀망을 깨뜨리지 말 것.

## Known pitfalls

- `.env.local`(gitignored)에 server-only 환경변수가 이미 문서화돼 있다 — repo 전체 grep은 이 파일을 건너뛰므로, 환경변수가 "없다"고 판단하기 전에 직접 열어 확인할 것(story 1.10 리뷰에서 이 파일을 못 보고 오판한 전례가 있다).
- `.env.local`에 미사용 `INTERNAL_CRON_SECRET`과 신규 `CRON_CALLBACK_SECRET`이 같은 용도로 이름만 다르게 공존한다 — 정리 전까지는 `CRON_CALLBACK_SECRET`이 실제 사용되는 이름이다.

<!-- /bmad:context -->
