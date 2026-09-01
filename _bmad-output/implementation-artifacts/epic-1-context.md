# Epic 1 Context: 배치 자동화 인프라 & 오늘의 후보 모집단

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

매 거래일마다 후보 모집단이 자동(및 수동)으로 갱신되고, Neo가 배치의 성공/실패/신선도를 항상 확인할 수 있으며, 시스템이 실제로 배포·백업되어 운영 가능한 상태를 만든다. 이 에픽은 이후 모든 에픽이 단지 확장만 하면 되는 완전한 배치 계약(5개 stage 키를 포함한 `stage_status`, outcome 확장점을 포함한 `publish_attempt` 트랜잭션 골격, TR-agnostic LS adapter client)을 세운다. 지금은 `candidates` stage만 필수이며, 후보 모집단 갱신(FR1/FR1a/FR2)과 스케줄·수동 실행 및 상태·신선도 표시(FR6/FR6a)가 이 에픽의 범위다.

## Stories

- Story 1.1: 프로젝트 스캐폴딩 & 개발 환경 고정
- Story 1.2: 거래 캘린더 확보
- Story 1.3: 배치 실행 계보 상태머신
- Story 1.4: LS OpenAPI 공통 클라이언트
- Story 1.5: 후보 모집단 자동 갱신
- Story 1.6: 후보 모집단 대체 경로 폴백
- Story 1.7: 스케줄 자동 배치 실행
- Story 1.8: 대시보드 스냅샷 조회 API
- Story 1.9: 오늘의 후보 화면 뼈대 & 배치 이력 화면
- Story 1.10: 인증 & 수동 트리거
- Story 1.11: 호스팅 배포 파이프라인
- Story 1.12: 백업 & 복원 검증

## Requirements & Constraints

- 후보 모집단은 매 거래일 개장 전/장중 30분/종가 확정 스케줄로 갱신되며, 휴장일에는 읽기 전용으로 no-op 조기 종료한다.
- t1859 조건검색식 실패 시 t1852/t1856 경로로 자동 폴백하고, 원천 구분과 기여도(weight 합계 1)를 보존한다.
- 후보 모집단 상한은 150종목(거래대금 내림차순·종목코드 오름차순 절단)이며, 절단·입력 해시·원본/제외 수를 배치에 기록해 기회 누락이 조용히 사라지지 않게 한다.
- 배치는 lease·fence를 가진 멱등 상태머신으로 관리되어 중첩 실행·stale worker가 데이터를 덮지 않고 재시도 이력이 보존된다.
- 스케줄과 수동 트리거를 구분 기록하며, 배치 상태·실행 시각·트리거·미처리 항목 수를 대시보드 상단에 항상 표시한다.
- 파이프라인은 단계별 부분 커밋을 허용하되 `partial`/`failed`는 완전 발행 후보가 아니며, 실패 단계가 이전 단계의 유효 데이터를 덮어쓰지 않는다.
- GitHub Actions의 `concurrency.group`은 보조 수단일 뿐, DB-level fence가 동시 실행 권위다.
- 무료 운영 제약: Next.js(웹)+Python(GitHub Actions)+Supabase 무료 플랜만 사용하며 유료 서비스 의존 금지. 리포지토리는 public 운영으로 GitHub Actions 무제한을 확보하고, 민감 정보는 GitHub Secrets로 분리한다.
- 호스팅은 Vercel Hobby(2026-09-01 결정)로 고정하고, 구현 시 contract smoke test로 한도 근접 상태의 신선도 표시 비혼동을 검증한다.
- DB 계약은 forward-only expand-migrate-contract: Supabase CLI 단일 timestamp migration이 권위이며, CI가 clean reset, N/N-1 호환성, generated types, SQL fixture parity를 게이트로 검증한다.
- 개발/운영 데이터 경계 분리: 로컬·CI는 fixture·local test DB만, production은 default branch trusted workflow만(PR/fork에 secret 미제공).
- 백업은 6시간마다 암호화 `pg_dump`를 14일 보관하고 분기 1회 복원 검증하며(RPO 6h/RTO 8h), 백업 실패는 능동 알림. 목표 미달 시 production release 차단.

## Technical Decisions

