import assert from "node:assert/strict";
import test from "node:test";

import { buildCandidateCardViewModels } from "./candidate-cards.ts";
import {
  buildCandidateFilterItems,
  filterCandidateItems,
  getDefaultCandidateFilterState,
  hasActiveCandidateFilters,
  HINT_STATUS_LABEL,
  summarizeCandidateFilters,
} from "./candidate-filters.ts";
import type {
  CandidateEvidenceRawRow,
  CandidateEvidenceRpcRow,
  CandidateSupplyHintRpcRow,
  TodayCandidateCardRow,
} from "./dashboard-types.ts";

const candidateRows: TodayCandidateCardRow[] = [
  {
    candidate_id: "candidate-good",
    ticker: "000001",
    name: "좋은 후보",
    strategies: ["A"],
    vanished_strategies: [],
    supply_partial_missing: false,
  },
  {
    candidate_id: "candidate-missing",
    ticker: "000002",
    name: "결측 후보",
    strategies: ["B"],
    vanished_strategies: ["C"],
    supply_partial_missing: false,
  },
  {
    candidate_id: "candidate-partial",
    ticker: "000003",
    name: "부분결측 후보",
    strategies: [],
    vanished_strategies: ["D"],
    supply_partial_missing: true,
  },
];

const evidenceRows: CandidateEvidenceRpcRow[] = [
  { candidate_id: "candidate-good", sources: ["t1859"], rows: [] },
  { candidate_id: "candidate-missing", sources: ["t1852"], rows: [] },
  { candidate_id: "candidate-partial", sources: ["t1856"], rows: [] },
];

function hint(candidate_id: string, hint_status: CandidateSupplyHintRpcRow["hint_status"], investor_net_status: CandidateSupplyHintRpcRow["investor_net_status"]): CandidateSupplyHintRpcRow {
  return {
    candidate_id,
    attempt_run_id: "attempt-1",
    ticker: "000001",
    trading_day: "2099-08-01",
    slot: "D0",
    batch_kind: "close",
    foreign_net: investor_net_status === "confirmed" ? 1 : null,
    institution_net: investor_net_status === "confirmed" ? 1 : null,
    individual_net: investor_net_status === "confirmed" ? 1 : null,
    program_net: investor_net_status === "confirmed" ? 1 : null,
    investor_net_status,
    collected_at: investor_net_status === "confirmed" ? "2099-08-01T03:00:00.000Z" : null,
    hint_status,
  };
}

function evidenceDay(trading_day: string, collected_at: string): CandidateEvidenceRawRow {
  return {
    trading_day,
    slot: "D0",
    close: 1,
    volume: 1,
    change_pct: 1,
    foreign_net: 1,
    institution_net: 1,
    individual_net: 1,
    program_net: 1,
    investor_net_status: "confirmed",
    collected_at,
  };
}

const items = buildCandidateFilterItems(
  buildCandidateCardViewModels(candidateRows),
  evidenceRows,
  [
    hint("candidate-good", "good", "confirmed"),
    hint("candidate-missing", "undetermined", "missing"),
  ],
  false,
);

test("good/not_met/undetermined 힌트 상태는 확정된 카드 라벨로 매핑된다", () => {
  assert.deepEqual(
    (["good", "not_met", "undetermined"] as const).map((status) => HINT_STATUS_LABEL[status]),
    ["좋은 수급", "미충족", "판정 불가 · 장 마감 후 확정"],
  );
});

test("힌트 행이 없으면 판정 불가이며 active/vanished 배열은 필터 메타로 보존된다", () => {
  const partial = items.find((item) => item.candidate.candidateId === "candidate-partial");
  assert.ok(partial);
  assert.equal(partial.hintStatus, "undetermined");
  assert.equal(partial.supplyMissing, true);
  assert.deepEqual(partial.candidate.vanishedStrategies, ["D"]);
  assert.equal(partial.candidate.signalStatus, "vanished");
});

test("힌트 RPC가 성공해도 후보의 hint row가 없으면 수급 결측으로 제외된다", () => {
  const noHintItems = buildCandidateFilterItems(
    buildCandidateCardViewModels([candidateRows[0]]),
    [evidenceRows[0]],
    [],
    false,
  );
  assert.equal(noHintItems[0].hintStatus, "undetermined");
  assert.equal(noHintItems[0].supplyMissing, true);
  const filters = getDefaultCandidateFilterState();
  filters.missingSupply = "exclude";
  assert.deepEqual(filterCandidateItems(noHintItems, filters), []);
});

test("전략·힌트·시그널·원천을 그룹 내 OR, 그룹 간 AND로 조합한다", () => {
  const filters = getDefaultCandidateFilterState();
  filters.strategies = ["A", "C"];
  filters.hintStatuses = ["good"];
  filters.signalStatuses = ["active"];
  filters.sources = ["t1859"];
  const matched = filterCandidateItems(items, filters);
  assert.deepEqual(matched.map((item) => item.candidate.candidateId), ["candidate-good"]);
});

