-- 전략 L(VWAP 상향 회복)을 운영 태깅/outcome/성과 검증 경로에 연결한다.
-- 기존 outcome 장부는 변경하지 않으며, 다음 정상 close 배치부터 L을 생성한다.
begin;

-- 1) candidate_tags는 운영 수동 전략 I와 백테스트+운영 전략 L을 모두 보존한다.
alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check,
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'L'));

-- 2) L의 운영 청산 규칙: TP 3%, SL 4%, 보유기간 제한 없음.
--    cutoff_n은 스키마의 NOT NULL 계약을 유지하기 위한 sentinel이다.
do $$
begin
  if exists (
    select 1 from public.outcome_strategy_rules
    where strategy = 'L' and (tp_pct, sl_pct, cutoff_n) <> (3.0, 4.0, 999999)
  ) then
    raise exception 'outcome_strategy_rules L row precondition failed: conflicting value already present';
  end if;
end $$;

alter table public.outcome_strategy_rules
  drop constraint outcome_strategy_rules_strategy_check,
  add constraint outcome_strategy_rules_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L'));

select set_config('wave_double.strategy_rule_reason', '전략 L 운영 연결: VWAP 상향 회복', true);
select set_config('wave_double.strategy_rule_changed_by', 'migration:202610011700_expand_strategy_l', true);
insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
values ('L', 3.0, 4.0, 999999)
on conflict (strategy) do nothing;

alter table public.outcome_events
  drop constraint outcome_events_strategy_check,
  add constraint outcome_events_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L'));

alter table public.candidate_outcome
  drop constraint candidate_outcome_strategy_check,
  add constraint candidate_outcome_strategy_check
  check (strategy in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L'));

-- 3) 현재 운영 함수 본문에서 허용 전략 목록을 L까지 확장한다.
do $migration$
declare
  item record;
  function_def text;
  rewritten text;
  old_ah text := '(''A'', ''B'', ''C'', ''D'', ''E'', ''F'', ''G'', ''H'')';
  new_ahl text := '(''A'', ''B'', ''C'', ''D'', ''E'', ''F'', ''G'', ''H'', ''L'')';
  old_dh text := '(''D'', ''E'', ''F'', ''G'', ''H'')';
  new_dhl text := '(''D'', ''E'', ''F'', ''G'', ''H'', ''L'')';
begin
  for item in
    select p.oid, p.proname, pg_get_function_identity_arguments(p.oid) as identity_args
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and (
        (p.proname = 'emit_open_command' and pg_get_function_identity_arguments(p.oid) = 'p_logical_run_key text, p_ticker text, p_strategy text')
        or p.proname = 'guard_outcome_strategy_snapshot'
        or p.proname = 'get_outcome_tracking_rows'
        or p.proname = 'get_outcome_metric_comparison'
      )
  loop
    select pg_get_functiondef(item.oid) into function_def;
    rewritten := replace(function_def, old_ah, new_ahl);
    rewritten := replace(rewritten, old_dh, new_dhl);

    if item.proname = 'get_outcome_metric_comparison'
       and item.identity_args = 'p_strategy text, p_source text' then
      rewritten := replace(
        rewritten,
        '(''C'', 0.6600::numeric, 1.8159::numeric)',
        '(''C'', 0.6600::numeric, 1.8159::numeric),
      (''L'', 0.7574::numeric, 1.1185::numeric)'
      );
    end if;

    if rewritten = function_def then
      raise exception 'strategy L function rewrite made no change: % (%)', item.proname, item.identity_args;
    end if;
    execute rewritten;
  end loop;
end
$migration$;

