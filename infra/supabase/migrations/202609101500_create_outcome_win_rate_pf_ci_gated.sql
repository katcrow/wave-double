-- Story 5.8: 95% 신뢰구간 계산 & 기대치 판정 — 5-7 표본 게이트 view를 그대로 소비해
-- 게이트 통과 행에 한해 승률의 95% Wilson score 신뢰구간(ci_lower/ci_upper)을 계산하고,
-- 전략 A/B/C의 고정 백테스트 기대치(68.71%/68.95%/66.00%)가 그 구간 안/밖 어디에 있는지
-- expected_in_ci로 판정한다. 게이트 임계값(30)은 이 view에서 재정의하지 않는다 — 5-7
-- view(candidate_outcome_win_rate_pf_by_strategy_gated)를 그대로 select한다.
--
-- expected_win_rate는 전략 A/B/C에만 정의된 고정 상수다. D/E/F 전략과 rollup(strategy
-- IS NULL) 행은 join에 실패해 자연히 NULL이 된다 — 별도 분기 없이 "기대치 없음"이
-- 표현된다. D/E/F에 임의의 기대치를 추정해 채우지 않는다.
--
-- 게이트 미통과 행(sample_gate_passed=false)은 ci_lower/ci_upper/expected_win_rate/
-- expected_in_ci 모두 NULL이다 — expected_win_rate도 게이트 통과 조건으로 감싸
-- 전략 C가 게이트 실패(29건)일 때 기대치(0.6600)가 노출되지 않도록 한다(AC).
--
-- z=1.959963985는 scipy.stats.norm.ppf(0.975) 값을 SQL 리터럴로 고정한 것이며,
-- Python parity 도구도 동일 상수를 써서 4dp까지 정확히 일치시킨다.
--
-- 표본이 50건을 초과해도 신뢰구간 판정 로직·우선순위는 동일하게 유지한다(표본
-- 크기별 판정 방식 전환 없음). 이탈 임계값(승률 ±10%p, PF ±25%) 보조 경고와
-- 컷오프 편향 고지는 각각 story 5.9/5.10 소관이며 여기서 구현하지 않는다.
--
-- 5-5/5-6/5-7 view는 이 migration에서 변경하지 않는다 — 별도 view다.
-- revoke를 통해 browser 역할(anon/authenticated)의 접근을 차단한다.
begin;

create or replace view public.candidate_outcome_win_rate_pf_ci_gated as
with base as (
  select * from public.candidate_outcome_win_rate_pf_by_strategy_gated
),
expected as (
  select * from (values
    ('A', 0.6871::numeric),
    ('B', 0.6895::numeric),
    ('C', 0.6600::numeric)
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
  strategy,
  total_settled,
  wins,
  losses,
  open_count,
  suspended_count,
  delisted_count,
  gross_win,
  gross_loss,
  win_rate,
  profit_factor,
  sample_gate_min_required,
  sample_gate_passed,
  sample_gate_label,
  round(center - z_denom_factor * spread, 4) as ci_lower,
  round(center + z_denom_factor * spread, 4) as ci_upper,
  case when sample_gate_passed then expected_win_rate_raw end as expected_win_rate,
  case when sample_gate_passed and expected_win_rate_raw is not null then
    expected_win_rate_raw between
      round(center - z_denom_factor * spread, 4) and round(center + z_denom_factor * spread, 4)
  end as expected_in_ci
from ci;

comment on view public.candidate_outcome_win_rate_pf_ci_gated is
  'Story 5.8: candidate_outcome_win_rate_pf_by_strategy_gated(5-7)를 그대로 소비해 게이트 통과 행(sample_gate_passed=true)에 한해 승률의 95% Wilson score 신뢰구간(ci_lower/ci_upper, z=1.959963985)을 계산하고, 전략 A/B/C의 고정 백테스트 기대치(0.6871/0.6895/0.6600)가 그 구간 안/밖 어디에 있는지 expected_in_ci로 판정한다. D/E/F 전략과 rollup(strategy IS NULL) 행은 expected_win_rate/expected_in_ci가 항상 NULL이며, 게이트 미통과 행은 ci_lower/ci_upper/expected_win_rate/expected_in_ci 모두 NULL이다. 게이트 임계값(30)은 5-7 view를 그대로 물려받으며 이 view에서 재정의하지 않는다. 표본이 50건을 초과해도 판정 로직은 동일하게 유지된다(표본 크기별 전환 없음).';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.strategy is
  '전략(A/B/C/D/E/F). NULL이면 rollup 전체 합계 행이다. 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.total_settled is
  'TP/SL/TIMEOUT 종결 건수(분모). 5-7 view에서 그대로 물려받으며 게이트 상태와 무관하게 항상 채워진다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.wins is
  '종결 건 중 return_pct > 0인 건수(승). 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.losses is
  '종결 건 중 return_pct < 0인 건수(패). 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.open_count is
  '현재 추적 중인 OPEN 상태 건수. 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.suspended_count is
  'SUSPENDED 상태 건수. 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.delisted_count is
  'DELISTED 상태 건수. 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.gross_win is
  '종결 건 중 양의 return_pct의 합. 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.gross_loss is
  '종결 건 중 음의 return_pct의 절대값 합. 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.win_rate is
  '승률(반올림 4자리). 5-7 view에서 그대로 물려받으며 total_settled < 30이면 NULL. Wilson CI 계산의 입력값이다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.profit_factor is
  'PF(반올림 4자리). 5-7 view에서 그대로 물려받으며 total_settled < 30이면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.sample_gate_min_required is
  '표본 게이트 임계값 상수(30). 5-7 view에서 그대로 물려받으며 이 view에서 재정의하지 않는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.sample_gate_passed is
  'total_settled >= 30 여부. false면 ci_lower/ci_upper/expected_win_rate/expected_in_ci가 모두 NULL이다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.sample_gate_label is
  '게이트 미충족 시 "표본 부족 (n/30)". 5-7 view에서 그대로 물려받는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.ci_lower is
  '승률의 95% Wilson score 신뢰구간 하한(반올림 4자리, z=1.959963985). sample_gate_passed=false면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.ci_upper is
  '승률의 95% Wilson score 신뢰구간 상한(반올림 4자리, z=1.959963985). sample_gate_passed=false면 NULL.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.expected_win_rate is
  '전략 A=0.6871/B=0.6895/C=0.6600 고정 백테스트 기대치. D/E/F·rollup 행은 항상 NULL이고, A/B/C이어도 sample_gate_passed=false면 NULL이다. 스펙에 정의되지 않은 전략에는 임의의 값을 채우지 않는다.';
comment on column public.candidate_outcome_win_rate_pf_ci_gated.expected_in_ci is
  '게이트 통과 + expected_win_rate 존재(A/B/C) 조건을 모두 만족할 때만 채워지는 boolean: expected_win_rate가 [ci_lower, ci_upper] 구간 안(true)/밖(false)인지 판정. 그 외 행은 NULL. 이 판정이 모든 표본 크기(30~50건 포함)에서 유일한 1차 판정 기준이며, 이탈 임계값(승률 ±10%p, PF ±25%) 보조 경고는 story 5.9 소관으로 여기서 구현하지 않는다.';

revoke select on table public.candidate_outcome_win_rate_pf_ci_gated from public, anon, authenticated;

commit;
