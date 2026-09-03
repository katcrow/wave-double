-- Story 3.1 review follow-up: close gaps the initial outcome schema left open.
-- TRUNCATE bypasses row-level triggers entirely, so the append-only guarantee
-- needs its own statement-level guard alongside the existing UPDATE/DELETE one.
begin;

alter table public.outcome_observations
  add constraint outcome_observations_high_low_close_order check (
    high >= low and close between low and high
  );

alter table public.candidate_outcome
  add constraint candidate_outcome_exit_not_before_entry check (
    exit_date is null or exit_date >= entry_date
  );

comment on column public.candidate_outcome.cutoff_n is
  'TIMEOUT 컷오프 실거래일 수(Story 3.7). 기본값 30은 진입 다음 거래일부터 센 정책 값이며, correction 없이는 소급 변경하지 않는다.';

create or replace function public.reject_outcome_ledger_truncate()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  raise exception using
    errcode = '55000',
    message = format('%I.%I is append-only; TRUNCATE is forbidden', tg_table_schema, tg_table_name);
end;
$$;

create trigger outcome_events_append_only_truncate
before truncate on public.outcome_events
for each statement execute function public.reject_outcome_ledger_truncate();

create trigger outcome_observations_append_only_truncate
before truncate on public.outcome_observations
for each statement execute function public.reject_outcome_ledger_truncate();

commit;
