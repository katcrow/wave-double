-- Supabase SQL fixture for Story 2.6.
-- 실행 전 202609022000_create_supply_3day.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

do $$
declare
  key text := 'close:2099-05-01'; started jsonb; run_id uuid; fence bigint; lease uuid;
  v_candidate_id uuid := gen_random_uuid();
  other_run_id uuid;
  second_run_id uuid; second_fence bigint; second_lease uuid; second_candidate_id uuid := gen_random_uuid();
  caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-05-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', v_candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  -- 정상 confirmed 삽입: 4컬럼 전부 NOT NULL + investor_net_status='confirmed'.
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (
    v_candidate_id, run_id, date '2099-04-29', 'D-2', 70000, 1000000, 1.23,
    1000, 2000, -3000, 500, 'confirmed'
  );
  if (select count(*) from public.supply_3day where attempt_run_id = run_id) <> 1 then
    raise exception 'expected confirmed row to be inserted';
  end if;

  -- 정상 pending 삽입: 4컬럼 전부 NULL + investor_net_status='pending'(장중 미확정).
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
  ) values (
    v_candidate_id, run_id, date '2099-04-30', 'D-1', 71000, 1100000, 1.43, 'pending'
  );
  if (select count(*) from public.supply_3day where attempt_run_id = run_id) <> 2 then
    raise exception 'expected pending row to be inserted';
  end if;

  -- 정상 missing 삽입: 4컬럼 전부 NULL + investor_net_status='missing'(미수집).
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
  ) values (
    v_candidate_id, run_id, date '2099-05-01', 'D0', 72000, 1200000, 1.41, 'missing'
  );
  if (select count(*) from public.supply_3day where attempt_run_id = run_id) <> 3 then
    raise exception 'expected missing row to be inserted';
  end if;

  -- confirmed인데 일부 NULL: CHECK 위반으로 거부.
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, institution_net, individual_net, program_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-02', 'D0', 73000, 1300000, 1.39,
      1000, 2000, -3000, null, 'confirmed'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'confirmed with a NULL investor column was accepted'; end if;

  -- pending인데 일부 실값: CHECK 위반으로 거부.
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-02', 'D0', 73000, 1300000, 1.39, 0, 'pending'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'pending with a non-NULL investor column was accepted'; end if;

  -- missing인데 일부 실값(0 포함): CHECK 위반으로 거부.
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      individual_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-02', 'D0', 73000, 1300000, 1.39, 0, 'missing'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'missing with a non-NULL investor column was accepted'; end if;

  -- 잘못된 slot: CHECK 위반으로 거부.
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D-3', 73000, 1300000, 1.39, 'pending'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'invalid slot value was accepted'; end if;

  -- 잘못된 investor_net_status: CHECK 위반으로 거부.
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 1300000, 1.39, 'confirmed_ish'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'invalid investor_net_status value was accepted'; end if;

  -- 유한값 위반: close/volume/change_pct의 NaN은 각각 거부된다.
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 'NaN'::numeric, 1300000, 1.39, 'pending'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'NaN close must be rejected by finite-value check'; end if;

  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 'Infinity'::numeric, 1.39, 'pending'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'Infinity volume must be rejected by finite-value check'; end if;

  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 1300000, '-Infinity'::numeric, 'pending'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception '-Infinity change_pct must be rejected by finite-value check'; end if;

  -- 유한값 위반: 투자자별 순매수 4컬럼도 NaN/Infinity를 거부한다(confirmed 상태로 삽입해
  -- consistency CHECK가 아니라 finite-value CHECK가 트리거되도록 한다; NULL이 아니라 NaN이므로
  -- confirmed↔4컬럼 일관성 규칙 자체는 만족한 채 finite-value 규칙만 위반한다).
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, institution_net, individual_net, program_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 1300000, 1.39,
      'NaN'::numeric, 2000, -3000, 500, 'confirmed'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'NaN foreign_net must be rejected by finite-value check'; end if;

  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, institution_net, individual_net, program_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 1300000, 1.39,
      1000, 'Infinity'::numeric, -3000, 500, 'confirmed'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'Infinity institution_net must be rejected by finite-value check'; end if;

  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, institution_net, individual_net, program_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 1300000, 1.39,
      1000, 2000, '-Infinity'::numeric, 500, 'confirmed'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception '-Infinity individual_net must be rejected by finite-value check'; end if;

  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, institution_net, individual_net, program_net, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-05-03', 'D0', 73000, 1300000, 1.39,
      1000, 2000, -3000, 'NaN'::numeric, 'confirmed'
    );
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'NaN program_net must be rejected by finite-value check'; end if;

  -- FK(candidate_id, attempt_run_id) -> candidates 위반: 존재하지 않는 attempt_run_id 조합.
  started := public.start_attempt('close:2099-05-04', date '2099-05-04', 'close', 'manual', 300);
  other_run_id := (started->>'run_id')::uuid;
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, other_run_id, date '2099-05-04', 'D0', 73000, 1300000, 1.39, 'pending'
    );
  exception when foreign_key_violation then caught := true;
  end;
  if not caught then raise exception 'supply_3day FK(candidate_id, attempt_run_id) was not enforced'; end if;

  -- UNIQUE(candidate_id, trading_day, attempt_run_id) 위반: 동일 조합 재삽입 거부(slot 무관).
  caught := false;
  begin
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
    ) values (
      v_candidate_id, run_id, date '2099-04-29', 'D-1', 70500, 1000000, 1.0, 'pending'
    );
  exception when unique_violation then caught := true;
  end;
  if not caught then raise exception 'duplicate (candidate_id, trading_day, attempt_run_id) was accepted'; end if;

  -- 누적(append-only) 검증(data-model.md): "당일(D0) 행은 배치마다 덮어쓰지 않고
  -- attempt_run_id별로 누적한다" -- 새 attempt(배치)의 D0 수집이 이전 attempt가 이미 적재한
  -- 같은 종목·같은 거래일의 행을 덮어쓰지 않고 별개 행으로 공존해야 한다.
  --
  -- 주의: candidates.candidate_id는 전역 PK(Story 1.5, 이 스토리 범위 밖)이므로 같은
  -- candidate_id가 서로 다른 attempt_run_id에 속할 수 없다(각 attempt는 항상 새 candidate_id를
  -- 발급받는다 -- write_candidates로 같은 candidate_id를 다른 run_id에 재사용하면 candidates_pkey
  -- 위반으로 예외가 난다, 실측 확인함). 따라서 실제 운영에서 "같은 종목의 D0 이력이 attempt마다
  -- 누적"되는 관찰 단위는 candidate_id가 아니라 ticker다: attempt마다 새 candidate_id가 발급되고,
  -- 그 candidate_id로 적재된 supply_3day 행이 이전 attempt의 행을 덮어쓰지 않고 공존해야 한다.
  -- 아래는 동일 ticker에 대해 서로 다른 attempt(서로 다른 candidate_id)가 각각 D0 행을 남기고,
  -- 두 행이 candidates.ticker 기준으로 공존함을 검증한다.
  started := public.start_attempt('close:2099-05-05', date '2099-05-05', 'close', 'manual', 300);
  second_run_id := (started->>'run_id')::uuid; second_fence := (started->>'fence_token')::bigint; second_lease := (started->>'lease_token')::uuid;
  perform public.write_stage(second_run_id, 'candidates', second_fence, second_lease, 'pending', 'running');
  perform public.write_candidates(second_run_id, second_fence, second_lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', second_candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(second_run_id, 'candidates', second_fence, second_lease, 'running', 'success');

  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (
    second_candidate_id, second_run_id, date '2099-04-29', 'D-2', 70200, 1000500, 1.25,
    1100, 2100, -3100, 550, 'confirmed'
  );
  if (
    select count(*) from public.supply_3day s
    join public.candidates c on c.candidate_id = s.candidate_id and c.attempt_run_id = s.attempt_run_id
    where c.ticker = '005930' and s.trading_day = date '2099-04-29' and s.slot = 'D-2'
  ) <> 2 then
    raise exception 'expected two accumulated rows (different attempt_run_id) for the same ticker/trading_day/slot';
  end if;
  if (
    select count(distinct s.attempt_run_id) from public.supply_3day s
    join public.candidates c on c.candidate_id = s.candidate_id and c.attempt_run_id = s.attempt_run_id
    where c.ticker = '005930' and s.trading_day = date '2099-04-29' and s.slot = 'D-2'
  ) <> 2 then
    raise exception 'expected the two accumulated rows to have distinct attempt_run_id values';
  end if;
  if (select count(*) from public.supply_3day s where s.candidate_id = v_candidate_id and s.attempt_run_id = run_id and s.trading_day = date '2099-04-29' and s.slot = 'D-2') <> 1 then
    raise exception 'expected the original attempt row to remain untouched (not overwritten)';
  end if;

  -- PK 없음(UNIQUE 제약만 존재)을 확인한다.
  if exists (
    select 1 from information_schema.table_constraints
    where table_schema = 'public' and table_name = 'supply_3day' and constraint_type = 'PRIMARY KEY'
  ) then raise exception 'supply_3day must not have a PRIMARY KEY (UNIQUE only)'; end if;

  -- RLS는 활성화되어 있으나 정책이 없다(deny-all, candidates/daily_ohlcv/candidate_tags와 동일).
  if not (
    select c.relrowsecurity from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relname = 'supply_3day'
  ) then raise exception 'supply_3day RLS must be enabled'; end if;

  if exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'supply_3day'
  ) then raise exception 'supply_3day must have zero RLS policies (deny-all for anon/authenticated)'; end if;
end $$;

rollback;
