# Rubric Review — wave-double V1 Architecture Spine

- 대상: `ARCHITECTURE-SPINE.md`
- 기준: BMad good-spine checklist
- 검토일: 2026-09-01
- 입력 대조: `SPEC.md` 및 companions, PRD, `DESIGN.md`, `EXPERIENCE.md`, 현재 `backtest/` 코드

## Gate verdict

**FAIL — 구현 착수 불가.** CAP-1~7의 큰 경계와 데이터 소유권은 폭넓게 다뤘지만, 현재 규칙을 그대로 구현하면 장기 outcome/태깅 이력이 삭제되고, 핵심 DDL이 PostgreSQL에서 실패하며, 무료 운영 제약과 복구 계약이 동시에 성립하지 않는다. 또한 부분성공 표시와 이력 부족 후보 처리에서 상위 요구사항을 직접 위반한다.

## Good-spine checklist

| 기준 | 판정 | 근거 |
| --- | --- | --- |
| 실제 분기점을 빠짐없이 고정 | **FAIL** | canonical 재선정 시점/권한, partial read 경로, 단일 사용자 인증 세션의 생성·갱신 경계가 고정되지 않았다. |
| 모든 Rule이 강제 가능하며 Prevents를 실제로 달성 | **FAIL** | AD-19 partial index는 PostgreSQL 문법상 생성 불가하며, `REFERENCES candidates(source)`도 참조 대상이 unique가 아니어서 생성 불가다. AD-18은 GitHub가 반환하지 않는 dispatch ID를 계약으로 사용한다. |
| Deferred가 하위 구현의 비호환을 허용하지 않음 | **PARTIAL** | 호스팅 제공자·TR 병렬화·보존기간은 revisit 조건이 있다. 그러나 Node 20 및 Next 14를 그대로 묶은 채 제공자 선택만 미루므로 현재 지원성 판단이 안전하게 deferred되지 않았다. |
| 명명 기술이 현재 검증됨 | **FAIL** | Node 20은 2026-03-24 EOL이고 Next.js 14.2.15는 현재 지원 계열이 아니다. Supabase Free에는 자동 백업/PITR이 없다. |
| brownfield를 모순 없이 ratify | **PARTIAL** | 기존 `backtest` 재사용 방향은 맞지만, 운영에서 호출할 오류 보존형 entrypoint가 정해지지 않았다. 현재 `build_signals()`는 broad exception을 무신호로 삼는다. |
| SPEC capabilities를 모두 커버 | **FAIL** | 표의 CAP 매핑은 전부 있으나, FR-3a의 종목별 제외를 전체 tagging 차단으로 바꾸고, FR-6a/NFR-5의 partial 데이터 노출을 선택사항으로 남겼다. |
| inherited spine과 충돌 없음 | **N/A** | 상위 spine이 선언되지 않았다. |
| 소유 altitude의 전 차원을 결정/defer/open | **FAIL** | 운영 복구를 다루지만 무료 플랜과 양립하는 백업 저장소·복원 권한이 없다. Supabase JWT를 요구하면서도 Neo 세션을 누가 어떻게 발급하는지 침묵한다. |

## Findings

### R-01 — CRITICAL — canonical publish가 장기 이력을 삭제한다

