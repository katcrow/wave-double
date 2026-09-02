import assert from "node:assert/strict";
import { test } from "node:test";
import { deriveTrustBarState } from "./trust-bar.ts";
import type { CompleteSnapshot, DashboardSnapshot, LatestAttempt } from "./dashboard-types.ts";

const NOW = Date.now();
const RECENT_ISO = new Date(NOW - 10 * 60 * 1000).toISOString(); // 10분 전
const STALE_ISO = new Date(NOW - 90 * 60 * 1000).toISOString(); // 90분 전

function snapshot(overrides: Partial<DashboardSnapshot>): DashboardSnapshot {
  return {
    no_snapshot: true,
    result_code: "NO_SNAPSHOT",
    complete_snapshot: null,
    latest_attempt: null,
    latest_partial_run_id: null,
    available_partial_sections: [],
    missing_sections: ["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"],
    unprocessed_items: 0,
    ...overrides,
  };
}

function complete(overrides: Partial<CompleteSnapshot> = {}): CompleteSnapshot {
  return {
    logical_run_key: "2026-09-02:close",
    run_id: "11111111-1111-1111-1111-111111111111",
    trading_day: "2026-09-02",
    batch_kind: "close",
    published_at: RECENT_ISO,
    sections: { candidates: { candidate_count: 12, truncated_count: 0, original_count: 12, excluded_count: 0 } },
    ...overrides,
  };
}

function attempt(overrides: Partial<LatestAttempt> = {}): LatestAttempt {
  return {
    run_id: "22222222-2222-2222-2222-222222222222",
    logical_run_key: "2026-09-02:close",
    trading_day: "2026-09-02",
    batch_kind: "close",
    status: "published",
    trigger: "schedule",
    started_at: RECENT_ISO,
    finished_at: RECENT_ISO,
    stage_status: { candidates: "success", tags: "pending", supply_3day: "pending", market_supply: "pending", outcome_tracking: "pending" },
    unprocessed_count: 0,
    truncated_count: 0,
    original_count: 12,
    excluded_count: 0,
    ...overrides,
  };
}

// I/O 매트릭스 행 1: 스냅샷 없음
test("no_snapshot: 상태 없음, stale 아님", () => {
  const state = deriveTrustBarState(snapshot({}));
  assert.equal(state.statusLine, "상태 없음");
  assert.equal(state.stale, false);
  assert.equal(state.candidateCount, undefined);
});

// I/O 매트릭스 행 2: 정상 발행
test("정상 발행: 배치 종류 라벨 + 시각 + 참고 후보 건수", () => {
  const state = deriveTrustBarState(
    snapshot({ no_snapshot: false, result_code: "OK", complete_snapshot: complete(), latest_attempt: attempt() })
  );
  assert.match(state.statusLine, /^종가 확정 · \d{2}:\d{2} KST$/);
  assert.equal(state.stale, false);
  assert.equal(state.candidateCount, 12);
});

// I/O 매트릭스 행 3: 실패 (이전 성공 있음)
test("실패 + 이전 성공 있음: 마지막 성공 시각 포함", () => {
  const state = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete(),
      latest_attempt: attempt({ status: "failed", finished_at: RECENT_ISO }),
    })
  );
  assert.match(state.statusLine, /^배치 실패 · 마지막 성공 /);
});

// 실패 + 이전 성공 없음(첫 배치부터 실패)
test("실패 + 이전 성공 없음: 전용 문구", () => {
  const state = deriveTrustBarState(
    snapshot({ latest_attempt: attempt({ status: "failed", finished_at: RECENT_ISO }) })
  );
  assert.equal(state.statusLine, "배치 실패 · 이전 성공 없음");
});

// I/O 매트릭스 행 4: 부분성공
test("부분성공: 미처리 건수 포함", () => {
  const state = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete(),
      latest_attempt: attempt({ status: "partial", unprocessed_count: 7, finished_at: RECENT_ISO }),
    })
  );
  assert.equal(state.statusLine, "부분성공 · 미처리 7건");
});

// I/O 매트릭스 행 5: 휴장일 스킵
test("휴장일 스킵: 실패로 표시하지 않는다", () => {
  const state = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete(),
      latest_attempt: attempt({ status: "skipped", finished_at: RECENT_ISO }),
    })
  );
  assert.equal(state.statusLine, "휴장일 · 배치 스킵");
});

// I/O 매트릭스 행 6: stale (60분 이상 경과)
test("stale: 60분 이상 경과 시 오래됨 문구 병기", () => {
  const state = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete({ published_at: STALE_ISO }),
      latest_attempt: attempt({ finished_at: STALE_ISO }),
    })
  );
  assert.equal(state.stale, true);
  assert.match(state.statusLine, /데이터가 60분 이상 오래됨/);
});

test("stale 아님: 60분 미만 경과", () => {
  const state = deriveTrustBarState(
    snapshot({ no_snapshot: false, result_code: "OK", complete_snapshot: complete(), latest_attempt: attempt() })
  );
  assert.equal(state.stale, false);
  assert.doesNotMatch(state.statusLine, /오래됨/);
});

// epics.md AC: "KST 실행 시각·트리거 유형·신선도"의 트리거 유형
test("트리거 유형: schedule/manual 라벨링, latest_attempt 없으면 undefined", () => {
  const scheduled = deriveTrustBarState(
    snapshot({ no_snapshot: false, result_code: "OK", complete_snapshot: complete(), latest_attempt: attempt({ trigger: "schedule" }) })
  );
  assert.equal(scheduled.triggerLabel, "자동");

  const manual = deriveTrustBarState(
    snapshot({ no_snapshot: false, result_code: "OK", complete_snapshot: complete(), latest_attempt: attempt({ trigger: "manual" }) })
  );
  assert.equal(manual.triggerLabel, "수동");

  const none = deriveTrustBarState(snapshot({}));
  assert.equal(none.triggerLabel, undefined);
});

// epics.md AC: 자동 배치 실패/부분성공/stale은 비차단 notice로도 전달된다(폴백 원천 제외)
test("notice: 실패/부분성공/stale에서만 채워지고 정상/휴장일에는 없다", () => {
  const failed = deriveTrustBarState(
    snapshot({ latest_attempt: attempt({ status: "failed", finished_at: RECENT_ISO }) })
  );
  assert.ok(failed.notice);

  const partial = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete(),
      latest_attempt: attempt({ status: "partial", unprocessed_count: 3, finished_at: RECENT_ISO }),
    })
  );
  assert.ok(partial.notice);

  const stale = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete({ published_at: STALE_ISO }),
      latest_attempt: attempt({ finished_at: STALE_ISO }),
    })
  );
  assert.ok(stale.notice);

  const published = deriveTrustBarState(
    snapshot({ no_snapshot: false, result_code: "OK", complete_snapshot: complete(), latest_attempt: attempt() })
  );
  assert.equal(published.notice, null);

  const skipped = deriveTrustBarState(
    snapshot({
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: complete(),
      latest_attempt: attempt({ status: "skipped", finished_at: RECENT_ISO }),
    })
  );
  assert.equal(skipped.notice, null);
});
