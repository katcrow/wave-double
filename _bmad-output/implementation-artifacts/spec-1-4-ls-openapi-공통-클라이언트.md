---
title: 'LS OpenAPI 공통 클라이언트'
type: 'feature'
created: '2026-09-01'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-1-context.md
  - C:/dev/wave-double/docs/api/ls-openapi/README.md
  - C:/dev/wave-double/_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md
warnings: []
deferred: []
baseline_revision: '869491cc1a2c46ec3ed0823e03d14073c11adeee'
baseline_commit: '869491cc1a2c46ec3ed0823e03d14073c11adeee'
---

<intent-contract>

## Intent

**Problem:** LS OpenAPI 호출마다 rate limit과 재시도 처리가 흩어지면 TR 추가 때 정책이 달라지고 30분 배치 예산을 초과할 수 있다.

**Approach:** `apps/batch`에 TR 코드와 요청 파라미터를 그대로 받는 공통 HTTP 경계를 만들고, TR별 token bucket·bounded retry·wall-clock budget을 한 곳에서 적용한다. OAuth 자격 증명과 LS 형식은 이 경계에만 둔다.

## Boundaries & Constraints

**Always:** 기본 개인 TR 예산은 1건/초이며 bucket은 TR별로 독립한다. 429의 `Retry-After`는 delta-seconds와 HTTP-date를 모두 해석하고 비정상 값은 제한된 기본 backoff를 사용한다. 재시도와 대기는 남은 budget을 넘지 않으며 소진 시 구조화된 `RATE_LIMIT_EXHAUSTED` 또는 budget-exhausted 결과를 반환한다. 공통 헤더와 범용 JSON payload를 유지하고 secret/token은 로그에 남기지 않는다.

**Never:** 특정 TR 전용 메서드만을 공통 클라이언트 계약으로 만들지 않는다. domain/backtest에 HTTPX·Supabase·LS 응답 형식을 넣지 않는다. TR 간 교차 병렬화는 실측 검증 전까지 설정으로 활성화할 수 없다. Story 1.5의 후보 선별·폴백·절단 로직은 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 임의 `tr_code`, dict params, 유효 token | LS endpoint에 공통 헤더와 payload로 1회 호출하고 JSON 응답 반환 | 오류 없음 |
| RATE_LIMIT_RETRY | 429와 `Retry-After` delta-seconds 또는 HTTP-date | 지정 시간만큼 기다린 뒤 bounded 횟수 내 재호출 | 비정상 헤더는 bounded default backoff |
| RETRY_EXHAUSTED | 연속 429/재시도 가능한 5xx가 최대 횟수 초과 | 호출 실패 결과와 `RATE_LIMIT_EXHAUSTED` 코드 반환 | 호출자가 partial/unprocessed_count로 전파 가능 |
| BUDGET_EXHAUSTED | 다음 backoff가 남은 wall-clock budget보다 큼 | 추가 요청 없이 budget-exhausted 결과 반환 | timeout으로 위장하지 않음 |
| PARALLEL_DISABLED | 교차 TR 병렬화 옵션을 true로 초기화 | 설정이 거부되어 순차 호출만 허용 | 명시적 configuration error |

</intent-contract>

## Code Map

- `apps/batch/run_state.py:11-22` -- Protocol 경계와 구조화 오류 패턴을 공통 클라이언트에 재사용한다.
- `apps/batch/pyproject.toml:1-8` -- HTTPX 0.28.1이 이미 배치 의존성으로 고정되어 있다.
- `apps/batch/ls_client.py` -- TR-agnostic HTTP client, token bucket, retry-after, budget, 오류 계약을 구현할 신규 경계.
- `tests/batch/test_ls_client.py` -- MockTransport로 성공·429 헤더 형식·재시도/예산·설정 강제를 결정적으로 검증할 신규 회귀망.
- `docs/api/ls-openapi/README.md:8-18` -- LS REST 도메인과 공통 인증/헤더 계약.
- `docs/api/ls-openapi/01-oauth-auth/issue-access-token.md:27-61` -- access token 및 OAuth 요청 형식 참고.
- `uv.lock:96-105` -- HTTPX와 전송 계층 잠금 버전의 증거.

## Tasks & Acceptance

**Execution:**
- [x] `apps/batch/ls_client.py` -- 범용 `request(tr_code, params)`와 token provider, TR별 limiter, retry/budget, 구조화 오류를 구현 -- 후속 TR이 재설계 없이 같은 정책을 사용하도록 한다.
- [x] `tests/batch/test_ls_client.py` -- HTTPX MockTransport와 주입 가능한 clock/sleeper로 I/O 매트릭스와 공통 헤더/payload를 검증 -- 외부 LS 호출 없이 결정성을 보장한다.

