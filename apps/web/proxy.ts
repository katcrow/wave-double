import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { CSRF_COOKIE_NAME } from "@/lib/csrf-constants";

/**
 * Story 1.10 (AD-7): 미인증 세션은 `/login`으로 리다이렉트한다.
 * Next.js 16은 `middleware.ts`를 `proxy.ts`로 이름을 바꿨다(node_modules/next/dist/docs 참고).
 * 여기서 하는 `getUser()` 체크는 낙관적 리다이렉트일 뿐이다 -- 실제 dispatch 권한 게이트는
 * `/api/dispatch`의 독립 JWKS 서명/issuer/audience/expiry/sub 검증이다(2단 방어, Design Notes KEEP).
 *
 * `/api/*` 전체를 제외한다: 이 낙관적 체크가 세션 만료/누락 상태의 POST를 302로 가로채면
 * 브라우저 `fetch()`가 그 리다이렉트를 따라가 로그인 페이지 HTML을 200으로 오인하고, route가
 * 내야 할 401 JSON(JWKS 검증 실패)이 실질적으로 무력화된다. 각 API route는 이미 자체 인증을
 * 한다(`/api/dispatch`는 JWKS, `/api/dispatch/worker`는 `CRON_CALLBACK_SECRET`).
 */
const PUBLIC_PATH_PATTERNS = [/^\/login(\/.*)?$/, /^\/auth(\/.*)?$/, /^\/api(\/.*)?$/];

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (PUBLIC_PATH_PATTERNS.some((pattern) => pattern.test(pathname))) {
    return NextResponse.next();
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey) {
    // 설정 누락은 이 파일이 판단할 문제가 아니다 -- 페이지/라우트가 각자 오류를 낸다.
    return NextResponse.next();
  }

  let response = NextResponse.next({ request });

  const supabase = createServerClient(url, publishableKey, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        for (const { name, value } of cookiesToSet) {
          request.cookies.set(name, value);
        }
        response = NextResponse.next({ request });
        for (const { name, value, options } of cookiesToSet) {
          response.cookies.set(name, value, options);
        }
      },
    },
  });

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (!request.cookies.get(CSRF_COOKIE_NAME)) {
    response.cookies.set(CSRF_COOKIE_NAME, crypto.randomUUID(), {
      httpOnly: false,
      sameSite: "strict",
      secure: process.env.NODE_ENV === "production",
      path: "/",
    });
  }

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
