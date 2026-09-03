-- Story 3.4: close 배치의 일자별 판정 관찰 수집.
-- publish_attempt(3-arg)를 202609031600 baseline 위에 create or replace한다(같은 시그니처이므로
-- 기존 revoke/grant는 그대로 유효). close 분기의 emit_open_command 루프 뒤에, terminal이 아닌
-- (status not in ('TP','SL','TIMEOUT')) 모든 candidate_outcome 행을 순회하며 신규 idempotent RPC
-- record_outcome_observation(outcome_id, ticker, evaluation_trading_day)을 호출해 daily_ohlcv의
-- 해당 거래일 고가/저가/종가를 outcome_observations에 기록한다. daily_ohlcv 결측은 emit_open_command의
-- MISSING_DAILY_OHLCV_CLOSE와 의도적으로 다르게, 그 티커만 건너뛰고 publish_attempt 전체를
-- rollback시키지 않는다(오래된 다른 종목의 결측이 오늘자 candidate/tag 발행을 막지 않도록 하기 위함 --
-- Story 3.5/3.9의 SUSPENDED/DELISTED 감지가 아직 없는 현재 상태에서의 의도적 blast-radius 축소).
begin;

create or replace function public.record_outcome_observation(
  p_outcome_id uuid,
  p_ticker text,
  p_evaluation_trading_day date
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_high numeric;
  v_low numeric;
  v_close numeric;
  new_row public.outcome_observations;
  existing_row public.outcome_observations;
begin
  select high, low, close into v_high, v_low, v_close
    from public.daily_ohlcv
    where ticker = p_ticker and trading_day = p_evaluation_trading_day;

  if not found then
    return jsonb_build_object(
      'recorded', false, 'reason', 'MISSING_DAILY_OHLCV',
      'outcome_id', p_outcome_id, 'evaluation_trading_day', p_evaluation_trading_day
    );
  end if;

  if not (v_high >= v_low and v_close between v_low and v_high) then
    return jsonb_build_object(
      'recorded', false, 'reason', 'INVALID_DAILY_OHLCV',
      'outcome_id', p_outcome_id, 'evaluation_trading_day', p_evaluation_trading_day
    );
  end if;

  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (p_outcome_id, p_evaluation_trading_day, v_high, v_low, v_close, 'OK')
    on conflict (outcome_id, evaluation_trading_day) do nothing
    returning * into new_row;

  if found then
    return jsonb_build_object(
      'recorded', true, 'replayed', false,
      'outcome_id', p_outcome_id, 'evaluation_trading_day', p_evaluation_trading_day,
      'high', new_row.high, 'low', new_row.low, 'close', new_row.close, 'result_code', new_row.result_code
    );
  end if;

  select * into existing_row
    from public.outcome_observations
    where outcome_id = p_outcome_id and evaluation_trading_day = p_evaluation_trading_day;

  return jsonb_build_object(
    'recorded', true, 'replayed', true,
    'outcome_id', p_outcome_id, 'evaluation_trading_day', p_evaluation_trading_day,
    'high', existing_row.high, 'low', existing_row.low, 'close', existing_row.close, 'result_code', existing_row.result_code
  );
end $$;

comment on function public.record_outcome_observation(uuid, text, date) is
  'Story 3.4: daily_ohlcv의 (ticker,trading_day) 고가/저가/종가를 outcome_observations에 idempotent하게 기록한다. 멱등 key (outcome_id,evaluation_trading_day) 재호출은 replayed:true로 기존 값을 반환한다. daily_ohlcv 결측은 예외를 던지지 않고 recorded:false, reason:MISSING_DAILY_OHLCV를 반환한다(emit_open_command의 MISSING_DAILY_OHLCV_CLOSE와 의도적으로 다른 처리 -- 호출부인 publish_attempt는 이 결과로 rollback하지 않는다). daily_ohlcv 행이 존재하더라도 high/low/close 순서가 outcome_observations_high_low_close_order 제약(high >= low and close between low and high)을 위반하면 insert 시도 없이 동일하게 예외를 던지지 않고 recorded:false, reason:INVALID_DAILY_OHLCV를 반환한다(오래된 종목의 잘못된 시세 데이터가 오늘자 publish_attempt 전체를 rollback시키지 않도록 하기 위함). result_code는 이 스토리에서 항상 OK만 쓴다(TP/SL/TIMEOUT 판정은 Story 3.6/3.7 범위).';

revoke execute on function public.record_outcome_observation(uuid, text, date) from public, anon, authenticated;
grant execute on function public.record_outcome_observation(uuid, text, date) to service_role;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint, p_lease_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  r public.runs;
  logical_row public.logical_runs;
  tag_row record;
  track_row record;
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

    update runs set stage_status = jsonb_set(stage_status, array['outcome_tracking'], to_jsonb('success'::text))
      where run_id = p_run_id;
  end if;

  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id, canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end, published_at = now() where logical_run_key = r.logical_run_key;
  return jsonb_build_object('run_id', p_run_id, 'status', 'published', 'canonical_success_run_id', case when logical_row.batch_kind = 'close' then p_run_id else null end);
end $$;

commit;
