-- epic-3-retro-item-16: outcome correction 정책 fixture.
--
-- 3.8 회귀 fixture(test_run_lineage.sql)가 단발 correction의 정상 경로와 개별 거절 사유를
-- 이미 덮고 있으므로, 여기서는 회고가 지목한 "정책" 층만 다룬다.
--   1) correction 반복 -- 연속 correction의 version 사슬과 payload previous_* 사슬
--   2) correction 충돌 -- 같은 version을 읽은 두 correction의 lost-update 불가
--   3) terminal 불변성 -- DELISTED에서 빠져나가는 전이 금지, 안에서의 수치 정정은 허용
--   4) event ordering -- created_at 동률에서 event_id 결정론(재구축 결과가 흔들리지 않음)
--   5) 오류 정규화 범위 -- 호출자가 고칠 수 있는 오류만 도메인 오류, 불변식 위반은 원본 SQLSTATE
begin;

-- ── 1) correction 반복: 앵커당 1건, 재정정은 다음 앵커로 ─────────────────────
-- 멱등 키 (logical_run_key, ticker, strategy, command_type)에 유니크 인덱스가 걸려 있어
-- (202609031500) 한 감사 앵커로는 한 outcome을 한 번만 정정할 수 있다. 재정정은 다음
-- 배치일의 앵커로 표현하며, 그때마다 version이 1씩 올라가고 payload에 사슬이 남는다.
do $$
declare
  outcome_id_v uuid;
  v_version integer;
  result jsonb;
  v_events jsonb;
  caught boolean := false;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values
    ('close:2099-02-01', date '2099-02-01', 'close'),
    ('close:2099-02-08', date '2099-02-08', 'close'),
    ('close:2099-02-09', date '2099-02-09', 'close')
  on conflict (logical_run_key) do nothing;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZREP1', 'A', 'OPEN', 'close:2099-02-01', jsonb_build_object('entry_date', date '2099-02-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZREP1', 'A', date '2099-02-01', 100, 'OPEN')
    returning outcome_id into outcome_id_v;

  if (select version from public.candidate_outcome where outcome_id = outcome_id_v) <> 1 then
    raise exception 'REPEAT: 신규 outcome의 version은 1이어야 한다';
  end if;

  -- 1차 정정(앵커 02-01): OPEN -> SUSPENDED
  select version into v_version from public.candidate_outcome where outcome_id = outcome_id_v;
  result := public.apply_outcome_correction('close:2099-02-01', outcome_id_v, v_version, '가격 조정 의심', 'SUSPENDED');
  if (result->>'version')::integer <> 2 then raise exception 'REPEAT: 1차 correction 후 version 2 기대, got %', result->>'version'; end if;

  -- 같은 앵커로 두 번째 정정은 거부된다(raw 23505이 아니라 도메인 오류로).
  begin
    perform public.apply_outcome_correction('close:2099-02-01', outcome_id_v, 2, '같은 앵커 재정정', 'OPEN');
  exception when others then
    if sqlerrm = 'CORRECTION_ALREADY_APPLIED_FOR_RUN' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'REPEAT: 같은 앵커의 두 번째 correction이 수락됐다'; end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_id_v) <> 2 then
    raise exception 'REPEAT: 거절된 재정정이 version을 올렸다';
  end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_id_v) <> 'SUSPENDED' then
    raise exception 'REPEAT: 거절된 재정정이 status를 바꿨다';
  end if;

  -- 2차 정정(다음 앵커 02-08): SUSPENDED -> OPEN
  result := public.apply_outcome_correction('close:2099-02-08', outcome_id_v, 2, '조정 오탐 해제', 'OPEN');
  if (result->>'version')::integer <> 3 then raise exception 'REPEAT: 2차 correction 후 version 3 기대, got %', result->>'version'; end if;

  -- 3차 정정(앵커 02-09): OPEN -> TIMEOUT (수치 함께 확정)
  result := public.apply_outcome_correction('close:2099-02-09', outcome_id_v, 3, '컷오프 도달 확정', 'TIMEOUT', null, date '2099-03-15', 98, -2.1, 30, 30);
  if (result->>'version')::integer <> 4 then raise exception 'REPEAT: 3차 correction 후 version 4 기대, got %', result->>'version'; end if;

  -- 반복 correction은 매번 이벤트를 하나씩 append한다(덮어쓰기 없음, 거절분은 남지 않음).
  if (select count(*) from public.outcome_events
      where ticker = 'ZZREP1' and strategy = 'A' and command_type = 'CORRECTION') <> 3 then
    raise exception 'REPEAT: CORRECTION 이벤트가 3건이어야 한다, got %',
      (select count(*) from public.outcome_events where ticker = 'ZZREP1' and command_type = 'CORRECTION');
  end if;

  -- payload의 previous_version -> new_status 사슬이 끊기지 않는지 확인한다.
  -- 정렬 키는 previous_version이다 -- created_at은 세 correction이 모두 같은 트랜잭션에서
  -- append됐으면 now()로 동률이 되고, 그 동률에서는 event_id(랜덤 uuid)가 순서를 정하므로
  -- 삽입 순서를 복원해주지 않는다(아래 4절이 이 타이브레이크를 따로 고정한다).
  select jsonb_agg(jsonb_build_object(
           'previous_version', payload->>'previous_version',
           'previous_status', payload->>'previous_status',
           'new_status', payload->>'new_status')
         order by (payload->>'previous_version')::integer)
    into v_events
    from public.outcome_events
    where ticker = 'ZZREP1' and strategy = 'A' and command_type = 'CORRECTION';

  if v_events <> '[
      {"previous_version":"1","previous_status":"OPEN","new_status":"SUSPENDED"},
      {"previous_version":"2","previous_status":"SUSPENDED","new_status":"OPEN"},
      {"previous_version":"3","previous_status":"OPEN","new_status":"TIMEOUT"}
    ]'::jsonb then
    raise exception 'REPEAT: correction 사슬이 기대와 다르다: %', v_events;
  end if;

  -- 마지막 correction의 수치가 projection에 반영되고 exit 3필드가 함께 채워졌는지 확인.
  if not exists (
    select 1 from public.candidate_outcome
    where outcome_id = outcome_id_v and status = 'TIMEOUT' and entry_price = 100
      and exit_date = date '2099-03-15' and exit_price = 98 and return_pct = -2.1
      and holding_days = 30 and cutoff_n = 30 and version = 4
  ) then raise exception 'REPEAT: 마지막 correction 결과가 projection에 반영되지 않았다'; end if;
