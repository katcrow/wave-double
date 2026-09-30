import type { TopTradingCandidateViewModel } from "@/lib/top-trading-candidates";

export default function TopTradingCandidates({
  candidates,
}: {
  candidates: TopTradingCandidateViewModel[];
}) {
  if (candidates.length === 0) return null;

  return (
    <section className="top-trading-candidates" aria-labelledby="top-trading-candidates-heading">
      <header className="top-trading-candidates__header">
        <div>
          <p className="top-trading-candidates__eyebrow">참고 순위</p>
          <h2 id="top-trading-candidates-heading">거래대금 상위 태깅 후보</h2>
          <p className="top-trading-candidates__description">오늘 태깅된 전체 후보 중 일간 거래대금 기준</p>
        </div>
      </header>
      <ol className="top-trading-candidates__list">
        {candidates.map((candidate) => (
          <li className="top-trading-candidates__item" key={candidate.candidateId}>
            <span className="top-trading-candidates__rank" aria-label={`${candidate.rank}위`}>
              {candidate.rank}
            </span>
            <div className="top-trading-candidates__identity">
              <p className="top-trading-candidates__name">{candidate.displayName}</p>
              <p className="top-trading-candidates__ticker">{candidate.ticker}</p>
            </div>
            <dl className="top-trading-candidates__value">
              <dt>일간 거래대금</dt>
              <dd>{candidate.formattedTradingValue}원</dd>
            </dl>
          </li>
        ))}
      </ol>
    </section>
  );
}
