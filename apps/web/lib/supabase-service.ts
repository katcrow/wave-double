import { createClient, type SupabaseClient } from "@supabase/supabase-js";

let client: SupabaseClient | null = null;

/**
 * Story 1.10: service_role 전용 RPC(`request_manual_dispatch`, `claim_dispatch_outbox`,
 * `advance_dispatch_outbox`, `reconcile_dispatch_outbox`)를 호출하는 server-only 클라이언트.
 * `SUPABASE_SERVICE_ROLE_KEY`는 `.github/workflows/scheduled-batch.yml`/`apps/batch`가 이미 쓰는
 * 이름과 통일한다(`NEXT_PUBLIC_*`이 아니므로 브라우저에는 절대 노출되지 않는다).
 */
export function getSupabaseServiceClient(): SupabaseClient {
  if (client) return client;

  const url = process.env.SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !serviceRoleKey) {
    throw new Error("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 환경변수가 필요합니다.");
  }

  client = createClient(url, serviceRoleKey, { auth: { persistSession: false } });
  return client;
}
