# [주식] 프로그램

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=6b554636-7b2a-4e1a-a615-54b0c131a558)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `6b554636-7b2a-4e1a-a615-54b0c131a558` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/program` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 프로그램매매 추이에 관한 정보를 확인할 수 있습니다. |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 프로그램매매종합조회 | [t1631](program-trading.md#tr-t1631) | 1 | 1 | 3 |
| 시간대별프로그램매매추이 | [t1632](program-trading.md#tr-t1632) | 1 | 1 | 3 |
| 기간별프로그램매매추이 | [t1633](program-trading.md#tr-t1633) | 1 | 1 | 3 |
| 종목별프로그램매매동향 | [t1636](program-trading.md#tr-t1636) | 1 | 1 | 3 |
| 종목별프로그램매매추이 | [t1637](program-trading.md#tr-t1637) | 1 | 1 | 3 |
| 프로그램매매종합조회(미니) | [t1640](program-trading.md#tr-t1640) | 1 | 1 | 3 |
| 시간대별프로그램매매추이(차트) | [t1662](program-trading.md#tr-t1662) | 1 | 1 | 3 |

---

<a id="tr-t1631"></a>
## `t1631` 프로그램매매종합조회

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
| `t1631InBlock` | t1631InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 1:거래소<br/>2:코스닥 |
| `&nbsp;&nbsp;-dgubun` | 일자구분 | String | Y | 1 | 1:당일조회<br/>2:기간조회 |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
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
| `t1631OutBlock` | t1631OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cdhrem` | 매도차익미체결잔량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bdhrem` | 매도비차익미체결잔량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tcdrem` | 매도차익주문수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tbdrem` | 매도비차익주문수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cshrem` | 매수차익미체결잔량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bshrem` | 매수비차익미체결잔량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tcsrem` | 매수차익주문수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tbsrem` | 매수비차익주문수량 | Number | Y | 8 | - |
| `t1631OutBlock1` | t1631OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-offervolume` | 매도수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offervalue` | 매도금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidvolume` | 매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidvalue` | 매수금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volume` | 순매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-value` | 순매수금액 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1631InBlock" : {
    "gubun" : "1",
    "dgubun" : "1",
    "sdate" : "",
    "edate" : ""
  }
}
```

### 응답 Example

