-- Story 4.1: publish_attempt에 supply_3day stage 완료 가드를 추가하고,
-- get_dashboard_snapshot()이 supply_3day 섹션을 반영하도록 갱신한다.
-- 202609051600의 publish_attempt(3-arg)/202609031600의 get_dashboard_snapshot()을
-- base로 create or replace한다(같은 시그니처이므로 기존 revoke/grant는 그대로 유효).
begin;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint, p_lease_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  r public.runs;
  logical_row public.logical_runs;
  tag_row record;
  track_row record;
  susp_row record;
  tpsl_row record;
  v_today_close numeric;
  v_pricechk integer;
  v_prev_close numeric;
  v_gap_pct numeric;
  v_should_suspend boolean;
  v_via_pricechk boolean;
  v_new_event public.outcome_events;
  suspended_transitions jsonb := '[]'::jsonb;
  v_obs_high numeric;
  v_obs_low numeric;
  v_obs_close numeric;
  v_obs_found boolean;
  v_tpsl_status text;
  v_exit_price numeric;
  v_return_pct numeric;
  v_traded_days integer;
  tp_sl_transitions jsonb := '[]'::jsonb;
begin
  select * into r from runs where run_id = p_run_id;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  perform pg_advisory_xact_lock(hashtextextended(r.logical_run_key, 0));
  select * into r from runs where run_id = p_run_id for update;
  select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
  if logical_row.active_attempt_run_id is distinct from p_run_id
     or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token
     or r.lease_expires_at <= now() then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  if r.status <> 'ready_to_publish' or r.stage_status->>'candidates' <> 'success' then
    raise exception using message = 'PUBLISH_GUARD_FAILED';
  end if;
  if r.stage_status->>'tags' is distinct from 'success' then
    raise exception using message = 'TAGS_STAGE_NOT_COMPLETE';
  end if;
  if r.stage_status->>'supply_3day' is distinct from 'success' then
    raise exception using message = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE';
  end if;
  if exists (
    select 1 from candidates c
    where c.attempt_run_id = p_run_id
      and not exists (
        select 1 from candidate_source_contrib s
        where s.candidate_id = c.candidate_id and s.attempt_run_id = c.attempt_run_id
      )
  ) or exists (
    select 1 from (
      select candidate_id, attempt_run_id, sum(contribution_weight) as total
      from candidate_source_contrib where attempt_run_id = p_run_id
      group by candidate_id, attempt_run_id
    ) s where s.total <> 1
  ) then
    raise exception using message = 'PUBLISH_PROVENANCE_GUARD_FAILED';
  end if;
  if logical_row.canonical_success_run_id is not null then
    raise exception using message = 'CANONICAL_ALREADY_PUBLISHED';
  end if;

  if logical_row.batch_kind = 'close' then
    for tag_row in
      select c.ticker as ticker, t.strategy as strategy
      from candidate_tags t
      join candidates c on c.candidate_id = t.candidate_id and c.attempt_run_id = t.attempt_run_id
      where t.attempt_run_id = p_run_id and t.status = 'active'
    loop
      perform public.emit_open_command(r.logical_run_key, tag_row.ticker, tag_row.strategy);
    end loop;

    for track_row in
      select outcome_id, ticker from public.candidate_outcome
      where status not in ('TP', 'SL', 'TIMEOUT', 'DELISTED')
      for update
    loop
      perform public.record_outcome_observation(track_row.outcome_id, track_row.ticker, logical_row.trading_day);
    end loop;

    for susp_row in
      select outcome_id, ticker, strategy from public.candidate_outcome
      where status = 'OPEN'
      for update
    loop
      v_today_close := null; v_pricechk := null; v_prev_close := null;
      v_gap_pct := null; v_should_suspend := false; v_via_pricechk := false;
      select close, pricechk into v_today_close, v_pricechk
      from public.daily_ohlcv
      where ticker = susp_row.ticker and trading_day = logical_row.trading_day;
      if not found then continue; end if;

      if v_pricechk is not null and v_pricechk <> 0 then
        v_should_suspend := true; v_via_pricechk := true;
      else
        select close into v_prev_close from public.daily_ohlcv
        where ticker = susp_row.ticker and trading_day < logical_row.trading_day
        order by trading_day desc limit 1;
        if found and v_prev_close is not null and v_prev_close <> 0 then
          v_gap_pct := abs((v_today_close - v_prev_close) / v_prev_close);
          if v_gap_pct > public.price_adjustment_gap_threshold() then v_should_suspend := true; end if;
        end if;
      end if;

      if v_should_suspend then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
        values (
          susp_row.ticker, susp_row.strategy, 'SUSPENDED', r.logical_run_key,
          jsonb_build_object('trading_day', logical_row.trading_day, 'via_pricechk', v_via_pricechk,
            'pricechk', v_pricechk, 'gap_pct', v_gap_pct)
        ) on conflict (logical_run_key, ticker, strategy, command_type) do nothing
        returning * into v_new_event;
        if found then
          perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
          update public.candidate_outcome set status = 'SUSPENDED' where outcome_id = susp_row.outcome_id;
          perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
          suspended_transitions := suspended_transitions || jsonb_build_array(jsonb_build_object(
            'outcome_id', susp_row.outcome_id, 'ticker', susp_row.ticker, 'strategy', susp_row.strategy,
            'via_pricechk', v_via_pricechk, 'gap_pct', v_gap_pct
          ));
        end if;
      end if;
    end loop;

    for tpsl_row in
      select outcome_id, ticker, strategy, entry_price, entry_date, tp_pct, sl_pct, cutoff_n
      from public.candidate_outcome
      where status = 'OPEN' and entry_date < logical_row.trading_day
      for update
    loop
      v_obs_high := null; v_obs_low := null; v_obs_close := null; v_traded_days := null;
      v_tpsl_status := null; v_exit_price := null; v_return_pct := null;
      select high, low, close into v_obs_high, v_obs_low, v_obs_close
      from public.outcome_observations
      where outcome_id = tpsl_row.outcome_id and evaluation_trading_day = logical_row.trading_day;
      v_obs_found := found;
      if not v_obs_found then continue; end if;

      select count(*) into v_traded_days
      from public.outcome_observations
      where outcome_id = tpsl_row.outcome_id
        and evaluation_trading_day > tpsl_row.entry_date
        and evaluation_trading_day <= logical_row.trading_day
        and result_code = 'OK';

      if v_obs_low <= tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0) then
        -- 같은 봉에서 TP와 SL이 함께 도달하면 SL을 우선한다.
        v_tpsl_status := 'SL';
        v_exit_price := tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0);
        v_return_pct := -tpsl_row.sl_pct - 0.1;
      elsif v_obs_high >= tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0) then
        v_tpsl_status := 'TP';
        v_exit_price := tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0);
        v_return_pct := tpsl_row.tp_pct - 0.1;
      elsif v_traded_days >= tpsl_row.cutoff_n then
        v_tpsl_status := 'TIMEOUT';
        v_exit_price := v_obs_close;
        v_return_pct := (v_obs_close / tpsl_row.entry_price - 1.0) * 100.0 - 0.1;
      end if;

      if v_tpsl_status is not null then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
        values (
          tpsl_row.ticker, tpsl_row.strategy, v_tpsl_status, r.logical_run_key,
          jsonb_build_object('trading_day', logical_row.trading_day, 'exit_price', v_exit_price,
            'return_pct', v_return_pct, 'holding_days', v_traded_days)
        ) on conflict (logical_run_key, ticker, strategy, command_type) do nothing
        returning * into v_new_event;
        if found then
          perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
          update public.candidate_outcome set status = v_tpsl_status,
            exit_date = logical_row.trading_day, exit_price = v_exit_price,
            return_pct = v_return_pct, holding_days = v_traded_days
          where outcome_id = tpsl_row.outcome_id;
          perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
          tp_sl_transitions := tp_sl_transitions || jsonb_build_array(jsonb_build_object(
            'outcome_id', tpsl_row.outcome_id, 'ticker', tpsl_row.ticker, 'strategy', tpsl_row.strategy,
            'status', v_tpsl_status, 'exit_price', v_exit_price, 'return_pct', v_return_pct,
            'holding_days', v_traded_days
          ));
        end if;
      end if;
    end loop;

    update runs set stage_status = jsonb_set(stage_status, array['outcome_tracking'], to_jsonb('success'::text))
    where run_id = p_run_id;
  end if;

  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id,
    canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end,
    published_at = now() where logical_run_key = r.logical_run_key;
  return jsonb_build_object(
    'run_id', p_run_id, 'status', 'published',
    'canonical_success_run_id', case when logical_row.batch_kind = 'close' then p_run_id else null end,
    'suspended_transitions', suspended_transitions, 'tp_sl_transitions', tp_sl_transitions
  );
