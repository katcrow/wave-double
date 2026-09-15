-- 전략 G(양음돌파패턴)/H(240이평돌파+120이평우상향필터) 추가 (2026-09-15, story 없이 직접 적용).
-- docs/양음돌파패턴.md·docs/240이평돌파_120이평우상향필터.md 참고. 원 설계는 분할청산이었으나
-- 운영 청산 규약(AD-5, 단일 TP%/SL%, SL-우선 기본)에 맞춰 근사했다:
--   G: TP 5% / SL 5% / cutoff 20 (SL-우선)
--   H: TP 4% / SL 5% / cutoff 999999(sentinel=무제한, 익절우선 — 커널 StrategyHParams.tp_first=True는
--      Python 백테스트 재현용이며, SQL emit_open_command/publish_attempt는 전략별 tp_first 분기가 없어
--      실제 운영 판정은 다른 전략과 동일하게 SL-우선으로 이뤄진다. G/H 문서의 "익절우선" 최적 성과는
--      Python 백테스트 기준이며, 운영 판정 결과는 이와 달라질 수 있다.)
-- 202609071000_expand_candidate_tags_strategy_check_f.sql·202609080900_parameterize_outcome_strategy_rules_f.sql
-- (F 선례)와 동일한 사전조건 검증 -> drop/add constraint -> comment 갱신 패턴을 그대로 따르고,
-- 추가로 발견된 whitelist 함수(get_outcome_tracking_rows/get_outcome_metric_comparison(2종)/
-- set_outcome_strategy_rule)도 함께 확장한다.
begin;

-- 1) candidate_tags.strategy CHECK을 A-F -> A-H로 확장한다.
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'candidate_tags'
      and c.conname = 'candidate_tags_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''F''%'
      and pg_get_constraintdef(c.oid) not like '%''G''%'
  ) then
    raise exception 'candidate_tags_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check;

alter table public.candidate_tags
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'));

-- 2) outcome_strategy_rules.strategy CHECK을 A-F -> A-H로 확장한다.
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'outcome_strategy_rules'
      and c.conname = 'outcome_strategy_rules_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''F''%'
      and pg_get_constraintdef(c.oid) not like '%''G''%'
  ) then
    raise exception 'outcome_strategy_rules_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.outcome_strategy_rules
  drop constraint outcome_strategy_rules_strategy_check;

alter table public.outcome_strategy_rules
  add constraint outcome_strategy_rules_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'));

-- 3) G/H의 청산 파라미터 행을 추가한다.
do $$
begin
  if exists (
    select 1 from public.outcome_strategy_rules
    where strategy = 'G' and (tp_pct, sl_pct, cutoff_n) <> (5.0, 5.0, 20)
  ) then
    raise exception 'outcome_strategy_rules G row precondition failed: conflicting value already present';
  end if;
  if exists (
    select 1 from public.outcome_strategy_rules
    where strategy = 'H' and (tp_pct, sl_pct, cutoff_n) <> (4.0, 5.0, 999999)
  ) then
    raise exception 'outcome_strategy_rules H row precondition failed: conflicting value already present';
  end if;
end $$;

-- outcome_strategy_rules는 epic-6-retro-item-25 이후 사유 없는 DML을 거부한다
-- (require_outcome_strategy_rule_reason 트리거). set_outcome_strategy_rule()과 동일하게
-- 세션 설정을 켰다 끄고 직접 insert한다.
select set_config('wave_double.strategy_rule_reason', '전략 G/H 추가(docs/양음돌파패턴.md, docs/240이평돌파_120이평우상향필터.md)', true);
select set_config('wave_double.strategy_rule_changed_by', 'migration:202609151700_expand_strategy_gh', true);

insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
values ('G', 5.0, 5.0, 20), ('H', 4.0, 5.0, 999999)
on conflict (strategy) do nothing;

select set_config('wave_double.strategy_rule_reason', '', true);
select set_config('wave_double.strategy_rule_changed_by', '', true);

