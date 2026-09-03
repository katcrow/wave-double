import assert from "node:assert/strict";
import { test } from "node:test";
import {
  buildDisappearedCandidateViewModels,
  DISAPPEARED_REASON_LABEL,
} from "./disappeared-candidates.ts";
import type { DisappearedCandidateRow } from "./dashboard-types.ts";

function row(overrides: Partial<DisappearedCandidateRow> = {}): DisappearedCandidateRow {
  return {
    ticker: "005930",
    name: "삼성전자",
    reason: "population_dropout",
    strategies: ["A"],
    ...overrides,
  };
}

// I/O 매트릭스: 모집단 이탈 -- "모집단 이탈" 문구로 매핑된다.
test("population_dropout은 '모집단 이탈' 문구로 매핑된다", () => {
  const [vm] = buildDisappearedCandidateViewModels([row({ reason: "population_dropout" })]);
  assert.equal(vm.reason, "population_dropout");
  assert.equal(vm.reasonLabel, "모집단 이탈");
});

// I/O 매트릭스: 수집 실패 -- "수집 실패" 문구로 매핑되어 이탈과 구분된다.
test("collection_failure는 '수집 실패' 문구로 매핑된다", () => {
  const [vm] = buildDisappearedCandidateViewModels([row({ reason: "collection_failure" })]);
  assert.equal(vm.reason, "collection_failure");
  assert.equal(vm.reasonLabel, "수집 실패");
  assert.notEqual(vm.reasonLabel, DISAPPEARED_REASON_LABEL.population_dropout);
});

test("name이 null이면 displayName은 ticker로 대체된다", () => {
  const [vm] = buildDisappearedCandidateViewModels([row({ name: null, ticker: "000660" })]);
  assert.equal(vm.displayName, "000660");
});

test("strategies는 재정렬 없이 그대로 전달된다", () => {
  const [vm] = buildDisappearedCandidateViewModels([row({ strategies: ["A", "C"] })]);
  assert.deepEqual(vm.strategies, ["A", "C"]);
});

test("빈 배열 입력은 빈 배열을 반환한다", () => {
  assert.deepEqual(buildDisappearedCandidateViewModels([]), []);
});

test("여러 행을 순서대로 각각 변환한다", () => {
  const vms = buildDisappearedCandidateViewModels([
    row({ ticker: "000001", reason: "population_dropout" }),
    row({ ticker: "000002", reason: "collection_failure" }),
  ]);
  assert.equal(vms.length, 2);
  assert.equal(vms[0].ticker, "000001");
  assert.equal(vms[1].reasonLabel, "수집 실패");
});
