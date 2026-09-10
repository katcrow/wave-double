---
title: 'Story 5.3: 편향 지표 계산 로직'
type: 'feature'
created: '2026-09-10'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      AGENTS.md에 문서화된 테스트 명령에 pyyaml이 빠져 있어 tools 테스트 3건이
      ModuleNotFoundError로 실패한다(Story 5.2에서도 동일하게 관측).
    evidence: |-
      `uv run --with pandas --with numpy --with pyarrow --with pytest pytest`로 돌리면
      tools/check_sprint_status.py의 `import yaml`이 실패하고, `--with pyyaml`을 더하면
      692건 전부 통과한다. 이 스토리와 무관한 선행 결함이며, 고치려면 agent-context
      문서(AGENTS.md) 또는 pyproject 의존성을 손대야 해 patch가 아니라 defer 대상이다.
    location: >-
      AGENTS.md:23
    severity: medium
  - summary: >-
      운영 `candidates`/`candidate_tags`가 비어 있어 실데이터 기반 편향 계산은 아직
      실증되지 않았다.
    evidence: |-
      운영 Supabase에 published candidate가 0건이라(모든 거래일) 실전 모집단 시그널
      집합을 만들 수 없다. 이번 패스는 산출값을 운영 DB의 실제 check 제약에 통과시키는
      방식(rollback probe, 120행 전건 통과)으로 대체 검증했다. 실데이터 대조는 Story 5.4의
      close 배치 배선 이후에 가능하다.
    location: >-
      apps/batch/bias_metrics.py
    severity: low
baseline_revision: 'ee26be6222f13fdf52c03a39a0c746a7ff3c211a'
baseline_commit: 'ee26be6222f13fdf52c03a39a0c746a7ff3c211a'
---

<intent-contract>

## Intent

**Problem:** Story 5.2가 유니버스 시그널 집합을, Epic 2 태깅이 후보 모집단 시그널을 각각 만들지만, 둘을 대조해 "두 집합 크기 · 교집합 · 차집합 · 기회 누락"을 source별로 산출하는 로직이 없다. 특히 NFR-7 상한(M=150)으로 잘려나간 종목의 시그널은 어디에도 계산되지 않아, 처리 상한이 만드는 조용한 누락이 지표에서 사라진다.

**Approach:** `bias_event_by_source` 한 행이 요구하는 5개 카운트를 source별로 산출하는 순수 계산 함수를 만든다. source 귀속은 `candidate_source_contrib`와 동일한 규칙(weight 내림차순 → `SOURCE_PRIORITY`)으로 도출한 primary source를 쓰고, 절단 종목의 시그널은 Story 5.2의 `compute_universe_signals`를 절단 티커 목록에 재사용해 계산한 뒤 기회 누락에 합산한다. DB 적재와 배치 배선은 하지 않는다.

## Boundaries & Constraints

**Always:** source 도메인은 `domain.candidate_selection.SOURCE_PRIORITY`에서 파생하고 재열거하지 않으며, 기여가 없는 source도 항상 null-safe 0 행으로 생성한다(3행 고정). 시그널 성립 판정은 운영 태깅과 동일한 D-1 확정봉(`iloc[-2]`)이어야 하므로 절단 종목 시그널도 `compute_universe_signals`를 재사용해 계산한다. 카운트는 전략 A~F 합집합 기준 종목 수이며(스키마에 전략 축이 없다), 전략별 분해는 `calculation_meta`에만 담는다. 산출값은 `bias_event_by_source`의 모든 check 제약(음수 불가, 교집합은 두 집합 크기 이하, `pop - intersection <= diff <= pop`, `missed >= universe - intersection`)을 항상 만족해야 하고, 함수가 반환 전에 스스로 검증한다. 같은 입력에는 같은 결과(정렬된 결정론적 출력)가 나온다. 유니버스 집합은 source 축이 없으므로 `backtest_universe_signal_count`는 모든 source 행에 동일한 전역 값이 들어가며 그 의미를 문서와 `calculation_meta`에 명시한다. 유니버스 쪽 `ineligible`/`error`/뒤처진 확정봉 종목 수는 삼켜지지 않고 `calculation_meta`로 노출한다(미수집과 실제 0의 구분).

