# [해외선물] 실시간 시세

> LS증권 OPEN API 정의서 · 그룹: **해외선물** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=c1ef0e8b-4666-4d8c-a77f-6ab488cfdb39&api_id=3dc1c51b-5ff2-456d-ad2a-055e78ba2b03)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `3dc1c51b-5ff2-456d-ad2a-055e78ba2b03` |
| Protocol | WEBSOCKET |
| Method | POST |
| Domain | `wss://openapi.ls-sec.co.kr:9443` |
| URL | `/websocket/overseas-futureoption` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외선물옵션 주문현황 및 시세정보를 실시간으로 확인할 수 있습니다. |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외선물 체결 | [OVC](realtime.md#tr-OVC) | - | - | - |
| 해외선물 호가 | [OVH](realtime.md#tr-OVH) | - | - | - |
| 해외옵션 체결 | [WOC](realtime.md#tr-WOC) | - | - | - |
| 해외옵션 호가 | [WOH](realtime.md#tr-WOH) | - | - | - |
| 해외선물 주문접수 | [TC1](realtime.md#tr-TC1) | - | - | - |
| 해외선물 주문응답 | [TC2](realtime.md#tr-TC2) | - | - | - |
| 해외선물 주문체결 | [TC3](realtime.md#tr-TC3) | - | - | - |

> **WebSocket 실시간 데이터**: 접속 도메인은 위 `Domain`(`wss://`)을 사용합니다.
> 접속 시 Header에 발급받은 `token`(접근토큰)을 설정하고, 각 TR 아래의 패킷 구조로 등록/해제(`tr_type`: 1 계좌등록, 2 계좌해제, 3 실시간 시세 등록, 4 실시간 시세 해제) 요청을 보냅니다. 실제 데이터는 동일 채널로 push 수신합니다.

---

<a id="tr-OVC"></a>
## `OVC` 해외선물 체결

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
| `symbol` | 종목코드 | String | Y | 8 | - |
| `ovsdate` | 체결일자(현지) | String | Y | 8 | - |
| `kordate` | 체결일자(한국) | String | Y | 8 | - |
| `trdtm` | 체결시간(현지) | String | Y | 6 | - |
| `kortm` | 체결시간(한국) | String | Y | 6 | - |
| `curpr` | 체결가격 | String | Y | 15.9 | - |
| `ydiffpr` | 전일대비 | String | Y | 15.9 | - |
| `ydiffSign` | 전일대비기호 | String | Y | 1 | - |
| `open` | 시가 | String | Y | 15.9 | - |
| `high` | 고가 | String | Y | 15.9 | - |
| `low` | 저가 | String | Y | 15.9 | - |
| `chgrate` | 등락율 | String | Y | 6.2 | - |
| `trdq` | 건별체결수량 | String | Y | 10 | - |
| `totq` | 누적체결수량 | String | Y | 15 | - |
| `cgubun` | 체결구분 | String | Y | 1 | - |
| `mdvolume` | 매도누적체결수량 | String | Y | 15 | - |
| `msvolume` | 매수누적체결수량 | String | Y | 15 | - |
| `ovsmkend` | 장마감일 | String | Y | 8 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjBmYTRhNmE1LWYwMzMtNGEyZS04MjgyLTE3MTdmOGRkN2EzZiIsIm5iZiI6MTY4Njc4Mjg2NSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2ODY2Mzk5LCJpYXQiOjE2ODY3ODI4NjUsImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.e2T7dj3jYedMsM8nd2FPr2OF8ZRxUwzqBNGgxwamMCa1PAx4oqjOuCdmKLs7oZfL9OICQ4AAA5_ceDulGBGCFg",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "OVC",
  "tr_key": "NQU23   "
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "OVC",
  "tr_key": "NQU23   "
 },
 "body": {
  "symbol": "NQU23",
  "chgrate": "-0.31",
  "kordate": "20230622",
  "trdtm": "001640",
  "curpr": "0. 14997.75",
  "ovsdate": "20230622",
  "mdvolume": "",
  "ydiffpr": "0.    46.25",
  "totq": "28064",
  "high": "0. 15058.00",
  "ydiffSign": "5",
  "low": "0. 14988.25",
  "msvolume": "",
  "cgubun": "-",
  "trdq": "1",
  "open": "0. 15038.75",
  "kortm": "141640"
 }
}
```

---

<a id="tr-OVH"></a>
## `OVH` 해외선물 호가

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
| `symbol` | 종목코드 | String | Y | 8 | - |
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가 1 | String | Y | 15.9 | - |
| `bidho1` | 매수호가 1 | String | Y | 15.9 | - |
| `offerrem1` | 매도호가 잔량 1 | String | Y | 10 | - |
| `bidrem1` | 매수호가 잔량 1 | String | Y | 10 | - |
| `offerno1` | 매도호가 건수 1 | String | Y | 10 | - |
| `bidno1` | 매수호가 건수 1 | String | Y | 10 | - |
| `offerho2` | 매도호가 2 | String | Y | 15.9 | - |
| `bidho2` | 매수호가 2 | String | Y | 15.9 | - |
| `offerrem2` | 매도호가 잔량 2 | String | Y | 10 | - |
| `bidrem2` | 매수호가 잔량 2 | String | Y | 10 | - |
| `offerno2` | 매도호가 건수 2 | String | Y | 10 | - |
| `bidno2` | 매수호가 건수 2 | String | Y | 10 | - |
| `offerho3` | 매도호가 3 | String | Y | 15.9 | - |
| `bidho3` | 매수호가 3 | String | Y | 15.9 | - |
| `offerrem3` | 매도호가 잔량 3 | String | Y | 10 | - |
| `bidrem3` | 매수호가 잔량 3 | String | Y | 10 | - |
| `offerno3` | 매도호가 건수 3 | String | Y | 10 | - |
| `bidno3` | 매수호가 건수 3 | String | Y | 10 | - |
| `offerho4` | 매도호가 4 | String | Y | 15.9 | - |
| `bidho4` | 매수호가 4 | String | Y | 15.9 | - |
| `offerrem4` | 매도호가 잔량 4 | String | Y | 10 | - |
| `bidrem4` | 매수호가 잔량 4 | String | Y | 10 | - |
| `offerno4` | 매도호가 건수 4 | String | Y | 10 | - |
| `bidno4` | 매수호가 건수 4 | String | Y | 10 | - |
| `offerho5` | 매도호가 5 | String | Y | 15.9 | - |
| `bidho5` | 매수호가 5 | String | Y | 15.9 | - |
| `offerrem5` | 매도호가 잔량 5 | String | Y | 10 | - |
| `bidrem5` | 매수호가 잔량 5 | String | Y | 10 | - |
| `offerno5` | 매도호가 건수 5 | String | Y | 10 | - |
| `bidno5` | 매수호가 건수 5 | String | Y | 10 | - |
| `totoffercnt` | 매도호가총건수 | String | Y | 10 | - |
| `totbidcnt` | 매수호가총건수 | String | Y | 10 | - |
| `totofferrem` | 매도호가총수량 | String | Y | 10 | - |
| `totbidrem` | 매수호가총수량 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjBmYTRhNmE1LWYwMzMtNGEyZS04MjgyLTE3MTdmOGRkN2EzZiIsIm5iZiI6MTY4Njc4Mjg2NSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2ODY2Mzk5LCJpYXQiOjE2ODY3ODI4NjUsImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.e2T7dj3jYedMsM8nd2FPr2OF8ZRxUwzqBNGgxwamMCa1PAx4oqjOuCdmKLs7oZfL9OICQ4AAA5_ceDulGBGCFg",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "OVH",
  "tr_key": "NQU23   "
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "OVH",
  "tr_key": "NQU23   "
 },
 "body": {
  "offerrem2": "6",
  "offerho4": "0. 14999.00",
  "bidho5": "0. 14996.75",
  "symbol": "NQU23",
  "offerho3": "0. 14998.75",
  "offerrem3": "5",
  "bidho4": "0. 14997.00",
  "bidno1": "3",
  "offerrem4": "8",
  "offerho5": "0. 14999.25",
  "offerrem5": "7",
  "offerno2": "6",
  "bidno3": "5",
  "offerno1": "2",
  "bidno2": "3",
  "offerno4": "4",
  "bidno5": "3",
  "offerrem1": "2",
  "offerno3": "5",
  "bidno4": "5",
  "offerno5": "6",
  "totoffercnt": "23",
  "totbidcnt": "19",
  "bidrem3": "5",
  "bidrem4": "5",
  "bidrem1": "3",
  "bidrem2": "3",
  "bidho1": "0. 14997.75",
  "hotime": "001642",
  "offerho2": "0. 14998.50",
  "bidho3": "0. 14997.25",
  "bidrem5": "3",
  "offerho1": "0. 14998.25",
  "bidho2": "0. 14997.50",
  "totofferrem": "28",
  "totbidrem": "19"
 }
}
```

---

<a id="tr-WOC"></a>
## `WOC` 해외옵션 체결

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
| `symbol` | 종목코드 | String | Y | 16 | - |
| `ovsdate` | 체결일자(현지) | String | Y | 8 | - |
| `kordate` | 체결일자(한국) | String | Y | 8 | - |
| `trdtm` | 체결시간(현지) | String | Y | 6 | - |
| `kortm` | 체결시간(한국) | String | Y | 6 | - |
| `curpr` | 체결가격 | String | Y | 15.9 | - |
| `ydiffpr` | 전일대비 | String | Y | 15.9 | - |
| `ydiffSign` | 전일대비기호 | String | Y | 1 | - |
| `open` | 시가 | String | Y | 15.9 | - |
| `high` | 고가 | String | Y | 15.9 | - |
| `low` | 저가 | String | Y | 15.9 | - |
| `chgrate` | 등락율 | String | Y | 6.2 | - |
| `trdq` | 건별체결수량 | String | Y | 10 | - |
| `totq` | 누적체결수량 | String | Y | 15 | - |
| `cgubun` | 체결구분 | String | Y | 1 | - |
| `mdvolume` | 매도누적체결수량 | String | Y | 15 | - |
| `msvolume` | 매수누적체결수량 | String | Y | 15 | - |
| `ovsmkend` | 장마감일 | String | Y | 8 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImRmYzQ2NThiLTQ3NmItNGQ4MS05OGM3LTI3NzlmNDhjMGZkZiIsIm5iZiI6MTY4NzM5MTEwOSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg3NDcxMTk5LCJpYXQiOjE2ODczOTExMDksImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.mZK8YsM8NNT-5-1Q7uPi1Xjnx9J-P_eRgn2fHCpMtT5CaXK7fu94xeR5iMGqhhTCW3W08IUUG0ixH01IOULtkg",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "WOC",
  "tr_key": "2ESU23_4400     "
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "WOC",
  "tr_key": "2ESU23_4400     "
 },
 "body": {
  "symbol": "2ESU23_4400     ",
  "chgrate": "107..0",
  "kordate": "0230622",
  "trdtm": "023062",
  "curpr": "15590.1",
  "ovsdate": "00",
  "mdvolume": "15 +",
  "ydiffpr": "107.00",
  "totq": "13？",
  "high": "111.25",
  "ydiffSign": "",
  "low": "111.25",
  "msvolume": "",
  "cgubun": "",
  "trdq": "-4.68",
  "open": "5.25？5",
  "kortm": "01590"
 }
}
```

---

<a id="tr-WOH"></a>
## `WOH` 해외옵션 호가

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
| `symbol` | 종목코드 | String | Y | 16 | - |
| `hotime` | 호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가 1 | String | Y | 15.9 | - |
| `bidho1` | 매수호가 1 | String | Y | 15.9 | - |
| `offerrem1` | 매도호가 잔량 1 | String | Y | 10 | - |
| `bidrem1` | 매수호가 잔량 1 | String | Y | 10 | - |
| `offerno1` | 매도호가 건수 1 | String | Y | 10 | - |
| `bidno1` | 매수호가 건수 1 | String | Y | 10 | - |
| `offerho2` | 매도호가 2 | String | Y | 15.9 | - |
| `bidho2` | 매수호가 2 | String | Y | 15.9 | - |
| `offerrem2` | 매도호가 잔량 2 | String | Y | 10 | - |
| `bidrem2` | 매수호가 잔량 2 | String | Y | 10 | - |
| `offerno2` | 매도호가 건수 2 | String | Y | 10 | - |
| `bidno2` | 매수호가 건수 2 | String | Y | 10 | - |
| `offerho3` | 매도호가 3 | String | Y | 15.9 | - |
| `bidho3` | 매수호가 3 | String | Y | 15.9 | - |
| `offerrem3` | 매도호가 잔량 3 | String | Y | 10 | - |
| `bidrem3` | 매수호가 잔량 3 | String | Y | 10 | - |
| `offerno3` | 매도호가 건수 3 | String | Y | 10 | - |
| `bidno3` | 매수호가 건수 3 | String | Y | 10 | - |
| `offerho4` | 매도호가 4 | String | Y | 15.9 | - |
| `bidho4` | 매수호가 4 | String | Y | 15.9 | - |
| `offerrem4` | 매도호가 잔량 4 | String | Y | 10 | - |
| `bidrem4` | 매수호가 잔량 4 | String | Y | 10 | - |
| `offerno4` | 매도호가 건수 4 | String | Y | 10 | - |
| `bidno4` | 매수호가 건수 4 | String | Y | 10 | - |
| `offerho5` | 매도호가 5 | String | Y | 15.9 | - |
| `bidho5` | 매수호가 5 | String | Y | 15.9 | - |
| `offerrem5` | 매도호가 잔량 5 | String | Y | 10 | - |
| `bidrem5` | 매수호가 잔량 5 | String | Y | 10 | - |
| `offerno5` | 매도호가 건수 5 | String | Y | 10 | - |
| `bidno5` | 매수호가 건수 5 | String | Y | 10 | - |
| `totoffercnt` | 매도호가총건수 | String | Y | 10 | - |
| `totbidcnt` | 매수호가총건수 | String | Y | 10 | - |
| `totofferrem` | 매도호가총수량 | String | Y | 10 | - |
| `totbidrem` | 매수호가총수량 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6ImRmYzQ2NThiLTQ3NmItNGQ4MS05OGM3LTI3NzlmNDhjMGZkZiIsIm5iZiI6MTY4NzM5MTEwOSwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg3NDcxMTk5LCJpYXQiOjE2ODczOTExMDksImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.mZK8YsM8NNT-5-1Q7uPi1Xjnx9J-P_eRgn2fHCpMtT5CaXK7fu94xeR5iMGqhhTCW3W08IUUG0ixH01IOULtkg",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "WOH",
  "tr_key": "2ESU23_4400     "
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "WOH",
  "tr_key": "2ESU23_4"
 },
 "body": {
  "offerrem2": "107.75？00",
  "offerho4": "0.1",
  "bidho5": "0.00",
  "symbol": "400     2ESU23_4",
  "offerho3": "0.2",
  "offerrem3": "90.00？00",
  "bidho4": "0.00",
  "bidno1": "1 00",
  "offerrem4": ".00？00",
  "offerho5": "0.0",
  "offerrem5": ".00？00",
  "offerno2": "50 00",
  "bidno3": "2 00",
  "offerno1": "19 00",
  "bidno2": "3 00",
  "offerno4": "0",
  "bidno5": "0",
  "offerrem1": "108.00？00",
  "offerno3": "1 00",
  "bidno4": "0",
  "offerno5": "0",
  "totoffercnt": "0",
  "totbidcnt": "6 00",
  "bidrem3": "48 00",
  "bidrem4": "0",
  "bidrem1": "13 00",
  "bidrem2": "6 00",
  "bidho1": "108.75",
  "hotime": "00",
  "offerho2": "0.4",
  "bidho3": "109.25",
  "bidrem5": "0",
  "offerho1": "354.0",
  "bidho2": "109.00",
  "totofferrem": "7 00",
  "totbidrem": "67 00"
 }
}
```

---

<a id="tr-TC1"></a>
## `TC1` 해외선물 주문접수

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
| `key` | KEY | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `svc_id` | 서비스ID | String | Y | 4 | HO01:주문ACK<br/>HO04:주문Pending |
| `ordr_dt` | 주문일자 | String | Y | 8 | - |
| `brn_cd` | 지점번호 | String | Y | 3 | - |
| `ordr_no` | 주문번호 | String | Y | 10 | - |
| `orgn_ordr_no` | 원주문번호 | String | Y | 10 | - |
| `mthr_ordr_no` | 모주문번호 | String | Y | 10 | - |
| `ac_no` | 계좌번호 | String | Y | 11 | - |
| `is_cd` | 종목코드 | String | Y | 30 | - |
| `s_b_ccd` | 매도매수유형 | String | Y | 1 | 1:매도<br/>2:매수 |
| `ordr_ccd` | 정정취소유형 | String | Y | 1 | 1:신규<br/>2:정정<br/>3:취소 |
| `ordr_typ_cd` | 주문유형코드 | String | Y | 1 | 1:시장가<br/>2:지정가<br/>3:Stop Market<br/>4:Stop Limit |
| `ordr_typ_prd_ccd` | 주문기간코드 | String | Y | 2 | 01:일반<br/>02:Average<br/>03:Spread |
| `ordr_aplc_strt_dt` | 주문적용시작일자 | String | Y | 8 | - |
| `ordr_aplc_end_dt` | 주문적용종료일자 | String | Y | 8 | - |
| `ordr_prc` | 주문가격 | String | Y | 18.11 | - |
| `cndt_ordr_prc` | 주문조건가격 | String | Y | 18.11 | - |
| `ordr_q` | 주문수량 | String | Y | 12 | - |
| `ordr_tm` | 주문시간 | String | Y | 9 | - |
| `userid` | 사용자ID | String | Y | 8 | - |
| `xrc_rsv_tp_code` | 행사예약구분코드 | String | Y | 1 | 1: 옵션행사예약<br/>0: 옵션행사예약아님 |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjljZWVkOWI3LTk4MTgtNDIwNi1hNmM3LTU1NjZiOWE0NWFjYyIsIm5iZiI6MTY4NjYzMjY5MywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzE5MDkzLCJpYXQiOjE2ODY2MzI2OTMsImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.l4l_wi59UXOBE_lZTL2wOSx40S_fIFdkHzBsK5ksMZ38LZGgy-MVl5onWCZg8-VaoGZIeClSj-8s2Tzs_gRDYQ",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "TC1",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "TC1"
 },
 "body": {
  "lineseq": " ",
  "s_b_ccd": "1",
  "ordr_typ_prd_ccd": "01",
  "is_cd": "ADM23",
  "ordr_dt": "20230609",
  "orgn_ordr_no": "0",
  "svc_id": "HO01",
  "ordr_aplc_strt_dt": "",
  "brn_cd": "000",
  "ordr_ccd": "1",
  "mthr_ordr_no": "34",
  "ac_no": "20629783903",
  "user": "qzvjaf",
  "ordr_no": "34",
  "ordr_typ_cd": "2",
  "key": "20629783903"
 }
}
```

---

<a id="tr-TC2"></a>
## `TC2` 해외선물 주문응답

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
| `key` | KEY | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `svc_id` | 서비스ID | String | Y | 4 | HO02:확인<br/>HO03:거부 |
| `ordr_dt` | 주문일자 | String | Y | 8 | - |
| `brn_cd` | 지점번호 | String | Y | 3 | - |
| `ordr_no` | 주문번호 | String | Y | 10 | - |
| `orgn_ordr_no` | 원주문번호 | String | Y | 10 | - |
| `mthr_ordr_no` | 모주문번호 | String | Y | 10 | - |
| `ac_no` | 계좌번호 | String | Y | 11 | - |
| `is_cd` | 종목코드 | String | Y | 30 | - |
| `s_b_ccd` | 매도매수유형 | String | Y | 1 | 1:매도<br/>2:매수 |
| `ordr_ccd` | 정정취소유형 | String | Y | 1 | 1:신규<br/>2:정정<br/>3:취소 |
| `ordr_typ_cd` | 주문유형코드 | String | Y | 1 | 1:시장가<br/>2:지정가<br/>3:Stop Market<br/>4:Stop Limit |
| `ordr_typ_prd_ccd` | 주문기간코드 | String | Y | 2 | 01:일반<br/>02:Average<br/>03:Spread |
| `ordr_aplc_strt_dt` | 주문적용시작일자 | String | Y | 8 | - |
| `ordr_aplc_end_dt` | 주문적용종료일자 | String | Y | 8 | - |
| `ordr_prc` | 주문가격 | String | Y | 18.11 | - |
| `cndt_ordr_prc` | 주문조건가격 | String | Y | 18.11 | - |
| `ordr_q` | 주문수량 | String | Y | 12 | - |
| `ordr_tm` | 주문시간 | String | Y | 9 | - |
| `cnfr_q` | 호가확인수량 | String | Y | 12 | - |
| `rfsl_cd` | 호가거부사유코드 | String | Y | 4 | - |
| `text` | 호가거부사유코드명 | String | Y | 80 | - |
| `userid` | 사용자ID | String | Y | 8 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjljZWVkOWI3LTk4MTgtNDIwNi1hNmM3LTU1NjZiOWE0NWFjYyIsIm5iZiI6MTY4NjYzMjY5MywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzE5MDkzLCJpYXQiOjE2ODY2MzI2OTMsImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.l4l_wi59UXOBE_lZTL2wOSx40S_fIFdkHzBsK5ksMZ38LZGgy-MVl5onWCZg8-VaoGZIeClSj-8s2Tzs_gRDYQ",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "TC2",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "TC2"
 },
 "body": {
  "lineseq": " ",
  "s_b_ccd": "1",
  "ordr_typ_prd_ccd": "01",
  "is_cd": "ADM23",
  "ordr_dt": "20230614",
  "orgn_ordr_no": "29",
  "svc_id": "HO02",
  "ordr_aplc_strt_dt": "",
  "brn_cd": "000",
  "ordr_ccd": "2",
  "mthr_ordr_no": "29",
  "ac_no": "20629783903",
  "user": "qzvjaf",
  "ordr_no": "30",
  "ordr_typ_cd": "2",
  "key": "20629783903"
 }
}
```

---

<a id="tr-TC3"></a>
## `TC3` 해외선물 주문체결

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
| `key` | KEY | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `svc_id` | 서비스ID | String | Y | 4 | CH01 |
| `ordr_dt` | 주문일자 | String | Y | 8 | - |
| `brn_cd` | 지점번호 | String | Y | 3 | - |
| `ordr_no` | 주문번호 | String | Y | 10 | - |
| `orgn_ordr_no` | 원주문번호 | String | Y | 10 | - |
| `mthr_ordr_no` | 모주문번호 | String | Y | 10 | - |
| `ac_no` | 계좌번호 | String | Y | 11 | - |
| `is_cd` | 종목코드 | String | Y | 30 | - |
| `s_b_ccd` | 매도매수유형 | String | Y | 1 | 1:매도<br/>2:매수 |
| `ordr_ccd` | 정정취소유형 | String | Y | 1 | 1:신규<br/>2:정정<br/>3:취소 |
| `ccls_q` | 체결수량 | String | Y | 15 | - |
| `ccls_prc` | 체결가격 | String | Y | 18.11 | - |
| `ccls_no` | 체결번호 | String | Y | 10 | - |
| `ccls_tm` | 체결시간 | String | Y | 9 | - |
| `avg_byng_uprc` | 매입평균단가 | String | Y | 18.11 | - |
| `byug_amt` | 매입금액 | String | Y | 25.8 | - |
| `clr_pl_amt` | 청산손익 | String | Y | 19.2 | - |
| `ent_fee` | 위탁수수료 | String | Y | 19.2 | - |
| `fcm_fee` | 매입잔고수량 | String | Y | 19 | - |
| `userid` | 사용자ID | String | Y | 8 | - |
| `now_prc` | 현재가격 | String | Y | 18.11 | - |
| `crncy_cd` | 통화코드 | String | Y | 3 | - |
| `mtrt_dt` | 만기일자 | String | Y | 8 | - |
| `ord_prdt_tp_code` | 주문상품구분코드 | String | Y | 1 | - |
| `exec_prdt_tp_code` | 주문상품구분코드 | String | Y | 1 | - |
| `sprd_base_isu_yn` | 스프레드종목여부 | String | Y | 1 | - |
| `ccls_dt` | 체결일자 | String | Y | 8 | - |
| `filler2` | FILLER2 | String | Y | 30 | - |
| `sprd_is_cd` | 스프레드종목코드 | String | Y | 30 | - |
| `lme_prdt_ccd` | LME상품유형 | String | Y | 1 | 1:LME(월물상품)<br/>2:LME(3M상품)<br/>0:LME외 |
| `lme_sprd_prc` | LME스프레드가격 | String | Y | 18.11 | - |
| `last_now_prc` | 최종현재가격 | String | Y | 18.11 | - |
| `bf_mtrt_dt` | 이전만기일자 | String | Y | 8 | - |
| `clr_q` | 청산수량 | String | Y | 15 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjljZWVkOWI3LTk4MTgtNDIwNi1hNmM3LTU1NjZiOWE0NWFjYyIsIm5iZiI6MTY4NjYzMjY5MywiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzE5MDkzLCJpYXQiOjE2ODY2MzI2OTMsImp0aSI6IlBTMzA3em5Jd2ZMSWxXR1Bhbm1SN2ZtMzl2NXRDbWYydWFPWCJ9.l4l_wi59UXOBE_lZTL2wOSx40S_fIFdkHzBsK5ksMZ38LZGgy-MVl5onWCZg8-VaoGZIeClSj-8s2Tzs_gRDYQ",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "TC3",
  "tr_key": ""
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "TC3"
 },
 "body": {
  "s_b_ccd": "1",
  "sprd_base_isu_yn": "",
  "ordr_dt": "20230613",
  "ccls_q": "1",
  "filler1": "20230613",
  "userid": "qzvjaf",
  "fcm_fee": "5",
  "filler2": "",
  "mtrt_dt": "20230616",
  "brn_cd": "202",
  "exec_prdt_tp_code": "F",
  "sprd_is_cd": "",
  "ordr_no": "34",
  "key": "20629783903",
  "lineseq": " ",
  "avg_byng_uprc": "73.46995000000",
  "ord_prdt_tp_code": "F",
  "ccls_prc": "122.00000000000",
  "clr_pl_amt": "0.00",
  "now_prc": "0.67630000000",
  "is_cd": "ADM23",
  "ent_fee": "7.50",
  "orgn_ordr_no": " ",
  "svc_id": "CH01",
  "crncy_cd": "USD",
  "ccls_tm": "144220250",
  "ordr_ccd": "1",
  "byug_amt": "36734975.00000000",
  "mthr_ordr_no": "34",
  "ccls_no": "0000000029",
  "ac_no": "20629783903",
  "user": "qzvjaf"
 }
}
```
