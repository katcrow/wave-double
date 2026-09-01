---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-wave-double-2026-08-31/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/EXPERIENCE.md
  - _bmad-output/specs/spec-wave-double/SPEC.md
  - _bmad-output/specs/spec-wave-double/api-map.md
  - _bmad-output/specs/spec-wave-double/data-model.md
  - _bmad-output/specs/spec-wave-double/backtest-baseline.md
---

# wave-double - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for wave-double, decomposing the requirements from the PRD, UX Design (DESIGN.md/EXPERIENCE.md), Architecture Spine, and SPEC companions (api-map.md, data-model.md, backtest-baseline.md) into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: 후보 모집단 자동 갱신 — 매 거래일 스케줄(개장 전/장중 30분/종가 확정)에 조건검색식(t1859)을 실행해 후보 모집단을 Supabase에 갱신한다.
FR1a: 후보 모집단 대체 경로 폴백 — t1859 실패 시 t1852/t1856 경로로 재시도하고, source 구분값과 함께 저장한다.
FR2: 후보 모집단 수동 갱신 — Neo가 프론트엔드 버튼으로 시간과 무관하게 배치를 수동 트리거한다.
FR3: 전략 A/B/C 시그널 계산 및 태깅 — 후보 모집단 한정으로 전략 A/B/C 시그널을 계산·태깅하며, 태깅된 종목만 노출한다. 골든 픽스처 회귀(Jaccard ≥ 0.9)로 검증한다.
FR3a: 시그널 계산용 시계열 이력 확보 — 최소 120거래일 일봉을 Supabase 영속 캐시 + 증분 갱신으로 확보한다.
FR3b: 장중 시그널 유지·소멸 표시 — 이전 배치에 태깅되었으나 최신 배치에 없는 종목을 "소멸" 상태로 구분 표시한다.
FR4: 후보별 3일치 수급·가격 표시 — 태깅된 각 후보의 2거래일전/1거래일전/당일 3행(가격·거래량·등락율·외인/기관/개인/프로그램 순매수)을 표시한다.
FR5: 시장 전체 수급 표시 — 코스피/코스닥 시장 전체 수급 집계(외인/기관/개인/프로그램)를 표시한다.
FR6: 스케줄 및 수동 배치 실행 — GitHub Actions 스케줄로 자동 실행하고 프론트엔드에서 수동 실행 가능하며, 배치 이력에 결과·트리거 유형을 기록한다.
FR6a: 배치 상태·신선도 표시 — 메인 대시보드와 추적페이지 상단에 최근 배치 상태·실행 시각·트리거 유형·미처리 항목 수를 항상 표시한다.
FR7: 후보별 '좋은 수급' 힌트 표시 — 프로그램+외인+기관 모두 순매수(>0)인 경우 '좋은 수급' 힌트를 표시한다(3상태: 좋은 수급/미충족/판정 불가).
FR8: 사후 결과 자동 적재 — 종가 확정 배치에서 태깅된 후보에 한해 진입일·진입가를 기록하고, TP/SL/TIMEOUT/OPEN 상태와 도달일을 candidate_outcome에 자동 적재·추적한다.
FR9: 실전 승률·PF 대조 검증 화면 — 추적페이지에서 실전 승률·PF를 백테스트 기대치와 대조 계산·표시한다(표본 게이트 30건, 95% 신뢰구간, 이탈 임계값, 컷오프 편향 고지).
FR10: 모집단 편향 관측 지표 — 조건검색식 후보 ∩ 전략 시그널과 백테스트 유니버스 ∩ 전략 시그널의 크기·교집합·차집합·기회 누락을 계산·표시한다.

### NonFunctional Requirements

NFR1: 무료 운영 제약 — 프론트엔드 Next.js, 로직 Python(GitHub Actions), DB Supabase 무료 플랜만 사용. 유료 서비스 의존 금지.
NFR2: 실행 시간 예산 — 리포지토리 public 운영으로 GitHub Actions 무제한 확보. 실질 제약은 다음 배치까지의 벽시계 시간(장중 30분). 민감 정보는 GitHub Secrets로 분리.
NFR3: API 속도 준수 — LS OpenAPI TR별 초당 제한 준수(팬아웃 TR인 t1702/t1637/t8410은 전부 개인 1건/초). 교차 파이프라이닝은 실측 검증 후에만 적용.
NFR4: 저장 용량 관리 — Supabase 무료 용량 내 유지. candidate_outcome/bias_metrics/daily_ohlcv/trading_calendar/runs는 보존, supply_3day 장중(D0) 이력·중간 산출물은 정리(90일 잠정).
NFR5: 신뢰성 — 배치 실패는 FR-6a로 표시. 파이프라인 단계별 부분 커밋 허용하되 stage_status에 단계별 완료 여부 기록. 실패 단계가 이전 단계 데이터를 덮어쓰거나 삭제하지 않는다.
NFR6: 데이터 정확성 — 표시되는 가격·수급·outcome 수치는 원천과 일치. 태깅 재현성은 골든 픽스처 회귀(Jaccard ≥ 0.9)로 검증하며 완전 재현이 아닌 통계적 유사도임을 명시.
NFR7: 처리 규모 상한 — 후보 모집단 상한 M ≤ 150종목(거래대금 상위 절단), 절단 사실은 runs.truncated_count에 기록. outcome 추적 대상은 FR-8 컷오프(30거래일)로 유계. 예산 초과 예상 시 부분 성공으로 종료.
NFR8: 거래 캘린더 — KRX 거래일 캘린더 보유, 휴장일에는 배치를 no-op으로 조기 종료. 판정 원천은 일봉 응답 존재 여부. 모든 cron은 UTC로 기술, KST 환산 주석 병기.
NFR9: 가격 기준·조정 — 모든 가격은 수정주가 기준 통일. 등락율은 전일 종가 대비. 가격 조정 이벤트 발생 시 SUSPENDED로 표시하고 자동 판정에서 제외. 거래정지 기간은 컷오프 계산에서 제외, 상장폐지는 DELISTED로 종결.

### Additional Requirements

(Architecture Spine — ARCHITECTURE-SPINE.md의 binding invariant, 모든 구현 단위가 준수해야 함)

- **구조 시드(Structural Seed):** 첫 lockfile은 Python 3.12.14 / pandas 3.0.5 / NumPy 2.5.2 / HTTPX 0.28.1 / PyArrow 25.0.1 / Node.js 24.20.0 LTS / Next.js 16.3.3 / React 19.2.8 / TypeScript 5.9.3 / @supabase/supabase-js 2.112.4 / @supabase/ssr 0.12.4 / Playwright 1.62.1 / GitHub Actions runner ubuntu-24.04로 생성하고, 기존 backtest 전체 테스트와 AD-5 golden parity를 통과해야 한다.
- **리포지토리 레이아웃:** `pyproject.toml`/`uv.lock`, `package.json`/`package-lock.json`, `apps/web`(Next App Router), `apps/batch`(Python CLI/오케스트레이터), `packages/domain`(outcome/hint/calendar/run-state 순수 규칙), `packages/read-model`(생성된 DB 타입/쿼리 계약), `backtest/`(기존 전략/지표 커널 재사용), `infra/supabase/migrations/`, `.github/workflows/`, `tests/fixtures/`.
- **AD-1 런타임 간 계약은 포트와 저장 모델이다:** apps/*만 외부 I/O·프레임워크 소유. domain/backtest는 순수 계약만 노출.
- **AD-2 Supabase가 운영 공유 데이터의 단일 소유자다:** 모든 배치 파생행은 attempt_run_id lineage를 가진다. 웹은 승인된 view/RPC만 읽는다.
- **AD-3 배치는 lease·fence를 가진 멱등 상태 머신이다:** logical_runs(active_attempt_run_id/canonical_success_run_id/current_complete_run_id/latest_partial_run_id) + runs(attempt 단위, fence_token, lease). start_attempt RPC, stage별 전용 RPC, heartbeat reaper.
- **AD-4 거래 시간 의미론은 하나뿐이다:** 저장/API instant는 UTC timestamptz, 거래일/표시는 Asia/Seoul. trading_calendar가 D-2/D-1/D0 소유. calendar 조회 실패는 CALENDAR_UNAVAILABLE.
- **AD-5 운영과 백테스트는 하나의 전략 API를 공유한다:** `backtest.strategy_api.compute_abc(frame) -> StrategyResult`가 유일 entrypoint. ohlcv_cache는 READY/INELIGIBLE_INSUFFICIENT_HISTORY/ERROR 반환.
- **AD-6 LS API 예산과 canonical 후보 집합은 공통 client가 소유한다:** TR별 token bucket, bounded retry, Retry-After 파싱. source 우선순위 t1859>t1852>t1856, 거래대금 내림차순/종목코드 오름차순 150개 선택.
- **AD-7 브라우저는 단일 운영자 세션과 읽기 권한만 가진다:** Supabase Auth email OTP/magic link. server-side subject allowlist. dispatch route는 JWKS 검증, CSRF, rate limit, idempotency.
- **AD-8 금융 지표는 versioned read model에서 계산한다:** 수급 3상태, 승률, PF, 신뢰구간, 표본 게이트는 SQL view/RPC가 반환. UI는 계산하지 않는다.
- **AD-9 Outcome은 append-only event 장부와 재생 가능한 projection이다:** outcome_events/outcome_observations append-only, candidate_outcome은 rebuildable projection. terminal 상태 불변, SUSPENDED 복귀는 outcome_correction event만.
- **AD-10 운영 가시성은 run_id 중심이다:** 모든 로그/stage result는 run_id/stage/batch_kind/trading_day/attempt_no/duration_ms/result_code. secret 로그 금지.
- **AD-11 개발과 운영의 데이터 경계를 분리한다:** 로컬/CI는 fixture·local test DB만. production migration/배치/백업은 default branch trusted workflow만.
- **AD-12 후보 상한과 편향은 같은 결정에서 기록한다:** selection_input_hash/original_count/excluded_count를 run에 기록. bias event는 append-only.
- **AD-13 완전 스냅샷은 원자적으로 공개하고 partial은 분리해 읽는다:** get_dashboard_snapshot()이 complete_snapshot/latest_attempt/available_partial_sections/missing_sections/unprocessed_items/no_snapshot 분리 반환. section taxonomy: candidates/tags/supply_3day/market_supply/outcome_tracking.
- **AD-14 DB 계약은 forward-only expand-migrate-contract로 진화한다:** Supabase CLI 단일 timestamp SQL migration. CI가 clean db reset, N/N-1 compatibility, generated types, SQL fixture parity 검증.
- **AD-15 한 logical run의 canonical winner는 한 번만 확정된다:** ready_to_publish + 올바른 fence만 publish 후보. canonical_success_run_id는 close에만 존재하고 불변.
- **AD-16 Source provenance는 정규화된 contribution 행으로 흐른다:** candidate_id는 attempt-scoped. candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight), weight 합계 1.
- **AD-17 무료 운영은 암호화 dump와 검증된 복원으로 보호한다:** 6시간마다 pg_dump, age 암호화, GitHub Actions artifact 14일 보관. 분기 1회 복원 검증(RPO 6h, RTO 8h).
- **AD-18 Dispatch는 DB 요청 ID와 transactional outbox로 멱등화한다:** dispatch_request/dispatch_outbox, FOR UPDATE SKIP LOCKED, pg_cron 1분 fallback.
- **AD-19 Non-canonical attempt는 보존하되 canonical view에서 제외한다:** attempt-scoped 행은 삭제하지 않고 canonical view에서만 제외.
- **AD-20 Publication 권한은 orchestrator의 단일 transaction에만 있다:** publish_attempt(run_id, fence_token) RPC가 유일 경로. close는 같은 transaction에서 outcome도 생성.
- **AD-21 Source별 지표의 유일한 권위는 candidate_source_contrib다:** 모든 *_by_source view는 candidate_source_contrib만 join.
- **Deferred(재검토 조건 도래 전 임의 결정 금지):** ~~Next.js 호스팅 제공자 선택~~ → **해결됨(Vercel Hobby, 2026-09-01)**, ATR(14) 게이트 제거(V1은 유지), TR 간 교차 병렬화(실측 후), 장중 snapshot 보존 기간(30일 추세 측정 후 조정), Python data stack 승격(compatibility spike 검증 후).

### UX Design Requirements

UX-DR1: 디자인 토큰 구현 — DESIGN.md frontmatter의 colors(canvas/surface/surface-raised/surface-elevated/ink-*/accent/accent-strong/positive/negative/caution/informational/overlay), typography(display/heading/body/label/data, Pretendard 우선), rounded(sm/md/lg/full), spacing(1~8) 토큰을 코드 디자인 시스템으로 구현한다.
UX-DR2: App shell — 좌측 고정 내비게이션(240px, ≥1200px), `오늘의 후보`/`성과 검증`/`배치 이력` 링크, 활성 항목 골드 텍스트+얇은 인셋, 좁은 화면에서 접히는 사이드 패널(햄버거 메뉴 금지).
UX-DR3: Data trust bar — 화면 상단 고정, 최신 배치 상태(성공/부분성공/실패/휴장일 스킵)·KST 실행 시각·트리거 유형·신선도를 표시. 실패/미갱신 시 단일 주요 수동 실행 버튼. 중복 클릭 방지 및 실행 중 상태 표시.
UX-DR4: Candidate summary card — 종목명·코드, 전략 A/B/C 태그, 수급 힌트, 당일 가격/등락률, 시그널 유지/소멸 상태를 한 행에 표시. 클릭/Enter로 근거 패널 확장(하나만 열림, 다른 카드 확장 시 기존 열린 카드 유지). 선택 시 accent 1px 테두리.
UX-DR5: Evidence panel — 후보별 2거래일전/1거래일전/당일 종가·거래량·등락률·외인/기관/개인/프로그램 순매수 표시. 거래일 순서는 최신이 위. 원천·생성 시각을 패널 상단에 표시. 장중 당일 종목별 수급은 "미확정"으로 렌더링(0과 구분). 결측은 "미수집"으로 표시. 폴백 원천은 t1852/t1856 명시. 좁은 화면에서 날짜별 행 카드로 전환.
UX-DR6: Market supply panel — 코스피/코스닥 탭(URL 또는 로컬 상태 보존), 외인/기관/개인/프로그램 방향을 숫자+막대로 표시. 장중 참고 정보 라벨 고정. 종목 수급과 다른 신선도 라벨 사용.
UX-DR7: Strategy tag — A/B/C 다중 태그 가로 나열, 좁은 폭에서 줄바꿈 대신 +N으로 접기. 태그 클릭은 필터가 아니라 해당 전략 설명/성과로 이동.
UX-DR8: Outcome badge — TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED를 텍스트로 표시하고, 색상은 보조 수단, 툴팁/상세 문장으로 의미 제공.
UX-DR9: Metric comparison — 전략 A/B/C 및 전체 전환 가능. 실전 승률·PF와 백테스트 기대치를 같은 축으로 비교하되 종결/진행중 건수 항상 병기. 종결 30건 미만이면 수치 대신 "표본 부족 n/30" 표시하고 기대치 판정 생략. 95% 신뢰구간과 안/밖 판정 표시.
UX-DR10: Bias diagnostic — 날짜 선택 시 후보 모집단∩전략 시그널, 백테스트 유니버스 시그널, 교집합, 기회 누락(절단 포함) 숫자 4개와 짧은 설명 표시. 차집합을 과장된 그래픽으로 표현하지 않음. 차이를 실패 원인으로 단정하지 않음.
UX-DR11: Toast/notice — 자동 배치 실패, 부분성공, stale, 폴백 원천 사용을 비차단 알림으로 표시. 색상보다 문장과 시각(타임스탬프)으로 오래됨을 명확히 함.
UX-DR12: 라우팅 구조 — `/`(오늘의 후보), `/tracking`(성과 검증), `/runs`(배치 이력)을 별도 라우트로 분리. 모달 위 모달 금지. 카드 확장은 페이지 내 disclosure, 추적 페이지 필터는 페이지 상태로 유지.
UX-DR13: 키보드 인터랙션 — `j/k` 후보 이동, `Enter` 근거 패널 열기/닫기, `/` 후보 검색, `r` 새로고침, `g t`/`g v` 네비게이션, `Esc` 패널/팝오버 닫기. hover 전용 액션 금지(모든 액션은 DOM 상주 또는 포커스로 노출).
UX-DR14: 접근성 플로어 — WCAG 2.2 AA. 색상만으로 상태 구분 금지. 카드/disclosure는 키보드 접근 가능 + aria-expanded. 후보 카드는 종목명·코드·전략태그·수급힌트·시그널상태가 하나의 접근 가능한 이름으로 읽힘. 데이터 테이블은 행/열 헤더 제공. 배치 상태 변경/새로고침 완료/오류는 aria-live="polite". 포커스 링은 accent-strong 대비 확보. 200% 확대에서 카드 내용 안 잘림. 모션 감소 설정 시 확장/토스트 전환 즉시 처리(카운트업/펄스 금지).
UX-DR15: 반응형 레이아웃 — `≥1200px`(사이드바 240px, 후보 요약 2분할, 시장 수급 전체 폭), `768-1199px`(사이드바 축소/토글, 1열 흐름 내 짧은 2단), `<768px`(사이드바 sheet, 후보 카드 세로 요약, 3일치 데이터 날짜별 행 카드, 표본/상태 고지 상단 고정).
UX-DR16: Voice and tone 카피 가이드 — `오늘의 후보`/`전략 A · 전략 C 시그널`/`좋은 수급`/`판정 불가 · 장 마감 후 확정`/`배치 실패 · 마지막 성공 08:10`/`표본 부족 · 종결 8/30건`/`데이터가 60분 이상 오래됨` 등 확정 문구를 사용하고, 금융조언·확정적 표현("강력 매수 신호", "매수 확정" 등)을 배제한다.
UX-DR17: 필터 — 전략, 수급 힌트, 시그널 상태, 원천으로 필터링. 필터 결과 0건이면 적용된 필터를 보여주고 일괄 초기화 제공.
UX-DR18: 상태 패턴 구현 — 정상 종가 확정/장중 참고/로딩(skeleton)/후보 없음/부분성공/실패/휴장일/stale/폴백 원천/표본 부족/가격 조정 이상(SUSPENDED) 각 상태별 EXPERIENCE.md State Patterns 표의 처리를 정확히 구현한다.

