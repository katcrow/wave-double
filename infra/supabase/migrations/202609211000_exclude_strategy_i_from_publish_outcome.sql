-- 전략 I(음봉수급쌍끌이)는 outcome 파이프라인 제외 대상으로 설계됐으나
-- (202609161200_expand_candidate_tags_strategy_i.sql 주석 참고) publish_attempt의
-- emit_open_command 순회 쿼리는 실제로 strategy='I' 태그를 걸러내지 않았다.
-- emit_open_command는 p_strategy가 A~H가 아니면 예외를 던지므로(202609151700),
-- close 배치 시점(16:00~20:00 KST와 겹치는 19:30 close)에 전략 I 태그가 하나라도
-- 존재하면 publish_attempt 트랜잭션 전체가 롤백되어 그날 A~H를 포함한 모든 전략의
-- outcome 발행(OPEN/TP/SL/SUSPENDED)이 통째로 막힌다(2026-09-17, 2026-09-18 close
-- 배치가 이렇게 ready_to_publish에서 멈춰 있었다).
--
-- 수정: emit_open_command 순회 대상에서 strategy='I'를 제외한다.
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
  if r.stage_status->>'market_supply' is distinct from 'success' then
    raise exception using message = 'MARKET_SUPPLY_STAGE_NOT_COMPLETE';
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
      where t.attempt_run_id = p_run_id and t.status = 'active' and t.strategy <> 'I'
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
  'close 발행 시 candidates/tags/supply_3day/market_supply 완료를 가드하고 OPEN/SUSPENDED/TP/SL을 판정한다.
  전략 I(음봉수급쌍끌이)는 outcome 파이프라인 제외 대상이라 emit_open_command 순회에서 제외한다
  (2026-09-21 patch: 202609161200 설계 의도를 실제 쿼리에 반영, I 태그 존재 시 emit_open_command가
  A-H 외 전략을 거부해 close 발행 전체가 롤백되던 결함 수정).';

revoke execute on function public.publish_attempt(uuid, bigint, uuid) from public, anon, authenticated;
grant execute on function public.publish_attempt(uuid, bigint, uuid) to service_role;

commit;
