-- Story 6.5 review patch (AD-14 forward-only).
-- 202609051600의 전략별 스냅샷 계약을 직접 INSERT와 자연키 충돌 경계까지 확장한다.
begin;

alter table public.outcome_strategy_rules
  add constraint outcome_strategy_rules_sl_pct_less_than_100_check
  check (sl_pct < 100);

alter table public.candidate_outcome
  add constraint candidate_outcome_sl_pct_less_than_100_check
  check (sl_pct < 100);

create or replace function public.guard_outcome_strategy_snapshot()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  rule_row public.outcome_strategy_rules;
begin
  select * into rule_row
    from public.outcome_strategy_rules
    where strategy = new.strategy;
  if not found then
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  -- A/B/C는 기존 직접 fixture와 correction의 사용자 지정 cutoff_n을 보존하되,
  -- TP/SL 스냅샷은 legacy 규칙과 일치해야 한다. D/E는 세 값 모두 고정한다.
  if new.tp_pct is distinct from rule_row.tp_pct
     or new.sl_pct is distinct from rule_row.sl_pct
     or (new.strategy in ('D', 'E') and new.cutoff_n is distinct from rule_row.cutoff_n) then
    raise exception using message = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH';
  end if;
  return new;
end;
$$;

drop trigger if exists candidate_outcome_strategy_snapshot_guard on public.candidate_outcome;
create trigger candidate_outcome_strategy_snapshot_guard
before insert or update of strategy, tp_pct, sl_pct, cutoff_n on public.candidate_outcome
for each row execute function public.guard_outcome_strategy_snapshot();

create or replace function public.reject_outcome_open_projection_conflict()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.command_type = 'OPEN'
     and new.payload ? 'entry_date'
     and exists (
       select 1
       from public.candidate_outcome co
       where co.ticker = new.ticker
         and co.strategy = new.strategy
         and co.entry_date = (new.payload->>'entry_date')::date
         and co.status in ('TP', 'SL', 'TIMEOUT', 'SUSPENDED', 'DELISTED')
     ) then
    raise exception using message = 'OUTCOME_PROJECTION_CONFLICT';
  end if;
  return new;
end;
$$;

drop trigger if exists outcome_open_projection_conflict_guard on public.outcome_events;
create trigger outcome_open_projection_conflict_guard
before insert on public.outcome_events
for each row execute function public.reject_outcome_open_projection_conflict();

comment on column public.candidate_outcome.tp_pct is
  'OPEN 시점 전략별 익절률 스냅샷. outcome_strategy_rules와 일치해야 한다.';
comment on column public.candidate_outcome.sl_pct is
  'OPEN 시점 전략별 손절률 스냅샷. outcome_strategy_rules와 일치해야 한다.';
comment on table public.outcome_strategy_rules is
  'Story 6.5 전략별 TP/SL/최대보유 권위. candidate_outcome OPEN 스냅샷 검증에 사용한다.';

commit;
