import type { TopTradingCandidateViewModel } from "@/lib/top-trading-candidates";
import { MAX_VISIBLE_THEMES } from "@/lib/candidate-themes";

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
          <h2 id="top-trading-candidates-heading">거래대금 상위 후보</h2>
          <p className="top-trading-candidates__description">오늘 후보 모집단 중 일간 거래대금 기준</p>
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
            <dl className="top-trading-candidates__metrics">
              <div className="top-trading-candidates__metric">
                <dt>거래대금</dt>
                <dd>{candidate.formattedTradingValue}억원</dd>
              </div>
              <div className="top-trading-candidates__metric">
                <dt>당일 상승률</dt>
                <dd>{candidate.formattedChangePct}</dd>
              </div>
              <div className="top-trading-candidates__metric top-trading-candidates__metric--themes">
                <dt>테마</dt>
                <dd>
                  {candidate.themes.length === 0
                    ? "미확인"
                    : candidate.themes.slice(0, MAX_VISIBLE_THEMES).map((theme, index) => (
                        <span className="top-trading-candidates__theme" key={theme.themeCode}>
                          {index > 0 && " · "}{theme.themeName} {theme.formattedAverageChangePct}
                        </span>
                      ))}
                  {candidate.themes.length > MAX_VISIBLE_THEMES && ` +${candidate.themes.length - MAX_VISIBLE_THEMES}`}
                </dd>
              </div>
              <div className="top-trading-candidates__metric">
                <dt>프로그램 순매수금액</dt>
                <dd>{candidate.formattedProgramBuyValue}{candidate.programBuyValue === null ? "" : "억원"}</dd>
              </div>
            </dl>
          </li>
        ))}
      </ol>
    </section>
  );
}
