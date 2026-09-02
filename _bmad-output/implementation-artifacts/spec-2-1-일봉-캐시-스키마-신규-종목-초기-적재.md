---
title: '일봉 캐시 스키마 & 신규 종목 초기 적재'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: '10473a5903674cedda3717ed563dc4e967300784'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      `SupabaseOhlcvCacheRepository.existing_tickers`가 이미 캐시된 각 티커에 대해
      `select=ticker`만으로 저장된 모든 `trading_day` 행(최대 120행)을 그대로 내려받아
      단순 존재 여부 확인치고는 비효율적이다.
    evidence: |-
      blind-hunter가 발견. PostgREST는 쿼리 파라미터만으로 서버측 DISTINCT를 제공하지
      않아, 진짜 distinct 조회는 뷰나 RPC 신설이 필요해 이번 패스에서 trivial하게
      고칠 수 없다. 클라이언트 측에서 `{row["ticker"] for row in rows}`로 정확한
      집합을 만들기 때문에 기능적으로는 정확하지만, 캐시가 누적될수록(종목당 최대
      120행) 매 배치의 존재-확인 조회 비용이 커진다.
    location: >-
      apps/batch/ohlcv_cache.py:113-129 (SupabaseOhlcvCacheRepository.existing_tickers)
    severity: low
  - summary: >-
      `SupabaseOhlcvCacheRepository.upsert_rows`가 일시적 5xx에 대한 재시도/backoff
      없이 `raise_for_status()`만 호출해, 이미 성공한 LS 조회 결과가 일시적 저장소
      장애만으로 전부 버려질 수 있다.
    evidence: |-
      blind-hunter가 발견. 이 패턴은 이번 스토리가 새로 도입한 것이 아니라
      `SupabaseCalendarRepository.upsert`(story 1.2)가 이미 동일하게 재시도 없이
      `raise_for_status()`만 쓰는 저장소 전반의 기존 관례를 그대로 재사용한 것이다.
    location: >-
      apps/batch/ohlcv_cache.py:131-154 (SupabaseOhlcvCacheRepository.upsert_rows),
      apps/batch/supabase_client.py:127-144 (SupabaseCalendarRepository.upsert, 선례)
    severity: low
---

<intent-contract>

## Intent

**Problem:** 전략 A/B/C 시그널 계산에는 종목당 최소 120거래일 일봉이 필요하지만, 현재 저장소에는 이 이력을 저장할 스키마도, 신규 편입 종목의 이력을 확보하는 로직도 없다.
**Approach:** `daily_ohlcv` 장기 캐시 테이블을 신설하고, 아직 캐시에 이력이 없는(신규 편입) 종목만 LS `t8410`(sujung=Y, qrycnt=120) 단일 콜로 전체 이력을 적재하는 배치 모듈을 추가한다. 이미 캐시된 종목의 증분 갱신(Story 2.2)과 이 데이터를 소비하는 태깅 stage 연결(Story 2.5)은 이번 스토리 범위 밖이다.

## Boundaries & Constraints