end $$;

-- ── 2) correction 충돌: 같은 version을 읽은 두 correction ─────────────────────
do $$
declare
  key text := 'close:2099-02-02';
  outcome_id_v uuid;
  reader_a_version integer;
  reader_b_version integer;
  caught boolean := false;
  v_status text;
  v_version integer;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values (key, date '2099-02-02', 'close')
    on conflict (logical_run_key) do nothing;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZCONF1', 'B', 'OPEN', key, jsonb_build_object('entry_date', date '2099-02-02', 'entry_price', 200));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZCONF1', 'B', date '2099-02-02', 200, 'OPEN')
    returning outcome_id into outcome_id_v;

  -- 두 호출자가 같은 시점의 version을 읽는다(운영에서는 서로 다른 세션/배치 재시도).
  select version into reader_a_version from public.candidate_outcome where outcome_id = outcome_id_v;
  select version into reader_b_version from public.candidate_outcome where outcome_id = outcome_id_v;
  if reader_a_version <> reader_b_version then raise exception 'CONFLICT: 두 독자가 같은 version을 읽어야 한다'; end if;

  -- 먼저 도착한 correction만 성립한다.
  perform public.apply_outcome_correction(key, outcome_id_v, reader_a_version, 'A가 먼저 확정', 'SUSPENDED');

  -- 나중 correction은 자기가 읽은 version으로 덮어쓰지 못한다(lost update 불가).
  begin
    perform public.apply_outcome_correction(key, outcome_id_v, reader_b_version, 'B가 뒤늦게 확정', 'TIMEOUT');
  exception when others then
    if sqlerrm = 'CORRECTION_VERSION_MISMATCH' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'CONFLICT: 뒤늦은 correction이 수락됐다(lost update)'; end if;

  select status, version into v_status, v_version
    from public.candidate_outcome where outcome_id = outcome_id_v;
  if v_status <> 'SUSPENDED' or v_version <> reader_a_version + 1 then
    raise exception 'CONFLICT: 거절된 correction이 상태/version을 건드렸다(status=%, version=%)', v_status, v_version;
  end if;
  if (select count(*) from public.outcome_events
      where ticker = 'ZZCONF1' and command_type = 'CORRECTION') <> 1 then
    raise exception 'CONFLICT: 거절된 correction이 이벤트를 남겼다';
  end if;

  -- 충돌한 호출자는 version을 다시 읽어 재시도하면 성립한다(정책의 회복 경로).
  select version into reader_b_version from public.candidate_outcome where outcome_id = outcome_id_v;
  -- 재시도는 다음 앵커로 표현한다(같은 앵커는 CORRECTION_ALREADY_APPLIED_FOR_RUN).
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values ('close:2099-02-10', date '2099-02-10', 'close')
    on conflict (logical_run_key) do nothing;
  perform public.apply_outcome_correction('close:2099-02-10', outcome_id_v, reader_b_version, 'B가 재조회 후 재시도', 'TIMEOUT', null, date '2099-03-10', 195, -2.6, 30, 30);
  if (select status from public.candidate_outcome where outcome_id = outcome_id_v) <> 'TIMEOUT' then
    raise exception 'CONFLICT: 재조회 후 재시도가 성립하지 않았다';
  end if;
