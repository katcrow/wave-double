-- Supabase SQL fixture for Story 1.8.
-- 실행 전 202609020000_create_dashboard_snapshot.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

create function public.__fixture_seed_market_supply(p_run_id uuid)
returns void language sql as $$
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  )
  select p_run_id, m.market, l.trading_day, 1, 2, 3, 4
  from public.runs r
  join public.logical_runs l on l.logical_run_key = r.logical_run_key
  cross join (values ('KOSPI'::text), ('KOSDAQ'::text)) m(market)
  where r.run_id = p_run_id
  on conflict (attempt_run_id, market, trading_day) do nothing;
$$;

-- 시나리오 1: 첫 발행 이전 -- no_snapshot=true, result_code='NO_SNAPSHOT', complete_snapshot=null.
do $$
declare snapshot jsonb;
begin
  snapshot := public.get_dashboard_snapshot();
  if (snapshot->>'no_snapshot')::boolean is not true then raise exception 'expected no_snapshot=true on empty db'; end if;
  if snapshot->>'result_code' <> 'NO_SNAPSHOT' then raise exception 'expected result_code=NO_SNAPSHOT on empty db'; end if;
  if snapshot->'complete_snapshot' <> 'null'::jsonb then raise exception 'expected complete_snapshot=null on empty db'; end if;
  if snapshot->'latest_attempt' <> 'null'::jsonb then raise exception 'expected latest_attempt=null on empty db'; end if;
  if snapshot->'available_partial_sections' <> '[]'::jsonb then
    raise exception 'expected no available partial sections on empty db';
  end if;
  if snapshot->'missing_sections' <> '["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"]'::jsonb then
    raise exception 'expected all five sections missing on empty db (candidates included)';
  end if;
end $$;

-- 시나리오 2: 정상 발행 존재 -- complete_snapshot에 candidates section만 포함, available_partial_sections=['candidates'].
-- premarket을 사용한다: close는 canonical_success_run_id 고정으로 재발행이 replay되어 시나리오 3의 "새 attempt"를 만들 수 없다.
do $$
declare
  key text := 'premarket:2099-02-01'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  snapshot jsonb;
begin
  started := public.start_attempt(key, date '2099-02-01', 'premarket', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '005930', 'name', 'Samsung', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', 'h1', 'original_count', 1, 'excluded_count', 0, 'truncated_count', 0, 'candidate_count', 1));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  -- Story 2.5: tags stage가 candidate_tags를 채운 뒤 success로 종결되어야 publish_attempt가 통과한다.
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (candidate_id, attempt_id, 'A', date '2099-02-01', '{"batch_kind": "premarket"}'::jsonb);
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 1));
  -- Story 4.1: supply_3day stage가 success여야 publish_attempt가 통과한다.
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success', jsonb_build_object('row_count', 0));
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success', jsonb_build_object('row_count', 0));
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);
  -- 트랜잭션 내내 now()가 고정되므로, 시나리오 간 started_at 동률로 latest_attempt 정렬이 우연에 기대지 않도록 명시 설정한다.
  update public.runs set started_at = timestamptz '2099-02-01 00:00:00+00' where run_id = attempt_id;

  -- Story 3.3 review patch: premarket 발행은 outcome 생성 루프를 아예 타지 않으므로(AD-15), stage_status의
  -- outcome_tracking 원시 컬럼이 'pending'으로 그대로 남아있는지 직접 확인한다(missing_sections를 통한 간접
  -- 확인만으로는 이 raw 컬럼 값 자체를 증명하지 못한다).
  if (select stage_status->>'outcome_tracking' from public.runs where run_id = attempt_id) <> 'pending' then
    raise exception 'expected outcome_tracking to remain pending for a premarket publish, got %',
      (select stage_status->>'outcome_tracking' from public.runs where run_id = attempt_id);
  end if;

  snapshot := public.get_dashboard_snapshot();
  if (snapshot->>'no_snapshot')::boolean is not false then raise exception 'expected no_snapshot=false after publish'; end if;
  if snapshot->'complete_snapshot'->>'run_id' <> attempt_id::text then raise exception 'complete_snapshot did not point at published run'; end if;
  if (snapshot->'complete_snapshot'->'sections'->'candidates'->>'candidate_count')::integer <> 1 then
    raise exception 'expected candidate_count=1 in complete_snapshot';
  end if;
  if (snapshot->'complete_snapshot'->'sections'->'tags'->>'tag_count')::integer <> 1 then
    raise exception 'expected tag_count=1 in complete_snapshot';
  end if;
  if snapshot->'available_partial_sections' <> '["candidates", "tags", "supply_3day", "market_supply"]'::jsonb then
    raise exception 'expected available_partial_sections=[candidates, tags, supply_3day, market_supply], got %', snapshot->'available_partial_sections';
  end if;
  if snapshot->'missing_sections' <> '["outcome_tracking"]'::jsonb then
    raise exception 'expected only outcome_tracking missing after publish, got %', snapshot->'missing_sections';
  end if;
  if (snapshot->'complete_snapshot'->'sections'->'supply_3day'->>'row_count')::integer <> 0 then
    raise exception 'expected supply_3day.row_count=0 in complete_snapshot';
  end if;
