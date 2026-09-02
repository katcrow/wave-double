import assert from "node:assert/strict";
import { test } from "node:test";
import { generateKeyPairSync, sign as cryptoSign } from "node:crypto";
import { verifyJwt, JwtVerificationError, type Jwks } from "./jwt-verify.ts";

const ISSUER = "https://project.supabase.co/auth/v1";
const AUDIENCE = "authenticated";
const JWKS_URL = "https://project.supabase.co/auth/v1/.well-known/jwks.json";

function base64Url(input: Buffer): string {
  return input.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function buildToken(
  header: Record<string, unknown>,
  payload: Record<string, unknown>,
  sign: (signingInput: Buffer) => Buffer
): string {
  const headerB64 = base64Url(Buffer.from(JSON.stringify(header), "utf8"));
  const payloadB64 = base64Url(Buffer.from(JSON.stringify(payload), "utf8"));
  const signingInput = Buffer.from(`${headerB64}.${payloadB64}`, "utf8");
  const signature = sign(signingInput);
  return `${headerB64}.${payloadB64}.${base64Url(signature)}`;
}

function baseClaims(overrides: Record<string, unknown> = {}) {
  const now = Math.floor(Date.now() / 1000);
  return {
    sub: "11111111-1111-1111-1111-111111111111",
    email: "neo@example.com",
    iss: ISSUER,
    aud: AUDIENCE,
    iat: now,
    exp: now + 3600,
    ...overrides,
  };
}

// --- RS256 fixture ---
const rsaKeys = generateKeyPairSync("rsa", { modulusLength: 2048 });
const rsaJwk = rsaKeys.publicKey.export({ format: "jwk" }) as { kty: string; n: string; e: string };

function signRs256(signingInput: Buffer): Buffer {
  return cryptoSign("RSA-SHA256", signingInput, rsaKeys.privateKey);
}

function fetchRsaJwks(): Promise<Jwks> {
  return Promise.resolve({ keys: [{ kty: rsaJwk.kty, kid: "rsa-kid", alg: "RS256", n: rsaJwk.n, e: rsaJwk.e }] });
}

// --- ES256 fixture ---
const ecKeys = generateKeyPairSync("ec", { namedCurve: "P-256" });
const ecJwk = ecKeys.publicKey.export({ format: "jwk" }) as { kty: string; crv: string; x: string; y: string };

function signEs256(signingInput: Buffer): Buffer {
  return cryptoSign("SHA256", signingInput, { key: ecKeys.privateKey, dsaEncoding: "ieee-p1363" });
}

function fetchEcJwks(): Promise<Jwks> {
  return Promise.resolve({ keys: [{ kty: ecJwk.kty, kid: "ec-kid", alg: "ES256", crv: ecJwk.crv, x: ecJwk.x, y: ecJwk.y }] });
}

test("RS256: 유효한 토큰을 수락한다", async () => {
  const token = buildToken({ alg: "RS256", kid: "rsa-kid", typ: "JWT" }, baseClaims(), signRs256);
  const claims = await verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks });
  assert.equal(claims.sub, "11111111-1111-1111-1111-111111111111");
  assert.equal(claims.email, "neo@example.com");
});

test("ES256: 유효한 토큰을 수락한다", async () => {
  const token = buildToken({ alg: "ES256", kid: "ec-kid", typ: "JWT" }, baseClaims(), signEs256);
  const claims = await verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchEcJwks });
  assert.equal(claims.sub, "11111111-1111-1111-1111-111111111111");
});

test("잘못된 서명은 거부된다", async () => {
  const token = buildToken({ alg: "RS256", kid: "rsa-kid", typ: "JWT" }, baseClaims(), () => Buffer.from("not-a-real-signature"));
  await assert.rejects(
    verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "INVALID_SIGNATURE"
  );
});

test("잘못된 issuer는 거부된다", async () => {
  const token = buildToken({ alg: "RS256", kid: "rsa-kid", typ: "JWT" }, baseClaims({ iss: "https://evil.example.com" }), signRs256);
  await assert.rejects(
    verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "INVALID_ISSUER"
  );
});

test("잘못된 audience는 거부된다", async () => {
  const token = buildToken({ alg: "RS256", kid: "rsa-kid", typ: "JWT" }, baseClaims({ aud: "anon" }), signRs256);
  await assert.rejects(
    verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "INVALID_AUDIENCE"
  );
});

test("만료된 토큰은 거부된다", async () => {
  const now = Math.floor(Date.now() / 1000);
  const token = buildToken({ alg: "RS256", kid: "rsa-kid", typ: "JWT" }, baseClaims({ iat: now - 7200, exp: now - 3600 }), signRs256);
  await assert.rejects(
    verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "TOKEN_EXPIRED"
  );
});

test("sub 누락은 거부된다", async () => {
  const claims = baseClaims();
  delete (claims as Record<string, unknown>).sub;
  const token = buildToken({ alg: "RS256", kid: "rsa-kid", typ: "JWT" }, claims, signRs256);
  await assert.rejects(
    verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "MISSING_SUB"
  );
});

test("알 수 없는 kid는 거부된다", async () => {
  const token = buildToken({ alg: "RS256", kid: "unknown-kid", typ: "JWT" }, baseClaims(), signRs256);
  await assert.rejects(
    verifyJwt(token, { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "KEY_NOT_FOUND"
  );
});

test("형식이 깨진 토큰은 거부된다", async () => {
  await assert.rejects(
    verifyJwt("not-a-jwt", { jwksUrl: JWKS_URL, issuer: ISSUER, audience: AUDIENCE, fetchJwks: fetchRsaJwks }),
    (err: unknown) => err instanceof JwtVerificationError && err.code === "INVALID_TOKEN"
  );
});
