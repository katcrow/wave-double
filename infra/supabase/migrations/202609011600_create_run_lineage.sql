-- Story 1.3: 영속 배치 실행 계보와 lease/fence 상태머신.
-- 이 migration과 아래 RPC만 run publication의 권위다 (AD-3, AD-13, AD-20).
create extension if not exists pgcrypto;

create table if not exists public.logical_runs (
  logical_run_key text primary key,
  trading_day date not null,
  batch_kind text not null check (batch_kind in ('premarket', 'intraday', 'close')),
  active_attempt_run_id uuid,
  canonical_success_run_id uuid,
  current_complete_run_id uuid,
  latest_partial_run_id uuid,
  published_at timestamptz,
  constraint logical_run_key_shape check (
    (batch_kind = 'intraday' and logical_run_key ~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):[0-5][0-9]$')
    or (batch_kind in ('premarket', 'close') and logical_run_key ~ ('^' || batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$'))
  ),
  constraint canonical_close_only check (batch_kind = 'close' or canonical_success_run_id is null)
);

create table if not exists public.runs (
  run_id uuid primary key default gen_random_uuid(),
  logical_run_key text not null references public.logical_runs(logical_run_key),
  attempt_no integer not null check (attempt_no > 0),
  fence_token bigint not null check (fence_token > 0),
  lease_token uuid not null default gen_random_uuid(),
  lease_expires_at timestamptz not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  trigger text not null check (trigger in ('schedule', 'manual')),
  status text not null check (status in ('running', 'ready_to_publish', 'published', 'partial', 'failed', 'skipped', 'superseded', 'cancelled')),
  skip_reason text,
  stage_status jsonb not null default '{"candidates":"pending","tags":"pending","supply_3day":"pending","market_supply":"pending","outcome_tracking":"pending"}'::jsonb,
  unprocessed_count integer not null default 0 check (unprocessed_count >= 0),
  truncated_count integer not null default 0 check (truncated_count >= 0),
  fallback_used boolean not null default false,
  selection_input_hash text,
  original_count integer check (original_count is null or original_count >= 0),
  excluded_count integer check (excluded_count is null or excluded_count >= 0),
  unique (logical_run_key, attempt_no),
  unique (logical_run_key, fence_token),
  constraint run_stage_keys check (
    stage_status = jsonb_build_object('candidates', stage_status->>'candidates', 'tags', stage_status->>'tags', 'supply_3day', stage_status->>'supply_3day', 'market_supply', stage_status->>'market_supply', 'outcome_tracking', stage_status->>'outcome_tracking')
  ),
  constraint run_stage_values check (
    (stage_status->>'candidates') in ('pending','running','success','failed','partial') and
    (stage_status->>'tags') in ('pending','running','success','failed','partial') and
    (stage_status->>'supply_3day') in ('pending','running','success','failed','partial') and
    (stage_status->>'market_supply') in ('pending','running','success','failed','partial') and
    (stage_status->>'outcome_tracking') in ('pending','running','success','failed','partial')
  )
);

alter table public.logical_runs
  drop constraint if exists logical_runs_active_attempt_run_id_fkey,
  drop constraint if exists logical_runs_canonical_success_run_id_fkey,
  drop constraint if exists logical_runs_current_complete_run_id_fkey,
  drop constraint if exists logical_runs_latest_partial_run_id_fkey;
alter table public.logical_runs
  add constraint logical_runs_active_attempt_run_id_fkey foreign key (active_attempt_run_id) references public.runs(run_id),
  add constraint logical_runs_canonical_success_run_id_fkey foreign key (canonical_success_run_id) references public.runs(run_id),
  add constraint logical_runs_current_complete_run_id_fkey foreign key (current_complete_run_id) references public.runs(run_id),
  add constraint logical_runs_latest_partial_run_id_fkey foreign key (latest_partial_run_id) references public.runs(run_id);

create index if not exists runs_logical_run_key_started_at_idx on public.runs(logical_run_key, started_at desc);
create index if not exists runs_lease_idx on public.runs(status, lease_expires_at);

comment on table public.logical_runs is '거래일/배치/장중 슬롯 단위의 논리 계보. attempt 이력은 삭제하지 않는다.';
comment on table public.runs is '재시도 가능한 attempt 단위 실행. lease_token과 fence_token은 현재 소유권을 증명한다.';

create or replace function public.start_attempt(
  p_logical_run_key text,
  p_trading_day date,
  p_batch_kind text,
  p_trigger text,
  p_lease_seconds integer default 300
) returns jsonb language plpgsql security definer set search_path = public as $$
declare
  logical_row public.logical_runs;
  new_run public.runs;
  next_attempt integer;
  next_fence bigint;
begin
  if p_lease_seconds <= 0 then raise exception using message = 'lease_seconds must be positive'; end if;
  if p_batch_kind not in ('premarket','intraday','close') or p_trigger not in ('schedule','manual') then
    raise exception using message = 'invalid batch kind or trigger';
  end if;
  insert into logical_runs(logical_run_key, trading_day, batch_kind)
    values (p_logical_run_key, p_trading_day, p_batch_kind)
    on conflict (logical_run_key) do nothing;
  select * into logical_row from logical_runs where logical_run_key = p_logical_run_key for update;
  if logical_row.trading_day <> p_trading_day or logical_row.batch_kind <> p_batch_kind then
    raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH';
  end if;
  if logical_row.canonical_success_run_id is not null then
    return jsonb_build_object('replayed', true, 'run_id', logical_row.canonical_success_run_id, 'logical_run_key', p_logical_run_key);
  end if;
  if logical_row.active_attempt_run_id is not null then
    update runs set status = 'superseded', finished_at = now()
      where run_id = logical_row.active_attempt_run_id and status in ('running', 'ready_to_publish');
  end if;
  select coalesce(max(attempt_no), 0) + 1, coalesce(max(fence_token), 0) + 1
    into next_attempt, next_fence from runs where logical_run_key = p_logical_run_key;
  insert into runs(logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status)
    values (p_logical_run_key, next_attempt, next_fence, now() + make_interval(secs => p_lease_seconds), p_trigger, 'running')
    returning * into new_run;
  update logical_runs set active_attempt_run_id = new_run.run_id where logical_run_key = p_logical_run_key;
  return jsonb_build_object('run_id', new_run.run_id, 'logical_run_key', new_run.logical_run_key,
    'attempt_no', new_run.attempt_no, 'fence_token', new_run.fence_token, 'lease_token', new_run.lease_token,
    'lease_expires_at', new_run.lease_expires_at);
end $$;

create or replace function public.write_stage(
  p_run_id uuid, p_stage text, p_fence_token bigint, p_lease_token uuid,
  p_expected_status text, p_status text, p_result jsonb default '{}'::jsonb,
  p_unprocessed_count integer default 0
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs; current_status text; next_run_status text;
begin
  if p_stage not in ('candidates','tags','supply_3day','market_supply','outcome_tracking') or p_status not in ('pending','running','success','failed','partial') then
    raise exception using message = 'invalid stage or stage status';
  end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now()
     or (r.status <> 'running' and not (r.stage_status->>p_stage = p_expected_status and p_expected_status = p_status and p_status in ('success','failed','partial'))) then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  current_status := r.stage_status->>p_stage;
  if current_status <> p_expected_status then raise exception using message = 'EXPECTED_STATUS_MISMATCH'; end if;
  if not ((p_expected_status = 'pending' and p_status = 'running') or (p_expected_status = 'running' and p_status in ('success','failed','partial')) or (p_expected_status = p_status and p_status in ('success','failed','partial'))) then
    raise exception using message = 'INVALID_STAGE_TRANSITION';
  end if;
  update runs set stage_status = jsonb_set(stage_status, array[p_stage], to_jsonb(p_status)),
      unprocessed_count = greatest(unprocessed_count, p_unprocessed_count),
      status = case when p_stage = 'candidates' and p_status = 'success' then 'ready_to_publish'
                    when p_stage = 'candidates' and p_status = 'partial' then 'partial'
                    when p_stage = 'candidates' and p_status = 'failed' then 'failed' else status end,
      finished_at = case when p_status in ('success','failed','partial') and p_stage = 'candidates' then now() else finished_at end
    where run_id = p_run_id returning * into r;
  if r.status = 'partial' then
    update logical_runs set latest_partial_run_id = r.run_id
      where logical_run_key = r.logical_run_key;
  end if;
  return jsonb_build_object('run_id', r.run_id, 'stage', p_stage, 'status', r.status, 'stage_status', r.stage_status);
end $$;

create or replace function public.heartbeat_attempt(
  p_run_id uuid, p_fence_token bigint, p_lease_token uuid, p_lease_seconds integer default 300
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs;
begin
  if p_lease_seconds <= 0 then raise exception using message = 'lease_seconds must be positive'; end if;
  update runs set lease_expires_at = now() + make_interval(secs => p_lease_seconds)
    where run_id = p_run_id and fence_token = p_fence_token and lease_token = p_lease_token
      and status = 'running' and lease_expires_at > now() returning * into r;
  if not found then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  return jsonb_build_object('run_id', r.run_id, 'lease_expires_at', r.lease_expires_at);
end $$;

create or replace function public.reap_expired_attempts(p_now timestamptz default now()) returns integer
language plpgsql security definer set search_path = public as $$
declare r public.runs; logical_row public.logical_runs; changed integer := 0; next_status text;
begin
  for r in select * from runs where status = 'running' and lease_expires_at <= p_now for update loop
    select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
    next_status := case when logical_row.active_attempt_run_id is distinct from r.run_id then 'failed'
      when r.stage_status->>'candidates' = 'success' then 'ready_to_publish' else 'failed' end;
    update runs set status = next_status, finished_at = p_now where run_id = r.run_id and status = 'running';
    update logical_runs set active_attempt_run_id = null where logical_run_key = r.logical_run_key and active_attempt_run_id = r.run_id;
    changed := changed + 1;
  end loop;
  return changed;
end $$;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint) returns jsonb
language plpgsql security definer set search_path = public as $$
declare r public.runs; logical_row public.logical_runs;
begin
  select * into r from runs where run_id = p_run_id;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  -- PostgreSQL 함수 내부에서 transaction isolation을 변경할 수 없으므로,
  -- logical key별 advisory xact lock을 serializable publication lock으로 사용한다.
  perform pg_advisory_xact_lock(hashtextextended(r.logical_run_key, 0));
  select * into r from runs where run_id = p_run_id for update;
  select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
  if logical_row.active_attempt_run_id is distinct from p_run_id or r.fence_token <> p_fence_token or r.lease_expires_at <= now() then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  if r.status <> 'ready_to_publish' or r.stage_status->>'candidates' <> 'success' then
    raise exception using message = 'PUBLISH_GUARD_FAILED';
  end if;
  if logical_row.canonical_success_run_id is not null then
    raise exception using message = 'CANONICAL_ALREADY_PUBLISHED';
  end if;
  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id,
      canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end,
      published_at = now()
    where logical_run_key = r.logical_run_key;
  return jsonb_build_object('run_id', p_run_id, 'status', 'published', 'canonical_success_run_id',
    case when logical_row.batch_kind = 'close' then p_run_id else null end);
end $$;
