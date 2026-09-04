-- Story 3.9 (AD-14 forward-only): 상장폐지(DELISTED)를 불변 terminal 상태로 마감한다.
-- 3.8의 apply_outcome_correction이 이미 DELISTED 전이를 허용하므로, 여기서는 두 함수 본문만
-- create or replace로 고쳐 "종결되면 정말 끝난다"는 경계를 실제 동작에 반영한다.
--   1) publish_attempt의 close 관찰 수집 루프 대상에서 DELISTED를 제외한다 -- 종결 outcome의
--      일자별 관찰 적재를 중단한다(추적 중단).
--   2) emit_open_command의 재진입 가드를 status in ('OPEN','SUSPENDED','DELISTED')로 넓히고,
--      DELISTED 매치는 항상 skip(reason ALREADY_DELISTED)으로 신규 OPEN을 만들지 않는다.
-- 원본 migration 파일(202609032200, 202609032201, 202609031501)은 손대지 않는다. 함수
-- 시그니처는 불변이므로 read-model 타입에는 diff가 없다.
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
  select * into r from runs where run_id = p_run_id; if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  perform pg_advisory_xact_lock(hashtextextended(r.logical_run_key, 0));
  select * into r from runs where run_id = p_run_id for update; select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
  if logical_row.active_attempt_run_id is distinct from p_run_id or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  if r.status <> 'ready_to_publish' or r.stage_status->>'candidates' <> 'success' then raise exception using message = 'PUBLISH_GUARD_FAILED'; end if;
  if r.stage_status->>'tags' is distinct from 'success' then raise exception using message = 'TAGS_STAGE_NOT_COMPLETE'; end if;
  if exists (select 1 from candidates c where c.attempt_run_id = p_run_id and not exists (select 1 from candidate_source_contrib s where s.candidate_id = c.candidate_id and s.attempt_run_id = c.attempt_run_id)) or exists (select 1 from (select candidate_id, attempt_run_id, sum(contribution_weight) as total from candidate_source_contrib where attempt_run_id = p_run_id group by candidate_id, attempt_run_id) s where s.total <> 1) then raise exception using message = 'PUBLISH_PROVENANCE_GUARD_FAILED'; end if;
  if logical_row.canonical_success_run_id is not null then raise exception using message = 'CANONICAL_ALREADY_PUBLISHED'; end if;

  if logical_row.batch_kind = 'close' then
    for tag_row in
      select c.ticker as ticker, t.strategy as strategy
        from candidate_tags t
        join candidates c on c.candidate_id = t.candidate_id and c.attempt_run_id = t.attempt_run_id
        where t.attempt_run_id = p_run_id and t.status = 'active'
    loop
      perform public.emit_open_command(r.logical_run_key, tag_row.ticker, tag_row.strategy);
    end loop;

    -- Story 3.9: DELISTED는 terminal 상태라 관찰 수집 대상에서 제외한다(추적 중단).
    -- OPEN/SUSPENDED만 관찰을 쌓는 기존 동작(3.4/3.5)은 그대로 유지한다.
    for track_row in
      select outcome_id, ticker from public.candidate_outcome
      where status not in ('TP', 'SL', 'TIMEOUT', 'DELISTED')
      for update
    loop
      perform public.record_outcome_observation(track_row.outcome_id, track_row.ticker, logical_row.trading_day);
    end loop;

    -- Story 3.5: OPEN인 candidate_outcome 전체를 다시 훑어 가격 조정 이상을 감지하고 SUSPENDED로 전이한다.
    for susp_row in
      select outcome_id, ticker, strategy from public.candidate_outcome
      where status = 'OPEN'
      for update
    loop
      v_today_close := null;
      v_pricechk := null;
      v_prev_close := null;
      v_gap_pct := null;
      v_should_suspend := false;
      v_via_pricechk := false;

      select close, pricechk into v_today_close, v_pricechk
        from public.daily_ohlcv
        where ticker = susp_row.ticker and trading_day = logical_row.trading_day;

      if not found then
        -- 오늘 daily_ohlcv가 없으면(3.4의 MISSING_DAILY_OHLCV와 동일 상황) 판정 근거가 없어 이번 attempt에서는 건너뛴다.
        continue;
      end if;

      if v_pricechk is not null and v_pricechk <> 0 then
        -- 1차: LS 원천 진실. 갭 크기와 무관하게 무조건 전이한다.
        v_should_suspend := true;
        v_via_pricechk := true;
      else
        select close into v_prev_close
          from public.daily_ohlcv
          where ticker = susp_row.ticker and trading_day < logical_row.trading_day
          order by trading_day desc
          limit 1;

        if found and v_prev_close is not null and v_prev_close <> 0 then
          v_gap_pct := abs((v_today_close - v_prev_close) / v_prev_close);
          if v_gap_pct > public.price_adjustment_gap_threshold() then
            -- 2차 안전망: pricechk가 없을 때만 갭 임계값으로 판정한다.
            v_should_suspend := true;
          end if;
        end if;
        -- 전일 daily_ohlcv 자체가 없으면(신규 진입 첫날 등) 갭 계산을 건너뛰고 전이하지 않는다(오탐 방지).
      end if;

      if v_should_suspend then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
          values (
            susp_row.ticker, susp_row.strategy, 'SUSPENDED', r.logical_run_key,
            jsonb_build_object(
              'trading_day', logical_row.trading_day,
              'via_pricechk', v_via_pricechk,
              'pricechk', v_pricechk,
              'gap_pct', v_gap_pct
            )
          )
          on conflict (logical_run_key, ticker, strategy, command_type) do nothing
          returning * into v_new_event;

        if found then
          perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
          update public.candidate_outcome set status = 'SUSPENDED'
            where outcome_id = susp_row.outcome_id;
          perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

          suspended_transitions := suspended_transitions || jsonb_build_array(jsonb_build_object(
            'outcome_id', susp_row.outcome_id,
            'ticker', susp_row.ticker,
            'strategy', susp_row.strategy,
            'via_pricechk', v_via_pricechk,
            'gap_pct', v_gap_pct
          ));
        end if;
        -- on conflict do nothing으로 삽입되지 않았다면(재시도) 이미 SUSPENDED 이벤트가 있는 것이므로
        -- 재확인만 하고 새 이벤트/전이/반환 항목을 만들지 않는다.
      end if;
    end loop;

    -- Story 3.6/3.7: SUSPENDED 감지 이후 재조회한 status='OPEN' 행만 대상으로 TP/SL/TIMEOUT을 판정한다.
    -- 방금 SUSPENDED로 전이된 행은 이 쿼리에서 자연히 제외된다("3.5 미수행/이미 SUSPENDED면 보류" 가드).
    for tpsl_row in
      select outcome_id, ticker, strategy, entry_price, entry_date, cutoff_n from public.candidate_outcome
      where status = 'OPEN' and entry_date < logical_row.trading_day
      for update
    loop
      v_obs_high := null;
      v_obs_low := null;
      v_obs_close := null;
      v_traded_days := null;
      v_tpsl_status := null;
      v_exit_price := null;
      v_return_pct := null;

      select high, low, close into v_obs_high, v_obs_low, v_obs_close
        from public.outcome_observations
        where outcome_id = tpsl_row.outcome_id and evaluation_trading_day = logical_row.trading_day;
      v_obs_found := found;

      if not v_obs_found then
        -- 오늘자 outcome_observations가 없으면(daily_ohlcv 결측/무효로 3.4가 기록하지 않음) 판정을 건너뛴다.
        continue;
      end if;

      -- Story 3.7: traded_days_since_entry = 이 outcome의 entry_date 이후, 오늘까지의 'OK'로
      -- 기록된 관찰 행 수. 휴장일과 거래정지 기간(유효 daily_ohlcv 없음)은 애초에 행이 없어 자동
      -- 제외된다(3.4 동작 재사용). 오늘자 관찰은 위에서 이미 기록되어 있으므로 이 count에 포함된다.
      -- 상한(<= logical_row.trading_day)은 수동 재처리 등으로 미래 거래일 관측이 먼저 존재하는
      -- 경우에도 컷오프가 앞당겨지지 않도록 하는 방어(review patch).
      select count(*) into v_traded_days
        from public.outcome_observations
        where outcome_id = tpsl_row.outcome_id
          and evaluation_trading_day > tpsl_row.entry_date
          and evaluation_trading_day <= logical_row.trading_day
          and result_code = 'OK';

      if v_obs_low <= tpsl_row.entry_price * 0.97 then
        -- SL을 TP보다 먼저 확인한다 -- 같은 날 둘 다 충족하면 SL이 확정된다.
        v_tpsl_status := 'SL';
        v_exit_price := tpsl_row.entry_price * 0.97;
        v_return_pct := -3.1;
      elsif v_obs_high >= tpsl_row.entry_price * 1.03 then
        v_tpsl_status := 'TP';
        v_exit_price := tpsl_row.entry_price * 1.03;
        v_return_pct := 2.9;
      elsif v_traded_days >= tpsl_row.cutoff_n then
        -- Story 3.7: cutoff_n(이 행에 저장된 값, 전역 재조회 없음)에 도달하면 오늘 종가 기준
        -- 실손익(왕복 0.1% 비용 차감)으로 TIMEOUT을 확정한다.
        v_tpsl_status := 'TIMEOUT';
        v_exit_price := v_obs_close;
        v_return_pct := (v_obs_close / tpsl_row.entry_price - 1.0) * 100.0 - 0.1;
      end if;

      if v_tpsl_status is not null then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
          values (
            tpsl_row.ticker, tpsl_row.strategy, v_tpsl_status, r.logical_run_key,
            jsonb_build_object(
              'trading_day', logical_row.trading_day,
              'exit_price', v_exit_price,
              'return_pct', v_return_pct,
              'holding_days', v_traded_days
            )
          )
          on conflict (logical_run_key, ticker, strategy, command_type) do nothing
          returning * into v_new_event;

        if found then
          perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
          update public.candidate_outcome set
              status = v_tpsl_status,
              exit_date = logical_row.trading_day,
              exit_price = v_exit_price,
              return_pct = v_return_pct,
              holding_days = v_traded_days
            where outcome_id = tpsl_row.outcome_id;
          perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

          tp_sl_transitions := tp_sl_transitions || jsonb_build_array(jsonb_build_object(
            'outcome_id', tpsl_row.outcome_id,
            'ticker', tpsl_row.ticker,
            'strategy', tpsl_row.strategy,
            'status', v_tpsl_status,
            'exit_price', v_exit_price,
            'return_pct', v_return_pct,
            'holding_days', v_traded_days
          ));
        end if;
        -- on conflict do nothing으로 삽입되지 않았다면(재시도) 이미 TP/SL/TIMEOUT 이벤트가 있는 것이므로
        -- 재확인만 하고 새 이벤트/전이/반환 항목을 만들지 않는다.
      end if;
    end loop;

    update runs set stage_status = jsonb_set(stage_status, array['outcome_tracking'], to_jsonb('success'::text))
      where run_id = p_run_id;
  end if;

  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id, canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end, published_at = now() where logical_run_key = r.logical_run_key;
  return jsonb_build_object(
    'run_id', p_run_id, 'status', 'published',
    'canonical_success_run_id', case when logical_row.batch_kind = 'close' then p_run_id else null end,
    'suspended_transitions', suspended_transitions,
    'tp_sl_transitions', tp_sl_transitions
  );
