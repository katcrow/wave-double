import type { MarketIndexProbabilityRpcRow } from "./dashboard-types.ts";

export type MarketProbabilityChipState =
  | { status: "failed" }
  | { status: "empty" }
  | {
      status: "ready";
      stale: boolean;
      kospiPercent: string;
      kosdaqPercent: string;
      row: MarketIndexProbabilityRpcRow;
    };

export function formatProbabilityPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

/** 종가배팅 참고확률 칩의 표시 상태. 조회 실패가 값 유무보다 우선한다. */
export function deriveMarketProbabilityChipState(
  row: MarketIndexProbabilityRpcRow | null,
  fetchFailed: boolean,
  todayKst: string,
): MarketProbabilityChipState {
  if (fetchFailed) return { status: "failed" };
  if (!row) return { status: "empty" };
  return {
    status: "ready",
    stale: row.trading_day !== todayKst,
    kospiPercent: formatProbabilityPercent(row.kospi_probability),
    kosdaqPercent: formatProbabilityPercent(row.kosdaq_probability),
    row,
  };
}