### FR Coverage Map

| FR | Epic | 설명 |
| --- | --- | --- |
| FR1, FR1a, FR2, FR6, FR6a | Epic 1 | 배치 자동화 인프라 & 오늘의 후보 모집단 |
| FR3, FR3a, FR3b | Epic 2 | 전략 태깅 & 오늘의 후보 노출 |
| FR8 | Epic 3 | 실전 사후 결과 자동 적재 |
| FR4, FR5, FR7 | Epic 4 | 후보 근거(3일치 수급) · 시장 전체 수급 · 좋은 수급 힌트 |
| FR9, FR10 | Epic 5 | 실전 성과 검증 화면 & 모집단 편향 |

## Epic List

상세 설명·계약 산출물·의존성은 각 에픽 섹션(아래 `## Epic 1`~`## Epic 5`)에 있다. 이 목록은 색인 용도다.

| Epic | 이름 | FRs covered |
| --- | --- | --- |
| 1 | 배치 자동화 인프라 & 오늘의 후보 모집단 | FR1, FR1a, FR2, FR6, FR6a |
| 2 | 전략 태깅 & 오늘의 후보 노출 | FR3, FR3a, FR3b |
| 3 | 실전 사후 결과 자동 적재 | FR8 |
| 4 | 후보 근거(3일치 수급) · 시장 전체 수급 · 좋은 수급 힌트 | FR4, FR5, FR7 |
| 5 | 실전 성과 검증 화면 & 모집단 편향 | FR9, FR10 |

<!-- ============================================================ -->

## Epic 1: 배치 자동화 인프라 & 오늘의 후보 모집단

Neo가 매 거래일 자동(및 수동)으로 후보 모집단이 갱신되는 것을 확인하고, 배치의 성공/실패/신선도를 항상 볼 수 있으며, 시스템이 실제로 배포·백업되어 운영 가능한 상태다. 이 에픽은 이후 모든 에픽이 확장만 하면 되는 완전한 배치 계약(5개 stage 키를 포함한 `stage_status`, outcome 확장점을 포함한 `publish_attempt` 트랜잭션 골격, TR-agnostic LS adapter client)을 만든다. AD-5 골든 픽스처 디렉터리 계약은 여기서 스캐폴딩되지만, 운영 시그널 회귀 게이트 자체는 Epic 2 Story 2.4가 단일 권위자다.

**스프린트 계획 노트:** 이 에픽은 인프라(1.1-1.4)·배치 로직(1.5-1.7)·화면/인증(1.8-1.10)·운영(1.11-1.12) 4개 영역, 12개 스토리로 구성되어 하나의 스프린트 단위로 보기엔 크다. Sprint Planning 단계에서 최소 2~3개 서브 배치(예: 인프라+상태머신 → 화면+인증 → 배포+백업)로 나눠 진행할 것을 권장한다.

**FRs covered:** FR1, FR1a, FR2, FR6, FR6a

### Story 1.1: 프로젝트 스캐폴딩 & 개발 환경 고정

As a Neo(시스템 운영자 겸 유일한 개발자),
I want 리포지토리가 Architecture Spine이 지정한 정확한 버전과 레이아웃으로 초기화되기를,
So that 이후 모든 에픽이 동일한 기반 위에서 안전하게 확장될 수 있다.

**Acceptance Criteria:**

**Given** 빈 리포지토리 상태에서
**When** 초기 스캐폴딩 커밋을 생성하면
**Then** `pyproject.toml`+`uv.lock`(Python 3.12.14), `package.json`+`package-lock.json`(Node.js 24.20.0 LTS, Next.js 16.3.3, React/react-dom 19.2.8, TypeScript 5.9.3, `@supabase/supabase-js` 2.112.4, `@supabase/ssr` 0.12.4, Playwright 1.62.1)이 exact version으로 고정되고, pandas 3.0.5/NumPy 2.5.2/HTTPX 0.28.1/PyArrow 25.0.1이 Python 의존성에 고정된다
**And** `apps/web`, `apps/batch`, `packages/domain`, `packages/read-model`, `backtest/`(기존 코드 재사용), `infra/supabase/migrations/`, `.github/workflows/`, `tests/fixtures/` 디렉터리가 생성된다.

**Given** 기존 `backtest/` 코드베이스(`screen_abc.py`, `engine.py`, `indicator_opt/*`, `metrics/*` 등)가 별도 위치에 존재하는 경우
**When** 리포지토리 스캐폴딩을 진행하면
**Then** 해당 코드가 새 레이아웃의 `backtest/` 디렉터리로 로직 변경 없이(의존성 버전 고정에 따른 최소 수정 제외) 그대로 이식되며, 이 이식 자체가 스캐폴딩 커밋의 일부로 완료된다(빈 리포지토리에서 시작하되 기존 검증된 전략/지표 커널은 재작성하지 않음).

**Given** 새 lockfile이 생성된 상태에서
**When** 기존 `backtest/` 전체 테스트 스위트를 실행하면
**Then** 전체 테스트가 통과한다(패키지 버전 변경으로 인한 회귀 없음을 확인 — 이 시점의 게이트는 **backtest 자체 테스트**에 한정하며, AD-5의 golden fixture(A/B/C 시그널 집합) 검증은 Epic 2 Story 2.4가 단일 권위자다).
**And** 실패 시 실패 패키지와 증거를 기록하고, 지원 중인 최소 호환 조합으로 spine을 갱신하는 후속 작업이 필요함을 표시한다(Deferred: Python data stack 승격).

**Given** GitHub Actions CI 워크플로가 구성된 상태에서
**When** PR이 열리면
**Then** `ubuntu-24.04` 러너에서 lockfile 기반 설치(런타임 preinstall 미의존, AD-11)로 빌드가 성공한다
**And** production secret이 이 워크플로에 노출되지 않는다(fork/PR 워크플로에는 secret 미제공, AD-11).

**Given** `infra/supabase/migrations/`에 SQL migration이 하나 이상 존재하는 경우(이 스토리 이후 모든 에픽이 여기에 migration을 추가한다)
**When** CI 워크플로가 실행되면
**Then** Supabase CLI로 clean DB에 전체 migration을 순서대로 적용하는 reset 단계가 통과하고, 직전 migration까지만 적용한 스키마(N-1)로도 애플리케이션 쿼리가 깨지지 않는 N/N-1 호환성 검증, `packages/read-model`의 generated DB 타입 재생성·diff 확인, `tests/fixtures/`의 SQL fixture와 스키마 정합성 검증이 모두 CI 게이트로 실행된다(AD-14). 이 게이트는 이 스토리에서 골격을 만들고, 이후 각 에픽이 migration을 추가할 때마다 그대로 적용받는다(신규 스토리 불필요, forward-only expand-migrate-contract 원칙).

### Story 1.2: 거래 캘린더 확보

As a Neo,
I want 시스템이 KRX 거래일을 정확히 판정하기를,
So that 모든 배치가 휴장일에는 불필요하게 실행되지 않고 "N거래일전" 계산이 정확하다.

**Acceptance Criteria:**

**Given** `trading_calendar` 테이블이 없는 상태에서
**When** migration을 적용하면
**Then** `trading_calendar(trading_day PK, is_open, open_time, close_time)` 스키마가 생성된다(NFR-8, AD-4).

**Given** 임의 거래일에 대해 일봉 조회가 성공하는 경우
**When** 캘린더 판정 로직을 실행하면
**Then** 해당 일자가 `is_open=true`로 `trading_calendar`에 캐싱된다(외부 캘린더 API 의존 없음, 일봉 응답 존재 여부가 판정 원천).

**Given** 임의 공휴일 날짜에 대해 일봉 조회 결과가 없는 경우
**When** 캘린더 판정 로직을 실행하면
**Then** 해당 일자가 `is_open=false`로 캐싱되고 배치가 이를 참조해 no-op 조기 종료할 수 있는 근거가 된다.

**Given** LS API 또는 일봉 조회가 일시적으로 실패하는 경우
**When** 캘린더 판정 로직이 원인을 알 수 없어 휴장일인지 확정할 수 없으면
**Then** 결과는 `CALENDAR_UNAVAILABLE` 실패로 반환되며 휴장일로 간주되지 않는다(AD-4).

**Given** 반차 거래일이 캘린더에 기록된 경우
**When** 장중 배치 범위를 산출하면
**Then** `open_time`/`close_time`을 기준으로 장중 30분 슬롯 범위가 정상 거래일과 다르게 계산된다.

### Story 1.3: 배치 실행 계보 상태머신

As a Neo,
I want 모든 배치 실행이 lease·fence를 가진 멱등 상태머신으로 관리되기를,
So that 중첩 실행이나 stale worker가 데이터를 덮어쓰지 않고 재시도 이력이 안전하게 보존된다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `logical_runs`(logical_run_key PK, trading_day, batch_kind, active_attempt_run_id, canonical_success_run_id, current_complete_run_id, latest_partial_run_id, published_at)와 `runs`(run_id PK UUID, logical_run_key FK, attempt_no, fence_token, lease_expires_at, started_at/finished_at, trigger, status, skip_reason, stage_status JSONB `{candidates, tags, supply_3day, market_supply, outcome_tracking}` 전체 키를 포함(각 초기값 `pending` — 단계별 값은 `pending | running | success | failed | partial` 5중 하나, data-model.md 전이 규칙 참조), unprocessed_count, truncated_count, fallback_used, selection_input_hash, original_count, excluded_count) 테이블이 생성된다(AD-3, data-model.md).

**Given** stage 결과를 쓰는 시점에 "부분 처리"와 "완료"를 구분해야 하는 경우
**When** stage-write RPC가 stage 값을 기록하면
**Then** 각 stage는 `success`(완결) 또는 `partial`(성공했으나 일부 행 누락·미해결, `unprocessed_count`와 함께) 또는 `failed`(실패) 중 하나로만 기록되며, **`partial`/`failed`는 `success`가 아니므로 이 attempt를 완전 발행(`ready_to_publish`/`published`) 후보로 만들지 않는다**(adapter의 일부 성공을 `success`로 위장해 부분 데이터가 완전 스냅샷에 섞이는 것 금지, AD-13/15/20).

**Given** close 또는 premarket 배치가 시작되는 경우
**When** `start_attempt(logical_run_key)` RPC를 호출하면
**Then** logical row가 잠기고 새 `run_id`(UUID), 증가하는 `attempt_no`, `fence_token`, lease가 발급되며 기존 `active_attempt_run_id`가 있었다면 `superseded`로 종결된다.

**Given** intraday 배치가 시작되는 경우
**When** `start_attempt`를 호출하면
**Then** logical_run_key가 `(trading_day, batch_kind, KST 30분 슬롯)` 형식으로 생성/조회된다(예: `intraday:2026-09-01:09:30`).

**Given** 특정 attempt가 stage 결과를 쓰려는 경우
**When** `(run_id, stage, fence_token, lease_token, expected_status)`를 받는 전용 stage-write RPC를 호출하면
**Then** 자신이 소유한 stage 결과만 idempotent upsert되고, fence_token이 일치하지 않으면 쓰기가 거부된다.

**Given** attempt의 heartbeat가 만료된 경우
**When** reaper가 주기 실행되면
**Then** 완료된 필수 stage가 하나라도 있으면 `ready_to_publish`로, 하나도 없으면 `failed`로 CAS 처리되며, 이미 다른 attempt가 같은 logical key를 `active`로 잡고 있으면 무조건 `failed`로 처리된다.
**And** 이 `ready_to_publish` CAS는 **crash 복구용 구출(salvage) 경로**이며 완전 발행을 보장하지 않는다 — 실제 발행은 아래 `publish_attempt`가 필수 stage가 **전부 `success`인지** 재검증하며(AD-20), `partial`/`failed` stage가 하나라도 있으면 완전 발행은 rollback되고 해당 attempt는 `latest_partial_run_id`로만 남는다(AD-13, data-model.md stage_status 전이 규칙).

**Given** `ready_to_publish` 상태의 attempt가 있는 경우
**When** `publish_attempt(run_id, fence_token)` RPC를 호출하면
**Then** serializable transaction 안에서 logical row가 잠기고 active/fence/lease, batch_kind, 필수 stage 완료 여부가 검증된 뒤 `current_complete_run_id`(및 close의 경우 `canonical_success_run_id`)와 `published_at`, attempt `published` 상태가 함께 commit되며 어느 단계든 실패하면 전부 rollback된다
**And** close가 아닌 batch_kind(premarket/intraday)는 `canonical_success_run_id`를 항상 NULL로 둔다(AD-15)
**And** Epic 1 시점에는 outcome/tags/supply/market stage가 아직 존재하지 않으므로 이 RPC는 `candidates` stage만을 필수 stage로 검증한다. **확장 지점(hook) 인터페이스(AD-20):** `publish_attempt`는 다음 시그니처의 stage verifier 레지스트리를 보유한다 —
  ```python
  StageVerifier = Callable[[run_id: UUID, stage: str], bool]  # True면 success 판정

  registry: dict[str, list[StageVerifier]] = {
      # 기본 등록: 'candidates' → [verify_candidates_stage]
      # Epic 2/3/4가 각자의 stage 추가 시:
      #   registry.setdefault('tags', []).append(verify_tags_stage)
      #   registry.setdefault('outcome_tracking', []).append(verify_outcome_stage)
      #   registry.setdefault('supply_3day', []).append(verify_supply_stage)
      #   registry.setdefault('market_supply', []).append(verify_market_stage)
  }
  ```
  verifier는 stage별 `success` 검증 외에 stage 결과 row 존재·정합성(예: tags stage면 `candidate_tags` 행 존재, outcome stage면 idempotent OPEN command가 `outcome_events`에 append됨)을 함께 확인한다. registry 키 추가가 곧 `publish_attempt`의 필수 stage 목록 확장이며, 이 합의는 `packages/domain`의 `stage_registry.py` 한 곳에 정의해 모든 호출자가 동일한 진입점을 공유한다(AD-1/20).

**Given** 이력 조회가 필요한 경우
**When** 과거 attempt를 조회하면
**Then** superseded/failed 이력 행이 삭제되지 않고 보존되어 있다(AD-19).

**Given** stage X가 이전 attempt에서 이미 `success`로 기록된 경우
**When** 이후 attempt의 동일 stage가 실패(`failed`/`partial`)하면
**Then** 이전 attempt의 stage X 결과 데이터는 변경·삭제되지 않고 그대로 조회 가능하다(NFR-5 — 실패 단계가 이전 단계의 유효 데이터를 덮어쓰지 않음, stage-write RPC는 항상 새 attempt 범위에만 쓴다).

