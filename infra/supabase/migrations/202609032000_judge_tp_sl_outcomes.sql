-- Story 3.6: TP/SL 판정 & 비용 반영 손익률.
-- publish_attempt(3-arg)를 202609031800 baseline 위에 create or replace한다(같은 시그니처이므로
-- 기존 revoke/grant는 그대로 유효). close 분기의 SUSPENDED 감지 루프(Story 3.5) 바로 뒤에,
-- status='OPEN' and entry_date < logical_row.trading_day인 candidate_outcome을 다시 순회하며
-- 오늘자 outcome_observations(Story 3.4가 이미 기록)의 고가/저가로 SL을 TP보다 먼저 확인해
-- outcome_events에 command_type='TP'/'SL' 행을 idempotent하게(기존 open_command_key_idx 재사용)
-- append하고 candidate_outcome을 terminal로 전이한다. exit_price는 임계값 자체(entry*0.97/1.03)로
-- 고정하고 return_pct는 왕복 0.1% 비용 차감 고정값(-3.1/2.9)으로 기록한다(backtest/engine.py의
-- gross - cost_rate*200 산식과 정확히 일치). TIMEOUT 확정(Story 3.7)과 SUSPENDED에서의 복귀
-- (Story 3.8)는 이 스토리 범위 밖이다.
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
  v_obs_found boolean;
  v_tpsl_status text;
  v_exit_price numeric;
  v_return_pct numeric;
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

    for track_row in
      select outcome_id, ticker from public.candidate_outcome
      where status not in ('TP', 'SL', 'TIMEOUT')
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
          update public.candidate_outcome set status = 'SUSPENDED'
            where outcome_id = susp_row.outcome_id;

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

    -- Story 3.6: SUSPENDED 감지 이후 재조회한 status='OPEN' 행만 대상으로 TP/SL을 판정한다.
    -- 방금 SUSPENDED로 전이된 행은 이 쿼리에서 자연히 제외된다("3.5 미수행/이미 SUSPENDED면 보류" 가드).
    for tpsl_row in
      select outcome_id, ticker, strategy, entry_price from public.candidate_outcome
      where status = 'OPEN' and entry_date < logical_row.trading_day
      for update
    loop
      v_obs_high := null;
      v_obs_low := null;
      v_tpsl_status := null;
      v_exit_price := null;
      v_return_pct := null;

      select high, low into v_obs_high, v_obs_low
        from public.outcome_observations
        where outcome_id = tpsl_row.outcome_id and evaluation_trading_day = logical_row.trading_day;
      v_obs_found := found;

      if not v_obs_found then
        -- 오늘자 outcome_observations가 없으면(daily_ohlcv 결측/무효로 3.4가 기록하지 않음) 판정을 건너뛴다.
        continue;
      end if;

      if v_obs_low <= tpsl_row.entry_price * 0.97 then
        -- SL을 TP보다 먼저 확인한다 -- 같은 날 둘 다 충족하면 SL이 확정된다.
        v_tpsl_status := 'SL';
        v_exit_price := tpsl_row.entry_price * 0.97;
        v_return_pct := -3.1;
      elsif v_obs_high >= tpsl_row.entry_price * 1.03 then
        v_tpsl_status := 'TP';
        v_exit_price := tpsl_row.entry_price * 1.03;
        v_return_pct := 2.9;
      end if;

      if v_tpsl_status is not null then
        insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
          values (
            tpsl_row.ticker, tpsl_row.strategy, v_tpsl_status, r.logical_run_key,
            jsonb_build_object(
              'trading_day', logical_row.trading_day,
              'exit_price', v_exit_price,
              'return_pct', v_return_pct
            )
          )
          on conflict (logical_run_key, ticker, strategy, command_type) do nothing
          returning * into v_new_event;

        if found then
          update public.candidate_outcome set
              status = v_tpsl_status,
              exit_date = logical_row.trading_day,
              exit_price = v_exit_price,
              return_pct = v_return_pct
            where outcome_id = tpsl_row.outcome_id;

          tp_sl_transitions := tp_sl_transitions || jsonb_build_array(jsonb_build_object(
            'outcome_id', tpsl_row.outcome_id,
            'ticker', tpsl_row.ticker,
            'strategy', tpsl_row.strategy,
            'status', v_tpsl_status,
            'exit_price', v_exit_price,
            'return_pct', v_return_pct
          ));
        end if;
        -- on conflict do nothing으로 삽입되지 않았다면(재시도) 이미 TP/SL 이벤트가 있는 것이므로
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
  'Story 1.x~3.6: close/premarket/intraday attempt 발행. close는 canonical 후보를 잠근 뒤 emit_open_command(3.2)로 OPEN을, record_outcome_observation(3.4)으로 일자별 관찰을 발행하고, status=''OPEN''인 candidate_outcome을 다시 훑어 가격 조정 이상 감지(3.5, SUSPENDED 전이) 후, 그 결과 재조회한 status=''OPEN'' and entry_date < trading_day인 candidate_outcome만 대상으로 오늘자 outcome_observations의 고가/저가로 SL(entry*0.97 이하, TP보다 우선)/TP(entry*1.03 이상)를 판정해 outcome_events에 idempotent하게 append하고 candidate_outcome을 terminal로 전이한다(3.6). exit_price는 임계값 자체로 고정하고 return_pct는 왕복 0.1% 비용 차감 고정값(-3.1/2.9)으로 기록한다. 반환 jsonb의 suspended_transitions/tp_sl_transitions 배열은 이번 attempt에서 신규로 전이된 outcome만 담는다(재시도로 이미 존재하는 이벤트는 포함하지 않음). TIMEOUT 판정(3.7)과 SUSPENDED에서의 복귀(3.8)는 이 함수의 범위 밖이다.';

commit;
