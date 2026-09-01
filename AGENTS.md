<!-- bmad:context -->
<!-- Verified 2026-09-01 against 4852d0b. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## wave-double

개인투자자 Neo를 위한 매수후보 추천 대시보드. 계획 문서는 `_bmad-output/`에 있고 주 계약은 `_bmad-output/specs/spec-wave-double/SPEC.md`다. 실존 파이썬 백테스트 커널은 `backtest/`에 있다.

## Policy

- 개발·테스트(e2e 등)는 **playwright MCP**를 사용한다.
- Supabase 작업 시엔 **supabase MCP**를 사용한다.
- 프로젝트 기본 언어는 **한국어**를 사용한다.

## Where things are

- 상호변경 불가 규칙(AD-1~AD-20): `_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md`
- 에픽·스토리: `_bmad-output/planning-artifacts/epics.md`, 진행 상태: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- LS OpenAPI 참조: `docs/api/ls-openapi/`

## Running and verifying

- backtest 테스트는 `uv run --with pandas --with numpy --with pyarrow --with pytest pytest`로 돌린다 — pyarrow 없이 실행하면 실데이터 테스트 3개가 ImportError로 실패한다.

## Conventions that differ from defaults

- 전략 A/B/C 태깅은 `specs/spec-wave-double/backtest-baseline.md`의 룰과 일치해야 하고 `backtest/` 커널을 깨뜨리지 말 것 — 커널 테스트가 회귀망이다.

<!-- /bmad:context -->
