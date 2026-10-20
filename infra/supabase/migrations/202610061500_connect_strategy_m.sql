-- 전략 M(다바스 박스)을 운영 태깅/outcome/성과 검증 경로에 연결한다.
-- M의 실제 청산 규칙(진입 시점 박스 하단 고정 손절 + ATR 트레일링)을 outcome 장부에
-- 반영하기 위해 candidate_outcome과 outcome_strategy_rules에 컬럼을 확장한다.
-- 기존 outcome 장부 값은 변경하지 않으며, 다음 정상 close 배치부터 M을 생성한다.
begin;

-- 1) candidate_tags는 운영 수동 전략 I와 함께 다바스 M을 보존한다.
alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check,
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L', 'M'));

alter table public.outcome_events
  drop constraint outcome_events_strategy_check,
  add constraint outcome_events_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M'));

alter table public.candidate_outcome
  drop constraint candidate_outcome_strategy_check,
  add constraint candidate_outcome_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M'));

alter table public.outcome_strategy_rules
  drop constraint outcome_strategy_rules_strategy_check,
  add constraint outcome_strategy_rules_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'M'));

-- 2) M은 TP/SL 정률 대신 진입 시점 박스 하단과 ATR 트레일링으로 청산한다.
--    trail_atr는 lookup에 두고, 진입 시점 스냅샷은 candidate_outcome에 고정한다.
do $$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'outcome_strategy_rules' and column_name = 'trail_atr'
  ) then
    alter table public.outcome_strategy_rules add column trail_atr numeric;
  end if;
  if not exists (
    select 1 from pg_constraint c
    join pg_class t on t.oid = c.conrelid
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'outcome_strategy_rules' and c.conname = 'outcome_strategy_rules_trail_atr_check'
  ) then
    alter table public.outcome_strategy_rules add constraint outcome_strategy_rules_trail_atr_check
      check (trail_atr is null or (trail_atr > 0 and trail_atr <> all (array['NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric])));
  end if;
end $$;

do $$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'candidate_outcome' and column_name = 'entry_floor'
  ) then
    alter table public.candidate_outcome add column entry_floor numeric;
  end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'candidate_outcome' and column_name = 'entry_atr'
  ) then
    alter table public.candidate_outcome add column entry_atr numeric;
  end if;
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'candidate_outcome' and column_name = 'trail_atr'
  ) then
    alter table public.candidate_outcome add column trail_atr numeric;
  end if;
  if not exists (
    select 1 from pg_constraint c
    join pg_class t on t.oid = c.conrelid
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'candidate_outcome' and c.conname = 'candidate_outcome_entry_floor_check'
  ) then
    alter table public.candidate_outcome add constraint candidate_outcome_entry_floor_check
      check (entry_floor is null or (entry_floor > 0 and entry_floor <> all (array['NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric])));
  end if;
  if not exists (
    select 1 from pg_constraint c
    join pg_class t on t.oid = c.conrelid
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'candidate_outcome' and c.conname = 'candidate_outcome_entry_atr_check'
  ) then
    alter table public.candidate_outcome add constraint candidate_outcome_entry_atr_check
      check (entry_atr is null or (entry_atr > 0 and entry_atr <> all (array['NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric])));
  end if;
  if not exists (
    select 1 from pg_constraint c
    join pg_class t on t.oid = c.conrelid
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'candidate_outcome' and c.conname = 'candidate_outcome_trail_atr_check'
  ) then
    alter table public.candidate_outcome add constraint candidate_outcome_trail_atr_check
      check (trail_atr is null or (trail_atr > 0 and trail_atr <> all (array['NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric])));
  end if;
end $$;

-- 3) M의 운영 청산 규칙: 정률 TP/SL을 쓰지 않으므로 sentinel을 유지하고 trail_atr=3.0을 둔다.
do $$
begin
  if exists (
    select 1 from public.outcome_strategy_rules
    where strategy = 'M'
      and (tp_pct, sl_pct, cutoff_n) is distinct from (999999, 99, 999999)
  ) then
    raise exception 'outcome_strategy_rules M row precondition failed: conflicting value already present';
  end if;
end $$;

select set_config('wave_double.strategy_rule_reason', '전략 M 운영 연결: 다바스 박스', true);
select set_config('wave_double.strategy_rule_changed_by', 'migration:202610061500_connect_strategy_m', true);
insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n, trail_atr)
values ('M', 999999, 99, 999999, 3.0)
on conflict (strategy) do nothing;

-- 4) 현재 운영 함수 본문에서 허용 전략 목록을 M까지 확장한다.
do $migration$
declare
  item record;
  function_def text;
  rewritten text;
  old_ah text := '(''A'', ''B'', ''C'', ''D'', ''E'', ''F'', ''G'', ''H'')';
  new_ahlm text := '(''A'', ''B'', ''C'', ''D'', ''E'', ''F'', ''G'', ''H'', ''L'', ''M'')';
  old_ahl text := '(''A'', ''B'', ''C'', ''D'', ''E'', ''F'', ''G'', ''H'', ''L'')';
  old_dhl text := '(''D'', ''E'', ''F'', ''G'', ''H'', ''L'')';
  new_dhlm text := '(''D'', ''E'', ''F'', ''G'', ''H'', ''L'', ''M'')';
begin
  for item in
    select p.oid, p.proname, pg_get_function_identity_arguments(p.oid) as identity_args
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and (
        (p.proname = 'emit_open_command' and pg_get_function_identity_arguments(p.oid) = 'p_logical_run_key text, p_ticker text, p_strategy text')
        or p.proname = 'guard_outcome_strategy_snapshot'
        or p.proname = 'get_outcome_tracking_rows'
        or p.proname = 'get_outcome_metric_comparison'
        or p.proname = 'set_outcome_strategy_rule'
      )
  loop
    select pg_get_functiondef(item.oid) into function_def;
    rewritten := replace(function_def, old_ahl, new_ahlm);
    rewritten := replace(rewritten, old_dhl, new_dhlm);
    rewritten := replace(rewritten, old_ah, new_ahlm);

    if item.proname = 'get_outcome_metric_comparison'
       and item.identity_args = 'p_strategy text, p_source text' then
      rewritten := replace(
        rewritten,
        '(''L'', 0.7574::numeric, 1.1185::numeric)',
        '(''L'', 0.7574::numeric, 1.1185::numeric),
      (''M'', 0.3590::numeric, 2.2300::numeric)'
      );
    end if;

    if rewritten = function_def then
      raise exception 'strategy M function rewrite made no change: % (%)', item.proname, item.identity_args;
    end if;
    execute rewritten;
  end loop;
end
$migration$;

-- 5) emit_open_command: 전략 M은 태깅 단계가 남긴 박스 하단/ATR 컨텍스트를 OPEN payload와
--    candidate_outcome 스냅샷에 고정한다.
do $migration$
declare
  function_def text;
  rewritten text;
  before text;
begin
  select pg_get_functiondef(p.oid) into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public' and p.proname = 'emit_open_command'
    and pg_get_function_identity_arguments(p.oid) = 'p_logical_run_key text, p_ticker text, p_strategy text';
  if function_def is null then
    raise exception 'EMIT_OPEN_COMMAND_FUNCTION_NOT_FOUND';
  end if;
  rewritten := function_def;

  before := rewritten;
  rewritten := replace(rewritten,
$old$  v_existing_cutoff_n integer;
begin$old$,
$new$  v_existing_cutoff_n integer;
  v_payload jsonb;
  v_m_context jsonb;
  v_entry_floor numeric;
  v_entry_atr numeric;
  v_trail_atr numeric;
begin$new$);
  if rewritten = before then raise exception 'STRATEGY_M_EMIT_DECLARE_REWRITE_FAILED'; end if;

  before := rewritten;
  rewritten := replace(rewritten,
$old$  if not found then
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
  )$old$,
$new$  if not found then
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  if p_strategy = 'M' then
    -- 전략 M은 진입 시점 박스 하단(entry_floor)과 ATR 트레일링(trail_atr x entry_atr)을
    -- 청산 기준으로 쓰므로, 태깅 단계가 남긴 전략 M 컨텍스트를 OPEN에 고정한다.
    select t.params_meta->'strategy_m_context'
      into v_m_context
    from public.candidate_tags t
    join public.candidates c
      on c.candidate_id = t.candidate_id
     and c.attempt_run_id = t.attempt_run_id
    join public.logical_runs lr
      on lr.logical_run_key = p_logical_run_key
    where t.attempt_run_id = lr.active_attempt_run_id
      and t.strategy = 'M'
      and t.status = 'active'
      and c.ticker = p_ticker
    limit 1;

    if v_m_context is null then
      raise exception using message = 'MISSING_STRATEGY_M_CONTEXT';
    end if;

    begin
      v_entry_floor := (v_m_context->>'entry_floor')::numeric;
      v_entry_atr := (v_m_context->>'entry_atr')::numeric;
      v_trail_atr := coalesce((v_m_context->>'trail_atr')::numeric, rule_row.trail_atr);
    exception when others then
      raise exception using message = 'INVALID_STRATEGY_M_CONTEXT';
    end;

    if v_entry_floor is null or v_entry_atr is null or v_trail_atr is null
       or v_entry_floor <= 0 or v_entry_atr <= 0 or v_trail_atr <= 0
       or v_entry_floor in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
       or v_entry_atr in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
       or v_trail_atr in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
      raise exception using message = 'INVALID_STRATEGY_M_CONTEXT';
    end if;
  end if;

  v_payload := jsonb_build_object(
    'entry_date', logical_row.trading_day, 'entry_price', v_close,
    'tp_pct', rule_row.tp_pct, 'sl_pct', rule_row.sl_pct,
    'cutoff_n', rule_row.cutoff_n
  );
  if p_strategy = 'M' then
    v_payload := v_payload || jsonb_build_object(
      'entry_floor', v_entry_floor, 'entry_atr', v_entry_atr, 'trail_atr', v_trail_atr
    );
  end if;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values (p_ticker, p_strategy, 'OPEN', p_logical_run_key, v_payload)$new$);
  if rewritten = before then raise exception 'STRATEGY_M_EMIT_OPEN_REWRITE_FAILED'; end if;

  before := rewritten;
  rewritten := replace(rewritten,
$old$      insert into public.candidate_outcome(
        ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n
      )
      values (
        p_ticker, p_strategy, logical_row.trading_day, v_close, 'OPEN',
        rule_row.tp_pct, rule_row.sl_pct, rule_row.cutoff_n
      )$old$,
$new$      insert into public.candidate_outcome(
        ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n,
        entry_floor, entry_atr, trail_atr
      )
      values (
        p_ticker, p_strategy, logical_row.trading_day, v_close, 'OPEN',
        rule_row.tp_pct, rule_row.sl_pct, rule_row.cutoff_n,
        v_entry_floor, v_entry_atr, v_trail_atr
      )$new$);
  if rewritten = before then raise exception 'STRATEGY_M_EMIT_SNAPSHOT_REWRITE_FAILED'; end if;

  execute rewritten;
end
$migration$;

-- 6) track_outcome_day: 전략 M은 박스 하단과 ATR 트레일링 중 먼저 닿는 선에서 SL로 청산한다.
do $migration$
declare
  function_def text;
  rewritten text;
  before text;
begin
  select pg_get_functiondef(p.oid) into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public' and p.proname = 'track_outcome_day'
    and pg_get_function_identity_arguments(p.oid) = 'p_logical_run_key text, p_outcome_id uuid, p_day date';
  if function_def is null then
    raise exception 'TRACK_OUTCOME_DAY_FUNCTION_NOT_FOUND';
  end if;
  rewritten := function_def;

  before := rewritten;
  rewritten := replace(rewritten,
$old$  v_tp_sl jsonb := null;
begin$old$,
$new$  v_tp_sl jsonb := null;
  v_trail_high numeric;
  v_trail_line numeric;
begin$new$);
  if rewritten = before then raise exception 'STRATEGY_M_TRACK_DECLARE_REWRITE_FAILED'; end if;

  before := rewritten;
  rewritten := replace(rewritten,
$old$      if o.strategy = 'L' then$old$,
$new$      if o.strategy = 'M' then
        -- 진입 시점 박스 하단(entry_floor) 고정 손절과 ATR 트레일링 중 먼저 닿는 선으로 청산한다.
        if o.entry_floor is null or o.entry_atr is null or o.trail_atr is null then
          raise exception using message = 'MISSING_STRATEGY_M_CONTEXT';
        end if;
        select greatest(coalesce(max(oh.high), 0), o.entry_price)
          into v_trail_high
        from public.outcome_observations oh
        where oh.outcome_id = o.outcome_id
          and oh.result_code = 'OK'
          and oh.evaluation_trading_day >= o.entry_date
          and oh.evaluation_trading_day < p_day;
        v_trail_line := v_trail_high - o.trail_atr * o.entry_atr;
        if v_obs_low <= o.entry_floor or v_obs_low <= v_trail_line then
          v_tpsl_status := 'SL';
          v_exit_price := case
            when v_obs_low <= o.entry_floor and v_obs_low <= v_trail_line
              then greatest(o.entry_floor, v_trail_line)
            when v_obs_low <= o.entry_floor then o.entry_floor
            else v_trail_line
          end;
          v_return_pct := (v_exit_price / o.entry_price - 1.0) * 100.0 - 0.1;
        end if;
      elsif o.strategy = 'L' then$new$);
  if rewritten = before then raise exception 'STRATEGY_M_TRACK_BRANCH_REWRITE_FAILED'; end if;

  execute rewritten;
end
$migration$;

-- 7) rebuild_outcome_projection: OPEN payload에 고정한 M 컨텍스트를 재생한다.
do $migration$
declare
  function_def text;
  rewritten text;
  before text;
begin
  select pg_get_functiondef(p.oid) into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public' and p.proname = 'rebuild_outcome_projection'
    and pg_get_function_identity_arguments(p.oid) = '';
  if function_def is null then
    raise exception 'REBUILD_OUTCOME_PROJECTION_FUNCTION_NOT_FOUND';
  end if;
  rewritten := function_def;

  before := rewritten;
  rewritten := replace(rewritten,
$old$  v_holding_days integer;
begin$old$,
$new$  v_holding_days integer;
  v_entry_floor numeric;
  v_entry_atr numeric;
  v_trail_atr numeric;
begin$new$);
  if rewritten = before then raise exception 'STRATEGY_M_REBUILD_DECLARE_REWRITE_FAILED'; end if;

  before := rewritten;
  rewritten := replace(rewritten,
$old$        insert into public.candidate_outcome(
          ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n
        )
        values (
          v_cur.ticker, v_cur.strategy, v_entry_date, v_entry_price, 'OPEN',
          v_tp_pct, v_sl_pct, v_cutoff_n
        )
        on conflict (ticker, strategy, entry_date) do update set
          entry_price = excluded.entry_price,
          status = 'OPEN',
          exit_date = null,
          exit_price = null,
          return_pct = null,
          tp_pct = excluded.tp_pct,
          sl_pct = excluded.sl_pct,
          cutoff_n = excluded.cutoff_n,
          holding_days = 0;$old$,
$new$        if v_cur.strategy = 'M' then
          if not (v_event.payload ? 'entry_floor'
                  and v_event.payload ? 'entry_atr'
                  and v_event.payload ? 'trail_atr') then
            raise exception 'REBUILD: OPEN payload missing strategy M context (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          v_raw := v_event.payload->>'entry_floor';
          if v_raw is null or btrim(v_raw) = '' then
            raise exception 'REBUILD: OPEN payload invalid entry_floor (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          begin v_entry_floor := v_raw::numeric;
          exception when others then
            raise exception 'REBUILD: OPEN payload invalid entry_floor (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end;
          v_raw := v_event.payload->>'entry_atr';
          if v_raw is null or btrim(v_raw) = '' then
            raise exception 'REBUILD: OPEN payload invalid entry_atr (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          begin v_entry_atr := v_raw::numeric;
          exception when others then
            raise exception 'REBUILD: OPEN payload invalid entry_atr (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end;
          v_raw := v_event.payload->>'trail_atr';
          if v_raw is null or btrim(v_raw) = '' then
            raise exception 'REBUILD: OPEN payload invalid trail_atr (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
          begin v_trail_atr := v_raw::numeric;
          exception when others then
            raise exception 'REBUILD: OPEN payload invalid trail_atr (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end;
          if v_entry_floor <= 0 or v_entry_atr <= 0 or v_trail_atr <= 0
             or v_entry_floor in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
             or v_entry_atr in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
             or v_trail_atr in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
            raise exception 'REBUILD: OPEN payload invalid strategy M context (ticker=%, strategy=%)',
              v_cur.ticker, v_cur.strategy;
          end if;
        else
          v_entry_floor := null;
          v_entry_atr := null;
          v_trail_atr := null;
        end if;

        insert into public.candidate_outcome(
          ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n,
          entry_floor, entry_atr, trail_atr
        )
        values (
          v_cur.ticker, v_cur.strategy, v_entry_date, v_entry_price, 'OPEN',
          v_tp_pct, v_sl_pct, v_cutoff_n,
          v_entry_floor, v_entry_atr, v_trail_atr
        )
        on conflict (ticker, strategy, entry_date) do update set
          entry_price = excluded.entry_price,
          status = 'OPEN',
          exit_date = null,
          exit_price = null,
          return_pct = null,
          tp_pct = excluded.tp_pct,
          sl_pct = excluded.sl_pct,
          cutoff_n = excluded.cutoff_n,
          entry_floor = excluded.entry_floor,
          entry_atr = excluded.entry_atr,
          trail_atr = excluded.trail_atr,
          holding_days = 0;$new$);
  if rewritten = before then raise exception 'STRATEGY_M_REBUILD_OPEN_REWRITE_FAILED'; end if;

  -- 같은 트랜잭션의 emit+track 이벤트는 now()가 동결돼 created_at이 모두 같다.
  -- 그때 event_id(uuid) 동률 처리는 무작위라 OPEN보다 SL이 먼저 재생될 수 있다
  -- (publish_attempt가 한 TX에서 emit과 청산 판정을 모두 실행하므로 운영에서도
  -- 발생 가능한 일이다). append-only 장부의 ctid는 삽입 물리 순서이므로 동률
  -- 처리기로 쓰면 OPEN → 종결 순서가 항상 보존된다.
  before := rewritten;
  rewritten := replace(rewritten,
$old$      order by oe.created_at, oe.event_id$old$,
$new$      order by oe.created_at, oe.ctid$new$);
  if rewritten = before then raise exception 'STRATEGY_M_REBUILD_EVENT_ORDER_REWRITE_FAILED'; end if;

  execute rewritten;
end
$migration$;

-- 8) 운영 성과 페이지의 백테스트 기대치에 문서 기준 M 값을 등록한다.
create or replace view public.candidate_outcome_win_rate_pf_ci_gated as
with base as (
  select * from public.candidate_outcome_win_rate_pf_by_strategy_gated
),
expected as (
  select * from (values
    ('A', 0.6871::numeric),
    ('B', 0.6895::numeric),
    ('C', 0.6600::numeric),
    ('L', 0.7574::numeric),
    ('M', 0.3590::numeric)
  ) as e(strategy, expected_win_rate)
),
ci as (
  select
    b.*,
    e.expected_win_rate as expected_win_rate_raw,
    case when b.sample_gate_passed then
      1.959963985 / (1 + (1.959963985 ^ 2) / b.total_settled)
    end as z_denom_factor,
    case when b.sample_gate_passed then
      (b.win_rate + (1.959963985 ^ 2) / (2 * b.total_settled))
        / (1 + (1.959963985 ^ 2) / b.total_settled)
    end as center,
    case when b.sample_gate_passed then
      sqrt(
        (b.win_rate * (1 - b.win_rate) + (1.959963985 ^ 2) / (4 * b.total_settled))
        / b.total_settled
      )
    end as spread
  from base b
  left join expected e on e.strategy = b.strategy
)
select
  strategy, total_settled, wins, losses, open_count, suspended_count, delisted_count,
  gross_win, gross_loss, win_rate, profit_factor, sample_gate_min_required,
  sample_gate_passed, sample_gate_label,
  round(center - z_denom_factor * spread, 4) as ci_lower,
  round(center + z_denom_factor * spread, 4) as ci_upper,
  case when sample_gate_passed then expected_win_rate_raw end as expected_win_rate,
  case when sample_gate_passed and expected_win_rate_raw is not null then
    expected_win_rate_raw between
      round(center - z_denom_factor * spread, 4) and round(center + z_denom_factor * spread, 4)
  end as expected_in_ci
from ci;

create or replace view public.candidate_outcome_win_rate_pf_threshold_gated as
with expected as (
  select * from (values
    ('A', 2.0540::numeric),
    ('B', 2.0770::numeric),
    ('C', 1.8159::numeric),
    ('L', 1.1185::numeric),
    ('M', 2.2300::numeric)
  ) as e(strategy, expected_profit_factor)
),
base as (
  select ci.*, case when ci.sample_gate_passed then e.expected_profit_factor end as expected_profit_factor
  from public.candidate_outcome_win_rate_pf_ci_gated ci
  left join expected e on e.strategy = ci.strategy
),
thresholds as (
  select b.*,
    case when b.expected_profit_factor is not null then 0.10::numeric end as win_rate_threshold_pp,
    case when b.expected_profit_factor is not null then 0.25::numeric end as profit_factor_threshold_ratio,
    case when b.sample_gate_passed and b.expected_win_rate is not null and b.win_rate is not null
      then abs(b.win_rate - b.expected_win_rate) > 0.10 end as win_rate_threshold_breached,
    case when b.sample_gate_passed and b.expected_profit_factor is not null and b.profit_factor is not null
      then abs(b.profit_factor - b.expected_profit_factor) / b.expected_profit_factor > 0.25 end as profit_factor_threshold_breached
  from base b
)
select strategy, total_settled, wins, losses, open_count, suspended_count, delisted_count,
  gross_win, gross_loss, win_rate, profit_factor, sample_gate_min_required,
  sample_gate_passed, sample_gate_label, ci_lower, ci_upper, expected_win_rate,
  expected_in_ci, expected_profit_factor, win_rate_threshold_pp,
  profit_factor_threshold_ratio, win_rate_threshold_breached,
  profit_factor_threshold_breached,
  case when win_rate_threshold_breached or profit_factor_threshold_breached then true
    when win_rate_threshold_breached is null and profit_factor_threshold_breached is null then null
    else false end as threshold_warning
from thresholds;

comment on table public.candidate_tags is
  '전략 A/B/C/D/E/F/G/H/I/L/M 시그널 태깅 이력. I는 운영 수동 확인, L은 VWAP 상향 회복, M은 다바스 박스 전략이다.';
comment on table public.outcome_strategy_rules is
  '전략별 TP/SL/최대보유일 lookup. L은 TP-first와 수익 종가 청산, M은 박스 하단 고정 손절과 ATR 트레일링(trail_atr)을 쓴다.';
comment on column public.candidate_outcome.entry_floor is
  '전략 M 진입 시점 박스 하단(고정 손절 기준가). 다른 전략은 null이다.';
comment on column public.candidate_outcome.entry_atr is
  '전략 M 진입 시점 ATR(14). 트레일링 폭 계산에 쓴다. 다른 전략은 null이다.';
comment on column public.candidate_outcome.trail_atr is
  '전략 M 진입 시점 트레일링 배수(기본 3.0). 다른 전략은 null이다.';
comment on function public.emit_open_command(text, text, text) is
  'close publish에서 OPEN 이벤트를 만들고 candidate_outcome 스냅샷을 고정한다. 전략 M은 박스 하단/ATR 컨텍스트를 함께 고정한다.';
comment on function public.track_outcome_day(text, uuid, date) is
  '관측 거래일별 청산 판정. 전략 M은 박스 하단 고정 손절과 ATR 트레일링 중 먼저 닿는 선에서 SL로 청산한다.';
comment on function public.rebuild_outcome_projection() is
  'outcome_events를 재생해 candidate_outcome을 재구축한다. 전략 M은 OPEN payload의 박스 하단/ATR 컨텍스트를 복원한다.';

commit;
