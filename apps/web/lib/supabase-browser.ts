import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

/**
 * Story 1.9: `/`와 `/runs`가 공유하는 publishable key 기반 Supabase 클라이언트 싱글턴.
 * anon 허용된 get_dashboard_snapshot() RPC 및 runs/logical_runs 공개 SELECT만 사용한다.
 */
export function getSupabaseBrowserClient(): SupabaseClient {
  if (client) return client;

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

  if (!url || !publishableKey) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY 환경변수가 필요합니다."
    );
  }

  client = createClient(url, publishableKey, {
    auth: { persistSession: false },
  });

  return client;
}
