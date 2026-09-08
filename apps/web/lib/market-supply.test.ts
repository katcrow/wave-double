import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildMarketSupplyViewModel,
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

test("1보다 작은 값도 0으로 뭉개지지 않고 상대 막대가 채워진다", () => {
  const view = buildMarketSupplyViewModel([
    row({ foreign_net: 0.004, institution_net: -0.002, individual_net: 0, program_net: 0.001 }),
  ], "KOSPI");
  assert.equal(formatMarketSupplyNumber(view.metrics[0].value), "0.004");
  assert.equal(view.metrics[0].barWidth, 100);
  assert.equal(view.metrics[1].barWidth, 50);
});

test("최대값에 비해 작은 유효 수치도 방향 막대가 사라지지 않는다", () => {
  const view = buildMarketSupplyViewModel([
    row({ foreign_net: 100, institution_net: -0.001, individual_net: 0, program_net: 0 }),
  ], "KOSPI");
  assert.equal(view.metrics[1].barWidth, 1);
});
