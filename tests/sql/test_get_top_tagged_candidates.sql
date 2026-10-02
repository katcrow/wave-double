-- get_top_tagged_candidates()의 published snapshot lineage, 태그 상태 독립성,
-- 거래대금 상위 3개와 ticker tie-break, p_exclude_tickers 제외 후 상위 3개 채움 fixture.
begin;

do $$
declare
  key text := 'intraday:2099-09-30:09:00';
  started jsonb;
  run_id uuid;
  test_run_id uuid;
  fence bigint;
  lease uuid;
  result jsonb;
  active_a uuid := gen_random_uuid();
  active_b uuid := gen_random_uuid();
  active_c uuid := gen_random_uuid();
  active_d uuid := gen_random_uuid();
  vanished_only uuid := gen_random_uuid();
  signal_date_mismatch uuid := gen_random_uuid();
  untagged uuid := gen_random_uuid();
  other_day_candidate uuid := gen_random_uuid();
begin
  started := public.start_attempt(key, date '2099-09-30', 'intraday', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  test_run_id := run_id;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;

  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', active_a, 'ticker', '000003', 'name', '상위1', 'trading_value', 300,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_b, 'ticker', '000002', 'name', '동률2', 'trading_value', 200,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_c, 'ticker', '000001', 'name', '동률1', 'trading_value', 200,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_d, 'ticker', '000004', 'name', '상위외', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', vanished_only, 'ticker', '999999', 'name', '소멸전용', 'trading_value', 1000,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', signal_date_mismatch, 'ticker', '888888', 'name', '시그널일불일치', 'trading_value', 1000,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', untagged, 'ticker', '777777', 'name', '무태그상위', 'trading_value', 1100,
        'themes', jsonb_build_array(jsonb_build_object('theme_code', '001', 'theme_name', '반도체', 'average_change_pct', 4.8), jsonb_build_object('theme_code', '002', 'theme_name', '전고체', 'average_change_pct', 2.2)),
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 7,
      'candidate_count', 7, 'excluded_count', 0, 'truncated_count', 0));
  update public.candidates
     set major_sector_name = '테스트 섹터'
   where candidate_id = untagged and attempt_run_id = run_id;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume, adjusted)
  values
    ('777777', date '2099-09-29', 100, 101, 99, 100, 1000, true),
    ('777777', date '2099-09-30', 109, 111, 108, 110, 2000, true);
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (
    untagged, run_id, date '2099-09-30', 'D0', 110, 2000, 10,
    1, 1, -1, 2272727, 'confirmed'
  );
  -- 같은 attempt에 남은 다른 거래일의 stale 행은 current snapshot에서 제외되어야 한다.
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
    values (other_day_candidate, run_id, '666666', '이전거래일', date '2099-09-29', 9999);
  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
    values (other_day_candidate, run_id, 't1859', 1.0);
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status) values
    (active_a, run_id, 'A', date '2099-09-30', 'active'),
    (active_b, run_id, 'B', date '2099-09-30', 'active'),
    (active_b, run_id, 'C', date '2099-09-30', 'vanished'),
    (active_c, run_id, 'D', date '2099-09-30', 'active'),
    (active_d, run_id, 'E', date '2099-09-30', 'active'),
    (vanished_only, run_id, 'F', date '2099-09-30', 'vanished'),
    (signal_date_mismatch, run_id, 'A', date '2099-09-29', 'active');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success');
  -- 이 fixture의 대상은 publish_attempt가 아니라 읽기 RPC이므로, 수급/시장수급
  -- 원천 데이터를 요구하는 publish 경로를 호출하지 않고 published lineage만 구성한다.
  update public.runs
     set status = 'published', finished_at = now()
   where public.runs.run_id = test_run_id;
  update public.logical_runs
     set current_complete_run_id = test_run_id, published_at = now()
   where logical_run_key = key;

  result := public.get_top_tagged_candidates(run_id);
  if jsonb_array_length(result) <> 3 then
    raise exception 'expected 3 top candidates, got %', jsonb_array_length(result);
  end if;
  if (result->0->>'ticker') <> '777777' or (result->1->>'ticker') <> '888888' or (result->2->>'ticker') <> '999999' then
    raise exception 'unexpected trading value/ticker order: %', result;
  end if;
  if not exists (select 1 from jsonb_array_elements(result) e where (e->>'ticker') = '777777') then
    raise exception 'untagged candidate must be included';
  end if;
  if not exists (select 1 from jsonb_array_elements(result) e where (e->>'ticker') = '999999') then
    raise exception 'vanished-only candidate must be included';
  end if;
  if exists (select 1 from jsonb_array_elements(result) e where (e->>'ticker') = '666666') then
    raise exception 'different trading_day candidate must be excluded';
  end if;
  if (result->0->>'candidate_id') <> untagged::text
     or (result->0->>'name') <> '무태그상위'
     or (result->0->>'trading_value') <> '1100' then
    raise exception 'candidate payload fields are not preserved: %', result->0;
  end if;
  if not (result->0 ? 'change_pct')
     or not (result->0 ? 'major_sector_name')
     or not (result->0 ? 'program_buy_value') then
    raise exception 'candidate detail fields are missing: %', result->0;
  end if;
  if (result->0->>'change_pct')::numeric <> 10
     or (result->0->>'major_sector_name') <> '테스트 섹터'
     or (result->0->>'program_buy_value')::numeric <> 2.5 then
    raise exception 'candidate detail fields are not calculated or preserved: %', result->0;
  end if;
  if jsonb_array_length(result->0->'themes') <> 2
     or (result->0->'themes'->0->>'theme_code') <> '001'
     or (result->0->'themes'->0->>'theme_name') <> '반도체'
     or (result->0->'themes'->0->>'average_change_pct')::numeric <> 4.8
     or (result->0->'themes'->1->>'theme_code') <> '002'
     or (result->0->'themes'->1->>'theme_name') <> '전고체'
     or (result->0->'themes'->1->>'average_change_pct')::numeric <> 2.2 then
    raise exception 'candidate themes are not returned in strength order: %', result->0->'themes';
  end if;
  if not exists (select 1 from jsonb_array_elements(result) e where e->>'ticker' = '888888' and e->'themes' = '[]'::jsonb) then
    raise exception 'candidate without themes must return an empty theme array';
  end if;
  if exists (select 1 from jsonb_array_elements(result) e where (e->>'attempt_run_id')::uuid <> run_id or (e->>'trading_day') <> '2099-09-30') then
    raise exception 'snapshot lineage is not preserved';
  end if;
  if public.get_top_tagged_candidates(gen_random_uuid()) <> '[]'::jsonb then
    raise exception 'nonexistent p_run_id must return an empty array';
  end if;
