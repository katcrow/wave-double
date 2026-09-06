-- Story 6.5 review patch (AD-14 forward-only).
-- 미정 전략은 기존 strategy CHECK가 표준 오류를 내도록 하고, A/B/C의 기존
-- 직접 fixture 및 저장 cutoff_n은 보존한다. D/E는 세 snapshot 값을 모두 고정한다.
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
  if coalesce(current_setting('wave_double.outcome_rule_override_allowed', true), 'off') = 'on' then
    return new;
  end if;

  if tg_op = 'UPDATE'
     and new.strategy is not distinct from old.strategy
     and new.tp_pct is not distinct from old.tp_pct
     and new.sl_pct is not distinct from old.sl_pct
     and new.cutoff_n is not distinct from old.cutoff_n then
    return new;
  end if;

  select * into rule_row
  from public.outcome_strategy_rules
  where strategy = new.strategy
  for share;

  -- F 등 미정 전략은 candidate_outcome_strategy_check가 표준 CHECK 오류를 내도록 한다.
  if not found then
    if new.strategy not in ('A', 'B', 'C', 'D', 'E') then
      return new;
    end if;
    raise exception using message = 'OUTCOME_STRATEGY_RULE_NOT_FOUND';
  end if;

  if new.tp_pct is distinct from rule_row.tp_pct
     or new.sl_pct is distinct from rule_row.sl_pct
     or (new.strategy in ('D', 'E') and new.cutoff_n is distinct from rule_row.cutoff_n) then
    raise exception using message = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH';
  end if;
  return new;
end;
$$;

revoke execute on function public.guard_outcome_strategy_snapshot() from public, anon, authenticated;

commit;
