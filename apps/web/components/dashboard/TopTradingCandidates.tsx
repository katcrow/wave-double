"use client";

import { useState } from "react";
import type { TopTradingCandidateViewModel } from "@/lib/top-trading-candidates";
import { MAX_VISIBLE_THEMES } from "@/lib/candidate-themes";

type TopTradingMode = "excluded" | "all";

const MODE_OPTIONS: ReadonlyArray<{ mode: TopTradingMode; label: string }> = [
  { mode: "excluded", label: "삼성전자·SK하이닉스 제외" },
  { mode: "all", label: "전체" },
];

/**
 * 서버가 미리 조회한 '제외'/'전체' 두 목록을 토글로 전환한다. 토글은 다시 조회하지 않으며,
 * 선택은 저장하지 않아 새로 고치면 기본값 '제외'로 시작한다.
 */
export default function TopTradingCandidates({
  excludedCandidates,
  allCandidates,
}: {
  excludedCandidates: TopTradingCandidateViewModel[];
  allCandidates: TopTradingCandidateViewModel[];
}) {
  const [mode, setMode] = useState<TopTradingMode>("excluded");

  if (excludedCandidates.length === 0 && allCandidates.length === 0) return null;

  const candidates = mode === "excluded" ? excludedCandidates : allCandidates;

  return (
    <section className="top-trading-candidates" aria-labelledby="top-trading-candidates-heading">
      <header className="top-trading-candidates__header">
        <div>
          <p className="top-trading-candidates__eyebrow">참고 순위</p>
          <h2 id="top-trading-candidates-heading">거래대금 상위 후보</h2>
          <p className="top-trading-candidates__description">오늘 후보 모집단 중 일간 거래대금 기준</p>
        </div>
        <div className="top-trading-candidates__toggle-group" role="group" aria-label="대형주 포함 여부">
          {MODE_OPTIONS.map((option) => (
            <button
              key={option.mode}
              type="button"
              className="top-trading-candidates__toggle"
              aria-pressed={mode === option.mode}
              onClick={() => setMode(option.mode)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </header>
      {candidates.length === 0 ? (
        <p className="top-trading-candidates__empty">표시할 후보가 없습니다</p>
      ) : (
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
      )}
    </section>
  );
}
