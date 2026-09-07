-- Supabase SQL fixture for Stories 2.5 and 6.3.
-- 실행 전 저장소의 모든 migration을 순서대로 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

do $$
<<candidate_tag_fixture>>
declare
  key text := 'close:2099-04-01'; started jsonb; run_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  other_run_id uuid;
  caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-04-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');

  -- AC1: 정상 삽입 -- PK/FK/기본값이 예상대로 적용된다.
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (candidate_id, run_id, 'A', date '2099-04-01', '{"batch_kind": "close"}'::jsonb);
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 1 then
    raise exception 'candidate_tags row was not inserted';
  end if;
  if (select status from public.candidate_tags where attempt_run_id = run_id and strategy = 'A') <> 'active' then
    raise exception 'expected default status=active';
  end if;

  -- 다중 태그(A∩B 등): 같은 후보에 다른 전략은 허용된다.
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, run_id, 'B', date '2099-04-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values
      (candidate_id, run_id, 'C', date '2099-04-01'),
      (candidate_id, run_id, 'D', date '2099-04-01'),
      (candidate_id, run_id, 'E', date '2099-04-01');
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 5 then
    raise exception 'expected five A/B/C/D/E tags for the same candidate';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id and strategy in ('A', 'B', 'C')) <> 3 then
    raise exception 'legacy A/B/C strategy filter semantics changed';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id and strategy in ('D', 'E')) <> 2 then
    raise exception 'expected D and E strategies to be accepted';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id and strategy in ('D', 'E') and status = 'active') <> 2 then
    raise exception 'expected D/E tags to receive status=active by default';
  end if;

  -- UNIQUE(candidate_id, strategy, attempt_run_id) 위반 거부.
  begin
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
      values (candidate_id, run_id, 'A', date '2099-04-01');
  exception when unique_violation then caught := true;
  end;
  if not caught then raise exception 'duplicate (candidate_id, strategy, attempt_run_id) was accepted'; end if;

  -- 신규 전략에도 동일한 attempt-scoped UNIQUE가 적용된다.
  caught := false;
  begin
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
      values (candidate_id, run_id, 'D', date '2099-04-01');
  exception when unique_violation then caught := true;
  end;
  if not caught then raise exception 'duplicate D tag was accepted'; end if;

  -- FK(candidate_id, attempt_run_id) -> candidates 위반 거부: 존재하지 않는 attempt_run_id 조합.
  started := public.start_attempt('close:2099-04-02', date '2099-04-02', 'close', 'manual', 300);
  other_run_id := (started->>'run_id')::uuid;
  caught := false;
  begin
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
      values (candidate_id, other_run_id, 'A', date '2099-04-02');
  exception when foreign_key_violation then caught := true;
  end;
  if not caught then raise exception 'candidate_tags FK(candidate_id, attempt_run_id) was not enforced'; end if;

  -- Story 7.2: strategy F도 허용된다.
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, run_id, 'F', date '2099-04-01');
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 6 then
    raise exception 'expected six A/B/C/D/E/F tags for the same candidate';
  end if;
  if (select status from public.candidate_tags where attempt_run_id = run_id and strategy = 'F') <> 'active' then
    raise exception 'expected F tag to receive status=active by default';
  end if;

  -- 신규 전략 F에도 동일한 attempt-scoped UNIQUE가 적용된다.
  caught := false;
  begin
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
      values (candidate_id, run_id, 'F', date '2099-04-01');
  exception when unique_violation then caught := true;
  end;
  if not caught then raise exception 'duplicate F tag was accepted'; end if;

  -- strategy는 A|B|C|D|E|F만 허용.
  caught := false;
  begin
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
      values (candidate_id, run_id, 'G', date '2099-04-01');
  exception when check_violation then caught := true;
  end;
  if not caught then raise exception 'invalid strategy value was accepted'; end if;

  -- RLS는 활성화되어 있으나 정책이 없다(deny-all, candidates 패턴과 동일).
  if not (select c.relrowsecurity from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relname = 'candidate_tags') then
    raise exception 'candidate_tags RLS must be enabled';
  end if;
  if exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'candidate_tags') then
    raise exception 'candidate_tags deny-all RLS contract must not gain a policy';
  end if;

  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 5));
  if (select (r.stage_results->'tags'->>'tagged_count')::integer from public.runs r where r.run_id = candidate_tag_fixture.run_id) <> 5 then
    raise exception 'expected tags stage_result tagged_count=5';
  end if;
end $$;

-- Story 2.5 코드 리뷰 발견(high) 수정 커버리지: tags stage가 failed로 종결되면
-- runs.status/finished_at이 candidates가 남긴 'ready_to_publish'에 머물지 않고
-- 'failed'로 반영되어야 한다(write_stage 202609021900).
do $$
declare
  key text := 'close:2099-04-03'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  run_status text; run_finished_at timestamptz;
begin
  started := public.start_attempt(key, date '2099-04-03', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');

  select r.status into run_status from public.runs r where r.run_id = attempt_id;
  if run_status <> 'ready_to_publish' then raise exception 'expected runs.status=ready_to_publish after candidates success'; end if;

  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'failed',
    jsonb_build_object('result_code', 'CANDIDATE_FETCH_FAILED'));

  select r.status, r.finished_at into run_status, run_finished_at from public.runs r where r.run_id = attempt_id;
  if run_status <> 'failed' then raise exception 'expected runs.status=failed after tags stage failed, got %', run_status; end if;
  if run_finished_at is null then raise exception 'expected finished_at to be set after tags stage terminal status'; end if;
end $$;

-- tags stage가 partial로 종결되면 candidates의 'ready_to_publish'를 'partial'로 낮춘다.
do $$
declare
  key text := 'close:2099-04-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  run_status text;
begin
  started := public.start_attempt(key, date '2099-04-04', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'partial',
    jsonb_build_object('result_code', 'PARTIAL_TAGGING'), 1);

  select r.status into run_status from public.runs r where r.run_id = attempt_id;
  if run_status <> 'partial' then raise exception 'expected runs.status=partial after tags stage partial, got %', run_status; end if;
end $$;

rollback;
