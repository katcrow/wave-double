-- epic-6-retro-item-25: outcome_strategy_rules의 감사 가능한 수정 경로.
--
-- 이 테이블은 "전략 X의 TP/SL/컷오프"의 유일한 권위이고 emit_open_command가 그 값을 OPEN
-- 이벤트에 스냅샷한다. 따라서 사유 없는 한 줄 UPDATE가 가능하면 그 시점 이후 판정 기준이
-- 조용히 달라진다. 이 fixture는 "이력 없는 변경이 불가능하다"를 고정한다.
begin;

do $$
declare
  result jsonb;
  caught_message text;
  caught_state text;
  v_hist integer;
begin
  -- 스키마: 이력 테이블은 RLS enable + 정책 0개(anon/authenticated 차단)여야 한다.
  if not (
    select c.relrowsecurity from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relname = 'outcome_strategy_rule_history'
  ) then raise exception 'AUDIT: outcome_strategy_rule_history RLS must be enabled'; end if;
  if exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'outcome_strategy_rule_history'
  ) then raise exception 'AUDIT: outcome_strategy_rule_history must have zero RLS policies'; end if;

  -- 사유 없는 직접 DML은 거부된다.
  caught_message := null;
  begin
    update public.outcome_strategy_rules set tp_pct = 99 where strategy = 'F';
  exception when others then caught_message := sqlerrm;
  end;
  if caught_message <> 'STRATEGY_RULE_REASON_REQUIRED' then
    raise exception 'AUDIT: 사유 없는 UPDATE가 거부되지 않았다(%)', caught_message;
  end if;

  -- 사유만 있고 변경자가 없어도 거부된다(둘 다 필수).
  perform set_config('wave_double.strategy_rule_reason', '사유만', true);
  caught_message := null;
  begin
    update public.outcome_strategy_rules set tp_pct = 99 where strategy = 'F';
  exception when others then caught_message := sqlerrm;
  end;
  if caught_message <> 'STRATEGY_RULE_CHANGED_BY_REQUIRED' then
    raise exception 'AUDIT: 변경자 없는 UPDATE가 거부되지 않았다(%)', caught_message;
  end if;
  perform set_config('wave_double.strategy_rule_reason', '', true);

  -- 사유 없는 INSERT/DELETE도 마찬가지다.
  caught_message := null;
  begin
    delete from public.outcome_strategy_rules where strategy = 'F';
  exception when others then caught_message := sqlerrm;
  end;
  if caught_message <> 'STRATEGY_RULE_REASON_REQUIRED' then
    raise exception 'AUDIT: 사유 없는 DELETE가 거부되지 않았다(%)', caught_message;
  end if;

  -- RPC 경로: 값이 바뀌고 이력이 남는다.
  result := public.set_outcome_strategy_rule('F', 3.0, 4.5, 999999, 'OOS 재평가 결과 SL 완화', 'neo');
  if result->>'operation' <> 'UPDATE' then raise exception 'AUDIT: operation UPDATE 기대, got %', result; end if;
  if (result->>'unchanged')::boolean then raise exception 'AUDIT: 값이 바뀌었는데 unchanged=true'; end if;
  if (result->'previous'->>'sl_pct')::numeric <> 4.0 then raise exception 'AUDIT: previous 값이 틀렸다: %', result; end if;
  if (select sl_pct from public.outcome_strategy_rules where strategy = 'F') <> 4.5 then
    raise exception 'AUDIT: RPC가 값을 반영하지 않았다';
  end if;

  select count(*) into v_hist from public.outcome_strategy_rule_history
    where strategy = 'F' and operation = 'UPDATE'
      and previous_sl_pct = 4.0 and new_sl_pct = 4.5
      and reason = 'OOS 재평가 결과 SL 완화' and changed_by = 'neo';
  if v_hist <> 1 then raise exception 'AUDIT: 이력이 남지 않았다(%)', v_hist; end if;

  -- RPC가 세션 설정을 되돌리므로, RPC 이후의 직접 DML도 다시 거부된다
  -- (설정이 새면 같은 트랜잭션의 뒤이은 변경이 사유 검사 없이 통과한다).
  caught_message := null;
  begin
    update public.outcome_strategy_rules set tp_pct = 99 where strategy = 'F';
  exception when others then caught_message := sqlerrm;
  end;
  if caught_message <> 'STRATEGY_RULE_REASON_REQUIRED' then
    raise exception 'AUDIT: RPC 후 세션 설정이 남아 직접 DML이 통과했다(%)', caught_message;
  end if;

  -- 같은 값으로 다시 호출해도 사유가 있는 재확인으로 이력에 남는다.
  result := public.set_outcome_strategy_rule('F', 3.0, 4.5, 999999, '값 재확인', 'neo');
  if not (result->>'unchanged')::boolean then raise exception 'AUDIT: unchanged=true 기대, got %', result; end if;
  if (select count(*) from public.outcome_strategy_rule_history where strategy = 'F') < 2 then
    raise exception 'AUDIT: 재확인 이력이 남지 않았다';
  end if;

  -- 이력은 append-only다(수정·삭제 불가).
  caught_state := null;
  begin
    update public.outcome_strategy_rule_history set reason = 'tampered' where strategy = 'F';
  exception when others then caught_state := sqlstate;
  end;
  if caught_state <> '55000' then raise exception 'AUDIT: 이력이 수정 가능했다(%)', caught_state; end if;

  caught_state := null;
  begin
    delete from public.outcome_strategy_rule_history where strategy = 'F';
  exception when others then caught_state := sqlstate;
  end;
  if caught_state <> '55000' then raise exception 'AUDIT: 이력이 삭제 가능했다(%)', caught_state; end if;

  -- RPC 인자 검증: 전략 목록, 사유, 파라미터 범위.
  caught_message := null;
  begin perform public.set_outcome_strategy_rule('Z', 3, 3, 30, 'x', 'y');
  exception when others then caught_message := sqlerrm; end;
  if caught_message <> 'INVALID_STRATEGY' then raise exception 'AUDIT: INVALID_STRATEGY 기대(%)', caught_message; end if;

  caught_message := null;
  begin perform public.set_outcome_strategy_rule('F', 3, 3, 30, '  ', 'y');
  exception when others then caught_message := sqlerrm; end;
  if caught_message <> 'STRATEGY_RULE_REASON_REQUIRED' then
    raise exception 'AUDIT: 공백 사유 거부 기대(%)', caught_message;
  end if;

  caught_message := null;
  begin perform public.set_outcome_strategy_rule('F', 3, 3, 30, 'x', '  ');
  exception when others then caught_message := sqlerrm; end;
  if caught_message <> 'STRATEGY_RULE_CHANGED_BY_REQUIRED' then
    raise exception 'AUDIT: 공백 변경자 거부 기대(%)', caught_message;
  end if;

  caught_message := null;
  begin perform public.set_outcome_strategy_rule('F', 0, 3, 30, 'x', 'y');
  exception when others then caught_message := sqlerrm; end;
  if caught_message <> 'INVALID_TP_PCT' then raise exception 'AUDIT: INVALID_TP_PCT 기대(%)', caught_message; end if;

  caught_message := null;
  begin perform public.set_outcome_strategy_rule('F', 3, -1, 30, 'x', 'y');
  exception when others then caught_message := sqlerrm; end;
  if caught_message <> 'INVALID_SL_PCT' then raise exception 'AUDIT: INVALID_SL_PCT 기대(%)', caught_message; end if;

  caught_message := null;
  begin perform public.set_outcome_strategy_rule('F', 3, 3, 0, 'x', 'y');
  exception when others then caught_message := sqlerrm; end;
  if caught_message <> 'INVALID_CUTOFF_N' then raise exception 'AUDIT: INVALID_CUTOFF_N 기대(%)', caught_message; end if;

  -- F의 sentinel cutoff(999999)은 허용돼야 한다(상한을 두면 무제한 보유가 깨진다).
  result := public.set_outcome_strategy_rule('F', 3.0, 4.0, 999999, 'sentinel 복원', 'neo');
  if (result->'current'->>'cutoff_n')::integer <> 999999 then
    raise exception 'AUDIT: sentinel cutoff_n이 거부됐다: %', result;
  end if;
end $$;

-- grant 경계: 감사 RPC는 service_role 전용이다.
do $$
begin
  if exists (
    select 1 from information_schema.role_routine_grants
    where routine_schema = 'public' and routine_name = 'set_outcome_strategy_rule'
      and grantee in ('PUBLIC', 'anon', 'authenticated')
  ) then raise exception 'set_outcome_strategy_rule must not be executable by public/anon/authenticated'; end if;

  if not exists (
    select 1 from information_schema.role_routine_grants
    where routine_schema = 'public' and routine_name = 'set_outcome_strategy_rule'
      and grantee = 'service_role' and privilege_type = 'EXECUTE'
  ) then raise exception 'set_outcome_strategy_rule must be executable by service_role'; end if;
end $$;

select 'outcome_strategy_rule_audit' as fixture, 'pass' as result;
rollback;
