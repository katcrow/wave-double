-- Story 5.1: 모집단 편향 관측치 append-only 스키마와 거래일별 canonical view.
-- 회차 메타(bias_events)와 source별 분해(bias_event_by_source)를 분리하고, 두 테이블 모두
-- DB 경계에서 UPDATE/DELETE/TRUNCATE를 거부한다. 재계산은 새 bias_event_id로만 append한다.
-- 카운트는 전부 bias_event_by_source에만 두어 source별 view(Story 5.6/5.14)가 단일 row에서
-- 바로 집계되게 하고, bias_events는 회차 메타만 갖는다. source 권위는 candidate_source_contrib에만
-- 두므로 bias 테이블에는 source 사본을 두지 않는다(AD-12/AD-21).
-- Story 5.3(산식)/5.4(close 배치 배선)/5.13·5.14(조회·UI)가 이 스키마를 소비한다.
-- 파일명 timestamp는 spec이 제안한 202609091200이 이미 사용 중이므로 202609091700으로 둔다
-- (tools/check_migration_order.py는 timestamp 중복을 금지한다).
begin;

create table if not exists public.bias_events (
  bias_event_id uuid primary key default gen_random_uuid(),
  trading_day date not null,
  logical_run_key text not null references public.logical_runs(logical_run_key),
  calculation_meta jsonb not null default '{}'::jsonb check (jsonb_typeof(calculation_meta) = 'object'),
  created_at timestamptz not null default now()
);

create table if not exists public.bias_event_by_source (
  bias_event_id uuid not null references public.bias_events(bias_event_id),
  source text not null check (source in ('t1859', 't1852', 't1856')),
  candidate_pop_signal_count integer not null check (candidate_pop_signal_count >= 0),
  backtest_universe_signal_count integer not null check (backtest_universe_signal_count >= 0),
  intersection_count integer not null check (intersection_count >= 0),
  diff_count integer not null check (diff_count >= 0),
  missed_opportunity_count integer not null check (missed_opportunity_count >= 0),
  created_at timestamptz not null default now(),
  primary key (bias_event_id, source),
  constraint bias_event_by_source_intersection_within_sets check (
    intersection_count <= least(candidate_pop_signal_count, backtest_universe_signal_count)
  ),
  constraint bias_event_by_source_diff_within_population check (
    diff_count <= candidate_pop_signal_count
  ),
  constraint bias_event_by_source_diff_covers_population_only check (
    diff_count >= candidate_pop_signal_count - intersection_count
  ),
  constraint bias_event_by_source_missed_covers_universe_only check (
    missed_opportunity_count >= backtest_universe_signal_count - intersection_count
  )
);

-- 거래일별 최신 회차 선택(canonical view)과 회차 단위 조회를 위한 index.
create index if not exists bias_events_trading_day_latest_idx
  on public.bias_events(trading_day, created_at desc, bias_event_id desc);
create index if not exists bias_events_logical_run_key_idx
  on public.bias_events(logical_run_key);

-- append-only guard는 Story 3.1의 범용 원장 guard를 그대로 재사용한다.
create or replace trigger bias_events_append_only
before update or delete on public.bias_events
for each row execute function public.reject_outcome_ledger_mutation();

create or replace trigger bias_events_append_only_truncate
before truncate on public.bias_events
for each statement execute function public.reject_outcome_ledger_truncate();

create or replace trigger bias_event_by_source_append_only
before update or delete on public.bias_event_by_source
for each row execute function public.reject_outcome_ledger_mutation();

create or replace trigger bias_event_by_source_append_only_truncate
before truncate on public.bias_event_by_source
for each statement execute function public.reject_outcome_ledger_truncate();

-- trading_day는 연결된 logical_run_key의 거래일과 일치해야 하고, 편향 계산은 종가 배치
-- 전용이므로 계보의 batch_kind도 close여야 한다. 둘 다 FK로는 표현할 수 없어 insert 시점
-- trigger로 고정한다. errcode를 명시해 호출부·fixture가 sqlerrm 문자열 비교 없이 잡는다.
create or replace function public.enforce_bias_event_trading_day()
returns trigger
language plpgsql
set search_path = public
as $$
declare
  v_trading_day date;
  v_batch_kind text;
begin
  select trading_day, batch_kind into v_trading_day, v_batch_kind
  from public.logical_runs
  where logical_run_key = new.logical_run_key;
  if v_trading_day is null or v_trading_day <> new.trading_day then
    raise exception using errcode = '55000', message = 'BIAS_EVENT_TRADING_DAY_MISMATCH';
  end if;
  if v_batch_kind <> 'close' then
    raise exception using errcode = '55000', message = 'BIAS_EVENT_NOT_CLOSE_BATCH';
  end if;
  return new;
end;
$$;

create or replace trigger bias_events_trading_day_matches_run
before insert on public.bias_events
for each row execute function public.enforce_bias_event_trading_day();

comment on table public.bias_events is
  'Story 5.1: 모집단 편향 관측 한 회차의 메타. 카운트는 두지 않으며 모든 수치는 bias_event_by_source의 source별 행으로만 표현한다(source 컬럼도 두지 않는다). append-only이며 UPDATE/DELETE/TRUNCATE는 trigger가 거부한다. 재계산은 새 bias_event_id로 append하고 bias_events_canonical이 거래일별 최신 회차를 고른다.';
comment on column public.bias_events.trading_day is
  '관측 대상 거래일. 연결된 logical_run_key의 trading_day와 일치해야 하며 어긋나면 BIAS_EVENT_TRADING_DAY_MISMATCH로 거부된다.';
