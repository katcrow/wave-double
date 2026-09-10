-- Story 5.6: 전략(strategy) × 원천(source) 분리 승률·PF view.
-- 5-5 전체 기준 view(candidate_outcome_win_rate_pf)와 동일한 산식·분모 규칙을
-- 전략 × primary source 그룹으로 분리해 반환한다.
-- source는 canonical close 발행 후보의 candidate_source_contrib만 join해 결정한다(AD-21).
-- primary source = contribution_weight 내림차순 → source 우선순위(t1859>t1852>t1856).
-- 파티션은 disjoint이므로 셀 합이 5-5 전체 view와 정확히 일치한다.
-- canonical close 후보가 없는 outcome은 source NULL 그룹으로 노출한다(미수집 ≠ 실제 0).
-- revoke를 통해 browser 역할(anon/authenticated)의 접근을 차단한다.
begin;

create or replace view public.candidate_outcome_win_rate_pf_by_strategy_source as
with resolved as (
  select co.strategy, co.status, co.return_pct, src.source
  from public.candidate_outcome co
  left join lateral (
    select lr.canonical_success_run_id, lr.trading_day
    from public.logical_runs lr
    where lr.batch_kind = 'close'
      and lr.trading_day = co.entry_date
      and lr.canonical_success_run_id is not null
  ) run on true
  left join lateral (
    select cl.candidate_id, cl.attempt_run_id
    from public.candidates cl
    where cl.trading_day = run.trading_day
      and cl.ticker = co.ticker
      and cl.attempt_run_id = run.canonical_success_run_id
  ) cand on true
  left join lateral (
    select cs.source
    from public.candidate_source_contrib cs
    where cs.candidate_id = cand.candidate_id
      and cs.attempt_run_id = cand.attempt_run_id
    order by cs.contribution_weight desc,
      case cs.source when 't1859' then 0 when 't1852' then 1 else 2 end
    limit 1
  ) src on true
),
cells as (
  select
    strategy,
    source,
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')) as total_settled,
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as wins,
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0) as losses,
    count(*) filter (where status = 'OPEN') as open_count,
    count(*) filter (where status = 'SUSPENDED') as suspended_count,
    count(*) filter (where status = 'DELISTED') as delisted_count,
    round(
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0)::numeric
      / nullif(count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')), 0),
      4
    ) as win_rate,
    sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as gross_win,
    abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)) as gross_loss,
    round(
      sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0)
      / nullif(abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)), 0),
      4
    ) as profit_factor
  from resolved
  group by strategy, source
)
select * from cells;

comment on view public.candidate_outcome_win_rate_pf_by_strategy_source is
  'Story 5.6: 전략 × 원천 분리 승률·PF view. 5-5 전체 view와 동일한 산식·분모 규칙을 전략(strategy) × primary source 그룹으로 분리한다. source는 canonical close 발행 후보의 candidate_source_contrib만 join해 결정하며(AD-21), primary source = contribution_weight 내림차순 → source 우선순위(t1859>t1852>t1856). 파티션은 disjoint이므로 셀 합이 5-5 전체 view와 일치한다. canonical close 후보가 없는 outcome은 source NULL 그룹으로 노출해 미수집과 실제 0을 구분한다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.strategy is
  '전략(A/B/C). candidate_outcome이 이미 보유하며 candidate_tags는 join하지 않는다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.source is
  'primary source(t1859/t1852/t1856). canonical close 후보가 없으면 NULL(미수집 ≠ 0).';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.total_settled is
  'TP/SL/TIMEOUT 종결 건수(분모). OPEN/SUSPENDED/DELISTED는 포함되지 않는다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.wins is
  '종결 건 중 return_pct > 0인 건수(승). 승패는 상태가 아니라 손익률 부호로 판정한다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.losses is
  '종결 건 중 return_pct < 0인 건수(패). 승패는 상태가 아니라 손익률 부호로 판정한다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.open_count is
  '현재 추적 중인 OPEN 상태 건수. 분모에서 제외되고 별도 카운트로 노출된다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.suspended_count is
  'SUSPENDED 상태 건수. 정상 종결 3종과 구분되어 별도 카운트로 노출된다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.delisted_count is
  'DELISTED 상태 건수. 정상 종결 3종과 구분되어 별도 카운트로 노출된다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.win_rate is
  '승률 = wins / total_settled (반올림 4자리). total_settled가 0이면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.gross_win is
  '종결 건 중 양의 return_pct의 합(반올림 없음). 양의 손익이 없으면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.gross_loss is
  '종결 건 중 음의 return_pct의 절대값 합(반올림 없음). 음의 손익이 없으면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_source.profit_factor is
  'PF = gross_win / gross_loss (반올림 4자리). gross_loss가 0이면 NULL(ALL_WIN edge).';

revoke select on table public.candidate_outcome_win_rate_pf_by_strategy_source from public, anon, authenticated;

commit;