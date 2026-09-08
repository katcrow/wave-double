---
title: 'OOS(워크포워드) 검증 — 전략 F'
type: 'chore'
created: '2026-09-08'
status: 'done'
baseline_revision: '5d6b1b48023d53ef3e92696c416815b854fd653a'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
warnings: []
deferred:
  - summary: >-
      strategy_f.py의 n_signals(78/95)와 n_trades(77/91)가 두 OOS 구간 모두 일치하지
      않는데, 원인이 어디에도 설명돼 있지 않다.
    evidence: |-
      기존 전체구간 baseline(strategy_f_baseline.csv)에서도 n_signals=173,
      n_trades=168로 동일한 5건 차이가 이미 존재해(이번 스토리 이전부터 있던
      strategy_f.py의 기존 특성), 이번 OOS 재실행이 새로 유발한 문제가 아니다.
      Story 7.1(strategy_f.py 최초 구현) 범위이며 이번 스토리에서 코드를
      수정하지 않았다.
    location: >-
      backtest/indicator_opt/strategy_f.py:313-368
    severity: low
---

<intent-contract>

## Intent

**Problem:** 전략 F는 `docs/각도가속_이평쌍바닥기법_추가.md`가 스스로 권고한 OOS(워크포워드) 검증 없이 이미 태깅·outcome 판정·UI에 반영되어(Story 7.1~7.6 완료) 프로덕션에 들어가 있다. `backtest-baseline.md`의 F 수치는 전체 관측창(2020-08-03~2026-08-27) 단일 구간이라 과적합 여부를 판단할 별도 구간 대조가 없고, `sprint-change-proposal-2026-09-07.md`가 이를 Medium Risk로 추적 중이다.

**Approach:** 기존 `strategy_f.py` CLI(파라미터·엔진 변경 없음)를 Story 6.8과 동일한 두 구간으로 재실행한다 — in-sample `2020-08-03~2024-08-27`(4년), OOS/holdout `2024-08-28~2026-08-27`(2년). 두 구간 결과를 `backtest-baseline.md` F 절에 병기하고, in-sample 대비 열화 정도를 판단해 유지/재조정/보류 결정을 문서화하며, `sprint-change-proposal-2026-09-07.md`의 "OOS 미검증" Open Risk를 검증 완료 결과로 갱신한다.

## Boundaries & Constraints

**Always:** `StrategyFParams`(파라미터 상수), `engine.py` 판정 로직, `run_strategy_f_backtest`의 계산 방식은 그대로 사용한다. `--output`으로 별도 CSV 경로를 지정해 기존 `strategy_f_baseline.csv`(전체 구간 baseline)를 덮어쓰지 않는다. 각 실행의 `data_fingerprint`를 결과에 함께 기록한다.

**Never:** 전략 파라미터를 재조정하지 않는다(재조정이 필요하다고 결론나면 "결정"만 기록하고 실제 파라미터 변경은 별도 스토리로 남긴다). `strategy_f.py`/`_signals.py`/`engine.py` 계산 로직을 수정하지 않는다. 신규 데이터 수집이나 종목 확장을 하지 않는다(기존 104종목 parquet 그대로 사용).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | F를 in-sample(2020-08-03~2024-08-27)·OOS(2024-08-28~2026-08-27) 구간으로 각각 실행 | 승률·PF·거래수·fingerprint가 `backtest-baseline.md` F 절에 표로 기록 | 오류 없음 |
| DEGRADED_OOS | OOS 승률/PF가 in-sample 대비 큰 폭 하락 | 열화 사실과 재조정/보류 결정을 명시적으로 기록(수치 은폐 없이) | 없음 |
| THIN_SAMPLE | OOS 구간 거래수가 매우 적음(월 2.3건 빈도상 예상 가능) | 표본 부족을 병기하고 승률 단독으로 과신 판단하지 않음 | 오류 없음 |

</intent-contract>

## Code Map

