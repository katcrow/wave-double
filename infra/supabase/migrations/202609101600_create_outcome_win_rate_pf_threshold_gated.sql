-- Story 5.9: 5-8 신뢰구간 판정을 보완하는 고정 이탈 임계값 view.
-- 승률은 기대치 대비 10%p 초과, PF는 기대치 대비 25% 초과인 경우에만
-- 보조 경고를 true로 만든다. 정확히 경계값은 경고하지 않는다.
-- 5-8 view의 게이트와 expected_in_ci를 그대로 소비하며 기존 view는 수정하지 않는다.
begin;

create or replace view public.candidate_outcome_win_rate_pf_threshold_gated as
with expected as (
  select * from (values
    ('A', 2.0540::numeric),
    ('B', 2.0770::numeric),
    ('C', 1.8159::numeric)
  ) as e(strategy, expected_profit_factor)
), enriched as (
  select
    c.*,
    case when c.sample_gate_passed then e.expected_profit_factor end as expected_profit_factor
  from public.candidate_outcome_win_rate_pf_ci_gated c
  left join expected e on e.strategy = c.strategy
), flags as (
  select
    e.*,
    case when e.sample_gate_passed and e.expected_win_rate is not null and e.win_rate is not null then
      abs(e.win_rate - e.expected_win_rate) > 0.10
    end as win_rate_threshold_breached,
    case when e.sample_gate_passed and e.expected_profit_factor is not null and e.profit_factor is not null then
      abs(e.profit_factor - e.expected_profit_factor) / e.expected_profit_factor > 0.25
    end as profit_factor_threshold_breached
  from enriched e
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
  0.10::numeric as win_rate_threshold_pp,
  0.25::numeric as profit_factor_threshold_ratio,
  win_rate_threshold_breached,
  profit_factor_threshold_breached,
  case when win_rate_threshold_breached is not null or profit_factor_threshold_breached is not null then
    coalesce(win_rate_threshold_breached, false) or coalesce(profit_factor_threshold_breached, false)
  end as threshold_warning
from flags;

comment on view public.candidate_outcome_win_rate_pf_threshold_gated is
  'Story 5.9: 5-8 CI gated view를 그대로 소비한다. 게이트 통과 A/B/C에 대해 승률 기대치 대비 10%p 초과 또는 PF 기대치 대비 25% 초과를 보조 경고로 표시한다. expected_in_ci는 95% CI 1차 판정으로 보존하며 threshold_warning은 이를 대체하지 않는다. 정확히 경계값은 경고하지 않고, 게이트 미통과·기대치 없는 D/E/F·rollup은 임계값 결과를 NULL로 둔다.';
comment on column public.candidate_outcome_win_rate_pf_threshold_gated.expected_profit_factor is
  '백테스트 기대 PF: A=2.0540, B=2.0770, C=1.8159. D/E/F·rollup 또는 게이트 미통과 행은 NULL.';
comment on column public.candidate_outcome_win_rate_pf_threshold_gated.win_rate_threshold_pp is
  '승률 보조 이탈 임계값(절대 차이, percentage point 단위): 0.10. 초과(>)할 때만 경고.';
comment on column public.candidate_outcome_win_rate_pf_threshold_gated.profit_factor_threshold_ratio is
  'PF 보조 이탈 임계값(기대 PF 대비 상대 차이): 0.25. 초과(>)할 때만 경고.';
comment on column public.candidate_outcome_win_rate_pf_threshold_gated.win_rate_threshold_breached is
  '게이트 통과 + A/B/C 기대 승률 존재 시 abs(win_rate - expected_win_rate) > 0.10 여부. 그 외 NULL.';
comment on column public.candidate_outcome_win_rate_pf_threshold_gated.profit_factor_threshold_breached is
  '게이트 통과 + A/B/C 기대 PF 및 관측 PF 존재 시 abs(profit_factor - expected_profit_factor) / expected_profit_factor > 0.25 여부. 그 외 NULL.';
comment on column public.candidate_outcome_win_rate_pf_threshold_gated.threshold_warning is
  '승률 또는 PF 보조 이탈 플래그의 OR. 95% CI expected_in_ci를 대체하지 않는 빠른 스크리닝용 결과. 비교할 기대치가 없으면 NULL.';

revoke select on table public.candidate_outcome_win_rate_pf_threshold_gated from public, anon, authenticated;

commit;
