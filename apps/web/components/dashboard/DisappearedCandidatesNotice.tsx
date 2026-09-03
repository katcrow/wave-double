import type { DisappearedCandidateViewModel } from "@/lib/disappeared-candidates";
import { getStrategyLabel } from "@/lib/strategy-labels";

/**
 * Story 2.8: 후보 모집단 자체에서 빠진(ticker가 현재 candidates에 없는) 종목을 "모집단 이탈"/
 * "수집 실패"로 구분해 보여준다. 카드 그리드와 별개 영역이며, 소멸(vanished, 카드에 남아있는
 * 종목)과 혼동되지 않도록 다른 문구를 쓴다.
 */
export default function DisappearedCandidatesNotice({
  candidates,
}: {
  candidates: DisappearedCandidateViewModel[];
}) {
  if (candidates.length === 0) return null;

  return (
    <section
      className="disappeared-candidates"
      aria-labelledby="disappeared-candidates-heading"
    >
      <h2 id="disappeared-candidates-heading" className="disappeared-candidates__heading">
        오늘 목록에서 빠진 종목
      </h2>
      <ul className="disappeared-candidates__list" role="list">
        {candidates.map((candidate) => (
          <li key={candidate.ticker} className="disappeared-candidates__item">
            <span className="disappeared-candidates__name">{candidate.displayName}</span>
            <span className="disappeared-candidates__ticker">{candidate.ticker}</span>
            <span className="disappeared-candidates__reason">{candidate.reasonLabel}</span>
            {candidate.strategies.length > 0 && (
              <span className="disappeared-candidates__strategies">
                이전 태그: {candidate.strategies.map((s) => getStrategyLabel(s) ?? `전략 ${s}`).join(", ")}
              </span>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
