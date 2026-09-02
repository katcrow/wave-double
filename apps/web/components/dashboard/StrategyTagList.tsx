import Link from "next/link";
import { getStrategyLabel } from "@/lib/strategy-labels";

/**
 * UX-DR7: 전략 태그 배지 목록. 태그 클릭은 필터링이 아니라 `/strategies/[strategy]`
 * 자리표시자 페이지로 이동하는 보조 액션이다(Never: 카드 전체 클릭 근거 패널은 Story 4.6 범위).
 * "+N" 접힘은 candidate-cards.ts의 순수 함수가 이미 계산해 넘긴 값을 그대로 렌더링만 한다.
 */
export default function StrategyTagList({
  visibleStrategies,
  hiddenCount,
}: {
  visibleStrategies: string[];
  hiddenCount: number;
}) {
  return (
    <ul className="strategy-tag-list" aria-label="전략 태그">
      {visibleStrategies.map((strategy) => (
        <li key={strategy}>
          <Link href={`/strategies/${strategy}`} className="strategy-tag">
            {getStrategyLabel(strategy) ?? `전략 ${strategy}`}
          </Link>
        </li>
      ))}
      {hiddenCount > 0 && (
        <li className="strategy-tag strategy-tag--more" aria-label={`추가 전략 태그 ${hiddenCount}건`}>
          +{hiddenCount}
        </li>
      )}
    </ul>
  );
}
