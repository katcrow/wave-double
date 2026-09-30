import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildTopTradingCandidateViewModels,
  formatTradingValue,
  isTopTradingCandidateRpcRow,
} from "./top-trading-candidates.ts";
import type { TopTradingCandidateRpcRow } from "./dashboard-types.ts";

const RUN_ID = "00000000-0000-4000-8000-000000000004";
const TRADING_DAY = "2026-09-09";

function row(overrides: Partial<TopTradingCandidateRpcRow> = {}): TopTradingCandidateRpcRow {
  return {
    candidate_id: "00000000-0000-4000-8000-000000000401",
    attempt_run_id: RUN_ID,
    ticker: "005930",
    name: "삼성전자",
    trading_day: TRADING_DAY,
    trading_value: 100000000,
    ...overrides,
  };
}

test("거래대금 내림차순으로 상위 3개만 만들고 순위를 붙인다", () => {
  const result = buildTopTradingCandidateViewModels([
    row({ candidate_id: "1", ticker: "000004", trading_value: 10 }),
    row({ candidate_id: "2", ticker: "000002", trading_value: 40 }),
    row({ candidate_id: "3", ticker: "000003", trading_value: 30 }),
    row({ candidate_id: "4", ticker: "000001", trading_value: 20 }),
  ], RUN_ID, TRADING_DAY);

  assert.deepEqual(result.map(({ ticker, rank }) => ({ ticker, rank })), [
    { ticker: "000002", rank: 1 },
    { ticker: "000003", rank: 2 },
    { ticker: "000001", rank: 3 },
  ]);
});

test("거래대금 동률은 ticker 오름차순으로 결정한다", () => {
  const result = buildTopTradingCandidateViewModels([
    row({ ticker: "000003", trading_value: 20 }),
    row({ ticker: "000001", trading_value: 20 }),
    row({ ticker: "000002", trading_value: 20 }),
  ], RUN_ID, TRADING_DAY);

  assert.deepEqual(result.map(({ ticker }) => ticker), ["000001", "000002", "000003"]);
});

test("active 후보가 1~2개면 존재하는 후보만 반환하고 빈 배열은 빈 상태다", () => {
  assert.equal(buildTopTradingCandidateViewModels([row()], RUN_ID, TRADING_DAY).length, 1);
  assert.deepEqual(buildTopTradingCandidateViewModels([], RUN_ID, TRADING_DAY), []);
});

test("다른 run 또는 trading_day 행은 같은 complete snapshot에 섞지 않는다", () => {
  const result = buildTopTradingCandidateViewModels([
    row({ ticker: "000001", trading_value: 999, attempt_run_id: "other-run" }),
    row({ ticker: "000002", trading_value: 998, trading_day: "2026-09-08" }),
    row({ ticker: "000003", trading_value: 1 }),
  ], RUN_ID, TRADING_DAY);

  assert.deepEqual(result.map(({ ticker }) => ticker), ["000003"]);
});

test("거래대금은 원 단위 한국어 숫자 문자열로 표시한다", () => {
  assert.equal(formatTradingValue(123456789), "123,456,789");
  assert.equal(formatTradingValue(-1), "미확인");
  assert.equal(formatTradingValue(Number.MAX_SAFE_INTEGER + 1), "미확인");
});

test("RPC shape guard는 유한 숫자와 날짜를 강제한다", () => {
  assert.equal(isTopTradingCandidateRpcRow(row()), true);
  assert.equal(isTopTradingCandidateRpcRow({ ...row(), trading_value: "123" }), false);
  assert.equal(isTopTradingCandidateRpcRow({ ...row(), trading_value: -1 }), false);
  assert.equal(isTopTradingCandidateRpcRow({ ...row(), trading_value: Number.MAX_SAFE_INTEGER + 1 }), false);
  assert.equal(isTopTradingCandidateRpcRow({ ...row(), trading_value: Number.POSITIVE_INFINITY }), false);
  assert.equal(isTopTradingCandidateRpcRow({ ...row(), trading_day: "2026-02-30" }), false);
});

test("이름이 공백이면 ticker를 표시 이름으로 사용하고 유효한 이름은 trim한다", () => {
  const [fallback] = buildTopTradingCandidateViewModels(
    [row({ name: "   ", ticker: "005930" })],
    RUN_ID,
    TRADING_DAY,
  );
  const [trimmed] = buildTopTradingCandidateViewModels(
    [row({ name: "  삼성전자  " })],
    RUN_ID,
    TRADING_DAY,
  );

  assert.equal(fallback.name, null);
  assert.equal(fallback.displayName, "005930");
  assert.equal(trimmed.name, "삼성전자");
  assert.equal(trimmed.displayName, "삼성전자");
});
