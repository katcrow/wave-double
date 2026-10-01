---
title: '전략 L · VWAP 상향 회복 백테스트 구현'
type: 'feature'
created: '2026-10-01'
status: 'done'
baseline_revision: '0d8d4e134421ee11439fe1b30a36d24a2dfcd11b'
baseline_commit: '0d8d4e134421ee11439fe1b30a36d24a2dfcd11b'
review_loop_iteration: 0
followup_review_recommended: true
context: []
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 문서에 추가된 `전략 L · VWAP 상향 회복 AND 양봉 AND VWAP 재시험 AND 거래량 확인` 후보가 백테스트 코드에 없어, 명시된 30봉 rolling VWAP 진입 조건과 3%/4% 청산 규칙을 재현할 수 없다.

**Approach:** 운영 A~I 태깅 계약과 분리된 전략 모듈에 고정 파라미터, 신호 마스크, 종가 진입 신호, 유니버스 백테스트 러너와 CLI를 추가하고, 합성 OHLCV 회귀 테스트로 조건·경계·청산·기간 필터를 검증한다.

## Boundaries & Constraints

**Always:** 당일 포함 30봉 Typical Price 거래량가중 VWAP, 전일 종가 `<=` 전일 VWAP에서 당일 종가 `>` 당일 VWAP 상향회복, 양봉, 당일 저가의 VWAP ±0.5% 재시험, 직전 15봉 평균 대비 거래량 1.2배 이상을 모두 요구한다. 진입은 신호 봉 종가이며 다음 봉부터 TP/SL을 평가하고, 같은 봉 TP·SL은 TP-first, 미도달 시 종가가 진입가보다 높을 때만 종가 청산한다. 왕복 비용은 기본 0.1%, 종목별 동시 보유는 1개로 한다.

**Never:** 새 전략을 `compute_abc`, 운영 `candidate_tags`, 전략 라벨/DB 계약에 연결하지 않는다. 기존 J의 VWAP 지지 의미나 공통 엔진의 보수적 SL-first 기본값을 새 규칙으로 오인해 변경하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 30봉 VWAP·15봉 선행 거래량을 갖춘 유효 OHLCV | 신호 마스크와 종가 신호가 동일한 날짜에 생성 | 오류 없음 |
| WARMUP | 이력 부족, 0 거래량 rolling 합계, NaN/invalid OHLCV | 해당 행/유효 구간은 신호·거래에서 제외, 후속 유효 구간과 연결하지 않음 | 명시적 입력 검증 또는 조용한 무신호 |
| EXIT_BOUNDARY | 다음 봉 TP/SL 동시 도달 또는 수익/비수익 종가 | TP-first, 수익 종가만 강제청산, 손실/동일 종가는 보유 | 거래 결과에 청산 사유 기록 |

</intent-contract>

## Code Map

