-- Story 1.5: attempt-scoped 후보 모집단과 원천 기여도.
-- 202609011600_create_run_lineage.sql 이후에 적용한다.
begin;

create table if not exists public.candidates (
  candidate_id uuid primary key default gen_random_uuid(),
  attempt_run_id uuid not null references public.runs(run_id),
  ticker text not null check (length(btrim(ticker)) > 0),
  name text,
  trading_day date not null,
  trading_value numeric not null check (trading_value <> 'NaN'::numeric and trading_value <> 'Infinity'::numeric and trading_value <> '-Infinity'::numeric),
  truncated boolean not null default false,
  unique (candidate_id, attempt_run_id),
  unique (ticker, trading_day, attempt_run_id)
);

create table if not exists public.candidate_source_contrib (
  candidate_id uuid not null,
  attempt_run_id uuid not null references public.runs(run_id),
  source text not null check (source in ('t1859', 't1852', 't1856')),
  contribution_weight numeric not null check (contribution_weight > 0 and contribution_weight <> 'NaN'::numeric and contribution_weight <> 'Infinity'::numeric and contribution_weight <> '-Infinity'::numeric),
  primary key (candidate_id, attempt_run_id, source),
  foreign key (candidate_id, attempt_run_id)
    references public.candidates(candidate_id, attempt_run_id)
);

create index if not exists candidates_attempt_day_idx on public.candidates(attempt_run_id, trading_day);
create index if not exists candidate_source_contrib_attempt_idx on public.candidate_source_contrib(attempt_run_id);

comment on table public.candidates is '조건검색으로 선정된 attempt-scoped 후보. 원천은 contribution 테이블에서만 관리한다.';
comment on table public.candidate_source_contrib is '후보 원천 provenance와 기여도. 합계 검증은 stage RPC가 수행한다.';

create or replace function public.write_candidates(
  p_run_id uuid,
  p_fence_token bigint,
  p_lease_token uuid,
  p_candidates jsonb,
  p_metadata jsonb
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs; item jsonb; candidate_count integer := 0; candidate_day date;
begin
  if jsonb_typeof(p_candidates) <> 'array' or jsonb_typeof(p_metadata) <> 'object' then
    raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
  end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status <> 'running' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  select trading_day into candidate_day from logical_runs where logical_run_key = r.logical_run_key;
  if coalesce((p_metadata->>'truncated_count')::integer, 0) < 0
     or coalesce((p_metadata->>'excluded_count')::integer, 0) < 0 then
    raise exception using message = 'INVALID_CANDIDATE_METADATA';
  end if;
  for item in select value from jsonb_array_elements(p_candidates) loop
    if (item->>'candidate_id') is null or (item->>'ticker') is null or length(btrim(item->>'ticker')) = 0
       or (item->>'trading_value') is null or (item->>'trading_value')::numeric in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
      raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
    end if;
    insert into candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value, truncated)
      values ((item->>'candidate_id')::uuid, p_run_id, btrim(item->>'ticker'), nullif(btrim(item->>'name'), ''),
              candidate_day, (item->>'trading_value')::numeric, false)
      on conflict (candidate_id, attempt_run_id) do nothing;
    insert into candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
      values ((item->>'candidate_id')::uuid, p_run_id, 't1859', 1.0)
      on conflict (candidate_id, attempt_run_id, source) do update set contribution_weight = excluded.contribution_weight;
    candidate_count := candidate_count + 1;
  end loop;
  update runs set selection_input_hash = p_metadata->>'selection_input_hash',
      original_count = (p_metadata->>'original_count')::integer,
      excluded_count = (p_metadata->>'excluded_count')::integer,
      truncated_count = (p_metadata->>'truncated_count')::integer
    where run_id = p_run_id;
  return jsonb_build_object('run_id', p_run_id, 'candidate_count', candidate_count);
exception when invalid_text_representation or numeric_value_out_of_range then
  raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
end $$;

commit;
