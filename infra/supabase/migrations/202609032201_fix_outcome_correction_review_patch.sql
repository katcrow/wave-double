-- Story 3.8 review patch (AD-14 forward-only): 202609032200의 apply_outcome_correction을
-- create or replace로 갱신한다. 원본 파일은 손대지 않는다 -- 이미 운영에 적용된 migration은
-- 불변이며, 수정은 항상 새 forward migration으로 표현한다.
-- 고친 것:
--   1) [high] p_expected_version이 NULL이면 `target.version <> p_expected_version`이 SQL
--      3치 논리로 NULL이 되어 IF 자체가 스킵되고 버전 검사가 통째로 우회됐다(프로덕션에서
--      직접 재현: NULL을 넘긴 correction이 예외 없이 성공). `p_expected_version is null or
--      target.version <> p_expected_version`으로 고쳐 NULL을 명시적으로 거부한다.
--   2) [medium] p_reason이 NULL이거나 빈 문자열이어도 correction이 성립해 epics AC4("모든
--      correction이 사유와 함께 남는다")를 충족하지 못했다 -- p_new_status 검증 직후
--      REASON_REQUIRED 조기 검증을 추가한다.
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
  if p_expected_version is null or target.version <> p_expected_version then
    raise exception using message = 'CORRECTION_VERSION_MISMATCH';
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
  'Story 3.8 (review patch): candidate_outcome의 유일한 유효 수정 경로. 대상 행을 잠근 뒤 p_expected_version이 NULL이 아니면서 현재 저장된 version과 일치할 때만(NULL은 명시적으로 거부, review patch) outcome_events에 command_type=''CORRECTION'' 이벤트를 append하고 wave_double.outcome_mutation_allowed 가드 플래그로 감싼 UPDATE로 projection을 갱신한다(불일치/NULL 시 CORRECTION_VERSION_MISMATCH, 아무 것도 쓰지 않음). p_reason이 NULL이거나 공백뿐이면 REASON_REQUIRED로 조기 거부한다(review patch, epics AC4). p_new_status=''OPEN''이면 exit_date/exit_price/return_pct를 null로 되돌리고(SUSPENDED 복귀), entry_date/entry_price는 보존한다. 그 외 상태로의 correction은 명시된 수치 파라미터만 갱신하고 나머지는 기존 값을 유지한다(terminal 상태의 수치 정정 허용). p_logical_run_key는 outcome_events.logical_run_key NOT NULL FK 제약을 만족시키기 위한 감사 앵커로, 기존 logical_runs 행을 재사용해야 한다(이 함수가 새로 만들지 않음, FK 위반 시 그대로 예외). p_new_status가 허용 목록 밖이면 스키마 CHECK 도달 전에 INVALID_STATUS로 조기 거부하고, 존재하지 않는 outcome_id는 OUTCOME_NOT_FOUND로 거부한다.';

revoke execute on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) from public, anon, authenticated;
grant execute on function public.apply_outcome_correction(text, uuid, integer, text, text, numeric, date, numeric, numeric, integer, integer) to service_role;

commit;