**Given** 두 attempt가 동일 `logical_run_key`에 대해 동시에 `start_attempt`를 호출하는 경우(예: 스케줄과 수동 트리거가 같은 순간에 도착)
**When** 두 요청이 실행되면
**Then** 정확히 하나만 새 `active_attempt_run_id`/fence를 획득하고, 다른 하나는 즉시 실패하거나 기존 active attempt 정보와 함께 거부된다 — 이 동작은 실제 동시 호출을 발생시키는 concurrency 테스트로 검증되며, GitHub Actions `concurrency.group`(Story 1.7)은 보조 수단일 뿐 이 DB-level fence가 유일한 권위임을 확인한다(AD-3).

**Given** 남은 벽시계 예산(NFR-2/7 — 다음 배치까지의 시간)이 설정된 임계값 이하로 줄어든 경우
**When** 오케스트레이터가 다음 stage를 시작하려 하면
**Then** 아직 시작하지 않은 stage는 시작되지 않고 `partial`로 표시되며 해당 stage의 후보/작업 수가 `unprocessed_count`에 반영된다 — 이미 실행 중인 stage는 중단하지 않고 완료까지 기다리되, 그 이후 신규 stage 시작만 차단한다(예산 워치독, NFR-2/7).

### Story 1.4: LS OpenAPI 공통 클라이언트

As a Neo,
I want 모든 LS OpenAPI 호출이 TR별 예산·재시도 정책을 공유하는 단일 클라이언트를 거치기를,
So that 이후 어떤 TR을 추가하는 에픽도 같은 클라이언트를 재사용할 수 있고 30분 벽시계 예산을 안전하게 지킨다.

**Acceptance Criteria:**

**Given** 클라이언트가 초기화되는 경우
**When** TR 호출 요청이 들어오면
**Then** TR 이름별로 독립된 token bucket(개인 기준 1건/초, 시장 단위 TR은 별도 설정 가능)이 적용된다(NFR-3, AD-6)
**And** 클라이언트 인터페이스는 특정 TR에 종속되지 않고 임의 TR 코드+파라미터를 받는 범용 형태로 구현되어 Epic 2/3/4의 신규 TR 추가 시 재설계가 필요 없다.

**Given** LS API가 429(rate limit)를 반환하는 경우
**When** 클라이언트가 응답을 처리하면
**Then** `Retry-After` 헤더의 delta-seconds 또는 HTTP-date를 파싱해 대기 후 재시도하며, 값이 비정상이면 bounded default backoff로 대체한다.

**Given** 재시도 횟수 또는 남은 벽시계 예산이 소진된 경우
**When** 클라이언트가 이를 감지하면
**Then** 호출은 `RATE_LIMIT_EXHAUSTED` 또는 예산 소진 result_code로 실패 반환되며, 호출자는 이를 `partial`/`unprocessed_count`로 상위에 전파할 수 있다.

**Given** TR 간 교차 병렬화가 시도되는 경우
**When** 개발자가 이를 활성화하려 하면
**Then** 클라이언트는 이를 기본 비활성 상태로 두며, 실측 검증(production secret 없이) 전까지 활성화할 수 없음을 설정으로 강제한다(Deferred).

### Story 1.5: 후보 모집단 자동 갱신

As a Neo,
I want 매 거래일 스케줄에 조건검색식(t1859)이 실행되어 후보 모집단이 저장되기를,
So that 이후 모든 태깅·수급·outcome 기능의 원천 데이터가 확보된다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `candidates`(candidate_id PK attempt-scoped, attempt_run_id FK, ticker, name, trading_day, truncated bool, UNIQUE(ticker, trading_day, attempt_run_id))와 `candidate_source_contrib`(PK (candidate_id, attempt_run_id, source), source `t1859|t1852|t1856`, contribution_weight (0,1])가 생성된다
**And** `candidates.source` 컬럼은 두지 않는다(AD-21).

**Given** screen stage가 실행되는 경우
**When** t1859 호출이 성공하면
**Then** 반환된 종목이 거래대금 기준으로 정규화되고(거래대금 null/비유한이면 제외, result code 기록), 150종목 초과 시 거래대금 내림차순·종목코드 오름차순으로 상위 150개만 선택되며 나머지는 `truncated=true`로 표시된다(NFR-7, AD-6).

**Given** 후보 선정이 완료된 경우
**When** `runs`에 결과를 기록하면
**Then** `selection_input_hash`, `original_count`, `excluded_count`, `truncated_count`가 함께 저장되며, 동일 input artifact에 대해서는 동일 hash·후보 집합이 재현된다(AD-12).

**Given** screen stage가 성공적으로 완료된 경우
**When** Story 1.3의 stage-write RPC를 호출하면
**Then** `stage_status.candidates`가 `success`로 기록되고 이 attempt가 이후 `publish_attempt`의 후보가 될 수 있다.

**Given** 저장 건수와 조건검색식 반환 건수를 대조하는 경우
**When** `runs` 테이블을 조회하면
**Then** 두 값이 정확히 일치하거나(절단 없음), 절단된 경우 그 차이가 `truncated_count`로 설명된다.

**Given** t1859 호출이 정상 응답했지만 조건을 만족하는 종목이 0건인 경우(정상적인 "오늘은 후보 없음")
**When** stage-write RPC를 호출하면
**Then** 이는 `failed`가 아닌 `success`(candidate_count=0)로 기록되어, 호출 자체가 실패한 경우와 명확히 구분된다.

### Story 1.6: 후보 모집단 대체 경로 폴백

As a Neo,
I want t1859가 실패했을 때 t1852/t1856 경로로 자동 폴백되기를,
So that 조건검색 세션 장애가 발생해도 후보 모집단 갱신이 완전히 중단되지 않는다.

**Acceptance Criteria:**

**Given** t1859 호출이 실패(세션/터미널 제약 등)하는 경우
**When** screen stage가 이를 감지하면
**Then** t1852/t1856 경로로 재시도하고, 성공 시 `runs.fallback_used = true`가 기록된다.

**Given** t1859와 t1852/t1856이 같은 종목에 대해 서로 다른 거래대금을 반환하는 경우
**When** 후보 집합을 정규화하면
**Then** source 우선순위 `t1859 > t1852 > t1856`과 최대 유효 거래대금으로 정규화되며, 각 종목의 `candidate_source_contrib`에 기여 source·weight가 기록된다(published candidate마다 최소 1행, weight 합계 1).

**Given** 폴백으로 수집된 모집단이 있는 경우
**When** 이후 에픽(태깅/outcome)이 이 후보를 참조하면
**Then** 원천 구분값으로 필터링 가능하며, 두 원천이 동일한 모집단이라고 가정하지 않는다(화면 구분 표기는 Epic 4/5에서 구현).

**Given** t1859와 폴백 경로가 모두 실패하는 경우
**When** screen stage가 완료되면
**Then** 배치는 `partial` 또는 `failed`로 종료되고 `unprocessed_count`가 기록되며 조용한 누락이 발생하지 않는다.

### Story 1.7: 스케줄 자동 배치 실행

As a Neo,
I want GitHub Actions가 개장 전/장중 30분/종가 확정 스케줄로 배치를 자동 실행하기를,
So that 매일 수동 개입 없이 후보 모집단이 최신 상태로 유지된다.

**Acceptance Criteria:**

**Given** `.github/workflows/`에 스케줄 워크플로가 정의된 경우
**When** cron이 트리거되면
**Then** 개장 전 1회, 장중 30분 간격, 종가 확정 1회(cron `0 7 * * 1-5` UTC = 16:00 KST) 스케줄이 UTC로 기술되고 KST 환산 주석이 병기된다(NFR-8).

**Given** 워크플로가 실행되는 경우
**When** 동일 `logical_run_key`에 대해 동시 실행이 시도되면
**Then** GitHub `concurrency.group: wave-double-${{ inputs.logical_run_key }}`가 중복 실행을 큐잉/취소하되 최종 권위는 Story 1.3의 DB fence임을 확인한다(AD-3).

**Given** 휴장일에 스케줄이 트리거되는 경우
**When** 배치가 Story 1.2의 `trading_calendar`를 조회하면
**Then** API 호출 없이 no-op으로 조기 종료하고 `runs.skip_reason = holiday`가 기록된다.

**Given** `trigger`가 스케줄인 경우
**When** `runs`에 기록하면
**Then** `trigger = schedule`로 구분 기록된다(수동은 Story 1.10에서 `manual`).

**Given** GitHub Actions 스케줄이 지연되거나 스킵되는 경우
**When** 배치 상태를 관찰하면
**Then** 이는 실패가 아닌 정상 조건으로 간주되며(NFR-1/8), Story 1.9의 화면이 "미갱신" 상태로 이를 표현할 수 있는 근거(finished_at 부재)가 `runs`에 남는다.

### Story 1.8: 대시보드 스냅샷 조회 API

As a Neo,
I want 화면이 완전한 스냅샷과 부분 스냅샷을 명확히 분리해 조회할 수 있기를,
So that 서로 다른 배치의 데이터가 한 화면에서 섞이지 않는다.

**Acceptance Criteria:**

**Given** `logical_runs`/`runs`/`candidates`가 존재하는 경우
**When** `get_dashboard_snapshot()` SQL 함수/RPC를 호출하면
**Then** `complete_snapshot`(current_complete_run_id 기준), `latest_attempt`, `available_partial_sections`, `missing_sections`, `unprocessed_items`, `no_snapshot`이 분리되어 반환된다(AD-13).

**Given** Epic 1 시점에는 candidates section만 구현되어 있는 경우
**When** 스냅샷을 조회하면
**Then** `available_partial_sections`/`missing_sections`는 `candidates` section만 평가하고, 나머지 section(`tags`,`supply_3day`,`market_supply`,`outcome_tracking`)은 이후 에픽이 구현할 때까지 항상 `missing_sections`에 포함된다
**And** section 하나는 오직 하나의 `run_id`에서만 읽는다.

**Given** 아직 첫 발행 이전(첫 배치도 실행되지 않은) 상태인 경우
**When** 스냅샷을 조회하면
**Then** `no_snapshot = true`가 반환되고 `NO_SNAPSHOT` result_code가 로그에 남는다(AD-10).

**Given** partial attempt가 존재하는 경우
**When** 스냅샷을 조회하면
**Then** `latest_partial_run_id`가 별도로 반환되며 `current_complete_run_id`(정상 pointer)를 낮추지 않는다.

**Given** 웹이 이 API를 호출하는 경우
**When** 인증을 확인하면
**Then** publishable key + RLS가 허용한 SELECT 경로로만 접근 가능하다(AD-7).

### Story 1.9: 오늘의 후보 화면 뼈대 & 배치 이력 화면

As a Neo,
I want 브라우저에서 배치 상태와 후보 모집단 현황을 확인할 수 있기를,
So that 매일 시스템이 정상 동작하는지 짧은 시간 안에 알 수 있다.

**Acceptance Criteria:**

**Given** DESIGN.md의 컬러/타이포그래피/spacing/rounded 토큰이 정의된 경우
**When** 디자인 시스템을 구현하면
**Then** canvas/surface/surface-raised/surface-elevated, ink-*, accent/accent-strong, positive/negative/caution/informational, Pretendard 기반 타이포그래피 스케일이 코드 토큰으로 존재한다(UX-DR1).

**Given** App shell을 구현하는 경우
**When** ≥1200px 화면에서 렌더링하면
**Then** 좌측 240px 고정 내비게이션에 `오늘의 후보`/`성과 검증`/`배치 이력` 링크가 있고 활성 항목은 골드 텍스트+인셋으로 표시되며, 768px 미만에서는 사이드바가 sheet로 전환된다(UX-DR2, UX-DR15).

**Given** `/` 라우트에 접속하는 경우
**When** Story 1.8의 스냅샷 API를 호출하면
**Then** Data trust bar가 화면 최상단에 고정되어 최근 배치 상태(성공/부분성공/실패/휴장일 스킵)·KST 실행 시각·트리거 유형·신선도(60분 이상 경과 시 stale 표시)를 표시한다(FR-6a, UX-DR3).

**Given** 아직 태깅 기능이 없는 Epic 1 시점인 경우
**When** `/`에 태깅된 후보가 없으면
**Then** "오늘 태깅된 후보가 없습니다."와 "조건검색 결과/전략 시그널 기준" 설명이 표시되며(배치가 실패한 경우 이 빈 상태보다 실패 상태가 우선 표시된다), 후보 모집단 건수는 신뢰도 확인용 참고 정보로 노출 가능하다.

**Given** `/runs` 라우트에 접속하는 경우
**When** 배치 이력을 조회하면
**Then** 각 attempt의 trigger/status/stage_status/skip_reason/truncated_count/unprocessed_count가 시간 역순으로 표시된다.

**Given** 로딩 중인 경우
**When** 데이터가 아직 도착하지 않았으면
**Then** 실제 카드와 같은 높이의 3~6개 skeleton이 표시되고 전체 화면이 빈 검정으로 보이지 않는다(UX-DR18).

**Given** 배치가 실패한 상태로 화면을 열면
**When** Data trust bar를 확인하면
**Then** 실패 배너와 수동 트리거 버튼(Story 1.10)이 함께 노출된다(FR-6a).

**Given** 배치 상태 변경이 발생하는 경우
**When** 화면이 이를 반영하면
**Then** `aria-live="polite"` 영역으로 알리며 키보드 포커스를 강제 이동하지 않는다(UX-DR14).

**Given** hover 전용 액션이 없는 화면인 경우
**When** 키보드로 조작하면
**Then** `j`/`k`로 후보 카드 간 이동, `Enter`로 근거 패널 열기/닫기, `/`로 후보 검색 포커스, `r`로 새로고침, `g t`/`g v`로 각각 오늘의 후보/성과 검증 네비게이션, `Esc`로 열린 패널/팝오버 닫기가 동작하며 모든 액션은 DOM에 상주하거나 포커스로 노출되어 hover 없이 접근 가능하다(UX-DR13).

**Given** 자동 배치 실패, 부분성공, stale, 폴백 원천 사용 중 하나가 발생하는 경우
**When** 화면이 이를 사용자에게 알리면
**Then** 비차단 Toast/notice가 표시되고 `aria-live="polite"`로 스크린 리더에도 전달되며, 색상이 아닌 문장과 타임스탬프로 오래됨/상태를 명확히 한다(UX-DR11, UX-DR14).

### Story 1.10: 인증 & 수동 트리거

As a Neo,
I want 인증된 세션에서만 배치를 수동으로 트리거할 수 있기를,
So that public 리포지토리에서도 비인가 실행이나 secret 노출 없이 안전하게 운영할 수 있다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `dispatch_request`(dispatch_request_id PK, idempotency_key, payload_hash, requested_by, created_at)와 `dispatch_outbox`(outbox_id PK, dispatch_request_id FK, status `queued→accepted→started→completed|failed|dead_letter`, lease_expires_at, logical_run_key) 테이블이 생성된다(AD-18, data-model.md).

**Given** Neo가 로그인하지 않은 상태인 경우
**When** `/`에 접속하면
**Then** Supabase Auth email OTP/magic link로 단일 운영자 세션을 요구하며, server-side subject allowlist에 없는 사용자는 dispatch 권한을 얻지 못한다(AD-7).

**Given** 인증된 Neo가 수동 실행 버튼을 누르는 경우
**When** dispatch 요청이 전송되면
**Then** route가 JWKS signature/issuer/audience/expiry/sub, SameSite=Strict double-submit CSRF, 사용자 rate limit을 검증한 뒤 단일 DB RPC로 `dispatch_request`+`dispatch_outbox`를 함께 생성한다(AD-7/18).

**Given** 같은 idempotency key+payload hash로 재요청하는 경우
**When** dispatch route가 이를 수신하면
**Then** 기존 `dispatch_request_id`를 replay하고 새 요청을 만들지 않으며, 같은 key+다른 hash는 `409`를 반환한다.

**Given** 요청된 `logical_run_key`에 이미 `active_attempt_run_id`가 설정되어 있는 경우(스케줄 실행이 진행 중이거나 다른 수동 실행이 이미 진행 중)
**When** 새 수동 dispatch가 요청되면
**Then** 새 attempt로 기존 실행을 대체(supersede)하지 않고 `409`로 거부되며, 응답에 기존 active attempt의 `run_id`/시작 시각/트리거 유형이 포함되어 운영자가 상황을 파악할 수 있다(Story 1.3의 fence 모델과 일관).

**Given** outbox worker가 동작하는 경우
**When** `queued` 상태의 outbox 행을 처리하면
**Then** `FOR UPDATE SKIP LOCKED`와 만료 lease로 claim한 뒤 GitHub workflow dispatch를 호출하고 상태가 `queued → accepted → started → completed|failed|dead_letter`로 전이한다.

