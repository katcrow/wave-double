---
title: 'OOS(워크포워드) 검증'
type: 'chore'
created: '2026-09-07'
status: 'done'
baseline_revision: '7f5fd70dc5bb0d44e3f1c091956243177a05e1bc'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      strategy_e.py는 data_fingerprint와 invalid_ohlcv_rows를 --start/--end
      윈도우 적용 전 원본 프레임에서 계산해, 서로 다른 관측창으로 실행해도
      두 값이 동일하게 나온다(strategy_d.py는 윈도우 적용 후 프레임에서 계산해 실행마다 값이 다름).
    evidence: |-
      strategy_e.py:308-316(frame 해시 후 start_ts/end_ts 필터링)과
      strategy_d.py:249-263(필터링 후 window 해시)을 대조해 확인.
      이번 스토리의 OOS in-sample/holdout 실행에서 실제로 E의 두 fingerprint가
      동일(b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3)하고
      invalid_ohlcv_rows도 동일(244)하게 관측되어 재현됨.
      Story 6.2(strategy_e.py 최초 구현) 범위의 기존 동작이며 이번 스토리에서
      코드를 수정하지 않았다.
    location: >-
      backtest/indicator_opt/strategy_e.py:308-316
    severity: low
---

<intent-contract>

## Intent

**Problem:** 전략 D/E는 `docs/돌파3%기법_추가.md`·`docs/익절2%_고정SL5%기법_추가.md`가 스스로 권고한 OOS(워크포워드) 검증 없이 이미 태깅·outcome 판정·UI에 반영되어(Story 6.1~6.7 완료) 프로덕션에 들어가 있다. `backtest-baseline.md`의 현재 D/E 수치는 전체 관측창(2020-08-03~2026-08-27) 단일 구간이라 과적합 여부를 판단할 별도 구간 대조가 없다.

**Approach:** 기존 `strategy_d.py`/`strategy_e.py` CLI(파라미터·엔진 변경 없음)를 관측창만 둘로 나눠 재실행한다 — in-sample `2020-08-03~2024-08-27`(4년), OOS(holdout) `2024-08-28~2026-08-27`(2년, 이후 데이터). 두 구간 결과를 `backtest-baseline.md`에 병기하고, in-sample 대비 OOS 열화 정도를 판단해 유지/파라미터 재조정/보류 결정을 문서화하며, `sprint-change-proposal-2026-09-04.md`의 "OOS 미검증" Open Risk를 검증 완료 결과로 갱신한다.

## Boundaries & Constraints

**Always:** `StrategyDParams`/`StrategyEParams`(파라미터 상수), `engine.py` 판정 로직, `run_strategy_d_backtest`/`run_strategy_e_backtest`의 계산 방식은 그대로 사용한다. `--output`으로 별도 CSV 경로를 지정해 기존 `strategy_d_baseline.csv`/`strategy_e_baseline.csv`(전체 구간 baseline)를 덮어쓰지 않는다. 각 실행의 `data_fingerprint`를 결과에 함께 기록한다.

**Never:** 전략 파라미터를 재조정하지 않는다(재조정이 필요하다고 결론나면 "결정"만 기록하고 실제 파라미터 변경은 별도 스토리로 남긴다 — 이 스토리 범위는 검증과 기록이다). `strategy_d.py`/`strategy_e.py`/`engine.py` 계산 로직을 수정하지 않는다. 신규 데이터 수집이나 종목 확장을 하지 않는다(기존 104종목 parquet 그대로 사용).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | D/E를 in-sample(2020-08-03~2024-08-27)·OOS(2024-08-28~2026-08-27) 구간으로 각각 실행 | 4개 결과(D in-sample/OOS, E in-sample/OOS)의 승률·PF·거래수·fingerprint가 `backtest-baseline.md`에 표로 기록 | 오류 없음 |
| DEGRADED_OOS | OOS 승률/PF가 in-sample 대비 큰 폭 하락 | `backtest-baseline.md`에 열화 사실과 재조정/보류 결정을 명시적으로 기록 | 수치 은폐 없이 그대로 기록 |
| THIN_SAMPLE | OOS 구간 거래수가 매우 적음(월간 빈도상 예상 가능) | 표본 부족을 함께 기록하고 승률 단독으로 과신 판단하지 않음(거래수 병기) | 오류 없음 |

