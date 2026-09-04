-- Story 6.5 (AD-14 forward-only): outcome 청산 파라미터를 전략별로 고정한다.
-- 기존 migration은 수정하지 않는다. 기존 A/B/C projection은 저장된 cutoff_n을 보존하고,
-- 새 파라미터 컬럼만 legacy 3%/3% 값으로 backfill한다.
begin;

create table public.outcome_strategy_rules (
  strategy text primary key check (strategy in ('A', 'B', 'C', 'D', 'E')),
  tp_pct numeric not null check (
    tp_pct > 0 and tp_pct <> 'NaN'::numeric and tp_pct <> 'Infinity'::numeric and tp_pct <> '-Infinity'::numeric
  ),
  sl_pct numeric not null check (
    sl_pct > 0 and sl_pct <> 'NaN'::numeric and sl_pct <> 'Infinity'::numeric and sl_pct <> '-Infinity'::numeric
  ),
  cutoff_n integer not null check (cutoff_n > 0),
  created_at timestamptz not null default now()
);

insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
values
  ('A', 3.0, 3.0, 30),
  ('B', 3.0, 3.0, 30),
  ('C', 3.0, 3.0, 30),
  ('D', 3.0, 5.0, 20),
  ('E', 2.0, 5.0, 30)
on conflict (strategy) do nothing;

alter table public.outcome_strategy_rules enable row level security;
revoke all on table public.outcome_strategy_rules from public, anon, authenticated;
grant select on table public.outcome_strategy_rules to service_role;

alter table public.candidate_outcome
  add column if not exists tp_pct numeric default 3.0,
  add column if not exists sl_pct numeric default 3.0;

-- 기존 행은 outcome별 cutoff_n을 절대 덮어쓰지 않는다. 파라미터 컬럼이 이미 존재하는
-- 환경에서도 NULL인 legacy 행만 A/B/C 값으로 채운다.
do $$
begin
  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  update public.candidate_outcome
  set tp_pct = 3.0
  where tp_pct is null and strategy in ('A', 'B', 'C');
  update public.candidate_outcome
  set sl_pct = 3.0
  where sl_pct is null and strategy in ('A', 'B', 'C');
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
end $$;

alter table public.candidate_outcome
  alter column tp_pct set default 3.0,
  alter column tp_pct set not null,
  alter column sl_pct set default 3.0,
  alter column sl_pct set not null;

alter table public.outcome_events
  drop constraint if exists outcome_events_strategy_check,
  add constraint outcome_events_strategy_check check (strategy in ('A', 'B', 'C', 'D', 'E'));

alter table public.candidate_outcome
  drop constraint if exists candidate_outcome_strategy_check,
  add constraint candidate_outcome_strategy_check check (strategy in ('A', 'B', 'C', 'D', 'E'));

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.candidate_outcome'::regclass
      and conname = 'candidate_outcome_tp_pct_check'
  ) then
    alter table public.candidate_outcome add constraint candidate_outcome_tp_pct_check check (
      tp_pct > 0 and tp_pct <> 'NaN'::numeric and tp_pct <> 'Infinity'::numeric and tp_pct <> '-Infinity'::numeric
    );
  end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.candidate_outcome'::regclass
      and conname = 'candidate_outcome_sl_pct_check'
  ) then
    alter table public.candidate_outcome add constraint candidate_outcome_sl_pct_check check (
      sl_pct > 0 and sl_pct <> 'NaN'::numeric and sl_pct <> 'Infinity'::numeric and sl_pct <> '-Infinity'::numeric
    );
  end if;
end $$;

