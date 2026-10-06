import type { Market, MarketMacroRpcRow, MarketMacroSymbol, MarketSupplyRpcRow } from "./dashboard-types";

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

export interface MarketIndexViewModel {
  price: number;
  changeRate: number;
  direction: MarketSupplyMetricDirection;
}

export interface MarketBreadthViewModel {
  advancing: number;
  unchanged: number;
  declining: number;
  /** 상승·보합·하락 비율 막대용 %(합계 100). */
  advancingShare: number;
  unchangedShare: number;
  decliningShare: number;
}

export interface MarketSupplyViewModel {
  market: Market;
  row: MarketSupplyRpcRow | null;
  available: boolean;
  metrics: MarketSupplyMetricViewModel[];
  index: MarketIndexViewModel | null;
  breadth: MarketBreadthViewModel | null;
}

// 금액(억원)은 소수점 없이 정수로 표시한다. 저장값의 정밀도는 막대 계산에만 쓴다.
const NUMBER_FORMATTER = new Intl.NumberFormat("ko-KR", {
  maximumFractionDigits: 0,
});

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isMarket(value: unknown): value is Market {
  return value === "KOSPI" || value === "KOSDAQ";
}

function isOptionalFiniteNumber(value: unknown): boolean {
  return value === undefined || value === null || isFiniteNumber(value);
}

function isOptionalCount(value: unknown): boolean {
  return value === undefined || value === null || (Number.isInteger(value) && (value as number) >= 0);
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
    isOptionalFiniteNumber(row.index_price) &&
    isOptionalFiniteNumber(row.index_change_rate) &&
    isOptionalCount(row.advancing_count) &&
    isOptionalCount(row.unchanged_count) &&
    isOptionalCount(row.declining_count) &&
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
  if (!row) return { market, row: null, available: false, metrics: [], index: null, breadth: null };

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

  return { market, row, available: true, metrics, index: buildIndex(row), breadth: buildBreadth(row) };
}

function buildIndex(row: MarketSupplyRpcRow): MarketIndexViewModel | null {
  if (!isFiniteNumber(row.index_price) || !isFiniteNumber(row.index_change_rate)) return null;
  const changeRate = formatZero(row.index_change_rate);
  return { price: row.index_price, changeRate, direction: metricDirection(changeRate).direction };
}

/** 세 종목수가 모두 있을 때만 구성한다. 일부만 있으면 비율이 왜곡되므로 숨긴다. */
function buildBreadth(row: MarketSupplyRpcRow): MarketBreadthViewModel | null {
  const { advancing_count: advancing, unchanged_count: unchanged, declining_count: declining } = row;
  if (!isFiniteNumber(advancing) || !isFiniteNumber(unchanged) || !isFiniteNumber(declining)) return null;
  const total = advancing + unchanged + declining;
  if (total <= 0) return null;
  const share = (count: number) => (count / total) * 100;
  return {
    advancing,
    unchanged,
    declining,
    advancingShare: share(advancing),
    unchangedShare: share(unchanged),
    decliningShare: share(declining),
  };
}

const INDEX_FORMATTER = new Intl.NumberFormat("ko-KR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function formatMarketIndexPrice(value: number): string {
  return INDEX_FORMATTER.format(value);
}

/** 등락률은 부호를 항상 붙인다(+0.85% / -0.85% / 0.00%). */
export function formatMarketIndexChangeRate(value: number): string {
  const rate = formatZero(value);
  const sign = rate > 0 ? "+" : "";
  return `${sign}${INDEX_FORMATTER.format(rate)}%`;
}

const COUNT_FORMATTER = new Intl.NumberFormat("ko-KR");

export function formatMarketBreadthCount(value: number): string {
  return COUNT_FORMATTER.format(value);
}

export function formatMarketSupplyNumber(value: number): string {
  // 부호와 무관하게 반올림(half away from zero)하고, -0.4 같은 값이 "-0"으로 보이지 않게 한다.
  const rounded = Math.sign(value) * Math.round(Math.abs(value));
  return NUMBER_FORMATTER.format(formatZero(rounded));
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

/** 표시 순서와 라벨. 가격 소수 자릿수는 시세 원본 단위를 따른다. */
export const MARKET_MACRO_ITEMS = [
  { symbol: "CME@NQ", label: "나스닥100 선물" },
  { symbol: "USDKRWSMBS", label: "원/달러" },
] as const satisfies readonly { symbol: MarketMacroSymbol; label: string }[];

export interface MarketMacroViewModel {
  symbol: MarketMacroSymbol;
  label: string;
  price: number;
  changeRate: number;
  direction: MarketSupplyMetricDirection;
  quoteDate: string | null;
}

function isMarketMacroSymbol(value: unknown): value is MarketMacroSymbol {
  return MARKET_MACRO_ITEMS.some((item) => item.symbol === value);
}

export function isMarketMacroRpcRow(value: unknown): value is MarketMacroRpcRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    isMarketMacroSymbol(row.symbol) &&
    isFiniteNumber(row.price) &&
    row.price > 0 &&
    isFiniteNumber(row.change) &&
    isFiniteNumber(row.change_rate) &&
    (row.quote_date === null || isIsoDate(row.quote_date)) &&
    isIsoDateTime(row.collected_at)
  );
}

/** 표시 순서대로, 행이 있는 심볼만 구성한다(조회 실패 심볼은 숨긴다). */
export function buildMarketMacroViewModels(
  rows: readonly MarketMacroRpcRow[] | null | undefined
): MarketMacroViewModel[] {
  return MARKET_MACRO_ITEMS.flatMap(({ symbol, label }) => {
    const row = (rows ?? []).find((candidate) => candidate.symbol === symbol);
    if (!row) return [];
    const changeRate = formatZero(row.change_rate);
    return [{
      symbol,
      label,
      price: row.price,
      changeRate,
      direction: metricDirection(changeRate).direction,
      quoteDate: row.quote_date,
    }];
  });
}

/** 2026-10-05 → 10/05 */
export function formatMarketMacroQuoteDate(iso: string): string {
  const [, month, day] = iso.split("-");
  return `${month}/${day}`;
}
