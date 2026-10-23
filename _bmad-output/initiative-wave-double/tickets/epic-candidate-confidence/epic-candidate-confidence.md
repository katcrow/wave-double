---
type: epic
title: "후보 화면에서 최신 데이터와 실패 상태를 구별할 수 있다"
parent: initiative-wave-double
covers: ["R4","R5","R6"]
sources: ["_bmad-output/initiative-wave-double/initiative-wave-double.md"]
companions: []
after: []
refined: false
risk: high
---

# 후보 화면에서 최신 데이터와 실패 상태를 구별할 수 있다

## Description

부모의 R4, R5, R6를 아래 세 작업으로 검증하거나 보완한다. 이미 구현된 기능은 다시 개발하지 않으며 검증 정의의 존재와 운영 성공 증거를 구분한다.

## Outcome

후보 화면에서 최신 데이터와 실패 상태를 구별할 수 있다. 통과·실패·미확인 결과와 근거를 구분할 수 있다.

## Requirements

- R1 (parent R4): 후보 스냅샷·카드·근거의 연결을 검증한다. 완료 증거: Playwright MCP에서 정상/빈 결과/실패/부분 상태를 확인하고 SQL 결과와 카드 순서·근거·기준시각이 일치하는 기록을 남긴다.
- R2 (parent R5): 수급·시장확률의 기준시각과 실패 표시를 검증한다. 완료 증거: Playwright MCP로 정상/지연/누락/실패를 확인한다. 시장확률에 후보와 같은 run을 강제하지 않고 각 정보의 상태·시각을 구별한다.
- R3 (parent R6): 로그인과 수동 실행 후 갱신 경계를 검증한다. 완료 증거: Playwright MCP로 허용/거부 접근과 수동 실행 응답·갱신을 확인한다. 운영 실행이 필요하면 통상 운영창의 단일 실행으로 제한한다.

## Constraints

부모의 Constraints를 모두 따른다. 검증 spike에서 문제를 발견하면 재현 조건·영향·후속 수정 범위를 기록하며 오류를 통과로 숨기지 않는다. 운영 규칙 변경이 필요하면 결정 항목으로 분리한다.

## Done when

- Playwright MCP에서 정상/빈 결과/실패/부분 상태를 확인하고 SQL 결과와 카드 순서·근거·기준시각이 일치하는 기록을 남긴다.
- Playwright MCP로 정상/지연/누락/실패를 확인한다. 시장확률에 후보와 같은 run을 강제하지 않고 각 정보의 상태·시각을 구별한다.
- Playwright MCP로 허용/거부 접근과 수동 실행 응답·갱신을 확인한다. 운영 실행이 필요하면 통상 운영창의 단일 실행으로 제한한다.
- 운영에 닿는 결과는 동일 배포 기준의 실측 증거로 수용한다. 수정이 있으면 관련 회귀와 배포 후 확인까지 포함하며 로컬 통과만으로 운영 완료라 하지 않는다.

## Boundaries

- 후보 화면과 접근·수동 실행의 관찰을 소유한다. 배치 스케줄 변경·성과 계산·포트폴리오 수정은 제외한다.
- 검증 결과 보고와 제품 릴리스 완료는 별개이며 미해결 운영 오류가 있으면 에픽 수용 상태에 명시한다.
- 첫 검증의 환경·증거 기록은 이 에픽이 소유하고 외부 전제는 tickets.toml의 after로 연결한다.

## References

- parent — _bmad-output/initiative-wave-double/initiative-wave-double.md, Requirements R4, R5, R6 및 Constraints
- assessment — _bmad-output/initiative-wave-double/project-assessment.md, 후보 판단

## Notes

- Decision: 2026-10-21 분할 제안 — tracer bullet은 2.1 후보 스냅샷·카드·근거의 연결을 검증한다이다. 기존 배포 기준에서 가장 얇은 입력→처리→관찰 경로부터 증거를 확보한다. 승인 전 초안이다.
- Decision: 2026-10-21 분할 제안 — 부모 요구사항만으로 세 티켓을 구체화했다. leaf 파일은 pull 시 생성하며 아직 실행하지 않았다.

- Decision: 2026-10-21 검증 반영 — 초안의 상세 분할은 아래 제안대로 보존하되 사용자 승인 전까지 refined는 false다.
- Decision: 2026-10-21 순서 제안 — 첫 항목은 최소 전체 경로, 다음은 독립 수급·확률 시각의 불확실성을 먼저 확인한다. 독립 항목은 불필요하게 직렬화하지 않는다.
- Decision: 2026-10-21 의존성 보완 — 2.3은 2.1의 화면과 1.2의 운영 실행 증거·검증창을 소비한다. 2.2와는 화면을 읽기 검증하므로 파일·시나리오 전역 상태 변경 없이 별도 브라우저 컨텍스트를 사용한다.
- Assumption: 2.1 위험도 medium 제안 — 후보의 순서·실패 상태를 잘못 판단하면 매수 판단 근거가 왜곡된다.
- Decision: 2.1 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-2-1.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
- Assumption: 2.2 위험도 medium 제안 — 다른 기준시각의 보조 정보를 최신 데이터로 오판할 수 있다.
- Decision: 2.2 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-2-2.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
- Assumption: 2.3 위험도 high 제안 — 인증·수동 실행의 오판은 무단 접근 또는 중복 실행을 놓칠 수 있다. 추가 확인: 로그아웃 후 이전 인증 세션의 보호 자원 접근을 다시 확인한다.
- Decision: 2.3 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-2-3.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