end $$;

comment on function public.publish_attempt(uuid, bigint, uuid) is
  'Story 4.1: 기존 close publish/관찰/SUSPENDED/DELISTED/TP-SL 흐름을 유지하면서, tags에 이어 supply_3day
  stage도 success여야만(SUPPLY_3DAY_STAGE_NOT_COMPLETE 가드) 발행을 진행한다(candidates/tags/supply_3day
  모두 batch_kind 무관 필수 stage, story 4.1 Always 규칙).';

create or replace function public.get_dashboard_snapshot()
returns jsonb
language plpgsql
security definer
stable
set search_path = public
as $$
declare
  complete_logical public.logical_runs%rowtype;
  complete_run public.runs%rowtype;
  latest_run public.runs%rowtype;
  latest_logical public.logical_runs%rowtype;
  candidate_count integer := 0;
  tag_count integer := 0;
  open_count integer := 0;
  supply_row_count integer := 0;
  has_complete boolean := false;
  has_latest boolean := false;
  has_outcome_tracking boolean := false;
  has_supply_3day boolean := false;
  sections jsonb;
  available_sections jsonb := '[]'::jsonb;
  missing_sections jsonb := '[]'::jsonb;
begin
  select * into complete_logical
    from logical_runs
    where current_complete_run_id is not null
    order by published_at desc nulls last, logical_run_key desc
    limit 1;

  if complete_logical.logical_run_key is not null then
    select * into complete_run from runs where run_id = complete_logical.current_complete_run_id;
    if complete_run.run_id is not null then
      has_complete := true;
      select count(*) into candidate_count from candidates where attempt_run_id = complete_run.run_id;
      select count(*) into tag_count from candidate_tags where attempt_run_id = complete_run.run_id;
      has_supply_3day := complete_run.stage_status->>'supply_3day' = 'success';
      if has_supply_3day then
        select count(*) into supply_row_count from supply_3day where attempt_run_id = complete_run.run_id;
      end if;
      has_outcome_tracking := complete_logical.batch_kind = 'close' and complete_run.stage_status->>'outcome_tracking' = 'success';
      if has_outcome_tracking then
        select count(*) into open_count
          from outcome_events
          where logical_run_key = complete_run.logical_run_key and command_type = 'OPEN';
      end if;
    end if;
  end if;

  select * into latest_run from runs order by started_at desc, run_id desc limit 1;
  if latest_run.run_id is not null then
    has_latest := true;
    select * into latest_logical from logical_runs where logical_run_key = latest_run.logical_run_key;
  end if;

  sections := jsonb_build_object(
    'candidates', jsonb_build_object(
      'candidate_count', candidate_count,
      'truncated_count', complete_run.truncated_count,
      'original_count', complete_run.original_count,
      'excluded_count', complete_run.excluded_count
    ),
    'tags', jsonb_build_object('tag_count', tag_count)
  );
  if has_supply_3day then
    sections := sections || jsonb_build_object('supply_3day', jsonb_build_object('row_count', supply_row_count));
  end if;
  if has_outcome_tracking then
    sections := sections || jsonb_build_object('outcome_tracking', jsonb_build_object('open_count', open_count));
  end if;

  -- 파이프라인 순서(candidates -> tags -> supply_3day -> market_supply -> outcome_tracking)를
  -- 그대로 따른다. market_supply는 이번 스토리 범위 밖(Story 4.5)이라 항상 missing이다.
  available_sections := '["candidates", "tags"]'::jsonb;
  if has_supply_3day then
    available_sections := available_sections || '["supply_3day"]'::jsonb;
  end if;
  if has_outcome_tracking then
    available_sections := available_sections || '["outcome_tracking"]'::jsonb;
  end if;

  if has_complete then
    missing_sections := '[]'::jsonb;
    if not has_supply_3day then
      missing_sections := missing_sections || '["supply_3day"]'::jsonb;
    end if;
    missing_sections := missing_sections || '["market_supply"]'::jsonb;
    if not has_outcome_tracking then
      missing_sections := missing_sections || '["outcome_tracking"]'::jsonb;
    end if;
  else
    missing_sections := '["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"]'::jsonb;
  end if;

  return jsonb_build_object(
    'no_snapshot', not has_complete,
    'result_code', case when has_complete then 'OK' else 'NO_SNAPSHOT' end,
    'complete_snapshot', case when not has_complete then null else jsonb_build_object(
      'logical_run_key', complete_run.logical_run_key,
      'run_id', complete_run.run_id,
      'trading_day', complete_logical.trading_day,
      'batch_kind', complete_logical.batch_kind,
      'published_at', complete_logical.published_at,
      'sections', sections
    ) end,
    'latest_attempt', case when not has_latest then null else jsonb_build_object(
      'run_id', latest_run.run_id,
      'logical_run_key', latest_run.logical_run_key,
      'trading_day', latest_logical.trading_day,
      'batch_kind', latest_logical.batch_kind,
      'status', latest_run.status,
      'trigger', latest_run.trigger,
      'started_at', latest_run.started_at,
      'finished_at', latest_run.finished_at,
      'stage_status', latest_run.stage_status,
      'unprocessed_count', latest_run.unprocessed_count,
      'truncated_count', latest_run.truncated_count,
      'original_count', latest_run.original_count,
      'excluded_count', latest_run.excluded_count
    ) end,
    'latest_partial_run_id', case when has_latest then latest_logical.latest_partial_run_id else null end,
    'available_partial_sections', case when has_complete then available_sections else '[]'::jsonb end,
    'missing_sections', missing_sections,
    'unprocessed_items', case when has_latest then latest_run.unprocessed_count else 0 end
  );
end;
$$;

comment on function public.get_dashboard_snapshot() is
  'Story 1.8 + Story 2.5 + Story 3.3 + Story 4.1: 대시보드 스냅샷 조회 계약. complete_snapshot과
  latest_attempt를 분리 반환하며, supply_3day stage가 success인 complete attempt는
  sections.supply_3day(row_count)를 노출하고 missing_sections/available_partial_sections에
  파이프라인 순서(candidates/tags/supply_3day/market_supply/outcome_tracking)로 반영한다.';

revoke execute on function public.publish_attempt(uuid, bigint, uuid) from public, anon, authenticated;
grant execute on function public.publish_attempt(uuid, bigint, uuid) to service_role;

commit;
