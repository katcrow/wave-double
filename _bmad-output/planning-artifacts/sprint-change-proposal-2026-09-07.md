# Sprint Change Proposal — 종가배팅 후보 탐지 기법 1종 추가 (전략 F, OR 확장 + 배지)

## 1. Issue Summary

Neo가 백테스트로 검증한 신규 종가배팅 후보 탐지 기법 1종(**전략 F — 각도 가속·이평선 쌍바닥 기법**)을 기존 전략 A/B/C/D/E 태깅에 **OR 조건으로 추가**하고, 후보 카드에 매칭된 모든 전략을 배지로 표시하고자 한다.

- **전략 F (각도 가속·이평선 쌍바닥 기법, 표본 확대형 파라미터 채택)** — 근거: `docs/각도가속_이평쌍바닥기법_추가.md`
  로그가격 30봉 최소제곱 선형회귀 기울기가 5봉 전 대비 0.004 이상 가속(상승 각도 가팔라짐) ∩ 이평선(MA16) 쌍바닥(국소 저점 2개, 높은 저점) 후 넥라인 상향 돌파 / TP 3% · SL 4%(고정, tp_first=True) · 최대보유 없음, 왕복 비용 0.1%.

**발견 경위:** 신규 스토리 실패가 아니라 Neo가 별도로 진행한 백테스트 리서치(`docs/각도가속_이평쌍바닥기법_추가.md`)에서 새로운 후보가 확인되어 제안됨. 2026-09-04(전략 D/E 추가)와 완전히 동일한 유형 — 체크리스트 분류상 **"신규 요구사항이 이해관계자로부터 발생"**에 해당한다.

**선행 작업 이미 완료(중요, 지난번과의 차이):** 이번 correct-course 착수 시점에 이미 다음이 미커밋 상태로 완료되어 있다.

