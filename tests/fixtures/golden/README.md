# 골든 픽스처 (Story 6.4)

운영 태깅(`backtest.strategy_api.compute_abc`)이 backtest(`screen_abc`)가 검증한
전략 A/B/C/D/E를 재현하는지 검증하는 **단일 권위 gate**의 고정 입력이다. `backtest/tests/test_golden_fixture.py`
가 이 픽스처를 소비해 Jaccard 회귀를 강제한다.

## 파일 스키마 계약

### `golden_day.json`
```json
{
  "trading_day": "2026-08-26",
  "batch_kind": "close",
  "universe": ["종목코드..."]
}
```
- `trading_day`: 고정 golden 거래일(2026-08-26).
- `universe`: 해당 거래일까지 일봉이 **120행 이상**인 종목 집합(98종목). 120거래일 미만
  종목은 계산 대상에서 제외된다(Story 2.1/2.3 계약).
- `batch_kind`: 종가 확정 배치(`close`).

### `ohlcv_raw.json.gz`
```json
{
  "sujung": "Y",
  "ohlcv": {
    "종목코드": {
      "trading_day": ["YYYY-MM-DD", ...],
      "open": [...], "high": [...], "low": [...], "close": [...], "volume": [...]
    }
  }
}
```
- universe 별 **전체 일봉 이력**(golden 거래일까지 포함)을 `daily_ohlcv` 스키마
  필드(`ticker`/`trading_day`/`open`/`high`/`low`/`close`/`volume`, 수정주가 `sujung=Y`)로 저장한다.
- 종목별 **컬럼형 배열**(열 우선)로 인코딩한다.
- **반올림 인코딩(결정적 최소 표현)**: `open`/`high`/`low`/`close`는 소수점 4자리,
  `volume`은 소수점 2자리로 반올림한다. 참조·신규 신호 모두 이 동일 반올림 데이터에서
  계산되어 내부 정합을 해치지 않는다.
- gzip 압축 JSON(압축 허용 조건 사용). 원본 JSON 약 9.0MB → 약 3.1MB.

### `golden_signals.json`
```json
{
  "trading_day": "2026-08-26",
  "strategy_signals": { "A": ["종목코드..."], "B": [...], "C": [...], "D": [...], "E": [...] }
}
```
- 참조 시그널 집합: 각 전략(A/B/C/D/E)에 대해 창 `[2026-01-01, trading_day]` 내 신호가
  1회 이상 발생한 종목 코드(오름차순) 목록. 각 전략은 비어 있으면 안 된다(빈 픽스처는
  명시적 실패, AD-5).
- 참조 산출 경로: A/B/C는 `combine_strategies.build_signals`를, D/E는 각각
  `strategy_d.compute_strategy_d`/`strategy_e.compute_strategy_e`를 유효한 연속 구간에
  적용해 동일한 호출·윈도우 규칙을 재현한다.
- 전략별 확정 값은 픽스처 재생성 도구가 원본 데이터에서 결정적으로 산출한다.

## 재생성 방법

픽스처는 고정이며 테스트가 자동 재생성하지 않는다. 명시적 재생성 도구만 픽스처를
다시 만든다.

```bash
uv run --with pandas --with numpy --with pyarrow \
  python tests/fixtures/golden/generate_golden.py [--trading-day 2026-08-26] [--window-start 2026-01-01]
```

- 스크립트는 상단 부트스트랩으로 `backtest`(루트)와 `domain`(packages/domain) 패키지를
  자동으로 import 경로에 추가하므로 별도 `PYTHONPATH` 없이 실행할 수 있다.
- 데이터 원천은 `backtest/data/raw/*.parquet`(pyarrow 필요).
- 재생성은 결정적이며, 완료 시 참조 대비 `compute_abc`의 A/B/C/D/E별 Jaccard가 0.9 이상인지
  sanity로 강제한다. 미달이면 `SystemExit(1)`로 실패한다(불일치 종목 목록 출력).
- parity sanity를 통과한 뒤에만 픽스처 3파일을 기록하므로, 실패 시 기존 권위
  픽스처를 덮어쓰지 않는다.

## 판정 기준

- gate는 완전 일치가 아닌 **통계적 유사도(전략별 Jaccard ≥ 0.9)**를 기준으로 판정한다.
- 참조 재현성(③)은 `ohlcv_raw`로 재계산한 참조가 저장된 `golden_signals`와 **정확히**
  일치해야 하며(수동 편집·픽스처 오염 탐지), Jaccard 게이트(④)와는 별개로 검증한다.
- **조정-방식론 선행조건(AD-5)**: backtest(yfinance 배당조정)와 운영(LS `t8410`/`t8451`의
  `sujung` 플래그, 액면분할 위주)의 조정 방식론이 신호 재현에 무시할 수 있는 수준으로
  동등함을 **별도 단발성 조정-방식론 동등성 검증**으로 확인한 뒤에만 이 gate가 유효하다.
  미검증 상태에서는 Jaccard 통과를 배포 승인의 근거로 신뢰하지 않는다.

## 게이트 포함

테스트는 `backtest/tests/`에 두어 `.github/workflows/test.yml`의 `pytest backtest -q`
에 자동 포함된다. 어느 전략이든 Jaccard < 0.9이거나 non-READY 종목이 있으면 배포가
차단된다.
