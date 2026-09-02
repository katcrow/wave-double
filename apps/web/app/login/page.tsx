"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { getSupabaseAuthBrowserClient } from "@/lib/supabase-browser-auth";

/**
 * Story 1.10 (AD-7), 2026-09-02 인증 방식 전환: Supabase Auth 이메일/비밀번호 로그인.
 * 사전 등록된 단일 슈퍼유저 계정만 존재하며(공개 회원가입 없음), 이 폼은 회원가입을
 * 제공하지 않는다. Never: 이 스토리는 새 디자인 요건이 없다 -- 최소 기능만 구현한다.
 */
export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "signing-in" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus("signing-in");
    setErrorMessage(null);

    try {
      const supabase = getSupabaseAuthBrowserClient();
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        setStatus("error");
        setErrorMessage(error.message);
        return;
      }
      router.push("/");
      router.refresh();
    } catch (error) {
      setStatus("error");
      setErrorMessage(error instanceof Error ? error.message : "로그인에 실패했습니다.");
    }
  }

  return (
    <section aria-labelledby="login-heading">
      <h1 id="login-heading">로그인</h1>
      <p>등록된 운영자 계정으로 로그인합니다.</p>

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

        <label htmlFor="login-password">비밀번호</label>
        <input
          id="login-password"
          name="password"
          type="password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button type="submit" disabled={status === "signing-in"}>
          {status === "signing-in" ? "로그인 중..." : "로그인"}
        </button>
      </form>

      {status === "error" && <p role="alert">{errorMessage ?? "로그인에 실패했습니다."}</p>}
    </section>
  );
}
