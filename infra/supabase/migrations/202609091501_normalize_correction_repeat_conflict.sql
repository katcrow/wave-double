-- epic-3-retro-item-16 review patch (AD-14 forward-only): 202609091500의
-- apply_outcome_correction을 create or replace로 갱신한다(원본 파일 불변).
--
-- 고친 것 [high]: correction 반복이 raw unique violation으로 터졌다.
--   `outcome_events_open_command_key_idx`(202609031500)는 멱등 키
--   (logical_run_key, ticker, strategy, command_type)에 걸린 유니크 인덱스로, OPEN command의
--   멱등성을 위해 만들어졌지만 command_type을 키에 포함하므로 CORRECTION 이벤트에도 그대로
--   적용된다. 즉 같은 감사 앵커(logical_run_key)로 같은 outcome을 두 번 정정하려 하면
--   두 번째 호출이 SQLSTATE 23505로 죽었고, 호출자는 제약 이름을 파싱해야 알 수 있었다
--   (item-16 fixture 작성 중 운영에서 직접 재현).
--
-- 반복/충돌 정책 확정(item-16):
--   - 한 감사 앵커(logical_run_key)당 한 outcome에 correction은 최대 1건이다. 재정정은 다음
--     배치일의 앵커로 표현한다 -- 그래야 "언제 무엇을 왜 고쳤는가"가 거래일 단위로 남는다.
--   - 같은 앵커로 두 번째 correction을 시도하면 CORRECTION_ALREADY_APPLIED_FOR_RUN으로
--     거부하고 아무 것도 쓰지 않는다(멱등 재시도가 아니라 명시적 거절 -- 같은 앵커의 두 번째
--     정정은 서로 다른 의도일 수 있으므로 조용히 replay하면 의도를 잃는다).
--   - 같은 version을 읽은 두 호출자의 경합은 CORRECTION_VERSION_MISMATCH가 담당한다(변경 없음).
--
-- 정규화 범위는 202609091500의 결정을 그대로 따른다 -- 호출자가 인자를 고쳐 해결할 수 있는
-- 오류만 도메인 오류로 올린다(알 수 없는 앵커, 같은 앵커 재정정). 불변식 위반(55000, CHECK)은
-- 정규화하지 않는다.
begin;

create or replace function public.apply_outcome_correction(
  p_logical_run_key text,
  p_outcome_id uuid,
  p_expected_version integer,
  p_reason text,
  p_new_status text,
  p_new_entry_price numeric default null,
  p_new_exit_date date default null,
  p_new_exit_price numeric default null,
  p_new_return_pct numeric default null,
  p_new_holding_days integer default null,
  p_new_cutoff_n integer default null
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  target public.candidate_outcome;
  new_event public.outcome_events;
  v_new_entry_price numeric;
  v_new_exit_date date;
  v_new_exit_price numeric;
  v_new_return_pct numeric;
  v_new_holding_days integer;
  v_new_cutoff_n integer;
begin
  -- 스키마 CHECK(candidate_outcome_status_check)에 도달하기 전에 조기 검증한다.
  if p_new_status is null or p_new_status not in ('TP', 'SL', 'TIMEOUT', 'OPEN', 'SUSPENDED', 'DELISTED') then
    raise exception using message = 'INVALID_STATUS';
  end if;

  -- review patch: 모든 correction은 감사 가능한 사유를 남겨야 한다(epics AC4).
  if p_reason is null or length(btrim(p_reason)) = 0 then
    raise exception using message = 'REASON_REQUIRED';
  end if;

  select * into target from public.candidate_outcome where outcome_id = p_outcome_id for update;
  if not found then
    raise exception using message = 'OUTCOME_NOT_FOUND';
  end if;

  -- review patch: p_expected_version is null이면 `<>` 비교가 NULL이 되어 아래 IF가 스킵되고
  -- 버전 검사가 우회된다 -- NULL을 명시적으로 거부한다.
  -- 이 낙관적 버전 검사가 correction 반복/충돌 정책 그 자체다: 행을 `for update`로 잠근 뒤
  -- 검사하므로, 같은 버전을 함께 읽은 두 correction 중 나중 것은 항상
  -- CORRECTION_VERSION_MISMATCH로 거부되고 아무 것도 쓰지 않는다(lost update 불가).
  if p_expected_version is null or target.version <> p_expected_version then
    raise exception using message = 'CORRECTION_VERSION_MISMATCH';
  end if;

  -- epic-3-retro-item-16: DELISTED는 terminal이다(202609042200). 같은 DELISTED 안에서의
  -- 수치 정정은 감사 경로로 남겨두고, 다른 상태로의 전이만 막는다.
  if target.status = 'DELISTED' and p_new_status <> 'DELISTED' then
    raise exception using message = 'DELISTED_IS_TERMINAL';
  end if;

  -- SUSPENDED에서 OPEN으로 복귀하는 correction은 exit 3필드를 다시 null로 되돌리고
  -- entry_date/entry_price는 보존한다. 그 외 신규 상태로의 correction은 명시된 값이 있으면
  -- 그 값으로, 없으면 기존 값을 그대로 유지한다(terminal 상태의 수치 정정도 이 경로로 허용).
  v_new_entry_price := coalesce(p_new_entry_price, target.entry_price);
  v_new_holding_days := coalesce(p_new_holding_days, target.holding_days);
  v_new_cutoff_n := coalesce(p_new_cutoff_n, target.cutoff_n);
  if p_new_status = 'OPEN' then
    v_new_exit_date := null;
    v_new_exit_price := null;
    v_new_return_pct := null;
  else
    v_new_exit_date := coalesce(p_new_exit_date, target.exit_date);
    v_new_exit_price := coalesce(p_new_exit_price, target.exit_price);
    v_new_return_pct := coalesce(p_new_return_pct, target.return_pct);
  end if;

  -- 알 수 없는 p_logical_run_key(FK 위반 23503)와 같은 앵커의 재정정(유니크 위반 23505)만
  -- 도메인 오류로 정규화한다. 다른 SQLSTATE는 잡지 않는다(정규화 범위 결정 참고).
  begin
    insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
      values (
        target.ticker, target.strategy, 'CORRECTION', p_logical_run_key,
        jsonb_build_object(
          'reason', p_reason,
          'outcome_id', p_outcome_id,
          'previous_version', target.version,
          'previous_status', target.status,
          'new_status', p_new_status,
          'previous_entry_price', target.entry_price,
          'new_entry_price', v_new_entry_price,
          'previous_exit_date', target.exit_date,
          'new_exit_date', v_new_exit_date,
          'previous_exit_price', target.exit_price,
          'new_exit_price', v_new_exit_price,
          'previous_return_pct', target.return_pct,
          'new_return_pct', v_new_return_pct,
          'previous_holding_days', target.holding_days,
          'new_holding_days', v_new_holding_days,
          'previous_cutoff_n', target.cutoff_n,
          'new_cutoff_n', v_new_cutoff_n
        )
      )
      returning * into new_event;
  exception
    when foreign_key_violation then
      raise exception using message = 'LOGICAL_RUN_NOT_FOUND';
    when unique_violation then
      -- 멱등 키 (logical_run_key, ticker, strategy, command_type) 충돌: 이 앵커로는 이미
      -- 정정했다. 재정정은 다음 배치일의 앵커로 표현한다.
      raise exception using message = 'CORRECTION_ALREADY_APPLIED_FOR_RUN';
  end;

  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  update public.candidate_outcome set
      status = p_new_status,
      entry_price = v_new_entry_price,
      exit_date = v_new_exit_date,
      exit_price = v_new_exit_price,
      return_pct = v_new_return_pct,
      holding_days = v_new_holding_days,
      cutoff_n = v_new_cutoff_n
    where outcome_id = p_outcome_id
    returning * into target;
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);

  return jsonb_build_object(
    'event_id', new_event.event_id,
    'outcome_id', target.outcome_id,
    'version', target.version,
    'status', target.status,
    'entry_price', target.entry_price,
    'exit_date', target.exit_date,
    'exit_price', target.exit_price,
    'return_pct', target.return_pct,
    'holding_days', target.holding_days,
    'cutoff_n', target.cutoff_n
  );
