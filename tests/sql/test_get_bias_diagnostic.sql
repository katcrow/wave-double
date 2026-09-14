-- Story 5.13 get_bias_diagnostic() 계약 fixture. 모든 데이터 변경은 rollback으로 되돌린다.
begin;

insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
values ('close:2099-09-14', date '2099-09-14', 'close')
on conflict (logical_run_key) do nothing;

do $$
declare
  v_event uuid;
  v jsonb;
  v_keys text[];
begin
  if pg_get_function_result('public.get_bias_diagnostic(date)'::regprocedure) <> 'jsonb' then
    raise exception 'get_bias_diagnostic must return jsonb';
  end if;

  insert into public.bias_events(trading_day, logical_run_key, calculation_meta)
  values (
    date '2099-09-14',
    'close:2099-09-14',
    '{"by_source":{"t1859":{"truncated_only_missed_count":2},"t1852":{"truncated_only_missed_count":1},"t1856":{"truncated_only_missed_count":0}}}'::jsonb
  ) returning bias_event_id into v_event;
  insert into public.bias_event_by_source(
    bias_event_id, source, candidate_pop_signal_count, backtest_universe_signal_count,
    intersection_count, diff_count, missed_opportunity_count
  ) values
    (v_event, 't1859', 5, 9, 3, 2, 8),
    (v_event, 't1852', 2, 9, 1, 1, 8),
    (v_event, 't1856', 1, 9, 0, 1, 9);

  v := public.get_bias_diagnostic(date '2099-09-14');
  select array_agg(key order by key) into v_keys from jsonb_object_keys(v) key;
  if v_keys is distinct from array[
    'backtest_universe_signal_count', 'candidate_population_signal_count', 'has_data',
    'intersection_count', 'missed_opportunity_count', 'trading_day'
  ] then raise exception 'RPC row keys mismatch: %', v_keys; end if;
  if v->>'trading_day' <> '2099-09-14' or v->>'has_data' <> 'true'
    or (v->>'candidate_population_signal_count')::integer <> 8
    or (v->>'backtest_universe_signal_count')::integer <> 9
    or (v->>'intersection_count')::integer <> 4
    or (v->>'missed_opportunity_count')::integer <> 8 then
    raise exception 'RPC aggregate mismatch: %', v;
  end if;
  -- 전역 max(9) - sum(intersection 4) + truncation 보정(3) = 8이다.
  -- source별 missed(8 + 8 + 9)를 합산하면 25이므로 RPC는 이를 사용하지 않는다.
  if (v->>'missed_opportunity_count')::integer = 25 then
    raise exception 'source missed rows were summed directly';
  end if;
  if exists (
    select 1 from jsonb_object_keys(v) key where key not in (
      'trading_day','has_data','candidate_population_signal_count',
      'backtest_universe_signal_count','intersection_count','missed_opportunity_count'
    )
  ) then raise exception 'unexpected RPC key: %', v; end if;
  raise notice 'story 5-13 happy path aggregate and exact row shape: pass';
end $$;

do $$
declare
  v_old uuid;
  v_latest uuid;
  v jsonb;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-09-15', date '2099-09-15', 'close')
  on conflict (logical_run_key) do nothing;

  insert into public.bias_events(trading_day, logical_run_key, calculation_meta, created_at)
  values (date '2099-09-15', 'close:2099-09-15',
    '{"by_source":{"t1859":{"truncated_only_missed_count":0},"t1852":{"truncated_only_missed_count":0},"t1856":{"truncated_only_missed_count":0}}}'::jsonb,
    timestamptz '2099-09-15 00:00:00+00') returning bias_event_id into v_old;
  insert into public.bias_event_by_source(
    bias_event_id, source, candidate_pop_signal_count, backtest_universe_signal_count,
    intersection_count, diff_count, missed_opportunity_count
  ) values
    (v_old, 't1859', 1, 2, 1, 0, 1),
    (v_old, 't1852', 0, 2, 0, 0, 2),
    (v_old, 't1856', 0, 2, 0, 0, 2);

  insert into public.bias_events(trading_day, logical_run_key, calculation_meta, created_at)
  values (date '2099-09-15', 'close:2099-09-15',
    '{"by_source":{"t1859":{"truncated_only_missed_count":2},"t1852":{"truncated_only_missed_count":1},"t1856":{"truncated_only_missed_count":0}}}'::jsonb,
    timestamptz '2099-09-15 00:01:00+00') returning bias_event_id into v_latest;
  insert into public.bias_event_by_source(
    bias_event_id, source, candidate_pop_signal_count, backtest_universe_signal_count,
    intersection_count, diff_count, missed_opportunity_count
  ) values
    (v_latest, 't1859', 5, 9, 3, 2, 8),
    (v_latest, 't1852', 2, 9, 1, 1, 8),
    (v_latest, 't1856', 1, 9, 0, 1, 9);

  v := public.get_bias_diagnostic(date '2099-09-15');
  if v->>'has_data' <> 'true' or v->>'trading_day' <> '2099-09-15'
    or (v->>'candidate_population_signal_count')::integer <> 8
    or (v->>'missed_opportunity_count')::integer <> 8 then
    raise exception 'latest canonical event was not selected: %', v;
  end if;
  raise notice 'story 5-13 latest canonical event selection: pass';
end $$;