- **위치:** `ARCHITECTURE-SPINE.md:135-146`(AD-9), `:231-240`(AD-19)
- **근거:** AD-9는 `candidate_outcome`을 현재 projection, `outcome_observations`를 append-only 원장으로 두고 terminal 결과 불변을 선언한다. 반면 AD-19는 같은 logical run의 이전 attempt에 연결된 `candidate_tags`, `candidate_outcome`, `bias_metrics`, `candidate_source_contrib`를 publish 때 삭제한다. PRD FR-3b는 `run_id`, `tagged_at` 단위 태깅 변화 이력 보존을 요구하고(`prd.md:165-173`), FR-10은 임의 거래일 편향 조회를 요구한다(`:299-308`). NFR-5는 실패 단계가 이전 유효 데이터를 삭제하지 못하게 한다(`:324`). 이후 성공 attempt가 이미 publish된 성공 attempt를 canonical에서 밀어낼 수 있는지도 정의되지 않아, 두 구현이 서로 다른 데이터를 보존할 수 있다.
- **영향:** 성과 분모와 장중 시그널 변화 이력이 재시도 시 사라지고, 결과 선택적 제외를 막으려던 CAP-7 방벽이 무너진다.
- **명확한 수정안:** immutable event/history 테이블은 절대 삭제하지 않는다. attempt별 행에 `attempt_run_id`와 `is_canonical` 또는 canonical view 조인 조건을 두고, `logical_runs.canonical_attempt_run_id`만 원자적으로 교체한다. `candidate_outcome` 생성은 최초 canonical close publish 한 번으로 제한하고, 이후 attempt는 동일 logical run의 outcome을 재생성하지 않는다. canonical 선택 권한과 시점은 “orchestrator의 success commit transaction” 하나로 고정한다.

### R-02 — CRITICAL — AD-17은 무료 운영 제약과 양립하지 않는다

