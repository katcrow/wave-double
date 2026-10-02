- source_spec: `_bmad-output/implementation-artifacts/spec-g-strategy-five-day-overextension-filter.md`
  summary: 전략 G의 기존 warm-up 최소 길이 계산을 풀백 실제 길이에 맞게 재검토한다.
  evidence: `max_pullback=3`이어도 1회 풀백 신호가 더 짧은 입력에서 가능하지만 기존 guard가 이를 제한한다.
- source_spec: `_bmad-output/implementation-artifacts/spec-g-strategy-five-day-overextension-filter.md`
  summary: 전략 G 필터 적용 후 추적 baseline CSV와 성과 수치를 재생성한다.
  evidence: 현재 tracked baseline은 필터 적용 전 131 signal 기록이며 새 실행 결과와 구분이 필요하다.
- source_spec: `_bmad-output/implementation-artifacts/spec-g-strategy-five-day-overextension-filter.md`
  summary: AGENTS의 MVP 이후 BMAD 산출물 유지 정책과 새 spec 산출물 정책을 정리한다.
  evidence: 기존 사용자 변경은 `_bmad-output/` 계획 문서를 더 이상 유지하지 않는다고 선언하면서 이번 spec을 추가했다.
- source_spec: `_bmad-output/implementation-artifacts/spec-g-strategy-five-day-overextension-filter.md`
  summary: AGENTS의 전략 근거 범위를 A~H로 정합화한다.
  evidence: 기존 사용자 변경의 전략 근거 문구가 A~F만 명시하고 G/H를 빠뜨린다.
- source_spec: `_bmad-output/implementation-artifacts/spec-g-strategy-five-day-overextension-filter.md`
  summary: AGENTS의 Supabase 인증/비밀값 보호 절차를 관리 블록과 보존 영역에 정리한다.
  evidence: 기존 사용자 변경에서 애플리케이션 인증과 MCP 연결 분리 확인, `.env.local` 커밋 금지의 상세 절차가 축약 또는 이동됐다.
- source_spec: `_bmad-output/implementation-artifacts/spec-g-strategy-five-day-overextension-filter.md`
  summary: AGENTS 관리 블록 밖의 지속 보존 정책을 정리한다.
  evidence: 기존 Supabase 정책 일부가 refresh 시 교체되는 bmad 관리 블록 안으로 이동됐다.
- source_spec: `_bmad-output/implementation-artifacts/spec-publish-tags-with-reference-supply-partial.md`
  summary: 운영 `get_dashboard_snapshot()` drift를 정리하고 published partial supply의 snapshot/UI/E2E 경계를 검증한다.
  evidence: 운영 함수가 현재 candidates section만 반환해 기존 supply snapshot fixture가 실패하며, 이번 태깅 발행 fixture의 카드/RPC 검증과 독립된 문제다.
- source_spec: `_bmad-output/implementation-artifacts/spec-publish-tags-with-reference-supply-partial.md`
  summary: production 외부 adapter 누락 시 market_supply stage를 명시적 terminal 상태로 기록하는 호환성 경로를 정리한다.
  evidence: scheduler의 legacy optional adapter 경로는 market stage를 건너뛰어 pending으로 남길 수 있으나 production CLI는 모든 adapter를 주입한다.
- source_spec: `_bmad-output/implementation-artifacts/spec-top-trading-candidate-details.md`
  summary: 거래대금 상위 후보의 실제 주요 섹터 원천과 배치 수집 및 기존 후보 backfill을 추가한다.
  evidence: 현재 candidates에 major_sector_name 저장 칼럼과 RPC/UI fallback은 있지만 t1859와 기존 배치가 섹터명을 제공하지 않아 운영 결과가 미확인으로 남는다.
- source_spec: `_bmad-output/implementation-artifacts/spec-top-trading-candidate-details.md`
  summary: 거래대금 상위 참고 영역에 snapshot 거래일과 freshness 상태를 함께 표시한다.
  evidence: 현재 영역은 complete snapshot의 거래일을 데이터로 사용하지만 화면에는 오늘이라는 고정 설명만 표시한다.
- source_spec: `_bmad-output/implementation-artifacts/spec-top-trading-candidate-details.md`
  summary: 구버전 top RPC 응답의 선택적 상세 필드에 대한 점진 배포 호환 처리를 추가한다.
  evidence: 새 웹 shape guard는 migration 적용 후의 상세 필드 계약을 요구하며, migration 선적용 후 웹 배포 순서를 전제로 한다.
- source_spec: `_bmad-output/implementation-artifacts/spec-top-trading-candidate-details.md`
  summary: top RPC 조회 실패와 상세 지표 결측을 화면 상태로 구분해 안내한다.
  evidence: 기존 오류 경계는 콘솔 로깅 후 상단 영역을 숨기고 상세 결측은 미확인으로 표시한다.
- source_spec: `_bmad-output/implementation-artifacts/spec-multi-strategy-candidate-card-sorting.md`
  summary: 운영 Supabase에 후보 카드 정렬 migration과 SQL fixture를 적용하고 실제 RPC/catalog/grant 결과를 확인한다.
  evidence: 현재 세션에는 Supabase MCP와 psql/Docker가 노출되지 않아 로컬 웹 검증만 완료했으며 운영 DB 실행 결과를 확보하지 못했다.
