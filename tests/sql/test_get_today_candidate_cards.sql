-- Supabase SQL fixture for Story 2.7 코드 리뷰 발견(high) 수정 커버리지.
-- 실행 전 202609022200_fix_get_today_candidate_cards_d0_dedupe.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
--
-- 커버리지:
--  1) 같은 (candidate_id, attempt_run_id)에 D0 행이 2건(다른 trading_day, 다른
--     investor_net_status) 있어도 get_today_candidate_cards()는 해당 후보를 정확히 1개
--     카드로만 반환한다(202609022200 LATERAL dedup 회귀 방지).
--  2) 태그가 없는 후보는 INNER JOIN으로 제외된다.
--  3) D0 행이 아예 없는 후보는 supply_partial_missing=false로 반환된다.
begin;

do $$
declare
  key text := 'close:2099-06-01'; started jsonb; run_id uuid; fence bigint; lease uuid;
  tagged_dup_id uuid := gen_random_uuid();   -- D0 2건, 태그 있음 -- dedup 검증 대상
  untagged_id uuid := gen_random_uuid();      -- 태그 없음 -- INNER JOIN 제외 검증 대상
  no_d0_id uuid := gen_random_uuid();         -- D0 없음, 태그 있음 -- supply_partial_missing=false 검증 대상
  result jsonb;
  dup_cards jsonb;
begin
  started := public.start_attempt(key, date '2099-06-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object(
        'candidate_id', tagged_dup_id, 'ticker', '000010', 'name', '중복테스트', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object(
        'candidate_id', untagged_id, 'ticker', '000020', 'name', '태그없음', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object(
        'candidate_id', no_d0_id, 'ticker', '000030', 'name', 'D0없음', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 3, 'candidate_count', 3, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  -- 태그: tagged_dup_id와 no_d0_id만 active 태그를 받는다. untagged_id는 태그 없음.
  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (tagged_dup_id, run_id, 'A', date '2099-06-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (no_d0_id, run_id, 'B', date '2099-06-01');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 2));

  -- tagged_dup_id: 같은 (candidate_id, attempt_run_id)에 D0 행 2건, 서로 다른 trading_day/investor_net_status.
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
  ) values (
    tagged_dup_id, run_id, date '2099-05-30', 'D0', 10000, 100000, 1.0, 'missing'
  );
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (
    tagged_dup_id, run_id, date '2099-06-01', 'D0', 10500, 110000, 1.5,
    100, 200, -300, 50, 'confirmed'
  );
  -- untagged_id에도 D0 행을 하나 남겨, INNER JOIN 제외가 supply_3day 유무와 무관함을 확인한다.
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct, investor_net_status
  ) values (
    untagged_id, run_id, date '2099-06-01', 'D0', 20000, 200000, 0.5, 'pending'
  );
  -- no_d0_id에는 D0 행을 남기지 않는다(D0 행 자체 부재 -> supply_partial_missing=false 검증).

  result := public.get_today_candidate_cards(run_id);

  -- 태그 없는 후보(untagged_id)는 결과에 없어야 한다(INNER JOIN).
  if jsonb_array_length(result) <> 2 then
    raise exception 'expected exactly 2 cards (tagged_dup_id + no_d0_id), got %', jsonb_array_length(result);
  end if;

  if exists (
    select 1 from jsonb_array_elements(result) e
    where (e->>'candidate_id')::uuid = untagged_id
  ) then
    raise exception 'untagged candidate must be excluded by INNER JOIN on candidate_tags';
  end if;

  -- tagged_dup_id는 D0 행이 2건이어도 카드가 정확히 1개여야 한다(dedup 회귀 방지).
  select jsonb_agg(e) into dup_cards
  from jsonb_array_elements(result) e
  where (e->>'candidate_id')::uuid = tagged_dup_id;

  if jsonb_array_length(dup_cards) <> 1 then
    raise exception 'expected exactly one card for a candidate with two D0 rows, got %', jsonb_array_length(dup_cards);
  end if;

  -- 최신 trading_day(2099-06-01, confirmed)가 반영되어야 하므로 supply_partial_missing=false.
  if (dup_cards->0->>'supply_partial_missing')::boolean <> false then
    raise exception 'expected supply_partial_missing=false from the latest (confirmed) D0 row, got %', dup_cards->0->>'supply_partial_missing';
  end if;

  -- D0 행이 아예 없는 후보(no_d0_id)는 카드가 존재하되 supply_partial_missing=false.
  if not exists (
    select 1 from jsonb_array_elements(result) e
    where (e->>'candidate_id')::uuid = no_d0_id
      and (e->>'supply_partial_missing')::boolean = false
  ) then
    raise exception 'candidate with no D0 row at all must get supply_partial_missing=false';
  end if;
end $$;

rollback;
