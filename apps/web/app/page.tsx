import CandidateCard from "@/components/dashboard/CandidateCard";
import DataTrustBar from "@/components/dashboard/DataTrustBar";
import DisappearedCandidatesNotice from "@/components/dashboard/DisappearedCandidatesNotice";
import NoticeBanner from "@/components/dashboard/NoticeBanner";
import { buildCandidateCardViewModels } from "@/lib/candidate-cards";
import { isCandidateEvidenceRpcRow } from "@/lib/candidate-evidence";
import type { CandidateEvidenceRpcRow } from "@/lib/dashboard-types";
import { isIntradaySnapshot } from "@/lib/dashboard-types";
import type { DashboardSnapshot, DisappearedCandidateRow, TodayCandidateCardRow } from "@/lib/dashboard-types";
import { buildDisappearedCandidateViewModels } from "@/lib/disappeared-candidates";
import { getSupabaseBrowserClient } from "@/lib/supabase-browser";
import { deriveTrustBarState } from "@/lib/trust-bar";

// get_dashboard_snapshot()은 매 요청 최신 배치 상태를 읽어야 하므로 정적 캐싱을 막는다.
export const dynamic = "force-dynamic";

export default async function HomePage() {
  const supabase = getSupabaseBrowserClient();
  const { data, error } = await supabase.rpc("get_dashboard_snapshot");

  if (error) {
    return (
      <section aria-labelledby="today-candidates-heading">
        <h1 id="today-candidates-heading">오늘의 후보</h1>
        <p role="alert">대시보드 데이터를 불러오지 못했습니다: {error.message}</p>
      </section>
    );
  }

  const snapshot = data as DashboardSnapshot;
  const candidateCount = snapshot.complete_snapshot?.sections.candidates.candidate_count;
  const { notice } = deriveTrustBarState(snapshot);

  // Story 2.7: complete_snapshot이 있을 때만 카드 원천 RPC를 호출한다. RPC 실패는 빈 상태로
  // 폴백하되(NoticeBanner가 이미 배치 실패를 우선 노출하므로 추가 에러 UI 분기는 두지 않는다)
  // 실패 자체는 로깅하고, 실패 케이스에서는 "참고용 · 오늘 태깅 후보 N건" 텍스트를 숨겨
  // 진짜 0건 케이스와 RPC 실패 케이스가 같은 문구로 섞이지 않게 한다.
  let candidateCards: ReturnType<typeof buildCandidateCardViewModels> = [];
  let candidateCardsFetchFailed = false;
  let candidateEvidenceById = new Map<string, CandidateEvidenceRpcRow>();
  let candidateEvidenceFetchFailed = false;
  if (snapshot.complete_snapshot) {
    const { data: cardRows, error: cardError } = await supabase.rpc("get_today_candidate_cards", {
      p_run_id: snapshot.complete_snapshot.run_id,
    });
    if (cardError) {
      candidateCardsFetchFailed = true;
      console.error("get_today_candidate_cards failed", cardError);
    } else if (Array.isArray(cardRows)) {
      candidateCards = buildCandidateCardViewModels(cardRows as TodayCandidateCardRow[]);
    } else {
      candidateCardsFetchFailed = true;
      console.error("unexpected get_today_candidate_cards shape", cardRows);
    }

    const { data: evidenceRows, error: evidenceError } = await supabase.rpc("get_candidate_evidence", {
      p_run_id: snapshot.complete_snapshot.run_id,
    });
    if (evidenceError) {
      candidateEvidenceFetchFailed = true;
      console.error("get_candidate_evidence failed", evidenceError);
    } else if (Array.isArray(evidenceRows) && evidenceRows.every(isCandidateEvidenceRpcRow)) {
      candidateEvidenceById = new Map(
        (evidenceRows as CandidateEvidenceRpcRow[]).map((row) => [row.candidate_id, row])
      );
    } else {
      candidateEvidenceFetchFailed = true;
      console.error("unexpected get_candidate_evidence shape", evidenceRows);
    }
  }

  // Story 2.8: get_today_candidate_cards와 같은 조건(complete_snapshot 존재 시)으로 호출한다.
  // 실패는 candidateCardsFetchFailed와 달리 NoticeBanner를 띄우지 않고 로깅 후 조용히 생략한다
  // (신규 기능 실패가 기존 카드 렌더를 막지 않게 하기 위함).
  let disappearedCandidates: ReturnType<typeof buildDisappearedCandidateViewModels> = [];
  if (snapshot.complete_snapshot) {
    const { data: disappearedRows, error: disappearedError } = await supabase.rpc(
      "get_today_disappeared_candidates",
      { p_run_id: snapshot.complete_snapshot.run_id }
    );
    if (disappearedError) {
      console.error("get_today_disappeared_candidates failed", disappearedError);
    } else if (Array.isArray(disappearedRows)) {
      disappearedCandidates = buildDisappearedCandidateViewModels(
        disappearedRows as DisappearedCandidateRow[]
      );
    } else {
      console.error("unexpected get_today_disappeared_candidates shape", disappearedRows);
    }
  }

  // UJ-2: 장중 배치(batch_kind !== 'close')로 만들어진 complete_snapshot에는 최종 추천이 아님을
  // 항상 고정 표시한다(trust bar의 상태 문구가 실패/부분성공/stale 알림으로 덮여도 이 라벨은 유지).
  const isIntraday = isIntradaySnapshot(snapshot);

  return (
    <section aria-labelledby="today-candidates-heading">
      <header>
        <h1 id="today-candidates-heading">오늘의 후보</h1>
      </header>

      <DataTrustBar snapshot={snapshot} />
      {isIntraday && (
        <p className="intraday-label" role="status">
          장중 참고 · 최종 추천 미확정
        </p>
      )}
      <NoticeBanner message={notice} />
      {candidateCardsFetchFailed && (
        <NoticeBanner message="오늘의 후보 카드를 불러오지 못했습니다." />
      )}

      {candidateCards.length > 0 ? (
        <ul className="candidate-card-grid" role="list">
          {candidateCards.map((candidate) => (
            <CandidateCard
              key={candidate.candidateId}
              candidate={candidate}
              evidence={candidateEvidenceById.get(candidate.candidateId)}
              evidenceFetchFailed={candidateEvidenceFetchFailed}
            />
          ))}
        </ul>
      ) : (
        <div className="empty-state">
          <p>오늘 태깅된 후보가 없습니다.</p>
          <p>조건검색 결과 · 전략 시그널 기준으로 후보가 태깅됩니다.</p>
          {!candidateCardsFetchFailed && typeof candidateCount === "number" && (
            <p className="reference-text">
              참고용 · 오늘 태깅 후보 {candidateCount}건
            </p>
          )}
        </div>
      )}

      <DisappearedCandidatesNotice candidates={disappearedCandidates} />
    </section>
  );
}
