---
type: epic
title: "추적 성과와 전략 계산의 근거를 재현할 수 있다"
parent: initiative-wave-double
covers: ["R7","R8","R9"]
sources: ["_bmad-output/initiative-wave-double/initiative-wave-double.md"]
companions: []
after: []
refined: false
risk: high
---

# 추적 성과와 전략 계산의 근거를 재현할 수 있다

## Description

부모의 R7, R8, R9를 아래 세 작업으로 검증하거나 보완한다. 이미 구현된 기능은 다시 개발하지 않으며 검증 정의의 존재와 운영 성공 증거를 구분한다.

## Outcome

추적 성과와 전략 계산의 근거를 재현할 수 있다. 통과·실패·미확인 결과와 근거를 구분할 수 있다.

## Requirements

- R1 (parent R7): close 발행부터 성과 추적까지 대조한다. 완료 증거: 운영 읽기 조회·격리 fixture·Playwright MCP 증거에서 같은 후보/전략/원천의 추적 행과 발행 계보가 일치한다.
- R2 (parent R8): 성과 통계와 편향 진단의 표시를 검증한다. 완료 증거: 기존 parity fixture와 Playwright MCP에서 표본 경계·기대치 없음·조회실패·0건이 구분되고 수치와 판정이 일치한다.
- R3 (parent R9): 전략별 실행기와 성과 비교 계약을 명시한다. 완료 증거: L의 동시 TP/SL·수익 종가·미청산, M의 박스 하단·트레일 회귀와 계약표가 일치한다. 서로 다른 실행 결과를 동일 기준 성과로 취급하지 않는다.

## Constraints

부모의 Constraints를 모두 따른다. 검증 spike에서 문제를 발견하면 재현 조건·영향·후속 수정 범위를 기록하며 오류를 통과로 숨기지 않는다. 운영 규칙 변경이 필요하면 결정 항목으로 분리한다.

## Done when

- 운영 읽기 조회·격리 fixture·Playwright MCP 증거에서 같은 후보/전략/원천의 추적 행과 발행 계보가 일치한다.
- 기존 parity fixture와 Playwright MCP에서 표본 경계·기대치 없음·조회실패·0건이 구분되고 수치와 판정이 일치한다.
- L의 동시 TP/SL·수익 종가·미청산, M의 박스 하단·트레일 회귀와 계약표가 일치한다. 서로 다른 실행 결과를 동일 기준 성과로 취급하지 않는다.
- 운영에 닿는 결과는 동일 배포 기준의 실측 증거로 수용한다. 수정이 있으면 관련 회귀와 배포 후 확인까지 포함하며 로컬 통과만으로 운영 완료라 하지 않는다.

## Boundaries

- 추적·통계 대조 및 실행기 비교 계약을 소유한다. 후보 화면 변경과 계좌 회계·M 계좌 연결은 제외한다.
- 검증 결과 보고와 제품 릴리스 완료는 별개이며 미해결 운영 오류가 있으면 에픽 수용 상태에 명시한다.
- 첫 검증의 환경·증거 기록은 이 에픽이 소유하고 외부 전제는 tickets.toml의 after로 연결한다.

## References

- parent — _bmad-output/initiative-wave-double/initiative-wave-double.md, Requirements R7, R8, R9 및 Constraints
- assessment — _bmad-output/initiative-wave-double/project-assessment.md, 성과와 재현성

## Notes

- Decision: 2026-10-21 분할 제안 — tracer bullet은 3.1 close 발행부터 성과 추적까지 대조한다이다. 기존 배포 기준에서 가장 얇은 입력→처리→관찰 경로부터 증거를 확보한다. 승인 전 초안이다.
- Decision: 2026-10-21 분할 제안 — 부모 요구사항만으로 세 티켓을 구체화했다. leaf 파일은 pull 시 생성하며 아직 실행하지 않았다.

- Decision: 2026-10-21 검증 반영 — 초안의 상세 분할은 아래 제안대로 보존하되 사용자 승인 전까지 refined는 false다.
- Decision: 2026-10-21 순서 제안 — 첫 항목은 최소 전체 경로, 다음은 통계의 경계값의 불확실성을 먼저 확인한다. 독립 항목은 불필요하게 직렬화하지 않는다.
- Assumption: 3.1 위험도 medium 제안 — 추적의 원천·계보를 잘못 연결하면 운영 성과를 오판할 수 있다.
- Decision: 3.1 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-3-1.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
- Assumption: 3.2 위험도 medium 제안 — 표본·통계 판정을 오해하면 불충분한 근거로 전략을 평가한다.
- Decision: 3.2 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-3-2.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
- Assumption: 3.3 위험도 high 제안 — 실행기 규칙을 혼동하면 후속 계좌 계산까지 다른 전략으로 계산한다. 추가 확인: 기존 운영 outcome 규칙을 읽기 전용으로 대조하고 차이를 별도 표로 남긴다.
