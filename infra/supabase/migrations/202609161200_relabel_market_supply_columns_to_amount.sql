-- market_supply 컬럼이 t1601/t1631을 수량(gubun1=1, volume) 대신 금액(gubun1=2, value)
-- 기준으로 수집하도록 배치 adapter를 바꿈에 따라 컬럼 주석을 맞춘다.
-- 컬럼 타입(numeric)과 제약조건은 그대로이며, 값의 의미만 수량(주)에서
-- 금액(억원)으로 바뀐다. 배포 시점 이전에 수집된 과거 행은 여전히 수량 기준이다.

comment on column public.market_supply.foreign_net is 't1601 svolume_17(금액, gubun1=2) 외국인 순매수, 억원 단위.';
comment on column public.market_supply.institution_net is 't1601 svolume_18(금액, gubun1=2) 기관계 순매수, 억원 단위.';
comment on column public.market_supply.individual_net is 't1601 svolume_08(금액, gubun1=2) 개인 순매수, 억원 단위.';
comment on column public.market_supply.program_net is 't1631 전체 행 value(금액) 프로그램 순매수, 억원 단위.';
