# [해외주식] 주문

> LS증권 OPEN API 정의서 · 그룹: **해외주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=cdb7e1bc-f7c5-425c-8248-aa83dbb6919f&api_id=6bafc43c-6080-4541-bfc2-c2608b269ca0)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `6bafc43c-6080-4541-bfc2-c2608b269ca0` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/overseas-stock/order` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외주식 주문서비스를 확인할 수 있습니다 |

## TR 목록 (4건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 미국시장주문 API | [COSAT00301](orders.md#tr-COSAT00301) | 10 | 10 | 10 |
| 미국시장정정주문 API | [COSAT00311](orders.md#tr-COSAT00311) | 10 | 10 | 10 |
| 해외증권 매도상환주문(미국) | [COSMT00300](orders.md#tr-COSMT00300) | 1 | 1 | 1 |
| 해외주식 예약주문 등록 및 취소 | [COSAT00400](orders.md#tr-COSAT00400) | 1 | 1 | 1 |

---

<a id="tr-COSAT00301"></a>
## `COSAT00301` 미국시장주문 API

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth토큰이필요한API경우발급한AccessToken을설정하기위한RequestHeaederParameter |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |
| `mac_address` | MAC주소 | String | Y | 12 | 법인인경우필수세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `COSAT00301InBlock1` | COSAT00301InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | 00001 |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | 01 : 매도주문<br/>02 : 매수주문<br/>08 : 취소주문 |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | 취소주문인 경우만 필수 입력 |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | 81 : 뉴욕거래소<br/>82 : NASDAQ |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | 단축종목코드<br/>ex.TSLA |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Number | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | 00@지정가<br/>M1@LOO<br/>M2@LOC<br/><br/>매도인경우 호가유형 확대<br/>03@시장가<br/>M3@MOO<br/>M4@MOC |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `COSAT00301OutBlock1` | COSAT00301OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Number | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-RegCommdaCode` | 등록통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |
| `COSAT00301OutBlock2` | COSAT00301OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |


### 요청 Example

```json
{
  "COSAT00301InBlock1": {
    "RecCnt": 1,
    "OrdPtnCode": "02",
    "OrdMktCode": "82",
    "IsuNo": "PLTR",
    "OrdQty": 5,
    "OvrsOrdPrc": 70,
    "OrdprcPtnCode": "00",
    "BrkTpCode": ""
  }
}
```

---

<a id="tr-COSAT00311"></a>
## `COSAT00311` 미국시장정정주문 API

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth토큰이필요한API경우발급한AccessToken을설정하기위한RequestHeaederParameter |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |
| `mac_address` | MAC주소 | String | Y | 12 | 법인인경우필수세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `COSAT00311InBlock1` | COSAT00311InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | 00001 |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | 07@정정주문 |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | 81@뉴욕거래소<br/>82@NASDAQ |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | 0 입력 |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Number | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `&nbsp;&nbsp;-COSAT00311OutBlock1` | COSAT00311OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-RegCommdaCode` | 등록통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-COSAT00311OutBlock2` | COSAT00311OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |


---

<a id="tr-COSMT00300"></a>
## `COSMT00300` 해외증권 매도상환주문(미국)

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth토큰이필요한API경우발급한AccessToken을설정하기위한RequestHeaederParameter |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |
| `mac_address` | MAC주소 | String | Y | 12 | 법인인경우필수세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `&nbsp;&nbsp;-COSMT00300InBlock1` | COSMT00300InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-MgntrnCode` | 신용거래코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-COSMT00300OutBlock1` | COSMT00300OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-RegCommdaCode` | 등록통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-MgntrnCode` | 신용거래코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-COSMT00300OutBlock2` | COSMT00300OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |


---

<a id="tr-COSAT00400"></a>
## `COSAT00400` 해외주식 예약주문 등록 및 취소

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth토큰이필요한API경우발급한AccessToken을설정하기위한RequestHeaederParameter |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |
| `mac_address` | MAC주소 | String | Y | 12 | 법인인경우필수세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `&nbsp;&nbsp;-COSAT00400InBlock1` | COSAT00400InBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-TrxTpCode` | 처리구분코드 | String | Y | 1 | 0 : 등록 <br/>2 : 취소 |
| `&nbsp;&nbsp;-CntryCode` | 국가코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RsvOrdInptDt` | 예약주문입력일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdNo` | 예약주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FcurrMktCode` | 외화시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | 00 : 지정가<br/>A2 : TWAP<br/>A3 : VWAP |
| `&nbsp;&nbsp;-RsvOrdSrtDt` | 예약주문시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdEndDt` | 예약주문종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdCndiCode` | 예약주문조건코드 | String | Y | 2 | 00 : 일반예약주문<br/>01 : 동일조건 반복예약주문<br/>02 : 미체결수량 반복예약주문 |
| `&nbsp;&nbsp;-MgntrnCode` | 신용거래코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래CD | String | Y | 10 | LS증권거래코드 |
| `tr_cont` | 연속거래여부 | String | Y | 1 | 연속거래여부Y:연속○N:연속× |
| `tr_cont_key` | 연속거래Key | String | Y | 18 | 연속일경우그전에내려온연속키값올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `&nbsp;&nbsp;-COSAT00400OutBlock1` | COSAT00400OutBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-TrxTpCode` | 처리구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CntryCode` | 국가코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RsvOrdInptDt` | 예약주문입력일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdNo` | 예약주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FcurrMktCode` | 외화시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-RegCommdaCode` | 등록통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-RsvOrdSrtDt` | 예약주문시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdEndDt` | 예약주문종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdCndiCode` | 예약주문조건코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-MgntrnCode` | 신용거래코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-COSAT00400OutBlock2` | COSAT00400OutBlock2 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-RsvOrdNo` | 예약주문번호 | Object | Y | 10 | - |