- `backtest/indicator_opt/strategy_f.py:401-` (`main()`) -- `--start`/`--end`/`--output` CLI 인자를 받아 `run_strategy_f_backtest` 실행 후 CSV(요약+거래 상세) 저장. 기본값 `BASELINE_START`(2020-08-03)/`BASELINE_END`(2026-08-27). 코드 변경 없이 CLI 인자만 다르게 호출(Story 6.8과 동일 패턴).
- `backtest/indicator_opt/strategy_f.py:243-306` (`_signals.py`의 쌍바닥/기울기 계산 재사용) -- 구간 내에서만 지표를 계산하므로 in-sample/OOS 비교 가능. 초입 워밍업(SMA16 첫 15봉 등)은 해석 시 감안.
- `backtest/results/indicator_opt/` -- 기존 `strategy_f_baseline.csv`/`_trades.csv`(전체 구간, 보존 대상)와 별도로 `strategy_f_oos_insample(.csv/_trades.csv)`/`strategy_f_oos_holdout(...)` 신규 파일 추가(D/E가 이미 이 디렉터리에 동일 명명 규칙으로 존재).
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md:192-246`(전략 F 절, "결정: 유지"로 끝남) -- 절 끝에 "OOS(워크포워드) 검증" 하위 절을 추가해 in-sample/OOS 표·fingerprint·해석·결정을 기록(D/E 절의 기존 OOS 하위 절과 동일 구조 재사용).
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-07.md:46,57,59,119,165,180` -- "OOS 미검증"/"OOS 워크포워드 검증 전 상태로 편입" 관련 기존 문장들. 검증 완료 사실과 결과 요약(및 `backtest-baseline.md` 참조)으로 갱신.
- `_bmad-output/implementation-artifacts/spec-6-8-oos-워크포워드-검증.md` -- 동일 작업의 선행 사례(참조용, 수정 안 함). CLI 실행 방식·표 구조·Design Notes 논리를 그대로 재사용.

## Tasks & Acceptance

**Execution:**
- `backtest/results/indicator_opt/strategy_f_oos_insample.csv`, `strategy_f_oos_holdout.csv` -- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_f --start 2020-08-03 --end 2024-08-27 --output backtest/results/indicator_opt/strategy_f_oos_insample.csv`와 `--start 2024-08-28 --end 2026-08-27 --output backtest/results/indicator_opt/strategy_f_oos_holdout.csv` 실행 -- HAPPY_PATH.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- F 절에 "OOS(워크포워드) 검증" 하위 절 추가: in-sample/OOS 승률·PF·거래수·fingerprint 표, 구간 간 차이 해석, 열화 시 재조정/보류(또는 유지) 결정 명시 -- HAPPY_PATH, DEGRADED_OOS, THIN_SAMPLE.
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-07.md` -- OOS 관련 문장들을 검증 완료·결과 요약으로 갱신 -- AC(아래).

