# [선물/옵션] 주문

> LS증권 OPEN API 정의서 · 그룹: **선물/옵션** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=2f1eea77-5606-4512-93c6-31b21d2ece90&api_id=b579d38a-3ce5-4b1b-b94e-b0c4bbbf1d27)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `b579d38a-3ce5-4b1b-b94e-b0c4bbbf1d27` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/futureoption/order` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 주간/야간 선물옵션 주문서비스를 확인할 수 있습니다 |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 선물옵션 정상주문 | [CFOAT00100](orders.md#tr-CFOAT00100) | 10 | 10 | 10 |
| 선물옵션 정정주문 | [CFOAT00200](orders.md#tr-CFOAT00200) | 10 | 10 | 10 |
| 선물옵션 취소주문 | [CFOAT00300](orders.md#tr-CFOAT00300) | 10 | 10 | 10 |
| 선물옵션 옵션매도시 주문증거금조회(옵션매도시 1계약당 주문증거금) | [CFOBQ10800](orders.md#tr-CFOBQ10800) | 1 | 1 | 10 |
| KRX야간파생 위탁 신규 주문 | [CCENT00100](orders.md#tr-CCENT00100) | 5 | 5 | 5 |
| KRX야간파생 위탁 정정 주문 | [CCENT00200](orders.md#tr-CCENT00200) | 5 | 5 | 5 |
| KRX야간파생 위탁 취소 주문 | [CCENT00300](orders.md#tr-CCENT00300) | 5 | 5 | 5 |

---

<a id="tr-CFOAT00100"></a>
## `CFOAT00100` 선물옵션 정상주문

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
| `CFOAT00100InBlock1` | CFOAT00100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | 1@매도<br/>2@매수 |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | 00@지정가<br/>03@시장가<br/>05@조건부지정가<br/>06@최유리지정가<br/>10@지정가(IOC)<br/>20@지정가(FOK)<br/>13@시장가(IOC)<br/>23@시장가(FOK)<br/>16@최유리지정가(IOC)<br/>26@최유리지정가(FOK) |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |


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
| `CFOAT00100OutBlock1` | CFOAT00100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FnoOrdPtnCode` | 선물옵션주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoTrdPtnCode` | 선물옵션거래유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DscusBnsCmpltTime` | 협의매매완료시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-OrdSeqno` | 주문일련번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PtflNo` | 포트폴리오번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BskNo` | 바스켓번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TrchNo` | 트렌치번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ItemNo` | 항목번호 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-MgempNo` | 관리사원번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FundId` | 펀드ID | String | Y | 12 | - |
| `&nbsp;&nbsp;-FundOrdNo` | 펀드주문번호 | Number | Y | 10 | - |
| `CFOAT00100OutBlock2` | CFOAT00100OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdMgn` | 현금주문증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOAT00100InBlock1" : {
    "FnoIsuNo" : "101T9000",
    "BnsTpCode" : "2",
    "FnoOrdprcPtnCode" : "00",
    "FnoOrdPrc" : 342.25,
    "OrdQty" : 5
  }
}
```

### 응답 Example

```json
{
   "rsp_cd": "00040",
    "rsp_msg": "매수 주문이 완료되었습니다.",
    "CFOAT00100OutBlock2": {
        "IsuNm": "P 202306 322.5",
        "OrdMgn": 600000,
        "OrdAbleQty": 0,
        "RecCnt": 1,
        "OrdAbleAmt": 9978355752,
        "MnyOrdAbleAmt": 9988627876,
        "AcntNm": "임동무",
        "MnyOrdMgn": 600000,
        "BrnNm": "",
        "OrdNo": 69007
    },

    "CFOAT00100OutBlock1": {
        "FnoIsuNo": "KR4301T63220",
        "FnoOrdPtnCode": "00",
        "BnsTpCode": "2",
        "DscusBnsCmpltTime": "",
        "FnoOrdprcPtnCode": "00",
        "FnoOrdPrc": "2.40000000",
        "TrchNo": 0,
        "MgempNo": "",
        "BskNo": 0,
        "OrdMktCode": "40",
        "OrdQty": 1,
        "CommdaCode": "40",
        "RecCnt": 1,
        "FnoTrdPtnCode": "03",
        "OrdSeqno": 0,
        "ItemNo": 0,
        "OpDrtnNo": "",
        "FundId": "",
        "AcntNo": "20001652603",
        "Pwd": "********",
        "PtflNo": 0,
        "FundOrdNo": 0,
        "GrpId": ""
    }
}
```

---

<a id="tr-CFOAT00200"></a>
## `CFOAT00200` 선물옵션 정정주문

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
| `CFOAT00200InBlock1` | CFOAT00200InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | 00@지정가<br/>03@시장가<br/>05@조건부지정가<br/>06@최유리지정가<br/>10@지정가(IOC)<br/>20@지정가(FOK)<br/>13@시장가(IOC)<br/>23@시장가(FOK)<br/>16@최유리지정가(IOC)<br/>26@최유리지정가(FOK) |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-MdfyQty` | 정정수량 | Number | Y | 16 | - |


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
| `CFOAT00200OutBlock1` | CFOAT00200OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-FnoOrdPtnCode` | 선물옵션주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-MdfyQty` | 정정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DscusBnsCmpltTime` | 협의매매완료시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-OrdSeqno` | 주문일련번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PtflNo` | 포트폴리오번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BskNo` | 바스켓번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TrchNo` | 트렌치번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ItemNo` | 아이템번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-MgempNo` | 관리사원번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FundId` | 펀드ID | String | Y | 12 | - |
| `&nbsp;&nbsp;-FundOrgOrdNo` | 펀드원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FundOrdNo` | 펀드주문번호 | Number | Y | 10 | - |
| `CFOAT00200OutBlock2` | CFOAT00200OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdMgn` | 현금주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOAT00200InBlock1" : {
    "FnoIsuNo" : "101T9000",
    "OrgOrdNo" : 67005,
    "FnoOrdprcPtnCode" : "00",
    "FnoOrdPrc" : 342.3,
    "MdfyQty" : 1
  }
}
```

### 응답 Example

```json
{
    "CFOAT00200OutBlock1": {
        "FnoIsuNo": "KR4101T60006",
        "FnoOrdPtnCode": "00",
        "DscusBnsCmpltTime": "",
        "FnoOrdprcPtnCode": "00",
        "FnoOrdPrc": "342.30000000",
        "TrchNo": 0,
        "OrgOrdNo": 69039,
        "MgempNo": "",
        "BskNo": 0,
        "OrdMktCode": "40",
        "CommdaCode": "40",
        "RecCnt": 1,
        "FundOrgOrdNo": 0,
        "MdfyQty": 1,
        "OrdSeqno": 0,
        "ItemNo": 0,
        "FundId": "",
        "AcntNo": "20277932702",
        "Pwd": "********",
        "PtflNo": 0,
        "FundOrdNo": 0,
        "GrpId": ""
    },
    "rsp_cd": "00132",
    "rsp_msg": "정정주문이 완료되었습니다.",
    "CFOAT00200OutBlock2": {
        "IsuNm": "F 202306",
        "OrdMgn": 50748360,
        "OrdAbleQty": 0,
        "RecCnt": 1,
        "OrdAbleAmt": 167347436,
        "MnyOrdAbleAmt": 214924024,
        "AcntNm": "충조감",
        "MnyOrdMgn": 25374179,
        "BrnNm": "",
        "OrdNo": 69041
    }
}
```

---

<a id="tr-CFOAT00300"></a>
## `CFOAT00300` 선물옵션 취소주문

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
| `CFOAT00300InBlock1` | CFOAT00300InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-CancQty` | 취소수량 | Number | Y | 16 | - |


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
| `CFOAT00300OutBlock1` | CFOAT00300OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-FnoOrdPtnCode` | 선물옵션주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-CancQty` | 취소수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DscusBnsCmpltTime` | 협의매매완료시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-OrdSeqno` | 주문일련번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PtflNo` | 포트폴리오번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BskNo` | 바스켓번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TrchNo` | 트렌치번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ItemNo` | 아이템번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-MgempNo` | 관리사원번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FundId` | 펀드ID | String | Y | 12 | - |
| `&nbsp;&nbsp;-FundOrgOrdNo` | 펀드원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FundOrdNo` | 펀드주문번호 | Number | Y | 10 | - |
| `CFOAT00300OutBlock2` | CFOAT00300OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdMgn` | 현금주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOAT00300InBlock1" : {
    "FnoIsuNo" : "101T9000",
    "OrgOrdNo" : 68002,
    "CancQty" : 2
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00156",
    "rsp_msg": "취소주문이 완료되었습니다.",
    "CFOAT00300OutBlock2": {
        "IsuNm": "F 202306",
        "OrdMgn": 0,
        "OrdAbleQty": 0,
        "RecCnt": 1,
        "OrdAbleAmt": 0,
        "MnyOrdAbleAmt": 0,
        "AcntNm": "충조감",
        "MnyOrdMgn": 0,
        "BrnNm": "",
        "OrdNo": 69044
    },
    "CFOAT00300OutBlock1": {
        "CancQty": 2,
        "FnoIsuNo": "101T6000",
        "FnoOrdPtnCode": "00",
        "DscusBnsCmpltTime": "",
        "TrchNo": 0,
        "OrgOrdNo": 69043,
        "MgempNo": "",
        "BskNo": 0,
        "OrdMktCode": "40",
        "CommdaCode": "40",
        "RecCnt": 1,
        "FundOrgOrdNo": 0,
        "OrdSeqno": 0,
        "ItemNo": 0,
        "FundId": "",
        "AcntNo": "20277932702",
        "Pwd": "********",
        "PtflNo": 0,
        "FundOrdNo": 0,
        "GrpId": ""
    }
}
```

---

<a id="tr-CFOBQ10800"></a>
## `CFOBQ10800` 선물옵션 옵션매도시 주문증거금조회(옵션매도시 1계약당 주문증거금)

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
| `CFOBQ10800InBlock1` | CFOBQ10800InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-SpclDtPtnCode` | 특별일자유형코드 | String | Y | 3 | 기본 공백, 단, 위클리옵션은 월요일 "MON" , 목요일 "THR" |
| `&nbsp;&nbsp;-SettWklyCnt` | 결제주간수 | String | Y | 2 | 기본 공백, 단, 위클리옵션은 해당 주물 "W1", "W3", "W4" |
| `&nbsp;&nbsp;-DueYymm` | 만기년월 | String | Y | 6 | 예)2023년 05월물 <br/>단, 위클리옵션은 공백 |
| `&nbsp;&nbsp;-IsuSmclssCode` | 종목소분류코드 | String | Y | 3 | 501@코스피200<br/>505@미니코스피200<br/>506@코스닥150<br/>509@위클리 ( 월, 목 무관 )<br/>5AF@위클리 ( 월, 목 무관 ) |
| `&nbsp;&nbsp;-IsuMdclssCode` | 종목중분류코드 | String | Y | 2 | 00@전체<br/>01@주가지수<br/>02@개별주식<br/>03@가공채권<br/>04@통화<br/>05@상품<br/>06@금리<br/>10@FLEX |


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
| `CFOBQ10800OutBlock1` | CFOBQ10800OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-SpclDtPtnCode` | 특별일자유형코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-IsuMdclssCode` | 종목중분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuSmclssCode` | 종목소분류코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-DueYymm` | 만기년월 | String | Y | 6 | - |
| `&nbsp;&nbsp;-SettWklyCnt` | 결제주간수 | String | Y | 2 | - |
| `CFOBQ10800OutBlock2` | CFOBQ10800OutBlock2 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-ElwXrcPrc` | 행사가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-HanglIsuNm1` | 한글종목명1 | String | Y | 40 | - |
| `&nbsp;&nbsp;-TpNm1` | 구분명1 | String | Y | 40 | - |
| `&nbsp;&nbsp;-UpOptRegulThrprc` | 상승옵션조정이론가 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-Thrprc1` | 이론가1 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-BasePrc1` | 기준가1 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-OrdMgn1` | 주문증거금액1 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoIsuNo0` | 선물옵션종목번호0 | String | Y | 12 | - |
| `&nbsp;&nbsp;-HanglIsuNm2` | 한글종목명2 | String | Y | 40 | - |
| `&nbsp;&nbsp;-TpNm2` | 구분명2 | String | Y | 40 | - |
| `&nbsp;&nbsp;-DownOptRegulThrprc` | 하락옵션조정이론가 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-Thrprc2` | 이론가2 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-BasePrc2` | 기준가2 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-OrdMgn2` | 주문증거금액2 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOBQ10800InBlock1" : {
    "IsuMdclssCode" : "00",
    "IsuSmclssCode" : "501",
    "DueYymm" : "202309",
    "SettWklyCnt" : "",
    "SpclDtPtnCode" : "" 
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CFOBQ10800OutBlock1": {
        "IsuMdclssCode": "00",
        "IsuSmclssCode": "501",
        "RecCnt": 1,
        "SpclDtPtnCode": "",
        "DueYymm": "202309",
        "SettWklyCnt": ""
    },
    "CFOBQ10800OutBlock2": [
        {
            "FnoIsuNo": "201T9160",
            "FnoIsuNo0": "301T9160",
            "OrdMgn1": 6866198,
            "TpNm2": "최소증거금",
            "HanglIsuNm1": "코스피200 C 202309 160.0",
            "TpNm1": "최대이론가",
            "OrdMgn2": 250000,
            "HanglIsuNm2": "코스피200 P 202309 160.0",
            "DownOptRegulThrprc": "0.05457800",
            "Thrprc1": "211.61479300",
            "Thrprc2": "0.20282900",
            "UpOptRegulThrprc": "238.41854400",
            "ElwXrcPrc": "160.00",
            "BasePrc1": "184.15",
            "BasePrc2": "0.01"
        },
        {
            "FnoIsuNo": "201T9465",
            "FnoIsuNo0": "301T9465",
            "OrdMgn1": 250000,
            "TpNm2": "최대이론가",
            "HanglIsuNm1": "코스피200 C 202309 465.0",
            "TpNm1": "최소증거금",
            "OrdMgn2": 6728153,
            "HanglIsuNm2": "코스피200 P 202309 465.0",
            "DownOptRegulThrprc": "172.54695000",
            "Thrprc1": "0.62100900",
            "Thrprc2": "145.71261000",
            "UpOptRegulThrprc": "0.85587700",
            "ElwXrcPrc": "465.00",
            "BasePrc1": "0.01",
            "BasePrc2": "118.80"
        }
    ],
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CCENT00100"></a>
## `CCENT00100` KRX야간파생 위탁 신규 주문

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | - |
| `authorization` | 접근토큰 | String | Y | 1000 | - |
| `tr_cd` | 거래 CD | String | Y | 10 | - |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | - |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | - |
| `mac_address` | MAC 주소 | String | Y | 12 | - |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CCENT00100InBlock1` | CCENT00100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | 1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | 00@지정가<br/>03@시장가<br/>05@조건부지정가<br/>06@최유리지정가<br/>10@지정가(IOC)<br/>20@지정가(FOK)<br/>13@시장가(IOC)<br/>23@시장가(FOK)<br/>16@최유리지정가(IOC)<br/>26@최유리지정가(FOK) |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | - |
| `tr_cd` | 거래 CD | String | Y | 10 | - |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | - |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | - |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CCENT00100OutBlock1` | CCENT00100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FnoOrdPtnCode` | 선물옵션주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoTrdPtnCode` | 선물옵션거래유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DscusBnsCmpltTime` | 협의매매완료시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-OrdSeqno` | 주문일련번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PtflNo` | 포트폴리오번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BskNo` | 바스켓번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TrchNo` | 트렌치번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ItemNo` | 항목번호 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-MgempNo` | 관리사원번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FundId` | 펀드ID | String | Y | 12 | - |
| `&nbsp;&nbsp;-FundOrdNo` | 펀드주문번호 | Number | Y | 10 | - |
| `CCENT00100OutBlock2` | CCENT00100OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdMgn` | 현금주문증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CCENT00100InBlock1" : {
    "FnoIsuNo" : "101W6000",
    "BnsTpCode" : "2",
    "FnoOrdprcPtnCode" : "00",
    "FnoOrdPrc" : 416,
    "OrdQty" : 1
  }
}
```

### 응답 Example

```json
{
	"CCENT00100OutBlock1": {
		"RecCnt": 1,
		"OrdMktCode": "40",
		"AcntNo": "***********",
		"Pwd": "********",
		"FnoIsuNo": "101W6000",
		"BnsTpCode": "2",
		"FnoOrdPtnCode": "00",
		"FnoOrdprcPtnCode": "00",
		"FnoTrdPtnCode": "03",
		"FnoOrdPrc": "416.00000000",
		"OrdQty": 1,
		"CommdaCode": "40",
		"DscusBnsCmpltTime": "",
		"GrpId": "",
		"OrdSeqno": 0,
		"PtflNo": 0,
		"BskNo": 0,
		"TrchNo": 0,
		"ItemNo": 0,
		"OpDrtnNo": "",
		"MgempNo": "",
		"FundId": "",
		"FundOrdNo": 0
	},
	"CCENT00100OutBlock2": {
		"RecCnt": 1,
		"OrdNo": 14,
		"BrnNm": "",
		"AcntNm": "***",
		"IsuNm": "F 202506",
		"OrdAbleAmt": 10301798,
		"MnyOrdAbleAmt": 22332251,
		"OrdMgn": 20050754,
		"MnyOrdMgn": 10025376,
		"OrdAbleQty": 0
	},
	"rsp_cd": "00040",
	"rsp_msg": "매수 주문이 완료되었습니다."
}
```

---

<a id="tr-CCENT00200"></a>
## `CCENT00200` KRX야간파생 위탁 정정 주문

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | - |
| `authorization` | 접근토큰 | String | Y | 1000 | - |
| `tr_cd` | 거래 CD | String | Y | 10 | - |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | - |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | - |
| `mac_address` | MAC 주소 | String | Y | 12 | - |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CCENT00200InBlock1` | CCENT00200InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | 00@지정가<br/>03@시장가<br/>05@조건부지정가<br/>06@최유리지정가<br/>10@지정가(IOC)<br/>20@지정가(FOK)<br/>13@시장가(IOC)<br/>23@시장가(FOK)<br/>16@최유리지정가(IOC)<br/>26@최유리지정가(FOK) |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-MdfyQty` | 정정수량 | Number | Y | 16 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | - |
| `tr_cd` | 거래 CD | String | Y | 10 | - |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | - |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | - |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CCENT00200OutBlock1` | CCENT00200OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-FnoOrdPtnCode` | 선물옵션주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-MdfyQty` | 정정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DscusBnsCmpltTime` | 협의매매완료시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-OrdSeqno` | 주문일련번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PtflNo` | 포트폴리오번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BskNo` | 바스켓번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TrchNo` | 트렌치번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ItemNo` | 아이템번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-MgempNo` | 관리사원번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FundId` | 펀드ID | String | Y | 12 | - |
| `&nbsp;&nbsp;-FundOrgOrdNo` | 펀드원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FundOrdNo` | 펀드주문번호 | Number | Y | 10 | - |
| `CCENT00200OutBlock2` | CCENT00200OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdMgn` | 현금주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CCENT00200InBlock1" : {
    "FnoIsuNo" : "101W6000",
    "OrgOrdNo" : 14,
    "FnoOrdprcPtnCode" : "00",
    "FnoOrdPrc" : 416.30,
    "MdfyQty" : 1
  }
}
```

### 응답 Example

```json
{
	"CCENT00200OutBlock1": {
		"RecCnt": 1,
		"OrdMktCode": "40",
		"AcntNo": "***********",
		"Pwd": "********",
		"FnoIsuNo": "101W6000",
		"FnoOrdPtnCode": "00",
		"OrgOrdNo": 14,
		"FnoOrdprcPtnCode": "00",
		"FnoOrdPrc": "416.30000000",
		"MdfyQty": 1,
		"CommdaCode": "40",
		"DscusBnsCmpltTime": "",
		"GrpId": "",
		"OrdSeqno": 0,
		"PtflNo": 0,
		"BskNo": 0,
		"TrchNo": 0,
		"ItemNo": 0,
		"MgempNo": "",
		"FundId": "",
		"FundOrgOrdNo": 0,
		"FundOrdNo": 0
	},
	"CCENT00200OutBlock2": {
		"RecCnt": 1,
		"OrdNo": 15,
		"BrnNm": "",
		"AcntNm": "***",
		"IsuNm": "F 202506",
		"OrdAbleAmt": 10301798,
		"MnyOrdAbleAmt": 22332251,
		"OrdMgn": 20050754,
		"MnyOrdMgn": 10025376,
		"OrdAbleQty": 0
	},
	"rsp_cd": "00132",
	"rsp_msg": "정정주문이 완료되었습니다."
}
```

---

<a id="tr-CCENT00300"></a>
## `CCENT00300` KRX야간파생 위탁 취소 주문

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | - |
| `authorization` | 접근토큰 | String | Y | 1000 | - |
| `tr_cd` | 거래 CD | String | Y | 10 | - |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | - |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | - |
| `mac_address` | MAC 주소 | String | Y | 12 | - |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CCENT00300InBlock1` | CCENT00300InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-CancQty` | 취소수량 | Number | Y | 16 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | - |
| `tr_cd` | 거래 CD | String | Y | 10 | - |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | - |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | - |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CCENT00300OutBlock1` | CCENT00300OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-FnoOrdPtnCode` | 선물옵션주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-CancQty` | 취소수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DscusBnsCmpltTime` | 협의매매완료시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-OrdSeqno` | 주문일련번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PtflNo` | 포트폴리오번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BskNo` | 바스켓번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TrchNo` | 트렌치번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ItemNo` | 아이템번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-MgempNo` | 관리사원번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FundId` | 펀드ID | String | Y | 12 | - |
| `&nbsp;&nbsp;-FundOrgOrdNo` | 펀드원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-FundOrdNo` | 펀드주문번호 | Number | Y | 10 | - |
| `CCENT00300OutBlock2` | CCENT00300OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdMgn` | 현금주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CCENT00300InBlock1" : {
    "FnoIsuNo" : "101W6000",
    "OrgOrdNo" : 15,
    "CancQty" : 1
  }
}
```

### 응답 Example

```json
{
	"CCENT00300OutBlock1": {
		"RecCnt": 1,
		"OrdMktCode": "40",
		"AcntNo": "***********",
		"Pwd": "********",
		"FnoIsuNo": "101W6000",
		"FnoOrdPtnCode": "00",
		"OrgOrdNo": 15,
		"CancQty": 1,
		"CommdaCode": "40",
		"DscusBnsCmpltTime": "",
		"GrpId": "",
		"OrdSeqno": 0,
		"PtflNo": 0,
		"BskNo": 0,
		"TrchNo": 0,
		"ItemNo": 0,
		"MgempNo": "",
		"FundId": "",
		"FundOrgOrdNo": 0,
		"FundOrdNo": 0
	},
	"CCENT00300OutBlock2": {
		"RecCnt": 1,
		"OrdNo": 16,
		"BrnNm": "",
		"AcntNm": "***",
		"IsuNm": "F 202506",
		"OrdAbleAmt": 0,
		"MnyOrdAbleAmt": 0,
		"OrdMgn": 0,
		"MnyOrdMgn": 0,
		"OrdAbleQty": 0
	},
	"rsp_cd": "00156",
	"rsp_msg": "취소주문이 완료되었습니다."
}
```
