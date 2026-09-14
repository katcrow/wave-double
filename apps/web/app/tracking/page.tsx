import DataTrustBar from "@/components/dashboard/DataTrustBar";
import BiasDiagnosticPanel from "@/components/tracking/BiasDiagnosticPanel";
import MetricComparisonPanel from "@/components/tracking/MetricComparisonPanel";
import OutcomeTrackingPanel from "@/components/tracking/OutcomeTrackingPanel";
import { isDashboardSnapshot, type DashboardSnapshot } from "@/lib/dashboard-types";
import {
  isBiasDiagnosticRpcResponse,
  normalizeBiasDate,
  toBiasDiagnosticRpcParams,
} from "@/lib/bias-diagnostic";
import {
  isOutcomeMetricComparisonRpcResponse,
  normalizeMetricStrategy,
  toMetricComparisonRpcParams,
} from "@/lib/metric-comparison";
import { normalizeSource } from "@/lib/source-filter";
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
  const params = await searchParams;
  const filters = normalizeOutcomeFilters(params);
  const metricStrategy = normalizeMetricStrategy(params);
  const biasDate = normalizeBiasDate(params);
  const source = normalizeSource(params);
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

  const { data: metricData, error: metricError } = await supabase.rpc(
    "get_outcome_metric_comparison",
    toMetricComparisonRpcParams(metricStrategy, source),
  );
  const metricFetchFailed = Boolean(metricError) || !isOutcomeMetricComparisonRpcResponse(metricData, metricStrategy);
  if (metricError) {
    console.error("get_outcome_metric_comparison failed", metricError);
  } else if (!isOutcomeMetricComparisonRpcResponse(metricData, metricStrategy)) {
    console.error("unexpected get_outcome_metric_comparison shape", metricData);
  }

  const { data: biasData, error: biasError } = await supabase.rpc(
    "get_bias_diagnostic",
    toBiasDiagnosticRpcParams(biasDate, source),
  );
  const biasFetchFailed = Boolean(biasError) || !isBiasDiagnosticRpcResponse(biasData, biasDate);
  if (biasError) {
    console.error("get_bias_diagnostic failed", biasError);
  } else if (!isBiasDiagnosticRpcResponse(biasData, biasDate)) {
    console.error("unexpected get_bias_diagnostic shape", biasData);
  }

  return (
    <section aria-labelledby="tracking-heading">
      <h1 id="tracking-heading">성과 검증</h1>
      <DataTrustBar snapshot={snapshot} focusStage="outcome_tracking" />
      <MetricComparisonPanel
        rows={metricFetchFailed ? [] : metricData}
        fetchFailed={metricFetchFailed}
        selectedStrategy={metricStrategy}
        selectedSource={source}
      />
      <BiasDiagnosticPanel
        row={biasFetchFailed ? null : biasData}
        fetchFailed={biasFetchFailed}
        selectedDate={biasDate}
        selectedSource={source}
      />
      <OutcomeTrackingPanel
        rows={fetchFailed ? [] : outcomeData}
        fetchFailed={fetchFailed}
      />
    </section>
  );
}
