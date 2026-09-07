---
name: wave-double
description: 1인용 매수후보 추천·검증 운영 콘솔. 고급스러운 다크모드와 절제된 데이터 표현을 기본으로 한다.
status: final
sources:
  - {planning_artifacts}/briefs/brief-wave-double-2026-08-31/brief.md
  - {planning_artifacts}/briefs/brief-wave-double-2026-08-31/addendum.md
  - {planning_artifacts}/prds/prd-wave-double-2026-08-31/prd.md
updated: 2026-08-31
colors:
  canvas: '#0B0D10'
  surface: '#11151A'
  surface-raised: '#171C23'
  surface-elevated: '#1D242D'
  ink-primary: '#F3F5F7'
  ink-secondary: '#A6AFBA'
  ink-muted: '#707B88'
  border: '#29313B'
  accent: '#B89B6A'
  accent-strong: '#D4B77F'
  positive: '#67C29B'
  negative: '#E27E83'
  caution: '#D9AA68'
  informational: '#7FA8D8'
  overlay: 'rgba(4, 6, 9, 0.72)'
typography:
  fontFamily: 'Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
  display:
    fontFamily: 'Pretendard'
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: '-0.02em'
  heading:
    fontFamily: 'Pretendard'
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.35'
  body:
    fontFamily: 'Pretendard'
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label:
    fontFamily: 'Pretendard'
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.4'
  data:
    fontFamily: 'Pretendard, ui-monospace, SFMono-Regular, Consolas, monospace'
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.4'
rounded:
  sm: 6px
  md: 10px
  lg: 14px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 20px
  '6': 24px
  '7': 32px
  '8': 40px
components:
  primary-action:
    background: '{colors.accent}'
    foreground: '#0B0D10'
    radius: '{rounded.sm}'
  strategy-tag:
    background: '{colors.surface-elevated}'
    foreground: '{colors.accent-strong}'
    radius: '{rounded.full}'
  candidate-card:
    background: '{colors.surface}'
    border: '{colors.border}'
    radius: '{rounded.md}'
  status-badge:
    radius: '{rounded.full}'
---

## Brand & Style

wave-double은 매매를 대신하는 앱이 아니라, Neo가 매수 판단을 내리기 전 데이터의 근거와 신선도를 점검하는 개인 운영 콘솔이다. 분위기는 금융 터미널의 긴장감보다 프리미엄 분석 도구의 침착함에 가깝다. 어두운 캔버스 위에 따뜻한 메탈릭 골드 포인트를 최소한으로 사용하고, 숫자·상태·시간의 위계를 명확히 한다.

고급스러움은 장식에서 만들지 않는다. 넓은 여백, 낮은 채도의 표면 레이어, 얇은 경계선, 정돈된 숫자 정렬, 조용한 전환으로 만든다. 화면에 모든 정보를 한꺼번에 펼치지 않으며, 핵심 후보의 존재와 이유를 먼저 보여주고 3일치 원천 데이터는 한 단계 안에서 확인한다.

## Colors

- `colors.canvas`는 전체 배경이다. 순수 검정 대신 아주 옅은 청색이 섞인 흑색을 사용해 장시간 확인 시 깊이를 유지한다.
- `colors.surface`는 후보 목록과 패널, `colors.surface-raised`는 선택된 카드와 데이터 테이블, `colors.surface-elevated`는 팝오버·툴팁·강조 영역이다.
- `colors.accent` / `colors.accent-strong`은 브랜드와 핵심 행동, 전략 태그에만 쓴다. 수익·매수 신호를 의미하는 색으로 오용하지 않는다.
- `colors.positive`는 좋은 수급·양의 손익, `colors.negative`는 음의 손익, `colors.caution`은 표본 부족·부분성공·미확정, `colors.informational`은 장중 참고·시그널 유지에 사용한다.
- 배치 실패나 위험 고지는 색상만으로 전달하지 않는다. 상태 이름, 아이콘, 설명을 함께 제공한다.

피한다: 네온 그린/레드의 대면적 채움, 그라디언트, 유리 효과, 과도한 글로우, 캔들 차트 중심의 장식, 수익률을 축하하는 모션, 한 화면에 여러 색상의 카드 경쟁.

## Typography

모든 UI 폰트는 Pretendard를 우선한다. 제목은 짧고 단단하게, 본문은 14px을 기본으로 한다. 데이터 숫자는 `typography.data`를 사용하고 우측 정렬하여 열 간 비교를 쉽게 한다. 등락률·순매수·PF는 숫자 부호와 색을 함께 사용한다.

대문자만으로 된 라벨을 남발하지 않는다. KST 시각, 실행 유형, 원천 같은 보조 정보는 `typography.label`로 조용하게 표시한다. 임의의 긴 제목으로 카드 높이를 키우지 않으며, 종목명과 코드는 두 줄 이내로 고정한다.

## Layout & Spacing

데스크톱 우선 반응형 웹이다. 전체는 좌측 고정 내비게이션(240px)과 우측 콘텐츠로 구성한다. 콘텐츠 최대 폭은 1440px이며, 기본 본문은 1120px 안에서 읽힌다.

메인 대시보드는 다음 순서의 단일 흐름을 갖는다: 페이지 헤더 → 데이터 신뢰도 바 → 오늘의 후보 요약 → 후보 카드 목록 → 시장 전체 수급. 후보 카드는 1열이지만 카드 내부는 짧은 2분할 정보 구조를 사용한다. 화면 폭이 좁아질수록 내부 분할은 세로로 바뀐다.

