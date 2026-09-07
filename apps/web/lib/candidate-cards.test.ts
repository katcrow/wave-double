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
    vanished_strategies: [],
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

// I/O 매트릭스: D/E 포함 조합 -- 전략 D/E가 A/B/C와 동일한 방식으로 취급된다
test("D 단독 태그: 그대로 visibleStrategies에 담기고 접힘 없음", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["D"] })]);
  assert.deepEqual(vm.visibleStrategies, ["D"]);
  assert.equal(vm.hiddenStrategyCount, 0);
});

test("E 단독 태그: 그대로 visibleStrategies에 담기고 접힘 없음", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["E"] })]);
  assert.deepEqual(vm.visibleStrategies, ["E"]);
  assert.equal(vm.hiddenStrategyCount, 0);
});

test("A∩D 조합: 두 태그 모두 표시되고 접힘 없음", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["A", "D"] })]);
  assert.deepEqual(vm.visibleStrategies, ["A", "D"]);
  assert.equal(vm.hiddenStrategyCount, 0);
});

// I/O 매트릭스: MULTI_TAG_5 -- A/B/C/D/E 5개 태그 모두 존재 시 MAX_VISIBLE_TAGS까지 표시 후 "+3" 접힘
test("5태그(A/B/C/D/E) 동시 존재: 앞 2개만 보이고 나머지 3개는 hiddenStrategyCount로 접힌다", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["A", "B", "C", "D", "E"] })]);
  assert.deepEqual(vm.visibleStrategies, ["A", "B"]);
  assert.equal(vm.hiddenStrategyCount, 3);
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

test("name이 null이면 displayName은 ticker로 대체된다", () => {
  const [vm] = buildCandidateCardViewModels([row({ name: null, ticker: "005930" })]);
  assert.equal(vm.displayName, "005930");
});

test("빈 배열 입력은 빈 배열을 반환한다", () => {
  assert.deepEqual(buildCandidateCardViewModels([]), []);
});

// I/O 매트릭스: 부분 재태깅 -- active(A) + vanished(B)가 함께 표시되고 카드는 정상 노출된다.
test("부분 재태깅: strategies와 vanishedStrategies가 함께 보존되고 isFullyVanished는 false다", () => {
  const [vm] = buildCandidateCardViewModels([
    row({ strategies: ["A"], vanished_strategies: ["B"] }),
  ]);
  assert.deepEqual(vm.visibleStrategies, ["A"]);
  assert.deepEqual(vm.vanishedStrategies, ["B"]);
  assert.equal(vm.isFullyVanished, false);
});

// I/O 매트릭스: 완전 소멸 -- active 태그 0건 + vanished 태그 존재 -- isFullyVanished=true, 카드는 유지.
test("완전 소멸: active 태그가 없고 vanished만 있으면 isFullyVanished=true", () => {
  const [vm] = buildCandidateCardViewModels([
    row({ strategies: [], vanished_strategies: ["A", "C"] }),
  ]);
  assert.deepEqual(vm.visibleStrategies, []);
  assert.deepEqual(vm.vanishedStrategies, ["A", "C"]);
  assert.equal(vm.isFullyVanished, true);
});

test("vanished 태그가 없으면 isFullyVanished는 false다(정상 케이스)", () => {
  const [vm] = buildCandidateCardViewModels([row({ strategies: ["A"], vanished_strategies: [] })]);
  assert.equal(vm.isFullyVanished, false);
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