**Given** GitHub가 dispatch를 수락했지만 workflow 첫 단계 receipt가 아직 없는 경우
**When** lease가 만료되면
**Then** 재발송 대신 `accepted` 상태를 유지한 채 receipt 폴링만 재시도하며, 일정 시간 내 receipt가 나타나지 않으면 `dead_letter`로 전이해 사람의 수동 재개를 요구한다.

**Given** outbox 행이 `dead_letter`에 도달하는 경우
**When** 상태 전이가 커밋되면
**Then** AD-10 알림 계약에 따라 GitHub Issue로 "필요 조치" 항목이 생성되어 Neo가 원인을 확인하고 수동으로 재개(재요청 또는 무시 처리)할 때까지 open으로 유지되며, 이 dead_letter 상태는 Data trust bar/배치 이력에서도 조용히 묻히지 않고 노출된다.

**Given** Database Webhook이 동작하지 않는 경우
**When** fallback을 확인하면
**Then** Supabase `pg_cron` 1분 scan이 durable fallback으로 동작한다.

**Given** 수동 트리거로 실행된 배치인 경우
**When** `runs`를 조회하면
**Then** `trigger = manual`로 기록되어 스케줄 실행과 구분된다.

**Given** 브라우저 콘텍스트인 경우
**When** 코드를 감사하면
**Then** Supabase secret, LS token, GitHub token이 `NEXT_PUBLIC_*`으로 노출되지 않고 server-only 환경에만 존재한다(AD-7, NFR-1).

### Story 1.11: 호스팅 배포 파이프라인

As a Neo,
I want 웹 애플리케이션이 무료로 실제 인터넷에 배포되기를,
So that 브라우저로 언제든 대시보드에 접속할 수 있다.

**Acceptance Criteria:**

**Given** 호스팅 제공자 후보를 평가하는 경우
**When** server-only Node 24 Route Handler, secret env, TLS, 무료 운영, 한국 리전(또는 허용 가능한 latency) 조건으로 비교하면
**Then** 공식 한도 문서와 contract smoke test 결과를 근거로 **하나의 제공자(Vercel Hobby, 2026-09-01 결정)** 로 선정되었고 Architecture Spine의 Deferred 항목이 결정으로 전환된다. 남은 것은 구현 시점의 contract smoke test(실배포·한도 근접의 신선도 표시 비혼동 검증)뿐이다.

**Given** 제공자가 선정된 경우
**When** 배포 파이프라인을 구성하면
**Then** main 브랜치 병합 시 자동 배포되고, secret은 제공자의 환경변수 저장소에만 존재하며 코드/로그/커밋 이력에 평문으로 남지 않는다(NFR1, §6.3).

**Given** 배포가 완료된 경우
**When** 실제 도메인으로 `/`, `/runs`에 접속하면
**Then** Story 1.9에서 구현한 화면이 정상 로딩되고 Story 1.8의 스냅샷 API 응답을 받는다(smoke test).

**Given** Vercel Hobby의 빌드 시간/대역폭 한도가 문서화되어 있는 경우
**When** 운영 중 사용량이 한도의 80%를 초과하면
**Then** 이를 감지하는 로그/알림(예: 배포 workflow의 사용량 조회 단계)이 기록되며, 실제 한도 초과로 서비스가 저하되는 경우 그 상태는 Data trust bar의 "stale"(신선도 저하) 표시와는 구분되는 별도 상태(예: "서비스 접속 불가")로 노출 가능함이 문서화·확인된다(혼동 방지).

### Story 1.12: 백업 & 복원 검증

As a Neo,
I want 운영 데이터가 정기적으로 암호화 백업되고 복원 가능함이 검증되기를,
So that 무료 Supabase 플랜에 PITR이 없어도 실전 데이터를 잃지 않는다.

**Acceptance Criteria:**

**Given** trusted backup workflow가 구성된 경우
**When** 6시간마다 스케줄이 트리거되면
**Then** transaction-consistent `pg_dump`가 생성되고 `age` 공개키로 암호화되어 GitHub Actions artifact로 14일간 보관된다(AD-17).

**Given** 백업 job이 완료되는 경우
**When** manifest를 확인하면
**Then** schema migration version, cutoff 시각, checksum이 기록되고 실패 시 능동 알림이 발생한다(AD-10 알림 계약 — GitHub Issue 접수, 백업 실패가 무인 환경에서 조용히 묻히지 않게 함).

**Given** 분기 1회 복원 드릴 스케줄이 트리거되는 경우
**When** 최신 backup을 disposable local PostgreSQL에 복원하면
**Then** migration 적용, read-model 생성, smoke test, canonical pointer 정합 확인이 모두 통과해야 하며 RPO 6시간·RTO 8시간 목표 충족 여부가 기록된다.

**Given** artifact quota/retention/restore test가 목표(RPO 6h/RTO 8h)를 충족하지 못하는 경우
**When** 이를 감지하면
**Then** production release가 차단되고 별도 결정으로 백업 저장소 변경을 검토해야 함이 문서화된다.

**Given** fork/PR 워크플로가 이 백업 job을 트리거할 수 없는 경우
**When** 워크플로 트리거 조건을 확인하면
**Then** default branch의 trusted workflow만 backup/restore를 수행하며 fork에는 production secret이 제공되지 않는다(AD-11).

<!-- ============================================================ -->

## Epic 2: 전략 태깅 & 오늘의 후보 노출

Neo가 후보 모집단 중 전략 A/B/C 시그널이 발생한 종목만 다중 태그와 함께 확인하고, 장중 시그널 유지/소멸을 구분해 본다.

**의존성 노트(중요):** Story 2.6(오늘의 후보 카드 UI)은 Epic 4 Story 4.1(`supply_3day` 스키마의 `investor_net_status`)에 대한 순방향 의존성을 가진다(Story 2.6 선행조건 노트 참조). Sprint Planning 시 Epic 4 Story 4.1을 이 에픽의 2.5-2.7 배치 이전 또는 동시 배치로 앞당길 것을 권장한다.

**FRs covered:** FR3, FR3a, FR3b

### Story 2.1: 일봉 캐시 스키마 & 신규 종목 초기 적재

As a Neo,
I want 시그널 계산에 필요한 120거래일 일봉이 신규 편입 종목에 대해 확보되기를,
So that 전략 A/B/C 시그널을 계산할 데이터 기반이 마련된다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `daily_ohlcv`(PK (ticker, trading_day), open/high/low/close/volume, adjusted, adjustment_version) 테이블이 생성된다(AD-5, data-model.md).

**Given** 후보 모집단에 신규 편입 종목이 있는 경우
**When** 일봉 확보 stage가 실행되면
**Then** t8410을 `sujung=Y`, `qrycnt=120`(≤500)으로 단일 콜 호출해 120거래일 이력을 확보한다.

**Given** 신규 종목의 이력이 120거래일 미만(상장 이력 부족)인 경우
**When** 캐시 조회 상태를 반환하면
**Then** 해당 종목은 `INELIGIBLE_INSUFFICIENT_HISTORY`로 반환되고 태깅 대상에서 제외되며 그 사실이 후보 상태로 기록된다(저장 컬럼이 아닌 adapter 응답 계약).

**Given** API 호출 또는 저장이 실패하는 경우
**When** 상태를 판정하면
**Then** `ERROR`로 반환되고 retryable stage error로 처리되어(정상적인 이력부족과 구분) stage가 재시도될 수 있다.

**Given** 여러 종목이 동시에 신규 편입되는 경우
**When** 배치당 처리량을 확인하면
**Then** 일봉 전체이력 조회는 신규 편입 종목 수에 비례하며 NFR-3의 TR별 1건/초 예산(Story 1.4의 LS 클라이언트) 안에서 처리된다.

### Story 2.2: 일봉 캐시 증분 갱신

As a Neo,
I want 기존에 캐시된 종목이 매 배치마다 최소한의 API 호출로 최신 상태를 유지하기를,
So that 벽시계 예산을 지키면서도 시그널 계산이 항상 최신 데이터를 사용한다.

**Acceptance Criteria:**

**Given** 종목이 이미 `daily_ohlcv`에 이력을 보유한 경우
**When** 증분 갱신 stage가 실행되면
**Then** 마지막 저장 거래일 다음부터 cutoff(당일)까지 누락일만 조회해 채운다(정상 운영 시 1거래일 증분).

**Given** corporate-action(분할/무상증자 등) 조정 버전이 변경된 경우
**When** 증분 갱신 stage가 이를 감지하면
**Then** `adjustment_version`이 갱신되고 영향 구간(해당 종목의 과거 구간)이 재구축된다.
**And** 재구축된 close/high/low/open 값은 **수정주가(adjusted)** 기준이며(LS `t8410 sujung=Y` 응답 사용, NFR-9), `adjustment_version` 메타데이터로 어떤 보정이 적용되었는지 보존되어 Epic 3의 outcome 진입가 계산에 그대로 사용될 수 있다.

**Given** 배치당 예산(NFR-2/7)을 검증하는 경우
**When** 회귀 테스트를 실행하면
**Then** 정상 운영 시 배치당 전체이력 조회는 신규 편입 종목 수에만 비례함이 확인된다.

**Given** 이 테이블에 대한 저장 정리 정책을 확인하는 경우
**When** NFR-4를 검토하면
**Then** `daily_ohlcv`는 정리 대상이 아니며 장기 보존됨이 코드/문서에 명시된다(정리하면 매일 재조회가 필요해 역효과).

**Given** 추적 중인 종목의 증분 갱신 중 LS 응답의 `pricechk`(수정주가 조정 마커) 또는 전일 종가 대비 ±30% 초과 갭이 관측되는 경우
**When** 이 stage가 완료되면
**Then** 해당 조정 신호(ticker, trading_day, pricechk 여부, 갭%)가 stage 결과에 typed 값으로 노출되어(예: stage 결과의 `adjustment_flags` 목록), Story 3.8의 판정 로직이 `daily_ohlcv`를 재조회하지 않고도 이 신호를 소비할 수 있다 — Story 3.8의 2단 감지(pricechk 1차, 갭 2차) 로직 자체는 이 stage가 아니라 Story 3.8이 소유하지만, 감지에 필요한 원시 신호는 이 stage가 최초로 관측하고 노출한다.

### Story 2.3: 운영·백테스트 공유 전략 API 진입점

As a Neo,
I want 실전 태깅과 백테스트가 동일한 전략 계산 함수를 사용하기를,
So that 운영 수식이 백테스트와 따로 진화하며 재현성이 깨지는 일이 없다.

**Acceptance Criteria:**

**Given** `backtest.strategy_api.compute_abc(frame) -> StrategyResult`가 구현되는 경우
**When** 임의의 일봉 프레임을 입력하면
**Then** 전략 A(RSI+CCI&OBV ∪ RSI+IBS&OBV ∪ RSI+ADX&OBV, OBV window=3, ADX 25 완화), B(일봉 스토캐스틱 %K(14-3) 쌍바닥 + 주봉 %K(20-3) 우상향), C(스토캐스틱 3바닥 하락 다이버전스 K5·D3·div20·gap5)의 시그널이 계산되며, 파라미터 상수는 `backtest/indicator_opt/combine_strategies.py`와 `union.py`에 고정된 값을 그대로 재사용한다(재사용 경계: 데이터 로더 교체, 지표 로직 무변경).

**Given** 백테스트 엔진의 숨은 필터 3건을 반영하는 경우
**When** 시그널을 계산하면
**Then** ATR(14) 유효성 게이트(finite & > 0 필요, 초기 약 14봉 폐기), 마지막 봉 시그널 폐기, 최소 보유 1봉 규칙이 실전 계산에도 동일하게 적용된다(Deferred: ATR 게이트 제거는 V1에서 하지 않음).

**Given** 동일 거래일에 TP·SL 판정이 동시에 발생하는 경우(Epic 3에서 재사용될 규칙)
**When** 우선순위를 적용하면
**Then** 기존 `backtest.engine`과 동일하게 SL을 우선한다.

**Given** 입력 데이터가 비유한(NaN/Inf 등)이거나 계산 불가능한 경우
**When** API가 이를 처리하면
**Then** 예외를 숨기지 않고 typed error(예: `SIGNAL_COMPUTE_ERROR`)를 반환하며, 하나의 신규 종목 오류가 전체 tagging을 막지 않는다(다른 종목은 정상 처리).

**Given** `ohlcv_cache`가 종목별 상태를 반환하는 경우
**When** 전략 API가 이를 참조하면
**Then** `READY`인 종목만 계산 대상이 되고, `INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR`는 각각 태깅 제외/retryable stage error로 구분 처리된다.

### Story 2.4: 골든 픽스처 회귀 테스트

As a Neo,
I want 신규 태깅 로직이 기존 `screen_abc.py`와 통계적으로 유사한 결과를 내는지 자동 검증되기를,
So that 태깅 재구현이 백테스트가 검증한 전략을 실제로 재현하는지 확신할 수 있다.

**Acceptance Criteria:**

**Given** 과거 임의 거래일 1일이 골든 픽스처로 고정된 경우
**When** 신규 태깅 로직(Story 2.3의 `compute_abc`)을 이 픽스처의 동일 종목집합에 실행하면
**Then** 결과 시그널 집합이 `screen_abc.py`를 동일 종목집합에 돌린 결과와 대조되고 전략별 Jaccard 유사도가 계산된다.

**Given** 골든 픽스처의 구체적 형식이 필요한 경우
**When** `tests/fixtures/golden/`에 픽스처를 정의하면
**Then** 다음 3파일로 구성된다(Story 1.1 스캐폴딩에서 `tests/fixtures/` 계약의 일부로 생성)
  - `golden_day.json` — `{ "trading_day": "YYYY-MM-DD", "batch_kind": "close", "universe": ["종목코드..."] }` (픽스처가 고정하는 거래일·대상 종목집합)
  - `ohlcv_raw.tar`/`ohlcv_raw.json`(또는 동일 형식의 압축 파일) — 그 거래일까지의 일봉 원본(OHLCV)으로, `daily_ohlcv` 스키마와 동일 필드(`ticker`/`trading_day`/`open`/`high`/`low`/`close`/`volume`, `sujung=Y` 기준)
  - `golden_signals.json` — `{ "trading_day", "strategy_signals": { "A": ["종목코드..."], "B": [...], "C": [...] } }` — `screen_abc.py`가 동일 종목집합에 대해 산출한 참조 시그널 집합(비어 있으면 안 됨, AD-5)
**And** 이 3파일 형식은 `tests/fixtures/`의 스키마 계약으로 문서화되며, CI는 파일 존재·비어있지 않음·`strategy_signals` 키 완비(A/B/C)를 선행 검증한다.

**Given** Jaccard 유사도가 0.9 이상인 경우
**When** CI가 이 테스트를 실행하면
**Then** 배포가 허용된다.

**Given** Jaccard 유사도가 0.9 미만인 경우
**When** CI가 이 테스트를 실행하면
**Then** 배포가 차단되고 불일치 종목이 목록으로 출력되어 원인(데이터 기준 차이 vs 로직 결함)을 조사할 수 있다.

**Given** 골든 픽스처가 비어 있는 경우
**When** 테스트를 실행하면
**Then** 이는 명시적으로 실패 처리된다(빈 픽스처로 통과되지 않음, AD-5).

**Given** yfinance(백테스트)와 LS `t8410 sujung=Y`(실전)의 수정주가 기준 차이(배당 조정 여부)가 알려진 경우
**When** 이 회귀 테스트의 판정 기준을 문서화하면
**Then** 완전 일치가 아니라 통계적 유사도(Jaccard≥0.9)가 판정 기준임이 테스트 코드 주석과 NFR-6 문서에 명시된다
**And** 이 게이트는 조정-방식론 동등성이 별도 단발성 검증으로 확인된 후에만 유효함이 명시된다(AD-5).

### Story 2.5: 후보 태깅 stage & 저장

As a Neo,
I want 후보 모집단 한정으로 전략 시그널이 계산되어 태깅 결과가 저장되기를,
So that 태깅된 후보만 대시보드에 노출될 수 있는 데이터가 마련된다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `candidate_tags`(tag_id PK, candidate_id FK, strategy `A|B|C`, signal_date, attempt_run_id, tagged_at, status `active|vanished`, params_meta JSONB, UNIQUE(candidate_id, strategy, attempt_run_id)) 테이블이 생성된다.

**Given** screen stage가 완료되어 후보 모집단이 확보된 경우
**When** tagging stage가 실행되면
**Then** 각 후보 종목에 대해 Story 2.1/2.2의 `daily_ohlcv`와 Story 2.3의 `compute_abc`를 호출해 시그널을 계산하고, 시그널이 발생한 종목에 하나 이상의 전략 태그(다중 가능, 예 A∩B)를 부여한다.

