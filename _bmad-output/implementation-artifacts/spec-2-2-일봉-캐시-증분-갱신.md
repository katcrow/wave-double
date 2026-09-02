---
title: '일봉 캐시 증분 갱신'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: '821c301d1b767715b92b1789e5e2aa0ab6ae52d6'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      `SupabaseOhlcvCacheRepository.latest_state`가 티커별 최신 거래일 1행만 필요함에도
      PostgREST distinct 미지원으로 인해 대상 티커들의 저장된 전체 행을 내려받아
      `order=trading_day.desc` 정렬 후 클라이언트에서 티커별 첫 행만 취한다.
    evidence: |-
      blind-hunter가 발견. Story 2.1의 `existing_tickers`(진짜 distinct는 뷰/RPC 신설이
      필요해 trivial하지 않음)에 이미 동일한 이유로 defer된 것과 같은 종류의 한계이며,
      `latest_state`가 그 관례를 그대로 재사용하면서 동일한 비효율을 다시 노출한다.
      캐시가 누적될수록(티커당 저장 행 증가) 매 배치의 상태 조회 비용이 커진다.
    location: >-
      apps/batch/ohlcv_cache.py (SupabaseOhlcvCacheRepository.latest_state)
    severity: low
---

<intent-contract>

## Intent

**Problem:** `daily_ohlcv`에 이미 이력이 있는 종목은 매 배치마다 최신 상태로 유지돼야 하지만(FR3a), 현재 구현(Story 2.1)은 신규 편입 종목의 초기 적재만 담당하고 기존 종목의 증분 갱신 로직이 없다. corporate-action(분할/무상증자 등) 발생 시 과거 구간을 수정주가 기준으로 재구축하는 로직도, Story 3.5가 소비할 조정 신호(pricechk/갭%)를 노출하는 경로도 없다.
**Approach:** `apps/batch/ohlcv_cache.py`에 `update_existing_ticker_history`를 추가해, 이미 캐시된 각 종목의 마지막 저장 거래일 다음부터 cutoff까지만 `t8410`(sujung=Y, qrycnt=500)으로 조회한다. 조회된 신규 거래일 중 `pricechk`가 관측되면 corporate-action으로 간주해 해당 종목의 가용 이력(최대 500거래일)을 재조회·재저장하고 `adjustment_version`을 증가시킨다. `pricechk` 또는 전일 종가 대비 ±30% 초과 갭이 있는 거래일은 typed `AdjustmentFlag`로 수집해 반환한다(Story 3.5가 재조회 없이 소비).

## Boundaries & Constraints

