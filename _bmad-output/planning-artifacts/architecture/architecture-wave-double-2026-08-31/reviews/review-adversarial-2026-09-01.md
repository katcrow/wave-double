# Adversarial Architecture Review — 2026-09-01

## 판정

**REJECT — 구현 착수 차단.** 현재 스파인은 중요한 방향은 제시하지만, 서로 독립적인 구현 단위가 모든 AD를 문자 그대로 지켜도 동일한 데이터와 상태를 만들 수 없는 계약 충돌이 남아 있다. 특히 publication/outcome 순환 의존, provenance의 상호 배타적인 물리 형상, append-only 장부와 canonical cleanup의 충돌은 단순 구현 세부가 아니라 정상 경로 자체를 막거나 과거 사실을 지울 수 있는 blocker다.

## 검토 기준

이 리뷰는 기존 review 파일의 결론을 전제하지 않았다. 웹, orchestrator, stage writer, SQL migration, read-model, restore worker, dispatch reconciler가 별도 구현 단위라고 가정하고, 각 구현자가 AD 문구만으로 같은 결과에 도달할 수 있는지를 공격적으로 검토했다.

## Findings

### ADV-01 — publication과 outcome 생성 자격이 순환 의존한다

- **심각도:** BLOCKER
- **해당 AD:** AD-3, AD-9, AD-13, AD-15
- **충돌 시나리오:**
  1. close attempt가 `screen`, `tagging`, `supply_3day`, `market_supply`, `bias`를 완료한다.
  2. AD-13은 `outcome`도 `success/OK`여야 attempt를 publish할 수 있다고 강제한다.
  3. 그러나 AD-15는 publication transaction이 canonical attempt를 선택하고, outcome 함수는 그 run이 이미 `status='success'`인 출판 상태여야 한다고 강제한다.
  4. 구현 A는 outcome을 먼저 만들면 AD-15 위반이고, 구현 B는 publish를 먼저 하면 AD-13 위반이다. 두 구현 모두 문구를 지키면 close run은 영원히 성공할 수 없다.
- **강화안:** close publication을 단일 원자 transaction의 명시적 순서로 재정의한다. 예: `RUNNING -> READY_TO_PUBLISH`; transaction 안에서 (a) fence/CAS와 필수 pre-publish stage 검증, (b) canonical 선정, (c) outcome 생성 및 outcome stage 기록, (d) published_at/current pointer/status=SUCCESS 갱신을 수행한다. AD-15의 사전조건을 “이미 published success”가 아니라 “동일 publication transaction에서 canonical로 잠금된 READY_TO_PUBLISH attempt”로 바꾸고, 실패 시 전부 rollback하도록 SQL RPC 시그니처와 isolation level을 고정해야 한다.

### ADV-02 — provenance 테이블에 서로 양립할 수 없는 두 물리 형상이 명시돼 있다

- **심각도:** BLOCKER
- **해당 AD:** AD-9, AD-15, AD-16, AD-19
- **충돌 시나리오:** AD-16은 `candidate_source_contrib(candidate_id, source, contribution_weight, contrib_run_id, restore_epoch)`를 source별 상세 기여 행으로 정의한다. 반면 AD-19는 candidate당 단일 행을 만들고 여러 source를 JSONB `sources` 배열에 집약하라고 한다. SQL 구현 A는 `(candidate_id, source)` 다중 행을 만들고, 구현 B는 candidate당 JSONB 단일 행을 만든다. 둘 다 해당 AD를 문자 그대로 따르지만 `bias_metrics` JOIN의 행 수와 가중 집계가 달라진다. 또한 AD-16의 `source TEXT NOT NULL REFERENCES candidates(source)`는 참조 대상 `candidates.source`가 unique key가 아니므로 일반적인 FK로 생성할 수 없고, AD-19의 다중 source 단일 행에는 단일 `source` 값 자체가 존재하지 않는다.
- **강화안:** 하나의 정규형만 선택한다. 권고안은 source별 행이며 PK를 `(candidate_id, source, contrib_run_id, restore_epoch)`, `CHECK (contribution_weight > 0 AND contribution_weight <= 1)`, 후보별 weight 합계 검증 RPC, primary source 결정 규칙을 둔다. source 값은 enum/check로 검증하고 후보 계보 FK는 `(candidate_id, contrib_run_id)` 같은 실제 candidate key를 참조한다. `source_jsonb`는 API projection으로만 생성하고 저장 권위로 사용하지 않는다. 반대로 JSONB 단일 행을 선택한다면 AD-16의 행 형상·`source` FK·JOIN 규칙을 모두 제거하고 JSON schema/version/weight 제약을 DB에서 강제해야 한다.

### ADV-03 — AD-19의 canonical partial index는 PostgreSQL에서 생성 불가능하다

