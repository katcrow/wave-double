# Sprint Change Proposal — 종가배팅 후보 탐지 기법 2종 추가 (전략 D/E, OR 확장 + 배지)

## 1. Issue Summary

Neo가 백테스트로 검증한 신규 종가배팅 후보 탐지 기법 2종을 기존 전략 A/B/C 태깅에 **OR 조건으로 추가**하고, 후보 카드에 매칭된 모든 전략을 배지로 표시하고자 한다.

- **전략 D (돌파3%기법, 후보 A 파라미터 채택)** — 근거: `docs/돌파3%기법_추가.md`
  고점기간 N=20 / 거래량윈도우 W=3 / VMR=0.95 / MA_long=240 / RSI(10,6) 상향돌파 RSI_thr=42, RSI_min=30 / TP 3% · SL 5% · 최대보유 20일. 백테스트 승률 83.1%, 총거래 77건(월 1.1건).
- **전략 E (익절2%_고정SL5%기법, 문서 그대로 채택)** — 근거: `docs/익절2%_고정SL5%기법_추가.md`
  SMA20×60 골든크로스 ∩ OBV20일MA 상향돌파 ∩ ADX(14)≥20 / TP 2% · SL 5%(고정) · 최대보유 30일, 수수료 0.1%. 백테스트 승률 78.2%, PF 1.34, 총거래 78건(월 1.7건).

**발견 경위:** 신규 스토리 실패가 아니라 Neo가 별도로 진행한 백테스트 리서치(위 두 문서)에서 새로운 후보가 확인되어 제안됨. 체크리스트 분류상 **"신규 요구사항이 이해관계자로부터 발생"**에 해당한다.

**핵심 충돌:** 이 요청은 기존 PRD(§7 Non-Goals, §8.2 Out of Scope)가 명시적으로 **"전략 확장(전략 D...) — V2+"**로 미룬 항목을 V1으로 앞당기는 것이다. 조사 결과(Explore agent), 후보 태깅 인프라(Epic 2, done)는 이미 다중 태그/배지 구조로 설계돼 있어 확장에 유리하지만, DB 제약·라벨맵·라우트가 A/B/C 3개로 하드코딩되어 있고, PRD가 요구하는 "백테스트 코드에서 확인된 값"(file:line 근거)이 전략 D/E에는 아직 없다(두 문서는 markdown 리서치 메모이며 `backtest/` 코드로 이식되지 않음).

## 2. Impact Analysis

### Epic Impact

| Epic | 상태 | 영향 |
| --- | --- | --- |
| Epic 1 (배치 인프라) | done | 영향 없음 |
| Epic 2 (전략 태깅 & 카드 UI) | done | **재사용됨, 재오픈하지 않음** — `candidate_tags`/`StrategyTagList`/`compute_abc` 패턴이 확장 대상이나, 이미 종료·회고된 에픽이므로 새 에픽으로 확장분을 분리 |
| Epic 3 (outcome 자동 적재) | in-progress | 간접 영향만 — `candidate_outcome`은 이미 strategy를 문자열로 다루므로 로직 변경 없음. CHECK 제약 확장 시점만 조율 필요 |
| Epic 4 (수급/힌트, backlog) | 영향 있음 | Story 4.10 "힌트 배지 통합 필터"가 전략 필터 옵션에 D/E 포함해야 함 |
| Epic 5 (실전 성과 검증, backlog) | 영향 있음 | FR9 "전략별+전체 대조", FR10 편향 지표가 A/B/C 고정 가정 — D/E 백테스트 기대치가 있어야 대조 가능 |

**신규 에픽 필요**: 기존 Epic 2를 재오픈하는 대신 **Epic 6: 전략 확장 — 신규 후보 탐지 기법(D/E) 통합**을 신설해 확장분을 담는다(완료·회고된 에픽 재오픈은 피하고, 의존은 Epic 2 산출물 재사용으로 명시).

**시퀀싱**: Epic 6은 Epic 4/5보다 먼저 완료되어야 한다(그렇지 않으면 Epic 5가 3-전략 가정으로 구현된 뒤 다시 고쳐야 함). Epic 3은 순서 무관.

### Artifact Conflicts

