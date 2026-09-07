-- Story 7.2 (AD-14 forward-only): candidate_tags가 전략 F 태그도 저장하도록
-- 기존 CHECK 제약만 확장한다. 기존 A/B/C/D/E 행·유일성·합성 FK·RLS는 유지한다.
-- 202609051400_expand_candidate_tags_strategy_check.sql(C -> D/E 확장)과
-- 202609051500_finalize_candidate_tags_strategy_contract.sql이 세운 D/E 선례와
-- 동일한 사전조건 검증 → drop/add constraint → comment 갱신 패턴을 그대로 따른다.
-- ALTER TABLE ... ADD CONSTRAINT는 기존 행 전체를 재검증하지만, 이 migration을
-- 작성한 시점 기준 production candidate_tags는 비어 있었으므로 lock/scan 비용은
-- 무시할 수준이다.
begin;

do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'candidate_tags'
      and c.conname = 'candidate_tags_strategy_check'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%strategy%'
      and pg_get_constraintdef(c.oid) like '%''A''%'
      and pg_get_constraintdef(c.oid) like '%''B''%'
      and pg_get_constraintdef(c.oid) like '%''C''%'
      and pg_get_constraintdef(c.oid) like '%''D''%'
      and pg_get_constraintdef(c.oid) like '%''E''%'
      and pg_get_constraintdef(c.oid) not like '%''F''%'
  ) then
    raise exception 'candidate_tags_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check;

alter table public.candidate_tags
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F'));

comment on table public.candidate_tags is
  'Story 7.2: 전략 A/B/C/D/E/F 시그널 태깅 이력. attempt-scoped(AD-19), candidates에 합성키 FK.';

comment on function public.get_today_candidate_cards(uuid) is
  'Story 2.7/2.8/6.3/7.2: candidate_tags.status가 active 또는 vanished인 후보를 카드 뷰모델 원시 행으로 반환한다. strategies는 active 태그만 정렬된 A/B/C/D/E/F 배열, vanished_strategies는 vanished 태그만 정렬된 배열(둘 다 빈 배열 가능, 둘 다 비어있는 행은 존재하지 않음 -- INNER JOIN 조건). supply_partial_missing은 D0 슬롯의 investor_net_status가 pending/missing일 때만 true(D0 행 자체가 없으면 false). D0 슬롯이 후보당 여러 행 누적돼 있어도 trading_day 기준 최신 1행만 반영해 카드 중복을 방지한다.';

commit;
