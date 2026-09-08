import assert from "node:assert/strict";
import { test } from "node:test";
import {
  formatEvidenceDateTime,
  formatEvidenceNumber,
  formatEvidenceSummary,
  formatEvidenceValue,
  isCandidateEvidenceRpcRow,
  normalizeCandidateEvidence,
} from "./candidate-evidence.ts";
import type { CandidateEvidenceRpcRow } from "./dashboard-types.ts";

const candidateId = "11111111-1111-1111-1111-111111111111";

function row(overrides: Partial<CandidateEvidenceRpcRow["rows"][number]> = {}) {
  return {
    trading_day: "2099-06-01",
    slot: "D0" as const,
    close: 70000,
    volume: 1200000,
    change_pct: 1.25,
    foreign_net: 0,
    institution_net: -200,
    individual_net: 200,
    program_net: 0,
    investor_net_status: "confirmed" as const,
    collected_at: "2099-06-01T03:00:00.000Z",
    ...overrides,
  };
}

function evidence(overrides: Partial<CandidateEvidenceRpcRow> = {}): CandidateEvidenceRpcRow {
  return {
    candidate_id: candidateId,
    sources: ["t1859"],
    rows: [
      row(),
      row({ slot: "D-1", trading_day: "2099-05-29" }),
      row({ slot: "D-2", trading_day: "2099-05-28" }),
    ],
    ...overrides,
  };
}

test("confirmed 0은 숫자 0으로 표시한다", () => {
  assert.equal(formatEvidenceValue(0, "confirmed"), "0");
});

test("pending과 missing은 숫자 0과 구분되는 상태 문구로 표시한다", () => {
  assert.equal(formatEvidenceValue(null, "pending"), "미확정");
  assert.equal(formatEvidenceValue(null, "missing"), "미수집");
  assert.equal(formatEvidenceValue(0, "missing"), "미수집");
});

test("pending/missing 슬롯은 하나의 부분결측 요약으로 함께 표시한다", () => {
  assert.equal(formatEvidenceSummary(["D-2"], ["D-1"]), "부분결측 · 미수집 1행(D-2) · 미확정 1행(D-1)");
  assert.equal(formatEvidenceSummary([], ["D0"]), "부분결측 · 미확정 1행(D0)");
  assert.equal(formatEvidenceSummary([], []), "");
});

test("근거를 D0/D-1/D-2 세 슬롯으로 정규화하고 없는 슬롯을 missing으로 채운다", () => {
  const model = normalizeCandidateEvidence(evidence({ rows: [row({ slot: "D-1" })] }));
  assert.deepEqual(model.slots.map((slot) => [slot.slot, slot.status]), [
    ["D0", "missing"],
    ["D-1", "confirmed"],
    ["D-2", "missing"],
  ]);
  assert.equal(model.missingSlotCount, 2);
  assert.deepEqual(model.missingSlots, ["D0", "D-2"]);
  assert.equal(model.hasRows, true);
});

test("pending 행은 대기 상태로 남고 source fallback은 기본으로 표시한다", () => {
  const model = normalizeCandidateEvidence(
    evidence({ sources: [], rows: [row({ investor_net_status: "pending", foreign_net: null })] })
  );
  assert.equal(model.sourceLabel, "기본");
  assert.equal(model.slots[0].status, "pending");
  assert.equal(model.pendingSlotCount, 1);
});

test("같은 슬롯이 중복되면 최신 거래일/수집 시각 행을 선택한다", () => {
  const model = normalizeCandidateEvidence(
    evidence({
      rows: [
        row({ trading_day: "2099-06-01", close: 70000 }),
        row({ trading_day: "2099-06-02", close: 71000 }),
      ],
    })
  );
  assert.equal(model.slots[0].row?.close, 71000);
});

test("행이 없으면 정상 데이터로 위장하지 않고 빈 상태로 표시한다", () => {
  const model = normalizeCandidateEvidence(undefined);
  assert.equal(model.hasRows, false);
  assert.equal(model.sourceLabel, "기본");
  assert.equal(model.collectedAt, null);
  assert.equal(formatEvidenceNumber(null), "미수집");
  assert.equal(formatEvidenceDateTime(null), "시각 미상");
});

test("지원되지 않는 슬롯만 있으면 근거 행이 없는 것으로 처리한다", () => {
  const model = normalizeCandidateEvidence(evidence({ rows: [{ ...row(), slot: "D3" as never }] }));
  assert.equal(model.hasRows, false);
  assert.equal(model.missingSlotCount, 3);
});

test("RPC 응답 shape가 깨지면 렌더 전에 거부한다", () => {
  assert.equal(isCandidateEvidenceRpcRow(evidence()), true);
  assert.equal(isCandidateEvidenceRpcRow({ ...evidence(), rows: null }), false);
  assert.equal(isCandidateEvidenceRpcRow({ ...evidence(), rows: [{ ...row(), close: "70000" }] }), false);
});
