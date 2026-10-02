-- 후보 attempt별 종목 테마(t1532)를 스냅샷으로 저장하고 카드 RPC에 반환한다.
-- 테마 조회 실패는 배치에서 빈 배열로 격리되며 후보 발행 계약은 유지한다.
begin;

create table if not exists public.candidate_themes (
  candidate_id uuid not null,
  attempt_run_id uuid not null references public.runs(run_id),
  theme_code text not null check (length(btrim(theme_code)) > 0),
  theme_name text not null check (length(btrim(theme_name)) > 0),
  average_change_pct numeric not null check (
    average_change_pct <> 'NaN'::numeric
    and average_change_pct <> 'Infinity'::numeric
    and average_change_pct <> '-Infinity'::numeric
  ),
  collected_at timestamptz not null default now(),
  primary key (candidate_id, attempt_run_id, theme_code),
  foreign key (candidate_id, attempt_run_id)
    references public.candidates(candidate_id, attempt_run_id)
    on delete cascade
);

alter table public.candidate_themes enable row level security;
create index if not exists candidate_themes_attempt_idx
  on public.candidate_themes(attempt_run_id, candidate_id, average_change_pct desc, theme_code);
comment on table public.candidate_themes is
  'LS t1532 종목별 테마의 attempt-scoped 스냅샷. average_change_pct는 LS가 반환한 테마 평균등락률이다.';

create or replace function public.write_candidates(
  p_run_id uuid,
  p_fence_token bigint,
  p_lease_token uuid,
  p_candidates jsonb,
  p_metadata jsonb
)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  r public.runs;
  item jsonb;
  theme_item jsonb;
  theme_payload jsonb;
  source_item jsonb;
  candidate_count integer := 0;
  candidate_day date;
  weight_sum numeric;
  source_code text;
  source_weight numeric;
begin
  if jsonb_typeof(p_candidates) <> 'array' or jsonb_typeof(p_metadata) <> 'object' then
    raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
  end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status <> 'running' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  if coalesce((p_metadata->>'candidate_count')::integer, -1) <> jsonb_array_length(p_candidates)
     or coalesce((p_metadata->>'candidate_count')::integer, -1) > 150
     or coalesce((p_metadata->>'original_count')::integer, -1) < coalesce((p_metadata->>'candidate_count')::integer, 0) + coalesce((p_metadata->>'excluded_count')::integer, 0) + coalesce((p_metadata->>'truncated_count')::integer, 0) then
    raise exception using message = 'INVALID_CANDIDATE_METADATA';
  end if;
  select trading_day into candidate_day from logical_runs where logical_run_key = r.logical_run_key;
  for item in select value from jsonb_array_elements(p_candidates) loop
    if (item->>'candidate_id') is null
       or (item->>'ticker') is null
       or length(btrim(item->>'ticker')) = 0
       or (item->>'trading_value') is null
       or (item->>'trading_value')::numeric in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
       or coalesce((item->>'truncated')::boolean, false)
       or jsonb_typeof(item->'sources') <> 'array'
       or jsonb_array_length(item->'sources') < 1 then
      raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
    end if;
    if (select count(distinct s->>'source') from jsonb_array_elements(item->'sources') s) <> jsonb_array_length(item->'sources') then
      raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
    end if;

    insert into candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value, truncated)
      values (
        (item->>'candidate_id')::uuid,
        p_run_id,
        btrim(item->>'ticker'),
        nullif(btrim(item->>'name'), ''),
        candidate_day,
        (item->>'trading_value')::numeric,
        false
      )
      on conflict (candidate_id, attempt_run_id) do nothing;

    delete from candidate_themes
      where candidate_id = (item->>'candidate_id')::uuid
        and attempt_run_id = p_run_id;
    theme_payload := coalesce(item->'themes', '[]'::jsonb);
    if jsonb_typeof(theme_payload) <> 'array' then
      raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
    end if;
    for theme_item in select value from jsonb_array_elements(theme_payload) loop
      if jsonb_typeof(theme_item) <> 'object'
         or nullif(btrim(theme_item->>'theme_code'), '') is null
         or nullif(btrim(theme_item->>'theme_name'), '') is null
         or (theme_item->>'average_change_pct') is null
         or (theme_item->>'average_change_pct')::numeric in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
        raise exception using message = 'INVALID_CANDIDATE_THEME_PAYLOAD';
      end if;
      insert into candidate_themes(
        candidate_id, attempt_run_id, theme_code, theme_name, average_change_pct
      ) values (
        (item->>'candidate_id')::uuid,
        p_run_id,
        btrim(theme_item->>'theme_code'),
        btrim(theme_item->>'theme_name'),
        (theme_item->>'average_change_pct')::numeric
      );
    end loop;

    weight_sum := 0;
    for source_item in select value from jsonb_array_elements(item->'sources') loop
      source_code := source_item->>'source';
      if source_code is null or source_code not in ('t1859', 't1852', 't1856') then
        raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
      end if;
      source_weight := nullif(source_item->>'weight', '')::numeric;
      if source_weight is null or source_weight <= 0 or source_weight > 1 then
        raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
      end if;
      weight_sum := weight_sum + source_weight;
      insert into candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
        values ((item->>'candidate_id')::uuid, p_run_id, source_code, source_weight)
        on conflict (candidate_id, attempt_run_id, source) do update set contribution_weight = excluded.contribution_weight;
    end loop;
    if abs(weight_sum - 1) > 0.0001 then
      raise exception using message = 'INVALID_CANDIDATE_SOURCE_WEIGHTS';
    end if;
    candidate_count := candidate_count + 1;
  end loop;
  update runs set
    selection_input_hash = p_metadata->>'selection_input_hash',
    original_count = (p_metadata->>'original_count')::integer,
    excluded_count = (p_metadata->>'excluded_count')::integer,
    truncated_count = (p_metadata->>'truncated_count')::integer
    where run_id = p_run_id;
  return jsonb_build_object('run_id', p_run_id, 'candidate_count', candidate_count);
