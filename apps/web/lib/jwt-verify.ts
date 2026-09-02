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
  return (await response.json()) as Jwks;
}

function toPublicKey(jwk: JwkRecord): KeyObject {
  const jwkInput: JsonWebKey =
    jwk.kty === "EC"
      ? { kty: jwk.kty, crv: jwk.crv, x: jwk.x, y: jwk.y }
      : { kty: jwk.kty, n: jwk.n, e: jwk.e };
  return createPublicKey({ key: jwkInput, format: "jwk" });
}

export async function verifyJwt(token: string, options: VerifyJwtOptions): Promise<JwtClaims> {
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

  const jwks = await fetchJwks(options.jwksUrl);
  const jwk = jwks.keys.find((key) => (header.kid ? key.kid === header.kid : true));
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
