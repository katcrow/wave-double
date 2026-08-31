# [주식] 상위종목

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=d3d0ef41-6a0f-4bda-9e28-160071f66206)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `d3d0ef41-6a0f-4bda-9e28-160071f66206` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/high-item` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 거래대금 및 등락율 등 항목별 상위데이터를 확인할 수 있는 서비스입니다. |

## TR 목록 (9건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 등락율상위 | [t1441](top-movers.md#tr-t1441) | 1 | 1 | 1 |
| 시가총액상위 | [t1444](top-movers.md#tr-t1444) | 2 | 2 | 3 |
| 거래량상위 | [t1452](top-movers.md#tr-t1452) | 2 | 2 | 3 |
| 거래대금상위 | [t1463](top-movers.md#tr-t1463) | 1 | 1 | 1 |
| 전일동시간대비거래급증 | [t1466](top-movers.md#tr-t1466) | 1 | 1 | 1 |
| 시간외등락율상위 | [t1481](top-movers.md#tr-t1481) | 1 | 1 | 1 |
| 시간외거래량상위 | [t1482](top-movers.md#tr-t1482) | 1 | 1 | 1 |
| 예상체결량상위조회 | [t1489](top-movers.md#tr-t1489) | 1 | 1 | 1 |
| 단일가예상등락율상위 | [t1492](top-movers.md#tr-t1492) | 1 | 1 | 1 |

---

<a id="tr-t1441"></a>
## `t1441` 등락율상위

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
| `t1441InBlock` | t1441InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 구분 | String | Y | 1 | 0:전체<br/>1:코스피<br/>2:코스닥 |
| `&nbsp;&nbsp;-gubun2` | 상승하락 | String | Y | 1 | 0: 상승률<br/>1: 하락률<br/>2: 보합 |
| `&nbsp;&nbsp;-gubun3` | 당일전일 | String | Y | 1 | 0: 당일<br/>1: 전일 |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값<br/>증거금50 : 0x00400000<br/>증거금100 : 0x00800000<br/>증거금50/100 : 0x00200000<br/>관리종목 : 0x00000080<br/>시장경보 : 0x00000100<br/>거래정지 : 0x00000200<br/>우선주 : 0x00004000<br/>투자유의 : 0x04000000<br/>정리매매 : 0x01000000<br/>불성실공시 : 0x80000000 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
| `&nbsp;&nbsp;-jc_num2` | 대상제외2 | Number | Y | 12 | 기본 => 000000000000<br/>상장지수펀드 => 000000000001<br/>선박투자회사 => 000000000002<br/>스펙 => 000000000004<br/>ETN => 000000000008(0x00000008)<br/>투자주의 => 000000000016(0x00000010)<br/>투자위험 => 000000000032(0x00000020)<br/>위험예고 => 000000000064(0x00000040)<br/>담보불가 => 000000000128(0x00000080)<br/>두개 이상 제외시 해당 값을 합산한다. |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t1441OutBlock` | t1441OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1441OutBlock1` | t1441OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-updaycnt` | 연속 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-jnildiff` | 전일등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-voldiff` | 거래량대비율 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-total` | 시가총액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
  "t1441InBlock" : {
    "gubun1" : "1",
    "gubun2" : "1",
    "gubun3" : "1",
    "jc_num" : 0,
    "sprice" : 0,
    "eprice" : 0,
    "volume" : 0,
    "idx" : 0,
    "jc_num2" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1441OutBlock1": [
        {
            "change": 20,
            "offerrem1": 2780,
            "shcode": "119650",
            "sign": "5",
            "diff": "-00.70",
            "volume": 514736,
            "bidrem1": 1307,
            "high": 2890,
            "voldiff": "00011.86",
            "total": 1027,
            "low": 2760,
            "price": 2845,
            "jnildiff": "-12.39",
            "bidho1": 2840,
            "value": 1449,
            "hname": "KC코트렐",
            "open": 2870,
            "offerho1": 2845,
            "updaycnt": 2
        },
        {
            "change": 0,
            "offerrem1": 5203059,
            "shcode": "550043",
            "sign": "3",
            "diff": "000.00",
            "volume": 671167,
            "bidrem1": 606185,
            "high": 120,
            "voldiff": "00384.24",
            "total": 180,
            "low": 115,
            "price": 120,
            "jnildiff": "-07.69",
            "bidho1": 115,
            "value": 78,
            "hname": "QV 인버스 레버리지 W",
            "open": 115,
            "offerho1": 120,
            "updaycnt": 0
        }
    ],
    "t1441OutBlock": {
        "idx": 20
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1444"></a>
## `t1444` 시가총액상위

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
| `t1444InBlock` | t1444InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시 Space 연속 조회시 이전 조회한 OutBlock의 idx 값으로 설정 |


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
| `t1444OutBlock` | t1444OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1444OutBlock1` | t1444OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-vol_rate` | 거래비중 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-total` | 시가총액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate` | 비중 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-for_rate` | 외인비중 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1444InBlock" : {
    "upcode" : "001",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1444OutBlock1": [
        {
            "volume": 4817941,
            "total": 4280334,
            "for_rate": "52.54",
            "vol_rate": "1.26",
            "rate": "19.67",
            "price": 71700,
            "shcode": "005930",
            "change": 500,
            "sign": "5",
            "diff": "-0.69",
            "hname": "삼성전자"
        },
        {
            "volume": 223627,
            "total": 183174,
            "for_rate": "24.66",
            "vol_rate": "0.06",
            "rate": "0.84",
            "price": 198100,
            "shcode": "096770",
            "change": 100,
            "sign": "2",
            "diff": "0.05",
            "hname": "SK이노베이션"
        }
    ],
    "t1444OutBlock": {
        "idx": 20
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1452"></a>
## `t1452` 거래량상위

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
| `t1452InBlock` | t1452InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-jnilgubun` | 전일구분 | String | Y | 1 | 1:당일 2:전일 |
| `&nbsp;&nbsp;-sdiff` | 시작등락율 | Number | Y | 3 | 현재등락율 >= sdiff |
| `&nbsp;&nbsp;-ediff` | 종료등락율 | Number | Y | 3 | 현재등락율 <= ediff |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값 (0x00000080)관리종목 => 000000000128 (0x00000100)시장경보 => 000000000256 (0x00000200)거래정지 => 000000000512 (0x00004000)우선주 => 000000016384 (0x00200000)증거금50 => 000008388608 (0x01000000)정리매매 => 000016777216 (0x04000000)투자유의 => 000067108864 (0x80000000)불성실공시 => -02147483648 두개 이상 제외시 해당 값을 합산한다 예)관리종목 + 시장경보 = 000000000128 + 000000000256 = 000000000384 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |


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
| `t1452OutBlock` | t1452OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1452OutBlock1` | t1452OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bef_diff` | 전일비 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
   "t1452InBlock" :{
      "gubun" : "1",
      "jnilgubun" : "1",
      "sdiff" : 0,
      "ediff" : 0,
      "jc_num" : 0,
      "sprice" : 0,
      "eprice" : 0,
      "volume" : 0,
      "idx" : 0
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1452OutBlock": {
        "idx": 40
    },
    "t1452OutBlock1": [
        {
            "volume": 2103252,
            "bef_diff": "0000021.02",
            "vol": "000.91",
            "price": 1005,
            "jnilvolume": 10006819,
            "change": 0,
            "shcode": "015590",
            "sign": "3",
            "diff": "000.00",
            "hname": "큐로"
        },
        {
            "volume": 7007,
            "bef_diff": "0000028.27",
            "vol": "000.70",
            "price": 10970,
            "jnilvolume": 24782,
            "change": 0,
            "shcode": "447620",
            "sign": "3",
            "diff": "000.00",
            "hname": "SOL 미국TOP5채권혼합"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1463"></a>
## `t1463` 거래대금상위

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
| `t1463InBlock` | t1463InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0 : 전체<br/>1 : 코스피<br/>2 : 코스닥 |
| `&nbsp;&nbsp;-jnilgubun` | 전일구분 | String | Y | 1 | 0 : 당일<br/>1 : 전일 |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값<br/>(0x00000080)관리종목 => 000000000128<br/>(0x00000100)시장경보 => 000000000256<br/>(0x00000200)거래정지 => 000000000512<br/>(0x00004000)우선주 => 000000016384<br/>(0x00200000)증거금50 => 000008388608<br/>(0x01000000)정리매매 => 000016777216<br/>(0x04000000)투자유의 => 000067108864<br/>(0x80000000)불성실공시 => -02147483648<br/>두개 이상 제외시 해당 값을 합산한다<br/>예)관리종목 + 시장경보 = 000000000128 + 000000000256 = 000000000384 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
| `&nbsp;&nbsp;-jc_num2` | 대상제외2 | Number | Y | 12 | 기본 => 000000000000<br/>상장지수펀드 => 000000000001<br/>선박투자회사 => 000000000002<br/>스펙 => 000000000004<br/>ETN => 000000000008(0x00000008)<br/>투자주의 => 000000000016(0x00000010)<br/>투자위험 => 000000000032(0x00000020)<br/>위험예고 => 000000000064(0x00000040)<br/>담보불가 => 000000000128(0x00000080)<br/>두개 이상 제외시 해당 값을 합산한다. |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t1463OutBlock` | t1463OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1463OutBlock1` | t1463OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilvalue` | 전일거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bef_diff` | 전일비 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-filler` | filler | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-total` | 시가총액 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1463InBlock" : {
    "gubun" : "1",
    "jnilgubun" : "1",
    "jc_num" : 0,
    "sprice" : 0,
    "eprice" : 0,
    "volume" : 0,
    "idx" : 0,
    "jc_num2" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1463OutBlock": {
        "idx": 20
    },
    "t1463OutBlock1": [
        {
            "volume": 4817961,
            "bef_diff": "0000039.71",
            "price": 71800,
            "jnilvolume": 12161798,
            "change": 400,
            "jnilvalue": 874631,
            "shcode": "005930",
            "sign": "5",
            "filler": "",
            "diff": "-00.55",
            "value": 347308,
            "hname": "삼성전자"
        },
        {
            "volume": 1087409,
            "bef_diff": "0000121.32",
            "price": 127000,
            "jnilvolume": 923145,
            "change": 3900,
            "jnilvalue": 113286,
            "shcode": "066570",
            "sign": "2",
            "filler": "",
            "diff": "003.17",
            "value": 137441,
            "hname": "LG전자"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1466"></a>
## `t1466` 전일동시간대비거래급증

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
| `t1466InBlock` | t1466InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0 : 전체<br/>1 : 코스피<br/>2 : 코스닥 |
| `&nbsp;&nbsp;-type1` | 전일거래량 | String | Y | 1 | 0@1주 이상<br/>1@1만주 이상<br/>2@5만주 이상<br/>3@10만주 이상<br/>4@20만주 이상<br/>5@50만주 이상<br/>6@100만주 이상 |
| `&nbsp;&nbsp;-type2` | 거래급등율 | String | Y | 1 | 0@전체<br/>1@2000%이하<br/>2@1500%이하<br/>3@1000%이하<br/>4@500%이하<br/>5@100%이하<br/>6@50%이하 |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값<br/>(0x00000080)관리종목 => 000000000128<br/>(0x00000100)시장경보 => 000000000256<br/>(0x00000200)거래정지 => 000000000512<br/>(0x00004000)우선주 => 000000016384<br/>(0x00200000)증거금50 => 000008388608<br/>(0x01000000)정리매매 => 000016777216<br/>(0x04000000)투자유의 => 000067108864<br/>(0x80000000)불성실공시 => -02147483648<br/>두개 이상 제외시 해당 값을 합산한다<br/>예)관리종목 + 시장경보 = 000000000128 + 000000000256 = 000000000384 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
| `&nbsp;&nbsp;-jc_num2` | 대상제외2 | Number | Y | 12 | 기본 => 000000000000<br/>상장지수펀드 => 000000000001<br/>선박투자회사 => 000000000002<br/>스펙 => 000000000004<br/>ETN => 000000000008(0x00000008)<br/>투자주의 => 000000000016(0x00000010)<br/>투자위험 => 000000000032(0x00000020)<br/>위험예고 => 000000000064(0x00000040)<br/>담보불가 => 000000000128(0x00000080)<br/>두개 이상 제외시 해당 값을 합산한다. |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t1466OutBlock` | t1466OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hhmm` | 현재시분 | String | Y | 5 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1466OutBlock1` | t1466OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-stdvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volume` | 당일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-voldiff` | 거래급등율 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
  "t1466InBlock" : {
    "gubun" : "1",
    "type1" : "1",
    "type2" : "1",
    "jc_num" : 0,
    "sprice" : 0,
    "eprice" : 0,
    "volume" : 0,
    "idx" : 0,
    "jc_num2" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1466OutBlock": {
        "hhmm": "10:26",
        "idx": 20
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1466OutBlock1": [
        {
            "volume": 20817762,
            "voldiff": "01749.01",
            "high": 145,
            "low": 135,
            "price": 145,
            "shcode": "530036",
            "change": 5,
            "sign": "5",
            "diff": "-3.33",
            "stdvolume": 1190262,
            "hname": "삼성 인버스 2X WTI원",
            "open": 140
        },
        {
            "volume": 953956,
            "voldiff": "00673.56",
            "high": 5890,
            "low": 5550,
            "price": 5610,
            "shcode": "123700",
            "change": 230,
            "sign": "5",
            "diff": "-3.94",
            "stdvolume": 141629,
            "hname": "SJM",
            "open": 5700
        }
    ]
}
```

---

<a id="tr-t1481"></a>
## `t1481` 시간외등락율상위

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
| `t1481InBlock` | t1481InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-gubun1` | 구분 | String | Y | 1 | 0:전체<br/>1:코스피<br/>2:코스닥 |
| `&nbsp;&nbsp;-gubun2` | 상승하락 | String | Y | 1 | 0: 상승률<br/>1: 하락률 |
| `&nbsp;&nbsp;-jongchk` | 종목체크 | String | Y | 1 | 0: 전체<br/>1: 우선제외<br/>2: 관리제외<br/>3: 우선관리제외 |
| `&nbsp;&nbsp;-volume` | 거래량 | String | Y | 1 | 0: 전체거래량<br/>1: 1천주 이상<br/>2: 5천주 이상<br/>3: 1만주 이상<br/>4: 5만주 이상<br/>5: 10만주 이상<br/>6: 50만주 이상<br/>7: 100만주 이상 |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 연속조회시 OutBlock의 idx 입력 |


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
| `t1481OutBlock` | t1481OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1481OutBlock1` | t1481OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-total` | 시가총액(억) | Number | Y | 12 | 2026.01.15 16시 이후 적용예정 |


