# epic-6-retro-item-24 — 6-5 review-patch migration의 guard 재정의 기록과 squash/pin 정책

- 작성일: 2026-09-09
- 대상: `infra/supabase/migrations/202609051600` ~ `202609052100` (Story 6.5)
- 회고 action: "6-5 review-patch migration(051700~052100)의 guard 재정의·의미 전환을 문서화하고,
  리뷰 반복 migration squash/pin 정책을 검토한다."

## 1. 무슨 일이 있었나

Story 6.5(전략별 outcome 판정 파라미터화) 한 스토리에서 리뷰 반복 때문에 forward migration이
**여섯 개** 쌓였고, 그 중 네 개가 같은 함수 `guard_outcome_strategy_snapshot()`을
`create or replace`로 다시 정의했다. 최종 상태만 보면 정상이지만, migration 목록만 훑으면
"같은 함수를 네 번 고쳤다"는 사실 외에 무엇이 왜 바뀌었는지 복원할 수 없다.

`sl_pct` CHECK 제약도 같은 스토리 안에서 이름과 범위가 두 번 바뀌었다.

## 2. guard 재정의 사슬 (의미 전환 기록)

| migration | `guard_outcome_strategy_snapshot()`에 일어난 의미 전환 |
| --- | --- |
| 202609051600 | 최초 도입. `candidate_outcome`의 직접 INSERT/UPDATE 스냅샷 값이 `outcome_strategy_rules`와 일치해야 한다. |
| 202609051700 | 경계 확장 — 직접 INSERT와 자연키 충돌까지 대상에 넣는다. 함께 `sl_pct < 100` CHECK를 `outcome_strategy_rules`/`candidate_outcome` 양쪽에 추가(제약명 `*_sl_pct_less_than_100_check`). |
| 202609051800 | **가로채기 순서 전환** — 정의되지 않은 전략(rule 행이 없는 값)은 guard가 도메인 오류로 가로채지 않고, 기존 `candidate_outcome_strategy_check`가 표준 CHECK 오류를 내도록 통과시킨다. "guard가 모든 것을 먼저 판정한다"에서 "스키마 CHECK가 먼저 말하게 한다"로 바뀐 지점이다. |
| 202609051900 | 함수 본문은 그대로. 트리거 함수는 RPC 표면이 아니므로 `public/anon/authenticated`의 EXECUTE를 회수한다(같은 migration에서 `reject_outcome_open_projection_conflict()`도 함께). |
| 202609052000 | 최종 보강. `sl_pct` 제약을 이름까지 정리해 하나로 고정(`*_sl_pct_check`/`*_sl_pct_less_than_100_check`를 `drop constraint if exists`로 제거하고 `*_sl_pct_range_check`로 통합: `> 0 and < 100` + 비유한값 배제). rebuild 오류 계약(`REBUILD: ...`)도 이 단계에서 확정. |
| 202609052100 | **legacy 호환 전환** — A/B/C의 기존 직접 fixture와 저장된 `cutoff_n`은 보존하고(cutoff 비교 대상에서 제외), D/E는 세 스냅샷 값(`tp_pct`/`sl_pct`/`cutoff_n`)을 모두 고정한다. 즉 "모든 전략을 동일하게 비교"에서 "전략군에 따라 비교 범위가 다르다"로 바뀐 지점이다. |

이후 Story 7.4의 202609080900이 같은 함수를 F까지 확장했고(비교 대상 전략 목록에 `'F'` 추가),
epic-6-retro-item-25의 202609091600이 `outcome_strategy_rules` 쪽에 별도의 감사 트리거를
추가했다(guard 본문은 건드리지 않음).

**현재 유효한 계약(최종 상태):**

- 세션 플래그 `wave_double.outcome_rule_override_allowed = 'on'`이면 통과한다(correction/rebuild 전용 우회).
- 스냅샷 4필드가 모두 그대로인 UPDATE는 통과한다(무관한 컬럼 갱신 허용).
- rule 행이 없고 전략이 A–F 밖이면 통과시켜 스키마 CHECK가 말하게 한다. A–F인데 rule 행이
  없으면 `OUTCOME_STRATEGY_RULE_NOT_FOUND`.
- `tp_pct`/`sl_pct`는 모든 전략에서 비교하고, `cutoff_n`은 **D/E/F에서만** 비교한다
  (A/B/C의 legacy cutoff correction 호환).
- 불일치는 `OUTCOME_STRATEGY_SNAPSHOT_MISMATCH`.

## 3. squash/pin 정책 검토 결과 — squash하지 않는다

검토한 선택지:

1. **적용된 migration을 squash한다** — 기각. AD-14는 forward-only이고 이 저장소는 운영
   프로젝트가 하나뿐이다(dev/staging 없음). 이미 `supabase_migrations.schema_migrations`에
   기록된 이름을 지우거나 합치면 로컬 목록과 운영 기록이 갈라지고, 그 불일치는 방금
   epic-3-retro-item-15로 세운 패리티 게이트가 곧바로 ERROR로 잡는다. 게이트를 우회하려고
   pin을 추가하는 것은 게이트의 목적을 스스로 훼손하는 일이다.
2. **미적용 상태에서만 squash한다** — 실효성 없음. 이 저장소의 리뷰 반복 migration은
   리뷰 중에 운영에 적용되면서 검증되므로, squash 가능한 창이 사실상 열리지 않는다.
3. **squash하지 않고 사슬을 문서로 고정한다(채택)** — migration 파일은 불변으로 두고,
   "같은 대상을 여러 번 재정의한 사슬"은 이 문서처럼 표로 남긴다.

**따라서 정책은 다음과 같다.**

- 적용된 migration은 squash·rename·삭제하지 않는다. 수정은 항상 새 forward migration이다.
  (이 세션의 `202609091500` → `202609091501` 패치가 그 예다.)
- 한 스토리에서 **같은 함수/제약을 두 번 이상 재정의하면**, 그 스토리의 회고 산출물에
  위와 같은 "의미 전환 표"를 남긴다. 파일 목록으로는 복원할 수 없는 정보이기 때문이다.
- 재정의하는 migration은 헤더 주석에 (a) 어떤 migration의 무엇을 바꾸는지, (b) 왜 바꾸는지,
  (c) 원본 파일은 손대지 않는다는 사실을 적는다. 202609032201과 202609091501이 이 형식의 선례다.
- 제약 이름을 바꿀 때는 `drop constraint if exists` + 새 이름으로 **한 migration 안에서**
  마무리한다(202609052000의 방식). 두 이름이 서로 다른 migration에 걸쳐 공존하면
  clean apply와 순차 apply의 결과가 갈라질 수 있다.
- pin(`tools/check_production_parity.py`의 `LOCAL_ONLY_MIGRATIONS`/`PROD_ONLY_MIGRATIONS`)은
  **이미 벌어진 이름 불일치를 기록하는 용도로만** 쓴다. 새 migration을 pin으로 가리는 것은
  금지한다. 각 pin 항목은 이유 문자열을 반드시 가진다(도구가 dict로 강제).

## 4. 이 정책이 지켜지는지 확인하는 방법

- `python tools/check_migration_order.py` — 파일명/순서 계약.
- `python tools/check_production_parity.py` — 커밋된 운영 스냅샷 대비 역방향 drift.
- `.github/workflows/test.yml`의 `N/N-1 forward-upgrade schema parity` — 순차 apply와
  clean apply의 스키마가 같은지(제약 이름 전환이 여기서 걸린다).
- `production-parity-gate` 잡 — default branch에서 live 운영 대비 미배포 migration/함수 차단.
