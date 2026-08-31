# [해외선물] 주문

> LS증권 OPEN API 정의서 · 그룹: **해외선물** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=c1ef0e8b-4666-4d8c-a77f-6ab488cfdb39&api_id=b820f925-e189-4553-a7d1-8e5f2750fe08)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `b820f925-e189-4553-a7d1-8e5f2750fe08` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/overseas-futureoption/order` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외선물옵션 주문서비스를 확인할 수 있습니다 |

## TR 목록 (3건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외선물 신규주문 | [CIDBT00100](orders.md#tr-CIDBT00100) | 5 | 5 | 5 |
| 해외선물 정정주문 | [CIDBT00900](orders.md#tr-CIDBT00900) | 5 | 5 | 5 |
| 해외선물 취소주문 | [CIDBT01000](orders.md#tr-CIDBT01000) | 5 | 5 | 5 |

---

<a id="tr-CIDBT00100"></a>
## `CIDBT00100` 해외선물 신규주문

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
| `CIDBT00100InBlock1` | CIDBT00100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | YYYYMMDD 형식 |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | 1:신규 |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-AbrdFutsOrdPtnCode` | 해외선물주문유형코드 | String | Y | 1 | 1:시장가<br/>2:지정가 |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | SPACE |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-CndiOrdPrc` | 조건주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdtCode` | 상품코드 | String | Y | 6 | SPACE |
| `&nbsp;&nbsp;-DueYymm` | 만기년월 | String | Y | 6 | SPACE |
| `&nbsp;&nbsp;-ExchCode` | 거래소코드 | String | Y | 10 | SPACE |


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
| `CIDBT00100OutBlock1` | CIDBT00100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BrnCode` | 지점코드 | String | Y | 7 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AbrdFutsOrdPtnCode` | 해외선물주문유형코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-CndiOrdPrc` | 조건주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdtCode` | 상품코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-DueYymm` | 만기년월 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ExchCode` | 거래소코드 | String | Y | 10 | - |
| `CIDBT00100OutBlock2` | CIDBT00100OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-OvrsFutsOrdNo` | 해외선물주문번호 | String | Y | 10 | - |


### 요청 Example

```json
{
  "CIDBT00100InBlock1" : {
    "RecCnt" : 1,
    "OrdDt" : "20230609",
    "BrnCode" : "100",
    "IsuCodeVal" : "ADM23",
    "FutsOrdTpCode" : "1",
    "BnsTpCode" : "1",
    "AbrdFutsOrdPtnCode" : "2",
    "CrcyCode" : " ",
    "OvrsDrvtOrdPrc" : 122.0,
    "CndiOrdPrc" : 0.664,
    "OrdQty" : 1,
    "PrdtCode" : "000000",
    "DueYymm" : "000001",
    "ExchCode" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "CIDBT00100OutBlock1": {
        "ExchCode": "",
        "FutsOrdTpCode": "1",
        "BnsTpCode": "1",
        "OrdQty": 1,
        "RecCnt": 1,
        "PrdtCode": "000000",
        "AcntNo": "20629783903",
        "CndiOrdPrc": "0.66400000000",
        "BrnCode": "",
        "Pwd": "********",
        "CrcyCode": "",
        "DueYymm": "000001",
        "IsuCodeVal": "ADM23",
        "AbrdFutsOrdPtnCode": "2",
        "OrdDt": "20230609",
        "OvrsDrvtOrdPrc": "122.00000000000"
    },
    "CIDBT00100OutBlock2": {
        "RecCnt": 1,
        "AcntNo": "20629783903",
        "OvrsFutsOrdNo": "0000000136"
    },
    "rsp_msg": "정상 처리되었습니다."
}
```

---

<a id="tr-CIDBT00900"></a>
## `CIDBT00900` 해외선물 정정주문

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
| `CIDBT00900InBlock1` | CIDBT00900InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | YYYYMMDD 형식 |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo` | 해외선물원주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | 2:정정 |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-FutsOrdPtnCode` | 선물주문유형코드 | String | Y | 1 | 2:지정가 |
| `&nbsp;&nbsp;-CrcyCodeVal` | 통화코드값 | String | Y | 3 | SPACE |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-CndiOrdPrc` | 조건주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsDrvtPrdtCode` | 해외파생상품코드 | String | Y | 10 | SPACE |
| `&nbsp;&nbsp;-DueYymm` | 만기년월 | String | Y | 6 | SPACE |
| `&nbsp;&nbsp;-ExchCode` | 거래소코드 | String | Y | 10 | SPACE |


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
| `CIDBT00900OutBlock1` | CIDBT00900OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RegBrnNo` | 등록지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo` | 해외선물원주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FutsOrdPtnCode` | 선물주문유형코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CrcyCodeVal` | 통화코드값 | String | Y | 3 | - |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-CndiOrdPrc` | 조건주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsDrvtPrdtCode` | 해외파생상품코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-DueYymm` | 만기년월 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ExchCode` | 거래소코드 | String | Y | 10 | - |
| `CIDBT00900OutBlock2` | CIDBT00900OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-OvrsFutsOrdNo` | 해외선물주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-InnerMsgCnts` | 내부메시지내용 | String | Y | 80 | - |


### 요청 Example

```json
{
  "CIDBT00900InBlock1" : {
    "RecCnt" : 1,
    "OrdDt" : "20230609",
    "RegBrnNo" : " ",
    "OvrsFutsOrgOrdNo" : "0000000029",
    "IsuCodeVal" : "ADM23",
    "FutsOrdTpCode" : "2",
    "BnsTpCode" : "1",
    "FutsOrdPtnCode" : "2",
    "CrcyCodeVal" : " ",
    "OvrsDrvtOrdPrc" : 122.0,
    "CndiOrdPrc" : 0.66400000000,
    "OrdQty" : 1,
    "OvrsDrvtPrdtCode" : "",
    "DueYymm" : "",
    "ExchCode" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00131",
    "rsp_msg": "정정이 완료되었습니다.",
    "CIDBT00900OutBlock2": {
        "RecCnt": 1,
        "AcntNo": "20629783903",
        "OvrsFutsOrdNo": "0000000030",
        "InnerMsgCnts": ""
    },
    "CIDBT00900OutBlock1": {
        "ExchCode": "",
        "FutsOrdTpCode": "2",
        "BnsTpCode": "1",
        "OvrsDrvtPrdtCode": "",
        "FutsOrdPtnCode": "2",
        "OvrsFutsOrgOrdNo": "0000000029",
        "OrdQty": 1,
        "RecCnt": 1,
        "AcntNo": "20629783903",
        "CndiOrdPrc": "0.66700000000",
        "RegBrnNo": "",
        "Pwd": "********",
        "DueYymm": "",
        "IsuCodeVal": "ADM23",
        "OrdDt": "20230609",
        "CrcyCodeVal": "",
        "OvrsDrvtOrdPrc": "122.50000000000"
    }
}
```

---

<a id="tr-CIDBT01000"></a>
## `CIDBT01000` 해외선물 취소주문

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
| `CIDBT01000InBlock1` | CIDBT01000InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | YYYYMMDD 형식 |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo` | 해외선물원주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | 3:취소 |
| `&nbsp;&nbsp;-PrdtTpCode` | 상품구분코드 | String | Y | 2 | SPACE |
| `&nbsp;&nbsp;-ExchCode` | 거래소코드 | String | Y | 10 | SPACE |


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
| `CIDBT01000OutBlock1` | CIDBT01000OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BrnNo` | 지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo` | 해외선물원주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-PrdtTpCode` | 상품구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-ExchCode` | 거래소코드 | String | Y | 10 | - |
| `CIDBT01000OutBlock2` | CIDBT01000OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-OvrsFutsOrdNo` | 해외선물주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-InnerMsgCnts` | 내부메시지내용 | String | Y | 80 | - |


### 요청 Example

```json
{
  "CIDBT01000InBlock1" : {
    "RecCnt" : 1,
    "OrdDt" : "20230609",
    "BrnNo" : " ",
    "IsuCodeVal" : "ADM23",
    "OvrsFutsOrgOrdNo" : "0000000030",
    "FutsOrdTpCode" : "3",
    "PrdtTpCode" : " ",
    "ExchCode" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00156",
    "CIDBT01000OutBlock1": {
        "RecCnt": 1,
        "ExchCode": "",
        "FutsOrdTpCode": "3",
        "BrnNo": "",
        "AcntNo": "20629783903",
        "Pwd": "********",
        "IsuCodeVal": "ADM23",
        "OvrsFutsOrgOrdNo": "0000000030",
        "PrdtTpCode": "",
        "OrdDt": "20230609"
    },
    "rsp_msg": "취소주문이 완료되었습니다.",
    "CIDBT01000OutBlock2": {
        "RecCnt": 1,
        "AcntNo": "20629783903",
        "OvrsFutsOrdNo": "0000000031",
        "InnerMsgCnts": ""
    }
}
```
