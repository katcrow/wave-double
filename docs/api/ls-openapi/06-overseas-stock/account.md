# [해외주식] 계좌

> LS증권 OPEN API 정의서 · 그룹: **해외주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=cdb7e1bc-f7c5-425c-8248-aa83dbb6919f&api_id=45b5abe1-a6e1-4833-a9cb-7eb0c408dba3)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `45b5abe1-a6e1-4833-a9cb-7eb0c408dba3` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/overseas-stock/accno` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외주식 계좌별 거래내역 및 잔고 등 계좌에 관련된 서비스를 확인할 수 있습니다. |

## TR 목록 (4건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외주식 계좌주문체결내역조회 API | [COSAQ00102](account.md#tr-COSAQ00102) | 1 | 1 | 10 |
| 예약주문 처리결과 조회 | [COSAQ01400](account.md#tr-COSAQ01400) | 1 | 1 | 10 |
| 해외주식 종합잔고평가 API | [COSOQ00201](account.md#tr-COSOQ00201) | 1 | 1 | 10 |
| 해외주식 예수금 조회 API | [COSOQ02701](account.md#tr-COSOQ02701) | 1 | 1 | 10 |

---

<a id="tr-COSAQ00102"></a>
## `COSAQ00102` 해외주식 계좌주문체결내역조회 API

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
| `&nbsp;&nbsp;-COSAQ00102InBlock1` | COSAQ00102InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | 00001 |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | 1@계좌별 |
| `&nbsp;&nbsp;-BkseqTpCode` | 역순구분코드 | String | Y | 1 | 1@역순<br/>2@정순 |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | 81@뉴욕거래소<br/>82@NASDAQ |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 0@전체<br/>1@매도<br/>2@매수 |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-SrtOrdNo` | 시작주문번호 | Object | Y | 10 | 역순인경우 999999999<br/>정순인 경우 0 |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ExecYn` | 체결여부 | String | Y | 1 | 0@전체<br/>1@체결<br/>2@미체결 |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | 000@전체<br/>USD@미국 |
| `&nbsp;&nbsp;-ThdayBnsAppYn` | 당일매매적용여부 | String | Y | 1 | 0@미적용<br/>1@적용 |
| `&nbsp;&nbsp;-LoanBalHldYn` | 대출잔고보유여부 | String | Y | 1 | 0@ 전체<br/>1@ 대출잔고만 |


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
| `&nbsp;&nbsp;-COSAQ00102OutBlock1` | COSAQ00102OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BkseqTpCode` | 역순구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-SrtOrdNo` | 시작주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ExecYn` | 체결여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-ThdayBnsAppYn` | 당일매매적용여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LoanBalHldYn` | 대출잔고보유여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-COSAQ00102OutBlock2` | COSAQ00102OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-JpnMktHanglIsuNm` | 일본시장한글종목명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-MgmtBrnNm` | 관리지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-SellExecFcurrAmt` | 매도체결외화금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-SellExecQty` | 매도체결수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-BuyExecFcurrAmt` | 매수체결외화금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-BuyExecQty` | 매수체결수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-COSAQ00102OutBlock3` | COSAQ00102OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-MgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-ExecTime` | 체결시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-OrdTime` | 주문시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Object | Y | 10 | - |
| `&nbsp;&nbsp;-ShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-OrdTrxPtnNm` | 주문처리유형명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-OrdTrxPtnCode` | 주문처리유형코드 | Object | Y | 9 | - |
| `&nbsp;&nbsp;-MrcAbleQty` | 정정취소가능수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 22.7 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsExecPrc` | 해외체결가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrdprcPtnNm` | 호가유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdPtnNm` | 주문유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-MrcTpCode` | 정정취소구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MrcTpNm` | 정정취소구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-AllExecQty` | 전체체결수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-MktNm` | 시장명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-CommdaNm` | 통신매체명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-JpnMktHanglIsuNm` | 일본시장한글종목명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-CnfQty` | 확인수량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BrkTpCode` | 중개인구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OppBrkNm` | 상대중개인명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-LoanAmt` | 대출금액 | Object | Y | 16 | - |