create or replace function public.emit_open_command(
  p_logical_run_key text,
  p_ticker text,
  p_strategy text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  logical_row public.logical_runs;
  existing_open public.candidate_outcome;
  new_event public.outcome_events;
  existing_event public.outcome_events;
  rule_row public.outcome_strategy_rules;
  v_close numeric;
  v_outcome_id uuid;
  v_entry_price numeric;
  v_existing_tp_pct numeric;
  v_existing_sl_pct numeric;
  v_existing_cutoff_n integer;
begin
  if p_strategy is null or p_strategy not in ('A', 'B', 'C', 'D', 'E') then
    raise exception using message = 'INVALID_STRATEGY';
  end if;

  select * into rule_row
    from public.outcome_strategy_rules
    where strategy = p_strategy;
  if not found then
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  select * into logical_row from public.logical_runs where logical_run_key = p_logical_run_key;
  if not found or logical_row.batch_kind <> 'close' then
    raise exception using message = 'OPEN_COMMAND_REQUIRES_CLOSE_BATCH';
  end if;

  select close into v_close
    from public.daily_ohlcv
    where ticker = p_ticker and trading_day = logical_row.trading_day;
  if v_close is null then
    raise exception using message = 'MISSING_DAILY_OHLCV_CLOSE';
  end if;

  select * into existing_open
    from public.candidate_outcome
    where ticker = p_ticker and strategy = p_strategy and status in ('OPEN', 'SUSPENDED', 'DELISTED')
    for update;
  if found and existing_open.status = 'SUSPENDED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_TRACKED_SUSPENDED',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price
    );
  end if;
  if found and existing_open.status = 'DELISTED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_DELISTED',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price
    );
  end if;
  if found and existing_open.entry_date <> logical_row.trading_day then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price
    );
  end if;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values (
      p_ticker, p_strategy, 'OPEN', p_logical_run_key,
      jsonb_build_object(
        'entry_date', logical_row.trading_day,
        'entry_price', v_close,
        'tp_pct', rule_row.tp_pct,
        'sl_pct', rule_row.sl_pct,
        'cutoff_n', rule_row.cutoff_n
      )
    )
    on conflict (logical_run_key, ticker, strategy, command_type) do nothing
    returning * into new_event;

  if found then
    begin
      insert into public.candidate_outcome(
        ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n
      )
      values (
        p_ticker, p_strategy, logical_row.trading_day, v_close, 'OPEN',
        rule_row.tp_pct, rule_row.sl_pct, rule_row.cutoff_n
      )
      returning outcome_id into v_outcome_id;
      return jsonb_build_object(
        'replayed', false, 'skipped', false,
        'event_id', new_event.event_id, 'outcome_id', v_outcome_id,
        'entry_date', logical_row.trading_day, 'entry_price', v_close,
        'tp_pct', rule_row.tp_pct, 'sl_pct', rule_row.sl_pct, 'cutoff_n', rule_row.cutoff_n
      );
    exception when unique_violation then
      select * into existing_open
        from public.candidate_outcome
        where ticker = p_ticker and strategy = p_strategy and status = 'OPEN';
      return jsonb_build_object(
        'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
        'event_id', new_event.event_id, 'outcome_id', existing_open.outcome_id,
        'entry_date', existing_open.entry_date, 'entry_price', existing_open.entry_price
      );
    end;
  end if;

  select * into existing_event
    from public.outcome_events
    where logical_run_key = p_logical_run_key and ticker = p_ticker
      and strategy = p_strategy and command_type = 'OPEN';
  if not found then
    raise exception using message = 'OUTCOME_EVENT_MISSING';
  end if;

  select outcome_id, entry_price, tp_pct, sl_pct, cutoff_n
    into v_outcome_id, v_entry_price, v_existing_tp_pct, v_existing_sl_pct, v_existing_cutoff_n
    from public.candidate_outcome
    where ticker = p_ticker and strategy = p_strategy and entry_date = logical_row.trading_day;
  if not found then
    raise exception using message = 'OUTCOME_PROJECTION_MISSING';
  end if;

  return jsonb_build_object(
    'replayed', true, 'skipped', false,
    'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
    'entry_date', logical_row.trading_day, 'entry_price', v_entry_price,
    'tp_pct', v_existing_tp_pct, 'sl_pct', v_existing_sl_pct, 'cutoff_n', v_existing_cutoff_n
  );
end $$;

comment on function public.emit_open_command(text, text, text) is
  'Story 6.5: close 배치의 전략별 outcome_strategy_rules(tp_pct/sl_pct/cutoff_n)를 OPEN event payload와 candidate_outcome에 원자적으로 스냅샷한다. A/B/C는 3/3/30, D는 3/5/20, E는 2/5/30이며, 멱등성·SUSPENDED·DELISTED 재진입 경계는 Story 3.2~3.9 계약을 유지한다.';

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
  'Story 6.5: 기존 close publish/관찰/SUSPENDED/DELISTED 흐름을 유지하면서 candidate_outcome 행에 저장된 tp_pct/sl_pct/cutoff_n으로 SL(우선), TP, TIMEOUT을 판정한다. TP/SL은 목표가 자체에서 왕복 0.1% 비용을 차감하고, TIMEOUT은 오늘 종가 실손익에서 0.1%를 차감한다. 기존 A/B/C outcome 행은 재판정하지 않고 저장된 스냅샷을 사용한다.';

create or replace function public.rebuild_outcome_projection()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_cur record;
  v_event record;
  v_entry_date date;
  v_entry_price numeric;
  v_tp_pct numeric;
  v_sl_pct numeric;
  v_cutoff_n integer;
  v_open_active boolean := false;
  v_rebuilt integer := 0;
