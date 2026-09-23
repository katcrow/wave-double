-- 성과 검증 사후 결과 추적에서 종목명을 장기 보존한다.
-- 기존 migration은 수정하지 않고, 후보 원천이 purge된 뒤에도 outcome 화면이
-- 종목명과 코드를 함께 표시할 수 있도록 forward-only로 projection/event를 확장한다.
begin;

alter table public.candidate_outcome
  add column if not exists name text;

comment on column public.candidate_outcome.name is
  'OPEN 시점 candidates.name의 nullable 스냅샷. 원천 후보가 없거나 명칭이 없으면 NULL이며 UI는 ticker를 fallback으로 표시한다.';

-- migration 시점에 아직 보존된 후보가 있는 기존 projection은 한 번만 보강한다.
with source as (
  select
    co.outcome_id,
    (
      select nullif(btrim(c.name), '')
      from public.candidates c
      join public.runs r on r.run_id = c.attempt_run_id
      where c.ticker = co.ticker
        and c.trading_day = co.entry_date
        and c.name is not null
      order by r.started_at desc, r.run_id desc, c.candidate_id desc
      limit 1
    ) as name
  from public.candidate_outcome co
  where co.name is null
)
update public.candidate_outcome co
set name = source.name
from source
where co.outcome_id = source.outcome_id
  and source.name is not null;

-- 새 OPEN event에는 후보 원천에서 확인한 이름을 payload에 스냅샷한다.
create or replace function public.snapshot_outcome_open_name()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  candidate_name text;
begin
  if new.command_type <> 'OPEN' or new.payload->>'entry_date' is null then
    return new;
  end if;

  select nullif(btrim(c.name), '') into candidate_name
  from public.candidates c
  join public.runs r on r.run_id = c.attempt_run_id
  where r.logical_run_key = new.logical_run_key
    and c.ticker = new.ticker
    and c.trading_day::text = new.payload->>'entry_date'
    and c.name is not null
  order by r.started_at desc, r.run_id desc, c.candidate_id desc
  limit 1;

  if candidate_name is not null then
    new.payload := jsonb_set(new.payload, '{name}', to_jsonb(candidate_name), true);
  end if;
  return new;
end;
$$;

drop trigger if exists outcome_events_snapshot_name on public.outcome_events;
create trigger outcome_events_snapshot_name
before insert on public.outcome_events
for each row execute function public.snapshot_outcome_open_name();

-- emit와 기존 rebuild 모두에서 name이 비어 있으면 event payload를 우선하고,
-- 구형 event에는 아직 보존된 candidates를 fallback으로 사용한다.
create or replace function public.snapshot_candidate_outcome_name()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
begin
  if nullif(btrim(new.name), '') is not null then
    new.name := nullif(btrim(new.name), '');
    return new;
  end if;

  select nullif(btrim(oe.payload->>'name'), '') into new.name
  from public.outcome_events oe
  where oe.ticker = new.ticker
    and oe.strategy = new.strategy
    and oe.command_type = 'OPEN'
    and oe.payload->>'entry_date' = new.entry_date::text
  order by oe.created_at desc, oe.event_id desc
  limit 1;
  if new.name is not null then
    return new;
  end if;

  select nullif(btrim(c.name), '') into new.name
  from public.candidates c
  join public.runs r on r.run_id = c.attempt_run_id
  where c.ticker = new.ticker
    and c.trading_day = new.entry_date
    and c.name is not null
  order by r.started_at desc, r.run_id desc, c.candidate_id desc
  limit 1;
  return new;
end;
$$;

drop trigger if exists candidate_outcome_snapshot_name on public.candidate_outcome;
create trigger candidate_outcome_snapshot_name
before insert on public.candidate_outcome
for each row execute function public.snapshot_candidate_outcome_name();

-- 추적 RPC는 직접 테이블 SELECT 권한을 노출하지 않고 canonical name을 함께 반환한다.
create or replace function public.get_outcome_tracking_rows(
  p_status text default null,
  p_strategy text default null,
  p_ticker text default null,
  p_limit integer default 500
) returns jsonb
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
  with normalized as (
    select
      case when p_status in ('TP', 'SL', 'TIMEOUT', 'OPEN', 'SUSPENDED', 'DELISTED') then p_status end as status,
      case when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then p_strategy end as strategy,
      nullif(replace(replace(replace(btrim(p_ticker), E'\\', E'\\\\'), '%', E'\\%'), '_', E'\\_'), '') as ticker,
      least(greatest(coalesce(p_limit, 500), 1), 500) as row_limit
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.entry_date desc, rows.outcome_id desc),
    '[]'::jsonb
  )
  from (
    select
      co.outcome_id,
      co.name,
      co.ticker,
      co.strategy,
      co.entry_date,
      co.status,
      co.exit_date,
      co.return_pct
    from public.candidate_outcome co
    cross join normalized n
    where (n.status is null or co.status = n.status)
      and (n.strategy is null or co.strategy = n.strategy)
      and (n.ticker is null or co.ticker ilike '%' || n.ticker || '%' escape E'\\')
    order by co.entry_date desc, co.outcome_id desc
    limit (select row_limit from normalized)
  ) rows;
$$;

comment on function public.get_outcome_tracking_rows(text, text, text, integer) is
  '인증된 outcome tracking 행과 nullable 종목명 스냅샷을 반환한다. candidate_outcome 직접 SELECT는 계속 차단한다.';

revoke execute on function public.snapshot_outcome_open_name() from public, anon, authenticated;
revoke execute on function public.snapshot_candidate_outcome_name() from public, anon, authenticated;
revoke execute on function public.get_outcome_tracking_rows(text, text, text, integer) from public, anon;
grant execute on function public.get_outcome_tracking_rows(text, text, text, integer) to authenticated, service_role;

commit;