- `backtest/indicator_opt/strategy_f.py` — `StrategyFParams`(slope_window=30, accel_window=5, min_slope_delta=0.004, ma_db_window=16, TP 3%/SL 4%, tp_first=True, max_holding_bars=None, cost_rate=0.0005) 및 계산 로직 구현
- `backtest/indicator_opt/_signals.py`에 범용 `_linreg_slope`/`_double_bottom_signal` 추가(전략 F 전용이 아닌 재사용 가능한 신호 유틸리티로 구현됨), `engine.py`/`test_engine.py` 소폭 확장
- `backtest/tests/test_strategy_f.py` — 13개 테스트 전체 통과 확인(본 세션에서 재실행 검증)
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md`에 "전략 F" 절이 file:line 근거와 함께 이미 작성됨: **승률 70.10%, PF 1.6585, 199건 시그널/194건 거래, 평균수익 +0.8072%, 평균보유 1.94봉, 월간 2.66건, fingerprint `b2e0...12e73a3`, 결정: 유지.**
  - 참고: 문서(`docs/각도가속_이평쌍바닥기법_추가.md`)가 보고한 표본 확대형 수치(승률 73.1%/PF 1.92/182건/월 2.8건)와 코드 재현 수치(70.10%/1.6585/194건/월 2.66건)는 정확히 일치하지 않으나, `backtest-baseline.md`가 이미 코드 재현치를 authoritative 값으로 채택하고 "결정: 유지"로 마무리한 상태다 — D/E 때와 같은 패턴(승률>50%, PF>1 기준 충족)이므로 이번 correct-course에서 재검토하지 않는다.

즉 에픽 6의 Story 6.1/6.2("계산 로직 코드화 & baseline 이식")에 해당하는 작업은 **이미 끝나 있다.** 남은 작업은 6.3~6.8에 해당하는 DB 스키마/API 일반화/outcome 파라미터화/UI/OOS 검증뿐이다.

**핵심 충돌:** 이 요청은 PRD §7/§8.2가 "전략 확장"을 V2+로 미뤘던 조항을 2026-09-04에 이미 한 차례 뒤집었고, 이번은 그 편입 대상을 A/B/C/D/E → **A/B/C/D/E/F**로 다시 확장하는 것이다. 다중 태그/배지 인프라(Epic 2, Epic 6)는 이미 가변 개수 전제로 설계되어 있어 확장에 유리하지만, DB 제약·라벨맵·라우트가 여전히 5개(A/B/C/D/E)로 하드코딩되어 있다.

## 2. Impact Analysis

### Epic Impact

| Epic | 상태 | 영향 |
| --- | --- | --- |
| Epic 1 (배치 인프라) | done | 영향 없음 |
| Epic 2 (전략 태깅 & 카드 UI) | done | 영향 없음 — 재오픈하지 않음(에픽 6과 동일 원칙) |
| Epic 3 (outcome 자동 적재) | in-progress | 간접 영향만 — `candidate_outcome`은 strategy를 문자열로 다루므로 로직 변경 없음 |
| Epic 4 (수급/힌트, in-progress·backlog 다수) | 영향 있음 | Story 4.10 "힌트 배지 통합 필터"가 전략 필터 옵션에 F 포함해야 함 |
| Epic 5 (실전 성과 검증, backlog) | 영향 있음 | FR9 "전략별+전체 대조", FR10 편향 지표가 A/B/C/D/E 고정 가정 — F 백테스트 기대치가 있어야 대조 가능 |
| Epic 6 (전략 D/E 통합) | done | 영향 없음 — 재오픈하지 않음. 산출물(다중 태그 스키마, `compute_abc`, `StrategyTagList`, 전략별 outcome 파라미터화)을 재사용 |

**신규 에픽 필요**: 기존 Epic 6을 재오픈하는 대신 **Epic 7: 전략 확장 — 신규 후보 탐지 기법(F) 통합**을 신설해 확장분을 담는다.

**시퀀싱**: Epic 7은 Epic 4/5보다 먼저 완료되어야 한다(에픽 6과 동일 사유 — 그렇지 않으면 Epic 5가 5-전략 가정으로 구현된 뒤 다시 고쳐야 함). Epic 3은 순서 무관.

### Artifact Conflicts

- **PRD 충돌 (Action-needed)**: §1 Vision("5종 매수 전략 A·B·C·D·E"), §3 Glossary(전략 A/B/C/D/E), §4.2 FR-3 본문("전략 A/B/C/D/E"), §8.1 In Scope 문구가 모두 5종 고정 표현이라 6종 일반화 필요. §7 Non-Goals는 이미 "전략 종류 확장은 V1 편입"으로 열려 있으므로 신규 철회 조항은 불필요 — 문구만 F 추가로 갱신.
- **Architecture Spine 충돌 (Action-needed)**: AD-5 addendum이 "A/B/C/D/E 5개 시그널 키"로 특정되어 있음. `StrategyResult`가 F까지 6개 키를 포함하도록 addendum에 소규모 추가 필요. `apps/web/lib/strategy-labels.ts`의 `STRATEGY_LABEL`, `/strategies/[strategy]` 라우트도 F 추가 필요.
- **UX 문서 충돌 (경미)**: DESIGN.md/EXPERIENCE.md가 이미 "A/B/C/D/E(가변 개수)"로 표현돼 있어(에픽 6에서 일반화됨) 문구 자체는 최소 수정("A/B/C/D/E" → "A/B/C/D/E/F" 예시 텍스트만 갱신). 배지 색상 접근성(UX-DR14) 재확인 필요.
- **backtest-baseline.md**: 이미 F 절이 존재하므로 추가 코드화 불필요. **OOS(워크포워드) 검증 완료(2026-09-08, Story 7.7)** — D/E(Story 6.8)와 같은 방식으로 in-sample(2020-08-03~2024-08-27)/OOS(2024-08-28~2026-08-27) 재실행 결과가 `backtest-baseline.md` F절 "OOS(워크포워드) 검증" 하위 절에 병기되었다: 승률 75.32%→67.03%(−8.29%p), PF 2.1592→1.4382, 거래수 77건→91건. 열화는 있으나 승률·PF 모두 실전 채택 기준을 상회해 **결정: 유지**.
- **DB 마이그레이션(Action-needed)**: `candidate_tags_strategy_check` 제약(`202609051500_finalize_candidate_tags_strategy_contract.sql`이 최종 확정한 A|B|C|D|E)을 A|B|C|D|E|F로 확장하는 forward-only migration 필요(AD-14). `outcome_strategy_rules`(Story 6.5/`202609051600_parameterize_outcome_strategy_rules.sql`)에 F의 TP3%/SL4%/무제한보유 행 추가 필요.
- **골든 픽스처**: `golden_signals.json`에 F 키 추가, 참조 구현은 이미 있는 `strategy_f.py`.

## 3. Recommended Approach

**선택: Option 1 (Direct Adjustment).**

- 에픽 6이 구축한 인프라(다중 태그 스키마, `compute_abc` 일반화 패턴, 전략별 outcome 파라미터화, UI 라벨맵)가 이미 "전략 개수는 가변"을 전제로 설계되어 있어, F 추가는 스키마·아키텍처 재설계 없이 값만 확장하면 된다.
- Option 2(롤백)는 대상 없음. Option 3(MVP 전체 재검토)는 과함 — 이번 변경은 FR3 서브스코프의 반복 확장이다.

**Effort:** Low~Medium — 계산 로직 코드화(에픽 6의 6.1/6.2에 해당)가 이미 끝나 있어, 남은 작업은 DB 제약 확장·API 일반화·outcome 파라미터 추가·UI 라벨 추가·OOS 검증뿐이다. 에픽 6 대비 작업량이 적다.

**Risk:** Medium → **검증 완료(2026-09-08)** — F도 D/E와 마찬가지로 OOS(워크포워드) 미검증 상태로 편입 검토 중이었으나, Story 7.7에서 in-sample/OOS 재실행을 완료했다(`backtest-baseline.md` F절 참조, 결정: 유지). 낮은 수준의 잔여 리스크(200건 누적 재평가 트리거로 관리 중)로 남아 있다.

## 4. Detailed Change Proposals

### 4.1 PRD — `_bmad-output/planning-artifacts/prds/prd-wave-double-2026-08-31/prd.md`

**§1 Vision**
```
OLD: Neo는 백테스트로 검증해 확정한 **5종 매수 전략(A·B·C·D·E)**을 보유하고 있습니다. A/B/C는 73개월·104종목
데이터에서 승률 66~69%, PF 1.82~2.08을 기록했습니다. D(돌파3%기법)는 승률 83.1%(총거래 77건), E(익절2%_고정SL5%
기법)는 승률 78.2%·PF 1.34(총거래 78건)를 기록했다(2026-09-04 Correct Course로 V1 편입, §7 참조).

