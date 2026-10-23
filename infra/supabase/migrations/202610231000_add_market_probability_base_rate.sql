-- 종가배팅 참고확률 v2: 정답 기준을 "익일 고가 > 당일 종가 × 1.005"로 바꾸고
-- 같은 기준의 기본 성공률(base rate)을 함께 저장한다.
-- base rate 컬럼은 nullable이라 기존 v1 행(재계산하지 않음)은 null로 남는다.
begin;

alter table public.market_index_probability
  add column if not exists kospi_base_rate double precision
    check (kospi_base_rate is null or kospi_base_rate between 0 and 1),
  add column if not exists kosdaq_base_rate double precision
    check (kosdaq_base_rate is null or kosdaq_base_rate between 0 and 1);

comment on table public.market_index_probability is
  'Latest successful same-day KOSPI/KOSDAQ probabilities that the next joint trading day high exceeds today''s close by the model target (v2: +0.5%), with same-target weighted base rates (null for v1 rows). Failures do not write this table.';

create or replace function public.upsert_market_index_probability(p_payload jsonb)
returns jsonb language plpgsql security definer set search_path = public as $$
declare written public.market_index_probability; p_trading_day date; p_target_trading_day date;
  p_kospi_probability double precision; p_kosdaq_probability double precision; p_slot time without time zone;
  p_last_success_at timestamptz; p_feature_as_of timestamptz; p_model_version text;
  p_validation_status text; p_input_quality jsonb; p_feature_snapshot jsonb;
  p_kospi_base_rate double precision; p_kosdaq_base_rate double precision;
begin
  -- base rate는 선택 필드다. 없거나 null이면 null로 저장하고, 있으면 JSON 숫자여야 한다.
  if coalesce(jsonb_typeof(p_payload->'kospi_base_rate'), 'null') not in ('null', 'number')
     or coalesce(jsonb_typeof(p_payload->'kosdaq_base_rate'), 'null') not in ('null', 'number') then
    raise exception using message = 'INVALID_MARKET_INDEX_PROBABILITY';
  end if;
  p_trading_day := (p_payload->>'trading_day')::date;
  p_target_trading_day := (p_payload->>'target_trading_day')::date;
  p_kospi_probability := (p_payload->>'kospi_probability')::double precision;
  p_kosdaq_probability := (p_payload->>'kosdaq_probability')::double precision;
  p_kospi_base_rate := (p_payload->>'kospi_base_rate')::double precision;
  p_kosdaq_base_rate := (p_payload->>'kosdaq_base_rate')::double precision;
  p_slot := (p_payload->>'slot')::time;
  p_last_success_at := (p_payload->>'last_success_at')::timestamptz;
  p_feature_as_of := (p_payload->>'feature_as_of')::timestamptz;
  p_model_version := p_payload->>'model_version';
  p_validation_status := p_payload->>'validation_status';
  p_input_quality := p_payload->'input_quality';
  p_feature_snapshot := p_payload->'feature_snapshot';
  if p_trading_day is null or p_target_trading_day is null or p_target_trading_day <= p_trading_day
     or p_kospi_probability is null or p_kospi_probability not between 0 and 1
     or p_kosdaq_probability is null or p_kosdaq_probability not between 0 and 1
     or (p_kospi_base_rate is not null and p_kospi_base_rate not between 0 and 1)
     or (p_kosdaq_base_rate is not null and p_kosdaq_base_rate not between 0 and 1)
     or p_slot is null or p_slot < time '15:00' or p_slot > time '19:00'
     or extract(minute from p_slot)::integer not in (0, 20, 40) or extract(second from p_slot) <> 0
     or (extract(hour from p_slot) = 19 and extract(minute from p_slot) <> 0)
     or p_last_success_at is null or p_feature_as_of is null
     or p_model_version is null or length(btrim(p_model_version)) = 0
     or p_validation_status not in ('experimental', 'validated') then
    raise exception using message = 'INVALID_MARKET_INDEX_PROBABILITY';
  end if;
  insert into public.market_index_probability(
    trading_day, target_trading_day, kospi_probability, kosdaq_probability, kospi_base_rate, kosdaq_base_rate,
    slot, last_success_at, feature_as_of, model_version, validation_status, input_quality, feature_snapshot
  ) values (
    p_trading_day, p_target_trading_day, p_kospi_probability, p_kosdaq_probability, p_kospi_base_rate, p_kosdaq_base_rate,
    p_slot, p_last_success_at, p_feature_as_of, p_model_version, p_validation_status,
    coalesce(p_input_quality, '{}'::jsonb), coalesce(p_feature_snapshot, '{}'::jsonb)
  )
  on conflict (trading_day) do update set
    target_trading_day = excluded.target_trading_day,
    kospi_probability = excluded.kospi_probability,
    kosdaq_probability = excluded.kosdaq_probability,
    kospi_base_rate = excluded.kospi_base_rate,
    kosdaq_base_rate = excluded.kosdaq_base_rate,
    slot = excluded.slot,
    last_success_at = excluded.last_success_at,
    feature_as_of = excluded.feature_as_of,
    model_version = excluded.model_version,
    validation_status = excluded.validation_status,
    input_quality = excluded.input_quality,
    feature_snapshot = excluded.feature_snapshot,
    updated_at = now()
  where excluded.slot > market_index_probability.slot
     or (excluded.slot = market_index_probability.slot and excluded.last_success_at > market_index_probability.last_success_at)
  returning * into written;
  if not found then
    return jsonb_build_object('stored', false, 'reason', 'STALE_OR_DUPLICATE_SLOT');
  end if;
  return jsonb_build_object('stored', true, 'trading_day', written.trading_day, 'slot', written.slot,
    'last_success_at', written.last_success_at);
end $$;

-- returns table의 컬럼이 바뀌므로 create or replace로는 교체할 수 없다.
drop function if exists public.get_latest_market_index_probability();
create function public.get_latest_market_index_probability()
returns table (
  trading_day date, target_trading_day date, kospi_probability double precision,
  kosdaq_probability double precision, kospi_base_rate double precision, kosdaq_base_rate double precision,
  last_success_at timestamptz, feature_as_of timestamptz, model_version text, validation_status text
)
language sql stable security definer set search_path = public as $$
  select p.trading_day, p.target_trading_day, p.kospi_probability, p.kosdaq_probability,
    p.kospi_base_rate, p.kosdaq_base_rate,
    p.last_success_at, p.feature_as_of, p.model_version, p.validation_status
  from public.market_index_probability p order by p.trading_day desc limit 1
$$;

revoke execute on function public.upsert_market_index_probability(jsonb) from public, anon, authenticated;
grant execute on function public.upsert_market_index_probability(jsonb) to service_role;
revoke execute on function public.get_latest_market_index_probability() from public, anon;
grant execute on function public.get_latest_market_index_probability() to anon, authenticated, service_role;

commit;
