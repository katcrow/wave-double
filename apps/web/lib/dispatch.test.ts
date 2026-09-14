import assert from "node:assert/strict";
import { test } from "node:test";
import { hashDispatchPayload, validateCsrf, timingSafeEqualStrings, isValidLogicalRunKey } from "./dispatch.ts";
import { isAllowedOperator } from "./auth-allowlist.ts";

test("hashDispatchPayload: 같은 필드는 항상 같은 hash를 낸다(결정성)", () => {
  const a = hashDispatchPayload({ logical_run_key: "close:2026-09-02", trading_day: "2026-09-02", batch_kind: "close" });
  const b = hashDispatchPayload({ logical_run_key: "close:2026-09-02", trading_day: "2026-09-02", batch_kind: "close" });
  assert.equal(a, b);
  assert.match(a, /^[0-9a-f]{64}$/);
});

test("hashDispatchPayload: 필드가 다르면 다른 hash가 나온다", () => {
  const a = hashDispatchPayload({ logical_run_key: "close:2026-09-02", trading_day: "2026-09-02", batch_kind: "close" });
  const b = hashDispatchPayload({ logical_run_key: "premarket:2026-09-02", trading_day: "2026-09-02", batch_kind: "premarket" });
  assert.notEqual(a, b);
});

test("validateCsrf: 쿠키와 헤더가 일치하면 true", () => {
  assert.equal(validateCsrf("token-123", "token-123"), true);
});

test("validateCsrf: 불일치, 누락, 길이 차이는 모두 false", () => {
  assert.equal(validateCsrf("token-123", "token-456"), false);
  assert.equal(validateCsrf(null, "token-123"), false);
  assert.equal(validateCsrf("token-123", undefined), false);
  assert.equal(validateCsrf("short", "much-longer-value"), false);
});

test("timingSafeEqualStrings: 대칭 동작을 재사용할 수 있다", () => {
  assert.equal(timingSafeEqualStrings("secret", "secret"), true);
  assert.equal(timingSafeEqualStrings("secret", "other"), false);
});

test("isValidLogicalRunKey: close/premarket은 YYYY-MM-DD 날짜만 허용한다", () => {
  assert.equal(isValidLogicalRunKey("close", "close:2026-09-02"), true);
  assert.equal(isValidLogicalRunKey("premarket", "premarket:2026-09-02"), true);
  assert.equal(isValidLogicalRunKey("close", "premarket:2026-09-02"), false);
  assert.equal(isValidLogicalRunKey("close", "close:2026-9-2"), false);
  assert.equal(isValidLogicalRunKey("close", "close:2026-09-02:09:00"), false);
});

test("isValidLogicalRunKey: intraday는 20분 슬롯(HH:MM)만 허용한다", () => {
  assert.equal(isValidLogicalRunKey("intraday", "intraday:2026-09-02:09:00"), true);
  assert.equal(isValidLogicalRunKey("intraday", "intraday:2026-09-02:15:20"), true);
  assert.equal(isValidLogicalRunKey("intraday", "intraday:2026-09-02:15:40"), true);
  assert.equal(isValidLogicalRunKey("intraday", "intraday:2026-09-02:15:30"), false);
  assert.equal(isValidLogicalRunKey("intraday", "intraday:2026-09-02:09:15"), false);
  assert.equal(isValidLogicalRunKey("intraday", "intraday:2026-09-02:24:00"), false);
  assert.equal(isValidLogicalRunKey("intraday", "close:2026-09-02"), false);
});

test("isValidLogicalRunKey: 알 수 없는 batch_kind는 항상 거부된다", () => {
  assert.equal(isValidLogicalRunKey("unknown", "close:2026-09-02"), false);
});

test("allowlist 거부: OPERATOR_ALLOWLIST 밖 이메일은 거부된다", () => {
  const original = process.env.OPERATOR_ALLOWLIST;
  process.env.OPERATOR_ALLOWLIST = "neo@example.com, ops@example.com";
  try {
    assert.equal(isAllowedOperator("neo@example.com"), true);
    assert.equal(isAllowedOperator("NEO@EXAMPLE.COM"), true);
    assert.equal(isAllowedOperator("intruder@example.com"), false);
    assert.equal(isAllowedOperator(null), false);
    assert.equal(isAllowedOperator(""), false);
  } finally {
    if (original === undefined) delete process.env.OPERATOR_ALLOWLIST;
    else process.env.OPERATOR_ALLOWLIST = original;
  }
});
