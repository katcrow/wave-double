# [주식] 거래원

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=3dbce945-a73c-475c-9758-88d9922ab94e)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `3dbce945-a73c-475c-9758-88d9922ab94e` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/exchange` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 종목별 거래 회원사를 호출하여 거래원을 확인할 수 있습니다. |

## TR 목록 (3건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 종목별상위회원사 | [t1752](brokerage.md#tr-t1752) | 1 | 1 | 3 |
| 회원사리스트 | [t1764](brokerage.md#tr-t1764) | 1 | 1 | 3 |
| 종목별회원사추이 | [t1771](brokerage.md#tr-t1771) | 1 | 1 | 3 |

---

<a id="tr-t1752"></a>
## `t1752` 종목별상위회원사

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth 토큰이 필요한 API 경우 발급한 Access Token을 설정하기 위한 Request Heaeder Parameter |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |
| `mac_address` | MAC 주소 | String | Y | 12 | 법인인 경우 필수 세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t1752InBlock` | t1752InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-traddate1` | 조회날짜1 | String | Y | 8 | 기간 조회시 시작일(YYYYMMDD) |
| `&nbsp;&nbsp;-traddate2` | 조회날짜2 | String | Y | 8 | 기간 조회시 종료일(YYYYMMDD) |
| `&nbsp;&nbsp;-fwgubun1` | 외국계구분 | String | Y | 1 | 0 : 전체<br/>1 : 외국계 회원사만 조회 |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | OutBlock 동일필드 연속조회시 입력 |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t1752OutBlock` | t1752OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-fwdvl` | 외국계매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-fwsvl` | 외국계매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | - |
| `t1752OutBlock1` | t1752OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-tradname` | 회원사 | String | Y | 20 | - |
| `&nbsp;&nbsp;-tradmdvol` | 매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradmsvol` | 매수수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradmssvol` | 순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-wintrd` | 창구거래 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-winrat` | 비중 | Number | Y | 6.1 | - |
| `&nbsp;&nbsp;-tradno` | 회원사코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-wgubun` | 외국계여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-swinrat` | 순비중 | Number | Y | 6.1 | - |


### 요청 Example

```json
{
  "t1752InBlock" : {
    "shcode" : "005930",
    "traddate1" : "20230502",
    "traddate2" : "20230601",
    "fwgubun1" : "0",
    "cts_idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1752OutBlock1": [
        {
            "tradmdvol": 10485472,
            "tradmsvol": 18297639,
            "tradno": "033",
            "wgubun": "1",
            "swinrat": "27.0",
            "tradname": "JP모간",
            "winrat": "51.0",
            "wintrd": 28783111,
            "tradmssvol": 7812167
        },
        {
            "tradmdvol": 10025294,
            "tradmsvol": 9401013,
            "tradno": "021",
            "wgubun": "0",
            "swinrat": "-2.0",
            "tradname": "한화투자",
            "winrat": "34.0",
            "wintrd": 19426307,
            "tradmssvol": -624281
        }
    ],
    "t1752OutBlock": {
        "cts_idx": 40,
        "fwdvl": 65771261,
        "fwsvl": 94034201
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1764"></a>
## `t1764` 회원사리스트

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth 토큰이 필요한 API 경우 발급한 Access Token을 설정하기 위한 Request Heaeder Parameter |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |
| `mac_address` | MAC 주소 | String | Y | 12 | 법인인 경우 필수 세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t1764InBlock` | t1764InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun1` | 구분1 | String | Y | 1 | 0 or 1 : 전회원사조회 0,1 이외의 값 입력시 InBlock.shcode 종목으로 거래가 있는 회원사만 조회됨 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t1764OutBlock` | t1764OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-rank` | 순위 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-tradno` | 거래원번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-tradname` | 거래원이름 | String | Y | 20 | - |


### 요청 Example

```json
{
  "t1764InBlock" : {
    "shcode" : "001200",
    "gubun1" : "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1764OutBlock": [
        {
            "tradno": "000",
            "tradname": "외국계회원사전체",
            "rank": 0
        },
        {
            "tradno": "086",
            "tradname": "BNK 증권",
            "rank": 1
        },
        {
            "tradno": "067",
            "tradname": "BNP 파리바",
            "rank": 2
        },
        {
            "tradno": "066",
            "tradname": "흥국증권",
            "rank": 63
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1771"></a>
## `t1771` 종목별회원사추이

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth 토큰이 필요한 API 경우 발급한 Access Token을 설정하기 위한 Request Heaeder Parameter |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |
| `mac_address` | MAC 주소 | String | Y | 12 | 법인인 경우 필수 세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t1771InBlock` | t1771InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-tradno` | 거래원코드 | String | Y | 3 | 거래원코드<br/>t1764 를 조회한 후 t1764OutBlock 의 tradno 의 값을 사용 |
| `&nbsp;&nbsp;-gubun1` | 구분1 | String | Y | 1 | 0 : 시간별<br/>1 : 일별 |
| `&nbsp;&nbsp;-traddate1` | 거래원날짜1 | String | Y | 8 | 일별 조회시 사용<br/>OutBlock1.traddate >= InBlock.traddate1 |
| `&nbsp;&nbsp;-traddate2` | 거래원날짜2 | String | Y | 8 | 일별 조회시 사용<br/>OutBlock1.traddate <= InBlock.traddate2 |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | 처음 조회시 Space 입력<br/>다음 조회시 OutBlock의 cts_idx 값을 입력 |
| `&nbsp;&nbsp;-cnt` | 요청건수 | Object | Y | 3 | - |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t1771OutBlock` | t1771OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | - |
| `t1771OutBlock2` | t1771OutBlock2 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-traddate` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tradtime` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradmdcha` | 매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradmscha` | 매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradmdval` | 매도대금 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tradmsval` | 매수대금 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tradmsscha` | 순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradmttvolume` | 누적순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tradavg` | 평균단가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tradmttavg` | 누적평균단가 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t1771InBlock" : {
    "shcode" : "005930",
    "tradno" : "086",
    "gubun1" : "1",
    "traddate1" : "20230101",
    "traddate2" : "20230619",
    "cts_idx" : 0,
    "cnt" : 100
  }
}
```

### 응답 Example

```json
{
    "t1771OutBlock2": [
        {
            "tradtime": "",
            "tradmsval": 105447198900,
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "tradmscha": 1483138,
            "traddate": "20230619",
            "volume": 0,
            "tradavg": 71110,
            "tradmdval": 108970167900,
            "price": 65100,
            "tradmdcha": 1532140,
            "tradmsscha": -49002,
            "tradmttavg": 64759,
            "tradmttvolume": -1721142
        },
        {
            "tradtime": "",
            "tradmsval": 0,
            "change": 15000,
            "sign": "1",
            "diff": "2994.00",
            "tradmscha": 0,
            "traddate": "20230619",
            "volume": 205461,
            "tradavg": 0,
            "tradmdval": 0,
            "price": 65100,
            "tradmdcha": 0,
            "tradmsscha": 0,
            "tradmttavg": 64675,
            "tradmttvolume": -1672140
        }
    ],
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1771OutBlock": {
        "cts_idx": 100
    }
}
```
