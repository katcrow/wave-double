-- Story 2.1: 시그널 계산용 장기 일봉 캐시. attempt-scoped가 아니다(PK에 run_id 없음, data-model.md).
-- candidates hardening 선례(202609011700/202609011800)와 동일하게 테이블 생성 + RLS enable(정책 없음)을
-- 한 migration 안에서 적용해 anon/authenticated 접근을 원천 차단한다.
begin;

create table if not exists public.daily_ohlcv (
  ticker text not null check (length(btrim(ticker)) > 0),
  trading_day date not null,
  open numeric not null check (open <> 'NaN'::numeric and open <> 'Infinity'::numeric and open <> '-Infinity'::numeric),
  high numeric not null check (high <> 'NaN'::numeric and high <> 'Infinity'::numeric and high <> '-Infinity'::numeric),
  low numeric not null check (low <> 'NaN'::numeric and low <> 'Infinity'::numeric and low <> '-Infinity'::numeric),
  close numeric not null check (close <> 'NaN'::numeric and close <> 'Infinity'::numeric and close <> '-Infinity'::numeric),
  volume numeric not null check (volume <> 'NaN'::numeric and volume <> 'Infinity'::numeric and volume <> '-Infinity'::numeric),
  adjusted boolean not null default true,
  adjustment_version integer not null default 1,
  pricechk integer,
  primary key (ticker, trading_day)
);

comment on table public.daily_ohlcv is '시그널 계산용 장기 일봉 캐시(최소 120거래일). attempt-scoped가 아니며 정리 대상이 아니다(NFR-4).';
comment on column public.daily_ohlcv.pricechk is 'LS t8410 수정주가반영항목 원본(nullable). Story 2.2 증분 갱신이 채운다 — 초기 적재는 항상 null.';

alter table public.daily_ohlcv enable row level security;

commit;
