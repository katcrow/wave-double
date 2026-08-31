# Data Model

> Companion: Supabase 저장 스키마. CAP-1~7의 저장 대상.
> **2026-08-31 갱신** — PRD §4의 전 FR을 저장 관점에서 커버하도록 개정했다. 이전 버전은 장기 일봉·거래 캘린더·유일제약·단계별 배치 상태·원천 구분·태깅 이력이 누락되어 있었고, `candidates.전략id[]`와 `candidate_tags`가 같은 사실을 이중 저장하고 있었다.

## 원칙

- **단일 진실.** 태깅 사실은 `candidate_tags`에만 둔다. `candidates`에 전략 배열을 중복 보관하지 않는다.
- **모든 데이터 행은 `run_id`로 생성 배치를 역참조**한다. 감사·디버깅·신선도 표시(FR-6a)의 전제.
- **거래일 기준.** 모든 날짜 컬럼은 KRX 거래일이며 달력일이 아니다(NFR-8).

## 테이블

### `runs` — 배치 실행 이력 (CAP-5, FR-6/FR-6a)

- `run_id` (PK), `started_at`/`finished_at` (KST), `trigger` (schedule | manual)
- `batch_kind` (premarket | intraday | close) — **종가 확정 배치만 outcome을 생성**하므로 구분이 필수(FR-8)
- `status` (success | partial | failed | skipped)
- `skip_reason` (holiday | …) — 휴장일 스킵은 실패가 아니다(NFR-8)
- `stage_status` (JSONB) — 단계별 완료 여부 `{screen, tagging, supply, market, outcome}`. 부분 실패를 화면이 정확히 표현하기 위함(FR-6a, NFR-5)
- `unprocessed_count` — 예산 소진 등으로 처리하지 못한 항목 수
- `truncated_count` — 후보 모집단 상한(M=150) 초과로 절단된 종목 수(NFR-7)
- `fallback_used` (bool) — t1859 실패로 t1852/t1856 폴백을 썼는지(FR-1a)

### `candidates` — 후보 모집단 (CAP-1, FR-1/FR-1a)

- `candidate_id` (PK), `run_id` (FK), `종목코드`, `종목명`, `거래일`
- **`source`** (t1859 | t1852 | t1856) — 폴백 모집단은 t1859와 동일하다고 가정하지 않는다(FR-1a)
- `truncated` (bool) — 절단 경계 밖이었는지 (기회 누락 관측용, FR-10)
- UNIQUE `(종목코드, 거래일, run_id)`

### `candidate_tags` — 전략 태깅 (CAP-2, FR-3/FR-3b)

- `tag_id` (PK), `candidate_id` (FK), `strategy` (A | B | C), `시그널일`
- **`run_id`, `tagged_at`** — 배치 시점 단위 태깅 이력. 장중 시그널 소멸 표시(FR-3b)의 전제
- `status` (active | vanished) — 이전 배치에 있었으나 최신 배치에서 사라진 태깅
- `params_meta` (JSONB) — 재현성 확보용 파라미터 스냅샷
- UNIQUE `(candidate_id, strategy, run_id)`

### `daily_ohlcv` — 시그널 계산용 장기 일봉 캐시 (FR-3a) **[신규]**

- `종목코드`, `거래일`, `open`/`high`/`low`/`close`/`volume`, `adjusted` (수정주가 적용 여부)
- PK `(종목코드, 거래일)`
- 최소 **120거래일** 보유(전략 B 주봉 %K(20-3) 요구). `t8410` `qrycnt≤500`이므로 신규 편입 종목도 단일 콜로 초기 적재
- 정상 운영 시 배치당 **1일 증분**만 갱신하며, 전체 이력 조회는 신규 편입 종목에 한정
- ⚠️ NFR-4의 "일봉 정리" 대상이 **아니다.** 이 테이블은 보존 대상이며, 정리 대상은 배치별 중간 스냅샷이다

### `trading_calendar` — 거래일·휴장일 (NFR-8) **[신규]**

- `거래일` (PK), `is_open`, `개장시각`/`폐장시각` (반차 거래일 대응)
- 판정 원천: 일봉 응답의 존재 여부로 거래일을 확정한 뒤 캐싱(외부 캘린더 API 의존 없음)
- FR-8의 컷오프 N거래일 계산과 "2일전/1일전" 산출이 이 테이블을 기준으로 한다

### `supply_3day` — 후보별 3일치 수급·가격 (CAP-3, FR-4)

- `candidate_id` (FK), `run_id` (FK), `거래일`, `slot` (D-2 | D-1 | D0)
- `종가`, `거래량`, `등락율`, `외인_순매수`, `기관_순매수`, `개인_순매수`, `프로그램_순매수`
- `collected_at` — 신선도 표시(FR-6a)
- 원천: `t1702` 1콜(종가·등락율·거래량·외인·기관·개인) + `t1637` 1콜(프로그램)
- ⚠️ **당일(D0) 행은 배치마다 덮어쓰지 않고 `run_id`별로 누적**한다. UJ-2의 "장중 수급 흐름"은 이력이 있어야 성립한다. 대신 D0 이력은 보존 주기를 짧게(NFR-4) 가져가 용량과 균형을 맞춘다
- UNIQUE `(candidate_id, 거래일, run_id)`

### `market_supply` — 시장 전체 수급 (CAP-4, FR-5)

- `run_id` (FK), `시장` (KOSPI | KOSDAQ), `거래일`, 외인/기관/개인/프로그램 집계, `collected_at`

### `candidate_outcome` — 사후 결과 추적 (CAP-7, FR-8/FR-9)

- `종목코드`, `strategy`, **`진입일`** — **UNIQUE `(종목코드, strategy, 진입일)`**
- `진입가` — **종가 확정 배치의 정규장 종가만.** 장중 배치는 이 테이블에 행을 생성하지 않는다
- `status` — **4상태: `TP` | `SL` | `TIMEOUT` | `OPEN`** (+ 예외 상태 `SUSPENDED` | `DELISTED`, NFR-9)
- `도달일`, `청산가`, `손익률` — 손익률은 **왕복 0.1% 비용 차감 후** (TP=+2.9%, SL=−3.1%, TIMEOUT=실제 종가 손익)
- `cutoff_n` — 판정에 쓴 N값(초기 30)을 행에 함께 저장. N 변경 시 과거 outcome을 재계산하지 않는다
- `보유거래일수` — TIMEOUT 판정과 분포 분석용
- 판정 규칙(백테스트 동일): 진입 **다음 거래일부터** 판정, 동일봉 TP·SL 동시 도달 시 **SL 우선**, 부등호 등호 포함
- `TIMEOUT`/`TP`/`SL` 확정 후에는 **이후 배치의 API 조회 대상에서 제외** → 추적 대상 수 P가 유계

### `bias_metrics` — 모집단 편향 관측 (FR-10) **[신규]**

- `거래일`, `후보모집단_시그널수`, `백테스트유니버스_시그널수`, `교집합수`, `차집합수`, `기회누락수`
- 비용 절감을 위해 **일 1회 종가 배치에서만** 계산

## 저장·보존 지침 (NFR-4)

- **보존**: `candidate_outcome`, `bias_metrics`, `daily_ohlcv`, `trading_calendar`, `runs` — 장기 보존
- **정리**: `supply_3day`의 장중(D0) 이력 스냅샷, 배치별 중간 산출물 — 보존 주기를 정해 순환 삭제
- Supabase 무료 용량 한도 내 유지를 상시 점검(PRD §10-5)