-- 4) outcome_events/candidate_outcome의 strategy CHECK을 A-F -> A-H로 확장한다.
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'outcome_events'
      and c.conname = 'outcome_events_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''F''%'
      and pg_get_constraintdef(c.oid) not like '%''G''%'
  ) then
    raise exception 'outcome_events_strategy_check old constraint precondition failed';
  end if;
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'candidate_outcome'
      and c.conname = 'candidate_outcome_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''F''%'
      and pg_get_constraintdef(c.oid) not like '%''G''%'
  ) then
    raise exception 'candidate_outcome_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.outcome_events
  drop constraint outcome_events_strategy_check,
  add constraint outcome_events_strategy_check check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'));

alter table public.candidate_outcome
  drop constraint candidate_outcome_strategy_check,
  add constraint candidate_outcome_strategy_check check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'));

-- 5) emit_open_command: 202609080900의 최신 본문(=현재 운영 본문, 사전 조회로 확인함)을 그대로
-- 복사하고 허용 전략 목록 한 줄만 H까지 확장한다.
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
  rule_row public.outcome_strategy_rules;
  v_close numeric;
  v_outcome_id uuid;
  v_entry_price numeric;
  v_existing_tp_pct numeric;
  v_existing_sl_pct numeric;
  v_existing_cutoff_n integer;
