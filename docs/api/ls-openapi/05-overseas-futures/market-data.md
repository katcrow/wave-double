# [해외선물] 시세

> LS증권 OPEN API 정의서 · 그룹: **해외선물** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=c1ef0e8b-4666-4d8c-a77f-6ab488cfdb39&api_id=d61d4f85-9845-41ef-b915-4efa8fd0aad1)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `d61d4f85-9845-41ef-b915-4efa8fd0aad1` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/overseas-futureoption/market-data` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외선물옵션 종목별 시세 및 차트 등 시세관련 데이터를 확인할 수 있습니다. |

## TR 목록 (14건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외선물마스터조회 | [o3101](market-data.md#tr-o3101) | 1 | 1 | 10 |
| 해외선물 일별체결 조회 | [o3104](market-data.md#tr-o3104) | 1 | 1 | 1 |
| 해외선물 현재가(종목정보) 조회 | [o3105](market-data.md#tr-o3105) | 2 | 2 | 50 |
| 해외선물 현재가호가 조회 | [o3106](market-data.md#tr-o3106) | 1 | 1 | 50 |
| 해외선물 관심종목 조회 | [o3107](market-data.md#tr-o3107) | 1 | 1 | 50 |
| 해외선물 시간대별(Tick)체결 조회 | [o3116](market-data.md#tr-o3116) | 1 | 1 | 1 |
| 해외선물옵션 마스터 조회 | [o3121](market-data.md#tr-o3121) | 1 | 1 | 10 |
| 해외선물옵션 차트 분봉 조회 | [o3123](market-data.md#tr-o3123) | 1 | 1 | 1 |
| 해외선물옵션 현재가(종목정보) 조회 | [o3125](market-data.md#tr-o3125) | 2 | 2 | 50 |
| 해외선물옵션 현재가호가 조회 | [o3126](market-data.md#tr-o3126) | 2 | 2 | 50 |
| 해외선물옵션 관심종목 조회 | [o3127](market-data.md#tr-o3127) | 1 | 1 | 50 |
| 해외선물옵션 차트 일주월 조회 | [o3128](market-data.md#tr-o3128) | 1 | 1 | 1 |
| 해외선물옵션 시간대별 Tick 체결 조회 | [o3136](market-data.md#tr-o3136) | 1 | 1 | 1 |
| 해외선물옵션 차트 NTick 체결 조회 | [o3137](market-data.md#tr-o3137) | 1 | 1 | 1 |

---

<a id="tr-o3101"></a>
## `o3101` 해외선물마스터조회

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
| `o3101InBlock` | o3101InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 입력구분(예비) | String | Y | 1 | - |


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
| `o3101OutBlock` | o3101OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-Symbol` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SymbolNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-ApplDate` | 종목배치수신일(한국일자) | String | Y | 8 | - |
| `&nbsp;&nbsp;-BscGdsCd` | 기초상품코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-BscGdsNm` | 기초상품명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-ExchCd` | 거래소코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExchNm` | 거래소명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-CrncyCd` | 기준통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-NotaCd` | 진법구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-UntPrc` | 호가단위가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-MnChgAmt` | 최소가격변동금액 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-RgltFctr` | 가격조정계수 | Number | Y | 15.10 | - |
| `&nbsp;&nbsp;-CtrtPrAmt` | 계약당금액 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-GdsCd` | 상품구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-LstngYr` | 월물(년) | String | Y | 4 | - |
| `&nbsp;&nbsp;-LstngM` | 월물(월) | String | Y | 1 | - |
| `&nbsp;&nbsp;-EcPrc` | 정산가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-DlStrtTm` | 거래시작시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlEndTm` | 거래종료시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlPsblCd` | 거래가능구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MgnCltCd` | 증거금징수구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OpngMgn` | 개시증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-MntncMgn` | 유지증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-OpngMgnR` | 개시증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-MntncMgnR` | 유지증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-DotGb` | 유효소수점자리수 | Number | Y | 2 | - |


### 요청 Example