긴 한 열 표를 기본으로 두지 않는다. 후보를 행 단위로 반복하면서 여러 줄을 쌓는 방식은 지양하고, 후보별 핵심 요약 1행 + 선택 시 확장되는 근거 패널을 사용한다. 3일치 데이터는 확장 패널 안의 고정 3행 테이블로 제공하며, 열 수가 많아 모바일에서 깨지지 않도록 모바일에서는 날짜별 행 카드로 전환한다.

여백은 `spacing/6`을 카드 내부 기본, `spacing/8`을 주요 섹션 사이 기본으로 한다. 표면 사이에는 경계선 또는 1단계 톤 차이 하나만 사용한다.

## Elevation & Depth

깊이는 그림자보다 표면 톤과 경계선으로 만든다. 일반 카드에는 그림자를 쓰지 않는다. 팝오버·모달만 `{colors.overlay}`와 매우 부드러운 그림자를 사용한다. 선택된 후보는 골드 테두리 1px 또는 표면 상승으로 구분하되, 발광 효과는 금지한다.

## Shapes

카드와 패널은 `rounded/md`, 버튼과 입력은 `rounded/sm`, 상태·전략 태그는 `rounded/full`을 쓴다. 둥근 모서리는 부드럽지만 장난스럽지 않게 유지한다. 원형 아이콘 버튼은 실제 아이콘 액션에만 허용한다.

## Components

- **App shell** — 좌측 내비게이션에 `오늘의 후보`, `성과 검증`, `배치 이력`을 둔다. 활성 항목은 골드 텍스트와 얇은 인셋 표시로 구분한다. 햄버거 메뉴 대신 작은 화면에서 접히는 사이드 패널을 사용한다.
- **Data trust bar** — 최신 배치 상태, KST 실행 시각, 트리거 유형, 데이터 신선도를 한 줄에 보여준다. 성공·부분성공·실패·휴장일 스킴을 텍스트로 명시한다. 실패/미갱신이면 수동 실행을 이 영역의 단일 주요 버튼으로 둔다.
- **Candidate summary card** — 종목명·코드, 전략 태그(A/B/C/D/E, 가변 개수), 수급 힌트, 당일 가격/등락률, 시그널 유지/소멸 상태를 한눈에 보여준다. 카드 전체를 클릭하면 근거 패널이 열리고, 선택된 카드는 `{colors.accent}` 경계선을 쓴다.
- **Evidence panel** — 후보별 2거래일전·1거래일전·당일의 종가, 거래량, 등락률, 외인·기관·개인·프로그램 순매수를 보여준다. 값마다 배치 시각을 반복하지 않고 패널 상단에 원천·생성 시각을 표시한다. 장중 당일 종목별 수급은 `미확정`으로 렌더링하며 0으로 보이지 않는다.
- **Market supply panel** — 코스피와 코스닥을 탭으로 나누고 외인·기관·개인·프로그램 방향을 간결한 숫자와 막대로 보여준다. 시장 수급은 장중 참고 정보임을 라벨로 고정한다.
- **Strategy tag** — A/B/C/D/E(가변 개수)를 태그로 표시하되 태그마다 다른 원색을 주지 않는다. 다중 태그는 가로로 나열하고 좁은 폭에서 줄바꿈하지 않고 `+N`으로 접는다.
- **Outcome badge** — TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED를 텍스트로 표시한다. 색상은 보조 수단이며 상태의 의미를 툴팁 또는 상세 문장으로 제공한다.
- **Metric comparison** — 성과 검증 페이지에서 실전 승률·PF와 백테스트 기대치를 같은 축으로 비교하되, 종결 건수와 진행중 건수를 항상 함께 둔다. 30건 미만이면 수치를 숨기고 `표본 부족 n/30`을 주된 메시지로 사용한다.
- **Bias diagnostic** — 후보 모집단, 백테스트 유니버스, 교집합, 기회 누락을 숫자 4개와 짧은 설명으로 보여준다. 차집합을 그래픽 장식으로 과장하지 않는다.
- **Toast / notice** — 자동 배치 실패, 부분성공, stale, 폴백 원천 사용을 비차단 알림으로 표시한다. 데이터가 오래됐다는 사실은 색보다 문장과 시각으로 명확히 한다.

## Do's and Don'ts

| Do | Don't |
|---|---|
| 핵심 후보 요약을 먼저, 3일치 근거는 펼침으로 제공 | 모든 필드를 기본으로 길게 나열하기 |
| Pretendard와 정렬된 숫자, 짧은 상태 문장 사용 | 서로 다른 색·아이콘으로 의미를 과도하게 장식하기 |
| 최신 시각·원천·부분성공을 항상 노출 | 데이터가 없을 때 0이나 빈 화면으로 오해시키기 |
| 표본 부족을 성과 수치보다 크게 표현 | 8건 승률을 백테스트와 당당히 비교하기 |
| 금색은 브랜드와 선택 상태에 제한 | 금색을 매수 확정 또는 수익 보장처럼 사용하기 |
| 1열 흐름 안에서 카드와 확장 패널로 밀도 조절 | 한 컬럼에 여러 줄짜리 후보 테이블을 계속 쌓기 |
