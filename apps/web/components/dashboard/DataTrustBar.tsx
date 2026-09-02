import type { DashboardSnapshot } from "@/lib/dashboard-types";
import { deriveTrustBarState } from "@/lib/trust-bar";

/**
 * Story 1.9 I/O 매트릭스 6개 상태(스냅샷 없음/정상 발행/실패/부분성공/휴장일 스킵/stale)를 렌더링한다.
 * 상태 판정 로직은 `lib/trust-bar.ts`의 순수 함수로 분리해 단위 테스트한다.
 */
export default function DataTrustBar({ snapshot }: { snapshot: DashboardSnapshot }) {
  const { statusLine, candidateCount, triggerLabel } = deriveTrustBarState(snapshot);

  return (
    <div className="data-trust-bar" role="status" aria-live="polite">
      <div className="data-trust-bar__status">
        <span className="data-trust-bar__label">데이터 신뢰도</span>
        <span className="data-trust-bar__value">{statusLine}</span>
        <span className="data-trust-bar__meta">
          {triggerLabel ? `트리거 · ${triggerLabel}` : "트리거 정보 없음"}
          {typeof candidateCount === "number" && ` · 참고 · 오늘 태깅 후보 ${candidateCount}건`}
        </span>
      </div>
      <button
        type="button"
        className="data-trust-bar__manual-run"
        disabled
        title="Story 1.10에서 활성화"
      >
        수동 실행 · Story 1.10에서 활성화
      </button>
    </div>
  );
}