NEW: Neo는 백테스트로 검증해 확정한 **6종 매수 전략(A·B·C·D·E·F)**을 보유하고 있습니다. A/B/C는 73개월·104종목
데이터에서 승률 66~69%, PF 1.82~2.08을 기록했습니다. D(돌파3%기법)는 승률 83.1%(총거래 77건), E(익절2%_고정SL5%
기법)는 승률 78.2%·PF 1.34(총거래 78건)를 기록했다(2026-09-04 Correct Course로 V1 편입, §7 참조). F(각도 가속·
이평선 쌍바닥 기법)는 승률 70.10%·PF 1.6585(총거래 194건)를 기록했다(2026-09-07 Correct Course로 V1 편입, §7 참조).
```

**§3 Glossary — 전략 태깅**
```
OLD: **전략 태깅(Strategy Tagging)** — 후보 모집단 한정으로 전략 A/B/C/D/E 시그널을 계산해 종목에 부여하는 표시.
NEW: **전략 태깅(Strategy Tagging)** — 후보 모집단 한정으로 전략 A/B/C/D/E/F 시그널을 계산해 종목에 부여하는 표시.
```

**§4.2 FR-3 제목 및 본문**
```
OLD: #### FR-3: 전략 A/B/C/D/E 시그널 계산 및 태깅
NEW: #### FR-3: 전략 A/B/C/D/E/F 시그널 계산 및 태깅

