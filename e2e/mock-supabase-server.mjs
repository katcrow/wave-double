import http from "node:http";
import crypto from "node:crypto";

const USER = { id: "e2e-user", email: "neo@example.test" };
const RUN_ID = "00000000-0000-4000-8000-000000000004";
const TRADING_DAY = "2026-09-09";
const BASE_URL = "http://127.0.0.1:54321";
const ISS = `${BASE_URL}/auth/v1`;
const AUD = "authenticated";
const KID = "e2e-kid";

// Retro epic-1-retro-item-6: 인증된 수동 dispatch 흐름을 e2e에서 자동 검증하기 위해 mock이
// 실제 Supabase Auth처럼 RS256 서명 JWT를 발급한다. 웹 서버(jwt-verify)는 이 mock이 서빙하는
// JWKS로 서명을 검증하므로, dispatch 인증 게이트가 운영 배포 전에 끝까지 동작함을 확인할 수 있다.
const { publicKey, privateKey } = crypto.generateKeyPairSync("rsa", { modulusLength: 2048 });

function b64url(value) {
  return Buffer.from(value, "utf8").toString("base64url");
}

function signJwt(overrides = {}) {
  const nowSec = Math.floor(Date.now() / 1000);
  const header = { alg: "RS256", kid: KID, typ: "JWT" };
  const payload = {
    sub: USER.id,
    email: USER.email,
    iss: ISS,
    aud: AUD,
    iat: nowSec,
    exp: nowSec + 3600,
    role: "authenticated",
    ...overrides,
  };
  const signingInput = `${b64url(JSON.stringify(header))}.${b64url(JSON.stringify(payload))}`;
  const signature = crypto.sign("RSA-SHA256", Buffer.from(signingInput, "utf8"), privateKey);
  return `${signingInput}.${signature.toString("base64url")}`;
}

function decodeJwt(token) {
  const parts = String(token ?? "").split(".");
  if (parts.length !== 3) return null;
  try {
    return JSON.parse(Buffer.from(parts[1], "base64url").toString("utf8"));
  } catch {
    return null;
  }
}

let dispatchCounter = 0;
const dispatchByIdempotency = new Map();

/**
 * epic-2-retro-item-12 / epic-7-retro-item-29: 시나리오 스위치.
 *
 * 후보 카드의 부분/완전 소멸, 모집단 이탈, 수집 실패, 장중 라벨, 전략 F 배지는 모두 같은
 * 화면의 다른 RPC 응답 조합이라 fixture 하나로는 렌더 결과를 검증할 수 없다. webServer는
 * 스위트당 하나만 뜨므로 프로세스 재시작 대신 제어 엔드포인트로 활성 시나리오를 바꾼다.
 *
 *   await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "partial-vanish" } });
 *
 * 알 수 없는 시나리오 이름은 400으로 거부한다(오타가 조용히 default를 검증하는 것을 막는다).
 */
const SCENARIOS = new Set([
  "default",
  "partial-vanish",
  "complete-vanish",
  "population-dropout",
  "collection-failure",
  "intraday",
  "strategy-f",
  "tracking-empty",
  "tracking-error",
  "tracking-malformed",
    "tracking-metric-below-gate",
    "tracking-metric-all-win",
    "tracking-metric-error",
  "tracking-metric-malformed",
]);
let activeScenario = "default";

function sendJson(response, status, body) {
  response.writeHead(status, {
    "content-type": "application/json",
    "access-control-allow-origin": "http://localhost:3000",
    "access-control-allow-credentials": "true",
    "access-control-allow-headers": "apikey, authorization, content-type, x-client-info, x-supabase-api-version",
    "access-control-allow-methods": "GET, POST, OPTIONS",
  });
  response.end(JSON.stringify(body));
}

