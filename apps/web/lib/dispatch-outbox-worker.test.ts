import assert from "node:assert/strict";
import { test } from "node:test";
import {
  decideOutboxAction,
  shouldDeadLetterAfterDispatchFailure,
  MAX_DISPATCH_ATTEMPTS,
  MAX_RECEIPT_ATTEMPTS,
  DEFAULT_WORKFLOW_REF,
  resolveWorkflowRef,
} from "./dispatch-outbox-worker.ts";

test("queued 상태, attempts가 상한 이내면 dispatch를 시도한다", () => {
  const decision = decideOutboxAction({ status: "queued", attempts: 1 });
  assert.deepEqual(decision, { action: "dispatch" });
});

test("queued 상태, attempts가 dispatch 상한을 넘으면 즉시 dead_letter다", () => {
  const decision = decideOutboxAction({ status: "queued", attempts: MAX_DISPATCH_ATTEMPTS + 1 });
  assert.deepEqual(decision, { action: "dead_letter", reasonCode: "ATTEMPTS_EXHAUSTED" });
});

test("queued 상태, attempts가 dispatch 상한과 같으면 아직 재시도한다(상한 초과만 dead_letter)", () => {
  const decision = decideOutboxAction({ status: "queued", attempts: MAX_DISPATCH_ATTEMPTS });
  assert.deepEqual(decision, { action: "dispatch" });
});

test("accepted 상태, attempts가 receipt 상한 이내면 receipt를 기다린다", () => {
  const decision = decideOutboxAction({ status: "accepted", attempts: MAX_DISPATCH_ATTEMPTS + 1 });
  assert.deepEqual(decision, { action: "await_receipt" });
});

test("accepted 상태, attempts가 receipt 상한을 넘으면 RECEIPT_TIMEOUT dead_letter다", () => {
  const decision = decideOutboxAction({ status: "accepted", attempts: MAX_RECEIPT_ATTEMPTS + 1 });
  assert.deepEqual(decision, { action: "dead_letter", reasonCode: "RECEIPT_TIMEOUT" });
});

test("accepted 단계의 예산은 queued 단계보다 훨씬 크다(콜드스타트 오탐 방지)", () => {
  assert.ok(MAX_RECEIPT_ATTEMPTS > MAX_DISPATCH_ATTEMPTS);
});

test("started 등 다른 상태는 noop이다", () => {
  const decision = decideOutboxAction({ status: "started", attempts: 0 });
  assert.deepEqual(decision, { action: "noop" });
});

test("shouldDeadLetterAfterDispatchFailure: 상한 미만이면 재시도", () => {
  assert.equal(shouldDeadLetterAfterDispatchFailure(MAX_DISPATCH_ATTEMPTS - 1), false);
});

test("shouldDeadLetterAfterDispatchFailure: 상한 이상이면 dead_letter", () => {
  assert.equal(shouldDeadLetterAfterDispatchFailure(MAX_DISPATCH_ATTEMPTS), true);
});

test("resolveWorkflowRef: 기본 ref는 이 저장소의 default branch인 master다", () => {
  assert.equal(DEFAULT_WORKFLOW_REF, "master");
  assert.equal(resolveWorkflowRef(undefined), "master");
});

test("resolveWorkflowRef: 존재하지 않는 ref로 dispatch가 422로 죽지 않도록 main을 기본값으로 쓰지 않는다", () => {
  assert.notEqual(DEFAULT_WORKFLOW_REF, "main");
});

test("resolveWorkflowRef: 환경변수가 있으면 그 ref를 쓴다", () => {
  assert.equal(resolveWorkflowRef("release/2026-09"), "release/2026-09");
});

test("resolveWorkflowRef: 빈 문자열/공백만 있는 환경변수는 기본값으로 되돌린다", () => {
  assert.equal(resolveWorkflowRef(""), DEFAULT_WORKFLOW_REF);
  assert.equal(resolveWorkflowRef("   "), DEFAULT_WORKFLOW_REF);
});

test("resolveWorkflowRef: 주변 공백을 제거한다", () => {
  assert.equal(resolveWorkflowRef("  master  "), "master");
});