end $$;

comment on function public.publish_attempt(uuid, bigint, uuid) is
  'Story 1.x~3.8: close/premarket/intraday attempt 발행. close는 canonical 후보를 잠근 뒤 emit_open_command(3.2, 3.8부터 SUSPENDED 재진입도 skip, 3.9부터 DELISTED 재진입도 skip)로 OPEN을, record_outcome_observation(3.4)으로 일자별 관찰을 발행하고, status=''OPEN''인 candidate_outcome을 다시 훑어 가격 조정 이상 감지(3.5, SUSPENDED 전이) 후, 그 결과 재조회한 status=''OPEN'' and entry_date < trading_day인 candidate_outcome만 대상으로 오늘자 outcome_observations의 고가/저가로 SL(entry*0.97 이하, TP보다 우선)/TP(entry*1.03 이상)를 판정하거나(3.6), 둘 다 미충족이고 entry_date 이후 오늘까지 result_code=''OK''인 관찰 행 수(traded_days_since_entry)가 그 행의 cutoff_n(기본 30, 저장된 값 그대로 사용) 이상이면 오늘 종가 기준 비용반영 실손익으로 TIMEOUT을 확정한다(3.7). 세 경우 모두 outcome_events에 idempotent하게 append하고, candidate_outcome UPDATE는 wave_double.outcome_mutation_allowed 세션 플래그를 트랜잭션 스코프로 켰다 끄는 방식으로 guard_candidate_outcome_mutation 트리거(3.8)를 통과시켜 terminal로 전이하며 holding_days를 그 시점 traded_days_since_entry로 함께 기록한다. exit_price/return_pct는 TP/SL은 임계값 자체와 왕복 0.1% 비용 차감 고정값(-3.1/2.9), TIMEOUT은 실측 종가와 (close/entry_price-1)*100-0.1이다. 반환 jsonb의 suspended_transitions/tp_sl_transitions 배열은 이번 attempt에서 신규로 전이된 outcome만 담는다(재시도로 이미 존재하는 이벤트는 포함하지 않음). SUSPENDED에서의 수치/상태 정정(3.8)과 DELISTED 종결(3.9)은 별도 RPC public.apply_outcome_correction이 담당하며 이 함수의 범위 밖이다. Story 3.9: 관찰 수집 루프는 status not in (''TP'',''SL'',''TIMEOUT'',''DELISTED'')로 DELISTED를 제외해 종결 outcome의 관찰 적재를 중단한다.';

