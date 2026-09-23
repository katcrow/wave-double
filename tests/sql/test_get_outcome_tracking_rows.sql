-- Story 5.11 + outcome name: outcome tracking read RPC 계약 fixture. 모든 fixture 데이터는 rollback으로 되돌린다.
begin;

insert into public.candidate_outcome(
  outcome_id, name, ticker, strategy, entry_date, entry_price, status, exit_date, return_pct,
  cutoff_n, holding_days, tp_pct, sl_pct
) values
  ('00000000-0000-4000-8000-000000000601', '테스트 종목 1', 'ZZ001', 'A', '2098-06-01', 1000, 'TP', '2098-06-03', 2.9, 30, 2, 3.0, 3.0),
  ('00000000-0000-4000-8000-000000000602', null, 'ZZ002', 'B', '2098-06-02', 1000, 'SL', '2098-06-04', -3.0, 30, 2, 3.0, 3.0),
  ('00000000-0000-4000-8000-000000000603', null, 'ZZ003', 'C', '2098-06-03', 1000, 'TIMEOUT', '2098-07-01', 0.5, 30, 30, 3.0, 3.0),
  ('00000000-0000-4000-8000-000000000604', null, 'ZZ004', 'D', '2098-06-04', 1000, 'OPEN', null, null, 20, 0, 3.0, 5.0),
  ('00000000-0000-4000-8000-000000000605', null, 'ZZ005', 'E', '2098-06-05', 1000, 'SUSPENDED', null, null, 30, 0, 2.0, 5.0),
  ('00000000-0000-4000-8000-000000000606', null, 'ZZ006', 'F', '2098-06-06', 1000, 'DELISTED', '2098-06-07', null, 999999, 1, 3.0, 4.0),
  ('00000000-0000-4000-8000-000000000607', null, 'ZZ007', 'A', '2098-06-06', 1000, 'TP', '2098-06-07', 1.1, 30, 1, 3.0, 3.0);

do $$
declare
  v jsonb;
  v_row jsonb;
begin
  if pg_get_function_result('public.get_outcome_tracking_rows(text,text,text,integer)'::regprocedure) <> 'jsonb' then
    raise exception 'get_outcome_tracking_rows must return jsonb';
  end if;

  v := public.get_outcome_tracking_rows(null, null, null, 500);
  if jsonb_array_length(v) <> 7 then raise exception 'expected 7 rows, got %', jsonb_array_length(v); end if;
  v_row := v->0;
  if not (v_row ? 'outcome_id' and v_row ? 'name' and v_row ? 'ticker' and v_row ? 'strategy' and v_row ? 'entry_date'
      and v_row ? 'status' and v_row ? 'exit_date' and v_row ? 'return_pct') then
    raise exception 'RPC row shape mismatch: %', v_row;
  end if;
  if v->0->>'outcome_id' <> '00000000-0000-4000-8000-000000000607'
      or v->1->>'outcome_id' <> '00000000-0000-4000-8000-000000000606'
      or v->6->>'status' <> 'TP' then
    raise exception 'rows must be ordered by entry_date desc: %', v;
  end if;
  if exists (
    select 1 from jsonb_array_elements(v) row
    where (select array_agg(key order by key) from jsonb_object_keys(row) key)
      <> array['entry_date','exit_date','name','outcome_id','return_pct','status','strategy','ticker']
      or jsonb_typeof(row->'outcome_id') <> 'string'
      or jsonb_typeof(row->'name') not in ('string', 'null')
      or jsonb_typeof(row->'ticker') <> 'string'
      or jsonb_typeof(row->'strategy') <> 'string'
      or jsonb_typeof(row->'entry_date') <> 'string'
      or jsonb_typeof(row->'status') <> 'string'
      or jsonb_typeof(row->'exit_date') not in ('string', 'null')
      or jsonb_typeof(row->'return_pct') not in ('number', 'null')
      or row->>'status' not in ('TP','SL','TIMEOUT','OPEN','SUSPENDED','DELISTED')
  ) then
    raise exception 'RPC row shape/type mismatch: %', v;
  end if;
  if (select count(*) from jsonb_array_elements(v) row where row->>'status' in ('TP','SL','TIMEOUT','OPEN','SUSPENDED','DELISTED')) <> 7 then
    raise exception 'all six statuses must be returned';
  end if;

  if jsonb_array_length(public.get_outcome_tracking_rows('OPEN', null, null, 500)) <> 1 then raise exception 'status filter failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, 'F', null, 500)) <> 1 then raise exception 'strategy filter failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, 'ZZ00', 500)) <> 7 then raise exception 'ticker filter failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, null, 2)) <> 2 then raise exception 'limit failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, null, 0)) <> 1 then raise exception 'lower limit clamp failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, null, -1)) <> 1 then raise exception 'negative limit clamp failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, null, null)) <> 7 then raise exception 'default limit failed'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows('INVALID', 'INVALID', null, 500)) <> 7 then raise exception 'invalid filters must normalize to all rows'; end if;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, 'ZZ_00', 500)) <> 0 then raise exception 'ticker wildcard must be literal'; end if;
  insert into public.candidate_outcome(
    outcome_id, ticker, strategy, entry_date, entry_price, status, exit_date, return_pct,
    cutoff_n, holding_days, tp_pct, sl_pct
  )
  select gen_random_uuid(), 'LIMIT' || gs::text, 'A', '2099-01-01', 1000, 'OPEN', null, null, 30, 0, 3.0, 3.0
  from generate_series(1, 501) gs;
  if jsonb_array_length(public.get_outcome_tracking_rows(null, null, null, 999)) <> 500 then raise exception 'upper limit clamp failed'; end if;

  -- 신규 OPEN event는 보존된 candidates.name을 payload에 넣고, replay 후 projection에도 복원한다.
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2098-06-08', '2098-06-08', 'close');
  insert into public.runs(
    run_id, logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status
  ) values (
    '00000000-0000-4000-8000-000000000691', 'close:2098-06-08', 1, 1, now() + interval '1 day', 'manual', 'published'
  );
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values ('00000000-0000-4000-8000-000000000692', '00000000-0000-4000-8000-000000000691', 'ZZSNAP', '스냅샷 종목', '2098-06-08', 100);
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values (
    '00000000-0000-4000-8000-000000000693', 'ZZSNAP', 'A', 'OPEN', 'close:2098-06-08',
    jsonb_build_object('entry_date', '2098-06-08', 'entry_price', 100)
  );
  if (select payload->>'name' from public.outcome_events where event_id = '00000000-0000-4000-8000-000000000693') <> '스냅샷 종목' then
    raise exception 'OPEN event name snapshot failed';
  end if;
  perform public.rebuild_outcome_projection();
  if (select name from public.candidate_outcome where ticker = 'ZZSNAP' and strategy = 'A') <> '스냅샷 종목' then
    raise exception 'rebuild must preserve outcome name';
  end if;
  raise notice 'story 5-11 row shape/filter/order/limit assertions: pass';
