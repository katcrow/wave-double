-- Restore snapshot sections lost by the trading-day ordering patch while keeping trading_day as primary order.
begin;

create or replace function public.get_dashboard_snapshot()
returns jsonb
language plpgsql
security definer
stable
set search_path = public
as $$
declare
  complete_logical public.logical_runs%rowtype;
  complete_run public.runs%rowtype;
  latest_run public.runs%rowtype;
  latest_logical public.logical_runs%rowtype;
  candidate_count integer := 0;
  tag_count integer := 0;
  open_count integer := 0;
  supply_row_count integer := 0;
  market_supply_row_count integer := 0;
  has_complete boolean := false;
  has_latest boolean := false;
  has_outcome_tracking boolean := false;
  has_supply_3day boolean := false;
  has_market_supply boolean := false;
  sections jsonb;
  available_sections jsonb := '[]'::jsonb;
  missing_sections jsonb := '[]'::jsonb;
begin
  select * into complete_logical
    from logical_runs
    where current_complete_run_id is not null
    order by trading_day desc, published_at desc nulls last, logical_run_key desc
    limit 1;

  if complete_logical.logical_run_key is not null then
    select * into complete_run from runs where run_id = complete_logical.current_complete_run_id;
    if complete_run.run_id is not null then
      has_complete := true;
      select count(*) into candidate_count from candidates where attempt_run_id = complete_run.run_id;
      select count(*) into tag_count from candidate_tags where attempt_run_id = complete_run.run_id;
      has_supply_3day := complete_run.stage_status->>'supply_3day' = 'success';
      if has_supply_3day then
        select count(*) into supply_row_count from supply_3day where attempt_run_id = complete_run.run_id;
      end if;
      has_market_supply := complete_run.stage_status->>'market_supply' = 'success';
      if has_market_supply then
        select count(*) into market_supply_row_count from market_supply where attempt_run_id = complete_run.run_id;
      end if;
      has_outcome_tracking := complete_logical.batch_kind = 'close' and complete_run.stage_status->>'outcome_tracking' = 'success';
      if has_outcome_tracking then
        select count(*) into open_count
          from outcome_events
          where logical_run_key = complete_run.logical_run_key and command_type = 'OPEN';
      end if;
    end if;
  end if;

  select * into latest_run from runs order by started_at desc, run_id desc limit 1;
  if latest_run.run_id is not null then
    has_latest := true;
    select * into latest_logical from logical_runs where logical_run_key = latest_run.logical_run_key;
  end if;

  sections := jsonb_build_object(
    'candidates', jsonb_build_object(
      'candidate_count', candidate_count,
      'truncated_count', complete_run.truncated_count,
      'original_count', complete_run.original_count,
      'excluded_count', complete_run.excluded_count
    ),
    'tags', jsonb_build_object('tag_count', tag_count)
  );
  if has_supply_3day then
    sections := sections || jsonb_build_object('supply_3day', jsonb_build_object('row_count', supply_row_count));
  end if;
  if has_market_supply then
    sections := sections || jsonb_build_object('market_supply', jsonb_build_object('row_count', market_supply_row_count));
  end if;
  if has_outcome_tracking then
    sections := sections || jsonb_build_object('outcome_tracking', jsonb_build_object('open_count', open_count));
  end if;

  available_sections := jsonb_build_array('candidates', 'tags');
  if has_supply_3day then
    available_sections := available_sections || jsonb_build_array('supply_3day');
  end if;
  if has_market_supply then
    available_sections := available_sections || jsonb_build_array('market_supply');
  end if;
  if has_outcome_tracking then
    available_sections := available_sections || jsonb_build_array('outcome_tracking');
  end if;

  if has_complete then
    missing_sections := '[]'::jsonb;
    if not has_supply_3day then
      missing_sections := missing_sections || '["supply_3day"]'::jsonb;
    end if;
    if not has_market_supply then
      missing_sections := missing_sections || '["market_supply"]'::jsonb;
    end if;
    if not has_outcome_tracking then
      missing_sections := missing_sections || '["outcome_tracking"]'::jsonb;
    end if;
  else
    missing_sections := '["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"]'::jsonb;
  end if;

  return jsonb_build_object(
    'no_snapshot', not has_complete,
    'result_code', case when has_complete then 'OK' else 'NO_SNAPSHOT' end,
    'complete_snapshot', case when not has_complete then null else jsonb_build_object(
      'logical_run_key', complete_run.logical_run_key,
      'run_id', complete_run.run_id,
      'trading_day', complete_logical.trading_day,
      'batch_kind', complete_logical.batch_kind,
      'published_at', complete_logical.published_at,
      'sections', sections
    ) end,
    'latest_attempt', case when not has_latest then null else jsonb_build_object(
      'run_id', latest_run.run_id,
      'logical_run_key', latest_run.logical_run_key,
      'trading_day', latest_logical.trading_day,
      'batch_kind', latest_logical.batch_kind,
      'status', latest_run.status,
      'trigger', latest_run.trigger,
      'started_at', latest_run.started_at,
      'finished_at', latest_run.finished_at,
      'stage_status', latest_run.stage_status,
      'unprocessed_count', latest_run.unprocessed_count,
      'truncated_count', latest_run.truncated_count,
      'original_count', latest_run.original_count,
      'excluded_count', latest_run.excluded_count
    ) end,
    'latest_partial_run_id', case when has_latest then latest_logical.latest_partial_run_id else null end,
    'available_partial_sections', case when has_complete then available_sections else '[]'::jsonb end,
    'missing_sections', missing_sections,
    'unprocessed_items', case when has_latest then latest_run.unprocessed_count else 0 end
  );
end;
$$;

comment on function public.get_dashboard_snapshot() is
  'Story 4.5: complete_snapshot에 성공한 market_supply section(row_count)을 반영하고, 미완료 시 missing_sections에 남긴다. section 순서는 candidates/tags/supply_3day/market_supply/outcome_tracking이다.';


revoke execute on function public.get_dashboard_snapshot() from public;
grant execute on function public.get_dashboard_snapshot() to anon, authenticated, service_role;

commit;