**Never:** `bias_events`/`bias_event_by_source`에 쓰지 않고 Supabase 클라이언트를 import하지 않는다(적재는 Story 5.4). migration을 추가하거나 기존 migration을 수정하지 않는다. `Stage` enum 값·`write_stage` 계약·`scheduler.py` 배선을 건드리지 않는다(Story 5.4). `tags_stage.py`/`candidate_stage.py`/`universe_signal.py`/`backtest/` 커널의 기존 동작을 변경하지 않는다(읽기·재사용만). 조회 view·RPC·UI(5.6/5.13/5.14)를 만들지 않는다. 승률·PF 등 성과 지표(5.5~5.9)를 계산하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | 3 source에 후보가 고루 분포하고 유니버스 시그널이 일부 겹침 | source 3행 각각에 5개 카운트 산출, 교집합/차집합/기회누락이 아래 산식대로 산출 | 없음 |
| EMPTY_SOURCE | `t1852` 기여 후보 0건 | `pop=0, intersection=0, diff=0, missed=유니버스 시그널 수` 행이 생성됨(누락 아님) | 없음 |
| MULTI_SOURCE_CANDIDATE | 한 후보에 t1856(w=0.5)·t1859(w=0.5) 기여 | primary source는 weight 동률이면 `SOURCE_PRIORITY` 우선(t1859) 하나로만 귀속(분할 계상 금지) | 없음 |
| TRUNCATED_SIGNAL | M=150 밖 절단 종목이 전략 시그널 성립 | 그 종목이 해당 source의 `missed_opportunity_count`에 가산되고, 이미 유니버스 시그널에 있으면 중복 계상되지 않음 | 없음 |
| TRUNCATED_UNCOMPUTABLE | 절단 종목의 일봉 캐시가 부족/오류 | 기회 누락에 넣지 않고 `calculation_meta.truncated`의 ineligible/error로 노출 | 종목 단위 격리 |
| NO_UNIVERSE_SIGNAL | 유니버스 시그널 집합이 비어 있음 | 모든 source의 universe=0, intersection=0, missed는 해당 source 절단 시그널 수 | 없음 |
| STALE_UNIVERSE_BAR | 유니버스 일부 종목의 확정봉이 최신보다 이름 | 계산은 수행하되 `calculation_meta.universe.stale_signal_date_tickers`에 기록 | 실패 아님 |
| CONSTRAINT_SELFCHECK | 산식 오류로 DB check를 위반하는 값이 만들어짐 | 반환 전에 예외로 중단 | `BiasMetricsInvariantError` |
| REPRODUCIBLE | 같은 입력으로 두 번 실행 | 완전히 동일한 결과 | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609091700_create_bias_events.sql:20-41` -- `bias_event_by_source`의 5개 카운트 컬럼과 4개 check 제약. 이 스토리의 산출물이 채워야 하는 계약이며, 자체 검증은 이 제약을 그대로 코드로 옮긴다. `source in ('t1859','t1852','t1856')`.
- `packages/domain/domain/candidate_selection.py:12,21,25-44,46-56,186-200` -- `MAX_CANDIDATES = 150`, `SOURCE_PRIORITY = ("t1859","t1852","t1856")`(source 도메인 단일 원천), `SourceContribution(source, weight)`, `SelectedCandidate(ticker, name, trading_value, sources)`, `CandidateSelection.truncated_candidates`/`all_candidates`. primary source 규칙(weight 내림차순 → priority)의 근거는 `merge_candidate_sources`의 기여자 채택 로직이다.
- `apps/batch/candidate_stage.py:128-133` -- **절단 종목은 DB에 저장되지 않는다**(`candidates`에는 상위 150건만 insert, 절단분은 `runs.truncated_count`로만 보존). 따라서 절단 시그널은 DB 재조회로 얻을 수 없고, 같은 배치 안의 `CandidateSelection.truncated_candidates`를 입력으로 받아야 한다 — 이 스토리 함수 시그니처의 핵심 제약이다.
- `apps/batch/tags_stage.py:53-59,143-166` -- `TaggedCandidate(ticker, candidate_id, strategies, signal_date)`와 시그널 성립 판정 `len(series) >= 2 and bool(series.iloc[-2])`. 후보 모집단 시그널의 원천이며 이 스토리는 이 결과를 입력으로 받는다(재계산하지 않는다).
- `apps/batch/universe_signal.py:60,115-177,229-303` -- `STRATEGY_KEYS`, `UniverseSignalResult(trading_day, universe_size, strategy_signals, ready/ineligible/error_tickers, signal_dates, stale_signal_date_tickers)`, `compute_universe_signals(ohlcv_loader, tickers, trading_day, *, strategy_client, heartbeat)`. **`tickers` 인자가 임의 목록을 받으므로 절단 종목 시그널 계산에 그대로 재사용**한다(동일 확정봉 규칙 보장).
- `apps/batch/ohlcv_cache_loader.py:33-36` -- `OhlcvDbClient` Protocol. 절단 종목 시그널 계산에 주입한다.
- `tests/batch/test_universe_signal.py` -- fake loader/strategy client 주입 패턴과 불변식 테스트 스타일. 이 스토리 테스트도 실 DB·실 API 없이 같은 fake로 구성한다.
- `_bmad-output/implementation-artifacts/spec-5-1-bias_events-append-only-스키마.md` (Design Notes) -- `diff_count`/`missed_opportunity_count`의 산식 확정이 이 스토리 몫이라는 선언과 DB에 남긴 약한 불변식의 의도.
- `tools/epic-path-manifests/epic-5.txt` -- 신규 경로와 이 spec을 추가해야 epic 범위 게이트가 성립한다.
- `AGENTS.md:23` -- 테스트 명령(`uv run --with pandas --with numpy --with pyarrow --with pytest pytest`). pyyaml 미포함은 Story 5.2에서 기록된 선행 결함이다.

## Tasks & Acceptance

**Execution:**
- `apps/batch/bias_metrics.py` -- (a) `resolve_primary_source(sources)`: weight 내림차순 → `SOURCE_PRIORITY` 순으로 단일 source 귀속. (b) `PopulationSignal`/`SourceBiasMetrics`/`BiasMetricsResult` 자료구조와 `BiasMetricsInvariantError`. (c) `compute_bias_metrics(...) -> BiasMetricsResult`: source별 5개 카운트와 `calculation_meta`를 산출하고 DB check 제약을 자체 검증한다. (d) `compute_truncated_signals(ohlcv_loader, truncated_candidates, trading_day, ...)`: `compute_universe_signals`를 절단 티커에 재사용하는 얇은 어댑터 -- Story 5.4가 그대로 append할 수 있는 순수 계산 경계를 만든다.
- `tests/batch/test_bias_metrics.py` -- I/O 매트릭스 9개 시나리오 전부와, 알려진 소규모 입력에 대한 교집합·차집합·기회누락의 **수치적 정확성**을 source별로 검증한다. DB check 제약 4개를 산출값에 직접 적용하는 불변식 테스트와, 절단 종목이 유니버스와 겹칠 때 중복 계상되지 않음을 함께 고정한다 -- 산식 오류가 조용히 적재되는 경로를 막는다.
- `tools/epic-path-manifests/epic-5.txt` -- 신규 경로 2개와 이 spec 파일을 추가한다 -- epic 범위 게이트를 유지한다.

**Acceptance Criteria:**
- Given 후보 모집단 시그널 집합과 유니버스 시그널 집합이 주어진 임의 거래일일 때, when 편향 계산을 실행하면, then `t1859`/`t1852`/`t1856` 세 source 각각에 대해 모집단 크기·유니버스 크기·교집합·차집합이 독립 산출된 3개 행이 반환된다.
- Given 유니버스 시그널 중 후보 모집단에 없는 종목과 M=150으로 절단된 종목의 시그널이 함께 있을 때, when 기회 누락을 계산하면, then 두 종류가 모두 포함되고 서로 겹치는 종목은 한 번만 계상되며, source별 행에 나뉘어 산출된다.
- Given 산출된 세 행을 검사할 때, when `bias_event_by_source`의 check 제약 4개를 그대로 적용하면, then 어떤 입력 조합에서도 위반이 없다.
- Given 저장소 상태를 확인할 때, when 이 스토리의 코드 경로를 추적하면, then `bias_events`/`bias_event_by_source`에 쓰는 코드와 Supabase 클라이언트 import가 없다.
- Given 테스트를 실행할 때, when `uv run --with pandas --with numpy --with pyarrow --with pyyaml --with pytest pytest`를 돌리면, then 신규 테스트를 포함해 전부 통과하고 기존 스위트가 회귀하지 않는다.

## Spec Change Log

## Review Triage Log

### 2026-09-10 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 8: (high 0, medium 3, low 5)
- defer: 2: (high 0, medium 1, low 1)
- dismissed:
  - `backtest_universe_signal_count`가 세 행 모두 같은 전역 값이라 에픽 AC의 "source별 백테스트 시그널"과 어긋난다 — 유니버스에는 source 축이 없고, Story 5.1이 이미 확정한 `missed >= universe - intersection` 제약이 이 해석에서만 항상 참이 된다. 다른 해석은 DB 계약과 충돌한다.
  - 카운트가 전략 A~F 합집합이라 전략별 수치가 컬럼으로 조회되지 않는다 — `bias_event_by_source`에 strategy 축이 없다는 확정된 스키마의 결과이며, 전략별 분해는 `calculation_meta.by_strategy`로 보존된다.
  - primary source 단일 귀속이 다중 기여 후보의 두 번째 source를 보이지 않게 한다 — 정수 카운트 컬럼에 분수 계상을 넣을 수 없고, 에픽 기술 결정이 "primary source는 weight 내림차순 → 우선순위"로 이미 규정한 규칙이다.
  - 미귀속(도메인 밖 source) published 티커가 세 source 행 모두에서 missed로 잡힌다 — 확정된 `missed_s = |(U ∪ T_s) - P_s|` 정의에서 다른 source가 발행한 티커도 s의 기회 누락이므로 정의와 일치한다. 미귀속 목록은 meta로 노출된다.
  - `_priority_rank`의 fallback 분기가 죽은 코드다 — 사전 필터 때문에 도달하지 않을 뿐 결과에 영향이 없다(cosmetic).
  - `frozen=True`가 얕아 `calculation_meta` dict를 소비자가 변형할 수 있다 — 실제 변형 소비자가 없고 결정론성 주장은 산출 시점의 것이다(cosmetic).
  - 배치 모듈인데 로그가 하나도 없다 — 이 모듈은 스펙이 지정한 순수 계산 경계이고 로깅은 stage 오케스트레이터(Story 5.4) 책임이다.
  - 절단/모집단 티커 중복 입력 시 먼저 온 항목이 이긴다 — `merge_candidate_sources`가 티커 유일성을 이미 보장하므로 주장된 경로가 없다.
  - weight가 0 이하인 기여가 primary로 뽑힐 수 있다 — `merge_candidate_sources`는 항상 `1/len(contributing)` > 0을 부여하므로 그런 입력이 만들어지는 경로가 없다.
  - Verification 절의 pyyaml 표기 불일치와 `warnings: ['oversized']` 미해소 — 이 build가 구현 중인 spec 자체를 고치는 수정이라 워크플로우 규칙상 dismiss한다.
  - sprint-status 미갱신·미커밋 — 이 워크플로우 Finalize 단계의 절차이며 코드 결함이 아니다.
  - 운영 배선(`scheduler.py`)과 실배치 e2e가 없다 — close 배치 배선은 Story 5.4의 AC가 명시적으로 소유한다. 실증 자체는 운영 DB rollback probe로 대체했다(아래 검증).
- addressed_findings:
  - `[medium]` `[patch]` P1 6자리 숫자가 아닌 종목코드(예: `00088K`) 하나가 절단 시그널 계산 전체를 예외로 중단시켰다 — `_normalize`가 원문을 흘려보내 `compute_universe_signals`의 `normalize_ticker`에서 터졌다. 정규화 불가 티커를 호출 전에 격리하고 population/절단 양쪽 모두 `calculation_meta`에 노출.
  - `[medium]` `[patch]` P2 `universe_result`/`truncated`의 거래일이 인자 `trading_day`와 다른지 확인하지 않아 다른 날 집합이 오늘 회차로 라벨링될 수 있었다(append-only라 사후 수정 불가). `BiasMetricsInvariantError`로 중단.
  - `[medium]` `[patch]` P3 DB check 제약을 Python으로 옮겨 적었을 뿐 원본 migration과의 drift를 막지 못했다 — migration SQL을 파싱해 source 도메인·4개 named check·5개 카운트 컬럼이 코드와 일치하는지 검증하는 테스트 추가.
  - `[low]` `[patch]` P4 행 단위 제약만 검증하고 결과 단위(정확히 3행, source 유일·도메인 일치)는 검증하지 않았다 — `_check_rows` 추가.
  - `[low]` `[patch]` P5 NaN/무한대 weight가 정렬 결정성을 깼다 — 비유한 값을 0.0으로 정규화.
  - `[low]` `[patch]` P6 조용히 사라지던 정보 노출 — 미지 전략 키, `T_s ∩ P_s` 전제 위반 티커, population과 겹칠 때 어긋나던 `truncated_only_missed_count`를 교정하고, source별 `missed_opportunity_count`가 합산 불가임을 상수·meta로 명시(5.6/5.14가 이 행들을 집계한다).
  - `[low]` `[patch]` P7 no-Supabase 테스트가 줄 시작 import만 grep해 지연 import를 놓치고 경로 추정이 취약했다 — `tokenize` 기반 검사 + 서브프로세스 import 후 `sys.modules` 확인으로 교체.
  - `[low]` `[patch]` P8 Story 5.4가 소비할 seam(`as_rows`/`as_dict`/`row()` KeyError/heartbeat)에 테스트가 없고 재현성 테스트가 population 순서만 뒤집었다 — 각각 테스트 추가.

## Design Notes

**전략 축이 없는 이유.** `bias_event_by_source`에는 strategy 컬럼이 없다. 따라서 한 행의 카운트는 "전략 A~F 중 하나라도 시그널이 성립한 종목 수"(합집합)다. 전략별 분해는 `calculation_meta.by_strategy`에 담아 5.13/5.14가 필요하면 쓰게 하되, 카운트 컬럼의 의미는 합집합 하나로 고정한다.

**source별 유니버스 크기.** 유니버스 104종목에는 source 개념이 없다. 그래서 `backtest_universe_signal_count`는 세 행 모두 같은 전역 값이고, source별로 달라지는 것은 intersection/diff/missed다. DB의 `missed >= universe - intersection` 제약도 이 해석에서만 항상 참이 된다.

**산식.** `P_s` = primary source가 s인 published 후보 중 시그널 성립 종목, `U` = 유니버스 시그널 종목, `T_s` = primary source가 s인 절단 종목 중 시그널 성립 종목.

```
pop_s          = |P_s|
universe_count = |U|                      # 모든 s에 동일
intersection_s = |P_s ∩ U|
diff_s         = |P_s - U|                # 모집단 전용 차집합
missed_s       = |(U ∪ T_s) - P_s|        # = (universe_count - intersection_s) + |T_s - U|
```

`T_s ∩ P_s = ∅`(절단 종목은 published가 아니다)이므로 `missed_s`는 항상 `universe_count - intersection_s` 이상이고, 절단분이 유니버스와 겹치면 자동으로 한 번만 세어진다.

**primary source 단일 귀속.** 한 후보가 두 source에 기여해도 분할 계상하지 않는다. 분수 계상은 정수 카운트 컬럼과 맞지 않고, source별 합이 전체와 어긋나는 해석을 만든다. weight 동률이면 `SOURCE_PRIORITY` 순서가 결정론적 tie-break다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/batch/test_bias_metrics.py` -- expected: 신규 테스트 전부 통과
- `uv run --with pandas --with numpy --with pyarrow --with pyyaml --with pytest pytest` -- expected: 전체 스위트 통과(회귀 없음)
- `python tools/check_epic_scope.py --epic 5 --range ee26be6..HEAD` -- expected: 범위 이탈 경로 없음
- `python tools/check_sprint_status.py` -- expected: 통과