- **PRD 충돌 (Action-needed)**: §7/§8.2 "전략 확장(전략 D...) — V2+" Non-Goal을 이번 변경으로 **명시적으로 뒤집는다**. §1 Vision("3종 전략 A·B·C"), §3 Glossary("전략 A/B/C"), §4.2 FR-3 본문이 모두 A/B/C 고정 표현이라 5종 일반화 필요.
  - **범위는 좁게 유지**: "조건검색식 추가"(신규 후보 모집단 원천)는 여전히 V2+ 유지. 이번 확장은 **기존 t1859 모집단 위에 시그널 종류만 추가**하는 것이라, Non-Goal 전체가 아니라 "전략 D..." 부분만 되돌린다.
- **Architecture Spine 충돌 (Action-needed)**: AD-5 "`compute_abc(frame) -> StrategyResult`가 유일 entrypoint"는 함수명·반환 형태가 A/B/C 3종에 특정되어 있음. `apps/web/lib/strategy-labels.ts`의 `STRATEGY_LABEL`, `/strategies/[strategy]` 라우트 검증도 하드코딩. 소규모 addendum으로 처리 가능(전면 재설계 아님).
- **UX 문서 충돌 (Action-needed, 경미)**: UX-DR7/UX-DR9/UX-DR16이 "A/B/C" 문구를 직접 명시. 가변 개수 전략을 전제로 문구 일반화 필요. 배지 색상 추가 시 접근성 대비(UX-DR14) 재확인.
- **backtest-baseline.md 충돌 (Action-needed, 선행 필수)**: PRD는 "판정 룰·비용·산식은 추정이 아니라 `backtest/` 실제 코드에서 확인한 값"이라고 못박음. 전략 D/E는 현재 `docs/*.md`의 리서치 메모일 뿐 `backtest/indicator_opt/`에 코드로 존재하지 않는다. **golden fixture 회귀(FR-3, Jaccard≥0.9)를 D/E까지 확장하려면 먼저 D/E 계산 로직을 코드화하고 baseline 문서에 file:line 근거를 남겨야 한다.**
- **DB 마이그레이션(Action-needed)**: `candidate_tags.strategy` CHECK 제약을 `A|B|C` → `A|B|C|D|E`로 확장하는 forward-only migration 필요(AD-14).
- **두 문서 자체가 요구하는 선행 절차**: 두 문서 모두 "향후 계획"에서 **OOS(워크포워드) 검증을 PRD 작성 전에 실시**하라고 명시. Neo가 이번에 파라미터를 확정(돌파3%=후보A, 익절2%_고정SL5%=문서 그대로)했으나 OOS 검증 자체는 당시 아직 수행되지 않았다 — 배치 리스크로 기록. **[2026-09-07 갱신] Story 6.8로 검증 완료.** D는 in-sample 승률 76.92%/PF 1.8954(13건) → OOS 승률 75.00%/PF 1.7059(4건)로 열화가 작아 유지 결정. E는 in-sample 승률 80.00%/PF 1.4902(15건) → OOS 승률 50.00%/PF 0.3725(4건)로 뚜렷한 열화가 관측되었으나 표본이 4건뿐이라 조건부 유지(모니터링 강화, 20건 누적 시 재평가) 결정. 상세는 `_bmad-output/specs/spec-wave-double/backtest-baseline.md`의 "OOS(워크포워드) 검증" 절 참조.

## 3. Recommended Approach

**선택: Option 1 (Direct Adjustment) + Option 3 요소(PRD MVP 범위 수정) 결합.**

- Option 1만으로는 부족하다 — PRD가 "전략 확장은 V2+"라고 **명시적으로** Non-Goal 처리했으므로, 새 스토리만 추가하고 PRD를 그대로 두면 문서와 구현이 모순된다. 따라서 PRD의 해당 Non-Goal 조항을 좁게(전략 종류 한정) 되돌리는 공식 수정이 함께 필요하다.
- Option 2(롤백)는 대상 없음 — 되돌릴 완료 스토리가 없다(불필요).
- Option 3 전체 MVP 재검토는 과함 — 나머지 MVP 범위(Epic 4/5 등)는 그대로 유효하며, 이번 변경은 FR3 하나의 서브스코프 확장이다.