end $$;

comment on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) is
  'Story 3.8 (epic-3-retro-item-16 review patch): candidate_outcome의 유일한 유효 수정 경로. 대상 행을 잠근 뒤 p_expected_version이 NULL이 아니면서 현재 저장된 version과 일치할 때만(NULL은 명시적으로 거부) outcome_events에 command_type=''CORRECTION'' 이벤트를 append하고 wave_double.outcome_mutation_allowed 가드 플래그로 감싼 UPDATE로 projection을 갱신한다(불일치/NULL 시 CORRECTION_VERSION_MISMATCH, 아무 것도 쓰지 않음). 이 낙관적 버전 검사가 반복/충돌 정책이다 -- 같은 버전을 읽은 두 correction 중 나중 것은 항상 거부되고, 연속 correction은 version을 1씩 올리며 payload에 previous_version -> new_status 사슬을 남긴다. p_reason이 NULL이거나 공백뿐이면 REASON_REQUIRED로 조기 거부한다(epics AC4). 현재 status가 DELISTED면 DELISTED 안에서의 수치 정정만 허용하고 다른 상태로의 전이는 DELISTED_IS_TERMINAL로 거부한다(item-16, 202609042200의 terminal 선언과 일치). p_new_status=''OPEN''이면 exit_date/exit_price/return_pct를 null로 되돌리고(SUSPENDED 복귀), entry_date/entry_price는 보존한다. 그 외 상태로의 correction은 명시된 수치 파라미터만 갱신하고 나머지는 기존 값을 유지한다(terminal 상태의 수치 정정 허용). p_logical_run_key는 감사 앵커로 기존 logical_runs 행을 재사용해야 하며, 없으면 FK 위반 대신 LOGICAL_RUN_NOT_FOUND로 정규화해 올린다. 한 앵커당 한 outcome에 correction은 최대 1건이다(멱등 키 유니크 인덱스) -- 같은 앵커로 두 번째 정정을 시도하면 CORRECTION_ALREADY_APPLIED_FOR_RUN으로 거부하므로, 재정정은 다음 배치일의 앵커로 표현한다. 불변식 위반(append-only/guard 트리거의 55000, 스키마 CHECK)은 의도적으로 정규화하지 않고 원본 SQLSTATE로 올린다. p_new_status가 허용 목록 밖이면 INVALID_STATUS, 존재하지 않는 outcome_id는 OUTCOME_NOT_FOUND로 거부한다.';

revoke execute on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) from public, anon, authenticated;
grant execute on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) to service_role;

commit;