```json
{
    "t1631OutBlock1": [
        {
            "bidvolume": 102,
            "volume": 99,
            "bidvalue": 6919,
            "offervalue": 479,
            "value": 6440,
            "offervolume": 3
        },
        {
            "bidvolume": 0,
            "volume": 0,
            "bidvalue": 1,
            "offervalue": 1,
            "value": 1,
            "offervolume": 0
        },
        {
            "bidvolume": 102,
            "volume": 99,
            "bidvalue": 6921,
            "offervalue": 480,
            "value": 6441,
            "offervolume": 3
        }
    ],
    "rsp_cd": "00000",
    "t1631OutBlock": {
        "tcdrem": 0,
        "cdhrem": 0,
        "tbdrem": 5,
        "bshrem": 149,
        "cshrem": 0,
        "tbsrem": 251,
        "bdhrem": 2,
        "tcsrem": 0
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1632"></a>
## `t1632` 시간대별프로그램매매추이

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
| `t1632InBlock` | t1632InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0@거래소<br/>1@코스닥 |
| `&nbsp;&nbsp;-gubun1` | 금액수량구분 | String | Y | 1 | 0:금액<br/>1:수량 |
| `&nbsp;&nbsp;-gubun2` | 직전대비증감 | String | Y | 1 | 1:직전대비증감 |
| `&nbsp;&nbsp;-gubun3` | 전일구분 | String | Y | 1 | 1:전일분 |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 date 값으로 설정 |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 time 값으로 설정 |
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
| `t1632OutBlock` | t1632OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜CTS | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간CTS | String | Y | 6 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `&nbsp;&nbsp;-ex_gubun` | 거래소별구분코드 | String | Y | 2 | - |
| `t1632OutBlock1` | t1632OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-k200jisu` | KP200 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-k200basis` | BASIS | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-tot3` | 전체순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot1` | 전체매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot2` | 전체매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha3` | 차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha1` | 차익매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha2` | 차익매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha3` | 비차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha1` | 비차익매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha2` | 비차익매도 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1632InBlock" : {
    "gubun" : "0",
    "gubun1" : "0",
    "gubun2" : "1",
    "gubun3" : "1",
    "date" : " ",
    "time" : " " 
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1632OutBlock": {
        "date": "20230602",
        "time": "175811",
        "idx": 19
    },
    "t1632OutBlock1": [
        {
            "bcha1": 0,
            "change": "004.59",
            "sign": "2",
            "bcha3": 0,
            "bcha2": 0,
            "k200basis": "000.28",
            "tot3": 0,
            "tot1": 0,
            "tot2": 0,
            "cha2": 0,
            "cha3": 0,
            "time": "180518",
            "cha1": 0,
            "k200jisu": "342.67"
        },
        {
            "bcha1": 0,
            "change": "004.59",
            "sign": "2",
            "bcha3": 0,
            "bcha2": 0,
            "k200basis": "000.28",
            "tot3": 0,
            "tot1": 0,
            "tot2": 0,
            "cha2": 0,
            "cha3": 0,
            "time": "175928",
            "cha1": 0,
            "k200jisu": "342.67"
        }
    ]
}
```

---

<a id="tr-t1633"></a>
## `t1633` 기간별프로그램매매추이

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
| `t1633InBlock` | t1633InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-gubun` | 시장구분 | String | Y | 1 | 0@거래소<br/>1@코스닥 |
| `&nbsp;&nbsp;-gubun1` | 금액수량구분 | String | Y | 1 | 0:금액<br/>1:수량 |
| `&nbsp;&nbsp;-gubun2` | 수치누적구분 | String | Y | 1 | 0@수치<br/>1@누적 |
| `&nbsp;&nbsp;-gubun3` | 일주월구분 | String | Y | 1 | 1@일<br/>2@주<br/>3@월 |
| `&nbsp;&nbsp;-fdate` | from일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tdate` | to일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-gubun4` | 직전대비증감구분 | String | Y | 1 | 0:Default<br/>1:직전대비증감 |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 date 값으로 설정 |
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
| `t1633OutBlock` | t1633OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1633OutBlock1` | t1633OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jisu` | KP200 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-tot3` | 전체순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot1` | 전체매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot2` | 전체매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha3` | 차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha1` | 차익매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha2` | 차익매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha3` | 비차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha1` | 비차익매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha2` | 비차익매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1633InBlock" : {
    "gubun" : "0",
    "gubun1" : "0",
    "gubun2" : "0",
    "gubun3" : "1",
    "fdate" : "20230101",
    "tdate" : "20230619",
    "gubun4" : "0",
    "date" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1633OutBlock1": [
        {
            "date": "20230619",
            "bcha1": 6921,
            "change": "16.32",
            "sign": "2",
            "bcha3": 6441,
            "bcha2": 480,
            "tot3": 6441,
            "tot1": 6921,
            "tot2": 480,
            "jisu": "329.85",
            "volume": 245,
            "cha2": 0,
            "cha3": 0,
            "cha1": 0
        },
        {
            "date": "20230616",
            "bcha1": 808,
            "change": "1.98",
            "sign": "2",
            "bcha3": 282,
            "bcha2": 526,
            "tot3": 391,
            "tot1": 917,
            "tot2": 526,
            "jisu": "345.17",
            "volume": 153589,
            "cha2": 0,
            "cha3": 109,
            "cha1": 109
        }
    ],
    "t1633OutBlock": {
        "date": "20230102",
        "idx": 115
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1636"></a>
## `t1636` 종목별프로그램매매동향

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
| `t1636InBlock` | t1636InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:코스피<br/>1:코스닥 |
| `&nbsp;&nbsp;-gubun1` | 금액수량구분 | String | Y | 1 | 0:수량<br/>1:금액 |
| `&nbsp;&nbsp;-gubun2` | 정렬기준 | String | Y | 1 | 0:시가총액비중<br/>1:순매수상위<br/>2:순매도상위<br/>3:매도상위<br/>4:매수상위 |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_idx` | IDXCTS | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_idx 값으로 설정 |
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
| `t1636OutBlock` | t1636OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-cts_idx` | IDXCTS | Number | Y | 4 | - |
| `t1636OutBlock1` | t1636OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-rank` | 순위 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svalue` | 순매수금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offervalue` | 매도금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stksvalue` | 매수금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume` | 순매수수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offervolume` | 매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stksvolume` | 매수수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sgta` | 시가총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-rate` | 비중 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-mkcap_cmpr_val` | 시총대비순매수비중 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1636InBlock" : {
    "gubun":"0",
    "gubun1":"0",
    "gubun2":"0",
    "shcode":"001200",
    "cts_idx": 0
  }
}
```

### 응답 Example

```json
{
    "t1636OutBlock": {
        "cts_idx": 312
    },
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1636OutBlock1": [
        {
            "stksvalue": 0,
            "change": 25,
            "shcode": "001200",
            "sign": "2",
            "diff": "0.68",
            "offervalue": 0,
            "offervolume": 74893,
            "volume": 322192,
            "sgta": 356952750330,
            "rate": "000.02",
            "price": 3685,
            "stksvolume": 124828,
            "svalue": 0,
            "rank": 293,
            "svolume": 49935,
            "hname": "유진투자증권"
        },
        {
            "stksvalue": 0,
            "change": 20,
            "shcode": "003610",
            "sign": "5",
            "diff": "-0.27",
            "offervalue": 0,
            "offervolume": 1532,
            "volume": 76162,
            "sgta": 311431702400,
            "rate": "000.02",
            "price": 7360,
            "stksvolume": 7949,
            "svalue": 0,
            "rank": 312,
            "svolume": 6417,
            "hname": "방림"
        }
    ]
}
```

---

