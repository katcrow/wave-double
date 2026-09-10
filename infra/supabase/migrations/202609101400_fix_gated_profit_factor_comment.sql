-- Story 5.7 follow-up (code review patch): candidate_outcome_win_rate_pf_by_strategy_gated의
-- profit_factor 컬럼 주석 정정. 기존 주석은 "gross_loss가 0이면 NULL"이라 적었지만, 실제로는
-- sum(...) filter(...)가 해당 부호의 거래가 하나도 없을 때 NULL을 반환하는 것이지 0을
-- 반환하는 것이 아니다(gross_win/gross_loss 모두 동일). nullif(gross_loss, 0)은 문자 그대로
-- 0인 값만 NULL로 바꾸는 방어용 가드일 뿐, NULL 자체를 만드는 주된 경로가 아니다.
-- forward-only(AD-14): view 정의는 변경하지 않고 comment on column만 정정한다.
begin;

comment on column public.candidate_outcome_win_rate_pf_by_strategy_gated.profit_factor is
  'PF = gross_win / gross_loss (반올림 4자리). total_settled < 30이면 NULL(표본 게이트 미충족). gross_win 또는 gross_loss가 NULL이면(승리 또는 패배 거래가 하나도 없으면) NULL(ALL_WIN/ALL_LOSS edge) — sum(...) filter(...)는 해당 부호의 거래가 없을 때 0이 아니라 NULL을 반환한다.';

commit;
