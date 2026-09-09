import http from "node:http";

const USER = { id: "e2e-user", email: "neo@example.test" };
const RUN_ID = "00000000-0000-4000-8000-000000000004";
const TRADING_DAY = "2026-09-09";

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

function rpcPayload(name) {
  if (name === "get_dashboard_snapshot") {
    return {
      no_snapshot: false,
      result_code: "OK",
      complete_snapshot: {
        logical_run_key: "close:2026-09-09",
        run_id: RUN_ID,
        trading_day: TRADING_DAY,
        batch_kind: "close",
        published_at: new Date().toISOString(),
        sections: { candidates: { candidate_count: 1, truncated_count: 0, original_count: 1, excluded_count: 0 } },
      },
      latest_attempt: {
        run_id: RUN_ID,
        logical_run_key: "close:2026-09-09",
        trading_day: TRADING_DAY,
        batch_kind: "close",
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
    return [{ candidate_id: "00000000-0000-4000-8000-000000000401", ticker: "005930", name: "조정후보", strategies: ["A"], vanished_strategies: [], supply_partial_missing: false }];
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
  if (name === "get_today_disappeared_candidates") return [];
  return null;
}

const server = http.createServer((request, response) => {
  if (request.method === "OPTIONS") return sendJson(response, 204, {});
  const url = new URL(request.url, "http://127.0.0.1");
  if (url.pathname === "/auth/v1/token") {
    return sendJson(response, 200, { access_token: "e2e-access-token", refresh_token: "e2e-refresh-token", token_type: "bearer", expires_in: 3600, user: USER });
  }
  if (url.pathname === "/auth/v1/user") {
    if (request.headers.authorization === "Bearer e2e-access-token") return sendJson(response, 200, USER);
    return sendJson(response, 401, { error: "invalid_token" });
  }
  if (url.pathname.startsWith("/rest/v1/rpc/")) {
    const payload = rpcPayload(url.pathname.split("/").pop());
    return payload === null ? sendJson(response, 404, { message: "unknown rpc" }) : sendJson(response, 200, payload);
  }
  return sendJson(response, 404, { message: "not found" });
});

server.listen(54321, "127.0.0.1");