end $$;

do $$
declare
  v_view text;
begin
  if has_function_privilege('anon', 'public.get_outcome_tracking_rows(text,text,text,integer)'::regprocedure, 'EXECUTE') then
    raise exception 'anon must not execute get_outcome_tracking_rows';
  end if;
  if not has_function_privilege('authenticated', 'public.get_outcome_tracking_rows(text,text,text,integer)'::regprocedure, 'EXECUTE') then
    raise exception 'authenticated must execute get_outcome_tracking_rows';
  end if;
  if not exists (
    select 1 from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public' and p.proname = 'get_outcome_tracking_rows'
      and p.prosecdef and p.proconfig @> array['search_path=pg_catalog, public']::text[]
  ) then
    raise exception 'RPC must be SECURITY DEFINER with fixed search_path';
  end if;
  if has_table_privilege('anon', 'public.candidate_outcome', 'SELECT') then
    raise exception 'anon must not have direct candidate_outcome SELECT';
  end if;
  if has_table_privilege('authenticated', 'public.candidate_outcome', 'SELECT') then
    raise exception 'authenticated must not have direct candidate_outcome SELECT';
  end if;
  foreach v_view in array array[
    'candidate_outcome_win_rate_pf',
    'candidate_outcome_win_rate_pf_by_strategy_gated',
    'candidate_outcome_win_rate_pf_ci_gated',
    'candidate_outcome_win_rate_pf_threshold_gated',
    'candidate_outcome_cutoff_bias_notice'
  ] loop
    if has_table_privilege('authenticated', 'public.' || v_view, 'SELECT') then
      raise exception 'authenticated must not directly SELECT restricted view %', v_view;
    end if;
  end loop;
end $$;

set local role authenticated;
do $$
declare
  v jsonb;
begin
  v := public.get_outcome_tracking_rows(null, 'F', null, 500);
  if jsonb_array_length(v) <> 1 or v->0->>'strategy' <> 'F' then
    raise exception 'authenticated RPC execution failed: %', v;
  end if;
end $$;
reset role;

set local role anon;
do $$
declare
  v_caught boolean := false;
begin
  begin
    perform public.get_outcome_tracking_rows(null, null, null, 500);
  exception when others then v_caught := true;
  end;
  if not v_caught then raise exception 'anon direct RPC call should be denied'; end if;
end $$;
reset role;

do $$ begin raise notice 'story 5-11 ACL assertions: pass'; end $$;
select 'PASS'::text as story_5_11_verification;
rollback;
