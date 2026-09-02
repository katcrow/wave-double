import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

/**
 * Story 1.10: 쿠키 기반 세션 클라이언트(로그인 콜백/세션 확인용).
 * Server Component/Route Handler에서만 사용한다(publishable key + 사용자 쿠키 세션).
 */
export async function createSupabaseServerClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey) {
    throw new Error("NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY 환경변수가 필요합니다.");
  }

  const cookieStore = await cookies();

  return createServerClient(url, publishableKey, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          for (const { name, value, options } of cookiesToSet) {
            cookieStore.set(name, value, options);
          }
        } catch {
          // Server Component에서 호출되면 쿠키를 쓸 수 없다 -- proxy가 세션 갱신을 담당하므로 무시한다.
        }
      },
    },
  });
}
