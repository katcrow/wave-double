-- 전략 M(다바스 박스) outcome 라이프사이클 + 성과 기대치 fixture.
-- 태깅 컨텍스트 → emit 스냅샷(트레일링 fallback 포함) → track 박스 하단/ATR 트레일링 판정
-- (우선순위·퇴행 유지·누락 가드) → rebuild 재생 → 성과 뷰/RPC 기대치까지 한 파일에서 고정한다.
-- 모든 변경은 rollback으로 되돌린다.

begin;

-- ══ 1) 운영 규칙 lookup 계약: M은 sentinel TP/SL + trail_atr=3.0 ══
do $$
declare
  v_rule record;
begin
  select tp_pct, sl_pct, cutoff_n, trail_atr into v_rule
  from public.outcome_strategy_rules
  where strategy = 'M';
  if not found then
    raise exception 'outcome_strategy_rules에 전략 M 행이 없다(마이그레이션 202610061500 미적용?)';
  end if;
  if v_rule.tp_pct is distinct from 999999
     or v_rule.sl_pct is distinct from 99
     or v_rule.cutoff_n is distinct from 999999
     or v_rule.trail_atr is distinct from 3.0 then
    raise exception 'outcome_strategy_rules M 계약 불일치: %', to_jsonb(v_rule);
  end if;
end $$;

-- ══ 2) close 배치 태깅 하니스: 후보 4종 + M 컨텍스트 태그 ══
do $$
declare
  v_started jsonb;
  v_run_id uuid;
  v_fence bigint;
  v_lease uuid;
  v_c1 uuid := gen_random_uuid();
  v_c2 uuid := gen_random_uuid();
  v_c3 uuid := gen_random_uuid();
  v_c4 uuid := gen_random_uuid();
begin
  v_started := public.start_attempt('close:2099-09-01', date '2099-09-01', 'close', 'manual', 300);
  v_run_id := (v_started->>'run_id')::uuid;
  v_fence := (v_started->>'fence_token')::bigint;
  v_lease := (v_started->>'lease_token')::uuid;

  perform public.write_stage(v_run_id, 'candidates', v_fence, v_lease, 'pending', 'running');
  perform public.write_candidates(
    v_run_id, v_fence, v_lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', v_c1, 'ticker', 'ZZM01', 'name', '다바스M1', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', v_c2, 'ticker', 'ZZM02', 'name', '다바스M2', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', v_c3, 'ticker', 'ZZM03', 'name', '다바스M3', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', v_c4, 'ticker', 'ZZM04', 'name', '다바스M4', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('u', 64), 'original_count', 4, 'candidate_count', 4,
      'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(v_run_id, 'candidates', v_fence, v_lease, 'running', 'success');

  -- c1: 풀 컨텍스트 / c2: trail_atr 누락(rule 3.0으로 fallback 검증) /
  -- c3: 컨텍스트 없음(MISSING) / c4: 캐스트 불가(INVALID)
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status, params_meta)
  values
    (v_c1, v_run_id, 'M', date '2099-09-01', 'active',
      jsonb_build_object('strategy_m_context', jsonb_build_object(
        'entry_floor', 93, 'entry_atr', 2, 'trail_atr', 3, 'mode', 'combined'))),
    (v_c2, v_run_id, 'M', date '2099-09-01', 'active',
      jsonb_build_object('strategy_m_context', jsonb_build_object(
        'entry_floor', 95, 'entry_atr', 2, 'mode', 'combined'))),
    (v_c3, v_run_id, 'M', date '2099-09-01', 'active', '{}'::jsonb),
    (v_c4, v_run_id, 'M', date '2099-09-01', 'active',
      jsonb_build_object('strategy_m_context', jsonb_build_object(
        'entry_floor', 'not-a-number', 'entry_atr', 2, 'trail_atr', 3, 'mode', 'combined')));
end $$;

-- ══ 3) 진입일/관측일 OHLCV (fake 틱커 — 운영 데이터와 충돌 없음) ══
-- ZZM01: 진입 100, floor 93, trail_line = 100 - 3x2 = 94
-- ZZM02: 진입 100, floor 95, trail_line = 94 (동시 히트 시 greatest(95, 94) = 95)
insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
values
  ('ZZM01', date '2099-09-01', 99, 100, 98, 100, 1000),
  ('ZZM01', date '2099-09-02', 97, 98, 93.5, 96, 1000),
  ('ZZM02', date '2099-09-01', 99, 100, 98, 100, 1000),
  ('ZZM02', date '2099-09-02', 98, 99, 95.5, 97, 1000),
  ('ZZM02', date '2099-09-03', 96, 97, 92.5, 93, 1000),
  ('ZZM03', date '2099-09-01', 99, 100, 98, 100, 1000),
  ('ZZM04', date '2099-09-01', 99, 100, 98, 100, 1000),
  ('ZZM05', date '2099-09-02', 100, 100.5, 99.5, 100, 1000)