do $$
declare
  v_event uuid;
  v jsonb;
  v_caught boolean := false;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-09-16', date '2099-09-16', 'close')
  on conflict (logical_run_key) do nothing;
  insert into public.bias_events(trading_day, logical_run_key, calculation_meta)
  values (date '2099-09-16', 'close:2099-09-16',
    '{"by_source":{"t1859":{"truncated_only_missed_count":0},"t1852":{"truncated_only_missed_count":0},"t1856":{"truncated_only_missed_count":0}}}'::jsonb)
  returning bias_event_id into v_event;
  insert into public.bias_event_by_source(
    bias_event_id, source, candidate_pop_signal_count, backtest_universe_signal_count,
    intersection_count, diff_count, missed_opportunity_count
  ) values
    (v_event, 't1859', 5, 9, 3, 2, 8),
    (v_event, 't1852', 2, 9, 1, 1, 8);

  begin
    v := public.get_bias_diagnostic(date '2099-09-16');
  exception when others then
    if sqlerrm <> 'BIAS_EVENT_INTEGRITY_ERROR' then raise; end if;
    v_caught := true;
  end;
  if not v_caught then raise exception 'partial source event must fail closed: %', v; end if;
  raise notice 'story 5-13 partial source event boundary: pass';
end $$;

do $$
declare
  v_event uuid;
  v jsonb;
  v_caught boolean := false;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-09-17', date '2099-09-17', 'close')
  on conflict (logical_run_key) do nothing;
  insert into public.bias_events(trading_day, logical_run_key, calculation_meta)
  values (date '2099-09-17', 'close:2099-09-17',
    '{"by_source":{"t1859":{"truncated_only_missed_count":"2"},"t1852":{"truncated_only_missed_count":1},"t1856":{"truncated_only_missed_count":0}}}'::jsonb)
  returning bias_event_id into v_event;
  insert into public.bias_event_by_source(
    bias_event_id, source, candidate_pop_signal_count, backtest_universe_signal_count,
    intersection_count, diff_count, missed_opportunity_count
  ) values
    (v_event, 't1859', 5, 9, 3, 2, 8),
    (v_event, 't1852', 2, 9, 1, 1, 8),
    (v_event, 't1856', 1, 9, 0, 1, 9);

  begin
    v := public.get_bias_diagnostic(date '2099-09-17');
  exception when others then
    if sqlerrm <> 'BIAS_EVENT_INTEGRITY_ERROR' then raise; end if;
    v_caught := true;
  end;
  if not v_caught then raise exception 'malformed truncated metadata must fail closed: %', v; end if;
  raise notice 'story 5-13 malformed metadata boundary: pass';
end $$;

do $$
declare v_caught boolean := false;
begin
  begin
    perform public.get_bias_diagnostic(null::date);
  exception when others then
    if sqlerrm <> 'BIAS_TRADING_DAY_REQUIRED' then raise; end if;
    v_caught := true;
  end;
  if not v_caught then raise exception 'null trading day must be rejected'; end if;
  raise notice 'story 5-13 null trading day boundary: pass';
end $$;

do $$
declare v jsonb;
begin
  v := public.get_bias_diagnostic(date '2099-09-18');
  if v->>'trading_day' <> '2099-09-18' or v->>'has_data' <> 'false'
    or v->'candidate_population_signal_count' <> 'null'::jsonb
    or v->'backtest_universe_signal_count' <> 'null'::jsonb
    or v->'intersection_count' <> 'null'::jsonb
    or v->'missed_opportunity_count' <> 'null'::jsonb then
    raise exception 'no-data shape must use has_data=false and null counts: %', v;
  end if;
  raise notice 'story 5-13 no-data shape: pass';
end $$;

do $$
declare v_view text;
begin
  if has_function_privilege('anon', 'public.get_bias_diagnostic(date)'::regprocedure, 'EXECUTE') then
    raise exception 'anon must not execute get_bias_diagnostic';
  end if;
  if not has_function_privilege('authenticated', 'public.get_bias_diagnostic(date)'::regprocedure, 'EXECUTE') then
    raise exception 'authenticated must execute get_bias_diagnostic';
  end if;
  if not exists (
    select 1 from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public' and p.proname = 'get_bias_diagnostic'
      and p.prosecdef and p.proconfig @> array['search_path=pg_catalog, public']::text[]
  ) then raise exception 'RPC must be SECURITY DEFINER with fixed search_path'; end if;
  foreach v_view in array array['bias_events','bias_event_by_source','bias_events_canonical','bias_event_by_source_canonical'] loop
    if has_table_privilege('anon', 'public.' || v_view, 'SELECT') then
      raise exception 'anon must not directly SELECT %', v_view;
    end if;
    if has_table_privilege('authenticated', 'public.' || v_view, 'SELECT') then
      raise exception 'authenticated must not directly SELECT %', v_view;
    end if;
  end loop;
end $$;

set local role authenticated;
do $$
declare v jsonb;
begin
  v := public.get_bias_diagnostic(date '2099-09-14');
  if v->>'has_data' <> 'true' or (v->>'intersection_count')::integer <> 4 then
    raise exception 'authenticated RPC execution failed: %', v;
  end if;
end $$;
reset role;

set local role anon;
do $$
declare v_caught boolean := false;
begin
  begin perform public.get_bias_diagnostic(date '2099-09-14');
  exception when others then v_caught := true;
  end;
  if not v_caught then raise exception 'anon direct RPC call should be denied'; end if;
end $$;
reset role;

select 'PASS'::text as story_5_13_verification;
rollback;
