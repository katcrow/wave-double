-- 2026-10-02: GitHub schedule 지연으로 장외(KST 20:00~08:00)에 실행된 예약 close attempt가
-- 실행 시점 날짜로 logical_run_key를 잡아 ready_to_publish로 남아 있었다. request_manual_dispatch는
-- active attempt가 ready_to_publish이면 ACTIVE_ATTEMPT conflict를 돌려주므로, 해당 거래일의
-- 정상 19:40 자동 close가 outbox에 들어가지 못했다(9/30, 10/1 실제 누락 확인).
-- 장외 예약 close 중 아직 종결되지 않은 attempt를 superseded로 닫고 active 포인터를 비운다.
-- publish된 적이 없으므로 대시보드/Outcome 데이터에는 영향이 없다.
begin;

with stale as (
  select r.run_id, r.logical_run_key
  from public.runs r
  join public.logical_runs l on l.logical_run_key = r.logical_run_key
  where r.trigger = 'schedule'
    and l.batch_kind = 'close'
    and l.canonical_success_run_id is null
    and r.status in ('running', 'ready_to_publish')
    and not ((r.started_at at time zone 'Asia/Seoul')::time >= time '19:30'
             and (r.started_at at time zone 'Asia/Seoul')::time < time '20:00')
), closed as (
  update public.runs r
  set status = 'superseded', finished_at = coalesce(r.finished_at, now())
  from stale
  where r.run_id = stale.run_id
  returning r.run_id, r.logical_run_key
)
update public.logical_runs l
set active_attempt_run_id = null
from closed
where l.logical_run_key = closed.logical_run_key
  and l.active_attempt_run_id = closed.run_id;

commit;