**Effort:** Medium — 기존 다중 태그 인프라가 이미 확장을 전제로 설계돼 있어 스키마/UI 재설계는 없음. 신규 작업은 (a) D/E 계산 로직 코드화 + 골든픽스처, (b) 하드코딩 제약 3곳 확장, (c) PRD/Architecture/UX 문서의 A/B/C 표현 일반화.
**Risk:** Medium — PRD Non-Goal을 뒤집는 결정 자체는 낮은 리스크(사용자가 직접 승인)이나, D/E가 아직 OOS 미검증 상태로 프로덕션에 들어가는 것은 실전 승률이 백테스트 기대치와 괴리될 리스크를 안고 간다(§9 SM-C1 카운터 지표와 정면으로 관련). **[2026-09-07 갱신] Story 6.8에서 OOS 검증 완료 — D는 열화 미미, E는 뚜렷한 열화(표본 4건)가 관측되어 조건부 유지·모니터링 강화로 리스크를 관리 중(`backtest-baseline.md` 참조).**

## 4. Detailed Change Proposals

### 4.1 PRD — `prds/prd-wave-double-2026-08-31/prd.md`

**§7 Non-Goals**
```
OLD: 전략 확장(조건검색식 추가, 전략 D...) — V2+.
NEW: 조건검색식 추가(신규 후보 모집단 원천) — V2+. (전략 D/E 시그널 확장은 2026-09-04 Correct Course로 V1에 편입, §8.1 참조)
```
**§8.1 In Scope**에 추가:
```
전략 D(돌파3%기법)·E(익절2%_고정SL5%기법) 시그널 태깅 — 전략 A/B/C와 OR 결합, 다중 배지 표시(FR-3 확장)
```
**§1 Vision** "3종 매수 전략(A·B·C)" → "5종 매수 전략(A·B·C·D·E)"로 갱신, D/E의 백테스트 수치(83.1%/78.2%) 병기.
**§3 Glossary** "전략 태깅" 정의의 "전략 A/B/C" → "전략 A/B/C/D/E"로 일반화.
**§4.2 FR-3** 본문 "전략 A/B/C 시그널" → "전략 A/B/C/D/E 시그널"로 갱신, 골든 픽스처 회귀 대조 대상에 D/E 포함 명시.

**Rationale:** PRD의 문언적 Non-Goal과 실제 구현 방향이 어긋나는 것을 막기 위함. 범위를 "전략 종류"에만 한정해 "조건검색식 추가"는 여전히 V2+로 남겨 과확장을 방지.

### 4.2 Epics — `epics.md`

**FR Coverage Map**에 행 추가:
```
| FR3(확장) | Epic 6 | 전략 D/E 시그널 태깅 통합 |
```
**Epic List**에 추가:
```
| 6 | 전략 확장 — 신규 후보 탐지 기법(D/E) 통합 | FR3(확장) |
```

**신규 Epic 6 스토리 초안** (상세 AC는 이후 `bmad-create-epics-and-stories` 또는 직접 스토리 작성 세션에서 확정):

- **6.1** 전략 D(돌파3%) 계산 로직 코드화 & 백테스트 baseline 이식 — `backtest/indicator_opt/`에 신규 지표 함수, `backtest-baseline.md`에 D 파라미터·기대치(83.1%/77건) file:line 근거 기록
- **6.2** 전략 E(SMA GC×OBV×ADX 고정SL5%) 계산 로직 코드화 & baseline 이식 — 동일하게 E 파라미터·기대치(78.2%/PF1.34/78건) 기록
- **6.3** `candidate_tags.strategy` CHECK 제약 확장 마이그레이션(`A|B|C` → `A|B|C|D|E`, AD-14 forward-only)
- **6.4** `compute_abc` → 일반화된 전략 계산 API 확장(AD-5 addendum), 골든 픽스처에 D/E 시그널 추가, Jaccard 회귀 대상 확장
- **6.5** UI 확장 — `STRATEGY_LABEL`/`StrategyTagList`/`/strategies/[strategy]` 라우트에 D/E 추가, UX-DR7/9/16 문구 일반화 반영
- **6.6** Epic 4 Story 4.10(힌트 배지 통합 필터), Epic 5 Story 5.6(전략별 분리 view)에 D/E 반영 — **Epic 4/5보다 먼저 완료 필요(시퀀싱 노트)**
- **6.7** OOS(워크포워드) 검증 — 두 문서가 요구한 선행 절차, 프로덕션 반영 전 과적합 여부 확인 기록

