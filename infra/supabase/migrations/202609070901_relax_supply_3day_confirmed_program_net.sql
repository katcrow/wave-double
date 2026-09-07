-- Story 4.1 후속(forward-only, AD-14): 202609022000이 만든
-- supply_3day_investor_net_status_consistency CHECK은 'confirmed'가 foreign_net/
-- institution_net/individual_net/program_net 4컬럼 모두 NOT NULL을 요구했다.
--
-- 그러나 Story 4.1은 t1702만 수집하고 program_net은 t1637(Story 4.2 범위)로 남겨 NULL을
-- 유지해야 한다(스펙 Never 규칙) -- 동시에 t1702 응답이 있으면 investor_net_status='confirmed'로
-- 기록해야 한다(스펙 Always 규칙). 두 규칙을 동시에 만족하려면 program_net을 'confirmed'
-- 필수 컬럼에서 제외해야 한다(Story 4.2가 나중에 같은 행을 UPDATE로 채울 수 있게 열어둔다).
-- pending/missing은 기존과 동일하게 4컬럼 모두 NULL을 요구한다(변경 없음).
begin;

alter table public.supply_3day
  drop constraint supply_3day_investor_net_status_consistency,
  add constraint supply_3day_investor_net_status_consistency check (
    (
      investor_net_status = 'confirmed'
      and foreign_net is not null and institution_net is not null and individual_net is not null
    )
    or
    (
      investor_net_status in ('pending', 'missing')
      and foreign_net is null and institution_net is null and individual_net is null and program_net is null
    )
  );

comment on column public.supply_3day.investor_net_status is
  '투자자별 순매수 컬럼(foreign_net/institution_net/individual_net/program_net)의 상태를 행 단위로
  선언. confirmed: foreign_net/institution_net/individual_net은 NOT NULL(실측값, 0 포함),
  program_net은 t1637(Story 4.2)이 채우기 전까지 독립적으로 NULL일 수 있다(Story 4.1/4.2 분업,
  202609070901). pending: 장중 미확정(재시도 후에도 미채움 포함), 4컬럼 모두 NULL. missing: 조회
  실패로 미수집, 4컬럼 모두 NULL. NULL과 실젯값(0 포함)은 서로 대체하지 않는다.';

commit;
