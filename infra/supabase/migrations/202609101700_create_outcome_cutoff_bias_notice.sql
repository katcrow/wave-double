-- Story 5.10: 5.9 성과 판정에 백테스트 부재 TIMEOUT 편향 고지를 부가한다.
-- 5.9 view의 모든 성과·게이트·CI·threshold 컬럼은 그대로 보존하고,
-- candidate_outcome의 실제 TIMEOUT 수와 A/B/C 전용 N=30 baseline만 추가한다.
begin;

create or replace view public.candidate_outcome_cutoff_bias_notice as
with timeout_counts as (
  select
    strategy,
    count(*) filter (where status = 'TIMEOUT')::integer as timeout_count
  from public.candidate_outcome
  group by rollup(strategy)
),
baseline as (
  select * from (values
    ('A', 0.0000::numeric, 0.0000::numeric, 'TIMEOUT 0% / PF차 ±0'),
    ('B', 0.0037::numeric, 0.0125::numeric, 'TIMEOUT 0.37% / PF차 +0.0125'),
    ('C', 0.0000::numeric, 0.0000::numeric, 'TIMEOUT 0% / PF차 ±0')
  ) as b(strategy, cutoff_bias_timeout_rate, cutoff_bias_profit_factor_delta, cutoff_bias_label)
)
select
  threshold.*,
  coalesce(timeout_counts.timeout_count, 0)::integer as timeout_count,
  case when baseline.strategy is not null then 30 end as cutoff_bias_sample_size,
  baseline.cutoff_bias_timeout_rate,
  baseline.cutoff_bias_profit_factor_delta,
  baseline.cutoff_bias_label
from public.candidate_outcome_win_rate_pf_threshold_gated threshold
left join timeout_counts
  on timeout_counts.strategy is not distinct from threshold.strategy
left join baseline
  on baseline.strategy = threshold.strategy;

comment on view public.candidate_outcome_cutoff_bias_notice is
  'Story 5.10: Story 5.9 threshold-gated outcome 성과 컬럼을 그대로 보존하고 실제 candidate_outcome TIMEOUT 건수와 N=30 컷오프 편향 고지를 추가한다. A/B/C baseline은 각각 TIMEOUT 0% / PF차 ±0, TIMEOUT 0.37% / PF차 +0.0125, TIMEOUT 0% / PF차 ±0으로 고정하며 표본 게이트와 독립적이다. D/E/F 및 strategy IS NULL rollup은 실제 timeout_count만 반환하고 baseline 고지 컬럼은 NULL이다.';

comment on column public.candidate_outcome_cutoff_bias_notice.timeout_count is
  'candidate_outcome.status = TIMEOUT의 실제 건수. 표본 게이트와 무관하게 반환하며 TP/SL/TIMEOUT 분모의 TIMEOUT을 재분류하지 않는다.';
comment on column public.candidate_outcome_cutoff_bias_notice.cutoff_bias_sample_size is
  '컷오프 편향 baseline의 고정 표본 크기 N=30. A/B/C만 채우며 게이트 미통과 여부와 무관하다.';
comment on column public.candidate_outcome_cutoff_bias_notice.cutoff_bias_timeout_rate is
  '백테스트에 TIMEOUT이 없는 차이를 알리기 위한 N=30 baseline 비율(A/C 0.0000, B 0.0037). 표시 단위는 UI가 퍼센트로 포맷한다.';
comment on column public.candidate_outcome_cutoff_bias_notice.cutoff_bias_profit_factor_delta is
  'N=30 baseline의 PF 차이(A/C 0.0000, B 0.0125). 성과 PF나 승률을 재계산한 값이 아니다.';
comment on column public.candidate_outcome_cutoff_bias_notice.cutoff_bias_label is
  'UI 표시용 고정 단위 label. A/C는 TIMEOUT 0% / PF차 ±0, B는 TIMEOUT 0.37% / PF차 +0.0125이다.';

revoke select on table public.candidate_outcome_cutoff_bias_notice from public, anon, authenticated;

commit;
