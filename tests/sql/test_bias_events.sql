-- Story 5.1 bias_events append-only 스키마 계약 fixture.
-- 모든 검증은 rollback으로 감싸 운영/CI DB에 잔여 데이터를 남기지 않는다.
begin;

create temp table _bias_events_fixture_results (scenario text primary key, status text not null) on commit drop;

-- 1) 카탈로그 계약: 컬럼 집합/타입, PK, source·카운트 컬럼 배치, FK, RLS.
do $$
declare
  v_columns text[];
  v_types text[];
  v_security boolean;
begin
  -- bias_events는 회차 메타만 갖는다(카운트도 source도 두지 않는다).
  select array_agg(column_name::text order by ordinal_position), array_agg(data_type::text order by ordinal_position)
    into v_columns, v_types
  from information_schema.columns
  where table_schema = 'public' and table_name = 'bias_events';
  if v_columns <> array[
    'bias_event_id','trading_day','logical_run_key','calculation_meta','created_at'
  ] then
    raise exception 'bias_events columns mismatch: %', v_columns;
  end if;
  if v_types <> array['uuid','date','text','jsonb','timestamp with time zone'] then
    raise exception 'bias_events column types mismatch: %', v_types;
  end if;
  if 'source' = any (v_columns) then
    raise exception 'bias_events must not carry a source column (AD-21)';
  end if;
  if exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'bias_events'
      and column_name in (
        'candidate_pop_signal_count','backtest_universe_signal_count',
        'intersection_count','diff_count','missed_opportunity_count'
      )
  ) then
    raise exception 'bias_events must not carry count columns; counts live in bias_event_by_source';
  end if;

  select array_agg(column_name::text order by ordinal_position), array_agg(data_type::text order by ordinal_position)
    into v_columns, v_types
  from information_schema.columns
  where table_schema = 'public' and table_name = 'bias_event_by_source';
  if v_columns <> array[
    'bias_event_id','source',
    'candidate_pop_signal_count','backtest_universe_signal_count','intersection_count',
    'diff_count','missed_opportunity_count','created_at'
  ] then
    raise exception 'bias_event_by_source columns mismatch: %', v_columns;
  end if;
  if v_types <> array[
    'uuid','text','integer','integer','integer','integer','integer','timestamp with time zone'
  ] then
    raise exception 'bias_event_by_source column types mismatch: %', v_types;
  end if;
  -- 계산 메타는 회차 단위 사실이므로 source 분해 행에는 두지 않는다.
  if 'calculation_meta' = any (v_columns) then
    raise exception 'bias_event_by_source must not carry calculation_meta';
  end if;

  -- PK 계약: 회차 메타는 bias_event_id, source 분해는 (bias_event_id, source).
  if (
    select pg_get_constraintdef(c.oid)
    from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'bias_events' and c.contype = 'p'
  ) <> 'PRIMARY KEY (bias_event_id)' then
    raise exception 'bias_events primary key is not bias_event_id';
  end if;
  if (
    select pg_get_constraintdef(c.oid)
    from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'bias_event_by_source' and c.contype = 'p'
  ) <> 'PRIMARY KEY (bias_event_id, source)' then
    raise exception 'bias_event_by_source primary key is not (bias_event_id, source)';
  end if;

  -- logical_run_key FK와 source 분해의 회차 FK.
  if not exists (
    select 1 from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'bias_events' and c.contype = 'f'
      and pg_get_constraintdef(c.oid) like '%logical_run_key%logical_runs%'
  ) then raise exception 'bias_events logical_run_key FK is missing'; end if;
  if not exists (
    select 1 from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'bias_event_by_source' and c.contype = 'f'
      and pg_get_constraintdef(c.oid) like '%bias_event_id%bias_events%'
  ) then raise exception 'bias_event_by_source bias_event_id FK is missing'; end if;

  select c.relrowsecurity into v_security
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public' and c.relname = 'bias_events';
  if v_security is not true then raise exception 'bias_events RLS is not enabled'; end if;
  select c.relrowsecurity into v_security
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
  where n.nspname = 'public' and c.relname = 'bias_event_by_source';
  if v_security is not true then raise exception 'bias_event_by_source RLS is not enabled'; end if;

  -- canonical view 쌍이 존재해야 한다.
  if not exists (
    select 1 from information_schema.views
    where table_schema = 'public' and table_name = 'bias_events_canonical'
  ) then raise exception 'bias_events_canonical view is missing'; end if;
  if not exists (
    select 1 from information_schema.views
    where table_schema = 'public' and table_name = 'bias_event_by_source_canonical'
  ) then raise exception 'bias_event_by_source_canonical view is missing'; end if;
  -- canonical 메타 view도 카운트를 노출하지 않는다.
  select array_agg(column_name::text order by ordinal_position) into v_columns
  from information_schema.columns
  where table_schema = 'public' and table_name = 'bias_events_canonical';
  if v_columns <> array['bias_event_id','trading_day','logical_run_key','calculation_meta','created_at'] then
    raise exception 'bias_events_canonical columns mismatch: %', v_columns;
  end if;
  select array_agg(column_name::text order by ordinal_position) into v_columns
  from information_schema.columns
  where table_schema = 'public' and table_name = 'bias_event_by_source_canonical';
  if v_columns <> array[
    'bias_event_id','trading_day','logical_run_key','source',
    'candidate_pop_signal_count','backtest_universe_signal_count','intersection_count',
    'diff_count','missed_opportunity_count','contributing_candidate_count','created_at'
  ] then
    raise exception 'bias_event_by_source_canonical columns mismatch: %', v_columns;
  end if;
