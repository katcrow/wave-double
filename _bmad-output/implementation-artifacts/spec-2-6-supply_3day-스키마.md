---
title: 'supply_3day 스키마'
type: 'feature'
created: '2026-09-02'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
baseline_revision: '1b0a809822a12de7dafb0b3a96acadf01fc1b29c'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/specs/spec-wave-double/data-model.md'
warnings: [oversized]
deferred:
  - summary: >-
      .github/workflows/test.yml의 sql-outbox-tests job 스텝 이름("Run Epic 1 SQL
      fixtures")이 실제로는 Epic 2 fixture(daily_ohlcv/candidate_tags/supply_3day)까지
      실행하는 오래된 라벨이다.
    evidence: |-
      Story 2.1/2.5에서 이미 Epic 2 fixture가 이 스텝에 추가됐지만 스텝 이름은 갱신되지
      않았고, 이번 스토리(supply_3day)가 fixture를 하나 더 추가하며 그 불일치를
      더 키웠다. 기능적 결함은 아니고 CI 로그 가독성 문제이며, 이 스토리가 새로 만든
      문제가 아니라 기존에 있던 라벨 오류다.
    location: .github/workflows/test.yml:104
    severity: low
---

<intent-contract>

## Intent

**Problem:** 후보별 3일치(D-2/D-1/D0) 가격·수급 데이터를 저장할 `supply_3day` 테이블이 아직 없어, 이후 수집 stage(Epic 4)와 카드 UI(Story 2.7의 부분결측 표시)가 의지할 스키마가 없다.

**Approach:** data-model.md에 이미 확정된 `supply_3day` 정의(컬럼·제약·`investor_net_status` 상태 계약)를 그대로 migration으로 만든다 — 이번 스토리는 스키마 신설만 하며, 수집 로직·정리(cleanup) 배치는 구현하지 않는다.

## Boundaries & Constraints

**Always:**
- `infra/supabase/migrations/`에 신규 migration으로 `public.supply_3day` 테이블을 생성한다: `candidate_id`(uuid not null), `attempt_run_id`(uuid not null), `trading_day`(date not null), `slot`(text not null, check in `D-2`/`D-1`/`D0`), `close`/`volume`/`change_pct`(numeric not null, 유한값만 — NaN/Infinity 거부), `foreign_net`/`institution_net`/`individual_net`/`program_net`(numeric, **nullable**), `investor_net_status`(text not null, check in `confirmed`/`pending`/`missing`), `collected_at`(timestamptz not null default now()).
- `foreign key (candidate_id, attempt_run_id) references public.candidates(candidate_id, attempt_run_id)` — `candidate_tags`(202609021600)와 동일한 합성키 FK 패턴을 재사용해 참조 무결성을 건다.
- `UNIQUE(candidate_id, trading_day, attempt_run_id)` — epics.md AC 원문 그대로(slot은 포함하지 않음; trading_day가 이미 slot을 함의한다).
- CHECK 제약으로 `investor_net_status`와 투자자별 4컬럼의 일관성을 DB 레벨에서 강제한다: `confirmed`이면 4컬럼 모두 NOT NULL, `pending`/`missing`이면 4컬럼 모두 NULL이어야 한다(둘 중 하나도 아닌 조합은 거부) — "NULL과 실젯값(0 포함)을 서로 대체하지 않는다"는 data-model.md 계약을 스키마로 보장한다.
- `candidates`/`daily_ohlcv` 하드닝 선례와 동일하게 `alter table ... enable row level security`만 적용한다(정책 0개, deny-all — anon/authenticated 접근 차단, service-role만 우회).
- 테이블/컬럼 `comment on`으로 `investor_net_status` 3상태의 의미(`confirmed`/`pending`/`missing`)와 D0 행이 attempt_run_id별로 누적되며 정리 대상은 D0만(NFR-4, 90일 잠정)이고 D-2/D-1은 정리 대상이 아니라는 사실을 문서화한다.
- `tests/sql/test_supply_3day.sql`을 신규 작성하고 `.github/workflows/test.yml`의 `sql-outbox-tests` psql 목록에 추가한다.

**Never:**
- t1702/t1637 수집 로직, 배치 stage 오케스트레이션, 카드 UI(부분결측 표시) — 모두 Epic 4 / Story 2.7 범위이며 이 스토리에서 구현하지 않는다.
- D0 정리(cleanup) 배치 잡 — NFR-4 정책은 comment로 문서화만 하고 실제 삭제 로직은 만들지 않는다.
- `candidates`/`candidate_tags`/`daily_ohlcv` 등 기존 테이블·마이그레이션을 수정하지 않는다(신규 테이블 추가만).

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609021900_write_stage_reacts_to_tags_completion.sql` -- 최신 migration(다음 파일의 타임스탬프 기준점). 신규 파일은 `202609022000_create_supply_3day.sql`.
- `infra/supabase/migrations/202609021600_create_candidate_tags.sql` -- 합성키 FK(candidate_id, attempt_run_id) → candidates, RLS enable-only 패턴의 직접 참고 대상(그대로 재사용).
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql` -- 유한값(NaN/Infinity 거부) CHECK 패턴의 참고 대상(`close <> 'NaN'::numeric and ... <> 'Infinity'::numeric and ... <> '-Infinity'::numeric` 형태를 close/volume/change_pct에 적용).
- `_bmad-output/specs/spec-wave-double/data-model.md:88-103` -- `supply_3day` 정의의 단일 출처. 컬럼/제약/`investor_net_status` 3상태 계약이 이미 확정되어 있으므로 여기서 재해석하지 않고 그대로 옮긴다.
- `tests/sql/test_daily_ohlcv.sql` -- 스키마 전용 스토리의 pgTAP 스타일 fixture 구조(컬럼/PK/RLS/CHECK 검증, `begin`/`rollback` 래핑) 참고.
- `tests/sql/test_candidate_tags.sql:1-75` -- `start_attempt`로 유효한 `(candidate_id, attempt_run_id)`를 만들어 FK 통과 케이스를 세팅하는 방법의 참고 대상(신규 파일도 `candidates`에 유효 행이 있어야 FK 성공 케이스를 검증할 수 있음).
- `.github/workflows/test.yml:108` -- `sql-outbox-tests` job의 psql 목록에 `tests/sql/test_supply_3day.sql` 추가.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609022000_create_supply_3day.sql` -- `supply_3day` 테이블(컬럼/CHECK/FK/UNIQUE/RLS) 생성 -- AC1, AC2.
- `tests/sql/test_supply_3day.sql` -- PK 없음(UNIQUE만)/FK/UNIQUE/CHECK(slot, investor_net_status, confirmed↔4컬럼 일관성, 유한값)/RLS pgTAP 검증 -- I/O 매트릭스 전체.
- `.github/workflows/test.yml` -- `sql-outbox-tests`의 psql 실행 목록에 신규 fixture 추가 -- CI 커버리지.

**Acceptance Criteria:**
- Given migration을 적용하면, when `supply_3day` 스키마를 조회하면, then data-model.md 정의대로 전체 컬럼·FK(candidate_id, attempt_run_id)→candidates·UNIQUE(candidate_id, trading_day, attempt_run_id)가 정확히 존재한다.
- Given `investor_net_status='confirmed'`로 삽입하면, when 4컬럼 중 하나라도 NULL이면, then CHECK 위반으로 거부된다.
- Given `investor_net_status`가 `pending`/`missing`이면, when 4컬럼 중 하나라도 NOT NULL이면, then CHECK 위반으로 거부된다.
- Given RLS 상태를 확인하면, when `pg_policies`를 조회하면, then `supply_3day`에 정책이 0개다(deny-all).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 confirmed 삽입 | 4컬럼 전부 NOT NULL + `investor_net_status='confirmed'` | 삽입 성공 | No error expected |
| 정상 pending 삽입 | 4컬럼 전부 NULL + `investor_net_status='pending'` | 삽입 성공(장중 미확정) | No error expected |
| confirmed인데 일부 NULL | 4컬럼 중 1개 NULL + `confirmed` | 거부 | CHECK 위반 |
| pending인데 일부 실값 | 4컬럼 중 1개 NOT NULL + `pending` | 거부 | CHECK 위반 |
| 잘못된 slot | `slot='D-3'` | 거부 | CHECK 위반 |
| FK 위반 | 존재하지 않는 `(candidate_id, attempt_run_id)` | 거부 | foreign_key_violation |
| UNIQUE 위반 | 동일 `(candidate_id, trading_day, attempt_run_id)` 재삽입 | 거부 | unique_violation |
| 유한값 위반 | `close`/`volume`/`change_pct`에 NaN | 거부 | CHECK 위반 |

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3 (high 0, medium 1, low 2)
- defer: 1 (high 0, medium 0, low 1)
- dismissed:
  - `comment on table`이 "90일" 정리 주기를 근거 없이 못박았다는 주장(blind-hunter) — epics.md Story 2.6 AC3 원문이 이미 "정리 대상(90일 잠정)"을 명시하며, data-model.md의 "짧게"는 같은 정책의 다른 표현일 뿐 90일과 모순되지 않는다. 지적은 data-model.md만 확인하고 epics.md AC를 놓친 오독이다.
  - close/volume/change_pct에 양수(>0/>=0) 제약이 없다는 주장(edge-case-hunter) — daily_ohlcv(202609021500) 선례도 동일하게 유한값(NaN/Infinity)만 거부하고 양수 제약은 두지 않는 확립된 관례이며, change_pct는 실제로 음수가 정상값이라 양수 제약을 추가하면 오히려 정상 데이터를 거부하게 된다.
  - 정리(cleanup) 배치를 위한 별도 인덱스(trading_day 등)가 없다는 주장(blind-hunter) — Story 2.5 리뷰에서 이미 확정된 관례(접근 패턴이 정해지지 않은 인덱스는 후속 스토리가 자신의 필요에 맞게 추가)와 동일하며, 실제 정리 배치 구현 자체가 이 스토리의 Never 경계 밖(Epic 4/후속)이다.
  - NOT NULL 컬럼 누락 삽입에 대한 네거티브 테스트가 없다는 주장(blind-hunter) — Postgres NOT NULL은 스키마 선언만으로 신뢰성 있게 강제되며, daily_ohlcv/candidate_tags 선례도 동일한 이유로 이를 별도 테스트하지 않는다.
  - `collected_at` 기본값(now())이 테스트되지 않는다는 주장(blind-hunter) — DB 기본값은 Postgres가 신뢰성 있게 보장하며 candidate_tags의 `tagged_at`도 동일 패턴을 별도 테스트하지 않는다.
  - institution_net/program_net이 일관성 CHECK 테스트에서 대표값(foreign_net/individual_net)으로만 다뤄진다는 주장(blind-hunter) — 제약이 4컬럼에 대칭적인 단일 AND/OR 선언이며 컬럼별로 분기하는 코드 경로가 없어, 대표 컬럼 검증만으로 동일 메커니즘이 이미 충분히 입증된다(패치 3에서 4컬럼 전부에 대한 finite-value 테스트는 추가함).
  - slot/trading_day/close/volume/change_pct에 컬럼 comment가 없다는 주장(blind-hunter) — daily_ohlcv 선례도 비자명한 컬럼(pricechk)에만 comment를 달고 나머지는 테이블 comment로 갈음하는 동일 관례를 따른다.
  - 같은 attempt 안에서 같은 slot이 다른 trading_day로 중복 삽입될 수 있다는 주장(blind-hunter) — slot-trading_day 매핑의 정확성은 수집 stage(Epic 4)의 책임이며, 이 스토리(스키마 신설만)의 Never 경계 밖이다.
  - FK 위반 테스트용 `other_run_id`가 이후 정리되지 않는다는 주장(blind-hunter) — 테스트 전체가 `begin`/`rollback`로 감싸여 있어 실제 부작용이 없다.
  - 마이그레이션 상단 주석이 인접 테이블 `market_supply`를 언급하지 않는다는 주장(blind-hunter) — 범위 진술은 이 스토리가 만드는 테이블 기준으로 충분하며 인접 테이블 전부를 열거할 필요는 없다.
  - 모든 유한값/enum CHECK가 제약 이름을 구분해 검증하지 않는다는 주장(blind-hunter) — daily_ohlcv 선례도 동일한 방식(`check_violation`만 확인)이며 이 스토리가 새로 도입한 약점이 아니다.
  - 향후 정리 배치를 위한 forward-compatible 마커 컬럼(`purged_at` 등)이 없다는 주장(blind-hunter) — 정리 배치 구현 자체가 이 스토리의 Never 경계 밖이며 설계는 해당 후속 스토리가 필요에 맞게 정할 사안이다.
  - `sprint-status.yaml`이 아직 backlog이고 커밋이 안 됐다는 지적(intent-alignment) — 리뷰 시점은 워크플로우의 Finalize 단계 이전이며, 스프린트 동기화·커밋은 리뷰 통과 후 정상적으로 수행되는 다음 단계다.
- addressed_findings:
  - `[medium]` `[patch]` investor-net 4컬럼(foreign_net/institution_net/individual_net/program_net)에 finite-value(NaN/Infinity 거부) CHECK가 없어 잘못된 부동소수값이 조용히 저장될 수 있었다 — close/volume/change_pct와 동일한 패턴으로 NULL 허용 + NaN/Infinity 거부 CHECK 4개를 추가하고, 각 컬럼에 대한 거부 테스트를 `tests/sql/test_supply_3day.sql`에 추가했다.
  - `[low]` `[patch]` D0 이력이 attempt마다 누적되고 덮어써지지 않는다는 data-model.md의 핵심 계약을 검증하는 테스트가 없었다 — 두 번째 attempt를 만들어 같은 ticker의 같은 trading_day/slot에 새 행을 삽입하고 두 attempt의 행이 공존함을 검증하는 테스트를 추가했다(candidate_id는 attempt마다 새로 발급되는 전역 PK라 동일 candidate_id로는 재현 불가능함을 실측으로 확인 후 ticker 기준으로 정확히 재구성).
  - `[low]` `[patch]` epics.md AC2가 요구하는 "candidate_id로 candidates뿐 아니라 candidate_tags와도 연결된다"는 사실이 테이블 comment에 문서화되지 않았다 — `comment on table`에 candidate_id가 candidate_tags와도 공유하는 조인 키라는 설명을 추가했다.

## Verification

**Commands:**
- `psql -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 -f tests/sql/test_supply_3day.sql` -- expected: 전체 시나리오 통과(로컬 Supabase/Postgres 컨테이너에 선행 migration까지 적용된 상태).
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):**
- 신규 migration을 Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 직접 적용하고, `supply_3day` 스키마·FK·CHECK·RLS를 실제 조회로 확인한다(단일 프로젝트, dev/staging 분리 없음 — 운영 적용이 곧 검증).

## Auto Run Result

- **구현 요약:** Story 2.6 `supply_3day` 스키마를 신설했다. data-model.md의 확정된 정의를 그대로 migration으로 옮겨 후보별 3일치(D-2/D-1/D0) 가격·수급 테이블을 만들었다 — `candidates(candidate_id, attempt_run_id)` 합성키 FK(candidate_tags 패턴 재사용), `UNIQUE(candidate_id, trading_day, attempt_run_id)`, `investor_net_status`(confirmed/pending/missing) 상태와 4개 투자자별 순매수 컬럼의 일관성을 강제하는 CHECK, close/volume/change_pct 및 4개 투자자별 컬럼 전체에 대한 유한값(NaN/Infinity 거부) CHECK, RLS enable(정책 0개, deny-all)을 갖췄다. 이번 스토리는 스키마 신설만 하며 수집 로직(t1702/t1637)·배치 오케스트레이션·카드 UI·정리(cleanup) 배치는 구현하지 않았다(Epic 4/Story 2.7 범위, comment로 정책만 문서화).
- **변경 파일:**
  - `infra/supabase/migrations/202609022000_create_supply_3day.sql` — 신규: `supply_3day` 테이블(컬럼/CHECK 8종/FK/UNIQUE/RLS) 생성, 테이블·컬럼 comment로 3상태 계약·D0 누적/정리 정책·candidate_tags 조인 관계 문서화.
  - `tests/sql/test_supply_3day.sql` — 신규: PK 없음(UNIQUE만)/FK/UNIQUE/CHECK(slot, investor_net_status, confirmed↔4컬럼 일관성, close/volume/change_pct 및 투자자별 4컬럼 유한값)/RLS/append-only 누적 pgTAP 픽스처(`begin`/`rollback` 래핑).
  - `.github/workflows/test.yml` — `sql-outbox-tests` job의 psql 실행 목록에 `tests/sql/test_supply_3day.sql` 추가.
- **리뷰 결과:** patch 3건 전부 수정(medium 1, low 2) · deferred 1건 기록(low, CI 스텝 이름 노후화) · dismissed 12건(근거는 Review Triage Log 참조) · bad_spec·intent_gap 없음.
- **추적 리뷰 권장:** 이번 패스 patch 중 medium 1건 포함 → **권장함**(score = 3×1(medium)+1×2(low) = 5, 임계값 5 이상).
- **수행한 검증:**
  - 4개 마이그레이션(1600/1700/1800/1900)에 이어 신규 `202609022000_create_supply_3day` 마이그레이션을 Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 직접 적용 확인(`list_migrations`로 검증) — 단일 프로젝트 정책에 따라 운영 적용이 곧 검증.
  - 라이브 Supabase에서 `information_schema.columns`/`pg_constraint`로 전체 컬럼·FK·UNIQUE·CHECK 8종(slot/investor_net_status/consistency/close·volume·change_pct 유한값/투자자별 4컬럼 유한값) 정의를 실제 조회로 확인, `pg_class.relrowsecurity=true` + `pg_policies` 0건(deny-all) 확인, PRIMARY KEY 없음(UNIQUE만) 확인.
  - `tests/sql/test_supply_3day.sql`의 전체 시나리오(정상 confirmed/pending/missing 삽입, confirmed/pending/missing 일관성 위반, 잘못된 slot/investor_net_status, close/volume/change_pct 및 투자자별 4컬럼 유한값 위반, FK 위반, UNIQUE 위반, append-only 누적, PK 없음, RLS)를 라이브 Supabase에서 `begin`/`rollback`로 감싼 트랜잭션으로 실행해 전부 통과 확인, 롤백 후 `supply_3day` 잔여 데이터 0건 확인(운영 데이터 오염 없음).
  - `git diff --check` → whitespace 오류 없음(CRLF 안내 경고만).
  - I/O 매트릭스 8개 시나리오 전부 전용 테스트로 커버(정상 confirmed/pending 삽입, confirmed 일부 NULL, pending 일부 실값, 잘못된 slot, FK 위반, UNIQUE 위반, 유한값 위반).
- **잔여 리스크:** ① `.github/workflows/test.yml`의 sql-outbox-tests 스텝 이름이 "Run Epic 1 SQL fixtures"로 남아 있어 Epic 2 fixture 실행을 반영하지 못함(defer, low, 이 스토리 이전부터 있던 라벨 오류). ② 정리(cleanup) 배치·수집 로직·카드 UI는 의도적으로 이번 스토리 범위 밖(Epic 4/Story 2.7)이며 스키마 comment로 정책만 문서화했다.
</content>
