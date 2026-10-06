import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildMarketSupplyViewModel,
  formatMarketIndexChangeRate,
  formatMarketIndexPrice,
  formatMarketSupplyNumber,
  isMarketSupplyRpcRow,
} from "./market-supply.ts";
import type { MarketSupplyRpcRow } from "./dashboard-types.ts";

function row(overrides: Partial<MarketSupplyRpcRow> = {}): MarketSupplyRpcRow {
  return {
    market: "KOSPI",
    trading_day: "2026-09-08",
    foreign_net: 100,
    institution_net: -50,
    individual_net: 0,
    program_net: 25,
    collected_at: "2026-09-08T01:00:00.000Z",
    ...overrides,
  };
}

test("RPC 행은 허용된 시장과 유한 숫자만 통과한다", () => {
  assert.equal(isMarketSupplyRpcRow(row()), true);
  assert.equal(isMarketSupplyRpcRow({ ...row(), market: "NASDAQ" }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), trading_day: "2026-02-30" }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), collected_at: "not-a-date" }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), foreign_net: Number.NaN }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), program_net: "25" }), false);
});

test("시장별 행이 하나뿐일 때 부호·0·방향·상대 막대를 보존한다", () => {
  const view = buildMarketSupplyViewModel([row()], "KOSPI");
  assert.equal(view.available, true);
  assert.deepEqual(
    view.metrics.map((metric) => [metric.key, metric.value, metric.direction, metric.directionLabel, metric.barWidth]),
    [
      ["foreign_net", 100, "positive", "매수", 100],
      ["institution_net", -50, "negative", "매도", 50],
      ["individual_net", 0, "neutral", "중립", 0],
      ["program_net", 25, "positive", "매수", 25],
    ]
  );
  assert.equal(formatMarketSupplyNumber(-50), "-50");
  assert.equal(formatMarketSupplyNumber(0), "0");
});

test("선택 시장의 행이 없거나 중복이면 정상 데이터로 위장하지 않는다", () => {
  assert.equal(buildMarketSupplyViewModel([row()], "KOSDAQ").available, false);
  assert.equal(buildMarketSupplyViewModel([row(), row()], "KOSPI").available, false);
});

test("1억원 미만 값은 0으로 표시되지만 상대 막대는 저장값 기준으로 채워진다", () => {
  const view = buildMarketSupplyViewModel([
    row({ foreign_net: 0.004, institution_net: -0.002, individual_net: 0, program_net: 0.001 }),
  ], "KOSPI");
  assert.equal(formatMarketSupplyNumber(view.metrics[0].value), "0");
  assert.equal(view.metrics[0].barWidth, 100);
  assert.equal(view.metrics[1].barWidth, 50);
});

test("최대값에 비해 작은 유효 수치도 방향 막대가 사라지지 않는다", () => {
  const view = buildMarketSupplyViewModel([
    row({ foreign_net: 100, institution_net: -0.001, individual_net: 0, program_net: 0 }),
  ], "KOSPI");
  assert.equal(view.metrics[1].barWidth, 1);
});

test("지수 등락 필드는 누락·null을 허용하되 값이 있으면 유효해야 한다", () => {
  assert.equal(isMarketSupplyRpcRow({ ...row(), index_price: null, index_change_rate: null }), true);
  assert.equal(isMarketSupplyRpcRow({ ...row(), index_change_rate: -0.85, advancing_count: 402 }), true);
  assert.equal(isMarketSupplyRpcRow({ ...row(), index_change_rate: Number.NaN }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), index_price: "6943.90" }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), advancing_count: -1 }), false);
  assert.equal(isMarketSupplyRpcRow({ ...row(), declining_count: 1.5 }), false);
});

test("지수와 종목수가 있으면 등락 방향과 비율을 구성한다", () => {
  const view = buildMarketSupplyViewModel([
    row({
      index_price: 6943.9,
      index_change_rate: -0.85,
      advancing_count: 402,
      unchanged_count: 76,
      declining_count: 466,
    }),
  ], "KOSPI");
  assert.deepEqual(view.index, { price: 6943.9, changeRate: -0.85, direction: "negative" });
  assert.equal(view.breadth?.advancing, 402);
  assert.equal(view.breadth?.declining, 466);
  const shares = view.breadth!;
  assert.ok(Math.abs(shares.advancingShare + shares.unchangedShare + shares.decliningShare - 100) < 1e-9);
  assert.equal(formatMarketIndexPrice(6943.9), "6,943.90");
  assert.equal(formatMarketIndexChangeRate(-0.85), "-0.85%");
  assert.equal(formatMarketIndexChangeRate(2.4), "+2.40%");
  assert.equal(formatMarketIndexChangeRate(0), "0.00%");
});

test("지수 필드가 없거나 일부만 있으면 해당 영역을 숨긴다", () => {
  const legacy = buildMarketSupplyViewModel([row()], "KOSPI");
  assert.equal(legacy.available, true);
  assert.equal(legacy.index, null);
  assert.equal(legacy.breadth, null);

  const partial = buildMarketSupplyViewModel([
    row({ index_price: 900, index_change_rate: null, advancing_count: 10, unchanged_count: null, declining_count: 5 }),
  ], "KOSPI");
  assert.equal(partial.index, null);
  assert.equal(partial.breadth, null);
});

test("금액은 소수점 없이 반올림해 표시하고 -0을 만들지 않는다", () => {
  assert.equal(formatMarketSupplyNumber(-980.1), "-980");
  assert.equal(formatMarketSupplyNumber(-3215.5), "-3,216");
  assert.equal(formatMarketSupplyNumber(1850.5), "1,851");
  assert.equal(formatMarketSupplyNumber(-0.4), "0");
});
