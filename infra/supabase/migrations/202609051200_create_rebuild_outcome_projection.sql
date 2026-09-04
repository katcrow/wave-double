-- Story 3.10 (AD-14 forward-only): append-only 장부(outcome_events)를 이벤트 재생으로
-- 소비해 candidate_outcome projection을 완전히 재구축하는 함수를 신설한다.
-- 재생은 판정 로직을 재계산하지 않는다 — TP/SL/TIMEOUT/SUSPENDED/CORRECTION 이벤트의
-- payload를 순서대로 투영만 하며(3.6/3.7이 이미 이벤트로 확정한 사실을 재현), 재생 불일치
-- 시 배포를 차단하는 CI 회귀 게이트의 핵심이다.
--
-- AD-19/NFR-4: outcome_events, outcome_observations, candidate_outcome은 모두 장기 보존
-- 대상(NFR-4 정리 대상 아님)이며, 이 함수는 장부를 변경하지 않는다(rebuild는 read-only replay).
--
-- Wavelet guard: candidate_outcome의 guard_candidate_outcome_mutation 트리거를 통과하기 위해
-- wave_double.outcome_mutation_allowed 세션 플래그를 사용한다.
--
-- 재생 모델(Spec Always/Design Notes): 각 (ticker,strategy)에 대해 이벤트를 created_at,
-- event_id 오름차순으로 순서 재생한다. OPEN 이벤트가 새 projection 행(진입일/진입가)을 만들고,
-- TP/SL/TIMEOUT/SUSPENDED/CORRECTION은 같은 (ticker,strategy)의 현재 projection 행에 payload
-- 를 순서대로 투영한다. CORRECTION 이벤트 행은 ticker/strategy 컬럼으로 해당 OPEN
-- (payload.entry_date)에 연결되며(Spec Always), 같은 (ticker,strategy)의 새 OPEN이 나타나면
-- 새 행으로 전환된다(과거 이력을 덮지 않음).
-- outcome_id/version은 장부가 생성하지 않는 서버 관리 정체성이므로 재생 결과로 새로 발급된다.
begin;

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
  v_open_active boolean := false;
  v_rebuilt integer := 0;
