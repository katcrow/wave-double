"use client";

import { useState } from "react";

/**
 * DESIGN.md "Toast / notice": 자동 배치 실패/부분성공/stale을 비차단 알림으로 표시한다.
 * 폴백 원천 알림은 스펙 Never 절에 따라 이번 스토리에서 만들지 않는다(원천 필드가 API에 없음).
 */
export default function NoticeBanner({ message }: { message: string | null }) {
  const [dismissed, setDismissed] = useState(false);

  if (!message || dismissed) return null;

  return (
    <div className="notice-banner" role="status" aria-live="polite">
      <span>{message}</span>
      <button
        type="button"
        className="notice-banner__dismiss"
        aria-label="알림 닫기"
        onClick={() => setDismissed(true)}
      >
        ×
      </button>
    </div>
  );
}
