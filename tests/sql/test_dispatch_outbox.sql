-- Supabase SQL fixture for Story 1.10.
-- 실행 전 lineage/candidates/hardening migration들과 202609021000 dispatch_outbox migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

-- 1) 정상 dispatch: dispatch_request + dispatch_outbox(queued)가 함께 생성된다.
do $$
declare res jsonb; req_id uuid;
begin
  res := public.request_manual_dispatch('idem-1', 'hash-1', 'neo@example.com', 'close:2099-03-01', date '2099-03-01', 'close');
  if res->>'status' <> 'queued' or res->>'reason' <> 'created' then raise exception 'expected fresh queued dispatch, got %', res; end if;
  req_id := (res->>'dispatch_request_id')::uuid;
  if not exists (select 1 from public.dispatch_outbox where dispatch_request_id = req_id and status = 'queued') then
    raise exception 'dispatch_outbox row was not created';
  end if;
end $$;

-- 2) 재요청(같은 key+hash): 기존 dispatch_request_id를 replay하고 새 행을 만들지 않는다.
do $$
declare res jsonb; req_id uuid; before_count integer; after_count integer;
begin
  select count(*) into before_count from public.dispatch_request;
  res := public.request_manual_dispatch('idem-1', 'hash-1', 'neo@example.com', 'close:2099-03-01', date '2099-03-01', 'close');
  select count(*) into after_count from public.dispatch_request;
  if res->>'reason' <> 'replayed' then raise exception 'expected replay, got %', res; end if;
  if before_count <> after_count then raise exception 'replay created a new dispatch_request row'; end if;
end $$;

-- 3) 재요청(같은 key+다른 hash): 거부(예외).
do $$
declare caught boolean := false;
begin
  begin
    perform public.request_manual_dispatch('idem-1', 'hash-DIFFERENT', 'neo@example.com', 'close:2099-03-01', date '2099-03-01', 'close');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'same key with different hash was accepted'; end if;
end $$;

-- 4) trading_day가 logical_run_key에 내포된 날짜와 불일치하면 예외.
do $$
declare caught boolean := false;
begin
  begin
    perform public.request_manual_dispatch('idem-mismatch', 'hash-x', 'neo@example.com', 'close:2099-03-01', date '2099-03-02', 'close');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'trading_day/logical_run_key mismatch was accepted'; end if;
end $$;

-- 4b) trading_day가 NULL이면(<> 비교가 NULL이 되어 조용히 통과되는 것을 막는다) 예외.
do $$
declare caught boolean := false;
begin
  begin
    perform public.request_manual_dispatch('idem-null-day', 'hash-x', 'neo@example.com', 'close:2099-03-01', null, 'close');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'NULL trading_day was accepted'; end if;
end $$;

-- 5) 활성 attempt 존재: 신규 dispatch를 conflict로 거부하고 기존 attempt 정보를 반환한다.
do $$
declare started jsonb; attempt_id uuid; res jsonb;
begin
  started := public.start_attempt('close:2099-03-05', date '2099-03-05', 'close', 'schedule', 300);
  attempt_id := (started->>'run_id')::uuid;
  res := public.request_manual_dispatch('idem-active', 'hash-active', 'neo@example.com', 'close:2099-03-05', date '2099-03-05', 'close');
  if res->>'status' <> 'conflict' or res->>'reason' <> 'ACTIVE_ATTEMPT' then raise exception 'expected active-attempt conflict, got %', res; end if;
  if (res->>'run_id')::uuid <> attempt_id then raise exception 'conflict response did not include the active run_id'; end if;
  if exists (select 1 from public.dispatch_request where idempotency_key = 'idem-active') then
    raise exception 'a dispatch_request row was created despite the active-attempt conflict';
  end if;
end $$;

-- 6) claim_dispatch_outbox: FOR UPDATE SKIP LOCKED로 queued 행을 claim하고 lease/attempts를 갱신한다.
do $$
declare res jsonb; claimed jsonb; claimed_outbox_id uuid; lease uuid;
begin
  res := public.request_manual_dispatch('idem-claim', 'hash-claim', 'neo@example.com', 'close:2099-03-06', date '2099-03-06', 'close');
  claimed := public.claim_dispatch_outbox(120, 20);
  if not exists (select 1 from jsonb_array_elements(claimed) e where (e->>'dispatch_request_id')::uuid = (res->>'dispatch_request_id')::uuid) then
    raise exception 'claim_dispatch_outbox did not return the queued row';
  end if;
  select (e->>'outbox_id')::uuid, (e->>'lease_token')::uuid into claimed_outbox_id, lease
    from jsonb_array_elements(claimed) e where (e->>'dispatch_request_id')::uuid = (res->>'dispatch_request_id')::uuid;
  if (select attempts from public.dispatch_outbox where outbox_id = claimed_outbox_id) <> 1 then raise exception 'attempts was not incremented on claim'; end if;
  -- 아직 lease가 살아있는 동안 재호출하면 다시 claim되지 않는다.
  claimed := public.claim_dispatch_outbox(120, 20);
  if exists (select 1 from jsonb_array_elements(claimed) e where (e->>'outbox_id')::uuid = claimed_outbox_id) then
    raise exception 'a leased row was claimed again before lease expiry';
  end if;
