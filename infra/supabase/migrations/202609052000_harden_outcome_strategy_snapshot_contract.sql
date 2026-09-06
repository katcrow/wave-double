-- Story 6.5 review patch (AD-14 forward-only): snapshot 경계와 rebuild 오류 계약을 최종 보강한다.
-- 202609051700~202609051900의 기존 review migration은 수정하지 않는다.
begin;

-- 기존 두 단계 check와도 멱등적으로 공존하도록 기존 이름을 제거하고 최종 범위를 하나로 고정한다.
alter table public.outcome_strategy_rules
  drop constraint if exists outcome_strategy_rules_sl_pct_check,
  drop constraint if exists outcome_strategy_rules_sl_pct_less_than_100_check,
  add constraint outcome_strategy_rules_sl_pct_range_check check (
    sl_pct > 0 and sl_pct < 100
    and sl_pct <> 'NaN'::numeric
    and sl_pct <> 'Infinity'::numeric
    and sl_pct <> '-Infinity'::numeric
  );

alter table public.candidate_outcome
  drop constraint if exists candidate_outcome_sl_pct_check,
  drop constraint if exists candidate_outcome_sl_pct_less_than_100_check,
  add constraint candidate_outcome_sl_pct_range_check check (
    sl_pct > 0 and sl_pct < 100
    and sl_pct <> 'NaN'::numeric
    and sl_pct <> 'Infinity'::numeric
    and sl_pct <> '-Infinity'::numeric
  );

-- 직접 INSERT/UPDATE의 snapshot은 항상 현재 rule table과 일치해야 한다.
-- correction/rebuild는 별도 transaction-local override를 사용한다. 기존 상태만
-- 전이하는 UPDATE는 snapshot을 건드리지 않으므로 rule row 누락에도 보존된다.
create or replace function public.guard_outcome_strategy_snapshot()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  rule_row public.outcome_strategy_rules;
begin
  if coalesce(current_setting('wave_double.outcome_rule_override_allowed', true), 'off') = 'on' then
    return new;
  end if;

  if tg_op = 'UPDATE'
     and new.strategy is not distinct from old.strategy
     and new.tp_pct is not distinct from old.tp_pct
     and new.sl_pct is not distinct from old.sl_pct
     and new.cutoff_n is not distinct from old.cutoff_n then
    return new;
  end if;

  select * into rule_row
  from public.outcome_strategy_rules
  where strategy = new.strategy
  for share;

  if not found then
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  if new.tp_pct is distinct from rule_row.tp_pct
     or new.sl_pct is distinct from rule_row.sl_pct
     or new.cutoff_n is distinct from rule_row.cutoff_n then
    raise exception using message = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH';
  end if;
  return new;
end;
$$;

drop trigger if exists candidate_outcome_strategy_snapshot_guard on public.candidate_outcome;
create trigger candidate_outcome_strategy_snapshot_guard
before insert or update of strategy, tp_pct, sl_pct, cutoff_n on public.candidate_outcome
for each row execute function public.guard_outcome_strategy_snapshot();