-- 4) 전략 L은 같은 봉 TP/SL 동시 도달 시 TP-first이며,
--    TP/SL 미도달 + 종가 수익이면 그 종가에서 강제 청산한다.
do $migration$
declare
  function_def text;
  rewritten text;
  old_block text := $old$
      if v_obs_low <= tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0) then
        -- 같은 봉에서 TP와 SL이 함께 도달하면 SL을 우선한다.
        v_tpsl_status := 'SL';
        v_exit_price := tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0);
        v_return_pct := -tpsl_row.sl_pct - 0.1;
      elsif v_obs_high >= tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0) then
        v_tpsl_status := 'TP';
        v_exit_price := tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0);
        v_return_pct := tpsl_row.tp_pct - 0.1;
      elsif v_traded_days >= tpsl_row.cutoff_n then
        v_tpsl_status := 'TIMEOUT';
        v_exit_price := v_obs_close;
        v_return_pct := (v_obs_close / tpsl_row.entry_price - 1.0) * 100.0 - 0.1;
      end if;
$old$;
  new_block text := $new$
      if tpsl_row.strategy = 'L' then
        -- 전략 L만 TP-first이며, 수익 종가 강제청산을 적용한다.
        if v_obs_high >= tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0) then
          v_tpsl_status := 'TP';
          v_exit_price := tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0);
          v_return_pct := tpsl_row.tp_pct - 0.1;
        elsif v_obs_low <= tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0) then
          v_tpsl_status := 'SL';
          v_exit_price := tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0);
          v_return_pct := -tpsl_row.sl_pct - 0.1;
        elsif v_obs_close > tpsl_row.entry_price then
          v_tpsl_status := 'TIMEOUT';
          v_exit_price := v_obs_close;
          v_return_pct := (v_obs_close / tpsl_row.entry_price - 1.0) * 100.0 - 0.1;
        end if;
      elsif v_obs_low <= tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0) then
        -- 기존 전략은 기존 운영 계약대로 SL-first를 유지한다.
        v_tpsl_status := 'SL';
        v_exit_price := tpsl_row.entry_price * (1.0 - tpsl_row.sl_pct / 100.0);
        v_return_pct := -tpsl_row.sl_pct - 0.1;
      elsif v_obs_high >= tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0) then
        v_tpsl_status := 'TP';
        v_exit_price := tpsl_row.entry_price * (1.0 + tpsl_row.tp_pct / 100.0);
        v_return_pct := tpsl_row.tp_pct - 0.1;
      elsif v_traded_days >= tpsl_row.cutoff_n then
        v_tpsl_status := 'TIMEOUT';
        v_exit_price := v_obs_close;
        v_return_pct := (v_obs_close / tpsl_row.entry_price - 1.0) * 100.0 - 0.1;
      end if;
$new$;
begin
  select pg_get_functiondef(p.oid)
    into function_def
  from pg_proc p
  join pg_namespace n on n.oid = p.pronamespace
  where n.nspname = 'public'
    and p.proname = 'publish_attempt'
    and pg_get_function_identity_arguments(p.oid) = 'p_run_id uuid, p_fence_token bigint, p_lease_token uuid';
  if function_def is null then
    raise exception 'PUBLISH_ATTEMPT_FUNCTION_NOT_FOUND';
  end if;
  rewritten := replace(function_def, old_block, new_block);
  if rewritten = function_def then
    raise exception 'STRATEGY_L_PUBLISH_REWRITE_FAILED';
  end if;
  execute rewritten;
end
$migration$;