<a id="tr-t1637"></a>
## `t1637` 종목별프로그램매매추이

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
| `t1637InBlock` | t1637InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 수량금액구분(0:수량1:금액) | String | Y | 1 | - |
| `&nbsp;&nbsp;-gubun2` | 시간일별구분(0:시간1:일자) | String | Y | 1 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | 일별 연속 조회시에 이전 조회한 OutBlock1의 마지막 Row의 date 값으로 설정 |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | 시간별 연속 조회시에 이전 조회한 OutBlock1의 마지막 Row의 time 값으로 설정 |
| `&nbsp;&nbsp;-cts_idx` | IDXCTS(9999:차트) | Number | Y | 4 | 차트 조회시에만 9999로 입력 |
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
| `t1637OutBlock` | t1637OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_idx` | IDXCTS | Number | Y | 4 | - |
| `t1637OutBlock1` | t1637OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svalue` | 순매수금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-offervalue` | 매도금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-stksvalue` | 매수금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-svolume` | 순매수수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offervolume` | 매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stksvolume` | 매수수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
  "t1637InBlock" : {
    "gubun1" : "0",
    "gubun2" : "0",
    "shcode" : "001200",
    "date" : "",
    "time" : "",
    "cts_idx" : 9999
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1637OutBlock": {
        "cts_idx": 0
    },
    "t1637OutBlock1": [
        {
            "date": "20230605",
            "stksvalue": 0,
            "change": 0,
            "shcode": "A00120",
            "sign": "",
            "diff": "0",
            "offervalue": 0,
            "offervolume": 0,
            "volume": 0,
            "price": 3685,
            "stksvolume": 0,
            "svalue": 188914,
            "svolume": 49935,
            "time": "102700"
        },
        {
            "date": "20230605",
            "stksvalue": 0,
            "change": 0,
            "shcode": "A00120",
            "sign": "",
            "diff": "0",
            "offervalue": 0,
            "offervolume": 0,
            "volume": 0,
            "price": 3645,
            "stksvolume": 0,
            "svalue": -74311,
            "svolume": -20307,
            "time": "090100"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1640"></a>
## `t1640` 프로그램매매종합조회(미니)

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
| `t1640InBlock` | t1640InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 2 | 11@거래소전체<br/>12@거래소차익<br/>13@거래소비차익<br/>21@코스닥전체<br/>22@코스닥차익<br/>23@코스닥비차익 |
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
| `t1640OutBlock` | t1640OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-offervolume` | 매도수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidvolume` | 매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 순매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerdiff` | 매도증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-biddiff` | 매수증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sundiff` | 순매수증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-basis` | 베이시스 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offervalue` | 매도금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidvalue` | 매수금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 순매수금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offervaldiff` | 매도금액증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidvaldiff` | 매수금액증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sunvaldiff` | 순매수증감 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1640InBlock" : {
    "gubun" : "11"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "조회완료",
    "t1640OutBlock": {
        "sundiff": 6,
        "bidvaldiff": "000000000250",
        "bidvalue": "000000786684",
        "offervalue": "000000758788",
        "basis": "000.01",
        "offervolume": 36452,
        "offerdiff": 10,
        "bidvolume": 39833,
        "volume": 3381,
        "sunvaldiff": "-00000000100",
        "biddiff": 16,
        "value": "000000027896",
        "offervaldiff": "000000000350"
    }
}
```

---

<a id="tr-t1662"></a>
## `t1662` 시간대별프로그램매매추이(차트)

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
| `t1662InBlock` | t1662InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0@코스피<br/>1@코스닥 |
| `&nbsp;&nbsp;-gubun1` | 금액수량구분 | String | Y | 1 | 0:금액<br/>1:수량 |
| `&nbsp;&nbsp;-gubun3` | 전일구분 | String | Y | 1 | 0:당일<br/>1:전일 |
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
| `t1662OutBlock` | t1662OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-k200jisu` | KP200 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-k200basis` | BASIS | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-tot3` | 전체순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot1` | 전체매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot2` | 전체매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha3` | 차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha1` | 차익매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha2` | 차익매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha3` | 비차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha1` | 비차익매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcha2` | 비차익매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1662InBlock" : {
    "gubun" : "0",
    "gubun1" : "0",
    "gubun3" : "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1662OutBlock": [
        {
            "bcha1": 768966,
            "change": "001.08",
            "sign": "2",
            "bcha3": 15815,
            "bcha2": 753151,
            "k200basis": "000.27",
            "tot3": 27896,
            "tot1": 786684,
            "tot2": 758788,
            "volume": 24,
            "cha2": 5637,
            "cha3": 12081,
            "time": "102600",
            "cha1": 17718,
            "k200jisu": "343.75"
        },
        {
            "bcha1": 12327,
            "change": "000.00",
            "sign": "3",
            "bcha3": -7637,
            "bcha2": 19964,
            "k200basis": "002.08",
            "tot3": -7637,
            "tot1": 12327,
            "tot2": 19964,
            "volume": 0,
            "cha2": 0,
            "cha3": 0,
            "time": "090000",
            "cha1": 0,
            "k200jisu": "342.67"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