exception when invalid_text_representation or numeric_value_out_of_range then
  raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
end $$;

create or replace function public.get_today_candidate_cards(p_run_id uuid)
returns jsonb
language sql
security definer
stable
set search_path = public
as $$
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', card.candidate_id,
        'ticker', card.ticker,
        'name', card.name,
        'strategies', to_jsonb(card.strategies),
        'vanished_strategies', to_jsonb(card.vanished_strategies),
        'supply_partial_missing', card.supply_partial_missing,
        'themes', card.themes
      )
      order by card.ticker
    ),
    '[]'::jsonb
  )
  from (
    select
      c.candidate_id,
      c.ticker,
      c.name,
      coalesce(
        array_agg(distinct t.strategy order by t.strategy) filter (where t.status = 'active'),
        array[]::text[]
      ) as strategies,
      coalesce(
        array_agg(distinct t.strategy order by t.strategy) filter (where t.status = 'vanished'),
        array[]::text[]
      ) as vanished_strategies,
      coalesce(d0.investor_net_status in ('pending', 'missing'), false) as supply_partial_missing,
      coalesce(
        (
          select jsonb_agg(
            jsonb_build_object(
              'theme_code', ct.theme_code,
              'theme_name', ct.theme_name,
              'average_change_pct', ct.average_change_pct
            ) order by ct.average_change_pct desc, ct.theme_code asc
          )
          from public.candidate_themes ct
          where ct.candidate_id = c.candidate_id
            and ct.attempt_run_id = c.attempt_run_id
        ),
        '[]'::jsonb
      ) as themes
    from public.candidates c
    inner join public.candidate_tags t
      on t.candidate_id = c.candidate_id
      and t.attempt_run_id = c.attempt_run_id
      and t.status in ('active', 'vanished')
    left join lateral (
      select s.investor_net_status
      from public.supply_3day s
      where s.candidate_id = c.candidate_id
        and s.attempt_run_id = c.attempt_run_id
        and s.slot = 'D0'
      order by s.trading_day desc
      limit 1
    ) d0 on true
    where c.attempt_run_id = p_run_id
    group by c.candidate_id, c.attempt_run_id, c.ticker, c.name, d0.investor_net_status
  ) card
