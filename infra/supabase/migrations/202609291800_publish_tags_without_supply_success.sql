-- 태깅 후보 발행은 candidates/tags 완료만 필수로 한다.
-- supply_3day와 market_supply는 후보 판단의 참고 근거이므로 partial/failed여도
-- 태깅 후보와 close outcome 발행을 막지 않는다. 기존 applied migration은 수정하지 않는다.
begin;

do $migration$
declare
  function_def text;
  rewritten text;
  pending_supply_guard text := $guard$
  if coalesce(r.stage_status->>'supply_3day', 'pending') in ('pending', 'running') then
    raise exception using message = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE';
  end if;$guard$;
  pending_market_guard text := $guard$
  if coalesce(r.stage_status->>'market_supply', 'pending') in ('pending', 'running') then
    raise exception using message = 'MARKET_SUPPLY_STAGE_NOT_COMPLETE';
  end if;$guard$;
begin
  select pg_get_functiondef(p.oid)
    into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public'
    and p.proname = 'publish_attempt'
    and pg_get_function_identity_arguments(p.oid) = 'p_run_id uuid, p_fence_token bigint, p_lease_token uuid';

  if function_def is null then
    raise exception using message = 'PUBLISH_ATTEMPT_FUNCTION_NOT_FOUND';
  end if;

  rewritten := regexp_replace(
    function_def,
    $pattern$if r\.stage_status->>'supply_3day' is distinct from 'success' then.*?end if;$pattern$,
    pending_supply_guard,
    'gs'
  );
  rewritten := regexp_replace(
    rewritten,
    $pattern$if r\.stage_status->>'market_supply' is distinct from 'success' then.*?end if;$pattern$,
    pending_market_guard,
    'gs'
  );

  -- 이 migration이 재실행되거나, 이전 초안 migration이 이미 supply guard를
  -- 제거한 운영 DB에서도 pending/running 가드는 다시 보강한다.
  if position('coalesce(r.stage_status->>''supply_3day'', ''pending'') in (''pending'', ''running'')' in rewritten) = 0 then
    rewritten := regexp_replace(
      rewritten,
      $pattern$if r\.stage_status->>'tags' is distinct from 'success' then.*?end if;$pattern$,
      $replacement$
  if r.stage_status->>'tags' is distinct from 'success' then
    raise exception using message = 'TAGS_STAGE_NOT_COMPLETE';
  end if;
$replacement$ || pending_supply_guard || pending_market_guard,
      'gs'
    );
  end if;

  if position('SUPPLY_3DAY_STAGE_NOT_COMPLETE' in rewritten) = 0
     or position('MARKET_SUPPLY_STAGE_NOT_COMPLETE' in rewritten) = 0
     or position($token$supply_3day' is distinct from 'success$token$ in rewritten) > 0
     or position($token$market_supply' is distinct from 'success$token$ in rewritten) > 0
     or position('PUBLISH_GUARD_FAILED' in rewritten) = 0
     or position('TAGS_STAGE_NOT_COMPLETE' in rewritten) = 0
     or position('PUBLISH_PROVENANCE_GUARD_FAILED' in rewritten) = 0
     or position('STALE_FENCE_OR_LEASE' in rewritten) = 0
     or position('CANONICAL_ALREADY_PUBLISHED' in rewritten) = 0
     or position('emit_open_command' in rewritten) = 0
     or position('strategy <> ''I''' in rewritten) = 0 then
    raise exception using message = 'PUBLISH_SUPPLY_GUARD_REWRITE_FAILED';
  end if;

  execute rewritten;
end
$migration$;

comment on function public.publish_attempt(uuid, bigint, uuid) is
  '태깅 후보 발행은 candidates/tags success를 가드한다. supply_3day와 market_supply는 참고값이며 partial/failed여도 발행을 막지 않는다. pending/running은 계속 수집 중이므로 가드한다. close outcome에서는 전략 I를 제외한다.';

commit;