- **심각도:** BLOCKER
- **해당 AD:** AD-14, AD-19
- **충돌 시나리오:** AD-19가 요구하는 `WHERE contrib_run_id IN (SELECT canonical_attempt_run_id FROM logical_runs)` partial unique index predicate에는 다른 테이블 subquery가 들어간다. PostgreSQL partial index predicate에는 subquery를 사용할 수 없다. migration 구현 A는 실패하고, 구현 B는 일반 unique index로 대체해 non-canonical history까지 단일행으로 제한하며, 구현 C는 애플리케이션 검증만 해 동시 publish 중복을 허용한다.
- **강화안:** 실행 가능한 제약으로 교체한다. 예를 들어 `candidate_source_contrib`에 transaction 내에서만 설정되는 `is_canonical boolean`을 두고 `UNIQUE (logical_run_key, candidate_id) WHERE is_canonical`, 또는 canonical contribution 전용 테이블을 분리해 `(logical_run_key, candidate_id)` PK로 만든다. canonical 전환 RPC가 logical_runs 행을 `FOR UPDATE`로 잠그고 이전 canonical 해제와 새 canonical 삽입을 같은 transaction에서 수행하도록 DDL과 RPC를 제시해야 한다.

### ADV-04 — canonical cleanup이 append-only outcome 장부와 운영 사실 단일 소유권을 파괴한다

- **심각도:** BLOCKER
- **해당 AD:** AD-2, AD-9, AD-15, AD-19
- **충돌 시나리오:** AD-9는 terminal outcome이 바뀌지 않고 observation 원장이 append-only라고 하며, `candidate_outcome`은 현재 projection이라고 정의한다. AD-19는 canonical publish 시 이전 attempt의 `candidate_outcome` 행을 삭제하라고 강제한다. 구현 A는 `created_run_id`가 이전 attempt인 OPEN/terminal projection을 삭제한다. 구현 B는 snapshot-scoped 후보 outcome만 삭제한다. 그런데 어느 행이 “attempt provenance 임시행”이고 어느 행이 여러 거래일에 걸친 운영 projection인지 식별하는 컬럼/수명 규칙이 없다. 같은 close logical run 재시도만으로 기존 OPEN position과 terminal 집계가 사라질 수 있다.
- **강화안:** snapshot 산출물과 장기 outcome 장부를 물리적으로 분리한다. non-canonical cleanup 대상은 `candidate_tags`, `bias_metric_draft`, `candidate_source_contrib_draft`처럼 attempt-scoped draft 테이블로 한정한다. `candidate_outcome`과 `outcome_observations`는 절대 cleanup하지 않고, canonical publication RPC만 outcome command/event를 append하게 한다. projection 재구축 규칙, event identity, duplicate command key `(logical_run_key, ticker, strategy, command_type)`를 명시한다. AD-19의 `candidate_outcome 삭제` 문구는 제거해야 한다.

### ADV-05 — restore_epoch 절차는 PITR 뒤 단조성과 불변성을 보장하지 못한다

- **심각도:** CRITICAL
- **해당 AD:** AD-9, AD-16, AD-17
- **충돌 시나리오:** PITR은 DB를 과거 시점으로 되돌리므로 DB 내부의 “epoch 증가” 기록도 함께 되돌아간다. 서로 다른 restore worker는 복구된 `MAX(epoch)+1`을 택하거나 복구 전 production 값을 기억해 +1 할 수 있어 같은 복구에 다른 epoch를 부여한다. 더구나 모든 provenance 테이블의 `restore_epoch`를 일괄 증가시키는 것은 immutable outcome/current fact를 in-place 수정한다. metrics가 `candidate_source_contrib`의 MAX만 기준으로 필터링하므로 해당 epoch에 contribution 행이 없으면 outcome/correction/bias 데이터가 전부 누락되거나 서로 다른 테이블 epoch가 섞인다. “staging epoch를 production과 동일하게 설정”도 어느 시점의 어떤 권위를 복사하는지 없다.
- **강화안:** 복원되는 DB 밖의 durable control plane에 monotonic `recovery_generation`을 발급하거나, 복구 직후 별도 `recovery_epochs(epoch_id, restored_from_ts, activated_at, operator, manifest_hash)` 행을 append하고 모든 새 write가 active epoch FK를 갖게 한다. 과거 ledger 행을 mass update하지 않는다. view는 각 테이블의 MAX가 아니라 단일 active epoch/복구 manifest와 명시적 포함 범위를 사용한다. restore/correction 선택, schedule 정지, restore, epoch activation, pointer 검증, schedule 재개의 fencing protocol과 재실행 멱등 키를 문서화해야 한다.

### ADV-06 — dispatch outbox가 dual-write gap과 GitHub 수신 확인을 실제로 닫지 못한다

