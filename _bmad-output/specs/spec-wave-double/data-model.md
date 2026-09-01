# Data Model

> Companion: Supabase 저장 스키마. CAP-1~7의 저장 대상.
> **2026-09-01 갱신 — ARCHITECTURE-SPINE.md(architecture-wave-double-2026-08-31)와 동기화.** 이전 버전은 단일 `runs` 테이블(attempt/lease 개념 없음), `candidates.source` 단일 컬럼, `candidate_outcome` 직접 UPDATE, 매일 재계산되는 `bias_metrics`, dispatch 테이블 부재로 AD-3/9/12/16/18/21과 충돌했다. 이번 갱신은 그 불변식을 저장 스키마에 반영한다. `run_id`라는 단어의 의미가 바뀌었다: 이제 **attempt 단위**를 가리키며, 거래일·배치종류 단위 실행 계보는 `logical_runs`가 별도로 갖는다.

## 원칙

- **단일 진실.** 태깅 사실은 `candidate_tags`에만 둔다. Source 기여 사실은 `candidate_source_contrib`에만 둔다(AD-21). Outcome 사실은 `outcome_events`/`outcome_observations`에만 있고 `candidate_outcome`은 재구축 가능한 projection이다(AD-9).
- **모든 데이터 행은 `attempt_run_id`로 생성 attempt를 역참조**한다. 감사·디버깅·신선도 표시(FR-6a)의 전제. Cross-attempt 조인은 `(ticker, strategy, attempt_run_id)`로 한다(AD-16) — `candidate_id`는 attempt마다 새로 발급되는 attempt-scoped identity이며 logical run을 가로지르는 안정 식별자가 아니다.
- **거래일 기준.** 모든 날짜 컬럼은 KRX 거래일이며 달력일이 아니다(NFR-8, AD-4).
- **이력은 삭제하지 않는다.** Non-canonical attempt도 보존하고 canonical view에서만 제외한다(AD-19).

## `runs.stage_status` 전이 규칙 (AD-3/13/15/20 정합)

`stage_status` JSONB의 **각 stage 값은 `pending | running | success | failed | partial` 5중 하나**이며, stage-write RPC는 `(run_id, stage, fence_token, lease_token, expected_status)`를 검증해 `pending` → `running` → 터미널(`success`/`failed`/`partial`)로만 전이한다(역방향 금지).

- `success`: 이 stage가 **완결**. 필수 stage 목록에 있는 stage가 `success`여야 `publish_attempt`(AD-20)가 이 attempt를 완전 발행할 수 있다.
- `partial`: 이 stage의 필요한 처리가 성공했으나 **일부 행이 누락/미해결**(예: `unprocessed_count` > 0, 재시도 후에도 미수집). `success`가 아니므로 필수 stage로는 완전 발행을 막는다. AD-13에 따라 partial attempt는 `latest_partial_run_id`로 분리되고 `available_partial_sections`에만 노출되며 `current_complete_run_id`를 낮추지 않는다.
- `failed`: 이 stage가 **실패**. 필수 stage가 `failed`면 이 attempt는 완전 발행(`published`)될 수 없다.

`ready_to_publish`/`published`의 **최종 발행 판정은 오직 `publish_attempt(run_id, fence_token)`(AD-20)이 내린다**: 해당 transaction은 전 필수 stage가 `success`인지 검증하고, 하나라도 `success`가 아니면 rollback한다(어떤 stage가 `partial`이든 `failed`든 동일). reaper가 heartbeat 만료 attempt를 `ready_to_publish`로 CAS하는 것(AD-3)은 **crash 복구용 구출(salvage) 경로**로, 이 상태가 발행을 보장하지 않는다 — 실제 발행은 AD-20이 재검증한다. `ready_to_publish`로 구출됐어도 필수 stage 중 `partial`/`failed`가 있으면 완전 발행은 불가하며 partial 데이터는 `latest_partial_run_id`로만 남는다(AD-13).

stage 이름은 이 data-model의 5개 키(`candidates`/`tags`/`supply_3day`/`market_supply`/`outcome_tracking`)와 동일하게 쓴다. `outcome`/`screen`/`tagging`/`supply`/`market` 같은 별칭은 쓰지 않는다(<b>`supply_3day`와 `market_supply`는 서로 다른 stage다</b>).