</intent-contract>

## Code Map

- `backtest/indicator_opt/strategy_d.py:308-325` -- `main()`이 `--start`/`--end`/`--output` CLI 인자를 받아 `run_strategy_d_backtest`를 실행하고 CSV(요약 1행 + 거래 상세)를 저장. `BASELINE_START`(2020-08-03)/`BASELINE_END`(2026-08-27)가 기본값. 코드 변경 없이 CLI 인자만 다르게 호출.
- `backtest/indicator_opt/strategy_e.py:384-411` -- 동일 구조의 `main()`. 코드 변경 없이 CLI 인자만 다르게 호출.
- `backtest/indicator_opt/strategy_d.py:220-278` (`run_strategy_d_backtest`) / `strategy_e.py` 대응 함수 -- `start`/`end`로 프레임을 자르고 그 구간 안에서만 지표(SMA240 등)를 계산·시그널을 뽑음(구간 밖 warmup 데이터를 끌어오지 않음). in-sample/OOS 양쪽 모두 동일한 방식이라 비교 가능하지만, 각 구간 초입 ~240봉은 SMA240 warmup으로 시그널이 나오지 않는 점을 결과 해석 시 감안.
- `backtest/data/loader.py:25-50` (`load_all`) -- 104종목 parquet 전량 로드, 실측 구간 2020-08-03~2026-08-27(일부 종목은 늦게 상장해 구간이 짧음). 데이터 재수집 없음.
- `backtest/results/indicator_opt/` -- 기존 `strategy_d_baseline.csv`/`strategy_e_baseline.csv`(전체 구간, 보존 대상)와 별도로 `strategy_d_oos_insample.csv`/`strategy_d_oos_holdout.csv`/`strategy_e_oos_insample.csv`/`strategy_e_oos_holdout.csv` 4개 신규 파일을 추가.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md:32-68` (전략 D 절), `:88-114` (전략 E 절) -- 각 절 끝에 "OOS(워크포워드) 검증" 하위 절을 추가해 in-sample/OOS 표·fingerprint·해석·결정을 기록.
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-04.md:40,51,91,121,125,140,143,151` -- "OOS 미검증"을 Open Risk로 추적하는 기존 문장들. 검증 완료 사실과 결과 요약(및 `backtest-baseline.md` 참조)으로 갱신.

## Tasks & Acceptance

**Execution:**
- `backtest/results/indicator_opt/strategy_d_oos_insample.csv`, `strategy_d_oos_holdout.csv` -- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d --start 2020-08-03 --end 2024-08-27 --output backtest/results/indicator_opt/strategy_d_oos_insample.csv`와 `--start 2024-08-28 --end 2026-08-27 --output backtest/results/indicator_opt/strategy_d_oos_holdout.csv`를 실행해 결과 생성 -- HAPPY_PATH.
- `backtest/results/indicator_opt/strategy_e_oos_insample.csv`, `strategy_e_oos_holdout.csv` -- `strategy_e` 모듈에 동일한 두 구간으로 실행 -- HAPPY_PATH.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- 전략 D/E 절 각각에 "OOS(워크포워드) 검증" 하위 절 추가: in-sample/OOS 승률·PF·거래수·fingerprint 표, 두 구간 간 차이 해석, 열화 시 재조정/보류 결정(또는 유지 결정) 명시 -- HAPPY_PATH, DEGRADED_OOS, THIN_SAMPLE.
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-04.md` -- OOS 관련 Open Risk 문장들을 검증 완료·결과 요약으로 갱신 -- AC(아래).

