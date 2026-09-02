import assert from "node:assert/strict";
import { test } from "node:test";
import { buildCandidateCardViewModels, MAX_VISIBLE_TAGS } from "./candidate-cards.ts";
import type { TodayCandidateCardRow } from "./dashboard-types.ts";

function row(overrides: Partial<TodayCandidateCardRow> = {}): TodayCandidateCardRow {
  return {
    candidate_id: "11111111-1111-1111-1111-111111111111",
    ticker: "005930",
    name: "삼성전자",
    strategies: ["A"],
    supply_partial_missing: false,
    ...overrides,
  };
}

// I/O 매트릭스: 태깅 후보 존재 -- 종목명/코드/전략 태그 그대로 전달
test("단일 태그: 태그가 그대로 visibleStrategies에 담기고 접힘 없음", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["B"] })]);
  assert.equal(vm.candidateId, "11111111-1111-1111-1111-111111111111");
  assert.equal(vm.ticker, "005930");
  assert.equal(vm.name, "삼성전자");
  assert.deepEqual(vm.visibleStrategies, ["B"]);
  assert.equal(vm.hiddenStrategyCount, 0);
});

// I/O 매트릭스: 다중 태그 -- 태그 2개 표시 + +1
// SQL(`array_agg(distinct t.strategy order by t.strategy)`)이 이미 정렬해 반환하므로
// 픽스처도 정렬된 입력으로 시딩한다(클라이언트 재정렬 없음, SQL이 단일 정렬 출처).
test("3태그: 앞 2개만 보이고 나머지는 hiddenStrategyCount로 접힌다", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["A", "B", "C"] })]);
  assert.equal(MAX_VISIBLE_TAGS, 2);
  assert.deepEqual(vm.visibleStrategies, ["A", "B"]);
  assert.equal(vm.hiddenStrategyCount, 1);
});

test("2태그: 임계값과 정확히 같으면 접히지 않는다", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["A", "C"] })]);
  assert.deepEqual(vm.visibleStrategies, ["A", "C"]);
  assert.equal(vm.hiddenStrategyCount, 0);
});

// I/O 매트릭스: 부분결측 -- D0 행 존재, investor_net_status pending/missing
test("부분결측: supply_partial_missing=true가 그대로 전달된다", () => {
  const [vm] = buildCandidateCardViewModels([row({ supply_partial_missing: true })]);
  assert.equal(vm.supplyPartialMissing, true);
});

// I/O 매트릭스: D0 데이터 없음 -- 부분결측 배지 없음
test("D0 데이터 없음: supply_partial_missing=false가 그대로 전달된다", () => {
  const [vm] = buildCandidateCardViewModels([row({ supply_partial_missing: false })]);
  assert.equal(vm.supplyPartialMissing, false);
});

test("name이 null이어도 그대로 보존한다(렌더 단계에서 ticker로 대체)", () => {
  const [vm] = buildCandidateCardViewModels([row({ name: null })]);
  assert.equal(vm.name, null);
});

test("빈 배열 입력은 빈 배열을 반환한다", () => {
  assert.deepEqual(buildCandidateCardViewModels([]), []);
});

test("여러 후보를 순서대로 각각 변환한다", () => {
  const vms = buildCandidateCardViewModels([
    row({ candidate_id: "1", ticker: "000001", strategies: ["A"] }),
    row({ candidate_id: "2", ticker: "000002", strategies: ["A", "B", "C"] }), // 이미 정렬된 입력
  ]);
  assert.equal(vms.length, 2);
  assert.equal(vms[0].candidateId, "1");
  assert.equal(vms[1].hiddenStrategyCount, 1);
});
