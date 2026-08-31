# [주식] 실시간 시세

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=9a2800c3-9bf2-4d67-8d83-905074f06646)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `9a2800c3-9bf2-4d67-8d83-905074f06646` |
| Protocol | WEBSOCKET |
| Method | POST |
| Domain | `wss://openapi.ls-sec.co.kr:9443` |
| URL | `/websocket/stock` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 주식 주문현황 및 시세, 투자정보를 실시간으로 확인할 수 있습니다. |

## TR 목록 (65건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| ETF호가잔량 | [B7_](realtime.md#tr-B7_) | - | - | - |
| KOSPI시간외단일가호가잔량 | [DH1](realtime.md#tr-DH1) | - | - | - |
| KOSDAQ시간외단일가호가잔량 | [DHA](realtime.md#tr-DHA) | - | - | - |
| KOSDAQ시간외단일가체결 | [DK3](realtime.md#tr-DK3) | - | - | - |
| KOSPI시간외단일가체결 | [DS3](realtime.md#tr-DS3) | - | - | - |
| 시간외단일가VI발동해제 | [DVI](realtime.md#tr-DVI) | - | - | - |
| KOSPI호가잔량 | [H1_](realtime.md#tr-H1_) | - | - | - |
| KOSPI장전시간외호가잔량 | [H2_](realtime.md#tr-H2_) | - | - | - |
| KOSDAQ호가잔량 | [HA_](realtime.md#tr-HA_) | - | - | - |
| KOSDAQ장전시간외호가잔량 | [HB_](realtime.md#tr-HB_) | - | - | - |
| 코스피ETF종목실시간NAV | [I5_](realtime.md#tr-I5_) | - | - | - |
| 지수 | [IJ_](realtime.md#tr-IJ_) | - | - | - |
| KOSPI거래원 | [K1_](realtime.md#tr-K1_) | - | - | - |
| KOSDAQ체결 | [K3_](realtime.md#tr-K3_) | - | - | - |
| KOSDAQ프로그램매매종목별 | [KH_](realtime.md#tr-KH_) | - | - | - |
| KOSDAQ프로그램매매전체집계 | [KM_](realtime.md#tr-KM_) | - | - | - |
| KOSDAQ우선호가 | [KS_](realtime.md#tr-KS_) | - | - | - |
| KOSDAQ거래원 | [OK_](realtime.md#tr-OK_) | - | - | - |
| KOSPI프로그램매매종목별 | [PH_](realtime.md#tr-PH_) | - | - | - |
| KOSPI프로그램매매전체집계 | [PM_](realtime.md#tr-PM_) | - | - | - |
| KOSPI우선호가 | [S2_](realtime.md#tr-S2_) | - | - | - |
| KOSPI체결 | [S3_](realtime.md#tr-S3_) | - | - | - |
| KOSPI기세 | [S4_](realtime.md#tr-S4_) | - | - | - |
| 주식주문접수 | [SC0](realtime.md#tr-SC0) | - | - | - |
| 주식주문체결 | [SC1](realtime.md#tr-SC1) | - | - | - |
| 주식주문정정 | [SC2](realtime.md#tr-SC2) | - | - | - |
| 주식주문취소 | [SC3](realtime.md#tr-SC3) | - | - | - |
| 주식주문거부 | [SC4](realtime.md#tr-SC4) | - | - | - |
| 상/하한가근접진입 | [SHC](realtime.md#tr-SHC) | - | - | - |
| 상/하한가근접이탈 | [SHD](realtime.md#tr-SHD) | - | - | - |
| 상/하한가진입 | [SHI](realtime.md#tr-SHI) | - | - | - |
| 상/하한가이탈 | [SHO](realtime.md#tr-SHO) | - | - | - |
| VI발동해제 | [VI_](realtime.md#tr-VI_) | - | - | - |
| 예상지수 | [YJ_](realtime.md#tr-YJ_) | - | - | - |
| KOSDAQ예상체결 | [YK3](realtime.md#tr-YK3) | - | - | - |
| KOSPI예상체결 | [YS3](realtime.md#tr-YS3) | - | - | - |
| 뉴ELW투자지표민감도 | [ESN](realtime.md#tr-ESN) | - | - | - |
| ELW장전시간외호가잔량 | [h2_](realtime.md#tr-h2_) | - | - | - |
| ELW호가잔량 | [h3_](realtime.md#tr-h3_) | - | - | - |
| ELW거래원 | [k1_](realtime.md#tr-k1_) | - | - | - |
| ELW우선호가 | [s2_](realtime.md#tr-s2_) | - | - | - |
| ELW체결 | [s3_](realtime.md#tr-s3_) | - | - | - |
| ELW기세 | [s4_](realtime.md#tr-s4_) | - | - | - |
| ELW예상체결 | [Ys3](realtime.md#tr-Ys3) | - | - | - |
| (NXT)체결 | [NS3](realtime.md#tr-NS3) | - | - | - |
| (NXT)호가잔량 | [NH1](realtime.md#tr-NH1) | - | - | - |
| (NXT)우선호가 | [NS2](realtime.md#tr-NS2) | - | - | - |
| (NXT)예상체결 | [NYS](realtime.md#tr-NYS) | - | - | - |
| (NXT)VI 발동 해제 | [NVI](realtime.md#tr-NVI) | - | - | - |
| (NXT)거래원 | [NK1](realtime.md#tr-NK1) | - | - | - |
| (NXT)프로그램매매종목별 | [NPH](realtime.md#tr-NPH) | - | - | - |
| (NXT)프로그램매매전체집계 | [NPM](realtime.md#tr-NPM) | - | - | - |
| (NXT)시간대별투자자매매추이 | [NBT](realtime.md#tr-NBT) | - | - | - |
| (NXT)업종별투자자별매매현황 | [NBM](realtime.md#tr-NBM) | - | - | - |
| (통합)체결 | [US3](realtime.md#tr-US3) | - | - | - |
| (통합)호가잔량 | [UH1](realtime.md#tr-UH1) | - | - | - |
| (통합)우선호가 | [US2](realtime.md#tr-US2) | - | - | - |
| (통합)예상체결 | [UYS](realtime.md#tr-UYS) | - | - | - |
| (통합)프로그램매매종목별 | [UPH](realtime.md#tr-UPH) | - | - | - |
| (통합)거래원 | [UK1](realtime.md#tr-UK1) | - | - | - |
| (통합)시간대별투자자매매추이 | [UBT](realtime.md#tr-UBT) | - | - | - |
| (통합) 업종별투자자별매매현황 | [UBM](realtime.md#tr-UBM) | - | - | - |
| (통합)프로그램매매전체집계 | [UPM](realtime.md#tr-UPM) | - | - | - |
| (통합)VI발동해제 | [UVI](realtime.md#tr-UVI) | - | - | - |
| API사용자조건검색실시간 | [AFR](realtime.md#tr-AFR) | - | - | - |

> **WebSocket 실시간 데이터**: 접속 도메인은 위 `Domain`(`wss://`)을 사용합니다.
> 접속 시 Header에 발급받은 `token`(접근토큰)을 설정하고, 각 TR 아래의 패킷 구조로 등록/해제(`tr_type`: 1 계좌등록, 2 계좌해제, 3 실시간 시세 등록, 4 실시간 시세 해제) 요청을 보냅니다. 실제 데이터는 동일 채널로 push 수신합니다.

---

<a id="tr-B7_"></a>
## `B7_` ETF호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `lp_offerho1` | LP매도호가수량1 | String | Y | 9 | - |
| `lp_bidho1` | LP매수호가수량1 | String | Y | 9 | - |
| `lp_offerho2` | LP매도호가수량2 | String | Y | 9 | - |
| `lp_bidho2` | LP매수호가수량2 | String | Y | 9 | - |
| `lp_offerho3` | LP매도호가수량3 | String | Y | 9 | - |
| `lp_bidho3` | LP매수호가수량3 | String | Y | 9 | - |
| `lp_offerho4` | LP매도호가수량4 | String | Y | 9 | - |
| `lp_bidho4` | LP매수호가수량4 | String | Y | 9 | - |
| `lp_offerho5` | LP매도호가수량5 | String | Y | 9 | - |
| `lp_bidho5` | LP매수호가수량5 | String | Y | 9 | - |
| `lp_offerho6` | LP매도호가수량6 | String | Y | 9 | - |
| `lp_bidho6` | LP매수호가수량6 | String | Y | 9 | - |
| `lp_offerho7` | LP매도호가수량7 | String | Y | 9 | - |
| `lp_bidho7` | LP매수호가수량7 | String | Y | 9 | - |
| `lp_offerho8` | LP매도호가수량8 | String | Y | 9 | - |
| `lp_bidho8` | LP매수호가수량8 | String | Y | 9 | - |
| `lp_offerho9` | LP매도호가수량9 | String | Y | 9 | - |
| `lp_bidho9` | LP매수호가수량9 | String | Y | 9 | - |
| `lp_offerho10` | LP매도호가수량10 | String | Y | 9 | - |
| `lp_bidho10` | LP매수호가수량10 | String | Y | 9 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | String | Y | 7 | - |
| `bidho1` | 매수호가1 | String | Y | 7 | - |
| `offerrem1` | 매도호가잔량1 | String | Y | 9 | - |
| `bidrem1` | 매수호가잔량1 | String | Y | 9 | - |
| `offerho2` | 매도호가2 | String | Y | 7 | - |
| `bidho2` | 매수호가2 | String | Y | 7 | - |
| `offerrem2` | 매도호가잔량2 | String | Y | 9 | - |
| `bidrem2` | 매수호가잔량2 | String | Y | 9 | - |
| `offerho3` | 매도호가3 | String | Y | 7 | - |
| `bidho3` | 매수호가3 | String | Y | 7 | - |
| `offerrem3` | 매도호가잔량3 | String | Y | 9 | - |
| `bidrem3` | 매수호가잔량3 | String | Y | 9 | - |
| `offerho4` | 매도호가4 | String | Y | 7 | - |
| `bidho4` | 매수호가4 | String | Y | 7 | - |
| `offerrem4` | 매도호가잔량4 | String | Y | 9 | - |
| `bidrem4` | 매수호가잔량4 | String | Y | 9 | - |
| `offerho5` | 매도호가5 | String | Y | 7 | - |
| `bidho5` | 매수호가5 | String | Y | 7 | - |
| `offerrem5` | 매도호가잔량5 | String | Y | 9 | - |
| `bidrem5` | 매수호가잔량5 | String | Y | 9 | - |
| `offerho6` | 매도호가6 | String | Y | 7 | - |
| `bidho6` | 매수호가6 | String | Y | 7 | - |
| `offerrem6` | 매도호가잔량6 | String | Y | 9 | - |
| `bidrem6` | 매수호가잔량6 | String | Y | 9 | - |
| `offerho7` | 매도호가7 | String | Y | 7 | - |
| `bidho7` | 매수호가7 | String | Y | 7 | - |
| `offerrem7` | 매도호가잔량7 | String | Y | 9 | - |
| `bidrem7` | 매수호가잔량7 | String | Y | 9 | - |
| `offerho8` | 매도호가8 | String | Y | 7 | - |
| `bidho8` | 매수호가8 | String | Y | 7 | - |
| `offerrem8` | 매도호가잔량8 | String | Y | 9 | - |
| `bidrem8` | 매수호가잔량8 | String | Y | 9 | - |
| `offerho9` | 매도호가9 | String | Y | 7 | - |
| `bidho9` | 매수호가9 | String | Y | 7 | - |
| `offerrem9` | 매도호가잔량9 | String | Y | 9 | - |
| `bidrem9` | 매수호가잔량9 | String | Y | 9 | - |
| `offerho10` | 매도호가10 | String | Y | 7 | - |
| `bidho10` | 매수호가10 | String | Y | 7 | - |
| `offerrem10` | 매도호가잔량10 | String | Y | 9 | - |
| `bidrem10` | 매수호가잔량10 | String | Y | 9 | - |
| `totofferrem` | 총매도호가잔량 | String | Y | 9 | - |
| `totbidrem` | 총매수호가잔량 | String | Y | 9 | - |
| `donsigubun` | 동시호가구분 | String | Y | 1 | - |
| `alloc_gubun` | 배분적용구분 | String | Y | 1 | - |
| `midprice` | 중간가격 | String | Y | 8 | - |
| `offermidsumrem` | 매도중간가잔량합계수량 | String | Y | 9 | - |
| `bidmidsumrem` | 매수중간가잔량합계수량 | String | Y | 9 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "B7_",
  "tr_key": "069500"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "B7_",
  "tr_key": "069500"
 },
 "body": {
  "offerho4": "0",
  "offerho3": "34730",
  "offerho6": "0",
  "offerho5": "0",
  "offerho8": "0",
  "offerho7": "0",
  "offerho9": "0",
  "lp_bidho5": "0",
  "lp_bidho6": "0",
  "lp_bidho7": "0",
  "lp_bidho8": "0",
  "lp_bidho1": "0",
  "lp_bidho2": "0",
  "donsigubun": "3",
  "lp_bidho3": "0",
  "lp_bidho4": "0",
  "lp_bidho9": "0",
  "hotime": "084748",
  "offerho2": "34725",
  "offerho1": "34720",
  "lp_offerho9": "0",
  "lp_offerho8": "0",
  "offerho10": "0",
  "lp_offerho3": "0",
  "lp_offerho2": "0",
  "lp_offerho1": "0",
  "totofferrem": "0",
  "lp_offerho7": "0",
  "lp_offerho6": "0",
  "lp_offerho5": "0",
  "lp_offerho4": "0",
  "totbidrem": "0",
  "offerrem2": "12775",
  "bidho5": "0",
  "offerrem3": "10",
  "bidho4": "0",
  "offerrem4": "0",
  "bidho7": "0",
  "offerrem5": "0",
  "bidho6": "0",
  "bidho9": "0",
  "bidho8": "0",
  "offerrem1": "9399",
  "offerrem6": "0",
  "offerrem7": "0",
  "offerrem8": "0",
  "offerrem9": "0",
  "bidrem3": "10020",
  "bidrem4": "0",
  "bidrem1": "2957",
  "bidrem2": "1000",
  "lp_bidho10": "0",
  "bidrem9": "0",
  "bidho1": "34700",
  "bidrem7": "0",
  "bidrem8": "0",
  "bidho3": "34675",
  "bidrem5": "0",
  "bidho2": "34680",
  "bidrem6": "0",
  "bidrem10": "0",
  "bidho10": "0",
  "shcode": "069500",
  "alloc_gubun": "",
  "lp_offerho10": "0",
  "offerrem10": "0"
 }
}
```

---

<a id="tr-DH1"></a>
## `DH1` KOSPI시간외단일가호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `dan_hotime` | 시간외단일가호가시간 | String | Y | 6 | - |
| `dan_hstatus` | 시간외단일가장구분 | String | Y | 2 | - |
| `dan_offerho1` | 시간외단일가매도호가1 | String | Y | 8 | - |
| `dan_bidho1` | 시간외단일가매수호가1 | String | Y | 8 | - |
| `dan_offerrem1` | 시간외단일가매도호가잔량1 | String | Y | 12 | - |
| `dan_bidrem1` | 시간외단일가매수호가잔량1 | String | Y | 12 | - |
| `dan_preoffercha1` | 시간외단일가직전매도대비수량1 | String | Y | 12 | - |
| `dan_prebidcha1` | 시간외단일가직전매수대비수량1 | String | Y | 12 | - |
| `dan_offerho2` | 시간외단일가매도호가2 | String | Y | 8 | - |
| `dan_bidho2` | 시간외단일가매수호가2 | String | Y | 8 | - |
| `dan_offerrem2` | 시간외단일가매도호가잔량2 | String | Y | 12 | - |
| `dan_bidrem2` | 시간외단일가매수호가잔량2 | String | Y | 12 | - |
| `dan_preoffercha2` | 시간외단일가직전매도대비수량2 | String | Y | 12 | - |
| `dan_prebidcha2` | 시간외단일가직전매수대비수량2 | String | Y | 12 | - |
| `dan_offerho3` | 시간외단일가매도호가3 | String | Y | 8 | - |
| `dan_bidho3` | 시간외단일가매수호가3 | String | Y | 8 | - |
| `dan_offerrem3` | 시간외단일가매도호가잔량3 | String | Y | 12 | - |
| `dan_bidrem3` | 시간외단일가매수호가잔량3 | String | Y | 12 | - |
| `dan_preoffercha3` | 시간외단일가직전매도대비수량3 | String | Y | 12 | - |
| `dan_prebidcha3` | 시간외단일가직전매수대비수량3 | String | Y | 12 | - |
| `dan_offerho4` | 시간외단일가매도호가4 | String | Y | 8 | - |
| `dan_bidho4` | 시간외단일가매수호가4 | String | Y | 8 | - |
| `dan_offerrem4` | 시간외단일가매도호가잔량4 | String | Y | 12 | - |
| `dan_bidrem4` | 시간외단일가매수호가잔량4 | String | Y | 12 | - |
| `dan_preoffercha4` | 시간외단일가직전매도대비수량4 | String | Y | 12 | - |
| `dan_prebidcha4` | 시간외단일가직전매수대비수량4 | String | Y | 12 | - |
| `dan_offerho5` | 시간외단일가매도호가5 | String | Y | 8 | - |
| `dan_bidho5` | 시간외단일가매수호가5 | String | Y | 8 | - |
| `dan_offerrem5` | 시간외단일가매도호가잔량5 | String | Y | 12 | - |
| `dan_bidrem5` | 시간외단일가매수호가잔량5 | String | Y | 12 | - |
| `dan_preoffercha5` | 시간외단일가직전매도대비수량5 | String | Y | 12 | - |
| `dan_prebidcha5` | 시간외단일가직전매수대비수량5 | String | Y | 12 | - |
| `dan_totofferrem` | 시간외단일가총매도호가잔량 | String | Y | 12 | - |
| `dan_totbidrem` | 시간외단일가총매수호가잔량 | String | Y | 12 | - |
| `dan_preoffercha` | 시간외단일가직전매도호가총대비수량 | String | Y | 12 | - |
| `dan_prebidcha` | 시간외단일가직전매수호가총대비수량 | String | Y | 12 | - |
| `dan_yeprice` | 시간외단일가예상체결가격 | String | Y | 8 | - |
| `dan_yevolume` | 시간외단일가예상체결수량 | String | Y | 12 | - |
| `dan_preysign` | 시간외단일가예상가직전가대비구분 | String | Y | 1 | - |
| `dan_preychange` | 시간외단일가예상가직전가대비 | String | Y | 8 | - |
| `dan_jnilysign` | 시간외단일가예상가전일가대비구분 | String | Y | 1 | - |
| `dan_jnilychange` | 시간외단일가예상가전일가대비 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "DH1",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "DH1",
  "tr_key": "005930"
 },
 "body": {
  "dan_bidrem2": "5282",
  "dan_bidrem1": "7165",
  "dan_preychange": "0",
  "dan_totbidrem": "18672",
  "dan_jnilychange": "0",
  "dan_bidrem5": "0",
  "dan_totofferrem": "38889",
  "dan_bidrem4": "0",
  "dan_bidrem3": "6225",
  "dan_prebidcha1": "0",
  "dan_offerho5": "0",
  "dan_prebidcha2": "2",
  "dan_prebidcha3": "0",
  "dan_hotime": "162616",
  "dan_hstatus": "01",
  "dan_bidho1": "72000",
  "dan_preoffercha2": "0",
  "dan_bidho3": "71800",
  "dan_preoffercha1": "0",
  "dan_bidho2": "71900",
  "dan_preoffercha4": "0",
  "dan_bidho5": "0",
  "dan_preoffercha": "0",
  "dan_preoffercha3": "0",
  "dan_bidho4": "0",
  "dan_preoffercha5": "0",
  "dan_yeprice": "72000",
  "dan_preysign": "3",
  "shcode": "005930",
  "dan_offerho2": "72200",
  "dan_prebidcha4": "0",
  "dan_offerho1": "72100",
  "dan_prebidcha5": "0",
  "dan_offerho4": "0",
  "dan_offerho3": "72300",
  "dan_offerrem4": "0",
  "volume": "629",
  "dan_offerrem5": "0",
  "dan_jnilysign": "3",
  "dan_prebidcha": "2",
  "dan_yevolume": "629",
  "dan_offerrem1": "14973",
  "dan_offerrem2": "12248",
  "dan_offerrem3": "11668"
 }
}
```

---

<a id="tr-DHA"></a>
## `DHA` KOSDAQ시간외단일가호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `dan_hotime` | 시간외단일가호가시간 | String | Y | 6 | - |
| `dan_hstatus` | 시간외단일가장구분 | String | Y | 2 | - |
| `dan_offerho1` | 시간외단일가매도호가1 | String | Y | 8 | - |
| `dan_bidho1` | 시간외단일가매수호가1 | String | Y | 8 | - |
| `dan_offerrem1` | 시간외단일가매도호가잔량1 | String | Y | 12 | - |
| `dan_bidrem1` | 시간외단일가매수호가잔량1 | String | Y | 12 | - |
| `dan_preoffercha1` | 시간외단일가직전매도대비수량1 | String | Y | 12 | - |
| `dan_prebidcha1` | 시간외단일가직전매수대비수량1 | String | Y | 12 | - |
| `dan_offerho2` | 시간외단일가매도호가2 | String | Y | 8 | - |
| `dan_bidho2` | 시간외단일가매수호가2 | String | Y | 8 | - |
| `dan_offerrem2` | 시간외단일가매도호가잔량2 | String | Y | 12 | - |
| `dan_bidrem2` | 시간외단일가매수호가잔량2 | String | Y | 12 | - |
| `dan_preoffercha2` | 시간외단일가직전매도대비수량2 | String | Y | 12 | - |
| `dan_prebidcha2` | 시간외단일가직전매수대비수량2 | String | Y | 12 | - |
| `dan_offerho3` | 시간외단일가매도호가3 | String | Y | 8 | - |
| `dan_bidho3` | 시간외단일가매수호가3 | String | Y | 8 | - |
| `dan_offerrem3` | 시간외단일가매도호가잔량3 | String | Y | 12 | - |
| `dan_bidrem3` | 시간외단일가매수호가잔량3 | String | Y | 12 | - |
| `dan_preoffercha3` | 시간외단일가직전매도대비수량3 | String | Y | 12 | - |
| `dan_prebidcha3` | 시간외단일가직전매수대비수량3 | String | Y | 12 | - |
| `dan_offerho4` | 시간외단일가매도호가4 | String | Y | 8 | - |
| `dan_bidho4` | 시간외단일가매수호가4 | String | Y | 8 | - |
| `dan_offerrem4` | 시간외단일가매도호가잔량4 | String | Y | 12 | - |
| `dan_bidrem4` | 시간외단일가매수호가잔량4 | String | Y | 12 | - |
| `dan_preoffercha4` | 시간외단일가직전매도대비수량4 | String | Y | 12 | - |
| `dan_prebidcha4` | 시간외단일가직전매수대비수량4 | String | Y | 12 | - |
| `dan_offerho5` | 시간외단일가매도호가5 | String | Y | 8 | - |
| `dan_bidho5` | 시간외단일가매수호가5 | String | Y | 8 | - |
| `dan_offerrem5` | 시간외단일가매도호가잔량5 | String | Y | 12 | - |
| `dan_bidrem5` | 시간외단일가매수호가잔량5 | String | Y | 12 | - |
| `dan_preoffercha5` | 시간외단일가직전매도대비수량5 | String | Y | 12 | - |
| `dan_prebidcha5` | 시간외단일가직전매수대비수량5 | String | Y | 12 | - |
| `dan_totofferrem` | 시간외단일가총매도호가잔량 | String | Y | 12 | - |
| `dan_totbidrem` | 시간외단일가총매수호가잔량 | String | Y | 12 | - |
| `dan_preoffercha` | 시간외단일가직전매도호가총대비수량 | String | Y | 12 | - |
| `dan_prebidcha` | 시간외단일가직전매수호가총대비수량 | String | Y | 12 | - |
| `dan_yeprice` | 시간외단일가예상체결가격 | String | Y | 8 | - |
| `dan_yevolume` | 시간외단일가예상체결수량 | String | Y | 12 | - |
| `dan_preysign` | 시간외단일가예상가직전가대비구분 | String | Y | 1 | - |
| `dan_preychange` | 시간외단일가예상가직전가대비 | String | Y | 8 | - |
| `dan_jnilysign` | 시간외단일가예상가전일가대비구분 | String | Y | 1 | - |
| `dan_jnilychange` | 시간외단일가예상가전일가대비 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "DHA",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "DHA",
  "tr_key": "086520"
 },
 "body": {
  "dan_bidrem2": "441",
  "dan_bidrem1": "318",
  "dan_preychange": "1000",
  "dan_totbidrem": "937",
  "dan_jnilychange": "-4000",
  "dan_bidrem5": "0",
  "dan_totofferrem": "1080",
  "dan_bidrem4": "0",
  "dan_bidrem3": "178",
  "dan_prebidcha1": "0",
  "dan_offerho5": "0",
  "dan_prebidcha2": "0",
  "dan_prebidcha3": "0",
  "dan_hotime": "162755",
  "dan_hstatus": "01",
  "dan_bidho1": "745000",
  "dan_preoffercha2": "0",
  "dan_bidho3": "743000",
  "dan_preoffercha1": "-2",
  "dan_bidho2": "744000",
  "dan_preoffercha4": "0",
  "dan_bidho5": "0",
  "dan_preoffercha": "-2",
  "dan_preoffercha3": "0",
  "dan_bidho4": "0",
  "dan_preoffercha5": "0",
  "dan_yeprice": "745000",
  "dan_preysign": "5",
  "shcode": "086520",
  "dan_offerho2": "747000",
  "dan_prebidcha4": "0",
  "dan_offerho1": "746000",
  "dan_prebidcha5": "0",
  "dan_offerho4": "0",
  "dan_offerho3": "748000",
  "dan_offerrem4": "0",
  "volume": "3801",
  "dan_offerrem5": "0",
  "dan_jnilysign": "5",
  "dan_prebidcha": "0",
  "dan_yevolume": "928",
  "dan_offerrem1": "608",
  "dan_offerrem2": "192",
  "dan_offerrem3": "280"
 }
}
```

---

<a id="tr-DK3"></a>
## `DK3` KOSDAQ시간외단일가체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `dan_chetime` | 시간외단일가체결시간 | String | Y | 6 | - |
| `dan_sign` | 시간외단일가전일대비구분 | String | Y | 1 | - |
| `dan_change` | 시간외단일가전일대비 | String | Y | 8 | - |
| `dan_drate` | 시간외단일가등락율 | String | Y | 6.2 | - |
| `dan_price` | 시간외단일가현재가 | String | Y | 8 | - |
| `dan_opentime` | 시간외단일가시가시간 | String | Y | 6 | - |
| `dan_open` | 시간외단일가시가 | String | Y | 8 | - |
| `dan_hightime` | 시간외단일가고가시간 | String | Y | 6 | - |
| `dan_high` | 시간외단일가고가 | String | Y | 8 | - |
| `dan_lowtime` | 시간외단일가저가시간 | String | Y | 6 | - |
| `dan_low` | 시간외단일가저가 | String | Y | 8 | - |
| `dan_cgubun` | 시간외단일가체결구분 | String | Y | 1 | - |
| `dan_cvolume` | 시간외단일가체결량 | String | Y | 8 | - |
| `dan_volume` | 시간외단일가누적거래량 | String | Y | 12 | - |
| `dan_value` | 시간외단일가누적거래대금 | String | Y | 12 | - |
| `dan_mdvolume` | 시간외단일가매도누적체결량 | String | Y | 12 | - |
| `dan_mdchecnt` | 시간외단일가매도누적체결건수 | String | Y | 8 | - |
| `dan_msvolume` | 시간외단일가매수누적체결량 | String | Y | 12 | - |
| `dan_mschecnt` | 시간외단일가매수누적체결건수 | String | Y | 8 | - |
| `dan_prevolume` | 시간외단일가직전거래량 | String | Y | 8 | - |
| `dan_precvolume` | 시간외단일가직전체결수량 | String | Y | 8 | - |
| `dan_cpower` | 시간외단일가체결강도 | String | Y | 9.2 | - |
| `dan_status` | 시간외단일가장정보 | String | Y | 2 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "DK3",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "DK3",
  "tr_key": "086520"
 },
 "body": {
  "dan_value": "4431",
  "dan_high": "749000",
  "dan_mdvolume": "0",
  "dan_hightime": "161008",
  "dan_mdchecnt": "0",
  "shcode": "086520",
  "dan_precvolume": "986",
  "dan_price": "746000",
  "dan_open": "749000",
  "dan_cpower": "0.00",
  "dan_volume": "5930",
  "dan_prevolume": "4787",
  "dan_low": "745000",
  "dan_chetime": "164002",
  "dan_change": "3000",
  "dan_mschecnt": "0",
  "dan_cgubun": "",
  "dan_msvolume": "0",
  "dan_drate": "-0.40",
  "dan_cvolume": "1143",
  "dan_sign": "5",
  "dan_lowtime": "163017",
  "dan_status": "01",
  "dan_opentime": "161008"
 }
}
```

---

<a id="tr-DS3"></a>
## `DS3` KOSPI시간외단일가체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `dan_chetime` | 시간외단일가체결시간 | String | Y | 6 | - |
| `dan_sign` | 시간외단일가전일대비구분 | String | Y | 1 | - |
| `dan_change` | 시간외단일가전일대비 | String | Y | 8 | - |
| `dan_drate` | 시간외단일가등락율 | String | Y | 6.2 | - |
| `dan_price` | 시간외단일가현재가 | String | Y | 8 | - |
| `dan_opentime` | 시간외단일가시가시간 | String | Y | 6 | - |
| `dan_open` | 시간외단일가시가 | String | Y | 8 | - |
| `dan_hightime` | 시간외단일가고가시간 | String | Y | 6 | - |
| `dan_high` | 시간외단일가고가 | String | Y | 8 | - |
| `dan_lowtime` | 시간외단일가저가시간 | String | Y | 6 | - |
| `dan_low` | 시간외단일가저가 | String | Y | 8 | - |
| `dan_cgubun` | 시간외단일가체결구분 | String | Y | 1 | - |
| `dan_cvolume` | 시간외단일가체결량 | String | Y | 8 | - |
| `dan_volume` | 시간외단일가누적거래량 | String | Y | 12 | - |
| `dan_value` | 시간외단일가누적거래대금 | String | Y | 12 | - |
| `dan_mdvolume` | 시간외단일가매도누적체결량 | String | Y | 12 | - |
| `dan_mdchecnt` | 시간외단일가매도누적체결건수 | String | Y | 8 | - |
| `dan_msvolume` | 시간외단일가매수누적체결량 | String | Y | 12 | - |
| `dan_mschecnt` | 시간외단일가매수누적체결건수 | String | Y | 8 | - |
| `dan_prevolume` | 시간외단일가직전거래량 | String | Y | 8 | - |
| `dan_precvolume` | 시간외단일가직전체결수량 | String | Y | 8 | - |
| `dan_cpower` | 시간외단일가체결강도 | String | Y | 9.2 | - |
| `dan_status` | 시간외단일가장정보 | String | Y | 2 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "DS3",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "DS3",
  "tr_key": "005930"
 },
 "body": {
  "dan_value": "1201",
  "dan_high": "72000",
  "dan_mdvolume": "0",
  "dan_hightime": "161009",
  "dan_mdchecnt": "0",
  "shcode": "005930",
  "dan_precvolume": "10250",
  "dan_price": "72000",
  "dan_open": "72000",
  "dan_cpower": "0.00",
  "dan_volume": "16692",
  "dan_prevolume": "15432",
  "dan_low": "71900",
  "dan_chetime": "164030",
  "dan_change": "0",
  "dan_mschecnt": "0",
  "dan_cgubun": "",
  "dan_msvolume": "0",
  "dan_drate": "0.00",
  "dan_cvolume": "1260",
  "dan_sign": "3",
  "dan_lowtime": "163002",
  "dan_status": "47",
  "dan_opentime": "161009"
 }
}
```

---

<a id="tr-DVI"></a>
## `DVI` 시간외단일가VI발동해제

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 6 | 단축코드 6자리 또는 전체종목 '000000' |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `vi_gubun` | 구분(0:해제 1:정적발동 2:동적발동 3:정적&동적) | String | Y | 1 | - |
| `svi_recprice` | 정적VI발동기준가격 | String | Y | 8 | - |
| `dvi_recprice` | 동적VI발동기준가격 | String | Y | 8 | - |
| `vi_trgprice` | VI발동가격 | String | Y | 8 | - |
| `shcode` | 단축코드(KEY) | String | Y | 6 | - |
| `ref_shcode` | 참조코드(미사용) | String | Y | 6 | - |
| `time` | 시간 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "DVI",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "DVI",
  "tr_key": "145270"
 },
 "body": {
  "svi_recprice": "0",
  "vi_gubun": "0",
  "shcode": "145270",
  "time": "092415",
  "vi_trgprice": "0",
  "dvi_recprice": "0",
  "ref_shcode": "145270"
 }
}
```

---

<a id="tr-H1_"></a>
## `H1_` KOSPI호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | String | Y | 7 | - |
| `bidho1` | 매수호가1 | String | Y | 7 | - |
| `offerrem1` | 매도호가잔량1 | String | Y | 9 | - |
| `bidrem1` | 매수호가잔량1 | String | Y | 9 | - |
| `offerho2` | 매도호가2 | String | Y | 7 | - |
| `bidho2` | 매수호가2 | String | Y | 7 | - |
| `offerrem2` | 매도호가잔량2 | String | Y | 9 | - |
| `bidrem2` | 매수호가잔량2 | String | Y | 9 | - |
| `offerho3` | 매도호가3 | String | Y | 7 | - |
| `bidho3` | 매수호가3 | String | Y | 7 | - |
| `offerrem3` | 매도호가잔량3 | String | Y | 9 | - |
| `bidrem3` | 매수호가잔량3 | String | Y | 9 | - |
| `offerho4` | 매도호가4 | String | Y | 7 | - |
| `bidho4` | 매수호가4 | String | Y | 7 | - |
| `offerrem4` | 매도호가잔량4 | String | Y | 9 | - |
| `bidrem4` | 매수호가잔량4 | String | Y | 9 | - |
| `offerho5` | 매도호가5 | String | Y | 7 | - |
| `bidho5` | 매수호가5 | String | Y | 7 | - |
| `offerrem5` | 매도호가잔량5 | String | Y | 9 | - |
| `bidrem5` | 매수호가잔량5 | String | Y | 9 | - |
| `offerho6` | 매도호가6 | String | Y | 7 | - |
| `bidho6` | 매수호가6 | String | Y | 7 | - |
| `offerrem6` | 매도호가잔량6 | String | Y | 9 | - |
| `bidrem6` | 매수호가잔량6 | String | Y | 9 | - |
| `offerho7` | 매도호가7 | String | Y | 7 | - |
| `bidho7` | 매수호가7 | String | Y | 7 | - |
| `offerrem7` | 매도호가잔량7 | String | Y | 9 | - |
| `bidrem7` | 매수호가잔량7 | String | Y | 9 | - |
| `offerho8` | 매도호가8 | String | Y | 7 | - |
| `bidho8` | 매수호가8 | String | Y | 7 | - |
| `offerrem8` | 매도호가잔량8 | String | Y | 9 | - |
| `bidrem8` | 매수호가잔량8 | String | Y | 9 | - |
| `offerho9` | 매도호가9 | String | Y | 7 | - |
| `bidho9` | 매수호가9 | String | Y | 7 | - |
| `offerrem9` | 매도호가잔량9 | String | Y | 9 | - |
| `bidrem9` | 매수호가잔량9 | String | Y | 9 | - |
| `offerho10` | 매도호가10 | String | Y | 7 | - |
| `bidho10` | 매수호가10 | String | Y | 7 | - |
| `offerrem10` | 매도호가잔량10 | String | Y | 9 | - |
| `bidrem10` | 매수호가잔량10 | String | Y | 9 | - |
| `totofferrem` | 총매도호가잔량 | String | Y | 9 | - |
| `totbidrem` | 총매수호가잔량 | String | Y | 9 | - |
| `donsigubun` | 동시호가구분 | String | Y | 1 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `alloc_gubun` | 배분적용구분 | String | Y | 1 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `midprice` | 중간가격 | String | Y | 8 | - |
| `offermidsumrem` | 매도중간가잔량합계수량 | String | Y | 9 | - |
| `bidmidsumrem` | 매수중간가잔량합계수량 | String | Y | 9 | - |
| `midsumrem` | 중간가잔량합계수량 | String | Y | 9 | - |
| `midsumremgubun` | 중간가잔량구분 | String | Y | 1 | ' '없음<br/>'1'매도<br/>'2'매수<br/> |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "H1_",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "H1_",
  "tr_key": "005930"
 },
 "body": {
  "offerrem2": "66102",
  "offerho4": "0",
  "bidho5": "0",
  "offerho3": "72600",
  "offerrem3": "74102",
  "bidho4": "0",
  "offerrem4": "0",
  "offerho6": "0",
  "bidho7": "0",
  "offerho5": "0",
  "offerrem5": "0",
  "bidho6": "0",
  "offerho8": "0",
  "bidho9": "0",
  "offerho7": "0",
  "bidho8": "0",
  "offerrem1": "32616",
  "offerho9": "0",
  "offerrem6": "0",
  "offerrem7": "0",
  "donsigubun": "3",
  "offerrem8": "0",
  "offerrem9": "0",
  "bidrem3": "156534",
  "bidrem4": "0",
  "bidrem1": "70581",
  "bidrem2": "100447",
  "bidrem9": "0",
  "bidho1": "72300",
  "bidrem7": "0",
  "bidrem8": "0",
  "hotime": "084242",
  "offerho2": "72500",
  "bidho3": "72100",
  "bidrem5": "0",
  "offerho1": "72400",
  "bidho2": "72200",
  "bidrem6": "0",
  "bidrem10": "0",
  "bidho10": "0",
  "shcode": "005930",
  "alloc_gubun": "",
  "volume": "136",
  "offerho10": "0",
  "offerrem10": "0",
  "totofferrem": "0",
  "totbidrem": "0"
 }
}
```

---

<a id="tr-H2_"></a>
## `H2_` KOSPI장전시간외호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `tmofferrem` | 시간외매도잔량 | String | Y | 12 | - |
| `tmbidrem` | 시간외매수잔량 | String | Y | 12 | - |
| `pretmoffercha` | 시간외매도수량직전대비 | String | Y | 12 | - |
| `pretmbidcha` | 시간외매수수량직전대비 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "H2_",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "H2_",
  "tr_key": "005930"
 },
 "body": {
  "tmbidrem": "11196",
  "shcode": "005930",
  "pretmoffercha": "0",
  "pretmbidcha": "1",
  "tmofferrem": "0",
  "hotime": "083419"
 }
}
```

---

<a id="tr-HA_"></a>
## `HA_` KOSDAQ호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | String | Y | 7 | - |
| `bidho1` | 매수호가1 | String | Y | 7 | - |
| `offerrem1` | 매도호가잔량1 | String | Y | 9 | - |
| `bidrem1` | 매수호가잔량1 | String | Y | 9 | - |
| `offerho2` | 매도호가2 | String | Y | 7 | - |
| `bidho2` | 매수호가2 | String | Y | 7 | - |
| `offerrem2` | 매도호가잔량2 | String | Y | 9 | - |
| `bidrem2` | 매수호가잔량2 | String | Y | 9 | - |
| `offerho3` | 매도호가3 | String | Y | 7 | - |
| `bidho3` | 매수호가3 | String | Y | 7 | - |
| `offerrem3` | 매도호가잔량3 | String | Y | 9 | - |
| `bidrem3` | 매수호가잔량3 | String | Y | 9 | - |
| `offerho4` | 매도호가4 | String | Y | 7 | - |
| `bidho4` | 매수호가4 | String | Y | 7 | - |
| `offerrem4` | 매도호가잔량4 | String | Y | 9 | - |
| `bidrem4` | 매수호가잔량4 | String | Y | 9 | - |
| `offerho5` | 매도호가5 | String | Y | 7 | - |
| `bidho5` | 매수호가5 | String | Y | 7 | - |
| `offerrem5` | 매도호가잔량5 | String | Y | 9 | - |
| `bidrem5` | 매수호가잔량5 | String | Y | 9 | - |
| `offerho6` | 매도호가6 | String | Y | 7 | - |
| `bidho6` | 매수호가6 | String | Y | 7 | - |
| `offerrem6` | 매도호가잔량6 | String | Y | 9 | - |
| `bidrem6` | 매수호가잔량6 | String | Y | 9 | - |
| `offerho7` | 매도호가7 | String | Y | 7 | - |
| `bidho7` | 매수호가7 | String | Y | 7 | - |
| `offerrem7` | 매도호가잔량7 | String | Y | 9 | - |
| `bidrem7` | 매수호가잔량7 | String | Y | 9 | - |
| `offerho8` | 매도호가8 | String | Y | 7 | - |
| `bidho8` | 매수호가8 | String | Y | 7 | - |
| `offerrem8` | 매도호가잔량8 | String | Y | 9 | - |
| `bidrem8` | 매수호가잔량8 | String | Y | 9 | - |
| `offerho9` | 매도호가9 | String | Y | 7 | - |
| `bidho9` | 매수호가9 | String | Y | 7 | - |
| `offerrem9` | 매도호가잔량9 | String | Y | 9 | - |
| `bidrem9` | 매수호가잔량9 | String | Y | 9 | - |
| `offerho10` | 매도호가10 | String | Y | 7 | - |
| `bidho10` | 매수호가10 | String | Y | 7 | - |
| `offerrem10` | 매도호가잔량10 | String | Y | 9 | - |
| `bidrem10` | 매수호가잔량10 | String | Y | 9 | - |
| `totofferrem` | 총매도호가잔량 | String | Y | 9 | - |
| `totbidrem` | 총매수호가잔량 | String | Y | 9 | - |
| `donsigubun` | 동시호가구분 | String | Y | 1 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `alloc_gubun` | 배분적용구분 | String | Y | 1 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `midprice` | 중간가격 | String | Y | 8 | - |
| `offermidsumrem` | 매도중간가잔량합계수량 | String | Y | 9 | - |
| `bidmidsumrem` | 매수중간가잔량합계수량 | String | Y | 9 | - |
| `midsumrem` | 중간가잔량합계수량 | String | Y | 9 | - |
| `midsumremgubun` | 중간가잔량구분 | String | Y | 1 | ' '없음<br/>'1'매도<br/>'2'매수 |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "HA_",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "HA_",
  "tr_key": "086520"
 },
 "body": {
  "offerrem2": "1081",
  "offerho4": "0",
  "bidho5": "0",
  "offerho3": "765000",
  "offerrem3": "1082",
  "bidho4": "0",
  "offerrem4": "0",
  "offerho6": "0",
  "bidho7": "0",
  "offerho5": "0",
  "offerrem5": "0",
  "bidho6": "0",
  "offerho8": "0",
  "bidho9": "0",
  "offerho7": "0",
  "bidho8": "0",
  "offerrem1": "560",
  "offerho9": "0",
  "offerrem6": "0",
  "offerrem7": "0",
  "donsigubun": "3",
  "offerrem8": "0",
  "offerrem9": "0",
  "bidrem3": "1438",
  "bidrem4": "0",
  "bidrem1": "286",
  "bidrem2": "14",
  "bidrem9": "0",
  "bidho1": "762000",
  "bidrem7": "0",
  "bidrem8": "0",
  "hotime": "084312",
  "offerho2": "764000",
  "bidho3": "760000",
  "bidrem5": "0",
  "offerho1": "763000",
  "bidho2": "761000",
  "bidrem6": "0",
  "bidrem10": "0",
  "bidho10": "0",
  "shcode": "086520",
  "alloc_gubun": "",
  "volume": "672",
  "offerho10": "0",
  "offerrem10": "0",
  "totofferrem": "0",
  "totbidrem": "0"
 }
}
```

---

<a id="tr-HB_"></a>
## `HB_` KOSDAQ장전시간외호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `tmofferrem` | 시간외매도잔량 | String | Y | 12 | - |
| `tmbidrem` | 시간외매수잔량 | String | Y | 12 | - |
| `pretmoffercha` | 시간외매도수량직전대비 | String | Y | 12 | - |
| `pretmbidcha` | 시간외매수수량직전대비 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "HB_",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "HB_",
  "tr_key": "086520"
 },
 "body": {
  "tmbidrem": "6124",
  "shcode": "086520",
  "pretmoffercha": "0",
  "pretmbidcha": "1",
  "tmofferrem": "0",
  "hotime": "083357"
 }
}
```

---

<a id="tr-I5_"></a>
## `I5_` 코스피ETF종목실시간NAV

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 시간 | String | Y | 8 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `navdiff` | NAV대비 | String | Y | 9.2 | - |
| `nav` | NAV | String | Y | 9.2 | - |
| `navchange` | 전일대비 | String | Y | 9.2 | - |
| `crate` | 추적오차 | String | Y | 9.2 | - |
| `grate` | 괴리 | String | Y | 9.2 | - |
| `jisu` | 지수 | String | Y | 8.2 | - |
| `jichange` | 전일대비 | String | Y | 8.2 | - |
| `jirate` | 전일대비율 | String | Y | 8.2 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "I5_",
  "tr_key": "069500"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "I5_",
  "tr_key": "069500"
 },
 "body": {
  "jirate": "-0.29",
  "nav": "34463.58",
  "navchange": "-99.59",
  "change": "70",
  "grate": "-0.10",
  "shcode": "069500",
  "sign": "5",
  "navdiff": "-0.29",
  "crate": "0.00",
  "jichange": "0.99",
  "volume": "2242885",
  "jisu": "343.66",
  "price": "34430",
  "time": "14:07:13"
 }
}
```

---

<a id="tr-IJ_"></a>
## `IJ_` 지수

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 시간 | String | Y | 6 | - |
| `jisu` | 지수 | String | Y | 8.2 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일비 | String | Y | 8.2 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `cvolume` | 체결량 | String | Y | 8 | - |
| `volume` | 거래량 | String | Y | 8 | - |
| `value` | 거래대금 | String | Y | 8 | - |
| `upjo` | 상한종목수 | String | Y | 4 | - |
| `highjo` | 상승종목수 | String | Y | 4 | - |
| `unchgjo` | 보합종목수 | String | Y | 4 | - |
| `lowjo` | 하락종목수 | String | Y | 4 | - |
| `downjo` | 하한종목수 | String | Y | 4 | - |
| `upjrate` | 상승종목비율 | String | Y | 6.2 | - |
| `openjisu` | 시가지수 | String | Y | 8.2 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `highjisu` | 고가지수 | String | Y | 8.2 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `lowjisu` | 저가지수 | String | Y | 8.2 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `frgsvolume` | 외인순매수수량 | String | Y | 8 | - |
| `orgsvolume` | 기관순매수수량 | String | Y | 8 | - |
| `frgsvalue` | 외인순매수금액 | String | Y | 10 | - |
| `orgsvalue` | 기관순매수금액 | String | Y | 10 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "IJ_",
  "tr_key": "001"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "IJ_",
  "tr_key": "001"
 },
 "body": {
  "sign": "2",
  "cvolume": "1280",
  "jisu": "2638.79",
  "highjisu": "2642.86",
  "upjo": "0",
  "highjo": "400",
  "value": "846176",
  "openjisu": "2640.81",
  "downjo": "0",
  "change": "0.84",
  "orgsvolume": "-585",
  "frgsvalue": "-39050",
  "upjrate": "42.11",
  "opentime": "090030",
  "lowtime": "090040",
  "volume": "46314",
  "drate": "0.03",
  "hightime": "090320",
  "upcode": "001",
  "time": "090510",
  "unchgjo": "140",
  "lowjisu": "2638.17",
  "lowjo": "410",
  "frgsvolume": "-3336",
  "orgsvalue": "-33117"
 }
}
```

---

<a id="tr-K1_"></a>
## `K1_` KOSPI거래원

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerno1` | 매도증권사코드1 | String | Y | 3 | - |
| `bidno1` | 매수증권사코드1 | String | Y | 3 | - |
| `offertrad1` | 매도회원사명1 | String | Y | 6 | - |
| `bidtrad1` | 매수회원사명1 | String | Y | 6 | - |
| `tradmdvol1` | 매도거래량1 | String | Y | 10 | - |
| `tradmsvol1` | 매수거래량1 | String | Y | 10 | - |
| `tradmdrate1` | 매도거래량비중1 | String | Y | 6.2 | - |
| `tradmsrate1` | 매도거래량비중1 | String | Y | 6.2 | - |
| `tradmdcha1` | 매도거래량직전대비1 | String | Y | 10 | - |
| `tradmscha1` | 매수거래량직전대비1 | String | Y | 10 | - |
| `offerno2` | 매도증권사코드2 | String | Y | 3 | - |
| `bidno2` | 매수증권사코드2 | String | Y | 3 | - |
| `offertrad2` | 매도회원사명2 | String | Y | 6 | - |
| `bidtrad2` | 매수회원사명2 | String | Y | 6 | - |
| `tradmdvol2` | 매도거래량2 | String | Y | 10 | - |
| `tradmsvol2` | 매수거래량2 | String | Y | 10 | - |
| `tradmdrate2` | 매도거래량비중2 | String | Y | 6.2 | - |
| `tradmsrate2` | 매수거래량비중2 | String | Y | 6.2 | - |
| `tradmdcha2` | 매도거래량직전대비2 | String | Y | 10 | - |
| `tradmscha2` | 매수거래량직전대비2 | String | Y | 10 | - |
| `offerno3` | 매도증권사코드3 | String | Y | 3 | - |
| `bidno3` | 매수증권사코드3 | String | Y | 3 | - |
| `offertrad3` | 매도회원사명3 | String | Y | 6 | - |
| `bidtrad3` | 매수회원사명3 | String | Y | 6 | - |
| `tradmdvol3` | 매도거래량3 | String | Y | 10 | - |
| `tradmsvol3` | 매수거래량3 | String | Y | 10 | - |
| `tradmdrate3` | 매도거래량비중3 | String | Y | 6.2 | - |
| `tradmsrate3` | 매수거래량비중3 | String | Y | 6.2 | - |
| `tradmdcha3` | 매도거래량직전대비3 | String | Y | 10 | - |
| `tradmscha3` | 매수거래량직전대비3 | String | Y | 10 | - |
| `offerno4` | 매도증권사코드4 | String | Y | 3 | - |
| `bidno4` | 매수증권사코드4 | String | Y | 3 | - |
| `offertrad4` | 매도회원사명4 | String | Y | 6 | - |
| `bidtrad4` | 매수회원사명4 | String | Y | 6 | - |
| `tradmdvol4` | 매도거래량4 | String | Y | 10 | - |
| `tradmsvol4` | 매수거래량4 | String | Y | 10 | - |
| `tradmdrate4` | 매도거래량비중4 | String | Y | 6.2 | - |
| `tradmsrate4` | 매수거래량비중4 | String | Y | 6.2 | - |
| `tradmdcha4` | 매도거래량직전대비4 | String | Y | 10 | - |
| `tradmscha4` | 매수거래량직전대비4 | String | Y | 10 | - |
| `offerno5` | 매도증권사코드5 | String | Y | 3 | - |
| `bidno5` | 매수증권사코드5 | String | Y | 3 | - |
| `offertrad5` | 매도회원사명5 | String | Y | 6 | - |
| `bidtrad5` | 매수회원사명5 | String | Y | 6 | - |
| `tradmdvol5` | 매도거래량5 | String | Y | 10 | - |
| `tradmsvol5` | 매수거래량5 | String | Y | 10 | - |
| `tradmdrate5` | 매도거래량비중5 | String | Y | 6.2 | - |
| `tradmsrate5` | 매수거래량비중5 | String | Y | 6.2 | - |
| `tradmdcha5` | 매도거래량직전대비5 | String | Y | 10 | - |
| `tradmscha5` | 매수거래량직전대비5 | String | Y | 10 | - |
| `ftradmdvol` | 외국계증권사매도합계 | String | Y | 10 | - |
| `ftradmsvol` | 외국계증권사매수합계 | String | Y | 10 | - |
| `ftradmdrate` | 외국계증권사매도거래량비중 | String | Y | 6.2 | - |
| `ftradmsrate` | 외국계증권사매수거래량비중 | String | Y | 6.2 | - |
| `ftradmdcha` | 외국계증권사매도거래량직전대비 | String | Y | 10 | - |
| `ftradmscha` | 외국계증권사매수거래량직전대비 | String | Y | 10 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `tradmdval1` | 매도거래대금1 | String | Y | 15 | - |
| `tradmsval1` | 매수거래대금1 | String | Y | 15 | - |
| `tradmdavg1` | 매도평균단가1 | String | Y | 7 | - |
| `tradmsavg1` | 매수평균단가1 | String | Y | 7 | - |
| `tradmdval2` | 매도거래대금2 | String | Y | 15 | - |
| `tradmsval2` | 매수거래대금2 | String | Y | 15 | - |
| `tradmdavg2` | 매도평균단가2 | String | Y | 7 | - |
| `tradmsavg2` | 매수평균단가2 | String | Y | 7 | - |
| `tradmdval3` | 매도거래대금3 | String | Y | 15 | - |
| `tradmsval3` | 매수거래대금3 | String | Y | 15 | - |
| `tradmdavg3` | 매도평균단가3 | String | Y | 7 | - |
| `tradmsavg3` | 매수평균단가3 | String | Y | 7 | - |
| `tradmdval4` | 매도거래대금4 | String | Y | 15 | - |
| `tradmsval4` | 매수거래대금4 | String | Y | 15 | - |
| `tradmdavg4` | 매도평균단가4 | String | Y | 7 | - |
| `tradmsavg4` | 매수평균단가4 | String | Y | 7 | - |
| `tradmdval5` | 매도거래대금5 | String | Y | 15 | - |
| `tradmsval5` | 매수거래대금5 | String | Y | 15 | - |
| `tradmdavg5` | 매도평균단가5 | String | Y | 7 | - |
| `tradmsavg5` | 매수평균단가5 | String | Y | 7 | - |
| `ftradmdval` | 외국계증권사매도거래대금 | String | Y | 15 | - |
| `ftradmsval` | 외국계증권사매수거래대금 | String | Y | 15 | - |
| `ftradmdavg` | 외국계증권사매도평균단가 | String | Y | 7 | - |
| `ftradmsavg` | 외국계증권사매수평균단가 | String | Y | 7 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "K1_",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "K1_",
  "tr_key": "005930"
 },
 "body": {
  "tradmdrate1": "13.15",
  "tradmdvol5": "34319",
  "tradmdvol3": "47293",
  "tradmdrate3": "10.83",
  "tradmdrate2": "11.00",
  "tradmdvol4": "36536",
  "offerno2": "033",
  "tradmdrate5": "7.86",
  "offerno1": "017",
  "tradmdrate4": "8.37",
  "offerno4": "063",
  "offerno3": "086",
  "bidtrad4": "맥쿼리",
  "offerno5": "041",
  "bidtrad5": "씨엘",
  "bidtrad2": "KB증권",
  "bidtrad3": "LS증권",
  "tradmdvol1": "57446",
  "bidtrad1": "UBS",
  "tradmdvol2": "48037",
  "tradmdval3": "3410",
  "offertrad5": "씨엘",
  "tradmdval4": "2634",
  "tradmdval1": "4141",
  "tradmdval2": "3463",
  "tradmdval5": "2474",
  "tradmscha2": "79121",
  "ftradmdval": "5938",
  "tradmscha1": "82043",
  "tradmscha4": "30697",
  "tradmscha3": "45048",
  "offertrad2": "JP모간",
  "offertrad1": "KB증권",
  "offertrad4": "eBEST",
  "offertrad3": "BNK 증",
  "tradmdcha5": "34319",
  "tradmdcha4": "36536",
  "tradmsavg1": "72106",
  "tradmsavg2": "72114",
  "tradmscha5": "30429",
  "tradmdavg1": "72083",
  "tradmdavg3": "72100",
  "tradmdavg2": "72100",
  "tradmdavg5": "72100",
  "tradmdavg4": "72096",
  "tradmsavg3": "72100",
  "ftradmscha": "0000143169",
  "tradmsavg4": "72100",
  "ftradmdvol": "0000082356",
  "tradmsavg5": "72100",
  "ftradmdavg": "72100",
  "tradmsval3": "3248",
  "tradmsval2": "5706",
  "tradmsval5": "2194",
  "ftradmsval": "10323",
  "tradmsval4": "2213",
  "tradmsval1": "5916",
  "tradmdcha1": "57446",
  "tradmdcha3": "47293",
  "tradmdcha2": "48037",
  "bidno1": "043",
  "bidno3": "063",
  "tradmsvol5": "30429",
  "bidno2": "017",
  "tradmsvol4": "30697",
  "bidno5": "041",
  "bidno4": "035",
  "tradmsvol1": "82043",
  "tradmsvol3": "45048",
  "tradmsvol2": "79121",
  "tradmsrate2": "18.12",
  "tradmsrate1": "18.79",
  "tradmsrate4": "7.03",
  "tradmsrate3": "10.32",
  "tradmsrate5": "6.97",
  "ftradmsvol": "0000143169",
  "ftradmdcha": "0000082356",
  "ftradmsrate": "32.78",
  "shcode": "005930",
  "ftradmsavg": "72104",
  "ftradmdrate": "18.86"
 }
}
```

---

<a id="tr-K3_"></a>
## `K3_` KOSDAQ체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `chetime` | 체결시간 | String | Y | 6 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `open` | 시가 | String | Y | 8 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `high` | 고가 | String | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | String | Y | 8 | - |
| `cgubun` | 체결구분 | String | Y | 1 | + : 매수<br/>- : 매도 |
| `cvolume` | 체결량 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `value` | 누적거래대금 | String | Y | 12 | - |
| `mdvolume` | 매도누적체결량 | String | Y | 12 | - |
| `mdchecnt` | 매도누적체결건수 | String | Y | 8 | - |
| `msvolume` | 매수누적체결량 | String | Y | 12 | - |
| `mschecnt` | 매수누적체결건수 | String | Y | 8 | - |
| `cpower` | 체결강도 | String | Y | 9.2 | - |
| `w_avrg` | 가중평균가 | String | Y | 8 | - |
| `offerho` | 매도호가 | String | Y | 8 | - |
| `bidho` | 매수호가 | String | Y | 8 | - |
| `status` | 장정보 | String | Y | 2 | - |
| `jnilvolume` | 전일동시간대거래량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "K3_",
  "tr_key": "122870"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "K3_",
        "tr_key": "122870"
    },
    "body": {
        "mdchecnt": "932",
        "sign": "2",
        "mschecnt": "654",
        "mdvolume": "105267",
        "w_avrg": "79658",
        "cpower": "44.30",
        "offerho": "81700",
        "cvolume": "3",
        "high": "81900",
        "bidho": "81500",
        "low": "64700",
        "price": "81700",
        "cgubun": "+",
        "value": "15083",
        "change": "18700",
        "shcode": "122870",
        "chetime": "104904",
        "opentime": "090023",
        "lowtime": "091107",
        "volume": "189353",
        "drate": "29.68",
        "hightime": "090814",
        "jnilvolume": "531425",
        "msvolume": "46630",
        "exchname": "KRX",
        "open": "68000",
        "status": "00"
    }
}
```

---

<a id="tr-KH_"></a>
## `KH_` KOSDAQ프로그램매매종목별

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 10 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `cdhrem` | 차익매도호가 잔량 | String | Y | 12 | - |
| `cshrem` | 차익매수호가 잔량 | String | Y | 12 | - |
| `bdhrem` | 비차익매도호가 잔량 | String | Y | 12 | - |
| `bshrem` | 비차익매수호가 잔량 | String | Y | 12 | - |
| `cdhvolume` | 차익매도호가 수량 | String | Y | 12 | - |
| `cshvolume` | 차익매수호가 수량 | String | Y | 12 | - |
| `bdhvolume` | 비차익매도호가 수량 | String | Y | 12 | - |
| `bshvolume` | 비차익매수호가 수량 | String | Y | 12 | - |
| `dwcvolume` | 전체매도위탁체결수량 | String | Y | 12 | - |
| `swcvolume` | 전체매수위탁체결수량 | String | Y | 12 | - |
| `djcvolume` | 전체매도자기체결수량 | String | Y | 12 | - |
| `sjcvolume` | 전체매수자기체결수량 | String | Y | 12 | - |
| `tdvolume` | 전체매도체결수량 | String | Y | 12 | - |
| `tsvolume` | 전체매수체결수량 | String | Y | 12 | - |
| `tvol` | 전체순매수 수량 | String | Y | 12 | - |
| `dwcvalue` | 전체매도위탁체결금액 | String | Y | 15 | - |
| `swcvalue` | 전체매수위탁체결금액 | String | Y | 15 | - |
| `djcvalue` | 전체매도자기체결금액 | String | Y | 15 | - |
| `sjcvalue` | 전체매수자기체결금액 | String | Y | 15 | - |
| `tdvalue` | 전체매도체결금액 | String | Y | 15 | - |
| `tsvalue` | 전체매수체결금액 | String | Y | 15 | - |
| `tval` | 전체순매수 금액 | String | Y | 15 | - |
| `pdgvolume` | 매도 사전공시수량 | String | Y | 12 | - |
| `psgvolume` | 매수 사전공시수량 | String | Y | 12 | - |
| `shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "KH_",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "KH_",
  "tr_key": "086520"
 },
 "body": {
  "bshrem": "69",
  "cshvolume": "0",
  "swcvolume": "0",
  "tsvolume": "0",
  "sign": "3",
  "dwcvolume": "0",
  "djcvalue": "0",
  "price": "749000",
  "dwcvalue": "0",
  "cshrem": "0",
  "bdhrem": "53",
  "bdhvolume": "53",
  "swcvalue": "0",
  "tval": "0",
  "djcvolume": "0",
  "bshvolume": "69",
  "sjcvalue": "0",
  "cdhvolume": "0",
  "tdvalue": "0",
  "change": "0",
  "shcode": "086520",
  "sjcvolume": "0",
  "tdvolume": "0",
  "tvol": "0",
  "tsvalue": "0",
  "volume": "672",
  "drate": "0.00",
  "cdhrem": "0",
  "psgvolume": "0",
  "time": "084011",
  "pdgvolume": "0"
 }
}
```

---

<a id="tr-KM_"></a>
## `KM_` KOSDAQ프로그램매매전체집계

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `cdhrem` | 차익매도호가 잔량 | String | Y | 6 | - |
| `cshrem` | 차익매수호가 잔량 | String | Y | 6 | - |
| `bdhrem` | 비차익매도호가 잔량 | String | Y | 6 | - |
| `bshrem` | 비차익매수호가 잔량 | String | Y | 6 | - |
| `cdhvolume` | 차익매도호가 수량 | String | Y | 6 | - |
| `cshvolume` | 차익매수호가 수량 | String | Y | 6 | - |
| `bdhvolume` | 비차익매도호가 수량 | String | Y | 6 | - |
| `bshvolume` | 비차익매수호가 수량 | String | Y | 6 | - |
| `cdwvolume` | 차익매도위탁체결수량 | String | Y | 6 | - |
| `cdjvolume` | 차익매도자기체결수량 | String | Y | 6 | - |
| `cswvolume` | 차익매수위탁체결수량 | String | Y | 6 | - |
| `csjvolume` | 차익매수자기체결수량 | String | Y | 6 | - |
| `cwvol` | 차익위탁순매수 수량 | String | Y | 6 | - |
| `cjvol` | 차익자기순매수 수량 | String | Y | 6 | - |
| `bdwvolume` | 비차익매도위탁체결수량 | String | Y | 6 | - |
| `bdjvolume` | 비차익매도자기체결수량 | String | Y | 6 | - |
| `bswvolume` | 비차익매수위탁체결수량 | String | Y | 6 | - |
| `bsjvolume` | 비차익매수자기체결수량 | String | Y | 6 | - |
| `bwvol` | 비차익위탁순매수 수량 | String | Y | 6 | - |
| `bjvol` | 비차익자기순매수 수량 | String | Y | 6 | - |
| `dwvolume` | 전체매도위탁체결수량 | String | Y | 6 | - |
| `swvolume` | 전체매수위탁체결수량 | String | Y | 6 | - |
| `wvol` | 전체위탁순매수 수량 | String | Y | 6 | - |
| `djvolume` | 전체매도자기체결수량 | String | Y | 6 | - |
| `sjvolume` | 전체매수자기체결수량 | String | Y | 6 | - |
| `jvol` | 전체자기순매수 수량 | String | Y | 6 | - |
| `cdwvalue` | 차익매도위탁체결금액 | String | Y | 8 | - |
| `cdjvalue` | 차익매도자기체결금액 | String | Y | 8 | - |
| `cswvalue` | 차익매수위탁체결금액 | String | Y | 8 | - |
| `csjvalue` | 차익매수자기체결금액 | String | Y | 8 | - |
| `cwval` | 차익위탁순매수 금액 | String | Y | 8 | - |
| `cjval` | 차익자기순매수 금액 | String | Y | 8 | - |
| `bdwvalue` | 비차익매도위탁체결금액 | String | Y | 8 | - |
| `bdjvalue` | 비차익매도자기체결금액 | String | Y | 8 | - |
| `bswvalue` | 비차익매수위탁체결금액 | String | Y | 8 | - |
| `bsjvalue` | 비차익매수자기체결금액 | String | Y | 8 | - |
| `bwval` | 비차익위탁순매수 금액 | String | Y | 8 | - |
| `bjval` | 비차익자기순매수 금액 | String | Y | 8 | - |
| `dwvalue` | 전체매도위탁체결금액 | String | Y | 8 | - |
| `swvalue` | 전체매수위탁체결금액 | String | Y | 8 | - |
| `wval` | 전체위탁순매수 금액 | String | Y | 8 | - |
| `djvalue` | 전체매도자기체결금액 | String | Y | 8 | - |
| `sjvalue` | 전체매수자기체결금액 | String | Y | 8 | - |
| `jval` | 전체자기순매수 금액 | String | Y | 8 | - |
| `k50jisu` | KOSDAQ50 지수 | String | Y | 6.2 | - |
| `k50sign` | KOSDAQ50 전일대비구분 | String | Y | 1 | - |
| `change` | KOSDAQ50 전일대비 | String | Y | 6.2 | - |
| `k50basis` | KOSDAQ50 베이시스 | String | Y | 4.2 | - |
| `cdvolume` | 차익매도체결수량합계 | String | Y | 6 | - |
| `csvolume` | 차익매수체결수량합계 | String | Y | 6 | - |
| `cvol` | 차익순매수 수량합계 | String | Y | 6 | - |
| `bdvolume` | 비차익매도체결수량합계 | String | Y | 6 | - |
| `bsvolume` | 비차익매수체결수량합계 | String | Y | 6 | - |
| `bvol` | 비차익순매수 수량합계 | String | Y | 6 | - |
| `tdvolume` | 전체매도체결수량합계 | String | Y | 6 | - |
| `tsvolume` | 전체매수체결수량합계 | String | Y | 6 | - |
| `tvol` | 전체순매수 수량합계 | String | Y | 6 | - |
| `cdvalue` | 차익매도체결금액합계 | String | Y | 8 | - |
| `csvalue` | 차익매수체결금액합계 | String | Y | 8 | - |
| `cval` | 차익순매수 금액합계 | String | Y | 8 | - |
| `bdvalue` | 비차익매도체결금액합계 | String | Y | 8 | - |
| `bsvalue` | 비차익매수체결금액합계 | String | Y | 8 | - |
| `bval` | 비차익순매수 금액합계 | String | Y | 8 | - |
| `tdvalue` | 전체매도체결금액합계 | String | Y | 8 | - |
| `tsvalue` | 전체매수체결금액합계 | String | Y | 8 | - |
| `tval` | 전체순매수 금액합계 | String | Y | 8 | - |
| `p_cdvolcha` | 차익매도체결수량직전대비 | String | Y | 6 | - |
| `p_csvolcha` | 차익매수체결수량직전대비 | String | Y | 6 | - |
| `p_cvolcha` | 차익순매수 수량직전대비 | String | Y | 6 | - |
| `p_bdvolcha` | 비차익매도체결수량직전대비 | String | Y | 6 | - |
| `p_bsvolcha` | 비차익매수체결수량직전대비 | String | Y | 6 | - |
| `p_bvolcha` | 비차익순매수 수량직전대비 | String | Y | 6 | - |
| `p_tdvolcha` | 전체매도체결수량직전대비 | String | Y | 6 | - |
| `p_tsvolcha` | 전체매수체결수량직전대비 | String | Y | 6 | - |
| `p_tvolcha` | 전체순매수 수량직전대비 | String | Y | 6 | - |
| `p_cdvalcha` | 차익매도체결금액직전대비 | String | Y | 8 | - |
| `p_csvalcha` | 차익매수체결금액직전대비 | String | Y | 8 | - |
| `p_cvalcha` | 차익순매수 금액직전대비 | String | Y | 8 | - |
| `p_bdvalcha` | 비차익매도체결금액직전대비 | String | Y | 8 | - |
| `p_bsvalcha` | 비차익매수체결금액직전대비 | String | Y | 8 | - |
| `p_bvalcha` | 비차익순매수 금액직전대비 | String | Y | 8 | - |
| `p_tdvalcha` | 전체매도체결금액직전대비 | String | Y | 8 | - |
| `p_tsvalcha` | 전체매수체결금액직전대비 | String | Y | 8 | - |
| `p_tvalcha` | 전체순매수 금액직전대비 | String | Y | 8 | - |
| `gubun` | 구분값 | String | Y | 1 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "KM_",
  "tr_key": "1"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "KM_",
  "tr_key": "1"
 },
 "body": {
  "sjvalue": "0",
  "p_bdvalcha": "58416",
  "p_cdvalcha": "419",
  "k50sign": "2",
  "cwval": "-440",
  "csjvolume": "0",
  "p_cvolcha": "-2",
  "bdvolume": "8923",
  "dwvalue": "114626",
  "cdvolume": "21",
  "bdwvolume": "8859",
  "sjvolume": "0",
  "jvol": "-83",
  "bdhrem": "1397",
  "tval": "-67954",
  "bdvalue": "114996",
  "bshvolume": "5221",
  "bjvol": "-64",
  "cdhvolume": "22",
  "bvol": "-5183",
  "csvolume": "0",
  "swvalue": "48143",
  "bdjvolume": "64",
  "tdvalue": "116097",
  "k50jisu": "1390.90",
  "tdvolume": "8944",
  "cjvol": "-19",
  "swvolume": "3741",
  "cswvolume": "0",
  "gubun": "1",
  "bwval": "-66043",
  "p_bvolcha": "-2147",
  "p_tsvolcha": "2350",
  "cdhrem": "0",
  "bswvalue": "48143",
  "csjvalue": "0",
  "p_bsvolcha": "2350",
  "p_tvalcha": "-29864",
  "bdjvalue": "809",
  "cdwvalue": "440",
  "cvol": "-21",
  "p_cvalcha": "-419",
  "bwvol": "-5118",
  "bshrem": "1480",
  "cshvolume": "0",
  "bdwvalue": "114186",
  "jval": "-1471",
  "tsvolume": "3741",
  "dwvolume": "8862",
  "p_bdvolcha": "4497",
  "bsjvolume": "0",
  "wvol": "-5121",
  "cdwvolume": "2",
  "bsvalue": "48143",
  "p_cdvolcha": "2",
  "bjval": "-809",
  "p_bsvalcha": "28971",
  "bval": "-66852",
  "djvolume": "83",
  "djvalue": "1471",
  "cshrem": "0",
  "p_csvalcha": "0",
  "p_tdvalcha": "58835",
  "bdhvolume": "10320",
  "p_tdvolcha": "4499",
  "bsvolume": "3741",
  "p_bvalcha": "-29445",
  "change": "2.33",
  "cdjvolume": "19",
  "tvol": "-5204",
  "p_tsvalcha": "28971",
  "bswvolume": "3741",
  "cdvalue": "1102",
  "tsvalue": "48143",
  "cval": "-1102",
  "csvalue": "0",
  "p_tvolcha": "-2149",
  "cswvalue": "0",
  "cwvol": "-2",
  "bsjvalue": "0",
  "cdjvalue": "662",
  "p_csvolcha": "0",
  "time": "090339",
  "k50basis": "-4.10",
  "wval": "-66483",
  "cjval": "-662"
 }
}
```

---

<a id="tr-KS_"></a>
## `KS_` KOSDAQ우선호가

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerho` | 매도호가 | String | Y | 8 | - |
| `bidho` | 매수호가 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "KS_",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "KS_",
  "tr_key": "086520"
 },
 "body": {
  "bidho": "759000",
  "shcode": "086520",
  "offerho": "760000"
 }
}
```

---

<a id="tr-OK_"></a>
## `OK_` KOSDAQ거래원

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerno1` | 매도증권사코드1 | String | Y | 3 | - |
| `bidno1` | 매수증권사코드1 | String | Y | 3 | - |
| `offertrad1` | 매도회원사명1 | String | Y | 6 | - |
| `bidtrad1` | 매수회원사명1 | String | Y | 6 | - |
| `tradmdvol1` | 매도거래량1 | String | Y | 10 | - |
| `tradmsvol1` | 매수거래량1 | String | Y | 10 | - |
| `tradmdrate1` | 매도거래량비중1 | String | Y | 6.2 | - |
| `tradmsrate1` | 매도거래량비중1 | String | Y | 6.2 | - |
| `tradmdcha1` | 매도거래량직전대비1 | String | Y | 10 | - |
| `tradmscha1` | 매수거래량직전대비1 | String | Y | 10 | - |
| `offerno2` | 매도증권사코드2 | String | Y | 3 | - |
| `bidno2` | 매수증권사코드2 | String | Y | 3 | - |
| `offertrad2` | 매도회원사명2 | String | Y | 6 | - |
| `bidtrad2` | 매수회원사명2 | String | Y | 6 | - |
| `tradmdvol2` | 매도거래량2 | String | Y | 10 | - |
| `tradmsvol2` | 매수거래량2 | String | Y | 10 | - |
| `tradmdrate2` | 매도거래량비중2 | String | Y | 6.2 | - |
| `tradmsrate2` | 매수거래량비중2 | String | Y | 6.2 | - |
| `tradmdcha2` | 매도거래량직전대비2 | String | Y | 10 | - |
| `tradmscha2` | 매수거래량직전대비2 | String | Y | 10 | - |
| `offerno3` | 매도증권사코드3 | String | Y | 3 | - |
| `bidno3` | 매수증권사코드3 | String | Y | 3 | - |
| `offertrad3` | 매도회원사명3 | String | Y | 6 | - |
| `bidtrad3` | 매수회원사명3 | String | Y | 6 | - |
| `tradmdvol3` | 매도거래량3 | String | Y | 10 | - |
| `tradmsvol3` | 매수거래량3 | String | Y | 10 | - |
| `tradmdrate3` | 매도거래량비중3 | String | Y | 6.2 | - |
| `tradmsrate3` | 매수거래량비중3 | String | Y | 6.2 | - |
| `tradmdcha3` | 매도거래량직전대비3 | String | Y | 10 | - |
| `tradmscha3` | 매수거래량직전대비3 | String | Y | 10 | - |
| `offerno4` | 매도증권사코드4 | String | Y | 3 | - |
| `bidno4` | 매수증권사코드4 | String | Y | 3 | - |
| `offertrad4` | 매도회원사명4 | String | Y | 6 | - |
| `bidtrad4` | 매수회원사명4 | String | Y | 6 | - |
| `tradmdvol4` | 매도거래량4 | String | Y | 10 | - |
| `tradmsvol4` | 매수거래량4 | String | Y | 10 | - |
| `tradmdrate4` | 매도거래량비중4 | String | Y | 6.2 | - |
| `tradmsrate4` | 매수거래량비중4 | String | Y | 6.2 | - |
| `tradmdcha4` | 매도거래량직전대비4 | String | Y | 10 | - |
| `tradmscha4` | 매수거래량직전대비4 | String | Y | 10 | - |
| `offerno5` | 매도증권사코드5 | String | Y | 3 | - |
| `bidno5` | 매수증권사코드5 | String | Y | 3 | - |
| `offertrad5` | 매도회원사명5 | String | Y | 6 | - |
| `bidtrad5` | 매수회원사명5 | String | Y | 6 | - |
| `tradmdvol5` | 매도거래량5 | String | Y | 10 | - |
| `tradmsvol5` | 매수거래량5 | String | Y | 10 | - |
| `tradmdrate5` | 매도거래량비중5 | String | Y | 6.2 | - |
| `tradmsrate5` | 매수거래량비중5 | String | Y | 6.2 | - |
| `tradmdcha5` | 매도거래량직전대비5 | String | Y | 10 | - |
| `tradmscha5` | 매수거래량직전대비5 | String | Y | 10 | - |
| `ftradmdvol` | 외국계증권사매도합계 | String | Y | 10 | - |
| `ftradmsvol` | 외국계증권사매수합계 | String | Y | 10 | - |
| `ftradmdrate` | 외국계증권사매도거래량비중 | String | Y | 6.2 | - |
| `ftradmsrate` | 외국계증권사매수거래량비중 | String | Y | 6.2 | - |
| `ftradmdcha` | 외국계증권사매도거래량직전대비 | String | Y | 10 | - |
| `ftradmscha` | 외국계증권사매수거래량직전대비 | String | Y | 10 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `tradmdval1` | 매도거래대금1 | String | Y | 15 | - |
| `tradmsval1` | 매수거래대금1 | String | Y | 15 | - |
| `tradmdavg1` | 매도평균단가1 | String | Y | 7 | - |
| `tradmsavg1` | 매수평균단가1 | String | Y | 7 | - |
| `tradmdval2` | 매도거래대금2 | String | Y | 15 | - |
| `tradmsval2` | 매수거래대금2 | String | Y | 15 | - |
| `tradmdavg2` | 매도평균단가2 | String | Y | 7 | - |
| `tradmsavg2` | 매수평균단가2 | String | Y | 7 | - |
| `tradmdval3` | 매도거래대금3 | String | Y | 15 | - |
| `tradmsval3` | 매수거래대금3 | String | Y | 15 | - |
| `tradmdavg3` | 매도평균단가3 | String | Y | 7 | - |
| `tradmsavg3` | 매수평균단가3 | String | Y | 7 | - |
| `tradmdval4` | 매도거래대금4 | String | Y | 15 | - |
| `tradmsval4` | 매수거래대금4 | String | Y | 15 | - |
| `tradmdavg4` | 매도평균단가4 | String | Y | 7 | - |
| `tradmsavg4` | 매수평균단가4 | String | Y | 7 | - |
| `tradmdval5` | 매도거래대금5 | String | Y | 15 | - |
| `tradmsval5` | 매수거래대금5 | String | Y | 15 | - |
| `tradmdavg5` | 매도평균단가5 | String | Y | 7 | - |
| `tradmsavg5` | 매수평균단가5 | String | Y | 7 | - |
| `ftradmdval` | 외국계증권사매도거래대금 | String | Y | 15 | - |
| `ftradmsval` | 외국계증권사매수거래대금 | String | Y | 15 | - |
| `ftradmdavg` | 외국계증권사매도평균단가 | String | Y | 7 | - |
| `ftradmsavg` | 외국계증권사매수평균단가 | String | Y | 7 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "OK_",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "OK_",
  "tr_key": "086520"
 },
 "body": {
  "tradmdrate1": "32.67",
  "tradmdvol5": "4218",
  "tradmdvol3": "7053",
  "tradmdrate3": "11.04",
  "tradmdrate2": "16.00",
  "tradmdvol4": "4439",
  "offerno2": "005",
  "tradmdrate5": "6.60",
  "offerno1": "050",
  "tradmdrate4": "6.95",
  "offerno4": "012",
  "offerno3": "002",
  "bidtrad4": "삼성증",
  "offerno5": "003",
  "bidtrad5": "NH투자",
  "bidtrad2": "한국증",
  "bidtrad3": "미래에",
  "tradmdvol1": "20868",
  "bidtrad1": "키움증",
  "tradmdvol2": "10220",
  "tradmdval3": "5332",
  "offertrad5": "한국증",
  "tradmdval4": "3351",
  "tradmdval1": "15746",
  "tradmdval2": "7738",
  "tradmdval5": "3181",
  "tradmscha2": "7210",
  "ftradmdval": "0",
  "tradmscha1": "21164",
  "tradmscha4": "5739",
  "tradmscha3": "5930",
  "offertrad2": "미래에",
  "offertrad1": "키움증",
  "offertrad4": "NH투자",
  "offertrad3": "신한투",
  "tradmdcha5": "4218",
  "tradmdcha4": "4439",
  "tradmsavg1": "755482",
  "tradmsavg2": "755335",
  "tradmscha5": "4572",
  "tradmdavg1": "754570",
  "tradmdavg3": "756014",
  "tradmdavg2": "757173",
  "tradmdavg5": "754197",
  "tradmdavg4": "754884",
  "tradmsavg3": "755310",
  "ftradmscha": "0000000000",
  "tradmsavg4": "756039",
  "ftradmdvol": "0000000000",
  "tradmsavg5": "755234",
  "ftradmdavg": " ",
  "tradmsval3": "4479",
  "tradmsval2": "5446",
  "tradmsval5": "3453",
  "ftradmsval": "0",
  "tradmsval4": "4339",
  "tradmsval1": "15989",
  "tradmdcha1": "20868",
  "tradmdcha3": "7053",
  "tradmdcha2": "10220",
  "bidno1": "050",
  "bidno3": "005",
  "tradmsvol5": "4572",
  "bidno2": "003",
  "tradmsvol4": "5739",
  "bidno5": "012",
  "bidno4": "030",
  "tradmsvol1": "21164",
  "tradmsvol3": "5930",
  "tradmsvol2": "7210",
  "tradmsrate2": "11.29",
  "tradmsrate1": "33.14",
  "tradmsrate4": "8.99",
  "tradmsrate3": "9.28",
  "tradmsrate5": "7.16",
  "ftradmsvol": "0000000000",
  "ftradmdcha": "0000000000",
  "ftradmsrate": "0.00",
  "shcode": "086520",
  "ftradmsavg": " ",
  "ftradmdrate": "0.00"
 }
}
```

---

<a id="tr-PH_"></a>
## `PH_` KOSPI프로그램매매종목별

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 10 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `cdhrem` | 차익매도호가 잔량 | String | Y | 12 | - |
| `cshrem` | 차익매수호가 잔량 | String | Y | 12 | - |
| `bdhrem` | 비차익매도호가 잔량 | String | Y | 12 | - |
| `bshrem` | 비차익매수호가 잔량 | String | Y | 12 | - |
| `cdhvolume` | 차익매도호가 수량 | String | Y | 12 | - |
| `cshvolume` | 차익매수호가 수량 | String | Y | 12 | - |
| `bdhvolume` | 비차익매도호가 수량 | String | Y | 12 | - |
| `bshvolume` | 비차익매수호가 수량 | String | Y | 12 | - |
| `dwcvolume` | 전체매도위탁체결수량 | String | Y | 12 | - |
| `swcvolume` | 전체매수위탁체결수량 | String | Y | 12 | - |
| `djcvolume` | 전체매도자기체결수량 | String | Y | 12 | - |
| `sjcvolume` | 전체매수자기체결수량 | String | Y | 12 | - |
| `tdvolume` | 전체매도체결수량 | String | Y | 12 | - |
| `tsvolume` | 전체매수체결수량 | String | Y | 12 | - |
| `tvol` | 전체순매수 수량 | String | Y | 12 | - |
| `dwcvalue` | 전체매도위탁체결금액 | String | Y | 15 | - |
| `swcvalue` | 전체매수위탁체결금액 | String | Y | 15 | - |
| `djcvalue` | 전체매도자기체결금액 | String | Y | 15 | - |
| `sjcvalue` | 전체매수자기체결금액 | String | Y | 15 | - |
| `tdvalue` | 전체매도체결금액 | String | Y | 15 | - |
| `tsvalue` | 전체매수체결금액 | String | Y | 15 | - |
| `tval` | 전체순매수 금액 | String | Y | 15 | - |
| `pdgvolume` | 매도 사전공시수량 | String | Y | 12 | - |
| `psgvolume` | 매수 사전공시수량 | String | Y | 12 | - |
| `shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "PH_",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "PH_",
  "tr_key": "005930"
 },
 "body": {
  "bshrem": "55729",
  "cshvolume": "0",
  "swcvolume": "0",
  "tsvolume": "0",
  "sign": "3",
  "dwcvolume": "0",
  "djcvalue": "0",
  "price": "72000",
  "dwcvalue": "0",
  "cshrem": "0",
  "bdhrem": "91585",
  "bdhvolume": "91585",
  "swcvalue": "0",
  "tval": "0",
  "djcvolume": "0",
  "bshvolume": "55729",
  "sjcvalue": "0",
  "cdhvolume": "0",
  "tdvalue": "0",
  "change": "0",
  "shcode": "005930",
  "sjcvolume": "0",
  "tdvolume": "0",
  "tvol": "0",
  "tsvalue": "0",
  "volume": "136",
  "drate": "0.00",
  "cdhrem": "0",
  "psgvolume": "0",
  "time": "084340",
  "pdgvolume": "0"
 }
}
```

---

<a id="tr-PM_"></a>
## `PM_` KOSPI프로그램매매전체집계

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `cdhrem` | 차익매도호가잔량 | String | Y | 6 | - |
| `cshrem` | 차익매수호가잔량 | String | Y | 6 | - |
| `bdhrem` | 비차익매도호가잔량 | String | Y | 6 | - |
| `bshrem` | 비차익매수호가잔량 | String | Y | 6 | - |
| `cdhvolume` | 차익매도호가수량 | String | Y | 6 | - |
| `cshvolume` | 차익매수호가수량 | String | Y | 6 | - |
| `bdhvolume` | 비차익매도호가수량 | String | Y | 6 | - |
| `bshvolume` | 비차익매수호가수량 | String | Y | 6 | - |
| `cdwvolume` | 차익매도위탁체결수량 | String | Y | 6 | - |
| `cdjvolume` | 차익매도자기체결수량 | String | Y | 6 | - |
| `cswvolume` | 차익매수위탁체결수량 | String | Y | 6 | - |
| `csjvolume` | 차익매수자기체결수량 | String | Y | 6 | - |
| `cwvol` | 차익위탁순매수수량 | String | Y | 6 | - |
| `cjvol` | 차익자기순매수수량 | String | Y | 6 | - |
| `bdwvolume` | 비차익매도위탁체결수량 | String | Y | 6 | - |
| `bdjvolume` | 비차익매도자기체결수량 | String | Y | 6 | - |
| `bswvolume` | 비차익매수위탁체결수량 | String | Y | 6 | - |
| `bsjvolume` | 비차익매수자기체결수량 | String | Y | 6 | - |
| `bwvol` | 비차익위탁순매수수량 | String | Y | 6 | - |
| `bjvol` | 비차익자기순매수수량 | String | Y | 6 | - |
| `dwvolume` | 전체매도위탁체결수량 | String | Y | 6 | - |
| `swvolume` | 전체매수위탁체결수량 | String | Y | 6 | - |
| `wvol` | 전체위탁순매수수량 | String | Y | 6 | - |
| `djvolume` | 전체매도자기체결수량 | String | Y | 6 | - |
| `sjvolume` | 전체매수자기체결수량 | String | Y | 6 | - |
| `jvol` | 전체자기순매수수량 | String | Y | 6 | - |
| `cdwvalue` | 차익매도위탁체결금액 | String | Y | 8 | - |
| `cdjvalue` | 차익매도자기체결금액 | String | Y | 8 | - |
| `cswvalue` | 차익매수위탁체결금액 | String | Y | 8 | - |
| `csjvalue` | 차익매수자기체결금액 | String | Y | 8 | - |
| `cwval` | 차익위탁순매수금액 | String | Y | 8 | - |
| `cjval` | 차익자기순매수금액 | String | Y | 8 | - |
| `bdwvalue` | 비차익매도위탁체결금액 | String | Y | 8 | - |
| `bdjvalue` | 비차익매도자기체결금액 | String | Y | 8 | - |
| `bswvalue` | 비차익매수위탁체결금액 | String | Y | 8 | - |
| `bsjvalue` | 비차익매수자기체결금액 | String | Y | 8 | - |
| `bwval` | 비차익위탁순매수금액 | String | Y | 8 | - |
| `bjval` | 비차익자기순매수금액 | String | Y | 8 | - |
| `dwvalue` | 전체매도위탁체결금액 | String | Y | 8 | - |
| `swvalue` | 전체매수위탁체결금액 | String | Y | 8 | - |
| `wval` | 전체위탁순매수금액 | String | Y | 8 | - |
| `djvalue` | 전체매도자기체결금액 | String | Y | 8 | - |
| `sjvalue` | 전체매수자기체결금액 | String | Y | 8 | - |
| `jval` | 전체자기순매수금액 | String | Y | 8 | - |
| `k200jisu` | KOSPI200지수 | String | Y | 6.2 | - |
| `k200sign` | KOSPI200전일대비구분 | String | Y | 1 | - |
| `change` | KOSPI200전일대비 | String | Y | 6.2 | - |
| `k200basis` | KOSPI200베이시스 | String | Y | 4.2 | - |
| `cdvolume` | 차익매도체결수량합계 | String | Y | 6 | - |
| `csvolume` | 차익매수체결수량합계 | String | Y | 6 | - |
| `cvol` | 차익순매수수량합계 | String | Y | 6 | - |
| `bdvolume` | 비차익매도체결수량합계 | String | Y | 6 | - |
| `bsvolume` | 비차익매수체결수량합계 | String | Y | 6 | - |
| `bvol` | 비차익순매수수량합계 | String | Y | 6 | - |
| `tdvolume` | 전체매도체결수량합계 | String | Y | 6 | - |
| `tsvolume` | 전체매수체결수량합계 | String | Y | 6 | - |
| `tvol` | 전체순매수수량합계 | String | Y | 6 | - |
| `cdvalue` | 차익매도체결금액합계 | String | Y | 8 | - |
| `csvalue` | 차익매수체결금액합계 | String | Y | 8 | - |
| `cval` | 차익순매수금액합계 | String | Y | 8 | - |
| `bdvalue` | 비차익매도체결금액합계 | String | Y | 8 | - |
| `bsvalue` | 비차익매수체결금액합계 | String | Y | 8 | - |
| `bval` | 비차익순매수금액합계 | String | Y | 8 | - |
| `tdvalue` | 전체매도체결금액합계 | String | Y | 8 | - |
| `tsvalue` | 전체매수체결금액합계 | String | Y | 8 | - |
| `tval` | 전체순매수금액합계 | String | Y | 8 | - |
| `p_cdvolcha` | 차익매도체결수량직전대비 | String | Y | 6 | - |
| `p_csvolcha` | 차익매수체결수량직전대비 | String | Y | 6 | - |
| `p_cvolcha` | 차익순매수수량직전대비 | String | Y | 6 | - |
| `p_bdvolcha` | 비차익매도체결수량직전대비 | String | Y | 6 | - |
| `p_bsvolcha` | 비차익매수체결수량직전대비 | String | Y | 6 | - |
| `p_bvolcha` | 비차익순매수수량직전대비 | String | Y | 6 | - |
| `p_tdvolcha` | 전체매도체결수량직전대비 | String | Y | 6 | - |
| `p_tsvolcha` | 전체매수체결수량직전대비 | String | Y | 6 | - |
| `p_tvolcha` | 전체순매수수량직전대비 | String | Y | 6 | - |
| `p_cdvalcha` | 차익매도체결금액직전대비 | String | Y | 8 | - |
| `p_csvalcha` | 차익매수체결금액직전대비 | String | Y | 8 | - |
| `p_cvalcha` | 차익순매수금액직전대비 | String | Y | 8 | - |
| `p_bdvalcha` | 비차익매도체결금액직전대비 | String | Y | 8 | - |
| `p_bsvalcha` | 비차익매수체결금액직전대비 | String | Y | 8 | - |
| `p_bvalcha` | 비차익순매수금액직전대비 | String | Y | 8 | - |
| `p_tdvalcha` | 전체매도체결금액직전대비 | String | Y | 8 | - |
| `p_tsvalcha` | 전체매수체결금액직전대비 | String | Y | 8 | - |
| `p_tvalcha` | 전체순매수금액직전대비 | String | Y | 8 | - |
| `gubun` | 구분값 | String | Y | 1 | - |


---

<a id="tr-S2_"></a>
## `S2_` KOSPI우선호가

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerho` | 매도호가 | String | Y | 8 | - |
| `bidho` | 매수호가 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "S2_",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "S2_",
  "tr_key": "005930"
 },
 "body": {
  "bidho": "71200",
  "shcode": "005930",
  "offerho": "71300"
 }
}
```

---

<a id="tr-S3_"></a>
## `S3_` KOSPI체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `chetime` | 체결시간 | String | Y | 6 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `open` | 시가 | String | Y | 8 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `high` | 고가 | String | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | String | Y | 8 | - |
| `cgubun` | 체결구분 | String | Y | 1 | + : 매수<br/>- : 매도 |
| `cvolume` | 체결량 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `value` | 누적거래대금 | String | Y | 12 | - |
| `mdvolume` | 매도누적체결량 | String | Y | 12 | - |
| `mdchecnt` | 매도누적체결건수 | String | Y | 8 | - |
| `msvolume` | 매수누적체결량 | String | Y | 12 | - |
| `mschecnt` | 매수누적체결건수 | String | Y | 8 | - |
| `cpower` | 체결강도 | String | Y | 9.2 | - |
| `w_avrg` | 가중평균가 | String | Y | 8 | - |
| `offerho` | 매도호가 | String | Y | 8 | - |
| `bidho` | 매수호가 | String | Y | 8 | - |
| `status` | 장정보 | String | Y | 2 | ' 0':장중<br/>' 4':장후시간외<br/>' 3':장마감<br/>'10':장전시간외 |
| `jnilvolume` | 전일동시간대거래량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "S3_",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "S3_",
        "tr_key": "005930"
    },
    "body": {
        "mdchecnt": "23",
        "sign": "2",
        "mschecnt": "96",
        "mdvolume": "946",
        "w_avrg": "55448",
        "cpower": "332.56",
        "offerho": "55600",
        "cvolume": "1",
        "high": "55800",
        "bidho": "55500",
        "low": "55500",
        "price": "55550",
        "cgubun": "+",
        "value": "604",
        "change": "1050",
        "shcode": "005930",
        "chetime": "090851",
        "opentime": "090030",
        "lowtime": "090030",
        "volume": "10887",
        "drate": "1.93",
        "hightime": "090504",
        "jnilvolume": "2508350",
        "msvolume": "3146",
        "exchname": "KRX",
        "open": "55600",
        "status": "00"
    }
}
```

---

<a id="tr-S4_"></a>
## `S4_` KOSPI기세

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `open` | 시가 | String | Y | 8 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `high` | 고가 | String | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


---

<a id="tr-SC0"></a>
## `SC0` 주식주문접수

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `accno` | Push키 | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `trcode` | TRCODE | String | Y | 8 | SONAT000:신규주문<br/>SONAT001:정정주문<br/>SONAT002:취소주문<br/>SONAS100:체결확인 |
| `compid` | 이용사번호 | String | Y | 3 | - |
| `userid` | 사용자ID | String | Y | 16 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `filler` | 예비영역 | String | Y | 6 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `ordchegb` | 주문체결구분 | String | Y | 2 | 01:주문<br/>02:정정<br/>03:취소<br/>11:체결<br/>12:정정확인<br/>13:취소확인<br/>14:거부<br/>A1:접수중<br/>AC:접수완료<br/> |
| `marketgb` | 시장구분 | String | Y | 2 | 00:비상장<br/>10:코스피<br/>11:채권<br/>19:장외시장<br/>20:코스닥<br/>23:코넥스<br/>30:프리보드<br/>61:동경거래소<br/>62:JASDAQ<br/> |
| `ordgb` | 주문구분 | String | Y | 2 | 01:현금매도<br/>02:현금매수<br/>03:신용매도<br/>04:신용매수<br/>05:저축매도<br/>06:저축매수<br/>07:상품매도(대차)<br/>09:상품매도<br/>10:상품매수<br/>11:선물대용매도(일반)<br/>12:선물대용매도(반대)<br/>13:현금매도(프)<br/>14:현금매수(프)<br/>15:현금매수(유가)<br/>16:현금매수(정리)<br/>17:상품매도(대차.프)<br/>19:상품매도(프)<br/>20:상품매수(프)<br/>30:장외매매<br/> |
| `orgordno` | 원주문번호 | String | Y | 10 | - |
| `accno1` | 계좌번호 | String | Y | 11 | - |
| `accno2` | 계좌번호 | String | Y | 9 | - |
| `passwd` | 비밀번호 | String | Y | 8 | - |
| `expcode` | 종목번호 | String | Y | 12 | 표준코드 12자리<br/> |
| `shtcode` | 단축종목번호 | String | Y | 9 | 주식은 단축코드 앞에 A포함 7자리<br/>ELW는 단촉코드 앞에 J포함 7자리<br/> |
| `hname` | 종목명 | String | Y | 40 | - |
| `ordqty` | 주문수량 | String | Y | 16 | - |
| `ordprice` | 주문가격 | String | Y | 13 | - |
| `hogagb` | 주문조건 | String | Y | 1 | 0:없음<br/>1:IOC<br/>2:FOK<br/> |
| `etfhogagb` | 호가유형코드 | String | Y | 2 | 00:지정가<br/>03:시장가<br/>05:조건부지정가<br/>06:최유리지정가<br/>07:최우선지정가<br/>09:자사주<br/>10:매입인도(일반)<br/>13:시장가 (IOC)<br/>16:최유리지정가 (IOC)<br/>18:사용안함<br/>20:지정가(임의)<br/>23:시장가(임의)<br/>26:최유리지정가 (FOK)<br/>41:부분충족(프리보드)<br/>42:전량충족(프리보드)<br/>51:장중대량<br/>52:장중바스켓<br/>61:장개시전시간외<br/>62:사용안함<br/>63:경매매<br/>66:장전시간외경쟁대량<br/>67:장개시전시간외대량<br/>68:장개시전시간외바스켓<br/>69:장개시전시간외자사주<br/>71:신고대량전장시가<br/>72:사용안함<br/>73:신고대량종가<br/>76:장중경쟁대량<br/>77:장중대량<br/>78:장중바스켓<br/>79:사용안함<br/>80:매입인도(당일)<br/>81:시간외종가<br/>82:시간외단일가<br/>87:시간외대량<br/>88:바스켓주문<br/>89:시간외자사주<br/>91:자사주스톡옵션<br/>A1:stop order |
| `pgmtype` | 프로그램호가구분 | String | Y | 2 | 00:일반<br/>01:지수차익<br/>02:지수비차익<br/>03:주식차익<br/>04:ETF차익(비차익제외)<br/>05:ETF설정(비차익제외)<br/>06:ETF차익(비차익)<br/>07:ETF설정(비차익)<br/>08:DR차익<br/>09:ELW LP헷지<br/>10:ETF LP헷지<br/>11:주식옵션 LP헷지<br/>12:장외파생상품헷지<br/> |
| `gmhogagb` | 공매도호가구분 | String | Y | 1 | 0:일반<br/>1:차입주식매도<br/>2:기타공매도<br/> |
| `gmhogayn` | 공매도가능여부 | String | Y | 1 | 0:일반<br/>1:공매도<br/> |
| `singb` | 신용구분 | String | Y | 3 | 000:보통<br/>001:유통융자신규<br/>003:자기융자신규<br/>005:유통대주신규<br/>007:자기대주신규<br/>011:미사용<br/>070:매도대금담보융자신규<br/>080:예탁주식담보융자신규<br/>082:예탁채권담보융자신규<br/>101:유통융자상환<br/>103:자기융자상환<br/>105:유통대주상환<br/>107:자기대주상환<br/>111:유통융자전액상환<br/>113:자기융자전액상환<br/>170:매도대금담보융자상환<br/>180:예탁주식담보융자상환<br/>182:예탁채권담보융자상환<br/>188:담보대출전액상환<br/>201:유통융자현금상환<br/>203:자기융자현금상환<br/>205:유통대주현물상환<br/>207:자기대주현물상환<br/>280:예탁주식담보융자현금상환<br/>282:예탁채권담보융자현금상환<br/>301:유통융자현금상환취소<br/>303:자기융자현금상환취소<br/>305:유통대주현물상환취소<br/>307:자기대주현물상환취소<br/> |
| `loandt` | 대출일 | String | Y | 8 | - |
| `cvrgordtp` | 반대매매주문구분 | String | Y | 1 | 0:일반<br/>1:자동반대매매<br/>2:지점반대매매<br/>3:예비주문에대한 본주문 |
| `strtgcode` | 전략코드 | String | Y | 6 | - |
| `groupid` | 그룹ID | String | Y | 20 | - |
| `ordseqno` | 주문회차 | String | Y | 10 | - |
| `prtno` | 포트폴리오번호 | String | Y | 10 | - |
| `basketno` | 바스켓번호 | String | Y | 10 | - |
| `trchno` | 트렌치번호 | String | Y | 10 | - |
| `itemno` | 아아템번호 | String | Y | 10 | - |
| `brwmgmyn` | 차입구분 | String | Y | 1 | - |
| `mbrno` | 회원사번호 | String | Y | 3 | - |
| `procgb` | 처리구분 | String | Y | 1 | - |
| `admbrchno` | 관리지점번호 | String | Y | 3 | - |
| `futaccno` | 선물계좌번호 | String | Y | 20 | - |
| `futmarketgb` | 선물상품구분 | String | Y | 1 | - |
| `tongsingb` | 통신매체구분 | String | Y | 2 | - |
| `lpgb` | 유동성공급자구분 | String | Y | 1 | 0:해당없음<br/>1:유동성공급자<br/> |
| `dummy` | DUMMY | String | Y | 20 | - |
| `ordno` | 주문번호 | String | Y | 10 | - |
| `ordtm` | 주문시각 | String | Y | 9 | - |
| `prntordno` | 모주문번호 | String | Y | 10 | - |
| `mgempno` | 관리사원번호 | String | Y | 9 | - |
| `orgordundrqty` | 원주문미체결수량 | String | Y | 16 | - |
| `orgordmdfyqty` | 원주문정정수량 | String | Y | 16 | - |
| `ordordcancelqty` | 원주문취소수량 | String | Y | 16 | - |
| `nmcpysndno` | 비회원사송신번호 | String | Y | 10 | - |
| `ordamt` | 주문금액 | String | Y | 16 | - |
| `bnstp` | 매매구분 | String | Y | 1 | 1:매도<br/>2:매수<br/> |
| `spareordno` | 예비주문번호 | String | Y | 10 | - |
| `cvrgseqno` | 반대매매일련번호 | String | Y | 10 | - |
| `rsvordno` | 예약주문번호 | String | Y | 10 | - |
| `mtordseqno` | 복수주문일련번호 | String | Y | 10 | - |
| `spareordqty` | 예비주문수량 | String | Y | 16 | - |
| `orduserid` | 주문사원번호 | String | Y | 16 | - |
| `spotordqty` | 실물주문수량 | String | Y | 16 | - |
| `ordruseqty` | 재사용주문수량 | String | Y | 16 | - |
| `mnyordamt` | 현금주문금액 | String | Y | 16 | - |
| `ordsubstamt` | 주문대용금액 | String | Y | 16 | - |
| `ruseordamt` | 재사용주문금액 | String | Y | 16 | - |
| `ordcmsnamt` | 수수료주문금액 | String | Y | 16 | - |
| `crdtuseamt` | 사용신용담보재사용금 | String | Y | 16 | - |
| `secbalqty` | 잔고수량 | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `spotordableqty` | 실물가능수량 | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `ordableruseqty` | 재사용가능수량(매도) | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `flctqty` | 변동수량 | String | Y | 16 | - |
| `secbalqtyd2` | 잔고수량(D2) | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `sellableqty` | 매도주문가능수량 | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `unercsellordqty` | 미체결매도주문수량 | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `avrpchsprc` | 평균매입가 | String | Y | 13 | 실서버 데이터 미제공 필드<br/> |
| `pchsamt` | 매입금액 | String | Y | 16 | 실서버 데이터 미제공 필드<br/> |
| `deposit` | 예수금 | String | Y | 16 | - |
| `substamt` | 대용금 | String | Y | 16 | - |
| `csgnmnymgn` | 위탁증거금현금 | String | Y | 16 | - |
| `csgnsubstmgn` | 위탁증거금대용 | String | Y | 16 | - |
| `crdtpldgruseamt` | 신용담보재사용금 | String | Y | 16 | - |
| `ordablemny` | 주문가능현금 | String | Y | 16 | - |
| `ordablesubstamt` | 주문가능대용 | String | Y | 16 | - |
| `ruseableamt` | 재사용가능금액 | String | Y | 16 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "SC0",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SC0"
 },
 "body": {
  "trchno": "0",
  "spareordqty": "0",
  "trcode": "SONAT000",
  "userid": "hdkrggg4",
  "dummy": "",
  "len": "1053",
  "loandt": "00000000",
  "orgordmdfyqty": "0",
  "avrpchsprc": ".00",
  "cont": "N",
  "hname": "삼성전자",
  "pgmtype": "0",
  "compress": "0",
  "ordprice": "60000",
  "procgb": "0",
  "unercsellordqty": "0",
  "ruseableamt": "0",
  "ordgb": "02",
  "gubun": "B",
  "trid": "2000095635771500",
  "flctqty": "0",
  "varmsglen": "0",
  "ordno": "86382",
  "passwd": "********",
  "singb": "000",
  "gmhogayn": "0",
  "ordruseqty": "0",
  "deposit": "79759964",
  "trsrc": "L",
  "gmhogagb": "0",
  "reqcnt": " ",
  "accno1": "20011132702",
  "strtgcode": "",
  "ordchegb": "01",
  "ordtm": "095636020",
  "orduserid": "hdkrggg4",
  "ordseqno": "0",
  "ordablesubstamt": "244160",
  "pchsamt": "0",
  "encrypt": "0",
  "accno2": "",
  "shtcode": "A005930",
  "contkey": "0",
  "brwmgmyn": "0",
  "seq": "000000154",
  "mtordseqno": "0",
  "lineseq": "200000001",
  "tongsingb": "40",
  "varlen": "50",
  "lpgb": "0",
  "rsvordno": "0",
  "spotordqty": "0",
  "cvrgseqno": "0",
  "filler": "",
  "hogagb": "0",
  "secbalqty": "0",
  "expcode": "KR7005930003",
  "prntordno": "86382",
  "ordablemny": "79459964",
  "pubip": "010130001138",
  "prvip": "",
  "funckey": "C",
  "accno": "20011132702",
  "compreq": "0",
  "orgordundrqty": "0",
  "ruseordamt": "0",
  "crdtpldgruseamt": " ",
  "ordordcancelqty": "0",
  "ordamt": "120000",
  "spareordno": "0",
  "termno": "",
  "etfhogagb": "00",
  "bpno": "106",
  "substamt": "244160",
  "mgempno": "999999106",
  "csgnsubstmgn": "0",
  "offset": "212",
  "sellableqty": "0",
  "groupid": "",
  "varhdlen": "0",
  "mnyordamt": "120000",
  "itemno": "0",
  "prtno": "0",
  "marketgb": "10",
  "ifinfo": "",
  "ordableruseqty": "0",
  "crdtuseamt": "0",
  "ordcmsnamt": "0",
  "secbalqtyd2": "0",
  "eventid": "",
  "csgnmnymgn": "300000",
  "pcbpno": "000",
  "orgordno": "0",
  "basketno": "0",
  "ifid": "000",
  "media": "HT",
  "filler1": "",
  "mbrno": "63",
  "proctm": "95636020",
  "ordsubstamt": "0",
  "lang": "K",
  "spotordableqty": "0",
  "cvrgordtp": "0",
  "ordqty": "2",
  "outgu": "",
  "msgcode": "0040",
  "futaccno": "00000000000000000000",
  "futmarketgb": "0",
  "admbrchno": "106",
  "comid": "063",
  "bnstp": "2",
  "user": "hdkrggg4",
  "nmcpysndno": "0"
 }
}
```

---

<a id="tr-SC1"></a>
## `SC1` 주식주문체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `grpId` | 그룹Id | String | Y | 20 | - |
| `trchno` | 트렌치번호 | String | Y | 10 | - |
| `trtzxLevytp` | 거래세징수구분 | String | Y | 1 | - |
| `ordtrxptncode` | 주문처리유형코드 | String | Y | 4 | - |
| `acntnm` | 계좌명 | String | Y | 40 | - |
| `trcode` | TRCODE | String | Y | 8 | SONAT000:신규주문<br/>SONAT001:정정주문<br/>SONAT002:취소주문<br/>SONAS100:체결확인 |
| `userid` | 사용자ID | String | Y | 16 | - |
| `agrgbrnno` | 집계지점번호 | String | Y | 3 | - |
| `regmktcode` | 등록시장코드 | String | Y | 2 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `opdrtnno` | 운용지시번호 | String | Y | 12 | - |
| `orgordmdfyqty` | 원주문정정수량 | String | Y | 16 | - |
| `avrpchsprc` | 평균매입가 | String | Y | 13 | 실서버 데이터 미제공 필드 |
| `exectime` | 체결시각 | String | Y | 9 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `mnymgnrat` | 현금증거금률 | String | Y | 7 | - |
| `mdfycnfqty` | 정정확인수량 | String | Y | 16 | - |
| `orgordcancqty` | 원주문취소수량 | String | Y | 16 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `execprc` | 체결가격 | String | Y | 13 | - |
| `mdfycnfprc` | 정정확인가격 | String | Y | 16 | - |
| `unercsellordqty` | 미체결매도주문수량 | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `cmsnamtexecamt` | 수수료체결금액 | String | Y | 16 | - |
| `ruseableamt` | 재사용가능금액 | String | Y | 16 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `flctqty` | 변동수량 | String | Y | 16 | - |
| `execno` | 체결번호 | String | Y | 10 | - |
| `lptp` | 유동성공급자구분 | String | Y | 1 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `ordno` | 주문번호 | String | Y | 10 | - |
| `futsmkttp` | 선물시장구분 | String | Y | 1 | - |
| `crdtexecamt` | 신용체결금액 | String | Y | 16 | - |
| `deposit` | 예수금 | String | Y | 16 | - |
| `frgrunqno` | 외국인고유번호 | String | Y | 6 | - |
| `crdayruseexecval` | 금일재사용체결금액 | String | Y | 16 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `ordacntno` | 주문계좌번호 | String | Y | 20 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `shtnIsuno` | 단축종목번호 | String | Y | 9 | - |
| `accno1` | 계좌번호 | String | Y | 11 | - |
| `strtgcode` | 전략코드 | String | Y | 6 | - |
| `ordseqno` | 주문회차 | String | Y | 10 | - |
| `Isunm` | 종목명 | String | Y | 40 | - |
| `ordablesubstamt` | 주문가능대용 | String | Y | 16 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `Isuno` | 종목번호 | String | Y | 12 | - |
| `accno2` | 계좌번호 | String | Y | 9 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `Loandt` | 대출일 | String | Y | 8 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `orduserId` | 주문자Id | String | Y | 16 | - |
| `mgmtbrnno` | 관리지점번호 | String | Y | 3 | - |
| `rjtqty` | 거부수량 | String | Y | 16 | - |
| `ordprcptncode` | 호가유형코드 | String | Y | 2 | 00:지정가<br/>03:시장가<br/>05:조건부지정가<br/>06:최유리지정가<br/>07:최우선지정가<br/>09:자사주<br/>10:매입인도(일반)<br/>13:시장가 (IOC)<br/>16:최유리지정가 (IOC)<br/>18:사용안함<br/>20:지정가(임의)<br/>23:시장가(임의)<br/>26:최유리지정가 (FOK)<br/>41:부분충족(프리보드)<br/>42:전량충족(프리보드)<br/>51:장중대량<br/>52:장중바스켓<br/>61:장개시전시간외<br/>62:사용안함<br/>63:경매매<br/>66:장전시간외경쟁대량<br/>67:장개시전시간외대량<br/>68:장개시전시간외바스켓<br/>69:장개시전시간외자사주<br/>71:신고대량전장시가<br/>72:사용안함<br/>73:신고대량종가<br/>76:장중경쟁대량<br/>77:장중대량<br/>78:장중바스켓<br/>79:사용안함<br/>80:매입인도(당일)<br/>81:시간외종가<br/>82:시간외단일가<br/>87:시간외대량<br/>88:바스켓주문<br/>89:시간외자사주<br/>91:자사주스톡옵션<br/>A1:stop order |
| `stdIsuno` | 표준종목번호 | String | Y | 12 | - |
| `pchsant` | 매입금액 | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `filler` | 예비영역 | String | Y | 6 | - |
| `secbalqty` | 잔고수량 | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `ordxctptncode` | 주문체결유형코드 | String | Y | 2 | 01:주문<br/>02:정정<br/>03:취소<br/>11:체결<br/>12 정정확인<br/>13 취소확인<br/>14 거부 |
| `canccnfqty` | 취소확인수량 | String | Y | 16 | - |
| `ordablemny` | 주문가능현금 | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `accno` | 계좌번호 | String | Y | 11 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `crdtpldgruseamt` | 신용담보재사용금 | String | Y | 16 | - |
| `ordamt` | 주문금액 | String | Y | 16 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `crdtpldgexecamt` | 신용담보체결금액 | String | Y | 16 | - |
| `ordcndi` | 주문조건 | String | Y | 1 | - |
| `rmndLoanamt` | 잔여대출금액 | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `substamt` | 대용금 | String | Y | 16 | - |
| `mgempno` | 관리사원번호 | String | Y | 9 | - |
| `csgnsubstmgn` | 위탁증거금대용 | String | Y | 16 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `rcptexectime` | 거래소수신체결시각 | String | Y | 9 | - |
| `sellableqty` | 매도주문가능수량 | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `spotexecqty` | 실물체결수량 | String | Y | 16 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `substmgnrat` | 대용증거금률 | String | Y | 9 | - |
| `ordavrexecprc` | 주문평균체결가격 | String | Y | 13 | - |
| `itemno` | 아이템번호 | String | Y | 10 | - |
| `mgntrncode` | 신용거래코드 | String | Y | 3 | [신규]<br/>000 : 보통<br/>001 : 유통융자신규<br/>003 : 자기융자신규<br/>005 : 유통대주신규<br/>007 : 자기대주신규<br/>080 : 예탁주식담보융자신규<br/>082 : 예탁채권담보융자신규<br/>[상환]<br/>101 : 유통융자상환<br/>103 : 자기융자상환<br/>105 : 유통대주상환<br/>107 : 자기대주상환<br/>111 : 유통융자전액상환<br/>113 : 자기융자전액상환<br/>180 : 예탁주식담보융자상환<br/>182 : 예탁채권담보융자상환<br/>188 : 담보대출전액상환 |
| `nsavtrdqty` | 비저축체결수량 | String | Y | 16 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `ordableruseqty` | 재사용가능수량(매도) | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `ptflno` | 포트폴리오번호 | String | Y | 10 | - |
| `secbalqtyd2` | 잔고수량(d2) | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `brwmgmtYn` | 차입관리여부 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `csgnmnymgn` | 위탁증거금현금 | String | Y | 16 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `orgordno` | 원주문번호 | String | Y | 10 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `mtiordseqno` | 복수주문일련번호 | String | Y | 10 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `orgordunercqty` | 원주문미체결수량 | String | Y | 16 | - |
| `mbrnmbrno` | 회원/비회원사번호 | String | Y | 3 | - |
| `futsLnkbrnno` | 선물연계지점번호 | String | Y | 3 | - |
| `commdacode` | 통신매체코드 | String | Y | 2 | - |
| `stslexecqty` | 공매도체결수량 | String | Y | 16 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `bfstdIsuno` | 전표준종목번호 | String | Y | 12 | - |
| `futsLnkacntno` | 선물연계계좌번호 | String | Y | 20 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `unercqty` | 미체결수량(주문) | String | Y | 16 | - |
| `execqty` | 체결수량 | String | Y | 16 | - |
| `adduptp` | 수수료합산코드 | String | Y | 2 | - |
| `bskno` | 바스켓번호 | String | Y | 10 | - |
| `spotordableqty` | 실물가능수량 | String | Y | 16 | 실서버 데이터 미제공 필드 |
| `ubstexecamt` | 대용체결금액 | String | Y | 16 | - |
| `cvrgordtp` | 반대매매주문구분 | String | Y | 1 | 0:일반<br/>1:자동반대매매<br/>2:지점반대매매<br/>3:예비주문에대한 본주문 |
| `ordqty` | 주문수량 | String | Y | 16 | - |
| `mnyexecamt` | 현금체결금액 | String | Y | 16 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `ordtrdptncode` | 주문거래유형코드 | String | Y | 2 | 00: 위탁<br/>01: 신용<br/>04: 선물대용 |
| `ordmktcode` | 주문시장코드 | String | Y | 2 | - |
| `ordptncode` | 주문유형코드 | String | Y | 2 | 00 해당없음<br/>01:현금매도<br/>02:현금매수<br/>03신용매도<br/>04:신용매수 |
| `prdayruseexecval` | 전일재사용체결금액 | String | Y | 16 | - |
| `comid` | COM ID | String | Y | 3 | - |
| `bnstp` | 매매구분 | String | Y | 1 | 1:매도<br/>2:매수 |
| `user` | 조작자ID | String | Y | 8 | - |
| `ordprc` | 주문가격 | String | Y | 13 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "SC1",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SC1"
 },
 "body": {
  "grpId": "A1100000000000000000",
  "trchno": "0",
  "trtzxLevytp": "1",
  "ordtrxptncode": "0",
  "acntnm": "우우돌",
  "trcode": "SONAS100",
  "userid": "hdkrggg4",
  "agrgbrnno": "106",
  "regmktcode": "10",
  "len": "1294",
  "opdrtnno": "0",
  "orgordmdfyqty": "0",
  "avrpchsprc": "0",
  "exectime": "095636107",
  "cont": "N",
  "mnymgnrat": "1.000",
  "mdfycnfqty": "0",
  "orgordcancqty": "0",
  "compress": "0",
  "execprc": "60000",
  "mdfycnfprc": "0",
  "unercsellordqty": "0",
  "cmsnamtexecamt": "0",
  "ruseableamt": "0",
  "gubun": "B",
  "trid": "2000095635771500",
  "flctqty": "1",
  "execno": "1",
  "lptp": "0",
  "varmsglen": "0",
  "ordno": "86382",
  "futsmkttp": "",
  "crdtexecamt": "0",
  "deposit": "79759964",
  "frgrunqno": "000000",
  "crdayruseexecval": "0",
  "trsrc": "L",
  "ordacntno": "20011132702",
  "reqcnt": " ",
  "shtnIsuno": "A005930",
  "accno1": "20011132702",
  "strtgcode": "",
  "ordseqno": "0",
  "Isunm": "삼성전자",
  "ordablesubstamt": "244160",
  "encrypt": "0",
  "Isuno": "KR7005930003",
  "accno2": "",
  "contkey": "0",
  "Loandt": "00000000",
  "seq": "000000154",
  "lineseq": "200000002",
  "varlen": "50",
  "orduserId": "hdkrggg4",
  "mgmtbrnno": "106",
  "rjtqty": "0",
  "ordprcptncode": "00",
  "stdIsuno": "KR7005930003",
  "pchsant": "0",
  "filler": "",
  "secbalqty": "0",
  "ordxctptncode": "11",
  "canccnfqty": "0",
  "ordablemny": "79459964",
  "pubip": "010130001138",
  "prvip": "",
  "funckey": "C",
  "accno": "20011132702",
  "compreq": "0",
  "crdtpldgruseamt": "0",
  "ordamt": "120000",
  "termno": "",
  "crdtpldgexecamt": "0",
  "ordcndi": "0",
  "rmndLoanamt": "0",
  "bpno": "106",
  "substamt": "244160",
  "mgempno": "999999106",
  "csgnsubstmgn": "0",
  "offset": "212",
  "rcptexectime": "095636098",
  "sellableqty": "0",
  "spotexecqty": "0",
  "varhdlen": "0",
  "substmgnrat": ".0000000",
  "ordavrexecprc": "60000",
  "itemno": "0",
  "mgntrncode": "000",
  "nsavtrdqty": "0",
  "ifinfo": "",
  "ordableruseqty": "0",
  "ptflno": "0",
  "secbalqtyd2": "0",
  "brwmgmtYn": "0",
  "eventid": "",
  "csgnmnymgn": "300000",
  "pcbpno": "000",
  "orgordno": "0",
  "ifid": "000",
  "media": "HT",
  "mtiordseqno": "0",
  "filler1": "",
  "orgordunercqty": "0",
  "mbrnmbrno": "0",
  "futsLnkbrnno": "",
  "commdacode": "40",
  "stslexecqty": "0",
  "proctm": "95636107",
  "bfstdIsuno": "KR7005930003",
  "futsLnkacntno": "",
  "lang": "K",
  "unercqty": "1",
  "execqty": "1",
  "adduptp": "40",
  "bskno": "0",
  "spotordableqty": "0",
  "ubstexecamt": "0",
  "cvrgordtp": "0",
  "ordqty": "2",
  "mnyexecamt": "60000",
  "outgu": "",
  "msgcode": "9999",
  "ordtrdptncode": "00",
  "ordmktcode": "10",
  "ordptncode": "02",
  "prdayruseexecval": "0",
  "comid": "063",
  "bnstp": "2",
  "user": "hdkrggg4",
  "ordprc": "60000"
 }
}
```

---

<a id="tr-SC2"></a>
## `SC2` 주식주문정정

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

_해당 항목 없음_

### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "SC2",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SC2"
 },
 "body": {
  "grpId": "A1100000000000000000",
  "trchno": "0",
  "trtzxLevytp": "0",
  "ordtrxptncode": "6",
  "acntnm": "우우돌",
  "trcode": "SONAS100",
  "userid": "hdkrggg4",
  "agrgbrnno": "106",
  "regmktcode": "10",
  "len": "1294",
  "opdrtnno": "0",
  "orgordmdfyqty": "1",
  "avrpchsprc": "0",
  "exectime": "100045203",
  "cont": "N",
  "mnymgnrat": "1.000",
  "mdfycnfqty": "1",
  "orgordcancqty": "0",
  "compress": "0",
  "execprc": "0",
  "mdfycnfprc": "70000",
  "unercsellordqty": "0",
  "cmsnamtexecamt": "0",
  "ruseableamt": "0",
  "gubun": "B",
  "trid": "2000100045171824",
  "flctqty": "0",
  "execno": "0",
  "lptp": "0",
  "varmsglen": "0",
  "ordno": "86383",
  "futsmkttp": "",
  "crdtexecamt": "0",
  "deposit": "79759964",
  "frgrunqno": "000000",
  "crdayruseexecval": "0",
  "trsrc": "L",
  "ordacntno": "20011132702",
  "reqcnt": " ",
  "shtnIsuno": "A005930",
  "accno1": "20011132702",
  "strtgcode": "",
  "ordseqno": "0",
  "Isunm": "삼성전자",
  "ordablesubstamt": "244160",
  "encrypt": "0",
  "Isuno": "KR7005930003",
  "accno2": "",
  "contkey": "0",
  "Loandt": "00000000",
  "seq": "000000172",
  "lineseq": "200000004",
  "varlen": "50",
  "orduserId": "hdkrggg4",
  "mgmtbrnno": "106",
  "rjtqty": "0",
  "ordprcptncode": "00",
  "stdIsuno": "KR7005930003",
  "pchsant": "0",
  "filler": "",
  "secbalqty": "0",
  "ordxctptncode": "12",
  "canccnfqty": "0",
  "ordablemny": "79449964",
  "pubip": "010130001138",
  "prvip": "",
  "funckey": "C",
  "accno": "20011132702",
  "compreq": "0",
  "crdtpldgruseamt": "0",
  "ordamt": "70000",
  "termno": "",
  "crdtpldgexecamt": "0",
  "ordcndi": "0",
  "rmndLoanamt": "0",
  "bpno": "106",
  "substamt": "244160",
  "mgempno": "999999106",
  "csgnsubstmgn": "0",
  "offset": "212",
  "rcptexectime": "100045203",
  "sellableqty": "0",
  "spotexecqty": "0",
  "varhdlen": "0",
  "substmgnrat": ".0000000",
  "ordavrexecprc": "0",
  "itemno": "0",
  "mgntrncode": "000",
  "nsavtrdqty": "0",
  "ifinfo": "",
  "ordableruseqty": "0",
  "ptflno": "0",
  "secbalqtyd2": "0",
  "brwmgmtYn": "0",
  "eventid": "",
  "csgnmnymgn": "310000",
  "pcbpno": "000",
  "orgordno": "86382",
  "ifid": "000",
  "media": "HT",
  "mtiordseqno": "0",
  "filler1": "",
  "orgordunercqty": "0",
  "mbrnmbrno": "0",
  "futsLnkbrnno": "",
  "commdacode": "40",
  "stslexecqty": "0",
  "proctm": "100045203",
  "bfstdIsuno": "KR7005930003",
  "futsLnkacntno": "",
  "lang": "K",
  "unercqty": "1",
  "execqty": "0",
  "adduptp": "40",
  "bskno": "0",
  "spotordableqty": "0",
  "ubstexecamt": "0",
  "cvrgordtp": "0",
  "ordqty": "1",
  "mnyexecamt": "0",
  "outgu": "1",
  "msgcode": "9999",
  "ordtrdptncode": "00",
  "ordmktcode": "10",
  "ordptncode": "02",
  "prdayruseexecval": "0",
  "comid": "063",
  "bnstp": "2",
  "user": "hdkrggg4",
  "ordprc": "70000"
 }
}
```

---

<a id="tr-SC3"></a>
## `SC3` 주식주문취소

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

_해당 항목 없음_

### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "SC3",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SC3"
 },
 "body": {
  "grpId": "A1100000000000000000",
  "trchno": "0",
  "trtzxLevytp": "0",
  "ordtrxptncode": "0",
  "acntnm": "우우돌",
  "trcode": "SONAS100",
  "userid": "hdkrggg4",
  "agrgbrnno": "106",
  "regmktcode": "10",
  "len": "1294",
  "opdrtnno": "0",
  "orgordmdfyqty": "0",
  "avrpchsprc": "0",
  "exectime": "150622765",
  "cont": "N",
  "mnymgnrat": ".000",
  "mdfycnfqty": "0",
  "orgordcancqty": "1",
  "compress": "0",
  "execprc": "0",
  "mdfycnfprc": "0",
  "unercsellordqty": "0",
  "cmsnamtexecamt": "0",
  "ruseableamt": "0",
  "gubun": "B",
  "trid": "4000150622737537",
  "flctqty": "0",
  "execno": "0",
  "lptp": "0",
  "varmsglen": "0",
  "ordno": "88343",
  "futsmkttp": "",
  "crdtexecamt": "0",
  "deposit": "78489774",
  "frgrunqno": "000000",
  "crdayruseexecval": "0",
  "trsrc": "L",
  "ordacntno": "20011132702",
  "reqcnt": " ",
  "shtnIsuno": "A000020",
  "accno1": "20011132702",
  "strtgcode": "",
  "ordseqno": "0",
  "Isunm": "동화약품",
  "ordablesubstamt": "1260000",
  "encrypt": "0",
  "Isuno": "KR7000020008",
  "accno2": "",
  "contkey": "0",
  "Loandt": "00000000",
  "seq": "000000009",
  "lineseq": "200000012",
  "varlen": "50",
  "orduserId": "hdkrggg4",
  "mgmtbrnno": "106",
  "rjtqty": "0",
  "ordprcptncode": "00",
  "stdIsuno": "KR7000020008",
  "pchsant": "0",
  "filler": "",
  "secbalqty": "0",
  "ordxctptncode": "13",
  "canccnfqty": "1",
  "ordablemny": "78173174",
  "pubip": "010130001138",
  "prvip": "",
  "funckey": "C",
  "accno": "20011132702",
  "compreq": "0",
  "crdtpldgruseamt": "0",
  "ordamt": "9500",
  "termno": "",
  "crdtpldgexecamt": "0",
  "ordcndi": "0",
  "rmndLoanamt": "0",
  "bpno": "106",
  "substamt": "1302000",
  "mgempno": "999999106",
  "csgnsubstmgn": "42000",
  "offset": "212",
  "rcptexectime": "150622765",
  "sellableqty": "0",
  "spotexecqty": "0",
  "varhdlen": "0",
  "substmgnrat": ".3000000",
  "ordavrexecprc": "0",
  "itemno": "0",
  "mgntrncode": "000",
  "nsavtrdqty": "0",
  "ifinfo": "",
  "ordableruseqty": "0",
  "ptflno": "0",
  "secbalqtyd2": "0",
  "brwmgmtYn": "0",
  "eventid": "",
  "csgnmnymgn": "316600",
  "pcbpno": "000",
  "orgordno": "88342",
  "ifid": "000",
  "media": "HT",
  "mtiordseqno": "0",
  "filler1": "",
  "orgordunercqty": "5",
  "mbrnmbrno": "0",
  "futsLnkbrnno": "",
  "commdacode": "40",
  "stslexecqty": "0",
  "proctm": "150622765",
  "bfstdIsuno": "KR7000020008",
  "futsLnkacntno": "",
  "lang": "K",
  "unercqty": "0",
  "execqty": "0",
  "adduptp": "40",
  "bskno": "0",
  "spotordableqty": "0",
  "ubstexecamt": "0",
  "cvrgordtp": "0",
  "ordqty": "1",
  "mnyexecamt": "0",
  "outgu": "1",
  "msgcode": "9999",
  "ordtrdptncode": "00",
  "ordmktcode": "10",
  "ordptncode": "02",
  "prdayruseexecval": "0",
  "comid": "063",
  "bnstp": "2",
  "user": "hdkrggg4",
  "ordprc": "0"
 }
}
```

---

<a id="tr-SC4"></a>
## `SC4` 주식주문거부

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

_해당 항목 없음_

---

<a id="tr-SHC"></a>
## `SHC` 상/하한가근접진입

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `sijanggubun` | 거래소/코스닥구분 | String | Y | 1 | - |
| `hname` | 종목명 | String | Y | 20 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `volincrate` | 거래증가율 | String | Y | 12.2 | - |
| `updnlmtprice` | 상/하한가 | String | Y | 8 | - |
| `updnlmtdrate` | 상/하한가대비율 | String | Y | 6.2 | - |
| `jnilvolume` | 전일거래량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `gwangubun` | 관리구분 | String | Y | 1 | - |
| `undergubun` | 이상급등구분 | String | Y | 1 | - |
| `tgubun` | 투자유의구분 | String | Y | 1 | - |
| `wgubun` | 우선주구분 | String | Y | 1 | - |
| `dishonest` | 불성실구분 | String | Y | 1 | - |
| `jkrate` | 증거금률 | String | Y | 1 | - |
| `updnlmtdaycnt` | 상한가/하한가연속일수 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "SHC",
  "tr_key": "1"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SHC",
  "tr_key": "1"
 },
 "body": {
  "wgubun": "0",
  "dishonest": "0",
  "change": "540",
  "shcode": "052460",
  "sign": "2",
  "tgubun": "0",
  "volume": "2198078",
  "sijanggubun": "2",
  "drate": "10.55",
  "updnlmtdrate": "14.89",
  "updnlmtprice": "6650",
  "price": "5660",
  "jnilvolume": "581641",
  "gwangubun": "0",
  "undergubun": "0",
  "volincrate": "200.00",
  "jkrate": "",
  "hname": "아이크래프트",
  "updnlmtdaycnt": "1"
 }
}
```

---

<a id="tr-SHD"></a>
## `SHD` 상/하한가근접이탈

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `sijanggubun` | 거래소/코스닥구분 | String | Y | 1 | - |
| `hname` | 종목명 | String | Y | 20 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `volincrate` | 거래증가율 | String | Y | 12.2 | - |
| `updnlmtprice` | 상/하한가 | String | Y | 8 | - |
| `updnlmtdrate` | 상/하한가대비율 | String | Y | 6.2 | - |
| `jnilvolume` | 전일거래량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `gwangubun` | 관리구분 | String | Y | 1 | - |
| `undergubun` | 이상급등구분 | String | Y | 1 | - |
| `tgubun` | 투자유의구분 | String | Y | 1 | - |
| `wgubun` | 우선주구분 | String | Y | 1 | - |
| `dishonest` | 불성실구분 | String | Y | 1 | - |
| `jkrate` | 증거금률 | String | Y | 1 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "SHD",
  "tr_key": "1"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SHD",
  "tr_key": "1"
 },
 "body": {
  "wgubun": "0",
  "dishonest": "0",
  "change": "440",
  "shcode": "900250",
  "sign": "2",
  "tgubun": "0",
  "volume": "12117762",
  "sijanggubun": "2",
  "drate": "9.94",
  "updnlmtdrate": "15.39",
  "updnlmtprice": "5750",
  "price": "4865",
  "jnilvolume": "20166876",
  "gwangubun": "0",
  "undergubun": "0",
  "volincrate": "0.00",
  "jkrate": "1",
  "hname": "크리스탈신소재"
 }
}
```

---

<a id="tr-SHI"></a>
## `SHI` 상/하한가진입

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `sijanggubun` | 거래소/코스닥구분 | String | Y | 1 | - |
| `hname` | 종목명 | String | Y | 20 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `volincrate` | 거래증가율 | String | Y | 12.2 | - |
| `totofferrem` | 매도호가총수량 | String | Y | 12 | - |
| `totbidrem` | 매수호가총수량 | String | Y | 12 | - |
| `updnlmtstime` | 상한가/하한가최종진입시간 | String | Y | 6 | - |
| `updnlmtdaycnt` | 상한가/하한가연속일수 | String | Y | 3 | - |
| `jnilvolume` | 전일거래량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `gwangubun` | 관리구분 | String | Y | 1 | - |
| `undergubun` | 이상급등구분 | String | Y | 1 | - |
| `tgubun` | 투자유의구분 | String | Y | 1 | - |
| `wgubun` | 우선주구분 | String | Y | 1 | - |
| `dishonest` | 불성실구분 | String | Y | 1 | - |
| `jkrate` | 증거금률 | String | Y | 1 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "SHI",
  "tr_key": "1"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SHI",
  "tr_key": "1"
 },
 "body": {
  "wgubun": "0",
  "dishonest": "0",
  "change": "8950",
  "shcode": "005950",
  "sign": "1",
  "updnlmtstime": "103324",
  "tgubun": "0",
  "volume": "10603317",
  "sijanggubun": "1",
  "drate": "29.93",
  "price": "38850",
  "jnilvolume": "10603307",
  "gwangubun": "0",
  "undergubun": "0",
  "volincrate": "0.00",
  "totofferrem": "446856",
  "jkrate": "1",
  "hname": "이수화학",
  "totbidrem": "83255",
  "updnlmtdaycnt": "1"
 }
}
```

---

<a id="tr-SHO"></a>
## `SHO` 상/하한가이탈

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `sijanggubun` | 거래소/코스닥구분 | String | Y | 1 | - |
| `hname` | 종목명 | String | Y | 20 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `volincrate` | 거래증가율 | String | Y | 12.2 | - |
| `updnlmtprice` | 상/하한가 | String | Y | 8 | - |
| `updnlmtchange` | 상/하한가대비 | String | Y | 8 | - |
| `updnlmtdrate` | 상/하한가대비율 | String | Y | 6.2 | - |
| `jnilvolume` | 전일거래량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `gwangubun` | 관리구분 | String | Y | 1 | - |
| `undergubun` | 이상급등구분 | String | Y | 1 | - |
| `tgubun` | 투자유의구분 | String | Y | 1 | - |
| `wgubun` | 우선주구분 | String | Y | 1 | - |
| `dishonest` | 불성실구분 | String | Y | 1 | - |
| `jkrate` | 증거금률 | String | Y | 1 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "SHO",
  "tr_key": "1"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "SHO",
  "tr_key": "1"
 },
 "body": {
  "wgubun": "0",
  "dishonest": "0",
  "change": "8900",
  "shcode": "005950",
  "sign": "2",
  "tgubun": "0",
  "volume": "10611096",
  "sijanggubun": "1",
  "drate": "29.77",
  "updnlmtdrate": "0.13",
  "updnlmtprice": "38850",
  "price": "38800",
  "jnilvolume": "8118866",
  "gwangubun": "0",
  "undergubun": "0",
  "updnlmtchange": "50",
  "volincrate": "0.00",
  "jkrate": "1",
  "hname": "이수화학"
 }
}
```

---

<a id="tr-VI_"></a>
## `VI_` VI발동해제

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 6 | 단축코드 6자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `vi_gubun` | 구분(0:해제1:정적발동2:동적발동3:정적&동적) | String | Y | 1 | - |
| `svi_recprice` | 정적VI발동기준가격 | String | Y | 8 | - |
| `dvi_recprice` | 동적VI발동기준가격 | String | Y | 8 | - |
| `vi_trgprice` | VI발동가격 | String | Y | 8 | - |
| `shcode` | 단축코드(KEY) | String | Y | 6 | - |
| `ref_shcode` | 참조코드 | String | Y | 6 | - |
| `time` | 시간 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "VI_",
  "tr_key": "145270"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "VI_",
  "tr_key": "145270"
 },
 "body": {
  "svi_recprice": "0",
  "vi_gubun": "0",
  "shcode": "145270",
  "time": "092415",
  "vi_trgprice": "0",
  "dvi_recprice": "0",
  "ref_shcode": "145270"
 }
}
```

---

<a id="tr-YJ_"></a>
## `YJ_` 예상지수

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 시간 | String | Y | 6 | - |
| `jisu` | 예상지수 | String | Y | 8.2 | - |
| `sign` | 예상전일대비구분 | String | Y | 1 | - |
| `change` | 예상전일비 | String | Y | 8.2 | - |
| `drate` | 예상등락율 | String | Y | 6.2 | - |
| `cvolume` | 예상체결량 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 8 | - |
| `value` | 예상거래대금 | String | Y | 8 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "YJ_",
  "tr_key": "001"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "YJ_",
  "tr_key": "001"
 },
 "body": {
  "jisu": "2645.21",
  "volume": "2453",
  "drate": "0.28",
  "change": "7.26",
  "upcode": "001",
  "sign": "2",
  "time": "084150",
  "value": "48520",
  "cvolume": "2453"
 }
}
```

---

<a id="tr-YK3"></a>
## `YK3` KOSDAQ예상체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `yeprice` | 예상체결가격 | String | Y | 8 | - |
| `yevolume` | 예상체결수량 | String | Y | 12 | - |
| `jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `jnilchange` | 예상체결가전일종가대비 | String | Y | 8 | - |
| `jnilydrate` | 예상체결가전일종가등락율 | String | Y | 6.2 | - |
| `yofferho0` | 예상매도호가 | String | Y | 8 | - |
| `ybidho0` | 예상매수호가 | String | Y | 8 | - |
| `yofferrem0` | 예상매도호가수량 | String | Y | 12 | - |
| `ybidrem0` | 예상매수호가수량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "YK3",
  "tr_key": "086520"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "YK3",
  "tr_key": "086520"
 },
 "body": {
  "jnilysign": "2",
  "yofferrem0": "502",
  "jnilchange": "14000",
  "yeprice": "763000",
  "ybidho0": "762000",
  "shcode": "086520",
  "yevolume": "6386",
  "hotime": "085113",
  "ybidrem0": "591",
  "jnilydrate": "1.87",
  "yofferho0": "763000"
 }
}
```

---

<a id="tr-YS3"></a>
## `YS3` KOSPI예상체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `yeprice` | 예상체결가격 | String | Y | 8 | - |
| `yevolume` | 예상체결수량 | String | Y | 12 | - |
| `jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `jnilchange` | 예상체결가전일종가대비 | String | Y | 8 | - |
| `jnilydrate` | 예상체결가전일종가등락율 | String | Y | 6.2 | - |
| `yofferho0` | 예상매도호가 | String | Y | 8 | - |
| `ybidho0` | 예상매수호가 | String | Y | 8 | - |
| `yofferrem0` | 예상매도호가수량 | String | Y | 12 | - |
| `ybidrem0` | 예상매수호가수량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijk5NGZkNjI5LWY4OGItNGQ0Ni05NTE0LTJjNmQzMjM1MWIyYSIsIm5iZiI6MTY4NjY0MDc3NywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzI3MTc3LCJpYXQiOjE2ODY2NDA3NzcsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.WT1pgGw-gawv2GAQiRNcEphlv3BfXZfeVG03wwBCoCKpUYYC0l019Oc0JJIqoR41WHm8kEuNgDgYhlib_LxI7g",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "YS3",
  "tr_key": "005930"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "YS3",
  "tr_key": "005930"
 },
 "body": {
  "jnilysign": "2",
  "yofferrem0": "14699",
  "jnilchange": "400",
  "yeprice": "72400",
  "ybidho0": "72300",
  "shcode": "005930",
  "yevolume": "208335",
  "hotime": "085201",
  "ybidrem0": "32693",
  "jnilydrate": "0.56",
  "yofferho0": "72400"
 }
}
```

---

<a id="tr-ESN"></a>
## `ESN` 뉴ELW투자지표민감도

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 시간 | String | Y | 6 | - |
| `theoryprice` | 장중이론가 | String | Y | 10.2 | - |
| `delt` | 델타 | String | Y | 7.6 | - |
| `gama` | 감마 | String | Y | 7.6 | - |
| `ceta` | 세타 | String | Y | 12.6 | - |
| `vega` | 베가 | String | Y | 12.6 | - |
| `rhox` | 로우 | String | Y | 12.6 | - |
| `impv` | 내재변동성 | String | Y | 5.2 | - |
| `egearing` | E.기어링 | String | Y | 8.2 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `elwclose` | ELW현재가 | String | Y | 8 | - |
| `sign` | ELW전일대비구분 | String | Y | 1 | - |
| `change` | ELW전일대비 | String | Y | 8 | - |
| `date` | 일자 | String | Y | 8 | - |
| `tickvalue` | 틱환산 | String | Y | 10.2 | - |
| `lp_impv` | LP내재변동성 | String | Y | 5.2 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "ESN",
  "tr_key": "52HAAA"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "ESN",
  "tr_key": "52HAAA"
 },
 "body": {
  "date": "20230920",
  "ceta": "-0.556109",
  "elwclose": "70",
  "delt": "0.544628",
  "shcode": "52HAAA",
  "change": "5",
  "sign": "5",
  "rhox": "1.173105",
  "lp_impv": "33.72",
  "egearing": "7.31",
  "time": "091930",
  "impv": "34.08",
  "theoryprice": "52.39",
  "tickvalue": "0.27",
  "gama": "0.000120",
  "vega": "1.914977"
 }
}
```

---

<a id="tr-h2_"></a>
## `h2_` ELW장전시간외호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `tmofferrem` | 시간외매도잔량 | String | Y | 12 | - |
| `tmbidrem` | 시간외매수잔량 | String | Y | 12 | - |
| `pretmoffercha` | 시간외매도수량직전대비 | String | Y | 12 | - |
| `pretmbidcha` | 시간외매수수량직전대비 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


---

<a id="tr-h3_"></a>
## `h3_` ELW호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | String | Y | 7 | - |
| `bidho1` | 매수호가1 | String | Y | 7 | - |
| `offerrem1` | 매도호가잔량1 | String | Y | 9 | - |
| `bidrem1` | 매수호가잔량1 | String | Y | 9 | - |
| `lp_offerho1` | LP매도호가수량1 | String | Y | 9 | - |
| `lp_bidho1` | LP매수호가수량1 | String | Y | 9 | - |
| `offerho2` | 매도호가2 | String | Y | 7 | - |
| `bidho2` | 매수호가2 | String | Y | 7 | - |
| `offerrem2` | 매도호가잔량2 | String | Y | 9 | - |
| `bidrem2` | 매수호가잔량2 | String | Y | 9 | - |
| `lp_offerho2` | LP매도호가수량2 | String | Y | 9 | - |
| `lp_bidho2` | LP매수호가수량2 | String | Y | 9 | - |
| `offerho3` | 매도호가3 | String | Y | 7 | - |
| `bidho3` | 매수호가3 | String | Y | 7 | - |
| `offerrem3` | 매도호가잔량3 | String | Y | 9 | - |
| `bidrem3` | 매수호가잔량3 | String | Y | 9 | - |
| `lp_offerho3` | LP매도호가수량3 | String | Y | 9 | - |
| `lp_bidho3` | LP매수호가수량3 | String | Y | 9 | - |
| `offerho4` | 매도호가4 | String | Y | 7 | - |
| `bidho4` | 매수호가4 | String | Y | 7 | - |
| `offerrem4` | 매도호가잔량4 | String | Y | 9 | - |
| `bidrem4` | 매수호가잔량4 | String | Y | 9 | - |
| `lp_offerho4` | LP매도호가수량4 | String | Y | 9 | - |
| `lp_bidho4` | LP매수호가수량4 | String | Y | 9 | - |
| `offerho5` | 매도호가5 | String | Y | 7 | - |
| `bidho5` | 매수호가5 | String | Y | 7 | - |
| `offerrem5` | 매도호가잔량5 | String | Y | 9 | - |
| `bidrem5` | 매수호가잔량5 | String | Y | 9 | - |
| `lp_offerho5` | LP매도호가수량5 | String | Y | 9 | - |
| `lp_bidho5` | LP매수호가수량5 | String | Y | 9 | - |
| `offerho6` | 매도호가6 | String | Y | 7 | - |
| `bidho6` | 매수호가6 | String | Y | 7 | - |
| `offerrem6` | 매도호가잔량6 | String | Y | 9 | - |
| `bidrem6` | 매수호가잔량6 | String | Y | 9 | - |
| `lp_offerho6` | LP매도호가수량6 | String | Y | 9 | - |
| `lp_bidho6` | LP매수호가수량6 | String | Y | 9 | - |
| `offerho7` | 매도호가7 | String | Y | 7 | - |
| `bidho7` | 매수호가7 | String | Y | 7 | - |
| `offerrem7` | 매도호가잔량7 | String | Y | 9 | - |
| `bidrem7` | 매수호가잔량7 | String | Y | 9 | - |
| `lp_offerho7` | LP매도호가수량7 | String | Y | 9 | - |
| `lp_bidho7` | LP매수호가수량7 | String | Y | 9 | - |
| `offerho8` | 매도호가8 | String | Y | 7 | - |
| `bidho8` | 매수호가8 | String | Y | 7 | - |
| `offerrem8` | 매도호가잔량8 | String | Y | 9 | - |
| `bidrem8` | 매수호가잔량8 | String | Y | 9 | - |
| `lp_offerho8` | LP매도호가수량8 | String | Y | 9 | - |
| `lp_bidho8` | LP매수호가수량8 | String | Y | 9 | - |
| `offerho9` | 매도호가9 | String | Y | 7 | - |
| `bidho9` | 매수호가9 | String | Y | 7 | - |
| `offerrem9` | 매도호가잔량9 | String | Y | 9 | - |
| `bidrem9` | 매수호가잔량9 | String | Y | 9 | - |
| `lp_offerho9` | LP매도호가수량9 | String | Y | 9 | - |
| `lp_bidho9` | LP매수호가수량9 | String | Y | 9 | - |
| `offerho10` | 매도호가10 | String | Y | 7 | - |
| `bidho10` | 매수호가10 | String | Y | 7 | - |
| `offerrem10` | 매도호가잔량10 | String | Y | 9 | - |
| `bidrem10` | 매수호가잔량10 | String | Y | 9 | - |
| `lp_offerho10` | LP매도호가수량10 | String | Y | 9 | - |
| `lp_bidho10` | LP매수호가수량10 | String | Y | 9 | - |
| `totofferrem` | 총매도호가잔량 | String | Y | 9 | - |
| `totbidrem` | 총매수호가잔량 | String | Y | 9 | - |
| `donsigubun` | 동시호가구분 | String | Y | 1 | - |
| `spread` | 스프레드 | String | Y | 6.2 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "h3_",
  "tr_key": "52HAAA"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "h3_",
  "tr_key": "52HAAA"
 },
 "body": {
  "offerho4": "0",
  "offerho3": "0",
  "offerho6": "0",
  "offerho5": "0",
  "offerho8": "0",
  "offerho7": "0",
  "offerho9": "0",
  "lp_bidho5": "0",
  "lp_bidho6": "0",
  "lp_bidho7": "0",
  "lp_bidho8": "0",
  "lp_bidho1": "30000",
  "lp_bidho2": "0",
  "donsigubun": "1",
  "lp_bidho3": "0",
  "lp_bidho4": "0",
  "lp_bidho9": "0",
  "hotime": "090416",
  "offerho2": "0",
  "offerho1": "70",
  "lp_offerho9": "0",
  "lp_offerho8": "0",
  "offerho10": "0",
  "lp_offerho3": "0",
  "lp_offerho2": "0",
  "lp_offerho1": "29980",
  "totofferrem": "29980",
  "lp_offerho7": "0",
  "lp_offerho6": "0",
  "lp_offerho5": "0",
  "lp_offerho4": "0",
  "totbidrem": "80000",
  "offerrem2": "0",
  "bidho5": "0",
  "offerrem3": "0",
  "bidho4": "0",
  "offerrem4": "0",
  "bidho7": "0",
  "offerrem5": "0",
  "bidho6": "0",
  "bidho9": "0",
  "bidho8": "0",
  "offerrem1": "29980",
  "offerrem6": "0",
  "offerrem7": "0",
  "offerrem8": "0",
  "offerrem9": "0",
  "bidrem3": "0",
  "bidrem4": "0",
  "bidrem1": "30000",
  "bidrem2": "50000",
  "lp_bidho10": "0",
  "bidrem9": "0",
  "bidho1": "65",
  "bidrem7": "0",
  "bidrem8": "0",
  "bidho3": "0",
  "bidrem5": "0",
  "bidho2": "5",
  "bidrem6": "0",
  "bidrem10": "0",
  "bidho10": "0",
  "shcode": "52HAAA",
  "spread": "0",
  "lp_offerho10": "0",
  "offerrem10": "0"
 }
}
```

---

<a id="tr-k1_"></a>
## `k1_` ELW거래원

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerno1` | 매도증권사코드1 | String | Y | 3 | - |
| `bidno1` | 매수증권사코드1 | String | Y | 3 | - |
| `offertrad1` | 매도회원사명1 | String | Y | 6 | - |
| `bidtrad1` | 매수회원사명1 | String | Y | 6 | - |
| `tradmdvol1` | 매도거래량1 | String | Y | 10 | - |
| `tradmsvol1` | 매수거래량1 | String | Y | 10 | - |
| `tradmdrate1` | 매도거래량비중1 | String | Y | 6.2 | - |
| `tradmsrate1` | 매도거래량비중1 | String | Y | 6.2 | - |
| `tradmdcha1` | 매도거래량직전대비1 | String | Y | 10 | - |
| `tradmscha1` | 매수거래량직전대비1 | String | Y | 10 | - |
| `offerno2` | 매도증권사코드2 | String | Y | 3 | - |
| `bidno2` | 매수증권사코드2 | String | Y | 3 | - |
| `offertrad2` | 매도회원사명2 | String | Y | 6 | - |
| `bidtrad2` | 매수회원사명2 | String | Y | 6 | - |
| `tradmdvol2` | 매도거래량2 | String | Y | 10 | - |
| `tradmsvol2` | 매수거래량2 | String | Y | 10 | - |
| `tradmdrate2` | 매도거래량비중2 | String | Y | 6.2 | - |
| `tradmsrate2` | 매수거래량비중2 | String | Y | 6.2 | - |
| `tradmdcha2` | 매도거래량직전대비2 | String | Y | 10 | - |
| `tradmscha2` | 매수거래량직전대비2 | String | Y | 10 | - |
| `offerno3` | 매도증권사코드3 | String | Y | 3 | - |
| `bidno3` | 매수증권사코드3 | String | Y | 3 | - |
| `offertrad3` | 매도회원사명3 | String | Y | 6 | - |
| `bidtrad3` | 매수회원사명3 | String | Y | 6 | - |
| `tradmdvol3` | 매도거래량3 | String | Y | 10 | - |
| `tradmsvol3` | 매수거래량3 | String | Y | 10 | - |
| `tradmdrate3` | 매도거래량비중3 | String | Y | 6.2 | - |
| `tradmsrate3` | 매수거래량비중3 | String | Y | 6.2 | - |
| `tradmdcha3` | 매도거래량직전대비3 | String | Y | 10 | - |
| `tradmscha3` | 매수거래량직전대비3 | String | Y | 10 | - |
| `offerno4` | 매도증권사코드4 | String | Y | 3 | - |
| `bidno4` | 매수증권사코드4 | String | Y | 3 | - |
| `offertrad4` | 매도회원사명4 | String | Y | 6 | - |
| `bidtrad4` | 매수회원사명4 | String | Y | 6 | - |
| `tradmdvol4` | 매도거래량4 | String | Y | 10 | - |
| `tradmsvol4` | 매수거래량4 | String | Y | 10 | - |
| `tradmdrate4` | 매도거래량비중4 | String | Y | 6.2 | - |
| `tradmsrate4` | 매수거래량비중4 | String | Y | 6.2 | - |
| `tradmdcha4` | 매도거래량직전대비4 | String | Y | 10 | - |
| `tradmscha4` | 매수거래량직전대비4 | String | Y | 10 | - |
| `offerno5` | 매도증권사코드5 | String | Y | 3 | - |
| `bidno5` | 매수증권사코드5 | String | Y | 3 | - |
| `offertrad5` | 매도회원사명5 | String | Y | 6 | - |
| `bidtrad5` | 매수회원사명5 | String | Y | 6 | - |
| `tradmdvol5` | 매도거래량5 | String | Y | 10 | - |
| `tradmsvol5` | 매수거래량5 | String | Y | 10 | - |
| `tradmdrate5` | 매도거래량비중5 | String | Y | 6.2 | - |
| `tradmsrate5` | 매수거래량비중5 | String | Y | 6.2 | - |
| `tradmdcha5` | 매도거래량직전대비5 | String | Y | 10 | - |
| `tradmscha5` | 매수거래량직전대비5 | String | Y | 10 | - |
| `ftradmdvol` | 외국계증권사매도합계 | String | Y | 10 | - |
| `ftradmsvol` | 외국계증권사매수합계 | String | Y | 10 | - |
| `ftradmdrate` | 외국계증권사매도거래량비중 | String | Y | 6.2 | - |
| `ftradmsrate` | 외국계증권사매수거래량비중 | String | Y | 6.2 | - |
| `ftradmdcha` | 외국계증권사매도거래량직전대비 | String | Y | 10 | - |
| `ftradmscha` | 외국계증권사매수거래량직전대비 | String | Y | 10 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "k1_",
  "tr_key": "52HAAA"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "k1_",
  "tr_key": "52HAAA"
 },
 "body": {
  "tradmdrate1": "100.00",
  "tradmdvol5": "0",
  "tradmdvol3": "0",
  "tradmdrate3": "0.00",
  "tradmdrate2": "0.00",
  "tradmdvol4": "0",
  "offerno2": "",
  "tradmdrate5": "0.00",
  "offerno1": "005",
  "tradmdrate4": "0.00",
  "offerno4": "",
  "offerno3": "",
  "bidtrad4": "",
  "offerno5": "",
  "bidtrad5": "",
  "bidtrad2": "",
  "bidtrad3": "",
  "tradmdvol1": "30",
  "bidtrad1": "키움증",
  "tradmdvol2": "0",
  "offertrad5": "",
  "tradmscha2": "0",
  "tradmscha1": "20",
  "tradmscha4": "0",
  "tradmscha3": "0",
  "offertrad2": "",
  "offertrad1": "미래에",
  "offertrad4": "",
  "offertrad3": "",
  "tradmdcha5": "0",
  "tradmdcha4": "0",
  "tradmscha5": "0",
  "ftradmscha": "0000000000",
  "ftradmdvol": "0000000000",
  "tradmdcha1": "20",
  "tradmdcha3": "0",
  "tradmdcha2": "0",
  "bidno1": "050",
  "bidno3": "",
  "tradmsvol5": "0",
  "bidno2": "",
  "tradmsvol4": "0",
  "bidno5": "",
  "bidno4": "",
  "tradmsvol1": "30",
  "tradmsvol3": "0",
  "tradmsvol2": "0",
  "tradmsrate2": "0.00",
  "tradmsrate1": "100.00",
  "tradmsrate4": "0.00",
  "tradmsrate3": "0.00",
  "tradmsrate5": "0.00",
  "ftradmsvol": "0000000000",
  "ftradmdcha": "0000000000",
  "ftradmsrate": "0.00",
  "shcode": "52HAAA",
  "ftradmdrate": "0.00"
 }
}
```

---

<a id="tr-s2_"></a>
## `s2_` ELW우선호가

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerho` | 매도호가 | String | Y | 8 | - |
| `bidho` | 매수호가 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "s2_",
  "tr_key": "52HAAA"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "s2_",
  "tr_key": "52HAAA"
 },
 "body": {
  "bidho": "5",
  "shcode": "52HAAA",
  "offerho": "70"
 }
}
```

---

<a id="tr-s3_"></a>
## `s3_` ELW체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `chetime` | 체결시간 | String | Y | 6 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `open` | 시가 | String | Y | 8 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `high` | 고가 | String | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | String | Y | 8 | - |
| `cgubun` | 체결구분 | String | Y | 1 | - |
| `cvolume` | 체결량 | String | Y | 8 | - |
| `volume` | 누적거래량 | String | Y | 12 | - |
| `value` | 누적거래대금 | String | Y | 12 | - |
| `mdvolume` | 매도누적체결량 | String | Y | 12 | - |
| `mdchecnt` | 매도누적체결건수 | String | Y | 8 | - |
| `msvolume` | 매수누적체결량 | String | Y | 12 | - |
| `mschecnt` | 매수누적체결건수 | String | Y | 8 | - |
| `cpower` | 체결강도 | String | Y | 9.2 | - |
| `w_avrg` | 가중평균가 | String | Y | 8 | - |
| `offerho` | 매도호가 | String | Y | 8 | - |
| `bidho` | 매수호가 | String | Y | 8 | - |
| `status` | 장정보 | String | Y | 2 | - |
| `jnilvolume` | 전일동시간대거래량 | String | Y | 12 | - |
| `premium` | 프리미엄 | String | Y | 8.2 | - |
| `moneyness` | ATM구분 | String | Y | 1 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |
| `lpvolume` | LP보유수량 | String | Y | 15 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "s3_",
  "tr_key": "52HAAA"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "s3_",
  "tr_key": "52HAAA"
 },
 "body": {
  "mdchecnt": "1",
  "sign": "5",
  "mschecnt": "1",
  "mdvolume": "10",
  "w_avrg": "76",
  "cpower": "200.00",
  "offerho": "70",
  "cvolume": "20",
  "high": "85",
  "bidho": "65",
  "premium": "7.35",
  "low": "70",
  "price": "70",
  "cgubun": "+",
  "value": "0",
  "change": "5",
  "shcode": "52HAAA",
  "chetime": "090416",
  "opentime": "090201",
  "lowtime": "090416",
  "volume": "30",
  "drate": "-6.67",
  "hightime": "090201",
  "jnilvolume": "0",
  "msvolume": "20",
  "lpvolume": "8165760",
  "open": "85",
  "moneyness": "2",
  "status": "00"
 }
}
```

---

<a id="tr-s4_"></a>
## `s4_` ELW기세

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | String | Y | 8 | - |
| `drate` | 등락율 | String | Y | 6.2 | - |
| `price` | 현재가 | String | Y | 8 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `open` | 시가 | String | Y | 8 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `high` | 고가 | String | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | String | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


---

<a id="tr-Ys3"></a>
## `Ys3` ELW예상체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | 단축코드 6자리 또는 8자리 (단건, 연속), (계좌등록/해제 일 경우 필수값 아님) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `yeprice` | 예상체결가격 | String | Y | 8 | - |
| `yevolume` | 예상체결수량 | String | Y | 12 | - |
| `jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `jnilchange` | 예상체결가전일종가대비 | String | Y | 8 | - |
| `jnilydrate` | 예상체결가전일종가등락율 | String | Y | 6.2 | - |
| `yofferho0` | 예상매도호가 | String | Y | 8 | - |
| `ybidho0` | 예상매수호가 | String | Y | 8 | - |
| `yofferrem0` | 예상매도호가수량 | String | Y | 12 | - |
| `ybidrem0` | 예상매수호가수량 | String | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "Ys3",
  "tr_key": "52HAAA"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "Ys3",
  "tr_key": "52HAAA"
 },
 "body": {
  "jnilysign": "3",
  "yofferrem0": "0",
  "jnilchange": "0",
  "yeprice": "0",
  "ybidho0": "80",
  "shcode": "52HAAA",
  "yevolume": "0",
  "hotime": "085544",
  "ybidrem0": "10",
  "jnilydrate": "0.00",
  "yofferho0": "0"
 }
}
```

---

<a id="tr-NS3"></a>
## `NS3` (NXT)체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `chetime` | 체결시간 | String | Y | 6 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | Number | Y | 8 | - |
| `drate` | 등락율 | Number | Y | 6.2 | - |
| `price` | 현재가 | Number | Y | 8 | - |
| `opentime` | 시가시간 | String | Y | 6 | - |
| `open` | 시가 | Number | Y | 8 | - |
| `hightime` | 고가시간 | Number | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | Number | Y | 8 | - |
| `cgubun` | 체결구분 | String | Y | 1 | - |
| `cvolume` | 체결량 | Number | Y | 8 | - |
| `volume` | 누적거래량 | Number | Y | 12 | - |
| `value` | 누적거래대금 | Number | Y | 12 | - |
| `mdvolume` | 매도누적체결량 | Number | Y | 12 | - |
| `mdchecnt` | 매도누적체결건수 | Number | Y | 8 | - |
| `msvolume` | 매수누적체결량 | Number | Y | 12 | - |
| `mschecnt` | 매수누적체결건수 | Number | Y | 8 | - |
| `cpower` | 체결강도 | Number | Y | 9.2 | - |
| `w_avrg` | 가중평균가 | Number | Y | 8 | - |
| `offerho` | 매도호가 | Number | Y | 8 | - |
| `bidho` | 매수호가 | Number | Y | 8 | - |
| `status` | 장정보 | String | Y | 2 | - |
| `jnilvolume` | 전일동시간대거래량 | Number | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlhZjc0YjZkLTI2OGItNDY5Yy1iNjk2LThjYmQ2ZjBiMjI3MSIsIm5iZiI6MTc0MTczMjM1MywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQxODE2Nzk5LCJpYXQiOjE3NDE3MzIzNTMsImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.I4s4ZGWyG05scODLcBhKzoSDGNy80Z03fXja1KkZlmznugb-6gIkb0ngZTDzHuNCwcuhjT6SAx5dgWwVkm",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NS3",
  "tr_key": "N010950   "
 }
}
```

### 응답 Example

```json
{
	"header": {
		"tr_cd": "NS3",
		"tr_key": "N010950   "
	},
	"body": {
		"mdchecnt": "662",
		"sign": "2",
		"mschecnt": "608",
		"mdvolume": "16648",
		"w_avrg": "61188",
		"cpower": "62.53",
		"offerho": "60600",
		"cvolume": "1",
		"high": "62700",
		"bidho": "60500",
		"low": "60300",
		"price": "60600",
		"cgubun": "+",
		"value": "1656",
		"change": "400",
		"shcode": "010950",
		"chetime": "143216",
		"ex_shcode": "N010950",
		"opentime": "080035",
		"lowtime": "094023",
		"volume": "27058",
		"drate": "0.66",
		"hightime": "080908",
		"jnilvolume": "44972",
		"msvolume": "10410",
		"exchname": "NXT",
		"open": "60400",
		"status": "00"
	}
}
```

---

<a id="tr-NH1"></a>
## `NH1` (NXT)호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | Number | Y | 7 | - |
| `bidho1` | 매수호가1 | Number | Y | 7 | - |
| `offerrem1` | 매도호가잔량1 | Number | Y | 9 | - |
| `bidrem1` | 매수호가잔량1 | Number | Y | 9 | - |
| `offerho2` | 매도호가2 | Number | Y | 7 | - |
| `bidho2` | 매수호가2 | Number | Y | 7 | - |
| `offerrem2` | 매도호가잔량2 | Number | Y | 9 | - |
| `bidrem2` | 매수호가잔량2 | Number | Y | 9 | - |
| `offerho3` | 매도호가3 | Number | Y | 7 | - |
| `bidho3` | 매수호가3 | Number | Y | 7 | - |
| `offerrem3` | 매도호가잔량3 | Number | Y | 9 | - |
| `bidrem3` | 매수호가잔량3 | Number | Y | 9 | - |
| `offerho4` | 매도호가4 | Number | Y | 7 | - |
| `bidho4` | 매수호가4 | Number | Y | 7 | - |
| `offerrem4` | 매도호가잔량4 | Number | Y | 9 | - |
| `bidrem4` | 매수호가잔량4 | Number | Y | 9 | - |
| `offerho5` | 매도호가5 | Number | Y | 7 | - |
| `bidho5` | 매수호가5 | Number | Y | 7 | - |
| `offerrem5` | 매도호가잔량5 | Number | Y | 9 | - |
| `bidrem5` | 매수호가잔량5 | Number | Y | 9 | - |
| `offerho6` | 매도호가6 | Number | Y | 7 | - |
| `bidho6` | 매수호가6 | Number | Y | 7 | - |
| `offerrem6` | 매도호가잔량6 | Number | Y | 9 | - |
| `bidrem6` | 매수호가잔량6 | Number | Y | 9 | - |
| `offerho7` | 매도호가7 | Number | Y | 7 | - |
| `bidho7` | 매수호가7 | Number | Y | 7 | - |
| `offerrem7` | 매도호가잔량7 | Number | Y | 9 | - |
| `bidrem7` | 매수호가잔량7 | Number | Y | 9 | - |
| `offerho8` | 매도호가8 | Number | Y | 7 | - |
| `bidho8` | 매수호가8 | Number | Y | 7 | - |
| `offerrem8` | 매도호가잔량8 | Number | Y | 9 | - |
| `bidrem8` | 매수호가잔량8 | Number | Y | 9 | - |
| `offerho9` | 매도호가9 | Number | Y | 7 | - |
| `bidho9` | 매수호가9 | Number | Y | 7 | - |
| `offerrem9` | 매도호가잔량9 | Number | Y | 9 | - |
| `bidrem9` | 매수호가잔량9 | Number | Y | 9 | - |
| `offerho10` | 매도호가10 | Number | Y | 7 | - |
| `bidho10` | 매수호가10 | Number | Y | 7 | - |
| `offerrem10` | 매도호가잔량10 | Number | Y | 9 | - |
| `bidrem10` | 매수호가잔량10 | Number | Y | 9 | - |
| `totofferrem` | 총매도호가잔량 | Number | Y | 9 | - |
| `totbidrem` | 총매수호가잔량 | Number | Y | 9 | - |
| `donsigubun` | 동시호가구분 | String | Y | 1 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `alloc_gubun` | 배분적용구분 | String | Y | 1 | - |
| `volume` | 누적거래량 | Number | Y | 12 | - |
| `midprice` | 중간가격 | Number | Y | 8 | - |
| `offermidsumrem` | 매도중간가잔량합계수량 | Number | Y | 9 | - |
| `bidmidsumrem` | 매수중간가잔량합계수량 | Number | Y | 9 | - |
| `midsumrem` | 중간가잔량합계수량 | Number | Y | 9 | - |
| `midsumremgubun` | 중간가잔량구분(''없음'1'매도'2'매수) | String | Y | 1 | ''없음'1'매도'2'매수 |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImU4Njk4Y2YyLWJiMTEtNGZlMy05OWE5LWIwNGFlOTE3MDJkOSIsIm5iZiI6MTc0MjQyNDQyOCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTA3OTk5LCJpYXQiOjE3NDI0MjQ0MjgsImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.1u2cfXonwmOrWQTvfPwmFvevvexV-NnqjR9u1lRMAb1-6lvddRGQ8CnWWakWWIfvMZ8",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NH1",
  "tr_key": "N000880   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NH1",
        "tr_key": "N000880   "
    },
    "body": {
        "offerho4": "46900",
        "offerho3": "46850",
        "offerho6": "47000",
        "offerho5": "46950",
        "offerho8": "47100",
        "offerho7": "47050",
        "offerho9": "47150",
        "midsumremgubun": "",
        "donsigubun": "1",
        "bidmidsumrem": "0",
        "hotime": "111244",
        "offerho2": "46800",
        "offerho1": "46750",
        "volume": "111022",
        "offerho10": "47200",
        "totofferrem": "4761",
        "totbidrem": "7116",
        "offermidsumrem": "0",
        "offerrem2": "523",
        "bidho5": "46450",
        "offerrem3": "479",
        "bidho4": "46500",
        "offerrem4": "359",
        "bidho7": "46350",
        "offerrem5": "439",
        "bidho6": "46400",
        "bidho9": "46250",
        "bidho8": "46300",
        "offerrem1": "295",
        "offerrem6": "1346",
        "offerrem7": "300",
        "offerrem8": "815",
        "offerrem9": "72",
        "bidrem3": "259",
        "bidrem4": "21",
        "bidrem1": "112",
        "bidrem2": "270",
        "midprice": "46700",
        "bidrem9": "987",
        "bidho1": "46650",
        "bidrem7": "1085",
        "bidrem8": "298",
        "bidho3": "46550",
        "bidrem5": "232",
        "bidho2": "46600",
        "bidrem6": "1023",
        "bidrem10": "2829",
        "bidho10": "46200",
        "shcode": "000880",
        "ex_shcode": "N000880",
        "alloc_gubun": "",
        "midsumrem": "0",
        "offerrem10": "133"
    }
}
```

---

<a id="tr-NS2"></a>
## `NS2` (NXT)우선호가

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerho` | 매도호가 | Number | Y | 8 | - |
| `bidho` | 매수호가 | Number | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImU4Njk4Y2YyLWJiMTEtNGZlMy05OWE5LWIwNGFlOTE3MDJkOSIsIm5iZiI6MTc0MjQyNDQyOCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTA3OTk5LCJpYXQiOjE3NDI0MjQ0MjgsImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.1u2cfXonwmOrWQTvfPwmFvevvexV-NnqjR9u1lRMAb1-6lvddRGQ8CnWWakWWIfvMZ8",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NS2",
  "tr_key": "N000880   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NS2",
        "tr_key": "N000880   "
    },
    "body": {
        "bidho": "46700",
        "shcode": "000880",
        "offerho": "46750",
        "ex_shcode": "N000880"
    }
}
```

---

<a id="tr-NYS"></a>
## `NYS` (NXT)예상체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 110 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `yeprice` | 예상체결가격 | Number | Y | 8 | - |
| `yevolume` | 예상체결수량 | Number | Y | 12 | - |
| `jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `jnilchange` | 예상체결가전일종가대비 | Number | Y | 8 | - |
| `jnilydrate` | 예상체결가전일종가등락율 | Number | Y | 6.2 | - |
| `yofferho0` | 예상매도호가 | Number | Y | 8 | - |
| `ybidho0` | 예상매수호가 | Number | Y | 8 | - |
| `yofferrem0` | 예상매도호가수량 | Number | Y | 12 | - |
| `ybidrem0` | 예상매수호가수량 | Number | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


---

<a id="tr-NVI"></a>
## `NVI` (NXT)VI 발동 해제

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 'N' + 단축코드 6자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `vi_gubun` | 구분 | String | Y | 1 | 0:해제1:정적발동2:동적발동3:정적&동적 |
| `svi_recprice` | 정적VI발동기준가격 | Number | Y | 8 | - |
| `dvi_recprice` | 동적VI발동기준가격 | Number | Y | 8 | - |
| `vi_trgprice` | VI발동가격 | Number | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `ref_shcode` | 참조코드(미사용) | String | Y | 6 | - |
| `time` | 시간 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImU4Njk4Y2YyLWJiMTEtNGZlMy05OWE5LWIwNGFlOTE3MDJkOSIsIm5iZiI6MTc0MjQyNDQyOCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTA3OTk5LCJpYXQiOjE3NDI0MjQ0MjgsImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.1u2cfXonwmOrWQTvfPwmFvevvexV-NnqjR9u1lRMAb1-6lvddRGQ8CnWWak",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NVI",
  "tr_key": "0000000000"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NVI",
        "tr_key": "0000000000"
    },
    "body": {
        "svi_recprice": "0",
        "vi_gubun": "0",
        "shcode": "000000000",
        "time": "K0257",
        "vi_trgprice": "0",
        "exchname": "NXT",
        "ex_shcode": "N115450",
        "dvi_recprice": "0",
        "ref_shcode": "115450"
    }
}
```

---

<a id="tr-NK1"></a>
## `NK1` (NXT)거래원

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerno1` | 매도증권사코드1 | String | Y | 3 | - |
| `bidno1` | 매수증권사코드1 | String | Y | 3 | - |
| `offertrad1` | 매도회원사명1 | String | Y | 6 | - |
| `bidtrad1` | 매수회원사명1 | String | Y | 6 | - |
| `tradmdvol1` | 매도거래량1 | Number | Y | 10 | - |
| `tradmsvol1` | 매수거래량1 | Number | Y | 10 | - |
| `tradmdrate1` | 매도거래량비중1 | Number | Y | 6.2 | - |
| `tradmsrate1` | 매도거래량비중1 | Number | Y | 6.2 | - |
| `tradmdcha1` | 매도거래량직전대비1 | Number | Y | 10 | - |
| `tradmscha1` | 매수거래량직전대비1 | Number | Y | 10 | - |
| `offerno2` | 매도증권사코드2 | String | Y | 3 | - |
| `bidno2` | 매수증권사코드2 | String | Y | 3 | - |
| `offertrad2` | 매도회원사명2 | String | Y | 6 | - |
| `bidtrad2` | 매수회원사명2 | String | Y | 6 | - |
| `tradmdvol2` | 매도거래량2 | Number | Y | 10 | - |
| `tradmsvol2` | 매수거래량2 | Number | Y | 10 | - |
| `tradmdrate2` | 매도거래량비중2 | Number | Y | 6.2 | - |
| `tradmsrate2` | 매수거래량비중2 | Number | Y | 6.2 | - |
| `tradmdcha2` | 매도거래량직전대비2 | Number | Y | 10 | - |
| `tradmscha2` | 매수거래량직전대비2 | Number | Y | 10 | - |
| `offerno3` | 매도증권사코드3 | String | Y | 3 | - |
| `bidno3` | 매수증권사코드3 | String | Y | 3 | - |
| `offertrad3` | 매도회원사명3 | String | Y | 6 | - |
| `bidtrad3` | 매수회원사명3 | String | Y | 6 | - |
| `tradmdvol3` | 매도거래량3 | Number | Y | 10 | - |
| `tradmsvol3` | 매수거래량3 | Number | Y | 10 | - |
| `tradmdrate3` | 매도거래량비중3 | Number | Y | 6.2 | - |
| `tradmsrate3` | 매수거래량비중3 | Number | Y | 6.2 | - |
| `tradmdcha3` | 매도거래량직전대비3 | Number | Y | 10 | - |
| `tradmscha3` | 매수거래량직전대비3 | Number | Y | 10 | - |
| `offerno4` | 매도증권사코드4 | String | Y | 3 | - |
| `bidno4` | 매수증권사코드4 | String | Y | 3 | - |
| `offertrad4` | 매도회원사명4 | String | Y | 6 | - |
| `bidtrad4` | 매수회원사명4 | String | Y | 6 | - |
| `tradmdvol4` | 매도거래량4 | Number | Y | 10 | - |
| `tradmsvol4` | 매수거래량4 | Number | Y | 10 | - |
| `tradmdrate4` | 매도거래량비중4 | Number | Y | 6.2 | - |
| `tradmsrate4` | 매수거래량비중4 | Number | Y | 6.2 | - |
| `tradmdcha4` | 매도거래량직전대비4 | Number | Y | 10 | - |
| `tradmscha4` | 매수거래량직전대비4 | Number | Y | 10 | - |
| `offerno5` | 매도증권사코드5 | String | Y | 3 | - |
| `bidno5` | 매수증권사코드5 | String | Y | 3 | - |
| `offertrad5` | 매도회원사명5 | String | Y | 6 | - |
| `bidtrad5` | 매수회원사명5 | String | Y | 6 | - |
| `tradmdvol5` | 매도거래량5 | Number | Y | 10 | - |
| `tradmsvol5` | 매수거래량5 | Number | Y | 10 | - |
| `tradmdrate5` | 매도거래량비중5 | Number | Y | 6.2 | - |
| `tradmsrate5` | 매수거래량비중5 | Number | Y | 6.2 | - |
| `tradmdcha5` | 매도거래량직전대비5 | Number | Y | 10 | - |
| `tradmscha5` | 매수거래량직전대비5 | Number | Y | 10 | - |
| `ftradmdvol` | 외국계증권사매도합계 | Number | Y | 10 | - |
| `ftradmsvol` | 외국계증권사매수합계 | Number | Y | 10 | - |
| `ftradmdrate` | 외국계증권사매도거래량비중 | Number | Y | 6.2 | - |
| `ftradmsrate` | 외국계증권사매수거래량비중 | Number | Y | 6.2 | - |
| `ftradmdcha` | 외국계증권사매도거래량직전대비 | Number | Y | 10 | - |
| `ftradmscha` | 외국계증권사매수거래량직전대비 | Number | Y | 10 | - |
| `shcode` | 단축코드 | Number | Y | 9 | - |
| `tradmdval1` | 매도거래대금1 | Number | Y | 15 | - |
| `tradmsval1` | 매수거래대금1 | Number | Y | 15 | - |
| `tradmdavg1` | 매도평균단가1 | Number | Y | 7 | - |
| `tradmsavg1` | 매수평균단가1 | Number | Y | 7 | - |
| `tradmdval2` | 매도거래대금2 | Number | Y | 15 | - |
| `tradmsval2` | 매수거래대금2 | Number | Y | 15 | - |
| `tradmdavg2` | 매도평균단가2 | Number | Y | 7 | - |
| `tradmsavg2` | 매수평균단가2 | Number | Y | 7 | - |
| `tradmdval3` | 매도거래대금3 | Number | Y | 15 | - |
| `tradmsval3` | 매수거래대금3 | Number | Y | 15 | - |
| `tradmdavg3` | 매도평균단가3 | Number | Y | 7 | - |
| `tradmsavg3` | 매수평균단가3 | Number | Y | 7 | - |
| `tradmdval4` | 매도거래대금4 | Number | Y | 15 | - |
| `tradmsval4` | 매수거래대금4 | Number | Y | 15 | - |
| `tradmdavg4` | 매도평균단가4 | Number | Y | 7 | - |
| `tradmsavg4` | 매수평균단가4 | Number | Y | 7 | - |
| `tradmdval5` | 매도거래대금5 | Number | Y | 15 | - |
| `tradmsval5` | 매수거래대금5 | Number | Y | 15 | - |
| `tradmdavg5` | 매도평균단가5 | Number | Y | 7 | - |
| `tradmsavg5` | 매수평균단가5 | Number | Y | 7 | - |
| `ftradmdval` | 외국계증권사매도거래대금 | Number | Y | 15 | - |
| `ftradmsval` | 외국계증권사매수거래대금 | Number | Y | 15 | - |
| `ftradmdavg` | 외국계증권사매도평균단가 | Number | Y | 7 | - |
| `ftradmsavg` | 외국계증권사매수평균단가 | Number | Y | 7 | - |
| `time` | 수신시간 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjYyY2NhNzgwLWZjN2EtNDcwZC04NjQ4LTMyOWQzZjFiMmE2NyIsIm5iZiI6MTc0MjQyOTY1MiwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTA4MDAwLCJpYXQiOjE3NDI0Mjk2NTIsImp0aSI6IlBTQ2lXTjBDZGZUYVZYb293Tnltb2dkdmxJaUxHV25UcGQzRCJ9.GJBiwx09tuREqY3AN0zSphhBTBMIC0X6l-TyETIFwoaxllhChr6IDqSVAdgB61y4ufh-J8zGBcu",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NK1",
  "tr_key": "N009520   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NK1",
        "tr_key": "N009520   "
    },
    "body": {
        "tradmdrate1": "39.69",
        "tradmdvol5": "15626",
        "tradmdvol3": "20687",
        "tradmdrate3": "11.55",
        "tradmdrate2": "13.37",
        "tradmdvol4": "16238",
        "offerno2": "005",
        "tradmdrate5": "8.72",
        "offerno1": "050",
        "tradmdrate4": "9.07",
        "offerno4": "017",
        "offerno3": "012",
        "bidtrad4": "NH투자",
        "offerno5": "030",
        "bidtrad5": "KB증권",
        "bidtrad2": "미래에",
        "bidtrad3": "삼성증",
        "tradmdvol1": "71083",
        "bidtrad1": "키움증",
        "tradmdvol2": "23938",
        "tradmdval3": "308",
        "offertrad5": "삼성증",
        "tradmdval4": "242",
        "tradmdval1": "1057",
        "tradmdval2": "357",
        "tradmdval5": "233",
        "tradmscha2": "188",
        "ftradmdval": "0",
        "tradmscha1": "666",
        "tradmscha4": "151",
        "tradmscha3": "42",
        "offertrad2": "미래에",
        "offertrad1": "키움증",
        "offertrad4": "KB증권",
        "offertrad3": "NH투자",
        "tradmdcha5": "0",
        "tradmdcha4": "0",
        "tradmsavg1": "14883",
        "tradmsavg2": "14872",
        "tradmscha5": "61",
        "tradmdavg1": "14875",
        "tradmdavg3": "14870",
        "tradmdavg2": "14901",
        "tradmdavg5": "14887",
        "tradmdavg4": "14900",
        "tradmsavg3": "14907",
        "ftradmscha": "0000000000",
        "tradmsavg4": "14888",
        "ftradmdvol": "0000000000",
        "tradmsavg5": "14866",
        "ftradmdavg": " ",
        "tradmsval3": "265",
        "tradmsval2": "401",
        "tradmsval5": "153",
        "ftradmsval": "0",
        "tradmsval4": "178",
        "tradmsval1": "1254",
        "tradmdcha1": "1159",
        "tradmdcha3": "0",
        "tradmdcha2": "0",
        "bidno1": "050",
        "bidno3": "030",
        "tradmsvol5": "10298",
        "bidno2": "005",
        "tradmsvol4": "11960",
        "bidno5": "017",
        "bidno4": "012",
        "tradmsvol1": "84288",
        "tradmsvol3": "17796",
        "tradmsvol2": "26993",
        "tradmsrate2": "15.07",
        "tradmsrate1": "47.06",
        "tradmsrate4": "6.68",
        "tradmsrate3": "9.94",
        "tradmsrate5": "5.75",
        "ftradmsvol": "0000000000",
        "ftradmdcha": "0000000000",
        "ftradmsrate": "0.0",
        "shcode": "009520",
        "ftradmsavg": " ",
        "ftradmdrate": "0.0",
        "ex_shcode": "N009520",
        "time": "132610",
        "exchname": "NXT"
    }
}
```

---

<a id="tr-NPH"></a>
## `NPH` (NXT)프로그램매매종목별

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | N | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `price` | 현재가 | Number | Y | 8 | - |
| `sign` | 전일대비구분 | Number | Y | 1 | - |
| `change` | 전일대비 | Number | Y | 8 | - |
| `volume` | 누적거래량 | Number | Y | 10 | - |
| `drate` | 등락율 | Number | Y | 6.2 | - |
| `cdhrem` | 차익매도호가잔량 | Number | Y | 12 | - |
| `cshrem` | 차익매수호가잔량 | Number | Y | 12 | - |
| `bdhrem` | 비차익매도호가잔량 | Number | Y | 12 | - |
| `bshrem` | 비차익매수호가잔량 | Number | Y | 12 | - |
| `cdhvolume` | 차익매도호가수량 | Number | Y | 12 | - |
| `cshvolume` | 차익매수호가수량 | Number | Y | 12 | - |
| `bdhvolume` | 비차익매도호가수량 | Number | Y | 12 | - |
| `bshvolume` | 비차익매수호가수량 | Number | Y | 12 | - |
| `dwcvolume` | 전체매도위탁체결수량 | Number | Y | 12 | - |
| `swcvolume` | 전체매수위탁체결수량 | Number | Y | 12 | - |
| `djcvolume` | 전체매도자기체결수량 | Number | Y | 12 | - |
| `sjcvolume` | 전체매수자기체결수량 | Number | Y | 12 | - |
| `tdvolume` | 전체매도체결수량 | Number | Y | 12 | - |
| `tsvolume` | 전체매수체결수량 | Number | Y | 12 | - |
| `tvol` | 전체순매수수량 | Number | Y | 12 | - |
| `dwcvalue` | 전체매도위탁체결금액 | Number | Y | 15 | - |
| `swcvalue` | 전체매수위탁체결금액 | Number | Y | 15 | - |
| `djcvalue` | 전체매도자기체결금액 | Number | Y | 15 | - |
| `sjcvalue` | 전체매수자기체결금액 | Number | Y | 15 | - |
| `tdvalue` | 전체매도체결금액 | Number | Y | 15 | - |
| `tsvalue` | 전체매수체결금액 | Number | Y | 15 | - |
| `tval` | 전체순매수금액 | Number | Y | 15 | - |
| `pdgvolume` | 매도사전공시수량 | Number | Y | 12 | - |
| `psgvolume` | 매수사전공시수량 | Number | Y | 12 | - |
| `shcode` | 종목코드 | Number | Y | 12 | - |
| `ex_shcode` | 거래소별단축코드 | Number | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjYyY2NhNzgwLWZjN2EtNDcwZC04NjQ4LTMyOWQzZjFiMmE2NyIsIm5iZiI6MTc0MjQyOTY1MiwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTA4MDAwLCJpYXQiOjE3NDI0Mjk2NTIsImp0aSI6IlBTQ2lXTjBDZGZUYVZYb293Tnltb2dkdmxJaUxHV25UcGQzRCJ9.GJBiwx09tuREqY3AN0zSphhBTBMIC0X6l-TyETIFwoaxllhChr6IDqSVAdgB61y4ufh-J8zGBcucZuVDfC54Qg",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NPH",
  "tr_key": "N009520   "
 }
}
```

---

<a id="tr-NPM"></a>
## `NPM` (NXT)프로그램매매전체집계

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 2 | 'N' + 구분값<br/>N0:코스피<br/>N1:코스닥 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `cdhrem` | 차익매도호가잔량 | Number | Y | 6 | - |
| `cshrem` | 차익매수호가잔량 | Number | Y | 6 | - |
| `bdhrem` | 비차익매도호가잔량 | Number | Y | 6 | - |
| `bshrem` | 비차익매수호가잔량 | Number | Y | 6 | - |
| `cdhvolume` | 차익매도호가수량 | Number | Y | 6 | - |
| `cshvolume` | 차익매수호가수량 | Number | Y | 6 | - |
| `bdhvolume` | 비차익매도호가수량 | Number | Y | 6 | - |
| `bshvolume` | 비차익매수호가수량 | Number | Y | 6 | - |
| `cdwvolume` | 차익매도위탁체결수량 | Number | Y | 6 | - |
| `cdjvolume` | 차익매도자기체결수량 | Number | Y | 6 | - |
| `cswvolume` | 차익매수위탁체결수량 | Number | Y | 6 | - |
| `csjvolume` | 차익매수자기체결수량 | Number | Y | 6 | - |
| `cwvol` | 차익위탁순매수수량 | Number | Y | 6 | - |
| `cjvol` | 차익자기순매수수량 | Number | Y | 6 | - |
| `bdwvolume` | 비차익매도위탁체결수량 | Number | Y | 6 | - |
| `bdjvolume` | 비차익매도자기체결수량 | Number | Y | 6 | - |
| `bswvolume` | 비차익매수위탁체결수량 | Number | Y | 6 | - |
| `bsjvolume` | 비차익매수자기체결수량 | Number | Y | 6 | - |
| `bwvol` | 비차익위탁순매수수량 | Number | Y | 6 | - |
| `bjvol` | 비차익자기순매수수량 | Number | Y | 6 | - |
| `dwvolume` | 전체매도위탁체결수량 | Number | Y | 6 | - |
| `swvolume` | 전체매수위탁체결수량 | Number | Y | 6 | - |
| `wvol` | 전체위탁순매수수량 | Number | Y | 6 | - |
| `djvolume` | 전체매도자기체결수량 | Number | Y | 6 | - |
| `sjvolume` | 전체매수자기체결수량 | Number | Y | 6 | - |
| `jvol` | 전체자기순매수수량 | Number | Y | 6 | - |
| `cdwvalue` | 차익매도위탁체결금액 | Number | Y | 8 | - |
| `cdjvalue` | 차익매도자기체결금액 | Number | Y | 8 | - |
| `cswvalue` | 차익매수위탁체결금액 | Number | Y | 8 | - |
| `csjvalue` | 차익매수자기체결금액 | Number | Y | 8 | - |
| `cwval` | 차익위탁순매수금액 | Number | Y | 8 | - |
| `cjval` | 차익자기순매수금액 | Number | Y | 8 | - |
| `bdwvalue` | 비차익매도위탁체결금액 | Number | Y | 8 | - |
| `bdjvalue` | 비차익매도자기체결금액 | Number | Y | 8 | - |
| `bswvalue` | 비차익매수위탁체결금액 | Number | Y | 8 | - |
| `bsjvalue` | 비차익매수자기체결금액 | Number | Y | 8 | - |
| `bwval` | 비차익위탁순매수금액 | Number | Y | 8 | - |
| `bjval` | 비차익자기순매수금액 | Number | Y | 8 | - |
| `dwvalue` | 전체매도위탁체결금액 | Number | Y | 8 | - |
| `swvalue` | 전체매수위탁체결금액 | Number | Y | 8 | - |
| `wval` | 전체위탁순매수금액 | Number | Y | 8 | - |
| `djvalue` | 전체매도자기체결금액 | Number | Y | 8 | - |
| `sjvalue` | 전체매수자기체결금액 | Number | Y | 8 | - |
| `jval` | 전체자기순매수금액 | Number | Y | 8 | - |
| `k200jisu` | KOSPI200지수 | Number | Y | 6.2 | - |
| `k200sign` | KOSPI200전일대비구분 | String | Y | 1 | - |
| `change` | KOSPI200전일대비 | Number | Y | 6.2 | - |
| `k200basis` | KOSPI200베이시스 | Number | Y | 4.2 | - |
| `cdvolume` | 차익매도체결수량합계 | Number | Y | 6 | - |
| `csvolume` | 차익매수체결수량합계 | Number | Y | 6 | - |
| `cvol` | 차익순매수수량합계 | Number | Y | 6 | - |
| `bdvolume` | 비차익매도체결수량합계 | Number | Y | 6 | - |
| `bsvolume` | 비차익매수체결수량합계 | Number | Y | 6 | - |
| `bvol` | 비차익순매수수량합계 | Number | Y | 6 | - |
| `tdvolume` | 전체매도체결수량합계 | Number | Y | 6 | - |
| `tsvolume` | 전체매수체결수량합계 | Number | Y | 6 | - |
| `tvol` | 전체순매수수량합계 | Number | Y | 6 | - |
| `cdvalue` | 차익매도체결금액합계 | Number | Y | 8 | - |
| `csvalue` | 차익매수체결금액합계 | Number | Y | 8 | - |
| `cval` | 차익순매수금액합계 | Number | Y | 8 | - |
| `bdvalue` | 비차익매도체결금액합계 | Number | Y | 8 | - |
| `bsvalue` | 비차익매수체결금액합계 | Number | Y | 8 | - |
| `bval` | 비차익순매수금액합계 | Number | Y | 8 | - |
| `tdvalue` | 전체매도체결금액합계 | Number | Y | 8 | - |
| `tsvalue` | 전체매수체결금액합계 | Number | Y | 8 | - |
| `tval` | 전체순매수금액합계 | Number | Y | 8 | - |
| `p_cdvolcha` | 차익매도체결수량직전대비 | Number | Y | 6 | - |
| `p_csvolcha` | 차익매수체결수량직전대비 | Number | Y | 6 | - |
| `p_cvolcha` | 차익순매수수량직전대비 | Number | Y | 6 | - |
| `p_bdvolcha` | 비차익매도체결수량직전대비 | Number | Y | 6 | - |
| `p_bsvolcha` | 비차익매수체결수량직전대비 | Number | Y | 6 | - |
| `p_bvolcha` | 비차익순매수수량직전대비 | Number | Y | 6 | - |
| `p_tdvolcha` | 전체매도체결수량직전대비 | Number | Y | 6 | - |
| `p_tsvolcha` | 전체매수체결수량직전대비 | Number | Y | 6 | - |
| `p_tvolcha` | 전체순매수수량직전대비 | Number | Y | 6 | - |
| `p_cdvalcha` | 차익매도체결금액직전대비 | Number | Y | 8 | - |
| `p_csvalcha` | 차익매수체결금액직전대비 | Number | Y | 8 | - |
| `p_cvalcha` | 차익순매수금액직전대비 | Number | Y | 8 | - |
| `p_bdvalcha` | 비차익매도체결금액직전대비 | Number | Y | 8 | - |
| `p_bsvalcha` | 비차익매수체결금액직전대비 | Number | Y | 8 | - |
| `p_bvalcha` | 비차익순매수금액직전대비 | Number | Y | 8 | - |
| `p_tdvalcha` | 전체매도체결금액직전대비 | Number | Y | 8 | - |
| `p_tsvalcha` | 전체매수체결금액직전대비 | Number | Y | 8 | - |
| `p_tvalcha` | 전체순매수금액직전대비 | Number | Y | 8 | - |
| `gubun` | 구분값 | String | Y | 1 | - |
| `ex_gubun` | 거래소별구분값 | String | Y | 2 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sqh",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NPM",
  "tr_key": "N0"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NPM",
        "tr_key": "N0"
    },
    "body": {
        "sjvalue": "0",
        "ex_gubun": "N0",
        "p_bdvalcha": "0",
        "p_cdvalcha": "0",
        "cwval": "0",
        "csjvolume": "0",
        "k200basis": "-0.13",
        "p_cvolcha": "0",
        "bdvolume": "2",
        "dwvalue": "108",
        "cdvolume": "0",
        "bdwvolume": "2",
        "sjvolume": "0",
        "jvol": "0",
        "bdhrem": "0",
        "tval": "-51",
        "k200jisu": "355.08",
        "bdvalue": "108",
        "bshvolume": "2",
        "bjvol": "0",
        "cdhvolume": "0",
        "bvol": "-1",
        "csvolume": "0",
        "swvalue": "57",
        "bdjvolume": "0",
        "tdvalue": "108",
        "tdvolume": "2",
        "cjvol": "0",
        "swvolume": "1",
        "cswvolume": "0",
        "gubun": "0",
        "bwval": "-51",
        "p_bvolcha": "0",
        "p_tsvolcha": "0",
        "cdhrem": "0",
        "bswvalue": "57",
        "csjvalue": "0",
        "p_bsvolcha": "0",
        "p_tvalcha": "0",
        "bdjvalue": "0",
        "cdwvalue": "0",
        "cvol": "0",
        "p_cvalcha": "0",
        "bwvol": "-1",
        "bshrem": "1",
        "cshvolume": "0",
        "bdwvalue": "108",
        "jval": "0",
        "tsvolume": "1",
        "dwvolume": "2",
        "p_bdvolcha": "0",
        "bsjvolume": "0",
        "wvol": "-1",
        "cdwvolume": "0",
        "bsvalue": "57",
        "p_cdvolcha": "0",
        "bjval": "0",
        "p_bsvalcha": "0",
        "bval": "-51",
        "djvolume": "0",
        "djvalue": "0",
        "cshrem": "0",
        "p_csvalcha": "0",
        "p_tdvalcha": "0",
        "bdhvolume": "2",
        "p_tdvolcha": "0",
        "bsvolume": "1",
        "p_bvalcha": "0",
        "change": "1.58",
        "cdjvolume": "0",
        "tvol": "-1",
        "p_tsvalcha": "0",
        "bswvolume": "1",
        "cdvalue": "0",
        "tsvalue": "57",
        "cval": "0",
        "csvalue": "0",
        "p_tvolcha": "0",
        "cswvalue": "0",
        "cwvol": "0",
        "bsjvalue": "0",
        "cdjvalue": "0",
        "p_csvolcha": "0",
        "time": "134238",
        "k200sign": "2",
        "wval": "-51",
        "cjval": "0"
    }
}
```

---

<a id="tr-NBT"></a>
## `NBT` (NXT)시간대별투자자매매추이

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 4 | N + 업종코드 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tjjtime` | 수신시간 | String | Y | 8 | - |
| `tjjcode1` | 투자자코드1(개인) | String | Y | 4 | - |
| `msvolume1` | 매수거래량1 | Number | Y | 8 | - |
| `mdvolume1` | 매도거래량1 | Number | Y | 8 | - |
| `msvol1` | 거래량순매수1 | Number | Y | 8 | - |
| `msvalue1` | 매수거래대금1 | Number | Y | 6 | - |
| `mdvalue1` | 매도거래대금1 | Number | Y | 6 | - |
| `msval1` | 거래대금순매수1 | Number | Y | 6 | - |
| `tjjcode2` | 투자자코드2(외국인) | String | Y | - | - |
| `msvolume2` | 매수거래량2 | Number | Y | 8 | - |
| `mdvolume2` | 매도거래량2 | Number | Y | 8 | - |
| `msvol2` | 거래량순매수2 | Number | Y | 8 | - |
| `msvalue2` | 매수거래대금2 | Number | Y | 6 | - |
| `mdvalue2` | 매도거래대금2 | Number | Y | 6 | - |
| `msval2` | 거래대금순매수2 | Number | Y | 6 | - |
| `tjjcode3` | 투자자코드3(기관계) | String | Y | 4 | - |
| `msvolume3` | 매수거래량3 | Number | Y | 8 | - |
| `mdvolume3` | 매도거래량3 | Number | Y | 8 | - |
| `msvol3` | 거래량순매수3 | Number | Y | 8 | - |
| `msvalue3` | 매수거래대금3 | Number | Y | 6 | - |
| `mdvalue3` | 매도거래대금3 | Number | Y | 6 | - |
| `msval3` | 거래대금순매수3 | Number | Y | 6 | - |
| `tjjcode4` | 투자자코드4(증권) | String | Y | 4 | - |
| `msvolume4` | 매수거래량4 | Number | Y | 8 | - |
| `mdvolume4` | 매도거래량4 | Number | Y | 8 | - |
| `msvol4` | 거래량순매수4 | Number | Y | 8 | - |
| `msvalue4` | 매수거래대금4 | Number | Y | 6 | - |
| `mdvalue4` | 매도거래대금4 | Number | Y | 6 | - |
| `msval4` | 거래대금순매수4 | Number | Y | 6 | - |
| `tjjcode5` | 투자자코드5(투신) | String | Y | 4 | - |
| `msvolume5` | 매수거래량5 | Number | Y | 8 | - |
| `mdvolume5` | 매도거래량5 | Number | Y | 8 | - |
| `msvol5` | 거래량순매수5 | Number | Y | 8 | - |
| `msvalue5` | 매수거래대금5 | Number | Y | 6 | - |
| `mdvalue5` | 매도거래대금5 | Number | Y | 6 | - |
| `msval5` | 거래대금순매수5 | Number | Y | 6 | - |
| `tjjcode6` | 투자자코드6(은행) | String | Y | 4 | - |
| `msvolume6` | 매수거래량6 | Number | Y | 8 | - |
| `mdvolume6` | 매도거래량6 | Number | Y | 8 | - |
| `msvol6` | 거래량순매수6 | Number | Y | 8 | - |
| `msvalue6` | 매수거래대금6 | Number | Y | 6 | - |
| `mdvalue6` | 매도거래대금6 | Number | Y | 6 | - |
| `msval6` | 거래대금순매수6 | Number | Y | 6 | - |
| `tjjcode7` | 투자자코드7(보험) | String | Y | 4 | - |
| `msvolume7` | 매수거래량7 | Number | Y | 8 | - |
| `mdvolume7` | 매도거래량7 | Number | Y | 8 | - |
| `msvol7` | 거래량순매수7 | Number | Y | 8 | - |
| `msvalue7` | 매수거래대금7 | Number | Y | 6 | - |
| `mdvalue7` | 매도거래대금7 | Number | Y | 6 | - |
| `msval7` | 거래대금순매수7 | Number | Y | 6 | - |
| `tjjcode8` | 투자자코드8(종금) | String | Y | 4 | - |
| `msvolume8` | 매수거래량8 | Number | Y | 8 | - |
| `mdvolume8` | 매도거래량8 | Number | Y | 8 | - |
| `msvol8` | 거래량순매수8 | Number | Y | 8 | - |
| `msvalue8` | 매수거래대금8 | Number | Y | 6 | - |
| `mdvalue8` | 매도거래대금8 | Number | Y | 6 | - |
| `msval8` | 거래대금순매수8 | Number | Y | 6 | - |
| `tjjcode9` | 투자자코드9(기금) | Number | Y | 4 | - |
| `msvolume9` | 매수거래량9 | Number | Y | 8 | - |
| `mdvolume9` | 매도거래량9 | Number | Y | 8 | - |
| `msvol9` | 거래량순매수9 | Number | Y | 8 | - |
| `msvalue9` | 매수거래대금9 | Number | Y | 6 | - |
| `mdvalue9` | 매도거래대금9 | Number | Y | 6 | - |
| `msval9` | 거래대금순매수9 | Number | Y | 6 | - |
| `tjjcode10` | 투자자코드10(선물업자) | String | Y | 4 | - |
| `msvolume10` | 매수거래량10 | Number | Y | 8 | - |
| `mdvolume10` | 매도거래량10 | Number | Y | 8 | - |
| `msvol10` | 거래량순매수10 | Number | Y | 8 | - |
| `msvalue10` | 매수거래대금10 | Number | Y | 8 | - |
| `mdvalue10` | 매도거래대금10 | Number | Y | 6 | - |
| `msval10` | 거래대금순매수10 | Number | Y | 6 | - |
| `tjjcode11` | 투자자코드11(기타) | String | Y | 4 | - |
| `msvolume11` | 매수거래량11 | Number | Y | 8 | - |
| `mdvolume11` | 매도거래량11 | Number | Y | 8 | - |
| `msvol11` | 거래량순매수11 | Number | Y | 8 | - |
| `msvalue11` | 매수거래대금11 | Number | Y | 6 | - |
| `mdvalue11` | 매도거래대금11 | Number | Y | 6 | - |
| `msval11` | 거래대금순매수11 | Number | Y | 6 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |
| `tjjcode0` | 투자자코드0(사모펀드) | String | Y | 4 | - |
| `msvolume0` | 매수거래량0 | Number | Y | 8 | - |
| `mdvolume0` | 매도거래량0 | Number | Y | 8 | - |
| `msvol0` | 거래량순매수0 | Number | Y | 8 | - |
| `msvalue0` | 매수거래대금0 | Number | Y | 6 | - |
| `mdvalue0` | 매도거래대금0 | Number | Y | 6 | - |
| `msval0` | 거래대금순매수0 | Number | Y | 6 | - |
| `ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sq",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NBT",
  "tr_key": "N003"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NBT",
        "tr_key": "N003"
    },
    "body": {
        "mdvalue0": "0",
        "mdvalue1": "425",
        "msvolume8": "0",
        "msvolume9": "0",
        "msvolume4": "0",
        "mdvalue6": "0",
        "msvolume5": "0",
        "mdvalue7": "0",
        "msvolume6": "0",
        "mdvalue8": "0",
        "msvolume7": "0",
        "mdvalue9": "0",
        "mdvalue2": "2",
        "msvolume0": "0",
        "msvolume1": "948",
        "mdvalue3": "0",
        "msvolume2": "2",
        "mdvalue4": "0",
        "msvolume3": "0",
        "mdvalue5": "0",
        "mdvolume0": "0",
        "mdvolume9": "0",
        "mdvolume3": "0",
        "mdvolume4": "0",
        "mdvolume1": "957",
        "mdvolume2": "5",
        "mdvolume7": "0",
        "mdvolume8": "0",
        "mdvolume5": "0",
        "mdvolume6": "0",
        "msvalue1": "422",
        "msvalue2": "1",
        "msvalue0": "0",
        "msvalue5": "0",
        "msvalue6": "0",
        "msvalue3": "0",
        "msvol11": "12",
        "msvalue4": "0",
        "msvol10": "0",
        "msvalue9": "0",
        "mdvalue11": "2",
        "msvalue7": "0",
        "msvalue8": "0",
        "mdvalue10": "0",
        "tjjtime": "14060001",
        "tjjcode0": "0000",
        "tjjcode10": "0011",
        "msvolume10": "0",
        "tjjcode11": "0007",
        "tjjcode6": "0004",
        "msval6": "0",
        "tjjcode5": "0003",
        "msval5": "0",
        "msval4": "0",
        "tjjcode8": "0005",
        "msval3": "0",
        "tjjcode7": "0002",
        "tjjcode2": "0017",
        "tjjcode1": "0008",
        "msval9": "0",
        "tjjcode4": "0001",
        "msval8": "0",
        "tjjcode3": "0018",
        "msval7": "0",
        "msval2": "-1",
        "msval1": "-3",
        "tjjcode9": "0006",
        "mdvolume10": "0",
        "msval0": "0",
        "mdvolume11": "4",
        "msvol9": "0",
        "msvol5": "0",
        "msvol6": "0",
        "msvol7": "0",
        "msvol8": "0",
        "msvol1": "-9",
        "ex_upcode": "N003",
        "msvol2": "-3",
        "msvol3": "0",
        "msval11": "4",
        "msvol4": "0",
        "msval10": "0",
        "msvol0": "0",
        "msvolume11": "15",
        "msvalue10": "0",
        "msvalue11": "5",
        "upcode": "003"
    }
}
```

---

<a id="tr-NBM"></a>
## `NBM` (NXT)업종별투자자별매매현황

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 4 | N + 업종코드 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tjjcode` | 투자자코드 | String | Y | 4 | - |
| `tjjtime` | 수신시간 | String | Y | 8 | - |
| `msvolume` | 매수거래량 | Number | Y | 8 | - |
| `mdvolume` | 매도거래량 | Number | Y | 8 | - |
| `msvol` | 거래량순매수 | Number | Y | 8 | - |
| `p_msvol` | 거래량순매수직전대비 | Number | Y | 8 | - |
| `msvalue` | 매수거래대금 | Number | Y | 6 | - |
| `매도거래대금` | 매도거래대금 | Number | Y | 6 | - |
| `msval` | 거래대금순매수 | Number | Y | 6 | - |
| `p_msval` | 거래대금순매수직전대비 | Number | Y | 6 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |
| `ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sqhk7Z-rHXpvNiyMbdtOS4-E3hQ",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "NBM",
  "tr_key": "N003"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "NBM",
        "tr_key": "N003"
    },
    "body": {
        "p_msval": "0",
        "tjjtime": "15030000",
        "p_msvol": "0",
        "mdvalue": "487",
        "msvolume": "1123",
        "upcode": "003",
        "ex_upcode": "N003",
        "tjjcode": "9999",
        "msvalue": "487",
        "mdvolume": "1127",
        "msvol": "-3",
        "msval": "-1"
    }
}
```

---

<a id="tr-US3"></a>
## `US3` (통합)체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `chetime` | 체결시간 | String | Y | 6 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | Number | Y | 8 | - |
| `drate` | 등락율 | Number | Y | 6.2 | - |
| `price` | 현재가 | Number | Y | 8 | - |
| `opentime` | 시가시간 | Number | Y | 6 | - |
| `open` | 시가 | Number | Y | 8 | - |
| `hightime` | 고가시간 | String | Y | 6 | - |
| `high` | 고가 | Number | Y | 8 | - |
| `lowtime` | 저가시간 | String | Y | 6 | - |
| `low` | 저가 | Number | Y | 8 | - |
| `cgubun` | 체결구분 | String | Y | 1 | + : 매수<br/>- : 매도 |
| `cvolume` | 체결량 | Number | Y | 8 | - |
| `volume` | 누적거래량 | Number | Y | 12 | - |
| `value` | 누적거래대금 | Number | Y | 12 | - |
| `mdvolume` | 매도누적체결량 | Number | Y | 12 | - |
| `mdchecnt` | 매도누적체결건수 | Number | Y | 8 | - |
| `msvolume` | 매수누적체결량 | Number | Y | 12 | - |
| `mschecnt` | 매수누적체결건수 | Number | Y | 8 | - |
| `cpower` | 체결강도 | Number | Y | 9.2 | - |
| `w_avrg` | 가중평균가 | Number | Y | 8 | - |
| `offerho` | 매도호가 | Number | Y | 8 | - |
| `bidho` | 매수호가 | Number | Y | 8 | - |
| `status` | 장정보 | String | Y | 2 | - |
| `jnilvolume` | 전일동시간대거래량 | Number | Y | 12 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `exchname` | 거래소명 | String | Y | 3 | KRX, NXT |
| `ex_shcode` | 거래소별단축코드 | Number | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "접근토큰",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "US3",
  "tr_key": "U005930   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "US3",
        "tr_key": "U005930   "
    },
    "body": {
        "mdchecnt": "42958",
        "sign": "2",
        "mschecnt": "63407",
        "mdvolume": "7156641",
        "w_avrg": "56184",
        "cpower": "107.51",
        "offerho": "56200",
        "cvolume": "40",
        "high": "56700",
        "bidho": "56100",
        "low": "55500",
        "price": "56100",
        "cgubun": "-",
        "value": "926807",
        "change": "900",
        "shcode": "005930",
        "chetime": "162202",
        "ex_shcode": "U005930",
        "opentime": "080000",
        "lowtime": "080000",
        "volume": "16495969",
        "drate": "1.63",
        "hightime": "080000",
        "jnilvolume": "16817478",
        "msvolume": "7694447",
        "exchname": "NXT",
        "open": "55500",
        "status": "00"
    }
}
```

---

<a id="tr-UH1"></a>
## `UH1` (통합)호가잔량

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | Number | Y | 7 | - |
| `bidho1` | 매수호가1 | Number | Y | 7 | - |
| `krx_offerrem1` | KRX매도호가잔량1 | Number | Y | 9 | - |
| `nxt_offerrem1` | NXT매도호가잔량1 | Number | Y | 9 | - |
| `unt_offerrem1` | 통합매도호가잔량1 | Number | Y | 9 | - |
| `krx_bidrem1` | KRX매수호가잔량1 | Number | Y | 9 | - |
| `nxt_bidrem1` | NXT매수호가잔량1 | Number | Y | 9 | - |
| `unt_bidrem1` | 통합매수호가잔량1 | Number | Y | 9 | - |
| `offerho2` | 매도호가2 | Number | Y | 7 | - |
| `bidho2` | 매수호가2 | Number | Y | 7 | - |
| `krx_offerrem2` | KRX매도호가잔량2 | Number | Y | 9 | - |
| `nxt_offerrem2` | NXT매도호가잔량2 | Number | Y | 9 | - |
| `unt_offerrem2` | 통합매도호가잔량2 | Number | Y | 9 | - |
| `krx_bidrem2` | KRX매수호가잔량2 | Number | Y | 9 | - |
| `nxt_bidrem2` | NXT매수호가잔량2 | Number | Y | 9 | - |
| `unt_bidrem2` | 통합매수호가잔량2 | Number | Y | 9 | - |
| `offerho3` | 매도호가3 | Number | Y | 7 | - |
| `bidho3` | 매수호가3 | Number | Y | 7 | - |
| `krx_offerrem3` | KRX매도호가잔량3 | Number | Y | 9 | - |
| `nxt_offerrem3` | NXT매도호가잔량3 | Number | Y | 9 | - |
| `unt_offerrem3` | 통합매도호가잔량3 | Number | Y | 9 | - |
| `krx_bidrem3` | KRX매수호가잔량3 | Number | Y | 9 | - |
| `nxt_bidrem3` | NXT매수호가잔량3 | Number | Y | 9 | - |
| `unt_bidrem3` | 통합매수호가잔량3 | Number | Y | 9 | - |
| `offerho4` | 매도호가4 | Number | Y | 7 | - |
| `bidho4` | 매수호가4 | Number | Y | 7 | - |
| `krx_offerrem4` | KRX매도호가잔량4 | Number | Y | 9 | - |
| `nxt_offerrem4` | NXT매도호가잔량4 | Number | Y | 9 | - |
| `unt_offerrem4` | 통합매도호가잔량4 | Number | Y | 9 | - |
| `krx_bidrem4` | KRX매수호가잔량4 | Number | Y | 9 | - |
| `nxt_bidrem4` | NXT매수호가잔량4 | Number | Y | 9 | - |
| `unt_bidrem4` | 통합매수호가잔량4 | Number | Y | 9 | - |
| `offerho5` | 매도호가5 | Number | Y | 7 | - |
| `bidho5` | 매수호가5 | Number | Y | 7 | - |
| `krx_offerrem5` | KRX매도호가잔량5 | Number | Y | 9 | - |
| `nxt_offerrem5` | NXT매도호가잔량5 | Number | Y | 9 | - |
| `unt_offerrem5` | 통합매도호가잔량5 | Number | Y | 9 | - |
| `krx_bidrem5` | KRX매수호가잔량5 | Number | Y | 9 | - |
| `nxt_bidrem5` | NXT매수호가잔량5 | Number | Y | 9 | - |
| `unt_bidrem5` | 통합매수호가잔량5 | Number | Y | 9 | - |
| `offerho6` | 매도호가6 | Number | Y | 7 | - |
| `bidho6` | 매수호가6 | Number | Y | 7 | - |
| `krx_offerrem6` | KRX매도호가잔량6 | Number | Y | 9 | - |
| `nxt_offerrem6` | NXT매도호가잔량6 | Number | Y | 9 | - |
| `unt_offerrem6` | 통합매도호가잔량6 | Number | Y | 9 | - |
| `krx_bidrem6` | KRX매수호가잔량6 | Number | Y | 9 | - |
| `nxt_bidrem6` | NXT매수호가잔량6 | Number | Y | 9 | - |
| `unt_bidrem6` | 통합매수호가잔량6 | Number | Y | 9 | - |
| `offerho7` | 매도호가7 | Number | Y | 7 | - |
| `bidho7` | 매수호가7 | Number | Y | 7 | - |
| `krx_offerrem7` | KRX매도호가잔량7 | Number | Y | 9 | - |
| `nxt_offerrem7` | NXT매도호가잔량7 | Number | Y | 9 | - |
| `unt_offerrem7` | 통합매도호가잔량7 | Number | Y | 9 | - |
| `krx_bidrem7` | KRX매수호가잔량7 | Number | Y | 9 | - |
| `nxt_bidrem7` | NXT매수호가잔량7 | Number | Y | 9 | - |
| `unt_bidrem7` | 통합매수호가잔량7 | Number | Y | 9 | - |
| `offerho8` | 매도호가8 | Number | Y | 7 | - |
| `bidho8` | 매수호가8 | Number | Y | 7 | - |
| `krx_offerrem8` | KRX매도호가잔량8 | Number | Y | 9 | - |
| `nxt_offerrem8` | NXT매도호가잔량8 | Number | Y | 9 | - |
| `unt_offerrem8` | 통합매도호가잔량8 | Number | Y | 9 | - |
| `krx_bidrem8` | KRX매수호가잔량8 | Number | Y | 9 | - |
| `nxt_bidrem8` | NXT매수호가잔량8 | Number | Y | 9 | - |
| `unt_bidrem8` | 통합매수호가잔량8 | Number | Y | 9 | - |
| `offerho9` | 매도호가9 | Number | Y | 7 | - |
| `bidho9` | 매수호가9 | Number | Y | 7 | - |
| `krx_offerrem9` | KRX매도호가잔량9 | Number | Y | 9 | - |
| `nxt_offerrem9` | NXT매도호가잔량9 | Number | Y | 9 | - |
| `unt_offerrem9` | 통합매도호가잔량9 | Number | Y | 9 | - |
| `krx_bidrem9` | KRX매수호가잔량9 | Number | Y | 9 | - |
| `nxt_bidrem9` | NXT매수호가잔량9 | Number | Y | 9 | - |
| `unt_bidrem9` | 통합매수호가잔량9 | Number | Y | 9 | - |
| `offerho10` | 매도호가10 | Number | Y | 7 | - |
| `bidho10` | 매수호가10 | Number | Y | 7 | - |
| `krx_offerrem10` | KRX매도호가잔량10 | Number | Y | 9 | - |
| `nxt_offerrem10` | NXT매도호가잔량10 | Number | Y | 9 | - |
| `unt_offerrem10` | 통합매도호가잔량10 | Number | Y | 9 | - |
| `krx_bidrem10` | KRX매수호가잔량10 | Number | Y | 9 | - |
| `nxt_bidrem10` | NXT매수호가잔량10 | Number | Y | 9 | - |
| `unt_bidrem10` | 통합매수호가잔량10 | Number | Y | 9 | - |
| `krx_totofferrem` | KRX총매도호가잔량 | Number | Y | 9 | - |
| `nxt_totofferrem` | NXT총매도호가잔량 | Number | Y | 9 | - |
| `unt_totofferrem` | 통합총매도호가잔량 | Number | Y | 9 | - |
| `krx_totbidrem` | KRX총매수호가잔량 | Number | Y | 9 | - |
| `nxt_totbidrem` | NXT총매수호가잔량 | Number | Y | 9 | - |
| `unt_totbidrem` | 통합총매수호가잔량 | Number | Y | 9 | - |
| `krx_donsigubun` | KRX동시호가구분 | String | Y | 1 | - |
| `nxt_donsigubun` | NXT동시호가구분 | String | Y | 1 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `alloc_gubun` | 배분적용구분 | String | Y | 1 | - |
| `volume` | 누적거래량 | Number | Y | 12 | - |
| `krx_midprice` | KRX중간가격 | Number | Y | 8 | - |
| `krx_offermidsumrem` | KRX매도중간가잔량합계수량 | Number | Y | 9 | - |
| `krx_bidmidsumrem` | KRX매수중간가잔량합계수량 | Number | Y | 9 | - |
| `nxt_midprice` | NXT중간가격 | Number | Y | 8 | - |
| `nxt_offermidsumrem` | NXT매도중간가잔량합계수량 | Number | Y | 9 | - |
| `nxt_bidmidsumrem` | NXT매수중간가잔량합계수량 | Number | Y | 9 | - |
| `krx_midsumrem` | KRX중간가잔량합계수량 | Number | Y | 9 | - |
| `krx_midsumremgubun` | KRX중간가잔량구분(''없음'1'매도'2'매수) | Number | Y | 1 | - |
| `nxt_midsumrem` | NXT중간가잔량합계수량 | Number | Y | 9 | - |
| `nxt_midsumremgubun` | NXT중간가잔량구분(''없음'1'매도'2'매수) | String | Y | 1 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sqhk7Z",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UH1",
  "tr_key": "U005930   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "UH1",
        "tr_key": "U005930   "
    },
    "body": {
        "offerho4": "61600",
        "offerho3": "61500",
        "offerho6": "61800",
        "offerho5": "61700",
        "offerho8": "62000",
        "offerho7": "61900",
        "offerho9": "62100",
        "offerho2": "61400",
        "offerho1": "61300",
        "krx_offerrem5": "580825",
        "krx_offerrem4": "450859",
        "krx_offerrem7": "595030",
        "krx_offerrem6": "311385",
        "krx_offerrem9": "176709",
        "krx_offerrem8": "980847",
        "krx_offermidsumrem": "0",
        "krx_offerrem1": "65308",
        "krx_offerrem3": "574194",
        "krx_offerrem2": "363373",
        "offerho10": "62200",
        "krx_totbidrem": "1623247",
        "nxt_midprice": "0",
        "nxt_bidrem3": "0",
        "nxt_offerrem4": "0",
        "nxt_bidrem2": "0",
        "nxt_offerrem3": "0",
        "nxt_bidrem5": "0",
        "nxt_offerrem6": "0",
        "krx_midsumrem": "0",
        "nxt_bidrem4": "0",
        "nxt_offerrem5": "0",
        "nxt_bidrem7": "0",
        "nxt_offerrem8": "0",
        "krx_bidrem10": "110802",
        "nxt_bidrem6": "0",
        "nxt_offerrem7": "0",
        "nxt_bidrem9": "0",
        "nxt_bidrem8": "0",
        "nxt_offerrem9": "0",
        "unt_totofferrem": "4245162",
        "nxt_midsumrem": "0",
        "krx_donsigubun": "1",
        "nxt_offerrem10": "0",
        "alloc_gubun": "",
        "nxt_totofferrem": "0",
        "nxt_offerrem2": "0",
        "nxt_offerrem1": "0",
        "unt_offerrem10": "146632",
        "unt_totbidrem": "1623247",
        "nxt_totbidrem": "0",
        "hotime": "151545",
        "nxt_donsigubun": "0",
        "volume": " ",
        "krx_offerrem10": "146632",
        "krx_midprice": "61250",
        "unt_bidrem9": "120706",
        "krx_totofferrem": "4245162",
        "nxt_bidrem1": "0",
        "unt_bidrem5": "114532",
        "nxt_midsumremgubun": "",
        "unt_bidrem6": "121293",
        "unt_bidrem7": "112897",
        "unt_bidrem8": "195433",
        "unt_bidrem1": "333970",
        "unt_bidrem2": "166229",
        "unt_bidrem3": "204186",
        "unt_bidrem4": "143199",
        "bidho5": "60800",
        "bidho4": "60900",
        "bidho7": "60600",
        "bidho6": "60700",
        "bidho9": "60400",
        "bidho8": "60500",
        "bidho1": "61200",
        "bidho3": "61000",
        "bidho2": "61100",
        "nxt_bidrem10": "0",
        "unt_offerrem1": "65308",
        "bidho10": "60300",
        "shcode": "005930",
        "nxt_offermidsumrem": "0",
        "ex_shcode": "U005930",
        "krx_midsumremgubun": "",
        "krx_bidrem1": "333970",
        "krx_bidrem2": "166229",
        "unt_offerrem7": "595030",
        "krx_bidrem7": "112897",
        "krx_bidmidsumrem": "0",
        "unt_offerrem6": "311385",
        "krx_bidrem8": "195433",
        "unt_offerrem9": "176709",
        "krx_bidrem9": "120706",
        "unt_offerrem8": "980847",
        "unt_offerrem3": "574194",
        "krx_bidrem3": "204186",
        "nxt_bidmidsumrem": "0",
        "unt_offerrem2": "363373",
        "krx_bidrem4": "143199",
        "unt_bidrem10": "110802",
        "unt_offerrem5": "580825",
        "krx_bidrem5": "114532",
        "unt_offerrem4": "450859",
        "krx_bidrem6": "121293"
    }
}
```

---

<a id="tr-US2"></a>
## `US2` (통합)우선호가

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerho` | 매도호가 | Number | Y | 8 | - |
| `bidho` | 매수호가 | Number | Y | 8 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sqhk7Z",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "US2",
  "tr_key": "N000080   "
 }
}
```

---

<a id="tr-UYS"></a>
## `UYS` (통합)예상체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `hotime` | 호가시간 | String | Y | 6 | - |
| `yeprice` | 예상체결가격 | Number | Y | 8 | - |
| `yevolume` | 예상체결수량 | Number | Y | 12 | - |
| `jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `jnilchange` | 예상체결가전일종가대비 | Number | Y | 8 | - |
| `jnilydrate` | 예상체결가전일종가등락율 | Number | Y | 6.2 | - |
| `yofferho0` | 예상매도호가 | Number | Y | 8 | - |
| `ybidho0` | 예상매수호가 | Number | Y | 8 | - |
| `yofferrem0` | 예상매도호가수량 | Number | Y | 12 | - |
| `ybidrem0` | 예상매수호가수량 | Number | Y | 12 | - |
| `shcode` | 단축코드 | Number | Y | 9 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UYS",
  "tr_key": "U005930   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "UYS",
        "tr_key": "U005930   "
    },
    "body": {
        "jnilysign": "2",
        "ybidho0": "61600",
        "shcode": "005930",
        "yevolume": "6938216",
        "ex_shcode": "U005930",
        "ybidrem0": "1501",
        "jnilydrate": "2.49",
        "yofferho0": "61700",
        "yofferrem0": "489443",
        "jnilchange": "1500",
        "yeprice": "61700",
        "exchname": "KRX",
        "hotime": "153020"
    }
}
```

---

<a id="tr-UPH"></a>
## `UPH` (통합)프로그램매매종목별

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `price` | 현재가 | Number | Y | 8 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `change` | 전일대비 | Number | Y | 8 | - |
| `volume` | 누적거래량 | Number | Y | 10 | - |
| `drate` | 등락율 | Number | Y | 6.2 | - |
| `cdhrem` | 차익매도호가잔량 | Number | Y | 12 | - |
| `cshrem` | 차익매수호가잔량 | Number | Y | 12 | - |
| `bdhrem` | 비차익매도호가잔량 | Number | Y | 12 | - |
| `bshrem` | 비차익매수호가잔량 | Number | Y | 12 | - |
| `cdhvolume` | 차익매도호가수량 | Number | Y | 12 | - |
| `cshvolume` | 차익매수호가수량 | Number | Y | 12 | - |
| `bdhvolume` | 비차익매도호가수량 | Number | Y | 12 | - |
| `bshvolume` | 비차익매수호가수량 | Number | Y | 12 | - |
| `dwcvolume` | 전체매도위탁체결수량 | Number | Y | 12 | - |
| `swcvolume` | 전체매수위탁체결수량 | Number | Y | 12 | - |
| `djcvolume` | 전체매도자기체결수량 | Number | Y | 12 | - |
| `sjcvolume` | 전체매수자기체결수량 | Number | Y | 12 | - |
| `tdvolume` | 전체매도체결수량 | Number | Y | 12 | - |
| `tsvolume` | 전체매수체결수량 | Number | Y | 12 | - |
| `tvol` | 전체순매수수량 | Number | Y | 12 | - |
| `dwcvalue` | 전체매도위탁체결금액 | Number | Y | 15 | - |
| `swcvalue` | 전체매수위탁체결금액 | Number | Y | 15 | - |
| `djcvalue` | 전체매도자기체결금액 | Number | Y | 15 | - |
| `sjcvalue` | 전체매수자기체결금액 | Number | Y | 15 | - |
| `tdvalue` | 전체매도체결금액 | Number | Y | 15 | - |
| `tsvalue` | 전체매수체결금액 | Number | Y | 15 | - |
| `tval` | 전체순매수금액 | Number | Y | 15 | - |
| `pdgvolume` | 매도사전공시수량 | Number | Y | 12 | - |
| `psgvolume` | 매수사전공시수량 | Number | Y | 12 | - |
| `shcode` | 종목코드 | String | Y | 9 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImNkMzdiY2FmLTUwMjAtNGY2Yy1hYzM3LTcxY2JhZjc2MGE2OCIsIm5iZiI6MTc0Mjg2MTM0OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyOTQwMDAwLCJpYXQiOjE3NDI4NjEzNDksImp0aSI6IlBTVXJIa0pWaWVRMzhMREN5NkVVNUpCNWlmV1gzRDhwRlBKcSJ9.KpX1lQQIs4W2HdQIHdJDuJ1AWaYH69soejsKkJFv_8bF4jnlocMJsushvYbesrs",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UPH",
  "tr_key": "U005930   "
 }
}
```

---

<a id="tr-UK1"></a>
## `UK1` (통합)거래원

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 10 | 단축코드 7자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `offerno1` | 매도증권사코드1 | String | Y | 3 | - |
| `bidno1` | 매수증권사코드1 | String | Y | 3 | - |
| `offertrad1` | 매도회원사명1 | String | Y | 6 | - |
| `bidtrad1` | 매수회원사명1 | String | Y | 6 | - |
| `tradmdvol1` | 매도거래량1 | Number | Y | 10 | - |
| `tradmsvol1` | 매수거래량1 | Number | Y | 10 | - |
| `tradmdrate1` | 매도거래량비중1 | Number | Y | 6.2 | - |
| `tradmsrate1` | 매수거래량비중1 | Number | Y | 6.2 | - |
| `tradmdcha1` | 매도거래량직전대비1 | Number | Y | 10 | - |
| `tradmscha1` | 매수거래량직전대비1 | Number | Y | 10 | - |
| `offerno2` | 매도증권사코드2 | String | Y | 3 | - |
| `bidno2` | 매수증권사코드2 | String | Y | 3 | - |
| `offertrad2` | 매도회원사명2 | String | Y | 6 | - |
| `bidtrad2` | 매수회원사명2 | String | Y | 6 | - |
| `tradmdvol2` | 매도거래량2 | Number | Y | 10 | - |
| `tradmsvol2` | 매수거래량2 | Number | Y | 10 | - |
| `tradmdrate2` | 매도거래량비중2 | Number | Y | 6.2 | - |
| `tradmsrate2` | 매수거래량비중2 | Number | Y | 6.2 | - |
| `tradmdcha2` | 매도거래량직전대비2 | Number | Y | 10 | - |
| `tradmscha2` | 매수거래량직전대비2 | Number | Y | 10 | - |
| `offerno3` | 매도증권사코드3 | String | Y | 3 | - |
| `bidno3` | 매수증권사코드3 | String | Y | 3 | - |
| `offertrad3` | 매도회원사명3 | String | Y | 6 | - |
| `bidtrad3` | 매수회원사명3 | String | Y | 6 | - |
| `tradmdvol3` | 매도거래량3 | Number | Y | 10 | - |
| `tradmsvol3` | 매수거래량3 | Number | Y | 10 | - |
| `tradmdrate3` | 매도거래량비중3 | Number | Y | 6.2 | - |
| `tradmsrate3` | 매수거래량비중3 | Number | Y | 6.2 | - |
| `tradmdcha3` | 매도거래량직전대비3 | Number | Y | 10 | - |
| `tradmscha3` | 매수거래량직전대비3 | Number | Y | 10 | - |
| `offerno4` | 매도증권사코드4 | String | Y | 3 | - |
| `bidno4` | 매수증권사코드4 | String | Y | 3 | - |
| `offertrad4` | 매도회원사명4 | String | Y | 6 | - |
| `bidtrad4` | 매수회원사명4 | String | Y | 6 | - |
| `tradmdvol4` | 매도거래량4 | Number | Y | 10 | - |
| `tradmsvol4` | 매수거래량4 | Number | Y | 10 | - |
| `tradmdrate4` | 매도거래량비중4 | Number | Y | 6.2 | - |
| `tradmsrate4` | 매수거래량비중4 | Number | Y | 6.2 | - |
| `tradmdcha4` | 매도거래량직전대비4 | Number | Y | 10 | - |
| `tradmscha4` | 매수거래량직전대비4 | Number | Y | 10 | - |
| `offerno5` | 매도증권사코드5 | String | Y | 3 | - |
| `bidno5` | 매수증권사코드5 | String | Y | 3 | - |
| `offertrad5` | 매도회원사명5 | String | Y | 6 | - |
| `bidtrad5` | 매수회원사명5 | String | Y | 6 | - |
| `tradmdvol5` | 매도거래량5 | Number | Y | 10 | - |
| `tradmsvol5` | 매수거래량5 | Number | Y | 10 | - |
| `tradmdrate5` | 매도거래량비중5 | Number | Y | 6.2 | - |
| `tradmsrate5` | 매수거래량비중5 | Number | Y | 6.2 | - |
| `tradmdcha5` | 매도거래량직전대비5 | Number | Y | 10 | - |
| `tradmscha5` | 매수거래량직전대비5 | Number | Y | 10 | - |
| `ftradmdvol` | 외국계증권사매도합계 | String | Y | 10 | - |
| `ftradmsvol` | 외국계증권사매수합계 | String | Y | 10 | - |
| `ftradmdrate` | 외국계증권사매도거래량비중 | Number | Y | 6.2 | - |
| `ftradmsrate` | 외국계증권사매수거래량비중 | Number | Y | 6.2 | - |
| `ftradmdcha` | 외국계증권사매도거래량직전대비 | String | Y | 10 | - |
| `ftradmscha` | 외국계증권사매수거래량직전대비 | String | Y | 10 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `tradmdval1` | 매도거래대금1 | Number | Y | 15 | - |
| `tradmsval1` | 매수거래대금1 | Number | Y | 15 | - |
| `tradmdavg1` | 매도평균단가1 | Number | Y | 7 | - |
| `tradmsavg1` | 매수평균단가1 | Number | Y | 7 | - |
| `tradmdval2` | 매도거래대금2 | Number | Y | 15 | - |
| `tradmsval2` | 매수거래대금2 | Number | Y | 15 | - |
| `tradmdavg2` | 매도평균단가2 | Number | Y | 7 | - |
| `tradmsavg2` | 매수평균단가2 | Number | Y | 7 | - |
| `tradmdval3` | 매도거래대금3 | Number | Y | 15 | - |
| `tradmsval3` | 매수거래대금3 | Number | Y | 15 | - |
| `tradmdavg3` | 매도평균단가3 | Number | Y | 7 | - |
| `tradmsavg3` | 매수평균단가3 | Number | Y | 7 | - |
| `tradmdval4` | 매도거래대금4 | Number | Y | 15 | - |
| `tradmsval4` | 매수거래대금4 | Number | Y | 15 | - |
| `tradmdavg4` | 매도평균단가4 | Number | Y | 7 | - |
| `tradmsavg4` | 매수평균단가4 | Number | Y | 7 | - |
| `tradmdval5` | 매도거래대금5 | Number | Y | 15 | - |
| `tradmsval5` | 매수거래대금5 | Number | Y | 15 | - |
| `tradmdavg5` | 매도평균단가5 | Number | Y | 7 | - |
| `tradmsavg5` | 매수평균단가5 | Number | Y | 7 | - |
| `ftradmdval` | 외국계증권사매도거래대금 | Number | Y | 15 | - |
| `ftradmsval` | 외국계증권사매수거래대금 | Number | Y | 15 | - |
| `ftradmdavg` | 외국계증권사매도평균단가 | Number | Y | 7 | - |
| `ftradmsavg` | 외국계증권사매수평균단가 | Number | Y | 7 | - |
| `time` | 수신시간 | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sqhk",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UK1",
  "tr_key": "U000080   "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "UK1",
        "tr_key": "U000080   "
    },
    "body": {
        "tradmdrate1": "17.12",
        "tradmdvol5": "11626",
        "tradmdvol3": "24816",
        "tradmdrate3": "9.46",
        "tradmdrate2": "10.35",
        "tradmdvol4": "16941",
        "offerno2": "012",
        "tradmdrate5": "4.43",
        "offerno1": "050",
        "tradmdrate4": "6.46",
        "offerno4": "003",
        "offerno3": "002",
        "bidtrad4": "메릴린",
        "offerno5": "005",
        "bidtrad5": "메리츠",
        "bidtrad2": "신한투",
        "bidtrad3": "NH투자",
        "tradmdvol1": "44893",
        "bidtrad1": "키움증",
        "tradmdvol2": "27140",
        "tradmdval3": "486",
        "offertrad5": "미래에",
        "tradmdval4": "331",
        "tradmdval1": "880",
        "tradmdval2": "532",
        "tradmdval5": "228",
        "tradmscha2": "0",
        "ftradmdval": "0",
        "tradmscha1": "0",
        "tradmscha4": "0",
        "tradmscha3": "0",
        "offertrad2": "NH투자",
        "offertrad1": "키움증",
        "offertrad4": "한국증",
        "offertrad3": "신한투",
        "tradmdcha5": "0",
        "tradmdcha4": "0",
        "tradmsavg1": "19655",
        "tradmsavg2": "19584",
        "tradmscha5": "0",
        "tradmdavg1": "19615",
        "tradmdavg3": "19602",
        "tradmdavg2": "19632",
        "tradmdavg5": "19656",
        "tradmdavg4": "19563",
        "tradmsavg3": "19571",
        "ftradmscha": "0000000000",
        "tradmsavg4": "19763",
        "ftradmdvol": "0000000911",
        "tradmsavg5": "19726",
        "ftradmdavg": "0",
        "tradmsval3": "414",
        "tradmsval2": "793",
        "tradmsval5": "260",
        "ftradmsval": "0",
        "tradmsval4": "356",
        "tradmsval1": "841",
        "tradmdcha1": "3",
        "tradmdcha3": "0",
        "tradmdcha2": "0",
        "bidno1": "050",
        "bidno3": "012",
        "tradmsvol5": "13187",
        "bidno2": "002",
        "tradmsvol4": "18035",
        "bidno5": "010",
        "bidno4": "044",
        "tradmsvol1": "42815",
        "tradmsvol3": "21185",
        "tradmsvol2": "40513",
        "tradmsrate2": "15.45",
        "tradmsrate1": "16.33",
        "tradmsrate4": "6.88",
        "tradmsrate3": "8.08",
        "tradmsrate5": "5.03",
        "ftradmsvol": "0000018035",
        "ftradmdcha": "0000000000",
        "ftradmsrate": "6.88",
        "shcode": "000080",
        "ftradmsavg": "0",
        "ftradmdrate": "0.35",
        "ex_shcode": "U000080",
        "time": "160349",
        "exchname": "NXT"
    }
}
```

---

<a id="tr-UBT"></a>
## `UBT` (통합)시간대별투자자매매추이

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 4 | U + 업종코드 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tjjtime` | 수신시간 | String | Y | 8 | - |
| `tjjcode1` | 투자자코드1(개인) | String | Y | 4 | - |
| `msvolume1` | 매수거래량1 | Number | Y | 8 | - |
| `mdvolume1` | 매도거래량1 | Number | Y | 8 | - |
| `msvol1` | 거래량순매수1 | Number | Y | 8 | - |
| `msvalue1` | 매수거래대금1 | Number | Y | 6 | - |
| `mdvalue1` | 매도거래대금1 | Number | Y | 6 | - |
| `msval1` | 거래대금순매수1 | Number | Y | 6 | - |
| `tjjcode2` | 투자자코드2(외국인) | String | Y | 4 | - |
| `msvolume2` | 매수거래량2 | Number | Y | 8 | - |
| `mdvolume2` | 매도거래량2 | Number | Y | 8 | - |
| `msvol2` | 거래량순매수2 | Number | Y | 8 | - |
| `msvalue2` | 매수거래대금2 | Number | Y | 6 | - |
| `mdvalue2` | 매도거래대금2 | Number | Y | 6 | - |
| `msval2` | 거래대금순매수2 | Number | Y | 6 | - |
| `tjjcode3` | 투자자코드3(기관계) | String | Y | 4 | - |
| `msvolume3` | 매수거래량3 | Number | Y | 8 | - |
| `mdvolume3` | 매도거래량3 | Number | Y | 8 | - |
| `msvol3` | 거래량순매수3 | Number | Y | 8 | - |
| `msvalue3` | 매수거래대금3 | Number | Y | 6 | - |
| `mdvalue3` | 매도거래대금3 | Number | Y | 6 | - |
| `msval3` | 거래대금순매수3 | Number | Y | - | - |
| `tjjcode4` | 투자자코드4(증권) | String | Y | 4 | - |
| `msvolume4` | 매수거래량4 | Number | Y | 8 | - |
| `mdvolume4` | 매도거래량4 | Number | Y | 8 | - |
| `msvol4` | 거래량순매수4 | Number | Y | 8 | - |
| `msvalue4` | 매수거래대금4 | Number | Y | 6 | - |
| `mdvalue4` | 매도거래대금4 | Number | Y | 6 | - |
| `msval4` | 거래대금순매수4 | Number | Y | 6 | - |
| `tjjcode5` | 투자자코드5(투신) | String | Y | 4 | - |
| `msvolume5` | 매수거래량5 | Number | Y | 8 | - |
| `mdvolume5` | 매도거래량5 | Number | Y | 8 | - |
| `msvol5` | 거래량순매수5 | Number | Y | 8 | - |
| `msvalue5` | 매수거래대금5 | Number | Y | 6 | - |
| `mdvalue5` | 매도거래대금5 | Number | Y | 6 | - |
| `msval5` | 거래대금순매수5 | Number | Y | 6 | - |
| `tjjcode6` | 투자자코드6(은행) | String | Y | 4 | - |
| `msvolume6` | 매수거래량6 | Number | Y | 8 | - |
| `mdvolume6` | 매도거래량6 | Number | Y | 8 | - |
| `msvol6` | 거래량순매수6 | Number | Y | 8 | - |
| `msvalue6` | 매수거래대금6 | Number | Y | 6 | - |
| `mdvalue6` | 매도거래대금6 | Number | Y | 6 | - |
| `msval6` | 거래대금순매수6 | Number | Y | 6 | - |
| `tjjcode7` | 투자자코드7(보험) | String | Y | 4 | - |
| `msvolume7` | 매수거래량7 | Number | Y | 8 | - |
| `mdvolume7` | 매도거래량7 | Number | Y | 8 | - |
| `msvol7` | 거래량순매수7 | Number | Y | 8 | - |
| `msvalue7` | 매수거래대금7 | Number | Y | 6 | - |
| `mdvalue7` | 매도거래대금7 | Number | Y | 6 | - |
| `msval7` | 거래대금순매수7 | Number | Y | 6 | - |
| `tjjcode8` | 투자자코드8(종금) | String | Y | 4 | - |
| `msvolume8` | 매수거래량8 | Number | Y | 8 | - |
| `mdvolume8` | 매도거래량8 | Number | Y | 8 | - |
| `msvol8` | 거래량순매수8 | Number | Y | 8 | - |
| `msvalue8` | 매수거래대금8 | Number | Y | 6 | - |
| `mdvalue8` | 매도거래대금8 | Number | Y | 6 | - |
| `msval8` | 거래대금순매수8 | Number | Y | 6 | - |
| `tjjcode9` | 투자자코드9(기금) | String | Y | 4 | - |
| `msvolume9` | 매수거래량9 | Number | Y | 8 | - |
| `mdvolume9` | 매도거래량9 | Number | Y | 8 | - |
| `msvol9` | 거래량순매수9 | Number | Y | 8 | - |
| `msvalue9` | 매수거래대금9 | Number | Y | 6 | - |
| `mdvalue9` | 매도거래대금9 | Number | Y | 6 | - |
| `msval9` | 거래대금순매수9 | Number | Y | 6 | - |
| `tjjcode10` | 투자자코드10(선물업자) | String | Y | 4 | - |
| `msvolume10` | 매수거래량10 | Number | Y | 8 | - |
| `mdvolume10` | 매도거래량10 | Number | Y | 8 | - |
| `msvol10` | 거래량순매수10 | Number | Y | 8 | - |
| `msvalue10` | 매수거래대금10 | Number | Y | 6 | - |
| `mdvalue10` | 매도거래대금10 | Number | Y | 6 | - |
| `msval10` | 거래대금순매수10 | Number | Y | 6 | - |
| `tjjcode11` | 투자자코드11(기타) | String | Y | 4 | - |
| `msvolume11` | 매수거래량11 | Number | Y | 8 | - |
| `mdvolume11` | 매도거래량11 | Number | Y | 8 | - |
| `msvol11` | 거래량순매수11 | Number | Y | 8 | - |
| `msvalue11` | 매수거래대금11 | Number | Y | 6 | - |
| `mdvalue11` | 매도거래대금11 | Number | Y | 6 | - |
| `msval11` | 거래대금순매수11 | Number | Y | 6 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |
| `tjjcode0` | 투자자코드0(사모펀드) | String | Y | 4 | - |
| `msvolume0` | 매수거래량0 | String | Y | 8 | - |
| `mdvolume0` | 매도거래량0 | Number | Y | 8 | - |
| `msvol0` | 거래량순매수0 | Number | Y | 8 | - |
| `msvalue0` | 매수거래대금0 | Number | Y | 6 | - |
| `mdvalue0` | 매도거래대금0 | Number | Y | 6 | - |
| `msval0` | 거래대금순매수0 | Number | Y | 6 | - |
| `ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImNkMzdiY2FmLTUwMjAtNGY2Yy1hYzM3LTcxY2JhZjc2MGE2OCIsIm5iZiI6MTc0Mjg2MTM0OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyOTQwMDAwLCJpYXQiOjE3NDI4NjEzNDksImp0aSI6IlBTVXJIa0pWaWVRMzhMREN5NkVVNUpCNWlmV1gzRDhwRlBKcSJ9.KpX1lQQIs4W2HdQIHdJDuJ1AWaYH69soejsKkJFv_8bF4jnlocMJsushvYbesrs2BM2evkz7",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UBT",
  "tr_key": "U001"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "UBT",
        "tr_key": "U001"
    },
    "body": {
        "mdvalue0": "1344",
        "mdvalue1": "55426",
        "msvolume8": "474",
        "msvolume9": "13560",
        "msvolume4": "10244",
        "mdvalue6": "78",
        "msvolume5": "2663",
        "mdvalue7": "566",
        "msvolume6": "82",
        "mdvalue8": "87",
        "msvolume7": "809",
        "mdvalue9": "9457",
        "mdvalue2": "25515",
        "msvolume0": "1410",
        "msvolume1": "342538",
        "mdvalue3": "16752",
        "msvolume2": "85505",
        "mdvalue4": "3649",
        "msvolume3": "29246",
        "mdvalue5": "1568",
        "mdvolume0": "2589",
        "mdvolume9": "14896",
        "mdvolume3": "30145",
        "mdvolume4": "7630",
        "mdvolume1": "338330",
        "mdvolume2": "89719",
        "mdvolume7": "1125",
        "mdvolume8": "738",
        "mdvolume5": "3000",
        "mdvolume6": "164",
        "msvalue1": "54772",
        "msvalue2": "24751",
        "msvalue0": "907",
        "msvalue5": "1490",
        "msvalue6": "55",
        "msvalue3": "17448",
        "msvol11": "905",
        "msvalue4": "4945",
        "msvol10": "0",
        "msvalue9": "9262",
        "mdvalue11": "770",
        "msvalue7": "499",
        "msvalue8": "287",
        "mdvalue10": "0",
        "tjjtime": "16460001",
        "tjjcode0": "0000",
        "tjjcode10": "0011",
        "msvolume10": "0",
        "tjjcode11": "0007",
        "tjjcode6": "0004",
        "msval6": "-23",
        "tjjcode5": "0003",
        "msval5": "-78",
        "msval4": "1296",
        "tjjcode8": "0005",
        "msval3": "697",
        "tjjcode7": "0002",
        "tjjcode2": "0017",
        "tjjcode1": "0008",
        "msval9": "-196",
        "tjjcode4": "0001",
        "msval8": "200",
        "tjjcode3": "0018",
        "msval7": "-66",
        "msval2": "-764",
        "msval1": "-655",
        "tjjcode9": "0006",
        "mdvolume10": "0",
        "msval0": "-437",
        "mdvolume11": "3275",
        "msvol9": "-1335",
        "msvol5": "-337",
        "msvol6": "-82",
        "msvol7": "-316",
        "msvol8": "-264",
        "msvol1": "4208",
        "ex_upcode": "U001",
        "msvol2": "-4214",
        "msvol3": "-899",
        "msval11": "722",
        "msvol4": "2614",
        "msval10": "0",
        "msvol0": "-1178",
        "msvolume11": "4179",
        "msvalue10": "0",
        "msvalue11": "1492",
        "upcode": "001"
    }
}
```

---

<a id="tr-UBM"></a>
## `UBM` (통합) 업종별투자자별매매현황

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 4 | U + 업종코드 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tjjcode` | 투자자코드 | String | Y | 4 | - |
| `tjjtime` | 수신시간 | String | Y | 8 | - |
| `msvolume` | 매수거래량 | Number | Y | 8 | - |
| `mdvolume` | 매도거래량 | Number | Y | 8 | - |
| `msvol` | 거래량순매수 | Number | Y | 8 | - |
| `p_msvol` | 거래량순매수직전대비 | Number | Y | 8 | - |
| `msvalue` | 매수거래대금 | Number | Y | 6 | - |
| `mdvalue` | 매도거래대금 | Number | Y | 6 | - |
| `msval` | 거래대금순매수 | Number | Y | 6 | - |
| `p_msval` | 거래대금순매수직전대비 | Number | Y | 6 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |
| `ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |


### 요청 Example

```
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImNkMzdiY2FmLTUwMjAtNGY2Yy1hYzM3LTcxY2JhZjc2MGE2OCIsIm5iZiI6MTc0Mjg2MTM0OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyOTQwMDAwLCJpYXQiOjE3NDI4NjEzNDksImp0aSI6IlBTVXJIa0pWaWVRMzhMREN5NkVVNUpCNWlmV1gzRDhwRlBKcSJ9.KpX1lQQIs4W2HdQIHdJDuJ1AWaYH69soejsKkJFv_8bF4jnlocMJsushvYbesrs2BM2evkz7",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UBM",
  "tr_key": "U001"
 }
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "UBM",
        "tr_key": "U001"
    },
    "body": {
        "p_msval": "0",
        "tjjtime": "17103000",
        "p_msvol": "0",
        "mdvalue": "219",
        "msvolume": "1380",
        "upcode": "001",
        "ex_upcode": "U001",
        "tjjcode": "0010",
        "msvalue": "184",
        "mdvolume": "1510",
        "msvol": "-130",
        "msval": "-34"
    }
}
```

---

<a id="tr-UPM"></a>
## `UPM` (통합)프로그램매매전체집계

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 2 | 'U' + 구분값<br/>U0:코스피<br/>U1:코스닥 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `time` | 수신시간 | String | Y | 6 | - |
| `cdhrem` | 차익매도호가잔량 | Number | Y | 6 | - |
| `cshrem` | 차익매수호가잔량 | Number | Y | 6 | - |
| `bdhrem` | 비차익매도호가잔량 | Number | Y | 6 | - |
| `bshrem` | 비차익매수호가잔량 | Number | Y | 6 | - |
| `cdhvolume` | 차익매도호가수량 | Number | Y | 6 | - |
| `cshvolume` | 차익매수호가수량 | Number | Y | 6 | - |
| `bdhvolume` | 비차익매도호가수량 | Number | Y | 6 | - |
| `bshvolume` | 비차익매수호가수량 | Number | Y | 6 | - |
| `cdwvolume` | 차익매도위탁체결수량 | Number | Y | 6 | - |
| `cdjvolume` | 차익매도자기체결수량 | Number | Y | 6 | - |
| `cswvolume` | 차익매수위탁체결수량 | Number | Y | 6 | - |
| `csjvolume` | 차익매수자기체결수량 | Number | Y | 6 | - |
| `cwvol` | 차익위탁순매수수량 | Number | Y | 6 | - |
| `cjvol` | 차익자기순매수수량 | Number | Y | 6 | - |
| `bdwvolume` | 비차익매도위탁체결수량 | Number | Y | 6 | - |
| `bdjvolume` | 비차익매도자기체결수량 | Number | Y | 6 | - |
| `bswvolume` | 비차익매수위탁체결수량 | Number | Y | 6 | - |
| `bsjvolume` | 비차익매수자기체결수량 | Number | Y | 6 | - |
| `bwvol` | 비차익위탁순매수수량 | Number | Y | 6 | - |
| `bjvol` | 비차익자기순매수수량 | Number | Y | 6 | - |
| `dwvolume` | 전체매도위탁체결수량 | Number | Y | 6 | - |
| `swvolume` | 전체매수위탁체결수량 | Number | Y | 6 | - |
| `전체매도자기체결수량` | 전체위탁순매수수량 | Number | Y | 6 | - |
| `sjvolume` | 전체매수자기체결수량 | Number | Y | 6 | - |
| `jvol` | 전체자기순매수수량 | Number | Y | 6 | - |
| `cdwvalue` | 차익매도위탁체결금액 | Number | Y | 8 | - |
| `cdjvalue` | 차익매도자기체결금액 | Number | Y | 8 | - |
| `cswvalue` | 차익매수위탁체결금액 | Number | Y | 8 | - |
| `csjvalue` | 차익매수자기체결금액 | Number | Y | 8 | - |
| `cwval` | 차익위탁순매수금액 | Number | Y | 8 | - |
| `cjval` | 차익자기순매수금액 | Number | Y | 8 | - |
| `bdwvalue` | 비차익매도위탁체결금액 | Number | Y | 8 | - |
| `bdjvalue` | 비차익매도자기체결금액 | Number | Y | 8 | - |
| `bswvalue` | 비차익매수위탁체결금액 | Number | Y | 8 | - |
| `bsjvalue` | 비차익매수자기체결금액 | Number | Y | 8 | - |
| `bwval` | 비차익위탁순매수금액 | Number | Y | 8 | - |
| `bjval` | 비차익자기순매수금액 | Number | Y | 8 | - |
| `dwvalue` | 전체매도위탁체결금액 | Number | Y | 8 | - |
| `swvalue` | 전체매수위탁체결금액 | Number | Y | 8 | - |
| `wval` | 전체위탁순매수금액 | Number | Y | 8 | - |
| `djvalue` | 전체매도자기체결금액 | Number | Y | 8 | - |
| `sjvalue` | 전체매수자기체결금액 | Number | Y | 8 | - |
| `jval` | 전체자기순매수금액 | Number | Y | 8 | - |
| `k200jisu` | KOSPI200지수 | Number | Y | 6.2 | - |
| `k200sign` | KOSPI200전일대비구분 | String | Y | 1 | - |
| `change` | KOSPI200전일대비 | Number | Y | 4.2 | - |
| `k200basis` | KOSPI200베이시스 | Number | Y | 4.2 | - |
| `cdvolume` | 차익매도체결수량합계 | Number | Y | 6 | - |
| `csvolume` | 차익매수체결수량합계 | Number | Y | 6 | - |
| `cvol` | 차익순매수수량합계 | Number | Y | 6 | - |
| `bdvolume` | 비차익매도체결수량합계 | Number | Y | 6 | - |
| `bsvolume` | 비차익매수체결수량합계 | Number | Y | 6 | - |
| `bvol` | 비차익순매수수량합계 | Number | Y | 6 | - |
| `tdvolume` | 전체매도체결수량합계 | Number | Y | 6 | - |
| `tsvolume` | 전체매수체결수량합계 | Number | Y | 6 | - |
| `tvol` | 전체순매수수량합계 | Number | Y | 6 | - |
| `cdvalue` | 차익매도체결금액합계 | Number | Y | 8 | - |
| `csvalue` | 차익매수체결금액합계 | Number | Y | 8 | - |
| `cval` | 차익순매수금액합계 | Number | Y | 8 | - |
| `bdvalue` | 비차익매도체결금액합계 | Number | Y | 8 | - |
| `bsvalue` | 비차익매수체결금액합계 | Number | Y | 8 | - |
| `bval` | 비차익순매수금액합계 | Number | Y | 8 | - |
| `tdvalue` | 전체매도체결금액합계 | Number | Y | 8 | - |
| `tsvalue` | 전체매수체결금액합계 | Number | Y | 8 | - |
| `tval` | 전체순매수금액합계 | Number | Y | 8 | - |
| `p_cdvolcha` | 차익매도체결수량직전대비 | Number | Y | 6 | - |
| `p_csvolcha` | 차익매수체결수량직전대비 | Number | Y | 6 | - |
| `p_cvolcha` | 차익순매수수량직전대비 | Number | Y | 6 | - |
| `p_bdvolcha` | 비차익매도체결수량직전대비 | Number | Y | 6 | - |
| `p_bsvolcha` | 비차익매수체결수량직전대비 | Number | Y | 6 | - |
| `p_bvolcha` | 비차익순매수수량직전대비 | Number | Y | 6 | - |
| `p_tdvolcha` | 전체매도체결수량직전대비 | Number | Y | 6 | - |
| `p_tsvolcha` | 전체매수체결수량직전대비 | Number | Y | 6 | - |
| `p_tvolcha` | 전체순매수수량직전대비 | Number | Y | 6 | - |
| `p_cdvalcha` | 차익매도체결금액직전대비 | Number | Y | 8 | - |
| `p_csvalcha` | 차익매수체결금액직전대비 | Number | Y | 8 | - |
| `p_cvalcha` | 차익순매수금액직전대비 | Number | Y | 8 | - |
| `p_bdvalcha` | 비차익매도체결금액직전대비 | Number | Y | 8 | - |
| `p_bsvalcha` | 비차익매수체결금액직전대비 | Number | Y | 8 | - |
| `p_bvalcha` | 비차익순매수금액직전대비 | Number | Y | 8 | - |
| `p_tdvalcha` | 전체매도체결금액직전대비 | Number | Y | 8 | - |
| `p_tsvalcha` | 전체매수체결금액직전대비 | Number | Y | 8 | - |
| `p_tvalcha` | 전체순매수금액직전대비 | Number | Y | 8 | - |
| `gubun` | 구분값 | String | Y | 1 | - |
| `ex_gubun` | 거래소별구분값 | String | Y | 2 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6Ijg4N2UxYTA3LWQ5MjgtNDU0YS1hZTZjLTE0YWVkMjRkMjk3NiIsIm5iZiI6MTc0Mjk0MzMyNywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQzMDI2Mzk5LCJpYXQiOjE3NDI5NDMzMjcsImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.GL_79eY2ogehy-Eqv2XoEvljvoM5TUSLIKripBfi3Oq6k1SGgsGk7njfk3kbb1YO8",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UPM",
  "tr_key": "01"
 }
}
```

---

<a id="tr-UVI"></a>
## `UVI` (통합)VI발동해제

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | Y | 10 | 'U' + 단축코드 6자리 + 공백 3자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `krx_vi_gubun` | KRXVI구분 (0:해제1:정적발동2:동적발동3:정적&동적) | String | Y | 1 | 0:해제1:정적발동2:동적발동3:정적&동적 |
| `krx_svi_recprice` | KRX정적VI발동기준가격 | Number | Y | 8 | - |
| `krx_dvi_recprice` | KRX동적VI발동기준가격 | Number | Y | 8 | - |
| `krx_vi_trgprice` | KRXVI발동가격 | Number | Y | 8 | - |
| `krx_time` | KRX시간 | String | Y | 6 | - |
| `nxt_vi_gubun` | NXTVI구분(0:해제1:정적발동2:동적발동3:정적&동적) | String | Y | - | 0:해제1:정적발동2:동적발동3:정적&동적 |
| `nxt_svi_recprice` | NXT정적VI발동기준가격 | Number | Y | 8 | - |
| `nxt_dvi_recprice` | NXT동적VI발동기준가격 | Number | Y | 8 | - |
| `nxt_vi_trgprice` | NXTVI발동가격 | Number | Y | 8 | - |
| `nxt_time` | NXT시간 | String | Y | 6 | - |
| `shcode` | 단축코드 | String | Y | 9 | - |
| `ref_shcode` | 참조코드(미사용) | String | Y | 6 | - |
| `exchname` | 거래소명 | String | Y | 3 | - |
| `ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjlkZmJhYWNiLWY5NWUtNGMwMi1hZGFlLTBhYzI3YTU4ZmM2NiIsIm5iZiI6MTc0MjUxMDc3OSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNzQyNTk0NDAwLCJpYXQiOjE3NDI1MTA3NzksImp0aSI6IlBTUFphQmp2S3V6V3VjeGlvYzhib21jdmsxY0U3cUs2V2JubSJ9.r8eqrh_LoLWvOa2WhCBLnXilk-2LZLSGcOSwJ3KuNolsHwRFvncrG0FEdw2sqhk7Z",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "UVI",
  "tr_key": "0000000000"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "UVI",
        "tr_key": "0000000000"
    },
    "body": {
        "krx_time": "173030",
        "shcode": "000000000",
        "krx_svi_recprice": "0",
        "nxt_svi_recprice": "0",
        "ex_shcode": "U258610",
        "krx_vi_gubun": "0",
        "krx_dvi_recprice": "0",
        "krx_vi_trgprice": "0",
        "ref_shcode": "258610",
        "nxt_dvi_recprice": "0",
        "nxt_time": "",
        "nxt_vi_gubun": "",
        "exchname": "1X",
        "nxt_vi_trgprice": "0"
    }
}
```

---

<a id="tr-AFR"></a>
## `AFR` API사용자조건검색실시간

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 사용자구분키 | String | N | 11 | t1860 TR의 t1860OutBlock. sAlertNum (실시간키) |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `gsCode` | 종목코드 | String | Y | 9 | - |
| `gshname` | 종목명 | String | Y | 40 | - |
| `gsPrice` | 현재가 | String | Y | 8 | - |
| `gsSign` | 전일대비구분 | String | Y | 1 | - |
| `gsChange` | 전일대비 | String | Y | 8 | - |
| `gsChgRate` | 등락율 | String | Y | 6 | - |
| `gsVolume` | 거래량 | String | Y | 9 | - |
| `gsJobFlag` | 종목상태 | String | Y | 1 | N:진입 R:재진입 O:이탈 |


### 요청 Example

```json
{
 "header": {
  "token": "토큰값",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "AFR",
  "tr_key": "실시간키"
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "AFR",
        "tr_key": "실시간키"
    },
    "body": {
        "gsJobFlag": "O",
        "gsVolume": "3432360",
        "gsPrice": "2435",
        "gsSign": "2",
        "gshname": "HB테크놀러지",
        "gsChange": "45",
        "gsChgRate": "1.88",
        "gsCode": "078150"
    }
}
```