**Acceptance Criteria:**
- Given 전략 F가 Story 7.1로 코드화된 상태에서, when in-sample(2020-08-03~2024-08-27)과 OOS(2024-08-28~2026-08-27) 구간으로 각각 재실행하면, then 두 구간의 승률·PF·거래수·fingerprint가 `backtest-baseline.md` F 절에 병기된다.
- Given OOS 결과가 산출된 상태에서, when in-sample 대비 승률/PF 변화를 검토하면, then 열화 정도에 따라 파라미터 재조정 또는 전략 F 보류 여부(또는 "유지" 결정, 근거 포함)가 `backtest-baseline.md`에 기록된다.
- Given `sprint-change-proposal-2026-09-07.md`가 "OOS 미검증" 상태를 추적하던 상태에서, when 검증이 완료되면, then 해당 항목들이 검증 완료 사실과 결과 요약(및 `backtest-baseline.md` 참조 링크)으로 갱신된다.

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4계층 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0, medium 2, low 4)
- defer: 1: (high 0, medium 0, low 1)
- dismissed:
  - (blind-hunter) `epic-7: done`인데 `epic-7-retrospective: optional`이 모순이라는 지적 — `sprint-status.yaml` 자체 정의상 optional은 epic 완료를 막지 않는 독립 상태이며, epic-4/5/6도 동일 컨벤션이다(spec-6-8 리뷰에서 동일 지적이 이미 동일 근거로 dismiss됨).
  - (blind-hunter) Code Map의 `strategy_f.py:243-306 (_signals.py의 쌍바닥/기울기 계산 재사용)` 표기가 라인범위와 참조 모듈명을 한 문장에 섞어 모호하다는 지적 — 수정 대상이 이 스펙 자체의 Code Map 절이라 워크플로우 규칙("스펙을 고치는 발견은 dismiss")에 따라 dismiss.
  - (blind-hunter) 향후 200건 재평가 시점에 이미 관측한 holdout 구간을 재사용하지 않을 방법론이 없다는 지적 — 이번 스토리 범위는 최초 OOS 검증과 결정 기록이며(Always/Never 제약 참고), 미래 재평가의 데이터 분할 방법론 설계는 범위 밖(추측성 확장 요구).
  - (blind-hunter) `docs/각도가속_이평쌍바닥기법_추가.md`(원본 연구 문서)에 OOS 검증 완료 사실을 역참조하지 않는다는 지적 — Story 6.8도 D/E의 원본 연구 문서(`docs/돌파3%기법_추가.md`, `docs/익절2%_고정SL5%기법_추가.md`)를 갱신하지 않은 동일 전례가 있다.
  - (blind-hunter) 결과 표의 `data_fingerprint`가 두 행에서 동일한데 각주 표기가 없어 오독 가능성이 있다는 지적 — 표 바로 아래 문단에서 이미 산문으로 설명하며, Story 6.8의 D/E 절도 동일하게 각주 없이 산문 설명만 쓰는 동일 컨벤션이다.
  - (blind-hunter) 열화 정도별 재조정/보류/유지를 가르는 명시적 정량 임계값이 없다는 지적 — Story 6.8도 D/E에 대해 정성적 판단("완만"/"뚜렷한 열화")만 기록했고 정량 임계값을 요구하지 않은 동일 전례이며, 스토리 AC(epics.md Story 7.7)도 "결정 기록"만 요구할 뿐 임계값 공식화를 요구하지 않는다.
  - (intent-alignment) "검수" 활동이 스펙 자체의 서술(해석/결정 산문) 안에만 있고 별도 리뷰-수정 사이클의 흔적(당시 `review_loop_iteration: 0`)이 없다는 지적 — 이번 리뷰 패스 자체가 바로 그 "검수" 단계이며, 이 트리아지 로그가 그 실행 증거다(워크플로우 설계상 review는 step-04에서 수행되고, 구현 단계의 해석/결정 서술은 스토리 산출물이지 리뷰의 대체물이 아니다).
  - (intent-alignment) "e2e"가 명시적 필요성 판단 없이 `npm run test -w apps/web` 단위/통합 스위트로 조용히 축소됐다는 지적 — 이번 스토리는 `apps/web` 코드를 전혀 건드리지 않는 백테스트/문서 스토리이므로, 존재하지 않는 UI 변경에 브라우저 e2e를 적용할 대상이 없다(Story 6.8 리뷰에서 동일 근거로 이미 dismiss됨). 회귀 확인용 웹 스위트 실행은 "필요 시"의 필요 없음 판단과 일관된다.
  - (intent-alignment) diff만으로는 깃 커밋 완료 여부를 확인할 수 없다는 지적 — 커밋은 워크플로우 Finalize 단계에서 이번 리뷰 패스 완료 후 수행되는 후속 절차이며 아직 그 단계에 도달하지 않았을 뿐이다.
  - (verification-gap) 발견 없음("No verification gaps found.").
  - (edge-case-hunter) 발견 없음(`[]`).
