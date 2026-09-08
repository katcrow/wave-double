"use client";

import { useState } from "react";
import type { CandidateCardViewModel } from "@/lib/candidate-cards";
import type { CandidateEvidenceRpcRow } from "@/lib/dashboard-types";
import { getStrategyLabel } from "@/lib/strategy-labels";
import CandidateEvidencePanel from "./CandidateEvidencePanel";
import StrategyTagList from "./StrategyTagList";

/**
 * UX-DR4/UX-DR16: 카드 1개 -- 종목명·코드, 전략 태그, (있다면) 수급 부분결측 단서.
 * Story 2.8: isFullyVanished(active 태그 0건 + vanished 태그만 존재)면 "소멸" 배지를 표시하되
 * 카드 자체는 목록에서 제외하지 않는다. 부분 재태깅(active + vanished 혼재)이면 소멸된 전략을
 * 별도 문구로 함께 표시한다(모집단 이탈/수집 실패는 DisappearedCandidatesNotice가 별도 렌더).
 * Story 4.6: 카드 헤더의 접근 가능한 토글로 근거 패널을 열고 닫는다. 전략 태그 링크는
 * 토글 바깥에 두어 기존 보조 액션을 유지한다.
 */
export default function CandidateCard({
  candidate,
  evidence,
  evidenceFetchFailed = false,
}: {
  candidate: CandidateCardViewModel;
  evidence?: CandidateEvidenceRpcRow;
  evidenceFetchFailed?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const panelId = `candidate-evidence-${candidate.candidateId}`;

  return (
    <li
      className={
        [
          "candidate-card",
          candidate.isFullyVanished && "candidate-card--vanished",
          open && "candidate-card--expanded",
        ]
          .filter(Boolean)
          .join(" ")
      }
    >
      <button
        type="button"
        className="candidate-card__toggle"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={`${candidate.displayName} 근거 패널 ${open ? "닫기" : "열기"}`}
        onClick={() => setOpen((current) => !current)}
      >
        <span className="candidate-card__header">
          <span className="candidate-card__name">{candidate.displayName}</span>
          <span className="candidate-card__ticker">{candidate.ticker}</span>
        </span>
        <span className="candidate-card__toggle-hint">{open ? "근거 닫기" : "근거 보기"}</span>
      </button>
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
      <CandidateEvidencePanel
        id={panelId}
        evidence={evidence}
        fetchFailed={evidenceFetchFailed}
        open={open}
      />
    </li>
  );
}
