-- 전략 I(음봉수급쌍끌이) 추가 (2026-09-16, Neo 요청 story 없이 직접 적용).
-- docs 없음 — 전략 A~F/G/H와 달리 백테스트 불가(국면 데이터 t1702가 백테스트 데이터셋에 없어
-- 운영 수동 확인 전용 stage apps/batch/strategy_i_stage.py가 16:00~20:00 KST 배치에서만
-- candidate_tags에 태그를 기록한다).
-- 따라서 outcome 파이프라인(emit_open_command/outcome_strategy_rules/outcome_events/
-- candidate_outcome)은 대상이 아니며(candidate_tags 외 CHECK 제약 변화 없음),
-- 202609071000/202609080900/202609151700 선례의 drop/add constraint -> comment 갱신 패턴만
-- candidate_tags에 적용한다.
begin;

-- 1) candidate_tags.strategy CHECK을 A-H -> A-I로 확장한다.
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
      and pg_get_constraintdef(c.oid) like '%''H''%'
      and pg_get_constraintdef(c.oid) not like '%''I''%'
  ) then
    raise exception 'candidate_tags_strategy_check old constraint precondition failed';
  end if;
end $$;

alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check;

alter table public.candidate_tags
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'));

-- 2) comment 갱신.
comment on table public.candidate_tags is
  '전략 A/B/C/D/E/F/G/H/I 시그널 태깅 이력(2026-09-16 I 추가). I는 백테스트 불가(음봉+외국인·기관 쌍끌이 수급)로 candidate_tags에만 기록되고 outcome 파이프라인에서는 제외된다. attempt-scoped(AD-19), candidates에 합성키 FK.';

commit;