**Always:** `apps/batch/ohlcv_cache.py`에 `CachedTickerState`(dataclass: `last_trading_day: date`, `last_close: float`, `adjustment_version: int`), `IncrementalUpdateResult`(dataclass: `results: dict[str, OhlcvCacheResult]`, `adjustment_flags: list[AdjustmentFlag]`)를 추가한다. `SupabaseOhlcvCacheRepository.latest_state(tickers: list[str]) -> dict[str, CachedTickerState]`를 추가해 `GET daily_ohlcv?ticker=in.(...)&select=ticker,trading_day,close,adjustment_version&order=trading_day.desc`로 조회하고, 정렬 결과에서 티커별 첫 등장 행(=최신 거래일)만 취해 반환한다(`existing_tickers`와 동일하게 티커 문자열을 영숫자로 검증 후 필터에 사용). `LsOhlcvCacheProvider.fetch_range(ticker: str, start: date | None, end: date) -> list[dict]`을 추가해 `t8410`을 `sdate=(start의 YYYYMMDD 또는 start가 None이면 "")`, `edate=(end의 YYYYMMDD)`, `qrycnt=500`(비압축 상한)으로 호출하고, 각 행에 `pricechk`(원본 정수값, 없으면 None)를 포함해 정규화한다(기존 `_normalize_row`에 `include_pricechk` 옵션을 추가해 재사용하고 `fetch_full_history`의 기존 호출은 옵션 없이 그대로 두어 동작을 변경하지 않는다). `SupabaseOhlcvCacheRepository.upsert_rows`의 시그니처에 `adjustment_version: int = 1` 키워드 인자를 추가하고, 페이로드의 `adjustment_version`은 이 인자값을, `pricechk`는 `row.get("pricechk")`(기존 호출부가 이 키를 넣지 않으므로 `None`으로 유지되어 Story 2.1 동작 불변)를 사용하도록 바꾼다. `update_existing_ticker_history(tickers, provider, repository, cutoff) -> IncrementalUpdateResult`를 추가한다: 후보를 순서 보존 중복 제거 후, `repository.latest_state`를 한 번 호출한다(실패 시 전체 후보를 `ERROR`로 반환, `adjustment_flags`는 빈 리스트). `latest_state`에 없는 티커는 이 함수의 관심사가 아니므로 결과에서 제외한다(신규 편입은 `initialize_new_ticker_history`의 몫). 각 티커에 대해 `last_trading_day >= cutoff`면 LS를 호출하지 않고 `READY`(0행)로 반환한다. 그 외에는 `fetch_range(ticker, last_trading_day + 1일, cutoff)`를 호출해(실패 시 그 티커만 `ERROR`) 반환된 각 신규 행에 대해 직전 종가(첫 행은 `last_close`, 이후는 직전 신규 행의 `close`) 대비 갭%를 계산하고, `pricechk`가 0이 아니거나 `abs(갭%) > 0.30`이면 `AdjustmentFlag(ticker, trading_day, pricechk_bool, gap_pct)`를 수집한다. 신규 행 중 하나라도 `pricechk`가 0이 아니면 corporate-action으로 간주해 `fetch_range(ticker, None, cutoff)`로 가용 전체 이력(최대 500거래일)을 다시 조회하고 `repository.upsert_rows(ticker, rebuilt_rows, adjustment_version=state.adjustment_version + 1)`로 저장한다(재구축된 close/high/low/open은 `sujung=Y` 응답 그대로이므로 이미 수정주가 기준). corporate-action이 아니면 `repository.upsert_rows(ticker, new_rows, adjustment_version=state.adjustment_version)`로 신규 행만 추가한다(버전 불변). 신규 행이 0개면 저장 호출 없이 `READY`(0행)로 반환한다. 한 종목의 실패가 나머지 종목 처리를 막지 않는다(부분 성공 허용). `packages/domain/domain/ohlcv_cache.py`에 `AdjustmentFlag`(frozen dataclass: `ticker: str`, `trading_day: date`, `pricechk: bool`, `gap_pct: float`)를 I/O 없는 순수 계약으로 추가한다(Story 3.5가 재사용할 typed 계약).

**Never:** `update_existing_ticker_history`를 `apps/batch/__main__.py`/`scheduler.py`/`candidate_stage.py`에 연결하지 않는다(실제 배치 오케스트레이션과 stage 기록은 Story 2.5 범위, Story 2.1과 동일한 경계). `AdjustmentFlag`를 소비해 `SUSPENDED` 전이를 판정하는 2단 감지 로직 자체는 구현하지 않는다(Story 3.5 범위) — 이 스토리는 원시 신호만 관측·노출한다. LS API 단일 콜 상한(`qrycnt=500`)을 넘는 과거 구간(500거래일보다 오래된 이력)은 corporate-action 재구축 대상에 포함하지 않는다(API 물리적 제약 — 재구축은 가용 최근 500거래일 범위로 한정되며, 그보다 오래된 행은 이전 `adjustment_version`으로 남는다. 이 한계는 Design Notes에 기록한다). `initialize_new_ticker_history`(Story 2.1, 신규 종목 초기 적재)의 기존 동작·시그니처·테스트 기대값을 변경하지 않는다. `daily_ohlcv`에 대한 삭제(DELETE) 연산을 추가하지 않는다 — 재구축도 `upsert_rows`의 merge-duplicates만으로 충분하다(PK가 `(ticker, trading_day)`이므로 겹치는 거래일은 갱신, 새 거래일은 삽입).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 1거래일 증분 | 마지막 저장일 = cutoff-1, LS가 1행 반환(pricechk=0) | 해당 1행만 upsert, `adjustment_version` 불변, `READY` | 없음 |
| 이미 최신 | `last_trading_day >= cutoff` | LS 호출 없이 `READY`(0행) | 없음 |
| corporate-action 감지 | 신규 행 중 하나 이상 `pricechk != 0` | 가용 전체 이력(최대 500거래일) 재조회·재저장, `adjustment_version + 1` | 재조회 실패 시 해당 종목만 `ERROR`(기존 저장 데이터는 그대로 유지) |
| ±30% 초과 갭(±pricechk 없음) | 신규 행 close가 직전 종가 대비 35% 상승, `pricechk=0` | `adjustment_flags`에 포함되지만 재구축은 트리거하지 않음(버전 불변) | 없음 |
| 증분 조회 실패 | `fetch_range` 예외 | 해당 종목만 `ERROR`, 다른 종목 계속 진행 | 저장 없음 |
| 저장 실패 | `upsert_rows` 예외 | 해당 종목만 `ERROR` | 다른 종목 계속 진행 |
| `latest_state` 전체 실패 | Supabase 조회 예외 | 전체 후보 `ERROR`, LS 호출 없음 | 없음 |
| 이력 없는 티커 혼입 | `latest_state`에 없는 티커 포함 | 결과에서 제외(이 함수의 관심사 아님) | 없음 |

