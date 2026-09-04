-- Story 6.5 review patch: 미정 전략은 snapshot guard가 가로채지 않고
-- 기존 candidate_outcome_strategy_check가 표준 CHECK 오류를 내도록 한다.
begin;

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
    return new;
  end if;

  if new.tp_pct is distinct from rule_row.tp_pct
     or new.sl_pct is distinct from rule_row.sl_pct
     or (new.strategy in ('D', 'E') and new.cutoff_n is distinct from rule_row.cutoff_n) then
    raise exception using message = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH';
  end if;
  return new;
end;
$$;

commit;
