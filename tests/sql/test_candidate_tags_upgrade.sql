-- Supabase SQL fixture for Story 6.3 N/N-1 upgrade compatibility.
-- CI runs this after the full migration set. It temporarily recreates the N-1
-- CHECK, commits legacy rows, then applies the exact Story 6.3 migration file.
-- The database is disposable in CI; production verification uses an equivalent
-- transaction-scoped SQL assertion through Supabase MCP.

begin;

alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check;
alter table public.candidate_tags
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C'));

do $$
declare
  started jsonb;
  run_id uuid;
  fence bigint;
  lease uuid;
  candidate_id uuid := gen_random_uuid();
begin
  started := public.start_attempt('close:2099-08-01', date '2099-08-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(
    run_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '000060', 'name', '업그레이드테스트', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('u', 64), 'original_count', 1, 'candidate_count', 1,
      'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values
      (candidate_id, run_id, 'A', date '2099-08-01'),
      (candidate_id, run_id, 'B', date '2099-08-01'),
      (candidate_id, run_id, 'C', date '2099-08-01');
end $$;

commit;

\ir ../../infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql

begin;

do $$
declare
  run_id uuid;
  candidate_id uuid;
begin
  select ct.attempt_run_id, ct.candidate_id
    into run_id, candidate_id
    from public.candidate_tags ct
   where ct.signal_date = date '2099-08-01'
   group by ct.attempt_run_id, ct.candidate_id;

  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 3 then
    raise exception 'legacy A/B/C candidate_tags rows were not preserved';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id and status = 'active') <> 3 then
    raise exception 'legacy candidate_tags defaults were not preserved';
  end if;

  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, run_id, 'D', date '2099-08-01'), (candidate_id, run_id, 'E', date '2099-08-01');
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 5 then
    raise exception 'D/E tags were not accepted after upgrade';
  end if;
end $$;

commit;

\ir ../../infra/supabase/migrations/202609071000_expand_candidate_tags_strategy_check_f.sql

begin;

do $$
declare
  run_id uuid;
  candidate_id uuid;
begin
  select ct.attempt_run_id, ct.candidate_id
    into run_id, candidate_id
    from public.candidate_tags ct
   where ct.signal_date = date '2099-08-01'
   group by ct.attempt_run_id, ct.candidate_id;

  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 5 then
    raise exception 'legacy A/B/C/D/E candidate_tags rows were not preserved after F expansion';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id and status = 'active') <> 5 then
    raise exception 'legacy candidate_tags defaults were not preserved after F expansion';
  end if;

  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, run_id, 'F', date '2099-08-01');
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 6 then
    raise exception 'F tag was not accepted after upgrade';
  end if;
  if (select status from public.candidate_tags where attempt_run_id = run_id and strategy = 'F') <> 'active' then
    raise exception 'expected F tag to receive status=active by default after upgrade';
  end if;
end $$;

-- 사전조건 가드 회귀: F 확장 migration을 (이미 한 번 적용된 상태에서) 실제로 다시
-- \ir 재실행해, migration 자신의 사전조건 DO 블록이 "F가 이미 존재함"을 감지하고
-- raise exception으로 스스로 중단하는지 검증한다. 사전조건 predicate를 이 테스트
-- 파일에 손으로 복사해 재평가하면, migration 파일 쪽 predicate에 실수(예: 오탈자로
-- `not like '%''F''%'` 절이 누락)가 있어도 이 테스트의 사본은 여전히 맞을 수 있어
-- 그 버그를 잡지 못한다 -- 그래서 반드시 실제 파일을 재실행한다.
--
-- ON_ERROR_STOP을 잠시 off로 두는 이유: 위 78행의 `begin;`으로 이미 트랜잭션이 열려
-- 있는 상태에서 이 migration 파일을 다시 \ir로 실행하면, 파일 안의 `begin;`은 이미
-- 진행 중인 트랜잭션에 대한 psql의 WARNING일 뿐 새 트랜잭션을 시작하지 않는다. 이어서
-- 파일의 사전조건 DO 블록이 "F가 이미 있음"을 감지해 raise exception을 던지면, 그 예외는
-- (새로 열린 게 아닌) 바로 이 바깥 트랜잭션 자체를 abort시킨다. 그 직후 파일의 `commit;`은
-- 이미 abort된 트랜잭션에 대한 psql의 암묵적 rollback이 되어 아무 것도 커밋하지 않고,
-- 세션은 트랜잭션이 없는 깨끗한 top-level 상태로 돌아온다(78행 이후 79-106행에서 검증한
-- 내용은 이미 raise exception 없이 통과했으므로, 이 rollback으로 사라져도 무방하다).
-- psql은 기본적으로 ON_ERROR_STOP이 켜져 있으면 이 예외에서 \ir 실행을 포함해 스크립트
-- 전체를 중단시켜 버리므로, 이 재적용 자체가 실패하는 것을 "기대하는" 이 블록에서만
-- 잠시 꺼두고, 위와 같이 안전하게 top-level로 돌아온 직후 다시 켜서 이 fixture의 나머지
-- 부분(진짜 회귀가 있으면 반드시 걸려야 하는 부분)은 계속 엄격하게 검사한다.
\set ON_ERROR_STOP off
\ir ../../infra/supabase/migrations/202609071000_expand_candidate_tags_strategy_check_f.sql
\set ON_ERROR_STOP on

-- 재적용 시도가 사전조건 가드에서 막혀 drop/add constraint까지 도달하지 못했는지
-- (즉 부분 손상 없이 A|B|C|D|E|F 그대로 남아있는지) 확인한다.
do $$
declare
  def text;
begin
  select pg_get_constraintdef(c.oid) into def
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'candidate_tags'
      and c.conname = 'candidate_tags_strategy_check'
      and c.contype = 'c';

  if def is null then
    raise exception 'candidate_tags_strategy_check constraint is missing after re-apply attempt';
  end if;
  if not (def like '%strategy%' and def like '%''A''%' and def like '%''B''%'
    and def like '%''C''%' and def like '%''D''%' and def like '%''E''%' and def like '%''F''%') then
    raise exception 'F-migration re-apply guard did not fire cleanly -- constraint no longer covers A|B|C|D|E|F, got: %', def;
  end if;
end $$;

select jsonb_build_object('status', 'PASS', 'fixture', 'test_candidate_tags_upgrade', 'legacy_rows_preserved', 5,
  'new_strategies_accepted', jsonb_build_array('D', 'E', 'F')) as verification;

rollback;