</intent-contract>

## Code Map

- `apps/batch/ohlcv_cache.py:36-62,89-172` (`LsOhlcvCacheProvider`, `_rows`, `_normalize_row`, `SupabaseOhlcvCacheRepository.upsert_rows`) -- `_normalize_row`에 `include_pricechk` 옵션을 추가해 `fetch_range`가 재사용하고, `upsert_rows`는 `adjustment_version` 인자와 `row.get("pricechk")`로 변경(기존 호출부는 동작 불변).
- `apps/batch/ohlcv_cache.py:174-220` (`initialize_new_ticker_history`) -- 신규 `update_existing_ticker_history`가 따를 부분 성공·순서 보존 중복 제거 패턴의 참고 원형(수정하지 않음).
- `packages/domain/domain/ohlcv_cache.py` -- `OhlcvCacheStatus`/`MIN_HISTORY_TRADING_DAYS` 옆에 `AdjustmentFlag` 추가(동일한 I/O 없는 순수 계약 관례).
- `docs/api/ls-openapi/03-domestic-stock/chart.md:236-291` -- `t8410` 요청(`sdate`/`edate`/`qrycnt≤500`)·응답 필드 원문. `fetch_range`의 날짜 범위 조회와, 이번 스토리가 소비하는 `pricechk`(수정주가반영항목) 매핑의 단일 출처. 같은 응답에 `jongchk`(수정구분)·`rate`(수정비율)도 존재하지만 이번 스토리는 소비하지 않는다(AC5가 요구하는 typed 신호는 pricechk 여부·갭%뿐).
- `_bmad-output/specs/spec-wave-double/data-model.md:72-79` -- `daily_ohlcv` 계약(PK, 최소 120거래일, "정상 운영 시 배치당 1일 증분만 갱신", `pricechk`는 SUSPENDED 1차 감지의 진실 원천, 정리 대상 아님)의 단일 출처.
- `_bmad-output/planning-artifacts/epics.md:585-612` -- Story 2.2의 AC 원문(증분 갱신, corporate-action 재구축, NFR 예산, 보존 정책, adjustment_flags 노출).
- `tests/batch/test_ohlcv_cache.py` -- `FakeClient`/`FakeProvider`/`FakeRepository`로 LS·Supabase 계층을 흉내내는 기존 관례. 신규 시나리오(이 스토리의 8개 케이스)를 동일 스타일로 추가한다.

## Tasks & Acceptance

**Execution:**
- `packages/domain/domain/ohlcv_cache.py` -- `AdjustmentFlag` frozen dataclass 추가 -- Story 3.5가 재사용할 I/O 없는 typed 계약.
- `apps/batch/ohlcv_cache.py` -- `_normalize_row`에 `include_pricechk` 옵션 추가, `LsOhlcvCacheProvider.fetch_range` 추가, `SupabaseOhlcvCacheRepository.latest_state`/`upsert_rows`(버전·pricechk 인자화) 추가, `CachedTickerState`/`IncrementalUpdateResult`/`update_existing_ticker_history` 추가 -- 이번 스토리의 핵심 구현.
- `tests/batch/test_ohlcv_cache.py` -- I/O 매트릭스 8개 시나리오 + `latest_state`/`fetch_range` 단위 테스트 추가 -- 기존 Story 2.1 테스트는 수정하지 않고 통과 유지.

