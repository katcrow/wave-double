import assert from "node:assert/strict";
import { test } from "node:test";
import { getStrategyLabel } from "./strategy-labels.ts";

test("전략 A/B/C는 정의된 라벨을 반환한다", () => {
  assert.equal(getStrategyLabel("A"), "전략 A");
  assert.equal(getStrategyLabel("B"), "전략 B");
  assert.equal(getStrategyLabel("C"), "전략 C");
});

test("전략 D/E/F는 정의된 라벨을 반환한다", () => {
  assert.equal(getStrategyLabel("D"), "전략 D");
  assert.equal(getStrategyLabel("E"), "전략 E");
  assert.equal(getStrategyLabel("F"), "전략 F");
});

test("정의되지 않은 전략 코드는 undefined를 반환한다", () => {
  assert.equal(getStrategyLabel("G"), undefined);
});

// prototype pollution 방지: Object.prototype에 존재하는 이름은 own-property가 아니므로 undefined.
test("prototype 체인의 이름들은 undefined를 반환한다(prototype pollution 방지)", () => {
  assert.equal(getStrategyLabel("constructor"), undefined);
  assert.equal(getStrategyLabel("toString"), undefined);
  assert.equal(getStrategyLabel("hasOwnProperty"), undefined);
});