on conflict (ticker, trading_day) do nothing;

-- ══ 4) emit_open_command: OPEN payload/프로젝션 스냅샷 + 실패 가드 ══
do $$
declare
  v_r1 jsonb;
  v_r1b jsonb;
  v_r2 jsonb;
  v_o1 uuid;
  v_o2 uuid;
  v_payload jsonb;
  v_row record;
  v_caught boolean;
begin
  -- (4-1) happy: 태깅 컨텍스트가 OPEN payload와 candidate_outcome 스냅샷에 고정된다.
  v_r1 := public.emit_open_command('close:2099-09-01', 'ZZM01', 'M');
  if (v_r1->>'replayed')::boolean is distinct from false
     or (v_r1->>'skipped')::boolean is distinct from false
     or v_r1->>'event_id' is null
     or v_r1->>'outcome_id' is null
     or (v_r1->>'entry_date')::date <> date '2099-09-01'
     or (v_r1->>'entry_price')::numeric <> 100
     or (v_r1->>'tp_pct')::numeric <> 999999
     or (v_r1->>'sl_pct')::numeric <> 99
     or (v_r1->>'cutoff_n')::integer <> 999999 then
    raise exception 'M happy emit 결과 불일치: %', v_r1;
  end if;
  v_o1 := (v_r1->>'outcome_id')::uuid;

  select payload into v_payload from public.outcome_events where event_id = (v_r1->>'event_id')::uuid;
  if v_payload is null
     or (v_payload->>'entry_floor')::numeric is distinct from 93
     or (v_payload->>'entry_atr')::numeric is distinct from 2
     or (v_payload->>'trail_atr')::numeric is distinct from 3
     or (v_payload->>'tp_pct')::numeric is distinct from 999999
     or (v_payload->>'sl_pct')::numeric is distinct from 99
     or (v_payload->>'cutoff_n')::integer is distinct from 999999 then
    raise exception 'M OPEN payload 스냅샷 불일치: %', v_payload;
  end if;

  select * into v_row from public.candidate_outcome where outcome_id = v_o1;
  if not found
     or v_row.status <> 'OPEN'
     or v_row.entry_price is distinct from 100
     or v_row.entry_floor is distinct from 93
     or v_row.entry_atr is distinct from 2
     or v_row.trail_atr is distinct from 3
     or v_row.tp_pct is distinct from 999999
     or v_row.sl_pct is distinct from 99
     or v_row.cutoff_n is distinct from 999999 then
    raise exception 'M candidate_outcome 스냅샷 불일치: %', to_jsonb(v_row);
  end if;

  -- (4-2) trail_atr 누락 컨텍스트 → rule trail_atr=3.0으로 coalesce fallback.
  v_r2 := public.emit_open_command('close:2099-09-01', 'ZZM02', 'M');
  if (v_r2->>'replayed')::boolean is distinct from false
     or v_r2->>'outcome_id' is null
     or (v_r2->>'entry_price')::numeric <> 100 then
    raise exception 'M trail_atr fallback emit 결과 불일치: %', v_r2;
  end if;
  v_o2 := (v_r2->>'outcome_id')::uuid;

  select payload into v_payload from public.outcome_events where event_id = (v_r2->>'event_id')::uuid;
  if (v_payload->>'entry_floor')::numeric is distinct from 95
     or (v_payload->>'entry_atr')::numeric is distinct from 2
     or (v_payload->>'trail_atr')::numeric is distinct from 3.0 then
    raise exception 'M trail_atr coalesce fallback 불일치: %', v_payload;
  end if;
  select * into v_row from public.candidate_outcome where outcome_id = v_o2;
  if not found or v_row.entry_floor is distinct from 95 or v_row.trail_atr is distinct from 3.0 then
    raise exception 'M2 스냅샷 fallback 불일치: %', to_jsonb(v_row);
  end if;

  -- (4-3) 동일 key 재호출은 replay — M 컨텍스트를 다시 읽지 않고 저장 스냅샷을 반환한다.
  v_r1b := public.emit_open_command('close:2099-09-01', 'ZZM01', 'M');
  if (v_r1b->>'replayed')::boolean is distinct from true
     or (v_r1b->>'skipped')::boolean is distinct from false
     or (v_r1b->>'outcome_id')::uuid is distinct from v_o1
     or (v_r1b->>'entry_price')::numeric <> 100 then
    raise exception 'M replay 결과 불일치: %', v_r1b;
  end if;

  -- (4-4) strategy_m_context 없는 태그 → MISSING_STRATEGY_M_CONTEXT errcode TS001 (무장부).
  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-09-01', 'ZZM03', 'M');
  exception when sqlstate 'TS001' then
    if sqlerrm = 'MISSING_STRATEGY_M_CONTEXT' then v_caught := true; else raise; end if;
  end;
  if not v_caught then
    raise exception 'MISSING_STRATEGY_M_CONTEXT 가드 미작동';
  end if;

  -- (4-5) 캐스트 불가 컨텍스트 → INVALID_STRATEGY_M_CONTEXT errcode TS001.
  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-09-01', 'ZZM04', 'M');
  exception when sqlstate 'TS001' then
    if sqlerrm = 'INVALID_STRATEGY_M_CONTEXT' then v_caught := true; else raise; end if;
  end;
  if not v_caught then
    raise exception 'INVALID_STRATEGY_M_CONTEXT 가드 미작동';
  end if;

  if exists (
    select 1 from public.outcome_events where ticker in ('ZZM03', 'ZZM04')
  ) or exists (
    select 1 from public.candidate_outcome where ticker in ('ZZM03', 'ZZM04')
  ) then
    raise exception 'emit 실패 경로가 장부/프로젝션 행을 남겼다';
  end if;
