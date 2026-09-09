-- epic-6-retro-item-25: outcome_strategy_rules에 감사 가능한 수정 경로를 만든다.
--
-- 문제: 이 테이블은 "전략 X의 TP/SL/컷오프가 무엇인가"의 유일한 권위다. emit_open_command가
-- 이 값을 OPEN 이벤트에 스냅샷하고, guard_outcome_strategy_snapshot이 직접 INSERT를 이 값과
-- 대조한다. 그런데 service_role은 이 테이블에 INSERT/UPDATE/DELETE 전권을 갖고 있었고 변경
-- 이력이 없었다 -- 한 줄 UPDATE로 전략의 의미를 바꿔도 "언제 누가 왜"가 아무 데도 남지 않고,
-- 그 시점 이후의 모든 스냅샷 대조 기준이 조용히 달라진다.
--
-- 설계(두 방식 중 "변경 이력 보존"을 택하고 upsert RPC를 그 위에 얹는다):
--   1) outcome_strategy_rule_history -- append-only 변경 이력. UPDATE/DELETE/TRUNCATE 금지.
--   2) BEFORE 트리거 -- 사유(reason)와 변경자(changed_by)가 세션에 설정돼 있지 않으면 어떤
--      DML도 거부한다. 즉 "사유 없는 변경"이 문법적으로 불가능하다.
--   3) AFTER 트리거 -- 통과한 모든 변경(INSERT/UPDATE/DELETE)을 무조건 이력에 남긴다.
--      RPC를 쓰지 않고 직접 SQL로 바꿔도 이력을 우회할 수 없다.
--   4) set_outcome_strategy_rule() -- service_role 전용 SECURITY DEFINER upsert RPC.
--      세션 설정을 자기 트랜잭션 범위로 켰다 끄고 upsert한다(일반 운영 경로).
--
-- upsert RPC 단독으로는 부족하다고 판단했다: RPC만 만들고 직접 DML을 열어두면 감사 경로가
-- "권장"에 그친다. 이력을 트리거로 강제하면 우회 경로가 없다.
--
-- 기존 migration들의 rule 삽입(202609051600/202609080900 등)은 이 migration보다 앞서 실행되므로
-- 영향을 받지 않는다. 이후 rule을 건드리는 migration/fixture는 사유를 설정해야 한다.
begin;

create table if not exists public.outcome_strategy_rule_history (
  history_id uuid primary key default gen_random_uuid(),
  strategy text not null,
  operation text not null check (operation in ('INSERT', 'UPDATE', 'DELETE')),
  previous_tp_pct numeric,
  previous_sl_pct numeric,
  previous_cutoff_n integer,
  new_tp_pct numeric,
  new_sl_pct numeric,
  new_cutoff_n integer,
  reason text not null check (length(btrim(reason)) > 0),
  changed_by text not null check (length(btrim(changed_by)) > 0),
  changed_at timestamptz not null default now()
);

comment on table public.outcome_strategy_rule_history is
  'epic-6-retro-item-25: outcome_strategy_rules의 append-only 변경 이력. 전략 파라미터는 판정 기준이므로 "언제 누가 왜 바꿨는가"가 남아야 한다. AD-19/NFR-4에 따라 장기 보존 대상이며 정리하지 않는다.';

create index if not exists outcome_strategy_rule_history_strategy_idx
  on public.outcome_strategy_rule_history(strategy, changed_at desc);

-- candidates/outcome 하드닝 선례와 동일하게 RLS enable + 정책 0개로 anon/authenticated를 차단한다.
alter table public.outcome_strategy_rule_history enable row level security;

-- ── append-only 강제 ─────────────────────────────────────────────────────────
create or replace function public.reject_outcome_strategy_rule_history_mutation()
returns trigger
language plpgsql
as $$
begin
  raise exception using
    errcode = '55000',
    message = 'outcome_strategy_rule_history is append-only';
end;
$$;

drop trigger if exists outcome_strategy_rule_history_append_only
  on public.outcome_strategy_rule_history;
create trigger outcome_strategy_rule_history_append_only
  before update or delete on public.outcome_strategy_rule_history
  for each row execute function public.reject_outcome_strategy_rule_history_mutation();

drop trigger if exists outcome_strategy_rule_history_no_truncate
  on public.outcome_strategy_rule_history;
