-- 종가배팅 참고확률 v2: upsert의 선택 필드 base rate 검증과 최신 조회 반환 컬럼을 검증한다.
begin;

do $$
declare
  base jsonb := jsonb_build_object(
    'trading_day', '2099-01-05', 'target_trading_day', '2099-01-06',
    'kospi_probability', 0.4, 'kosdaq_probability', 0.3, 'slot', '15:20:00',
    'last_success_at', '2099-01-05T06:20:00Z', 'feature_as_of', '2099-01-05T06:20:00Z',
    'model_version', 'historical_conditional_rate_v2', 'validation_status', 'experimental'
  );
  caught boolean;
  stored record;
  latest record;
begin
  -- 범위 밖 base rate는 거부한다.
  caught := false;
  begin
    perform public.upsert_market_index_probability(base || '{"kospi_base_rate": 1.2}');
  exception when others then
    if position('INVALID_MARKET_INDEX_PROBABILITY' in sqlerrm) = 0 then raise; end if;
    caught := true;
  end;
  if not caught then raise exception 'kospi_base_rate 1.2 was accepted'; end if;

  -- 문자열 base rate는 숫자로 캐스팅 가능해도 거부한다.
  caught := false;
  begin
    perform public.upsert_market_index_probability(base || '{"kosdaq_base_rate": "0.5"}');
  exception when others then
    if position('INVALID_MARKET_INDEX_PROBABILITY' in sqlerrm) = 0 then raise; end if;
    caught := true;
  end;
  if not caught then raise exception 'string kosdaq_base_rate was accepted'; end if;

  -- 유효한 base rate는 그대로 저장한다.
  perform public.upsert_market_index_probability(base || '{"kospi_base_rate": 0.25, "kosdaq_base_rate": 0.75}');
  select kospi_base_rate, kosdaq_base_rate into stored
    from public.market_index_probability where trading_day = date '2099-01-05';
  if stored.kospi_base_rate is distinct from 0.25 or stored.kosdaq_base_rate is distinct from 0.75 then
    raise exception 'valid base rates were not stored: % %', stored.kospi_base_rate, stored.kosdaq_base_rate;
  end if;

  -- base rate를 생략한 (v1 호환) payload는 null로 저장하고, 최신 조회가 base rate 컬럼을 반환한다.
  perform public.upsert_market_index_probability(base || jsonb_build_object(
    'trading_day', '2099-01-06', 'target_trading_day', '2099-01-07'));
  select * into latest from public.get_latest_market_index_probability();
  if latest.trading_day <> date '2099-01-06' then
    raise exception 'latest row is not 2099-01-06: %', latest.trading_day;
  end if;
  if latest.kospi_base_rate is not null or latest.kosdaq_base_rate is not null then
    raise exception 'omitted base rates were not stored as null';
  end if;
end
$$;

rollback;