**Given** tagging stage가 성공적으로 완료된 경우
**When** Story 1.3의 stage-write RPC를 호출하면
**Then** `stage_status.tags`가 `success`로 기록되고, 이 stage가 이제 `publish_attempt`의 필수 stage 목록에 포함된다(Epic 1의 확장 지점 사용)
**And** Story 1.8의 `get_dashboard_snapshot()`이 이 시점부터 `tags` section을 `available_partial_sections`/`complete_snapshot`에 반영한다(이전까지는 `missing_sections`에 있던 section이 채워짐).

**Given** 태깅이 모든 배치(개장전/장중/종가)에서 계산되는 경우
**When** `candidate_outcome` 생성 자격을 확인하면
**Then** 종가 확정 배치의 태깅만 이후 Epic 3의 outcome 생성 자격을 가지며, 장중 배치의 태깅은 참고 표시 전용임이 코드 경로로 구분된다.

**Given** 재현성을 확인해야 하는 경우
**When** `params_meta`를 조회하면
**Then** 시그널 계산에 사용된 파라미터 스냅샷이 태깅 시점 기준으로 보존되어 있다.

**Given** 일부 종목에서 Story 2.3의 `SIGNAL_COMPUTE_ERROR`가 발생하는 경우(다른 종목은 정상 계산됨)
**When** tagging stage 결과를 stage-write RPC로 기록하면
**Then** 전체를 `success`로 기록하지 않고 `partial`로 기록하며, 에러가 발생한 종목 수가 `unprocessed_count`로 함께 저장된다 — 정상 계산된 종목의 태깅 결과는 그대로 저장되어 조용히 누락되지 않는다.

### Story 2.6: 오늘의 후보 카드 UI

As a Neo,
I want 대시보드에서 태깅된 후보만 전략 태그와 함께 확인할 수 있기를,
So that 왜 이 종목이 노출됐는지 5분 안에 판단할 수 있다.

**선행조건 노트:** 아래 "부분결측" AC는 Epic 4 Story 4.1이 정의하는 `investor_net_status`(`confirmed`/`pending`/`missing`) 상태 구분을 전제로 한다. Epic 4보다 먼저 이 스토리를 구현하는 경우, 해당 AC는 Story 4.1이 완료될 때까지 스텁(항상 결측 없음으로 표시) 상태로 두거나 이 스토리의 구현을 Story 4.1 이후로 순서를 조정한다.

**Acceptance Criteria:**

**Given** Story 2.5에서 태깅된 후보가 존재하는 경우
**When** `/`에 접속하면
**Then** 하나 이상의 태그를 가진 후보만 Candidate summary card로 노출되며(태깅 없는 후보는 노출되지 않음), 카드에는 종목명·코드·전략 A/B/C 태그가 표시된다(UX-DR4).

**Given** 후보가 다중 태그(A∩B 등)를 가진 경우
**When** Strategy tag 컴포넌트를 렌더링하면
**Then** 모든 태그가 가로로 나열되고 좁은 폭에서는 줄바꿈 대신 `+N`으로 접힌다(UX-DR7).

**Given** 태그를 클릭하는 경우
**When** 사용자가 상호작용하면
**Then** 필터링이 아니라 해당 전략의 설명/성과로 이동하는 보조 액션이 실행된다.

**Given** 카드 문구를 작성하는 경우
**When** 텍스트를 렌더링하면
**Then** `전략 A · 전략 C 시그널`처럼 관찰 가능한 표현을 쓰고 `강력 매수 신호` 같은 확정적 표현은 사용하지 않는다(UX-DR16).

**Given** 태깅된 후보의 수급 데이터 중 일부가 결측인 경우(부분결측)
**When** Candidate summary card를 렌더링하면
**Then** 카드에 `수급 일부 미수집` 같은 단서가 표시되어 사용자가 근거 패널(Story 4.7)을 열기 전에 상태를 인지할 수 있다. 이 상태는 카드를 목록에서 제외하지 않으며, "태깅된 후보 없음"(빈 상태)이나 "배치 실패"(우선 표시)와는 구분된다.

**Given** 태깅된 후보가 없는 경우
**When** `/`를 열면
**Then** Epic 1의 "오늘 태깅된 후보가 없습니다." 빈 상태가 그대로 표시된다(배치 실패 시 실패 상태 우선).

### Story 2.7: 장중 시그널 유지·소멸 표시

As a Neo,
I want 오전에 태깅되었던 종목이 장중에 사라지면 그 이유를 구분해서 볼 수 있기를,
So that 시그널 소멸과 배치 실패, 모집단 이탈을 혼동하지 않는다.

**Acceptance Criteria:**

**Given** 09:30 배치에서 태깅된 종목이 11:00 배치에서 태깅되지 않는 경우
**When** tagging stage가 이를 감지하면
**Then** 해당 태그의 `status`가 `vanished`로 전이되고, 후보 목록에서 사라지지 않고 "소멸" 표시로 남는다.

**Given** 종목이 소멸(시그널 재계산 결과 미충족), 모집단 이탈(조건검색식 결과에서 빠짐), 수집 실패(Epic 1의 부분성공)의 세 원인 중 하나로 목록에서 빠지는 경우
**When** 화면에 표시하면
**Then** 세 상태가 서로 다른 문구/배지로 명확히 구분되어 혼동되지 않는다.

**Given** 태깅 이력을 조회하는 경우
**When** `candidate_tags`를 `run_id`/`tagged_at` 단위로 조회하면
**Then** 당일 태깅 변화 추이(언제 태깅됐고 언제 소멸했는지)가 조회 가능하다.

**Given** 장중 화면에 접속하는 경우
**When** UJ-2(장중 상태 라벨, EXPERIENCE.md) 상태 표시를 확인하면
**Then** "장중 참고 · 최종 추천 미확정"이 고정 표시되어 장중 태깅이 최종 추천이 아님을 명확히 한다.

<!-- ============================================================ -->

## Epic 3: 실전 사후 결과 자동 적재

종가 확정 배치가 태깅된 후보의 진입가·TP/SL/TIMEOUT/OPEN 판정을 append-only로 자동 적재하기 시작해, 실전 검증 데이터(SM-3: 90거래일 시점 종결 outcome ≥ 50건)가 최대한 빨리 쌓이기 시작한다.

**배포 순서 노트(중요):** Story 3.8(가격 조정 이상 감지 & SUSPENDED 전이)의 감지 로직은 Story 3.5(TP/SL 판정)보다 먼저 또는 최소한 동시에 배포되어야 한다. NFR-9가 경고하는 "분할 미보정 시 진입가 대비 저가 비교로 즉시 SL 오판정"은 3.5가 3.8 없이 단독 배포될 때 그대로 재현되는 위험이다. Story 3.5는 이 위험을 스스로 차단하는 가드 AC를 포함한다(아래 참조).

**스프린트 계획 노트:** 이 에픽은 10개 스토리로 Epic 1과 유사한 규모이며 하나의 스프린트 단위로 보기엔 크다. Sprint Planning 단계에서 최소 2개 서브 배치(예: 이벤트/관찰 스키마 3.1-3.4 → 판정 로직 3.5-3.10, 단 3.8은 위 배포 순서 노트에 따라 3.5와 같은 배치 또는 그 이전 배치에 포함)로 나눠 진행할 것을 권장한다.

**FRs covered:** FR8

### Story 3.1: Outcome 이벤트/관찰/projection 스키마

As a Neo,
I want outcome 생명주기가 append-only 이벤트 장부와 재구축 가능한 projection으로 저장되기를,
So that 재실행이 과거 결과를 삭제·변경하지 못한다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `outcome_events`(event_id PK, ticker, strategy, command_type, logical_run_key, payload, created_at)가 append-only로 생성된다(AD-9).

**Given** 이벤트 장부가 생성된 경우
**When** `outcome_observations`를 정의하면
**Then** PK (outcome_id, evaluation_trading_day), high/low/close/result_code 컬럼을 가진 append-only 테이블이 생성된다.

**Given** projection이 필요한 경우
**When** `candidate_outcome`을 정의하면
**Then** outcome_id PK, ticker, strategy, entry_date(UNIQUE (ticker,strategy,entry_date)), entry_price, status(TP|SL|TIMEOUT|OPEN|SUSPENDED|DELISTED), exit_date, exit_price, return_pct, cutoff_n, holding_days 컬럼을 가진 rebuildable projection이 생성된다.

**Given** 동일 (ticker,strategy)에 대한 OPEN이 중복 생성되면 안 되는 경우
**When** partial unique index를 적용하면
**Then** 동일 (ticker,strategy)의 OPEN 상태는 최대 1개만 허용된다.

**Given** source별 지표 산출이 필요한 경우
**When** `candidate_outcome`의 컬럼을 검토하면
**Then** `source` 또는 `source_jsonb` 컬럼을 두지 않는다(AD-21 — Epic 5에서 `candidate_source_contrib` join으로만 산출).

### Story 3.2: Idempotent OPEN command 발행 로직

As a Neo,
I want 종가 확정 배치가 태깅된 후보마다 정확히 한 번만 진입 이벤트를 발행하기를,
So that 재시도나 중복 실행이 중복 진입을 만들지 않는다.

**Acceptance Criteria:**

**Given** close 배치의 canonical 후보 집합이 확정된 경우
**When** OPEN command 발행 로직이 실행되면
**Then** idempotent command key `(logical_run_key, ticker, strategy, command_type=OPEN)`로 `outcome_events`에 append되며, 같은 key로 재호출 시 새 이벤트를 만들지 않고 기존 이벤트를 반환한다.

**Given** OPEN 이벤트가 발행되는 경우
**When** entry 필드를 기록하면
**Then** 진입일=해당 거래일, 진입가=해당 거래일 정규장 종가로 기록된다(장중 확정치가 아닌 종가 확정 배치의 최종 종가)
**And** 이 종가는 Epic 2 Story 2.2가 증분 갱신한 `daily_ohlcv`의 해당 거래일 `close` 값(수정주가 adjusted 기준, NFR-9)을 출처로 하며, Epic 4의 `supply_3day`(3일치 근거 UI 전용 테이블)를 출처로 하지 않는다(두 테이블은 서로 다른 attempt/목적을 가지므로 outcome 진입가 계산에는 `daily_ohlcv`만 사용). corporate-action 영향 구간 재구축(Story 2.2)에 의해 adjusted close가 갱신되었더라도 entry_price는 **OPEN 이벤트가 처음 append된 시점의 close 값으로 고정**되며, 이후 adjusted close 재계산은 영향받지 않는다(이미 발행된 outcome의 entry_price 불변 — Story 3.7 correction event만 예외).

**Given** 이미 해당 (ticker,strategy)에 OPEN 상태인 outcome이 존재하는 경우
**When** 같은 종목이 다음 거래일에 다시 태깅되면
**Then** 새 진입(OPEN)을 생성하지 않는다(재진입 금지, 백테스트 `engine.py:112-113`과 동일).

**Given** 장중 배치에서 태깅된 종목인 경우
**When** OPEN command 발행 대상을 확인하면
**Then** 장중 배치는 이 로직을 호출하지 않으며 `candidate_outcome`에 행을 만들지 않는다.

### Story 3.3: Close 발행 트랜잭션 연결 & 재진입 금지

As a Neo,
I want outcome 생성이 Epic 1의 발행 트랜잭션 안에서 후보 발행과 함께 원자적으로 커밋되기를,
So that outcome이 아직 발행되지 않은 후보를 참조하는 일이 없다.

**Acceptance Criteria:**

**Given** Epic 1 Story 1.3의 `publish_attempt` 확장 지점이 있는 경우
**When** close batch_kind의 attempt를 발행하면
**Then** 같은 serializable transaction 안에서 canonical 후보를 잠근 뒤 Story 3.2의 OPEN command 발행 로직이 호출되고 `outcome` stage 결과가 함께 생성된다(AD-20).

**Given** outcome stage가 이 close 배치의 필수 stage 목록에 추가되는 경우
**When** 필수 stage 완료 여부를 검증하면
**Then** outcome 생성이 실패하면 전체 publish transaction이 rollback된다(candidate/tag 발행과 outcome 생성이 분리되어 불일치 상태가 남지 않음).

**Given** premarket/intraday 배치가 발행되는 경우
**When** 필수 stage 목록을 확인하면
**Then** outcome stage는 이 batch_kind에 포함되지 않는다(AD-15 — `canonical_success_run_id`는 close에만 존재).

**Given** `runs.stage_status.outcome_tracking`을 조회하는 경우
**When** close 배치가 완료되면
**Then** 이 값이 `success`로 기록되어 있다
**And** Story 1.8의 `get_dashboard_snapshot()`이 이 시점부터 `outcome_tracking` section을 반영하며, Epic 5의 `/tracking` 페이지(Story 5.11)가 이를 조회해 Data trust bar를 렌더링할 수 있다.

### Story 3.4: 일자별 판정 관찰 수집

As a Neo,
I want OPEN 상태 outcome마다 매 거래일 고가/저가/종가가 수집되기를,
So that TP/SL/TIMEOUT 판정의 근거 데이터가 확보된다.

**Acceptance Criteria:**

**Given** OPEN 상태의 outcome이 존재하는 경우
**When** 종가 확정 배치가 실행되면
**Then** 해당 종목의 당일 고가/저가/종가가 조회되어 `outcome_observations(outcome_id, evaluation_trading_day)`에 기록된다.

**Given** 동일 (outcome_id, evaluation_trading_day)에 대해 재시도가 발생하는 경우
**When** observation을 다시 기록하려 하면
**Then** 새 행을 만들지 않고 기존 observation을 반환한다(멱등).

**Given** 관찰 대상 조회 시
**When** 추적 대상 목록을 산출하면
**Then** terminal 상태(TP/SL/TIMEOUT)로 확정된 outcome은 이후 배치의 API 조회 대상에서 제외된다(Story 3.6에서 완성).

**Given** 거래정지 기간(SUSPENDED)인 종목이 있는 경우
**When** 관찰을 수집하면
**Then** Story 3.8이 구현되기 전까지는 이 케이스를 별도 처리하지 않되, 이후 스토리에서 자동판정 제외 대상으로 확장될 지점임을 인지한다.

### Story 3.5: TP/SL 판정 & 비용 반영 손익률

As a Neo,
I want 일자별 관찰치를 기준으로 TP/SL이 백테스트와 동일한 규칙으로 판정되기를,
So that 실전 outcome이 백테스트 기대치와 같은 기준으로 비교 가능하다.

**Acceptance Criteria:**

**Given** 해당 종목에 대해 아직 Story 3.8의 가격조정 이상 감지가 수행되지 않았거나(예: Story 3.8이 배포되기 전) 이미 `SUSPENDED`로 판정된 경우
**When** TP/SL/TIMEOUT 판정을 시도하면
**Then** 판정은 보류되며 자동 확정되지 않는다 — Story 3.8이 아직 배포되지 않은 기간에는 이 가드가 유일한 방어선이므로, 두 스토리를 반드시 함께(또는 3.8을 먼저) 배포해야 한다.

**Given** OPEN 상태 outcome의 진입일이 있는 경우
**When** 판정을 시작하면
**Then** 진입 다음 거래일부터 판정하며 시그널 당일(진입일)에는 TP/SL이 발생하지 않는다(최소 보유 1거래일).

**Given** 관찰치의 고가가 TP(진입가×1.03) 이상인 경우
**When** 판정하면
**Then** TP로 확정되며 조건은 `고가 >= TP`(등호 포함)다.

**Given** 관찰치의 저가가 SL(진입가×0.97) 이하인 경우
**When** 판정하면
**Then** SL로 확정되며 조건은 `저가 <= SL`(등호 포함)다.

**Given** 동일 거래일에 TP와 SL이 모두 충족되는 경우
**When** 우선순위를 적용하면
**Then** SL이 우선 확정된다(보수적).

**Given** TP 또는 SL이 확정되는 경우
**When** 손익률을 기록하면
**Then** 왕복 0.1% 비용 차감 후 TP는 정확히 +2.9%, SL은 정확히 −3.1%로 기록된다.

**Given** terminal 상태(TP/SL)가 확정된 경우
**When** 이후 배치가 같은 outcome을 다시 판정하려 하면
**Then** 이미 terminal이므로 재판정하지 않는다(불변, Story 3.7의 correction event만 예외).

### Story 3.6: TIMEOUT 컷오프 확정 & 추적 대상 유계화

As a Neo,
I want 30거래일 내 TP/SL 미도달 종목이 TIMEOUT으로 자동 확정되기를,
So that 추적 대상 수가 무한히 늘어나지 않고 유계로 관리된다.

**Acceptance Criteria:**

