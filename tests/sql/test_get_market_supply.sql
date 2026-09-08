-- Supabase SQL fixture for Story 4.8 시장 수급 read RPC.
-- 모든 fixture는 rollback되어 실제 데이터는 남기지 않는다.
begin;

do $$
declare
  started jsonb;
  published_run uuid;
  unpublished_run uuid;
  fence bigint;
  lease uuid;
  result jsonb;
begin
  if has_table_privilege('anon', 'public.market_supply', 'select')
     or has_table_privilege('authenticated', 'public.market_supply', 'select') then
    raise exception 'market_supply direct SELECT must remain revoked';
  end if;
  if not has_function_privilege('anon', 'public.get_market_supply(uuid)'::regprocedure, 'EXECUTE')
     or not has_function_privilege('authenticated', 'public.get_market_supply(uuid)'::regprocedure, 'EXECUTE')
     or not has_function_privilege('service_role', 'public.get_market_supply(uuid)'::regprocedure, 'EXECUTE') then
    raise exception 'get_market_supply execute grants are incomplete';
  end if;
  if exists (
    select 1
    from information_schema.routine_privileges
    where specific_schema = 'public'
      and routine_name = 'get_market_supply'
      and grantee = 'PUBLIC'
      and privilege_type = 'EXECUTE'
  ) then
    raise exception 'PUBLIC must not retain execute on get_market_supply';
  end if;

  started := public.start_attempt('close:2099-07-08', date '2099-07-08', 'close', 'manual', 300);
  published_run := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(published_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values
    (published_run, 'KOSPI', date '2099-07-08', 100, -20, 0, 50),
    (published_run, 'KOSDAQ', date '2099-07-08', -10, 30, 40, -5);
  perform public.publish_attempt(published_run, fence, lease);

  result := public.get_market_supply(published_run);
  if jsonb_array_length(result) <> 2
     or result->0->>'market' <> 'KOSPI'
     or result->1->>'market' <> 'KOSDAQ'
     or (result->0->>'foreign_net')::numeric <> 100
     or (result->0->>'individual_net')::numeric <> 0
     or (result->0->>'institution_net')::numeric <> -20
     or (result->0->>'individual_net')::numeric <> 0
     or (result->0->>'program_net')::numeric <> 50
     or result->0->>'trading_day' <> '2099-07-08'
     or result->0->>'collected_at' is null
     or (result->1->>'foreign_net')::numeric <> -10
     or (result->1->>'institution_net')::numeric <> 30
     or (result->1->>'individual_net')::numeric <> 40
     or (result->1->>'program_net')::numeric <> -5
     or result->1->>'trading_day' <> '2099-07-08'
     or result->1->>'collected_at' is null then
    raise exception 'published market rows or signed values are wrong: %', result;
  end if;

  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values (published_run, 'KOSPI', date '2099-07-07', 777, 777, 777, 777);
  if jsonb_array_length(public.get_market_supply(published_run)) <> 2 then
    raise exception 'rows from another trading day leaked into the read RPC';
  end if;

  set local role anon;
  result := public.get_market_supply(published_run);
  if jsonb_array_length(result) <> 2 then
    raise exception 'anon could not execute the security-definer read RPC: %', result;
  end if;
  set local role postgres;

  -- 동일 logical run의 이전 published attempt는 current complete pointer에서 제외한다.
  started := public.start_attempt('intraday:2099-07-08:10:00', date '2099-07-08', 'intraday', 'manual', 300);
  published_run := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(published_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values
    (published_run, 'KOSPI', date '2099-07-08', 1, 1, 1, 1),
    (published_run, 'KOSDAQ', date '2099-07-08', 2, 2, 2, 2);
  perform public.publish_attempt(published_run, fence, lease);

  started := public.start_attempt('intraday:2099-07-08:10:00', date '2099-07-08', 'intraday', 'manual', 300);
  unpublished_run := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(unpublished_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(unpublished_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(unpublished_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(unpublished_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(unpublished_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(unpublished_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(unpublished_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(unpublished_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values
    (unpublished_run, 'KOSPI', date '2099-07-08', 3, 3, 3, 3),
    (unpublished_run, 'KOSDAQ', date '2099-07-08', 4, 4, 4, 4);
  perform public.publish_attempt(unpublished_run, fence, lease);
  if public.get_market_supply(published_run) <> '[]'::jsonb
     or jsonb_array_length(public.get_market_supply(unpublished_run)) <> 2 then
    raise exception 'previous published attempt was not isolated from current complete attempt';
  end if;

  started := public.start_attempt('intraday:2099-07-08:10:30', date '2099-07-08', 'intraday', 'manual', 300);
  unpublished_run := (started->>'run_id')::uuid;
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values (unpublished_run, 'KOSPI', date '2099-07-08', 999, 999, 999, 999);
  if public.get_market_supply(unpublished_run) <> '[]'::jsonb then
    raise exception 'unpublished attempt was exposed';
  end if;
end $$;

select 'story_4_8_market_supply_read: pass' as result;

rollback;
