# LS증권 OPEN API 정의서

> 출처: [LS증권 OPEN API 포털](https://openapi.ls-sec.co.kr/apiservice) · 수집 기준일: 2026-08-26 · API **41**개 / TR **364**건 전수 수집

**본 문서는 sub-signal-system 에서 LS증권 Open API 를 사용하는 모든 작업의 단일 참조(Single Source of Truth)입니다. API 관련 작업 시 반드시 본 정의서를 먼저 확인할 것 (규칙은 저장소 루트 `AGENTS.md` 참조).**

## 1. 공통 규격

### 도메인

| 구분 | Domain | 비고 |
|---|---|---|
| REST | `https://openapi.ls-sec.co.kr:8080` | 시세/차트/계좌/주문 등 TR 조회 및 주문 |
| WebSocket | `wss://openapi.ls-sec.co.kr:9443` | 실시간 시세 등록/해제 및 push 수신 |

### 인증 (OAuth 2.0)

1. 포털에서 발급받은 `appkey` / `appsecretkey` 로 `POST /oauth2/token` 호출 → `access_token`(유효 24h) 발급 ([정의서](01-oauth-auth/issue-access-token.md))
2. 이후 모든 요청 Header 에 `authorization: Bearer {access_token}` 설정
3. 토큰 폐기는 `POST /oauth2/revoke` ([정의서](01-oauth-auth/revoke-access-token.md))

### 공통 요청 Header (REST)

| Element | 한글명 | 필수 | 설명 | 적용 TR 수 |
|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | Y | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" | 247/248 |
| `authorization` | 접근토큰 | Y | OAuth 토큰이 필요한 API 경우 발급한 Access Token을 설정하기 위한 Request Heaeder Parameter | 245/248 |
| `tr_cd` | 거래 CD | Y | LS증권 거래코드 | 245/248 |
| `tr_cont` | 연속 거래 여부 | Y | 연속거래 여부<br/>Y:연속○<br/>N:연속× | 245/248 |
| `tr_cont_key` | 연속 거래 Key | Y | 연속일 경우 그전에 내려온 연속키 값 올림 | 245/248 |
| `mac_address` | MAC 주소 | Y | 법인인 경우 필수 세팅 | 245/248 |
| `type` | 컨텐츠타입 | Y | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" | 1/248 |

- `content-type` 은 `application/json; charset=UTF-8` 고정(OAuth 제외).
- `tr_cont`(연속조회 여부), `tr_cont_key`(연속조회 키)는 연속 조회가 가능한 TR 에서 사용.

### 속성 타입 코드

| 코드 | 타입 |
|---|---|
| A0001 | String |
| A0002 | Array |
| A0003 | Object |
| A0004 | Number |
| A0005 | Object Array |

## 2. 문서 구조

```
docs/api/ls-openapi/
├── README.md                 # 이 문서 (공통 규격 + 전체 인덱스)
├── _data/ls-openapi.json     # 원본 수집 데이터(기계 판독용)
├── 01-oauth-auth/
├── 02-sector/
├── 03-domestic-stock/
├── 04-futures-options/
├── 05-overseas-futures/
├── 06-overseas-stock/
├── 07-misc/
├── 08-realtime-invest-info/
```

## 3. 전체 API 인덱스

### OAuth 인증 (2개 API / 2개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [접근토큰 발급](01-oauth-auth/issue-access-token.md) | `/oauth2/token` | POST | 1 | `token` |
| [접근토큰 폐기](01-oauth-auth/revoke-access-token.md) | `/oauth2/revoke` | POST | 1 | `revoke` |

### 업종 (3개 API / 9개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[업종] 시세](02-sector/market-data.md) | `/indtp/market-data` | POST | 5 | `t1514` `t8424` `t1485` `t1511` `t1516` |
| [[업종] 실시간 시세](02-sector/realtime.md) | `/websocket/indtp` | WS | 1 | `BM_` |
| [[업종] 차트](02-sector/chart.md) | `/indtp/chart` | POST | 3 | `t8408` `t8409` `t8429` |

### 주식 (16개 API / 197개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[주식] ELW](03-domestic-stock/elw.md) | `/stock/elw` | POST | 20 | `t1950` `t1951` `t1954` `t1956` `t1958` `t1959` `t1960` `t1961` `t1964` `t1966` `t1969` `t1971` `t1972` `t1973` `t1974` `t1988` `t8431` `t9905` `t9907` `t9942` |
| [[주식] ETF](03-domestic-stock/etf.md) | `/stock/etf` | POST | 5 | `t1901` `t1902` `t1903` `t1904` `t1906` |
| [[주식] 거래원](03-domestic-stock/brokerage.md) | `/stock/exchange` | POST | 3 | `t1752` `t1764` `t1771` |
| [[주식] 계좌](03-domestic-stock/account.md) | `/stock/accno` | POST | 12 | `CDPCQ04700` `CSPAQ00600` `CSPAQ12200` `CSPAQ12300` `CSPAQ13700` `CSPAQ22200` `CSPBQ00200` `FOCCQ33600` `t0150` `t0151` `t0424` `t0425` |
| [[주식] 기타](03-domestic-stock/misc.md) | `/stock/etc` | POST | 10 | `CLNAQ00100` `t1403` `t1411` `t1638` `t1921` `t1926` `t1927` `t1941` `t8430` `t8436` |
| [[주식] 상위종목](03-domestic-stock/top-movers.md) | `/stock/high-item` | POST | 9 | `t1441` `t1444` `t1452` `t1463` `t1466` `t1481` `t1482` `t1489` `t1492` |
| [[주식] 섹터](03-domestic-stock/sector.md) | `/stock/sector` | POST | 5 | `t1531` `t1532` `t1533` `t1537` `t8425` |
| [[주식] 시세](03-domestic-stock/market-data.md) | `/stock/market-data` | POST | 25 | `t1101` `t1102` `t1104` `t1105` `t1109` `t1301` `t1302` `t1305` `t1308` `t1310` `t1404` `t1405` `t1410` `t1422` `t1427` `t1442` `t1449` `t1471` `t1475` `t1486` `t1488` `t8407` `t8450` `t8454` `t9945` |
| [[주식] 실시간 시세](03-domestic-stock/realtime.md) | `/websocket/stock` | WS | 65 | `B7_` `DH1` `DHA` `DK3` `DS3` `DVI` `H1_` `H2_` `HA_` `HB_` `I5_` `IJ_` `K1_` `K3_` `KH_` `KM_` `KS_` `OK_` `PH_` `PM_` `S2_` `S3_` `S4_` `SC0` `SC1` `SC2` `SC3` `SC4` `SHC` `SHD` `SHI` `SHO` `VI_` `YJ_` `YK3` `YS3` `ESN` `h2_` `h3_` `k1_` `s2_` `s3_` `s4_` `Ys3` `NS3` `NH1` `NS2` `NYS` `NVI` `NK1` `NPH` `NPM` `NBT` `NBM` `US3` `UH1` `US2` `UYS` `UPH` `UK1` `UBT` `UBM` `UPM` `UVI` `AFR` |
| [[주식] 외인/기관](03-domestic-stock/foreign-institution.md) | `/stock/frgr-itt` | POST | 3 | `t1702` `t1716` `t1717` |
| [[주식] 종목검색](03-domestic-stock/stock-search.md) | `/stock/item-search` | POST | 8 | `t1809` `t1825` `t1826` `t1852` `t1856` `t1866` `t1859` `t1860` |
| [[주식] 주문](03-domestic-stock/orders.md) | `/stock/order` | POST | 3 | `CSPAT00601` `CSPAT00701` `CSPAT00801` |
| [[주식] 차트](03-domestic-stock/chart.md) | `/stock/chart` | POST | 7 | `t1665` `t8410` `t8411` `t8412` `t8451` `t8452` `t8453` |
| [[주식] 투자자](03-domestic-stock/investors.md) | `/stock/investor` | POST | 7 | `t1601` `t1602` `t1603` `t1615` `t1617` `t1621` `t1664` |
| [[주식] 투자정보](03-domestic-stock/investment-info.md) | `/stock/investinfo` | POST | 8 | `t3102` `t3202` `t3320` `t3341` `t3401` `t3518` `t3521` `t8428` |
| [[주식] 프로그램](03-domestic-stock/program-trading.md) | `/stock/program` | POST | 7 | `t1631` `t1632` `t1633` `t1636` `t1637` `t1640` `t1662` |

### 선물/옵션 (7개 API / 91개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[선물/옵션] 계좌](04-futures-options/account.md) | `/futureoption/accno` | POST | 13 | `CFOAQ00600` `CFOAQ50600` `CFOAQ10100` `CFOBQ10500` `CFOEQ11100` `CFOEQ82600` `CFOFQ02400` `t0434` `t0441` `CCENQ10100` `CCENQ30100` `CCENQ90200` `FOCCQ33700` |
| [[선물/옵션] 기타](04-futures-options/misc.md) | `/futureoption/etc` | POST | 1 | `MMDAQ91200` |
| [[선물/옵션] 시세](04-futures-options/market-data.md) | `/futureoption/market-data` | POST | 30 | `t2111` `t2112` `t2106` `t2212` `t2214` `t2210` `t2301` `t2407` `t2424` `t2522` `t8401` `t8402` `t8403` `t8404` `t8405` `t8406` `t8426` `t8427` `t8467` `t8433` `t8434` `t8435` `t9943` `t9944` `t8455` `t8456` `t8457` `t8458` `t8459` `t8460` |
| [[선물/옵션] 실시간 시세](04-futures-options/realtime.md) | `/websocket/futureoption` | WS | 31 | `C01` `CD0` `FC9` `FD0` `FH9` `FX9` `H01` `JC0` `JD0` `JH0` `JX0` `O01` `OC0` `OD0` `OH0` `OMG` `OX0` `YC3` `YF9` `YJC` `YOC` `DC0` `O02` `C02` `DH0` `H02` `DD0` `DX0` `DYC` `DBM` `DBT` |
| [[선물/옵션] 주문](04-futures-options/orders.md) | `/futureoption/order` | POST | 7 | `CFOAT00100` `CFOAT00200` `CFOAT00300` `CFOBQ10800` `CCENT00100` `CCENT00200` `CCENT00300` |
| [[선물/옵션] 차트](04-futures-options/chart.md) | `/futureoption/chart` | POST | 5 | `t2216` `t8464` `t8465` `t8466` `t8461` |
| [[선물/옵션] 투자자](04-futures-options/investors.md) | `/futureoption/investor` | POST | 4 | `t2541` `t2545` `t8462` `t8463` |

### 해외선물 (5개 API / 35개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[해외선물] 계좌](05-overseas-futures/account.md) | `/overseas-futureoption/accno` | POST | 7 | `CIDBQ01400` `CIDBQ01500` `CIDBQ01800` `CIDBQ02400` `CIDBQ03000` `CIDBQ05300` `CIDEQ00800` |
| [[해외선물] 시세](05-overseas-futures/market-data.md) | `/overseas-futureoption/market-data` | POST | 14 | `o3101` `o3104` `o3105` `o3106` `o3107` `o3116` `o3121` `o3123` `o3125` `o3126` `o3127` `o3128` `o3136` `o3137` |
| [[해외선물] 실시간 시세](05-overseas-futures/realtime.md) | `/websocket/overseas-futureoption` | WS | 7 | `OVC` `OVH` `WOC` `WOH` `TC1` `TC2` `TC3` |
| [[해외선물] 주문](05-overseas-futures/orders.md) | `/overseas-futureoption/order` | POST | 3 | `CIDBT00100` `CIDBT00900` `CIDBT01000` |
| [[해외선물] 차트](05-overseas-futures/chart.md) | `/overseas-futureoption/chart` | POST | 4 | `o3103` `o3108` `o3117` `o3139` |

### 해외주식 (5개 API / 24개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[해외주식] 계좌](06-overseas-stock/account.md) | `/overseas-stock/accno` | POST | 4 | `COSAQ00102` `COSAQ01400` `COSOQ00201` `COSOQ02701` |
| [[해외주식] 시세](06-overseas-stock/market-data.md) | `/overseas-stock/market-data` | POST | 5 | `g3101` `g3102` `g3104` `g3106` `g3190` |
| [[해외주식] 실시간 시세](06-overseas-stock/realtime.md) | `/websocket/overseas-stock` | WS | 7 | `AS0` `AS1` `AS2` `AS3` `AS4` `GSH` `GSC` |
| [[해외주식] 주문](06-overseas-stock/orders.md) | `/overseas-stock/order` | POST | 4 | `COSAT00301` `COSAT00311` `COSMT00300` `COSAT00400` |
| [[해외주식] 차트](06-overseas-stock/chart.md) | `/overseas-stock/chart` | POST | 4 | `g3103` `g3202` `g3203` `g3204` |

### 기타 (2개 API / 3개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[기타] 시간조회](07-misc/server-time.md) | `/etc/time-search` | POST | 1 | `t0167` |
| [[기타] 실시간 시세](07-misc/realtime.md) | `/websocket/etc` | WS | 2 | `JIF` `NWS` |

### 실시간 시세 투자정보 (1개 API / 3개 TR)

| 문서 | URL | Method | TR 수 | TR코드 |
|---|---|---|---|---|
| [[실시간 시세 투자정보] 투자정보](08-realtime-invest-info/investment-info.md) | `/websocket/investinfo` | WS | 3 | `BMT` `CUR` `MK2` |

## 4. 유의사항

- 초당 전송 건수(TR 목록 표의 "개인/법인 초당 제한")를 반드시 준수. 초과 시 오류 또는 차단될 수 있음.
- 본 정의서와 포털 내용이 불일치하면 포털 원문이 우선하며, 해당 문서의 하단에 있는 포털 링크로 재확인 후 정의서를 갱신한다.
- 실시간(WebSocket) TR 의 응답 Body 는 push 로 수신되는 데이터 스키마이다.