**Given** outcome이 생성되는 경우
**When** `cutoff_n` 값을 기록하면
**Then** 초기값 30이 판정에 사용된 실제 N값으로 행에 함께 저장되며, 이후 N이 설정에서 변경되어도 과거 outcome은 재계산되지 않는다.

**Given** 진입 후 30거래일(휴장일 제외) 내 TP/SL 미도달인 경우
**When** 컷오프 판정을 실행하면
**Then** 30거래일째 종가 기준 손익률(비용차감 후 실제 종가 손익)과 함께 TIMEOUT으로 확정된다.

**Given** TIMEOUT으로 확정된 경우
**When** 이후 배치가 추적 대상을 산출하면
**Then** 이 outcome은 API 조회 대상에서 제외되어, 추적 대상 수 P가 항상 `P ≤ (일평균 태깅 후보 수 × 30)`을 만족함이 회귀 테스트로 확인된다.

**Given** 거래정지 기간이 컷오프 계산에 포함되는지 확인하는 경우
**When** 판정 로직을 검토하면
**Then** 다음 산식이 적용되어 거래정지 기간이 컷오프에서 제외된다(2026-09-01 결정):
  - **판정 기준 변수는 달력 경과가 아니라 "실거래 경과일수" `traded_days_since_entry`다.**
  - `traded_days_since_entry` = 진입일 다음 거래일부터 현재까지 **실거래(해당일에 유효한 일봉이 존재)가 발생한 거래일 수**.
  - TIMEOUT 발동 조건: `traded_days_since_entry >= cutoff_n`(초기 30).
  - **휴장일과 거래정지 기간(일봉이 없는 기간) 모두 카운트에서 제외**한다. 거래정지가 끼면 달력으로는 더 늦은 날에 30번째 실거래일이 도래하므로 TIMEOUT도 그만큼 지연된다.
  - 이 정의는 `holding_days`(실제 보유거래일수)와 **동일 원천**을 쓴다 — 거래정지·휴장일은 두 곳 모두에서 빠지므로 TIMEOUT 판정과 분포 분석이 정합한다(Story 3.8과 연계).

**Given** `holding_days`를 조회하는 경우
**When** outcome을 확인하면
**Then** 실제 보유거래일수가 기록되어 TIMEOUT 판정과 분포 분석에 사용 가능하다. **`holding_days`는 위 `traded_days_since_entry`와 같은 실거래 경과일수 정의를 따른다(휴장일·거래정지일 제외).**

### Story 3.7: Outcome correction 이벤트 메커니즘

As a Neo,
I want SUSPENDED 복귀나 수치 수정이 원행 UPDATE가 아니라 버전 관리된 이벤트로만 이뤄지기를,
So that terminal 상태의 불변성이 깨지지 않고 모든 수정 이력이 감사 가능하다.

**Acceptance Criteria:**

**Given** terminal 상태(TP/SL/TIMEOUT)의 outcome이 있는 경우
**When** 일반 UPDATE로 이를 수정하려 하면
**Then** 이 경로는 코드/DB 권한상 차단되며 `outcome_correction` event만 유효한 수정 경로다.

**Given** `outcome_correction` event를 발행하는 경우
**When** expected version을 지정하면
**Then** 현재 버전과 일치할 때만 적용되고(낙관적 동시성), 불일치 시 거부된다.

**Given** SUSPENDED 상태의 outcome이 정상 복귀하는 경우
**When** correction event를 적용하면
**Then** projection이 correction event로부터 재계산되어 업데이트되며 `outcome_events` 원본 이력은 삭제되지 않는다.

**Given** correction 이력을 감사하는 경우
**When** `outcome_events`를 조회하면
**Then** 모든 correction이 사유와 함께 시간순으로 남아있다.

### Story 3.8: 가격 조정 이상 감지 & SUSPENDED 전이

As a Neo,
I want 액면분할·병합 등 가격 조정 이벤트가 발생한 종목을 자동으로 SUSPENDED 처리하기를,
So that 분할 미보정으로 인한 조용한 오판정(즉시 SL 오판정 등)을 방지한다.

**Acceptance Criteria:**

**Given** 추적 중 종목의 Story 2.2 일봉 갱신에서 조정 이벤트가 발생하는 경우
**When** 판정 로직이 이를 감지하면
**Then** **2단 감지(2026-09-01 결정)를 따른다:** ① 1차 신호 — LS `t8410`/`t8451`의 `pricechk`(수정주가 반영 필드)가 해당 거래일에 조정을 보고하면 **갭 크기와 무관하게** `SUSPENDED`로 전이한다(유상증자·주식배당·액면분할 등 갭이 30% 미만인 조정도 놓치지 않음, `pricechk`는 데이터 원천의 조정 진실 원천). ② 2차 안전망 — `pricechk` 마커가 없어도 전일 종가 대비 **±30% 초과 갭**이 관측되면 `SUSPENDED`로 전이한다(미반영 조정·급변 포착). 임계값(±30%)은 설정값으로 한 곳에서 관리·조정 가능하다.
**And** 어느 경로든 자동 TP/SL 판정을 수행하지 않고 Story 3.7의 correction event로 `SUSPENDED` 플래그와 함께 전이시키며 **능동 알림을 발생시킨다(AD-10 알림 계약 — GitHub Issue로 "필요 조치" 항목 생성, Neo가 원인을 확인해 해소할 때까지 open 유지).**

**Given** SUSPENDED 상태인 경우
**When** 컷오프(30거래일) 계산을 수행하면
**Then** 거래정지 기간은 컷오프 계산에서 제외된다 — **산식(Story 3.6의 실거래 경과일수 정의)에 따라 `traded_days_since_entry`는 실거래가 있는 날만 세므로, SUSPENDED로 거래정지·멈춘 기간은 카운트에 포함되지 않는다.**

**Given** 원인이 확인되어 정상 가격으로 복귀한 경우
**When** 운영자가 이를 확인하면
**Then** Story 3.7의 correction event로 SUSPENDED에서 정상 판정 흐름으로 복귀하며, 앞서 발행된 SUSPENDED GitHub Issue가 close된다(수신 확인·해소 이력이 남는다).

**Given** SUSPENDED 상태로 남아있는 outcome이 있는 경우
**When** Epic 5의 승률·PF 계산을 확인하면
**Then** SUSPENDED는 분모(종결 건수)에서 제외된다(Epic 5에서 소비되는 계약).

**Given** SUSPENDED 상태의 GitHub Issue가 일정 기간(예: 14일) 이상 open으로 남아있는 경우
**When** 정기 점검(예: 백업 워크플로와 유사한 주기 job 또는 배치 실행 시 체크)이 이를 감지하면
**Then** 해당 Issue에 경과 일수를 알리는 에스컬레이션 코멘트가 추가되어 무기한 방치되지 않는다(NFR-7의 "outcome 추적 대상은 유계" 원칙과 정합 — SUSPENDED 자체는 분모에서 제외되어 산식에는 영향 없지만, 미해결 상태가 운영자 눈에 계속 보이도록 보장).

### Story 3.9: 상장폐지 DELISTED 종결

As a Neo,
I want 상장폐지된 종목의 outcome이 자동으로 종결 처리되기를,
So that 더 이상 존재하지 않는 종목을 계속 추적 시도하지 않는다.

**Acceptance Criteria:**

**Given** 추적 중 종목이 상장폐지되는 경우
**When** 관찰 수집 stage(Story 3.4)가 종목 상태를 조회하면
**Then** LS 종목 상태 조회 TR(예: 일봉 조회 응답의 상장폐지/거래정지 상태 코드 — 정확한 필드는 구현 시점에 LS OpenAPI 문서로 재확인 필요)이 상장폐지를 보고하는 것을 감지 트리거로 사용한다(Story 3.8의 pricechk/갭 2단 감지와 유사하게 명시적 감지 소스를 가짐).

**Given** 상장폐지 감지 트리거가 발동하는 경우
**When** 이를 감지하면
**Then** Story 3.7의 correction event로 `DELISTED` 상태로 종결되고 추적이 중단되며, **능동 알림을 발생시킨다(AD-10 알림 계약 — GitHub Issue로 "필요 조치" 항목 생성, 수신 확인까지 open).**

**Given** DELISTED로 종결된 경우
**When** 이후 배치가 추적 대상을 산출하면
**Then** 이 outcome은 API 조회 대상에서 완전히 제외된다.

**Given** DELISTED가 승률·PF 계산에 미치는 영향을 확인하는 경우
**When** Epic 5의 지표 계산을 검토하면
**Then** DELISTED는 TP/SL/TIMEOUT과 구분되어 분모 처리 방식이 명확히 정의되어 있다(정상 종결 3종과 혼동되지 않음).

### Story 3.10: Outcome projection 재구축 검증

As a Neo,
I want candidate_outcome이 이벤트 장부로부터 항상 재구축 가능함이 검증되기를,
So that 장애 발생 시 projection을 event로부터 안전하게 복구할 수 있다.

**Acceptance Criteria:**

**Given** 일정 기간 운영되어 `outcome_events`/`outcome_observations`에 이력이 쌓인 경우
**When** 이 이벤트들을 처음부터 재생(replay)하면
**Then** 재구축된 `candidate_outcome`이 현재 저장된 projection과 정확히 일치한다(회귀 테스트).

**Given** 재구축 테스트를 최초 구현 시점부터 동작시키기 위해 fixture가 필요한 경우
**When** `tests/fixtures/outcome_rebuild/`에 테스트 픽스처를 정의하면
**Then** 다음 3파일로 구성된다(Story 1.1 스캐폴딩 `tests/fixtures/` 계약의 일부로 생성, 실제 API에 의존하지 않는 결정적 샘플)
  - `events.json` — `outcome_events`와 동일 필드(`event_id`/`ticker`/`strategy`/`command_type`/`logical_run_key`/`payload`/`created_at`) 배열. OPEN·correction·SUSPENDED/DELISTED 전이를 포함
  - `observations.json` — `outcome_observations`와 동일 필드(`outcome_id`/`evaluation_trading_day`/`high`/`low`/`close`/`result_code`) 배열
  - `expected_projection.json` — 이 두 장부를 재생했을 때 기대되는 `candidate_outcome` projection(`outcome_id`/`ticker`/`strategy`/`entry_date`/`entry_price`/`status`/`exit_date`/`exit_price`/`return_pct`/`cutoff_n`/`holding_days`) 배열
**And** correction event가 포함된 이력의 최종 상태까지 이 fixture가 커버하며, CI가 이 fixture로 재생-대조를 실행한다(결과 불일치 시 배포 차단).

**Given** correction event가 포함된 이력인 경우
**When** 재생을 수행하면
**Then** correction이 적용된 최종 상태까지 정확히 재현된다.

**Given** 이 재구축 테스트가 CI에 포함되는 경우
**When** 스키마나 로직이 변경되면
**Then** 재구축 불일치가 발생하면 배포가 차단된다.

**Given** AD-19에 따라 이 ledger/projection이 cleanup 대상이 아님을 확인하는 경우
**When** NFR-4 정리 정책을 검토하면
**Then** outcome 관련 테이블 전체가 장기 보존 대상임이 명시되어 있다.

<!-- ============================================================ -->

## Epic 4: 후보 근거(3일치 수급) · 시장 전체 수급 · 좋은 수급 힌트

Neo가 태깅된 각 후보의 2일전/1일전/당일 가격·수급, 시장 전체 수급 맥락, '좋은 수급' 힌트를 확인해 5분 안에 매수 판단을 내린다.

**스프린트 계획 노트:** 이 에픽은 수집(4.1-4.6)·화면(4.7-4.11) 2개 영역, 11개 스토리로 하나의 스프린트 단위로 보기엔 크다. Sprint Planning 단계에서 최소 2개 서브 배치(수집 로직 → UI/필터)로 나눠 진행할 것을 권장한다. 단, Story 4.1(`supply_3day` 스키마)은 Epic 2 Story 2.6이 이를 전제(선행조건 노트 참조)로 하므로, Epic 2의 태깅 UI 배치보다 먼저 또는 그와 동시에 배치되어야 한다.

**FRs covered:** FR4, FR5, FR7

### Story 4.1: `supply_3day` 스키마

As a Neo,
I want 후보별 3일치 가격·수급 데이터가 저장될 스키마가 마련되기를,
So that 수집 stage와 화면이 이 위에서 동작할 수 있다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `supply_3day`(candidate_id FK, attempt_run_id FK, trading_day, slot `D-2|D-1|D0`, close, volume, change_pct, foreign_net, institution_net, individual_net, program_net, **investor_net_status `confirmed|pending|missing` (NOT NULL)**, collected_at, UNIQUE(candidate_id, trading_day, attempt_run_id)) 테이블이 생성된다(data-model.md).
**And** `close`/`volume`/`change_pct`는 장중에도 실시간으로 채워지는 반면, **투자자별 순매수 4컬럼(`foreign_net`/`institution_net`/`individual_net`/`program_net`)은 `numeric NULLABLE`**이며, `investor_net_status`가 이 컬럼들의 상태를 행 단위로 선언한다 — `confirmed`(종가 확정 실측값, 실제 0 포함) / `pending`(장중 미확정 — t1702/t1637 투자자별 필드가 전부 0인 상태, 순매수는 NULL) / `missing`(미수집 — 순매수는 NULL). **NULL과 실젯값(0 포함)을 서로 대체하지 않는다**(일관성 규칙 — `미수집·미확정·실제 0` 구분). 4컬럼 중 어느 하나라도 확정값이 없으면 `confirmed`가 될 수 없다.

**Given** 후보가 태깅된 경우
**When** 이 테이블을 참조하면
**Then** candidate_id FK로 Epic 1의 `candidates`, Epic 2의 `candidate_tags`와 연결된다.

**Given** 저장 정리 정책을 확인하는 경우
**When** NFR-4를 검토하면
**Then** D0의 장중 이력 스냅샷만 정리 대상(90일 잠정)이고 D-2/D-1 행은 정리 대상이 아님이 문서화된다.

### Story 4.2: t1702 종목별 가격·수급 수집

As a Neo,
I want 각 태깅된 후보의 2일전/1일전/당일 종가·등락율·거래량·외인·기관·개인 순매수가 자동 수집되기를,
So that 후보 근거 패널에 표시할 데이터가 확보된다.

**Acceptance Criteria:**

**Given** 태깅된 후보 목록이 있는 경우
**When** supply stage가 실행되면
**Then** 각 후보에 대해 t1702를 `fromdt`=2거래일전, `todt`=당일로 1콜 호출해 종가·등락율·거래량·외인(`tjj0016`)·기관(`tjj0018`)·개인(`tjj0008`)을 확보한다(후보당 1콜, NFR-3 1건/초 예산 안에서 Story 1.4 클라이언트를 통해 처리).

**Given** 등락율을 계산하는 경우
**When** 값을 저장하면
**Then** 전일 종가 대비로 계산된 등락율이 저장된다(NFR-9).

**Given** 태깅된 후보 전건에 3행이 존재해야 하는 경우
**When** 결과를 검증하면
**Then** 각 후보마다 D-2/D-1/D0 3행이 거래일 기준으로 정확히 채워지며, 연휴 직후에도 달력일이 아닌 거래일 기준으로 3행이 채워진다.

**Given** supply stage(t1702 부분)가 성공적으로 완료되는 경우
**When** Epic 1 Story 1.3의 stage-write RPC를 호출하면
**Then** `stage_status.supply_3day`가 `success`로 기록되고, 이 stage가 `publish_attempt`의 필수 stage 목록에 포함되며 Story 1.8의 `get_dashboard_snapshot()`이 이 시점부터 `supply_3day` section을 반영한다.

### Story 4.3: t1637 프로그램 순매수 수집 병합

As a Neo,
I want 프로그램 순매수 데이터가 t1702 결과와 병합되기를,
So that 후보별 3일치 데이터의 7개 항목이 완성된다.

**Acceptance Criteria:**

**Given** 후보별 t1702 결과가 확보된 경우
**When** t1637(`gubun2=1` 일자별)을 1콜 호출하면
**Then** `svolume`(순매수수량) 기준 프로그램 순매수가 확보되어 `program_net`으로 병합 저장된다.

**Given** t1636(단일 시점 순위형 스냅샷)을 사용하려는 시도가 있는 경우
**When** 코드 리뷰를 수행하면
**Then** t1636은 3일 시계열에 부적합하므로 사용되지 않고 반드시 t1637이 사용됨이 확인된다.

**Given** 병합이 완료된 경우
**When** `supply_3day` 행을 조회하면
**Then** 종가·거래량·등락율·외인·기관·개인·프로그램 7개 항목이 모두 채워져 있다.