create trigger outcome_strategy_rule_history_no_truncate
  before truncate on public.outcome_strategy_rule_history
  for each statement execute function public.reject_outcome_strategy_rule_history_mutation();

-- ── 사유 없는 변경 금지 ──────────────────────────────────────────────────────
create or replace function public.require_outcome_strategy_rule_reason()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
begin
  if coalesce(btrim(current_setting('wave_double.strategy_rule_reason', true)), '') = '' then
    raise exception using message = 'STRATEGY_RULE_REASON_REQUIRED';
  end if;
  if coalesce(btrim(current_setting('wave_double.strategy_rule_changed_by', true)), '') = '' then
    raise exception using message = 'STRATEGY_RULE_CHANGED_BY_REQUIRED';
  end if;
  if tg_op = 'DELETE' then
    return old;
  end if;
  return new;
end;
$$;

comment on function public.require_outcome_strategy_rule_reason() is
  'epic-6-retro-item-25: outcome_strategy_rules의 모든 DML은 wave_double.strategy_rule_reason과 wave_double.strategy_rule_changed_by가 설정된 세션에서만 성립한다. set_outcome_strategy_rule()이 이 설정을 관리하며, 직접 SQL로 바꿔야 하는 예외 상황에서도 사유를 남기도록 강제한다.';

drop trigger if exists outcome_strategy_rules_require_reason on public.outcome_strategy_rules;
create trigger outcome_strategy_rules_require_reason
  before insert or update or delete on public.outcome_strategy_rules
  for each row execute function public.require_outcome_strategy_rule_reason();

-- ── 통과한 모든 변경을 이력에 남긴다 ─────────────────────────────────────────
create or replace function public.record_outcome_strategy_rule_history()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  v_reason text := btrim(current_setting('wave_double.strategy_rule_reason', true));
  v_changed_by text := btrim(current_setting('wave_double.strategy_rule_changed_by', true));
begin
  -- tg_op으로 분기한다. DELETE 트리거에서 NEW를, INSERT 트리거에서 OLD를 참조하는 것은
  -- PL/pgSQL에서 정의되지 않은 접근이므로 한 문장으로 합치지 않는다.
  if tg_op = 'INSERT' then
    insert into public.outcome_strategy_rule_history(
      strategy, operation, new_tp_pct, new_sl_pct, new_cutoff_n, reason, changed_by)
    values (new.strategy, 'INSERT', new.tp_pct, new.sl_pct, new.cutoff_n, v_reason, v_changed_by);
  elsif tg_op = 'UPDATE' then
    insert into public.outcome_strategy_rule_history(
      strategy, operation,
      previous_tp_pct, previous_sl_pct, previous_cutoff_n,
      new_tp_pct, new_sl_pct, new_cutoff_n,
      reason, changed_by)
    values (new.strategy, 'UPDATE',
      old.tp_pct, old.sl_pct, old.cutoff_n,
      new.tp_pct, new.sl_pct, new.cutoff_n,
      v_reason, v_changed_by);
  else
    insert into public.outcome_strategy_rule_history(
      strategy, operation, previous_tp_pct, previous_sl_pct, previous_cutoff_n, reason, changed_by)
    values (old.strategy, 'DELETE', old.tp_pct, old.sl_pct, old.cutoff_n, v_reason, v_changed_by);
  end if;
  return null;
end;
$$;

comment on function public.record_outcome_strategy_rule_history() is
  'epic-6-retro-item-25: outcome_strategy_rules의 INSERT/UPDATE/DELETE를 outcome_strategy_rule_history에 무조건 append한다. BEFORE 트리거가 사유/변경자를 이미 강제하므로 이력 없는 변경은 존재할 수 없다.';

drop trigger if exists outcome_strategy_rules_record_history on public.outcome_strategy_rules;
create trigger outcome_strategy_rules_record_history
  after insert or update or delete on public.outcome_strategy_rules
  for each row execute function public.record_outcome_strategy_rule_history();

-- ── service_role 전용 upsert RPC (일반 운영 경로) ────────────────────────────
create or replace function public.set_outcome_strategy_rule(
  p_strategy text,
  p_tp_pct numeric,
  p_sl_pct numeric,
  p_cutoff_n integer,
  p_reason text,
  p_changed_by text
) returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  previous public.outcome_strategy_rules;
  updated public.outcome_strategy_rules;