function rpcPayload(name, body = {}) {
  if (name === "request_manual_dispatch") {
    const idempotencyKey = body?.p_idempotency_key;
    if (idempotencyKey && dispatchByIdempotency.has(idempotencyKey)) {
      const existing = dispatchByIdempotency.get(idempotencyKey);
      return { status: existing.status, dispatch_request_id: existing.dispatch_request_id, reason: "replayed" };
    }
    dispatchCounter += 1;
    const created = {
      status: "created",
      dispatch_request_id: `00000000-0000-4000-8000-00000000040${dispatchCounter}`,
      outbox_id: `00000000-0000-4000-8000-00000000050${dispatchCounter}`,
      reason: "created",
    };
    if (idempotencyKey) dispatchByIdempotency.set(idempotencyKey, created);
    return created;
  }
  if (name === "get_dashboard_snapshot") {
    // 장중 시나리오는 complete_snapshot과 latest_attempt의 batch_kind만 바꾼다
    // (isIntradaySnapshot이 그 값으로 "장중 참고 · 최종 추천 미확정" 라벨을 고정 표시한다).
    const batchKind = activeScenario === "intraday" ? "intraday" : "close";
    const logicalRunKey = `${batchKind}:${TRADING_DAY}`;
    return {
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: {
        logical_run_key: logicalRunKey,
        run_id: RUN_ID,
        trading_day: TRADING_DAY,
        batch_kind: batchKind,
        published_at: new Date().toISOString(),
        sections: { candidates: { candidate_count: 1, truncated_count: 0, original_count: 1, excluded_count: 0 } },
      },
      latest_attempt: {
        run_id: RUN_ID,
        logical_run_key: logicalRunKey,
        trading_day: TRADING_DAY,
        batch_kind: batchKind,
        status: "published",
        trigger: "manual",
        started_at: new Date().toISOString(),
        finished_at: new Date().toISOString(),
        stage_status: { candidates: "success", tags: "success", supply_3day: "success", market_supply: "success", outcome_tracking: "success" },
        unprocessed_count: 0,
        truncated_count: 0,
        original_count: 1,
        excluded_count: 0,
      },
      latest_partial_run_id: null,
      available_partial_sections: ["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"],
      missing_sections: [],
      unprocessed_items: 0,
    };
  }
  if (name === "get_today_candidate_cards") {
    const base = { candidate_id: "00000000-0000-4000-8000-000000000401", ticker: "005930", name: "조정후보", strategies: ["A"], vanished_strategies: [], supply_partial_missing: false };
    if (activeScenario === "partial-vanish") {
      // active 태그와 vanished 태그가 함께 있는 상태 -> 카드는 남고 "소멸: 전략 B" 문구가 붙는다.
      return [{ ...base, strategies: ["A"], vanished_strategies: ["B"] }];
    }
    if (activeScenario === "complete-vanish") {
      // active 태그 0건 + vanished만 -> 카드는 목록에 남고 시그널이 "소멸"이다.
      return [{ ...base, strategies: [], vanished_strategies: ["A", "B"] }];
    }
    if (activeScenario === "collection-failure") {
      return [{ ...base, supply_partial_missing: true }];
    }
    if (activeScenario === "strategy-f") {
      return [{ ...base, name: "F후보", strategies: ["F"], vanished_strategies: [] }];
    }
    return [base];
  }
  if (name === "get_candidate_evidence") {
    return [{
      candidate_id: "00000000-0000-4000-8000-000000000401",
      sources: ["t1859"],
      rows: [
        { trading_day: "2026-09-09", slot: "D0", close: 71000, volume: 1200000, change_pct: 2.9, foreign_net: 800, institution_net: 400, individual_net: -1200, program_net: 50, investor_net_status: "confirmed", collected_at: new Date().toISOString() },
        { trading_day: "2026-09-08", slot: "D-1", close: 69000, volume: 1100000, change_pct: 1.4, foreign_net: 200, institution_net: 100, individual_net: -300, program_net: 20, investor_net_status: "confirmed", collected_at: new Date().toISOString() },
        { trading_day: "2026-09-07", slot: "D-2", close: 68000, volume: 1000000, change_pct: 1.0, foreign_net: 100, institution_net: 50, individual_net: -150, program_net: 10, investor_net_status: "confirmed", collected_at: new Date().toISOString() },
      ],
    }];
  }
  if (name === "get_candidate_supply_hints") {
    return [{ candidate_id: "00000000-0000-4000-8000-000000000401", attempt_run_id: RUN_ID, ticker: "005930", trading_day: TRADING_DAY, slot: "D0", batch_kind: "close", foreign_net: 800, institution_net: 400, individual_net: -1200, program_net: 50, investor_net_status: "confirmed", collected_at: new Date().toISOString(), hint_status: "good" }];
  }
  if (name === "get_market_supply") {
    return [
      { market: "KOSPI", trading_day: TRADING_DAY, foreign_net: 100, institution_net: -20, individual_net: 50, program_net: 30, collected_at: new Date().toISOString() },
      { market: "KOSDAQ", trading_day: TRADING_DAY, foreign_net: -10, institution_net: 30, individual_net: 40, program_net: -5, collected_at: new Date().toISOString() },
    ];
  }
  if (name === "get_today_disappeared_candidates") {
    if (activeScenario === "population-dropout") {
      return [{ ticker: "000660", name: "이탈종목", reason: "population_dropout", strategies: ["A"] }];
    }
    if (activeScenario === "collection-failure") {
      return [{ ticker: "035420", name: "수집실패종목", reason: "collection_failure", strategies: ["B"] }];
    }
    return [];
  }
  if (name === "get_outcome_tracking_rows") {
    if (activeScenario === "tracking-error") return null;
    if (activeScenario === "tracking-malformed") return { unexpected: true };
    if (activeScenario === "tracking-empty") return [];

      const rows = [
      { outcome_id: "00000000-0000-4000-8000-000000000601", ticker: "005930", strategy: "A", entry_date: "2026-09-09", status: "TP", exit_date: "2026-09-12", return_pct: 2.9 },
      { outcome_id: "00000000-0000-4000-8000-000000000602", ticker: "000660", strategy: "B", entry_date: "2026-09-08", status: "SL", exit_date: "2026-09-10", return_pct: -3.1 },
      { outcome_id: "00000000-0000-4000-8000-000000000603", ticker: "035420", strategy: "C", entry_date: "2026-09-07", status: "TIMEOUT", exit_date: "2026-09-30", return_pct: 0.4 },
      { outcome_id: "00000000-0000-4000-8000-000000000604", ticker: "051910", strategy: "D", entry_date: "2026-09-06", status: "OPEN", exit_date: null, return_pct: null },
      { outcome_id: "00000000-0000-4000-8000-000000000605", ticker: "068270", strategy: "E", entry_date: "2026-09-05", status: "SUSPENDED", exit_date: null, return_pct: null },
      { outcome_id: "00000000-0000-4000-8000-000000000606", ticker: "035720", strategy: "F", entry_date: "2026-09-04", status: "DELISTED", exit_date: "2026-09-05", return_pct: null },
    ];
    const status = ["TP", "SL", "TIMEOUT", "OPEN", "SUSPENDED", "DELISTED"].includes(body?.p_status) ? body.p_status : null;
    const strategy = ["A", "B", "C", "D", "E", "F"].includes(body?.p_strategy) ? body.p_strategy : null;
    const ticker = typeof body?.p_ticker === "string" ? body.p_ticker.trim() : "";
    const limit = Math.max(1, Math.min(Number.isFinite(body?.p_limit) ? body.p_limit : 500, 500));
    return rows
      .filter((row) => (!status || row.status === status) && (!strategy || row.strategy === strategy) && (!ticker || row.ticker.includes(ticker)))
      .slice(0, limit);
  }
  if (name === "get_outcome_metric_comparison") {
    if (activeScenario === "tracking-metric-error") return null;
    if (activeScenario === "tracking-metric-malformed") return { unexpected: true };

    const base = {
      total_settled: 40,
      wins: 28,
      losses: 12,
      open_count: 2,
      suspended_count: 0,
      delisted_count: 0,
      gross_win: 56,
      gross_loss: 12,
      win_rate: 0.7,
      profit_factor: 4.6667,
      sample_gate_min_required: 30,
      sample_gate_passed: true,
      sample_gate_label: null,
      ci_lower: 0.54,
      ci_upper: 0.82,
      expected_win_rate: null,
      expected_in_ci: null,
      expected_profit_factor: null,
      win_rate_threshold_pp: null,
      profit_factor_threshold_ratio: null,
      win_rate_threshold_breached: null,
      profit_factor_threshold_breached: null,
      threshold_warning: null,
      timeout_count: 0,
      cutoff_bias_sample_size: null,
      cutoff_bias_timeout_rate: null,
      cutoff_bias_profit_factor_delta: null,
      cutoff_bias_label: null,
    };
    const rows = [
      { ...base, strategy: null, total_settled: 179, wins: 89, losses: 90, open_count: 1, suspended_count: 1, delisted_count: 1, gross_win: 174.9, gross_loss: 105, win_rate: 0.4972, profit_factor: 1.6657, ci_lower: 0.4248, ci_upper: 0.5697, timeout_count: 2 },
      { ...base, strategy: "A", expected_win_rate: 0.6871, expected_in_ci: true, expected_profit_factor: 2.054, win_rate_threshold_breached: false, profit_factor_threshold_breached: false, threshold_warning: false, timeout_count: 1, cutoff_bias_sample_size: 30, cutoff_bias_timeout_rate: 0, cutoff_bias_profit_factor_delta: 0, cutoff_bias_label: "TIMEOUT 0% / PF차 ±0" },
      { ...base, strategy: "B", expected_win_rate: 0.6895, expected_in_ci: false, expected_profit_factor: 2.077, win_rate_threshold_breached: true, profit_factor_threshold_breached: true, threshold_warning: true, timeout_count: 1, cutoff_bias_sample_size: 30, cutoff_bias_timeout_rate: 0.0037, cutoff_bias_profit_factor_delta: 0.0125, cutoff_bias_label: "TIMEOUT 0.37% / PF차 +0.0125" },
      { ...base, strategy: "C", total_settled: 29, wins: 14, losses: 15, win_rate: null, profit_factor: null, sample_gate_passed: false, sample_gate_label: "표본 부족 (29/30)", ci_lower: null, ci_upper: null, expected_win_rate: null, expected_in_ci: null, expected_profit_factor: null, win_rate_threshold_pp: null, profit_factor_threshold_ratio: null, win_rate_threshold_breached: null, profit_factor_threshold_breached: null },
      { ...base, strategy: "D" },
      { ...base, strategy: "E" },
        { ...base, strategy: "F" },
      ];
      const strategy = ["A", "B", "C", "D", "E", "F"].includes(body?.p_strategy) ? body.p_strategy : null;
      if (activeScenario === "tracking-metric-all-win") {
        const allWinRows = rows.map((row) => row.strategy === "F" ? {
          ...row,
          wins: 40,
          losses: 0,
          gross_win: 80,
          gross_loss: null,
          win_rate: 1,
          profit_factor: null,
        } : row);
        return strategy ? allWinRows.filter((row) => row.strategy === strategy) : allWinRows;
      }
      return strategy ? rows.filter((row) => row.strategy === strategy) : rows;
  }
  return null;
}