```json
{
  "o3101InBlock": {
    "gubun": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3101OutBlock": [
        {
            "GdsCd": "002",
            "MnChgAmt": "5.000000000",
            "BscGdsCd": "AD",
            "Symbol": "ADM23",
            "UntPrc": "0.000050000",
            "ApplDate": "20230608",
            "ExchNm": "시카고상업거래소",
            "MntncMgnR": "0.000",
            "OpngMgn": "2035.00",
            "CtrtPrAmt": "100000.00",
            "DotGb": 5,
            "LstngM": "M",
            "DlEndTm": "060000",
            "DlPsblCd": "1",
            "BscGdsNm": "Australian Dollar",
            "NotaCd": "10",
            "OpngMgnR": "0.000",
            "RgltFctr": "1.0000000000",
            "MgnCltCd": "1",
            "DlStrtTm": "070000",
            "CrncyCd": "USD",
            "LstngYr": "2023",
            "EcPrc": "0.665750000",
            "MntncMgn": "2035.00",
            "SymbolNm": "Australian Dollar(2023.06)",
            "ExchCd": "CME"
        },
        {
            "GdsCd": "002",
            "MnChgAmt": "1.250000000",
            "BscGdsCd": "M6E",
            "Symbol": "M6EZ23",
            "UntPrc": "0.000100000",
            "ApplDate": "20230608",
            "ExchNm": "시카고상업거래소",
            "MntncMgnR": "0.000",
            "OpngMgn": "292.00",
            "CtrtPrAmt": "12500.00",
            "DotGb": 5,
            "LstngM": "Z",
            "DlEndTm": "060000",
            "DlPsblCd": "1",
            "BscGdsNm": "E-micro EUR\/USD",
            "NotaCd": "10",
            "OpngMgnR": "0.000",
            "RgltFctr": "1.0000000000",
            "MgnCltCd": "1",
            "DlStrtTm": "070000",
            "CrncyCd": "USD",
            "LstngYr": "2023",
            "EcPrc": "1.081150000",
            "MntncMgn": "292.00",
            "SymbolNm": "E-micro EUR\/USD(2023.12)",
            "ExchCd": "CME"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3104"></a>
## `o3104` 해외선물 일별체결 조회

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
| `o3104InBlock` | o3104InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 조회구분 | String | Y | 1 | 0:일별 1:주별 2:월별 |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-date` | 조회일자 | String | Y | 8 | YYYYMMDD |


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
| `o3104OutBlock1 (Occurs)` | o3104OutBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chedate` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-cgubun` | 체결구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3104InBlock": {
    "gubun": "0",
    "shcode": "ADM23",
    "date": "20230608"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3104OutBlock1": [
        {
            "volume": 57123,
            "chedate": "20230501",
            "high": "0.66820",
            "low": "0.66215",
            "price": "0.66435",
            "change": "0.00150",
            "sign": "2",
            "diff": "0.23",
            "cgubun": "",
            "open": "0.66300"
        },
        {
            "volume": 78764,
            "chedate": "20230428",
            "high": "0.66555",
            "low": "0.65820",
            "price": "0.66285",
            "change": "-0.00160",
            "sign": "5",
            "diff": "-0.24",
            "cgubun": "",
            "open": "0.66435"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3105"></a>
## `o3105` 해외선물 현재가(종목정보) 조회

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
| `o3105InBlock` | o3105InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목심볼 | String | Y | 8 | - |


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
| `o3105OutBlock` | o3105OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-Symbol` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SymbolNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-ApplDate` | 종목배치수신일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BscGdsCd` | 기초상품코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-BscGdsNm` | 기초상품명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-ExchCd` | 거래소코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExchNm` | 거래소명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-EcCd` | 정산구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CrncyCd` | 기준통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-NotaCd` | 진법구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-UntPrc` | 호가단위가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-MnChgAmt` | 최소가격변동금액 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-RgltFctr` | 가격조정계수 | Number | Y | 15.10 | - |
| `&nbsp;&nbsp;-CtrtPrAmt` | 계약당금액 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-LstngMCnt` | 상장개월수 | Number | Y | 2 | - |
| `&nbsp;&nbsp;-GdsCd` | 상품구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-MrktCd` | 시장구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-EminiCd` | Emini구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LstngYr` | 상장년 | String | Y | 4 | - |
| `&nbsp;&nbsp;-LstngM` | 상장월 | String | Y | 1 | - |
| `&nbsp;&nbsp;-SeqNo` | 월물순서 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-LstngDt` | 상장일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-MtrtDt` | 만기일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnlDlDt` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FstTrsfrDt` | 최초인도통지일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-EcPrc` | 정산가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-DlDt` | 거래시작일자(한국) | String | Y | 8 | - |
| `&nbsp;&nbsp;-DlStrtTm` | 거래시작시간(한국) | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlEndTm` | 거래종료시간(한국) | String | Y | 6 | - |
| `&nbsp;&nbsp;-OvsStrDay` | 거래시작일자(현지) | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvsStrTm` | 거래시작시간(현지) | String | Y | 6 | - |
| `&nbsp;&nbsp;-OvsEndDay` | 거래종료일자(현지) | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvsEndTm` | 거래종료시간(현지) | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlPsblCd` | 거래가능구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MgnCltCd` | 증거금징수구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OpngMgn` | 개시증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-MntncMgn` | 유지증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-OpngMgnR` | 개시증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-MntncMgnR` | 유지증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-DotGb` | 유효소수점자리수 | Number | Y | 2 | - |
| `&nbsp;&nbsp;-TimeDiff` | 시차 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OvsDate` | 현지체결일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-KorDate` | 한국체결일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TrdTm` | 현지체결시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-RcvTm` | 한국체결시각 | String | Y | 6 | - |
| `&nbsp;&nbsp;-TrdP` | 체결가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-TrdQ` | 체결수량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TotQ` | 누적거래량 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-TrdAmt` | 체결거래대금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-TotAmt` | 누적거래대금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-OpenP` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-HighP` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-LowP` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-CloseP` | 전일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-YdiffP` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-YdiffSign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-Cgubun` | 체결구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-Diff` | 등락율 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
   "o3105InBlock" :{
      "symbol" : "CUSN23  "
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3105OutBlock": {
        "GdsCd": "002",
        "MnChgAmt": "10.000000000",
        "CloseP": "7.2081",
        "Diff": "-0.10",
        "UntPrc": "0.0001",
        "OvsEndTm": "163000",
        "TimeDiff": -1,
        "EminiCd": "0",
        "CtrtPrAmt": "100000.00",
        "DotGb": 4,
        "OvsStrDay": "20230625",
        "DlEndTm": "173000",
        "EcCd": "1",
        "TotQ": 1011,
        "SeqNo": 1,
        "BscGdsNm": "Renminbi_USD\/CNH",
        "YdiffP": "-0.0070",
        "RgltFctr": "1.0000000000",
        "OpenP": "7.2081",
        "MgnCltCd": "1",
        "RcvTm": "103710",
        "TrdQ": 1,
        "TrdP": "7.2011",
        "TrdAmt": "7.20",
        "DlStrtTm": "181500",
        "CrncyCd": "CNY",
        "MrktCd": "001",
        "LowP": "7.1907",
        "YdiffSign": "5",
        "OvsStrTm": "171500",
        "BscGdsCd": "CUS",
        "MtrtDt": "20230717",
        "Symbol": "CUSN23",
        "OvsDate": "20230626",
        "TrdTm": "093710",
        "LstngMCnt": 12,
        "ApplDate": "20230626",
        "ExchNm": "홍콩거래소",
        "MntncMgnR": "0",
        "OpngMgn": "14084.00",
        "LstngM": "N",
        "Cgubun": "",
        "DlPsblCd": "1",
        "NotaCd": "10",
        "OpngMgnR": "0",
        "TotAmt": "0.00",
        "FnlDlDt": "20230717",
        "HighP": "7.2081",
        "LstngYr": "2023",
        "DlDt": "20230626",
        "KorDate": "20230626",
        "FstTrsfrDt": "",
        "EcPrc": "7.2081",
        "MntncMgn": "14084.00",
        "SymbolNm": "Renminbi_USD\/CNH(2023.07)",
        "LstngDt": "20230116",
        "OvsEndDay": "20230626",
        "ExchCd": "HKEX"
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3106"></a>
## `o3106` 해외선물 현재가호가 조회

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
| `o3106InBlock` | o3106InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목심볼 | String | Y | 8 | - |


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
| `o3106OutBlock` | o3106OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-symbolname` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-hotime` | 호가수신시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt1` | 매도호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt1` | 매수호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt2` | 매도호가건수2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt2` | 매수호가건수2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt3` | 매도호가건수3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt3` | 매수호가건수3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt4` | 매도호가건수4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt4` | 매수호가건수4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt5` | 매도호가건수5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt5` | 매수호가건수5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offercnt` | 매도호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt` | 매수호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offer` | 매도호가수량합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bid` | 매수호가수량합 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3106InBlock": {
    "symbol": "ADM23"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3106OutBlock": {
        "offerrem2": 19,
        "offerho4": "0.67685",
        "bidho5": "0.67645",
        "symbol": "ADM23",
        "offerho3": "0.67680",
        "offerrem3": 30,
        "bidho4": "0.67650",
        "offerrem4": 43,
        "offerho5": "0.67690",
        "offerrem5": 53,
        "jnilclose": "0.67535",
        "offerrem1": 4,
        "sign": "2",
        "symbolname": "Australian Dollar(2023.06)",
        "bidrem3": 52,
        "offer": 149,
        "bidrem4": 55,
        "high": "0.67680",
        "bidrem1": 21,
        "bidrem2": 38,
        "low": "0.67395",
        "price": "0.67670",
        "bidcnt5": 20,
        "bidcnt4": 18,
        "bidcnt3": 20,
        "bidcnt2": 16,
        "bidcnt1": 12,
        "bidho1": "0.67665",
        "hotime": "000533",
        "offerho2": "0.67675",
        "bidho3": "0.67655",
        "bidrem5": 54,
        "offerho1": "0.67670",
        "bidho2": "0.67660",
        "offercnt5": 16,
        "change": "0.00135",
        "offercnt3": 16,
        "offercnt4": 21,
        "diff": "0.20",
        "offercnt1": 2,
        "offercnt2": 12,
        "volume": 18844,
        "bid": 220,
        "offercnt": 67,
        "bidcnt": 86,
        "open": "0.67510"
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3107"></a>
## `o3107` 해외선물 관심종목 조회

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
| `o3107InBlock (Occurs)` | o3107InBlock (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목심볼 | String | Y | 8 | - |


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
| `o3107OutBlock (Occurs)` | o3107OutBlock (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-symbolname` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt1` | 매도호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt1` | 매수호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offercnt` | 매도호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt` | 매수호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offer` | 매도호가수량합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bid` | 매수호가수량합 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3107InBlock": {
    "symbol": "ADM23"
  }
}
```

### 응답 Example

```json
{
  "o3107OutBlock": [],
  "rsp_cd": "00000",
  "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3116"></a>
## `o3116` 해외선물 시간대별(Tick)체결 조회

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
| `o3116InBlock` | o3116InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 조회구분 | String | Y | 1 | 0:당일 만 사용가능 |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-readcnt` | 조회갯수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cts_seq` | 순번CTS | Number | Y | 8 | - |


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
| `o3116OutBlock` | o3116OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_seq` | 순번CTS | Number | Y | 8 | - |
| `o3116OutBlock1 (Occurs)` | o3116OutBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-ovsdate` | 현지일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ovstime` | 현지시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3116InBlock": {
    "gubun": "0",
    "shcode": "ADM23",
    "readcnt": 20,
    "cts_seq": 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3116OutBlock": {
        "cts_seq": 4826
    },
    "o3116OutBlock1": [
        {
            "volume": 18844,
            "ovstime": "000533",
            "price": "0.67670",
            "change": "0.00135",
            "sign": "2",
            "ovsdate": "20230613",
            "diff": "0.20",
            "cvolume": 1
        },
        {
            "volume": 18771,
            "ovstime": "000438",
            "price": "0.67665",
            "change": "0.00130",
            "sign": "2",
            "ovsdate": "20230613",
            "diff": "0.19",
            "cvolume": 1
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3121"></a>
## `o3121` 해외선물옵션 마스터 조회

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
| `o3121InBlock` | o3121InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-MktGb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-BscGdsCd` | 옵션기초상품코드 | String | Y | 10 | ex) ['시장구분' 옵션의 경우]<br/> 공란(옵션상품 목록),<br/> O_ES(ES상품옵션종목 목록) |


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
| `o3121OutBlock` | o3121OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-Symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-SymbolNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-ApplDate` | 종목배치수신일(한국일자) | String | Y | 8 | - |
| `&nbsp;&nbsp;-BscGdsCd` | 기초상품코드 | String | Y | 10 | 시장구분 공란 시 옵션기초상품코드 받는 필드 |
| `&nbsp;&nbsp;-BscGdsNm` | 기초상품명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-ExchCd` | 거래소코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExchNm` | 거래소명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-CrncyCd` | 기준통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-NotaCd` | 진법구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-UntPrc` | 호가단위가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-MnChgAmt` | 최소가격변동금액 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-RgltFctr` | 가격조정계수 | Number | Y | 15.10 | - |
| `&nbsp;&nbsp;-CtrtPrAmt` | 계약당금액 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-GdsCd` | 상품구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-LstngYr` | 월물(년) | String | Y | 4 | - |
| `&nbsp;&nbsp;-LstngM` | 월물(월) | String | Y | 1 | - |
| `&nbsp;&nbsp;-EcPrc` | 정산가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-DlStrtTm` | 거래시작시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlEndTm` | 거래종료시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlPsblCd` | 거래가능구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MgnCltCd` | 증거금징수구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OpngMgn` | 개시증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-MntncMgn` | 유지증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-OpngMgnR` | 개시증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-MntncMgnR` | 유지증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-DotGb` | 유효소수점자리수 | Number | Y | 2 | - |
| `&nbsp;&nbsp;-XrcPrc` | 옵션행사가 | String | Y | 15 | - |
| `&nbsp;&nbsp;-FdasBasePrc` | 기초자산기준가격 | String | Y | 15 | - |
| `&nbsp;&nbsp;-OptTpCode` | 옵션콜풋구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-RgtXrcPtnCode` | 권리행사구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-Moneyness` | ATM구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LastSettPtnCode` | 해외파생기초자산종목코드 | String | Y | 30 | - |
| `&nbsp;&nbsp;-OptMinBaseOrcPrc` | 해외옵션최소기준호가 | String | Y | 15 | - |
| `&nbsp;&nbsp;-OptMinOrcPrc` | 해외옵션최소호가 | String | Y | 15 | - |
| `&nbsp;&nbsp;-ticktype` | ticktype | String | Y | 1 | 2026.01.31 적용예정<br/><br/>** 틱 크기는 가격의 절댓값 기준으로 적용됩니다.<br/> - ticktype = 0<br/> 10이하 0.05<br/> 10이상 0.25<br/><br/> - ticktype = 1 (NQ)<br/> 5 이하 0.05<br/> 100 이하 0.25<br/> 500 이하 0.50<br/> 500 이상 1.00<br/><br/> - ticktype = 2 (ES)<br/> 5이하 0.05<br/> 20 이하 0.10<br/> 100 이하 0.25<br/> 100 이상 0.50 |


