import type { MarketIndexProbabilityRpcRow } from "./dashboard-types.ts";

export type MarketProbabilityChipState =
  | { status: "failed" }
  | { status: "empty" }
  | {
      status: "ready";
      stale: boolean;
      kospiPercent: string;
      kosdaqPercent: string;
      /** 같은 기준의 평소(기본) 성공률. base rate가 없으면(v1 행) null. */
      kospiBasePercent: string | null;
      kosdaqBasePercent: string | null;
      /** 평소 대비 차이("+0.8%p"). base rate가 없으면 null. */
      kospiDelta: string | null;
      kosdaqDelta: string | null;
      row: MarketIndexProbabilityRpcRow;
    };

export function formatProbabilityPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

/** 표시된 두 퍼센트(각각 formatProbabilityPercent와 같은 소수 1자리 반올림)의 차이를 %p로 표시한다.
 *  표시값끼리 뺀 값이라 "62.3% · 평소 61.6% · +0.7%p"처럼 칩 안에서 서로 어긋나지 않는다. 0이면 "±0.0%p". */
export function formatProbabilityDelta(probability: number, baseRate: number): string {
  const tenths = (value: number) => Math.round(Number(formatProbabilityPercent(value).slice(0, -1)) * 10);
  const diff = tenths(probability) - tenths(baseRate);
  if (diff === 0) return "±0.0%p";
  return `${diff > 0 ? "+" : "-"}${(Math.abs(diff) / 10).toFixed(1)}%p`;
}

/** 종가배팅 참고확률 칩의 표시 상태. 조회 실패가 값 유무보다 우선한다. */
export function deriveMarketProbabilityChipState(
  row: MarketIndexProbabilityRpcRow | null,
  fetchFailed: boolean,
  todayKst: string,
): MarketProbabilityChipState {
  if (fetchFailed) return { status: "failed" };
  if (!row) return { status: "empty" };
  const kospiBase = row.kospi_base_rate ?? null;
  const kosdaqBase = row.kosdaq_base_rate ?? null;
  return {
    status: "ready",
    stale: row.trading_day !== todayKst,
    kospiPercent: formatProbabilityPercent(row.kospi_probability),
    kosdaqPercent: formatProbabilityPercent(row.kosdaq_probability),
    kospiBasePercent: kospiBase === null ? null : formatProbabilityPercent(kospiBase),
    kosdaqBasePercent: kosdaqBase === null ? null : formatProbabilityPercent(kosdaqBase),
    kospiDelta: kospiBase === null ? null : formatProbabilityDelta(row.kospi_probability, kospiBase),
    kosdaqDelta: kosdaqBase === null ? null : formatProbabilityDelta(row.kosdaq_probability, kosdaqBase),
    row,
  };
}
