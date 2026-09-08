-- Story 7.4 (AD-14 forward-only): 전략 F의 outcome 판정 파라미터(TP 3%/SL 4%/무제한 보유)를
-- outcome_strategy_rules에 추가하고, emit_open_command/outcome_events/candidate_outcome의
-- strategy CHECK 및 guard_outcome_strategy_snapshot의 cutoff 비교 목록을 F까지 확장한다.
-- 202609051600_parameterize_outcome_strategy_rules.sql·202609052000_harden_outcome_strategy_snapshot_contract.sql·
-- 202609052100_preserve_legacy_outcome_snapshot_compatibility.sql(D/E 선례)·
-- 202609071000_expand_candidate_tags_strategy_check_f.sql(F 확장 선례)과 동일한
-- 사전조건 검증 -> drop/add constraint -> comment 갱신 패턴을 그대로 따른다.
-- cutoff_n은 NOT NULL(> 0) 제약을 유지하며 "무제한"은 sentinel 999999로 표현한다(스키마 변경 금지).
-- publish_attempt/rebuild_outcome_projection은 이미 전략-비의존적이라 변경하지 않는다.
begin;

-- 1) outcome_strategy_rules.strategy CHECK을 A-E -> A-F로 확장한다.
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'outcome_strategy_rules'
      and c.conname = 'outcome_strategy_rules_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''A''%'
      and pg_get_constraintdef(c.oid) like '%''B''%'
      and pg_get_constraintdef(c.oid) like '%''C''%'
      and pg_get_constraintdef(c.oid) like '%''D''%'
      and pg_get_constraintdef(c.oid) like '%''E''%'
      and pg_get_constraintdef(c.oid) not like '%''F''%'
  ) then
    raise exception 'outcome_strategy_rules_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.outcome_strategy_rules
  drop constraint outcome_strategy_rules_strategy_check;

alter table public.outcome_strategy_rules
  add constraint outcome_strategy_rules_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F'));

-- 2) F의 청산 파라미터 행을 추가한다(TP 3% / SL 4% / cutoff_n sentinel 999999 = 무제한).
-- on conflict do nothing은 재실행 시 조용히 넘어가므로, 이미 다른 값의 F 행이 존재하면
-- 의도한 3.0/4.0/999999 계약과 어긋난 값이 조용히 유지되지 않도록 사전에 명시적으로 막는다.
do $$
begin
  if exists (
    select 1 from public.outcome_strategy_rules
    where strategy = 'F' and (tp_pct, sl_pct, cutoff_n) <> (3.0, 4.0, 999999)
  ) then
    raise exception 'outcome_strategy_rules F row precondition failed: conflicting value already present';
  end if;
end $$;

insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
values ('F', 3.0, 4.0, 999999)
on conflict (strategy) do nothing;

-- 3) outcome_events/candidate_outcome의 strategy CHECK을 A-E -> A-F로 확장한다.
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'outcome_events'
      and c.conname = 'outcome_events_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''A''%'
      and pg_get_constraintdef(c.oid) like '%''E''%'
      and pg_get_constraintdef(c.oid) not like '%''F''%'
  ) then
    raise exception 'outcome_events_strategy_check old constraint precondition failed';
  end if;
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'candidate_outcome'
      and c.conname = 'candidate_outcome_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''A''%'
      and pg_get_constraintdef(c.oid) like '%''E''%'
      and pg_get_constraintdef(c.oid) not like '%''F''%'
  ) then
    raise exception 'candidate_outcome_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.outcome_events
  drop constraint outcome_events_strategy_check,
  add constraint outcome_events_strategy_check check (strategy in ('A', 'B', 'C', 'D', 'E', 'F'));

alter table public.candidate_outcome
  drop constraint candidate_outcome_strategy_check,
  add constraint candidate_outcome_strategy_check check (strategy in ('A', 'B', 'C', 'D', 'E', 'F'));

-- 4) emit_open_command: 202609052000_harden_outcome_strategy_snapshot_contract.sql:75-266의
-- 최신 본문을 그대로 복사하고 허용 전략 목록 한 줄만 F까지 확장한다.
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
  if p_strategy is null or p_strategy not in ('A', 'B', 'C', 'D', 'E', 'F') then
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

-- 5) guard_outcome_strategy_snapshot: 202609052100_preserve_legacy_outcome_snapshot_compatibility.sql:6-47의
-- 최신 본문을 그대로 복사하고 두 곳만 F까지 확장한다: 미정 전략 통과 목록, cutoff_n 비교 대상 전략 목록.
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

  -- 미정 전략은 candidate_outcome_strategy_check가 표준 CHECK 오류를 내도록 한다.
  if not found then
    if new.strategy not in ('A', 'B', 'C', 'D', 'E', 'F') then
      return new;
    end if;
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  if new.tp_pct is distinct from rule_row.tp_pct
     or new.sl_pct is distinct from rule_row.sl_pct
     or (new.strategy in ('D', 'E', 'F') and new.cutoff_n is distinct from rule_row.cutoff_n) then
    raise exception using message = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH';
  end if;
  return new;
end;
$$;

-- 6) revoke/grant execute는 기존과 동일 유지(service_role 전용).
revoke execute on function public.emit_open_command(text, text, text) from public, anon, authenticated;
grant execute on function public.emit_open_command(text, text, text) to service_role;
revoke execute on function public.guard_outcome_strategy_snapshot() from public, anon, authenticated;

-- 7) 이 migration의 변경 범위(F 추가)를 기록한다.
comment on table public.outcome_strategy_rules is
  'Story 7.4: 전략별(A-F) TP%/SL%/최대보유일 lookup. A/B/C는 3/3/30, D는 3/5/20, E는 2/5/30, F는 3/4/999999(sentinel=무제한, publish_attempt의 v_traded_days >= cutoff_n 비교 재사용).';

comment on function public.emit_open_command(text, text, text) is
  'Story 7.4: A-F 전략의 outcome_strategy_rules(tp_pct/sl_pct/cutoff_n)를 OPEN event payload와 candidate_outcome에 원자적으로 스냅샷한다. F는 TP 3%/SL 4%/cutoff_n sentinel 999999(무제한 보유)이며, 그 외 idempotency·SUSPENDED·DELISTED 경계는 Story 6.5 계약을 그대로 유지한다.';

comment on function public.guard_outcome_strategy_snapshot() is
  'Story 7.4: direct candidate_outcome INSERT/UPDATE snapshot 값은 outcome_strategy_rules와 일치해야 한다(F 포함). F도 D/E와 동일하게 cutoff_n까지 스냅샷 비교 대상이다. correction/rebuild만 내부 override로 우회한다.';

commit;