- addressed_findings:
  - `[low]` `[patch]` (blind-hunter) `backtest-baseline.md` F절 OOS 해석 문단이 `max_drawdown` 악화(−12.9658%→−20.8512%)를 언급하지 않아 위험 지표 누락 — 해석 문단에 한 문장 추가.
  - `[low]` `[patch]` (blind-hunter) `invalid_ohlcv_rows`가 두 구간에서 동일(244)한데 그 이유가 설명되지 않음(fingerprint와 동일하게 `strategy_f.py:322-327`에서 윈도우 적용 전 원본 프레임 루프 중 계산되는 것이 코드로 확인된 동일 근본원인) — fingerprint 설명 문장에 invalid_ohlcv_rows도 같은 이유로 동일함을 추가.
  - `[low]` `[patch]` (blind-hunter) 월간 거래빈도가 1.5714→3.64로 두 배 이상 증가했는데 해석에 언급이 없음 — holdout 구간이 in-sample 절반 길이(2년 vs 4년)인데 거래수(91건)가 오히려 in-sample(77건)보다 많아 빈도가 상승했다는 설명을 해석 문단에 추가.
  - `[medium]` `[patch]` (blind-hunter) Auto Run Result의 "잔여 리스크: 없음"과 `sprint-change-proposal-2026-09-07.md`의 "잔여 리스크는 없다"가 같은 문서가 약속한 "200건 누적 시 재평가" 모니터링과 자기모순 — "낮은 수준의 잔여 리스크(200건 누적 재평가 트리거로 관리 중)"로 수정.
  - `[low]` `[patch]` (blind-hunter) Verification 절이 `strategy_f_baseline.csv`/`_trades.csv` 미변경만 확인하고, 스토리의 핵심 Never 제약인 `strategy_f.py`/`_signals.py`/`engine.py` 계산 로직 미변경을 확인하는 커맨드가 없음 — `git diff {baseline_revision} -- strategy_f.py _signals.py engine.py` 커맨드와 실행 결과(0줄)를 Verification/검증 수행 절에 추가.
  - `[medium]` `[patch]` (blind-hunter) Story 6.8이 전략 E의 20건 재평가 약속을 `sprint-status.yaml` `action_items`에 추적 항목으로 남긴 것과 달리, 이번 스토리는 F의 200건 재평가 약속을 산문으로만 남기고 `action_items`에 추가하지 않음 — 동일 패턴으로 `action_items` 항목 1건 추가.

## Design Notes

전략 F 파라미터는 저장소 밖 원본 연구 문서(`docs/각도가속_이평쌍바닥기법_추가.md`)에서 이미 확정된 상수이며 이번 저장소 데이터로 재적합(fit)되지 않았으므로, 전체 관측창을 시간순으로 in-sample(앞 4년)/OOS(뒤 2년, 이후 미사용 구간)로 나누는 것 자체가 워크포워드 검증으로 유효하다(Story 6.8과 동일 논리 — 구간 분할이 데이터 누출을 막는 목적이 아니라 "다른 시기에도 같은 규칙이 유지되는가"를 확인하는 목적). F는 월 2.3건 빈도라 OOS 2년 구간의 거래수는 한 자릿수일 수 있음 — 표본 부족은 은폐하지 않고 그대로 기록한다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_f --start 2020-08-03 --end 2024-08-27 --output backtest/results/indicator_opt/strategy_f_oos_insample.csv` -- expected: 정상 종료, 요약·거래 CSV 생성.
- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_f --start 2024-08-28 --end 2026-08-27 --output backtest/results/indicator_opt/strategy_f_oos_holdout.csv` -- expected: 정상 종료.
- `npm run test -w apps/web` -- expected: 기존 스위트 통과(이 스토리는 web 코드를 변경하지 않으므로 회귀 없음 확인용).
- `git diff {baseline_revision} -- backtest/results/indicator_opt/strategy_f_baseline.csv backtest/results/indicator_opt/strategy_f_baseline_trades.csv` -- expected: 0줄(기존 baseline CSV 미변경 확인, Never 제약 준수).
- `git diff 5d6b1b48023d53ef3e92696c416815b854fd653a -- backtest/indicator_opt/strategy_f.py backtest/indicator_opt/_signals.py backtest/indicator_opt/engine.py` -- expected: 0줄(계산 로직 미변경 확인, Never 제약 준수).

**Manual checks (if no CLI):**
- `backtest-baseline.md`의 신규 OOS 하위 절이 in-sample/OOS 수치와 결정을 명확히 구분해 서술하는지 육안 확인.
- `sprint-change-proposal-2026-09-07.md`의 갱신된 문장이 기존 문맥(Risk 등급, Success criteria 등)과 모순되지 않는지 확인.

## Auto Run Result