**Always:** `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql`에서 `public.daily_ohlcv`(PK `(ticker, trading_day)`, `open`/`high`/`low`/`close`/`volume` numeric not null with finite-value check(`candidates` 테이블의 NaN/Infinity guard 관례를 그대로 따름), `adjusted boolean not null default true`, `adjustment_version integer not null default 1`, `pricechk integer`(nullable — Story 2.2가 채움, 이번 스토리는 초기 삽입 시 `null`로 둔다))를 생성하고, 같은 migration에서 `alter table ... enable row level security`만 적용한다(정책 없음 — `candidates` 테이블 하드닝 선례와 동일하게 service-role만 우회 접근, anon/authenticated는 전혀 접근 불가). `packages/domain/domain/ohlcv_cache.py`(신규)에 순수 계약 `OhlcvCacheStatus` `StrEnum`(`READY`/`INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR`)과 `MIN_HISTORY_TRADING_DAYS = 120` 상수만 둔다(I/O 없음, `domain/calendar.py`·`domain/run_state.py`와 동일한 층 분리). `apps/batch/ohlcv_cache.py`(신규)에 세 요소를 구현한다: (1) `LsOhlcvCacheProvider.fetch_full_history(ticker, cutoff: date)` — `t8410`을 `shcode=ticker, gubun="2", qrycnt=120, sdate="", edate=cutoff의 YYYYMMDD, cts_date="", comp_yn="N", sujung="Y"`로 호출해(`ls_daily_bar.py`의 요청 구성 스타일을 따름) `t8410OutBlock1`의 `date`/`open`/`high`/`low`/`close`/`jdiff_vol`(거래량, `docs/api/ls-openapi/03-domestic-stock/chart.md:280-285`)을 `{trading_day, open, high, low, close, volume}` 행으로 정규화해 반환하고, `response.ok`가 아니거나 `t8410OutBlock1`이 없거나 list가 아니면 `RuntimeError`를 던진다(`ls_daily_bar.py:44-54`와 동일한 실패 계약); (2) `SupabaseOhlcvCacheRepository` — `SupabaseCalendarRepository`와 동일하게 REST 직접 접근(service-role key)만 쓰며, `existing_tickers(tickers: list[str]) -> set[str]`(`GET daily_ohlcv?ticker=in.(...)&select=ticker`)와 `upsert_rows(ticker, rows) -> None`(`POST` + `Prefer: resolution=merge-duplicates`, `on_conflict=ticker,trading_day`)를 제공; (3) `initialize_new_ticker_history(candidates: list[str], provider, repository, cutoff: date) -> dict[str, OhlcvCacheResult]` — `repository.existing_tickers(candidates)`에 없는 티커만 신규로 간주해 순회하며(이미 이력 있는 티커는 LS를 호출하지 않음 — Story 2.2 범위), 각 신규 티커에 대해 `provider.fetch_full_history`를 호출: 예외 또는 실패 응답이면 저장 없이 `ERROR`; 반환 행 수가 `MIN_HISTORY_TRADING_DAYS` 미만이면 저장 없이 `INELIGIBLE_INSUFFICIENT_HISTORY`(저장 컬럼이 아닌 반환값 계약, data-model.md); 그 외에는 `repository.upsert_rows` 호출 후 `READY`(이 호출이 예외를 던지면 `ERROR`). 한 종목의 실패가 나머지 종목 처리를 막지 않는다(부분 성공 허용). 신규 티커 호출은 순차 실행이며, `LsClient`(Story 1.4)의 TR별 token-bucket이 이미 1건/초를 강제하므로 별도의 처리량 제한 로직을 추가하지 않는다(NFR-3).

**Never:** `initialize_new_ticker_history`를 `apps/batch/__main__.py`/`scheduler.py`/`candidate_stage.py`에 연결하지 않는다 — `domain/run_state.py`의 `Stage` 파이프라인에는 아직 이 캐시를 위한 stage가 없고(`__main__.py`는 현재 candidates stage만 호출), 실제 배치 통합과 stage-status 기록은 Story 2.5의 몫이다. 기존에 이력이 있는 티커의 증분 갱신, corporate-action `adjustment_version` 재계산, `pricechk`/갭 기반 `adjustment_flags` 감지는 구현하지 않는다(Story 2.2 범위) — `pricechk` 컬럼은 생성만 하고 이번 스토리의 초기 삽입에서는 항상 `null`로 둔다. `backtest.strategy_api.compute_abc`(Story 2.3)나 `tags` stage/`candidate_tags` 저장(Story 2.5)을 구현하지 않는다. `daily_ohlcv`는 attempt-scoped 테이블이 아니므로(PK에 `run_id` 없음, data-model.md) 신규 `write_*` RPC나 `RunStateGateway` fencing을 추가하지 않는다 — `trading_calendar`의 `SupabaseCalendarRepository`와 동일하게 service-role REST 직접 upsert로 충분하다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 신규 종목, 이력 충분 | `daily_ohlcv`에 없는 티커, LS가 120행 반환 | `READY`, 120행 upsert | 없음 |
| 신규 종목, 이력 부족(상장 이력 짧음) | `daily_ohlcv`에 없는 티커, LS가 <120행 반환 | `INELIGIBLE_INSUFFICIENT_HISTORY` 반환, 저장하지 않음 | 조용히 누락되지 않고 명시적 상태로 반환 |
| 이미 캐시된 종목 | 티커가 이미 `daily_ohlcv`에 존재 | LS 호출 없이 건너뜀(Story 2.2 범위) | 없음 |
| LS 호출 실패/malformed 응답 | `t8410` 예외 또는 `response.ok`가 False | `ERROR` 반환, 저장 없음 | 예외를 상위로 전파하지 않고 상태값으로 변환(retryable로 재시도 가능) |
| Supabase 저장 실패 | fetch는 성공했으나 `upsert_rows`가 예외 | `ERROR` 반환 | 해당 종목만 실패 처리, 다른 종목 계속 진행 |
| 여러 종목 동시 신규 편입 | N개 신규 티커 | `LsClient` token bucket으로 순차 1건/초 처리, 신규 종목 수에만 비례한 호출량 | 없음 |