## 테이블

### `logical_runs` — 배치 실행 계보 (CAP-1~7, AD-3/13/15) **[신규]**

- `logical_run_key` (PK, 예: `close:2026-09-01` 또는 `intraday:2026-09-01:14:30`), `trading_day`, `batch_kind` (premarket | intraday | close)
- `active_attempt_run_id` — 현재 실행권자 attempt (nullable)
- `canonical_success_run_id` — outcome 등 canonical 결과의 원천 attempt. **`batch_kind='close'`에만 존재**하며 premarket/intraday는 항상 NULL(AD-15)
- `current_complete_run_id` — 화면에 노출되는 완전 스냅샷의 attempt
- `latest_partial_run_id` — 가장 최근 partial attempt. complete pointer에는 영향 없음(AD-13)
- `published_at`

### `runs` — 배치 attempt (CAP-5, FR-6/FR-6a, AD-3) **[구조 변경: attempt 단위로 재정의]**

- `run_id` (PK, UUID) — 이 attempt의 식별자. 이전 버전의 "실행 이력 행"과 달리 **하나의 logical run에 재시도마다 여러 행이 쌓인다**
- `logical_run_key` (FK → `logical_runs`), `attempt_no` (증가), `fence_token`, `lease_expires_at`
- `started_at`/`finished_at` (KST), `trigger` (schedule | manual)
- `status` — `running → ready_to_publish → published` 또는 `partial | failed | skipped | superseded | cancelled`. `partial`은 필요한 모든 필수 stage 중 적어도 하나가 `success`인 attempt(나머지는 실패/부분), `failed`는 성공한 필수 stage가 하나도 없는 attempt를 뜻한다(AD-3 reaper 규칙)
- `skip_reason` (holiday | …) — 휴장일 스킵은 실패가 아니다(NFR-8)
- `stage_status` (JSONB) — 단계별 완료 여부 `{candidates, tags, supply_3day, market_supply, outcome_tracking}`, **각 stage 값은 `pending | running | success | failed | partial` 5중 하나만 쓴다**(FR-6a, NFR-5, AD-13 taxonomy·아래 전이 규칙 참조). **`partial`은 "그 stage는 성공했으나 일부 행이 누락/미해결"이라는 의미**이며, `success`가 아니므로 이 stage만으로는 이 attempt를 완전 발행 후보로 만들 수 없다
- `unprocessed_count` — 예산 소진 등으로 처리하지 못한 항목 수
- `truncated_count` — 후보 모집단 상한(M=150) 초과로 절단된 종목 수(NFR-7)
- `fallback_used` (bool) — t1859 실패로 t1852/t1856 폴백을 썼는지(FR-1a)
- `selection_input_hash`, `original_count`, `excluded_count` — AD-12: canonical 후보 집합 선정의 원본수·제외수·재현 해시. 같은 input artifact는 같은 값이 나와야 한다

### `candidates` — 후보 모집단 (CAP-1, FR-1/FR-1a, AD-16)

- `candidate_id` (PK) — **attempt-scoped.** 같은 종목이 다른 attempt에서 재선정되면 새 `candidate_id`를 받는다
- `attempt_run_id` (FK → `runs.run_id`), `ticker`(종목코드), `name`(종목명), `trading_day`(거래일)
- `truncated` (bool) — 절단 경계 밖이었는지 (기회 누락 관측용, FR-10)
- UNIQUE `(ticker, trading_day, attempt_run_id)`
- ~~`source`~~ **컬럼 제거 (AD-21).** 원천 기여는 아래 `candidate_source_contrib`가 유일 권위. 화면에서 필요한 `source_jsonb`는 그 테이블에서 만드는 read projection이며 저장하지 않는다

### `candidate_source_contrib` — 원천 기여 (CAP-1/2/7, AD-16/21) **[신규]**

- PK `(candidate_id, attempt_run_id, source)`
- `source` (`t1859 | t1852 | t1856`), `contribution_weight` — 범위 `(0,1]`
- 제약: published candidate마다 최소 1행, weight 합계 = 1 (AD-20 publication RPC가 검증)
- primary source 도출 규칙: weight 내림차순 → source 우선순위 `t1859 > t1852 > t1856`

