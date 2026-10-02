-- Supabase SQL fixture for Story 2.7 코드 리뷰 발견(high) 수정 커버리지.
-- 실행 전 현재 migration(202610021100_sort_candidate_cards_by_strategy_count.sql)까지 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
--
-- 커버리지:
--  1) 같은 (candidate_id, attempt_run_id)에 D0 행이 2건(다른 trading_day, 다른
--     investor_net_status) 있어도 get_today_candidate_cards()는 해당 후보를 정확히 1개
--     카드로만 반환한다(202609022200 LATERAL dedup 회귀 방지).
--  2) 태그가 없는 후보는 INNER JOIN으로 제외된다.
--  3) D0 행이 아예 없는 후보는 supply_partial_missing=false로 반환된다.
--  4) active 전략 수 DESC, 거래대금 DESC, ticker ASC 정렬을 검증한다.
begin;

do $$
declare
  key text := 'close:2099-06-01'; started jsonb; run_id uuid; fence bigint; lease uuid;
  tagged_dup_id uuid := gen_random_uuid();   -- D0 2건, 태그 있음 -- dedup 검증 대상
  untagged_id uuid := gen_random_uuid();      -- 태그 없음 -- INNER JOIN 제외 검증 대상
  no_d0_id uuid := gen_random_uuid();         -- D0 없음, 태그 있음 -- supply_partial_missing=false 검증 대상
  multi_strategy_id uuid := gen_random_uuid(); -- active 전략 3개, 거래대금은 더 작음 -- 다중 전략 우선 검증 대상
  tie_id uuid := gen_random_uuid();           -- active 전략 1개, 거래대금 동률 -- ticker tie-break 검증 대상
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
        'themes', jsonb_build_array(jsonb_build_object('theme_code', '001', 'theme_name', '반도체', 'average_change_pct', 4.8)),
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object(
        'candidate_id', untagged_id, 'ticker', '000020', 'name', '태그없음', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object(
        'candidate_id', no_d0_id, 'ticker', '000030', 'name', 'D0없음', 'trading_value', 200,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object(
        'candidate_id', multi_strategy_id, 'ticker', '000025', 'name', '다중전략', 'trading_value', 50,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object(
        'candidate_id', tie_id, 'ticker', '000040', 'name', '동률테스트', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 5, 'candidate_count', 5, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  -- 태그: tagged_dup_id/no_d0_id/tie_id는 active 1개, multi_strategy_id는 active 3개를 받는다. untagged_id는 태그 없음.
  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (tagged_dup_id, run_id, 'A', date '2099-06-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (no_d0_id, run_id, 'B', date '2099-06-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values
      (multi_strategy_id, run_id, 'A', date '2099-06-01'),
      (multi_strategy_id, run_id, 'B', date '2099-06-01'),
      (multi_strategy_id, run_id, 'C', date '2099-06-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (tie_id, run_id, 'A', date '2099-06-01');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 6));

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
  if jsonb_array_length(result) <> 4 then
    raise exception 'expected exactly 4 cards (tagged_dup_id + no_d0_id + multi_strategy_id + tie_id), got %', jsonb_array_length(result);
  end if;

  if (result->0->>'candidate_id')::uuid <> multi_strategy_id then
    raise exception 'multi-strategy candidate must be first even with lower trading value, got %', result->0->>'candidate_id';
  end if;
  if (result->1->>'candidate_id')::uuid <> no_d0_id
     or (result->2->>'candidate_id')::uuid <> tagged_dup_id
     or (result->3->>'candidate_id')::uuid <> tie_id then
    raise exception 'same active-count candidates must use trading_value DESC then ticker ASC: %', result;
  end if;
  if (result->1->>'trading_value')::numeric <> 200 then
    raise exception 'card must expose candidates.trading_value: %', result->1;
  end if;
  if result->0->'strategies' <> '["A", "B", "C"]'::jsonb then
    raise exception 'multi-strategy candidate must expose all active strategies: %', result->0->'strategies';
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
  if jsonb_array_length(dup_cards->0->'themes') <> 1
     or (dup_cards->0->'themes'->0->>'theme_code') <> '001'
     or (dup_cards->0->'themes'->0->>'theme_name') <> '반도체'
     or (dup_cards->0->'themes'->0->>'average_change_pct')::numeric <> 4.8 then
    raise exception 'candidate themes are missing from today card: %', dup_cards->0->'themes';
  end if;

  -- D0 행이 아예 없는 후보(no_d0_id)는 카드가 존재하되 supply_partial_missing=false.
  if not exists (
    select 1 from jsonb_array_elements(result) e
    where (e->>'candidate_id')::uuid = no_d0_id
      and (e->>'supply_partial_missing')::boolean = false
  ) then
    raise exception 'candidate with no D0 row at all must get supply_partial_missing=false';
  end if;
  if not exists (
    select 1 from jsonb_array_elements(result) e
    where (e->>'candidate_id')::uuid = no_d0_id
      and e->'themes' = '[]'::jsonb
  ) then
    raise exception 'candidate without themes must return an empty theme array';
  end if;

  -- active 태그만 있는 후보(tagged_dup_id, no_d0_id)는 vanished_strategies가 빈 배열이어야 한다.
  if exists (
    select 1 from jsonb_array_elements(result) e
    where (e->>'candidate_id')::uuid in (tagged_dup_id, no_d0_id)
      and e->'vanished_strategies' <> '[]'::jsonb
  ) then
    raise exception 'candidates with only active tags must have empty vanished_strategies';
  end if;
end $$;

-- Story 2.8: 부분 재태깅 -- 후보가 active(A) + vanished(B) 태그를 모두 가지면
-- strategies=["A"], vanished_strategies=["B"]가 함께 반환되고 카드는 정상 노출된다.
-- 완전 소멸(active 태그 0건 + vanished 태그만 존재)해도 카드는 제외되지 않는다.
do $$
declare
  key text := 'close:2099-06-02'; started jsonb; run_id uuid; fence bigint; lease uuid;
  partial_id uuid := gen_random_uuid();  -- A active, B vanished
  fully_vanished_id uuid := gen_random_uuid(); -- vanished만 존재
  active_two_id uuid := gen_random_uuid(); -- A/B active, partial보다 active 수가 많음
  result jsonb;
  partial_card jsonb;
  vanished_card jsonb;
begin
  started := public.start_attempt(key, date '2099-06-02', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', partial_id, 'ticker', '000040', 'name', '부분재태깅', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', fully_vanished_id, 'ticker', '000050', 'name', '완전소멸', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_two_id, 'ticker', '000030', 'name', '다중활성', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('d', 64), 'original_count', 3, 'candidate_count', 3, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values (partial_id, run_id, 'A', date '2099-06-02', 'active');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values
      (partial_id, run_id, 'B', date '2099-06-02', 'vanished'),
      (partial_id, run_id, 'C', date '2099-06-02', 'vanished');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values (fully_vanished_id, run_id, 'D', date '2099-06-02', 'vanished');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values
      (active_two_id, run_id, 'A', date '2099-06-02', 'active'),
      (active_two_id, run_id, 'B', date '2099-06-02', 'active');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 6));

  result := public.get_today_candidate_cards(run_id);

  if jsonb_array_length(result) <> 3 then
    raise exception 'expected exactly 3 cards (partial_id + fully_vanished_id + active_two_id), got %', jsonb_array_length(result);
  end if;

  if (result->0->>'candidate_id')::uuid <> active_two_id
     or (result->1->>'candidate_id')::uuid <> partial_id
     or (result->2->>'candidate_id')::uuid <> fully_vanished_id then
    raise exception 'active strategy count must exclude vanished strategies: %', result;
  end if;

  select e into partial_card from jsonb_array_elements(result) e where (e->>'candidate_id')::uuid = partial_id;
  if partial_card->'strategies' <> '["A"]'::jsonb then
    raise exception 'expected strategies=[A] for partially retagged candidate, got %', partial_card->'strategies';
  end if;
  if partial_card->'vanished_strategies' <> '["B", "C"]'::jsonb then
    raise exception 'expected vanished_strategies=[B,C] for partially retagged candidate, got %', partial_card->'vanished_strategies';
  end if;

  select e into vanished_card from jsonb_array_elements(result) e where (e->>'candidate_id')::uuid = fully_vanished_id;
  if vanished_card is null then
    raise exception 'a candidate with only vanished tags must still be returned as a card';
  end if;
  if vanished_card->'strategies' <> '[]'::jsonb then
    raise exception 'expected strategies=[] for a fully vanished candidate, got %', vanished_card->'strategies';
  end if;
  if vanished_card->'vanished_strategies' <> '["D"]'::jsonb then
    raise exception 'expected vanished_strategies=[D] for a fully vanished candidate, got %', vanished_card->'vanished_strategies';
  end if;
end $$;

rollback;