-- 신규 OPEN만 rule lookup이 필수다. 기존 same-key replay와 OPEN/SUSPENDED/DELISTED
-- 재진입은 저장된 snapshot을 먼저 반환한다.
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

  select * into logical_row
  from public.logical_runs
  where logical_run_key = p_logical_run_key;
  if not found or logical_row.batch_kind <> 'close' then
    raise exception using message = 'OPEN_COMMAND_REQUIRES_CLOSE_BATCH';
  end if;

  select close into v_close
  from public.daily_ohlcv
  where ticker = p_ticker and trading_day = logical_row.trading_day;
  if v_close is null then
    raise exception using message = 'MISSING_DAILY_OHLCV_CLOSE';
  end if;

  select * into existing_event
  from public.outcome_events
  where logical_run_key = p_logical_run_key
    and ticker = p_ticker
    and strategy = p_strategy
    and command_type = 'OPEN';

  if found then
    select outcome_id, entry_price, tp_pct, sl_pct, cutoff_n
      into v_outcome_id, v_entry_price, v_existing_tp_pct, v_existing_sl_pct, v_existing_cutoff_n
    from public.candidate_outcome
    where ticker = p_ticker
      and strategy = p_strategy
      and entry_date = logical_row.trading_day;
    if not found then
      raise exception using message = 'OUTCOME_PROJECTION_MISSING';
    end if;

    return jsonb_build_object(
      'replayed', true, 'skipped', false,
      'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
      'entry_date', logical_row.trading_day, 'entry_price', v_entry_price,
      'tp_pct', v_existing_tp_pct, 'sl_pct', v_existing_sl_pct,
      'cutoff_n', v_existing_cutoff_n
    );
  end if;

  select * into existing_open
  from public.candidate_outcome
  where ticker = p_ticker
    and strategy = p_strategy
    and status in ('OPEN', 'SUSPENDED', 'DELISTED')
  for update;

  if found and existing_open.status = 'SUSPENDED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_TRACKED_SUSPENDED',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price, 'tp_pct', existing_open.tp_pct,
      'sl_pct', existing_open.sl_pct, 'cutoff_n', existing_open.cutoff_n
    );
  end if;
  if found and existing_open.status = 'DELISTED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_DELISTED',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price, 'tp_pct', existing_open.tp_pct,
      'sl_pct', existing_open.sl_pct, 'cutoff_n', existing_open.cutoff_n
    );
  end if;
  if found and existing_open.entry_date <> logical_row.trading_day then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price, 'tp_pct', existing_open.tp_pct,
      'sl_pct', existing_open.sl_pct, 'cutoff_n', existing_open.cutoff_n
    );
  end if;

  select * into rule_row
  from public.outcome_strategy_rules
  where strategy = p_strategy
  for share;
  if not found then
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values (
    p_ticker, p_strategy, 'OPEN', p_logical_run_key,
    jsonb_build_object(
      'entry_date', logical_row.trading_day, 'entry_price', v_close,
      'tp_pct', rule_row.tp_pct, 'sl_pct', rule_row.sl_pct,
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
        'tp_pct', rule_row.tp_pct, 'sl_pct', rule_row.sl_pct,
        'cutoff_n', rule_row.cutoff_n
      );
    exception when unique_violation then
      select * into existing_open
      from public.candidate_outcome
      where ticker = p_ticker and strategy = p_strategy and status = 'OPEN'
      for update;

      if found then
        return jsonb_build_object(
          'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
          'event_id', new_event.event_id, 'outcome_id', existing_open.outcome_id,
          'entry_date', existing_open.entry_date, 'entry_price', existing_open.entry_price,
          'tp_pct', existing_open.tp_pct, 'sl_pct', existing_open.sl_pct,
          'cutoff_n', existing_open.cutoff_n
        );
      end if;

      if exists (
        select 1 from public.candidate_outcome
        where ticker = p_ticker and strategy = p_strategy
          and entry_date = logical_row.trading_day
      ) then
        raise exception using message = 'OUTCOME_PROJECTION_CONFLICT';
      end if;
      raise;
    end;
  end if;

  select * into existing_event
  from public.outcome_events
  where logical_run_key = p_logical_run_key
    and ticker = p_ticker
    and strategy = p_strategy
    and command_type = 'OPEN';
  if not found then
    raise exception using message = 'OUTCOME_EVENT_MISSING';
  end if;

  select outcome_id, entry_price, tp_pct, sl_pct, cutoff_n
    into v_outcome_id, v_entry_price, v_existing_tp_pct, v_existing_sl_pct, v_existing_cutoff_n
  from public.candidate_outcome
  where ticker = p_ticker and strategy = p_strategy
    and entry_date = logical_row.trading_day;
  if not found then
    raise exception using message = 'OUTCOME_PROJECTION_MISSING';
  end if;

  return jsonb_build_object(
    'replayed', true, 'skipped', false,
    'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
    'entry_date', logical_row.trading_day, 'entry_price', v_entry_price,
    'tp_pct', v_existing_tp_pct, 'sl_pct', v_existing_sl_pct,
    'cutoff_n', v_existing_cutoff_n
  );
end;
$$;

-- rebuild는 판정하지 않고 payload를 투영한다. payload의 구조/형식 오류는
-- 원본 cast/check 오류가 아니라 REBUILD 오류로 fail closed한다.
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
  v_has_tp boolean;
  v_has_sl boolean;
  v_has_cutoff boolean;
  v_raw text;
  v_exit_date date;
  v_exit_price numeric;
  v_return_pct numeric;
  v_holding_days integer;
begin
  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  perform set_config('wave_double.outcome_rule_override_allowed', 'on', true);
  delete from public.candidate_outcome;

  for v_cur in
    select distinct oe.ticker, oe.strategy
    from public.outcome_events oe
    order by oe.ticker, oe.strategy
  loop
    v_open_active := false;

    for v_event in
      select oe.command_type, oe.payload, oe.created_at, oe.event_id
      from public.outcome_events oe
      where oe.ticker = v_cur.ticker and oe.strategy = v_cur.strategy
      order by oe.created_at, oe.event_id
    loop
      if v_event.command_type = 'OPEN' then
        if v_event.payload->>'entry_date' is null
           or btrim(v_event.payload->>'entry_date') = ''
           or v_event.payload->>'entry_price' is null
           or btrim(v_event.payload->>'entry_price') = '' then
          raise exception 'REBUILD: OPEN payload missing entry_date/entry_price (ticker=%, strategy=%)',
            v_cur.ticker, v_cur.strategy;
        end if;

        begin
          v_entry_date := (v_event.payload->>'entry_date')::date;
        exception when others then
          raise exception 'REBUILD: OPEN payload invalid entry_date (ticker=%, strategy=%)',
            v_cur.ticker, v_cur.strategy;
        end;
        begin
          v_entry_price := (v_event.payload->>'entry_price')::numeric;
        exception when others then
          raise exception 'REBUILD: OPEN payload invalid entry_price (ticker=%, strategy=%)',
            v_cur.ticker, v_cur.strategy;
        end;
        if v_entry_price <= 0
           or v_entry_price in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
          raise exception 'REBUILD: OPEN payload invalid entry_price (ticker=%, strategy=%)',
            v_cur.ticker, v_cur.strategy;
        end if;

        v_has_tp := v_event.payload ? 'tp_pct';
        v_has_sl := v_event.payload ? 'sl_pct';
        v_has_cutoff := v_event.payload ? 'cutoff_n';

        if not v_has_tp and not v_has_sl and not v_has_cutoff then
          if v_cur.strategy in ('A', 'B', 'C') then
            v_tp_pct := 3.0; v_sl_pct := 3.0; v_cutoff_n := 30;
          else
            raise exception 'REBUILD: OPEN payload missing strategy rules (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
        elsif not (v_has_tp and v_has_sl and v_has_cutoff) then
          raise exception 'REBUILD: OPEN payload partial strategy rule snapshot (ticker=%, strategy=%)',
            v_cur.ticker, v_cur.strategy;
        else
          v_raw := v_event.payload->>'tp_pct';
          if v_raw is null or btrim(v_raw) = '' then
            raise exception 'REBUILD: OPEN payload invalid tp_pct (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          begin v_tp_pct := v_raw::numeric;
          exception when others then
            raise exception 'REBUILD: OPEN payload invalid tp_pct (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end;
          if v_tp_pct <= 0 or v_tp_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
            raise exception 'REBUILD: OPEN payload invalid tp_pct (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;

          v_raw := v_event.payload->>'sl_pct';
          if v_raw is null or btrim(v_raw) = '' then
            raise exception 'REBUILD: OPEN payload invalid sl_pct (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          begin v_sl_pct := v_raw::numeric;
          exception when others then
            raise exception 'REBUILD: OPEN payload invalid sl_pct (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end;
          if v_sl_pct <= 0 or v_sl_pct >= 100
             or v_sl_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
            raise exception 'REBUILD: OPEN payload invalid sl_pct (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;

          v_raw := v_event.payload->>'cutoff_n';
          if v_raw is null or btrim(v_raw) = '' then
            raise exception 'REBUILD: OPEN payload invalid cutoff_n (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          begin v_cutoff_n := v_raw::integer;
          exception when others then
            raise exception 'REBUILD: OPEN payload invalid cutoff_n (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end;
          if v_cutoff_n <= 0 then
            raise exception 'REBUILD: OPEN payload invalid cutoff_n (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
        end if;

        insert into public.candidate_outcome(
          ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n
        )
        values (
          v_cur.ticker, v_cur.strategy, v_entry_date, v_entry_price, 'OPEN',
          v_tp_pct, v_sl_pct, v_cutoff_n
        )
        on conflict (ticker, strategy, entry_date) do update set
          entry_price = excluded.entry_price,
          status = 'OPEN',
          exit_date = null,
          exit_price = null,
          return_pct = null,
          tp_pct = excluded.tp_pct,
          sl_pct = excluded.sl_pct,
          cutoff_n = excluded.cutoff_n,
          holding_days = 0;
        v_open_active := true;
        v_rebuilt := v_rebuilt + 1;

      elsif v_open_active and v_event.command_type in ('TP', 'SL', 'TIMEOUT') then
        if v_event.payload->>'trading_day' is null
           or btrim(v_event.payload->>'trading_day') = '' then
          raise exception 'REBUILD: % payload missing trading_day (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end if;
        begin v_exit_date := (v_event.payload->>'trading_day')::date;
        exception when others then
          raise exception 'REBUILD: % payload invalid trading_day (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end;

        if v_event.payload->>'exit_price' is null
           or btrim(v_event.payload->>'exit_price') = ''
           or v_event.payload->>'return_pct' is null
           or btrim(v_event.payload->>'return_pct') = '' then
          raise exception 'REBUILD: % payload missing exit_price/return_pct (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end if;
        begin v_exit_price := (v_event.payload->>'exit_price')::numeric;
        exception when others then
          raise exception 'REBUILD: % payload invalid exit_price (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end;
        if v_exit_price <= 0
           or v_exit_price in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
          raise exception 'REBUILD: % payload invalid exit_price (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end if;
        begin v_return_pct := (v_event.payload->>'return_pct')::numeric;
        exception when others then
          raise exception 'REBUILD: % payload invalid return_pct (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end;
        if v_return_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
          raise exception 'REBUILD: % payload invalid return_pct (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end if;

        if v_event.payload ? 'holding_days' then
          begin v_holding_days := (v_event.payload->>'holding_days')::integer;
          exception when others then
            raise exception 'REBUILD: % payload invalid holding_days (ticker=%, strategy=%)',
              v_event.command_type, v_cur.ticker, v_cur.strategy;
          end;
          if v_holding_days < 0 then
            raise exception 'REBUILD: % payload invalid holding_days (ticker=%, strategy=%)',
              v_event.command_type, v_cur.ticker, v_cur.strategy;
          end if;
        else
          v_holding_days := null;
        end if;

        update public.candidate_outcome set
          status = v_event.command_type,
          exit_date = v_exit_date,
          exit_price = v_exit_price,
          return_pct = v_return_pct,
          holding_days = coalesce(v_holding_days, holding_days)
        where ticker = v_cur.ticker and strategy = v_cur.strategy
          and entry_date = v_entry_date;

      elsif v_open_active and v_event.command_type = 'SUSPENDED' then
        update public.candidate_outcome set status = 'SUSPENDED'
        where ticker = v_cur.ticker and strategy = v_cur.strategy
          and entry_date = v_entry_date;

      elsif v_open_active and v_event.command_type = 'CORRECTION' then
        -- correction payload는 기존 RPC가 생성한 값만 소비하며, 숫자/날짜 cast 오류도
        -- rebuild 전용 오류로 감싼다. OPEN 복귀 시 exit 3필드는 의도적으로 null이다.
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
        where ticker = v_cur.ticker and strategy = v_cur.strategy
          and entry_date = v_entry_date;
      end if;
    end loop;
  end loop;

  perform set_config('wave_double.outcome_rule_override_allowed', 'off', true);
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
  return jsonb_build_object('rebuilt', true, 'rows', v_rebuilt);
end;
$$;

create or replace function public.apply_outcome_correction(
  p_logical_run_key text,
  p_outcome_id uuid,
  p_expected_version integer,
  p_reason text,
  p_new_status text,
  p_new_entry_price numeric default null,
  p_new_exit_date date default null,
  p_new_exit_price numeric default null,
  p_new_return_pct numeric default null,
  p_new_holding_days integer default null,
  p_new_cutoff_n integer default null
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  target public.candidate_outcome;
  new_event public.outcome_events;
  v_new_entry_price numeric;
  v_new_exit_date date;
  v_new_exit_price numeric;
  v_new_return_pct numeric;
  v_new_holding_days integer;
  v_new_cutoff_n integer;
begin
  if p_new_status is null or p_new_status not in ('TP', 'SL', 'TIMEOUT', 'OPEN', 'SUSPENDED', 'DELISTED') then
    raise exception using message = 'INVALID_STATUS';
  end if;
  if p_reason is null or length(btrim(p_reason)) = 0 then
    raise exception using message = 'REASON_REQUIRED';
  end if;

  select * into target from public.candidate_outcome where outcome_id = p_outcome_id for update;
  if not found then raise exception using message = 'OUTCOME_NOT_FOUND'; end if;
  if p_expected_version is null or target.version <> p_expected_version then
    raise exception using message = 'CORRECTION_VERSION_MISMATCH';
  end if;

  v_new_entry_price := coalesce(p_new_entry_price, target.entry_price);
  v_new_holding_days := coalesce(p_new_holding_days, target.holding_days);
  v_new_cutoff_n := coalesce(p_new_cutoff_n, target.cutoff_n);
  if p_new_status = 'OPEN' then
    v_new_exit_date := null; v_new_exit_price := null; v_new_return_pct := null;
  else
    v_new_exit_date := coalesce(p_new_exit_date, target.exit_date);
    v_new_exit_price := coalesce(p_new_exit_price, target.exit_price);
    v_new_return_pct := coalesce(p_new_return_pct, target.return_pct);
  end if;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values (
    target.ticker, target.strategy, 'CORRECTION', p_logical_run_key,
    jsonb_build_object(
      'reason', p_reason, 'outcome_id', p_outcome_id,
      'previous_version', target.version, 'previous_status', target.status,
      'new_status', p_new_status, 'previous_entry_price', target.entry_price,
      'new_entry_price', v_new_entry_price, 'previous_exit_date', target.exit_date,
      'new_exit_date', v_new_exit_date, 'previous_exit_price', target.exit_price,
      'new_exit_price', v_new_exit_price, 'previous_return_pct', target.return_pct,
      'new_return_pct', v_new_return_pct, 'previous_holding_days', target.holding_days,
      'new_holding_days', v_new_holding_days, 'previous_cutoff_n', target.cutoff_n,
      'new_cutoff_n', v_new_cutoff_n
    )
  )
  returning * into new_event;

  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  perform set_config('wave_double.outcome_rule_override_allowed', 'on', true);
  update public.candidate_outcome set
    status = p_new_status, entry_price = v_new_entry_price,
    exit_date = v_new_exit_date, exit_price = v_new_exit_price,
    return_pct = v_new_return_pct, holding_days = v_new_holding_days,
    cutoff_n = v_new_cutoff_n
  where outcome_id = p_outcome_id
  returning * into target;
  perform set_config('wave_double.outcome_rule_override_allowed', 'off', true);
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

  return jsonb_build_object(
    'event_id', new_event.event_id, 'outcome_id', target.outcome_id,
    'version', target.version, 'status', target.status,
    'entry_price', target.entry_price, 'exit_date', target.exit_date,
    'exit_price', target.exit_price, 'return_pct', target.return_pct,
    'holding_days', target.holding_days, 'cutoff_n', target.cutoff_n
  );
end;
$$;

comment on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) is
  'Story 3.8 review compatibility: correction update also uses the internal outcome rule override so A/B/C legacy cutoff corrections remain valid.';


comment on function public.guard_outcome_strategy_snapshot() is
  'Story 6.5 review patch: direct candidate_outcome INSERT/UPDATE snapshot values must match outcome_strategy_rules; only correction/rebuild internal override can change historical values.';

comment on function public.emit_open_command(text, text, text) is
  'Story 6.5 review patch: existing replay and OPEN/SUSPENDED/DELISTED idempotency paths return stored snapshots before rule lookup; new OPEN requires the authoritative rule row and terminal natural-key conflicts fail closed.';

comment on function public.rebuild_outcome_projection() is
  'Story 6.5 review patch: partial or malformed OPEN/terminal payloads fail with explicit REBUILD errors; only legacy A/B/C OPEN payloads with all three rule keys absent use 3/3/30 fallback.';

revoke execute on function public.guard_outcome_strategy_snapshot() from public, anon, authenticated;
revoke execute on function public.reject_outcome_open_projection_conflict() from public, anon, authenticated;
revoke execute on function public.emit_open_command(text, text, text) from public, anon, authenticated;
grant execute on function public.emit_open_command(text, text, text) to service_role;
revoke execute on function public.rebuild_outcome_projection() from public, anon, authenticated;
grant execute on function public.rebuild_outcome_projection() to service_role;
revoke execute on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) from public, anon, authenticated;
grant execute on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) to service_role;

commit;
