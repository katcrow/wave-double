-- Supabase SQL fixture for Story 4.5.
-- 모든 검증은 rollback으로 감싸 운영/CI DB에 잔여 데이터를 남기지 않는다.
begin;

create temp table _market_supply_fixture_results (scenario text primary key, status text not null) on commit drop;

do $$
declare
  rel_security boolean;
  constraint_text text;
begin
  select c.relrowsecurity into rel_security
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public' and c.relname = 'market_supply';
  if rel_security is not true then raise exception 'market_supply RLS is not enabled'; end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'market_supply'
      and column_name in ('attempt_run_id', 'market', 'trading_day', 'foreign_net', 'institution_net', 'individual_net', 'program_net', 'collected_at')
    group by table_schema, table_name having count(*) = 8
  ) then raise exception 'market_supply columns are incomplete'; end if;
  if not exists (
    select 1 from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'market_supply' and c.contype = 'u'
      and pg_get_constraintdef(c.oid) like '%attempt_run_id%market%trading_day%'
  ) then raise exception 'market_supply natural key is missing'; end if;
  select string_agg(pg_get_constraintdef(c.oid), ' ') into constraint_text
  from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
  where n.nspname = 'public' and t.relname = 'market_supply' and c.contype = 'c';
  if constraint_text not like '%NaN%' or constraint_text not like '%Infinity%' then
    raise exception 'finite numeric checks are missing';
  end if;
  if not exists (
    select 1 from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'market_supply' and c.contype = 'f'
      and pg_get_constraintdef(c.oid) like '%attempt_run_id%runs%'
  ) then raise exception 'attempt_run_id FK is missing'; end if;
end $$;
insert into _market_supply_fixture_results values ('schema_contract', 'pass');

do $$
declare
  started jsonb;
  attempt_id uuid;
  field_name text;
begin
  started := public.start_attempt('intraday:2099-07-01:11:00', date '2099-07-01', 'intraday', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid;
  foreach field_name in array array['foreign_net', 'institution_net', 'individual_net', 'program_net'] loop
    begin
      execute format(
        'insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
         values ($1, $2, $3, $4, $5, $6, $7)'
      ) using attempt_id, 'KOSPI', date '2099-07-01',
        case when field_name = 'foreign_net' then 'NaN'::numeric else 1 end,
        case when field_name = 'institution_net' then 'Infinity'::numeric else 2 end,
        case when field_name = 'individual_net' then '-Infinity'::numeric else 3 end,
        case when field_name = 'program_net' then 'NaN'::numeric else 4 end;
      raise exception 'finite check did not reject %', field_name;
    exception when check_violation then
      null;
    end;
  end loop;
end $$;
insert into _market_supply_fixture_results values ('finite_value_checks', 'pass');

do $$
declare
  started jsonb;
  attempt_id uuid;
  attempt_two uuid;
  fence bigint;
  lease uuid;
  first_value numeric;
begin
  started := public.start_attempt('intraday:2099-07-01:10:00', date '2099-07-01', 'intraday', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values (attempt_id, 'KOSPI', date '2099-07-01', 100, 200, -300, 40);
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values (attempt_id, 'KOSPI', date '2099-07-01', 999, 200, -300, 40)
  on conflict (attempt_run_id, market, trading_day) do update set foreign_net = excluded.foreign_net;
  select foreign_net into first_value from public.market_supply where attempt_run_id = attempt_id and market = 'KOSPI';
  if first_value <> 999 or (select count(*) from public.market_supply where attempt_run_id = attempt_id) <> 1 then
    raise exception 'same attempt market/day was not idempotently upserted';
  end if;
  started := public.start_attempt('intraday:2099-07-01:10:20', date '2099-07-01', 'intraday', 'manual', 300);
  attempt_two := (started->>'run_id')::uuid;
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values (attempt_two, 'KOSPI', date '2099-07-01', 1, 2, 3, 4);
  if (select count(*) from public.market_supply where market = 'KOSPI' and trading_day = date '2099-07-01') <> 2 then
    raise exception 'another attempt changed or removed the first attempt row';
  end if;
end $$;
insert into _market_supply_fixture_results values ('attempt_scoped_upsert', 'pass');

do $$
declare
  started jsonb;
  attempt_id uuid;
  fence bigint;
  lease uuid;
  snapshot jsonb;
  caught boolean := false;
begin
  started := public.start_attempt('close:2099-07-02', date '2099-07-02', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'MARKET_SUPPLY_STAGE_NOT_COMPLETE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not gate market_supply'; end if;
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');
  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'MARKET_SUPPLY_DATA_INCOMPLETE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not gate incomplete market_supply data'; end if;
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values
    (attempt_id, 'KOSPI', date '2099-07-02', 1, 2, 3, 4),
    (attempt_id, 'KOSDAQ', date '2099-07-02', 5, 6, 7, 8);
  -- stage is already successful; inserting both market rows completes the publish data contract.
  perform public.publish_attempt(attempt_id, fence, lease);
  update public.logical_runs set published_at = timestamptz '2099-07-02 00:00:00+00' where logical_run_key = 'close:2099-07-02';
  snapshot := public.get_dashboard_snapshot();
  if not (snapshot->'complete_snapshot'->'sections' ? 'market_supply') then raise exception 'market_supply section missing'; end if;
  if (snapshot->'complete_snapshot'->'sections'->'market_supply'->>'row_count')::integer <> 2 then raise exception 'market row count is wrong'; end if;
  if snapshot->'missing_sections' @> '["market_supply"]'::jsonb then raise exception 'market_supply remains missing after success'; end if;
end $$;
insert into _market_supply_fixture_results values ('publish_and_snapshot_contract', 'pass');

do $$
begin
  if (select count(*) from _market_supply_fixture_results) <> 4
     or exists (select 1 from _market_supply_fixture_results where status <> 'pass') then
    raise exception 'market supply fixture did not produce exactly three pass rows';
  end if;
end $$;
select scenario, status from _market_supply_fixture_results order by scenario;

rollback;
