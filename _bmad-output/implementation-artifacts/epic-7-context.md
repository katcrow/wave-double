# Epic 7 Context: 전략 확장 — 신규 후보 탐지 기법(F) 통합

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

기존 매수 전략 A/B/C/D/E에 더해 전략 F(각도 가속·이평선 쌍바닥 기법)를 같은 후보 모집단 위에서 OR 조건으로 계산·태깅해, 여섯 전략 중 하나라도 매칭된 후보가 다중 배지와 함께 대시보드에 노출되게 한다. Epic 6(D/E 통합)이 구축한 가변 개수 전제의 다중 태그 인프라를 그대로 재사용하며, Epic 6 자체는 재오픈하지 않는다. 이 에픽은 Epic 4(Story 4.10 힌트 배지 통합 필터)와 Epic 5(Story 5.6/5.12)보다 먼저 완료되어야 한다 — 그렇지 않으면 두 에픽이 5-전략 가정으로 구현된 뒤 재작업이 필요하다.

## Stories

- Story 7.1: 전략 F 계산 로직 코드화 & 백테스트 baseline 이식 (커밋·최종 검토만 남음)
- Story 7.2: `candidate_tags` 전략 제약 확장 (A|B|C|D|E → A|B|C|D|E|F)
- Story 7.3: 전략 계산 API 일반화 — `compute_abc`가 F까지 6개 시그널 키 반환
- Story 7.4: Outcome 판정 로직 F 파라미터화 (TP3%/SL4%/최대보유 없음)
- Story 7.5: 후보 태깅 stage에 전략 F 반영
- Story 7.6: UI 확장 — 라벨·배지·라우트 (F)
- Story 7.7: OOS(워크포워드) 검증 — 전략 F

## Requirements & Constraints

- 후보 모집단(조건검색식 t1859가 뽑은 집합, 백테스트 104종목 전체와 구분) 한정으로 전략 A/B/C/D/E/F 시그널을 계산하고, 시그널이 발생한 종목에 다중 태깅을 부여한다(예 A∩F). 태깅 로직은 백테스트 룰과 일치해야 한다.
- 태깅된 후보만 대시보드에 노출된다. 종가 확정 배치의 태깅만 `candidate_outcome`을 생성할 자격을 가지며, 장중 배치의 태깅은 참고 표시 전용이다.
- 신뢰성(NFR-5): 파이프라인 단계 실패 시 부분 커밋을 허용하되 단계별 완료 여부를 기록하고, 실패한 단계가 이전 단계의 유효 데이터를 덮어쓰거나 삭제해서는 안 된다. 과거에 적재된 outcome 행은 재계산·재판정되지 않아야 한다(불변).
- 공개 리포지토리 운영이므로 전략 F를 포함한 전략 로직·파라미터가 공개됨을 전제로 한다(이미 인지·수용된 트레이드오프, 신규 이슈 아님).
- 실매매 자동화는 범위 밖이며, 이 에픽의 산출물은 추천(태깅)·추적 목적에 한정된다.
- OOS(워크포워드) 검증 미완료 상태에서 태깅 stage(7.5)가 먼저 반영될 수 있으며, 이 경우 "OOS 미검증" 상태를 열린 리스크로 추적하고 검증 완료 시 갱신해야 한다.

## Technical Decisions