OLD: [시스템]이 [후보 모집단 한정]으로 [전략 A/B/C/D/E 시그널]을 계산하고 ... 전략 D(돌파3%기법)·E(익절2%_고정SL5%
기법)는 2026-09-04 Correct Course로 A/B/C와 동일한 OR 결합·다중 배지 대상에 편입되었다 ...
NEW: [시스템]이 [후보 모집단 한정]으로 [전략 A/B/C/D/E/F 시그널]을 계산하고 ... 전략 D(돌파3%기법)·E(익절2%_고정
SL5%기법)는 2026-09-04 Correct Course로, 전략 F(각도 가속·이평선 쌍바닥 기법)는 2026-09-07 Correct Course로
A/B/C와 동일한 OR 결합·다중 배지 대상에 편입되었다 — F의 파라미터·기대치는 `docs/각도가속_이평쌍바닥기법_추가.md`
(표본 확대형 채택) 및 `backtest-baseline.md` F절 참조.
```

**§4.2 FR-3 Consequences — 골든 픽스처 문구**
```
OLD: 신규 태깅 로직의 A/B/C/D/E 시그널 집합을 각각의 참조 구현(A/B/C는 `screen_abc.py`, D/E는 신규 코드화된
백테스트 함수) 결과와 대조하는 회귀 테스트를 둔다.
NEW: 신규 태깅 로직의 A/B/C/D/E/F 시그널 집합을 각각의 참조 구현(A/B/C는 `screen_abc.py`, D/E/F는 신규
코드화된 백테스트 함수) 결과와 대조하는 회귀 테스트를 둔다.
```

**§8.1 In Scope**
```
OLD: - 전략 A/B/C/D/E 시그널 태깅(후보 모집단 한정), 태깅된 후보만 노출, **골든 픽스처 회귀 대조**
     - **전략 D(돌파3%기법)·E(익절2%_고정SL5%기법) 시그널 태깅** — 전략 A/B/C와 OR 결합, 다중 배지 표시
       (FR-3 확장, 2026-09-04 Correct Course, Epic 6)
NEW: - 전략 A/B/C/D/E/F 시그널 태깅(후보 모집단 한정), 태깅된 후보만 노출, **골든 픽스처 회귀 대조**
     - **전략 D(돌파3%기법)·E(익절2%_고정SL5%기법) 시그널 태깅** — 전략 A/B/C와 OR 결합, 다중 배지 표시
       (FR-3 확장, 2026-09-04 Correct Course, Epic 6)
     - **전략 F(각도 가속·이평선 쌍바닥 기법) 시그널 태깅** — 전략 A/B/C/D/E와 OR 결합, 다중 배지 표시
       (FR-3 확장, 2026-09-07 Correct Course, Epic 7)
```

**§9 Success Metrics 표 — 전략 확장 행 추가**
```
NEW 행 추가: | 전략 확장(전략 F)은 V2+ | **철회 후 재작성(2026-09-07)** — Correct Course로 전략
F(각도 가속·이평선 쌍바닥 기법)가 V1 편입. F는 OOS 워크포워드 검증을 완료(2026-09-08, Story 7.7 —
승률 75.32%→67.03%, PF 2.1592→1.4382, 결정: 유지)했으며 해당 리스크는 해소됨
(sprint-change-proposal-2026-09-07.md 및 backtest-baseline.md F절 참조) |
```

**Rationale:** §7 Non-Goals는 2026-09-04에 이미 "전략 종류 확장은 V1"으로 열려 있어 재작성이 불필요하다. 나머지는 A/B/C/D/E → A/B/C/D/E/F 표기 갱신과 F의 근거 문서 참조 추가뿐이다.

### 4.2 Architecture — `ARCHITECTURE-SPINE.md` AD-5 addendum

```
OLD Addendum (2026-09-04, Epic 6): 전략 D(돌파3%기법)·E(익절2%_고정SL5%기법) 추가 시 함수명 `compute_abc`는
하위호환을 위해 유지하되, 반환하는 `StrategyResult`가 A/B/C/D/E 5개 시그널 키를 모두 포함하도록 확장한다. ...