### 요청 Example

```json
{
  "o3121InBlock": {
    "MktGb": "O",
    "BscGdsCd": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3121OutBlock": [
        {
            "GdsCd": "001",
            "MnChgAmt": "0",
            "BscGdsCd": "O_E1A",
            "Symbol": "",
            "XrcPrc": "",
            "UntPrc": "0",
            "OptMinOrcPrc": "",
            "ApplDate": "20230608",
            "ExchNm": "시카고상업거래소",
            "MntncMgnR": "0",
            "OpngMgn": "0",
            "FdasBasePrc": "",
            "CtrtPrAmt": "0",
            "DotGb": 0,
            "OptMinBaseOrcPrc": "",
            "LstngM": "",
            "DlEndTm": "",
            "RgtXrcPtnCode": "",
            "DlPsblCd": "",
            "BscGdsNm": "W1 Monday E-mini S&P 500 Option",
            "NotaCd": "",
            "OpngMgnR": "0",
            "RgltFctr": "0",
            "OptTpCode": "",
            "LastSettPtnCode": "",
            "MgnCltCd": "",
            "Moneyness": "",
            "DlStrtTm": "",
            "CrncyCd": "",
            "LstngYr": "",
            "EcPrc": "0",
            "MntncMgn": "0",
            "SymbolNm": "",
            "ExchCd": "CME"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3123"></a>
## `o3123` 해외선물옵션 차트 분봉 조회

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
| `o3123InBlock` | o3123InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mktgb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | ex) ADU13,2ESF16_1915 |
| `&nbsp;&nbsp;-ncnt` | N분주기 | Number | Y | 4 | ex) 0(30초), 1(1분), 30(30분), … |
| `&nbsp;&nbsp;-readcnt` | 조회건수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 6 | - |


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
| `o3123OutBlock` | o3123OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-timediff` | 시차 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-readcnt` | 조회건수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 6 | - |
| `o3123OutBlock1 (Occurs)` | o3123OutBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 현지시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "o3123InBlock": {
    "mktgb": "F",
    "shcode": "ADM23",
    "ncnt": 1,
    "readcnt": 20,
    "cts_date": "",
    "cts_time": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3123OutBlock1": [
        {
            "date": "20230613",
            "volume": 51,
            "high": "0.67680",
            "low": "0.67670",
            "time": "000600",
            "close": "0.67670",
            "open": "0.67675"
        },
        {
            "date": "20230612",
            "volume": 12,
            "high": "0.67650",
            "low": "0.67640",
            "time": "234700",
            "close": "0.67640",
            "open": "0.67650"
        }
    ],
    "rsp_msg": "조회완료",
    "o3123OutBlock": {
        "cts_date": "20230612",
        "readcnt": 20,
        "shcode": "ADM23",
        "timediff": -14,
        "cts_time": "234700"
    }
}
```

