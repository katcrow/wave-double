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

const nextConfig: NextConfig = {};

export default nextConfig;
