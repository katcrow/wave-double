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
