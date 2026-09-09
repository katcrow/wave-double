import assert from "node:assert/strict";
import test from "node:test";

import type { BatchKind, CandidateSupplyHintRpcRow, SupplyHintStatus } from "./dashboard-types.ts";
import { isCandidateSupplyHintRpcRow } from "./supply-hints.ts";

const validRow: CandidateSupplyHintRpcRow = {
  candidate_id: "candidate-1",
  attempt_run_id: "attempt-1",
  ticker: "005930",
  trading_day: "2099-08-01",
  slot: "D0",
  batch_kind: "close",
  foreign_net: null,
  institution_net: null,
  individual_net: null,
  program_net: null,
  investor_net_status: "missing",
  collected_at: null,
  hint_status: "undetermined",
};

test("accepts the missing-row RPC contract and narrows literals", () => {
  const value: unknown = validRow;
  assert.equal(isCandidateSupplyHintRpcRow(value), true);

  if (isCandidateSupplyHintRpcRow(value)) {
    const status: SupplyHintStatus = value.hint_status;
    const batchKind: BatchKind = value.batch_kind;
    assert.equal(status, "undetermined");
    assert.equal(batchKind, "close");
    assert.equal(value.slot, "D0");
  }
});

test("accepts a complete good row with nullable field types", () => {
  assert.equal(isCandidateSupplyHintRpcRow({
    ...validRow,
    foreign_net: 101,
    institution_net: 202,
    individual_net: -303,
    program_net: 404,
    investor_net_status: "confirmed",
    collected_at: "2099-08-01T03:00:00.000Z",
    hint_status: "good",
}), true);
});

test("accepts a confirmed row whose SQL hint status is not_met", () => {
  assert.equal(isCandidateSupplyHintRpcRow({
    ...validRow,
    foreign_net: 0,
    institution_net: 0,
    individual_net: 0,
    program_net: 0,
    investor_net_status: "confirmed",
    collected_at: "2099-08-01T03:00:00.000Z",
    hint_status: "not_met",
  }), true);
});

test("rejects invalid slot, literals, dates, and non-finite numbers", () => {
  assert.equal(isCandidateSupplyHintRpcRow({ ...validRow, slot: "D-1" }), false);
  assert.equal(isCandidateSupplyHintRpcRow({ ...validRow, batch_kind: "unknown" }), false);
  assert.equal(isCandidateSupplyHintRpcRow({ ...validRow, trading_day: "2099-02-29" }), false);
  assert.equal(isCandidateSupplyHintRpcRow({ ...validRow, foreign_net: Number.NaN }), false);
  assert.equal(isCandidateSupplyHintRpcRow({ ...validRow, collected_at: "not-a-date" }), false);
});