end $$;

-- ══ 5) track_outcome_day: 박스 하단 고정 손절 + ATR 트레일링 판정 ══
do $$
declare
  v_o1 uuid;
  v_o2 uuid;
  v_o5 uuid;
  v_res jsonb;
  v_row record;
  v_status text;
  v_caught boolean;
begin
  select outcome_id into v_o1
  from public.candidate_outcome where ticker = 'ZZM01' and strategy = 'M';
  select outcome_id into v_o2
  from public.candidate_outcome where ticker = 'ZZM02' and strategy = 'M';
  if v_o1 is null or v_o2 is null then
    raise exception 'emit 산출 candidate_outcome 행 누락';
  end if;

  -- (5-1) trail-only: floor(93) 미터치, 트레일 라인(94)만 터치 → SL@94 (floor가 아닌 line 청산).
  v_res := public.track_outcome_day('close:2099-09-01', v_o1, date '2099-09-02');
  if v_res->'tp_sl' = 'null'::jsonb
     or v_res->'tp_sl'->>'status' <> 'SL'
     or (v_res->'tp_sl'->>'exit_price')::numeric is distinct from 94
     or (v_res->'tp_sl'->>'return_pct')::numeric is distinct from -6.1
     or (v_res->'tp_sl'->>'holding_days')::integer <> 1 then
    raise exception 'M trail-only SL 판정 불일치: %', v_res;
  end if;
  select * into v_row from public.candidate_outcome where outcome_id = v_o1;
  if v_row.status <> 'SL'
     or v_row.exit_date is distinct from date '2099-09-02'
     or v_row.exit_price is distinct from 94
     or v_row.return_pct is distinct from -6.1
     or v_row.holding_days <> 1 then
    raise exception 'M1 투영(SL) 불일치: %', to_jsonb(v_row);
  end if;

  -- (5-2) 퇴행 유지: 고가(99) >= trail_line(94)이어도 저가(95.5) > 라인·floor면 OPEN 유지.
  --       (라인을 고가로 판정하던 반전·우선순위 버그를 이 케이스가 잡는다.)
  v_res := public.track_outcome_day('close:2099-09-01', v_o2, date '2099-09-02');
  if v_res->'tp_sl' <> 'null'::jsonb then
    raise exception 'M 퇴행 데이 OPEN 유지 실패(고가 기준 판정 남용?): %', v_res;
  end if;
  select status into v_status from public.candidate_outcome where outcome_id = v_o2;
  if v_status <> 'OPEN' then
    raise exception 'M2가 09-02에 이미 종결됐다: %', v_status;
  end if;
  if not exists (
    select 1 from public.outcome_observations
    where outcome_id = v_o2
      and evaluation_trading_day = date '2099-09-02'
      and result_code = 'OK'
  ) then
    raise exception 'M2 09-02 관측(OK) 행 누락';
  end if;
  if exists (
    select 1 from public.outcome_events where ticker = 'ZZM02' and command_type = 'SL'
  ) then
    raise exception 'M2 퇴행 데이에 SL 이벤트가 남았다';
  end if;

  -- (5-3) 동시 히트: 저가(92.5) <= floor(95) 이면서 <= trail_line(94) → greatest = floor@95.
  v_res := public.track_outcome_day('close:2099-09-01', v_o2, date '2099-09-03');
  if v_res->'tp_sl' = 'null'::jsonb
     or v_res->'tp_sl'->>'status' <> 'SL'
     or (v_res->'tp_sl'->>'exit_price')::numeric is distinct from 95
     or (v_res->'tp_sl'->>'return_pct')::numeric is distinct from -5.1
     or (v_res->'tp_sl'->>'holding_days')::integer <> 2 then
    raise exception 'M 동시 히트 우선순위(greatest) 불일치: %', v_res;
  end if;
  select * into v_row from public.candidate_outcome where outcome_id = v_o2;
  if v_row.status <> 'SL'
     or v_row.exit_date is distinct from date '2099-09-03'
     or v_row.exit_price is distinct from 95
     or v_row.return_pct is distinct from -5.1
     or v_row.holding_days <> 2 then
    raise exception 'M2 투영(SL) 불일치: %', to_jsonb(v_row);
  end if;

  -- (5-4) 스냅샷 없는 legacy형 행: track이 관측에 도달해도 MISSING을던진다.
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n)
  values ('ZZM05', 'M', date '2099-09-01', 100, 'OPEN', 999999, 99, 999999)
  returning outcome_id into v_o5;

  v_caught := false;
  begin
    perform public.track_outcome_day('close:2099-09-01', v_o5, date '2099-09-02');
  exception when others then
    if sqlerrm = 'MISSING_STRATEGY_M_CONTEXT' then v_caught := true; else raise; end if;
  end;
  if not v_caught then
    raise exception 'track 스냅샷 누락 가드 미작동';
  end if;
  if (select status from public.candidate_outcome where outcome_id = v_o5) <> 'OPEN' then
    raise exception 'MISSING 가드 후에도 ZZM05 상태가 바뀌었다';
  end if;