### `candidate_tags` — 전략 태깅 (CAP-2, FR-3/FR-3b)

- `tag_id` (PK), `candidate_id` (FK), `strategy` (A | B | C), `signal_date`(시그널일)
- `attempt_run_id`, `tagged_at` — 배치 시점 단위 태깅 이력. 장중 시그널 소멸 표시(FR-3b)의 전제
- `status` (active | vanished) — 이전 배치에 있었으나 최신 배치에서 사라진 태깅
- `params_meta` (JSONB) — 재현성 확보용 파라미터 스냅샷
- UNIQUE `(candidate_id, strategy, attempt_run_id)`

### `daily_ohlcv` — 시그널 계산용 장기 일봉 캐시 (FR-3a, AD-5)

- `ticker`(종목코드), `trading_day`(거래일), `open`/`high`/`low`/`close`/`volume`, `adjusted`(수정주가 적용 여부), `adjustment_version` — corporate-action 조정 갱신 시 영향 구간 재구축 추적용(AD-5), `pricechk`(LS `t8410`/`t8451` 수정주가 반영 필드 원본 저장) — **SUSPENDED 1차 감지의 진실 원천(Story 3.8)**: 이 필드가 조정을 보고한 거래일은 갭 크기와 무관하게 가격 조정 이벤트로 취급한다
- PK `(ticker, trading_day)`
- 최소 **120거래일** 보유(전략 B 주봉 %K(20-3) 요구). `t8410` `qrycnt≤500`이므로 신규 편입 종목도 단일 콜로 초기 적재
- 정상 운영 시 배치당 **1일 증분**만 갱신. 신규 편입 종목만 전체 이력 조회
- 조회 시 종목별 상태는 `READY | INELIGIBLE_INSUFFICIENT_HISTORY | ERROR`로 반환(저장 컬럼 아님, adapter 응답 계약) — 120거래일 미만은 해당 종목만 제외, API/저장 실패만 retryable stage error(AD-5)
- ⚠️ NFR-4의 "일봉 정리" 대상이 **아니다.** 이 테이블은 보존 대상이며, 정리 대상은 배치별 중간 스냅샷이다

### `trading_calendar` — 거래일·휴장일 (NFR-8, AD-4)

- `trading_day` (PK), `is_open`, `open_time`/`close_time` (반차 거래일 대응)
- 판정 원천: 일봉 응답의 존재 여부로 거래일을 확정한 뒤 캐싱(외부 캘린더 API 의존 없음)
- 조회 실패는 휴장일이 아니라 `CALENDAR_UNAVAILABLE` 실패다(AD-4)
- FR-8의 컷오프 N거래일 계산과 "2일전/1일전" 산출이 이 테이블을 기준으로 한다

### `supply_3day` — 후보별 3일치 수급·가격 (CAP-3, FR-4)

- `candidate_id` (FK), `attempt_run_id` (FK), `trading_day`(거래일), `slot` (D-2 | D-1 | D0)
- `close`(종가), `volume`(거래량), `change_pct`(등락율), `foreign_net`(외인_순매수), `institution_net`(기관_순매수), `individual_net`(개인_순매수), `program_net`(프로그램_순매수)
- `collected_at` — 신선도 표시(FR-6a)
- ⚠️ **투자자별 순매수 4컬럼(`foreign_net`/`institution_net`/`individual_net`/`program_net`)은 `numeric NULLABLE`.** NULL과 실젯값(0 포함)을 **서로 대체하지 않는다**(AD Consistency — `미수집·미확정·실제 0` 구분). 실제 0은 `0`, 미확정/미수집은 NULL로 저장한다.
  - `investor_net_status` (`confirmed | pending | missing`, NOT NULL) — 투자자별 순매수 컬럼의 상태를 한 행에서 단일하게 선언
    - `confirmed`: 종가 확정 배치의 실측값(실제 0 포함). 이 상태에서만 FR-7 힌트를 `좋은 수급`/`미충족`으로 판정한다
    - `pending`: **장중 미확정** — t1702/t1637 투자자별 필드가 전부 0(장중 정상)이거나 재시도 후에도 채워지지 않은 상태. 순매수 4컬럼은 NULL. FR-7 힌트는 `판정 불가`. Story 4.5의 "미확정" 저장 상태
    - `missing`: 미수집 — 조회 실패로 행이 채워지지 않은 상태. FR-7 힌트는 `판정 불가`. Story 4.7의 "미수집" 표시와 대응
  - 가격(`close`/`volume`/`change_pct`)은 장중에도 실시간으로 확보되므로 이 상태와 무관하게 채워진다(api-map 장중 실측)
  - `investor_net_status`는 행 단위(전체 4컬럼 공통)로 선언한다. 부분 수집 최악의 경우 4컬럼이 불완전하므로, **4컬럼 중 어느 하나라도 확정값이 없으면 `confirmed`가 될 수 없다**(전부 확정일 때만 `confirmed`)