---

<a id="tr-o3125"></a>
## `o3125` 해외선물옵션 현재가(종목정보) 조회

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
| `o3125InBlock` | o3125InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mktgb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-symbol` | 종목심볼 | String | Y | 16 | ex) 2ESF16_1915 |


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
| `o3125OutBlock` | o3125OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-Symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-SymbolNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-ApplDate` | 종목배치수신일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BscGdsCd` | 기초상품코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-BscGdsNm` | 기초상품명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-ExchCd` | 거래소코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExchNm` | 거래소명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-EcCd` | 정산구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CrncyCd` | 기준통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-NotaCd` | 진법구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-UntPrc` | 호가단위가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-MnChgAmt` | 최소가격변동금액 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-RgltFctr` | 가격조정계수 | Number | Y | 15.10 | - |
| `&nbsp;&nbsp;-CtrtPrAmt` | 계약당금액 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-LstngMCnt` | 상장개월수 | Number | Y | 2 | - |
| `&nbsp;&nbsp;-GdsCd` | 상품구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-MrktCd` | 시장구분코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-EminiCd` | Emini구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LstngYr` | 상장년 | String | Y | 4 | - |
| `&nbsp;&nbsp;-LstngM` | 상장월 | String | Y | 1 | - |
| `&nbsp;&nbsp;-SeqNo` | 월물순서 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-LstngDt` | 상장일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-MtrtDt` | 만기일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnlDlDt` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FstTrsfrDt` | 최초인도통지일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-EcPrc` | 정산가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-DlDt` | 거래시작일자(한국) | String | Y | 8 | - |
| `&nbsp;&nbsp;-DlStrtTm` | 거래시작시간(한국) | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlEndTm` | 거래종료시간(한국) | String | Y | 6 | - |
| `&nbsp;&nbsp;-OvsStrDay` | 거래시작일자(현지) | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvsStrTm` | 거래시작시간(현지) | String | Y | 6 | - |
| `&nbsp;&nbsp;-OvsEndDay` | 거래종료일자(현지) | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvsEndTm` | 거래종료시간(현지) | String | Y | 6 | - |
| `&nbsp;&nbsp;-DlPsblCd` | 거래가능구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MgnCltCd` | 증거금징수구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OpngMgn` | 개시증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-MntncMgn` | 유지증거금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-OpngMgnR` | 개시증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-MntncMgnR` | 유지증거금율 | Number | Y | 7.3 | - |
| `&nbsp;&nbsp;-DotGb` | 유효소수점자리수 | Number | Y | 2 | - |
| `&nbsp;&nbsp;-TimeDiff` | 시차 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OvsDate` | 현지체결일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-KorDate` | 한국체결일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TrdTm` | 현지체결시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-RcvTm` | 한국체결시각 | String | Y | 6 | - |
| `&nbsp;&nbsp;-TrdP` | 체결가격 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-TrdQ` | 체결수량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TotQ` | 누적거래량 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-TrdAmt` | 체결거래대금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-TotAmt` | 누적거래대금 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-OpenP` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-HighP` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-LowP` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-CloseP` | 전일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-YdiffP` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-YdiffSign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-Cgubun` | 체결구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-Diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-MinOrcPrc` | 최소호가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-MinBaseOrcPrc` | 최소기준호가 | Number | Y | 15.9 | - |


