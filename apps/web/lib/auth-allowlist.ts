/**
 * Story 1.10 (AD-7): dispatch 권한의 유일한 권위인 server-side subject allowlist.
 * `OPERATOR_ALLOWLIST`는 쉼표로 구분된 이메일 목록이다(server-only 환경변수, NEXT_PUBLIC_* 아님).
 */
export function isAllowedOperator(subjectEmail: string | null | undefined): boolean {
  if (!subjectEmail) return false;
  const normalized = subjectEmail.trim().toLowerCase();
  if (!normalized) return false;

  const raw = process.env.OPERATOR_ALLOWLIST ?? "";
  const allowed = raw
    .split(",")
    .map((entry) => entry.trim().toLowerCase())
    .filter((entry) => entry.length > 0);

  return allowed.includes(normalized);
}