- 구조 시드: Python 3.12.14/pandas 3.0.5/NumPy 2.5.2/HTTPX 0.28.1/PyArrow 25.0.1, Node.js 24.20.0/Next.js 16.3.3/React 19.2.8/TS 5.9.3/@supabase/supabase-js 2.112.4/@supabase/ssr 0.12.4/Playwright 1.62.1, GitHub Actions `ubuntu-24.04`. 기존 `backtest/` 커널은 로직 변경 없이 이식하되 재작성하지 않으며, 이식 후 기존 전체 테스트가 통과해야 한다(AD-5 golden parity는 Epic 2 Story 2.4의 단일 권위).
- 레이아웃: `apps/web`(Next App Router), `apps/batch`(Python orchestrator), `packages/domain`(순수 규칙), `packages/read-model`(생성 DB 타입), `backtest/`, `infra/supabase/migrations/`, `.github/workflows/`, `tests/fixtures/`. `apps/*`만 외부 I/O·프레임워크 소유, domain은 순수 계약만 노출.
- Supabase가 운영 공유 데이터의 단일 소유자: 모든 배치 파생행은 attempt_run_id lineage를 가지며, 웹은 승인된 view/RPC만 읽는다.
- 상태머신: `logical_runs`(active/canonical_success/current_complete/latest_partial)와 `runs`(attempt 단위, fence/lease, `stage_status` 5개 키 `candidates/tags/supply_3day/market_supply/outcome_tracking`, 각 `pending|running|success|failed|partial`). `start_attempt` RPC가 logical row를 잠그고 새 run_id·attempt_no·fence·lease 발급. reaper의 `ready_to_publish`는 crash 구출용 salvage일 뿐, 완전 발행은 `publish_attempt(run_id, fence_token)`가 serializable transaction 안에서 필수 stage 전부 `success`를 재검증하며(AD-20), Epic 1에는 `candidates`만 필수. stage verifier registry(`stage_registry.py`)가 확장 지점이며 Epic 2/3/4가 자기 stage를 등록한다.
- 거래 시간 의미론: 저장/API는 UTC timestamptz, 거래일·표시는 Asia/Seoul. `trading_calendar`가 D-2/D-1/D0 소유, 조회 실패는 `CALENDAR_UNAVAILABLE`(휴장일 아님).
- LS 공통 클라이언트: TR별 token bucket(개인 1건/초), bounded retry + `Retry-After` 파싱, 범용(TR-agnostic) 인터페이스로 이후 에픽의 신규 TR 추가 시 재설계 불필요. 교차 병렬화는 실측 검증 전까지 비활성.
- 후보 저장: `candidates`(candidate_id attempt-scoped, UNIQUE(ticker, trading_day, attempt_run_id)) + `candidate_source_contrib`(source/contribution_weight). `candidates.source` 컬럼은 두지 않는다(AD-21). 절단 완료 후 저장 건수와 반환 건수 대조는 `truncated_count`로 설명.
- 스냅샷: `get_dashboard_snapshot()`이 `complete_snapshot`/`latest_attempt`/`available_partial_sections`/`missing_sections`/`unprocessed_items`/`no_snapshot`을 분리 반환. Epic 1에는 `candidates` section만 구현(나머지는 후속 에픽까지 항상 `missing_sections`), section 하나는 단일 run_id에서만 읽는다.
- Dispatch 멱등화: `dispatch_request`+`dispatch_outbox`(queued→accepted→started→completed|failed|dead_letter), `FOR UPDATE SKIP LOCKED`+만료 lease, `pg_cron` 1분 durable fallback. 같은 idempotency key+hash는 replay, 다른 hash는 409. active attempt 존재 시 409. 브라우저는 publishable key+RLS SELECT만, dispatch는 server-only + JWKS/CSRF/rate limit 검증, `NEXT_PUBLIC_*`에 secret 금지.
- 인증: Supabase Auth email OTP/magic link 단일 운영자 세션 + server-side subject allowlist. cron은 전부 UTC로 기술하고 KST 환산 주석 병기. 백업은 `age` 공개키 암호화 후 GitHub Actions artifact로 보관.

## UX & Interaction Patterns

- App shell: 좌측 240px 고정 내비(오늘의 후보/성과 검증/배치 이력), 활성 항목 골드 텍스트+인셋, `<768px`에서 사이드바 sheet(햄버거 메뉴 금지).
- Data trust bar: 최신 배치 상태(성공/부분성공/실패/휴장일 스킵)·KST 시각·트리거·신선도(60분 이상 stale) 표시, 실패/미갱신 시 수동 실행 단일 버튼(중복 클릭 방지·실행 중 상태).
- `/`(오늘의 후보)와 `/runs`(배치 이력)를 별도 라우트로 분리. `/runs`는 attempt의 trigger/status/stage_status/skip_reason/truncated_count/unprocessed_count를 시간 역순 표시.
- Epic 1 시점 태깅 없음: `/`에서 후보 없으면 "오늘 태깅된 후보가 없습니다."+"조건검색 결과/전략 시그널 기준" 문구(배치 실패 시 빈 상태보다 실패 상태 우선), 후보 모집단 건수는 신뢰도 참고용으로 노출 가능.
- 상태 처리: 로딩 시 실제 높이의 skeleton 3~6개(전체 검정 화면 금지), 실패 시 stale로 유지+수동 실행, 휴장일·부분성공·실패·stale·폴백 원천을 색이 아닌 문장+시각으로 비차단 토스트/notice.
- 접근성(WCAG 2.2 AA): 자동 배치 실패/부분성공/stale/폴백을 `aria-live="polite"`로 알리고 포커스 강제 이동 금지. 키보드 `j/k` 후보 이동, `Enter` 패널 토글, `/` 검색, `r` 새로고침, `g t`/`g v` 내비, `Esc` 닫기 — 모든 액션은 DOM 상주/포커스로 노출(hover 전용 금지).
- 디자인 토큰: DESIGN.md의 colors/surface/ink/accent/positive/negative/caution/informational, Pretendard 타이포그래피 스케일, rounded(sm/md/lg/full), spacing(1~8)을 코드 토큰으로 구현. gold는 브랜드·선택 상태에만, 배치 실패·위험은 색상 단독으로 전달하지 않는다.

## Cross-Story Dependencies

- Story 1.3의 stage-write RPC·`publish_attempt`·fence가 1.5/1.6(후보 쓰기)과 1.7/1.10(실행)의 기반이며, dispatch 거부(409)는 1.3의 fence 모델과 일관해야 한다.
- Story 1.8의 스냅샷 API는 1.3에 정의된 logical_runs/runs/candidates(1.5)를 소비하고, 1.9 화면은 이를 호출한다.
- Story 1.2의 `trading_calendar`는 1.7 스케줄의 휴장일 판정에 의존된다.
- 1.3의 확장 지점(5개 stage 키 + stage verifier registry)과 1.4의 TR-agnostic 클라이언트는 Epic 2/3/4가 확장만 하면 되는 계약이며, 이 에픽에서 스캐폴딩됨.
- Story 1.11은 1.9/1.8 결과물을 배포해 smoke test하며, 1.12 백업은 production 데이터 보호 전제로 운영 출시를 뒷받침한다.