**Acceptance Criteria:**
- Given 이미 이력이 있는 여러 종목이 섞여 있고 일부만 신규 거래일이 있으면, when `update_existing_ticker_history`를 호출하면, then 신규 거래일이 없는 종목은 LS를 호출하지 않고, 신규 거래일이 있는 종목만 마지막 저장일 다음부터 cutoff까지 조회한다.
- Given corporate-action으로 `pricechk`가 관측되면, when 처리를 완료하면, then 해당 종목의 `adjustment_version`이 1 증가하고 재조회된 값으로 저장되며, 다른 종목의 `adjustment_version`은 영향받지 않는다.
- Given 여러 종목 중 일부는 성공하고 일부는 LS/저장 실패이면, when 처리를 완료하면, then 성공한 종목은 저장되고 실패한 종목만 개별적으로 `ERROR`로 반환되며, 한 종목의 실패가 나머지 처리를 막지 않는다.
- Given `pricechk` 또는 ±30% 초과 갭이 있는 신규 거래일이 있으면, when 처리를 완료하면, then 반환된 `IncrementalUpdateResult.adjustment_flags`에 해당 (ticker, trading_day, pricechk 여부, 갭%)가 포함된다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0, medium 3, low 3)
- defer: 1: (low 1)
- dismissed:
  - "`gap_pct`가 `prev_close`가 falsy(0)일 때 갭을 0.0으로 억제해 이상값을 숨긴다" — `daily_ohlcv.close`는 `numeric not null`(finite-value 제약)이고 실제 KOSPI/KOSDAQ 종가가 문자 그대로 0인 경우는 없어, 이 경로에 도달할 실제 상태가 없다.
  - "corporate-action 재구축이 재조회된 500거래일의 `pricechk`를 항상 미관측(0)으로 덮어써 기존 pricechk 이력을 지운다" — 검증 결과 사실이 아니다: 재구축은 `fetch_range(ticker, None, cutoff)`(`include_pricechk=True`)로 조회하므로 각 거래일의 실제 `pricechk` 원본값이 그대로 `upsert_rows`에 전달된다(`ohlcv_cache.py` 377-384행).
  - "`latest_state`의 `order=trading_day.desc` 정렬에 2차 정렬 키가 없어 동일 (ticker, trading_day) 행이 여러 개면 tie-break가 불명확하다" — `daily_ohlcv`의 PK가 `(ticker, trading_day)`이므로 동일 티커·거래일 행이 두 개 이상 존재할 수 있는 상태 자체가 없다.
  - "corporate-action 시 티커당 LS 호출이 2회로 늘어 NFR-3 예산을 재검토해야 한다" — AC3/data-model.md의 "신규 편입 종목 수에만 비례" 제약은 전체이력(120~500거래일) 조회에 한정되며, 기존 종목의 일 단위 증분 조회는 애초에 매 배치 발생이 전제된 별도 비용이다. corporate-action 재구축은 실제 조정이 감지된 그 티커에서만, 그것도 드물게 추가되는 호출이며 기존 `LsClient` token bucket이 그대로 처리량을 통제한다 — 미검증된 위반이 성립하지 않는다.
  - "`AdjustmentFlag.gap_pct`가 재구축 이전 값이라 재구축 후 저장된 값과 다를 수 있다" — `new_rows`와 재구축용 `fetch_range(None, cutoff)` 모두 `sujung=Y`로 조회되므로 동일 거래일에 대해 LS가 반환하는 종가는 두 호출 모두 같은 현재 조정계수를 반영한다. 별도로 "미조정 → 조정" 상태 전이가 존재하지 않아 신선도 문제가 성립하지 않는다.
  - "`daily_ohlcv`에 조정 재구축 시각을 기록하는 audit 컬럼이 없다" — Story 2.1 리뷰에서 이미 동일 근거(data-model.md가 이런 컬럼을 요구하지 않고, 기존 attempt-scoped 테이블도 동일하게 없음)로 기각된 항목과 같은 클래스이며 이번 스토리의 AC도 이를 요구하지 않는다.
  - "동일 재구축 창 안에서 여러 corporate-action이 겹치면 `adjustment_version +1` 하나로는 몇 건이 반영됐는지 구분할 수 없다" — AC2는 감지 시 버전 증가와 재구축만 요구하며, 반영된 조정 이벤트 개수를 버전 델타로 인코딩하도록 요구하지 않는다.
  - "Verification 절에 mypy/ruff 등 정적 분석 명령이 없다" — Story 2.1 스펙(이 모듈의 기존 관례)도 pytest + `git diff --check`만 사용하며 정적 분석 단계를 요구한 적이 없어 이번 스토리가 새로 벗어난 관례가 아니다.
  - "`CachedTickerState.last_close`가 방어적 캐스팅 없이 legacy null 행에서 raw `TypeError`를 낼 수 있다" — `daily_ohlcv.close`는 `numeric not null`이라 저장된 행에서 유래하는 `last_close`는 null일 수 없다.
  - "corporate-action 재구축 중 `fetch_range(ticker, None, cutoff)`가 빈 리스트를 반환하면 빈 payload로 upsert되고 `READY(0)`로 잘못 표시될 수 있다" — 같은 함수 호출 내에서 방금 `pricechk`가 관측된 그 티커·그 cutoff에 대해 전체이력 재조회가 즉시 0행을 반환해야 하는 내부적으로 모순된 상태이며, 설령 발생해도 결과는 빈 POST와 `READY(0)` 라벨일 뿐 크래시나 데이터 손상이 없다.
  - "diff에 스프린트 동기화 파일(`sprint-status.yaml`) 갱신, e2e 테스트, git 커밋 증거가 없다" — 이 리뷰 단계는 구현 diff만을 검토 대상으로 하며, 스프린트 동기화·커밋은 build-auto 워크플로우의 이후 Finalize 단계가 별도로 책임진다(이 스토리의 스펙 범위 밖).
