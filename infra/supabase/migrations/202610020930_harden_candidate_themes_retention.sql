-- candidate_themes는 후보 attempt와 함께 보존 정리되어야 한다.
-- 기존 202610020900 migration이 이미 적용된 운영 DB도 FK 동작을 갱신한다.
begin;

alter table public.candidate_themes
  drop constraint if exists candidate_themes_candidate_id_attempt_run_id_fkey;

alter table public.candidate_themes
  add constraint candidate_themes_candidate_id_attempt_run_id_fkey
  foreign key (candidate_id, attempt_run_id)
  references public.candidates(candidate_id, attempt_run_id)
  on delete cascade;

commit;
