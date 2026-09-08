import {
  evidenceSlotLabel,
  formatEvidenceDateTime,
  formatEvidenceNumber,
  formatEvidenceSummary,
  formatEvidenceValue,
  normalizeCandidateEvidence,
} from "@/lib/candidate-evidence";
import type { CandidateEvidenceRpcRow } from "@/lib/dashboard-types";

interface CandidateEvidencePanelProps {
  id: string;
  evidence?: CandidateEvidenceRpcRow;
  fetchFailed: boolean;
  open: boolean;
}

const INVESTOR_COLUMNS = [
  ["foreign_net", "외인"],
  ["institution_net", "기관"],
  ["individual_net", "개인"],
  ["program_net", "프로그램"],
] as const;

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
          <p className="candidate-evidence-panel__eyebrow">3일 수급 근거</p>
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
        <div className="candidate-evidence-panel__table-wrap">
          <table className="candidate-evidence-table">
            <caption className="sr-only">후보의 최근 3거래일 가격 및 투자자별 순매수</caption>
            <thead>
              <tr>
                <th scope="col">일자</th>
                <th scope="col">종가(원)</th>
                <th scope="col">거래량(주)</th>
                <th scope="col">등락률(%)</th>
                {INVESTOR_COLUMNS.map(([, label]) => (
                  <th scope="col" key={label}>{label}(주)</th>
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
                      {row?.trading_day ?? "거래일 없음"}
                    </span>
                    <span className="candidate-evidence-table__status">
                      {status === "confirmed" ? "확정" : status === "pending" ? "미확정" : "미수집"}
                    </span>
                  </th>
                  <td>{formatEvidenceNumber(row?.close)}</td>
                  <td>{formatEvidenceNumber(row?.volume)}</td>
                  <td>{row ? `${formatEvidenceNumber(row.change_pct)}%` : "미수집"}</td>
                  {INVESTOR_COLUMNS.map(([key, label]) => (
                    <td key={key} aria-label={`${label} ${formatEvidenceValue(row?.[key], status)}`}>
                      {formatEvidenceValue(row?.[key], status)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