### 요청 Example

```json
{
   "o3125InBlock" :{
      "mktgb" : "F",
      "symbol" : "HSIM23          "
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3125OutBlock": {
        "GdsCd": "001",
        "MnChgAmt": "50.000000000",
        "CloseP": "18875.0",
        "MinBaseOrcPrc": "0",
        "Diff": "0.25",
        "UntPrc": "1.0",
        "OvsEndTm": "163000",
        "TimeDiff": -1,
        "EminiCd": "0",
        "CtrtPrAmt": "50.00",
        "DotGb": 0,
        "OvsStrDay": "20230625",
        "DlEndTm": "173000",
        "EcCd": "1",
        "TotQ": 93965,
        "SeqNo": 1,
        "BscGdsNm": "Hang Seng",
        "YdiffP": "47.0",
        "RgltFctr": "1.0000000000",
        "OpenP": "18877.0",
        "MgnCltCd": "1",
        "RcvTm": "122002",
        "TrdQ": 3,
        "TrdP": "18922.0",
        "TrdAmt": "56766.00",
        "DlStrtTm": "181500",
        "CrncyCd": "HKD",
        "MrktCd": "001",
        "LowP": "18676.0",
        "YdiffSign": "2",
        "OvsStrTm": "171500",
        "BscGdsCd": "HSI",
        "MtrtDt": "20230629",
        "Symbol": "HSIM23",
        "OvsDate": "20230626",
        "TrdTm": "112002",
        "LstngMCnt": 12,
        "ApplDate": "20230626",
        "ExchNm": "홍콩거래소",
        "MntncMgnR": "0",
        "MinOrcPrc": "0",
        "OpngMgn": "101944.00",
        "LstngM": "M",
        "Cgubun": "",
        "DlPsblCd": "1",
        "NotaCd": "10",
        "OpngMgnR": "0",
        "TotAmt": "0.00",
        "FnlDlDt": "20230629",
        "HighP": "19022.0",
        "LstngYr": "2023",
        "DlDt": "20230626",
        "KorDate": "20230626",
        "FstTrsfrDt": "",
        "EcPrc": "18875.0",
        "MntncMgn": "101944.00",
        "SymbolNm": "Hang Seng(2023.06)",
        "LstngDt": "20221226",
        "OvsEndDay": "20230626",
        "ExchCd": "HKEX"
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3126"></a>
## `o3126` 해외선물옵션 현재가호가 조회

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
| `o3126InBlock` | o3126InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mktgb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-symbol` | 종목심볼 | String | Y | 16 | ex) 2ESF16_1915 |


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
| `o3126OutBlock` | o3126OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-symbolname` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-hotime` | 호가수신시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt1` | 매도호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt1` | 매수호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt2` | 매도호가건수2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt2` | 매수호가건수2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt3` | 매도호가건수3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt3` | 매수호가건수3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt4` | 매도호가건수4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt4` | 매수호가건수4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt5` | 매도호가건수5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt5` | 매수호가건수5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offercnt` | 매도호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt` | 매수호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offer` | 매도호가수량합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bid` | 매수호가수량합 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3126InBlock": {
    "mktgb": "F",
    "symbol": "ADM23"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "조회완료",
    "o3126OutBlock": {
        "offerrem2": 20,
        "offerho4": "0.67685",
        "bidho5": "0.67645",
        "symbol": "ADM23",
        "offerho3": "0.67680",
        "offerrem3": 30,
        "bidho4": "0.67650",
        "offerrem4": 43,
        "offerho5": "0.67690",
        "offerrem5": 53,
        "jnilclose": "0.67535",
        "offerrem1": 4,
        "sign": "2",
        "symbolname": "Australian Dollar(2023.06)",
        "bidrem3": 52,
        "offer": 150,
        "bidrem4": 55,
        "high": "0.67680",
        "bidrem1": 21,
        "bidrem2": 38,
        "low": "0.67395",
        "price": "0.67670",
        "bidcnt5": 20,
        "bidcnt4": 18,
        "bidcnt3": 20,
        "bidcnt2": 16,
        "bidcnt1": 12,
        "bidho1": "0.67665",
        "hotime": "000534",
        "offerho2": "0.67675",
        "bidho3": "0.67655",
        "bidrem5": 54,
        "offerho1": "0.67670",
        "bidho2": "0.67660",
        "offercnt5": 16,
        "change": "0.00135",
        "offercnt3": 16,
        "offercnt4": 21,
        "diff": "0.20",
        "offercnt1": 2,
        "offercnt2": 13,
        "volume": 18844,
        "bid": 220,
        "offercnt": 68,
        "bidcnt": 86,
        "open": "0.67510"
    }
}
```

---

<a id="tr-o3127"></a>
## `o3127` 해외선물옵션 관심종목 조회

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
| `o3127InBlock` | o3127InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-nrec` | 건수 | Number | Y | 4 | - |
| `o3127InBlock1 (Occurs)` | o3127InBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-mktgb` | 기본입력 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-symbol` | 종목심볼 | String | Y | 16 | ex) 2ESF16_1915 |


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
| `o3127OutBlock (Occurs)` | o3127OutBlock (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-symbolname` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-offercnt1` | 매도호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt1` | 매수호가건수1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offercnt` | 매도호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bidcnt` | 매수호가건수합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offer` | 매도호가수량합 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-bid` | 매수호가수량합 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3127InBlock": {
    "nrec": 20
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3127OutBlock": [
        {
            "symbol": "",
            "change": "0",
            "jnilclose": "0",
            "offerrem1": 0,
            "sign": "",
            "diff": "0",
            "offercnt1": 0,
            "symbolname": "",
            "volume": 0,
            "offer": 0,
            "high": "0",
            "bidrem1": 0,
            "low": "0",
            "price": "0",
            "bidcnt1": 0,
            "bidho1": "0",
            "bid": 0,
            "offercnt": 0,
            "bidcnt": 0,
            "open": "0",
            "offerho1": "0"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3128"></a>
## `o3128` 해외선물옵션 차트 일주월 조회

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
| `o3128InBlock` | o3128InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mktgb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | ex) ADU13,2ESF16_1915 |
| `&nbsp;&nbsp;-gubun` | 주기구분 | String | Y | 1 | ex) 0(일), 1(주), 2(월) |
| `&nbsp;&nbsp;-qrycnt` | 요청건수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | ex) 조회당일 |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |


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
| `o3128OutBlock` | o3128OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-jiclose` | 존일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-mk_stime` | 장시작시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-mk_etime` | 장마감시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `o3128OutBlock1 (Occurs)` | o3128OutBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "o3128InBlock": {
    "mktgb": "F",
    "shcode": "ADM23",
    "gubun": "1",
    "qrycnt": 20,
    "sdate": "20230525",
    "edate": "20230609",
    "cts_date": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3128OutBlock": {
        "cts_date": "00000000",
        "shcode": "ADM23",
        "jivolume": 0,
        "mk_etime": "160000",
        "jisiga": "0",
        "jilow": "0",
        "diclose": "0.67670",
        "disiga": "0.67510",
        "dihigh": "0.67680",
        "jihigh": "0",
        "rec_count": 6,
        "dilow": "0.67395",
        "mk_stime": "170000",
        "jiclose": "0"
    },
    "rsp_msg": "조회완료",
    "o3128OutBlock1": [
        {
            "date": "20230505",
            "volume": 412248,
            "high": "0.67675",
            "low": "0.66215",
            "close": "0.67660",
            "open": "0.66300"
        }
    ]
}
```

---

<a id="tr-o3136"></a>
## `o3136` 해외선물옵션 시간대별 Tick 체결 조회

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
| `o3136InBlock` | o3136InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 조회구분 | String | Y | 1 | ex) 0(당일), 1(전일) |
| `&nbsp;&nbsp;-mktgb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | ex) 2ESF16_1915 |
| `&nbsp;&nbsp;-readcnt` | 조회갯수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cts_seq` | 순번CTS | Number | Y | 8 | - |


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
| `o3136OutBlock` | o3136OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_seq` | 순번CTS | Number | Y | 8 | - |
| `o3136OutBlock1 (Occurs)` | o3136OutBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-ovsdate` | 현지일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ovstime` | 현지시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "o3136InBlock": {
    "gubun": "0",
    "mktgb": "F",
    "shcode": "ADM23",
    "readcnt": 20,
    "cts_seq": 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "o3136OutBlock1": [
        {
            "volume": 18844,
            "ovstime": "000533",
            "price": "0.67670",
            "change": "0.00135",
            "sign": "2",
            "ovsdate": "20230613",
            "diff": "0.20",
            "cvolume": 1
        },
        {
            "volume": 18771,
            "ovstime": "000438",
            "price": "0.67665",
            "change": "0.00130",
            "sign": "2",
            "ovsdate": "20230613",
            "diff": "0.19",
            "cvolume": 1
        }
    ],
    "o3136OutBlock": {
        "cts_seq": 4826
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-o3137"></a>
## `o3137` 해외선물옵션 차트 NTick 체결 조회

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
| `o3137InBlock` | o3137InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mktgb` | 시장구분 | String | Y | 1 | ex) F(선물), O(옵션) |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | ex) 2ESF16_1915 |
| `&nbsp;&nbsp;-ncnt` | 단위 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 건수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cts_seq` | 순번CTS | String | Y | 10 | - |
| `&nbsp;&nbsp;-cts_daygb` | 당일구분CTS | String | Y | 2 | - |


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
| `o3137OutBlock` | o3137OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-cts_seq` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-cts_daygb` | 연속당일구분 | String | Y | 2 | - |
| `o3137OutBlock1 (Occurs)` | o3137OutBlock1 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 15.9 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "o3137InBlock": {
    "mktgb": "F",
    "shcode": "ADM23",
    "ncnt": 1,
    "qrycnt": 20,
    "cts_seq": "",
    "cts_daygb": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "조회완료",
    "o3137OutBlock": {
        "shcode": null,
        "rec_count": null,
        "cts_daygb": null,
        "cts_seq": null
    },
    "o3137OutBlock1": [
        {
            "date": "20230613",
            "volume": 1,
            "high": "0.67670",
            "low": "0.67670",
            "time": "000533",
            "close": "0.67670",
            "open": "0.67670"
        },
        {
            "date": "20230613",
            "volume": 1,
            "high": "0.67665",
            "low": "0.67665",
            "time": "000438",
            "close": "0.67665",
            "open": "0.67665"
        }
    ]
}
```
