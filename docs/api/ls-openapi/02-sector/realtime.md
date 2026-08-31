# [업종] 실시간 시세

> LS증권 OPEN API 정의서 · 그룹: **업종** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=f82999f4-eb1a-4ead-a0b1-a4386e8721ab&api_id=3c2b0280-6663-41e2-8995-a179de99e074)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `3c2b0280-6663-41e2-8995-a179de99e074` |
| Protocol | WEBSOCKET |
| Method | POST |
| Domain | `wss://openapi.ls-sec.co.kr:9443` |
| URL | `/websocket/indtp` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 업종 관련 정보를 실시간으로 확인할 수 있습니다. |

## TR 목록 (1건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 업종별투자자별매매현황 | [BM_](realtime.md#tr-BM_) | - | - | - |

> **WebSocket 실시간 데이터**: 접속 도메인은 위 `Domain`(`wss://`)을 사용합니다.
> 접속 시 Header에 발급받은 `token`(접근토큰)을 설정하고, 각 TR 아래의 패킷 구조로 등록/해제(`tr_type`: 1 계좌등록, 2 계좌해제, 3 실시간 시세 등록, 4 실시간 시세 해제) 요청을 보냅니다. 실제 데이터는 동일 채널로 push 수신합니다.

---

<a id="tr-BM_"></a>
## `BM_` 업종별투자자별매매현황

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 3 | 001 : 코스피<br/>101 : KP200<br/>301 : 코스닥<br/>550 : ELW<br/>560 : ETF<br/>600 : 주식선물<br/>700 : 콜옵션<br/>800 : 풋옵션<br/>900 : 선물<br/>940 : 미니KP200선물<br/>941 : 미니KP200옵션-콜<br/>942 : 미니KP200옵션-풋<br/>946 : 코스피200위클리-콜<br/>947 : 코스피200위클리-풋 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tjjcode` | 투자자코드 | String | Y | 4 | 001:코스피<br/>101:KP200<br/>301:코스닥<br/>900:선 물<br/>700:콜옵션<br/>800:풋옵션<br/>550:ELW<br/>560:ETF |
| `tjjtime` | 수신시간 | String | Y | 8 | - |
| `msvolume` | 매수거래량 | String | Y | 8 | - |
| `mdvolume` | 매도거래량 | String | Y | 8 | - |
| `msvol` | 거래량순매수 | String | Y | 8 | - |
| `p_msvol` | 거래량순매수직전대비 | String | Y | 8 | - |
| `msvalue` | 매수거래대금 | String | Y | 6 | - |
| `mdvalue` | 매도거래대금 | String | Y | 6 | - |
| `msval` | 거래대금순매수 | String | Y | 6 | - |
| `p_msval` | 거래대금순매수직전대비 | String | Y | 6 | - |
| `upcode` | 업종코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ0b2tlbiIsImF1ZCI6IjY2NDVmOGU0LTRkYzEtNDk4ZS05MjEzLTJlYTU5YjNmYjk2MyIsIm5iZiI6MTY4NjY5NjA3MCwiZ3JhbnRfdHlwZSI6IkNsaWVudCIsImlzcyI6InVub2d3IiwiZXhwIjoxNjg2NzgyNDcwLCJpYXQiOjE2ODY2OTYwNzAsImp0aSI6IlBTRU1CcWF5Q1N6QmxnTjZ3SlRkUTV5dkRNdjllWjlNZWJ2UCJ9.0roE4en_J2M3PDFr8xrZK4l0pw4uz5-kIc7I_w-E2gXlfMvIdIYqTn3LH_kr-V_iOhiOU-dLRrRbbavzNHJX3Q",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "BM_",
  "tr_key": "001"
 }
}
```

### 응답 Example

```json
{
 "header": {
  "tr_cd": "BM_",
  "tr_key": "001"
 },
 "body": {
  "p_msval": "21",
  "tjjtime": "09510000",
  "p_msvol": "123",
  "mdvalue": "54037",
  "msvolume": "236487",
  "upcode": "001",
  "tjjcode": "9999",
  "msvalue": "53764",
  "mdvolume": "241626",
  "msvol": "-5139",
  "msval": "-273"
 }
}
```
