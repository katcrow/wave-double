-- 전략 M 코드 리뷰 후속 패치(2026-10-20, review of 6d831d9 + connect_strategy_m):
-- 1) rebuild 재생 정렬을 내구성 있는 append_seq(단조 identity)로 전환한다.
--    ctid는 VACUUM FULL/CLUSTER/pg_repack으로 물리 재배치되면 바뀌므로 재생
--    동률 처리기로 쓰면 안 된다. append_seq는 삽입 순서를 단조로 보존한다.
-- 2) emit_open_command/track_outcome_day의 M 컨텍스트 가드에 errcode TS001을
--    부여하고, publish_attempt이 TS001만 종목 단위로 격리한다(하나의 손상된 M
--    태그가 close 발행 전체를 rollback하지 않게). MISSING_DAILY_OHLCV_CLOSE의
--    기존 격리 패턴을 따른다. 그 외 예외는 기존과 동일하게 전파된다.
-- 3) outcome_strategy_rules M 행의 trail_atr을 강제 정정한다(센티널 3필드가
--    일치하는데 trail_atr만 다르면 3.0으로 교정, 충돌 값이면 기존과 같이 중단).
begin;

-- ══ 1) outcome_events.append_seq: 단조 동률 처리기 ══
alter table public.outcome_events
  add column if not exists append_seq bigint generated always as identity;

comment on column public.outcome_events.append_seq is
  '삽입 단조 시퀀스. created_at 동률(같은 트랜잭션의 emit+청산) 이벤트의 재생 정렬용. ctid와 달리 VACUUM FULL/CLUSTER 후에도 안정적이다.';

-- rebuild_outcome_projection: ctid → append_seq.
do $migration$
declare
  function_def text;
  rewritten text;
begin
  select pg_get_functiondef(p.oid) into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public' and p.proname = 'rebuild_outcome_projection'
    and pg_get_function_identity_arguments(p.oid) = '';
  if function_def is null then
    raise exception 'REBUILD_OUTCOME_PROJECTION_FUNCTION_NOT_FOUND';
  end if;
  rewritten := replace(function_def,
    '      order by oe.created_at, oe.ctid',
    '      order by oe.created_at, oe.append_seq');
  if rewritten = function_def then
    raise exception 'append_seq event order rewrite made no change';
  end if;
  execute rewritten;
end
$migration$;

-- ══ 2) outcome_strategy_rules M trail_atr 정정 ══
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

select set_config('wave_double.strategy_rule_reason', '전략 M 리뷰 패치: trail_atr=3.0 정정', true);
select set_config('wave_double.strategy_rule_changed_by', 'migration:202610061600_strategy_m_review_patches', true);
update public.outcome_strategy_rules
set trail_atr = 3.0
where strategy = 'M' and trail_atr is distinct from 3.0;

-- ══ 3) M 컨텍스트 가드 errcode TS001 ══
do $migration$
declare
  item record;
  function_def text;
  rewritten text;
  before text;
begin
  for item in
    select p.oid, p.proname, pg_get_function_identity_arguments(p.oid) as identity_args
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and (
        (p.proname = 'emit_open_command' and pg_get_function_identity_arguments(p.oid) = 'p_logical_run_key text, p_ticker text, p_strategy text')
        or (p.proname = 'track_outcome_day' and pg_get_function_identity_arguments(p.oid) = 'p_logical_run_key text, p_outcome_id uuid, p_day date')
      )
  loop
    select pg_get_functiondef(item.oid) into function_def;
    rewritten := function_def;

    before := rewritten;
    rewritten := replace(rewritten,
      'raise exception using message = ''MISSING_STRATEGY_M_CONTEXT'';',
      'raise exception using message = ''MISSING_STRATEGY_M_CONTEXT'', errcode = ''TS001'';');
    before := rewritten;
    rewritten := replace(rewritten,
      'raise exception using message = ''INVALID_STRATEGY_M_CONTEXT'';',
      'raise exception using message = ''INVALID_STRATEGY_M_CONTEXT'', errcode = ''TS001'';');

    if rewritten = function_def then
      raise exception 'TS001 errcode rewrite made no change: % (%)', item.proname, item.identity_args;
    end if;
    execute rewritten;
  end loop;
end
$migration$;

-- ══ 4) publish_attempt: TS001만 종목 단위 격리 ══
do $migration$
declare
  function_def text;
  rewritten text;
begin
  select pg_get_functiondef(p.oid) into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public' and p.proname = 'publish_attempt'
    and pg_get_function_identity_arguments(p.oid) = 'p_run_id uuid, p_fence_token bigint, p_lease_token uuid';
  if function_def is null then
    raise exception 'PUBLISH_ATTEMPT_FUNCTION_NOT_FOUND';
  end if;

  rewritten := replace(function_def,
$old$      perform public.emit_open_command(r.logical_run_key, tag_row.ticker, tag_row.strategy);$old$,
$new$      begin
        perform public.emit_open_command(r.logical_run_key, tag_row.ticker, tag_row.strategy);
      exception when sqlstate 'TS001' then
        -- 전략 M 컨텍스트 누락/손상(TS001)만 종목 단위로 격리한다. 한 종목의 M
        -- 태그가 후보/태그/다른 종목 진입까지 포함한 close 발행 전체를
        -- rollback하지 않게, MISSING_DAILY_OHLCV_CLOSE와 같은 패턴으로 거른다.
        skipped_open_commands := skipped_open_commands || jsonb_build_array(jsonb_build_object(
          'ticker', tag_row.ticker, 'strategy', tag_row.strategy, 'reason', SQLERRM
        ));
      end;$new$);

  if rewritten = function_def then
    raise exception 'publish_attempt TS001 isolation rewrite made no change';
  end if;
  execute rewritten;
end
$migration$;

commit;
