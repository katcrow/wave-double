-- Story 1.10: 인증 & 수동 트리거 -- dispatch_request/dispatch_outbox와 관련 RPC.
-- AD-7/AD-18: dispatch route는 하나의 RPC로 dispatch_request+dispatch_outbox를 원자적으로 생성하고,
-- outbox worker만 FOR UPDATE SKIP LOCKED + lease로 claim해 GitHub workflow dispatch를 호출한다.
-- request_manual_dispatch는 start_attempt를 호출하지 않는다(Design Notes) -- 실제 attempt 생성은
-- GitHub Actions에서 배치 CLI가 record_dispatch_receipt로 receipt를 남기는 시점에 일어난다.
begin;

create table if not exists public.dispatch_request (
  dispatch_request_id uuid primary key default gen_random_uuid(),
  idempotency_key text not null,
  payload_hash text not null,
  requested_by text not null,
  logical_run_key text not null,
  created_at timestamptz not null default now(),
  unique (idempotency_key)
);

create table if not exists public.dispatch_outbox (
  outbox_id uuid primary key default gen_random_uuid(),
  dispatch_request_id uuid not null references public.dispatch_request(dispatch_request_id),
  status text not null default 'queued' check (status in ('queued', 'accepted', 'started', 'completed', 'failed', 'dead_letter')),
  lease_token uuid,
  lease_expires_at timestamptz,
  run_id uuid references public.runs(run_id),
  github_run_id bigint,
  attempts integer not null default 0 check (attempts >= 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (dispatch_request_id)
);

create index if not exists dispatch_outbox_claimable_idx
  on public.dispatch_outbox (status, lease_expires_at);
create index if not exists dispatch_outbox_started_run_idx
  on public.dispatch_outbox (run_id) where status = 'started';

alter table public.dispatch_request enable row level security;
alter table public.dispatch_outbox enable row level security;
-- 의도적으로 policy를 만들지 않는다: anon/authenticated에게는 deny-all이고, service_role은 RLS를 우회한다.

comment on table public.dispatch_request is
  'Story 1.10: 인증된 수동 실행 요청의 idempotency 원장. 같은 idempotency_key+payload_hash는 재요청이며, 같은 key+다른 hash는 거부한다.';
comment on table public.dispatch_outbox is
  'Story 1.10: transactional outbox. queued -> accepted -> started -> completed | failed | dead_letter로만 전이한다(AD-18). started는 종결 상태가 아니다 -- reconcile_dispatch_outbox가 연결된 runs.status로 종결시킨다.';

create or replace function public.request_manual_dispatch(
  p_idempotency_key text,
  p_payload_hash text,
  p_requested_by text,
  p_logical_run_key text,
  p_trading_day date,
  p_batch_kind text
) returns jsonb language plpgsql security definer set search_path = public as $$
declare
  existing_request public.dispatch_request;
  existing_outbox public.dispatch_outbox;
  active_run uuid;
  active_row public.runs;
  new_request public.dispatch_request;
  new_outbox public.dispatch_outbox;
begin
  if p_idempotency_key is null or length(btrim(p_idempotency_key)) = 0
     or p_payload_hash is null or length(btrim(p_payload_hash)) = 0
     or p_requested_by is null or length(btrim(p_requested_by)) = 0 then
    raise exception using message = 'INVALID_DISPATCH_REQUEST';
  end if;
  if p_batch_kind not in ('premarket', 'intraday', 'close') then
    raise exception using message = 'invalid batch kind';
  end if;
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|30)$')
     or (p_batch_kind in ('premarket', 'close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then
    raise exception using message = 'invalid logical run key';
  end if;
  -- Boundaries "Always": p_trading_day가 p_logical_run_key에 내포된 날짜와 일치해야 한다.
  -- p_trading_day가 NULL이면 <>는 NULL로 평가돼 if 조건이 조용히 통과되므로 NULL을 명시적으로 거부한다.
  if p_trading_day is null or split_part(p_logical_run_key, ':', 2)::date <> p_trading_day then
    raise exception using message = 'TRADING_DAY_MISMATCH';
  end if;

  select * into existing_request from dispatch_request where idempotency_key = p_idempotency_key for update;
  if found then
    if existing_request.payload_hash <> p_payload_hash then
      raise exception using message = 'IDEMPOTENCY_KEY_CONFLICT';
    end if;
    select * into existing_outbox from dispatch_outbox where dispatch_request_id = existing_request.dispatch_request_id;
    return jsonb_build_object(
      'status', coalesce(existing_outbox.status, 'queued'),
      'dispatch_request_id', existing_request.dispatch_request_id,
      'reason', 'replayed'
    );
  end if;

  -- 활성 attempt 가드: 1.3 fence 모델의 active_attempt_run_id를 읽기전용으로만 확인한다.
  -- start_attempt의 supersede 분기는 호출하지 않는다(Design Notes).
  select active_attempt_run_id into active_run from logical_runs where logical_run_key = p_logical_run_key for update;
  if active_run is not null then
    select * into active_row from runs where run_id = active_run;
    return jsonb_build_object(
      'status', 'conflict',
      'reason', 'ACTIVE_ATTEMPT',
      'run_id', active_row.run_id,
      'started_at', active_row.started_at,
      'trigger', active_row.trigger
    );
  end if;

  insert into dispatch_request(idempotency_key, payload_hash, requested_by, logical_run_key)
    values (p_idempotency_key, p_payload_hash, p_requested_by, p_logical_run_key)
    returning * into new_request;
  insert into dispatch_outbox(dispatch_request_id, status)
    values (new_request.dispatch_request_id, 'queued')
    returning * into new_outbox;
  return jsonb_build_object(
    'status', new_outbox.status,
    'dispatch_request_id', new_request.dispatch_request_id,
    'outbox_id', new_outbox.outbox_id,
    'reason', 'created'
  );
exception when unique_violation then
  -- 동시 요청이 같은 idempotency_key로 먼저 커밋됐다. 재조회해 idempotent 응답으로 수렴한다.
  select * into existing_request from dispatch_request where idempotency_key = p_idempotency_key;
  if existing_request.payload_hash <> p_payload_hash then
    raise exception using message = 'IDEMPOTENCY_KEY_CONFLICT';
  end if;
  select * into existing_outbox from dispatch_outbox where dispatch_request_id = existing_request.dispatch_request_id;
  return jsonb_build_object(
    'status', coalesce(existing_outbox.status, 'queued'),
    'dispatch_request_id', existing_request.dispatch_request_id,
    'reason', 'replayed'
  );
end $$;

create or replace function public.claim_dispatch_outbox(
  p_worker_lease_seconds integer default 120,
  p_limit integer default 20
) returns jsonb language plpgsql security definer set search_path = public as $$
declare result jsonb;
begin
  if p_worker_lease_seconds <= 0 or p_limit <= 0 then
    raise exception using message = 'invalid claim parameters';
  end if;

  with candidates as (
    select o.outbox_id
    from dispatch_outbox o
    where (o.status = 'queued' and (o.lease_expires_at is null or o.lease_expires_at <= now()))
       or (o.status = 'accepted' and o.lease_expires_at <= now())
    order by o.updated_at
    limit p_limit
    for update of o skip locked
  ), updated as (
    update dispatch_outbox o
      set lease_token = gen_random_uuid(),
          lease_expires_at = now() + make_interval(secs => p_worker_lease_seconds),
          attempts = o.attempts + 1,
          updated_at = now()
      from candidates
      where o.outbox_id = candidates.outbox_id
      returning o.outbox_id, o.dispatch_request_id, o.status, o.lease_token, o.run_id, o.github_run_id, o.attempts
  )
  select coalesce(jsonb_agg(jsonb_build_object(
      'outbox_id', updated.outbox_id,
      'dispatch_request_id', updated.dispatch_request_id,
      'status', updated.status,
      'lease_token', updated.lease_token,
      'run_id', updated.run_id,
      'github_run_id', updated.github_run_id,
      'attempts', updated.attempts,
      'logical_run_key', dr.logical_run_key,
      'idempotency_key', dr.idempotency_key
    )), '[]'::jsonb)
    into result
    from updated join dispatch_request dr on dr.dispatch_request_id = updated.dispatch_request_id;

  return result;
end $$;

create or replace function public.advance_dispatch_outbox(
  p_outbox_id uuid,
  p_status text,
  p_lease_token uuid,
  p_run_id uuid default null,
  p_github_run_id bigint default null
) returns jsonb language plpgsql security definer set search_path = public as $$
declare o public.dispatch_outbox;
begin
  if p_status not in ('queued', 'accepted', 'started', 'completed', 'failed', 'dead_letter') then
    raise exception using message = 'invalid outbox status';
  end if;
  select * into o from dispatch_outbox where outbox_id = p_outbox_id for update;
  if not found then raise exception using message = 'OUTBOX_NOT_FOUND'; end if;
  if o.lease_token is distinct from p_lease_token then raise exception using message = 'STALE_LEASE'; end if;
  if o.status in ('completed', 'failed', 'dead_letter') then raise exception using message = 'OUTBOX_ALREADY_TERMINAL'; end if;
  -- 순방향 상태 전이만 허용한다: queued->accepted, {queued,accepted}->dead_letter.
  -- started/completed/failed는 이 RPC의 책임이 아니다(각각 record_dispatch_receipt/
  -- reconcile_dispatch_outbox가 전담) -- 그 외 조합은 호출자 실수/오용으로 간주해 거부한다.
  if not (
    (o.status = 'queued' and p_status in ('accepted', 'dead_letter'))
    or (o.status = 'accepted' and p_status = 'dead_letter')
  ) then
    raise exception using message = 'INVALID_OUTBOX_TRANSITION';
  end if;
  update dispatch_outbox
    set status = p_status,
        run_id = coalesce(p_run_id, run_id),
        github_run_id = coalesce(p_github_run_id, github_run_id),
        updated_at = now()
    where outbox_id = p_outbox_id
    returning * into o;
  return jsonb_build_object('outbox_id', o.outbox_id, 'status', o.status, 'run_id', o.run_id, 'github_run_id', o.github_run_id, 'attempts', o.attempts);
end $$;

create or replace function public.record_dispatch_receipt(
  p_dispatch_request_id uuid,
  p_run_id uuid
) returns jsonb language plpgsql security definer set search_path = public as $$
declare o public.dispatch_outbox;
begin
  if p_dispatch_request_id is null or p_run_id is null then
    raise exception using message = 'INVALID_RECEIPT';
  end if;
  select * into o from dispatch_outbox where dispatch_request_id = p_dispatch_request_id for update;
  if not found then raise exception using message = 'DISPATCH_REQUEST_NOT_FOUND'; end if;
  if o.status in ('completed', 'failed', 'dead_letter') then
    -- 이미 종결된 outbox에 대한 지연 receipt는 무시한다 -- 재시도로 상태를 되돌리지 않는다(Boundaries).
    return jsonb_build_object('outbox_id', o.outbox_id, 'status', o.status, 'run_id', o.run_id, 'ignored', true);
  end if;
  if o.run_id is not null and o.run_id <> p_run_id then
    raise exception using message = 'RECEIPT_RUN_ID_MISMATCH';
  end if;
  update dispatch_outbox set run_id = p_run_id, status = 'started', updated_at = now()
    where outbox_id = o.outbox_id returning * into o;
  return jsonb_build_object('outbox_id', o.outbox_id, 'status', o.status, 'run_id', o.run_id, 'ignored', false);
end $$;

-- started -> completed|failed 종결 규칙(Boundaries "Always"): outbox worker가 매 tick 끝에 호출한다.
-- running/ready_to_publish(미종결)은 건드리지 않는다.
create or replace function public.reconcile_dispatch_outbox() returns jsonb
language plpgsql security definer set search_path = public as $$
declare completed_count integer := 0; failed_count integer := 0;
begin
  with target as (
    select o.outbox_id, r.status as run_status
    from dispatch_outbox o
    join runs r on r.run_id = o.run_id
    where o.status = 'started'
      and r.status in ('published', 'partial', 'skipped', 'failed', 'superseded', 'cancelled')
    for update of o
  ), updated as (
    update dispatch_outbox o
      set status = case when target.run_status in ('published', 'partial', 'skipped') then 'completed' else 'failed' end,
          updated_at = now()
      from target
      where o.outbox_id = target.outbox_id
      returning (case when target.run_status in ('published', 'partial', 'skipped') then 'completed' else 'failed' end) as new_status
  )
  select count(*) filter (where new_status = 'completed'), count(*) filter (where new_status = 'failed')
    into completed_count, failed_count
    from updated;
  return jsonb_build_object('completed', completed_count, 'failed', failed_count);
end $$;

revoke execute on function public.request_manual_dispatch(text, text, text, text, date, text) from public, anon, authenticated;
revoke execute on function public.claim_dispatch_outbox(integer, integer) from public, anon, authenticated;
revoke execute on function public.advance_dispatch_outbox(uuid, text, uuid, uuid, bigint) from public, anon, authenticated;
revoke execute on function public.record_dispatch_receipt(uuid, uuid) from public, anon, authenticated;
revoke execute on function public.reconcile_dispatch_outbox() from public, anon, authenticated;

grant execute on function public.request_manual_dispatch(text, text, text, text, date, text) to service_role;
grant execute on function public.claim_dispatch_outbox(integer, integer) to service_role;
grant execute on function public.advance_dispatch_outbox(uuid, text, uuid, uuid, bigint) to service_role;
grant execute on function public.record_dispatch_receipt(uuid, uuid) to service_role;
grant execute on function public.reconcile_dispatch_outbox() to service_role;

commit;