- 원천: `t1702` 1콜(종가·등락율·거래량·외인·기관·개인) + `t1637` 1콜(프로그램)
- ⚠️ **당일(D0) 행은 배치마다 덮어쓰지 않고 `attempt_run_id`별로 누적**한다. UJ-2의 "장중 수급 흐름"은 이력이 있어야 성립한다. D0 이력은 보존 주기를 짧게(NFR-4) 가져가 용량과 균형을 맞춘다
- 투자자별 필드가 전부 0이면 미완료로 처리하고 재시도한다 (api-map.md 장중 실측 가드)
- UNIQUE `(candidate_id, trading_day, attempt_run_id)`

### `market_supply` — 시장 전체 수급 (CAP-4, FR-5)

- `attempt_run_id` (FK), `market`(시장, KOSPI | KOSDAQ), `trading_day`(거래일), 외인/기관/개인/프로그램 집계, `collected_at`

### Outcome — 사후 결과 추적 (CAP-7, FR-8/FR-9, AD-9) **[구조 변경: append-only 장부 + projection]**

이전 버전의 단일 가변 `candidate_outcome` 테이블을 폐기하고 3개 구조로 대체한다. 재실행이 과거 결과를 삭제·변경하지 못하게 하기 위함(AD-9).

- **`outcome_events`** (append-only) — outcome 생명주기의 모든 사실을 기록하는 event 장부
  - `event_id` (PK), `ticker`, `strategy`, `command_type` (OPEN | correction 종류 등), `logical_run_key`, `payload`, `created_at`
  - close publication만 idempotent command key `(logical_run_key, ticker, strategy, command_type)`로 append (AD-9/20)
  - 동일 `(ticker, strategy)`의 `OPEN`은 partial unique index로 최대 1개
- **`outcome_observations`** (append-only) — 일자별 판정 관찰치
  - PK `(outcome_id, evaluation_trading_day)` — retry는 기존 observation을 반환(멱등)
  - `high`, `low`, `close`, `result_code` 등 판정에 쓰인 원 관측값
- **`candidate_outcome`** (rebuildable current projection) — 화면·지표가 읽는 대상
  - `outcome_id` (PK), `ticker`, `strategy`, `entry_date`(진입일) — UNIQUE `(ticker, strategy, entry_date)`
  - `entry_price`(진입가) — **종가 확정 배치의 정규장 종가만.** 장중 배치는 이 projection에 행을 만들지 않는다
  - `status` — `TP | SL | TIMEOUT | OPEN` (+ 예외 `SUSPENDED | DELISTED`, NFR-9)
  - `exit_date`(도달일), `exit_price`(청산가), `return_pct`(손익률) — **왕복 0.1% 비용 차감 후** (TP=+2.9%, SL=−3.1%, TIMEOUT=실제 종가 손익)
  - `cutoff_n` — 판정에 쓴 N값(초기 30)을 행에 함께 저장. N 변경 시 과거 outcome을 재계산하지 않는다
  - `holding_days`(보유거래일수) — TIMEOUT 판정과 분포 분석용. **실거래 경과일수 정의(2026-09-01 결정, Story 3.6):** 진입 다음 거래일부터 현재까지 **유효 일봉이 존재한(실거래) 거래일 수**. 휴장일·거래정지 기간(일봉 부재)은 **제외**된다. TIMEOUT 발동 조건은 `holding_days >= cutoff_n`이며, 같은 원천을 쓰므로 거래정지/휴장이 낀 outcome도 판정과 분포가 정합한다(NFR-9)
  - 판정 규칙(백테스트 동일): 진입 **다음 거래일부터** 판정, 동일봉 TP·SL 동시 도달 시 **SL 우선**
  - **terminal 상태(`TP`/`SL`/`TIMEOUT`)는 불변.** `SUSPENDED` 복귀/종결과 수치 수정은 expected version을 가진 `outcome_correction` event만 허용 — 원행 UPDATE 금지
  - Terminal 확정 후에는 이후 배치의 API 조회 대상에서 제외 → 추적 대상 수 P가 유계
  - AD-19 cleanup 대상이 아니며, projection이므로 event로부터 재구축 가능해야 한다(장애 복구 요건)
  - ~~`source`~~ **컬럼 두지 않음(AD-21).** source별 승률/PF는 `candidate_source_contrib` join으로만 산출