end $$;

-- 7) dead_letter 전이: advance_dispatch_outbox가 lease 소유 하에서만 종결 상태로 전이시킨다.
do $$
declare res jsonb; claimed jsonb; claimed_outbox_id uuid; lease uuid; advanced jsonb; caught boolean := false;
begin
  res := public.request_manual_dispatch('idem-dead', 'hash-dead', 'neo@example.com', 'close:2099-03-07', date '2099-03-07', 'close');
  claimed := public.claim_dispatch_outbox(120, 20);
  select (e->>'outbox_id')::uuid, (e->>'lease_token')::uuid into claimed_outbox_id, lease
    from jsonb_array_elements(claimed) e where (e->>'dispatch_request_id')::uuid = (res->>'dispatch_request_id')::uuid;
  advanced := public.advance_dispatch_outbox(claimed_outbox_id, 'dead_letter', lease);
  if advanced->>'status' <> 'dead_letter' then raise exception 'advance_dispatch_outbox did not reach dead_letter'; end if;
  begin
    perform public.advance_dispatch_outbox(claimed_outbox_id, 'accepted', lease);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'a terminal outbox row accepted a further transition'; end if;
end $$;

-- 8) record_dispatch_receipt: accepted -> started로 idempotent하게 run_id를 기록한다.
do $$
declare res jsonb; claimed jsonb; claimed_outbox_id uuid; lease uuid; started jsonb; run_id uuid; receipt jsonb;
begin
  res := public.request_manual_dispatch('idem-receipt', 'hash-receipt', 'neo@example.com', 'close:2099-03-08', date '2099-03-08', 'close');
  claimed := public.claim_dispatch_outbox(120, 20);
  select (e->>'outbox_id')::uuid, (e->>'lease_token')::uuid into claimed_outbox_id, lease
    from jsonb_array_elements(claimed) e where (e->>'dispatch_request_id')::uuid = (res->>'dispatch_request_id')::uuid;
  perform public.advance_dispatch_outbox(claimed_outbox_id, 'accepted', lease);
  started := public.start_attempt('close:2099-03-08', date '2099-03-08', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  receipt := public.record_dispatch_receipt((res->>'dispatch_request_id')::uuid, run_id);
  if receipt->>'status' <> 'started' then raise exception 'record_dispatch_receipt did not move outbox to started'; end if;
  -- 같은 receipt를 다시 보내도(재시도) run_id가 같으면 idempotent하게 성공한다.
  receipt := public.record_dispatch_receipt((res->>'dispatch_request_id')::uuid, run_id);
  if receipt->>'status' <> 'started' then raise exception 'repeated receipt with the same run_id was rejected'; end if;
end $$;

-- 9) reconcile_dispatch_outbox: started 행을 연결된 runs.status로 completed/failed에 매핑한다.
do $$
declare
  res_ok jsonb; res_fail jsonb;
  started_ok jsonb; started_fail jsonb;
  run_ok uuid; run_fail uuid;
  outbox_ok uuid; outbox_fail uuid;
  fence_ok bigint; lease_ok uuid; fence_fail bigint; lease_fail uuid;
  reconciled jsonb;
