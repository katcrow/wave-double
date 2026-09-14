-- Supabase 무료 플랜 용량 관리(2026-09-14) fixture: purge_old_attempt_data가
--   1) retention 기간보다 오래되고 logical_runs 포인터에 안 걸리는 run과 그 attempt 데이터만 지우고,
--   2) logical_runs가 가리키는(보존해야 하는) run은 아무리 오래돼도 절대 안 건드리고,
--   3) retention 기간 안에 있는 최근 run은 오래된 것처럼 보여도 안 건드리는지 검증한다.
-- 모든 변경은 rollback으로 되돌린다.
begin;

do $$
declare
  v_candidate_id uuid := gen_random_uuid();

  -- 시나리오 A: 오래됐고 어떤 logical_runs 포인터에도 안 걸리는 run -- 지워져야 한다.
  purge_key text := 'intraday:2099-02-01:09:00';
  purge_started jsonb; purge_run_id uuid; purge_fence bigint; purge_lease uuid;

  -- 시나리오 B: 오래됐지만 logical_runs.current_complete_run_id가 가리키는 run -- 보존돼야 한다.
  keep_key text := 'close:2099-02-01';
  keep_started jsonb; keep_run_id uuid; keep_fence bigint; keep_lease uuid;

  -- 시나리오 C: retention 기간 안(최근)인 run -- 오래된 것과 같은 조건이어도 보존돼야 한다.
  recent_key text := 'intraday:2099-02-02:09:00';
  recent_started jsonb; recent_run_id uuid; recent_fence bigint; recent_lease uuid;

  purge_result jsonb;
begin
  -- ── 시나리오 A: 삭제 대상 ──────────────────────────────────────────────
  purge_started := public.start_attempt(purge_key, date '2099-02-01', 'intraday', 'manual', 300);
  purge_run_id := (purge_started->>'run_id')::uuid;
  purge_fence := (purge_started->>'fence_token')::bigint;
  purge_lease := (purge_started->>'lease_token')::uuid;
  perform public.write_stage(purge_run_id, 'candidates', purge_fence, purge_lease, 'pending', 'running');
  perform public.write_candidates(
    purge_run_id, purge_fence, purge_lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', v_candidate_id, 'ticker', '900001', 'name', '퍼지대상', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1,
      'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(purge_run_id, 'candidates', purge_fence, purge_lease, 'running', 'success');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (v_candidate_id, purge_run_id, 'A', date '2099-02-01');
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
    values (purge_run_id, 'KOSPI', date '2099-02-01', 1, 2, 3, 4);
  update public.runs set started_at = now() - interval '30 days' where run_id = purge_run_id;

  -- ── 시나리오 B: logical_runs.current_complete_run_id가 가리키므로 보존 ──────
  keep_started := public.start_attempt(keep_key, date '2099-02-01', 'close', 'manual', 300);
  keep_run_id := (keep_started->>'run_id')::uuid;
  keep_fence := (keep_started->>'fence_token')::bigint;
  keep_lease := (keep_started->>'lease_token')::uuid;
  perform public.write_stage(keep_run_id, 'candidates', keep_fence, keep_lease, 'pending', 'running');
  perform public.write_stage(keep_run_id, 'candidates', keep_fence, keep_lease, 'running', 'success');
  update public.logical_runs set current_complete_run_id = keep_run_id where logical_run_key = keep_key;
  update public.runs set started_at = now() - interval '30 days' where run_id = keep_run_id;

  -- ── 시나리오 C: retention 기간 안의 최근 run -- 어떤 포인터에도 안 걸려도 보존 ──
  recent_started := public.start_attempt(recent_key, date '2099-02-02', 'intraday', 'manual', 300);
  recent_run_id := (recent_started->>'run_id')::uuid;
  recent_fence := (recent_started->>'fence_token')::bigint;
  recent_lease := (recent_started->>'lease_token')::uuid;
  perform public.write_stage(recent_run_id, 'candidates', recent_fence, recent_lease, 'pending', 'running');
  perform public.write_stage(recent_run_id, 'candidates', recent_fence, recent_lease, 'running', 'success');
  -- started_at은 now() 그대로 둔다(방금 시작한 run).

  -- ── 실행 ───────────────────────────────────────────────────────────
  purge_result := public.purge_old_attempt_data(7);

  if (purge_result->>'purged_runs')::integer < 1 then
    raise exception 'purge fixture: expected at least one run purged, got %', purge_result;
  end if;

  if exists (select 1 from public.runs where run_id = purge_run_id) then
    raise exception 'purge fixture: old unprotected run was not purged';
  end if;
  if exists (select 1 from public.candidate_tags where attempt_run_id = purge_run_id) then
    raise exception 'purge fixture: candidate_tags for purged run survived';
  end if;
  if exists (select 1 from public.market_supply where attempt_run_id = purge_run_id) then
    raise exception 'purge fixture: market_supply for purged run survived';
  end if;
  if exists (select 1 from public.candidates where attempt_run_id = purge_run_id) then
    raise exception 'purge fixture: candidates for purged run survived';
  end if;
  if exists (select 1 from public.logical_runs where logical_run_key = purge_key and active_attempt_run_id is not null) then
    raise exception 'purge fixture: active_attempt_run_id pointer to purged run was not cleared';
  end if;

  if not exists (select 1 from public.runs where run_id = keep_run_id) then
    raise exception 'purge fixture: logical_runs-pointed old run was incorrectly purged';
  end if;
  if not exists (select 1 from public.logical_runs where logical_run_key = keep_key and current_complete_run_id = keep_run_id) then
    raise exception 'purge fixture: logical_runs pointer to protected run was disturbed';
  end if;

  if not exists (select 1 from public.runs where run_id = recent_run_id) then
    raise exception 'purge fixture: recent (within retention) run was incorrectly purged';
  end if;

  -- 멱등성: 이미 지운 뒤 다시 돌려도 같은 대상이 또 없어 안전해야 한다(추가 오류 없이 0건).
  perform public.purge_old_attempt_data(7);

  raise notice 'purge_old_attempt_data fixture: pass (%)', purge_result;
end $$;

do $$
begin
  if has_function_privilege('anon', 'public.purge_old_attempt_data(integer)'::regprocedure, 'execute')
     or has_function_privilege('authenticated', 'public.purge_old_attempt_data(integer)'::regprocedure, 'execute') then
    raise exception 'purge_old_attempt_data must not be executable by browser roles';
  end if;
  if not has_function_privilege('service_role', 'public.purge_old_attempt_data(integer)'::regprocedure, 'execute') then
    raise exception 'purge_old_attempt_data must be executable by service_role';
  end if;
end $$;

select 'PASS' as purge_old_attempt_data_verification;
rollback;
