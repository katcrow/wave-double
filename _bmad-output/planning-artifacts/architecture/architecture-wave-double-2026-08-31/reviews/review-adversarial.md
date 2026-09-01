# Reviewer Gate — 적대적 재검토

- 대상: `../ARCHITECTURE-SPINE.md` 수정본
- 렌즈: shared-data shape, owner, mutation path, time/concurrency, security, operations
- 판정: **BLOCK — Critical 2건, High 3건 잔존**

이 재검토는 서로 독립적인 하위 구현 둘이 수정된 스파인을 문자 그대로 따르는 경우를 구성했다. JWT 검증 기준, expand-migrate-contract, 관측 원장 분리는 개선됐지만, “어느 attempt의 데이터가 현재 사실인가”를 고정하는 publication/fencing 계약과 운영 복구 계약은 아직 닫히지 않았다.

## Critical

### RA-01 — partial 공개와 마지막 성공 스냅샷 보존이 동시에 성립하지 않는다

**관련 규칙:** AD-10은 UI가 마지막 성공 스냅샷을 보존하라고 한다. AD-13은 `success`뿐 아니라 `screen+tagging`이 끝난 `partial`도 공개할 수 있고, read view는 하나의 published `run_id`만 읽으라고 한다.

**서로 비호환인 두 준수 구현:**

- 구현 A는 `published_at IS NOT NULL ORDER BY published_at DESC LIMIT 1`을 현재 pointer로 본다. 어제 success 뒤 오늘 screen+tagging-only partial이 publish되면 CAP-3/4 수급 행이 없는 오늘 run이 현재 데이터가 되어 “마지막 성공 스냅샷 보존”을 깨뜨린다.
- 구현 B는 최신 success만 현재 pointer로 유지하고 partial은 운영 상태에만 노출한다. 이는 AD-10은 지키지만 AD-13의 “partial도 공개 가능”을 데이터 공개로 해석한 구현과 API 결과가 다르다.
- 구현 C가 partial의 없는 수급을 직전 success에서 보충하면 화면은 풍부해지지만, AD-13의 “하나의 published `run_id` 안에서만 join”을 위반한다.

**영향:** 같은 read-model contract를 구현한 웹과 SQL view가 서로 다른 현재 후보 집합·신선도·결측 의미를 반환한다. partial이 success보다 늦게 publish되는 정상 경로만으로 재현되므로 단순 장애 edge case가 아니다.

**필수 보완 규칙:**

1. `current_complete_run_id`와 `latest_partial_run_id`를 별도 pointer로 둘지, partial은 pointer를 절대 바꾸지 않는 preview로 둘지 하나를 결정한다.
2. 기본 CAP-1~7 read contract는 `current_complete_run_id` 하나만 읽도록 고정한다. partial preview를 허용한다면 별도 RPC/route와 capability coverage(`completed_stages`)를 반환하고 완전 스냅샷과 합성하지 않는다.
3. `published_at` 자체를 pointer 선택 규칙으로 쓰지 말고 `(logical_run_key, publication_kind)` unique row 또는 동등한 명시적 pointer를 단일 transaction/CAS로 갱신한다.
4. partial이 success 이후 도착해도 complete pointer를 낮추지 못하는 단조성 조건을 DB constraint/RPC에 둔다.

**처리:** 구현 인계 전 AD-10/13 수정 필요.

### RA-02 — 재시도 winner와 outcome의 최초 source/provenance가 연결되지 않는다

**관련 규칙:** AD-3은 동일 logical run의 시도마다 새 `run_id`를 만들고 직렬화한다. AD-9는 outcome identity를 `(ticker, strategy, entry_trading_day)`로 유지하면서 최초 `entry_candidate_id`와 `created_run_id`를 보존한다. AD-12는 source별 성과를 별도 slice로 노출한다. AD-13은 success 또는 일부 partial attempt를 publish할 수 있다.

**서로 비호환인 두 준수 구현:**

