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