</intent-contract>

## Code Map

- `apps/batch/ls_daily_bar.py:20-54` (`LsDailyBarProvider`) -- `t8410` 요청 구성·응답 파싱·실패 시 `RuntimeError` 계약의 참고 원형. 신규 `LsOhlcvCacheProvider`는 동일 TR을 `qrycnt=120`·다종목으로 재사용하되 이 클래스를 상속/수정하지 않고 별도 구현한다(단일 콜 캘린더 판정용과 책임이 다름).
- `docs/api/ls-openapi/03-domestic-stock/chart.md:230-291` -- `t8410` 요청/응답 필드 원문. `t8410OutBlock1`은 `date`/`open`/`high`/`low`/`close`/`jdiff_vol`(거래량)/`value`/`jongchk`/`rate`/`pricechk`/`ratevalue`/`sign`를 포함하며, 신규 provider의 필드 매핑은 이 표를 그대로 따른다.
- `apps/batch/ls_client.py:107-272` (`LsClient`) -- TR별 token bucket으로 1건/초를 강제하는 공유 클라이언트. 신규 provider는 이 클라이언트의 `request(tr_code, params)`만 호출하고 별도 rate limiting을 구현하지 않는다.
- `apps/batch/supabase_client.py:83-160` (`SupabaseCalendarRepository`) -- attempt-scoped가 아닌 테이블에 대한 REST 직접 GET/POST(`Prefer: resolution=merge-duplicates`) 패턴의 참고 원형. 신규 `SupabaseOhlcvCacheRepository`가 동일 구조를 따른다.
- `apps/batch/candidate_stage.py:43-145` (`run_candidate_stage`) -- "한 종목/한 원천의 실패가 전체를 막지 않는다"는 부분 성공 설계의 참고 원형(단, 이 stage 자체는 attempt-scoped RPC를 쓰므로 신규 모듈이 그대로 재사용하지는 않는다).
- `packages/domain/domain/calendar.py:11-14` (`CalendarStatus`), `packages/domain/domain/run_state.py:36-50` (`Stage`/`StageStatus`) -- I/O 없는 순수 상태 enum을 domain 패키지에 두는 기존 관례. 신규 `OhlcvCacheStatus`가 동일 패턴을 따른다.
- `packages/domain/domain/run_state.py:36-53` (`Stage`, `STAGES`, `REQUIRED_STAGES`) -- `Stage` enum에는 아직 OHLCV 전용 stage가 없음(candidates/tags/supply_3day/market_supply/outcome_tracking만 존재)을 확인. 이번 스토리가 stage 파이프라인에 개입하지 않는 근거.
- `apps/batch/__main__.py:44-76` (`run`) -- 현재 candidates stage만 호출하는 실제 배치 진입점. 신규 모듈을 여기에 연결하지 않는다(Story 2.5 범위).
- `infra/supabase/migrations/202609011700_create_candidates.sql`, `202609011800_harden_candidate_rls.sql` -- 테이블 생성 + RLS enable(정책 없음) 조합의 선례. 신규 migration이 동일 조합을 한 파일 안에서 적용한다.
- `_bmad-output/specs/spec-wave-double/data-model.md:72-79` -- `daily_ohlcv` 컬럼·PK·상태 계약(`READY`/`INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR`, 저장 컬럼 아님)의 단일 출처.
- `tests/sql/test_candidates.sql` -- `pg_class.relrowsecurity`로 RLS 활성화를 검증하는 SQL fixture 패턴. 신규 `tests/sql/test_daily_ohlcv.sql`이 동일 패턴을 따른다.
- `tests/batch/test_ls_daily_bar.py`, `tests/batch/test_candidate_stage.py` -- `FakeClient`/`FakeRpc`로 LS·Supabase 계층을 흉내내는 기존 테스트 관례. 신규 `tests/batch/test_ohlcv_cache.py`가 동일 스타일을 따른다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql`(신규) -- `public.daily_ohlcv` 테이블(PK `(ticker, trading_day)`, finite-value 제약, `adjusted`/`adjustment_version`/`pricechk`) 생성 + RLS enable(정책 없음) -- data-model.md의 스키마를 물리적으로 구현하고 anon/authenticated 접근을 원천 차단.
- `packages/domain/domain/ohlcv_cache.py`(신규) -- `OhlcvCacheStatus` `StrEnum` + `MIN_HISTORY_TRADING_DAYS = 120` -- Story 2.3(전략 API)도 참조할 상태 계약을 I/O 없는 domain 층에 둔다.
- `apps/batch/ohlcv_cache.py`(신규) -- `LsOhlcvCacheProvider`, `SupabaseOhlcvCacheRepository`, `OhlcvCacheResult`(dataclass: `ticker`, `status`, `trading_days`, `message`), `initialize_new_ticker_history` -- 신규 편입 종목만 골라 `t8410` 단일 콜로 이력을 확보·저장하고 상태를 반환.
- `tests/batch/test_ohlcv_cache.py`(신규) -- I/O 매트릭스의 6개 시나리오(이력 충분/부족/기존 종목 스킵/LS 실패/저장 실패/다건 처리 시 순차 호출)를 `FakeClient`/fake repository로 커버.
- `tests/sql/test_daily_ohlcv.sql`(신규) -- PK/finite 제약/RLS 활성화, anon/authenticated에 write 권한 없음을 검증.

**Acceptance Criteria:**
- Given migration을 적용하면, when `information_schema.columns`와 `pg_class.relrowsecurity`로 `daily_ohlcv`를 확인하면, then PK `(ticker, trading_day)`가 존재하고 RLS가 활성화되어 있으며 anon/authenticated 역할에 어떤 write 권한도 부여되지 않는다.
- Given 신규 편입 후보 목록과 이미 `daily_ohlcv`에 이력이 있는 티커 집합이 섞여 있으면, when `initialize_new_ticker_history`를 호출하면, then 이미 이력이 있는 티커는 `t8410`을 호출하지 않고, 신규 티커만 호출 대상이 된다(과다 호출 방지, NFR-3).
- Given 여러 신규 티커 중 일부는 성공하고 일부는 LS/저장 실패인 경우, when 처리를 완료하면, then 성공한 티커는 저장되고 실패한 티커만 개별적으로 `ERROR`/`INELIGIBLE_INSUFFICIENT_HISTORY`로 반환되며, 한 종목의 실패가 나머지 종목 처리를 중단시키지 않는다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7: (high 0, medium 2, low 5)
- defer: 2: (low 2)
- dismissed:
  - "신규 종목 이력 중 한 행이라도 not-null 위반이면 `upsert_rows`가 그 종목의 120행 전체를 저장 실패로 버린다(부분 성공이 row 단위로는 없음)" — 스펙의 "부분 성공"은 명시적으로 종목 단위("한 종목의 실패가 나머지 종목 처리를 막지 않는다")로 범위가 한정되며, data-model.md도 row 단위 부분 저장을 요구하지 않는다. 해당 종목이 `ERROR`(retryable)로 반환되는 현재 동작은 스펙 범위 안이다.
  - "`daily_ohlcv`에 OHLC 상호 정합성 제약(high>=low 등)이 없다" — data-model.md가 이 테이블 스키마의 단일 권위 출처이며 이런 교차 컬럼 검증을 요구하지 않는다. `candidates` 등 기존 테이블에도 동일한 관례가 없다.
  - "`MIN_HISTORY_TRADING_DAYS=120`이 주봉 %K(20-3) 계산에 여유가 부족할 수 있다" — 이 값은 data-model.md/AD-5에서 그대로 가져온 것으로, 이 상수의 타당성은 이번 스토리가 아니라 아키텍처(AD-5)/Story 2.3의 권한이다.
  - "`daily_ohlcv`에 생성/갱신 시각 audit 컬럼이 없다" — data-model.md가 이런 컬럼을 요구하지 않으며, `candidates` 등 기존 attempt-scoped 테이블도 동일하게 없다.
  - "타임아웃이 `initialize_new_ticker_history` 밖으로 처리되지 않은 채 전파될 수 있다" — `httpx` 타임아웃 예외는 `Exception`의 하위 타입이므로 이미 존재하는 `except Exception` 블록에 잡혀 `ERROR`로 정상 변환된다(검증 완료, 실제 결함 없음, 테스트 커버리지 보강 여지만 있음).
  - "`initialize_new_ticker_history`/repository에 로깅·관측 지표가 없어 NFR-3 예산 준수를 운영에서 확인할 수 없다" — epic-2-context.md의 Cross-Story Dependencies가 배치 오케스트레이션·관측을 Story 2.5의 몫으로 명시하며, 이 스토리는 아직 어떤 배치 진입점에도 연결되지 않는다(스펙 Never 절).
  - "frontmatter `warnings: [oversized]`가 Design Notes에서 설명되지 않는다" — 수정하려면 스펙 문서 자체를 편집해야 하는 항목이라 규칙상 기각한다.
  - "다수 신규 티커를 하나의 `in.(...)` 쿼리스트링에 담을 때 길이 상한 가드가 없다" — NFR-7이 후보 모집단을 최대 150종목·6자리 티커로 제한하므로 쿼리스트링 길이가 약 1,050자를 넘지 않아 실질적 상한을 벗어나는 경로가 없다.
- addressed_findings:
  - `[medium]` `[patch]` `.github/workflows/test.yml`의 "Scheduler tests (Python)"·`sql-outbox-tests` 스텝이 파일을 명시적으로 나열하는 방식이라, 신규 `tests/batch/test_ohlcv_cache.py`와 `tests/sql/test_daily_ohlcv.sql`이 CI에서 전혀 실행되지 않았다(verification-gap이 발견, 직접 파일 재확인으로 검증). 두 스텝의 파일 목록에 추가.
  - `[medium]` `[patch]` `apps/batch/ohlcv_cache.py`(`initialize_new_ticker_history`): `repository.existing_tickers(candidates)` 호출에 예외 처리가 없어, 이 호출 하나가 실패하면 (개별 신규 티커 실패와 달리) 전체 후보가 처리되지 못한 채 예외가 그대로 전파되어 "조용한 누락 금지" 원칙을 이 지점에서만 어겼다(edge-case-hunter가 발견, 코드 직접 확인으로 검증). try/except로 감싸 실패 시 전체 후보를 `ERROR`로 반환하도록 수정.
  - `[low]` `[patch]` `apps/batch/ohlcv_cache.py`(`initialize_new_ticker_history`): `candidates` 입력에 중복 티커가 있으면 같은 티커를 LS에 중복 호출하고(NFR-3 비례 원칙 위반) 반환 dict에서 이전 결과가 조용히 덮어써진다(edge-case-hunter·blind-hunter 공통 발견). 신규 티커 목록을 순서 보존 중복 제거하도록 수정.
  - `[low]` `[patch]` `apps/batch/ohlcv_cache.py`(`LsOhlcvCacheProvider.fetch_full_history`): 실패 시 `response.result_code`만 담고 `response.message`(진단 정보)를 버린다(blind-hunter가 발견). 메시지도 함께 포함하도록 수정.
  - `[low]` `[patch]` `apps/batch/ohlcv_cache.py`(`_normalize_row`): `date` 필드가 없거나 형식이 어긋나면 모듈의 나머지 실패 계약(명시적 `RuntimeError`)과 다르게 원시 `KeyError`/`ValueError`가 새어나간다(blind-hunter가 발견, `initialize_new_ticker_history`의 포괄 예외 처리로 기능상 영향은 없으나 `LsOhlcvCacheProvider`를 직접 쓰는 호출자에는 계약 불일치). try/except로 감싸 일관된 `RuntimeError`를 던지도록 수정.
  - `[low]` `[patch]` `tests/sql/test_daily_ohlcv.sql`: finite-value 제약 검증이 `close`의 NaN 거부만 다루고 `open`/`high`/`low`/`volume`은 검증하지 않는다(edge-case-hunter·blind-hunter 공통 발견, "PK/제약/RLS 검증"이라는 스펙의 작업 서술과도 어긋남). 나머지 4개 컬럼에 대한 NaN 거부 검증 추가.
  - `[low]` `[patch]` `apps/batch/ohlcv_cache.py`(`SupabaseOhlcvCacheRepository.existing_tickers`): 티커 문자열을 검증 없이 PostgREST `in.(...)` 필터에 그대로 이어붙여, 쉼표·괄호를 포함한 값이 들어오면 필터 구문이 조용히 깨질 수 있다(blind-hunter가 발견). 각 티커가 영숫자만으로 구성되었는지 검증하고 위반 시 명시적으로 실패하도록 수정.

## Design Notes

`t8410`의 `sdate`는 문서상 "처음조회기준일", `edate`는 "조회구간종료일(LE)"로 표기가 다소 혼란스럽지만, `qrycnt=120`과 함께 `edate`를 조회 기준일(cutoff 거래일)로, `sdate`를 빈 문자열로 두면 LS가 `edate` 이전 최근 120거래일을 반환한다(`ls_daily_bar.py`가 이미 이 방식으로 단일 콜을 구성하는 선례). `INELIGIBLE_INSUFFICIENT_HISTORY`는 data-model.md에 "저장 컬럼이 아닌 adapter 응답 계약"으로 명시되어 있으므로, 이 상태를 별도 테이블이나 컬럼에 기록하지 않고 `initialize_new_ticker_history`의 반환값으로만 전달한다 — 이 상태를 후보 화면에 노출하는 저장 위치(예: candidates 상태 컬럼)는 Story 2.5/2.7이 결정할 몫이다.

`daily_ohlcv`는 `candidates`와 달리 attempt-scoped가 아니다(PK에 `run_id`가 없다, data-model.md). 그래서 `write_candidates`처럼 fencing을 검증하는 Postgres RPC가 필요하지 않고, `trading_calendar`가 이미 쓰는 "service-role REST 직접 upsert" 패턴을 그대로 재사용하는 것이 이 저장소의 기존 관례와 일치한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_ohlcv_cache.py -q` -- expected: 신규 6개 시나리오 테스트 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` -- expected: 기존 domain/batch 회귀 통과.
- Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 migration 적용 후 `tests/sql/test_daily_ohlcv.sql` 실행 -- expected: PK/제약/RLS 검증 통과.
- `git diff --check` -- expected: whitespace 오류 없음.

## Auto Run Result

**요약:** 전략 A/B/C 시그널 계산에 필요한 120거래일 일봉 이력을 신규 편입 종목에 대해 확보하는 기반을 구현했다. `daily_ohlcv` 장기 캐시 테이블(PK `(ticker, trading_day)`, finite-value 제약, RLS enable·정책 0개로 anon/authenticated 차단)을 프로덕션 Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 직접 적용했고, `t8410`(sujung=Y, qrycnt=120) 단일 콜로 아직 이력이 없는 티커만 전체 이력을 조회·저장하는 배치 모듈을 추가했다. 이미 캐시된 티커는 LS를 호출하지 않으며(Story 2.2 범위), 한 티커의 실패가 나머지 처리를 막지 않는 부분 성공 설계를 적용했다. 실제 배치 오케스트레이터(`__main__.py`/`scheduler.py`) 연결과 `tags` stage 통합은 스펙의 Never 절대로 이번 스토리 범위 밖에 남겨두었다(Story 2.5).

**변경 파일:**
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql`(신규) — `daily_ohlcv` 테이블 생성 + RLS enable. 프로덕션에 적용 완료(`list_migrations`로 확인).
- `packages/domain/domain/ohlcv_cache.py`(신규) — `OhlcvCacheStatus`(`READY`/`INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR`), `MIN_HISTORY_TRADING_DAYS=120`.
- `apps/batch/ohlcv_cache.py`(신규) — `LsOhlcvCacheProvider`, `SupabaseOhlcvCacheRepository`, `OhlcvCacheResult`, `initialize_new_ticker_history`.
- `tests/batch/test_ohlcv_cache.py`(신규) — 18개 테스트, I/O 매트릭스 6개 시나리오 전부 포함.
- `tests/sql/test_daily_ohlcv.sql`(신규) — PK·RLS·finite-value(5개 컬럼 모두) 검증.
- `.github/workflows/test.yml` — 신규 테스트 두 개를 CI 실행 목록에 등록(리뷰 patch).

