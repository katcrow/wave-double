"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import {
  BIAS_DATE_QUERY_KEY,
  formatBiasCount,
  type BiasDiagnosticRpcRow,
} from "@/lib/bias-diagnostic";
import {
  getSourceLabel,
  getSourceScopeDescription,
  SOURCE_QUERY_KEY,
  type SourceFilter,
} from "@/lib/source-filter";

interface BiasDiagnosticPanelProps {
  row: BiasDiagnosticRpcRow | null;
  fetchFailed: boolean;
  selectedDate: string;
  selectedSource: SourceFilter;
}

const METRICS = [
  {
    key: "candidate_population_signal_count",
    label: "후보 모집단 ∩ 전략 시그널",
    description: "후보 모집단에 포함된 A~F 전략 시그널 종목 수입니다.",
  },
  {
    key: "backtest_universe_signal_count",
    label: "백테스트 유니버스 ∩ 전략 시그널",
    description: "백테스트 유니버스에서 성립한 A~F 전략 시그널 종목 수입니다.",
  },
  {
    key: "intersection_count",
    label: "교집합",
    description: "후보 모집단과 백테스트 유니버스에 모두 포함된 시그널 종목 수입니다.",
  },
  {
    key: "missed_opportunity_count",
    label: "기회 누락",
    description: "후보 모집단에서 관측되지 않은 백테스트 기회 수입니다. 성과 실패 원인을 뜻하지는 않습니다.",
  },
] as const satisfies ReadonlyArray<{
  key: keyof Pick<BiasDiagnosticRpcRow, "candidate_population_signal_count" | "backtest_universe_signal_count" | "intersection_count" | "missed_opportunity_count">;
  label: string;
  description: string;
}>;

export default function BiasDiagnosticPanel({ row, fetchFailed, selectedDate, selectedSource }: BiasDiagnosticPanelProps) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();

  function handleDateSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const value = String(formData.get(BIAS_DATE_QUERY_KEY) ?? "").trim();
    const nextParams = new URLSearchParams(searchParams.toString());
    if (value) nextParams.set(BIAS_DATE_QUERY_KEY, value);
    else nextParams.delete(BIAS_DATE_QUERY_KEY);
    const query = nextParams.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return (
    <section className="bias-diagnostic" aria-labelledby="bias-diagnostic-heading">
      <header className="bias-diagnostic__header">
        <div>
          <p className="bias-diagnostic__eyebrow">모집단 편향 참고 정보</p>
          <h2 id="bias-diagnostic-heading">Bias diagnostic</h2>
          <p className="bias-diagnostic__description">
            종가 배치가 저장한 A~F 전략 시그널 합집합을 기준으로 두 모집단의 기회 차이를 확인합니다. 성과 실패 원인으로 단정하지 않습니다.
          </p>
        </div>
        <p className="bias-diagnostic__scope" role="status">기준일: {selectedDate} · {getSourceLabel(selectedSource)}</p>
      </header>

      <form key={selectedDate} className="bias-diagnostic__filters" method="get" action={pathname} onSubmit={handleDateSubmit}>
        <div className="bias-diagnostic__filter-field">
          <label htmlFor="bias-date-filter">편향 진단 날짜</label>
          <input id="bias-date-filter" name={BIAS_DATE_QUERY_KEY} type="date" defaultValue={selectedDate} required />
        </div>
        {Array.from(searchParams.entries()).filter(([key]) => key !== BIAS_DATE_QUERY_KEY && key !== SOURCE_QUERY_KEY).map(([key, value], index) => (
          <input key={`${key}-${index}`} type="hidden" name={key} value={value} />
        ))}
        {selectedSource && <input type="hidden" name={SOURCE_QUERY_KEY} value={selectedSource} />}
        <div className="bias-diagnostic__filter-actions">
          <button type="submit">날짜 적용</button>
        </div>
      </form>

      {fetchFailed ? (
        <p className="bias-diagnostic__state" role="alert">편향 진단 데이터를 불러오지 못했습니다</p>
      ) : !row || !row.has_data ? (
        <p className="bias-diagnostic__state" role="status">이 날짜의 편향 데이터가 없습니다</p>
      ) : (
        <>
          <p className="bias-diagnostic__source-note">{getSourceScopeDescription(selectedSource)}</p>
          <div className="bias-diagnostic__grid" role="list" aria-label={`${selectedDate} ${getSourceLabel(selectedSource)} Bias diagnostic 수치`}>
            {METRICS.map((metric) => (
              <article className="bias-diagnostic__metric" role="listitem" key={metric.key}>
                <h3>{metric.label}</h3>
                <p className="bias-diagnostic__value">{formatBiasCount(row[metric.key])}</p>
                <p className="bias-diagnostic__metric-description">{metric.description}</p>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