begin
  if p_strategy is null or p_strategy not in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then
    raise exception using message = 'INVALID_STRATEGY';
  end if;

  select * into logical_row
  from public.logical_runs
  where logical_run_key = p_logical_run_key;
  if not found or logical_row.batch_kind <> 'close' then
    raise exception using message = 'OPEN_COMMAND_REQUIRES_CLOSE_BATCH';
  end if;

  select close into v_close
  from public.daily_ohlcv
  where ticker = p_ticker and trading_day = logical_row.trading_day;
  if v_close is null then
    raise exception using message = 'MISSING_DAILY_OHLCV_CLOSE';
  end if;

  select * into existing_event
  from public.outcome_events
  where logical_run_key = p_logical_run_key
    and ticker = p_ticker
    and strategy = p_strategy
    and command_type = 'OPEN';

  if found then
    select outcome_id, entry_price, tp_pct, sl_pct, cutoff_n
      into v_outcome_id, v_entry_price, v_existing_tp_pct, v_existing_sl_pct, v_existing_cutoff_n
    from public.candidate_outcome
    where ticker = p_ticker
      and strategy = p_strategy
      and entry_date = logical_row.trading_day;
    if not found then
      raise exception using message = 'OUTCOME_PROJECTION_MISSING';
    end if;

    return jsonb_build_object(
      'replayed', true, 'skipped', false,
      'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
      'entry_date', logical_row.trading_day, 'entry_price', v_entry_price,
      'tp_pct', v_existing_tp_pct, 'sl_pct', v_existing_sl_pct,
      'cutoff_n', v_existing_cutoff_n
    );
  end if;

  select * into existing_open
  from public.candidate_outcome
  where ticker = p_ticker
    and strategy = p_strategy
    and status in ('OPEN', 'SUSPENDED', 'DELISTED')
  for update;

  if found and existing_open.status = 'SUSPENDED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_TRACKED_SUSPENDED',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price, 'tp_pct', existing_open.tp_pct,
      'sl_pct', existing_open.sl_pct, 'cutoff_n', existing_open.cutoff_n
    );
  end if;
  if found and existing_open.status = 'DELISTED' then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_DELISTED',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price, 'tp_pct', existing_open.tp_pct,
      'sl_pct', existing_open.sl_pct, 'cutoff_n', existing_open.cutoff_n
    );
  end if;
  if found and existing_open.entry_date <> logical_row.trading_day then
    return jsonb_build_object(
      'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
      'outcome_id', existing_open.outcome_id, 'entry_date', existing_open.entry_date,
      'entry_price', existing_open.entry_price, 'tp_pct', existing_open.tp_pct,
      'sl_pct', existing_open.sl_pct, 'cutoff_n', existing_open.cutoff_n
    );
  end if;

  select * into rule_row
  from public.outcome_strategy_rules
  where strategy = p_strategy
  for share;
  if not found then
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values (
    p_ticker, p_strategy, 'OPEN', p_logical_run_key,
    jsonb_build_object(
      'entry_date', logical_row.trading_day, 'entry_price', v_close,
      'tp_pct', rule_row.tp_pct, 'sl_pct', rule_row.sl_pct,
      'cutoff_n', rule_row.cutoff_n
    )
  )
  on conflict (logical_run_key, ticker, strategy, command_type) do nothing
  returning * into new_event;

  if found then
    begin
      insert into public.candidate_outcome(
        ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n
      )
      values (
        p_ticker, p_strategy, logical_row.trading_day, v_close, 'OPEN',
        rule_row.tp_pct, rule_row.sl_pct, rule_row.cutoff_n
      )
      returning outcome_id into v_outcome_id;

      return jsonb_build_object(
        'replayed', false, 'skipped', false,
        'event_id', new_event.event_id, 'outcome_id', v_outcome_id,
        'entry_date', logical_row.trading_day, 'entry_price', v_close,
        'tp_pct', rule_row.tp_pct, 'sl_pct', rule_row.sl_pct,
        'cutoff_n', rule_row.cutoff_n
      );
    exception when unique_violation then
      select * into existing_open
      from public.candidate_outcome
      where ticker = p_ticker and strategy = p_strategy and status = 'OPEN'
      for update;

      if found then
        return jsonb_build_object(
          'replayed', false, 'skipped', true, 'reason', 'ALREADY_OPEN',
          'event_id', new_event.event_id, 'outcome_id', existing_open.outcome_id,
          'entry_date', existing_open.entry_date, 'entry_price', existing_open.entry_price,
          'tp_pct', existing_open.tp_pct, 'sl_pct', existing_open.sl_pct,
          'cutoff_n', existing_open.cutoff_n
        );
      end if;

      if exists (
        select 1 from public.candidate_outcome
        where ticker = p_ticker and strategy = p_strategy
          and entry_date = logical_row.trading_day
      ) then
        raise exception using message = 'OUTCOME_PROJECTION_CONFLICT';
      end if;
      raise;
    end;
  end if;

  select * into existing_event
  from public.outcome_events
  where logical_run_key = p_logical_run_key
    and ticker = p_ticker
    and strategy = p_strategy
    and command_type = 'OPEN';
  if not found then
    raise exception using message = 'OUTCOME_EVENT_MISSING';
  end if;

  select outcome_id, entry_price, tp_pct, sl_pct, cutoff_n
    into v_outcome_id, v_entry_price, v_existing_tp_pct, v_existing_sl_pct, v_existing_cutoff_n
  from public.candidate_outcome
  where ticker = p_ticker and strategy = p_strategy
    and entry_date = logical_row.trading_day;
  if not found then
    raise exception using message = 'OUTCOME_PROJECTION_MISSING';
  end if;

  return jsonb_build_object(
    'replayed', true, 'skipped', false,
    'event_id', existing_event.event_id, 'outcome_id', v_outcome_id,
    'entry_date', logical_row.trading_day, 'entry_price', v_entry_price,
    'tp_pct', v_existing_tp_pct, 'sl_pct', v_existing_sl_pct,
    'cutoff_n', v_existing_cutoff_n
  );
end;
$$;

