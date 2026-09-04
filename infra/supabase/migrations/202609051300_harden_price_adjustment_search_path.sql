-- Epic 3 acceptance remediation: 상수 함수의 search_path 고정.
-- 함수 본문은 pg_catalog의 numeric cast만 사용하므로 public 객체 탐색이 필요 없다.
begin;

alter function public.price_adjustment_gap_threshold()
  set search_path = pg_catalog;

commit;