comment on column public.bias_events.logical_run_key is
  '이 관측을 수행한 배치의 논리 실행 키. 편향 계산은 종가 배치 전용이다(Story 5.4).';
comment on column public.bias_events.calculation_meta is
  '회차 단위 계산 컨텍스트(전략 집합, 유니버스 fixture 버전, 절단 정보 등) JSONB. object만 허용한다.';
comment on column public.bias_events.created_at is
  '회차 생성 시각. canonical 선택은 created_at 최신, 동시각이면 bias_event_id 큰 쪽이다.';

comment on table public.bias_event_by_source is
  'Story 5.1: 한 편향 관측 회차의 source별 분해 행. PK는 (bias_event_id, source)이고 source 도메인은 candidate_source_contrib.source와 동일한 집합이다. 모든 카운트가 이 행에 있어 source별 view가 단일 row에서 바로 집계된다. append-only이며 기여가 없는 폴백 source의 전부 0 행도 유효한 관측치다.';
comment on column public.bias_event_by_source.source is
  '조건검색 원천. candidate_source_contrib.source와 동일 도메인(t1859|t1852|t1856)이며 기여 사실 확인은 candidate_source_contrib join으로만 한다.';
comment on column public.bias_event_by_source.candidate_pop_signal_count is
  '해당 source 후보 모집단 ∩ 전략 시그널 종목 수.';
comment on column public.bias_event_by_source.backtest_universe_signal_count is
  '백테스트 유니버스 ∩ 전략 시그널 종목 수(Story 5.2가 계산).';
comment on column public.bias_event_by_source.intersection_count is
  '두 집합의 교집합 크기. 두 집합 크기 중 작은 값을 초과할 수 없다.';
comment on column public.bias_event_by_source.diff_count is
  '해당 source 모집단 전용 차집합 크기. 정확한 산식은 Story 5.3이 확정하며, 어떤 정의에서도 candidate_pop_signal_count를 넘지 못한다는 약한 불변식만 DB에 남긴다.';
comment on column public.bias_event_by_source.missed_opportunity_count is
  '해당 source 기준 기회 누락 수. 정확한 산식은 Story 5.3이 확정하며, NFR-7 모집단 상한 절단분이 더해지므로 어떤 정의에서도 backtest_universe_signal_count - intersection_count 이상이다.';
comment on column public.bias_event_by_source.created_at is
  'append-only 원장 관례에 따른 행 생성 시각.';

alter table public.bias_events enable row level security;
alter table public.bias_event_by_source enable row level security;

create or replace view public.bias_events_canonical as
select distinct on (e.trading_day)
  e.bias_event_id,
  e.trading_day,
  e.logical_run_key,
  e.calculation_meta,
  e.created_at
from public.bias_events e
order by e.trading_day, e.created_at desc, e.bias_event_id desc;

comment on view public.bias_events_canonical is
  'Story 5.1: 거래일별 최신 편향 관측 회차의 메타만 노출한다. created_at 최신, 동시각 tie는 bias_event_id 내림차순으로 결정론적으로 해소한다. 과거 회차는 bias_events 원본에 그대로 남는다.';

-- 기여 집계는 그 날의 canonical close run이 아니라 bias event 자신의 logical_run_key가
-- 가리키는 canonical attempt에 연결한다. 거래일로 연결하면 재실행이 canonical attempt를
-- 바꿀 때 과거 회차의 기여 수치가 소급 변해 append-only 보존 목적이 깨진다.
create or replace view public.bias_event_by_source_canonical as
select
  e.bias_event_id,
  e.trading_day,
  e.logical_run_key,
  s.source,
  s.candidate_pop_signal_count,
  s.backtest_universe_signal_count,
  s.intersection_count,
  s.diff_count,
  s.missed_opportunity_count,
  case
    when l.canonical_success_run_id is null then null
    else coalesce(c.contributing_candidate_count, 0)
  end as contributing_candidate_count,
  s.created_at
from public.bias_events_canonical e
join public.bias_event_by_source s
  on s.bias_event_id = e.bias_event_id
left join public.logical_runs l
  on l.logical_run_key = e.logical_run_key
left join lateral (
  select count(distinct sc.candidate_id) as contributing_candidate_count
  from public.candidate_source_contrib sc
  where sc.attempt_run_id = l.canonical_success_run_id
    and sc.source = s.source
) c on true;

comment on view public.bias_event_by_source_canonical is
  'Story 5.1: 거래일별 최신 회차의 source별 편향 행. 기여 사실은 그 회차 logical_run_key의 canonical close attempt에 속한 candidate_source_contrib join으로만 확인하며(AD-21), bias 테이블에는 source 사본을 두지 않는다.';
comment on column public.bias_event_by_source_canonical.contributing_candidate_count is
  '해당 source가 그 회차의 canonical close attempt에서 기여한 후보 수. NULL은 canonical close가 아직 발행되지 않아 미수집이라는 뜻이고, 0은 canonical close는 있으나 그 source의 기여가 없다는 뜻이다(미수집과 실제 0을 구분한다).';

revoke select on table
  public.bias_events,
  public.bias_event_by_source,
  public.bias_events_canonical,
  public.bias_event_by_source_canonical
from public, anon, authenticated;

-- 내부 트리거 함수는 RPC 표면이 아니므로 브라우저 역할의 EXECUTE를 허용하지 않는다
-- (202609051900_revoke_outcome_snapshot_trigger_execute.sql 선례).
revoke execute on function public.enforce_bias_event_trading_day() from public, anon, authenticated;

commit;