-- 6) guard_outcome_strategy_snapshot: 현재 운영 본문(사전 조회로 확인함)을 그대로 복사하고
-- 두 곳만 H까지 확장한다: 미정 전략 통과 목록, cutoff_n 비교 대상 전략 목록.
create or replace function public.guard_outcome_strategy_snapshot()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  rule_row public.outcome_strategy_rules;
begin
  if coalesce(current_setting('wave_double.outcome_rule_override_allowed', true), 'off') = 'on' then
    return new;
  end if;

  if tg_op = 'UPDATE'
     and new.strategy is not distinct from old.strategy
     and new.tp_pct is not distinct from old.tp_pct
     and new.sl_pct is not distinct from old.sl_pct
     and new.cutoff_n is not distinct from old.cutoff_n then
    return new;
  end if;

  select * into rule_row
  from public.outcome_strategy_rules
  where strategy = new.strategy
  for share;

  -- 미정 전략은 candidate_outcome_strategy_check가 표준 CHECK 오류를 내도록 한다.
  if not found then
    if new.strategy not in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then
      return new;
    end if;
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  if new.tp_pct is distinct from rule_row.tp_pct
     or new.sl_pct is distinct from rule_row.sl_pct
     or (new.strategy in ('D', 'E', 'F', 'G', 'H') and new.cutoff_n is distinct from rule_row.cutoff_n) then
    raise exception using message = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH';
  end if;
  return new;
end;
$$;

-- 7) set_outcome_strategy_rule: 현재 운영 본문(사전 조회로 확인함)을 그대로 복사하고
-- 허용 전략 목록 한 줄만 H까지 확장한다.
create or replace function public.set_outcome_strategy_rule(
  p_strategy text,
  p_tp_pct numeric,
  p_sl_pct numeric,
  p_cutoff_n integer,
  p_reason text,
  p_changed_by text
) returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  previous public.outcome_strategy_rules;
  updated public.outcome_strategy_rules;
begin
  if p_strategy is null or p_strategy not in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then
    raise exception using message = 'INVALID_STRATEGY';
  end if;
  if p_reason is null or length(btrim(p_reason)) = 0 then
    raise exception using message = 'STRATEGY_RULE_REASON_REQUIRED';
  end if;
  if p_changed_by is null or length(btrim(p_changed_by)) = 0 then
    raise exception using message = 'STRATEGY_RULE_CHANGED_BY_REQUIRED';
  end if;
  if p_tp_pct is null or p_tp_pct <= 0
     or p_tp_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
    raise exception using message = 'INVALID_TP_PCT';
  end if;
  if p_sl_pct is null or p_sl_pct <= 0
     or p_sl_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
    raise exception using message = 'INVALID_SL_PCT';
  end if;
  if p_cutoff_n is null or p_cutoff_n <= 0 then
    raise exception using message = 'INVALID_CUTOFF_N';
  end if;

  select * into previous from public.outcome_strategy_rules where strategy = p_strategy for update;

  perform set_config('wave_double.strategy_rule_reason', btrim(p_reason), true);
  perform set_config('wave_double.strategy_rule_changed_by', btrim(p_changed_by), true);

  insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
  values (p_strategy, p_tp_pct, p_sl_pct, p_cutoff_n)
  on conflict (strategy) do update
    set tp_pct = excluded.tp_pct,
        sl_pct = excluded.sl_pct,
        cutoff_n = excluded.cutoff_n
  returning * into updated;

  perform set_config('wave_double.strategy_rule_reason', '', true);
  perform set_config('wave_double.strategy_rule_changed_by', '', true);

  return jsonb_build_object(
    'strategy', updated.strategy,
    'operation', case when previous.strategy is null then 'INSERT' else 'UPDATE' end,
    'previous', case
      when previous.strategy is null then null
      else jsonb_build_object('tp_pct', previous.tp_pct, 'sl_pct', previous.sl_pct, 'cutoff_n', previous.cutoff_n)
    end,
    'current', jsonb_build_object('tp_pct', updated.tp_pct, 'sl_pct', updated.sl_pct, 'cutoff_n', updated.cutoff_n),
    'unchanged', previous.strategy is not null
      and previous.tp_pct = updated.tp_pct
      and previous.sl_pct = updated.sl_pct
      and previous.cutoff_n = updated.cutoff_n
  );