**Acceptance Criteria:**
- Given 전략 D/E가 Story 6.1/6.2로 코드화된 상태에서, when in-sample(2020-08-03~2024-08-27)과 OOS(2024-08-28~2026-08-27) 구간으로 각각 재실행하면, then 두 구간의 승률·PF·거래수·fingerprint가 `backtest-baseline.md` D/E 절에 병기된다.
- Given OOS 결과가 산출된 상태에서, when in-sample 대비 승률/PF 변화를 검토하면, then 열화 정도에 따라 파라미터 재조정 또는 해당 전략 보류 여부에 대한 결정(또는 "유지" 결정, 근거 포함)이 `backtest-baseline.md`에 기록된다.
- Given `sprint-change-proposal-2026-09-04.md`가 "OOS 미검증" 상태를 Open Risk로 추적하던 상태에서, when 검증이 완료되면, then 해당 항목들이 검증 완료 사실과 결과 요약(및 `backtest-baseline.md` 참조 링크)으로 갱신된다.

## Spec Change Log

## Review Triage Log

### 2026-09-07 — 독립 리뷰 4종(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)

- intent_gap: 0
- bad_spec: 0
- patch: 2: (high 0, medium 1, low 1)
- defer: 1: (high 0, medium 0, low 1)
- dismissed:
  - THIN_SAMPLE 구간에 신뢰구간/이항검정 등 정량 통계치가 없다는 지적 — 스토리 AC(epics.md Story 6.8)는 "in-sample 대비 과도한 하락 문서화"와 "결정 기록"만 요구하며 통계적 유의성 검정을 요구하지 않는다. 표본 부족은 이미 거래수 병기로 명시했다(스펙 THIN_SAMPLE 행 충족).
  - D/E 모니터링 커밋 비대칭(D는 재평가 트리거 없음) 지적 — D는 열화가 완만(승률 −1.92%p, PF −0.1895)한 반면 E는 승률 −30%p·PF<1로 급락해, 관측된 열화 크기 차이가 비대칭 대응의 근거다.
  - frontmatter `warnings: ['oversized']`에 트리밍 근거 설명이 없다는 지적 — 이 필드는 오케스트레이션용 기계가독 플래그이며 사람이 읽는 설명을 요구하지 않는다.
  - `followup_review_recommended: false`가 근거 없이 설정됐다는 지적 — 구현 서브에이전트가 리뷰 이전에 조기 설정한 값이며, 이번 step-04 Finalize에서 이번 패스의 patch 집계로 재계산되어 덮어써진다(아래 Finalize 참조).
  - `epic-6: done`인데 `epic-6-retrospective: optional`이 모순이라는 지적 — `sprint-status.yaml` 자체 정의(`# Retrospective Status: - optional: Can be completed but not required`)상 optional은 epic 완료를 막지 않는 독립 상태이며, epic-4/5도 동일 컨벤션이다.
  - `sprint-change-proposal-2026-09-04.md`의 갱신 표기 방식(취소선/괄호부기/제자리수정)이 3가지로 혼재해 감사추적이 어렵다는 지적 — 가독성 선호 사항이며 각 갱신 문구 자체는 사실관계가 정확해 결론을 오도하지 않는다.
  - `backtest-baseline.md`의 신규 OOS 절이 `sprint-change-proposal-2026-09-04.md`로 역참조하지 않는다는 지적 — 참조 방향(proposal → baseline)은 이미 존재하고, 기술 문서(baseline)가 리스크 관리 문서(proposal)를 항상 역참조해야 한다는 근거가 스펙에 없다.
  - PRD가 갱신되지 않았다는 지적 — PRD(`prd.md:452`)는 이미 "OOS 워크포워드 검증 전 상태 리스크"를 `sprint-change-proposal-2026-09-04.md` 참조로 위임하고 있어, 그 문서 갱신만으로 PRD의 인용 체인이 최신화된다.
  - 4년/2년 분할 비율이 정당화되지 않았다는 지적(대안: 확장 윈도우 다중 폴드 등) — 스토리 Never 제약("신규 데이터 수집이나 종목 확장을 하지 않는다")과 AC("in-sample과 별도 기간")는 단일 시간순 분할만 요구하며, Design Notes가 분할의 목적(재적합 아님, 규칙 지속성 확인)을 이미 명시했다.
  - Verification 섹션에 baseline CSV 미변경을 확인하는 커맨드가 없다는 지적 — 이번 리뷰에서 `git diff {baseline_revision} -- strategy_d_baseline.csv strategy_e_baseline.csv`로 직접 대조해 변경 0건을 확인했다(제약 위반 없음, 은폐된 문제 아님).
  - 신규 결과 CSV 디렉터리에 README/색인이 없다는 지적 — `backtest-baseline.md`의 각 OOS 하위 절이 파일 경로를 이미 본문에서 설명해 실질적 문서화를 제공한다.
  - D의 `invalid_ohlcv_rows`(204→40) 변화가 설명되지 않았다는 지적 — 이 값은 원본 CSV에만 존재하고 스토리 AC가 요구하는 표(승률·PF·거래수·fingerprint)에는 애초에 포함되지 않는 파생 지표라 서술 누락이 AC 미충족을 의미하지 않는다.
  - intent-alignment의 "브라우저 e2e가 없다" 서술 — 이번 스토리는 `apps/web`을 다루지 않는 백테스트/문서 스토리이며, 원 지시의 "필요 시 e2e"는 조건부(필요 시)이고 이 도메인의 end-to-end 검증은 실제 CLI를 실제 데이터로 실행하는 것이다(스펙 Verification 커맨드로 이미 수행·재확인됨).
  - intent-alignment의 "diff만으로는 `npm run test -w apps/web` 실행 여부·git 커밋 여부를 확인할 수 없다"는 서술 — 이번 review 단계에서 직접 재실행해 77/77 통과를 재확인했고(위 Verify 절 참조), git 커밋은 워크플로우 Finalize 단계에서 수행되는 후속 절차다.