end $$;

-- ── 3) terminal 불변성: DELISTED에서 빠져나갈 수 없다 ─────────────────────────
do $$
declare
  key text := 'close:2099-02-03';
  outcome_id_v uuid;
  v_version integer;
  v_status text;
  bad_status text;
  caught boolean;
  result jsonb;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values (key, date '2099-02-03', 'close')
    on conflict (logical_run_key) do nothing;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZTERM1', 'C', 'OPEN', key, jsonb_build_object('entry_date', date '2099-02-03', 'entry_price', 300));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, holding_days)
    values ('ZZTERM1', 'C', date '2099-02-03', 300, 'DELISTED', date '2099-02-20', 250, -16.8, 12)
    returning outcome_id into outcome_id_v;

  -- DELISTED -> 다른 상태로의 전이는 전부 거부된다. 모두 이벤트 append 전에 거절되므로
  -- 같은 앵커를 반복해도 멱등 키 충돌이 아니라 항상 DELISTED_IS_TERMINAL이어야 한다.
  foreach bad_status in array array['OPEN', 'SUSPENDED', 'TP', 'SL', 'TIMEOUT'] loop
    select version into v_version from public.candidate_outcome where outcome_id = outcome_id_v;
    caught := false;
    begin
      perform public.apply_outcome_correction(key, outcome_id_v, v_version, '종결 되돌리기 시도', bad_status);
    exception when others then
      if sqlerrm = 'DELISTED_IS_TERMINAL' then caught := true; else raise; end if;
    end;
    if not caught then raise exception 'TERMINAL: DELISTED -> %가 수락됐다', bad_status; end if;

    select status, version into v_status, v_version from public.candidate_outcome where outcome_id = outcome_id_v;
    if v_status <> 'DELISTED' then raise exception 'TERMINAL: 거절 후에도 status가 바뀌었다(%)', v_status; end if;
  end loop;

  -- 거절된 전이는 이벤트도 version도 남기지 않는다.
  if (select count(*) from public.outcome_events
      where ticker = 'ZZTERM1' and command_type = 'CORRECTION') <> 0 then
    raise exception 'TERMINAL: 거절된 전이가 CORRECTION 이벤트를 남겼다';
  end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_id_v) <> 1 then
    raise exception 'TERMINAL: 거절된 전이가 version을 올렸다';
  end if;

  -- 반면 DELISTED 안에서의 수치 정정은 감사 경로로 계속 허용된다(정산 금액 오기 수정 등).
  select version into v_version from public.candidate_outcome where outcome_id = outcome_id_v;
  result := public.apply_outcome_correction(key, outcome_id_v, v_version, '정리매매 종가 정정', 'DELISTED', null, null, 248, -17.4);
  if (result->>'status') <> 'DELISTED' then raise exception 'TERMINAL: DELISTED 내 수치 정정이 거부됐다: %', result; end if;
  if not exists (
    select 1 from public.candidate_outcome
    where outcome_id = outcome_id_v and status = 'DELISTED'
      and exit_price = 248 and return_pct = -17.4
      and exit_date = date '2099-02-20' and version = v_version + 1
  ) then raise exception 'TERMINAL: DELISTED 내 수치 정정 결과가 기대와 다르다'; end if;