### 4.3 Architecture — `ARCHITECTURE-SPINE.md`

**AD-5 addendum:**
```
OLD: 운영과 백테스트는 하나의 전략 API를 공유한다: `backtest.strategy_api.compute_abc(frame) -> StrategyResult`가 유일 entrypoint.
NEW: 운영과 백테스트는 하나의 전략 API를 공유한다: `backtest.strategy_api.compute_abc(frame) -> StrategyResult`가 유일 entrypoint이며, 전략 D/E 추가(2026-09-04 Correct Course) 시 함수는 유지하되 반환 `StrategyResult`가 A~E 5개 시그널 키를 모두 포함하도록 확장한다(호출자 breaking change 최소화).
```
**Rationale:** 함수명은 하위호환을 위해 유지하고 반환 스키마만 확장 — 기존 Epic 2/3 호출부 재작성 방지.

### 4.4 UX — `EXPERIENCE.md`

UX-DR7/UX-DR9/UX-DR16의 "A/B/C" 고정 문구를 "태깅된 전략 목록(가변)"으로 일반화하는 편집 필요(문구 예시는 실제 세션에서 D/E 표시 문구 확정 시 함께 갱신).

### 4.5 코드/스키마 변경 (구현 단계에서 수행, 이 세션은 계획만)

- `infra/supabase/migrations/` 신규 migration: `candidate_tags.strategy` CHECK 확장
- `apps/web/lib/strategy-labels.ts`: D/E 라벨 추가
- `apps/web/app/strategies/[strategy]/page.tsx`: 라우트 검증 목록 확장
- `backtest/indicator_opt/combine_strategies.py` 또는 신규 모듈: D/E 시그널 함수 추가
- `tests/fixtures/golden/golden_signals.json`: D/E 키 추가

## 5. Implementation Handoff

**Scope 분류: Moderate.** 엔지니어링 blast radius는 국소적(스키마 확장 + 계산 함수 추가 + UI 라벨 확장)이나, PRD Non-Goal을 공식적으로 뒤집는 결정이 포함되어 backlog 재구성이 필요하다.

- **PRD/Epics 문서 수정** — Neo 본인(PM 겸 개발자 역할) 승인 후 이 세션 또는 `bmad-prd`/`bmad-create-epics-and-stories`에서 실제 편집
- **Epic 6 스토리 상세화 & 스프린트 반영** — `bmad-sprint-planning` 또는 직접 sprint-status.yaml 갱신(§6.4 체크리스트 항목)
- **구현** — `bmad-build`로 Story 6.1부터 순차 진행(6.1/6.2가 6.3~6.6의 선행 조건)
- **OOS 검증(6.7, 재번호 후 6.8)** — 이 세션 범위 밖이었으나 **[2026-09-07 완료]** Story 6.8로 수행됨 — §6 Open Risk 갱신 및 `backtest-baseline.md` 참조

## 6. Open Risk (2026-09-07 Story 6.8로 검증 완료 — 상세는 backtest-baseline.md 참조)

- ~~전략 D/E는 아직 OOS(워크포워드) 검증 전이며, 각 소스 문서가 자체적으로 이 검증을 권고했다. 승인 시 "OOS 미검증 상태로 프로덕션 반영"이라는 리스크를 명시적으로 수용하는 것임을 기록한다.~~
- **[2026-09-07 검증 완료]** Story 6.8에서 `strategy_d.py`/`strategy_e.py`를 in-sample(2020-08-03~2024-08-27)/OOS(2024-08-28~2026-08-27)로 재실행했다. D: in-sample 승률 76.92%/PF 1.8954(13건) → OOS 승률 75.00%/PF 1.7059(4건), 열화 미미 → **유지** 결정. E: in-sample 승률 80.00%/PF 1.4902(15건) → OOS 승률 50.00%/PF 0.3725(4건), 뚜렷한 열화 관측(표본 4건으로 통계적 결론은 제한적) → **조건부 유지(모니터링 강화, OOS 표본 20건 누적 시 재평가)** 결정. 파라미터 재조정은 하지 않았으며(범위 밖), 필요 시 별도 스토리로 이관한다. 상세 표·해석·결정 근거는 `_bmad-output/specs/spec-wave-double/backtest-baseline.md`의 "OOS(워크포워드) 검증" 절(전략 D/E 각 절 하위) 참조. 잔존 리스크: E는 OOS 표본이 매우 작아 실전 승률이 이번 관측치보다 더 나쁠 가능성을 배제할 수 없으므로 계속 모니터링이 필요하다.

