-- Story 3.2: idempotent OPEN command 발행 로직.
-- command 멱등 키는 (logical_run_key, ticker, strategy, command_type)이며 outcome_events
-- 유니크 인덱스로 강제한다. 같은 key로 재호출하면 새 이벤트를 만들지 않고 기존 결과를
-- replay한다(start_attempt 패턴). 이미 다른 거래일에 (ticker,strategy) OPEN이 있으면
-- 이벤트도 projection도 만들지 않는 사전 조회 no-op(ALREADY_OPEN)이다. 이 RPC는
-- Story 3.3에서 close publication transaction 안에 결합될 예정이며 이 스토리에서는
-- 아무 호출부도 추가하지 않는다(apps/batch/, publish_attempt 모두 미변경).
begin;

create unique index outcome_events_open_command_key_idx
  on public.outcome_events(logical_run_key, ticker, strategy, command_type);

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
  v_close numeric;
  v_outcome_id uuid;
  v_entry_price numeric;
begin
  if p_strategy not in ('A', 'B', 'C') then
    raise exception using message = 'INVALID_STRATEGY';
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

  -- 재진입 금지: 이미 (ticker,strategy) OPEN이 있고 그 진입일이 이번 거래일과 다르면
  -- 이벤트도 projection도 만들지 않는 사전 조회 no-op이다.
  select * into existing_open
    from public.candidate_outcome
    where ticker = p_ticker and strategy = p_strategy and status = 'OPEN'
    for update;
  if found and existing_open.entry_date <> logical_row.trading_day then
    return jsonb_build_object(
      'skipped', true, 'reason', 'ALREADY_OPEN',
      'outcome_id', existing_open.outcome_id,
      'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price
    );
  end if;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values (
      p_ticker, p_strategy, 'OPEN', p_logical_run_key,
      jsonb_build_object('entry_date', logical_row.trading_day, 'entry_price', v_close)
    )
    on conflict (logical_run_key, ticker, strategy, command_type) do nothing
    returning * into new_event;

  if found then
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
      values (p_ticker, p_strategy, logical_row.trading_day, v_close, 'OPEN')
      returning outcome_id into v_outcome_id;
    return jsonb_build_object(
      'replayed', false, 'skipped', false,
      'event_id', new_event.event_id, 'outcome_id', v_outcome_id,
      'entry_date', logical_row.trading_day, 'entry_price', v_close
    );
  end if;

  -- 동일 key 재호출: 새 이벤트를 만들지 않고 기존 event_id/outcome_id를 반환한다.
  select * into existing_event
    from public.outcome_events
    where logical_run_key = p_logical_run_key and ticker = p_ticker
      and strategy = p_strategy and command_type = 'OPEN';
  select outcome_id, entry_price into v_outcome_id, v_entry_price
    from public.candidate_outcome
    where ticker = p_ticker and strategy = p_strategy and entry_date = logical_row.trading_day;

  return jsonb_build_object(
    'replayed', true, 'skipped', false,
    'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
    'entry_date', logical_row.trading_day, 'entry_price', v_entry_price
  );
end $$;

comment on function public.emit_open_command(text, text, text) is
  'Story 3.2: close 배치 canonical 후보의 (logical_run_key,ticker,strategy)로 OPEN 이벤트와 candidate_outcome 행을 원자적으로 발행한다. command 멱등 키 (logical_run_key,ticker,strategy,command_type) 재호출은 replay:true로 기존 결과를 반환하고, 이미 다른 거래일에 OPEN 중이면 skipped:true(ALREADY_OPEN)로 재진입을 막는다. batch_kind<>''close''는 OPEN_COMMAND_REQUIRES_CLOSE_BATCH로, 종가 부재는 MISSING_DAILY_OHLCV_CLOSE로 거부한다. Story 3.3 이전까지는 어디서도 호출되지 않는다(apps/batch/, publish_attempt 미변경).';

revoke execute on function public.emit_open_command(text, text, text) from public, anon, authenticated;
grant execute on function public.emit_open_command(text, text, text) to service_role;

commit;
