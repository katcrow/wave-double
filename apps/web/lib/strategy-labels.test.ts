import assert from "node:assert/strict";
import { test } from "node:test";
import { getStrategyLabel } from "./strategy-labels.ts";

test("전략 A/B/C는 정의된 라벨을 반환한다", () => {
  assert.equal(getStrategyLabel("A"), "전략 A · OBV 합집합");
  assert.equal(getStrategyLabel("B"), "전략 B · 쌍바닥+주봉K");
  assert.equal(getStrategyLabel("C"), "전략 C · 3바닥 다이버전스");
});

test("전략 D/E/F는 정의된 라벨을 반환한다", () => {
  assert.equal(getStrategyLabel("D"), "전략 D · 돌파3%");
  assert.equal(getStrategyLabel("E"), "전략 E · SMA GC+OBV+ADX");
  assert.equal(getStrategyLabel("F"), "전략 F · 각도가속 쌍바닥");
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
