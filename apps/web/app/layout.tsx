import type { Metadata } from "next";
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
      <body>{children}</body>
    </html>
  );
}