### 요청 Example

```json
{
  "COSAQ00102InBlock1": {
    "RecCnt": 1,
    "QryTpCode": "1",
    "BkseqTpCode": "1",
    "OrdMktCode": "82",
    "BnsTpCode": "0",
    "IsuNo": "TSLA",
    "SrtOrdNo": 999999999,
    "OrdDt": "20250407",
    "ExecYn": "0",
    "CrcyCode": "000",
    "ThdayBnsAppYn": "0",
    "LoanBalHldYn": "0"
  }
}
```

### 응답 Example

```json
{
	"COSAQ00102OutBlock1": {
		"RecCnt": 1,
		"QryTpCode": "1",
		"BkseqTpCode": "1",
		"OrdMktCode": "82",
		"AcntNo": "12345678900",
		"Pwd": "********",
		"BnsTpCode": "0",
		"IsuNo": "",
		"SrtOrdNo": 999999999,
		"OrdDt": "20250407",
		"ExecYn": "0",
		"CrcyCode": "000",
		"ThdayBnsAppYn": "0",
		"LoanBalHldYn": "0"
	},
	"COSAQ00102OutBlock2": {
		"RecCnt": 1,
		"AcntNm": "",
		"JpnMktHanglIsuNm": "",
		"MgmtBrnNm": "회사전체",
		"SellExecFcurrAmt": "0.0000",
		"SellExecQty": 0,
		"BuyExecFcurrAmt": "3300.0000",
		"BuyExecQty": 15
	},
	"COSAQ00102OutBlock3": [
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "224041436",
			"OrdNo": 141,
			"OrgOrdNo": 0,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "취소완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "200.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수",
			"OrdPtnCode": "02",
			"MrcTpCode": "",
			"MrcTpNm": "정상",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 0,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "223819132",
			"OrdTime": "212742355",
			"OrdNo": 94,
			"OrgOrdNo": 64,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "정정완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 15,
			"OvrsOrdPrc": "220.0000000",
			"ExecQty": 15,
			"OvrsExecPrc": "220.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수정정",
			"OrdPtnCode": "07",
			"MrcTpCode": "",
			"MrcTpNm": "정정",
			"AllExecQty": 15,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 15,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "211844358",
			"OrdNo": 87,
			"OrgOrdNo": 0,
			"ShtnIsuNo": "PLTR",
			"OrdTrxPtnNm": "취소완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 25,
			"OvrsOrdPrc": "65.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수",
			"OrdPtnCode": "02",
			"MrcTpCode": "",
			"MrcTpNm": "정상",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "팔란티어 테크",
			"UnercQty": 0,
			"CnfQty": 0,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "PLTR",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "204012782",
			"OrdNo": 64,
			"OrgOrdNo": 0,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "접수완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 15,
			"OvrsOrdPrc": "210.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수",
			"OrdPtnCode": "02",
			"MrcTpCode": "",
			"MrcTpNm": "정상",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 0,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "203932980",
			"OrdNo": 63,
			"OrgOrdNo": 60,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "취소완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "0.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수취소",
			"OrdPtnCode": "08",
			"MrcTpCode": "",
			"MrcTpNm": "취소",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 10,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "203928642",
			"OrdNo": 62,
			"OrgOrdNo": 61,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "취소완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "0.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수취소",
			"OrdPtnCode": "08",
			"MrcTpCode": "",
			"MrcTpNm": "취소",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 10,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "203917598",
			"OrdNo": 61,
			"OrgOrdNo": 0,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "접수완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "200.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수",
			"OrdPtnCode": "02",
			"MrcTpCode": "",
			"MrcTpNm": "정상",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 0,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "203851736",
			"OrdNo": 60,
			"OrgOrdNo": 57,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "정정완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "200.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수정정",
			"OrdPtnCode": "07",
			"MrcTpCode": "",
			"MrcTpNm": "정정",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 10,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "203426976",
			"OrdNo": 57,
			"OrgOrdNo": 55,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "정정완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "220.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수정정",
			"OrdPtnCode": "07",
			"MrcTpCode": "",
			"MrcTpNm": "정정",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 10,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		},
		{
			"MgmtBrnNo": "209",
			"AcntNo": "12345678900",
			"AcntNm": "***",
			"ExecTime": "",
			"OrdTime": "203222932",
			"OrdNo": 55,
			"OrgOrdNo": 0,
			"ShtnIsuNo": "TSLA",
			"OrdTrxPtnNm": "접수완료",
			"OrdTrxPtnCode": 0,
			"MrcAbleQty": 0,
			"OrdQty": 10,
			"OvrsOrdPrc": "225.0000000",
			"ExecQty": 0,
			"OvrsExecPrc": "0.0000000",
			"OrdprcPtnCode": "00",
			"OrdprcPtnNm": "지정가",
			"OrdPtnNm": "매수",
			"OrdPtnCode": "02",
			"MrcTpCode": "",
			"MrcTpNm": "정상",
			"AllExecQty": 0,
			"CommdaCode": "51",
			"OrdMktCode": "82",
			"MktNm": "NASDAQ",
			"CommdaNm": "투혼(iOS)",
			"JpnMktHanglIsuNm": "테슬라",
			"UnercQty": 0,
			"CnfQty": 0,
			"CrcyCode": "USD",
			"RegMktCode": "82",
			"IsuNo": "TSLA",
			"BrkTpCode": "18",
			"OppBrkNm": "MORGAN STANLEY",
			"BnsTpCode": "2",
			"LoanDt": "",
			"LoanAmt": 0
		}
	],
	"rsp_cd": "00136",
	"rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-COSAQ01400"></a>
## `COSAQ01400` 예약주문 처리결과 조회

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
| `COSAQ01400InBlock1` | COSAQ01400InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CntryCode` | 국가코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SrtDt` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-EndDt` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-RsvOrdCndiCode` | 예약주문조건코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-RsvOrdStatCode` | 예약주문상태코드 | String | Y | 1 | - |


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
| `COSAQ01400OutBlock1` | COSAQ01400OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CntryCode` | 국가코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SrtDt` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-EndDt` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-RsvOrdCndiCode` | 예약주문조건코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-RsvOrdStatCode` | 예약주문상태코드 | String | Y | 1 | - |
| `COSAQ01400OutBlock2` | COSAQ01400OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-RsvOrdInptDt` | 예약주문입력일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RsvOrdNo` | 예약주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-JpnMktHanglIsuNm` | 일본시장한글종목명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdprcPtnNm` | 호가유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OvrsOrdPrc` | 해외주문가 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TotExecQty` | 총체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RsvOrdStatCode` | 예약주문상태코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MktTpNm` | 시장구분명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-ErrCnts` | 오류내용 | String | Y | 100 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-MgntrnCode` | 신용거래코드 | String | Y | 3 | - |


### 요청 Example

```json
{
  "COSAQ01400InBlock1": {
    "RecCnt": 1,
    "QryTpCode": "1",
    "CntryCode": "001",
    "SrtDt": "20250401",
    "EndDt": "20250426",
    "BnsTpCode": "0",
    "RsvOrdCndiCode": "00",
    "RsvOrdStatCode": "1"
  }
}
```

### 응답 Example

```json
{
	"COSAQ01400OutBlock1": {
		"RecCnt": 1,
		"QryTpCode": "1",
		"CntryCode": "001",
		"AcntNo": "***********",
		"Pwd": "********",
		"SrtDt": "20250401",
		"EndDt": "20250426",
		"BnsTpCode": "0",
		"RsvOrdCndiCode": "00",
		"RsvOrdStatCode": "1"
	},
	"COSAQ01400OutBlock2": [],
	"rsp_cd": "00200",
	"rsp_msg": "조회내역이 없습니다."
}
```

---

<a id="tr-COSOQ00201"></a>
## `COSOQ00201` 해외주식 종합잔고평가 API

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
| `&nbsp;&nbsp;-COSOQ00201InBlock1` | COSOQ00201InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | 00001 |
| `&nbsp;&nbsp;-BaseDt` | 기준일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | ALL@전체<br/>USD@미국 |
| `&nbsp;&nbsp;-AstkBalTpCode` | 해외증권잔고구분코드 | String | Y | 2 | 00 전체<br/>10 일반<br/>20 소수점 |


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
| `&nbsp;&nbsp;-COSOQ00201OutBlock1` | COSOQ00201OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BaseDt` | 기준일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AstkBalTpCode` | 해외증권잔고구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-COSOQ00201OutBlock2` | COSOQ00201OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Object | Y | 5 | - |
| `&nbsp;&nbsp;-ErnRat` | 수익율 | Object | Y | 18.6 | - |
| `&nbsp;&nbsp;-DpsConvEvalAmt` | 예수금환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-StkConvEvalAmt` | 주식환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-DpsastConvEvalAmt` | 예탁자산환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-WonEvalSumAmt` | 원화평가합계금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-ConvEvalPnlAmt` | 환산평가손익금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-WonDpsBalAmt` | 원화예수금잔고금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-D2EstiDps` | D2추정예수금 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-LoanAmt` | 대출금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-COSOQ00201OutBlock3` | COSOQ00201OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-FcurrDps` | 외화예수금 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrEvalAmt` | 외화평가금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrEvalPnlAmt` | 외화평가손익금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | Object | Y | 18.6 | - |
| `&nbsp;&nbsp;-BaseXchrat` | 기준환율 | Object | Y | 15.4 | - |
| `&nbsp;&nbsp;-DpsConvEvalAmt` | 예수금환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-PchsAmt` | 매입금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-StkConvEvalAmt` | 주식환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-ConvEvalPnlAmt` | 환산평가손익금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrBuyAmt` | 외화매수금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrOrdAbleAmt` | 외화주문가능금액 | Object | Y | 19.2 | - |
| `&nbsp;&nbsp;-LoanAmt` | 대출금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-COSOQ00201OutBlock4` | COSOQ00201OutBlock4 | Object | Y | - | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-ShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-JpnMktHanglIsuNm` | 일본시장한글종목명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-AstkBalTpCode` | 해외증권잔고구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-AstkBalTpCodeNm` | 해외증권잔고구분코드명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AstkBalQty` | 해외증권잔고수량 | Object | Y | 28.6 | - |
| `&nbsp;&nbsp;-AstkSellAbleQty` | 해외증권매도가능수량 | Object | Y | 28.6 | - |
| `&nbsp;&nbsp;-FcstckUprc` | 외화증권단가 | Object | Y | 24.4 | - |
| `&nbsp;&nbsp;-FcurrBuyAmt` | 외화매수금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcstckMktIsuCode` | 외화증권시장종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-OvrsScrtsCurpri` | 해외증권시세 | Object | Y | 28.7 | - |
| `&nbsp;&nbsp;-FcurrEvalAmt` | 외화평가금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrEvalPnlAmt` | 외화평가손익금액 | Object | Y | 21.4 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | Object | Y | 18.6 | - |
| `&nbsp;&nbsp;-BaseXchrat` | 기준환율 | Object | Y | 15.4 | - |
| `&nbsp;&nbsp;-PchsAmt` | 매입금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-DpsConvEvalAmt` | 예수금환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-StkConvEvalAmt` | 주식환산평가금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-ConvEvalPnlAmt` | 환산평가손익금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-AstkSettQty` | 해외증권결제수량 | Object | Y | 28.6 | - |
| `&nbsp;&nbsp;-MktTpNm` | 시장구분명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-FcurrMktCode` | 외화시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-LoanAmt` | 대출금액 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-DueDt` | 만기일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-AstkBasePrc` | 해외증권기준가격 | Object | Y | 28.6 | - |