- **단일 전략 API 공유(AD-5, Epic 6/7 addendum):** `backtest.strategy_api.compute_abc(frame) -> StrategyResult`가 운영·백테스트 공유 유일 entrypoint다. 함수명은 하위호환을 위해 그대로 유지하되, 반환하는 `StrategyResult`가 A/B/C/D/E/F 6개 시그널 키를 모두 포함하도록 확장한다. 각 전략은 고유한 청산조건(TP/SL/최대보유)을 노출해 outcome 적재가 전략별로 올바르게 적용되게 한다. 같은 일봉에서 TP/SL이 동시 충족되면 SL을 우선한다.
- **F 전용 계산 로직:** `backtest/indicator_opt/strategy_f.py`(`StrategyFParams`: slope_window=30, accel_window=5, min_slope_delta=0.004, ma_db_window=16, TP 3%/SL 4%, tp_first=True, max_holding_bars=None, cost_rate=0.0005)와 `_signals.py`의 범용 `_linreg_slope`/`_double_bottom_signal`이 운영/백테스트 공유 계산 함수에서 재사용되어야 한다("데이터 로더 교체, 지표 로직 무변경" 원칙, A~E와 동일).
- **DB 계약 진화(AD-14):** 모든 스키마 변경은 forward-only expand-migrate-contract로 수행한다(add/expand → backfill/dual-read → consumer 전환 → 다음 release의 contract). CI는 clean db reset, N/N-1 호환성, generated types, SQL fixture parity를 검증해야 한다. Destructive down migration이나 rollback 의존은 금지.
- **`candidate_tags_strategy_check` 제약:** 기존 A|B|C|D|E 확정 제약을 A|B|C|D|E|F로 확장하며, 기존 A/B/C/D/E 행·쿼리는 영향받지 않아야 한다.
- **Outcome 파라미터화:** `outcome_strategy_rules`/`candidate_outcome`의 `cutoff_n`은 `integer not null check (cutoff_n > 0)`이라 NULL 불가 — F의 "최대보유 없음"은 충분히 큰 sentinel 정수(예 999999)로 표현하며 스키마 변경(NOT NULL 제약 완화)은 하지 않는다. 기존 `v_traded_days >= cutoff_n` 비교 로직을 그대로 재사용한다.
- **골든 픽스처 회귀:** `golden_signals.json`에 F 키를 추가하고 Jaccard ≥ 0.9 기준으로 검증한다. 참조 구현은 `strategy_f.py`.
- **Attempt-scoped lineage:** `candidate_tags` 등 attempt-scoped 행은 `attempt_run_id`와 terminal status를 보존하며, 재시도/publication이 이력을 삭제하지 않는다.

## UX & Interaction Patterns

- 전략 태그는 가로로 나열하고, 좁은 폭에서는 줄바꿈 대신 `+N`으로 접힌다(`StrategyTagList.tsx`). 태그 클릭은 필터가 아니라 해당 전략의 설명/성과 페이지(`/strategies/[strategy]`)로 이동한다.
- 색상만으로 전략을 구분해서는 안 되며, 텍스트 라벨이 항상 함께 제공되어야 한다(WCAG 2.2 AA 접근성 플로어). 배지 색상 체계에 F를 추가할 때 접근성 대비를 재확인한다.
- `apps/web/lib/strategy-labels.ts`의 `STRATEGY_LABEL`과 `/strategies/[strategy]` 라우트에 F를 추가하되, 정의되지 않은 전략 코드는 여전히 404 처리되어야 한다.

## Cross-Story Dependencies

- Story 7.1(계산 로직 코드화)이 7.2~7.6의 선행 조건이다.
- Story 7.2(DB 제약)와 7.3(계산 API 일반화)이 완료되어야 Story 7.5(태깅 stage 반영)를 진행할 수 있다.
- Story 7.4(outcome 파라미터화)가 완료되어야 Story 7.5에서 태그가 `emit_open_command`에 전달될 때 F의 청산조건이 정확히 적용된다.
- Story 7.7(OOS 검증)은 7.5와 일정상 병행될 수 있으나, 그 경우 "OOS 미검증" 상태를 대시보드/문서에 명시하고 추적해야 한다.
- 이 에픽은 Epic 4(Story 4.10)·Epic 5(Story 5.6, 5.12)보다 먼저 완료되어야 한다. Epic 3은 순서 무관(간접 영향만 있음 — `candidate_outcome`은 strategy를 문자열로 다루므로 로직 변경 없음).
- Epic 6의 산출물(`candidate_tags` 다중 태그 스키마, `compute_abc`, `StrategyTagList`, 전략별 outcome 파라미터화)을 재사용하며, Epic 6은 재오픈하지 않는다.
