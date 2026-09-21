import {
  evidenceSlotLabel,
  formatEvidenceDateTime,
  formatEvidenceSummary,
  normalizeCandidateEvidence,
} from "@/lib/candidate-evidence";
import {
  EVIDENCE_METRICS,
  formatEvidenceMetricValue,
  formatEvidenceStatusLabel,
  getEvidenceMetricTone,
  getEvidenceTradingDay,
} from "@/lib/candidate-evidence-view";
import type {
  CandidateEvidenceRpcRow,
} from "@/lib/dashboard-types";
import { toneClassName } from "@/lib/value-tone";

interface CandidateEvidencePanelProps {
  id: string;
  evidence?: CandidateEvidenceRpcRow;
  fetchFailed: boolean;
  open: boolean;
}

export default function CandidateEvidencePanel({
  id,
  evidence,
  fetchFailed,
  open,
}: CandidateEvidencePanelProps) {
  const viewModel = normalizeCandidateEvidence(evidence);

  return (
    <section
      id={id}
      className="candidate-evidence-panel"
      aria-label="후보 근거 패널"
      hidden={!open}
    >
      <header className="candidate-evidence-panel__header">
        <div>
          <p className="candidate-evidence-panel__eyebrow">3일 수급 근거 · 종가·등락률 수정주가</p>
          <p className="candidate-evidence-panel__meta">
            원천: <span>{fetchFailed ? "확인 불가" : viewModel.sourceLabel}</span>
            <span aria-hidden="true"> · </span>
            생성: <span>{fetchFailed ? "시각 미상" : formatEvidenceDateTime(viewModel.collectedAt)}</span>
          </p>
        </div>
        {!fetchFailed && evidence && (viewModel.missingSlotCount > 0 || viewModel.pendingSlotCount > 0) && (
          <span
            className={
              viewModel.missingSlotCount > 0
                ? "candidate-evidence-panel__summary"
                : "candidate-evidence-panel__summary candidate-evidence-panel__summary--pending"
            }
            role="status"
          >
            {formatEvidenceSummary(viewModel.missingSlots, viewModel.pendingSlots)}
          </span>
        )}
      </header>

      {fetchFailed ? (
        <p className="candidate-evidence-panel__state" role="alert">
          근거 데이터를 불러오지 못했습니다.
        </p>
      ) : !evidence ? (
        <p className="candidate-evidence-panel__state" role="status">
          근거 데이터가 없습니다.
        </p>
      ) : (
        <>
          <div className="candidate-evidence-panel__table-wrap">
            <table className="candidate-evidence-table">
              <caption className="sr-only">후보의 최근 3거래일 가격 및 투자자별 순매수</caption>
              <thead>
                <tr>
                  <th scope="col">일자</th>
                  {EVIDENCE_METRICS.map((metric) => (
                    <th scope="col" key={metric.key}>{metric.label}({metric.unit})</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {viewModel.slots.map(({ slot, row, status }) => (
                  <tr
                    key={slot}
                    className={
                      row === null || status === "missing"
                        ? "candidate-evidence-table__row candidate-evidence-table__row--missing"
                        : status === "pending"
                          ? "candidate-evidence-table__row candidate-evidence-table__row--pending"
                          : "candidate-evidence-table__row"
                    }
                  >
                    <th scope="row">
                      <span className="candidate-evidence-table__slot">{evidenceSlotLabel(slot)}</span>
                      <span className="candidate-evidence-table__day">
                        {getEvidenceTradingDay(row) ?? "거래일 없음"}
                      </span>
                      <span className="candidate-evidence-table__status">
                        {formatEvidenceStatusLabel(status)}
                      </span>
                    </th>
                    {EVIDENCE_METRICS.map((metric) => (
                      <td
                        key={metric.key}
                        aria-label={`${metric.label} ${formatEvidenceMetricValue(row, status, metric.key)}`}
                      >
                        <span className={toneClassName(getEvidenceMetricTone(row, status, metric.key))}>
                          {formatEvidenceMetricValue(row, status, metric.key)}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="candidate-evidence-card-list" aria-label="거래일별 근거">
            {viewModel.slots.map(({ slot, row, status }) => (
              <article
                key={slot}
                aria-labelledby={`${id}-${slot}-heading`}
                className={
                  status === "missing"
                    ? "candidate-evidence-card candidate-evidence-card--missing"
                    : status === "pending"
                      ? "candidate-evidence-card candidate-evidence-card--pending"
                      : "candidate-evidence-card"
                }
              >
                <header className="candidate-evidence-card__header">
                  <h3 id={`${id}-${slot}-heading`} className="sr-only">
                    {evidenceSlotLabel(slot)} {getEvidenceTradingDay(row) ?? "거래일 없음"} 근거
                  </h3>
                  <div className="candidate-evidence-card__date">
                    <span className="candidate-evidence-card__slot">{evidenceSlotLabel(slot)}</span>
                    <span className="candidate-evidence-card__date-label">기준일</span>
                    {getEvidenceTradingDay(row) ? (
                      <time dateTime={getEvidenceTradingDay(row) ?? undefined}>
                        {getEvidenceTradingDay(row)}
                      </time>
                    ) : (
                      <span>거래일 없음</span>
                    )}
                  </div>
                  <span className="candidate-evidence-card__status">{formatEvidenceStatusLabel(status)}</span>
                </header>
                <dl className="candidate-evidence-card__metrics">
                  {EVIDENCE_METRICS.map((metric) => (
                    <div className="candidate-evidence-card__metric" key={metric.key}>
                      <dt>{metric.label}({metric.unit})</dt>
                      <dd className={toneClassName(getEvidenceMetricTone(row, status, metric.key))}>
                        {formatEvidenceMetricValue(row, status, metric.key)}
                      </dd>
                    </div>
                  ))}
                </dl>
              </article>
            ))}
          </div>
        </>
      )}
    </section>
  );
}