test("vanished 전략도 전략 필터에서 선택할 수 있고 결측 제외는 pending/missing과 카드 결측을 제외한다", () => {
  const strategyFilter = getDefaultCandidateFilterState();
  strategyFilter.signalStatuses = [];
  strategyFilter.strategies = ["C"];
  assert.deepEqual(
    filterCandidateItems(items, strategyFilter).map((item) => item.candidate.candidateId),
    ["candidate-missing"],
  );

  strategyFilter.strategies = [];
  strategyFilter.missingSupply = "exclude";
  assert.deepEqual(
    filterCandidateItems(items, strategyFilter).map((item) => item.candidate.candidateId),
    ["candidate-good"],
  );
});

test("vanished와 mixed 시그널 상태를 각각 필터링한다", () => {
  const filters = getDefaultCandidateFilterState();
  filters.signalStatuses = ["vanished"];
  assert.deepEqual(
    filterCandidateItems(items, filters).map((item) => item.candidate.candidateId),
    ["candidate-partial"],
  );
  filters.signalStatuses = ["mixed"];
  assert.deepEqual(
    filterCandidateItems(items, filters).map((item) => item.candidate.candidateId),
    ["candidate-missing"],
  );
});

test("기본 필터는 시그널 상태를 활성으로 고정해 소멸·혼합 후보를 숨긴다", () => {
  const filters = getDefaultCandidateFilterState();
  assert.deepEqual(filters.signalStatuses, ["active"]);
  assert.deepEqual(
    filterCandidateItems(items, filters).map((item) => item.candidate.candidateId),
    ["candidate-good"],
  );
  assert.equal(hasActiveCandidateFilters(filters), false);
});

test("원천을 여러 개 선택하면 후보의 sources 중 하나와 일치하는 후보를 남긴다", () => {
  const multiSourceItems = buildCandidateFilterItems(
    buildCandidateCardViewModels([candidateRows[0]]),
    [{ candidate_id: "candidate-good", sources: ["t1859", "t1852"], rows: [] }],
    [hint("candidate-good", "good", "confirmed")],
    false,
  );
  const filters = getDefaultCandidateFilterState();
  filters.sources = ["t1852"];
  assert.deepEqual(filterCandidateItems(multiSourceItems, filters).map((item) => item.candidate.candidateId), ["candidate-good"]);
});

test("중복 evidence/hint 행은 배열 순서와 무관하게 trading_day와 collected_at이 최신인 행을 선택한다", () => {
  const evidenceDuplicates: CandidateEvidenceRpcRow[] = [
    { candidate_id: "candidate-good", sources: ["t1856"], rows: [evidenceDay("2099-07-31", "2099-07-31T03:00:00.000Z")] },
    { candidate_id: "candidate-good", sources: ["t1852"], rows: [evidenceDay("2099-08-01", "2099-08-01T03:00:00.000Z")] },
    { candidate_id: "candidate-good", sources: ["t1859"], rows: [evidenceDay("2099-08-01", "2099-08-01T04:00:00.000Z")] },
  ];
  const hintDuplicates: CandidateSupplyHintRpcRow[] = [
    { ...hint("candidate-good", "good", "confirmed"), trading_day: "2099-07-31", collected_at: "2099-07-31T03:00:00.000Z" },
    { ...hint("candidate-good", "not_met", "confirmed"), trading_day: "2099-08-01", collected_at: "2099-08-01T03:00:00.000Z" },
    { ...hint("candidate-good", "undetermined", "missing"), trading_day: "2099-08-01", collected_at: "2099-08-01T04:00:00.000Z" },
  ];
  const forward = buildCandidateFilterItems(
    buildCandidateCardViewModels([candidateRows[0]]),
    evidenceDuplicates,
    hintDuplicates,
    false,
  )[0];
  const reverse = buildCandidateFilterItems(
    buildCandidateCardViewModels([candidateRows[0]]),
    [...evidenceDuplicates].reverse(),
    [...hintDuplicates].reverse(),
    false,
  )[0];
  assert.deepEqual(forward.sources, ["t1859"]);
  assert.equal(forward.hintStatus, "undetermined");
  assert.equal(forward.supplyMissing, true);
  assert.deepEqual(reverse.sources, forward.sources);
  assert.equal(reverse.hintStatus, forward.hintStatus);
  assert.equal(reverse.supplyMissing, forward.supplyMissing);
});

test("힌트 RPC 실패는 판정 불가로 표시하되 결측 제외를 강제하지 않는다", () => {
  const failedItems = buildCandidateFilterItems(buildCandidateCardViewModels(candidateRows), evidenceRows, [], true);
  const filters = getDefaultCandidateFilterState();
  filters.signalStatuses = [];
  filters.missingSupply = "exclude";
  assert.deepEqual(
    filterCandidateItems(failedItems, filters).map((item) => item.candidate.candidateId),
    ["candidate-good", "candidate-missing"],
  );
  assert.ok(failedItems.every((item) => item.hintStatus === "undetermined"));
});

test("필터 결과 0건이면 현재 필터를 요약하고 초기화 가능한 상태를 판정한다", () => {
  const filters = getDefaultCandidateFilterState();
  filters.hintStatuses = ["not_met"];
  const matched = filterCandidateItems(items, filters);
  assert.equal(matched.length, 0);
  assert.equal(hasActiveCandidateFilters(filters), true);
  assert.deepEqual(summarizeCandidateFilters(filters), ["수급 힌트: 미충족"]);
  assert.equal(hasActiveCandidateFilters(getDefaultCandidateFilterState()), false);
});