end $$;

-- ══ 6) rebuild_outcome_projection: OPEN payload에서 M 컨텍스트를 재생한다 ══
do $$
declare
  v_row record;
  v_caught boolean;
begin
  -- 스냅샷 컬럼을 지운 뒤 rebuild가 payload에서 복원하는지 본다.
  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  update public.candidate_outcome
    set entry_floor = null, entry_atr = null, trail_atr = null
  where strategy = 'M' and ticker in ('ZZM01', 'ZZM02');
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

  perform public.rebuild_outcome_projection();

  select * into v_row from public.candidate_outcome where ticker = 'ZZM01' and strategy = 'M';
  if not found
     or v_row.status <> 'SL'
     or v_row.entry_floor is distinct from 93
     or v_row.entry_atr is distinct from 2
     or v_row.trail_atr is distinct from 3
     or v_row.exit_price is distinct from 94
     or v_row.return_pct is distinct from -6.1
     or v_row.holding_days <> 1
     or v_row.tp_pct is distinct from 999999
     or v_row.sl_pct is distinct from 99
     or v_row.cutoff_n is distinct from 999999 then
    raise exception 'rebuild M1 복원 불일치: %', to_jsonb(v_row);
  end if;

  select * into v_row from public.candidate_outcome where ticker = 'ZZM02' and strategy = 'M';
  if not found
     or v_row.status <> 'SL'
     or v_row.entry_floor is distinct from 95
     or v_row.entry_atr is distinct from 2
     or v_row.trail_atr is distinct from 3
     or v_row.exit_price is distinct from 95
     or v_row.return_pct is distinct from -5.1
     or v_row.holding_days <> 2 then
    raise exception 'rebuild M2 복원 불일치: %', to_jsonb(v_row);
  end if;

  -- 장부(outcome_events)에 없는 행은 projection에 남지 않는다.
  if exists (select 1 from public.candidate_outcome where ticker = 'ZZM05') then
    raise exception '이벤트 없는 ZZM05 행이 rebuild 후 남았다';
  end if;

  -- 결손 M 컨텍스트의 OPEN 이벤트는 rebuild를 차단한다(내부 변경은 서브트랜잭션으로 되돌아간다).
  -- 규칙 3필드(tp/sl/cutoff)는 채워 두어, M 컨텍스트 가드 자체가 먼저 식별되게 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values ('ZZM06', 'M', 'OPEN', 'close:2099-09-01',
    jsonb_build_object(
      'entry_date', date '2099-09-05', 'entry_price', 100,
      'tp_pct', 999999, 'sl_pct', 99, 'cutoff_n', 999999));

  v_caught := false;
  begin
    perform public.rebuild_outcome_projection();
  exception when others then
    if sqlerrm like 'REBUILD: OPEN payload missing strategy M context%'
       then v_caught := true; else raise; end if;
  end;
  if not v_caught then
    raise exception '결손 M 컨텍스트 rebuild 차단 실패';
  end if;
  if not exists (
    select 1 from public.candidate_outcome where ticker = 'ZZM01' and strategy = 'M'
  ) then
    raise exception '차단된 rebuild의 서브트랜잭션 롤백이 원장 프로젝션을 되돌리지 못했다';
  end if;
