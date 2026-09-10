-- Story 5.7: 표본 게이트(30건) 처리 — 전략별 + 전체(rollup) 승률·PF view.
-- candidate_outcome에서 strategy의 rollup(strategy)으로 전략별 행 + 전체 합계 행
-- (strategy IS NULL)을 한 번에 반환한다. 산식·분모 규칙은 5-5
-- (candidate_outcome_win_rate_pf)와 완전 동일하다: TP/SL/TIMEOUT만 분모, 승패는
-- return_pct 부호, OPEN/SUSPENDED/DELISTED는 별도 카운트.
-- 종결(TP+SL+TIMEOUT) 건수가 30 미만이면 win_rate/profit_factor를 NULL로 감추고
-- sample_gate_passed=false, sample_gate_label='표본 부족 (n/30)'을 반환한다.
-- 종결/진행중 카운트는 게이트 상태와 무관하게 항상 채워진다("종결 n건 / 진행중 m건"
-- 병기를 위해 숨기지 않는다).
-- 5-5/5-6 view는 이 migration에서 변경하지 않는다 — 별도 view다.
-- revoke를 통해 browser 역할(anon/authenticated)의 접근을 차단한다.
begin;

create or replace view public.candidate_outcome_win_rate_pf_by_strategy_gated as
with base as (
  select
    strategy,
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')) as total_settled,
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as wins,
    count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0) as losses,
    count(*) filter (where status = 'OPEN') as open_count,
    count(*) filter (where status = 'SUSPENDED') as suspended_count,
    count(*) filter (where status = 'DELISTED') as delisted_count,
    sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as gross_win,
    abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)) as gross_loss
  from public.candidate_outcome
  group by rollup(strategy)
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
  case when total_settled >= 30
    then round(wins::numeric / nullif(total_settled, 0), 4) end as win_rate,
  case when total_settled >= 30
    then round(gross_win / nullif(gross_loss, 0), 4) end as profit_factor,
  30 as sample_gate_min_required,
  (total_settled >= 30) as sample_gate_passed,
  case when total_settled < 30
    then '표본 부족 (' || total_settled || '/30)' end as sample_gate_label
from base;

comment on view public.candidate_outcome_win_rate_pf_by_strategy_gated is
  'Story 5.7: 전략별 + 전체(rollup) 표본 게이트 승률·PF view. candidate_outcome을 rollup(strategy)로 집계해 전략별 행과 strategy IS NULL 전체 합계 행을 함께 반환한다. 산식·분모 규칙은 5-5(candidate_outcome_win_rate_pf)와 완전 동일. 종결(TP/SL/TIMEOUT) 건수가 30 미만이면 win_rate/profit_factor를 NULL로 대체하고 sample_gate_passed=false, sample_gate_label에 표본 부족 문구를 채운다. total_settled/open_count 등 카운트는 게이트 상태와 무관하게 항상 채워진다. 5-5/5-6 view는 그대로 유지되며 이 view가 대체하지 않는다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.strategy is
  '전략(A/B/C). NULL이면 rollup 전체 합계 행이다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.total_settled is
  'TP/SL/TIMEOUT 종결 건수(분모). 게이트 상태와 무관하게 항상 채워진다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.wins is
  '종결 건 중 return_pct > 0인 건수(승). 승패는 상태가 아니라 손익률 부호로 판정한다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.losses is
  '종결 건 중 return_pct < 0인 건수(패). 승패는 상태가 아니라 손익률 부호로 판정한다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.open_count is
  '현재 추적 중인 OPEN 상태 건수. 게이트 상태와 무관하게 항상 채워진다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.suspended_count is
  'SUSPENDED 상태 건수. 게이트 상태와 무관하게 항상 채워진다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.delisted_count is
  'DELISTED 상태 건수. 게이트 상태와 무관하게 항상 채워진다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.gross_win is
  '종결 건 중 양의 return_pct의 합(반올림 없음). 게이트 상태와 무관하게 채워진다. 양의 손익이 없으면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.gross_loss is
  '종결 건 중 음의 return_pct의 절대값 합(반올림 없음). 게이트 상태와 무관하게 채워진다. 음의 손익이 없으면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.win_rate is
  '승률 = wins / total_settled (반올림 4자리). total_settled < 30이면 NULL(표본 게이트 미충족).';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.profit_factor is
  'PF = gross_win / gross_loss (반올림 4자리). total_settled < 30이면 NULL(표본 게이트 미충족). gross_loss가 0이면 NULL(ALL_WIN edge).';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.sample_gate_min_required is
  '표본 게이트 임계값 상수(30). 모든 행에서 동일하다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.sample_gate_passed is
  'total_settled >= 30 여부. false면 win_rate/profit_factor가 NULL로 대체된다.';
comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.sample_gate_label is
  '게이트 미충족 시 "표본 부족 (n/30)"(n=실제 total_settled). 충족 시 NULL.';

revoke select on table public.candidate_outcome_win_rate_pf_by_strategy_gated from public, anon, authenticated;

commit;