## 7. Approval & Implementation Record (2026-09-04)

**승인:** Neo가 "스스로 알아서 진행하세요"로 Batch 제안 전체를 승인.

**적용된 문서 변경:**
- `prds/prd-wave-double-2026-08-31/prd.md` — §1 Vision(5종 전략), §3 Glossary, §4.2 FR-3, §7 Non-Goals(전략 D 조항 철회), §8.1/8.2, §11 Assumptions Index
- `epics.md` — FR Coverage Map, Epic List, 신규 `## Epic 6: 전략 확장 — 신규 후보 탐지 기법(D/E) 통합`(Story 6.1~6.7), UX-DR7/9/16 문구
- `architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md` — AD-5 addendum(전략별 청산조건 포함하도록 `StrategyResult` 확장)
- `ux-designs/ux-wave-double-2026-08-31/EXPERIENCE.md` — Metric comparison, Flow 1/3 문구 일반화
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — `epic-6` 및 스토리 6.1~6.7 `backlog`로 등록

**미실행(다음 단계로 이월):**
- Epic 6 스토리 상세 AC 확정 및 실제 코드 구현(`bmad-build` 또는 `bmad-create-epics-and-stories`로 세분화)
- ~~Story 6.7 OOS 워크포워드 검증(이 세션 범위 밖, Neo가 별도 수행)~~ **[2026-09-07 완료, Story 6.8 — §6 Open Risk 참조]**
- `backtest-baseline.md`에 전략 D/E 절 추가(Story 6.1/6.2 구현 시점에 작성) — **[2026-09-07 완료]** OOS 하위 절도 Story 6.8로 함께 추가됨

**Scope 분류 확정:** Moderate. Handoff: PO/Developer(Epic 6 스토리 실행), Neo 본인(OOS 검증 — **[2026-09-07 Story 6.8로 완료]**).

## 8. Addendum (2026-09-04, 후속 조사) — Epic 3/6 시퀀싱 정정

**발견:** Epic 3(done)의 TP/SL 판정 SQL(`publish_attempt`, `202609032101_fix_timeout_cutoff_review_patch.sql` 등)이 TP/SL을 `1.03`/`0.97`(±3%)로, `cutoff_n`을 30으로 **모든 전략에 공통 하드코딩**하고 있음(`emit_open_command`가 `cutoff_n`을 세팅하지 않아 컬럼 기본값에 의존). `candidate_tags.params_meta`에는 TP/SL/최대보유 필드가 없음. A/B/C는 우연히 모두 TP3%/SL3%/30일이라 지금까지 드러나지 않았으나, D(TP3/SL5/20일)·E(TP2/SL5/30일)는 값이 달라 **이 하드코딩이 그대로면 전략별 청산조건을 반영할 수 없다.**

**조치:** Epic 6에 **Story 6.5(Outcome 판정 로직 전략별 파라미터화, Epic 3 확장)**를 신설해 기존 6.5~6.7을 6.6~6.8로 재번호. 6.5는 forward-only migration으로 전략별 `tp_pct`/`sl_pct`/`cutoff_n` 조회를 도입하며 Epic 3의 "done" 상태나 기존 A/B/C outcome 데이터는 변경하지 않는다(NFR-5).

**시퀀싱 결론:** Epic 3의 잔여 백로그(3-9 상장폐지, 3-10 projection 재구축 검증)는 전략 TP/SL과 무관해 Epic 6와 독립적으로 아무 순서로나 진행 가능하다. Epic 6 내부에서는 6.1/6.2(계산 로직) → 6.3(스키마) → 6.4(API) → **6.5(Epic 3 outcome 판정 확장)** → 6.6(태깅 stage 반영) → 6.7(UI) 순서가 강제되며, 6.8(OOS)은 6.1/6.2 이후 아무 때나 병행 가능하다.
