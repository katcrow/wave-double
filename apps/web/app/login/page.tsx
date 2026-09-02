"use client";

import { useState } from "react";
import { getSupabaseAuthBrowserClient } from "@/lib/supabase-browser-auth";

/**
 * Story 1.10 (AD-7): Supabase Auth email OTP/magic link 단일 운영자 세션 요청 폼.
 * Never: 이 스토리는 새 디자인 요건이 없다 -- 최소 기능만 구현한다.
 */
export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("sending");
    setErrorMessage(null);

    try {
      const supabase = getSupabaseAuthBrowserClient();
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/auth/callback`,
        },
      });
      if (error) {
        setStatus("error");
        setErrorMessage(error.message);
        return;
      }
      setStatus("sent");
    } catch (error) {
      setStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "로그인 요청에 실패했습니다.");
    }
  }

  return (
    <section aria-labelledby="login-heading">
      <h1 id="login-heading">로그인</h1>
      <p>등록된 운영자 이메일로 매직 링크를 보냅니다.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="login-email">이메일</label>
        <input
          id="login-email"
          name="email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />
        <button type="submit" disabled={status === "sending"}>
          {status === "sending" ? "전송 중..." : "매직 링크 보내기"}
        </button>
      </form>

      {status === "sent" && <p role="status">메일함을 확인해 주세요. 매직 링크로 로그인할 수 있습니다.</p>}
      {status === "error" && <p role="alert">{errorMessage ?? "로그인 요청에 실패했습니다."}</p>}
    </section>
  );
}
