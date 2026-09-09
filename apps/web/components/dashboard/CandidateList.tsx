"use client";

import { useEffect, useMemo, useState } from "react";
import type { CandidateCardViewModel } from "@/lib/candidate-cards";
import {
  buildCandidateFilterItems,
  filterCandidateItems,
  getDefaultCandidateFilterState,
  hasActiveCandidateFilters,
  HINT_STATUS_LABEL,
  MISSING_SUPPLY_LABEL,
  SIGNAL_STATUS_LABEL,
  summarizeCandidateFilters,
  type CandidateFilterState,
} from "@/lib/candidate-filters";
import type {
  CandidateEvidenceRpcRow,
  CandidateSupplyHintRpcRow,
  SupplyHintStatus,
} from "@/lib/dashboard-types";
import { getStrategyLabel } from "@/lib/strategy-labels";
import CandidateCard from "./CandidateCard";

const HINT_STATUSES: SupplyHintStatus[] = ["good", "not_met", "undetermined"];
const SIGNAL_STATUSES = ["active", "vanished", "mixed"] as const;

function toggleValue<T>(values: T[], value: T): T[] {
  return values.includes(value) ? values.filter((current) => current !== value) : [...values, value];
}

function FilterCheckboxGroup<T extends string>({
  legend,
  name,
  options,
  selected,
  getLabel,
  onChange,
  unavailableMessage = "옵션 없음",
}: {
  legend: string;
  name: string;
  options: readonly T[];
  selected: T[];
  getLabel: (value: T) => string;
  onChange: (value: T) => void;
  unavailableMessage?: string;
}) {
  return (
    <fieldset className="candidate-filter__group">
      <legend>{legend}</legend>
      {options.length > 0 ? options.map((value) => (
        <label className="candidate-filter__option" key={value}>
          <input
            type="checkbox"
            name={name}
            value={value}
            checked={selected.includes(value)}
            onChange={() => onChange(value)}
          />
          <span>{getLabel(value)}</span>
        </label>
      )) : <span className="candidate-filter__unavailable">{unavailableMessage}</span>}
    </fieldset>
  );
}