begin
  -- 기존 projection을 비운다(재생으로 온전히 재구축). DELETE는
  -- guard_candidate_outcome_mutation(BEFORE UPDATE)를 트리거하지 않지만, 이후 INSERT/UPDATE가
  -- 트리거를 통과하도록 플래그를 사용한다.
  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  delete from public.candidate_outcome;
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

  -- 각 (ticker,strategy)에 대해 장부를 순서 재생한다.
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
        -- 새 OPEN은 새 projection 행을 시작한다(과거 이력을 새로운 행으로).
        if v_event.payload->>'entry_date' is null then
          raise exception 'REBUILD: OPEN payload missing entry_date (ticker=%, strategy=%)', v_cur.ticker, v_cur.strategy;
        end if;
        if v_event.payload->>'entry_price' is null then
          raise exception 'REBUILD: OPEN payload missing entry_price (ticker=%, strategy=%)', v_cur.ticker, v_cur.strategy;
        end if;
        v_entry_date := (v_event.payload->>'entry_date')::date;
        v_entry_price := (v_event.payload->>'entry_price')::numeric;
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
        values (v_cur.ticker, v_cur.strategy, v_entry_date, v_entry_price, 'OPEN')
        on conflict (ticker, strategy, entry_date) do update
          set entry_price = excluded.entry_price, status = 'OPEN',
              exit_date = null, exit_price = null, return_pct = null,
              cutoff_n = 30, holding_days = 0;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
        v_open_active := true;
        v_rebuilt := v_rebuilt + 1;
      elsif v_open_active and v_event.command_type in ('TP', 'SL', 'TIMEOUT') then
        -- terminal 종결: exit 3필드 + holding_days를 payload 그대로 투영한다(재판정 없음).
        if v_event.payload->>'exit_price' is null or v_event.payload->>'return_pct' is null then
          raise exception 'REBUILD: % payload missing exit_price/return_pct (ticker=%, strategy=%)',
            v_event.command_type, v_cur.ticker, v_cur.strategy;
        end if;
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        update public.candidate_outcome set
          status = v_event.command_type,
          exit_date = (v_event.payload->>'trading_day')::date,
          exit_price = (v_event.payload->>'exit_price')::numeric,
          return_pct = (v_event.payload->>'return_pct')::numeric,
          holding_days = coalesce(nullif(v_event.payload->>'holding_days','')::integer, holding_days)
        where ticker = v_cur.ticker and strategy = v_cur.strategy
          and entry_date = v_entry_date;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
      elsif v_open_active and v_event.command_type = 'SUSPENDED' then
        -- SUSPENDED는 예외 상태 전이일 뿐이고, publish_attempt(3.5)가 status만 갱신하고
        -- exit 필드는 건드리지 않는 동작을 그대로 재현한다(exit 3필드는 보존/변경 없음).
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        update public.candidate_outcome set status = 'SUSPENDED'
        where ticker = v_cur.ticker and strategy = v_cur.strategy
          and entry_date = v_entry_date;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
      elsif v_open_active and v_event.command_type = 'CORRECTION' then
        -- CORRECTION의 new_* 필드를 순서대로 적용한다. new_status='OPEN'이면 exit 3필드를
        -- null로 되돌리고(SUSPENDED 복귀), entry_date/entry_price는 보존한다.
        perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
        update public.candidate_outcome set
          status = coalesce(v_event.payload->>'new_status', status),
          entry_price = case
            when v_event.payload ? 'new_entry_price'
            then (v_event.payload->>'new_entry_price')::numeric
            else entry_price end,
          exit_date = case
            when v_event.payload->>'new_status' = 'OPEN' then null
            when v_event.payload ? 'new_exit_date'
            then (v_event.payload->>'new_exit_date')::date
            else exit_date end,
          exit_price = case
            when v_event.payload->>'new_status' = 'OPEN' then null
            when v_event.payload ? 'new_exit_price'
            then (v_event.payload->>'new_exit_price')::numeric
            else exit_price end,
          return_pct = case
            when v_event.payload->>'new_status' = 'OPEN' then null
            when v_event.payload ? 'new_return_pct'
            then (v_event.payload->>'new_return_pct')::numeric
            else return_pct end,
          holding_days = case
            when v_event.payload ? 'new_holding_days'
            then (v_event.payload->>'new_holding_days')::integer
            else holding_days end,
          cutoff_n = case
            when v_event.payload ? 'new_cutoff_n'
            then (v_event.payload->>'new_cutoff_n')::integer
            else cutoff_n end
        where ticker = v_cur.ticker and strategy = v_cur.strategy
          and entry_date = v_entry_date;
        perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
      end if;
    end loop;
  end loop;

  return jsonb_build_object('rebuilt', true, 'rows', v_rebuilt);
end $$;

comment on function public.rebuild_outcome_projection() is
  'Story 3.10: outcome_events 장부를 이벤트 재생으로 소비해 candidate_outcome projection을 온전히 재구축한다(AD-9 재생 가능성). 재판정은 하지 않는다 — TP/SL/TIMEOUT/SUSPENDED는 payload를 그대로 투영하고, CORRECTION은 new_* 필드를 적용한다. OPEN은 새 행을 시작하고, 같은 (ticker,strategy)의 새 OPEN은 새 행으로 전환해 과거 이력을 덮지 않는다. outcome_id/version은 서버 관리 정체성이라 재생 결과로 새로 발급된다(자연 키 (ticker,strategy,entry_date)가 복구 식별 기준). projection 재쓰기는 wave_double.outcome_mutation_allowed 가드를 사용해 guard_candidate_outcome_mutation 트리거를 통과시킨다. 장부(outcome_events/outcome_observations)는 절대 변경하지 않는다(AD-19/NFR-4 장기 보존).';

revoke execute on function public.rebuild_outcome_projection() from public, anon, authenticated;
grant execute on function public.rebuild_outcome_projection() to service_role;

commit;
