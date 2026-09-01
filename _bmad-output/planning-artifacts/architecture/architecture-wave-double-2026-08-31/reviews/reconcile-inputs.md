# Finalize 입력 정합 리뷰

## Verdict

**NEEDS_CHANGES** — 스파인은 주요 런타임·보안·배치 경계를 대체로 수용했지만, 아래 5건은 서로 다른 구현 단위가 독립적으로 만들 경우 호환되지 않을 수 있는 하중 지지 계약이다. Finalize 전에 스파인에 반영해야 한다.

검토 범위: `SPEC.md`, `data-model.md`, `api-map.md`, `backtest-baseline.md`, final `prd.md`, `DESIGN.md`, `EXPERIENCE.md` 대 `ARCHITECTURE-SPINE.md`. 아래에는 단순 UI 표현·상세 스키마 반복이 아니라 누락 또는 충돌만 기록했다.

## Findings

### RI-1 — OPEN 포지션 재진입 금지 계약이 outcome 멱등 키에 반영되지 않았다 (High, conflict)

- **입력 계약:** PRD FR-8은 같은 `(종목코드, strategy)`에 `OPEN` outcome이 있으면 다음 거래일에 다시 태깅돼도 새 진입을 만들지 말라고 명시한다(`prd.md:274`). 이는 선택적·중복 적재를 막는 검증 방벽이기도 하다(`prd.md:417`). `backtest-baseline.md`도 종목당 동시 1포지션과 보유 중 신호 폐기를 확정한다.
- **현재 스파인:** AD-9의 자연 키 `(ticker, strategy, entry_trading_day)`는 거래일이 바뀌면 새 행을 허용한다. “`OPEN`만 새 시장 데이터로 전이”는 기존 행의 전이 규칙일 뿐, 같은 ticker/strategy의 두 번째 OPEN 생성 방지 규칙이 아니다(`ARCHITECTURE-SPINE.md:114`).
- **필요한 정합:** AD-9에 **동일 `(ticker, strategy)`의 미종결 outcome은 최대 1개**라는 invariant와, 종가 태깅 단계가 기존 OPEN을 만나면 신호를 폐기한다는 원자적 생성 규칙을 고정한다. DB partial unique index, transaction/advisory lock 등 구체 수단은 하위 구현에 맡겨도 되지만 경합 시에도 불변식이 유지돼야 한다.

### RI-2 — 폴백 모집단의 provenance가 outcome·성과 지표까지 이어지는 lineage 계약이 없다 (High, omission)

- **입력 계약:** t1859 실패 시 t1852/t1856을 사용하되 동일 모집단으로 간주하지 않고 `source`를 저장해야 한다(`prd.md:117`). 파생 태깅·outcome은 원천별 필터가 가능해야 하고 승률·PF도 원천별 분리 조회해야 한다(`prd.md:122`). `data-model.md:28`은 후보의 `source`를, `EXPERIENCE.md:58,76`은 근거·신뢰도 바·추적 필터에서 원천 노출을 요구한다.
- **현재 스파인:** CAP-1 map과 AD-2/3/6에는 fallback 실행·provenance 전파 계약이 없고, AD-9 outcome 키에도 source 또는 source로 역추적 가능한 관계가 없다. AD-8은 지표 산식을 중앙화하지만 원천별 partition을 고정하지 않는다.
- **필요한 정합:** 후보의 `source`가 candidate tag → outcome → metrics read model까지 손실 없이 추적되는 lineage를 결정하고, 혼합 집계와 원천별 집계를 구분하는 규칙을 AD-2/8 또는 별도 AD로 고정한다. `runs.fallback_used`는 실행 상태일 뿐 행 단위 provenance를 대체하지 못한다.

### RI-3 — CAP-7의 핵심인 모집단 편향 계산 경로와 소유권이 스파인에서 빠졌다 (High, omission)