**리뷰 결과 (2026-09-02 pass):** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어 병렬 실행. patch 7건(medium 2, low 5) 전부 수정·재검증 완료 — 가장 중요한 두 건은 (1) 신규 테스트 2개가 CI 워크플로의 명시적 파일 목록에 없어 전혀 실행되지 않던 문제, (2) `existing_tickers` 조회 실패가 개별 티커 실패와 달리 예외로 전체 후보 처리를 중단시키던 문제였다. 나머지 5건(중복 티커 미제거, LS 실패 메시지 손실, 날짜 파싱 예외 불일치, SQL fixture의 컬럼별 NaN 검증 누락, 티커 문자열 미검증)도 모두 수정했다. defer 2건(low) — `existing_tickers`의 조회 효율성(진짜 distinct는 뷰/RPC가 필요해 trivial하지 않음), `upsert_rows`의 재시도 부재(기존 `SupabaseCalendarRepository` 관례의 연장)를 frontmatter `deferred`에 기록. dismissed 7건 — row 단위 부분성공, OHLC 교차 제약, 120일 기준값, audit 컬럼, 타임아웃 처리(이미 정상 동작 확인), 관측성 훅(Story 2.5 범위), 스펙 문서 자체 수정 요구 중 하나에 해당해 기각(세부 근거는 Review Triage Log 참고).

