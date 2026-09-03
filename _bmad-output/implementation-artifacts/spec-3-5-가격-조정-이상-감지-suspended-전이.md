---
title: 'Story 3.5: 가격 조정 이상 감지 & SUSPENDED 전이'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: '2cba17ade74c8c62853e3f1a5f2e95e04fb88865'
baseline_commit: '2cba17ade74c8c62853e3f1a5f2e95e04fb88865'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      emit_open_command(Story 3.2)의 재진입 방지 가드가 status='OPEN'만 확인해,
      SUSPENDED 상태인 (ticker,strategy)를 나중에 재태깅하면 새 candidate_outcome
      행이 중복 생성될 수 있다.
    evidence: |-
      candidate_outcome_one_open_per_ticker_strategy_idx는 status='OPEN'에만 걸린
      partial unique index이고 (ticker,strategy,entry_date) unique 제약도 entry_date가
      다르면 막지 못한다. emit_open_command의 ALREADY_OPEN 체크(202609031501)도
      status='OPEN'만 조회한다. SUSPENDED는 이 스토리(3.5)가 처음 실제로 생성 가능하게
      만든 상태라 이전에는 도달 불가능했다(blind-hunter 리뷰 발견, 2026-09-03 review pass에서
      확인). epics.md Story 3.1 AC는 OPEN 중복 방지만 명시하고 SUSPENDED 재진입은 다루지
      않아 이 스토리의 intent-contract만으로는 해결할 수 없는 원 스펙(epics.md)의 공백이다.
    location: >-
      infra/supabase/migrations/202609031501_fix_emit_open_command_review_patch.sql:57
    severity: medium
  - summary: >-
      daily_ohlcv.close에 양수 제약이 없어, 전일 종가가 0이면 갭 안전망 계산이
      조용히 건너뛰어져(false negative) 이상 감지를 놓칠 수 있다.
    evidence: |-
      202609021500_create_daily_ohlcv.sql의 close check 제약은 NaN/Infinity만
      배제하고 0/음수는 허용한다. 202609031800의 v_prev_close <> 0 가드는 나눗셈
      예외를 막기 위한 것이지만, pricechk도 없는 상태에서 전일 종가가 0이면 그 어떤
      경로로도 감지되지 않는다(blind-hunter 리뷰 발견, 2026-09-03 review pass).
      이 스키마 제약(Story 2.1 산출물)은 3.5가 만든 것이 아니라 이미 존재하던 공백이다.
    location: >-
      infra/supabase/migrations/202609031800_detect_price_adjustment_suspension.sql:208
    severity: low
---

<intent-contract>

## Intent

**Problem:** OPEN 상태 outcome의 티커에 액면분할·병합 등 가격 조정 이벤트가 발생해도 이를 감지·전이하는 로직이 전혀 없다. Story 3.6의 TP/SL 판정이 이보다 먼저(또는 동시에) 배포되면 분할 미보정 갭을 진입가 대비 저가/고가 급변으로 오판정(즉시 SL 오판정 등, NFR-9)할 위험이 있다.
**Approach:** `publish_attempt`를 다시 `create or replace`해, close 분기의 관찰 수집 루프(Story 3.4) 다음에 SUSPENDED 감지 루프를 추가한다. `status='OPEN'`인 `candidate_outcome`마다 오늘 거래일 `daily_ohlcv.pricechk`(1차, 갭 무관) 또는 전일 대비 종가 갭 절대값 30% 초과(2차 안전망)를 확인하고, 감지되면 idempotent하게 `outcome_events`에 `command_type='SUSPENDED'` 행을 append하고 `candidate_outcome.status`를 `'SUSPENDED'`로 전이한다. 자동 TP/SL 판정은 이 스토리에서 수행하지 않는다(3.6 범위). SUSPENDED에서 정상 흐름으로의 복귀는 Story 3.8의 correction event 몫이므로, 이 스토리는 OPEN→SUSPENDED 단방향 전이만 구현한다.

## Boundaries & Constraints