end $$;

-- ══ 6.5) publish_attempt: 손상된 M 태그가 close 발행 전체를 죽이지 않는다 ══
-- §2 하니스의 동일 attempt(close:2099-09-01)에 태그·수급 stage를 완료하고 발행한다.
-- ZZM03(컨텍스트 없음)·ZZM04(캐스트 불가)는 TS001로 종목 단위 격리되고,
-- ZZM01/ZZM02는 replay로 정상 유지되며, 발행 자체는 성공해야 한다.
do $$
declare
  v_run_id uuid;
  v_fence bigint;
  v_lease uuid;
  v_result jsonb;
  v_skipped jsonb;
  v_reason text;
begin
  select run_id, fence_token, lease_token into v_run_id, v_fence, v_lease
  from public.runs where logical_run_key = 'close:2099-09-01';
  if v_run_id is null then
    raise exception '§2 하니스 attempt를 찾을 수 없다';
  end if;

  perform public.write_stage(v_run_id, 'tags', v_fence, v_lease, 'pending', 'running');
  perform public.write_stage(v_run_id, 'tags', v_fence, v_lease, 'running', 'success');
  perform public.write_stage(v_run_id, 'supply_3day', v_fence, v_lease, 'pending', 'running');
  perform public.write_stage(v_run_id, 'supply_3day', v_fence, v_lease, 'running', 'success');
  perform public.write_stage(v_run_id, 'market_supply', v_fence, v_lease, 'pending', 'running');
  perform public.write_stage(v_run_id, 'market_supply', v_fence, v_lease, 'running', 'success');

  -- published 전이 가드(enforce_market_supply_before_publish): KOSPI/KOSDAQ 2행 필수.
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values (v_run_id, 'KOSPI', date '2099-09-01', 1, 2, -3, 4),
         (v_run_id, 'KOSDAQ', date '2099-09-01', 1, 2, -3, 4)
  on conflict (attempt_run_id, market, trading_day) do nothing;

  v_result := public.publish_attempt(v_run_id, v_fence, v_lease);
  if v_result->>'status' is distinct from 'published' then
    raise exception 'publish_attempt이 TS001 격리 없이 실패했다: %', v_result;
  end if;

  v_skipped := v_result->'skipped_open_commands';
  if jsonb_array_length(v_skipped) <> 2 then
    raise exception 'skipped_open_commands 길이 불일치(기대 2: ZZM03·ZZM04): %', v_skipped;
  end if;

  select s->>'reason' into v_reason
  from jsonb_array_elements(v_skipped) s
  where s->>'ticker' = 'ZZM03' and s->>'strategy' = 'M';
  if v_reason is distinct from 'MISSING_STRATEGY_M_CONTEXT' then
    raise exception 'ZZM03 격리 reason 불일치: %', v_skipped;
  end if;

  select s->>'reason' into v_reason
  from jsonb_array_elements(v_skipped) s
  where s->>'ticker' = 'ZZM04' and s->>'strategy' = 'M';
  if v_reason is distinct from 'INVALID_STRATEGY_M_CONTEXT' then
    raise exception 'ZZM04 격리 reason 불일치: %', v_skipped;
  end if;

  if not exists (
    select 1 from public.outcome_events where ticker = 'ZZM01' and strategy = 'M' and command_type = 'OPEN'
  ) then
    raise exception '격리 후에도 ZZM01 OPEN 이벤트가 남아 있어야 한다';
  end if;
  if exists (
    select 1 from public.outcome_events where ticker in ('ZZM03', 'ZZM04')
  ) then
    raise exception '격리된 종목의 OPEN 이벤트가 남았다';
  end if;