- **심각도:** CRITICAL
- **해당 AD:** AD-3, AD-7, AD-18
- **충돌 시나리오:** 문서는 idempotency row와 outbox row가 같은 DB transaction에 생성된다고 명시하지 않는다. 구현 A는 둘을 순차 insert하다 장애가 나고, 구현 B는 한 transaction으로 묶는다. 이후 GitHub dispatch 호출은 성공했지만 응답 저장 전에 worker가 죽을 수 있다. 문서가 가정한 `github_dispatch_id`와 “실제 dispatch 상태 조회”의 correlation 계약이 없으므로 reconciler는 미발송인지 이미 수신된 dispatch인지 구별하지 못한다. `unknown` 상태에서 같은 요청 replay가 재발송인지 기존 결과 반환인지도 없다. 한편 “논리 실행 키당 단일 사용자/단일 시도”는 AD-3의 동일 논리 키 retry/attempt 증가와 충돌한다.
- **강화안:** idempotency와 outbox insert를 하나의 DB RPC/transaction으로 고정하고 outbox PK를 GitHub `client_payload`에 correlation ID로 전달한다. workflow 시작 즉시 별도 callback/receipt 테이블에 correlation ID와 `run_id`, Actions run 식별자를 기록하도록 한다. reconciler는 receipt 우선 조회 후 안전한 재발송 규칙을 적용한다. `pending/accepted/started/succeeded/failed/unknown` 전이, 각 상태의 replay 응답, lease/attempt_count/next_attempt_at/dead-letter, GitHub가 요청은 받았지만 workflow가 시작되지 않은 경우의 정책을 고정한다. manual “시도”는 dispatch request와 run attempt를 분리해 용어와 cardinality를 재정의한다.

### ADV-07 — run 상태 머신의 획득·취소·재시도 mutation protocol이 완결되지 않았다

- **심각도:** HIGH
- **해당 AD:** AD-3, AD-10, AD-13, AD-15
- **충돌 시나리오:** GitHub `cancel-in-progress: true`가 이전 job을 종료하는 시점과 새 job의 DB lock/attempt 생성 시점은 원자적이지 않다. 이전 attempt는 `running`으로 남을 수 있다. 문서는 재시도 시작 시 이전 stage를 삭제하거나 superseded로 표시하라고 두 선택지를 주고, stale worker 차단은 fence 자격 검사에 맡긴다. 구현 A는 삭제하고 구현 B는 마킹한다. read model과 운영 지표의 이력/카운트가 달라진다. 또한 `canonical_attempt_run_id`가 attempt 시작 때 새 run을 뜻하는지 success publication 때 winner를 뜻하는지 AD-3과 AD-15에서 용도가 다르다.
- **강화안:** `active_attempt_run_id`와 `canonical_success_run_id`를 분리한다. `start_attempt(logical_key, trigger, expected_active)` RPC가 lock, attempt_no, fence 발급, 이전 active의 `superseded/cancelled` 전이, latest_partial reset을 원자적으로 수행하게 한다. stage 행은 삭제하지 않고 terminal reason을 보존한다. lease/heartbeat/expiry와 orphan reaper, allowed transition table, retryable result_code 목록, CAS 실패 응답을 정의한다. stage writer는 `(run_id, stage, fence_token)`과 writer lease를 포함한 단일 finalize RPC만 사용하도록 한다.

### ADV-08 — 후보/source/절단의 canonical shape과 결정 입력이 부족해 같은 모집단을 재현할 수 없다

- **심각도:** HIGH
- **해당 AD:** AD-2, AD-6, AD-12, AD-15, AD-16
- **충돌 시나리오:** “t1859 또는 fallback 모집단”이 fallback 대체, 합집합, 우선순위 merge 중 무엇인지 없고, AD-9/16은 composite fallback 가중치를 허용하지만 weight 산식과 primary source 선택 규칙이 없다. 거래대금 내림차순 절단도 거래대금의 기준 거래일, null/음수/정정값 처리, decimal 정규화, 중복 ticker merge 전후 중 어느 시점에 적용하는지 없다. 구현 A는 source별 후보를 합친 뒤 ticker dedupe하고 절단하고, 구현 B는 source별 절단 후 합친다. 둘 다 150 상한과 tie-break를 지키지만 후보, provenance, bias가 다르다.
- **강화안:** versioned screen contract를 DDL/의사코드로 고정한다. 최소한 source 호출 우선순위와 fallback 조건, raw candidate identity, ticker dedupe key, source merge 순서, contribution weight 산식/합계, primary source tie-break, 거래대금 기준 시점/통화/scale/null 정책, 절단 적용 단계, `screen_algorithm_version`과 input hash를 명시한다. 골든 fixture로 Python screen 결과와 SQL/read-model의 candidate/source/weight/truncated_count가 byte-equivalent인지 검증한다.

## 통과를 위한 최소 보완 순서

1. ADV-01의 publication/outcome transaction을 먼저 닫는다. 정상 close run의 성공 경로가 현재는 존재하지 않는다.
2. ADV-02/03에서 provenance 저장 권위를 하나로 선택하고 실행 가능한 DDL로 고정한다.
3. ADV-04에서 장기 outcome ledger를 attempt-scoped cleanup에서 분리한다.
4. ADV-05의 복구 generation 권위를 restored DB 밖 또는 별도 activation manifest로 고정한다.
5. ADV-06/07의 dispatch receipt 및 run acquisition 상태 머신을 RPC 수준 계약으로 완결한다.

이 다섯 항목이 해결되고 충돌 시나리오별 migration/integration fixture가 추가되기 전에는 architecture gate를 통과시키면 안 된다.
