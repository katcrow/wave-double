-- Story 1.10: pg_cron이 매 1분 pg_net으로 outbox worker route를 깨운다.
-- Design Notes: Vercel Hobby는 1분 간격 cron을 지원하지 않으므로 durable fallback은 Supabase
-- pg_cron 1분 scan이다(AD-18). 실제 claim/GitHub 호출 로직은 Next.js server route에 남는다.
--
-- 운영 필수 후속 조치(이 migration만으로는 완결되지 않음 -- 배포별 URL/secret은 migration 시점에 알 수 없다):
--   alter database postgres set app.settings.dispatch_worker_url = 'https://<deployment-domain>/api/dispatch/worker';
--   alter database postgres set app.settings.cron_callback_secret = '<CRON_CALLBACK_SECRET과 동일한 값>';
-- 두 설정이 비어 있으면 net.http_post의 url/헤더가 비어 호출이 실패한다(로그로 확인 가능).
begin;

create extension if not exists pg_cron with schema extensions;
create extension if not exists pg_net with schema extensions;

do $$
begin
  if exists (select 1 from cron.job where jobname = 'dispatch-outbox-worker-tick') then
    perform cron.unschedule('dispatch-outbox-worker-tick');
  end if;
end $$;

select cron.schedule(
  'dispatch-outbox-worker-tick',
  '* * * * *',
  $$
  select net.http_post(
    url := current_setting('app.settings.dispatch_worker_url', true),
    headers := jsonb_build_object(
      'content-type', 'application/json',
      'x-cron-secret', current_setting('app.settings.cron_callback_secret', true)
    ),
    body := '{}'::jsonb
  );
  $$
);

commit;
