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
 *
 * 정적 자산(robots.txt/manifest.json 등)도 matcher에서 제외한다 -- 이 앱은 지금 그런 파일을
 * 서빙하지 않지만, 나중에 추가되면 로그인 리다이렉트에 걸리지 않아야 크롤러/PWA 요청이 깨지지 않는다.
 *
 * 2026-09-02 인증 방식 전환: 이메일/비밀번호 로그인으로 바뀌면서 매직 링크 PKCE 콜백
 * (`/auth/callback`)이 삭제됐다 -- `/auth/*` 하위 라우트가 더 이상 없으므로 예외 패턴에서 뺐다.
 */
const PUBLIC_PATH_PATTERNS = [
  /^\/login(\/.*)?$/,
  /^\/api(\/.*)?$/,
  /^\/robots\.txt$/,
  /^\/manifest\.json$/,
  /^\/sitemap\.xml$/,
];

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (PUBLIC_PATH_PATTERNS.some((pattern) => pattern.test(pathname))) {
    return NextResponse.next();
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const publishableKey = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
  if (!url || !publishableKey) {
    // 이 앱의 유일한 목적은 단일 운영자 세션 게이트다 -- 설정 누락 시 통과시키면(fail-open) 누구나
    // 인증 없이 대시보드를 볼 수 있게 된다. 가용성보다 안전을 택해 로그인으로 리다이렉트한다
    // (fail-closed). 실제 dispatch 권한은 어차피 `/api/dispatch`가 같은 환경변수 부재를 500으로
    // 별도 거부한다.
    return NextResponse.redirect(new URL("/login", request.url));
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

  let user: { id: string } | null = null;
  try {
    ({
      data: { user },
    } = await supabase.auth.getUser());
  } catch (error) {
    // getUser()는 문서상 예외를 던지지 않지만(네트워크/서비스 오류도 {data,error}로 반환), 클라이언트
    // 내부 오류까지 완전히 배제할 수는 없다 -- 여기서 크래시하면 이 matcher에 걸리는 모든 요청이
    // 죽으므로, 안전한 쪽(재로그인 유도)으로 넘어간다.
    console.error(`proxy getUser threw: ${error instanceof Error ? error.message : "unknown error"}`);
    return NextResponse.redirect(new URL("/login", request.url));
  }

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
