-- 2026-10-06: 성과 추적이 close 배치 당일 하루만 관측하던 구조를, 아직 관측되지 않은 모든
-- 거래일을 날짜순으로 소급 처리하도록 바꾼다.
--
-- 배경: publish_attempt는 logical_row.trading_day 하루의 관측/SUSPENDED/TP·SL만 처리했다.
-- 그래서 (1) close 배치가 publish되지 못한 날(2026-09-22/23/28/30, 10-01)과 (2) 추적 종목이
-- 그날 후보가 아니어서 daily_ohlcv가 갱신되지 않은 날의 관측이 영구히 빠졌고, TP/SL 판정을
-- 놓치거나 보유일(cutoff_n) 카운트가 어긋났다.
--
-- 변경:
-- * track_outcome_day: 한 outcome의 한 거래일에 대해 기존 publish_attempt와 동일한 순서·규칙
--   (관측 기록 -> OPEN이면 가격조정 SUSPENDED 판정 -> 여전히 OPEN이고 진입일 이후면 TP/SL/TIMEOUT)
--   을 적용한다. 판정 로직은 202610011700(전략 L 포함) 본문과 동일하며 기준일만 p_day로 일반화했다.
-- * publish_attempt(close): 종료되지 않은 각 outcome에 대해 daily_ohlcv가 있고 아직 관측이 없는
--   거래일(진입일 ~ 오늘)을 날짜순으로 track_outcome_day에 넘긴다. 오늘만 있던 기존 동작은
--   "미관측 거래일이 오늘 하루"인 특수한 경우로 그대로 보존된다.
-- * 소급 처리로 생기는 이벤트도 현재 close run의 logical_run_key를 감사 앵커로 쓰고, 실제
--   거래일은 payload.trading_day에 남긴다(기존 SUSPENDED/TP/SL 이벤트와 같은 형식).
begin;