end $$;

-- 시나리오 3: 최신 attempt가 실패 -- latest_attempt는 새 attempt를 반영하되 complete_snapshot은 이전 published run 유지(stale).
do $$
declare
  key text := 'premarket:2099-02-01'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  prior_complete_run_id uuid;
  snapshot jsonb;
begin
  select (get_dashboard_snapshot()->'complete_snapshot'->>'run_id')::uuid into prior_complete_run_id;

  started := public.start_attempt(key, date '2099-02-01', 'premarket', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'failed');
  update public.runs set started_at = timestamptz '2099-02-01 00:00:01+00' where run_id = attempt_id;

  snapshot := public.get_dashboard_snapshot();
  if (snapshot->'latest_attempt'->>'run_id')::uuid <> attempt_id then raise exception 'latest_attempt did not track new failed attempt'; end if;
  if snapshot->'latest_attempt'->>'status' <> 'failed' then raise exception 'expected latest_attempt.status=failed'; end if;
  if (snapshot->'complete_snapshot'->>'run_id')::uuid <> prior_complete_run_id then
    raise exception 'complete_snapshot should remain stale on the prior published run';
  end if;
end $$;

-- 시나리오 4: partial attempt 존재 -- latest_partial_run_id가 latest_attempt와 같은 logical_run_key 기준으로 별도 반환되고 current_complete_run_id는 그대로.
do $$
declare
  key text := 'intraday:2099-02-02:10:00'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  snapshot jsonb;
begin
  started := public.start_attempt(key, date '2099-02-02', 'intraday', 'schedule', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'partial', '{}'::jsonb, 3);
  update public.runs set started_at = timestamptz '2099-02-02 00:00:00+00' where run_id = attempt_id;

  snapshot := public.get_dashboard_snapshot();
  if (snapshot->'latest_attempt'->>'run_id')::uuid <> attempt_id then raise exception 'latest_attempt did not track the newest (intraday partial) attempt'; end if;
  if (snapshot->>'latest_partial_run_id')::uuid <> attempt_id then raise exception 'expected latest_partial_run_id to reflect the partial attempt'; end if;
  if snapshot->'complete_snapshot' is null or snapshot->'complete_snapshot' = 'null'::jsonb then
    raise exception 'complete_snapshot should not disappear due to an unrelated partial attempt';
  end if;
  if (snapshot->>'unprocessed_items')::integer <> 3 then raise exception 'expected unprocessed_items to reflect latest_attempt.unprocessed_count'; end if;
end $$;

-- 시나리오 5: 브라우저(anon) 조회 -- candidates 원본 행은 RLS로 차단되고, get_dashboard_snapshot()만
-- security definer로 그 잠긴 테이블을 집계해 candidate_count를 안전하게 노출한다(AD-7, 리뷰 발견 patch).
set local role anon;

do $$
declare direct_row_count integer;
begin
  select count(*) into direct_row_count from public.candidates;
  if direct_row_count <> 0 then raise exception 'anon should not be able to read candidates rows directly via RLS'; end if;
end $$;

do $$
declare direct_row_count integer;
begin
  select count(*) into direct_row_count from public.candidate_tags;
  if direct_row_count <> 0 then raise exception 'anon should not be able to read candidate_tags rows directly via RLS'; end if;
end $$;

do $$
declare snapshot jsonb;
begin
  snapshot := public.get_dashboard_snapshot();
  if snapshot is null then raise exception 'anon should be able to call get_dashboard_snapshot via RLS-allowed SELECT'; end if;
  if snapshot->'complete_snapshot'->>'logical_run_key' <> 'premarket:2099-02-01' then
    raise exception 'anon-visible complete_snapshot should still point at the published premarket run';
  end if;
  if (snapshot->'complete_snapshot'->'sections'->'candidates'->>'candidate_count')::integer <> 1 then
    raise exception 'security definer aggregation should still report candidate_count=1 for anon despite RLS lockout on candidates';
  end if;
  if (snapshot->'complete_snapshot'->'sections'->'tags'->>'tag_count')::integer <> 1 then
    raise exception 'security definer aggregation should still report tag_count=1 for anon despite RLS lockout on candidate_tags';
  end if;
end $$;

do $$
declare caught boolean := false;
begin
  begin
    perform public.write_candidates(gen_random_uuid(), 1, gen_random_uuid(), '[]'::jsonb,
      jsonb_build_object('original_count', 0, 'excluded_count', 0, 'truncated_count', 0, 'candidate_count', 0));
  exception when others then caught := true;
  end;
  if not caught then raise exception 'anon should not have execute privilege on write_candidates'; end if;
