-- 실전 조사(2026-09-14): reject_outcome_open_projection_conflict() 트리거가
-- new.payload->>'entry_date'를 검증 없이 ::date로 캐스팅해서, outcome_events에
-- 잘못된 entry_date를 가진 OPEN 이벤트를 append하려는 순간 raw Postgres 오류
-- ("invalid input syntax for type date")로 즉시 죽는다. append-only 장부 자체는
-- 이 정도 형식 오류로 insert를 막을 이유가 없다 -- 형식 검증은
-- rebuild_outcome_projection()이 이미 명확한 'REBUILD: OPEN payload invalid
-- entry_date' 메시지로 책임진다(202609052000). 이 트리거의 역할은 오직 "이미 종결된
-- entry_date와 충돌하는 재오픈"을 막는 것이므로, 파싱 불가능한 날짜는 충돌 여부를
-- 판단할 수 없다는 뜻이지 충돌이 있다는 뜻이 아니다 -- 캐스팅 실패 시 조용히 통과시켜
-- rebuild가 정상 오류 경로로 처리하게 한다.
begin;

create or replace function public.reject_outcome_open_projection_conflict()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_entry_date date;
begin
  if new.command_type = 'OPEN' and new.payload ? 'entry_date' then
    begin
      v_entry_date := (new.payload->>'entry_date')::date;
    exception when others then
      return new;
    end;
    if exists (
      select 1
      from public.candidate_outcome co
      where co.ticker = new.ticker
        and co.strategy = new.strategy
        and co.entry_date = v_entry_date
        and co.status in ('TP', 'SL', 'TIMEOUT', 'SUSPENDED', 'DELISTED')
    ) then
      raise exception using message = 'OUTCOME_PROJECTION_CONFLICT';
    end if;
  end if;
  return new;
end;
$$;

revoke execute on function public.reject_outcome_open_projection_conflict() from public, anon, authenticated;

commit;