- close attempt 1이 fallback source로 screen+tagging을 완료해 partial publish되고 outcome을 먼저 생성한다. attempt 2가 t1859 source로 success publish돼도 AD-9 때문에 `entry_candidate_id`와 `created_run_id`는 attempt 1에 고정된다. 현재 추천 스냅샷은 attempt 2인데 성과 source는 attempt 1이다.
- 구현 A는 AD-9의 보존 규칙을 따라 최초 outcome을 유지한다. 구현 B는 현재 published winner와 맞추려고 `entry_candidate_id`를 attempt 2로 갱신한다. B는 provenance를 바로잡지만 append-once 의미를 위반한다.
- 다른 구현은 outcome 생성을 success attempt에만 제한할 수 있으나, 현재 스파인은 “close만 생성”할 뿐 “canonical published close attempt만 생성”이라고 하지 않는다.

**영향:** 원천별 성과와 편향 slice가 어떤 attempt가 먼저 실행됐는지에 따라 달라진다. 재시도가 데이터 품질을 회복해도 장부의 추천 원천이 실패/partial attempt에 영구 귀속될 수 있다.

**필수 보완 규칙:**

1. logical run마다 하나의 immutable `canonical_attempt_run_id`를 publication transaction이 선택하고, outcome 생성 자격을 그 canonical close attempt로만 제한한다.
2. partial close가 outcome을 만들 수 있는지 명시한다. 허용하지 않는 것이 권고안이며, 허용한다면 이후 success가 canonical winner를 바꿀 수 없는지와 source attribution 정책을 함께 고정해야 한다.
3. outcome 생성 함수는 candidate가 동일 `canonical_attempt_run_id`에 속하고 그 run이 요구 publication 상태인지 FK/constraint로 검증한다.
4. source가 여러 fallback 결과의 합집합일 수 있다면 canonical candidate 선택/기여-source 연결 shape를 정의한다. outcome projection의 단일 `entry_candidate_id`만으로 source별 slice를 만들 수 있다는 가정을 금지한다.

**처리:** 구현 인계 전 AD-3/9/12/13을 하나의 winner 계약으로 연결해야 한다.

## High

### RA-03 — 상태 저장 shape와 stale worker fencing이 아직 결정되지 않았다

**관련 규칙:** AD-3은 orchestrator만 `runs`, `attempt_no`, `stage_status`를 변경하고 GitHub concurrency와 advisory lock으로 logical key를 직렬화한다고 한다. Run convention은 `run_id`가 attempt UUID라고 한다.

**서로 비호환인 두 준수 구현:**

- DB 구현 A는 logical run마다 `runs` 한 행을 두고 JSON `stage_status`와 최신 `run_id`를 덮어쓴다. 구현 B는 attempt마다 `runs` 행을 두고 `(run_id, stage)` 행을 별도 저장한다. 둘 다 문구를 지키지만 generated read-model type과 UI의 latest-run query가 호환되지 않는다.
- worker가 advisory lock을 잃은 뒤 외부 LS 호출에서 돌아와 stage table을 쓰는 경우, 새 attempt가 이미 시작됐어도 AD-3의 “자기 테이블 upsert”는 막히지 않는다. GitHub concurrency도 이미 시작된 외부 프로세스/재전달 작업에 DB fencing을 제공하지 않는다.
- 구현마다 GitHub concurrency group과 `cancel-in-progress` 정책, advisory lock의 session/transaction 범위가 다르면 schedule과 manual이 동일 logical key인데도 서로 다른 lock namespace를 사용할 수 있다.

**필수 보완 규칙:**

1. 최소 shared shape를 고정한다: `logical_runs(logical_run_key unique, canonical_attempt_run_id, ...)`, `run_attempts(run_id, logical_run_key, attempt_no unique per key, ...)`, `run_stages(run_id, stage unique, status, ...)` 또는 동등한 하나의 명시 모델.
2. attempt 시작 시 단조 증가 `fence_token`을 발급하고 모든 stage write/publish RPC가 현재 token과 canonical eligibility를 검사하도록 한다. advisory lock만을 stale-write 방지 수단으로 사용하지 않는다.
3. GitHub concurrency group의 canonical serialization, schedule/manual 공통 namespace, `cancel-in-progress` 값을 고정한다.
4. 상태 전이는 expected status를 받는 전용 RPC/CAS만 허용하고 JSON read-modify-write 같은 임의 mutation을 금지한다.

**처리:** AD-3의 enforceable shared contract로 보완 필요.