- addressed_findings:
  - `[medium]` `[patch]` `sprint-change-proposal-2026-09-04.md`의 "## 6. Open Risk" 제목이 "(미해결로 이월)"과 "[검증 완료]"를 한 줄에 동시에 표기해 자기모순이었다 — 제목을 모순 없는 단일 상태 표기로 정정.
  - `[low]` `[patch]` 전략 E의 "OOS 표본 20건 누적 시 재평가" 후속 모니터링 약속이 산문 서술로만 남아 추적되지 않았다 — `sprint-status.yaml` `action_items`에 추적 항목을 추가.

## Design Notes

전략 D/E 파라미터는 저장소 밖 원본 연구 문서(`docs/돌파3%기법_추가.md`, `docs/익절2%_고정SL5%기법_추가.md`)에서 이미 확정된 상수이며 이번 저장소 데이터로 재적합(fit)되지 않았으므로, 전체 관측창(2020-08-03~2026-08-27)을 시간순으로 in-sample(앞 4년)/OOS(뒤 2년, 이후 미사용 구간)로 나누는 것 자체가 워크포워드 검증으로 유효하다(파라미터가 이 저장소 데이터로 재학습된 적이 없어 구간 분할이 데이터 누출을 막는 목적이 아니라 "다른 시기에도 같은 규칙이 유지되는가"를 확인하는 목적). 신호 빈도가 낮아(월 0.26건, 6년 19건) OOS 2년 구간의 거래수는 한 자릿수일 수 있음 — 표본 부족은 은폐하지 않고 그대로 기록한다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d --start 2020-08-03 --end 2024-08-27 --output backtest/results/indicator_opt/strategy_d_oos_insample.csv` -- expected: 정상 종료, 요약·거래 CSV 생성.
- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d --start 2024-08-28 --end 2026-08-27 --output backtest/results/indicator_opt/strategy_d_oos_holdout.csv` -- expected: 정상 종료, 요약·거래 CSV 생성.
- 동일한 두 명령을 `strategy_e` 모듈로 반복 -- expected: 정상 종료.
- `npm run test -w apps/web` -- expected: 기존 스위트 통과(이 스토리는 web 코드를 변경하지 않으므로 회귀 없음 확인용).

**Manual checks (if no CLI):**
- `backtest-baseline.md`의 신규 OOS 하위 절이 in-sample/OOS 수치와 결정을 명확히 구분해 서술하는지 육안 확인.
- `sprint-change-proposal-2026-09-04.md`의 갱신된 문장이 기존 문맥(Risk 등급, 시퀀싱 결론 등)과 모순되지 않는지 확인.

## Auto Run Result