### 요청 Example

```json
{
  "COSOQ00201InBlock1": {
    "RecCnt": 1,
    "BaseDt": "20250217",
    "CrcyCode": "ALL",
    "AstkBalTpCode": "00"
  }
}
```

### 응답 Example

```json
{
	"COSOQ00201OutBlock1": {
		"RecCnt": 1,
		"AcntNo": "***********",
		"Pwd": "********",
		"BaseDt": "20250428",
		"CrcyCode": "ALL",
		"AstkBalTpCode": "00"
	},
	"COSOQ00201OutBlock2": {
		"RecCnt": 1,
		"ErnRat": "28.810000",
		"DpsConvEvalAmt": 0,
		"StkConvEvalAmt": 6098484,
		"DpsastConvEvalAmt": 6098484,
		"WonEvalSumAmt": 4734180,
		"ConvEvalPnlAmt": 1364304,
		"WonDpsBalAmt": 13927349,
		"D2EstiDps": 13927349,
		"LoanAmt": 0
	},
	"COSOQ00201OutBlock3": [
		{
			"CrcyCode": "USD",
			"FcurrDps": "0.0000",
			"FcurrEvalAmt": "4251.0000",
			"FcurrEvalPnlAmt": "951.0000",
			"PnlRat": "28.818182",
			"BaseXchrat": "1434.6000",
			"DpsConvEvalAmt": 0,
			"PchsAmt": 4734180,
			"StkConvEvalAmt": 6098484,
			"ConvEvalPnlAmt": 1364304,
			"FcurrBuyAmt": "3300.0000",
			"FcurrOrdAbleAmt": "0.00",
			"LoanAmt": 0
		}
	],
	"COSOQ00201OutBlock4": [
		{
			"CrcyCode": "USD",
			"ShtnIsuNo": "TSLA",
			"IsuNo": "US88160R1014",
			"JpnMktHanglIsuNm": "테슬라",
			"AstkBalTpCode": "10",
			"AstkBalTpCodeNm": "일반",
			"AstkBalQty": "15.000000",
			"AstkSellAbleQty": "15.000000",
			"FcstckUprc": "220.0000",
			"FcurrBuyAmt": "3300.0000",
			"FcstckMktIsuCode": "82US88160R1014",
			"OvrsScrtsCurpri": "283.4000000",
			"FcurrEvalAmt": "4251.0000",
			"FcurrEvalPnlAmt": "951.0000",
			"PnlRat": "28.818182",
			"BaseXchrat": "1434.6000",
			"PchsAmt": 4734180,
			"DpsConvEvalAmt": 0,
			"StkConvEvalAmt": 6098484,
			"ConvEvalPnlAmt": 1364304,
			"AstkSettQty": "15.000000",
			"MktTpNm": "NASDAQ",
			"FcurrMktCode": "82",
			"LoanDt": "",
			"LoanDtlClssCode": "",
			"LoanAmt": 0,
			"DueDt": "",
			"AstkBasePrc": "284.950000"
		}
	],
	"rsp_cd": "00001",
	"rsp_msg": "조회가 완료되었습니다"
}
```

