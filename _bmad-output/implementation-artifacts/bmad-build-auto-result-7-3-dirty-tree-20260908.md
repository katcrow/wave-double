---
status: blocked
---

# BMad Build Auto Result

Status: blocked
Blocking condition: dirty working tree (스토리 7-3 진행에 앞서 워킹 트리가 깨끗해야 합니다 — `backtest/` 아래 스테이징된 변경(`backtest/indicator_opt/strategy_ma_derivative.py`, `backtest/results/strategy_g_baseline*.csv`)과 다수의 미추적 백테스트 결과 CSV(`strategy_g_*` 계열, 총 41개 항목)가 커밋되지 않은 상태입니다. 이 파일들은 스토리 7-3(전략 계산 API 일반화, AD-5 addendum 2)과 무관해 보이며, 별도 실험 작업의 산출물로 판단되어 임의로 커밋하거나 삭제하지 않았습니다.)