- **위치:** `ARCHITECTURE-SPINE.md:207-218`(AD-17), `:319`, PRD `:312-316`(NFR-1/2)
- **근거:** AD-17은 Supabase PITR과 프로덕션 PITR→staging 분기별 복원 드릴을 사실상 필수 흐름으로 둔다. 그러나 현재 Supabase Free는 자동 백업과 PITR을 제공하지 않으며, PITR은 유료 플랜/add-on이다. 공식 문서는 Free 프로젝트에 정기 `db dump`와 off-site backup을 권고한다. AD-17의 “동등한 self-managed backup” 예외는 뒤의 자동화 절차에 반영되지 않아, 구현자는 유료 PITR과 무료 dump 중 어느 계약을 따라야 할지 갈린다.
- **영향:** “전액 무료 운영”을 지키면 RPO≤1h/PITR drill을 구현할 수 없고, AD-17을 지키면 제품의 상위 비용 제약을 위반한다.
- **명확한 수정안:** V1 무료 경로를 하나로 고정한다. 예: GitHub Actions가 매시간 `supabase db dump`/`pg_dump`를 암호화해 별도 무료 저장소에 보관하고, 정해진 retention과 분기별 scratch project/local Postgres restore test를 수행한다. 실제 측정 가능한 RPO/RTO로 완화한다. 또는 PITR이 필수라면 PRD NFR-1을 변경하고 월 비용을 승인된 제약으로 올린다. 두 경로를 `또는`으로 남기지 않는다.
- **외부 확인:** [Supabase pricing](https://supabase.com/pricing), [Supabase database backups](https://supabase.com/docs/guides/platform/backups)

### R-03 — HIGH — AD-16/19의 provenance DDL은 생성 불가능하고 서로 모순된다

- **위치:** `ARCHITECTURE-SPINE.md:198-205`(AD-16), `:231-240`(AD-19)
- **근거:** AD-19의 partial unique index predicate는 `WHERE contrib_run_id IN (SELECT ...)` 서브쿼리를 포함한다. PostgreSQL은 index predicate의 subquery를 금지한다. AD-16의 `source TEXT NOT NULL REFERENCES candidates(source)`도 `candidates.source`가 unique key가 아니므로 FK 대상이 될 수 없다. 동시에 AD-16은 source별 여러 정규화 행을 정의하지만 AD-19는 candidate당 단일 행과 JSONB 배열을 강제한다. `candidate_outcome.source_jsonb`까지 더해져 source 권위가 세 군데다.
- **영향:** migration이 즉시 실패하거나, 구현팀별로 JSONB/행 모델 중 하나를 임의 채택해 원천별 승률·PF가 달라진다.
- **명확한 수정안:** provenance의 단일 권위를 정규화 테이블로 고정한다. 예: `candidate_source_contrib(candidate_id, source, contribution_weight, contrib_run_id, PRIMARY KEY(candidate_id, source, contrib_run_id))`, `source`는 enum/check constraint로 검증하고 후보 연계는 `candidate_id` FK로 한다. canonical 여부는 `logical_runs`와 join하는 view로 도출하며 subquery partial index를 제거한다. `candidate_outcome.source_jsonb`는 삭제하거나 읽기 캐시로 명시하고 동기화 권위를 하나로 둔다.
- **외부 확인:** [PostgreSQL CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)

### R-04 — HIGH — 120거래일 이력 부족 처리 규칙이 FR-3a와 반대다

- **위치:** `ARCHITECTURE-SPINE.md:96-106`(AD-5), PRD `:153-164`(FR-3a)
- **근거:** AD-5는 대상 종목 하나라도 120거래일 미만이면 stage error로 승격해 tagging 전체를 막는다. FR-3a는 이력 부족 후보만 태깅 대상에서 제외하고 그 상태를 후보에 기록하라고 요구한다.
- **영향:** 신규 상장 종목 하나가 150종목 전체 배치를 partial/failed로 만들 수 있고, 두 하위 구현이 전체 실패와 종목별 제외로 갈린다.
- **명확한 수정안:** `ohlcv_cache`는 종목별 readiness 결과를 낸다. API/저장 실패는 retryable stage error로, 정상적인 120일 미만 상장은 `INELIGIBLE_INSUFFICIENT_HISTORY`로 기록하고 해당 종목만 tagging에서 제외한다. stage success 조건은 모든 후보가 `READY | INELIGIBLE` 중 하나로 종결된 경우로 정의한다.

### R-05 — HIGH — partial 성공 데이터의 읽기 계약이 필수 요구사항을 충족하지 않는다

- **위치:** `ARCHITECTURE-SPINE.md:167-184`(AD-13), PRD `:226-236`(FR-6a), `:324`(NFR-5), `EXPERIENCE.md`의 State Patterns/부분성공
- **근거:** AD-13은 read view가 마지막 complete run만 읽게 하고 partial preview는 “필요하다면” 별도 RPC로 둔다. 하지만 FR-6a는 부분성공 시 수집된 후보를 표시하고 미수집 경고·목록을 함께 보여야 한다고 강제한다. UX도 같은 동작을 명시한다.
- **영향:** AD-13만 준수한 구현은 stale complete 데이터만 보여주어 CAP-3/FR-6a를 위반하거나, 팀별로 partial/complete 합성 방식이 달라진다.
- **명확한 수정안:** partial read contract를 필수로 승격한다. `get_dashboard_snapshot()`이 `complete_snapshot`, `latest_attempt`, `available_partial_sections`, `missing_sections`, `unprocessed_items`를 분리 반환하고 절대 서로 다른 run의 row를 같은 section 안에서 join하지 않도록 고정한다. 화면별 어떤 section을 partial에서 보여줄지 표로 정의한다.

### R-06 — HIGH — AD-18은 존재하지 않는 `github_dispatch_id`를 replay 계약으로 사용한다

- **위치:** `ARCHITECTURE-SPINE.md:220-229`(AD-18)
- **근거:** GitHub의 “Create a workflow dispatch event” 성공 응답은 `204 No Content`이며 run/dispatch ID를 반환하지 않는다. 그런데 AD-18은 성공 시 `github_dispatch_id`를 저장·반환하고, reconciler가 GitHub API로 “실제 dispatch 상태”를 조회하도록 한다. outbox worker가 dispatch의 유일한 주체인지 Next route가 먼저 호출하고 reconciler가 보정하는지도 불명확하다.
- **영향:** 동일 요청 replay에 돌려줄 안정 ID가 없고, 204 이후 workflow 미시작/지연/중복을 안전하게 구분할 수 없다.
- **명확한 수정안:** API는 자체 `dispatch_request_id`를 먼저 생성하고 이를 workflow input으로 전달한다. outbox worker만 GitHub API를 호출하며, workflow 첫 단계가 같은 ID로 `run_attempts`를 idempotent upsert한다. 상태는 `queued → accepted_204 → started(run_id) → completed`로 고정하고, reconciler는 GitHub run name/input 또는 DB heartbeat를 correlation한다. `github_dispatch_id` 필드는 제거한다.
- **외부 확인:** [GitHub workflow dispatch REST API](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)

### R-07 — HIGH — Stack seed가 2026-09 현재 지원 상태를 위반한다

- **위치:** `ARCHITECTURE-SPINE.md:258-278`(Stack), `:336-345`(hosting Deferred)
- **근거:** Node.js 20은 2026-03-24 EOL인데 `20.18.0 LTS`로 묶였다. Next.js 14.2.15 역시 현재 지원 계열이 아니며 공식 공지는 16.2.11을 Active LTS, 15.5.21을 Maintenance LTS로 안내한다. 현재 repo에는 `package.json`, lockfile, `pyproject.toml`, `uv.lock`이 없어 brownfield 호환성 근거도 없다.
- **영향:** 새 웹 앱을 시작부터 보안 패치가 끝난 런타임/프레임워크에 고정하고, 호스팅 평가표도 EOL Node 20 지원을 필수로 잘못 평가한다.
- **명확한 수정안:** 구현 직전 starter spike로 Node 24 LTS + Next.js 16 Active LTS(또는 명시적 사유가 있는 Next 15 Maintenance LTS)를 검증해 exact patch를 lockfile에 고정한다. React/TypeScript/Supabase SDK도 같은 날 호환 조합을 설치·빌드한 결과를 seed의 근거로 삼는다. 표에는 lifecycle과 재검토 날짜를 추가한다.
- **외부 확인:** [Node.js releases](https://nodejs.org/en/about/previous-releases), [Next.js release/security notices](https://nextjs.org/blog)

### R-08 — MEDIUM — 기존 전략 커널의 안정된 운영 entrypoint가 없다

- **위치:** `ARCHITECTURE-SPINE.md:96-109`(AD-5), `backtest/indicator_opt/combine_strategies.py:31-54`, `backtest/indicator_opt/screen_abc.py:18-19`
- **근거:** AD-5는 `backtest.indicator_opt.*`의 함수·상수를 호출하고 broad exception을 구조화 오류로 승격하라고 하지만, 실제 공용 조합 함수 `build_signals()`는 전략별 `except Exception: pass` 후 False mask를 반환한다. `screen_abc.py`도 이 함수를 그대로 import한다. “지표 로직 무변경”과 “broad exception 금지”를 동시에 만족하는 호출 경계가 정해지지 않았다.
- **영향:** 한 팀은 기존 `build_signals()`를 재사용해 오류를 무신호로 숨기고, 다른 팀은 내부 private 함수들을 다시 조합해 전략 로직이 분기할 수 있다.
- **명확한 수정안:** `backtest.strategy_api.compute_abc(df) -> StrategyResult` 같은 단일 public API를 brownfield에 추가한다. 기존 신호 함수/상수는 그대로 호출하되 오류를 종목·전략별 typed error로 반환하고, backtest CLI와 운영 tagging이 모두 이 API를 사용하게 한다. 골든 픽스처는 이 public API를 대상으로 한다.

### R-09 — MEDIUM — `restore_epoch` 규칙은 스키마와 PITR 의미론이 완결되지 않았다

- **위치:** `ARCHITECTURE-SPINE.md:207-218`(AD-17), `:198-205`(AD-16)
- **근거:** AD-17은 `candidate_tags`, `candidate_outcome`, `bias_metrics`, `candidate_source_contrib` 전체 epoch 증가를 요구하지만 명시 스키마에는 일부만 존재한다. `MAX(restore_epoch)`를 `candidate_source_contrib` 한 테이블에서 구하면 그 테이블이 비어 있거나 다른 테이블 적재가 지연될 때 유효 데이터가 사라진다. PITR은 DB 자체를 과거로 되돌리므로 DB 내부 epoch만으로 “복원 횟수”를 안정적으로 기억할 수도 없다.
- **영향:** 복원 직후 metrics가 0건이 되거나 서로 다른 epoch 행이 중복/누락될 수 있다.
- **명확한 수정안:** 무료 백업 경로 결정 후 외부 restore manifest가 발급한 `restore_id`를 DB 복원 완료 시 한 번 기록하고, event 원장의 restore 이후 재적재분만 그 ID를 참조하게 한다. 정상 이력 행을 일괄 UPDATE하지 않는다. metrics는 복원 세대가 아니라 canonical logical identity와 supersession/correction event로 유효 행을 선택한다.

### R-10 — MEDIUM — 단일 사용자 인증 경계가 상위 범위와 연결되지 않는다

- **위치:** `ARCHITECTURE-SPINE.md:123-127`(AD-7), PRD `:363-370`, `EXPERIENCE.md` Foundation
- **근거:** PRD/UX는 외부 사용자·인증·계정 시스템을 V1 비대상으로 둔다. AD-7은 Supabase JWT와 allowlisted `sub`를 요구하지만 Neo의 세션/JWT를 누가 발급하고 만료·갱신하며, 로그인 화면이 있는지 정하지 않는다.
- **영향:** 웹과 dispatch route가 서로 다른 인증 가정을 선택하거나, 수동 실행이 실제로는 사용할 수 없게 된다.
- **명확한 수정안:** “외부 사용자 관리 없음”과 “단일 운영자 인증 있음”을 분리해 명시한다. Supabase Auth magic link/OTP 등 한 가지 흐름, 고정 allowlist 저장 위치, 세션 갱신, 최초 bootstrap, 로그아웃/토큰 폐기를 architecture rule로 고정하고 UX에 최소 로그인 surface를 반영한다. 또는 인증 UI를 정말 제외한다면 서버 배포 계층의 단일 secret 접근 방식으로 바꾸고 CSRF/JWT 계약을 재작성한다.

### R-11 — LOW — spine이 seed와 구현 설계를 과도하게 혼합한다

- **위치:** AD-3/6/17/18/19의 상세 DDL·cron·복구 절차, `Structural Seed`
- **근거:** 문서는 19개 AD와 구체 DDL/환경변수/cron/HTTP retry 알고리즘까지 고정하지만, 서로 중복되는 소유권(AD-6/12), provenance 표현(AD-9/16/19), 복구 세부(AD-17)가 오히려 모순을 만들었다. 현재 brownfield에는 웹/배치/infra scaffold가 없어 이 세부를 ratify할 코드도 없다.
- **영향:** 하위 story가 코드에서 자연스럽게 정해야 할 shape를 오래된 문서가 소유하고, 변경 때 여러 AD를 동시에 수정해야 한다.
- **명확한 수정안:** spine에는 publication authority, history immutability, source provenance authority, partial read contract, 무료 backup strategy처럼 진짜 비호환 분기만 남긴다. 테이블 전체 shape, retry 수치, cron 구현, restore runbook은 schema/API/runbook companion으로 이동하고 AD에서는 그 계약 ID만 참조한다.

## 수정 우선순위

1. **R-01~R-03 해결 전 DB migration/story 작성 금지.** 보존·canonical·provenance 권위를 먼저 하나로 만든다.
2. **R-02/R-07을 함께 결정.** 무료 운영을 유지할지 지원되는 유료 운영 기능을 채택할지 상위 제약을 재승인한다.
3. **R-04/R-05로 SPEC 정합 회복.** 종목별 eligibility와 partial snapshot API를 강제 계약으로 올린다.
4. **R-06/R-08/R-10으로 외부 seam을 고정.** dispatch correlation, 전략 public API, 단일 운영자 인증을 구현 단위가 임의 선택하지 못하게 한다.
5. 수정 후 lint + rubric + adversarial gate를 다시 실행한다.

## 확인된 강점

- hexagonal modular monolith + staged batch pipeline이라는 paradigm은 웹·배치·전략 커널의 의존 방향을 이해시키는 데 적합하다.
- UTC/KST·거래일, LS TR 예산, snapshot publication, 금융 지표의 SQL read model 소유권은 실제 분기점을 겨냥한다.
- CAP-1~7 매핑과 `Binds / Prevents / Rule` 형식은 추적성이 좋다. 위 충돌을 제거하면 유효한 spine으로 축약 가능하다.
