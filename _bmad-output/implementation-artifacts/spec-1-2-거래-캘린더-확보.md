---
title: '거래 캘린더 확보'
type: 'feature'
created: '2026-09-01'
status: 'done'
baseline_revision: 'b78141403d4d5624ee2263efcd80adaf6a58ea9d'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - _bmad-output/implementation-artifacts/epic-1-context.md
  - _bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md
warnings: []
deferred:
  - summary: >-
      Supabase clean-reset에서 trading_calendar migration을 실행하고 제약을 검사하는 검증을 후속 DB 계약 스토리에서 추가한다.
    evidence: |-
      현재 환경에는 Supabase local DB 실행 경로가 없고 이번 스토리는 SQL migration 파일과 애플리케이션 단위 테스트를 추가했다.
    location: >-
      infra/supabase/migrations/202609011500_create_trading_calendar.sql
    severity: medium
  - summary: >-
      신규 운영 테이블의 RLS와 인증 기반 접근 정책을 인증/수동 트리거 스토리에서 확정한다.
    evidence: |-
      Story 1.2는 캘린더 저장 계약만 정의하며 브라우저 접근 경로는 후속 Story 1.10의 범위다.
    location: >-
      infra/supabase/migrations/202609011500_create_trading_calendar.sql
    severity: medium
  - summary: >-
      Python 3.12.14 exact 고정과 기존 스캐폴딩의 런타임 편차를 별도 환경 정합성 작업에서 해소한다.
    evidence: |-
      기존 Story 1.1에서 Windows uv 제약으로 범위 지정이 기록되어 있으며 Story 1.2 변경으로 발생한 결함이 아니다.
    location: >-
      pyproject.toml:5
    severity: low
---

<intent-contract>

## Intent

**Problem:** 배치가 주말·공휴일과 거래일을 구분하고 D-2/D-1/D0를 일관되게 계산할 수 있는 영속 캘린더 계약이 아직 없다.

**Approach:** `trading_calendar` 스키마와 순수 거래 세션 규칙을 만들고, 일봉 응답 존재 여부를 저장소에 upsert하는 배치 경계를 제공한다. 조회 실패는 휴장으로 추정하지 않고 `CALENDAR_UNAVAILABLE`로 반환한다.

## Boundaries & Constraints

**Always:** 거래일·표시 시간대는 Asia/Seoul, 저장/API 시각은 UTC 의미론을 따른다. 외부 휴일 캘린더 API를 사용하지 않으며, 일봉 응답 존재만 거래일 판정 원천으로 삼는다. 반차는 저장된 `open_time`/`close_time`으로 세션 슬롯을 계산한다.

**Never:** 조회 실패를 `is_open=false`로 저장하지 않는다. 이 스토리에서 후보 수집, 스케줄러, production Supabase 적용, 다른 배치 stage를 구현하지 않는다.

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609011500_create_trading_calendar.sql` -- `trading_calendar` 테이블과 시간 범위 제약을 추가하는 forward-only migration.
- `packages/domain/domain/calendar.py` -- 외부 I/O 없는 거래일 판정 결과와 30분 장중 슬롯 계산 규칙.
- `apps/batch/calendar.py` -- 일봉 조회 provider와 캘린더 repository 사이의 저장·오류 경계.
- `tests/domain/test_calendar.py` -- 거래일/휴장일/조회 실패 및 반차 슬롯 단위 테스트.
- `tests/batch/test_calendar.py` -- adapter의 upsert와 `CALENDAR_UNAVAILABLE` 변환 테스트.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609011500_create_trading_calendar.sql` -- `trading_day` PK, `is_open`, `open_time`, `close_time` 및 유효성 제약을 생성한다 -- AD-4/NFR-8의 영속 계약을 만든다.
- `packages/domain/domain/calendar.py` -- 판정 상태와 세션 슬롯 계산을 순수 함수로 구현한다 -- 테스트와 배치가 동일 규칙을 공유하게 한다.
- `apps/batch/calendar.py` -- 일봉 존재/없음/예외를 각각 open/closed/unavailable로 매핑하고 repository에 캐시한다 -- 실패 시 휴장 오판을 방지한다.
- `tests/domain/test_calendar.py`, `tests/batch/test_calendar.py` -- 정상·휴장·일시 실패·반차 사례를 검증한다 -- I/O 경계와 핵심 규칙의 회귀를 고정한다.

