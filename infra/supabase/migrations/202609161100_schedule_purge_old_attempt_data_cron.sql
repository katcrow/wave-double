-- 2026-09-16: purge_old_attempt_data(202609141800)가 함수만 만들어지고 실제로 부르는
-- pg_cron job이 없었다(Neo 확인) -- Supabase 무료 플랜(500MB) 용량 관리가 자동화되지
-- 않고 있었다. 매일 KST 00:00(=UTC 15:00 전날, cron.timezone=GMT 확인됨)에 1회
-- retention_days=7(함수 기본값)로 정리한다. pg_cron/SQL만으로 완결되는 순수 DB 내부
-- 작업이라 dispatch 파이프라인(Vercel/GitHub Actions)과는 무관하다.
begin;

-- pg_cron job은 postgres 역할로 실행되는데, purge_old_attempt_data는 지금 service_role
-- 에게만 EXECUTE가 부여돼 있다(Story item-14 기준). auto-schedule-dispatch-tick 선례와
-- 동일하게 postgres에게도 EXECUTE를 추가한다.
grant execute on function public.purge_old_attempt_data(integer) to postgres;

do $$
begin
  if exists (select 1 from cron.job where jobname = 'purge-old-attempt-data-daily') then
    perform cron.unschedule('purge-old-attempt-data-daily');
  end if;
end $$;

select cron.schedule(
  'purge-old-attempt-data-daily',
  '0 15 * * *', -- UTC 15:00 = KST 00:00 (cron.timezone=GMT)
  $$select public.purge_old_attempt_data(7);$$
);

commit;
