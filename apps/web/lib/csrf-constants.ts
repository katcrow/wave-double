/**
 * Story 1.10: `/api/dispatch`의 SameSite=Strict double-submit CSRF 방어에 쓰는 이름 상수.
 * 클라이언트(DataTrustBar)와 서버(proxy.ts, api/dispatch/route.ts)가 같은 이름을 공유해야 하므로
 * node:crypto 등 서버 전용 API에 의존하지 않는 별도 파일로 분리한다(클라이언트 번들에도 안전).
 */
export const CSRF_COOKIE_NAME = "wd_csrf";
export const CSRF_HEADER_NAME = "x-wd-csrf";