export default function CandidateList({
  candidates,
  evidenceRows,
  hintRows,
  hintFetchFailed,
  evidenceFetchFailed,
  candidateCardsFetchFailed,
  candidateCount,
}: {
  candidates: CandidateCardViewModel[];
  evidenceRows: CandidateEvidenceRpcRow[];
  hintRows: CandidateSupplyHintRpcRow[];
  hintFetchFailed: boolean;
  evidenceFetchFailed: boolean;
  candidateCardsFetchFailed: boolean;
  candidateCount: number | undefined;
}) {
  const [filters, setFilters] = useState<CandidateFilterState>(getDefaultCandidateFilterState);
  const items = useMemo(
    () => buildCandidateFilterItems(candidates, evidenceRows, hintRows, hintFetchFailed),
    [candidates, evidenceRows, hintRows, hintFetchFailed],
  );
  const filteredItems = useMemo(() => filterCandidateItems(items, filters), [items, filters]);
  const filterOptions = useMemo(() => {
    const strategies = new Set<string>();
    const sources = new Set<string>();
    for (const item of items) {
      item.candidate.strategies.forEach((strategy) => strategies.add(strategy));
      item.candidate.vanishedStrategies.forEach((strategy) => strategies.add(strategy));
      item.sources.forEach((source) => sources.add(source));
    }
    return {
      strategies: [...strategies].sort((a, b) => a.localeCompare(b)),
      sources: [...sources].sort((a, b) => a.localeCompare(b)),
    };
  }, [items]);

  useEffect(() => {
    if (items.length === 0) return;
    setFilters((current) => {
      const strategies = current.strategies.filter((value) => filterOptions.strategies.includes(value));
      const sources = current.sources.filter((value) => filterOptions.sources.includes(value));
      if (strategies.length === current.strategies.length && sources.length === current.sources.length) {
        return current;
      }
      return { ...current, strategies, sources };
    });
  }, [filterOptions, items.length]);

  function updateArrayFilter(
    key: "strategies" | "hintStatuses" | "signalStatuses" | "sources",
    value: string,
  ) {
    setFilters((current) => ({
      ...current,
      [key]: toggleValue(current[key], value),
    }));
  }

  function resetFilters() {
    setFilters(getDefaultCandidateFilterState());
  }

  const hasFilters = hasActiveCandidateFilters(filters);
  const emptyFilterSummary = summarizeCandidateFilters(filters);
  const showFilterSurface = items.length > 0 || hasFilters;

  return (
    <>
      {showFilterSurface && (
        <section className="candidate-filter" aria-labelledby="candidate-filter-heading">
          <header className="candidate-filter__header">
            <div>
              <h2 id="candidate-filter-heading">후보 필터</h2>
              <p className="candidate-filter__description">조건을 여러 개 선택하면 각 그룹은 OR, 그룹 간에는 AND로 적용됩니다.</p>
            </div>
            {hasFilters && filteredItems.length > 0 && (
              <button type="button" className="candidate-filter__reset" onClick={resetFilters}>
                전체 초기화
              </button>
            )}
          </header>
          <div className="candidate-filter__groups">
            <FilterCheckboxGroup
              legend="전략"
              name="candidate-filter-strategy"
              options={filterOptions.strategies}
              selected={filters.strategies}
              getLabel={(strategy) => getStrategyLabel(strategy) ?? `전략 ${strategy}`}
              onChange={(value) => updateArrayFilter("strategies", value)}
            />
            <FilterCheckboxGroup
              legend="수급 힌트"
              name="candidate-filter-hint"
              options={HINT_STATUSES}
              selected={filters.hintStatuses}
              getLabel={(status) => HINT_STATUS_LABEL[status]}
              onChange={(value) => updateArrayFilter("hintStatuses", value)}
            />
            <FilterCheckboxGroup
              legend="시그널 상태"
              name="candidate-filter-signal"
              options={SIGNAL_STATUSES}
              selected={filters.signalStatuses}
              getLabel={(status) => SIGNAL_STATUS_LABEL[status]}
              onChange={(value) => updateArrayFilter("signalStatuses", value)}
            />
            <FilterCheckboxGroup
              legend="원천"
              name="candidate-filter-source"
              options={filterOptions.sources}
              selected={filters.sources}
              getLabel={(source) => source}
              onChange={(value) => updateArrayFilter("sources", value)}
              unavailableMessage={evidenceFetchFailed ? "원천 정보를 불러오지 못했습니다" : undefined}
            />
            <fieldset className="candidate-filter__group candidate-filter__group--missing">
              <legend>수급 결측</legend>
              {(Object.entries(MISSING_SUPPLY_LABEL) as [CandidateFilterState["missingSupply"], string][]).map(
                ([value, label]) => (
                  <label className="candidate-filter__option" key={value}>
                    <input
                      type="radio"
                      name="candidate-filter-missing-supply"
                      value={value}
                      checked={filters.missingSupply === value}
                      onChange={() => setFilters((current) => ({ ...current, missingSupply: value }))}
                    />
                    <span>{label}</span>
                  </label>
                ),
              )}
            </fieldset>
          </div>
          <p className="candidate-filter__result-count" role="status" aria-live="polite">
            필터 결과 {filteredItems.length}건 · 전체 {items.length}건
          </p>
        </section>
      )}

      {filteredItems.length > 0 ? (
        <ul className="candidate-card-grid" role="list">
          {filteredItems.map(({ candidate, evidence, hintStatus, supplyMissing }) => (
            <CandidateCard
              key={candidate.candidateId}
              candidate={candidate}
              evidence={evidence}
              evidenceFetchFailed={evidenceFetchFailed}
              hintStatus={hintStatus}
              supplyMissing={supplyMissing}
            />
          ))}
        </ul>
      ) : hasFilters ? (
        <div className="empty-state candidate-filter__empty" role="status">
          <p>현재 필터에 맞는 후보가 없습니다.</p>
          <ul aria-label="현재 적용 필터">
            {emptyFilterSummary.map((summary) => <li key={summary}>{summary}</li>)}
          </ul>
          <button type="button" className="candidate-filter__reset" onClick={resetFilters}>
            전체 초기화
          </button>
        </div>
      ) : (
        <div className="empty-state">
          <p>오늘 태깅된 후보가 없습니다.</p>
          <p>조건검색 결과 · 전략 시그널 기준으로 후보가 태깅됩니다.</p>
          {!candidateCardsFetchFailed && typeof candidateCount === "number" && (
            <p className="reference-text">참고용 · 오늘 태깅 후보 {candidateCount}건</p>
          )}
        </div>
      )}
    </>
  );
}
