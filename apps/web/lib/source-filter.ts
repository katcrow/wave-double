export const SOURCE_QUERY_KEY = "source";
import type { TrackingSource } from "./dashboard-types";

export const SOURCE_OPTIONS = ["t1859", "t1852", "t1856"] as const satisfies readonly TrackingSource[];

export type SourceFilter = TrackingSource | "";

type QueryInput = URLSearchParams | Readonly<Record<string, string | string[] | undefined | null>>;

const SOURCE_LABELS: Record<TrackingSource, string> = {
  t1859: "t1859 본원천",
  t1852: "t1852 폴백 원천",
  t1856: "t1856 폴백 원천",
};

function readQueryValue(input: QueryInput, key: string): string | null {
  if (input instanceof URLSearchParams) return input.get(key);
  const value = input[key];
  return Array.isArray(value) ? value[0] ?? null : value ?? null;
}

export function normalizeSource(input: QueryInput): SourceFilter {
  const value = readQueryValue(input, SOURCE_QUERY_KEY)?.trim() ?? "";
  return (SOURCE_OPTIONS as readonly string[]).includes(value) ? value as TrackingSource : "";
}

export function getSourceLabel(source: SourceFilter): string {
  return source ? SOURCE_LABELS[source] : "전체 원천 통합";
}

export function getSourceScopeDescription(source: SourceFilter): string {
  return source
    ? `${getSourceLabel(source)} 기준의 원천별 결과입니다.`
    : "세 원천을 합친 전체 통합 결과이며, 여러 원천이 혼합된 지표입니다.";
}