$$;

create or replace function public.get_top_tagged_candidates(p_run_id uuid)
returns jsonb
language sql
security definer
stable
set search_path = pg_catalog, public
as $$
  with published_complete_attempt as (
    select r.run_id, l.trading_day
    from public.runs r
    join public.logical_runs l on l.logical_run_key = r.logical_run_key
    where r.run_id = p_run_id
      and r.status = 'published'
      and l.current_complete_run_id = r.run_id
  )
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', top_candidate.candidate_id,
        'attempt_run_id', top_candidate.attempt_run_id,
        'ticker', top_candidate.ticker,
        'name', top_candidate.name,
        'trading_day', top_candidate.trading_day,
        'trading_value', top_candidate.trading_value,
        'change_pct', top_candidate.change_pct,
        'major_sector_name', top_candidate.major_sector_name,
        'themes', top_candidate.themes,
        'program_buy_value', top_candidate.program_buy_value
      )
      order by top_candidate.trading_value desc, top_candidate.ticker asc
    ),
    '[]'::jsonb
  )
  from (
    select
      c.candidate_id,
      c.attempt_run_id,
      c.ticker,
      c.name,
      c.trading_day,
      c.trading_value,
      c.major_sector_name,
      coalesce(
        (
          select jsonb_agg(
            jsonb_build_object(
              'theme_code', ct.theme_code,
              'theme_name', ct.theme_name,
              'average_change_pct', ct.average_change_pct
            ) order by ct.average_change_pct desc, ct.theme_code asc
          )
          from public.candidate_themes ct
          where ct.candidate_id = c.candidate_id
            and ct.attempt_run_id = c.attempt_run_id
        ),
        '[]'::jsonb
      ) as themes,
      coalesce(
        round(((current_bar.close - previous_bar.close) / nullif(previous_bar.close, 0)) * 100, 2),
        d0.change_pct
      ) as change_pct,
      case
        when d0.program_net is null then null
        else round((d0.program_net * coalesce(current_bar.close, d0.close)) / 100000000.0, 2)
      end as program_buy_value
    from published_complete_attempt p
    join public.candidates c
      on c.attempt_run_id = p.run_id
      and c.trading_day = p.trading_day
    left join lateral (
      select s.close, s.change_pct, s.program_net
      from public.supply_3day s
      where s.candidate_id = c.candidate_id
        and s.attempt_run_id = c.attempt_run_id
        and s.trading_day = c.trading_day
        and s.slot = 'D0'
        and s.investor_net_status = 'confirmed'
      order by s.collected_at desc
      limit 1
    ) d0 on true
    left join lateral (
      select d.close
      from public.daily_ohlcv d
      where d.ticker = c.ticker
        and d.trading_day = c.trading_day
        and d.adjusted is true
      limit 1
    ) current_bar on true
    left join lateral (
      select d.close
      from public.daily_ohlcv d
      where d.ticker = c.ticker
        and d.trading_day < c.trading_day
        and d.adjusted is true
      order by d.trading_day desc
      limit 1
    ) previous_bar on true
    order by c.trading_value desc, c.ticker asc
    limit 3
  ) top_candidate;
$$;

revoke execute on function public.get_today_candidate_cards(uuid) from public;
grant execute on function public.get_today_candidate_cards(uuid) to anon, authenticated, service_role;
revoke execute on function public.get_top_tagged_candidates(uuid) from public;
grant execute on function public.get_top_tagged_candidates(uuid) to anon, authenticated, service_role;

comment on function public.get_today_candidate_cards(uuid) is
  '후보 카드와 attempt-scoped 테마(t1532)를 함께 반환한다. 테마는 average_change_pct DESC, theme_code ASC로 정렬하며 비어 있으면 빈 배열이다.';
comment on function public.get_top_tagged_candidates(uuid) is
  'published complete snapshot의 거래대금 상위 3개 후보와 attempt-scoped t1532 테마를 반환한다. 테마는 average_change_pct DESC, theme_code ASC로 정렬한다.';

commit;
