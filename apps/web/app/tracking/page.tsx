import DataTrustBar from "@/components/dashboard/DataTrustBar";
import OutcomeTrackingPanel from "@/components/tracking/OutcomeTrackingPanel";
import { isDashboardSnapshot, type DashboardSnapshot } from "@/lib/dashboard-types";
import {
  isOutcomeTrackingRpcResponse,
  normalizeOutcomeFilters,
  toOutcomeTrackingRpcParams,
} from "@/lib/outcome-tracking";
import { createSupabaseServerClient } from "@/lib/supabase-server";

export const dynamic = "force-dynamic";

export default async function TrackingPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const supabase = await createSupabaseServerClient();
  const { data: snapshotData, error: snapshotError } = await supabase.rpc("get_dashboard_snapshot");

  if (snapshotError) {
    console.error("get_dashboard_snapshot failed", snapshotError);
    return (
      <section aria-labelledby="tracking-heading">
        <h1 id="tracking-heading">성과 검증</h1>
        <p role="alert">성과 검증 데이터를 불러오지 못했습니다.</p>
      </section>
    );
  }

  if (!isDashboardSnapshot(snapshotData)) {
    console.error("unexpected get_dashboard_snapshot shape", snapshotData);
    return (
      <section aria-labelledby="tracking-heading">
        <h1 id="tracking-heading">성과 검증</h1>
        <p role="alert">성과 검증 데이터를 불러오지 못했습니다.</p>
      </section>
    );
  }

  const snapshot: DashboardSnapshot = snapshotData;
  const filters = normalizeOutcomeFilters(await searchParams);
  const { data: outcomeData, error: outcomeError } = await supabase.rpc(
    "get_outcome_tracking_rows",
    toOutcomeTrackingRpcParams(filters),
  );
  const fetchFailed = Boolean(outcomeError) || !isOutcomeTrackingRpcResponse(outcomeData);
  if (outcomeError) {
    console.error("get_outcome_tracking_rows failed", outcomeError);
  } else if (!isOutcomeTrackingRpcResponse(outcomeData)) {
    console.error("unexpected get_outcome_tracking_rows shape", outcomeData);
  }

  return (
    <section aria-labelledby="tracking-heading">
      <h1 id="tracking-heading">성과 검증</h1>
      <DataTrustBar snapshot={snapshot} focusStage="outcome_tracking" />
      <OutcomeTrackingPanel
        rows={fetchFailed ? [] : outcomeData}
        fetchFailed={fetchFailed}
      />
    </section>
  );
}