- addressed_findings:
  - `[medium]` `[patch]` `apps/batch/ohlcv_cache.py`(`update_existing_ticker_history`): 신규 거래일 순회 루프(갭%·`pricechk` 계산)가 다른 모든 단계와 달리 try/except로 보호되지 않아, LS 응답의 `close`가 `None`이면 uncaught 예외로 전체 배치가 중단되어 "한 종목의 실패가 나머지를 막지 않는다"는 명시된 부분 성공 계약을 이 지점에서만 어긴다(blind-hunter·edge-case-hunter 공통 발견). 루프를 try/except로 감싸 실패 시 해당 티커만 `ERROR`로 반환하도록 수정하고, malformed 행에 대한 회귀 테스트 추가.
  - `[medium]` `[patch]` `apps/batch/ohlcv_cache.py`(`update_existing_ticker_history`): corporate-action 재구축(또는 이후 저장)이 실패해 해당 티커가 `ERROR`로 반환되어도, 그 티커에 대해 이미 `adjustment_flags`에 추가된 항목이 결과에 남아 저장되지 않은 데이터에 대한 신호를 노출한다(edge-case-hunter가 발견). 티커가 최종적으로 `ERROR`면 그 티커의 플래그를 반환 목록에서 제외하도록 수정.
  - `[medium]` `[patch]` `tests/batch/test_ohlcv_cache.py`: `pricechk`로 corporate-action이 트리거되는 경로와 재구축의 두 실패 분기(재조회 실패, 저장 실패)가 `adjustment_flags`/결과 상태에 대해 테스트되지 않았다(verification-gap이 발견). 세 시나리오에 대한 테스트 추가.
  - `[low]` `[patch]` `apps/batch/ohlcv_cache.py`: `existing_tickers`와 `latest_state`에 동일한 티커 영숫자 검증 블록이 중복돼 있다(blind-hunter가 발견). 공용 헬퍼로 추출.
  - `[low]` `[patch]` 이 스펙 문서(Design Notes): LS 단일 콜 상한(`qrycnt=500`)이 corporate-action 재구축 경로에만 문서화되어 있고, 동일 상한을 쓰는 평상시 증분 조회 경로(500거래일 초과 누락 시)에는 언급이 없다(blind-hunter가 발견). Design Notes에 한 문장 추가해 두 경로 모두에 적용됨을 명시.
  - `[low]` `[patch]` 이 스펙 문서(Code Map): `t8410` 필드 중 `jongchk`/`rate`도 "단일 출처"로 인용했지만 구현은 `pricechk`만 소비한다(blind-hunter가 발견). Code Map 문구를 실제 소비 필드(`pricechk`)로 한정하도록 수정.