### 요청 Example

```json
{
  "t1481InBlock" : {
    "gubun1" : "1",
    "gubun2" : "1",
    "jongchk" : "1",
    "volume" : "1",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1481OutBlock": {
        "idx": 20
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1481OutBlock1": [
        {
            "volume": 2136,
            "bidrem1": 301,
            "price": 10490,
            "change": 445,
            "offerrem1": 764,
            "shcode": "449180",
            "sign": "5",
            "diff": "-04.07",
            "bidho1": 10305,
            "value": 22493050,
            "hname": "KODEX 미국S&P500(H)",
            "offerho1": 10485
        },
        {
            "volume": 369875,
            "bidrem1": 9738,
            "price": 935,
            "change": 8,
            "offerrem1": 248,
            "shcode": "031820",
            "sign": "5",
            "diff": "-00.85",
            "bidho1": 935,
            "value": 346240565,
            "hname": "콤텍시스템",
            "offerho1": 936
        }
    ]
}
```

---

<a id="tr-t1482"></a>
## `t1482` 시간외거래량상위

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
| `t1482InBlock` | t1482InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-sort_gbn` | 정렬구분 | Number | Y | 1 | 0: 거래량<br/>1: 거래대금 |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0: 전체<br/>1: 코스피<br/>2: 코스닥 |
| `&nbsp;&nbsp;-jongchk` | 거래량 | String | Y | 1 | 0: 전체<br/>1: 우선제외<br/>2: 관리제외<br/>3: 우선관리제외 |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 연속조회시 OutBlock의 idx 입력 |


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
| `t1482OutBlock` | t1482OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1482OutBlock1` | t1482OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1482InBlock" : {
    "gubun" : "1",
    "jongchk" : "1",
    "idx" : 0,
    "sort_gbn": 0
  }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "t1482OutBlock1": [
        {
            "volume": 2413264,
            "vol": "000.29",
            "price": 2485,
            "change": 10,
            "shcode": "252670",
            "sign": "5",
            "diff": "-00.40",
            "value": 5998142760,
            "hname": "KODEX 200선물인버스2"
        },
        {
            "volume": 116309,
            "vol": "000.03",
            "price": 1120,
            "change": 5,
            "shcode": "530031",
            "sign": "2",
            "diff": "000.45",
            "value": 130067985,
            "hname": "삼성 레버리지 WTI원？"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1482OutBlock": {
        "idx": 20
    }
}"
```

---

<a id="tr-t1489"></a>
## `t1489` 예상체결량상위조회

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
| `t1489InBlock` | t1489InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 거래소구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-jgubun` | 장구분 | String | Y | 1 | 0:장전 1:장후 |
| `&nbsp;&nbsp;-jongchk` | 종목체크 | String | Y | 12 | 대상제외값(설정시 저장됨) 증거금50 : 0x00400000 증거금100 : 0x00800000 증거금50/100 : 0x00200000 관리종목 : 0x00000080 시장경보 : 0x00000100 거래정지 : 0x00000200 우선주 : 0x00004000 투자유의 : 0x04000000 정리매매 : 0x01000000 불성실공시 : 0x80000000 |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 다음 조회시 사용 첫 조회시 Space |
| `&nbsp;&nbsp;-yesprice` | 예상체결시작가격 | Number | Y | 8 | yesprice <= 예상체결가 인 종목 |
| `&nbsp;&nbsp;-yeeprice` | 예상체결종료가격 | Number | Y | 8 | 예상체결가 <= yeeprice 인 종목 |
| `&nbsp;&nbsp;-yevolume` | 예상체결량 | Number | Y | 12 | 예상체결량 >= yevolume 인 종목 |


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
| `t1489OutBlock` | t1489OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1489OutBlock1` | t1489OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 예상거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1489InBlock" : {
    "gubun" : "1",
    "jgubun" : "1",
    "jongchk" : "1",
    "idx" : 0,
    "yesprice" : 0,
    "yeeprice" : 0,
    "yevolume" : 0
  }
}
```