end;
$$;

-- 8) get_outcome_tracking_rows: p_strategy whitelist를 A-H로 확장한다 (그 외 로직 불변, 사전 조회로 확인함).
create or replace function public.get_outcome_tracking_rows(
  p_status text default null,
  p_strategy text default null,
  p_ticker text default null,
  p_limit integer default 500
) returns jsonb
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
  with normalized as (
    select
      case when p_status in ('TP', 'SL', 'TIMEOUT', 'OPEN', 'SUSPENDED', 'DELISTED') then p_status end as status,
      case when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then p_strategy end as strategy,
      nullif(replace(replace(replace(btrim(p_ticker), E'\\', E'\\\\'), '%', E'\\%'), '_', E'\\_'), '') as ticker,
      least(greatest(coalesce(p_limit, 500), 1), 500) as row_limit
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.entry_date desc, rows.outcome_id desc),
    '[]'::jsonb
  )
  from (
    select
      co.outcome_id,
      co.ticker,
      co.strategy,
      co.entry_date,
      co.status,
      co.exit_date,
      co.return_pct
    from public.candidate_outcome co
    cross join normalized n
    where (n.status is null or co.status = n.status)
      and (n.strategy is null or co.strategy = n.strategy)
      and (n.ticker is null or co.ticker ilike '%' || n.ticker || '%' escape E'\\')
    order by co.entry_date desc, co.outcome_id desc
    limit (select row_limit from normalized)
  ) rows;
$$;

-- 9) get_outcome_metric_comparison(text): p_strategy whitelist를 A-H로 확장한다 (그 외 불변).
create or replace function public.get_outcome_metric_comparison(
  p_strategy text default null
) returns jsonb
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
  with normalized as (
    select case
      when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then p_strategy
      else null
    end as strategy_filter
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.strategy is not null, rows.strategy),
    '[]'::jsonb
  )
  from (
    select v.*
    from public.candidate_outcome_cutoff_bias_notice v
    cross join normalized n
    where n.strategy_filter is null or v.strategy = n.strategy_filter
  ) rows;
$$;