function readRequestBody(request) {
  return new Promise((resolve) => {
    const chunks = [];
    request.on("data", (chunk) => chunks.push(chunk));
    request.on("end", () => {
      if (!chunks.length) return resolve({});
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      } catch {
        resolve({});
      }
    });
  });
}

const server = http.createServer((request, response) => {
  if (request.method === "OPTIONS") return sendJson(response, 204, {});
  const url = new URL(request.url, BASE_URL);

  if (url.pathname === "/auth/v1/.well-known/jwks.json") {
    const jwk = { ...publicKey.export({ format: "jwk" }), kid: KID, alg: "RS256", use: "sig" };
    return sendJson(response, 200, { keys: [jwk] });
  }

  if (url.pathname === "/auth/v1/token") {
    return sendJson(response, 200, {
      access_token: signJwt(),
      refresh_token: "e2e-refresh-token",
      token_type: "bearer",
      expires_in: 3600,
      user: USER,
    });
  }

  if (url.pathname === "/auth/v1/user") {
    const token = request.headers.authorization?.replace(/^Bearer /, "");
    const claims = decodeJwt(token);
    if (claims && claims.sub === USER.id && typeof claims.exp === "number" && claims.exp * 1000 > Date.now()) {
      return sendJson(response, 200, USER);
    }
    return sendJson(response, 401, { error: "invalid_token" });
  }

  if (url.pathname === "/__e2e/scenario") {
    if (request.method === "GET") return sendJson(response, 200, { scenario: activeScenario });
    return readRequestBody(request).then((body) => {
      const requested = body?.scenario ?? "default";
      if (!SCENARIOS.has(requested)) {
        return sendJson(response, 400, { message: `unknown scenario: ${requested}`, known: [...SCENARIOS] });
      }
      activeScenario = requested;
      return sendJson(response, 200, { scenario: activeScenario });
    });
  }

  if (url.pathname.startsWith("/rest/v1/rpc/")) {
    const name = url.pathname.split("/").pop();
    return readRequestBody(request).then((body) => {
      const payload = rpcPayload(name, body);
      return payload === null ? sendJson(response, 404, { message: "unknown rpc" }) : sendJson(response, 200, payload);
    });
  }

  return sendJson(response, 404, { message: "not found" });
});

server.listen(54321, "127.0.0.1");
