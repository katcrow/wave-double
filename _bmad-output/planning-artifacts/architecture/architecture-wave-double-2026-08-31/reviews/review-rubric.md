# Reviewer Gate — Good-spine rubric walker (최종 재검토)

- **대상:** `../ARCHITECTURE-SPINE.md`
- **검토 범위:** Good-spine checklist 전체, canonical SPEC package, 기존 `backtest/` 코드
- **최종 판정:** **FAIL — HIGH 1건 수정 후 재확인 필요.** 최초 리뷰의 실행 키, Next.js 보안 패치, broad exception, GitHub Actions 경로 문제는 실질적으로 해소됐다. 그러나 새 AD-13의 partial 공개 규칙이 AD-10의 마지막 정상 스냅샷 보존과 충돌하여 CAP-3/4 데이터가 사라지는 구현을 허용한다.

## 남은 Critical / High

### R-1 — HIGH — partial run 공개가 마지막 정상 스냅샷을 대체해 CAP-3/4를 비울 수 있다

- **근거:** AD-10은 UI가 “마지막 성공 스냅샷을 보존한 채” latest run의 partial/failed 상태를 우선 표시하도록 고정한다. 반면 AD-13은 `screen+tagging`만 끝난 partial도 공개할 수 있고, read view는 한 published `run_id` 안에서만 join하도록 한다. CAP-3 `supply`와 CAP-4 `market` stage가 실패한 partial을 공개하면 그 run 안에는 수급 행이 없지만 이전 성공 run과 join할 수도 없다.
- **영향:** 같은 규칙을 따르는 구현조차 하나는 partial의 후보만 보여 수급/시장 데이터를 비우고, 다른 하나는 AD-10을 따라 이전 성공 스냅샷을 유지할 수 있다. 이는 스파인이 막아야 할 실제 divergence이며, 메인 화면의 CAP-3/4 성공 계약과 stale-data UX를 직접 훼손한다.
- **처분:** **autofix.** `latest_run_status`와 `published_data_pointer`를 분리한다. partial/failed run은 상태 포인터만 갱신하고, 데이터 포인터는 각 read surface의 필수 stage 집합이 완료된 경우에만 원자적으로 이동해야 한다. 메인 대시보드의 필수 집합은 최소 `screen+tagging+supply+market`으로 명시하고, 미완료 시 이전 published snapshot과 최신 run 경고를 함께 반환한다. 하나의 전역 published pointer를 유지하려면 success만 공개 가능하게 제한한다.

## Medium / Low tail

### R-2 — MEDIUM — canonical data-model과 spine의 신규 저장 계약이 아직 동기화되지 않았다

- AD-3의 `logical_run_key`/`attempt_no`, AD-9의 `outcome_observations`와 projection lineage, AD-13의 `published_at`, AD-14의 `schema_version`은 canonical `data-model.md`에 없다. 반대로 `data-model.md`는 여전히 `runs.started_at/finished_at`을 KST라고 쓰며, `daily_ohlcv`, `trading_calendar`, `candidate_outcome`, `bias_metrics`의 lineage 정의도 spine과 다르다.
- **처분:** spine의 의도를 유지하고 canonical companion을 함께 갱신한다. SPEC이 companion을 complete contract로 선언하므로 구현 전에 하나의 schema 계약으로 합쳐야 한다.

### R-3 — MEDIUM — 운영 전략 커널 entry point와 canonical DataFrame 계약이 여전히 이름으로 고정되지 않았다

- AD-5는 broad exception을 stage error로 승격하라고 명확히 개선했지만, 기존 `build_signals()` 자체가 예외를 내부에서 삼키므로 외부 wrapper만으로는 오류를 감지할 수 없다. `backtest.indicator_opt.*` wildcard도 어느 함수가 운영 entry point인지 고정하지 않는다.
- **처분:** 운영 호출 함수 하나를 실명으로 지정하고 내부 broad `except` 제거 또는 typed-result 반환을 계약으로 둔다. DataFrame의 필수 index/column/정렬/중복/결측 의미론은 adapter contract test 이름으로 고정하면 된다.

### R-4 — LOW — 일부 cold-start 버전은 지원 범위에는 있으나 최신 maintenance가 아니다

- Next.js 16.3.3 등 주요 패키지는 현재 보안 패치와 일치한다. Node.js 24.17.0은 지원되는 LTS이며 2026-06 보안 릴리스지만, 검토일 현재 같은 LTS 선의 최신은 24.20.0이다. 최신 고정이 목적이 아니라 검증된 호환 조합이라면 허용 가능하나, memlog에 선택 근거를 남기는 편이 정확하다. 공식 릴리스: <https://nodejs.org/en/blog/release/v24.20.0>

## 최초 발견사항 해소 확인

| 최초 finding | 최종 상태 | 확인 내용 |
| --- | --- | --- |
| F-1 장중 실행 키 충돌 | **Resolved** | intraday KST 30-minute slot, attempt UUID, logical key가 분리됐다. |
| F-2 취약한 Next.js 16.2.11 | **Resolved** | 16.3.3 Active LTS로 갱신됐다. |
| F-3 전략 예외의 silent no-signal | **Mostly resolved** | 오류 종목 배포 차단과 stage error 승격이 Rule에 들어갔다. 정확한 entry point는 R-3 tail로 남았다. |
| F-4 잘못된 workflow 경로 | **Resolved** | `.github/workflows/`로 수정됐다. |
| F-5 canonical data-model 불일치 | **Open, Medium** | 신규 AD로 더 명확해졌으나 companion 갱신은 아직 필요하다(R-2). |

## Good-spine checklist 최종 평가

| 체크 | 판정 | 요약 |
| --- | --- | --- |
| 한 단계 아래의 실제 divergence point를 모두 고정 | **Fail** | partial 공개와 정상 스냅샷 유지가 충돌한다(R-1). |
| 모든 AD Rule이 enforceable하고 stated divergence를 실제 방지 | **Fail** | AD-10과 AD-13을 동시에 만족하는 단일 data pointer 동작이 정의되지 않았다. |
| Deferred가 구현 단위의 비호환 선택을 허용하지 않음 | **Pass** | 호스팅, TR 병렬화, 보존 재검토 조건이 명확하다. |
| named tech가 verified-current | **Pass with note** | Next.js 보안 패치는 현재다. Node 24.17은 지원 LTS이나 최신 maintenance 24.20은 아니다(R-4). |
| brownfield를 모순 없이 ratify | **Pass with note** | 기존 kernel 재사용과 오류 승격 방향은 정합하다. entry point 구체화는 R-3에 남았다. |
| SPEC capabilities 전체 커버 | **Fail** | map은 CAP-1~7을 모두 포함하지만 R-1이 CAP-3/4 표시 계약을 깨뜨릴 수 있다. |
| inherited parent spine과 비충돌 | **N/A** | parent spine 없음. |
| feature altitude의 모든 구조 차원을 결정/유예/질문 처리 | **Pass** | 데이터, 보안, 배포/환경, 운영/관측, migration/rollback까지 다룬다. |

## 최종 Gate 결론

R-1을 고쳐 latest run 상태와 published data snapshot의 관계를 하나로 수렴시키면 critical/high는 해소된다. R-2와 R-3은 구현 전 companion/contract 정리로 처리할 수 있는 medium tail이며, R-4는 호환 조합 근거를 기록하면 충분하다.