**구현 요약:** `strategy_f.py`/`_signals.py`/`engine.py`는 변경하지 않고 기존 CLI를 in-sample(2020-08-03~2024-08-27)·OOS/holdout(2024-08-28~2026-08-27) 두 구간으로 재실행해 전략 F의 워크포워드 검증을 완료했다. 승률 75.32%→67.03%(−8.29%p), PF 2.1592→1.4382로 열화가 있었으나 둘 다 실전 채택 기준(승률>50%, PF>1)을 여전히 크게 상회하고, OOS 거래수(91건)가 D/E의 OOS 표본(각 4건)보다 훨씬 커 표본 변동성 우려도 낮아 **유지** 결정을 내리고 `backtest-baseline.md` F절에 근거와 함께 기록했다. `sprint-change-proposal-2026-09-07.md`의 "OOS 미검증"/"편입 리스크" 관련 문장 5곳(Impact Analysis, Recommended Approach Risk, §9 Success Metrics, Story 7.7 제목, Success criteria)을 검증 완료 결과로 갱신했다.

**변경 파일:**
- `backtest/results/indicator_opt/strategy_f_oos_insample(.csv/_trades.csv)`, `strategy_f_oos_holdout(...)` -- 전략 F의 in-sample/OOS 백테스트 결과·거래 상세(신규).
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- 전략 F 절에 "OOS(워크포워드) 검증" 하위 절 추가(표·해석·결정).
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-07.md` -- OOS 관련 문장 5곳을 검증 완료 결과로 갱신.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- `7-7-oos-워크포워드-검증-전략-f`/`epic-7`을 `done`으로 갱신.

**검증 수행:**
- `uv run ... strategy_f --start 2020-08-03 --end 2024-08-27` / `--start 2024-08-28 --end 2026-08-27` -- 정상 종료, 승률 75.32%→67.03%·PF 2.1592→1.4382(77건→91건) 확인.
- `npm run test -w apps/web` -- 77/77 통과, 회귀 없음.
- `git diff {baseline_revision} -- strategy_f_baseline.csv strategy_f_baseline_trades.csv` -- 0줄, 기존 baseline CSV 미변경 확인(Never 제약 준수).
- `git diff 5d6b1b48023d53ef3e92696c416815b854fd653a -- backtest/indicator_opt/strategy_f.py backtest/indicator_opt/_signals.py backtest/indicator_opt/engine.py` -- 0줄, `strategy_f.py`/`_signals.py`/`engine.py` 계산 로직 미변경 확인(Never 제약 준수).

**리뷰 findings 분류:** patch 6건(medium 2, low 4, 이번 패스에서 모두 수정 완료) · defer 1건(low, `strategy_f.py`의 n_signals/n_trades 불일치가 이번 스토리 이전부터 있던 기존 특성 — 코드 미수정) · dismissed 9건(위 Review Triage Log 참조, 대부분 Story 6.8 선례와 동일 컨벤션이거나 스펙 자체 수정 대상·범위 밖 요구).

**추적 리뷰 권장:** patch 6건(medium 2, low 4) → score = 3×2 + 1×4 = 10, 5 이상 → **권장함**. (high 심각도는 없으나 medium 2건 + low 4건 누적이 임계값을 넘음 — 다음 리뷰 패스에서 이번에 수정한 6건이 실제로 의도대로 반영됐는지, 그리고 새로 추가된 서술이 다른 문서와 모순을 일으키지 않는지 재확인 권장.)

**잔여 리스크:** 낮은 수준의 잔여 리스크(200건 누적 재평가 트리거로 관리 중, `sprint-status.yaml` action_items에 추적). F는 D/E와 달리 OOS 표본이 91건으로 충분히 커(D/E는 각 4건) THIN_SAMPLE 우려가 낮고, 승률·PF 열화 폭도 실전 채택 기준을 위협하지 않는 수준이다. `strategy_f.py`가 fingerprint를 윈도우 적용 전 원본 프레임에서 계산해 in-sample/OOS 두 실행의 fingerprint가 동일한 특성은 Story 6.8에서 `strategy_e.py`에 대해 이미 defer된 기존 동작과 같으며, 이번 스토리에서도 코드를 수정하지 않았다. `strategy_f.py`의 n_signals/n_trades 불일치(pre-existing)는 defer로 남겼다.