end $$;
insert into _bias_events_fixture_results values ('catalog_contract', 'pass');

-- 2) source 도메인이 candidate_source_contrib과 동일한 집합인지 (drift 차단).
do $$
declare
  v_bias text[];
  v_contrib text[];
begin
  select array(
    select distinct m[1] from (
      select regexp_matches(pg_get_constraintdef(c.oid), '''([a-z0-9]+)''', 'g') as m
      from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
      where n.nspname = 'public' and t.relname = 'bias_event_by_source' and c.contype = 'c'
        and pg_get_constraintdef(c.oid) like '%source%'
    ) s order by 1
  ) into v_bias;
  select array(
    select distinct m[1] from (
      select regexp_matches(pg_get_constraintdef(c.oid), '''([a-z0-9]+)''', 'g') as m
      from pg_constraint c join pg_class t on t.oid = c.conrelid join pg_namespace n on n.oid = t.relnamespace
      where n.nspname = 'public' and t.relname = 'candidate_source_contrib' and c.contype = 'c'
        and pg_get_constraintdef(c.oid) like '%source%'
    ) s order by 1
  ) into v_contrib;
  if v_contrib <> array['t1852','t1856','t1859'] then
    raise exception 'candidate_source_contrib source domain changed: %', v_contrib;
  end if;
  if v_bias <> v_contrib then
    raise exception 'bias source domain % drifted from candidate_source_contrib %', v_bias, v_contrib;
  end if;
end $$;
insert into _bias_events_fixture_results values ('source_domain_matches_contrib', 'pass');