**검증 수행:**
- `uv run --with pytest pytest tests/batch/test_ohlcv_cache.py -q` — 18 passed(패치 전 12개에서 6개 신규 테스트 추가).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` — 143 passed, 회귀 없음(패치 전 137개).
- `tests/sql/test_daily_ohlcv.sql`을 프로덕션 Supabase 프로젝트에 `begin`/`rollback`으로 감싸 직접 실행 — PK/RLS/5개 컬럼 finite-value 검증 전부 통과, 롤백 후 테이블 0행 확인.
- `git diff --check` — whitespace 오류 없음.
- `.github/workflows/test.yml`의 두 스텝에 신규 테스트 파일이 실제로 나열되어 있음을 `grep`으로 재확인.
- I/O & Edge-Case Matrix 6개 시나리오 전부 커버하는 테스트가 실행·통과함을 확인(matrix test audit 통과).

**잔여 위험:**
- `initialize_new_ticker_history`는 아직 어떤 배치 진입점에도 연결되지 않았다(스펙 범위) — Story 2.5가 이를 `tags` stage에 연결하고 stage-status 기록·재시도 정책을 설계해야 실제 배치에서 동작한다.
- `existing_tickers`의 조회 비효율(캐시가 누적될수록 존재-확인 비용 증가)과 `upsert_rows`의 재시도 부재는 defer로 남겼다(frontmatter `deferred` 참고) — 캐시 규모가 커지거나 저장소 장애 빈도가 문제가 될 때 재검토가 필요하다.
