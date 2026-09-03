# Epic 3 Context: 실전 사후 결과 자동 적재

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

종가 확정 배치에서 태깅된 후보의 진입과 이후 거래일별 관찰·판정 이력을 삭제나 덮어쓰기 없이 축적하고, 현재 상태를 언제든 재구축할 수 있게 한다. 이를 통해 TP·SL·TIMEOUT·OPEN 및 예외 상태를 백테스트와 비교 가능한 기준으로 자동 추적하여 90거래일 시점 종결 outcome 50건 이상의 실전 검증 데이터를 빠르게 확보한다.

## Stories

- Story 3.1: Outcome 이벤트/관찰/projection 스키마
- Story 3.2: Idempotent OPEN command 발행 로직
- Story 3.3: Close 발행 트랜잭션 연결 & 재진입 금지
- Story 3.4: 일자별 판정 관찰 수집
- Story 3.5: 가격 조정 이상 감지 & SUSPENDED 전이
- Story 3.6: TP/SL 판정 & 비용 반영 손익률
- Story 3.7: TIMEOUT 컷오프 확정 & 추적 대상 유계화
- Story 3.8: Outcome correction 이벤트 메커니즘
- Story 3.9: 상장폐지 DELISTED 종결
- Story 3.10: Outcome projection 재구축 검증

## Requirements & Constraints

- outcome 생성 자격은 종가 확정 배치의 canonical 태깅 결과에만 있다. 장중 태깅은 참고용이며 진입을 만들지 않는다.
- 진입일과 진입가는 해당 거래일 및 `daily_ohlcv`의 정규장 adjusted 종가다. 최초 OPEN 이벤트에 기록된 진입가는 이후 가격 재조정으로 바꾸지 않으며, 명시적 correction만 예외다.
- 동일 종목·전략의 OPEN은 한 건만 허용하고 보유 중 재태깅으로 새 진입을 만들지 않는다. 재시도는 command key와 관찰 식별자를 통해 같은 결과를 반환해야 한다.
- 판정은 진입 다음 거래일부터 시작한다. TP는 고가가 진입가의 103% 이상, SL은 저가가 97% 이하일 때이며 같은 날 둘 다 충족하면 SL을 우선한다. 왕복 0.1% 비용 차감 후 손익률은 각각 +2.9%, -3.1%다.
- TP나 SL에 도달하지 않은 outcome은 30번째 실거래일 종가로 TIMEOUT 처리한다. 휴장일과 유효 일봉이 없는 거래정지 기간은 `holding_days`와 컷오프 계산에서 제외하며, 적용한 N은 `cutoff_n`에 고정해 과거 결과를 재계산하지 않는다.
- 가격 조정 판정은 LS 수정주가 마커를 우선하고, 마커가 없더라도 전일 종가 대비 절대 30% 초과 갭을 안전망으로 사용한다. 이상이 의심되면 자동 TP/SL 판정을 금지하고 SUSPENDED로 전이한다.
- terminal 상태는 불변이며 원행 UPDATE로 수정할 수 없다. 복귀·종결·수치 정정은 사유와 expected version을 가진 correction event로만 수행한다.
- SUSPENDED와 DELISTED는 정상 종결 상태와 분리하고 추적·성과 집계에서 오인하지 않는다. 두 상태의 감지는 수신 확인이 필요한 GitHub Issue를 생성하며, SUSPENDED가 장기 미해결이면 경과 알림을 남긴다.
- outcome 장부·관찰·projection은 장기 보존 대상이다. 실제 주문이나 청산 실행은 범위 밖이며, 이 에픽은 추천 이후의 가상 성과 관찰만 담당한다.

## Technical Decisions

- `outcome_events`와 `outcome_observations`는 append-only 장부이고 `candidate_outcome`은 장부 재생으로 복원 가능한 current projection이다. 이벤트는 종목·전략·논리 실행 키·명령 유형을, 관찰은 outcome과 평가 거래일별 고가·저가·종가·결과 코드를 보존한다.
- projection은 진입 정보, `TP | SL | TIMEOUT | OPEN | SUSPENDED | DELISTED`, 청산 정보, 비용 반영 수익률, 컷오프, 보유 거래일을 제공한다. `(ticker, strategy, entry_date)`는 유일하고, `(ticker, strategy)`별 OPEN은 partial unique index로 제한한다.
- close publication의 단일 serializable transaction이 canonical 후보를 잠근 뒤 OPEN 이벤트와 outcome stage를 만들고 발행 포인터까지 함께 커밋한다. outcome 단계가 실패하면 후보·태그 발행을 포함한 전체 transaction을 rollback한다.
- command 멱등 키는 `(logical_run_key, ticker, strategy, command_type)`이고, 관찰 멱등 키는 `(outcome_id, evaluation_trading_day)`다. 재처리 무효화는 삭제가 아니라 supersession 또는 correction event로 표현한다.
- 브라우저는 RLS가 허용한 읽기만 수행하고 elevated 쓰기는 trusted 실행 경계에 둔다. DB 금액·비율은 `numeric`, API에서는 decimal string을 사용하며, 시각은 UTC로 저장하고 거래일은 `date`로 유지한다.
- outcome 자체에 원천 컬럼이나 원천 JSON을 복제하지 않는다. 향후 원천별 지표는 canonical 후보의 정규화된 기여 관계를 join해 계산한다.
- `outcome_tracking`은 대시보드 snapshot의 고정 section이며 한 section 안에서 여러 run의 데이터를 섞지 않는다. 로그와 stage 결과는 실행 ID, stage, 배치 유형, 거래일, 시도 번호, 소요 시간, 결과 코드를 포함한다.
- 이벤트·관찰 fixture를 처음부터 재생한 결과가 기대 projection 및 현재 projection과 정확히 일치해야 하며, correction과 예외 상태 전이를 포함한 이 회귀 검증이 배포 게이트다.

## UX & Interaction Patterns

추적 화면은 TP·SL·TIMEOUT·OPEN과 SUSPENDED·DELISTED를 텍스트 배지로 구분하고 색상만으로 의미를 전달하지 않는다. OPEN은 진행 중 수로 별도 표시해 성과 분모와 섞지 않으며, 가격 보정 이상은 자동 판정을 멈춘 이유와 운영자 확인 필요성을 명확히 안내한다. outcome section의 실행 시각·상태·신선도는 다른 배치 데이터와 구분해 노출한다.

## Cross-Story Dependencies

종가 canonical 후보와 adjusted 일봉 데이터가 OPEN 생성의 선행 입력이며, outcome 생성은 close publication transaction에 결합된다. 관찰 수집이 판정의 근거를 만들고, correction 메커니즘이 SUSPENDED 복귀와 DELISTED 종결의 유일한 변경 경로다. 가격 조정 감지는 TP/SL 판정보다 먼저 또는 동시에 배포해야 하며, 판정 로직도 감지 완료 여부를 확인하지 못하면 확정을 보류해야 한다. 완성된 outcome projection과 `outcome_tracking` section은 후속 추적 화면 및 실전 승률·PF·편향 분석의 입력이 된다.