end $$;

do $$
declare
  key text := 'intraday:2099-10-01:09:00';
  started jsonb;
  run_id uuid;
  test_run_id uuid;
  fence bigint;
  lease uuid;
  candidate_id uuid := gen_random_uuid();
  untagged_candidate_id uuid := gen_random_uuid();
  result jsonb;
begin
  started := public.start_attempt(key, date '2099-10-01', 'intraday', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  test_run_id := run_id;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', candidate_id, 'ticker', '000010', 'name', '소멸만', 'trading_value', 500,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', untagged_candidate_id, 'ticker', '000011', 'name', '무태그만', 'trading_value', 400,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 2,
      'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values (candidate_id, run_id, 'A', date '2099-10-01', 'vanished');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success');
  update public.runs
     set status = 'published', finished_at = now()
   where public.runs.run_id = test_run_id;
  update public.logical_runs
     set current_complete_run_id = test_run_id, published_at = now()
   where logical_run_key = key;

  result := public.get_top_tagged_candidates(run_id);
  if jsonb_array_length(result) <> 2
     or (result->0->>'ticker') <> '000010'
     or (result->1->>'ticker') <> '000011' then
    raise exception 'no-active-tag snapshot must return both candidates, got %', result;
  end if;

  -- 제외 대상이 후보에 없으면 두 모드의 결과가 같다.
  if public.get_top_tagged_candidates(run_id, array['005930', '000660']) <> result then
    raise exception 'exclusion of absent tickers must not change result, got %',
      public.get_top_tagged_candidates(run_id, array['005930', '000660']);
  end if;
end $$;

do $$
declare
  key text := 'intraday:2099-10-02:09:00';
  started jsonb;
  run_id uuid;
  test_run_id uuid;
  fence bigint;
  lease uuid;
  result jsonb;
begin
  started := public.start_attempt(key, date '2099-10-02', 'intraday', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  test_run_id := run_id;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', gen_random_uuid(), 'ticker', '005930', 'name', '삼성전자', 'trading_value', 500,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', gen_random_uuid(), 'ticker', '000660', 'name', 'SK하이닉스', 'trading_value', 400,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', gen_random_uuid(), 'ticker', '035420', 'name', 'NAVER', 'trading_value', 300,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', gen_random_uuid(), 'ticker', '051910', 'name', 'LG화학', 'trading_value', 200,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', gen_random_uuid(), 'ticker', '068270', 'name', '셀트리온', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('c', 64), 'original_count', 5,
      'candidate_count', 5, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  update public.runs
     set status = 'published', finished_at = now()
   where public.runs.run_id = test_run_id;
  update public.logical_runs
     set current_complete_run_id = test_run_id, published_at = now()
   where logical_run_key = key;

  -- p_run_id만 넘기는 기존 호출은 제외 없이 상위 3개를 반환한다.
  result := public.get_top_tagged_candidates(run_id);
  if jsonb_array_length(result) <> 3
     or (result->0->>'ticker') <> '005930'
     or (result->1->>'ticker') <> '000660'
     or (result->2->>'ticker') <> '035420' then
    raise exception 'default call must keep previous top 3, got %', result;
  end if;

  -- 제외 대상은 limit 3 전에 빠져 다음 순위가 채워진다.
  result := public.get_top_tagged_candidates(run_id, array['005930', '000660']);
  if jsonb_array_length(result) <> 3
     or (result->0->>'ticker') <> '035420'
     or (result->1->>'ticker') <> '051910'
     or (result->2->>'ticker') <> '068270' then
    raise exception 'excluded tickers must be removed before limit 3, got %', result;
  end if;

  -- NULL 배열은 빈 배열과 같게 취급한다.
  result := public.get_top_tagged_candidates(run_id, null);
  if jsonb_array_length(result) <> 3 or (result->0->>'ticker') <> '005930' then
    raise exception 'null exclude array must behave like empty array, got %', result;
  end if;

  -- 배열 안의 NULL 원소는 무시하고 나머지 제외만 적용한다.
  result := public.get_top_tagged_candidates(run_id, array['005930', null]);
  if jsonb_array_length(result) <> 3 or (result->0->>'ticker') <> '000660' then
    raise exception 'null element must not empty the result, got %', result;
  end if;

  -- 제외 후 남은 후보가 3개 미만이면 남은 후보만 반환한다.
  result := public.get_top_tagged_candidates(run_id, array['005930', '000660', '035420', '051910']);
  if jsonb_array_length(result) <> 1 or (result->0->>'ticker') <> '068270' then
    raise exception 'few remaining candidates must be returned as-is, got %', result;
  end if;
end $$;

rollback;