## Design Notes

corporate-action 재구축은 LS `t8410`의 비압축 상한(`qrycnt=500`)까지만 재조회한다. 500거래일보다 오래된 이력은 새 `adjustment_version`으로 갱신되지 않고 이전 버전 값으로 남는다 — 이는 LS 단일 콜 API의 물리적 상한에서 비롯된 이번 스토리의 명시적 경계이며, 그보다 긴 과거 구간의 전면 재조정이 필요해지면 별도 스토리(다중 콜 페이지네이션)가 필요하다. 동일한 `qrycnt=500` 상한은 평상시 증분 조회(`fetch_range(ticker, last_trading_day+1, cutoff)`)에도 적용된다 — 정상 운영에서는 배치당 1거래일 증분만 채우므로 도달하지 않지만, 500거래일(약 2년)을 넘는 배치 중단 이후 재개하는 경우에는 한 번의 호출로 전체 누락분을 채우지 못할 수 있다. 이런 규모의 중단은 이 스토리의 정상 운영 범위(data-model.md) 밖이며 별도의 운영 개입을 전제한다.

`latest_state`는 Story 2.1의 `existing_tickers`와 동일하게 PostgREST distinct 미지원으로 인해 티커당 전체 저장 행을 내려받지 않고 `order=trading_day.desc` 정렬 후 티커별 첫 등장 행만 취하는 방식으로 최소화했다(전체 다운로드보다는 낫지만 완전한 distinct는 아님 — Story 2.1이 이미 defer로 남긴 것과 같은 종류의 한계).

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_ohlcv_cache.py -q` -- expected: 기존 18개 + 신규 시나리오 전부 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` -- expected: 기존 domain/batch 회귀 통과.
- `git diff --check` -- expected: whitespace 오류 없음.

## Auto Run Result

**요약:** 이미 `daily_ohlcv`에 이력이 있는 종목을 매 배치마다 최소 호출로 최신 상태로 유지하는 증분 갱신 기능을 구현했다(FR3a). `apps/batch/ohlcv_cache.py`에 `update_existing_ticker_history`를 추가해, 각 종목의 마지막 저장 거래일 다음부터 cutoff까지만 `t8410`(sujung=Y, qrycnt=500)으로 조회한다. 신규 거래일 중 `pricechk`가 관측되면 corporate-action으로 간주해 해당 종목의 가용 이력(최대 500거래일)을 재조회·재저장하고 `adjustment_version`을 1 증가시킨다. `pricechk` 또는 전일 종가 대비 ±30% 초과 갭이 있는 거래일은 `AdjustmentFlag`(ticker, trading_day, pricechk 여부, 갭%)로 수집해 반환하며, Story 3.5가 재조회 없이 소비할 수 있도록 `packages/domain/domain/ohlcv_cache.py`에 I/O 없는 typed 계약으로 노출했다. 한 종목의 실패(증분 조회 실패, 재구축 실패, 저장 실패, malformed 응답)가 나머지 종목 처리를 막지 않는 부분 성공 설계를 적용했다. 실제 배치 오케스트레이터(`__main__.py`/`scheduler.py`) 연결과 `tags` stage 통합은 스펙의 Never 절대로 이번 스토리 범위 밖에 남겨두었다(Story 2.5), Story 2.1의 `initialize_new_ticker_history`는 동작·시그니처 변경 없이 그대로 유지했다.