**Acceptance Criteria:**
- Given `trading_calendar` 테이블이 없는 상태, when migration을 적용하면, then `trading_day` PK와 `is_open`, `open_time`, `close_time` 컬럼이 생성된다.
- Given 일봉 조회가 성공해 하나 이상의 일봉을 반환하면, when 캘린더 판정을 실행하면, then 해당 날짜가 `is_open=true`로 캐시된다.
- Given 일봉 조회가 성공했지만 결과가 없으면, when 캘린더 판정을 실행하면, then 해당 날짜가 `is_open=false`로 캐시된다.
- Given LS API/일봉 조회가 실패하면, when 캘린더 판정을 실행하면, then `CALENDAR_UNAVAILABLE` 결과를 반환하고 휴장 행을 저장하지 않는다.
- Given `open_time`/`close_time`이 정상 거래일과 다른 반차 세션이면, when 30분 슬롯을 계산하면, then 종료 시각까지의 슬롯 범위가 정상 세션과 다르게 계산된다.

## Design Notes

캘린더 판단은 provider가 반환하는 `bool` 의미(일봉 존재)를 도메인 결과로 변환하고, 저장은 batch adapter가 담당한다. 기본 세션은 09:00–15:30 KST로 제공하며, 저장된 시간이 있으면 이를 우선해 반차를 지원한다. 단위 테스트는 fake provider/repository를 사용해 production 자격증명이나 외부 네트워크에 의존하지 않는다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/domain/test_calendar.py tests/batch/test_calendar.py -q` -- expected: all calendar tests pass.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: existing backtest regression suite passes unchanged.
- `git diff --check` -- expected: no whitespace errors.

## Review Triage Log

### 2026-09-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3: (high 0, medium 0, low 3)
- defer: 3: (high 0, medium 2, low 1)
- dismissed:
  - 웹 다크모드·인증·Node/Python 고정·기존 Story 1.1 CI 구성 지적 — Story 1.2의 캘린더 계약과 직접 관련 없는 기존 스캐폴딩 표면이다.
  - 캘린더 원천 해시·갱신시각 지적 — Story 1.2 acceptance criteria에 없는 운영 신선도 메타데이터이며 후속 배치 실행/스냅샷 계약에서 다룬다.
- addressed_findings:
  - `[low]` `[patch]` CI가 캘린더 테스트를 실행하지 않음 — Python 캘린더 테스트 단계를 추가했다.
  - `[low]` `[patch]` 잘못된 open 세션 범위가 빈 슬롯으로 조용히 처리됨 — 범위 검증과 회귀 테스트를 추가했다.
  - `[low]` `[patch]` provider의 비 boolean 응답이 판정될 수 있음 — malformed 결과를 `CALENDAR_UNAVAILABLE`로 처리하고 테스트했다.

## Auto Run Result

Status: done

**구현 요약:** KRX 거래일 캐시를 위한 Supabase migration, 일봉 응답 기반 거래일 판정 도메인 규칙, 배치 저장 adapter와 오류 경계를 추가했다. 기본 09:00–15:30 KST 세션과 저장된 반차 세션의 30분 슬롯 계산을 지원하며, 조회 실패·malformed 응답은 휴장으로 저장하지 않는다.

**변경 파일:**
- `infra/supabase/migrations/202609011500_create_trading_calendar.sql` -- trading_calendar 테이블과 세션 제약.
- `packages/domain/domain/calendar.py` -- 순수 판정 상태와 슬롯 계산.
- `apps/batch/calendar.py` -- provider/repository adapter 및 unavailable 처리.
- `tests/domain/test_calendar.py`, `tests/batch/test_calendar.py` -- 8개 단위 테스트.
- `.github/workflows/test.yml` -- 캘린더 테스트 CI 단계.
- `pyproject.toml` -- 테스트 import 경로 설정.

**리뷰 결과:** patch 3건(low 3)을 적용했고, DB migration 실행 검증·RLS/인증 정책·기존 런타임 편차 3건을 defer했다. 웹 스캐폴딩 및 후속 운영 메타데이터 지적은 이번 스토리와 직접 관련 없어 기각했다.

**후속 리뷰 권장:** false (patched low 3건, score 3; high 0, medium 0, low 3).

**검증:**
- `uv run --with pytest pytest tests/domain/test_calendar.py tests/batch/test_calendar.py -q` → 8 passed.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` → 16 passed.
- `npm run build -w apps/web` → Next.js production build 성공.
- `git diff --check` → whitespace 오류 없음.

**잔여 리스크:** Supabase remote/local migration 적용은 실행하지 않았으며, production 적용은 trusted workflow에서 수행해야 한다. E2E는 UI 변경이 없어 실행하지 않았다.
