-- Story 4.5 review fix: market_supply stage success만으로 빈/불완전한 발행이 되지 않게 한다.
-- 기존 publish_attempt 함수는 수정하지 않고 runs 상태 전이의 forward-only guard로 보강한다.
begin;

create or replace function public.enforce_market_supply_before_publish()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  expected_day date;
begin
  if new.status = 'published' and old.status is distinct from 'published'
     and new.stage_status->>'market_supply' = 'success' then
    select trading_day into expected_day
    from public.logical_runs
    where logical_run_key = new.logical_run_key;

    if expected_day is null or (
      select count(*)
      from public.market_supply
      where attempt_run_id = new.run_id
        and trading_day = expected_day
        and market in ('KOSPI', 'KOSDAQ')
    ) <> 2 then
      raise exception using message = 'MARKET_SUPPLY_DATA_INCOMPLETE';
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists enforce_market_supply_before_publish on public.runs;
create trigger enforce_market_supply_before_publish
before update of status on public.runs
for each row execute function public.enforce_market_supply_before_publish();

revoke execute on function public.enforce_market_supply_before_publish() from public, anon, authenticated;
grant execute on function public.enforce_market_supply_before_publish() to service_role;

comment on function public.enforce_market_supply_before_publish() is
  'Story 4.5: market_supply stage success 시 KOSPI/KOSDAQ 양 시장의 해당 trading_day 행이 있어야 runs published 전이를 허용한다.';

commit;
