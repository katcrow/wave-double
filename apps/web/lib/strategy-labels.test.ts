import assert from "node:assert/strict";
import { test } from "node:test";
import { getStrategyLabel } from "./strategy-labels.ts";

test("전략 A/B/C는 정의된 라벨을 반환한다", () => {
  assert.equal(getStrategyLabel("A"), "전략 A");
  assert.equal(getStrategyLabel("B"), "전략 B");
  assert.equal(getStrategyLabel("C"), "전략 C");
});

// prototype pollution 방지: Object.prototype에 존재하는 이름은 own-property가 아니므로 undefined.
test("prototype 체인의 이름들은 undefined를 반환한다(prototype pollution 방지)", () => {
  assert.equal(getStrategyLabel("constructor"), undefined);
  assert.equal(getStrategyLabel("toString"), undefined);
  assert.equal(getStrategyLabel("hasOwnProperty"), undefined);
});