-- 3) HAPPY_PATH / RECALC_APPEND / EMPTY_SOURCE / 임의 회차 조회 / canonical 최신 선택.
do $$
declare
  v_first uuid;
  v_second uuid;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-08-03', date '2099-08-03', 'close')
  on conflict (logical_run_key) do nothing;

  insert into public.bias_events(trading_day, logical_run_key, calculation_meta, created_at)
  values (
    date '2099-08-03', 'close:2099-08-03',
    jsonb_build_object('strategies', jsonb_build_array('A','B','C')),
    timestamptz '2099-08-03 09:00:00+00'
  ) returning bias_event_id into v_first;

  insert into public.bias_event_by_source(
    bias_event_id, source,
    candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
    diff_count, missed_opportunity_count
  ) values
    (v_first, 't1859', 7, 8, 5, 2, 4),
    (v_first, 't1852', 3, 8, 2, 1, 6),
    -- EMPTY_SOURCE: 기여 없는 폴백 source의 null-safe 0 행도 유효한 관측치다.
    (v_first, 't1856', 0, 0, 0, 0, 0);

  if (select count(*) from public.bias_event_by_source where bias_event_id = v_first) <> 3 then
    raise exception 'source decomposition rows were not stored';
  end if;
  if (select bias_event_id from public.bias_events_canonical where trading_day = date '2099-08-03') <> v_first then
    raise exception 'canonical view did not return the only event';
  end if;
  if (select count(*) from public.bias_event_by_source_canonical where trading_day = date '2099-08-03') <> 3 then
    raise exception 'canonical source view did not return three source rows';
  end if;
  if (
    select missed_opportunity_count from public.bias_event_by_source_canonical
    where trading_day = date '2099-08-03' and source = 't1856'
  ) <> 0 then
    raise exception 'zero-count fallback source row is not exposed as 0';
  end if;
  if (
    select candidate_pop_signal_count from public.bias_event_by_source_canonical
    where trading_day = date '2099-08-03' and source = 't1859'
  ) <> 7 then
    raise exception 'canonical source view did not expose candidate_pop_signal_count';
  end if;
  -- canonical close가 아직 발행되지 않은 회차는 미수집(NULL)으로 노출되어야 한다
  -- (실제 0과 구분한다 — 기여 수치는 아래 contribution_authority 블록에서 검증한다).
  if exists (
    select 1 from public.bias_event_by_source_canonical
    where trading_day = date '2099-08-03' and contributing_candidate_count is not null
  ) then
    raise exception 'unpublished canonical close must expose contributing_candidate_count as NULL';
  end if;

  -- RECALC_APPEND: 같은 거래일에 두 번째 회차를 append한다.
  insert into public.bias_events(trading_day, logical_run_key, created_at)
  values (date '2099-08-03', 'close:2099-08-03', timestamptz '2099-08-03 10:00:00+00')
  returning bias_event_id into v_second;
  insert into public.bias_event_by_source(
    bias_event_id, source,
    candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
    diff_count, missed_opportunity_count
  ) values
    (v_second, 't1859', 8, 8, 6, 2, 2),
    (v_second, 't1852', 4, 8, 3, 1, 5),
    (v_second, 't1856', 0, 0, 0, 0, 0);

  if (select count(*) from public.bias_events_canonical where trading_day = date '2099-08-03') <> 1 then
    raise exception 'canonical view returned more than one round for a trading day';
  end if;
  if (select bias_event_id from public.bias_events_canonical where trading_day = date '2099-08-03') <> v_second then
    raise exception 'canonical view did not select the latest round';
  end if;
  if (
    select count(distinct bias_event_id) from public.bias_event_by_source_canonical
    where trading_day = date '2099-08-03'
  ) <> 1 then
    raise exception 'canonical source view mixed rounds';
  end if;

  -- 과거 회차는 원본 테이블에 그대로 남아 임의 bias_event_id로 조회된다.
  if (select count(*) from public.bias_events where bias_event_id = v_first) <> 1 then
    raise exception 'the previous round was not preserved';
  end if;
  if (select count(*) from public.bias_event_by_source where bias_event_id = v_first) <> 3 then
    raise exception 'the previous round source rows were not preserved';
  end if;
  if (
    select intersection_count from public.bias_event_by_source
    where bias_event_id = v_first and source = 't1859'
  ) <> 5 then
    raise exception 'the previous round source counts were altered';
  end if;

  -- 동시각 tie는 bias_event_id 내림차순으로 결정론적으로 해소된다.
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-08-04', date '2099-08-04', 'close')
  on conflict (logical_run_key) do nothing;
  insert into public.bias_events(bias_event_id, trading_day, logical_run_key, created_at)
  values
    ('00000000-0000-4000-8000-000000000001'::uuid, date '2099-08-04', 'close:2099-08-04', timestamptz '2099-08-04 09:00:00+00'),
    ('00000000-0000-4000-8000-000000000002'::uuid, date '2099-08-04', 'close:2099-08-04', timestamptz '2099-08-04 09:00:00+00');
  if (select bias_event_id from public.bias_events_canonical where trading_day = date '2099-08-04')
     <> '00000000-0000-4000-8000-000000000002'::uuid then
    raise exception 'canonical tie-break is not deterministic';
  end if;
