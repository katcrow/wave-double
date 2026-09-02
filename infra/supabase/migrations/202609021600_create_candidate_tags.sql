-- Story 2.5: 후보 태깅 stage & 저장.
-- candidate_tags 테이블: 전략 A/B/C 시그널이 발생한 후보에 대한 태깅 이력.
-- attempt-scoped(AD-19): 태깅은 시도 단위로 기록되며 실패한 attempt가 이전 데이터를 덮어쓰지 않는다.
-- candidates(candidate_id, attempt_run_id) 합성키 FK를 candidate_source_contrib(202609011700)와
-- 동일하게 걸어 참조 무결성을 보장한다.
begin;

create table if not exists public.candidate_tags (
  tag_id uuid primary key default gen_random_uuid(),
  candidate_id uuid not null,
  attempt_run_id uuid not null,
  strategy text not null check (strategy in ('A', 'B', 'C')),
  signal_date date not null,
  tagged_at timestamptz not null default now(),
  status text not null default 'active' check (status in ('active', 'vanished')),
  params_meta jsonb not null default '{}'::jsonb,
  unique (candidate_id, strategy, attempt_run_id),
  foreign key (candidate_id, attempt_run_id)
    references public.candidates(candidate_id, attempt_run_id)
);

create index if not exists candidate_tags_attempt_idx on public.candidate_tags(attempt_run_id);

comment on table public.candidate_tags is 'Story 2.5: 전략 A/B/C 시그널 태깅 이력. attempt-scoped(AD-19), candidates에 합성키 FK.';
comment on column public.candidate_tags.signal_date is '시그널이 발생한 거래일(strategy_api 계산 기준, 마지막 봉 폐기 필터 반영).';
comment on column public.candidate_tags.params_meta is '시그널 계산에 사용된 파라미터 스냅샷(재현성 검증용).';
comment on column public.candidate_tags.status is 'active: 현재 배치에서 유효. vanished: 이전 배치에서 태깅되었으나 현재 배치에서 소멸(Story 2.8, 이번 스토리는 항상 active만 삽입).';

alter table public.candidate_tags enable row level security;

commit;
