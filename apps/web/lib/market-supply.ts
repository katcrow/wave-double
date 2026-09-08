import type { Market, MarketSupplyRpcRow } from "./dashboard-types";

export const MARKET_OPTIONS = ["KOSPI", "KOSDAQ"] as const satisfies readonly Market[];

export type MarketSupplyMetricKey =
  | "foreign_net"
  | "institution_net"
  | "individual_net"
  | "program_net";

export const MARKET_SUPPLY_METRICS = [
  { key: "foreign_net", label: "외인" },
  { key: "institution_net", label: "기관" },
  { key: "individual_net", label: "개인" },
  { key: "program_net", label: "프로그램" },
] as const satisfies readonly { key: MarketSupplyMetricKey; label: string }[];

export type MarketSupplyMetricDirection = "positive" | "negative" | "neutral";

export interface MarketSupplyMetricViewModel {
  key: MarketSupplyMetricKey;
  label: string;
  value: number;
  direction: MarketSupplyMetricDirection;
  directionLabel: "매수" | "매도" | "중립";
  barWidth: number;
}

export interface MarketSupplyViewModel {
  market: Market;
  row: MarketSupplyRpcRow | null;
  available: boolean;
  metrics: MarketSupplyMetricViewModel[];
}

const NUMBER_FORMATTER = new Intl.NumberFormat("ko-KR", {
  maximumFractionDigits: 6,
});

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isMarket(value: unknown): value is Market {
  return value === "KOSPI" || value === "KOSDAQ";
}

function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const candidate = new Date(Date.UTC(year, month - 1, day));
  return candidate.getUTCFullYear() === year
    && candidate.getUTCMonth() === month - 1
    && candidate.getUTCDate() === day;
}

function isIsoDateTime(value: unknown): value is string {
  return typeof value === "string" && Number.isFinite(new Date(value).getTime());
}

/** 브라우저 경계에서 RPC 응답의 숫자·시장·필수 문자열을 먼저 검증한다. */
export function isMarketSupplyRpcRow(value: unknown): value is MarketSupplyRpcRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    isMarket(row.market) &&
    isIsoDate(row.trading_day) &&
    isFiniteNumber(row.foreign_net) &&
    isFiniteNumber(row.institution_net) &&
    isFiniteNumber(row.individual_net) &&
    isFiniteNumber(row.program_net) &&
    isIsoDateTime(row.collected_at)
  );
}

/** 허용하지 않은 탭 값과 null은 KOSPI로 정규화한다. */
export function normalizeMarket(value: string | null | undefined): Market {
  return value === "KOSDAQ" ? "KOSDAQ" : "KOSPI";
}

function metricDirection(value: number): Pick<MarketSupplyMetricViewModel, "direction" | "directionLabel"> {
  if (value > 0) return { direction: "positive", directionLabel: "매수" };
  if (value < 0) return { direction: "negative", directionLabel: "매도" };
  return { direction: "neutral", directionLabel: "중립" };
}

function formatZero(value: number): number {
  return value === 0 ? 0 : value;
}

/** 시장 행의 네 수급 값과 화면용 상대 막대만 구성한다. 금융 힌트나 임계값은 계산하지 않는다. */
export function buildMarketSupplyViewModel(
  rows: readonly MarketSupplyRpcRow[] | null | undefined,
  market: Market
): MarketSupplyViewModel {
  const matchingRows = (rows ?? []).filter((row) => row.market === market);
  const row = matchingRows.length === 1 ? matchingRows[0] : null;
  if (!row) return { market, row: null, available: false, metrics: [] };

  const values = MARKET_SUPPLY_METRICS.map(({ key }) => formatZero(row[key]));
  const maxAbsoluteValue = Math.max(...values.map((value) => Math.abs(value)), Number.EPSILON);
  const metrics = MARKET_SUPPLY_METRICS.map(({ key, label }, index) => {
    const value = values[index];
    return {
      key,
      label,
      value,
      ...metricDirection(value),
      barWidth: value === 0 ? 0 : Math.max(1, Math.round((Math.abs(value) / maxAbsoluteValue) * 100)),
    };
  });

  return { market, row, available: true, metrics };
}

export function formatMarketSupplyNumber(value: number): string {
  return NUMBER_FORMATTER.format(formatZero(value));
}

export function formatMarketSupplyDate(iso: string): string {
  const timestamp = new Date(iso).getTime();
  if (!Number.isFinite(timestamp)) return "시각 미상";
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(timestamp));
}