end $$;
insert into _bias_events_fixture_results values ('append_and_canonical_contract', 'pass');

-- 4) MUTATION_REJECTED: UPDATE/DELETE/TRUNCATE가 두 테이블 모두에서 거부된다.
do $$
declare
  v_event uuid;
  v_caught boolean;
begin
  select bias_event_id into v_event from public.bias_events where trading_day = date '2099-08-03'
  order by created_at limit 1;

  v_caught := false;
  begin
    update public.bias_events set trading_day = date '2099-08-04' where bias_event_id = v_event;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'bias_events UPDATE was accepted'; end if;

  v_caught := false;
  begin
    delete from public.bias_events where bias_event_id = v_event;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'bias_events DELETE was accepted'; end if;

  v_caught := false;
  begin
    update public.bias_event_by_source set diff_count = 0 where bias_event_id = v_event;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'bias_event_by_source UPDATE was accepted'; end if;

  v_caught := false;
  begin
    delete from public.bias_event_by_source where bias_event_id = v_event;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'bias_event_by_source DELETE was accepted'; end if;

  v_caught := false;
  begin
    truncate public.bias_events cascade;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'bias_events TRUNCATE was accepted'; end if;

  v_caught := false;
  begin
    truncate public.bias_event_by_source;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'bias_event_by_source TRUNCATE was accepted'; end if;
end $$;
insert into _bias_events_fixture_results values ('append_only_rejection', 'pass');