begin
  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  delete from public.candidate_outcome;
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

  for v_cur in
    select distinct oe.ticker, oe.strategy from public.outcome_events oe order by oe.ticker, oe.strategy
  loop
    v_open_active := false;
    for v_event in
      select oe.command_type, oe.payload, oe.created_at, oe.event_id
      from public.outcome_events oe
      where oe.ticker = v_cur.ticker and oe.strategy = v_cur.strategy
      order by oe.created_at, oe.event_id
    loop
      if v_event.command_type = 'OPEN' then
        if v_event.payload->>'entry_date' is null or v_event.payload->>'entry_price' is null then
          raise exception 'REBUILD: OPEN payload missing entry_date/entry_price (ticker=%, strategy=%)', v_cur.ticker, v_cur.strategy;
        end if;
        v_entry_date := (v_event.payload->>'entry_date')::date;
        v_entry_price := (v_event.payload->>'entry_price')::numeric;
        v_tp_pct := nullif(v_event.payload->>'tp_pct', '')::numeric;
        v_sl_pct := nullif(v_event.payload->>'sl_pct', '')::numeric;
        v_cutoff_n := nullif(v_event.payload->>'cutoff_n', '')::integer;
        if v_tp_pct is null or v_sl_pct is null or v_cutoff_n is null then
          if v_cur.strategy in ('A', 'B', 'C') then
            v_tp_pct := 3.0; v_sl_pct := 3.0; v_cutoff_n := 30;
          else
            raise exception 'REBUILD: OPEN payload missing strategy rules (ticker=%, strategy=%)', v_cur.ticker, v_cur.strategy;
          end if;
        end if;
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        insert into public.candidate_outcome(
          ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n
        ) values (
          v_cur.ticker, v_cur.strategy, v_entry_date, v_entry_price, 'OPEN', v_tp_pct, v_sl_pct, v_cutoff_n
        ) on conflict (ticker, strategy, entry_date) do update set
          entry_price = excluded.entry_price, status = 'OPEN', exit_date = null,
          exit_price = null, return_pct = null, tp_pct = excluded.tp_pct,
          sl_pct = excluded.sl_pct, cutoff_n = excluded.cutoff_n, holding_days = 0;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
        v_open_active := true;
        v_rebuilt := v_rebuilt + 1;
      elsif v_open_active and v_event.command_type in ('TP', 'SL', 'TIMEOUT') then
        if v_event.payload->>'exit_price' is null or v_event.payload->>'return_pct' is null then
          raise exception 'REBUILD: % payload missing exit_price/return_pct (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end if;
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        update public.candidate_outcome set status = v_event.command_type,
          exit_date = (v_event.payload->>'trading_day')::date,
          exit_price = (v_event.payload->>'exit_price')::numeric,
          return_pct = (v_event.payload->>'return_pct')::numeric,
          holding_days = coalesce(nullif(v_event.payload->>'holding_days','')::integer, holding_days)
        where ticker = v_cur.ticker and strategy = v_cur.strategy and entry_date = v_entry_date;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
      elsif v_open_active and v_event.command_type = 'SUSPENDED' then
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        update public.candidate_outcome set status = 'SUSPENDED'
        where ticker = v_cur.ticker and strategy = v_cur.strategy and entry_date = v_entry_date;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
      elsif v_open_active and v_event.command_type = 'CORRECTION' then
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        update public.candidate_outcome set
          status = coalesce(v_event.payload->>'new_status', status),
          entry_price = case when v_event.payload ? 'new_entry_price'
            then (v_event.payload->>'new_entry_price')::numeric else entry_price end,
          exit_date = case when v_event.payload->>'new_status' = 'OPEN' then null
            when v_event.payload ? 'new_exit_date' then (v_event.payload->>'new_exit_date')::date else exit_date end,
          exit_price = case when v_event.payload->>'new_status' = 'OPEN' then null
            when v_event.payload ? 'new_exit_price' then (v_event.payload->>'new_exit_price')::numeric else exit_price end,
          return_pct = case when v_event.payload->>'new_status' = 'OPEN' then null
            when v_event.payload ? 'new_return_pct' then (v_event.payload->>'new_return_pct')::numeric else return_pct end,
          holding_days = case when v_event.payload ? 'new_holding_days'
            then (v_event.payload->>'new_holding_days')::integer else holding_days end,
          cutoff_n = case when v_event.payload ? 'new_cutoff_n'
            then (v_event.payload->>'new_cutoff_n')::integer else cutoff_n end
        where ticker = v_cur.ticker and strategy = v_cur.strategy and entry_date = v_entry_date;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
      end if;
    end loop;
  end loop;
  return jsonb_build_object('rebuilt', true, 'rows', v_rebuilt);
end $$;

comment on function public.rebuild_outcome_projection() is
  'Story 6.5: outcome_events를 판정 재실행 없이 순서대로 투영한다. OPEN payload의 tp_pct/sl_pct/cutoff_n을 보존하고, payload가 없는 구형 OPEN은 A/B/C에만 legacy 3/3/30을 적용한다. D/E의 구형 OPEN은 재구축을 실패시켜 파라미터 손실을 숨기지 않는다. 장부는 변경하지 않는다.';

revoke execute on function public.emit_open_command(text, text, text) from public, anon, authenticated;
grant execute on function public.emit_open_command(text, text, text) to service_role;
revoke execute on function public.publish_attempt(uuid, bigint, uuid) from public, anon, authenticated;
grant execute on function public.publish_attempt(uuid, bigint, uuid) to service_role;
revoke execute on function public.rebuild_outcome_projection() from public, anon, authenticated;
grant execute on function public.rebuild_outcome_projection() to service_role;

commit;