end $$;

-- ── 4) event ordering: created_at 동률에서 event_id로 결정론적 재생 ───────────
-- rebuild_outcome_projection은 (created_at, event_id) 오름차순으로 재생한다. 같은 배치가
-- 같은 트랜잭션 안에서 두 이벤트를 append하면 created_at(now())이 동률이 되므로, 동률에서
-- 순서가 흔들리면 재구축 결과가 실행마다 달라진다 -- event_id 타이브레이크를 고정한다.
do $$
declare
  key text := 'close:2099-02-04';
  fixed_at timestamptz := timestamptz '2099-02-04 15:00:00+09';
  v_status text;
  v_first text;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values (key, date '2099-02-04', 'close')
    on conflict (logical_run_key) do nothing;

  -- 동일 created_at의 세 이벤트. event_id 오름차순은 ...01(OPEN) < ...02(SL) < ...03(CORRECTION).
  -- 따라서 결정론적 재생 결과는 마지막 event_id인 CORRECTION의 상태(TIMEOUT)여야 한다.
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload, created_at)
  values
    ('aa000000-0000-0000-0000-000000000001', 'ZZORD1', 'A', 'OPEN', key,
     '{"entry_date":"2099-02-04","entry_price":100}'::jsonb, fixed_at),
    ('aa000000-0000-0000-0000-000000000002', 'ZZORD1', 'A', 'SL', key,
     '{"trading_day":"2099-02-05","exit_price":97,"return_pct":-3.1,"holding_days":1}'::jsonb, fixed_at),
    ('aa000000-0000-0000-0000-000000000003', 'ZZORD1', 'A', 'CORRECTION', key,
     '{"reason":"SL 오판정 정정","previous_status":"SL","new_status":"TIMEOUT","previous_exit_price":97,"new_exit_price":99,"previous_return_pct":-3.1,"new_return_pct":-1.1,"previous_holding_days":1,"new_holding_days":30,"previous_cutoff_n":30,"new_cutoff_n":30}'::jsonb,
     fixed_at);

  perform public.rebuild_outcome_projection();

  select status into v_status from public.candidate_outcome where ticker = 'ZZORD1' and strategy = 'A';
  if v_status <> 'TIMEOUT' then
    raise exception 'ORDERING: created_at 동률에서 event_id 타이브레이크가 깨졌다(status=%)', v_status;
  end if;

  -- 같은 재생을 반복해도 같은 결과여야 한다(동률 순서가 실행마다 흔들리지 않는다).
  perform public.rebuild_outcome_projection();
  if (select status from public.candidate_outcome where ticker = 'ZZORD1' and strategy = 'A') <> 'TIMEOUT' then
    raise exception 'ORDERING: 반복 재생에서 결과가 흔들렸다';
  end if;

  -- 재생 순서 자체가 (created_at, event_id)임을 직접 확인한다.
  select command_type into v_first
    from public.outcome_events
    where ticker = 'ZZORD1' and strategy = 'A'
    order by created_at, event_id
    limit 1;
  if v_first <> 'OPEN' then raise exception 'ORDERING: 첫 재생 이벤트가 OPEN이 아니다(%)', v_first; end if;

  -- 결정론의 범위를 명시한다: 같은 트랜잭션에서 append된 이벤트들은 created_at(now())이
  -- 동률이므로 순서를 정하는 것은 event_id뿐이다. event_id는 기본값이 랜덤 uuid이므로
  -- "장부에 기록된 순서"는 삽입 순서와 무관하다 -- 다만 일단 기록된 장부에 대한 재생은
  -- 항상 같은 순서다(위 반복 재생 확인). 따라서 한 트랜잭션에서 같은 (ticker,strategy)에
  -- 순서가 의미 있는 두 이벤트를 append하려면 created_at을 명시적으로 벌려야 한다.
  if (select count(distinct created_at) from public.outcome_events
      where ticker = 'ZZORD1' and strategy = 'A') <> 1 then
    raise exception 'ORDERING: 이 시나리오는 created_at 동률을 전제로 한다';
  end if;
end $$;