begin
  if p_strategy is null or p_strategy not in ('A', 'B', 'C', 'D', 'E', 'F') then
    raise exception using message = 'INVALID_STRATEGY';
  end if;
  if p_reason is null or length(btrim(p_reason)) = 0 then
    raise exception using message = 'STRATEGY_RULE_REASON_REQUIRED';
  end if;
  if p_changed_by is null or length(btrim(p_changed_by)) = 0 then
    raise exception using message = 'STRATEGY_RULE_CHANGED_BY_REQUIRED';
  end if;
  -- 판정 기준이므로 값 자체도 검증한다. cutoff_n은 F의 sentinel(999999)까지 허용해야 하므로
  -- 상한을 두지 않고 양수만 요구한다.
  if p_tp_pct is null or p_tp_pct <= 0
     or p_tp_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
    raise exception using message = 'INVALID_TP_PCT';
  end if;
  if p_sl_pct is null or p_sl_pct <= 0
     or p_sl_pct in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) then
    raise exception using message = 'INVALID_SL_PCT';
  end if;
  if p_cutoff_n is null or p_cutoff_n <= 0 then
    raise exception using message = 'INVALID_CUTOFF_N';
  end if;

  select * into previous from public.outcome_strategy_rules where strategy = p_strategy for update;

  perform set_config('wave_double.strategy_rule_reason', btrim(p_reason), true);
  perform set_config('wave_double.strategy_rule_changed_by', btrim(p_changed_by), true);

  insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
  values (p_strategy, p_tp_pct, p_sl_pct, p_cutoff_n)
  on conflict (strategy) do update
    set tp_pct = excluded.tp_pct,
        sl_pct = excluded.sl_pct,
        cutoff_n = excluded.cutoff_n
  returning * into updated;

  perform set_config('wave_double.strategy_rule_reason', '', true);
  perform set_config('wave_double.strategy_rule_changed_by', '', true);

  return jsonb_build_object(
    'strategy', updated.strategy,
    'operation', case when previous.strategy is null then 'INSERT' else 'UPDATE' end,
    'previous', case
      when previous.strategy is null then null
      else jsonb_build_object('tp_pct', previous.tp_pct, 'sl_pct', previous.sl_pct, 'cutoff_n', previous.cutoff_n)
    end,
    'current', jsonb_build_object('tp_pct', updated.tp_pct, 'sl_pct', updated.sl_pct, 'cutoff_n', updated.cutoff_n),
    'unchanged', previous.strategy is not null
      and previous.tp_pct = updated.tp_pct
      and previous.sl_pct = updated.sl_pct
      and previous.cutoff_n = updated.cutoff_n
  );
end;
$$;

comment on function public.set_outcome_strategy_rule(text, numeric, numeric, integer, text, text) is
  'epic-6-retro-item-25: outcome_strategy_rules의 감사 가능한 upsert 경로(service_role 전용). 사유/변경자를 필수로 받아 트랜잭션 범위 세션 설정으로 넘기고, AFTER 트리거가 outcome_strategy_rule_history에 변경을 append한다. 값이 이전과 같아도 이력은 남는다(사유가 있는 재확인도 기록 대상). 반환 jsonb의 unchanged가 그 경우를 알린다. 전략 목록 밖 값은 INVALID_STRATEGY, 비양수/비유한 파라미터는 INVALID_TP_PCT/INVALID_SL_PCT/INVALID_CUTOFF_N으로 거부한다.';

revoke execute on function public.set_outcome_strategy_rule(text, numeric, numeric, integer, text, text)
  from public, anon, authenticated;
grant execute on function public.set_outcome_strategy_rule(text, numeric, numeric, integer, text, text)
  to service_role;

-- 트리거 함수는 트리거로만 호출된다(직접 실행 경로를 닫는다, 202609051900 선례).
revoke execute on function public.require_outcome_strategy_rule_reason() from public, anon, authenticated;
revoke execute on function public.record_outcome_strategy_rule_history() from public, anon, authenticated;
revoke execute on function public.reject_outcome_strategy_rule_history_mutation() from public, anon, authenticated;

commit;