end $$;

reset role;

-- 시나리오 6 (Story 3.3): close 발행 + 활성 태그 1건 -- complete_snapshot.sections.outcome_tracking이
-- 채워지고 missing_sections에서 outcome_tracking이 빠진다.
do $$
declare
  key text := 'close:2099-02-03'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  snapshot jsonb;
begin
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZSNAP1', date '2099-02-03', 100, 105, 99, 101, 1000)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-02-03', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', 'ZZSNAP1', 'name', 'Snapshot Test', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('d', 64), 'original_count', 1, 'excluded_count', 0, 'truncated_count', 0, 'candidate_count', 1));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, attempt_id, 'A', date '2099-02-03');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 1));
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success', jsonb_build_object('row_count', 0));
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success', jsonb_build_object('row_count', 0));
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);
  update public.runs set started_at = timestamptz '2099-02-03 00:00:00+00' where run_id = attempt_id;
  -- 트랜잭션 내내 now()가 고정되어 시나리오 2의 published_at과 동률이 나므로, 이 시나리오가
  -- 최신 complete_snapshot으로 선택되도록 published_at을 명시적으로 이후 시각으로 못박는다
  -- (get_dashboard_snapshot()의 tie-break는 published_at desc, 다음 logical_run_key desc).
  update public.logical_runs set published_at = timestamptz '2099-02-03 00:00:00+00' where logical_run_key = key;

  snapshot := public.get_dashboard_snapshot();
  if snapshot->'complete_snapshot'->>'run_id' <> attempt_id::text then raise exception 'complete_snapshot did not point at the close publish'; end if;
  if (snapshot->'complete_snapshot'->'sections'->'outcome_tracking'->>'open_count')::integer <> 1 then
    raise exception 'expected outcome_tracking.open_count=1 in complete_snapshot, got %', snapshot->'complete_snapshot'->'sections'->'outcome_tracking';
  end if;
  if snapshot->'available_partial_sections' <> '["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"]'::jsonb then
    raise exception 'expected available_partial_sections to include supply_3day, market_supply, and outcome_tracking, got %', snapshot->'available_partial_sections';
  end if;
  if snapshot->'missing_sections' <> '[]'::jsonb then
    raise exception 'expected no missing sections after market supply success, got %', snapshot->'missing_sections';
  end if;
end $$;

-- 시나리오 7 (Story 3.3 review patch): close 발행 + 활성 태그 0건 -- 빈 루프도 outcome_tracking='success'로
-- 종결되므로(test_run_lineage.sql의 close:2099-01-02 패턴 참고), complete_snapshot.sections.outcome_tracking.open_count가
-- null/누락이 아니라 명시적으로 0이어야 하고, 그럼에도 missing_sections에서는 제외되어야 한다.
do $$
declare
  key text := 'close:2099-02-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  snapshot jsonb;
begin
  started := public.start_attempt(key, date '2099-02-04', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 0));
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success', jsonb_build_object('row_count', 0));
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success', jsonb_build_object('row_count', 0));
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);
  update public.runs set started_at = timestamptz '2099-02-04 00:00:00+00' where run_id = attempt_id;
  -- 시나리오 6과 published_at 동률을 피해 이 시나리오가 최신 complete_snapshot으로 선택되게 한다.
  update public.logical_runs set published_at = timestamptz '2099-02-04 00:00:00+00' where logical_run_key = key;

  if (select stage_status->>'outcome_tracking' from public.runs where run_id = attempt_id) <> 'success' then
    raise exception 'expected outcome_tracking=success for close publish with zero active tags';
  end if;

  snapshot := public.get_dashboard_snapshot();
  if snapshot->'complete_snapshot'->>'run_id' <> attempt_id::text then raise exception 'complete_snapshot did not point at the tag-less close publish'; end if;
  if not (snapshot->'complete_snapshot'->'sections'->'outcome_tracking' ? 'open_count') then
    raise exception 'expected outcome_tracking.open_count key to be present, got %', snapshot->'complete_snapshot'->'sections'->'outcome_tracking';
  end if;
  if snapshot->'complete_snapshot'->'sections'->'outcome_tracking'->'open_count' = 'null'::jsonb then
    raise exception 'expected outcome_tracking.open_count to be 0, not null';
  end if;
  if (snapshot->'complete_snapshot'->'sections'->'outcome_tracking'->>'open_count')::integer <> 0 then
    raise exception 'expected outcome_tracking.open_count=0 for zero active tags, got %', snapshot->'complete_snapshot'->'sections'->'outcome_tracking';
  end if;
  if snapshot->'missing_sections' <> '[]'::jsonb then
    raise exception 'expected no missing sections even with zero active tags, got %', snapshot->'missing_sections';
  end if;
end $$;

rollback;