## Auto Run Result

Status: done

### 구현 요약

후보 모집단 시그널과 백테스트 유니버스 시그널을 대조해 `bias_event_by_source` 한 행이 요구하는 5개 카운트를 source별로 산출하는 순수 계산 경계를 만들었다. source 귀속은 `candidate_source_contrib`와 같은 규칙(weight 내림차순 → `SOURCE_PRIORITY`)의 primary source 단일 귀속이고, NFR-7 상한(M=150)으로 절단된 종목의 시그널은 Story 5.2의 `compute_universe_signals`를 절단 티커 목록에 재사용해 계산한 뒤 기회 누락에 합산한다(유니버스와 겹치면 1회만). DB 적재·close 배치 배선·migration은 Story 5.4 몫으로 남겼다.

절단 종목은 `candidates` 테이블에 저장되지 않는다(상위 150건만 insert)는 사실이 이 스토리 설계의 핵심 제약이었다 — 그래서 절단 시그널은 DB 재조회가 아니라 같은 배치의 `CandidateSelection.truncated_candidates`를 입력으로 받는다.

### 변경 파일

- `apps/batch/bias_metrics.py` — `resolve_primary_source`, `PopulationSignal`/`SourceBiasMetrics`/`BiasMetricsResult`/`TruncatedSignals`, `compute_bias_metrics`(5개 카운트 + `calculation_meta` + DB 제약 자체 검증), `compute_truncated_signals`(Story 5.2 진입점 재사용 어댑터). Supabase 미의존.
- `tests/batch/test_bias_metrics.py` — I/O 매트릭스 9행 전건 + 수치 정확성·불변식·migration drift·seam·격리 테스트 31건.
- `tools/epic-path-manifests/epic-5.txt` — 신규 경로 2개와 이 spec 추가.