- `docs/후보종목-태깅-조건.md` -- 새 후보의 단일 요구사항과 기준 성과(2020-08-03~2026-08-27)를 담은 참조 문서.
- `backtest/indicator_opt/strategy_j.py` -- rolling VWAP·유효 OHLCV·유니버스 러너·CLI의 재사용 패턴; 의미와 청산은 새 규칙에 맞게 별도 구현.
- `backtest/engine.py` -- `Trade` 구조와 비용 계산을 재사용할 수 있는 경계; 기존 `run_backtest`는 이 전략의 수익 종가 강제청산을 표현하지 못하므로 전용 루프가 필요.
- `backtest/metrics/metrics.py` -- `summarize`로 거래 성과, PF, 복리수익률, MDD, 청산 사유를 산출.
- `backtest/data/loader.py` -- 기본 일봉 parquet 유니버스 로더.
- `backtest/tests/test_strategy_j.py` -- 전략 모듈 테스트의 fixture·CLI·runner 검증 스타일.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_vwap_recovery.py` -- 고정 파라미터, rolling VWAP/진입 마스크, 종가 신호, TP-first·수익 종가 강제청산 러너, 결과 평탄화와 CLI를 구현한다.
- [x] `backtest/tests/test_strategy_vwap_recovery.py` -- 진입 조건별 필수성·경계, 미래값 독립성, warmup/invalid 구간, TP-first·forced-close·동시보유 차단, runner/CLI를 회귀 검증한다.
- [x] `_bmad-output/implementation-artifacts/spec-vwap-recovery-backtest.md` -- 구현 결과와 검증 증거를 기록할 수 있도록 상태를 갱신한다.

**Acceptance Criteria:**
- Given 유효한 최근 30봉과 직전 15봉 거래량, when 네 진입 조건을 동시에 만족하면, then 해당 봉 종가의 단일 신호가 생성되고 어느 한 조건이라도 빠지면 생성되지 않는다.
- Given 신호 이후 봉의 고가/저가가 TP·SL에 함께 닿으면, when 백테스트가 실행되면, then TP 가격과 `tp` 사유로 종료된다.
- Given TP/SL 미도달 봉의 종가가 진입가보다 높으면, when 그 봉을 평가하면, then 그 종가와 `close_profit` 사유로 종료되고 동일/낮은 종가는 다음 봉으로 보유된다.
- Given 보유 중 추가 신호가 존재하면, when 동일 종목을 실행하면, then 추가 거래는 무시되고 청산 후 신호만 재진입한다.
- Given 기존 전체 백테스트 테스트와 새 타깃 테스트를 실행하면, then 모두 통과하고 새 모듈이 운영 A~I API의 시그널 키를 바꾸지 않는다.

## Design Notes

- 신호 봉 자체는 청산 평가에서 제외한다. 마지막 봉에 진입할 수는 있으나 다음 봉이 없으면 거래로 기록하지 않아 look-ahead 없는 기존 백테스트 계약을 따른다.
- 기간 `start/end`는 warmup 이력 계산 후 신호와 거래의 관측 범위에만 적용한다. 결과에는 데이터 fingerprint와 실제 유효 종목/월 수를 남긴다.

## Verification

**Commands:**
- [x] `uv run --with pytest pytest backtest/tests/test_strategy_vwap_recovery.py` -- 19개 통과.
- [x] `uv run --with pytest pytest backtest/tests` -- 275개 통과.
- [x] `git diff --check` -- exit code 0; 공백/패치 오류 없음.

구현 범위에는 운영 A~I API, `candidate_tags`, 전략 라벨/DB 계약 변경이 없으며 새 모듈과 회귀 테스트만 추가했다. I/O 매트릭스의 HAPPY_PATH, WARMUP, EXIT_BOUNDARY는 각각 타깃 테스트에서 실행·통과했다.

## Review Triage Log

### 2026-10-01 — Review pass

- intent_gap: 0
- bad_spec: 0
- patch: 3 (medium 1, low 2)
- defer: 0
- dismissed:
  - 운영 A~I 표면을 변경하지 않았다는 지적 — 문서가 이 항목을 운영 태깅이 아닌 백테스트 후보로 명시한다.
  - `SimpleSignal`의 exit 필드를 무시한다는 지적 — 이 전략은 고정 파라미터 계약이며 신호 생성기와 러너가 같은 파라미터를 사용한다.
  - 관측 `end` 이후 청산·미완료 포지션 제외·raw signal count 지적 — 기존 indicator-opt runner 관례와 명세의 완료 거래 중심 결과에 따른 의도된 동작이다.
  - 여러 종목 성과를 순차 거래 커브로 집계한다는 지적 — 결과는 포트폴리오 자본배분 성과가 아니라 기존 `summarize` 호환 거래 성과이며 포트폴리오로 주장하지 않는다.
  - 갭 체결·거래정지·상하한가 지적 — 일봉 OHLCV의 고가/저가 도달 가격 체결이라는 기존 백테스트 가정 밖이며 본 요구사항에 정책이 없다.
  - 날짜 빈도·환경 버전 fingerprint 지적 — fingerprint는 입력 데이터 재현성용이고 인덱스의 각 행을 거래 봉으로 취급하는 기존 계약을 따른다.
  - exact boundary 및 start/end/혼합 timezone 테스트 추가 지적 — 핵심 경계는 기존 20개 타깃 테스트와 직접 비교식으로 검증되며, timezone/기간 계약은 동일 runner 패턴으로 검증된다.
  - 운영 API 시그널 키 별도 테스트 지적 — 새 모듈은 해당 import 경로를 변경하지 않고 전체 276개 회귀망의 `test_strategy_api.py`가 통과했다.
  - 비수치 OHLCV 입력의 전용 오류 메시지 지적 — 입력 변환 실패가 조용히 성공하지 않고 예외로 중단되며, 운영 parquet 계약은 수치 OHLCV다.
- addressed_findings:
  - `[medium][patch]` 저수준 러너가 invalid 봉을 직접 받을 수 있음 — 유효 OHLCV 구간만 허용하도록 guard를 추가하고 runner가 invalid 행 기준으로 `[20, 29]` 구간을 나누는 테스트를 추가했다.
  - `[low][patch]` 왕복 비용 차감이 회귀망에서 보호되지 않음 — 기본 비용으로 3% 익절이 2.9% 순수익이 되는 테스트를 추가했다.
  - `[low][patch]` 역순/비정상 진입 신호 입력 계약이 불명확함 — 날짜순 정렬과 유한 양수 진입가 검사를 추가하고 오해를 부르는 alias를 제거했다.

## Auto Run Result

Status: done

Summary: 운영 태깅과 분리된 전략 L(VWAP 상향 회복) 백테스트 모듈, 전략 전용 청산 루프, CLI와 회귀 테스트를 추가했다.

Files changed:

- `backtest/indicator_opt/strategy_vwap_recovery.py` — 30봉 rolling VWAP 진입 마스크, 3%/4% TP/SL, TP-first, 수익 종가 청산, 유니버스 runner와 CLI.
- `backtest/tests/test_strategy_vwap_recovery.py` — 조건·경계·청산·invalid 구간·비용·CLI 회귀 테스트.
- `docs/후보종목-태깅-조건.md` — 새 백테스트 구현 출처 경로 추가.

Review findings breakdown: 패치 3건, 보류 0건, 기각은 위 triage log에 기록한 9개 항목이다. 패치 중 medium 1건·low 2건이며 점수는 `3 × 1 + 2 = 5`, follow-up review recommendation은 `true`다.

Verification:

- `uv run --with pytest pytest backtest/tests/test_strategy_vwap_recovery.py` — 20 passed.
- `uv run --with pytest pytest backtest/tests` — 276 passed.
- `git diff --check` — 통과.
- 실제 parquet 전체 실행 — 104종목, 391시그널, 385완료거래, 승률 75.58%, 평균 +0.1260%, PF 1.1272, 복리 +42.7372%, MDD -41.1191%, 거래 발생 월평균 5.274회.

Residual risks: 문서에 기록된 기준치(404거래, PF 1.1185 등)와 현재 parquet 실행치가 다르다. 현재 데이터 fingerprint/스냅샷 차이 또는 과거 산출 시의 미완료 포지션 처리 차이를 추가 대조해야 하며, 이번 구현은 근거 없이 기준치를 맞추도록 결과를 조정하지 않았다. 미완료 포지션 6건은 거래 성과에서 제외되며 이후 신호를 막는다.