### 응답 Example

```json
{
    "t1489OutBlock1": [
        {
            "volume": 1711086,
            "bidho": 2460,
            "price": 2465,
            "jnilvolume": 94909304,
            "change": 30,
            "shcode": "252670",
            "sign": "5",
            "diff": "-01.20",
            "offerho": 2465,
            "hname": "KODEX 200선물인버스2"
        },
        {
            "volume": 114483,
            "bidho": 896,
            "price": 897,
            "jnilvolume": 125588,
            "change": 106,
            "shcode": "009810",
            "sign": "2",
            "diff": "013.40",
            "offerho": 897,
            "hname": "플레이그램"
        }
    ],
    "rsp_cd": "00000",
    "t1489OutBlock": {
        "idx": 20
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1492"></a>
## `t1492` 단일가예상등락율상위

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
| `t1492InBlock` | t1492InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 구분 | String | Y | 1 | 0: 전체 1: 코스피 2: 코스닥 |
| `&nbsp;&nbsp;-gubun2` | 상승하락 | String | Y | 1 | 0: 상승률 1: 하락률 |
| `&nbsp;&nbsp;-jongchk` | 종목체크 | String | Y | 1 | 전체@0 우선제외@1 관리제외@2 우선관리제외@3 |
| `&nbsp;&nbsp;-volume` | 거래량 | String | Y | 1 | 전체거래량@0 1백주 이상@1 5백주 이상@2 1천주 이상@3 5천주 이상@4 1만주 이상@5 5만주 이상@6 50만주 이상@6 100만주 이상@7 |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 연속조회시 OutBlock의 idx 입력 |


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
| `t1492OutBlock` | t1492OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1492OutBlock1` | t1492OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 예상체결가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-yevolume` | 예상체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1492InBlock" : {
    "gubun1" : "1",
    "gubun2" : "1",
    "jongchk" : "1",
    "volume" : "1",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1492OutBlock": {
        "idx": 21
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1492OutBlock1": [
        {
            "change": -450,
            "offerrem1": 2078,
            "shcode": "005950",
            "sign": "5",
            "yevolume": 24188,
            "diff": "-01.67",
            "volume": 121009,
            "bidrem1": 4015,
            "price": 26550,
            "bidho1": 26500,
            "value": 3226499400,
            "hname": "이수화학",
            "offerho1": 26550
        },
        {
            "change": -60,
            "offerrem1": 1,
            "shcode": "006880",
            "sign": "5",
            "yevolume": 1025,
            "diff": "-00.73",
            "volume": 2840,
            "bidrem1": 122,
            "price": 8180,
            "bidho1": 8180,
            "value": 23213320,
            "hname": "신송홀딩스",
            "offerho1": 8210
        }
    ]
}
```