-- 5) BAD_COUNTS / DAY_MISMATCH / calculation_meta 형식.
do $$
declare
  v_event uuid;
  v_caught boolean;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-08-05', date '2099-08-05', 'close')
  on conflict (logical_run_key) do nothing;

  -- calculation_meta는 JSON object만 허용한다.
  v_caught := false;
  begin
    insert into public.bias_events(trading_day, logical_run_key, calculation_meta)
    values (date '2099-08-05', 'close:2099-08-05', '[]'::jsonb);
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'non-object calculation_meta was accepted'; end if;

  -- DAY_MISMATCH: logical_run_key의 거래일과 다른 trading_day는 거부한다.
  v_caught := false;
  begin
    insert into public.bias_events(trading_day, logical_run_key)
    values (date '2099-08-06', 'close:2099-08-05');
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'trading_day mismatch was accepted'; end if;

  -- 편향 계산은 종가 배치 전용이므로 premarket/intraday 계보는 거부된다.
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('premarket:2099-08-05', date '2099-08-05', 'premarket'),
         ('intraday:2099-08-05:10:00', date '2099-08-05', 'intraday')
  on conflict (logical_run_key) do nothing;
  v_caught := false;
  begin
    insert into public.bias_events(trading_day, logical_run_key)
    values (date '2099-08-05', 'premarket:2099-08-05');
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'premarket lineage was accepted'; end if;
  v_caught := false;
  begin
    insert into public.bias_events(trading_day, logical_run_key)
    values (date '2099-08-05', 'intraday:2099-08-05:10:00');
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'intraday lineage was accepted'; end if;

  -- diff_count의 하한(모집단 전용 차집합) 위반 거부.
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values (
      -- 2099-08-04 tie-break 회차는 source 행이 없어 PK 충돌 없이 check만 검증한다.
      '00000000-0000-4000-8000-000000000001'::uuid,
      't1856', 10, 10, 1, 0, 9
    );
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'diff_count below the population-only lower bound was accepted'; end if;

  -- 알 수 없는 bias_event_id는 FK로 거부된다.
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values ('00000000-0000-4000-8000-0000000000ff'::uuid, 't1859', 0, 0, 0, 0, 0);
  exception when foreign_key_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'unknown bias_event_id was accepted'; end if;

  -- 내용이 있는 calculation_meta object는 허용된다(거부만 테스트하지 않는다).
  insert into public.bias_events(trading_day, logical_run_key, calculation_meta)
  values (
    date '2099-08-05', 'close:2099-08-05',
    jsonb_build_object('universe_fixture', 'kospi200-104', 'truncated', 3)
  );
  if not exists (
    select 1 from public.bias_events
    where trading_day = date '2099-08-05'
      and calculation_meta->>'universe_fixture' = 'kospi200-104'
  ) then raise exception 'populated calculation_meta object was not stored'; end if;

  -- 선언한 두 index가 실제로 존재한다.
  if not exists (
    select 1 from pg_indexes where schemaname = 'public'
      and indexname = 'bias_events_trading_day_latest_idx'
  ) then raise exception 'bias_events_trading_day_latest_idx is missing'; end if;
  if not exists (
    select 1 from pg_indexes where schemaname = 'public'
      and indexname = 'bias_events_logical_run_key_idx'
  ) then raise exception 'bias_events_logical_run_key_idx is missing'; end if;

  insert into public.bias_events(trading_day, logical_run_key)
  values (date '2099-08-05', 'close:2099-08-05')
  returning bias_event_id into v_event;

  -- 음수 카운트 거부.
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values (v_event, 't1859', -1, 1, 0, 0, 1);
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'negative count was accepted'; end if;

  -- intersection_count가 두 집합 크기를 초과하면 거부.
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values (v_event, 't1859', 2, 3, 3, 0, 0);
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'oversized intersection_count was accepted'; end if;

  -- diff_count는 해당 source 모집단 시그널 수를 넘지 못한다(Story 5.3 산식과 무관한 약한 불변식).
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values (v_event, 't1859', 2, 2, 2, 3, 0);
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'diff_count above the population was accepted'; end if;

  -- missed_opportunity_count는 유니버스 전용 차집합보다 작을 수 없다.
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values (v_event, 't1859', 5, 5, 1, 0, 3);
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'understated missed_opportunity_count was accepted'; end if;

  -- source 도메인 밖의 값은 거부한다.
  v_caught := false;
  begin
    insert into public.bias_event_by_source(
      bias_event_id, source,
      candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
      diff_count, missed_opportunity_count
    ) values (v_event, 'unknown_source', 0, 0, 0, 0, 0);
  exception when sqlstate '23514' then v_caught := true;
  end;
  if not v_caught then raise exception 'unknown source value was accepted'; end if;
end $$;
insert into _bias_events_fixture_results values ('count_and_lineage_invariants', 'pass');