-- 10) get_outcome_metric_comparison(text, text): p_strategy whitelist를 A-H로 확장한다 (그 외 불변,
-- expected/cutoff_bias 상수는 A/B/C 전용이라 그대로 유지 — G/H는 해당 열이 null로 나온다).
create or replace function public.get_outcome_metric_comparison(
  p_strategy text,
  p_source text
) returns jsonb
language sql
stable
security definer
set search_path = pg_catalog, public
as $$
  with normalized as (
    select
      case
        when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H') then p_strategy
        else null
      end as strategy_filter,
      case
        when p_source in ('t1859', 't1852', 't1856') then p_source
        else null
      end as source_filter
  ),
  resolved as (
    select co.strategy, co.status, co.return_pct, src.source
    from public.candidate_outcome co
    left join lateral (
      select lr.canonical_success_run_id, lr.trading_day
      from public.logical_runs lr
      where lr.batch_kind = 'close'
        and lr.trading_day = co.entry_date
        and lr.canonical_success_run_id is not null
    ) run on true
    left join lateral (
      select cl.candidate_id, cl.attempt_run_id
      from public.candidates cl
      where cl.trading_day = run.trading_day
        and cl.ticker = co.ticker
        and cl.attempt_run_id = run.canonical_success_run_id
    ) cand on true
    left join lateral (
      select cs.source
      from public.candidate_source_contrib cs
      where cs.candidate_id = cand.candidate_id
        and cs.attempt_run_id = cand.attempt_run_id
      order by cs.contribution_weight desc,
        case cs.source when 't1859' then 0 when 't1852' then 1 else 2 end
      limit 1
    ) src on true
  ),
  scoped as (
    select r.*
    from resolved r
    cross join normalized n
    where n.source_filter is null or r.source = n.source_filter
  ),
  base as (
    select
      strategy,
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')) as total_settled,
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as wins,
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0) as losses,
      count(*) filter (where status = 'OPEN') as open_count,
      count(*) filter (where status = 'SUSPENDED') as suspended_count,
      count(*) filter (where status = 'DELISTED') as delisted_count,
      sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as gross_win,
      abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)) as gross_loss
    from scoped
    group by rollup(strategy)
  ),
  expected as (
    select * from (values
      ('A', 0.6871::numeric, 2.0540::numeric),
      ('B', 0.6895::numeric, 2.0770::numeric),
      ('C', 0.6600::numeric, 1.8159::numeric)
    ) as e(strategy, expected_win_rate, expected_profit_factor)
  ),
  ci as (
    select
      b.*,
      case when b.total_settled >= 30 then round(b.wins::numeric / nullif(b.total_settled, 0), 4) end as win_rate,
      case when b.total_settled >= 30 then round(b.gross_win / nullif(b.gross_loss, 0), 4) end as profit_factor,
      30 as sample_gate_min_required,
      (b.total_settled >= 30) as sample_gate_passed,
      case when b.total_settled < 30 then '표본 부족 (' || b.total_settled || '/30)' end as sample_gate_label,
      case when b.total_settled >= 30 then
        1.959963985 / (1 + (1.959963985 ^ 2) / b.total_settled)
      end as z_denom_factor,
      case when b.total_settled >= 30 then
        (round(b.wins::numeric / nullif(b.total_settled, 0), 4) + (1.959963985 ^ 2) / (2 * b.total_settled))
          / (1 + (1.959963985 ^ 2) / b.total_settled)
      end as center,
      case when b.total_settled >= 30 then
        sqrt(
          ((round(b.wins::numeric / nullif(b.total_settled, 0), 4)
            * (1 - round(b.wins::numeric / nullif(b.total_settled, 0), 4)))
            + (1.959963985 ^ 2) / (4 * b.total_settled))
          / b.total_settled
        )
      end as spread,
      e.expected_win_rate,
      e.expected_profit_factor
    from base b
    left join expected e on e.strategy = b.strategy
  ),
  threshold_values as (
    select
      c.*,
      case when c.sample_gate_passed then round(c.center - c.z_denom_factor * c.spread, 4) end as ci_lower,
      case when c.sample_gate_passed then round(c.center + c.z_denom_factor * c.spread, 4) end as ci_upper
    from ci c
  ),
  timeout_counts as (
    select strategy, count(*) filter (where status = 'TIMEOUT')::integer as timeout_count
    from scoped
    group by rollup(strategy)
  ),
  output_rows as (
    select
      t.strategy,
      t.total_settled,
      t.wins,
      t.losses,
      t.open_count,
      t.suspended_count,
      t.delisted_count,
      t.gross_win,
      t.gross_loss,
      t.win_rate,
      t.profit_factor,
      t.sample_gate_min_required,
      t.sample_gate_passed,
      t.sample_gate_label,
      case when t.sample_gate_passed then t.ci_lower end as ci_lower,
      case when t.sample_gate_passed then t.ci_upper end as ci_upper,
      case when t.sample_gate_passed then t.expected_win_rate end as expected_win_rate,
      case when t.sample_gate_passed and t.expected_win_rate is not null then
        t.expected_win_rate between t.ci_lower and t.ci_upper
      end as expected_in_ci,
      case when t.sample_gate_passed then t.expected_profit_factor end as expected_profit_factor,
      case when t.sample_gate_passed and t.expected_win_rate is not null then 0.10::numeric end as win_rate_threshold_pp,
      case when t.sample_gate_passed and t.expected_profit_factor is not null then 0.25::numeric end as profit_factor_threshold_ratio,
      case when t.sample_gate_passed and t.expected_win_rate is not null and t.win_rate is not null
        then abs(t.win_rate - t.expected_win_rate) > 0.10
      end as win_rate_threshold_breached,
      case when t.sample_gate_passed and t.expected_profit_factor is not null and t.profit_factor is not null
        then abs(t.profit_factor - t.expected_profit_factor) / t.expected_profit_factor > 0.25
      end as profit_factor_threshold_breached,
      coalesce(tc.timeout_count, 0)::integer as timeout_count,
      case when t.strategy in ('A', 'B', 'C') then 30 end as cutoff_bias_sample_size,
      case t.strategy when 'B' then 0.0037::numeric when 'A' then 0.0000::numeric when 'C' then 0.0000::numeric end as cutoff_bias_timeout_rate,
      case t.strategy when 'B' then 0.0125::numeric when 'A' then 0.0000::numeric when 'C' then 0.0000::numeric end as cutoff_bias_profit_factor_delta,
      case t.strategy when 'B' then 'TIMEOUT 0.37% / PF차 +0.0125' when 'A' then 'TIMEOUT 0% / PF차 ±0' when 'C' then 'TIMEOUT 0% / PF차 ±0' end as cutoff_bias_label
    from threshold_values t
    left join timeout_counts tc on tc.strategy is not distinct from t.strategy
  ),
  final_rows as (
    select
      o.*,
      case when o.win_rate_threshold_breached or o.profit_factor_threshold_breached then true
        when o.win_rate_threshold_breached is null and o.profit_factor_threshold_breached is null then null
        else false
      end as threshold_warning
    from output_rows o
    cross join normalized n
    where n.strategy_filter is null or o.strategy = n.strategy_filter
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.strategy is not null, rows.strategy),
    '[]'::jsonb
  )
  from final_rows rows;
