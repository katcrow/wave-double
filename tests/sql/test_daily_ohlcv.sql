-- Story 2.1 SQL fixture. daily_ohlcv migration까지 적용한다.
begin;
do $$
begin
  if not exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'daily_ohlcv' and column_name = 'pricechk'
  ) then raise exception 'daily_ohlcv.pricechk column missing'; end if;

  if (
    select array_agg(kcu.column_name::text order by kcu.ordinal_position)
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on kcu.constraint_name = tc.constraint_name and kcu.constraint_schema = tc.constraint_schema
    where tc.table_schema = 'public' and tc.table_name = 'daily_ohlcv' and tc.constraint_type = 'PRIMARY KEY'
  ) <> array['ticker', 'trading_day'] then
    raise exception 'daily_ohlcv primary key must be (ticker, trading_day)';
  end if;

  if not (
    select c.relrowsecurity from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relname = 'daily_ohlcv'
  ) then raise exception 'daily_ohlcv RLS must be enabled'; end if;

  -- finite-value guard: NaN/Infinity must be rejected for every price/volume column.
  begin
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('005930', date '2026-09-01', 1, 1, 1, 'NaN'::numeric, 1);
    raise exception 'NaN close must be rejected by finite-value check';
  exception when check_violation then
    null;
  end;

  begin
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('005930', date '2026-09-01', 'NaN'::numeric, 1, 1, 1, 1);
    raise exception 'NaN open must be rejected by finite-value check';
  exception when check_violation then
    null;
  end;

  begin
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('005930', date '2026-09-01', 1, 'NaN'::numeric, 1, 1, 1);
    raise exception 'NaN high must be rejected by finite-value check';
  exception when check_violation then
    null;
  end;

  begin
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('005930', date '2026-09-01', 1, 1, 'NaN'::numeric, 1, 1);
    raise exception 'NaN low must be rejected by finite-value check';
  exception when check_violation then
    null;
  end;

  begin
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('005930', date '2026-09-01', 1, 1, 1, 1, 'NaN'::numeric);
    raise exception 'NaN volume must be rejected by finite-value check';
  exception when check_violation then
    null;
  end;

  -- candidates 하드닝 선례와 동일하게 RLS enable + 정책 0개로 anon/authenticated 접근을 막는다
  -- (Supabase 기본 GRANT는 테이블 권한을 부여하지만, RLS가 있고 정책이 없으면 non-bypassrls
  -- 역할은 어떤 행도 보거나 쓸 수 없다 — service-role만 RLS를 우회한다).
  if exists (
    select 1 from pg_policies where schemaname = 'public' and tablename = 'daily_ohlcv'
  ) then raise exception 'daily_ohlcv must have zero RLS policies (deny-all for anon/authenticated)'; end if;

  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('005930', date '2026-09-01', 100, 110, 90, 105, 1000);
  if (select count(*) from public.daily_ohlcv where ticker = '005930' and trading_day = date '2026-09-01') <> 1 then
    raise exception 'expected row to be inserted';
  end if;
end $$;
rollback;
