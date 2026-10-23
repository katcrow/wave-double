import assert from "node:assert/strict";
import { test } from "node:test";
import { deriveMarketProbabilityChipState, formatProbabilityDelta } from "./market-probability.ts";
import { isMarketIndexProbabilityRpcRow, type MarketIndexProbabilityRpcRow } from "./dashboard-types.ts";

const TODAY = "2026-10-21";

function row(overrides: Partial<MarketIndexProbabilityRpcRow> = {}): MarketIndexProbabilityRpcRow {
  return {
    trading_day: TODAY,
    target_trading_day: "2026-10-22",
    kospi_probability: 0.6234,
    kosdaq_probability: 0.4,
    kospi_base_rate: 0.6154,
    kosdaq_base_rate: 0.4512,
    last_success_at: "2026-10-21T06:20:00Z",
    feature_as_of: "2026-10-21T06:15:00Z",
    model_version: "v1",
    validation_status: "experimental",
    ...overrides,
  };
}

test("정상: 오늘 행이면 ready, stale 아님, 소수 1자리 퍼센트", () => {
  const state = deriveMarketProbabilityChipState(row(), false, TODAY);
  assert.equal(state.status, "ready");
  if (state.status !== "ready") return;
  assert.equal(state.stale, false);
  assert.equal(state.kospiPercent, "62.3%");
  assert.equal(state.kosdaqPercent, "40.0%");
});

test("직전값: trading_day가 오늘과 다르면 stale", () => {
  const state = deriveMarketProbabilityChipState(row({ trading_day: "2026-10-20" }), false, TODAY);
  assert.equal(state.status, "ready");
  if (state.status !== "ready") return;
  assert.equal(state.stale, true);
});

test("값 없음: row null이고 실패 아니면 empty", () => {
  assert.deepEqual(deriveMarketProbabilityChipState(null, false, TODAY), { status: "empty" });
});

test("조회 실패: fetchFailed면 row가 있어도 failed", () => {
  assert.deepEqual(deriveMarketProbabilityChipState(null, true, TODAY), { status: "failed" });
  assert.deepEqual(deriveMarketProbabilityChipState(row(), true, TODAY), { status: "failed" });
});

test("평소 대비: base rate가 있으면 평소 퍼센트와 부호 있는 %p 차이", () => {
  const state = deriveMarketProbabilityChipState(row(), false, TODAY);
  assert.equal(state.status, "ready");
  if (state.status !== "ready") return;
  assert.equal(state.kospiBasePercent, "61.5%");
  assert.equal(state.kospiDelta, "+0.8%p");
  assert.equal(state.kosdaqBasePercent, "45.1%");
  assert.equal(state.kosdaqDelta, "-5.1%p");
});

test("평소 대비 포맷: 반올림 0은 ±0.0%p, 음수 0 표기 없음", () => {
  assert.equal(formatProbabilityDelta(0.5, 0.5), "±0.0%p");
  assert.equal(formatProbabilityDelta(0.50004, 0.5), "±0.0%p");
  assert.equal(formatProbabilityDelta(0.49996, 0.5), "±0.0%p");
  assert.equal(formatProbabilityDelta(0.3, 0.81), "-51.0%p");
});

test("평소 대비 포맷: 표시된 두 퍼센트의 차이라 칩 안에서 어긋나지 않는다", () => {
  // 62.3% - 61.6% = +0.7%p (반올림 전 차이 0.78%p로 계산하면 +0.8%p가 되어 모순)
  assert.equal(formatProbabilityDelta(0.6234, 0.6156), "+0.7%p");
  assert.equal(formatProbabilityDelta(0.6156, 0.6234), "-0.7%p");
});

test("v1 행: base rate가 null이거나 누락되면 평소 문구 없음", () => {
  for (const overrides of [
    { kospi_base_rate: null, kosdaq_base_rate: null },
    { kospi_base_rate: undefined, kosdaq_base_rate: undefined },
  ]) {
    const state = deriveMarketProbabilityChipState(row(overrides), false, TODAY);
    assert.equal(state.status, "ready");
    if (state.status !== "ready") return;
    assert.equal(state.kospiPercent, "62.3%");
    assert.equal(state.kospiBasePercent, null);
    assert.equal(state.kospiDelta, null);
    assert.equal(state.kosdaqDelta, null);
  }
});

test("RPC 가드: base rate는 누락·null·0~1 숫자만 허용", () => {
  const { kospi_base_rate: _kospi, kosdaq_base_rate: _kosdaq, ...legacy } = row();
  assert.equal(isMarketIndexProbabilityRpcRow(legacy), true);
  assert.equal(isMarketIndexProbabilityRpcRow(row({ kospi_base_rate: null })), true);
  assert.equal(isMarketIndexProbabilityRpcRow(row()), true);
  assert.equal(isMarketIndexProbabilityRpcRow({ ...row(), kospi_base_rate: 1.2 }), false);
  assert.equal(isMarketIndexProbabilityRpcRow({ ...row(), kosdaq_base_rate: "0.5" }), false);
});
