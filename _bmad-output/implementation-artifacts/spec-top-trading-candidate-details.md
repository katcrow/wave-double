---
title: '거래대금 상위 후보 핵심 지표 표시'
type: 'feature'
created: '2026-09-30'
status: 'done'
route: 'one-shot'
---

# 거래대금 상위 후보 핵심 지표 표시

## Intent

**Problem:** 거래대금 상위 후보 영역이 원 단위 거래대금만 보여 사용자가 당일 상승률, 주요 섹터, 프로그램 수급 금액을 한눈에 비교할 수 없다. 특히 거래대금과 프로그램 금액은 억원 단위로 읽어야 하며 소수점 없는 표시가 필요하다.

**Approach:** 상위 후보 RPC에 당일 등락률, 저장된 주요 섹터명, 프로그램 순매수 금액을 추가하고, 프로그램 수급 수집 대상을 active 태그 후보와 거래대금 상위 3개 후보의 합집합으로 확장한다. 웹 카드에는 거래대금 억원, 당일 상승률, 주요 섹터, 프로그램 순매수금액 억원을 표시하며 결측은 미확인으로 표시한다.

주요 섹터 원천은 현재 배치/API에 없어 저장 칼럼과 fallback만 준비했으며, 실제 섹터 수집 및 backfill은 deferred-work로 남겼다.

## Suggested Review Order

1. [상위 후보 RPC와 억원 환산](../../infra/supabase/migrations/202609301200_expand_top_trading_candidate_details.sql) — snapshot lineage와 지표 계산을 확인한다.
2. [수급 수집 대상 확장](../../apps/batch/tagged_candidate_fetcher.py) — 태그 없는 상위 3개도 프로그램 수급 수집 대상인지 확인한다.
3. [상위 후보 화면](../../apps/web/components/dashboard/TopTradingCandidates.tsx) — 네 지표의 라벨, 결측, 모바일 배치를 확인한다.
4. [화면 계약 테스트](../../e2e/authenticated-dashboard.spec.ts) — 각 라벨과 값의 연결을 확인한다.

## Review Triage Log

- 구버전 RPC 상세 필드 호환 처리는 migration을 운영에 먼저 적용하고 웹을 배포하는 순서로 현재 rollout에서 보장되므로 deferred했다.
- snapshot 거래일/freshness와 RPC 실패 전용 안내는 기존 신뢰도 표면의 후속 UX 범위라 deferred했다.