end $$;

-- ══ 7) 성과 기대치: 30건 M settle 시드 → ci_gated / threshold_gated / metric RPC ══
-- 기대치 리터럴은 마이그레이션 3곳(2개 gated view + 2인자 RPC)에 중복 기록된다.
-- 이 fixture가 세 곳의 M 값(0.3590 / 2.2300)을 한 번에 고정한다.
savepoint metric_fixture_isolation;
delete from public.candidate_outcome;

insert into public.candidate_outcome(
  ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct,
  cutoff_n, holding_days, tp_pct, sl_pct
)
select
  'ZZMP' || lpad(gs::text, 3, '0'),
  'M',
  date '2099-06-01' + gs,
  1000,
  -- M은 운영에서 박스 하단/트레일로만 종결되므로 상태는 전부 'SL'이다.
  -- 승패는 return_pct 부호로 구분한다(수익 SL = 승).
  'SL',
  date '2099-07-01' + gs,
  case when gs <= 11 then 1020 else 980 end,
  case when gs <= 11 then 2 else -1 end,
  999999, 2, 999999, 99
from generate_series(1, 30) as series(gs);

do $$
declare
  v_ci record;
  v_th record;
  v_rpc jsonb;
  v_src jsonb;
begin
  select total_settled, sample_gate_passed, expected_win_rate, expected_in_ci, ci_lower, ci_upper
    into v_ci
  from public.candidate_outcome_win_rate_pf_ci_gated
  where strategy = 'M';
  if not found
     or v_ci.total_settled <> 30
     or v_ci.sample_gate_passed is not true
     or v_ci.expected_win_rate is distinct from 0.3590
     or v_ci.ci_lower is null
     or v_ci.ci_upper is null
     or v_ci.expected_in_ci is not true then
    raise exception 'ci_gated M 기대치 계약 불일치: %', to_jsonb(v_ci);
  end if;

  select expected_profit_factor, win_rate_threshold_pp, profit_factor_threshold_ratio
    into v_th
  from public.candidate_outcome_win_rate_pf_threshold_gated
  where strategy = 'M';
  if not found
     or v_th.expected_profit_factor is distinct from 2.2300
     or v_th.win_rate_threshold_pp is distinct from 0.10
     or v_th.profit_factor_threshold_ratio is distinct from 0.25 then
    raise exception 'threshold_gated M 기대치 계약 불일치: %', to_jsonb(v_th);
  end if;

  -- 1인자 RPC(cutoff_bias_notice passthrough)도 동일 기대치를 노출한다.
  v_rpc := public.get_outcome_metric_comparison('M');
  if jsonb_array_length(v_rpc) <> 1
     or v_rpc->0->>'strategy' <> 'M'
     or (v_rpc->0->>'expected_win_rate')::numeric is distinct from 0.3590
     or (v_rpc->0->>'expected_profit_factor')::numeric is distinct from 2.2300
     or (v_rpc->0->>'sample_gate_passed')::boolean is not true then
    raise exception '1인자 metric RPC의 M 기대치 불일치: %', v_rpc;
  end if;

  -- 2인자 RPC의 expected 리터럴(전략 M 연결 시 추가된 M 행) — 허용 밖 source는 통합 정규화.
  v_src := public.get_outcome_metric_comparison('M', 'not-a-real-source');
  if jsonb_array_length(v_src) <> 1
     or v_src->0->>'strategy' <> 'M'
     or (v_src->0->>'expected_win_rate')::numeric is distinct from 0.3590
     or (v_src->0->>'expected_profit_factor')::numeric is distinct from 2.2300
     or (v_src->0->>'sample_gate_passed')::boolean is not true then
    raise exception '2인자 metric RPC(통합)의 M 기대치 불일치: %', v_src;
  end if;
end $$;

select 'outcome_strategy_m' as fixture, 'pass' as result;
rollback;