-- ── 5) 오류 정규화 범위 ───────────────────────────────────────────────────────
do $$
declare
  key text := 'close:2099-02-05';
  outcome_id_v uuid;
  v_version integer;
  caught_message text;
  caught_state text;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values (key, date '2099-02-05', 'close')
    on conflict (logical_run_key) do nothing;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZERR1', 'A', 'OPEN', key, jsonb_build_object('entry_date', date '2099-02-05', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZERR1', 'A', date '2099-02-05', 100, 'OPEN')
    returning outcome_id into outcome_id_v;

  -- 정규화한다: 호출자가 인자를 고쳐 해결할 수 있는 오류(알 수 없는 logical_run_key).
  -- 이전에는 outcome_events FK 위반(23503)이 그대로 올라왔다.
  select version into v_version from public.candidate_outcome where outcome_id = outcome_id_v;
  caught_message := null;
  caught_state := null;
  begin
    perform public.apply_outcome_correction('close:1999-01-01', outcome_id_v, v_version, '없는 앵커', 'SUSPENDED');
  exception when others then
    caught_message := sqlerrm;
    caught_state := sqlstate;
  end;
  if caught_message <> 'LOGICAL_RUN_NOT_FOUND' then
    raise exception 'NORMALIZE: 알 수 없는 logical_run_key가 LOGICAL_RUN_NOT_FOUND로 정규화되지 않았다(message=%, state=%)',
      caught_message, caught_state;
  end if;
  if caught_state = '23503' then
    raise exception 'NORMALIZE: raw FK 위반 SQLSTATE가 그대로 노출됐다';
  end if;
  -- 거절된 correction은 아무 것도 쓰지 않는다.
  if (select version from public.candidate_outcome where outcome_id = outcome_id_v) <> v_version then
    raise exception 'NORMALIZE: 거절된 correction이 version을 올렸다';
  end if;
  if (select count(*) from public.outcome_events where ticker = 'ZZERR1' and command_type = 'CORRECTION') <> 0 then
    raise exception 'NORMALIZE: 거절된 correction이 이벤트를 남겼다';
  end if;

  -- 정규화한다: 같은 앵커의 재정정(유니크 위반 23505) -> CORRECTION_ALREADY_APPLIED_FOR_RUN.
  select version into v_version from public.candidate_outcome where outcome_id = outcome_id_v;
  perform public.apply_outcome_correction(key, outcome_id_v, v_version, '첫 정정', 'SUSPENDED');
  select version into v_version from public.candidate_outcome where outcome_id = outcome_id_v;
  caught_message := null;
  caught_state := null;
  begin
    perform public.apply_outcome_correction(key, outcome_id_v, v_version, '같은 앵커 재정정', 'OPEN');
  exception when others then
    caught_message := sqlerrm;
    caught_state := sqlstate;
  end;
  if caught_message <> 'CORRECTION_ALREADY_APPLIED_FOR_RUN' then
    raise exception 'NORMALIZE: 같은 앵커 재정정이 정규화되지 않았다(message=%, state=%)', caught_message, caught_state;
  end if;
  if caught_state = '23505' then
    raise exception 'NORMALIZE: raw 유니크 위반 SQLSTATE가 그대로 노출됐다';
  end if;

  -- 정규화하지 않는다: 불변식 위반은 도메인 오류로 감싸지 않고 원본 SQLSTATE(55000)로 올린다.
  -- 이건 호출자의 입력 문제가 아니라 코드 결함의 신호이므로 삼키면 원인 추적을 잃는다.
  caught_state := null;
  begin
    update public.candidate_outcome set status = 'TIMEOUT' where outcome_id = outcome_id_v;
  exception when others then
    caught_state := sqlstate;
  end;
  if caught_state <> '55000' then
    raise exception 'NORMALIZE: raw UPDATE가 55000으로 거부되지 않았다(state=%)', caught_state;
  end if;

  caught_state := null;
  begin
    update public.outcome_events set payload = '{}'::jsonb where ticker = 'ZZERR1';
  exception when others then
    caught_state := sqlstate;
  end;
  if caught_state <> '55000' then
    raise exception 'NORMALIZE: outcome_events append-only 위반이 55000으로 거부되지 않았다(state=%)', caught_state;
  end if;
end $$;

rollback;