### Story 4.4: D0 당일 행 attempt별 누적 저장

As a Neo,
I want 당일 행이 배치마다 덮어써지지 않고 attempt별로 누적되기를,
So that 장중 수급 흐름의 이력을 볼 수 있다.

**Acceptance Criteria:**

**Given** 장중 30분 간격 배치가 반복 실행되는 경우
**When** D0 slot 데이터를 저장하면
**Then** 이전 attempt의 D0 행을 덮어쓰지 않고 attempt_run_id별로 새 행이 누적된다(UNIQUE (candidate_id, trading_day, attempt_run_id) 제약 활용).

**Given** 하루 동안의 D0 이력을 조회하는 경우
**When** 시계열을 확인하면
**Then** 09:30, 10:00, 10:30 등 각 배치 시점의 값이 개별 행으로 존재해 흐름을 재구성할 수 있다.

**Given** NFR-4의 저장 정리 정책을 적용하는 경우
**When** 정리 주기(잠정 90일)가 도래하면
**Then** D0 장중 이력 스냅샷만 정리되고, D-2/D-1 행이나 종가 확정 시점의 D0 행은 보존 판단 기준에 따라 별도 처리됨이 문서화된다.

### Story 4.5: 빈 수급 적재 방지 가드

As a Neo,
I want 투자자별 필드가 전부 0인 응답을 실제 순매수 0으로 오인해 저장하지 않기를,
So that 장중 미확정 값이 조용히 오염되어 힌트(FR-7)를 틀어지게 하지 않는다.

**Acceptance Criteria:**

**Given** t1702/t1637 응답의 투자자별 필드(외인/기관/개인/프로그램)가 전부 0인 경우
**When** supply stage가 이를 감지하면
**Then** 이 응답을 미완료로 처리하고 재시도하며, 0을 "순매수 0"으로 즉시 적재하지 않는다.

**Given** 재시도 후에도 값이 채워지지 않는 경우(장중 정상 상황)
**When** 배치가 이를 최종 처리하면
**Then** 투자자별 순매수 4컬럼을 **NULL**로 두고 `investor_net_status = 'pending'`으로 저장되어 화면에서 "미확정"으로 렌더링되며, 확정된 0(실제 거래 없음, `confirmed` + 값 0)과 구분된다(Story 4.1 스키마, data-model.md).

**Given** 조회 자체가 실패해 행이 수집되지 않은 경우
**When** 배치가 이를 처리하면
**Then** 투자자별 순매수 4컬럼을 **NULL**로 두고 `investor_net_status = 'missing'`으로 저장되어 화면에서 "미수집"으로 구분된다(0과 혼동 금지).

**Given** 결측 종목이 1건이라도 있는 경우
**When** 배치가 완료되면
**Then** 해당 배치를 부분실패로 `runs`에 기록하고 결측 종목 목록이 함께 남는다(Epic 1의 stage-write RPC 사용).

**Given** 종가 확정 배치에서 이 가드가 발동하는 경우
**When** 15:36 기준 실측 근거를 확인하면
**Then** 재시도 로직이 충분한 여유(16:00 KST 실행, 24분 여유)를 갖고 동작함을 확인한다.

### Story 4.6: `market_supply` 스키마 & t1601 수집

As a Neo,
I want 코스피/코스닥 시장 전체 수급이 자동 수집되기를,
So that 종목별 수급이 비어 있는 장중에도 시장 맥락을 참고할 수 있다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** `market_supply`(attempt_run_id FK, market `KOSPI|KOSDAQ`, trading_day, foreign_net, institution_net, individual_net, program_net, collected_at) 테이블이 생성된다.

**Given** market stage가 실행되는 경우
**When** t1601을 호출하면
**Then** 코스피/코스닥 각각의 외인/기관/개인 집계가 수집되고, 프로그램은 관련 TR(t1631 등)로 보강되어 저장된다.

**Given** 장중 30분 배치 시점마다 조회하는 경우
**When** 값을 비교하면
**Then** t1601은 종목별 TR과 달리 장중 실시간 값을 제공하며 매 배치마다 최신값으로 갱신된다.

**Given** t1601을 종목별 수급에 사용하려는 시도가 있는 경우
**When** 코드 리뷰를 수행하면
**Then** t1601InBlock에는 종목코드(shcode) 파라미터가 없어 시장 단위 전용임이 확인되고 종목별 용도로 오용되지 않는다.

**Given** market stage가 성공적으로 완료되는 경우
**When** Epic 1 Story 1.3의 stage-write RPC를 호출하면
**Then** `stage_status.market_supply`가 `success`로 기록되고, 이 stage가 `publish_attempt`의 필수 stage 목록에 포함되며 Story 1.8의 `get_dashboard_snapshot()`이 이 시점부터 `market_supply` section을 반영한다.

### Story 4.7: 후보 근거 패널(Evidence panel) UI

As a Neo,
I want 후보 카드를 열면 3일치 데이터를 근거로 확인할 수 있기를,
So that 수급 흐름을 판단 근거로 삼을 수 있다.

**Acceptance Criteria:**

**Given** 후보 카드를 클릭/Enter로 여는 경우
**When** Evidence panel이 렌더링되면
**Then** 거래일 순서는 최신(D0)이 위로, 종가·거래량·등락률·외인·기관·개인·프로그램 순매수가 표시된다(UX-DR5).

**Given** 패널이 열리는 경우
**When** 상단 정보를 표시하면
**Then** 원천(t1859/t1852/t1856 또는 기본)과 데이터 생성 시각이 패널 상단에 한 번 표시된다(값마다 반복하지 않음).

**Given** 장중 당일 종목별 수급이 미확정인 경우
**When** 패널을 렌더링하면
**Then** `investor_net_status = 'pending'`에 따라 "미확정"으로 렌더링되며 0으로 보이지 않는다(Story 4.1 스키마).

**Given** 결측 데이터가 있는 경우
**When** 패널을 렌더링하면
**Then** `investor_net_status = 'missing'`에 따라 "미수집"으로 표시되어 빈 칸/0과 구분된다.

**Given** 폴백 원천으로 수집된 후보인 경우
**When** 패널을 렌더링하면
**Then** t1852/t1856 등 실제 원천이 명시적으로 표시된다.

**Given** 태깅된 후보의 3행 중 일부만 결측이고 나머지는 정상인 경우(부분결측)
**When** Evidence panel을 렌더링하면
**Then** 패널 상단(원천/생성시각 라인 아래)에 **부분결측 배지**가 표시되어 "D-2/D-1/D0 중 N행이 미수집" 등 어느 슬롯이 비었는지 알리고, 정상 슬롯과 결측 슬롯(`missing`)이 시각적으로 구분된다. 이 상태는 "태깅된 후보가 없음" 빈 상태(Story 1.9/2.6)와 "완전한 후보" 사이의 **제3의 상태**로, Epic 1 Story 1.9의 "배치 실패 시 실패 상태가 우선 표시된다" 규칙을 그대로 따라 **배치 실패가 더 광범위하면 부분결측보다 실패가 우선**된다.

### Story 4.8: 근거 패널 반응형 전환

As a Neo,
I want 좁은 화면에서도 3일치 데이터를 읽기 편하게 확인할 수 있기를,
So that 모바일에서도 최소한의 확인이 가능하다.

**Acceptance Criteria:**

**Given** 화면 폭이 ≥1200px인 경우
**When** 근거 패널을 렌더링하면
**Then** 고정 3행 테이블 형태로 표시된다.

**Given** 화면 폭이 <768px인 경우
**When** 근거 패널을 렌더링하면
**Then** 날짜별 행 카드 형태로 전환되어 열이 많아도 한 줄에 우겨넣지 않는다(UX-DR15).

**Given** 200% 브라우저 확대 상태인 경우
**When** 패널을 확인하면
**Then** 카드 내용이 잘리지 않는다(UX-DR14).

**Given** 데이터 테이블 형태로 렌더링되는 경우
**When** 접근성을 확인하면
**Then** 행/열 헤더가 제공되고 숫자 단위와 기준일이 숨겨지지 않는다.

### Story 4.9: 시장 전체 수급 패널 UI

As a Neo,
I want 코스피/코스닥 시장 전체 수급을 한눈에 볼 수 있기를,
So that 종목별 수급이 비어있는 장중에도 시장 맥락을 참고할 수 있다.

**Acceptance Criteria:**

**Given** `/`에 접속하는 경우
**When** Market supply panel을 렌더링하면
**Then** 코스피/코스닥 탭으로 나뉘어 외인/기관/개인/프로그램 방향이 숫자+막대로 표시된다(UX-DR6).

**Given** 탭을 전환하는 경우
**When** 상태를 확인하면
**Then** 선택된 탭이 URL 또는 로컬 상태에 보존되어 새로고침 후에도 유지된다.

**Given** 시장 수급이 종목 수급과 다른 신선도를 갖는 경우
**When** 신선도 라벨을 표시하면
**Then** 종목별 수급과 별도의 라벨을 사용해 "장중에도 갱신될 수 있음"을 구분해 표시한다.

**Given** 장중 화면인 경우
**When** 패널 상단을 확인하면
**Then** "장중 참고" 라벨이 고정 표시되어 시장 수급이 참고 정보임을 명시한다.

### Story 4.10: '좋은 수급' 힌트 계산 view

As a Neo,
I want 힌트가 UI가 아니라 버전 관리된 SQL view에서 계산되기를,
So that Python과 UI가 힌트를 다르게 계산하는 불일치가 생기지 않는다.

**Acceptance Criteria:**

**Given** `supply_3day`의 당일(D0) 확정 수급이 있는 경우
**When** versioned SQL view/RPC(AD-8)를 호출하면
**Then** **`investor_net_status = 'confirmed'`인 행에 한해** 프로그램+외인+기관이 모두 `> 0`인 경우에만 "좋은 수급"으로 판정된다(`>= 0`이 아님 — 프로그램매매 0인 거래없는 종목을 최고 등급으로 오판정하는 결함 방지).

**Given** 세 부문 중 하나라도 0 이하이거나 미충족인 경우
**When** 판정하면
**Then** "미충족"으로 표시된다.

**Given** 데이터가 없어 판정할 수 없는 경우(장중 미확정 `pending`, 미수집 `missing`)
**When** 판정하면
**Then** "판정 불가"로 표시되며 "미충족"으로 잘못 표시되지 않는다. view는 순매수 컬럼의 NULL을 "판정 불가"로, `confirmed`+실제 0을 "미충족"으로 구분해야 한다(일관성 규칙, Story 4.1 참조).

**Given** 장중 시점인 경우
**When** 힌트를 조회하면
**Then** 종목별 수급이 미제공되므로 "판정 불가"가 기본값이며, 종가 확정 배치에서만 "좋은 수급"/"미충족"으로 확정된다.

**Given** 임계값을 조정해야 하는 경우
**When** 코드를 검토하면
**Then** 임계값 정의가 한 곳(view/설정)에서 유지·조정 가능하다.

**Given** 동일 fixture로 Python 계산값과 SQL view 결과를 비교하는 경우
**When** migration gate 테스트를 실행하면
**Then** 두 결과가 동등함이 검증된다(AD-8).

### Story 4.11: 힌트 배지 통합 & 필터

As a Neo,
I want 후보 카드에서 수급 힌트를 바로 확인하고 조건별로 후보를 걸러볼 수 있기를,
So that 여러 후보 중 우선순위를 빠르게 정할 수 있다.

**Acceptance Criteria:**

**Given** Story 4.10의 힌트 view 결과가 있는 경우
**When** Candidate summary card를 렌더링하면
**Then** 수급 힌트(좋은 수급/미충족/판정 불가)가 카드에 표시된다(UX-DR4 연계).

**Given** 전략/수급힌트/시그널상태/원천 필터를 적용하는 경우
**When** 사용자가 필터를 선택하면
**Then** 후보 목록이 해당 조건으로 걸러진다.
**And** 수급 데이터에 부분결측이 있는 후보를 명시적으로 제외/포함할 수 있는 "수급 결측 포함/제외" 필터 옵션이 제공되어, 데이터 정합성이 필요한 분석(예: `좋은 수급` 비율 확인)에서 부분결측 후보를 제외할 수 있다(Story 2.6/4.7의 부분결측 상태와 연동).

**Given** 필터 결과가 0건인 경우
**When** 화면을 렌더링하면
**Then** 현재 적용된 필터가 표시되고 한 번의 조작으로 전체 초기화할 수 있다.

**Given** 필터 UI를 키보드로 조작하는 경우
**When** 접근성을 확인하면
**Then** 모든 필터 옵션이 키보드로 접근 가능하다(UX-DR14).

<!-- ============================================================ -->

## Epic 5: 실전 성과 검증 화면 & 모집단 편향

Neo가 `/tracking` 페이지에서 추천 후보의 사후 결과를 확인하고, 실전 승률·PF를 백테스트 기대치와 대조하며, 모집단 편향의 크기를 직접 관측한다. V2(자동매매) 진행 게이트의 유일한 근거.

**스프린트 계획 노트:** 이 에픽은 스키마/계산(5.1-5.4)·지표 view(5.5-5.10)·화면(5.11-5.14) 3개 영역, 14개 스토리로 5개 에픽 중 가장 크며 하나의 스프린트 단위로 보기엔 크다. Sprint Planning 단계에서 최소 3개 서브 배치(편향 스키마/계산 → 지표 view → 화면)로 나눠 진행할 것을 권장한다.

**FRs covered:** FR9, FR10

### Story 5.1: `bias_events` append-only 스키마

As a Neo,
I want 모집단 편향 관측치가 append-only 이벤트로 저장되기를,
So that 임의 거래일 조회가 과거 이벤트를 보존한 채 source별로 분해되어 이뤄질 수 있다.

**Acceptance Criteria:**

**Given** migration을 적용하면
**Then** **두 테이블**이 append-only로 생성된다(FR-10, AD-12, AD-21):
  - `bias_events`(bias_event_id PK, trading_day, logical_run_key, calculation_meta JSONB, created_at) — 편향 계산 한 회차의 메타. **`source` 컬럼을 두지 않는다**(AD-21 — source 권위는 `candidate_source_contrib`에 있음).
  - `bias_event_by_source`(bias_event_id FK, source `t1859|t1852|t1856`, candidate_pop_signal_count, backtest_universe_signal_count, intersection_count, diff_count, missed_opportunity_count, PK(bias_event_id, source)) — 한 bias_event 회차가 여러 source에 대해 행을 가지며, 이 분해 때문에 source별 view(Story 5.6/5.14)가 단일 row에서 바로 집계 가능하다. `diff_count`/`missed_opportunity_count`는 해당 source 모집단 한정의 수치다.

**Given** 같은 `trading_day`에 대해 재계산이 필요한 경우
**When** 새 계산 결과가 발생하면
**Then** 기존 `bias_events`/`bias_event_by_source` 행을 수정하지 않고 새 `bias_event_id`로 append하며, canonical view가 동일 `trading_day`에 대해 **가장 최근 created_at의 bias_event_id**를 선택한다.

**Given** 과거 event를 조회하는 경우
**When** 임의 거래일(또는 임의 bias_event_id)을 조회하면
**Then** 그 시점의 행이 삭제되지 않고 그대로 남아있으며, source별 행(`bias_event_by_source`)도 함께 보존된다.

**Given** source별 분해가 AD-21을 따르는지 검증해야 하는 경우
**When** canonical view 정의를 검토하면
**Then** `bias_event_by_source.source`는 `candidate_source_contrib.source`만 참조하며, 별도 source 컬럼을 row에 보관하지 않는다(AD-21 — 권위 일관성).

### Story 5.2: 백테스트 유니버스 시그널 계산

As a Neo,
I want 104종목 백테스트 유니버스 전체에 대해서도 전략 시그널이 계산되기를,
So that 후보 모집단과 비교할 기준선이 마련된다.

**Acceptance Criteria:**

**Given** 104종목 백테스트 유니버스 목록이 현재 `backtest/data/fetch_kospi200.py`(백테스트 전용 스크립트)에만 존재하는 경우
**When** 운영 배치가 이 목록을 참조해야 하면
**Then** 이 목록이 `tests/fixtures/`(또는 그에 준하는 버전 고정 위치)에 운영 배치가 직접 import할 수 있는 fixture로 승격되며, 원본 스크립트와 값이 어긋나지 않음이 테스트로 확인된다.

**Given** 백테스트 유니버스(104종목) 목록이 확보된 경우
**When** Epic 2의 `compute_abc`를 이 유니버스 전체에 실행하면
**Then** 각 종목의 전략 A/B/C 시그널 발생 여부가 계산된다(`screen_abc.py`의 104종목 고정 유니버스와 별도로 구축, 지표 로직은 무변경).

