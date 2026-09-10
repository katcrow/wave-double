-- Story 5.5: 전체 기준 승률·PF 핵심 산식 view.
-- candidate_outcome의 TP/SL/TIMEOUT 종결 건만 분모로 사용하는
-- versioned read model view를 생성한다.
-- OPEN/SUSPENDED/DELISTED는 분모에서 제외되나 별도 카운트로 노출된다.
-- revoke를 통해 browser 역할(anon/authenticated)의 접근을 차단한다.
begin;

create or replace view public.candidate_outcome_win_rate_pf as
select
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
from public.candidate_outcome;

comment on view public.candidate_outcome_win_rate_pf is
  'Story 5.5: 전체 기준 승률·PF 산식 view. candidate_outcome의 TP/SL/TIMEOUT 종결 건만 분모로 사용하며, 승패는 return_pct 부호로 판정한다. OPEN/SUSPENDED/DELISTED는 별도 카운트로 노출. Python 백테스트 metrics와 동일한 산식을 적용하며, migration gate(JSON+SQL+Python 3중 대조)로 동등성이 검증된다.';
comment on column public.candidate_outcome_win_rate_pf.total_settled is
  'TP/SL/TIMEOUT 종결 건수(분모). OPEN/SUSPENDED/DELISTED는 포함되지 않는다.';
comment on column public.candidate_outcome_win_rate_pf.wins is
  '종결 건 중 return_pct > 0인 건수(승). 승패는 상태가 아니라 손익률 부호로 판정한다.';
comment on column public.candidate_outcome_win_rate_pf.losses is
  '종결 건 중 return_pct < 0인 건수(패). 승패는 상태가 아니라 손익률 부호로 판정한다.';
comment on column public.candidate_outcome_win_rate_pf.open_count is
  '현재 추적 중인 OPEN 상태 건수. 분모에서 제외되고 별도 카운트로 노출된다.';
comment on column public.candidate_outcome_win_rate_pf.suspended_count is
  'SUSPENDED 상태 건수. 정상 종결 3종과 구분되어 별도 카운트로 노출된다.';
comment on column public.candidate_outcome_win_rate_pf.delisted_count is
  'DELISTED 상태 건수. 정상 종결 3종과 구분되어 별도 카운트로 노출된다.';
comment on column public.candidate_outcome_win_rate_pf.win_rate is
  '승률 = wins / total_settled (반올림 4자리). total_settled가 0이면 NULL.';
comment on column public.candidate_outcome_win_rate_pf.gross_win is
  '종결 건 중 양의 return_pct의 합(반올림 없음).';
comment on column public.candidate_outcome_win_rate_pf.gross_loss is
  '종결 건 중 음의 return_pct의 절대값 합(반올림 없음). 음의 손익이 없으면 NULL.';
comment on column public.candidate_outcome_win_rate_pf.profit_factor is
  'PF = gross_win / gross_loss (반올림 4자리). gross_loss가 0이면 NULL(ALL_WIN edge).';

revoke select on table public.candidate_outcome_win_rate_pf from public, anon, authenticated;

commit;
