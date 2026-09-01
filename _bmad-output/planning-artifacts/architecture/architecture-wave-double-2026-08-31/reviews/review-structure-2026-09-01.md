# Editorial Structure Review — wave-double V1 Architecture Spine

이 문서는 인간 구현자와 리뷰어가 wave-double의 전체 구조를 빠르게 이해하고, 서로 다른 구현 단위가 따라야 할 불변 계약을 찾아 일관되게 구현하도록 돕기 위해 존재한다.

- **선택한 구조 모델:** Explanation (Conceptual) — `Definition/Paradigm → Context/Map → Concrete contracts` 순서가 주 구조이며, AD 목록은 그 아래의 reference layer로 취급
- **측정 기준:** 총 7,321 words (`word_metrics.py` 실측). 주요 구간은 AD-3 499, AD-5 452, AD-6 423, AD-9 393, AD-15 219, AD-16 354, AD-17 576, AD-18 455, AD-19 243, Deferred 521 words.
- **검토 범위:** 아이디어와 기술 결정은 그대로 두고, 인간 독자의 탐색성·진행 순서·중복·문서 경계만 검토

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| structure | `## Invariants & Rules` 아래 AD-1~19가 5,206 words 규모의 단일 평면 목록으로 이어짐 | **MOVE** AD ID는 유지한 채 네 묶음으로 재배치: `Runtime & ownership`(AD-1/2/11/14), `Batch lifecycle & publication`(AD-3/4/6/10/13/15/18), `Strategy, outcome & provenance`(AD-5/8/9/12/16/19), `Security & operations`(AD-7/17) | 현재 독자는 뒤의 AD가 앞의 어느 계약을 확장하는지 기억해야 한다. 주제별 H3/H4 scaffolding을 추가하면 conceptual model의 추상→구체 흐름과 random access가 함께 살아난다. 내용 삭제 없음, word impact 약 +20~30 words. |
| structure | `Capability → Architecture Map` 156 words가 모든 AD를 읽은 뒤에 등장 | **MOVE** `Design Paradigm` 바로 다음으로 이동하고, 각 capability 링크가 아래 themed AD 묶음으로 내려가게 함 | 독자가 세부 계약에 들어가기 전에 제품 범위와 구조의 대응을 얻어야 한다. 현재 위치는 orientation을 recap으로 소비한다. 절감 0 words. |
| structure | `Stack` 131 words와 `Structural Seed` 298 words가 AD-19 뒤에 등장 | **MOVE** Capability Map 다음, 상세 AD 이전으로 이동하여 `Stack & Structural Seed`라는 concrete context 층을 만듦 | AD 본문은 `apps/*`, `packages/domain`, `read-model`, migration, runner를 이미 사용한다. 정의가 사용 뒤에 와서 독자가 앞뒤로 이동한다. 절감 0 words. |
| structure | frontmatter의 `purpose`, `altitude`, `status`, `binds`와 본문 곳곳의 “seed 권위/Deferred” 설명 | **CONDENSE** 제목 아래 50~70 words의 `How to read this spine` 블록으로 재배치: 무엇이 binding invariant이고 무엇이 cold-start seed이며 무엇이 deferred인지 한 번만 설명 | 기계용 frontmatter만으로는 인간 독자가 문서 계층의 규범 강도를 알기 어렵다. 기존 설명을 옮겨 쓰면 순증가는 약 10~20 words에 그친다. |
| structure | AD-2(232), AD-5(452), AD-6(423), AD-12(169), AD-14(128)에서 migration, 120일 캐시, 150종목 절단을 반복 설명 | **MERGE** 각 사실의 단일 소유 AD만 상세 규칙을 유지하고 나머지는 `Governed by AD-x` 한 줄로 연결 | 동일한 120일/증분 캐시가 AD-5와 AD-6에, 150종목 절단이 AD-6과 AD-12에, migration 진화가 AD-2와 AD-14에 반복된다. 강화용 요약이 아니라 유지보수 지점이 둘 이상인 진짜 중복이다. 예상 절감 **110~150 words**. |
| structure | AD-9(393), AD-15(219), AD-16(354), AD-19(243)가 outcome identity, canonical attempt, source provenance와 canonical contribution shape를 여러 번 다시 서술 | **MERGE** 네 AD의 안정 ID와 각각의 `Binds/Prevents/Rule`은 보존하되, 공통 데이터 흐름은 하나의 `Canonical outcome & provenance contract` 표/도식으로 한 번만 제시하고 각 AD는 해당 행을 참조 | 총 1,209 words의 연속 구간에서 동일 entity와 lineage를 반복 재정의해 독자가 차이를 찾기 어렵다. 공통 shape를 한 곳으로 모으면 결정은 그대로 유지하면서 예상 **240~320 words** 절감. |
| structure | AD-17 576 words 안에 provider acceptance contract, restore epoch 설계, 분기별 GitHub Actions 절차, smoke test, 알림 채널이 한 수준으로 섞임 | **MOVE** spine에는 복구 불변식과 acceptance criteria만 남기고, `restore_epoch` 상세와 자동화 단계는 `OPERATIONS-RECOVERY.md` 같은 companion runbook으로 이동; AD-17은 링크와 failure boundary만 유지 | architecture decision과 운영 실행 절차가 한 섹션에서 경쟁한다. 인간 독자는 먼저 무엇이 반드시 참이어야 하는지 알아야 하고, drill 작업자는 별도 runbook에서 순서를 찾아야 한다. 본문 예상 절감 **250~330 words**(내용은 companion에 보존). |
| structure | AD-18 455 words 안에 idempotency contract, DB shape, outbox 상태, reconciler 구현 대안, 10초/30초 배포 수치, health check가 혼재 | **MOVE** spine에는 request identity, authoritative state machine, dual-write boundary만 남기고 reconciler 배포·polling·health 운영은 dispatch companion/runbook으로 이동 | 규범 계약과 worker 운용 설정을 분리하면 AD-18의 핵심을 한 번에 스캔할 수 있다. 본문 예상 절감 **150~210 words**(내용은 companion에 보존). |
| structure | AD-3/5/6/9/13/17/18/19만 `Binds/Prevents/Rule` 뒤에 schema, DDL, CI, cron, deployment 같은 서로 다른 보조 블록을 가짐 | **CONDENSE** 모든 AD의 첫 화면을 동일한 `Binds → Prevents → Rule → Enforcement reference` 형식으로 맞추고, 8개 장문 AD의 세부 블록은 바로 아래 compact table 또는 companion 링크로 분리 | AD catalog가 reference layer로 기능하려면 항목 schema가 일정해야 한다. 현재는 특정 AD의 Rule 경계가 어디서 끝나는지 눈으로 판단해야 한다. 별도 절감은 위 MOVE/MERGE 행에 포함하며 중복 계산하지 않음. |
| structure | `Deferred` 521 words에 현재 미결 항목, 장문의 hosting 평가표, 이미 해결된 항목의 취소선 이력이 함께 있음 | **MOVE** hosting 평가표는 `HOSTING_EVALUATION.md`로 옮기고 spine에는 선택 시점·필수 조건만 유지. **CUT** `해결된 이전 Deferred 항목`은 memlog/history로 이동 | Deferred는 현재 열려 있는 결정만 빠르게 보여야 한다. 해결 이력과 상세 평가 양식이 섞이면 무엇이 아직 행동을 요구하는지 흐려진다. 예상 절감 **150~210 words**. |
| structure | Design Paradigm의 dependency diagram, Structural Seed의 deployment diagram, Consistency Conventions 표 | **PRESERVE** 각각 `의존 방향`, `운영 데이터 흐름`, `횡단 규칙`이라는 다른 질문에 답하도록 현재 시각 자료를 유지 | 인간 독자에게 두 도식과 표는 장문 규칙을 압축하는 mental model이다. 겉보기 중복으로 잘라내면 탐색성과 이해가 나빠진다. 절감 0 words; comprehension trade-off를 피하는 보존 권고. |

## Summary

- **총 권고:** 11건 — MOVE 5, MERGE 2, CONDENSE 2, CUT 1(Deferred 행에 결합), PRESERVE 1
- **예상 본문 감소:** 약 **900~1,220 words**, 원문 7,321 words의 **12~17%**. 모두 수용하면 약 **6,100~6,420 words**.
- **길이 목표:** 별도 목표는 제공되지 않았다. 위 감소량은 결정 내용 삭제가 아니라 중복 제거와 runbook/companion 분리에서 나온다.
- **권장 최종 흐름:** `How to read → Design Paradigm → Capability Map → Stack & Structural Seed → themed Invariants → Consistency Conventions → Deferred`.
- **이해도 trade-off:** 도식·표·Binds/Prevents/Rule은 보존한다. 복구·dispatch 세부를 companion으로 옮길 때는 링크와 적용 조건을 남기지 않으면 random access가 악화되므로, 단순 삭제가 아니라 명시적 이동이어야 한다.
