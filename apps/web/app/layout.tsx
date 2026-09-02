import type { Metadata } from "next";
import AppShell from "@/components/app-shell/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  title: "wave-double",
  description: "매수후보 추천 대시보드",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css"
        />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
