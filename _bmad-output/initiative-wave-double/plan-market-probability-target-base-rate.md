---
title: '종가배팅 참고확률: 목표 +0.5% 기준·기본 성공률 대비·최근 가중·휴장일 보완'
type: 'feature'
ticket: ''
created: '2026-10-23'
status: 'built'
baseline_revision: '63b4437ecbb5a7d5443d655ad560831ee94d94b2'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context: ['{project-root}/infra/supabase/migrations/README.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 현행 칩은 "익일 고가 > 당일 종가"의 과거 빈도를 보여 준다. 이 사건은 평소에도 81~85% 일어나서 변별력이 없다. 2026-10-22에는 -3.5% 급락에도 81.9%/86.3%가 나와 상승 신호로 오해될 수 있었다. 또 `KRX_HOLIDAYS`에 2024~2025년 휴장일과 2026-07-17이 빠져 있어 과거 표본 28개가 누락됐다.

**Approach:** 정답 기준을 "익일 고가 > 당일 종가 × 1.005"(목표 +0.5%) 하나로 바꾼다. 같은 기준의 기본 성공률을 함께 저장하고, 칩에는 "평소 대비 ±x%p"를 표시한다. 표본에는 최근일수록 높은 지수가중(반감기 120표본)을 주고, 휴장일 달력을 보완한다.

## Boundaries & Constraints

**Always:** 기존 `kospi_probability`/`kosdaq_probability` 컬럼은 새 기준 확률로 그대로 쓴다. 기본 성공률은 nullable 신규 컬럼에 저장해 과거(v1) 행과 호환한다. 기본 성공률은 조건 구간과 같은 가중·Laplace 보정으로 전체 표본에서 계산한다. 조건 구간 폴백(가중 전 표본 수 < 20)과 전체 표본 < 30 중단 규칙은 유지한다. 운영 Supabase에는 supabase MCP로 바로 적용한다(AGENTS.md 정책).

**Never:** 종가 상승·시가 갭 등 다른 기준은 계산하거나 표시하지 않는다. 등락률 구간(20% 분위 경계) 방식은 바꾸지 않는다. 과거 행을 재계산하거나 수정하지 않는다. slot·upsert 덮어쓰기 규칙은 바꾸지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 목표 경계 | 익일 고가 = 종가×1.005 정확히 | 실패(0), 초과 시 성공(1) | — |
| 최근 가중 | 같은 구간에서 최근 표본만 성공 | 가중 확률 > 무가중 확률 | — |
| 기본 성공률 | 정상 이력 | payload에 `kospi_base_rate`/`kosdaq_base_rate`(0~1) 포함, diagnostics에 가중합 기록 | — |
| v1 행 | 최신 행의 base_rate가 null | 칩은 확률만 표시하고 평소 대비 문구 숨김 | 오류 없음 |
| 잘못된 base_rate | upsert에 1.2 또는 문자열 | `INVALID_MARKET_INDEX_PROBABILITY` 예외 | 배치 저장 실패 처리(기존) |
| 휴장 연휴 | 2025-10-02 → 다음 공동 거래일 | 2025-10-10 | — |

</frozen-after-approval>

## Code Map

- `apps/batch/market_probability.py` -- `empirical_probability`(라벨 `following.high > current.close`, Laplace, band 분류), `build_payload`(payload·`model_version` `historical_conditional_rate_v1`), `next_joint_trading_day`(KRX_HOLIDAYS 사용). 계산 변경 지점.
- `packages/domain/domain/calendar.py:50` -- `KRX_HOLIDAYS` (현재 2026·2027만). `decide_from_weekday`와 배치 스케줄러도 같은 집합을 쓴다.
- `infra/supabase/migrations/202610211000_add_market_probability.sql` -- 테이블, `upsert_market_index_probability`(검증 후 insert/on conflict), `get_latest_market_index_probability`(returns table, 컬럼 추가 시 drop 후 재생성 필요), grant 문. 새 migration이 이 정의를 대체한다.
- `apps/web/lib/dashboard-types.ts:19` -- `MarketIndexProbabilityRpcRow`, `isMarketIndexProbabilityRpcRow` 가드.
- `apps/web/lib/market-probability.ts` -- `deriveMarketProbabilityChipState`, `formatProbabilityPercent`.
- `apps/web/components/dashboard/MarketProbabilityChip.tsx` -- 라벨 "익일 고가 돌파", ⓘ 설명 문구, 값 `<dl>`.
- `packages/read-model/src/database.types.ts:530,1247` -- 테이블 Row/Insert/Update와 RPC Returns 타입.
- `e2e/mock-supabase-server.mjs:118`, `e2e/authenticated-dashboard.spec.ts:37` -- 칩 mock 행과 단언.
- `tools/check_production_parity.py:92-129` -- 로컬 파일명 ↔ 운영 migration명 매핑. 새 migration도 두 사전에 추가한다.
- `tests/batch/test_market_probability.py`, `apps/web/lib/market-probability.test.ts`, `tests/domain/test_calendar.py` -- 기존 테스트. `.github/workflows/test.yml:41` 배치 테스트 목록에 market_probability 테스트가 빠져 있다.

## Tasks & Acceptance

**Execution:**
- [x] `packages/domain/domain/calendar.py` -- 2024·2025년 KRX 휴장일 전체와 2026-07-17(제헌절)을 추가한다 -- 표본 누락과 휴장 판정 오류 해소.
- [x] `apps/batch/market_probability.py` -- `TARGET_RETURN_PCT=0.5`, `HALF_LIFE_SAMPLES=120` 상수를 추가한다. 라벨을 목표 기준으로 바꾸고, 표본 가중 `0.5 ** (age/120)`(age=가장 최근 표본으로부터의 순번)을 적용한 Laplace 확률과 기본 성공률을 반환한다. payload에 base rate 필드를 넣고 `model_version`을 `historical_conditional_rate_v2`로 올린다. history에는 `next_high_return_pct`와 `target_hit`를 기록한다.
- [x] `infra/supabase/migrations/202610231000_add_market_probability_base_rate.sql` -- nullable `kospi_base_rate`/`kosdaq_base_rate` 컬럼(0~1 check)을 추가한다. upsert는 선택 필드를 검증해 저장하도록, get_latest는 drop 후 base rate 포함으로 재생성하고 grant를 복원한다. 테이블 comment도 갱신한다.
- [x] `tools/check_production_parity.py` -- 새 migration의 운영명 매핑을 추가한다.
- [x] `packages/read-model/src/database.types.ts` -- 신규 컬럼과 RPC 반환 필드를 반영한다.
- [x] `apps/web/lib/dashboard-types.ts`, `apps/web/lib/market-probability.ts` -- base rate(`number | null`, 누락 시 null 취급)를 검증하고, 상태에 `kospiDelta`/`kosdaqDelta`("+0.8%p" 또는 null)와 평소 퍼센트를 추가한다.
- [x] `apps/web/components/dashboard/MarketProbabilityChip.tsx` -- 라벨을 "익일 고가 +0.5%"로 바꾼다. 각 값 아래에 "평소 81.0% · +0.8%p"를 표시하고(null이면 생략) ⓘ 설명을 새 기준으로 고친다.
- [x] 테스트: `tests/batch/test_market_probability.py`(I/O 매트릭스의 목표 경계·최근 가중·base rate·payload), `tests/domain/test_calendar.py`(2025 연휴, 2026-07-17), `apps/web/lib/market-probability.test.ts`(delta 포맷·null), e2e mock·spec(평소 대비 문구), `.github/workflows/test.yml`(market_probability 테스트 추가).

**Acceptance Criteria:**
- Given 운영 DB에 migration을 적용했을 때, when `get_latest_market_index_probability()`를 호출하면, then base rate 두 컬럼이 반환되고 기존 v1 행은 null로 나온다.
- Given 2026-10-22 실제 t8429 일봉에, when 새 `empirical_probability`로 재계산하면, then 확률이 v1(81.9%/86.3%)보다 낮고 같은 기준 기본 성공률과의 차이를 보고할 수 있다.
- Given base rate가 있는 최신 행이 있을 때, when 대시보드를 열면, then 칩에 "익일 고가 +0.5%" 라벨과 각 시장의 "평소 x% · ±y%p"가 보인다.

## Implementation Notes

- 목표 경계 비교는 부동소수 오차(100×1.005 = 100.4999…)를 피하려고 `Decimal(str(x))`로 한다. `empirical_probability`는 튜플 대신 `ProbabilityEstimate(probability, base_rate, diagnostics, history)`를 돌려준다.
- 가중치 age는 전체 유효 표본 기준 순번이다(조건 구간 안에서 다시 매기지 않음). diagnostics에는 계획의 6개 키 외에 `success_count`, `base_sample_count`, `base_weight_sum`, `base_success_weight`, `condition`, `smoothing`(`weighted_laplace_1_1`)도 남긴다.
- upsert는 base rate가 JSON 숫자/null/누락이 아니면(문자열 등) 캐스팅 전에 `INVALID_MARKET_INDEX_PROBABILITY`로 거부한다. 운영명 `add_market_probability_base_rate`로 적용(2026-10-23), 롤백 블록에서 1.2·문자열 거부와 정상 저장을 확인했다.
- 웹 타입은 base rate를 optional(`?: number | null`)로 두어 구 RPC 응답 누락을 null로 취급한다. 평소 대비 반올림 0은 `±0.0%p`.
- 2026-10-22 재계산(idx.json, 장중 -3.52%/-3.62%): 코스피 66.3%(평소 69.1%, -2.8%p), 코스닥 68.3%(평소 66.8%, +1.4%p). v1 81.9%/86.3%보다 낮다. 휴장일 보완으로 조건 표본이 147→156, 166→175로 늘었다.

## Plan Change Log

## Review Triage Log

**Pass 1 (quick)** — high 0 / medium 0 / low 4 / false 1 / maybe-false 0

| # | 지적 | 판정 | 경로 | 근거·조치 |
|---|---|---|---|---|
| 1 | `market-probability.ts` delta가 반올림 전 값 차이라 화면 숫자와 어긋남(62.3%/61.6%인데 +0.8%p), 음수 .5 반올림 비대칭 | low | patch | node로 0.6234/0.6156 → "62.3","61.6","+0.8" 재현. 표시된 두 퍼센트(1자리 반올림)의 차로 계산하도록 수정 |
| 2 | ⓘ 문구 "평소=전체 기간 성공률"이 실제(최근 가중·Laplace)와 다름 | low | patch | `_weighted_laplace(전체 표본, 같은 weights)` 확인. 문구를 "같은 기준·같은 가중의 전체 표본 성공률"로 수정 |
| 3 | history `next_high_return_pct`(float)와 `target_hit`(Decimal) 경계 불일치 가능 | low | patch | float 100.5/100 → 0.49999…; 경계에서 두 필드 계산 경로가 다름은 사실. return도 Decimal로 계산해 일관시킴 |
| 4 | AC2(10/22 재계산) 자동 검증 없음 | false | reject | 계획 Verification에 수동 확인으로 명시되어 있고, 오케스트레이터가 운영 일봉으로 직접 재확인함 |
| 5 | 잘못된 base_rate 거부에 대한 저장소 테스트 없음 | low | patch | `tests/sql/test_*.sql`을 CI가 자동 수집(test.yml:275~)하는데 확률용 fixture 없음. SQL fixture 추가 |

## Design Notes

가중 Laplace: `p = (Σ w·y + 1) / (Σ w + 2)`. 반감기 120표본은 약 6개월이다. 2026 하반기처럼 국면이 바뀐 구간을 반영하면서도, 조건 구간당 유효 표본 수가 수십 개 이상 남도록 고른 값이다. 폴백 판단은 가중 전 표본 수로 해서 기존 의미를 유지한다. diagnostics에는 `sample_count`, `weight_sum`, `success_weight`, `base_rate`, `target_return_pct`, `half_life_samples`를 남겨 사후 검증에 쓴다.

## Verification

**Commands:**
- `uv run --no-project --python 3.12 --with pytest --with httpx==0.28.1 python -m pytest tests/batch/test_market_probability.py tests/domain/test_calendar.py tests/batch/test_calendar.py -q` -- expected: 전부 통과 (루트 `.venv`는 Linux용이라 `--no-project` 사용)
- `npm run test && npm run typecheck` -- expected: 통과
- `npm run test:e2e -- e2e/authenticated-dashboard.spec.ts` -- expected: 칩 단언 통과

**Manual checks (if no CLI):**
- supabase MCP로 migration 적용 후 `select * from get_latest_market_index_probability()` 결과 컬럼 확인.
- scratchpad 일봉(`idx.json`)으로 2026-10-22 재계산 값 확인.
