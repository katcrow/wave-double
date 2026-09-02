import DataTrustBar from "@/components/dashboard/DataTrustBar";
import NoticeBanner from "@/components/dashboard/NoticeBanner";
import type { DashboardSnapshot } from "@/lib/dashboard-types";
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

  return (
    <section aria-labelledby="today-candidates-heading">
      <header>
        <h1 id="today-candidates-heading">오늘의 후보</h1>
      </header>

      <DataTrustBar snapshot={snapshot} />
      <NoticeBanner message={notice} />

      {/*
        Never: Epic 1은 태깅이 없어 `/`는 항상 빈 상태다. candidate_count는 참고 텍스트로만
        노출하고, 후보 카드/근거 패널/시장수급 패널은 만들지 않는다.
      */}
      <div className="empty-state">
        <p>오늘 태깅된 후보가 없습니다.</p>
        <p>조건검색 결과 · 전략 시그널 기준으로 후보가 태깅됩니다.</p>
        {typeof candidateCount === "number" && (
          <p className="reference-text">
            참고용 · 오늘 태깅 후보 {candidateCount}건 (후보 카드 화면은 다음 스토리에서 제공됩니다.)
          </p>
        )}
      </div>
    </section>
  );
}