### 리뷰 결과

리뷰 레이어 4종(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)을 병렬 실행했다. intent_gap 0, bad_spec 0, patch 8건 적용(medium 3, low 5), defer 2건, dismissed 12건. 각 판정 근거는 위 Review Triage Log에 있다.

실질적 결함은 셋이었다. (1) 영숫자 종목코드 하나가 절단 시그널 계산 전체를 예외로 중단시켰다 — 스펙이 요구한 종목 단위 격리가 이 경로에서 깨져 있었다. (2) 입력 집합의 거래일을 대조하지 않아 다른 날 집합이 오늘 회차로 라벨링될 수 있었다(append-only라 복구 불가). (3) DB check 제약을 Python으로 옮겨 적기만 하고 원본 migration과의 drift를 아무것도 막지 않았다.

**후속 리뷰 권고: true** — patch 항목이 medium 3건, low 5건이고 점수는 3×3 + 1×5 = 14로 기준(5) 이상이다. high는 없다.

### 검증

- `uv run --with pandas --with numpy --with pyarrow --with pyyaml --with pytest pytest -q` → **692 passed**(기준선 681 + 신규 11, 이 파일 31건). 회귀 없음.
- I/O 매트릭스 감사: 9개 행(HAPPY_PATH/EMPTY_SOURCE/MULTI_SOURCE_CANDIDATE/TRUNCATED_SIGNAL/TRUNCATED_UNCOMPUTABLE/NO_UNIVERSE_SIGNAL/STALE_UNIVERSE_BAR/CONSTRAINT_SELFCHECK/REPRODUCIBLE) 전부 실행·통과한 테스트로 커버.
- `python tools/check_epic_scope.py --epic 5 --range ee26be6 --worktree` → 변경 경로 4건 전부 epic-5 manifest 안.
- `python tools/check_sprint_status.py` → 통과.
- **운영 Supabase 실측(rollback probe).** UI 표면이 없는 계산 경계라 Playwright e2e는 해당하지 않고, 운영 `candidates`가 0건이라 실데이터 모집단도 만들 수 없다. 대신 무작위 40회 계산이 만든 **source 행 120건의 실제 수치**를 운영 `bias_event_by_source`에 직접 insert해 실 check 제약으로 판정했다 — `constraint_ok=120, constraint_violations=0`. 트랜잭션은 의도적 예외로 중단시켰고 `bias_events`/`bias_event_by_source` 잔여 행이 각각 0임을 재조회로 확인했다. 즉 Python 자체 검증이 아니라 **운영 DB의 진짜 제약**이 산식을 통과시켰다.

### 잔여 리스크

- 실데이터 대조는 아직 없다. 운영에 published candidate가 한 건도 없어 모집단 시그널 집합을 만들 수 없고, 유니버스도 104종목 중 2종목만 백필돼 있다. 실전 수치는 Story 5.4가 close 배치에 배선한 뒤에야 나온다.
- `missed_opportunity_count`는 source별 합산이 불가능하다(각 행이 유니버스 전용 시그널을 중복해 센다). 상수와 `calculation_meta`에 경고를 남겼지만, Story 5.6/5.14의 집계 view가 이를 지키는지는 그쪽 스토리에서 확인해야 한다.
- 미귀속(도메인 밖 source) published 티커는 어느 source 행의 모집단에도 들어가지 않고 `calculation_meta`로만 노출된다. 운영 데이터에서 실제로 발생하는지는 Story 5.4가 확인해야 한다.