**Always:** 감지는 `status='OPEN'`인 `candidate_outcome` 행만 대상으로 하며(이미 `SUSPENDED`/terminal인 행은 자연히 재감지 대상에서 제외), `daily_ohlcv`에서 오늘 거래일(`logical_row.trading_day`) 행의 `pricechk is not null and pricechk <> 0`이면 갭 크기와 무관하게 무조건 전이한다(1차, LS 원천 진실). `pricechk`가 없으면 전일(같은 티커의 `daily_ohlcv`에서 오늘보다 이전 최신 거래일) 종가 대비 `abs((오늘 close - 전일 close) / 전일 close) > 0.30`이면 전이한다(2차 안전망). 임계값 `0.30`은 한 곳(신규 SQL 함수, 아래 참조)에 상수로 정의해 조정 가능하게 한다. 전이는 idempotent해야 하며, `outcome_events(logical_run_key, ticker, strategy, command_type)` unique index(Story 3.2 `emit_open_command` 선례와 동일 컨벤션)를 `command_type='SUSPENDED'`에도 적용해 같은 attempt 재시도가 중복 행을 만들지 않게 한다(이미 존재하면 재감지·재전이 skip). `publish_attempt`의 반환 jsonb에 이번 attempt에서 새로 SUSPENDED 전이된 outcome 목록(`ticker`, `strategy`, `outcome_id`, `pricechk` 여부, `gap_pct`)을 `suspended_transitions` 키로 노출한다(향후 알림 소비자가 재조회 없이 쓸 수 있도록, Design Notes 참조).