-- 5) 운영 성과 페이지의 백테스트 기대치에 문서 기준 L 값을 등록한다.
create or replace view public.candidate_outcome_win_rate_pf_ci_gated as
with base as (
  select * from public.candidate_outcome_win_rate_pf_by_strategy_gated
),
expected as (
  select * from (values
    ('A', 0.6871::numeric),
    ('B', 0.6895::numeric),
    ('C', 0.6600::numeric),
    ('L', 0.7574::numeric)
  ) as e(strategy, expected_win_rate)
),
ci as (
  select
    b.*,
    e.expected_win_rate as expected_win_rate_raw,
    case when b.sample_gate_passed then
      1.959963985 / (1 + (1.959963985 ^ 2) / b.total_settled)
    end as z_denom_factor,
    case when b.sample_gate_passed then
      (b.win_rate + (1.959963985 ^ 2) / (2 * b.total_settled))
        / (1 + (1.959963985 ^ 2) / b.total_settled)
    end as center,
    case when b.sample_gate_passed then
      sqrt(
        (b.win_rate * (1 - b.win_rate) + (1.959963985 ^ 2) / (4 * b.total_settled))
        / b.total_settled
      )
    end as spread
  from base b
  left join expected e on e.strategy = b.strategy
)
select
  strategy, total_settled, wins, losses, open_count, suspended_count, delisted_count,
  gross_win, gross_loss, win_rate, profit_factor, sample_gate_min_required,
  sample_gate_passed, sample_gate_label,
  round(center - z_denom_factor * spread, 4) as ci_lower,
  round(center + z_denom_factor * spread, 4) as ci_upper,
  case when sample_gate_passed then expected_win_rate_raw end as expected_win_rate,
  case when sample_gate_passed and expected_win_rate_raw is not null then
    expected_win_rate_raw between
      round(center - z_denom_factor * spread, 4) and round(center + z_denom_factor * spread, 4)
  end as expected_in_ci
from ci;

create or replace view public.candidate_outcome_win_rate_pf_threshold_gated as
with expected as (
  select * from (values
    ('A', 2.0540::numeric),
    ('B', 2.0770::numeric),
    ('C', 1.8159::numeric),
    ('L', 1.1185::numeric)
  ) as e(strategy, expected_profit_factor)
),
base as (
  select ci.*, case when ci.sample_gate_passed then e.expected_profit_factor end as expected_profit_factor
  from public.candidate_outcome_win_rate_pf_ci_gated ci
  left join expected e on e.strategy = ci.strategy
),
thresholds as (
  select b.*,
    case when b.expected_profit_factor is not null then 0.10::numeric end as win_rate_threshold_pp,
    case when b.expected_profit_factor is not null then 0.25::numeric end as profit_factor_threshold_ratio,
    case when b.sample_gate_passed and b.expected_win_rate is not null and b.win_rate is not null
      then abs(b.win_rate - b.expected_win_rate) > 0.10 end as win_rate_threshold_breached,
    case when b.sample_gate_passed and b.expected_profit_factor is not null and b.profit_factor is not null
      then abs(b.profit_factor - b.expected_profit_factor) / b.expected_profit_factor > 0.25 end as profit_factor_threshold_breached
  from base b
)
select strategy, total_settled, wins, losses, open_count, suspended_count, delisted_count,
  gross_win, gross_loss, win_rate, profit_factor, sample_gate_min_required,
  sample_gate_passed, sample_gate_label, ci_lower, ci_upper, expected_win_rate,
  expected_in_ci, expected_profit_factor, win_rate_threshold_pp,
  profit_factor_threshold_ratio, win_rate_threshold_breached,
  profit_factor_threshold_breached,
  case when win_rate_threshold_breached or profit_factor_threshold_breached then true
    when win_rate_threshold_breached is null and profit_factor_threshold_breached is null then null
    else false end as threshold_warning
from thresholds;

comment on table public.candidate_tags is
  '전략 A/B/C/D/E/F/G/H/I/L 시그널 태깅 이력. I는 운영 수동 확인, L은 VWAP 상향 회복 전략이다.';
comment on table public.outcome_strategy_rules is
  '전략별 TP/SL/최대보유일 lookup. L은 TP 3%/SL 4%/cutoff sentinel 999999이며 publish_attempt에서 TP-first 및 수익 종가 청산을 적용한다.';
comment on function public.publish_attempt(uuid, bigint, uuid) is
  'close publish에서 전략 L은 TP-first, SL 4%, TP/SL 미도달 시 수익 종가 강제청산을 적용하고 기존 전략은 기존 SL-first 계약을 유지한다.';

commit;
