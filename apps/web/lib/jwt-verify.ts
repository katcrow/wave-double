import { createPublicKey, verify as cryptoVerify, type KeyObject } from "node:crypto";

/**
 * Story 1.10 (AD-7): `/api/dispatch`가 통과하는 유일한 인가 게이트.
 * `node:crypto`만으로 JWKS 기반 RS256/ES256 서명·issuer·audience·expiry·sub를 검증한다.
 * proxy.ts의 `getUser()` 낙관적 체크와는 별개의 독립 검증이다(2단 방어, Design Notes KEEP).
 */

export interface JwkRecord {
  kty: string;
  kid?: string;
  alg?: string;
  n?: string;
  e?: string;
  crv?: string;
  x?: string;
  y?: string;
}

export interface Jwks {
  keys: JwkRecord[];
}

export interface JwtClaims {
  sub: string;
  email?: string;
  iss?: string;
  aud?: string | string[];
  exp?: number;
  iat?: number;
  [key: string]: unknown;
}

export type JwtVerificationErrorCode =
  | "INVALID_TOKEN"
  | "UNSUPPORTED_ALG"
  | "JWKS_FETCH_FAILED"
  | "KEY_NOT_FOUND"
  | "INVALID_KEY"
  | "INVALID_SIGNATURE"
  | "INVALID_ISSUER"
  | "INVALID_AUDIENCE"
  | "TOKEN_EXPIRED"
  | "MISSING_SUB";

export class JwtVerificationError extends Error {
  readonly code: JwtVerificationErrorCode;

  constructor(code: JwtVerificationErrorCode, message: string) {
    super(message);
    this.name = "JwtVerificationError";
    this.code = code;
  }
}

export interface VerifyJwtOptions {
  jwksUrl: string;
  issuer: string;
  audience: string;
  /** 테스트에서 시계를 고정하기 위한 훅. epoch milliseconds를 반환한다. */
  now?: () => number;
  /** 테스트에서 네트워크 호출을 대체하기 위한 훅. */
  fetchJwks?: (url: string) => Promise<Jwks>;
}

const ALGORITHMS: Record<string, { nodeAlgorithm: string; dsaEncoding?: "ieee-p1363" }> = {
  RS256: { nodeAlgorithm: "RSA-SHA256" },
  ES256: { nodeAlgorithm: "SHA256", dsaEncoding: "ieee-p1363" },
};

function base64UrlDecode(input: string): Buffer {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  return Buffer.from(normalized, "base64");
}

async function defaultFetchJwks(url: string): Promise<Jwks> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new JwtVerificationError("JWKS_FETCH_FAILED", `failed to fetch JWKS: HTTP ${response.status}`);
  }
  const body = (await response.json()) as Partial<Jwks>;
  if (!Array.isArray(body.keys)) {
    throw new JwtVerificationError("JWKS_FETCH_FAILED", "JWKS response is missing a keys array");
  }
  return body as Jwks;
}

/**
 * JWKS는 짧은 TTL로 캐싱한다 -- 매 dispatch 호출마다 네트워크를 왕복하면 불필요한 지연/의존성이
 * 생기고, Supabase Auth/JWKS 엔드포인트의 일시 장애가 곧바로 401(세션 무효)로 오인된다(실제로는
 * JWKS_FETCH_FAILED). `KEY_NOT_FOUND`(키 로테이션 직후일 수 있음)를 만나면 캐시를 무시하고 한 번
 * 즉시 재조회한다.
 */
const JWKS_CACHE_TTL_MS = 10 * 60 * 1000;
let jwksCache: { url: string; jwks: Jwks; fetchedAtMs: number } | null = null;

async function cachedFetchJwks(url: string, fetchJwks: (url: string) => Promise<Jwks>, nowMs: number): Promise<Jwks> {
  if (jwksCache && jwksCache.url === url && nowMs - jwksCache.fetchedAtMs < JWKS_CACHE_TTL_MS) {
    return jwksCache.jwks;
  }
  const jwks = await fetchJwks(url);
  jwksCache = { url, jwks, fetchedAtMs: nowMs };
  return jwks;
}

