-- Story 5.9 review patch: 최종 view 계약과 catalog comment를 일치시킨다.
-- 앞선 migration은 이미 적용되었으므로 comment만 forward-only로 보강한다.
begin;

comment on view public.candidate_outcome_win_rate_pf_threshold_gated is
  'Story 5.9 final contract: 5-8 CI 판정을 보존하고 게이트 통과 A/B/C만 승률 10%p 초과 또는 PF 25% 초과를 보조 경고로 표시한다. expected_in_ci는 95% CI 1차 판정이며 threshold_warning은 대체하지 않는다. 게이트 미통과·기대치 없는 D/E/F·rollup은 expected_profit_factor·임계값 상수·플래그를 NULL로 둔다. 정확히 경계값은 경고하지 않는다.';

revoke select on table public.candidate_outcome_win_rate_pf_threshold_gated from public, anon, authenticated;

commit;
