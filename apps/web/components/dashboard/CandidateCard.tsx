import type { CandidateCardViewModel } from "@/lib/candidate-cards";
import { getStrategyLabel } from "@/lib/strategy-labels";
import StrategyTagList from "./StrategyTagList";

/**
 * UX-DR4/UX-DR16: 카드 1개 -- 종목명·코드, 전략 태그, (있다면) 수급 부분결측 단서.
 * Story 2.8: isFullyVanished(active 태그 0건 + vanished 태그만 존재)면 "소멸" 배지를 표시하되
 * 카드 자체는 목록에서 제외하지 않는다. 부분 재태깅(active + vanished 혼재)이면 소멸된 전략을
 * 별도 문구로 함께 표시한다(모집단 이탈/수집 실패는 DisappearedCandidatesNotice가 별도 렌더).
 * Never: 카드 전체 클릭 상호작용(근거 패널, Story 4.6), 당일 가격/등락률은 이번 스토리 범위가 아니다.
 */
export default function CandidateCard({ candidate }: { candidate: CandidateCardViewModel }) {
  return (
    <li
      className={
        candidate.isFullyVanished ? "candidate-card candidate-card--vanished" : "candidate-card"
      }
    >
      <div className="candidate-card__header">
        <h2 className="candidate-card__name">{candidate.displayName}</h2>
        <span className="candidate-card__ticker">{candidate.ticker}</span>
      </div>
      {candidate.isFullyVanished && (
        <p className="candidate-card__badge candidate-card__badge--vanished">시그널 소멸</p>
      )}
      <StrategyTagList
        visibleStrategies={candidate.visibleStrategies}
        hiddenCount={candidate.hiddenStrategyCount}
      />
      {!candidate.isFullyVanished && candidate.vanishedStrategies.length > 0 && (
        <p className="candidate-card__notice candidate-card__notice--vanished">
          소멸: {candidate.vanishedStrategies.map((s) => getStrategyLabel(s) ?? `전략 ${s}`).join(", ")}
        </p>
      )}
      {candidate.supplyPartialMissing && (
        <p className="candidate-card__notice">수급 일부 미수집</p>
      )}
    </li>
  );
}
