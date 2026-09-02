-- Story 2.6: 후보별 3일치(D-2/D-1/D0) 가격·수급 데이터 스키마.
-- data-model.md:88-103의 supply_3day 정의를 그대로 옮긴다 -- 이번 스토리는 신설만 하며
-- 수집 로직(t1702/t1637)/배치 오케스트레이션/카드 UI는 Epic 4·Story 2.7 범위다.
-- candidate_tags(202609021600)와 동일하게 candidates(candidate_id, attempt_run_id) 합성키
-- FK를 재사용하고, daily_ohlcv(202609021500)와 동일한 유한값(NaN/Infinity 거부) CHECK 패턴을
-- close/volume/change_pct에 적용한다.
begin;

create table if not exists public.supply_3day (
  candidate_id uuid not null,
  attempt_run_id uuid not null,
  trading_day date not null,
  slot text not null check (slot in ('D-2', 'D-1', 'D0')),
  close numeric not null check (close <> 'NaN'::numeric and close <> 'Infinity'::numeric and close <> '-Infinity'::numeric),
  volume numeric not null check (volume <> 'NaN'::numeric and volume <> 'Infinity'::numeric and volume <> '-Infinity'::numeric),
  change_pct numeric not null check (change_pct <> 'NaN'::numeric and change_pct <> 'Infinity'::numeric and change_pct <> '-Infinity'::numeric),
  foreign_net numeric check (foreign_net is null or (foreign_net <> 'NaN'::numeric and foreign_net <> 'Infinity'::numeric and foreign_net <> '-Infinity'::numeric)),
  institution_net numeric check (institution_net is null or (institution_net <> 'NaN'::numeric and institution_net <> 'Infinity'::numeric and institution_net <> '-Infinity'::numeric)),
  individual_net numeric check (individual_net is null or (individual_net <> 'NaN'::numeric and individual_net <> 'Infinity'::numeric and individual_net <> '-Infinity'::numeric)),
  program_net numeric check (program_net is null or (program_net <> 'NaN'::numeric and program_net <> 'Infinity'::numeric and program_net <> '-Infinity'::numeric)),
  investor_net_status text not null check (investor_net_status in ('confirmed', 'pending', 'missing')),
  collected_at timestamptz not null default now(),
  unique (candidate_id, trading_day, attempt_run_id),
  foreign key (candidate_id, attempt_run_id)
    references public.candidates(candidate_id, attempt_run_id),
  constraint supply_3day_investor_net_status_consistency check (
    (
      investor_net_status = 'confirmed'
      and foreign_net is not null and institution_net is not null
      and individual_net is not null and program_net is not null
    )
    or
    (
      investor_net_status in ('pending', 'missing')
      and foreign_net is null and institution_net is null
      and individual_net is null and program_net is null
    )
  )
);

create index if not exists supply_3day_attempt_idx on public.supply_3day(attempt_run_id);

comment on table public.supply_3day is 'Story 2.6: 후보별 3일치(D-2/D-1/D0) 가격·수급. candidates에 합성키 FK, UNIQUE(candidate_id, trading_day, attempt_run_id). D0 행은 attempt_run_id별로 누적되며(덮어쓰지 않음), 정리(cleanup) 대상은 D0뿐이고 보존 주기는 90일(NFR-4, 잠정) -- 이번 스토리는 스키마만 만들고 실제 정리 배치는 구현하지 않는다. D-2/D-1은 정리 대상이 아니다. candidate_id는 Epic 1의 candidates뿐 아니라 Epic 2의 candidate_tags와도 공유하는 조인 키다(epics.md Story 2.6 AC2) -- Story 2.7 카드 UI가 태그(candidate_tags)와 수급(supply_3day) 데이터를 candidate_id 기준으로 조인해 사용한다.';
comment on column public.supply_3day.investor_net_status is '투자자별 순매수 4컬럼(foreign_net/institution_net/individual_net/program_net)의 상태를 행 단위로 선언. confirmed: 종가 확정 배치의 실측값(실제 0 포함), 4컬럼 모두 NOT NULL. pending: 장중 미확정(재시도 후에도 미채움 포함), 4컬럼 모두 NULL. missing: 조회 실패로 미수집, 4컬럼 모두 NULL. NULL과 실젯값(0 포함)은 서로 대체하지 않는다.';
comment on column public.supply_3day.foreign_net is '외인 순매수. NULL은 미확정/미수집(investor_net_status 참고), 0은 실제 순매수 0.';
comment on column public.supply_3day.institution_net is '기관 순매수. NULL은 미확정/미수집(investor_net_status 참고), 0은 실제 순매수 0.';
comment on column public.supply_3day.individual_net is '개인 순매수. NULL은 미확정/미수집(investor_net_status 참고), 0은 실제 순매수 0.';
comment on column public.supply_3day.program_net is '프로그램 순매수. NULL은 미확정/미수집(investor_net_status 참고), 0은 실제 순매수 0.';
comment on column public.supply_3day.collected_at is '신선도 표시(FR-6a).';

alter table public.supply_3day enable row level security;

commit;