---

<a id="tr-COSOQ02701"></a>
## `COSOQ02701` 해외주식 예수금 조회 API

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
| `COSOQ02701InBlock1` | COSOQ02701InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |


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
| `COSOQ02701OutBlock1` | COSOQ02701OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `COSOQ02701OutBlock2` | COSOQ02701OutBlock2 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-FcurrBuyAdjstAmt1` | 외화매수정산금1 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrBuyAdjstAmt2` | 외화매수정산금2 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrBuyAdjstAmt3` | 외화매수정산금3 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrBuyAdjstAmt4` | 외화매수정산금4 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrSellAdjstAmt1` | 외화매도정산금1 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrSellAdjstAmt2` | 외화매도정산금2 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrSellAdjstAmt3` | 외화매도정산금3 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrSellAdjstAmt4` | 외화매도정산금4 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptFcurrDps1` | 추정외화예수금1 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptFcurrDps2` | 추정외화예수금2 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptFcurrDps3` | 추정외화예수금3 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptFcurrDps4` | 추정외화예수금4 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptMxchgAbleAmt1` | 추정환전가능금1 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptMxchgAbleAmt2` | 추정환전가능금2 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptMxchgAbleAmt3` | 추정환전가능금3 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrsmptMxchgAbleAmt4` | 추정환전가능금4 | Number | Y | 17.4 | - |
| `COSOQ02701OutBlock3` | COSOQ02701OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-CntryNm` | 국가명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-T4FcurrDps` | T4외화예수금 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrDps` | 외화예수금 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrOrdAbleAmt` | 외화주문가능금액 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-PrexchOrdAbleAmt` | 가환전주문가능금액 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrOrdAmt` | 외화주문금액 | Number | Y | 24.4 | - |
| `&nbsp;&nbsp;-FcurrPldgAmt` | 외화담보금액 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-ExecRuseFcurrAmt` | 체결재사용외화금액 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-FcurrMxchgAbleAmt` | 외화환전가능금 | Number | Y | 17.4 | - |
| `&nbsp;&nbsp;-BaseXchrat` | 기준환율 | Number | Y | 15.4 | - |
| `COSOQ02701OutBlock4` | COSOQ02701OutBlock4 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-WonDpsBalAmt` | 원화예수금잔고금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAbleAmt` | 출금가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-WonPrexchAbleAmt` | 원화가환전가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsMgn` | 해외증거금 | Number | Y | 17 | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-NrfCode` | 내외국인코드 | String | Y | 2 | - |


### 요청 Example

```json
{
  "COSOQ02701InBlock1": {
    "RecCnt": 1,
    "CrcyCode": "ALL"
  }
}
```

### 응답 Example

```json
{
	"COSOQ02701OutBlock1": {
		"RecCnt": 1,
		"AcntNo": "***********",
		"Pwd": "********",
		"CrcyCode": "ALL"
	},
	"COSOQ02701OutBlock2": [
		{
			"CrcyCode": "JPY",
			"FcurrBuyAdjstAmt1": "0.0000",
			"FcurrBuyAdjstAmt2": "0.0000",
			"FcurrBuyAdjstAmt3": "0.0000",
			"FcurrBuyAdjstAmt4": "0.0000",
			"FcurrSellAdjstAmt1": "0.0000",
			"FcurrSellAdjstAmt2": "0.0000",
			"FcurrSellAdjstAmt3": "0.0000",
			"FcurrSellAdjstAmt4": "0.0000",
			"PrsmptFcurrDps1": "0.0000",
			"PrsmptFcurrDps2": "0.0000",
			"PrsmptFcurrDps3": "0.0000",
			"PrsmptFcurrDps4": "0.0000",
			"PrsmptMxchgAbleAmt1": "0.0000",
			"PrsmptMxchgAbleAmt2": "0.0000",
			"PrsmptMxchgAbleAmt3": "0.0000",
			"PrsmptMxchgAbleAmt4": "0.0000"
		},
		{
			"CrcyCode": "HKD",
			"FcurrBuyAdjstAmt1": "0.0000",
			"FcurrBuyAdjstAmt2": "0.0000",
			"FcurrBuyAdjstAmt3": "0.0000",
			"FcurrBuyAdjstAmt4": "0.0000",
			"FcurrSellAdjstAmt1": "0.0000",
			"FcurrSellAdjstAmt2": "0.0000",
			"FcurrSellAdjstAmt3": "0.0000",
			"FcurrSellAdjstAmt4": "0.0000",
			"PrsmptFcurrDps1": "0.0000",
			"PrsmptFcurrDps2": "0.0000",
			"PrsmptFcurrDps3": "0.0000",
			"PrsmptFcurrDps4": "0.0000",
			"PrsmptMxchgAbleAmt1": "0.0000",
			"PrsmptMxchgAbleAmt2": "0.0000",
			"PrsmptMxchgAbleAmt3": "0.0000",
			"PrsmptMxchgAbleAmt4": "0.0000"
		},
		{
			"CrcyCode": "CNY",
			"FcurrBuyAdjstAmt1": "0.0000",
			"FcurrBuyAdjstAmt2": "0.0000",
			"FcurrBuyAdjstAmt3": "0.0000",
			"FcurrBuyAdjstAmt4": "0.0000",
			"FcurrSellAdjstAmt1": "0.0000",
			"FcurrSellAdjstAmt2": "0.0000",
			"FcurrSellAdjstAmt3": "0.0000",
			"FcurrSellAdjstAmt4": "0.0000",
			"PrsmptFcurrDps1": "0.0000",
			"PrsmptFcurrDps2": "0.0000",
			"PrsmptFcurrDps3": "0.0000",
			"PrsmptFcurrDps4": "0.0000",
			"PrsmptMxchgAbleAmt1": "0.0000",
			"PrsmptMxchgAbleAmt2": "0.0000",
			"PrsmptMxchgAbleAmt3": "0.0000",
			"PrsmptMxchgAbleAmt4": "0.0000"
		},
		{
			"CrcyCode": "USD",
			"FcurrBuyAdjstAmt1": "0.0000",
			"FcurrBuyAdjstAmt2": "0.0000",
			"FcurrBuyAdjstAmt3": "0.0000",
			"FcurrBuyAdjstAmt4": "0.0000",
			"FcurrSellAdjstAmt1": "0.0000",
			"FcurrSellAdjstAmt2": "0.0000",
			"FcurrSellAdjstAmt3": "0.0000",
			"FcurrSellAdjstAmt4": "0.0000",
			"PrsmptFcurrDps1": "0.0000",
			"PrsmptFcurrDps2": "0.0000",
			"PrsmptFcurrDps3": "0.0000",
			"PrsmptFcurrDps4": "0.0000",
			"PrsmptMxchgAbleAmt1": "0.0000",
			"PrsmptMxchgAbleAmt2": "0.0000",
			"PrsmptMxchgAbleAmt3": "0.0000",
			"PrsmptMxchgAbleAmt4": "0.0000"
		}
	],
	"COSOQ02701OutBlock3": [
		{
			"CntryNm": "미국",
			"CrcyCode": "USD",
			"T4FcurrDps": "0.0000",
			"FcurrDps": "0.0000",
			"FcurrOrdAbleAmt": "0.0000",
			"PrexchOrdAbleAmt": "9245.8800",
			"FcurrOrdAmt": "9245.8800",
			"FcurrPldgAmt": "0.0000",
			"ExecRuseFcurrAmt": "0.0000",
			"FcurrMxchgAbleAmt": "0.0000",
			"BaseXchrat": "1434.6000"
		},
		{
			"CntryNm": "홍콩",
			"CrcyCode": "HKD",
			"T4FcurrDps": "0.0000",
			"FcurrDps": "0.0000",
			"FcurrOrdAbleAmt": "0.0000",
			"PrexchOrdAbleAmt": "71721.3200",
			"FcurrOrdAmt": "71721.3200",
			"FcurrPldgAmt": "0.0000",
			"ExecRuseFcurrAmt": "0.0000",
			"FcurrMxchgAbleAmt": "0.0000",
			"BaseXchrat": "184.9400"
		}
	],
	"COSOQ02701OutBlock4": {
		"RecCnt": 1,
		"WonDpsBalAmt": 13927349,
		"MnyoutAbleAmt": 13927349,
		"WonPrexchAbleAmt": 13927349,
		"OvrsMgn": 0
	},
	"COSOQ02701OutBlock5": {
		"RecCnt": 1,
		"NrfCode": "01"
	},
	"rsp_cd": "00136",
	"rsp_msg": "조회가 완료되었습니다."
}
```