### `bias_metrics` → `bias_events` + `bias_event_by_source` — 모집단 편향 관측 (FR-10, AD-12/21) **[구조 변경: append-only, source별 분해]**

이전 버전의 매일 재계산·overwrite되는 단일 집계 테이블(row에 `source` 컬럼 보유)을 append-only event로 대체하고, source 권위가 오직 `candidate_source_contrib`에만 있어야 한다는 AD-21에 맞춰 source별 분해를 별도 테이블로 분리한다(Story 5.1).

- **`bias_events`** — `bias_event_id` (PK), `trading_day`, `logical_run_key`, `calculation_meta` (JSONB), `created_at`. 편향 계산 한 회차의 메타. **`source` 컬럼을 두지 않는다**(AD-21 — source 권위는 `candidate_source_contrib`에 있음)
- **`bias_event_by_source`** — `bias_event_id` (FK → `bias_events`), `source` (`t1859 | t1852 | t1856`), `candidate_pop_signal_count`(후보모집단_시그널수), `backtest_universe_signal_count`(백테스트유니버스_시그널수), `intersection_count`(교집합수), `diff_count`(차집합수), `missed_opportunity_count`(기회누락수, 절단 포함) — PK `(bias_event_id, source)`. 한 `bias_event` 회차가 여러 source에 대해 행을 가지며, `bias_event_by_source.source`는 `candidate_source_contrib.source`만 참조한다(별도 source 컬럼 값을 독자적으로 보관하지 않음)
- 비용 절감을 위해 **일 1회 종가 배치에서만** 생성. 같은 `trading_day`에 재계산이 필요하면 기존 행을 수정하지 않고 새 `bias_event_id` + 해당 `bias_event_by_source` 행들을 append하며, canonical view가 동일 `trading_day`에 대해 가장 최근 `created_at`의 `bias_event_id`를 선택한다(과거 행은 삭제하지 않음)

### Dispatch — 수동 트리거 멱등화 (CAP-5, AD-18) **[신규, 이전 버전 누락]**

- **`dispatch_request`** — `dispatch_request_id` (PK), `idempotency_key`, `payload_hash`, `requested_by`, `created_at`. 같은 key+hash는 기존 `dispatch_request_id`를 replay, 같은 key+다른 hash는 `409`
- **`dispatch_outbox`** — `outbox_id` (PK), `dispatch_request_id` (FK), `status` (`queued → accepted → started → completed | failed | dead_letter`), `lease_expires_at`, `logical_run_key`
- worker는 `FOR UPDATE SKIP LOCKED`로 claim. GitHub workflow 첫 단계가 같은 request ID로 receipt와 batch `run_id`를 idempotent 기록

## 저장·보존 지침 (NFR-4)

- **보존**: `candidate_outcome`(및 `outcome_events`/`outcome_observations`), `bias_events`(및 `bias_event_by_source`), `daily_ohlcv`, `trading_calendar`, `logical_runs`, `runs` — 장기 보존
- **정리**: `supply_3day`의 장중(D0) 이력 스냅샷, attempt-scoped 배치별 중간 산출물(비-canonical `candidates`/`candidate_tags`/`candidate_source_contrib`는 AD-19에 따라 **삭제하지 않고** canonical view에서만 제외) — 실제 정리 대상은 산출물이 아니라 조회 노출 범위임에 유의
- Supabase 무료 용량 한도 내 유지를 상시 점검(PRD §10-5)