begin
  -- 성공 종결: runs.status가 published가 되면 outbox는 completed.
  res_ok := public.request_manual_dispatch('idem-reconcile-ok', 'hash-ok', 'neo@example.com', 'close:2099-03-09', date '2099-03-09', 'close');
  started_ok := public.start_attempt('close:2099-03-09', date '2099-03-09', 'close', 'manual', 300);
  run_ok := (started_ok->>'run_id')::uuid; fence_ok := (started_ok->>'fence_token')::bigint; lease_ok := (started_ok->>'lease_token')::uuid;
  perform public.record_dispatch_receipt((res_ok->>'dispatch_request_id')::uuid, run_ok);
  select outbox_id into outbox_ok from public.dispatch_outbox where dispatch_request_id = (res_ok->>'dispatch_request_id')::uuid;
  perform public.write_stage(run_ok, 'candidates', fence_ok, lease_ok, 'pending', 'running');
  perform public.write_stage(run_ok, 'candidates', fence_ok, lease_ok, 'running', 'success');
  -- Story 2.5: publish_attempt는 tags stage success도 게이트로 요구한다.
  perform public.write_stage(run_ok, 'tags', fence_ok, lease_ok, 'pending', 'running');
  perform public.write_stage(run_ok, 'tags', fence_ok, lease_ok, 'running', 'success');
  perform public.publish_attempt(run_ok, fence_ok, lease_ok);

  -- 실패 종결: runs.status가 failed가 되면 outbox는 failed.
  res_fail := public.request_manual_dispatch('idem-reconcile-fail', 'hash-fail', 'neo@example.com', 'close:2099-03-10', date '2099-03-10', 'close');
  started_fail := public.start_attempt('close:2099-03-10', date '2099-03-10', 'close', 'manual', 300);
  run_fail := (started_fail->>'run_id')::uuid; fence_fail := (started_fail->>'fence_token')::bigint; lease_fail := (started_fail->>'lease_token')::uuid;
  perform public.record_dispatch_receipt((res_fail->>'dispatch_request_id')::uuid, run_fail);
  select outbox_id into outbox_fail from public.dispatch_outbox where dispatch_request_id = (res_fail->>'dispatch_request_id')::uuid;
  perform public.write_stage(run_fail, 'candidates', fence_fail, lease_fail, 'pending', 'running');
  perform public.write_stage(run_fail, 'candidates', fence_fail, lease_fail, 'running', 'failed');

  reconciled := public.reconcile_dispatch_outbox();
  if coalesce((reconciled->>'completed')::integer, 0) < 1 or coalesce((reconciled->>'failed')::integer, 0) < 1 then
    raise exception 'reconcile_dispatch_outbox did not report both completed and failed transitions, got %', reconciled;
  end if;
  if (select status from public.dispatch_outbox where outbox_id = outbox_ok) <> 'completed' then raise exception 'published run did not map outbox to completed'; end if;
  if (select status from public.dispatch_outbox where outbox_id = outbox_fail) <> 'failed' then raise exception 'failed run did not map outbox to failed'; end if;

  -- running/ready_to_publish처럼 미종결 상태는 건드리지 않는다: 이미 completed/failed가 된 행을 다시 돌리지 않는지 확인.
  reconciled := public.reconcile_dispatch_outbox();
  if (reconciled->>'completed')::integer <> 0 or (reconciled->>'failed')::integer <> 0 then
    raise exception 'reconcile_dispatch_outbox re-processed already-terminal outbox rows';
  end if;
end $$;

-- 10) advance_dispatch_outbox는 순방향 전이만 허용한다: queued 행에 started/queued로의 전이는 거부된다
-- (started는 record_dispatch_receipt 전담, 그 외 임의 전이는 호출자 오용으로 간주한다).
do $$
declare res jsonb; claimed jsonb; claimed_outbox_id uuid; lease uuid; caught_started boolean := false; caught_queued boolean := false;
begin
  res := public.request_manual_dispatch('idem-transition', 'hash-transition', 'neo@example.com', 'close:2099-03-11', date '2099-03-11', 'close');
  claimed := public.claim_dispatch_outbox(120, 20);
  select (e->>'outbox_id')::uuid, (e->>'lease_token')::uuid into claimed_outbox_id, lease
    from jsonb_array_elements(claimed) e where (e->>'dispatch_request_id')::uuid = (res->>'dispatch_request_id')::uuid;

  begin
    perform public.advance_dispatch_outbox(claimed_outbox_id, 'started', lease);
  exception when others then caught_started := true;
  end;
  if not caught_started then raise exception 'queued->started was accepted by advance_dispatch_outbox'; end if;

  begin
    perform public.advance_dispatch_outbox(claimed_outbox_id, 'queued', lease);
  exception when others then caught_queued := true;
  end;
  if not caught_queued then raise exception 'queued->queued was accepted by advance_dispatch_outbox'; end if;

  if (select status from public.dispatch_outbox where outbox_id = claimed_outbox_id) <> 'queued' then
    raise exception 'rejected transitions still mutated the outbox row';
  end if;

  -- 정상 순방향 전이(queued->accepted)는 여전히 허용된다.
  perform public.advance_dispatch_outbox(claimed_outbox_id, 'accepted', lease);
  if (select status from public.dispatch_outbox where outbox_id = claimed_outbox_id) <> 'accepted' then
    raise exception 'valid queued->accepted transition was rejected';
  end if;
end $$;

rollback;
