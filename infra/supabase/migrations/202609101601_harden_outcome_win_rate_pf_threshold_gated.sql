-- Story 5.9 review patch: 게이트 미통과 행에는 expected_profit_factor도 노출하지 않는다.
-- 202609101600을 수정하지 않고 forward-only로 같은 view 계약을 보강한다.
begin;

create or replace view public.candidate_outcome_win_rate_pf_threshold_gated as
with expected as (
  select * from (values
    ('A', 2.0540::numeric),
    ('B', 2.0770::numeric),
    ('C', 1.8159::numeric)
  ) as e(strategy, expected_profit_factor)
),
base as (
  select
    ci.*,
    case when ci.sample_gate_passed then e.expected_profit_factor end as expected_profit_factor
  from public.candidate_outcome_win_rate_pf_ci_gated ci
  left join expected e on e.strategy = ci.strategy
),
thresholds as (
  select
    b.*,
    case when b.sample_gate_passed then 0.10::numeric end as win_rate_threshold_pp,
    case when b.sample_gate_passed then 0.25::numeric end as profit_factor_threshold_ratio,
    case when b.sample_gate_passed
      and b.expected_win_rate is not null
      and b.win_rate is not null
      then abs(b.win_rate - b.expected_win_rate) > 0.10
    end as win_rate_threshold_breached,
    case when b.sample_gate_passed
      and b.expected_profit_factor is not null
      and b.profit_factor is not null
      then abs(b.profit_factor - b.expected_profit_factor) / b.expected_profit_factor > 0.25
    end as profit_factor_threshold_breached
  from base b
)
select
  strategy,
  total_settled,
  wins,
  losses,
  open_count,
  suspended_count,
  delisted_count,
  gross_win,
  gross_loss,
  win_rate,
  profit_factor,
  sample_gate_min_required,
  sample_gate_passed,
  sample_gate_label,
  ci_lower,
  ci_upper,
  expected_win_rate,
  expected_in_ci,
  expected_profit_factor,
  win_rate_threshold_pp,
  profit_factor_threshold_ratio,
  win_rate_threshold_breached,
  profit_factor_threshold_breached,
  case when win_rate_threshold_breached or profit_factor_threshold_breached
    then true
    when win_rate_threshold_breached is null and profit_factor_threshold_breached is null
    then null
    else false
  end as threshold_warning
from thresholds;

revoke select on table public.candidate_outcome_win_rate_pf_threshold_gated from public, anon, authenticated;

comment on view public.candidate_outcome_win_rate_pf_threshold_gated is
  'Story 5.9 final contract: 5-8 CI 판정을 보존하고 게이트 통과 A/B/C만 승률 10%p 초과 또는 PF 25% 초과를 보조 경고로 표시한다. expected_in_ci는 95% CI 1차 판정이며 threshold_warning은 대체하지 않는다. 게이트 미통과·기대치 없는 D/E/F·rollup은 expected_profit_factor·임계값 상수·플래그를 NULL로 둔다. 정확히 경계값은 경고하지 않는다.';

commit;
