-- Story 3.2 review patch (AD-14 forward-only): 202609031500의 emit_open_command를
-- create or replace로 갱신한다. 원본 파일은 손대지 않는다 — 이미 운영에 적용된 migration은
-- 불변이며, 수정은 항상 새 forward migration으로 표현한다.
-- 고친 것:
--   1) p_strategy가 NULL이면 `not in (...)`이 NULL로 평가되어 INVALID_STRATEGY 가드를
--      우회하고 이후 불친절한 NOT NULL 제약 위반으로 이어졌다 -- `is null or` 추가.
--   2) 최초 OPEN 삽입은 대상 행이 없을 때 잠금을 걸지 않으므로, 서로 다른 거래일의 두
--      close 배치가 같은 (ticker,strategy)에 동시에 최초 진입을 시도하면 partial unique
--      index 위반이 처리되지 않은 예외로 전파될 수 있었다 -- candidate_outcome insert를
--      예외 블록으로 감싸 unique_violation을 잡아 동시 승자의 OPEN 행으로 ALREADY_OPEN
--      응답을 반환한다(이미 삽입된 outcome_events 행은 제출 사실의 정확한 기록으로 유지).
--   3) 사전 조회 ALREADY_OPEN 응답에만 `replayed` 키가 빠져 세 응답 스키마가
--      일관되지 않았다 -- `replayed: false`를 추가.
--   4) 동일 key 재호출(replay) 분기의 두 재조회가 not found를 확인하지 않아 원장 드리프트
--      시 event_id/entry_price가 null인 응답을 조용히 반환할 수 있었다 -- 각각
--      OUTCOME_EVENT_MISSING/OUTCOME_PROJECTION_MISSING 가드를 추가.
begin;

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
  if p_strategy is null or p_strategy not in ('A', 'B', 'C') then
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
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
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
    begin
      insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
        values (p_ticker, p_strategy, logical_row.trading_day, v_close, 'OPEN')
        returning outcome_id into v_outcome_id;
      return jsonb_build_object(
        'replayed', false, 'skipped', false,
        'event_id', new_event.event_id, 'outcome_id', v_outcome_id,
        'entry_date', logical_row.trading_day, 'entry_price', v_close
      );
    exception when unique_violation then
      -- 동시에 다른 거래일(logical_run_key)에서 같은 (ticker,strategy)에 대해 먼저
      -- OPEN을 잡은 호출이 있었던 경우: 이 이벤트는 그대로 두고(제출 사실의 정확한
      -- 기록), projection 삽입만 동시 승자의 OPEN 행을 그대로 반영해 ALREADY_OPEN으로
      -- 응답한다.
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

  -- 동일 key 재호출: 새 이벤트를 만들지 않고 기존 event_id/outcome_id를 반환한다.
  select * into existing_event
    from public.outcome_events
    where logical_run_key = p_logical_run_key and ticker = p_ticker
      and strategy = p_strategy and command_type = 'OPEN';
  if not found then
    raise exception using message = 'OUTCOME_EVENT_MISSING';
  end if;

  select outcome_id, entry_price into v_outcome_id, v_entry_price
    from public.candidate_outcome
    where ticker = p_ticker and strategy = p_strategy and entry_date = logical_row.trading_day;
  if not found then
    raise exception using message = 'OUTCOME_PROJECTION_MISSING';
  end if;

  return jsonb_build_object(
    'replayed', true, 'skipped', false,
    'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
    'entry_date', logical_row.trading_day, 'entry_price', v_entry_price
  );
end $$;

comment on function public.emit_open_command(text, text, text) is
  'Story 3.2: close 배치 canonical 후보의 (logical_run_key,ticker,strategy)로 OPEN 이벤트와 candidate_outcome 행을 원자적으로 발행한다. command 멱등 키 (logical_run_key,ticker,strategy,command_type) 재호출은 replay:true로 기존 결과를 반환하고, 이미 다른 거래일에 OPEN 중이면 skipped:true(ALREADY_OPEN)로 재진입을 막는다. batch_kind<>''close''는 OPEN_COMMAND_REQUIRES_CLOSE_BATCH로, 종가 부재는 MISSING_DAILY_OHLCV_CLOSE로 거부한다. Story 3.3 이전까지는 어디서도 호출되지 않는다(apps/batch/, publish_attempt 미변경).';

commit;
