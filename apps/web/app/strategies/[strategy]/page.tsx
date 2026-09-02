import { notFound } from "next/navigation";
import { getStrategyLabel } from "@/lib/strategy-labels";

// Never: 실제 전략 설명/성과 콘텐츠는 이번 스토리에서 채우지 않는다(자리표시자만, /tracking과 동일 패턴).

export default async function StrategyPage({
  params,
}: {
  params: Promise<{ strategy: string }>;
}) {
  const { strategy } = await params;
  const label = getStrategyLabel(strategy);
  if (!label) notFound();

  return (
    <section aria-labelledby="strategy-heading">
      <h1 id="strategy-heading">{label}</h1>
      <p>{label} 설명/성과 준비 중입니다.</p>
    </section>
  );
}