**Given** 유니버스 종목의 일봉 이력이 필요한 경우
**When** 데이터 원천을 확인하면
**Then** 이 계산은 Epic 2의 `daily_ohlcv`(LS 데이터)를 재사용해 실전 시그널과 동일 기준으로 비교됨이 문서화된다.

**Given** 백테스트 유니버스(104종목) 중 현재 후보 모집단(최대 150종목, 조건검색식 기준)에 포함되지 않은 종목이 있는 경우(대부분의 유니버스 종목이 이에 해당할 수 있음 — Epic 2는 후보 모집단 종목만 `daily_ohlcv`에 적재하므로)
**When** 편향 지표 계산이 시작되면
**Then** 이 스토리(또는 이 스토리가 호출하는 별도 적재 stage)가 해당 종목들의 `daily_ohlcv`를 후보 모집단 멤버십과 무관하게 독립적으로 적재/백필하며, `INELIGIBLE_INSUFFICIENT_HISTORY`로 대부분의 유니버스 종목이 계산 제외되는 상황을 방지한다(FR-10의 편향 지표가 유효하려면 유니버스 전체의 시그널 계산이 가능해야 함).

**Given** 계산 결과가 필요한 경우
**When** 결과를 조회하면
**Then** 임의 거래일에 대해 백테스트 유니버스 시그널 집합이 재현 가능하게 산출된다.

### Story 5.3: 편향 지표 계산 로직

As a Neo,
I want 후보 모집단 시그널과 백테스트 유니버스 시그널의 교집합·차집합·기회누락이 계산되기를,
So that 모집단 편향의 크기를 수치로 관측할 수 있다.

**Acceptance Criteria:**

**Given** 임의 거래일에 대해 "조건검색식 후보 ∩ 전략 시그널"과 "백테스트 유니버스(104종목) ∩ 전략 시그널" 두 집합이 있는 경우
**When** 편향 계산 로직을 실행하면
**Then** 두 집합의 크기·교집합·차집합이 계산된다.
**And** 이 계산은 `candidate_source_contrib`(Epic 1 Story 1.6)를 통해 **각 source 별로 분해되어** 수행된다 — 즉 `t1859` 모집단 시그널 ∩ `t1859` 백테스트 시그널, `t1852` 모집단 시그널 ∩ `t1852` 백테스트 시그널, `t1856` 모집단 시그널 ∩ `t1856` 백테스트 시그널이 각각 독립 계산되어 Story 5.1의 `bias_event_by_source` 한 회차의 source별 행이 된다. 폴백으로 한 source가 비어 있을 때는 size=0/intersection=0/null-safe 산식이 적용된다.

**Given** 백테스트 유니버스 기준 시그널 중 후보 모집단에 포함되지 않아 추천되지 않은 건이 있는 경우
**When** 기회 누락을 계산하면
**Then** 이 건수가 산출되며, NFR-7로 절단된 종목(M=150 초과분)의 시그널도 기회 누락에 포함된다.
**And** 기회 누락도 `bias_event_by_source`의 source별 행에 나뉘어 저장되어, 폴백 source의 기회 누락이 주 source의 기회 누락과 구분된다.

**Given** 계산 결과를 검증하는 경우
**When** 단위 테스트를 실행하면
**Then** 알려진 입력 집합에 대해 교집합·차집합·기회누락 수가 source별로 수학적으로 정확히 계산됨이 확인된다.

### Story 5.4: 편향 계산 close 배치 연결 & append

As a Neo,
I want 편향 계산이 비용 절감을 위해 일 1회 종가 배치에서만 실행되기를,
So that 배치 예산을 낭비하지 않으면서도 편향을 매일 관측할 수 있다.

**Acceptance Criteria:**

**Given** close 배치가 실행되는 경우
**When** bias stage가 실행되면
**Then** Story 5.2/5.3의 source별 분해 계산 결과가 Story 5.1의 `bias_events` 1행 + `bias_event_by_source` source별 N행으로 함께 append된다.

**Given** premarket/intraday 배치인 경우
**When** bias stage 실행 여부를 확인하면
**Then** 이 stage는 실행되지 않는다(일 1회 종가 배치 전용).

**Given** bias stage가 완료되는 경우
**When** Epic 1 stage-write RPC를 호출하면
**Then** `stage_status`에 편향 계산 완료 여부가 기록된다(옵션 stage로, **AD-13의 5개 section taxonomy(`candidates`/`tags`/`supply_3day`/`market_supply`/`outcome_tracking`)에는 포함되지 않는 독립 키**로 기록되며, 필수 발행 조건에는 포함하지 않아 편향 계산 실패가 후보/태깅/outcome 발행을 막지 않는다).

### Story 5.5: 승률·PF 핵심 산식 view(전체 기준)

As a Neo,
I want 실전 승률·PF가 SQL view에서 백테스트와 동일한 기준으로 계산되기를,
So that Python과 화면이 다른 값을 보여주는 불일치가 없다.

**Acceptance Criteria:**

**Given** `candidate_outcome`에 종결(TP/SL/TIMEOUT) 건이 있는 경우
**When** versioned SQL view(AD-8)를 호출하면
**Then** 승률 = (손익률 > 0인 종결 건수) / (TP+SL+TIMEOUT 건수), PF = Σ(양의 손익률)/|Σ(음의 손익률)|이 계산되며 둘 다 비용 차감 후 손익률 기준이다.

**Given** OPEN 상태 건이 있는 경우
**When** 분모를 계산하면
**Then** OPEN은 분모에서 제외된다.

**Given** SUSPENDED/DELISTED 상태 건이 있는 경우
**When** 분모를 계산하면
**Then** 이들은 정상 종결(TP/SL/TIMEOUT) 3종과 구분되어 별도 처리되며 혼입되지 않는다.

**Given** 승패를 판정하는 경우
**When** 기준을 확인하면
**Then** 상태가 아니라 손익률 부호로 판정한다(백테스트 `metrics/metrics.py:70-72`와 동일 — TIMEOUT이 양의 손익으로 끝나면 승으로 집계).

**Given** 동일 fixture에 대해 Python 계산값과 이 view 결과를 비교하는 경우
**When** migration gate 테스트를 실행하면
**Then** 두 값이 동일함이 검증된다(AD-8).

### Story 5.6: 전략별 + 원천별 분리 view

As a Neo,
I want 전략(A/B/C)별, 원천(t1859/t1852/t1856)별로도 승률·PF를 분리 조회할 수 있기를,
So that 폴백 원천이 지표에 미치는 영향을 구분해 볼 수 있다.

**Acceptance Criteria:**

**Given** Story 5.5의 핵심 view가 있는 경우
**When** 전략별 파라미터를 추가하면
**Then** A/B/C 각각 및 전체 승률·PF가 조회 가능하다.

**Given** source별로 분리하는 경우
**When** view를 조회하면
**Then** `candidate_source_contrib`(Epic 1 Story 1.6)만 join하여 source를 결정하며, `candidate_outcome`에 독립된 source 컬럼/JSONB 사본을 두지 않는다(AD-21).

**Given** 여러 source가 하나의 candidate에 기여한 경우
**When** primary source를 표시하면
**Then** weight 내림차순 → source 우선순위(t1859>t1852>t1856) 규칙으로 도출된다.

### Story 5.7: 표본 게이트(30건) 처리

As a Neo,
I want 종결 건수가 부족할 때 승률·PF 대신 표본 부족 상태가 표시되기를,
So that 잡음 수준의 숫자를 실제 신호로 착각하지 않는다.

**Acceptance Criteria:**

**Given** 종결(TP+SL+TIMEOUT) 건수가 30건 미만인 경우
**When** Metric comparison 계산을 요청하면
**Then** 승률·PF 수치 대신 "표본 부족(n/30)"이 반환되고 백테스트 기대치와의 대조 판정이 수행되지 않는다.

**Given** 종결 건수가 30건 이상인 경우
**When** 계산을 요청하면
**Then** 정상적으로 승률·PF 수치가 반환된다.

**Given** 종결/진행중 건수를 화면에 표시하는 경우
**When** 결과를 반환하면
**Then** "종결 n건 / 진행중 m건"이 게이트 상태와 무관하게 항상 함께 반환된다.

### Story 5.8: 95% 신뢰구간 계산 & 기대치 판정

As a Neo,
I want 전략별 승률의 95% 신뢰구간과 백테스트 기대치의 위치가 계산되기를,
So that 표본 30~50건 구간에서도 고정 임계값보다 통계적으로 타당한 판정을 볼 수 있다.

**Acceptance Criteria:**

**Given** 종결 건수가 30건 이상인 경우(Story 5.7의 표본 게이트 판정을 그대로 사용 — 이 스토리가 임계값을 별도로 재정의하지 않음)
**When** 신뢰구간 계산을 요청하면
**Then** 전략별 승률의 95% 신뢰구간이 계산된다.

**Given** 백테스트 기대치(A 68.71%, B 68.95%, C 66.00%)가 있는 경우
**When** 신뢰구간과 대조하면
**Then** 기대치가 신뢰구간 안/밖 어디에 위치하는지 판정되어 반환된다.

**Given** 표본이 30~50건 구간인 경우
**When** 판정 방식을 검토하면
**Then** 이 구간에서는 신뢰구간 판정이 고정 임계값(Story 5.9)보다 우선 참조되도록 설계된다.

**Given** 표본이 50건을 초과하는 경우
**When** 판정 방식을 검토하면
**Then** 신뢰구간 기반 판정이 계속 우선 참조되며(표본이 클수록 신뢰구간이 좁아져 판정력이 높아짐), Story 5.9의 고정 이탈 임계값은 모든 표본 크기에서 보조 경고로만 병행 표시된다 — 별도의 표본 크기별 판정 방식 전환은 없다.

### Story 5.9: 이탈 임계값(보조) 표시

As a Neo,
I want 신뢰구간 판정을 보완하는 보조 이탈 임계값도 함께 볼 수 있기를,
So that 큰 이탈을 빠르게 스크리닝할 수 있다.

**Acceptance Criteria:**

**Given** 종결 건수가 30건 이상인 경우
**When** 승률이 기대치 대비 ±10%p 밖이거나 PF가 기대치 대비 ±25% 밖인 경우
**Then** 경고로 구분 표시된다.

**Given** 이 임계값이 신뢰구간 판정과 함께 존재하는 경우
**When** 화면에 표시하면
**Then** 이탈 임계값이 신뢰구간 판정을 대체하지 않고 보완하는 보조 지표로 표시된다.

### Story 5.10: 컷오프 편향 고지

As a Neo,
I want TIMEOUT이 백테스트에 없는 상태임을 알고 그로 인한 왜곡 크기를 볼 수 있기를,
So that 실전 대조 결과를 오독하지 않는다.

**Acceptance Criteria:**

**Given** 종결 건 중 TIMEOUT이 포함된 경우
**When** 화면에 표시하면
**Then** TIMEOUT 건수와 그로 인한 예상 왜곡(N=30 기준 A ±0 / B PF +0.0125 / C ±0)이 함께 표기된다.

**Given** 이 고지가 화면에 노출되는 경우
**When** 배치 설계를 확인하면
**Then** 이는 표본 게이트·비용 모델과 함께 셋이 동시에 구현되어야 하는 항목으로 취급되며 개별 후순위화되지 않았음이 확인된다(PRD `[NOTE FOR PM]`).

### Story 5.11: `/tracking` 라우트 & Outcome row UI

As a Neo,
I want 추적페이지에서 후보별 사후 결과를 확인할 수 있기를,
So that 어떤 후보가 어떤 상태로 종결/진행중인지 알 수 있다.

**Acceptance Criteria:**

**Given** `/tracking`에 접속하는 경우
**When** 페이지가 렌더링되면
**Then** 메인 대시보드와 별도 라우트로 존재하며(UX-DR12), 후보별 TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED가 Outcome badge로 텍스트 표시된다(UX-DR8).

**Given** FR-6a가 "메인 대시보드와 추적페이지 상단" 모두에 배치 신뢰도 표시를 요구하는 경우
**When** `/tracking` 페이지를 렌더링하면
**Then** Epic 1 Story 1.9의 Data trust bar와 동일한 규칙(배치 상태·KST 실행 시각·트리거 유형·신선도, 실패 시 수동 실행 버튼)이 이 페이지 상단에도 표시되며, Story 3.3에서 반영된 `outcome_tracking` section의 `run_id`/시각을 기준으로 한다.

**Given** OPEN 상태인 outcome이 있는 경우
**When** 목록을 렌더링하면
**Then** OPEN은 항상 별도 카운트로 표시되며 성과 분모에 포함되지 않는다.

**Given** 상태 배지를 표시하는 경우
**When** 색상을 적용하면
**Then** 색상은 보조 수단이며 툴팁 또는 상세 문장으로 상태 의미가 제공된다.

**Given** 페이지 필터 상태가 있는 경우
**When** 사용자가 필터를 변경하면
**Then** 그 상태가 페이지 상태로 유지된다(뒤로가기/새로고침에도 보존).

### Story 5.12: Metric comparison UI

As a Neo,
I want 실전 승률·PF와 백테스트 기대치를 같은 화면에서 비교할 수 있기를,
So that 전략이 실제로 통하는지 데이터로 판단할 수 있다.

**Acceptance Criteria:**

**Given** `/tracking`에서 전략 A/B/C 또는 전체를 전환하는 경우
**When** Metric comparison을 렌더링하면
**Then** 선택된 범위의 승률·PF와 백테스트 기대치가 같은 축으로 비교되고 종결/진행중 건수가 항상 함께 표시된다(UX-DR9).

**Given** 종결 건수가 30건 미만인 경우
**When** 화면을 렌더링하면
**Then** 승률·PF 수치 대신 "표본 부족 n/30"이 성과 수치보다 크게 표현된다.

**Given** 종결 건수가 30건 이상인 경우
**When** 화면을 렌더링하면
**Then** Story 5.8의 95% 신뢰구간과 안/밖 판정, Story 5.9의 이탈 임계값 경고가 함께 표시된다.

**Given** Story 5.10의 컷오프 편향 고지가 있는 경우
**When** 화면에 표시하면
**Then** TIMEOUT 건수와 예상 왜곡이 노출된다.

### Story 5.13: Bias diagnostic UI

As a Neo,
I want 특정 날짜의 모집단 편향을 숫자로 확인할 수 있기를,
So that 실전 승률 이탈의 원인이 모집단 편향인지 판단할 수 있다.

**Acceptance Criteria:**

**Given** `/tracking`에서 날짜를 선택하는 경우
**When** Bias diagnostic을 렌더링하면
**Then** 후보모집단∩전략시그널, 백테스트유니버스시그널, 교집합, 기회누락 숫자 4개와 짧은 설명이 표시된다(UX-DR10).

**Given** 차집합을 표현하는 경우
**When** 시각화를 적용하면
**Then** 과장된 그래픽 장식 없이 담백하게 표현된다.

**Given** 승률 이탈이 관측된 경우
**When** 편향 지표와 함께 조회하면
**Then** 차이가 실패 원인으로 단정되지 않고 참고 정보로 제시된다.

**Given** 선택한 날짜에 `bias_events`가 없는 경우(아직 배치가 실행되지 않은 미래 날짜, 또는 이 기능이 배포되기 전의 과거 날짜)
**When** Bias diagnostic을 렌더링하면
**Then** 숫자 4개가 `0`으로 표시되지 않고 "이 날짜의 편향 데이터가 없습니다"와 같은 명시적 빈 상태로 표시되어, 실제 편향이 0이라는 오해를 주지 않는다(FR-4/FR-7이 지켜온 "미수집과 실제 0을 구분한다" 원칙과 동일하게 적용).

### Story 5.14: 원천별 분리 조회 필터 UI

As a Neo,
I want 성과 지표를 원천(t1859/t1852/t1856)별로도 분리해 볼 수 있기를,
So that 폴백 데이터가 지표를 왜곡하는지 확인할 수 있다.

**Acceptance Criteria:**

**Given** `/tracking` 화면에서 원천 필터를 적용하는 경우
**When** Story 5.6의 원천별 view를 조회하면
**Then** 선택한 원천 기준으로 승률·PF·편향 지표가 분리되어 표시된다.

**Given** 필터를 초기화하는 경우
**When** 사용자가 조작하면
**Then** 전체(모든 원천 통합) 뷰로 되돌아간다.

**Given** 두 원천을 혼합한 지표를 보는 경우
**When** 화면을 확인하면
**Then** 혼합 지표임이 화면에서 구분 표기된다(FR-1a).