### RA-04 — production 데이터의 복구·교정 운영 계약이 없다

**관련 규칙:** AD-11은 hosted production 하나와 trusted workflow를 정한다. AD-14는 앱 rollback 뒤 additive fix를 말하지만, DB migration/data corruption/운영자 실수에 대한 복구 지점을 정하지 않는다. AD-9의 terminal outcome은 수정 불가다.

**서로 비호환인 두 준수 구현:**

- 운영 구현 A는 Supabase provider의 기본 backup/PITR이 있다고 가정한다. 구현 B는 무료/선택한 plan에 PITR이 없다고 보고 수동 dump를 만든다. 호스팅 provider가 Deferred이므로 실제 RPO와 복구 가능성이 배포 단위에 따라 달라진다.
- 잘못된 migration이나 오염된 market data가 대량 projection을 만들 때, 한 구현은 DB restore로 전체를 되돌리고 다른 구현은 append-only correction을 시도한다. 어느 시점의 외부 LS 데이터와 GitHub run을 재현해야 하는지도 없다.

**필수 보완 규칙:**

1. V1의 RPO/RTO, backup/PITR 필요 조건, 보존 기간, migration 전 restore point 생성 여부를 provider 선택의 필수 acceptance contract로 둔다.
2. 정기 restore drill과 복구 책임자/절차, 복구 후 publication pointer 및 GitHub schedule 재개 순서를 명시한다.
3. immutable outcome 오류는 원행 수정이 아닌 감사 가능한 correction event와 집계 제외/대체 규칙으로 복구하도록 고정한다. 대량 오염 시 restore와 correction 중 선택 기준을 둔다.
4. LS 원문 응답을 영구 보존하지 않는다면 재현 가능한 최소 input hash/cutoff/adapter version을 run artifact에 남긴다.

**처리:** 운영 차원 전체가 Deferred에도 없어 High. AD-11 또는 별도 운영 AD가 필요하다.

### RA-05 — dispatch idempotency key의 보안 scope와 충돌 의미가 없다

**관련 규칙:** AD-7은 same-origin CSRF, 사용자별 rate limit, idempotency key를 요구하고 같은 key면 기존 dispatch 결과를 반환한다. 그러나 key 발급 주체, 저장 scope/TTL, 동일 key에 다른 payload가 온 경우를 정하지 않는다.

**서로 비호환인 두 준수 구현:**

- route A는 client key를 전역 unique로 저장하고 payload가 달라도 최초 결과를 반환한다. 사용자가 같은 key로 close 다음 intraday를 보내면 intraday 요청이 성공처럼 보이지만 close dispatch 결과가 반환된다.
- route B는 `(sub, batch_kind, trading_day, slot, key)`로 scope를 잡아 둘 다 실행한다. 둘 다 “같은 key는 기존 결과 반환”을 따른다고 주장할 수 있다.
- key TTL이 route 인스턴스 메모리 수명이라면 재배포 뒤 replay가 새 GitHub dispatch를 만든다. DB 영속 구현과 보안 결과가 다르다.

**필수 보완 규칙:**

1. key는 DB에 영속하고 최소 `(sub, route_contract, idempotency_key)` unique로 고정한다.
2. canonical request hash를 함께 저장해 같은 key+같은 hash만 replay하고, 같은 key+다른 hash는 `409`로 거부한다.
3. 보존 TTL은 GitHub/API retry 최대창보다 길게 정하고, pending/succeeded/failed/unknown 상태와 timeout 후 reconciliation owner를 정한다.
4. DB idempotency record 생성과 GitHub dispatch 사이의 불가피한 dual-write gap을 outbox/reconciler 또는 동등한 mutation path로 닫는다.

**처리:** AD-7 mutation path 구체화 필요.

## Gate 결론

**BLOCK.** RA-01과 RA-02는 현재 읽기 데이터와 성과 장부의 의미가 정상 재시도 순서만으로 달라지는 Critical이다. RA-03은 그 두 문제를 재발시키는 concurrency/fencing 공백이다. RA-04와 RA-05는 production 운영과 보안 mutation의 결과를 구현별로 달라지게 하는 High다. 이 리뷰는 스파인을 수정하지 않았다.