**구현 요약:** `strategy_d.py`/`strategy_e.py`/`engine.py`는 변경하지 않고 기존 CLI를 in-sample(2020-08-03~2024-08-27)·OOS/holdout(2024-08-28~2026-08-27) 두 구간으로 재실행해 전략 D/E의 워크포워드 검증을 완료했다. D는 열화가 완만해 **유지** 결정, E는 승률 −30%p·PF 1.49→0.37로 뚜렷한 열화가 관측됐으나 OOS 표본이 4건뿐이라 **조건부 유지(모니터링 강화, 20건 누적 시 재평가)** 결정을 내리고 `backtest-baseline.md`에 근거와 함께 기록했다. `sprint-change-proposal-2026-09-04.md`의 "OOS 미검증" Open Risk를 검증 완료 결과로 갱신했다.

**변경 파일:**
- `backtest/results/indicator_opt/strategy_d_oos_insample(.csv/_trades.csv)`, `strategy_d_oos_holdout(...)` -- 전략 D의 in-sample/OOS 백테스트 결과·거래 상세(신규).
- `backtest/results/indicator_opt/strategy_e_oos_insample(...)`, `strategy_e_oos_holdout(...)` -- 전략 E의 in-sample/OOS 백테스트 결과·거래 상세(신규).
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- 전략 D/E 절에 "OOS(워크포워드) 검증" 하위 절 추가(표·해석·결정).
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-04.md` -- OOS 관련 Open Risk 8곳을 검증 완료 결과로 갱신, "## 6. Open Risk" 제목의 자기모순 문구를 리뷰 패치로 정정.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- `6-8-oos-워크포워드-검증`/`epic-6`을 `done`으로 갱신, 리뷰 패치로 전략 E 20건 재평가 추적을 위한 `action_items` 항목 1건 추가.

**리뷰 findings 분류:** patch 2건(medium 1, low 1, 이번 패스에서 모두 수정 완료) · defer 1건(low, 전략 E의 fingerprint/invalid_ohlcv_rows가 윈도우 적용 전 원본 프레임에서 계산되는 `strategy_e.py`의 기존(이 스토리 이전부터 존재) 특성 -- Story 6.2 범위, 이번 스토리에서 코드 수정 없음) · dismissed 14건(위 Review Triage Log 참조, 대부분 스토리 AC 범위 밖이거나 파생 지표·기존 컨벤션·조기 기본값으로 이미 해소됨).

**추적 리뷰 권장:** patch 2건(medium 1, low 1) → score = 3×1 + 1×1 = 4, 5 미만이고 high 0건 → **권장하지 않음**.

**검증 수행:**
- `uv run ... strategy_d --start 2020-08-03 --end 2024-08-27` / `--start 2024-08-28 --end 2026-08-27` -- 정상 종료, 승률 76.92%→75.00%·PF 1.8954→1.7059(13건→4건) 확인.
- `uv run ... strategy_e` 동일 두 구간 -- 정상 종료, 승률 80.00%→50.00%·PF 1.4902→0.3725(15건→4건) 확인.
- `npm run test -w apps/web` -- 77/77 통과, 리뷰 패치 전후 총 3회 실행(구현 시 1회, 리뷰어 독립 재실행 1회, 패치 후 재실행 1회), 회귀 없음.
- `git diff {baseline_revision} -- strategy_d_baseline.csv strategy_e_baseline.csv` -- 0줄, 기존 baseline CSV 미변경 확인(Never 제약 준수).
- 리뷰 4종(blind-hunter 15건, edge-case-hunter 2건, verification-gap 0건, intent-alignment 서술형) 결과를 모두 판정·분류.

**잔여 리스크:** 전략 E의 OOS 표본이 4건(2승 2패)뿐이라 이번 관측치(승률 50%, PF 0.37)가 실전 성과를 신뢰성 있게 대표하는지 통계적으로 확정할 수 없다. `sprint-status.yaml` action_items에 20건 누적 시 재평가 추적 항목을 추가했으나, 그 시점까지는 전략 E가 "조건부 유지" 상태로 프로덕션에 남아 있다는 리스크가 계속된다. `strategy_e.py`의 fingerprint/invalid_ohlcv_rows가 윈도우 적용 전 프레임에서 계산되는 기존 특성(Story 6.2, 이번 스토리 범위 밖)은 defer로 남겼다.