-- (2) emit_open_command: 재진입 가드를 status in ('OPEN','SUSPENDED','DELISTED')로 넓힌다.
-- SUSPENDED 매치는 항상 skip(reason ALREADY_TRACKED_SUSPENDED), DELISTED 매치는 항상
-- skip(reason ALREADY_DELISTED)한다. 기존 ALREADY_OPEN reason 문자열과 그 시나리오의
-- 동작(OPEN이면서 entry_date가 다른 경우만 skip)은 그대로 둔다.
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

  -- 재진입 금지: 이미 (ticker,strategy) OPEN, SUSPENDED 또는 DELISTED가 있으면 사전 조회 no-op이다.
  -- SUSPENDED는 진입일과 무관하게 항상 skip한다(3.8: SUSPENDED 재태깅 시 중복 projection 방지).
  -- DELISTED는 진입일과 무관하게 항상 skip한다(3.9: 상장폐지된 종목은 재추적하지 않는 불변 종결).
  -- OPEN은 진입일이 이번 거래일과 다를 때만 skip한다(기존 3.2 동작 보존).
  select * into existing_open
    from public.candidate_outcome
    where ticker = p_ticker and strategy = p_strategy and status in ('OPEN', 'SUSPENDED', 'DELISTED')
    for update;
  if found and existing_open.status = 'SUSPENDED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_TRACKED_SUSPENDED',
      'outcome_id', existing_open.outcome_id,
      'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price
    );
  end if;
  if found and existing_open.status = 'DELISTED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_DELISTED',
      'outcome_id', existing_open.outcome_id,
      'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price
    );
  end if;
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
  'Story 3.2: close 배치 canonical 후보의 (logical_run_key,ticker,strategy)로 OPEN 이벤트와 candidate_outcome 행을 원자적으로 발행한다. command 멱등 키 (logical_run_key,ticker,strategy,command_type) 재호출은 replay:true로 기존 결과를 반환하고, 이미 다른 거래일에 OPEN 중이면 skipped:true(ALREADY_OPEN)로 재진입을 막는다. Story 3.8: 같은 (ticker,strategy)가 SUSPENDED 상태면 진입일과 무관하게 항상 skipped:true(ALREADY_TRACKED_SUSPENDED)로 재진입을 막아 SUSPENDED 재태깅 시 candidate_outcome 중복 행 생성을 방지한다. Story 3.9: 같은 (ticker,strategy)가 DELISTED 상태면 진입일과 무관하게 항상 skipped:true(ALREADY_DELISTED)로 재진입을 막아 상장폐지된 종목의 재추적을 금지한다. batch_kind<>''close''는 OPEN_COMMAND_REQUIRES_CLOSE_BATCH로, 종가 부재는 MISSING_DAILY_OHLCV_CLOSE로 거부한다. Story 3.3 이전까지는 어디서도 호출되지 않는다(apps/batch/, publish_attempt 미변경).';

commit;
