-- 예약 배치 운영시간 guard의 실제 trigger 경계와 manual 예외를 검증한다.
begin;

do $$
declare
  caught boolean := false;
  manual_run jsonb;
begin
  -- premarket 예약은 허용 창이 없으므로, 실제 현재 시각과 무관하게 차단되어야 한다.
  begin
    perform public.start_attempt(
      'premarket:2099-12-01', date '2099-12-01', 'premarket', 'schedule'
    );
  exception when others then
    if position('SCHEDULE_OUTSIDE_OPERATING_WINDOW' in sqlerrm) = 0 then
      raise;
    end if;
    caught := true;
  end;
  if not caught then
    raise exception 'scheduled premarket insert was not blocked';
  end if;

  caught := false;
  begin
    perform public.request_manual_dispatch(
      'operating-window-guard-system-scheduler', 'hash-window-guard',
      'system:scheduler', 'premarket:2099-12-01', date '2099-12-01', 'premarket'
    );
  exception when others then
    if position('SCHEDULE_OUTSIDE_OPERATING_WINDOW' in sqlerrm) = 0 then
      raise;
    end if;
    caught := true;
  end;
  if not caught then
    raise exception 'system scheduler dispatch outside window was not blocked';
  end if;

  -- manual은 운영시간과 무관하게 기존 실행 계약을 보존한다.
  manual_run := public.start_attempt(
    'premarket:2099-12-01', date '2099-12-01', 'premarket', 'manual'
  );
  if manual_run->>'run_id' is null then
    raise exception 'manual run did not bypass operating window guard';
  end if;
end
$$;

rollback;
