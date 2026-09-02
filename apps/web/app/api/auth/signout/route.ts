import { NextResponse, type NextRequest } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase-server";

/**
 * Story 1.10 후속: 로그인/콜백은 있는데 로그아웃 경로가 없었다 -- 세션 침해 의심 등으로 강제
 * 로그아웃이 필요할 때 앱 안에서 할 방법이 없어, 브라우저 쿠키를 수동으로 지우거나 Supabase
 * 대시보드에서 세션을 revoke해야 했다. 단일 운영자 세션이 이 앱의 유일한 보안 경계이므로
 * in-product 로그아웃을 제공한다.
 */
export async function POST(request: NextRequest) {
  const supabase = await createSupabaseServerClient();
  await supabase.auth.signOut();
  return NextResponse.redirect(new URL("/login", request.url));
}
