import type { CandidateCardViewModel } from "@/lib/candidate-cards";
import StrategyTagList from "./StrategyTagList";

/**
 * UX-DR4/UX-DR16: 카드 1개 -- 종목명·코드, 전략 태그, (있다면) 수급 부분결측 단서.
 * Never: 카드 전체 클릭 상호작용(근거 패널, Story 4.6), 당일 가격/등락률, 장중 소멸 표시(Story 2.8)는
 * 이번 스토리 범위가 아니다.
 */
export default function CandidateCard({ candidate }: { candidate: CandidateCardViewModel }) {
  return (
    <li className="candidate-card">
      <div className="candidate-card__header">
        <h2 className="candidate-card__name">{candidate.displayName}</h2>
        <span className="candidate-card__ticker">{candidate.ticker}</span>
      </div>
      <StrategyTagList
        visibleStrategies={candidate.visibleStrategies}
        hiddenCount={candidate.hiddenStrategyCount}
      />
      {candidate.supplyPartialMissing && (
        <p className="candidate-card__notice">수급 일부 미수집</p>
      )}
    </li>
  );
}