$$;

-- 11) revoke/grant는 기존과 동일 유지(service_role 전용, CREATE OR REPLACE는 권한을 보존하지만
-- 명시적으로 재확인해 드리프트를 막는다).
revoke execute on function public.emit_open_command(text, text, text) from public, anon, authenticated;
grant execute on function public.emit_open_command(text, text, text) to service_role;
revoke execute on function public.guard_outcome_strategy_snapshot() from public, anon, authenticated;
revoke execute on function public.set_outcome_strategy_rule(text, numeric, numeric, integer, text, text) from public, anon, authenticated;
grant execute on function public.set_outcome_strategy_rule(text, numeric, numeric, integer, text, text) to service_role;

-- 12) comment 갱신.
comment on table public.candidate_tags is
  '전략 A/B/C/D/E/F/G/H 시그널 태깅 이력(2026-09-15 G/H 추가). attempt-scoped(AD-19), candidates에 합성키 FK.';

comment on table public.outcome_strategy_rules is
  '전략별(A-H) TP%/SL%/최대보유일 lookup. A/B/C는 3/3/30, D는 3/5/20, E는 2/5/30, F는 3/4/999999, G는 5/5/20, H는 4/5/999999(sentinel=무제한, publish_attempt의 v_traded_days >= cutoff_n 비교 재사용). G/H는 원래 분할청산 설계(docs/양음돌파패턴.md, docs/240이평돌파_120이평우상향필터.md)를 단일청산으로 근사한 값이다.';

comment on function public.emit_open_command(text, text, text) is
  'A-H 전략의 outcome_strategy_rules(tp_pct/sl_pct/cutoff_n)를 OPEN event payload와 candidate_outcome에 원자적으로 스냅샷한다. 그 외 idempotency·SUSPENDED·DELISTED 경계는 기존 계약을 그대로 유지한다.';

comment on function public.guard_outcome_strategy_snapshot() is
  'direct candidate_outcome INSERT/UPDATE snapshot 값은 outcome_strategy_rules와 일치해야 한다(G/H 포함). G/H도 D/E/F와 동일하게 cutoff_n까지 스냅샷 비교 대상이다. correction/rebuild만 내부 override로 우회한다.';

commit;
