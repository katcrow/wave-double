-- CI 전용 pg_cron 스텁.
--
-- 순정 postgres:16 이미지에는 pg_cron/pg_net이 없다. `cron.schedule`/`cron.unschedule`을
-- 호출하는 migration은 실제 Supabase 운영에서만 성립하므로, CI의 로컬 적용 단계에서
-- 그대로 실행하면 실패한다. migration 본문을 수정하지 않기 위해(forward-only, 적용 이력 보존)
-- CI에서만 필요한 최소 객체(스키마/테이블/함수)를 미리 만들어 둔다.
--
-- 대상 migration:
--   - 202609151600_add_auto_schedule_dispatch_cron.sql
--   - 202609161100_schedule_purge_old_attempt_data_cron.sql
-- pg_cron을 `create extension` 하는 202609021100_schedule_dispatch_worker_cron.sql은
-- 확장 자체가 없어 이 스텁으로도 수행할 수 없으므로 CI 적용 단계에서 별도로 건너뛴다.
--
-- 스키마에 아무 DDL도 남기지 않으므로(migration들은 cron.schedule/unschedule만 호출) pg_dump
-- 기반 N/N-1 스키마 패리티 비교에는 영향을 주지 않는다.

create schema if not exists cron;

create table if not exists cron.job (
  jobid bigserial primary key,
  jobname text
);

create or replace function cron.schedule(p_job_name text, p_schedule text, p_command text)
returns bigint
language sql
as $$ select 1::bigint $$;

create or replace function cron.unschedule(p_job_name text)
returns boolean
language sql
as $$ select true $$;
