const SKELETON_COUNT = 4;

/** EXPERIENCE.md: 로딩은 실제 카드와 같은 높이의 skeleton 3~6개, 전체 빈 검정 화면 금지. */
export default function Loading() {
  return (
    <section aria-busy="true">
      <p className="sr-only" role="status" aria-live="polite">
        데이터를 불러오는 중입니다.
      </p>
      <div className="skeleton-list">
        {Array.from({ length: SKELETON_COUNT }).map((_, index) => (
          <div key={index} className="skeleton-card" aria-hidden="true" />
        ))}
      </div>
    </section>
  );
}
