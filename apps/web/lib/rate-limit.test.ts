import assert from "node:assert/strict";
import { test } from "node:test";
import { RateLimiter } from "./rate-limit.ts";

test("한도 이내: limit만큼은 허용된다", () => {
  const limiter = new RateLimiter(3, 60_000);
  const now = 1_000_000;
  assert.equal(limiter.check("neo", now).allowed, true);
  assert.equal(limiter.check("neo", now + 1).allowed, true);
  const third = limiter.check("neo", now + 2);
  assert.equal(third.allowed, true);
  assert.equal(third.remaining, 0);
});

test("한도 초과: limit+1번째 요청은 거부되고 retryAfterMs를 반환한다", () => {
  const limiter = new RateLimiter(2, 60_000);
  const now = 1_000_000;
  limiter.check("neo", now);
  limiter.check("neo", now + 100);
  const blocked = limiter.check("neo", now + 200);
  assert.equal(blocked.allowed, false);
  assert.ok(blocked.retryAfterMs > 0);
});

test("윈도우 만료: 윈도우가 지나면 다시 허용된다", () => {
  const limiter = new RateLimiter(1, 1_000);
  const now = 1_000_000;
  assert.equal(limiter.check("neo", now).allowed, true);
  assert.equal(limiter.check("neo", now + 500).allowed, false);
  assert.equal(limiter.check("neo", now + 1_001).allowed, true);
});

test("사용자별로 독립된 카운터를 유지한다", () => {
  const limiter = new RateLimiter(1, 60_000);
  const now = 1_000_000;
  assert.equal(limiter.check("neo", now).allowed, true);
  assert.equal(limiter.check("other", now).allowed, true);
  assert.equal(limiter.check("neo", now + 1).allowed, false);
});
