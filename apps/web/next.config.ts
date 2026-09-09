import type { NextConfig } from "next";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

/**
 * Story 1.9: apps/web에는 자체 .env.local이 없고, 워크스페이스 루트의 .env.local에
 * NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY가 있다.
 * 새 npm 패키지를 추가하지 않고 dev/build 프로세스 시작 시점에 루트 .env.local을
 * process.env로 병합해 next dev/build가 항상 같은 값을 읽도록 한다(이미 설정된 값은 덮지 않음).
 */
function loadRootEnvFile() {
  const rootEnvPath = path.resolve(__dirname, "../../.env.local");
  if (!existsSync(rootEnvPath)) return;

  const contents = readFileSync(rootEnvPath, "utf8");
  for (const line of contents.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;

    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }

    if (process.env[key] === undefined) {
      process.env[key] = value;
    }
  }
}

loadRootEnvFile();

/**
 * Story 1.10 후속: 이 앱의 double-submit CSRF(`wd_csrf`)와 dispatch route의 JWT 검증은 둘 다
 * `apps/web` 자체에 XSS가 없다는 가정 위에 서 있다 -- CSP 없이는 방어선이 없다. 인라인 스크립트는
 * Next.js가 hydration에 nonce 없는 인라인 JSON을 쓰므로 완전히 막을 수 없어 `unsafe-inline`을
 * 둔다(엄밀한 방어는 아니지만 외부 스크립트 주입/제3자 로드는 막는다). 새 의존성을 추가하지
 * 않는다는 스펙 제약과 무관한 변경이라 `next.config.ts`의 `headers()`만으로 구현한다.
 */
async function headers() {
  // React/Next 개발 모드는 디버깅용 스택 재구성에 eval()을 쓴다(프로덕션 빌드는 쓰지 않는다,
  // Next 공식 안내) -- 'unsafe-eval'을 프로덕션까지 열어두면 CSP의 실질적 방어력이 없어지므로
  // 개발 환경에서만 추가한다.
  const scriptSrc = process.env.NODE_ENV === "production" ? "'self' 'unsafe-inline'" : "'self' 'unsafe-inline' 'unsafe-eval'";
  const connectSources = ["'self'", "https://*.supabase.co"];
  // Deterministic authenticated E2E uses a loopback Supabase fixture. Keep this
  // origin development-only so production CSP never trusts arbitrary local hosts.
  if (process.env.NODE_ENV !== "production" && process.env.NEXT_PUBLIC_SUPABASE_URL) {
    try {
      const origin = new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).origin;
      if (origin === "http://127.0.0.1:54321") connectSources.push(origin);
    } catch {
      // Runtime env validation remains the responsibility of the Supabase clients.
    }
  }
  return [
    {
      source: "/:path*",
      headers: [
        {
          key: "Content-Security-Policy",
          value: [
            "default-src 'self'",
            `script-src ${scriptSrc}`,
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "font-src 'self' https://cdn.jsdelivr.net",
            "img-src 'self' data:",
            `connect-src ${connectSources.join(" ")}`,
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
          ].join("; "),
        },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      ],
    },
  ];
}

const nextConfig: NextConfig = { headers };

export default nextConfig;