-- 6) 기여 권위(AD-21): contributing_candidate_count가 canonical close attempt의
--    candidate_source_contrib에서 실제 값으로 산출되는지. 이 블록이 없으면 join을
--    where false로 바꿔도 fixture가 전부 통과한다(모든 값이 coalesce 기본값 0).
do $$
declare
  v_run uuid := '00000000-0000-4000-8000-00000000aa01'::uuid;
  v_c1 uuid := '00000000-0000-4000-8000-00000000bb01'::uuid;
  v_c2 uuid := '00000000-0000-4000-8000-00000000bb02'::uuid;
  v_event uuid;
  v_t1859 integer;
  v_t1856 integer;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-08-10', date '2099-08-10', 'close')
  on conflict (logical_run_key) do nothing;

  insert into public.runs(
    run_id, logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status
  ) values (
    v_run, 'close:2099-08-10', 1, 1, now() + interval '1 hour', 'schedule', 'published'
  );

  -- 후보 2건이 t1859로 기여하고 t1856으로는 아무도 기여하지 않는다.
  insert into public.candidates(candidate_id, attempt_run_id, ticker, trading_day, trading_value)
  values (v_c1, v_run, '005930', date '2099-08-10', 1000),
         (v_c2, v_run, '000660', date '2099-08-10', 900);
  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
  values (v_c1, v_run, 't1859', 1), (v_c2, v_run, 't1859', 1);

  -- 이 attempt를 그 논리 실행의 canonical close attempt로 만든다.
  update public.logical_runs
  set canonical_success_run_id = v_run, current_complete_run_id = v_run, published_at = now()
  where logical_run_key = 'close:2099-08-10';

  insert into public.bias_events(trading_day, logical_run_key)
  values (date '2099-08-10', 'close:2099-08-10')
  returning bias_event_id into v_event;
  insert into public.bias_event_by_source(
    bias_event_id, source,
    candidate_pop_signal_count, backtest_universe_signal_count, intersection_count,
    diff_count, missed_opportunity_count
  ) values
    (v_event, 't1859', 2, 5, 2, 0, 3),
    (v_event, 't1856', 0, 0, 0, 0, 0);

  select contributing_candidate_count into v_t1859
  from public.bias_event_by_source_canonical
  where trading_day = date '2099-08-10' and source = 't1859';
  if not found then raise exception 'contribution row for t1859 is missing'; end if;
  if v_t1859 is distinct from 2 then
    raise exception 'contributing_candidate_count for t1859 must be 2, got %', v_t1859;
  end if;

  select contributing_candidate_count into v_t1856
  from public.bias_event_by_source_canonical
  where trading_day = date '2099-08-10' and source = 't1856';
  if not found then raise exception 'contribution row for t1856 is missing'; end if;
  if v_t1856 is distinct from 0 then
    raise exception 'a source with no contribution must be 0 (not NULL), got %', v_t1856;
  end if;

  -- 기여 집계는 거래일이 아니라 그 회차의 logical_run_key에 연결되어야 한다.
  -- canonical attempt를 떼면 같은 거래일이라도 미수집(NULL)이 된다.
  update public.logical_runs set canonical_success_run_id = null
  where logical_run_key = 'close:2099-08-10';
  select contributing_candidate_count into v_t1859
  from public.bias_event_by_source_canonical
  where trading_day = date '2099-08-10' and source = 't1859';
  if v_t1859 is not null then
    raise exception 'without a canonical close attempt the count must be NULL, got %', v_t1859;
  end if;
end $$;
insert into _bias_events_fixture_results values ('contribution_authority', 'pass');

-- 7) BROWSER_READ: 두 테이블·두 view의 SELECT와 트리거 함수 EXECUTE가 브라우저 역할에 없다.
do $$
begin
  if exists (
    select 1 from information_schema.role_table_grants
    where table_schema = 'public'
      and table_name in ('bias_events', 'bias_event_by_source', 'bias_events_canonical', 'bias_event_by_source_canonical')
      and grantee in ('PUBLIC', 'anon', 'authenticated')
      and privilege_type = 'SELECT'
  ) then raise exception 'bias tables/views must not be readable by browser roles'; end if;
  -- 내부 트리거 함수는 RPC 표면이 아니다(202609051900 선례).
  if exists (
    select 1 from information_schema.role_routine_grants
    where routine_schema = 'public'
      and routine_name = 'enforce_bias_event_trading_day'
      and grantee in ('PUBLIC', 'anon', 'authenticated')
      and privilege_type = 'EXECUTE'
  ) then raise exception 'enforce_bias_event_trading_day must not be executable by browser roles'; end if;
  -- daily_ohlcv/outcome 선례와 동일하게 RLS enable + 정책 0개 catalog 검사로 확인한다.
  -- 로컬 CI의 vanilla Postgres에는 anon/authenticated 역할이 없어 SET ROLE로 실제 거부를
  -- 재현할 수 없고, RLS가 있고 정책이 없으면 non-bypassrls 역할은 어떤 행도 볼 수 없다.
  if exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename in ('bias_events', 'bias_event_by_source')
  ) then raise exception 'bias tables must not carry permissive policies'; end if;
end $$;
insert into _bias_events_fixture_results values ('browser_read_blocked', 'pass');

do $$
begin
  if (select count(*) from _bias_events_fixture_results) <> 7
     or exists (select 1 from _bias_events_fixture_results where status <> 'pass') then
    raise exception 'bias events fixture did not produce exactly seven pass rows';
  end if;
end $$;
select scenario, status from _bias_events_fixture_results order by scenario;

rollback;
