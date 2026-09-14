-- 실전 조사(2026-09-14): candidate_outcome_win_rate_pf_threshold_gated의
-- win_rate_threshold_pp/profit_factor_threshold_ratio가 자신의 계약 comment
-- ("게이트 통과 A/B/C만... 게이트 미통과·기대치 없는 D/E/F·rollup은 임계값 상수·플래그를
-- NULL로 둔다", 202609101601)와 달리 sample_gate_passed만 검사하고 있었다.
-- expected baseline이 있는 A/B/C 외 D/E/F도 30건 표본만 채우면 이 두 상수가 채워지는
-- 결함을 이 SQL fixture(tests/sql/test_get_outcome_metric_comparison.sql)가 처음
-- 실행되며 드러냈다. win_rate_threshold_breached/profit_factor_threshold_breached는
-- 이미 expected_*_is not null 가드가 있어 정상이었다 -- 같은 가드를 두 상수 컬럼에도
-- 맞춘다.
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
    case when b.expected_profit_factor is not null then 0.10::numeric end as win_rate_threshold_pp,
    case when b.expected_profit_factor is not null then 0.25::numeric end as profit_factor_threshold_ratio,
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
  'Story 5.9 final contract (202609141500 fix): 5-8 CI 판정을 보존하고 게이트 통과 A/B/C만 승률 10%p 초과 또는 PF 25% 초과를 보조 경고로 표시한다. expected_in_ci는 95% CI 1차 판정이며 threshold_warning은 대체하지 않는다. 게이트 미통과·기대치 없는 D/E/F·rollup은 expected_profit_factor·임계값 상수·플래그를 NULL로 둔다(임계값 상수 두 컬럼도 이제 expected_profit_factor is not null로 A/B/C에 한정한다). 정확히 경계값은 경고하지 않는다.';

commit;
