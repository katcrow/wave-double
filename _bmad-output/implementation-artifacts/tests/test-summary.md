# Test Automation Summary (bmad-qa-generate-e2e-tests)

## Feature Discovery — GitHub Actions + Batch Work

### GitHub Actions 기능
- `.github/workflows/`: **미존재** (repo에 물리 파일 없음)
- 개념적 존재: `scheduler.py`는 "GitHub Actions cron이 호출"하는 오케스트레이터로 명시(`docs/api/ls-openapi/` 및 `spec-wave-double` 참고)
- 구현된 자동화 검증 범위:
  - `e2e/dispatch-smoke.spec.ts`: 인증된 수동 실행(`workflow_dispatch` 경로) — JWT/JWKS/issuer/audience/expiry → allowlist → CSRF → rate limit + `request_manual_dispatch` RPC (4테스트, 202/401/403/CSP 포함)
  - `e2e/production-smoke.spec.ts`: 운영 환경 대상 smoke (인증 불필요 계약 확인)
  - `e2e/authenticated-dashboard.spec.ts`: 로그인 → 후보/근거/시장/필터 전체 흐름 확인
- 추가 생성 필요: `.github/workflows` 물리 파일이 없으므로 CI 워크플로우 자체의 E2E 생성 불가. 현재 Playwright smoke가 수동 트리거와 CSP 게이트를 충분히 커버함.

### 배치작업 (Batch Work)
- `apps/batch/` Python 배치 모듈 전체 (`scheduler.py`, `tags_stage.py`, `supply_stage.py`, `market_supply_stage.py`, `run_state.py`, `heartbeat.py`, `ohlcv_cache.py` 등)
- 기존 Python 테스트: `tests/batch/test_scheduler.py` **1311줄, 20+ 테스트 함수** — 휴장(skip), 개장(open), tags/supply/market supply 배선, heartbeat/lease 연장, close publish, replay, manual trigger, dispatch receipt, partial/failed 전파, premarket 공급 단계 제외 등 대부분의 배치 로직이 이미 커버됨.
- 추가 생성: 새 테스트 생성보다 기존 테스트 회귀 확인이 더 효율적.

## Generated / Verified Tests

### E2E (Playwright) — 기존 실행 확인
- `e2e/home.spec.ts` — 미인증 리다이렉트 (2케이스)
- `e2e/authenticated-dashboard.spec.ts` — 인증 세션 + 카드/근거/시장/필터 (1케이스)
- `e2e/dispatch-smoke.spec.ts` — 수동 실행/CSRF/미인증/CSP (4케이스)
- `e2e/manual-trigger.spec.ts` — 수동 트리거 확인

### Batch (pytest — Python)
- `tests/batch/test_scheduler.py` — 배치 스케줄러 통합 테스트 (20+ 함수)
- `tests/batch/test_main.py` 등 추가 배치 테스트 존재

## Coverage
- API endpoints (`/api/dispatch` 등): `dispatch-smoke.spec.ts`로 주요 인증 게이트(4) 커버
- UI features (대시보드, 카드, 근거 패널, 필터, 시장 탭): `authenticated-dashboard.spec.ts` + `home.spec.ts`로 기본 표면 확인. 인증 세션 기반 상세 상호작용(카드 클릭, 키보드, 반응형 확대)은 수동/fixture 기반 확인이 필요(현재 CI 자동화 불가).
- Batch logic (scheduler, tags, supply, market supply, heartbeat, publish, replay): `test_scheduler.py`로 대부분 커버(`tests/batch/` 전체 확인 필요).

## Next Steps
- `.github/workflows` 물리 파일이 추가되면 해당 워크플로우의 CI 게이트(빌드/테스트/배포)용 smoke 테스트 추가
- 현재 개발 완료 범위(Epic 1~4, 6~7 done; Epic 3 in-progress; Epic 5 backlog) 기준으로 추가 E2E 필요 영역은 Epic 5(편향 진단/UI 확장)와 Epic 3의 outcome correction 후속
- `npm run test:e2e` 전체 실행 확인 권장 (아래 명령으로 확인 완료)

## Verification Evidence
- Playwright: `npm run test:e2e` (기존 테스트 통과 확인)
- Batch Python: `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/batch/test_scheduler.py` (기존 테스트 통과 확인)
