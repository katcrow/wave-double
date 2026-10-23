---
type: epic
title: "운영 배치와 데이터 발행을 신뢰할 수 있다"
parent: initiative-wave-double
covers: ["R1","R2","R3"]
sources: ["_bmad-output/initiative-wave-double/initiative-wave-double.md"]
companions: []
after: []
refined: false
risk: high
---

# 운영 배치와 데이터 발행을 신뢰할 수 있다

## Description

부모의 R1, R2, R3를 아래 세 작업으로 검증하거나 보완한다. 이미 구현된 기능은 다시 개발하지 않으며 검증 정의의 존재와 운영 성공 증거를 구분한다.

## Outcome

운영 배치와 데이터 발행을 신뢰할 수 있다. 통과·실패·미확인 결과와 근거를 구분할 수 있다.

## Requirements

- R1 (parent R1): 배포·CI·운영 스키마의 현재 기준을 확보한다. 완료 증거: 동일 배포 기준의 CI 결과와 운영 대조표에서 통과·실패·미확인을 구분할 수 있다. 기존 정상 배치 한 건의 dispatch→run→publish→후보 화면 경로를 읽기 조회와 Playwright MCP로 연결한다.
- R2 (parent R2): 자동 배치부터 화면 발행까지 수명주기를 검증한다. 완료 증거: run_id·logical_run_key·거래일로 배치와 발행 화면을 연결하고 중복 발행·실패 숨김 여부를 판정한 증거가 있다.
- R3 (parent R3): 최신 백업과 격리 복구 드릴의 증거를 확인한다. 완료 증거: 암호화 백업 식별자·격리 복원 결과·기존 workflow 기준 대비 실측 RPO/RTO와 미해결 항목이 기록되어 있다.

## Constraints

부모의 Constraints를 모두 따른다. 검증 spike에서 문제를 발견하면 재현 조건·영향·후속 수정 범위를 기록하며 오류를 통과로 숨기지 않는다. 운영 규칙 변경이 필요하면 결정 항목으로 분리한다.

## Done when

- 동일 배포 기준의 CI 결과와 운영 대조표에서 통과·실패·미확인을 구분할 수 있다.
- run_id·logical_run_key·거래일로 배치와 발행 화면을 연결하고 중복 발행·실패 숨김 여부를 판정한 증거가 있다.
- 암호화 백업 식별자·격리 복원 결과·기존 workflow 기준 대비 실측 RPO/RTO와 미해결 항목이 기록되어 있다.
- 운영에 닿는 결과는 동일 배포 기준의 실측 증거로 수용한다. 수정이 있으면 관련 회귀와 배포 후 확인까지 포함하며 로컬 통과만으로 운영 완료라 하지 않는다.

## Boundaries

- 배치 스케줄·발행과 복구 증거를 소유한다. 후보/성과 에픽의 화면 시나리오와 포트폴리오 계산 수정은 제외한다.
- 검증 결과 보고와 제품 릴리스 완료는 별개이며 미해결 운영 오류가 있으면 에픽 수용 상태에 명시한다.
- 첫 검증의 환경·증거 기록은 이 에픽이 소유하고 외부 전제는 tickets.toml의 after로 연결한다.

## References

- parent — _bmad-output/initiative-wave-double/initiative-wave-double.md, Requirements R1, R2, R3 및 Constraints
- assessment — _bmad-output/initiative-wave-double/project-assessment.md, 운영 신뢰성

## Notes

- Decision: 2026-10-21 분할 제안 — tracer bullet은 1.1 배포·CI·운영 스키마의 현재 기준을 확보한다이다. 기존 배포 기준에서 가장 얇은 입력→처리→관찰 경로부터 증거를 확보한다. 승인 전 초안이다.
- Decision: 2026-10-21 분할 제안 — 부모 요구사항만으로 세 티켓을 구체화했다. leaf 파일은 pull 시 생성하며 아직 실행하지 않았다.

- Decision: 2026-10-21 검증 반영 — 초안의 상세 분할은 아래 제안대로 보존하되 사용자 승인 전까지 refined는 false다.
- Decision: 2026-10-21 순서 제안 — 첫 항목은 최소 전체 경로, 다음은 실제 스케줄·재시도의 불확실성을 먼저 확인한다. 독립 항목은 불필요하게 직렬화하지 않는다.
- Assumption: 1.1 위험도 medium 제안 — 배포 기준을 잘못 읽으면 이후 검증 전체가 다른 버전에 연결된다.
- Decision: 1.1 조사 질문은 해당 Requirements의 검증 여부이며 이 에픽의 후속 티켓과 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-1-1.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
- Assumption: 1.2 위험도 high 제안 — 운영 재시도·실행 검증이 실제 발행에 영향을 줄 수 있다. 추가 확인: 검증창 종료 뒤 새로운 중복 실행이나 미처리 outbox가 남지 않았는지 확인한다.
- Decision: 1.2 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-1-2.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
- Assumption: 1.3 위험도 medium 제안 — 복구 성공을 오판하면 장애 시 사용할 백업이 없을 수 있다.
- Decision: 1.3 조사 질문은 해당 Requirements의 검증 여부이며 이후 의존 티켓과 에픽 수용 판단이 결과를 소비한다. 결과는 이 에픽 폴더의 evidence-1-3.md에 SHA·시각·입력·관찰·실패/미확인·후속 과제를 기록한다.