create or replace function public.track_outcome_day(
  p_logical_run_key text,
  p_outcome_id uuid,
  p_day date
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  o public.candidate_outcome;
  v_today_close numeric;
  v_pricechk integer;
  v_prev_close numeric;
  v_gap_pct numeric;
  v_should_suspend boolean := false;
  v_via_pricechk boolean := false;
  v_new_event public.outcome_events;
  v_obs_high numeric;
  v_obs_low numeric;
  v_obs_close numeric;
  v_tpsl_status text;
  v_exit_price numeric;
  v_return_pct numeric;
  v_traded_days integer;
  v_suspended jsonb := null;
  v_tp_sl jsonb := null;
begin
  select * into o from public.candidate_outcome where outcome_id = p_outcome_id for update;
  if not found or o.status in ('TP', 'SL', 'TIMEOUT', 'DELISTED') then
    return jsonb_build_object('suspended', null, 'tp_sl', null);
  end if;

  perform public.record_outcome_observation(o.outcome_id, o.ticker, p_day);

  if o.status = 'OPEN' then
    select close, pricechk into v_today_close, v_pricechk
    from public.daily_ohlcv
    where ticker = o.ticker and trading_day = p_day;
    if found then
      if v_pricechk is not null and v_pricechk <> 0 then
        v_should_suspend := true; v_via_pricechk := true;
      else
        select close into v_prev_close from public.daily_ohlcv
        where ticker = o.ticker and trading_day < p_day
        order by trading_day desc limit 1;
        if found and v_prev_close is not null and v_prev_close <> 0 then
          v_gap_pct := abs((v_today_close - v_prev_close) / v_prev_close);
          if v_gap_pct > public.price_adjustment_gap_threshold() then v_should_suspend := true; end if;
        end if;
      end if;

      if v_should_suspend then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
        values (
          o.ticker, o.strategy, 'SUSPENDED', p_logical_run_key,
          jsonb_build_object('trading_day', p_day, 'via_pricechk', v_via_pricechk,
            'pricechk', v_pricechk, 'gap_pct', v_gap_pct)
        ) on conflict (logical_run_key, ticker, strategy, command_type) do nothing
        returning * into v_new_event;
        if found then
          perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
          update public.candidate_outcome set status = 'SUSPENDED' where outcome_id = o.outcome_id;
          perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
          o.status := 'SUSPENDED';
          v_suspended := jsonb_build_object(
            'outcome_id', o.outcome_id, 'ticker', o.ticker, 'strategy', o.strategy,
            'trading_day', p_day, 'via_pricechk', v_via_pricechk, 'gap_pct', v_gap_pct
          );
        end if;
      end if;
    end if;
  end if;

  if o.status = 'OPEN' and o.entry_date < p_day then
    select high, low, close into v_obs_high, v_obs_low, v_obs_close
    from public.outcome_observations
    where outcome_id = o.outcome_id and evaluation_trading_day = p_day;
    if found then
      select count(*) into v_traded_days
      from public.outcome_observations
      where outcome_id = o.outcome_id
        and evaluation_trading_day > o.entry_date
        and evaluation_trading_day <= p_day
        and result_code = 'OK';

      if o.strategy = 'L' then
        -- 전략 L만 TP-first이며, 수익 종가 강제청산을 적용한다.
        if v_obs_high >= o.entry_price * (1.0 + o.tp_pct / 100.0) then
          v_tpsl_status := 'TP';
          v_exit_price := o.entry_price * (1.0 + o.tp_pct / 100.0);
          v_return_pct := o.tp_pct - 0.1;
        elsif v_obs_low <= o.entry_price * (1.0 - o.sl_pct / 100.0) then
          v_tpsl_status := 'SL';
          v_exit_price := o.entry_price * (1.0 - o.sl_pct / 100.0);
          v_return_pct := -o.sl_pct - 0.1;
        elsif v_obs_close > o.entry_price then
          v_tpsl_status := 'TIMEOUT';
          v_exit_price := v_obs_close;
          v_return_pct := (v_obs_close / o.entry_price - 1.0) * 100.0 - 0.1;
        end if;
      elsif v_obs_low <= o.entry_price * (1.0 - o.sl_pct / 100.0) then
        -- 기존 전략은 기존 운영 계약대로 SL-first를 유지한다.
        v_tpsl_status := 'SL';
        v_exit_price := o.entry_price * (1.0 - o.sl_pct / 100.0);
        v_return_pct := -o.sl_pct - 0.1;
      elsif v_obs_high >= o.entry_price * (1.0 + o.tp_pct / 100.0) then
        v_tpsl_status := 'TP';
        v_exit_price := o.entry_price * (1.0 + o.tp_pct / 100.0);
        v_return_pct := o.tp_pct - 0.1;
      elsif v_traded_days >= o.cutoff_n then
        v_tpsl_status := 'TIMEOUT';
        v_exit_price := v_obs_close;
        v_return_pct := (v_obs_close / o.entry_price - 1.0) * 100.0 - 0.1;
      end if;

      if v_tpsl_status is not null then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
        values (
          o.ticker, o.strategy, v_tpsl_status, p_logical_run_key,
          jsonb_build_object('trading_day', p_day, 'exit_price', v_exit_price,
            'return_pct', v_return_pct, 'holding_days', v_traded_days)
        ) on conflict (logical_run_key, ticker, strategy, command_type) do nothing
        returning * into v_new_event;
        if found then
          perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
          update public.candidate_outcome set status = v_tpsl_status,
            exit_date = p_day, exit_price = v_exit_price,
            return_pct = v_return_pct, holding_days = v_traded_days
          where outcome_id = o.outcome_id;
          perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
          v_tp_sl := jsonb_build_object(
            'outcome_id', o.outcome_id, 'ticker', o.ticker, 'strategy', o.strategy,
            'status', v_tpsl_status, 'trading_day', p_day, 'exit_price', v_exit_price,
            'return_pct', v_return_pct, 'holding_days', v_traded_days
          );
        end if;
      end if;
    end if;
  end if;

  return jsonb_build_object('suspended', v_suspended, 'tp_sl', v_tp_sl);
end $$;

comment on function public.track_outcome_day(text, uuid, date) is
  '2026-10-06: 한 outcome의 한 거래일에 대해 관측 기록 -> (OPEN) 가격조정 SUSPENDED 판정 -> (OPEN, 진입일 이후) TP/SL/TIMEOUT 판정을 적용한다. 규칙은 publish_attempt(202610011700) 본문과 동일하고 기준일만 p_day로 일반화했다. 이벤트는 p_logical_run_key를 감사 앵커로, 실제 거래일은 payload.trading_day에 남긴다. publish_attempt가 미관측 거래일을 날짜순으로 소급 처리할 때 사용한다.';

revoke all on function public.track_outcome_day(text, uuid, date) from public, anon, authenticated;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint, p_lease_token uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  r public.runs;
  logical_row public.logical_runs;
  tag_row record;
  track_row record;
  day_row record;
  v_day_result jsonb;
  suspended_transitions jsonb := '[]'::jsonb;
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

  if coalesce(r.stage_status->>'supply_3day', 'pending') in ('pending', 'running') then
    raise exception using message = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE';
  end if;
  if coalesce(r.stage_status->>'market_supply', 'pending') in ('pending', 'running') then
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

    -- 종료되지 않은 outcome마다 아직 관측되지 않은 거래일(진입일 ~ 오늘)을 날짜순으로 처리한다.
    -- close가 publish되지 못한 날이나 일봉이 늦게 채워진 날도 다음 close에서 소급된다.
    for track_row in
      select outcome_id, ticker, entry_date from public.candidate_outcome
      where status not in ('TP', 'SL', 'TIMEOUT', 'DELISTED')
      order by outcome_id
      for update
    loop
      for day_row in
        select d.trading_day
        from public.daily_ohlcv d
        where d.ticker = track_row.ticker
          and d.trading_day >= track_row.entry_date
          and d.trading_day <= logical_row.trading_day
          and not exists (
            select 1 from public.outcome_observations ob
            where ob.outcome_id = track_row.outcome_id
              and ob.evaluation_trading_day = d.trading_day
          )
        order by d.trading_day
      loop
        v_day_result := public.track_outcome_day(r.logical_run_key, track_row.outcome_id, day_row.trading_day);
        if v_day_result->'suspended' is not null and jsonb_typeof(v_day_result->'suspended') = 'object' then
          suspended_transitions := suspended_transitions || jsonb_build_array(v_day_result->'suspended');
        end if;
        if v_day_result->'tp_sl' is not null and jsonb_typeof(v_day_result->'tp_sl') = 'object' then
          tp_sl_transitions := tp_sl_transitions || jsonb_build_array(v_day_result->'tp_sl');
          exit;
        end if;
      end loop;
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

commit;