- **입력 계약:** FR-10은 후보 모집단 시그널과 104종목 백테스트 유니버스 시그널의 교집합·차집합·기회 누락을 종가 배치에서 일 1회 계산한다(`prd.md:299-308`). `data-model.md:78-81`은 `bias_metrics` 저장을, `DESIGN.md:135`와 `EXPERIENCE.md:62`는 추적 화면의 진단 소비자를 고정한다. 이 지표는 모집단 편향을 숨기지 않는 검증 방벽이다(`prd.md:417`).
- **현재 스파인:** CAP-7 map은 `outcome stage, metrics views, /tracking`만 가리키며(`ARCHITECTURE-SPINE.md:200`), 104종목 비교 계산의 batch stage, `bias_metrics` 소유권·보존, read model 계약이 없다.
- **필요한 정합:** close-only bias stage가 어떤 canonical 전략 커널을 사용해 두 집합을 만들고, 결과를 누가 저장·노출하는지 고정한다. 절단된 종목도 기회 누락에 포함되며, UI는 이 지표를 단순 성과 metric과 혼합 계산하지 않는다는 경계를 포함한다.

### RI-4 — M=150 결정론적 절단 규칙과 관측 계약이 누락됐다 (Medium, omission)

- **입력 계약:** NFR-7은 후보가 150을 넘으면 **거래대금 상위**로 결정론적으로 절단하고 `runs.truncated_count`와 화면에 노출하며, 잘린 후보의 시그널은 FR-10 기회 누락에 포함하라고 한다(`prd.md:330`). `data-model.md:22,29`도 실행·후보 단위 관측 필드를 둔다.
- **현재 스파인:** AD-6은 시간 예산 소진 시 `partial`/`unprocessed_count`만 고정한다. 모집단 상한, 정렬 기준, `truncated_count`, 절단과 partial의 의미 차이는 어느 AD나 capability map에도 없다.
- **필요한 정합:** screen stage에서 안정적인 tie-break를 포함한 거래대금 내림차순으로 M=150을 선택하고, **절단은 실패/미처리가 아닌 관측 가능한 정상 경계**임을 고정한다. 같은 입력이면 동일 후보가 선택돼야 하며 truncation lineage가 RI-3으로 이어져야 한다.

### RI-5 — 전략 입력 캐시의 수명주기·최소 이력 계약이 구조에서 누락됐다 (Medium, omission)

- **입력 계약:** FR-3a는 `daily_ohlcv`를 Supabase 영속 캐시로 두고 최소 120거래일을 유지하며, 기존 종목은 1거래일 증분, 신규 종목만 전체 이력을 단일 t8410 호출로 적재한다(`prd.md:155-163`; `data-model.md:40-47`). 이 캐시는 NFR-4의 정리 대상이 아니라 장기 보존 대상이다(`data-model.md:85`).
- **현재 스파인:** AD-5는 canonical DataFrame과 커널 재사용만, AD-6은 호출 예산만 정한다. Structural Seed와 CAP-2 map에는 `daily_ohlcv`의 소유 모듈, 증분 갱신 경계, 120일 미달 후보 처리, 보존 예외가 없다.
- **필요한 정합:** tagging 이전의 OHLCV cache stage와 저장 소유권을 고정하고, `>=120 trading days` readiness gate, 신규/full 대 기존/incremental fetch, cache 장기 보존을 invariant로 명시한다. 그렇지 않으면 batch 구현이 매 실행 전체 조회하거나 90일 snapshot 정리에 함께 삭제해 API 예산과 전략 B 재현성을 동시에 깨뜨릴 수 있다.

## Reconciliation conclusion

위 5건 외에는 입력의 주요 하중 지지 요구사항과 스파인 사이에서 별도의 충돌을 찾지 못했다. 특히 종목별 장중 수급의 `판정 불가`, close-only outcome, 거래일/KST 의미론, Jaccard 0.9 gate, 수치 계산의 SQL read-model 소유권, stale/partial/failed 상태 우선 표시, secret 경계는 현재 AD-4/5/7/8/10/11에 충분히 수용되어 있다.
