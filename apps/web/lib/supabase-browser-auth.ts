import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

/**
 * Story 1.10: 로그인 폼과 수동 실행 버튼이 공유하는 쿠키 기반 인증 세션 클라이언트.
 * `lib/supabase-browser.ts`(persistSession:false, 공개 스냅샷 조회 전용)와는 별개다 --
 * 이 클라이언트는 `@supabase/ssr`의 쿠키 저장소를 써서 proxy.ts/서버가 같은 세션을 본다.
 */
export function getSupabaseAuthBrowserClient(): SupabaseClient {
  if (client) return client;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey) {
    throw new Error("NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY 환경변수가 필요합니다.");
  }

  client = createBrowserClient(url, publishableKey);
  return client;
}