function toPublicKey(jwk: JwkRecord): KeyObject {
  const jwkInput: JsonWebKey =
    jwk.kty === "EC"
      ? { kty: jwk.kty, crv: jwk.crv, x: jwk.x, y: jwk.y }
      : { kty: jwk.kty, n: jwk.n, e: jwk.e };
  return createPublicKey({ key: jwkInput, format: "jwk" });
}

export async function verifyJwt(token: string, options: VerifyJwtOptions): Promise<JwtClaims> {
  // 캐싱은 실제 네트워크 fetch(기본 경로)에만 적용한다 -- 테스트가 주입하는 `fetchJwks`는 매 호출을
  // 그대로 실행해야 하므로(예: RS256/ES256 fixture가 같은 jwksUrl로 서로 다른 키를 반환) 캐시를
  // 우회한다.
  const usingDefaultFetch = options.fetchJwks === undefined;
  const fetchJwks = options.fetchJwks ?? defaultFetchJwks;
  const nowMs = (options.now ?? Date.now)();

  const parts = token.split(".");
  if (parts.length !== 3) throw new JwtVerificationError("INVALID_TOKEN", "malformed JWT");
  const [headerB64, payloadB64, signatureB64] = parts;

  let header: { alg?: string; kid?: string };
  let claims: JwtClaims;
  try {
    header = JSON.parse(base64UrlDecode(headerB64).toString("utf8"));
    claims = JSON.parse(base64UrlDecode(payloadB64).toString("utf8"));
  } catch {
    throw new JwtVerificationError("INVALID_TOKEN", "malformed JWT header or payload");
  }

  const algSpec = header.alg ? ALGORITHMS[header.alg] : undefined;
  if (!algSpec) throw new JwtVerificationError("UNSUPPORTED_ALG", `unsupported alg: ${String(header.alg)}`);

  const findMatch = (jwks: Jwks) =>
    jwks.keys.find((key) => (header.kid ? key.kid === header.kid : key.alg === header.alg));

  let jwks = usingDefaultFetch
    ? await cachedFetchJwks(options.jwksUrl, fetchJwks, nowMs)
    : await fetchJwks(options.jwksUrl);
  let jwk = findMatch(jwks);
  if (!jwk && usingDefaultFetch) {
    // 캐시가 최신 키 로테이션을 놓쳤을 수 있으니, 캐시를 무시하고 한 번만 강제로 재조회한다.
    jwks = await fetchJwks(options.jwksUrl);
    jwksCache = { url: options.jwksUrl, jwks, fetchedAtMs: nowMs };
    jwk = findMatch(jwks);
  }
  if (!jwk) throw new JwtVerificationError("KEY_NOT_FOUND", "no matching JWK for kid");

  let publicKey: KeyObject;
  try {
    publicKey = toPublicKey(jwk);
  } catch {
    throw new JwtVerificationError("INVALID_KEY", "could not import JWK as a public key");
  }

  const signingInput = Buffer.from(`${headerB64}.${payloadB64}`, "utf8");
  const signature = base64UrlDecode(signatureB64);
  let signatureValid: boolean;
  try {
    signatureValid = algSpec.dsaEncoding
      ? cryptoVerify(algSpec.nodeAlgorithm, signingInput, { key: publicKey, dsaEncoding: algSpec.dsaEncoding }, signature)
      : cryptoVerify(algSpec.nodeAlgorithm, signingInput, publicKey, signature);
  } catch {
    signatureValid = false;
  }
  if (!signatureValid) throw new JwtVerificationError("INVALID_SIGNATURE", "JWT signature verification failed");

  if (claims.iss !== options.issuer) throw new JwtVerificationError("INVALID_ISSUER", "unexpected issuer");

  const audiences = Array.isArray(claims.aud) ? claims.aud : claims.aud ? [claims.aud] : [];
  if (!audiences.includes(options.audience)) {
    throw new JwtVerificationError("INVALID_AUDIENCE", "unexpected audience");
  }

  if (typeof claims.exp !== "number" || claims.exp * 1000 <= nowMs) {
    throw new JwtVerificationError("TOKEN_EXPIRED", "token is expired");
  }

  if (!claims.sub || typeof claims.sub !== "string") {
    throw new JwtVerificationError("MISSING_SUB", "token is missing the sub claim");
  }

  return claims;
}