**Never:** TP/SL/TIMEOUT 판정을 구현하지 않는다(Story 3.6/3.7). `SUSPENDED`에서 정상 상태로의 복귀나 `DELISTED` 종결을 구현하지 않는다(Story 3.8/3.9 범위 — AC의 "정상 복귀" 절은 이 스토리에서 미구현). 컷오프(`traded_days_since_entry`) 계산 로직을 변경하지 않는다(Story 3.7 범위 — SUSPENDED가 컷오프에서 제외되는 산식 자체는 3.7이 소유). 실제 GitHub Issue 생성 API 호출이나 이를 위한 Python/워크플로 배선을 구현하지 않는다 — `publish_attempt`(따라서 이 스토리의 SUSPENDED 감지 전체)는 `emit_open_command`/`record_outcome_observation`과 마찬가지로 아직 어떤 실제 배치 진입점에도 연결되지 않은 기존 gap(`deferred-work.md` epic-1 항목, spec-3-1~3-4에서 반복 확인됨)이며, 이 상태에서 알림 배선을 추가해도 실제로 트리거될 방법이 없어 검증 불가능한 죽은 코드가 된다. 이 gap은 `deferred-work.md`에 별도 기록한다(Tasks 참조). Story 2.2의 `AdjustmentFlag`/`update_existing_ticker_history`를 재사용하거나 호출하지 않는다 — 그 신호는 오늘의 후보 모집단 티커에만 한정되어(`run_scheduled_batch`가 `result.selection.candidates`만 전달) 이미 후보에서 이탈한 OPEN outcome 티커를 놓치므로, 이 스토리는 `candidate_outcome`의 모든 OPEN 티커를 대상으로 `daily_ohlcv`를 직접 재확인한다(Design Notes 참조). `emit_open_command`/`record_outcome_observation`의 로직·호출부를 수정하지 않는다 — 새 루프는 관찰 수집 루프 뒤에 추가만 한다. `runs.stage_status`에 새 stage key를 추가하지 않는다(기존 `outcome_tracking` 안에서 처리, Story 3.4와 동일 제약).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| pricechk 관측(갭 무관) | OPEN outcome 티커의 오늘 `daily_ohlcv.pricechk`가 0이 아님, 갭은 10%에 불과 | 갭 크기와 무관하게 `SUSPENDED`로 전이, `outcome_events`에 `command_type='SUSPENDED'` 1행, `candidate_outcome.status='SUSPENDED'` | 없음 |
| 갭 안전망(pricechk 없음) | `pricechk`가 null, 전일 대비 종가 갭 35% | `SUSPENDED`로 전이 | 없음 |
| 임계값 이하 정상 변동 | `pricechk`가 null, 전일 대비 종가 갭 12% | 전이 없음, `status='OPEN'` 유지, 관찰만 계속 축적(3.4) | 없음 |
| 이미 SUSPENDED | 대상 outcome의 `status`가 이미 `'SUSPENDED'` | 감지 루프 대상에서 제외(재전이·중복 이벤트 없음) | 없음 |
| 재시도(동일 attempt 재발행) | 이미 `(logical_run_key,ticker,strategy,'SUSPENDED')` 이벤트 존재 | 새 이벤트를 만들지 않고 재확인만, `publish_attempt`는 정상 커밋 | 없음 |
| 전일 daily_ohlcv 없음(신규 진입 첫날 등) | 오늘 `daily_ohlcv`는 있으나 그 이전 거래일 행이 없음 | 갭 계산을 건너뛰고 `pricechk`만으로 판정(갭 미달로 인한 오탐 없음) | 없음 |
| 오늘 daily_ohlcv 없음 | 3.4의 `MISSING_DAILY_OHLCV`와 동일 상황 | 이 outcome은 이번 감지 대상에서 자연 제외(관찰도 없으므로 판정 근거 자체가 없음) | 예외 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031700_record_close_batch_observations.sql` -- 현재 `publish_attempt`의 권위 있는 최신 정의(create or replace 대상 baseline). Story 3.4의 관찰 수집 루프(`record_outcome_observation` 호출부) 바로 뒤에 이번 SUSPENDED 감지 루프를 추가한다.
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql:10-11` -- `outcome_events(logical_run_key, ticker, strategy, command_type)` unique index 선례. `command_type='SUSPENDED'`도 같은 index가 이미 커버하므로(값만 다를 뿐 컬럼은 동일) 신규 index 불필요 -- 기존 index 재사용.
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql:16,21` -- `daily_ohlcv.pricechk`(nullable integer, Story 2.2가 채움)가 이 스토리의 1차 감지 신호 원천. 재조회 없이 이미 저장된 컬럼을 그대로 쓴다.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:40` -- `candidate_outcome.status` check 제약이 이미 `'SUSPENDED'`를 포함하므로 스키마 변경 불필요.
- `packages/domain/domain/ohlcv_cache.py:22-37` -- Story 2.2가 노출한 `AdjustmentFlag`(ticker/trading_day/pricechk/gap_pct). 이 스토리는 이를 재사용하지 않는다(Boundaries 참조 -- 오늘 후보 모집단으로 범위가 좁아 OPEN outcome 전체를 커버 못 함). 참고용으로만 남긴다.
- `apps/batch/scheduler.py:154-156` -- `update_existing_ticker_history`의 반환값이 현재 버려지고 있다는 확인(변경 대상 아님, 배치 배선은 기존 gap).
- `tests/sql/test_run_lineage.sql:117-280` (`close:2099-01-07`/`close:2099-01-10` 시나리오) -- 이번 스토리의 감지 시나리오를 자연스럽게 이어붙일 지점. 신규 티커(예: `ZZLIN8`/`ZZLIN9`)로 pricechk/갭/임계값 이하 케이스를 추가한다.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- 신규 항목 추가 대상(publish_attempt 미배선 상태에서 GitHub Issue 알림 배선이 불가능하다는 기록).

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609031800_detect_price_adjustment_suspension.sql` -- `public.price_adjustment_gap_threshold() returns numeric`(상수 `0.30` 반환, `security definer` 불필요 -- 순수 상수 함수) 신규 생성. `publish_attempt`를 `create or replace`해 close 분기의 관찰 수집 루프 뒤에, `status='OPEN'`인 `candidate_outcome`을 순회하며 오늘/전일 `daily_ohlcv` 조회 → pricechk/갭 판정 → 감지 시 `outcome_events` insert(`on conflict (logical_run_key,ticker,strategy,command_type) do nothing`) + `candidate_outcome.status='SUSPENDED'` update + 반환 jsonb `suspended_transitions` 배열에 누적하는 루프를 추가한다.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 7개 시나리오를 커버하는 fixture를 기존 close 시나리오에 추가(신규 SUSPENDED 케이스 각각에 대해 `outcome_events`/`candidate_outcome.status`/`publish_attempt` 반환 jsonb의 `suspended_transitions` assertion).
- `_bmad-output/implementation-artifacts/deferred-work.md` -- "Story 3.5 build verification" 섹션을 추가해, GitHub Issue 알림 배선이 `publish_attempt` 프로덕션 미배선 gap 해소 이후에나 가능하다는 점을 기록.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입 갱신 확인(신규 `price_adjustment_gap_threshold` RPC 항목 추가 예상, `publish_attempt` 시그니처는 불변).

**Acceptance Criteria:**
- Given OPEN 상태 outcome 티커의 오늘 거래일 `daily_ohlcv.pricechk`가 0이 아닌 경우, when `publish_attempt`가 실행되면, then 갭 크기와 무관하게 그 outcome이 `SUSPENDED`로 전이되고 `outcome_events`에 사유가 기록된다.
- Given `pricechk`가 없고 전일 종가 대비 갭이 ±30%를 초과하는 경우, when `publish_attempt`가 실행되면, then 해당 outcome이 `SUSPENDED`로 전이된다.
- Given `pricechk`가 없고 갭이 ±30% 이내인 경우, when 감지 루프가 이를 확인하면, then 전이가 발생하지 않고 outcome은 `OPEN`으로 남아 계속 관찰된다.
- Given 이미 `SUSPENDED`인 outcome이 있는 경우, when 다음 close 배치가 발행되면, then 그 outcome은 감지 대상에서 제외되어 중복 이벤트나 재전이가 발생하지 않는다.
- Given 이번 attempt에서 SUSPENDED로 신규 전이된 outcome이 있는 경우, when `publish_attempt`의 반환값을 확인하면, then `suspended_transitions` 배열에 해당 outcome의 ticker/strategy/사유가 노출된다.

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 1: (high 0high, medium 1medium, low 0low)
- defer: 2: (high 0high, medium 1medium, low 1low)
- dismissed:
  - 오늘 SUSPENDED 감지 시점보다 먼저 실행되는 관찰(3.4) 루프가 같은 거래일의 (조정으로 왜곡됐을 수 있는) 고가/저가/종가를 `outcome_observations`에 그대로 기록한다는 지적(blind-hunter) — Story 3.4가 이미 확립한 설계(SUSPENDED도 non-terminal이라 관찰 대상에서 제외하지 않음, 관찰은 감사 이력이지 판정이 아님)와 정합하며, 자동 TP/SL 판정(아직 존재하지 않는 3.6)이 이 관찰을 근거로 오판정할 위험은 3.6이 판정 시점의 `candidate_outcome.status`(이미 이 트랜잭션에서 SUSPENDED로 갱신됨)를 확인해야 할 3.6 자신의 책임이며, 이 스토리가 만든 결함이 아니다.
  - `publish_attempt` 반환 jsonb가 premarket/intraday에서도 항상 `suspended_transitions`(빈 배열)를 포함해 응답 스키마가 조용히 바뀐다는 지적(blind-hunter) — 추가적(additive) 필드라 기존 소비자가 읽던 키에 영향이 없고, 함수 자체 comment에 이미 문서화돼 있어 실제 소비자에게 해가 되는 결과가 없다.
  - SUSPENDED 이벤트 payload가 `entry_price`/오늘 종가를 담지 않고 `via_pricechk=true`일 때 `gap_pct`가 null이라는 지적(blind-hunter) — 스펙의 Boundaries가 명시한 필드 집합(ticker/strategy/outcome_id/pricechk 여부/gap_pct)과 정확히 일치하며 스펙 위반이 아니다.
  - 스펙 frontmatter `deferred: []`가 Boundaries/Design Notes/deferred-work.md가 서술하는 GitHub Issue 알림 배선 gap과 "불일치"한다는 지적(blind-hunter) — `deferred:` frontmatter는 리뷰 단계(step-04)가 새로 표면화한 항목을 위한 필드이지, 계획 단계(step-02)에서 이미 Boundaries에 명시적으로 문서화된 범위 결정을 위한 필드가 아니므로 애초에 불일치가 성립하지 않는다.
  - migration이 실제로 운영 project에 적용됐다는 증거가 diff에 없다는 지적(blind-hunter) — 이번 리뷰 패스에서 `mcp__supabase__execute_sql`로 운영 project(`qqhjeumlecaudsiqhhdu`)에 전체 fixture(기존 6개 시나리오 + 신규 3.5 시나리오 2개)를 직접 재실행해 `price_adjustment_gap_threshold`/`publish_attempt`가 실제로 존재하고 정상 동작함을 독립적으로 재확인했다.
  - `price_adjustment_gap_threshold()`의 "조정 가능(adjustable)" 표현이 실제로는 런타임 설정이 아니라 새 migration 배포가 필요해 과장이라는 지적(blind-hunter) — 스펙 문구가 약속한 것은 "임계값이 한 곳에 정의돼 있어 조정 가능"이라는 단일 정의 지점이지 런타임 설정이 아니므로, 실제 구현이 스펙 문구와 정확히 일치한다.
  - `ohlcv_cache.py`에 SQL 쪽 새 감지 로직을 가리키는 상호 참조 주석이 없다는 지적(blind-hunter) — 기능에 영향 없는 문서화 사안이며, 스펙의 Code Map/Boundaries에 이미 두 메커니즘이 서로 다른 신호원임이 명시돼 있다.
  - `revoke`/`grant`가 실제 `service_role`-scoped 호출 경로로 검증되지 않았다는 지적(blind-hunter) — 이 저장소의 다른 모든 함수(emit_open_command 등)도 동일하게 검증되지 않은 기존 컨벤션과 일치해 이 스토리만의 새로운 공백이 아니다.
  - 두 loop(3.4 관찰 루프, 3.5 감지 루프)의 정렬 없는 `for update` 스캔이 서로 다른 logical_run_key의 동시 close attempt 사이에서 잠금 순서 교착을 유발할 수 있다는 지적(edge-case-hunter) — 동일한 종류의 "전체 스캔+잠금" 우려가 Story 3.2/3.3/3.4 리뷰에서 이미 실측 근거 없는 조기 최적화 우려로 반복 기각된 선례가 있고, 이번에도 구체적 재현이나 실측 근거가 제시되지 않았다.
  - "재시도(동일 attempt 재발행)" 테스트가 `publish_attempt`를 실제로 재호출하지 않고 직접 insert로 unique index만 검증한다는 지적(blind-hunter/edge-case-hunter 공통) — `publish_attempt`는 `status<>'ready_to_publish'`/`canonical_success_run_id is not null` 가드로 한 run에 대해 구조적으로 한 번만 발행 가능해, 같은 트랜잭션 안에서 동일 충돌 키로 이 insert 분기가 실제로 두 번 실행되는 경로 자체가 존재하지 않는다(전체 rollback이 아니면 재시도할 방법이 없고, rollback되면 아무것도 남지 않아 애초에 충돌이 생기지 않는다). `if found then ... end if` 분기는 이미 3.2/3.3의 동일 패턴과 같은 수준으로 코드 검사로 신뢰 가능하다.
- addressed_findings:
  - `[medium]` `[patch]` 같은 attempt 안에서 `emit_open_command`가 방금 새로 OPEN시킨 outcome이 오늘 daily_ohlcv에 `pricechk`가 관측되면 SUSPENDED 감지 루프에 의해 곧바로 전이되는 결합 경로가 테스트되지 않았다는 지적(verification-gap/edge-case-hunter 중복 제기) — `tests/sql/test_run_lineage.sql`에 `close:2099-01-12` 시나리오(ZZLIN13)를 추가해 `candidate_tags`→`emit_open_command`→SUSPENDED 감지 루프가 실제로 결합되는 경로를 검증했다(같은 attempt 안에서 OPEN 이벤트 1건과 SUSPENDED 이벤트 1건이 모두 기록되고 최종 status가 SUSPENDED임을 확인).

## Design Notes

Story 2.2의 `AdjustmentFlag`는 "오늘 후보 모집단(`result.selection.candidates`)"에만 한정된 신호다(`run_scheduled_batch`가 그 목록만 `update_existing_ticker_history`에 전달). OPEN outcome은 진입 후 후보 모집단에서 얼마든지 이탈할 수 있으므로(태깅은 매일 재평가), 그 신호에만 의존하면 이탈한 OPEN outcome 티커의 가격 조정을 놓친다. 반대로 `daily_ohlcv.pricechk`는 그 티커의 증분 갱신이 실제로 일어난 모든 거래일에 이미 저장돼 있으므로, `candidate_outcome`의 OPEN 전체를 직접 훑는 편이 더 넓은 커버리지를 준다(단, 후보에서 이탈해 `daily_ohlcv` 자체가 갱신되지 않는 티커는 여전히 놓친다 -- Story 3.4가 이미 인정한 것과 동일한 한계이며 별도 스토리 없이는 해소되지 않는다).

`publish_attempt`가 실제 배치 오케스트레이터에 연결되지 않은 상태(Story 3.1~3.4에서 반복 확인된 기존 gap)이므로, `suspended_transitions` jsonb 노출은 "알림을 실제로 발송하는" 구현이 아니라 "알림 소비자가 나중에 재조회 없이 쓸 수 있는 typed 신호를 만들어 둔다"는 의미다. SQL fixture 테스트는 `begin;...rollback;`로 감싸 실행되므로(Story 3.1~3.4 선례) `outcome_events`에 영구히 남는 행이 없고, 이 상태에서 GitHub Issue 생성 워크플로/Python 배선을 추가해도 트리거할 실제 이벤트가 없어 검증 불가능한 코드가 된다. 알림 배선은 `publish_attempt` 프로덕션 연결(기존 gap 해소) 이후 별도로 다뤄야 한다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과(`tests/batch/test_scheduler.py`의 7건은 Story 3.1~3.4에서도 동일하게 확인된 baseline 실패로 이 스토리와 무관).
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용, `publish_attempt`/`price_adjustment_gap_threshold` 함수 정의 갱신 및 fixture pass를 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.4와 동일 판단).

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 신규 함수 `price_adjustment_gap_threshold()`(상수 0.30, service_role 전용)를 만들고 `publish_attempt`를 다시 `create or replace`했다. close 분기에서 Story 3.4의 관찰 수집 루프 뒤에, `status='OPEN'`인 `candidate_outcome`을 다시 훑어 오늘 `daily_ohlcv.pricechk`(1차, 갭 무관) 또는 전일 대비 종가 갭 절대값이 30%를 초과(pricechk 없을 때만, 2차 안전망)하면 `outcome_events`에 `command_type='SUSPENDED'`를 idempotent하게 append하고 `candidate_outcome.status`를 SUSPENDED로 전이하는 루프를 추가했다. 신규 전이는 `publish_attempt` 반환 jsonb의 `suspended_transitions` 배열로 노출된다. TP/SL/TIMEOUT 판정(3.6/3.7), SUSPENDED→정상 복귀/DELISTED 종결(3.8/3.9), 실제 GitHub Issue 알림 배선(publish_attempt 프로덕션 미배선이라는 기존 gap 때문에 검증 불가능한 코드가 되므로 보류)은 이 스토리 범위 밖으로 명시적으로 남겼다.

**변경 파일:**
- `infra/supabase/migrations/202609031800_detect_price_adjustment_suspension.sql` -- 신규 `price_adjustment_gap_threshold()` 함수, `publish_attempt`에 SUSPENDED 감지 루프 추가.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 7개 시나리오(`close:2099-01-11`, ZZLIN8~12)와 리뷰 패치로 추가된 결합 경로 시나리오(`close:2099-01-12`, ZZLIN13: `candidate_tags`→`emit_open_command`→SUSPENDED 감지 루프가 실제로 결합되는 경로) 및 3.4 기존 시나리오에 outcome_b가 daily_ohlcv 결측 시 SUSPENDED로 오판정되지 않고 OPEN을 유지함을 확인하는 assertion을 추가.
- `_bmad-output/implementation-artifacts/deferred-work.md` -- "story 3.5 build verification"(GitHub Issue 알림 배선 gap) 및 "story 3.5 code review"(emit_open_command SUSPENDED 재진입 가드 미비, daily_ohlcv 0/음수 종가 무방비) 두 섹션 추가.
- `packages/read-model/src/database.types.ts` -- 운영 project 최신 타입으로 갱신(`price_adjustment_gap_threshold` RPC 항목 추가, `publish_attempt` 시그니처 불변).

**리뷰 findings 분류:** patch 1건(적용 완료 -- 같은 attempt 안에서 emit_open_command가 방금 OPEN시킨 outcome이 SUSPENDED 감지 루프와 결합되는 경로의 테스트 누락[medium]), defer 2건(emit_open_command의 SUSPENDED 재진입 가드 미비[medium], daily_ohlcv 0/음수 종가 시 갭 안전망 무방비[low] -- 둘 다 frontmatter `deferred`와 `deferred-work.md`에 기록), dismissed 9건(관찰-후-감지 순서, premarket/intraday 응답 스키마 확장, SUSPENDED payload 필드 범위, frontmatter deferred 필드 오해, migration 미적용 의심[재검증으로 반증], "조정 가능" 문구 해석, 문서 상호참조 부재, service_role 미검증[기존 컨벤션], 정렬 없는 FOR UPDATE 잠금 우려[기존 선례로 기각] 및 재시도 테스트가 unique index만 검증한다는 지적[publish_attempt의 구조적 1회성 가드로 재현 불가 확인] -- 세부 근거는 Review Triage Log 참고).

**후속 리뷰 권고:** `false`(patch medium 1건 → 3×1=3 < 5).

**검증 수행:**
- Supabase MCP `execute_sql`로 운영 project에서 `tests/sql/test_run_lineage.sql` 전체(리뷰 패치 전 1회, 패치 후 전체 재실행 1회, 신규 결합-경로 시나리오 단독 사전검증 1회)를 `begin;...rollback;`으로 감싸 실행 -- 모두 예외 없이 통과.
- `npm run typecheck` -- 통과(리뷰 패치 전/후 각 1회).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 234 passed, 7 failed(모두 `tests/batch/test_scheduler.py`, baseline(2cba17a)에서도 동일하게 실패하는 기존 회귀로 이 스토리와 무관, Story 3.1~3.4에서도 동일하게 확인된 사항, 리뷰 패치 후 재확인).
- `git diff --check` -- 공백 오류 없음(CRLF 관련 무해한 경고만 존재).
- Matrix Test Audit: I/O 매트릭스 7개 행 모두 실행되어 통과한 테스트로 커버됨을 확인(오늘 daily_ohlcv 결측 행은 리뷰 중 발견된 감사 공백을 메우기 위해 기존 3.4 시나리오에 명시적 assertion을 보강).
- 4개 독립 리뷰 레이어(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)를 병렬 실행 후 모든 finding을 개별 검증 -- 실제 결함으로 확인된 1건은 테스트 보강으로 패치, 2건은 이 스토리가 아닌 사전 스키마/함수(Story 2.1/3.2)의 공백으로 defer, 나머지는 반증되거나 기존 컨벤션·선례와 일치해 dismiss.
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 Story 3.1~3.4 선례 일치).

**잔여 위험:**
- `emit_open_command`의 재진입 방지 가드가 `status='OPEN'`만 확인해, SUSPENDED 상태인 (ticker,strategy)가 재태깅되면 중복 candidate_outcome 행이 생길 수 있다(defer, Story 3.8 SUSPENDED 복귀 정책과 함께 다뤄야 함).
- `daily_ohlcv.close`에 양수 제약이 없어 전일 종가가 0이면 갭 안전망이 조용히 감지를 건너뛴다(defer, Story 2.1 스키마의 기존 공백).
- SUSPENDED 감지 루프는 매 close 발행마다 `status='OPEN'`인 모든 `candidate_outcome` 행을 전체 스캔·재잠금한다 -- Story 3.2/3.3/3.4와 동일한 이유로 현재는 AC가 요구하는 정상 동작이자 NFR-7로 유계이지만, Story 3.6/3.7이 같은 행 집합에 쓰기를 추가하면 잠금 경합을 재검토할 필요가 있다(Story 3.4 잔여 위험과 동일 계열).
- `publish_attempt`가 여전히 어떤 실제 배치 오케스트레이터에도 연결되지 않아(Story 3.1부터의 기존 gap), 이 스토리가 만든 SUSPENDED 감지·전이·`suspended_transitions` 노출도 프로덕션에서 실제로 실행되지 않는다 -- GitHub Issue 알림 배선은 이 gap 해소 이후에나 의미가 있다.
- Story 1.1에서 기록된 `skip_attempt` RPC 운영 미적용 건은 이 스토리와 무관하게 여전히 미해결이다(`deferred-work.md` 참조).