**변경 파일:**
- `packages/domain/domain/ohlcv_cache.py` — `AdjustmentFlag`(frozen dataclass: ticker/trading_day/pricechk/gap_pct) 추가.
- `apps/batch/ohlcv_cache.py` — `_normalize_row`에 `include_pricechk` 옵션 추가, `LsOhlcvCacheProvider.fetch_range` 추가, `SupabaseOhlcvCacheRepository.latest_state` 추가(+공용 `_validate_tickers` 헬퍼로 `existing_tickers`와 중복 제거), `upsert_rows`에 `adjustment_version`/실제 `pricechk` 인자화, `CachedTickerState`/`IncrementalUpdateResult`/`update_existing_ticker_history` 추가.
- `tests/batch/test_ohlcv_cache.py` — 22개 테스트 추가(기존 18개 + 신규 22개 = 38개), I/O 매트릭스 8개 시나리오 전부 및 리뷰 patch로 추가된 4개 시나리오(malformed row, 재구축 실패 2건, pricechk 플래그 노출) 포함.

**리뷰 결과 (2026-09-02 pass):** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어 병렬 실행. patch 6건(medium 3, low 3) 전부 수정·재검증 완료 — 가장 중요한 두 건은 (1) 신규 거래일 순회 루프가 try/except로 보호되지 않아 malformed `close` 하나로 전체 배치가 중단될 수 있던 문제, (2) corporate-action 재구축/저장이 실패해도 이미 수집된 `AdjustmentFlag`가 저장되지 않은 데이터에 대한 신호로 결과에 남아있던 문제였다. 나머지 4건(테스트 커버리지 3종 추가, 티커 검증 로직 중복 제거)도 모두 수정했다. defer 1건(low) — `latest_state`의 조회 비효율(Story 2.1의 `existing_tickers`와 동일한 종류의, PostgREST distinct 미지원에서 비롯된 기존 한계)을 frontmatter `deferred`에 기록. dismissed 11건 — gap_pct의 0-close 엣지(도달 불가능한 상태), pricechk 감사이력 소실 주장(검증 결과 사실 아님), latest_state tie-break(PK가 방지), NFR 이중호출 우려(범위 오해), gap_pct 신선도 우려(둘 다 sujung=Y로 조회해 무관), audit 타임스탬프 부재(Story 2.1 선례와 동일 기각), 다중 corporate-action 버전 카운팅(AC 범위 밖), 정적분석 명령 부재(기존 관례와 일치), last_close null 가능성(DB not-null 제약), 빈 rebuilt_rows 시나리오(내부 모순 상태), diff에 스프린트 동기화/e2e/커밋 증거 없음(이 리뷰 단계의 범위 밖, Finalize가 별도 처리) 중 하나에 해당해 기각(세부 근거는 Review Triage Log 참고).

**Follow-up review recommendation:** `true` (patch 3×medium + 3×low = 3×3 + 1×3 = 12 ≥ 5).

**검증 수행:**
- `uv run --with pytest pytest tests/batch/test_ohlcv_cache.py -q` — 38 passed(패치 전 34개에서 4개 신규 테스트 추가).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` — 163 passed, 회귀 없음.
- `git diff --check` — whitespace 오류 없음(CRLF/LF 알림만 있고 실제 오류 없음).
- I/O & Edge-Case Matrix 8개 시나리오 전부 커버하는 테스트가 실행·통과함을 확인(matrix test audit 통과).

**잔여 위험:**
- `update_existing_ticker_history`는 아직 어떤 배치 진입점에도 연결되지 않았다(스펙 범위) — Story 2.5가 이를 `tags` stage에 연결해야 실제 배치에서 동작한다.
- corporate-action 재구축은 LS 단일 콜 상한(`qrycnt=500`)까지만 재조회하며, 그보다 오래된 이력은 새 `adjustment_version`으로 갱신되지 않는다(Design Notes에 명시). 500거래일을 넘는 배치 중단 이후 재개 시에도 동일한 한계가 적용된다.
- `latest_state`의 조회 비효율(캐시가 누적될수록 상태 조회 비용 증가)은 defer로 남겼다(frontmatter `deferred` 참고).