NEW Addendum 2 (2026-09-07, Epic 7): 전략 F(각도 가속·이평선 쌍바닥 기법) 추가 시 `StrategyResult`가
A/B/C/D/E/F 6개 시그널 키를 모두 포함하도록 확장한다. F는 고유 청산조건(TP3%/SL4%/최대보유 없음)을 가지므로,
`StrategyResult`의 전략별 청산 파라미터 노출 구조(Epic 6에서 이미 도입)에 F 항목을 추가하는 것으로 족하다
(신규 구조 도입 불필요).
```

### 4.3 UX — DESIGN.md / EXPERIENCE.md

가변 개수 전제로 이미 일반화되어 있으므로, "A/B/C/D/E(가변 개수)" 등 예시 문구에 F를 추가하는 최소 수정만 필요(문구 구조 변경 없음). 배지 색상 추가 시 UX-DR14(텍스트 라벨 병기) 재확인.

### 4.4 DB — 신규 forward-only migration

- `candidate_tags_strategy_check` 제약을 `A|B|C|D|E` → `A|B|C|D|E|F`로 확장 (에픽 6의 6.3/`202609051400_expand_candidate_tags_strategy_check.sql`, `202609051500_finalize_candidate_tags_strategy_contract.sql` 패턴 반복)
- `outcome_strategy_rules`(에픽 6의 6.5/`202609051600_parameterize_outcome_strategy_rules.sql`)에 F 행 추가: `tp_pct=3, sl_pct=4, cutoff_n=999999`(스키마가 `cutoff_n integer not null check (> 0)`이라 NULL 저장 불가 — sentinel 정수로 "무제한 보유"를 표현, 2026-09-07 조사로 확인)

### 4.5 신규 Epic 7 — 에픽/스토리 (epics.md에 추가)

```
## Epic 7: 전략 확장 — 신규 후보 탐지 기법(F) 통합

> 출처: 2026-09-07 Correct Course (sprint-change-proposal-2026-09-07.md). Epic 6(done)의 다중 태그
> 스키마/compute_abc 일반화/전략별 outcome 파라미터화 산출물을 재사용하며, Epic 6 자체는 재오픈하지 않는다.

시퀀싱 노트: Epic 4(Story 4.10)·Epic 5(Story 5.6, 5.12)보다 먼저 완료되어야 한다.

### Story 7.1: 전략 F 계산 로직 코드화 & 백테스트 baseline 이식 — 선행 완료됨
Given/When/Then: strategy_f.py, test_strategy_f.py(13 tests pass), backtest-baseline.md F절이
이미 존재·검증됨(승률 70.10%/PF 1.6585/194건). 본 스토리는 커밋 및 최종 확인만 남는다.

### Story 7.2: `candidate_tags` 전략 제약 확장 (A|B|C|D|E → A|B|C|D|E|F)
### Story 7.3: 전략 계산 API 일반화 (AD-5 addendum 2 확장, StrategyResult 6키)
### Story 7.4: Outcome 판정 로직 F 파라미터화 (TP3%/SL4%/무제한보유, outcome_strategy_rules 확장)
### Story 7.5: 후보 태깅 stage에 전략 F 반영
### Story 7.6: UI 확장 — 라벨·배지·라우트 (strategy-labels.ts, /strategies/[strategy])
### Story 7.7: OOS(워크포워드) 검증 — 전략 F in-sample/holdout 대조 — 완료(2026-09-08)
```

(스토리별 Given/When/Then은 Epic 6의 6.2~6.8을 F로 치환한 동일 골격 — Sprint Planning 단계에서 상세 AC를 확정한다.)

## 5. Implementation Handoff

**Change scope: Moderate** — 신규 에픽/스토리 추가와 backlog 재구성이 필요하나(PO/DEV 조정), PRD 근본 방향이나 아키텍처 패턴 자체는 바뀌지 않는다(에픽 6과 동일 분류).

- **PM**: PRD §1/§3/§4.2/§8.1/§9 갱신(위 4.1) 반영
- **Architect**: ARCHITECTURE-SPINE.md AD-5 addendum 2 추가(위 4.2)
- **UX**: DESIGN.md/EXPERIENCE.md 예시 문구에 F 추가(위 4.3)
- **Developer**: Epic 7 스토리 7.2~7.7 구현(7.1은 코드 확인 및 커밋만), migration 작성(위 4.4)
- **Neo**: 승인 후 `bmad-create-epics-and-stories`로 Epic 7 정식 문서화 → `bmad-sprint-planning`으로 sprint-status.yaml 갱신 → `bmad-build`로 스토리별 구현

**Success criteria**: 전략 F가 A/B/C/D/E와 동일하게 OR 결합·다중 배지로 대시보드에 노출되고, `backtest-baseline.md`에 OOS 검증 결과가 병기되며(Story 7.7, 2026-09-08 완료 — 승률 75.32%→67.03%, PF 2.1592→1.4382, 결정: 유지), 골든 픽스처 회귀가 F를 포함해 Jaccard ≥ 0.9로 통과한다.