**Acceptance Criteria:**
- Given 클라이언트가 초기화된 경우, when 서로 다른 TR 코드로 요청하면, then 각 TR에 독립된 token bucket이 적용되고 기본 개인 한도는 1건/초이다.
- Given 429 응답이 발생한 경우, when `Retry-After`가 delta-seconds 또는 HTTP-date이면, then 해당 대기 후 재시도하며 비정상 값이면 bounded default backoff를 사용한다.
- Given 재시도 횟수 또는 남은 wall-clock 예산이 소진된 경우, when 호출을 계속하려 하면, then 추가 요청 없이 `RATE_LIMIT_EXHAUSTED` 또는 budget-exhausted 구조화 결과를 반환한다.
- Given 임의의 TR 코드와 파라미터가 전달된 경우, when 요청을 전송하면, then 특정 TR 전용 분기 없이 공통 endpoint·헤더·payload 계약으로 응답을 반환한다.
- Given 교차 TR 병렬화가 활성화되려는 경우, when 클라이언트를 구성하면, then 실측 검증 전 기본 비활성 정책을 위반하는 설정이 거부된다.

## Design Notes

HTTP client 자체와 rate policy를 분리해 clock/sleeper를 주입하면 실제 대기 없이 retry-after와 budget 경계를 검증할 수 있다. Retry-After HTTP-date가 이미 지난 시각이면 0초로 정규화하고, 음수·너무 큰 값·파싱 불가 값은 bounded default로 치환한다. transport 오류와 HTTP 5xx는 bounded retry 대상이며, 인증/4xx 일반 오류는 재시도하지 않는 구조화 오류로 반환한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_ls_client.py -q` -- expected: all client contract tests pass.
- `uv run --with pytest pytest tests/domain tests/batch -q` -- expected: existing state/calendar and client tests pass.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: existing backtest regression suite passes unchanged.
- `git diff --check` -- expected: no whitespace errors.

## Review Triage Log

### 2026-09-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5: (high 0, medium 3, low 2)
- defer: 0
- dismissed:
  - API 업무 응답 메타데이터·401 갱신·4xx 세분화 요구 — 이번 intent는 공통 전송·rate/retry/budget 계약이며 후속 응답 모델 확장으로 현재 acceptance 결과가 훼손되지 않는다.
  - OAuth token 발급 form 계약·transport 지연의 별도 timeout·공급자 예외 — 현재 명세의 검증 대상이 아닌 후속 운영 계약이다.
  - TR 코드 제어문자 정규화와 테스트 자원 정리 — 현재 기능 결과를 바꾸지 않는 방어적 개선이며 결함의 결과를 입증하지 못했다.
- addressed_findings:
  - `[medium]` `[patch]` TR별 limiter를 refill token bucket과 per-TR lock으로 수정해 동시 호출에서도 한도를 보장.
  - `[medium]` `[patch]` sleeper 이후 wall-clock budget을 재확인해 예산 초과 요청을 차단.
  - `[medium]` `[patch]` 실제 LS API path와 선택적 mac_address를 공통 요청 경계에서 지원.
  - `[low]` `[patch]` NaN/inf rate·backoff·budget 설정을 거부.
  - `[low]` `[patch]` 비정상 Retry-After fallback과 최대 재시도 소진을 실제 경과시간·호출 횟수로 검증.

## Auto Run Result

Status: done

**구현 요약:** 임의 TR 코드·파라미터를 수용하는 LS REST 공통 클라이언트를 추가하고, TR별 독립 token bucket, 동시 호출 보호, 429/5xx/transport bounded retry, Retry-After(delta-seconds/HTTP-date), wall-clock budget, API path와 선택적 법인 MAC 헤더, 교차 TR 병렬화 금지 설정을 구현했다.

**변경 파일:**

- `apps/batch/ls_client.py` -- 공통 LS HTTP 경계와 rate/retry/budget 정책.
- `tests/batch/test_ls_client.py` -- HTTPX MockTransport 기반 계약·경계 테스트.
- `_bmad-output/implementation-artifacts/spec-1-4-ls-openapi-공통-클라이언트.md` -- 구현 명세, 리뷰 및 검증 결과.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- Story 1.4 최종 상태 동기화.

**리뷰 결과:** patch 5건(중간 3, 낮음 2)을 적용했고 intent gap·bad spec·defer는 0건이다. dismissed 항목은 위 로그에 이유를 기록했다. 후속 리뷰 권고는 true이며 patch 점수는 `3 × 3 + 1 × 2 = 11`이다.

**검증:** 전용 테스트 23 passed, domain/batch 전체 48 passed, backtest 회귀 16 passed, `git diff --check` 통과. 웹/사용자 인터페이스 변경이 없어 Playwright E2E는 불필요하여 실행하지 않았다. 실제 LS 인증정보 없이 production 호출은 수행하지 않았다.

**잔여 위험:** 실운영 LS 계정의 공유 rate limit과 실제 endpoint별 업무 응답 계약은 자격 증명 없이 검증하지 않았다.
