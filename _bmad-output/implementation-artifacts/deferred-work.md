# Deferred Work

## Deferred from: code review (2026-09-01)

- Story 1.3: `logical_runs`와 `runs`의 RLS 정책을 확정한다. 현재 공개 API 테이블이지만 policy 없이 RLS를 활성화하면 배치·후속 dashboard read-model 경계까지 차단되므로, Story 1.8/1.10의 approved view/RPC와 함께 적용한다. 2026-09-01 실제 Supabase SQL fixture와 RPC 권한 검증은 통과했다.
