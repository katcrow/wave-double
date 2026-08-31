# [주식] 계좌

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=37d22d4d-83cd-40a4-a375-81b010a4a627)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `37d22d4d-83cd-40a4-a375-81b010a4a627` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/accno` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 계좌별 거래내역 및 잔고 등 계좌에 관련된 서비스를 확인할 수 있습니다. |

## TR 목록 (12건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 계좌 거래내역 | [CDPCQ04700](account.md#tr-CDPCQ04700) | 1 | 1 | 10 |
| 계좌별신용한도조회 | [CSPAQ00600](account.md#tr-CSPAQ00600) | 1 | 1 | 2 |
| 현물계좌예수금 주문가능금액 총평가 조회 | [CSPAQ12200](account.md#tr-CSPAQ12200) | 1 | 1 | 1 |
| BEP단가조회 | [CSPAQ12300](account.md#tr-CSPAQ12300) | 1 | 1 | 10 |
| 현물계좌 주문체결내역 조회(API) | [CSPAQ13700](account.md#tr-CSPAQ13700) | 1 | 1 | 10 |
| 현물계좌예수금 주문가능금액 총평가2 | [CSPAQ22200](account.md#tr-CSPAQ22200) | 1 | 1 | 10 |
| 현물계좌증거금률별주문가능수량조회 | [CSPBQ00200](account.md#tr-CSPBQ00200) | 1 | 1 | 10 |
| 주식계좌 기간별수익률 상세 | [FOCCQ33600](account.md#tr-FOCCQ33600) | 1 | 1 | 10 |
| 주식당일매매일지/수수료 | [t0150](account.md#tr-t0150) | 2 | 2 | 10 |
| 주식당일매매일지/수수료(전일) | [t0151](account.md#tr-t0151) | 2 | 2 | 10 |
| 주식잔고2 | [t0424](account.md#tr-t0424) | 2 | 2 | 10 |
| 주식체결/미체결 | [t0425](account.md#tr-t0425) | 2 | 2 | 10 |

---

<a id="tr-CDPCQ04700"></a>
## `CDPCQ04700` 계좌 거래내역

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
| `CDPCQ04700InBlock1` | CDPCQ04700InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | 0@전체, 1@입출금, 2@입출고, 3@매매, 4@환전, 9@기타 |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SrtNo` | 시작번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PdptnCode` | 상품유형코드 | String | Y | 2 | 01 |
| `&nbsp;&nbsp;-IsuLgclssCode` | 종목대분류코드 | String | Y | 2 | 00@전체, 01@주식, 02@채권, 04@펀드, 03@선물, 05@해외주식, 06@해외파생 |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |


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
| `CDPCQ04700OutBlock1` | CDPCQ04700OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SrtNo` | 시작번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-PdptnCode` | 상품유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuLgclssCode` | 종목대분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `CDPCQ04700OutBlock2` | CDPCQ04700OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `CDPCQ04700OutBlock3` | CDPCQ04700OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TrdNo` | 거래번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-TpCodeNm` | 구분코드명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-SmryNo` | 적요번호 | String | Y | 4 | - |
| `&nbsp;&nbsp;-SmryNm` | 적요명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-CancTpNm` | 취소구분 | String | Y | 20 | - |
| `&nbsp;&nbsp;-TrdQty` | 거래수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Trtax` | 거래세 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrAdjstAmt` | 외화정산금액 | Number | Y | 25.4 | - |
| `&nbsp;&nbsp;-AdjstAmt` | 정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvdSum` | 연체합 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpsBfbalAmt` | 예수금전잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellPldgRfundAmt` | 매도담보상환금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpspdgLoanBfbalAmt` | 예탁담보대출전잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TrdmdaNm` | 거래매체명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrgTrdNo` | 원거래번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-TrdUprc` | 거래단가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-CmsnAmt` | 수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrCmsnAmt` | 외화수수료금액 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-RfundDiffAmt` | 상환차이금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RepayAmtSum` | 변제금합계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SecCrbalQty` | 유가증권금잔수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CslLoanRfundIntrstAmt` | 매도대금담보대출상환이자금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpspdgLoanCrbalAmt` | 예탁담보대출금잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TrxTime` | 처리시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-Inouno` | 출납번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-TrdAmt` | 거래금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ChckAmt` | 수표금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TaxSumAmt` | 세금합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrTaxSumAmt` | 외화세금합계금액 | Number | Y | 26.6 | - |
| `&nbsp;&nbsp;-IntrstUtlfee` | 이자이용료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyDvdAmt` | 배당금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblOcrAmt` | 미수발생금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TrxBrnNo` | 처리지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-TrxBrnNm` | 처리지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-DpspdgLoanAmt` | 예탁담보대출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpspdgLoanRfundAmt` | 예탁담보대출상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BasePrc` | 기준가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-DpsCrbalAmt` | 예수금금잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BoaAmt` | 과표 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAbleAmt` | 출금가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BcrLoanOcrAmt` | 수익증권담보대출발생금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BcrLoanBfbalAmt` | 수익증권담보대출전잔금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BnsBasePrc` | 매매기준가 | Number | Y | 20.1 | - |
| `&nbsp;&nbsp;-TaxchrBasePrc` | 과세기준가 | Number | Y | 20.1 | - |
| `&nbsp;&nbsp;-TrdUnit` | 거래좌수 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BalUnit` | 잔고좌수 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvrTax` | 제세금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalAmt` | 평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BcrLoanRfundAmt` | 수익증권담보대출상환금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BcrLoanCrbalAmt` | 수익증권담보대출금잔금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMgnOcrTotamt` | 추가증거금발생총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMnyMgnOcrAmt` | 추가현금증거금발생금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMgnDfryTotamt` | 추가증거금납부총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMnyMgnDfryAmt` | 추가현금증거금납부금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BnsplAmt` | 매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Ictax` | 소득세 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Ihtax` | 주민세 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-FcurrAmt` | 외화금액 | Number | Y | 24.4 | - |
| `&nbsp;&nbsp;-FcurrTrdAmt` | 외화거래금액 | Number | Y | 24.4 | - |
| `&nbsp;&nbsp;-FcurrDps` | 외화예수금 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrDpsBfbalAmt` | 외화예수금전잔금액 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-OppAcntNm` | 상대계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OppAcntNo` | 상대계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-LoanRfundAmt` | 대출상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LoanIntrstAmt` | 대출이자금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AskpsnNm` | 의뢰인명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TrdXchrat` | 거래환율 | Number | Y | 15.4 | - |
| `&nbsp;&nbsp;-RdctCmsn` | 감면수수료 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrStmpTx` | 외화인지세 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcurrElecfnTrtax` | 외화전자금융거래세 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-FcstckTrtax` | 외화증권거래세 | Number | Y | 21.4 | - |
| `CDPCQ04700OutBlock4` | CDPCQ04700OutBlock4 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-PnlSumAmt` | 손익합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CtrctAsm` | 약정누계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CmsnAmtSumAmt` | 수수료합계금액 | Number | Y | 16 | - |
| `CDPCQ04700OutBlock5` | CDPCQ04700OutBlock5 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-MnyinAmt` | 입금금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SecinAmt` | 입고금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAmt` | 출금금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SecoutAmt` | 출고금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DiffAmt` | 차이금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DiffAmt0` | 차이금액0 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellQty` | 매도수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellAmt` | 매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellCmsn` | 매도수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvrTax` | 제세금 | Number | Y | 19 | - |
| `&nbsp;&nbsp;-FcurrSellAdjstAmt` | 외화매도정산금액 | Number | Y | 25.4 | - |
| `&nbsp;&nbsp;-BuyQty` | 매수수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyAmt` | 매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyCmsn` | 매수수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ExecTax` | 체결세금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrBuyAdjstAmt` | 외화매수정산금액 | Number | Y | 25.4 | - |


### 요청 Example

```json
{
  "CDPCQ04700InBlock1": {
    "RecCnt": 1,
    "QryTp": "0",
    "QrySrtDt": "20230515",
    "QryEndDt": "20230516",
    "SrtNo": 0,
    "PdptnCode": "01",
    "IsuLgclssCode": "01",
    "IsuNo": "KR7000020008"
  }
}
```

### 응답 Example

```json
{
  "CDPCQ04700OutBlock1": {
    "RecCnt": 1,
    "QryTp": "0",
    "AcntNo": "20277932702",
    "Pwd": "********",
    "QrySrtDt": "20230515",
    "QryEndDt": "20230516",
    "SrtNo": 0,
    "PdptnCode": "01",
    "IsuLgclssCode": "01",
    "IsuNo": "KR7000020008"
  },
  "CDPCQ04700OutBlock2": {
    "RecCnt": 1,
    "AcntNm": "충조감"
  },
  "CDPCQ04700OutBlock3": [],
  "CDPCQ04700OutBlock4": {
    "RecCnt": 1,
    "PnlSumAmt": 0,
    "CtrctAsm": 0,
    "CmsnAmtSumAmt": 0
  },
  "CDPCQ04700OutBlock5": {
    "RecCnt": 1,
    "MnyinAmt": 0,
    "SecinAmt": 0,
    "MnyoutAmt": 0,
    "SecoutAmt": 0,
    "DiffAmt": 0,
    "DiffAmt0": 0,
    "SellQty": 0,
    "SellAmt": 0,
    "SellCmsn": 0,
    "EvrTax": 0,
    "FcurrSellAdjstAmt": "0.0000",
    "BuyQty": 0,
    "BuyAmt": 0,
    "BuyCmsn": 0,
    "ExecTax": 0,
    "FcurrBuyAdjstAmt": "0.0000"
  },
  "rsp_cd": "00200",
  "rsp_msg": "조회내역이 없습니다."
}
```

---

<a id="tr-CSPAQ00600"></a>
## `CSPAQ00600` 계좌별신용한도조회

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
| `CSPAQ00600InBlock1` | CSPAQ00600InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | 01@유통융자, 03@자기융자, 05@유통대주, 07@자기대주 |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | 41@xingAPI |


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
| `CSPAQ00600OutBlock1` | CSPAQ00600OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `CSPAQ00600OutBlock2` | CSPAQ00600OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-SloanLmtAmt` | 대주한도 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SloanAmtSum` | 대주금액합계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SloanNewAmt` | 대주신규금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SloanRfundAmt` | 대주상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktcplMloanLmtAmt` | 유통융자한도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktcplMloanAmtSum` | 유통융자금액합계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktcplMloanNewAmt` | 유통융자신규금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktcplMloanRfundAmt` | 유통융자상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SfaccMloanLmtAmt` | 자기융자한도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SfaccMloanAmtSum` | 자기융자금액합계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SfaccMloanNewAmt` | 자기융자신규금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SfaccMloanRfundAmt` | 자기융자상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnMktcplMloanLmtAmt` | 지점유통융자한도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnMktcplMloanNewAmt` | 지점유통융자신규금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnMktcplMloanRfundAmt` | 지점유통융자상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnMktcplMloanUseAmt` | 지점유통융자사용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnSfaccMloanLmtAmt` | 지점자기융자한도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnSfaccMloanNewAmt` | 지점자기융자신규금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnSfaccMloanRfundAmt` | 지점자기융자상환금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BrnSfaccMloanUseAmt` | 지점자기융자사용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FirmMloanLmtMgmtYn` | 이용사융자한도관리여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FirmCrdtIsuRestrcTp` | 이용사신용종목제한구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-PldgMaintRat` | 담보유지비율 | Number | Y | 7.4 | - |
| `&nbsp;&nbsp;-FirmNm` | 이용사명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-PldgRat` | 담보비율 | Number | Y | 7.4 | - |
| `&nbsp;&nbsp;-DpsastSum` | 예탁자산합계 | Number | Y | 17 | - |
| `&nbsp;&nbsp;-LmtChgAbleAmt` | 한도변경가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblUablOrdAbleQty` | 미수불가주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CSPAQ00600InBlock1" : {
    "LoanDtlClssCode" : "01",
    "IsuNo" : "A000020",
    "OrdPrc" : 1.11,
    "CommdaCode" : "41"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CSPAQ00600OutBlock1": {
        "CommdaCode": "04",
        "RecCnt": 1,
        "OrdPrc": "1.11",
        "IsuNo": "A000020",
        "AcntNo": "20187511401",
        "InptPwd": "********",
        "LoanDtlClssCode": "01"
    },
    "CSPAQ00600OutBlock2": {
        "BrnMktcplMloanNewAmt": 0,
        "SloanNewAmt": 0,
        "LmtChgAbleAmt": 0,
        "SfaccMloanNewAmt": 0,
        "MktcplMloanNewAmt": 0,
        "MktcplMloanRfundAmt": 0,
        "FirmNm": "",
        "SfaccMloanLmtAmt": 999999999999999,
        "OrdAbleQty": 1638001637,
        "MktcplMloanLmtAmt": 999999999999999,
        "PldgMaintRat": "1.4000",
        "BrnMktcplMloanUseAmt": 2663782796,
        "SfaccMloanRfundAmt": 0,
        "FirmCrdtIsuRestrcTp": "",
        "DpsastSum": 100004619279,
        "MktcplMloanAmtSum": 0,
        "RcvblUablOrdAbleQty": 1638001637,
        "SfaccMloanAmtSum": 0,
        "OrdPrc": "0.00",
        "BrnSfaccMloanNewAmt": 0,
        "OrdAbleAmt": 1818181818,
        "SloanRfundAmt": 0,
        "SloanAmtSum": 0,
        "PldgRat": "0.0000",
        "BrnSfaccMloanRfundAmt": 0,
        "SloanLmtAmt": 999999999999999,
        "BrnMktcplMloanRfundAmt": 0,
        "BrnSfaccMloanUseAmt": 95819909,
        "BrnMktcplMloanLmtAmt": 42000000000,
        "RecCnt": 1,
        "BrnSfaccMloanLmtAmt": 63000000000,
        "AcntNm": "가차금",
        "FirmMloanLmtMgmtYn": ""
    },
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CSPAQ12200"></a>
## `CSPAQ12200` 현물계좌예수금 주문가능금액 총평가 조회

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
| `CSPAQ12200InBlock1` | CSPAQ12200InBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-BalCreTp` | 잔고생성구분 | String | Y | 1 | 0 |


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
| `CSPAQ12200OutBlock1` | CSPAQ12200OutBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-MgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BalCreTp` | 잔고생성구분 | String | Y | 1 | - |
| `CSPAQ12200OutBlock2` | CSPAQ12200OutBlock2 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAbleAmt` | 출금가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SeOrdAbleAmt` | 거래소금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-KdqOrdAbleAmt` | 코스닥금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BalEvalAmt` | 잔고평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblAmt` | 미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpsastTotamt` | 예탁자산총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | Number | Y | 18.6 | - |
| `&nbsp;&nbsp;-InvstOrgAmt` | 투자원금 | Number | Y | 20 | - |
| `&nbsp;&nbsp;-InvstPlAmt` | 투자손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgOrdAmt` | 신용담보주문금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstAmt` | 대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1Dps` | D1예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2Dps` | D2예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyrclAmt` | 현금미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnMny` | 증거금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnSubst` | 증거금대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ChckAmt` | 수표금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstOrdAbleAmt` | 대용주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100pctOrdAbleAmt` | 증거금률100퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat35ordAbleAmt` | 증거금률35%주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat50ordAbleAmt` | 증거금률50%주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdaySellAdjstAmt` | 전일매도정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayBuyAdjstAmt` | 전일매수정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdaySellAdjstAmt` | 금일매도정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayBuyAdjstAmt` | 금일매수정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1ovdRepayRqrdAmt` | D1연체변제소요금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2ovdRepayRqrdAmt` | D2연체변제소요금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1PrsmptWthdwAbleAmt` | D1추정인출가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2PrsmptWthdwAbleAmt` | D2추정인출가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpspdgLoanAmt` | 예탁담보대출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Imreq` | 신용설정보증금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MloanAmt` | 융자금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ChgAfPldgRat` | 변경후담보비율 | Number | Y | 9.3 | - |
| `&nbsp;&nbsp;-OrgPldgAmt` | 원담보금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubPldgAmt` | 부담보금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RqrdPldgAmt` | 소요담보금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrgPdlckAmt` | 원담보부족금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PdlckAmt` | 담보부족금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddPldgMny` | 추가담보현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1OrdAbleAmt` | D1주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtIntdltAmt` | 신용이자미납금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EtclndAmt` | 기타대여금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayPrsmptCvrgAmt` | 익일추정반대매매금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrgPldgSumAmt` | 원담보합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtOrdAbleAmt` | 신용주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubPldgSumAmt` | 부담보합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgAmtMny` | 신용담보금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgSubstAmt` | 신용담보대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddCrdtPldgMny` | 추가신용담보현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgRuseAmt` | 신용담보재사용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddCrdtPldgSubst` | 추가신용담보대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CslLoanAmtdt1` | 매도대금담보대출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpslRestrcAmt` | 처분제한금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblUablOrdAbleAmt` | 미수불가주문가능금액 | Number | Y | 16 | - |


### 요청 Example

```json
{  
"CSPAQ12200InBlock1" : {
	"BalCreTp" : "1"
 }
}
```

### 응답 Example

```json
{
	"CSPAQ12200OutBlock1": {
		"RecCnt": 1,
		"MgmtBrnNo": "",
		"AcntNo": "12345678901",
		"Pwd": "********",
		"BalCreTp": "1"
	},
	"CSPAQ12200OutBlock2": {
		"RecCnt": 1,
		"BrnNm": "다이렉트203",
		"AcntNm": "엘에스",
		"MnyOrdAbleAmt": 307,
		"MnyoutAbleAmt": 307,
		"SeOrdAbleAmt": 306,
		"KdqOrdAbleAmt": 306,
		"BalEvalAmt": 227989450,
		"RcvblAmt": 0,
		"DpsastTotamt": 227989757,
		"PnlRat": "1031.979979",
		"InvstOrgAmt": 0,
		"InvstPlAmt": 227989757,
		"CrdtPldgOrdAmt": 0,
		"Dps": 307,
		"SubstAmt": 142982800,
		"D1Dps": 307,
		"D2Dps": 307,
		"MnyrclAmt": 0,
		"MgnMny": 0,
		"MgnSubst": 0,
		"ChckAmt": 0,
		"SubstOrdAbleAmt": 142982800,
		"MgnRat100pctOrdAbleAmt": 306,
		"MgnRat35ordAbleAmt": 306,
		"MgnRat50ordAbleAmt": 306,
		"PrdaySellAdjstAmt": 0,
		"PrdayBuyAdjstAmt": 0,
		"CrdaySellAdjstAmt": 0,
		"CrdayBuyAdjstAmt": 0,
		"D1ovdRepayRqrdAmt": 0,
		"D2ovdRepayRqrdAmt": 0,
		"D1PrsmptWthdwAbleAmt": 307,
		"D2PrsmptWthdwAbleAmt": 307,
		"DpspdgLoanAmt": 0,
		"Imreq": 0,
		"MloanAmt": 0,
		"ChgAfPldgRat": "0.000",
		"OrgPldgAmt": 0,
		"SubPldgAmt": 0,
		"RqrdPldgAmt": 0,
		"OrgPdlckAmt": 0,
		"PdlckAmt": 0,
		"AddPldgMny": 0,
		"D1OrdAbleAmt": 0,
		"CrdtIntdltAmt": 0,
		"EtclndAmt": 0,
		"NtdayPrsmptCvrgAmt": 0,
		"OrgPldgSumAmt": 0,
		"CrdtOrdAbleAmt": 0,
		"SubPldgSumAmt": 0,
		"CrdtPldgAmtMny": 0,
		"CrdtPldgSubstAmt": 0,
		"AddCrdtPldgMny": 0,
		"CrdtPldgRuseAmt": 0,
		"AddCrdtPldgSubst": 0,
		"CslLoanAmtdt1": 0,
		"DpslRestrcAmt": 0,
		"RcvblUablOrdAbleAmt": 306
	},
	"rsp_cd": "00136",
	"rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CSPAQ12300"></a>
## `CSPAQ12300` BEP단가조회

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
| `CSPAQ12300InBlock1` | CSPAQ12300InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-BalCreTp` | 잔고생성구분 | String | Y | 1 | 0:전체 1:현물 9:선물대용 |
| `&nbsp;&nbsp;-CmsnAppTpCode` | 수수료적용구분 | String | Y | 1 | 0:평가시 수수료 미적용 1:평가시 수수료 적용 |
| `&nbsp;&nbsp;-D2balBaseQryTp` | D2잔고기준조회구분 | String | Y | 1 | 0:전부조회 1:D2잔고 0이상만 조회 |
| `&nbsp;&nbsp;-UprcTpCode` | 단가구분 | String | Y | 1 | 0:평균단가 1:BEP단가 |


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
| `CSPAQ12300OutBlock1` | CSPAQ12300OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BalCreTp` | 잔고생성구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CmsnAppTpCode` | 수수료적용구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-D2balBaseQryTp` | D2잔고기준조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-UprcTpCode` | 단가구분 | String | Y | 1 | - |
| `CSPAQ12300OutBlock2` | CSPAQ12300OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAbleAmt` | 출금가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SeOrdAbleAmt` | 거래소금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-KdqOrdAbleAmt` | 코스닥금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-HtsOrdAbleAmt` | HTS주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100pctOrdAbleAmt` | 증거금률100퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BalEvalAmt` | 잔고평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PchsAmt` | 매입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblAmt` | 미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | Number | Y | 18.6 | - |
| `&nbsp;&nbsp;-InvstOrgAmt` | 투자원금 | Number | Y | 20 | - |
| `&nbsp;&nbsp;-InvstPlAmt` | 투자손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgOrdAmt` | 신용담보주문금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1Dps` | D1예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2Dps` | D2예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-MnyMgn` | 현금증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstMgn` | 대용증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstAmt` | 대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayBuyExecAmt` | 전일매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdaySellExecAmt` | 전일매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayBuyExecAmt` | 금일매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdaySellExecAmt` | 금일매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalPnlSum` | 평가손익합계 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-DpsastTotamt` | 예탁자산총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Evrprc` | 제비용 | Number | Y | 19 | - |
| `&nbsp;&nbsp;-RuseAmt` | 재사용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EtclndAmt` | 기타대여금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrcAdjstAmt` | 가정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1CmsnAmt` | D1수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2CmsnAmt` | D2수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1EvrTax` | D1제세금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2EvrTax` | D2제세금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1SettPrergAmt` | D1결제예정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2SettPrergAmt` | D2결제예정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKseMnyMgn` | 전일KSE현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKseSubstMgn` | 전일KSE대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKseCrdtMnyMgn` | 전일KSE신용현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKseCrdtSubstMgn` | 전일KSE신용대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKseMnyMgn` | 금일KSE현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKseSubstMgn` | 금일KSE대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKseCrdtMnyMgn` | 금일KSE신용현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKseCrdtSubstMgn` | 금일KSE신용대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKdqMnyMgn` | 전일코스닥현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKdqSubstMgn` | 전일코스닥대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKdqCrdtMnyMgn` | 전일코스닥신용현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayKdqCrdtSubstMgn` | 전일코스닥신용대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKdqMnyMgn` | 금일코스닥현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKdqSubstMgn` | 금일코스닥대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKdqCrdtMnyMgn` | 금일코스닥신용현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayKdqCrdtSubstMgn` | 금일코스닥신용대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayFrbrdMnyMgn` | 전일프리보드현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayFrbrdSubstMgn` | 전일프리보드대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayFrbrdMnyMgn` | 금일프리보드현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayFrbrdSubstMgn` | 금일프리보드대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayCrbmkMnyMgn` | 전일장외현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayCrbmkSubstMgn` | 전일장외대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayCrbmkMnyMgn` | 금일장외현금증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayCrbmkSubstMgn` | 금일장외대용증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpspdgQty` | 예탁담보수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyAdjstAmtD2` | 매수정산금(D+2) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellAdjstAmtD2` | 매도정산금(D+2) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RepayRqrdAmtD1` | 변제소요금(D+1) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RepayRqrdAmtD2` | 변제소요금(D+2) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LoanAmt` | 대출금액 | Number | Y | 16 | - |
| `CSPAQ12300OutBlock3` | CSPAQ12300OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-SecBalPtnCode` | 유가증권잔고유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-SecBalPtnNm` | 유가증권잔고유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BalQty` | 잔고수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BnsBaseBalQty` | 매매기준잔고수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayBuyExecQty` | 금일매수체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdaySellExecQty` | 금일매도체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellPrc` | 매도가 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-BuyPrc` | 매수가 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-SellPnlAmt` | 매도손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | Number | Y | 18.6 | - |
| `&nbsp;&nbsp;-NowPrc` | 현재가 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-CrdtAmt` | 신용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DueDt` | 만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-PrdaySellExecPrc` | 전일매도체결가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-PrdaySellQty` | 전일매도수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayBuyExecPrc` | 전일매수체결가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-PrdayBuyQty` | 전일매수수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-AvrUprc` | 평균단가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-SellAbleQty` | 매도가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellOrdQty` | 매도주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayBuyExecAmt` | 금일매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdaySellExecAmt` | 금일매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayBuyExecAmt` | 전일매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdaySellExecAmt` | 전일매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BalEvalAmt` | 잔고평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalPnl` | 평가손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellUnercQty` | 매도미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellUnsttQty` | 매도미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyUnercQty` | 매수미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyUnsttQty` | 매수미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UnsttQty` | 미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayCprc` | 전일종가 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-PchsAmt` | 매입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-LoanDtlClssCode` | 대출상세분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-DpspdgLoanQty` | 예탁담보대출수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CSPAQ12300InBlock1": {
    "RecCnt": 1,
    "BalCreTp": "0",
    "CmsnAppTpCode": "0",
    "D2balBaseQryTp": "0",
    "UprcTpCode": "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CSPAQ12300OutBlock2": {
        "BuyAdjstAmtD2": 0,
        "KdqOrdAbleAmt": 0,
        "PrdayKdqMnyMgn": 0,
        "D2CmsnAmt": 0,
        "D1EvrTax": 0,
        "CrdayFrbrdMnyMgn": 0,
        "RepayRqrdAmtD2": 0,
        "D1CmsnAmt": 0,
        "CrdayCrbmkMnyMgn": 0,
        "BrnNm": "",
        "PrdayFrbrdMnyMgn": 0,
        "BalEvalAmt": 0,
        "EvalPnlSum": 0,
        "PrdayFrbrdSubstMgn": 0,
        "CrdayKdqSubstMgn": 0,
        "RepayRqrdAmtD1": 0,
        "CrdayKseCrdtMnyMgn": 0,
        "PrdayKdqSubstMgn": 0,
        "PrdayKseMnyMgn": 0,
        "D2EvrTax": 0,
        "MnyOrdAbleAmt": 0,
        "DpspdgQty": 0,
        "SellAdjstAmtD2": 0,
        "PrcAdjstAmt": 0,
        "EtclndAmt": 0,
        "Evrprc": 0,
        "CrdayKdqCrdtSubstMgn": 0,
        "PrdaySellExecAmt": 0,
        "MnyMgn": 0,
        "MgnRat100pctOrdAbleAmt": 0,
        "PrdayKseSubstMgn": 0,
        "OrdDt": "",
        "CrdayCrbmkSubstMgn": 0,
        "InvstPlAmt": 0,
        "D1SettPrergAmt": 0,
        "D2SettPrergAmt": 0,
        "SeOrdAbleAmt": 0,
        "Dps": 0,
        "DpsastTotamt": 0,
        "PrdayBuyExecAmt": 0,
        "D2Dps": 0,
        "CrdtPldgOrdAmt": 0,
        "CrdayKdqMnyMgn": 0,
        "SubstMgn": 0,
        "LoanAmt": 0,
        "PrdayKdqCrdtSubstMgn": 0,
        "PrdayKdqCrdtMnyMgn": 0,
        "InvstOrgAmt": 0,
        "PchsAmt": 0,
        "CrdayFrbrdSubstMgn": 0,
        "PrdayKseCrdtMnyMgn": 0,
        "CrdayBuyExecAmt": 0,
        "PrdayCrbmkMnyMgn": 0,
        "CrdayKdqCrdtMnyMgn": 0,
        "RcvblAmt": 0,
        "HtsOrdAbleAmt": 0,
        "PrdayCrbmkSubstMgn": 0,
        "CrdayKseCrdtSubstMgn": 0,
        "D1Dps": 0,
        "RecCnt": 1,
        "PnlRat": "0.000000",
        "PrdayKseCrdtSubstMgn": 0,
        "AcntNm": "",
        "MnyoutAbleAmt": 0,
        "CrdaySellExecAmt": 0,
        "CrdayKseMnyMgn": 0,
        "SubstAmt": 0,
        "RuseAmt": 0,
        "CrdayKseSubstMgn": 0
    },
    "CSPAQ12300OutBlock1": {
        "RecCnt": 1,
        "UprcTpCode": "0",
        "AcntNo": "20011132702",
        "D2balBaseQryTp": "0",
        "Pwd": "********",
        "CmsnAppTpCode": "0",
        "BalCreTp": "0"
    },
    "CSPAQ12300OutBlock3": [
        {
            "BuyUnercQty": 0,
            "SecBalPtnNm": "유가KSE",
            "BuyUnsttQty": 1,
            "SellUnercQty": 0,
            "UnercQty": 0,
            "SecBalPtnCode": "00",
            "PrdayBuyExecAmt": 0,
            "LoanDtlClssCode": "",
            "BalEvalAmt": 82700,
            "BuyPrc": "60000.0000",
            "SellOrdQty": 0,
            "AvrUprc": "60000.00",
            "BnsBaseBalQty": 1,
            "SellUnsttQty": 0,
            "PchsAmt": 60000,
            "PrdaySellExecPrc": "0.00",
            "PrdayCprc": "68500.00",
            "BalQty": 0,
            "PrdaySellQty": 0,
            "EvalPnl": 22700,
            "CrdayBuyExecAmt": 60000,
            "PrdayBuyExecPrc": "0.00",
            "SellAbleQty": 1,
            "OrdAbleAmt": 0,
            "MnyOrdAbleAmt": 0,
            "NowPrc": "82700.00",
            "CrdtAmt": 0,
            "SellPrc": "0.0000",
            "IsuNm": "삼성전자",
            "CrdayBuyExecQty": 1,
            "DueDt": "",
            "PnlRat": "0.378333",
            "PrdaySellExecAmt": 0,
            "IsuNo": "A005930",
            "CrdaySellExecQty": 0,
            "CrdaySellExecAmt": 0,
            "RegMktCode": "10",
            "LoanDt": "",
            "UnsttQty": 1,
            "PrdayBuyQty": 0,
            "SellPnlAmt": 22700,
            "DpspdgLoanQty": 0
        }
    ],
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CSPAQ13700"></a>
## `CSPAQ13700` 현물계좌 주문체결내역 조회(API)

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
| `CSPAQ13700InBlock1` | CSPAQ13700InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | 00.전체<br/>10.거래소<br/>20.코스닥<br/>30.프리보드 |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | 0@전체<br/>1@매도<br/>2@매수 |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | 주식 : A+종목코드<br/>ELW : J+종목코드 |
| `&nbsp;&nbsp;-ExecYn` | 체결여부 | String | Y | 1 | 0.전체<br/>1.체결<br/>3.미체결 |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SrtOrdNo2` | 시작주문번호2 | Number | Y | 10 | 역순구분이 순 : 000000000<br/>역순구분이 역순 : 999999999 |
| `&nbsp;&nbsp;-BkseqTpCode` | 역순구분 | String | Y | 1 | 0.역순<br/>1.정순 |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | 00.전체<br/>98.매도전체<br/>99.매수전체<br/>01.현금매도<br/>02.현금매수<br/>05.저축매도<br/>06.저축매수<br/>09.상품매도<br/>10.상품매수<br/>03.융자매도<br/>04.융자매수<br/>07.대주매도<br/>08.대주매수<br/>11.선물대용매도<br/>13.현금매도(프)<br/>14.현금매수(프)<br/>17.대출<br/>18.대출상환 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API 응답 Response Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CSPAQ13700OutBlock1` | CSPAQ13700OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-ExecYn` | 체결여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-SrtOrdNo2` | 시작주문번호2 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BkseqTpCode` | 역순구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `CSPAQ13700OutBlock2` | CSPAQ13700OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-SellExecAmt` | 매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyExecAmt` | 매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellExecQty` | 매도체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyExecQty` | 매수체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SellOrdQty` | 매도주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyOrdQty` | 매수주문수량 | Number | Y | 16 | - |
| `CSPAQ13700OutBlock3` | CSPAQ13700OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-MgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-OrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrdPtnNm` | 주문유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdTrxPtnCode` | 주문처리유형코드 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-OrdTrxPtnNm` | 주문처리유형명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-MrcTpCode` | 정정취소구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MrcTpNm` | 정정취소구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-MrcQty` | 정정취소수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MrcAbleQty` | 정정취소가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가격 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ExecPrc` | 체결가 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-ExecTrxTime` | 체결처리시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-LastExecTime` | 최종체결시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-OrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OrdprcPtnNm` | 호가유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdCndiTpCode` | 주문조건구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AllExecQty` | 전체체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RegCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-CommdaNm` | 통신매체명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-MbrNo` | 회원번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RsvOrdYn` | 예약주문여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LoanDt` | 대출일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdTime` | 주문시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-OpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OdrrId` | 주문자ID | String | Y | 16 | - |


### 요청 Example

```json
{
  "CSPAQ13700InBlock1" : {
    "OrdMktCode" : "00",
    "BnsTpCode" : "0",
    "IsuNo" : "A005930",
    "ExecYn" : "0",
    "OrdDt" : "20230613",
    "SrtOrdNo2" : 0,
    "BkseqTpCode" : "0", 
    "OrdPtnCode" : "00"
  }
}
```

### 응답 Example

```json
{
    "CSPAQ13700OutBlock2": {
        "RecCnt": 1,
        "SellOrdQty": 0,
        "BuyExecAmt": 180000,
        "BuyExecQty": 3,
        "SellExecAmt": 0,
        "SellExecQty": 0,
        "BuyOrdQty": 6
    },
    "rsp_cd": "00200",
    "CSPAQ13700OutBlock3": [
    ],
    "CSPAQ13700OutBlock1": {
        "OrdMktCode": "00",
        "BkseqTpCode": "0",
        "RecCnt": 1,
        "BnsTpCode": "0",
        "IsuNo": "A005930",
        "AcntNo": "20011132702",
        "InptPwd": "********",
        "SrtOrdNo2": 0,
        "OrdPtnCode": "00",
        "ExecYn": "0",
        "OrdDt": "20230613"
    },
    "rsp_msg": "조회내역이 없습니다."
}
```

---

<a id="tr-CSPAQ22200"></a>
## `CSPAQ22200` 현물계좌예수금 주문가능금액 총평가2

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
| `CSPAQ22200InBlock1` | CSPAQ22200InBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-BalCreTp` | 잔고생성구분 | String | Y | 1 | 0 |


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
| `CSPAQ22200OutBlock1` | CSPAQ22200OutBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | 1 |
| `&nbsp;&nbsp;-MgmtBrnNo` | 관리지점번호 | String | Y | 3 | 현재 미사용 |
| `&nbsp;&nbsp;-BalCreTp` | 잔고생성구분 | String | Y | 1 | 0:주식잔고<br/>1:기타 <br/>2:재투자잔고<br/>3:유통대주<br/>4:자기융자<br/>5:유통대주<br/>6:자기대주 |
| `CSPAQ22200OutBlock2` | CSPAQ22200OutBlock2 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-BrnNm` | 지점명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstOrdAbleAmt` | 대용주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SeOrdAbleAmt` | 거래소금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-KdqOrdAbleAmt` | 코스닥금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgOrdAmt` | 신용담보주문금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100pctOrdAbleAmt` | 증거금률100퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat35ordAbleAmt` | 증거금률35%주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat50ordAbleAmt` | 증거금률50%주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtOrdAbleAmt` | 신용주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstAmt` | 대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnMny` | 증거금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnSubst` | 증거금대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1Dps` | D1예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2Dps` | D2예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblAmt` | 미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D1ovdRepayRqrdAmt` | D1연체변제소요금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-D2ovdRepayRqrdAmt` | D2연체변제소요금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MloanAmt` | 융자금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ChgAfPldgRat` | 변경후담보비율 | Number | Y | 9.3 | - |
| `&nbsp;&nbsp;-RqrdPldgAmt` | 소요담보금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PdlckAmt` | 담보부족금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrgPldgSumAmt` | 원담보합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubPldgSumAmt` | 부담보합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgAmtMny` | 신용담보금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgSubstAmt` | 신용담보대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Imreq` | 신용설정보증금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgRuseAmt` | 신용담보재사용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpslRestrcAmt` | 처분제한금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdaySellAdjstAmt` | 전일매도정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrdayBuyAdjstAmt` | 전일매수정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdaySellAdjstAmt` | 금일매도정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdayBuyAdjstAmt` | 금일매수정산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CslLoanAmtdt1` | 매도대금담보대출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblUablOrdAbleAmt` | 미수불가주문가능금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CSPAQ22200InBlock1": {
    "BalCreTp": "1"
  }
}
```

### 응답 Example

```json
{
	"CSPAQ22200OutBlock1": {
		"RecCnt": 1,
		"MgmtBrnNo": "",
		"AcntNo": "12345678901",
		"Pwd": "********",
		"BalCreTp": "1"
	},
	"CSPAQ22200OutBlock2": {
		"RecCnt": 1,
		"BrnNm": "다이렉트203",
		"AcntNm": "엘에스",
		"MnyOrdAbleAmt": 307,
		"SubstOrdAbleAmt": 142982800,
		"SeOrdAbleAmt": 306,
		"KdqOrdAbleAmt": 306,
		"CrdtPldgOrdAmt": 0,
		"MgnRat100pctOrdAbleAmt": 306,
		"MgnRat35ordAbleAmt": 306,
		"MgnRat50ordAbleAmt": 306,
		"CrdtOrdAbleAmt": 0,
		"Dps": 307,
		"SubstAmt": 142982800,
		"MgnMny": 0,
		"MgnSubst": 0,
		"D1Dps": 307,
		"D2Dps": 307,
		"RcvblAmt": 0,
		"D1ovdRepayRqrdAmt": 0,
		"D2ovdRepayRqrdAmt": 0,
		"MloanAmt": 0,
		"ChgAfPldgRat": "0.000",
		"RqrdPldgAmt": 0,
		"PdlckAmt": 0,
		"OrgPldgSumAmt": 0,
		"SubPldgSumAmt": 0,
		"CrdtPldgAmtMny": 0,
		"CrdtPldgSubstAmt": 0,
		"Imreq": 0,
		"CrdtPldgRuseAmt": 0,
		"DpslRestrcAmt": 0,
		"PrdaySellAdjstAmt": 0,
		"PrdayBuyAdjstAmt": 0,
		"CrdaySellAdjstAmt": 0,
		"CrdayBuyAdjstAmt": 0,
		"CslLoanAmtdt1": 0,
		"RcvblUablOrdAbleAmt": 306
	},
	"rsp_cd": "00136",
	"rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CSPBQ00200"></a>
## `CSPBQ00200` 현물계좌증거금률별주문가능수량조회

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
| `CSPBQ00200InBlock1` | CSPBQ00200InBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | 1@매도, 2@매수 |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가격 | Number | Y | 15.2 | - |


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
| `CSPBQ00200OutBlock1` | CSPBQ00200OutBlock1 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가격 | Number | Y | 15.2 | - |
| `&nbsp;&nbsp;-RegCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `CSPBQ00200OutBlock2` | CSPBQ00200OutBlock2 | Object | Y | null | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstAmt` | 대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CrdtPldgRuseAmt` | 신용담보재사용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstOrdAbleAmt` | 대용주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyMgn` | 현금증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstMgn` | 대용증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SeOrdAbleAmt` | 거래소금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-KdqOrdAbleAmt` | 코스닥금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrsmptDpsD1` | 추정예수금(D+1) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrsmptDpsD2` | 추정예수금(D+2) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAbleAmt` | 출금가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblAmt` | 미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CmsnRat` | 수수료율 | Number | Y | 15.5 | - |
| `&nbsp;&nbsp;-AddLevyAmt` | 추가징수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RuseObjAmt` | 재사용대상금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyRuseObjAmt` | 현금재사용대상금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FirmMgnRat` | 이용사증거금률 | Number | Y | 7.4 | - |
| `&nbsp;&nbsp;-SubstRuseObjAmt` | 대용재사용대상금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-IsuMgnRat` | 종목증거금률 | Number | Y | 7.4 | - |
| `&nbsp;&nbsp;-AcntMgnRat` | 계좌증거금률 | Number | Y | 7.4 | - |
| `&nbsp;&nbsp;-TrdMgnrt` | 거래증거금률 | Number | Y | 7.4 | - |
| `&nbsp;&nbsp;-Cmsn` | 수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat20pctOrdAbleAmt` | 증거금률20퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat20OrdAbleQty` | 증거금률100퍼센트현금주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat30pctOrdAbleAmt` | 증거금률30퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat30OrdAbleQty` | 증거금률30퍼센트주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat40pctOrdAbleAmt` | 증거금률40퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat40OrdAbleQty` | 증거금률40퍼센트주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100pctOrdAbleAmt` | 증거금률100퍼센트주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100OrdAbleQty` | 증거금률100퍼센트주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100MnyOrdAbleAmt` | 증거금률100퍼센트현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100MnyOrdAbleQty` | 증거금률100퍼센트현금주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat20pctRuseAbleAmt` | 증거금률20퍼센트재사용가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat30pctRuseAbleAmt` | 증거금률30퍼센트재사용가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat40pctRuseAbleAmt` | 증거금률40퍼센트재사용가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRat100pctRuseAbleAmt` | 증거금률100퍼센트재사용가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CSPBQ00200InBlock1": {
    "RecCnt": 1,
    "BnsTpCode": "1",
    "IsuNo": "KR7000020008",
    "OrdPrc": 0.00,
    "RegCommdaCode": "41"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CSPBQ00200OutBlock2": {
        "KdqOrdAbleAmt": 265866666,
        "MgnRat100OrdAbleQty": 0,
        "SeOrdAbleAmt": 265866666,
        "Cmsn": 0,
        "MgnRat100pctRuseAbleAmt": 0,
        "Dps": 80000000,
        "RuseObjAmt": 0,
        "CmsnRat": "0.00000",
        "TrdMgnrt": "0.3000",
        "MgnRat20pctRuseAbleAmt": 0,
        "SubstOrdAbleAmt": 0,
        "OrdAbleQty": 0,
        "SubstMgn": 0,
        "MgnRat100MnyOrdAbleQty": 0,
        "FirmMgnRat": "0.3000",
        "CrdtPldgRuseAmt": 0,
        "IsuMgnRat": "0.3000",
        "PrsmptDpsD2": 79879982,
        "PrsmptDpsD1": 80000000,
        "MgnRat20OrdAbleQty": 0,
        "MgnRat100MnyOrdAbleAmt": 79744009,
        "MgnRat30pctOrdAbleAmt": 265866666,
        "SubstRuseObjAmt": 0,
        "OrdAbleAmt": 0,
        "MnyOrdAbleAmt": 79760000,
        "RcvblAmt": 0,
        "MgnRat40pctRuseAbleAmt": 0,
        "AddLevyAmt": 0,
        "AcntMgnRat": "0.3000",
        "MgnRat30OrdAbleQty": 0,
        "IsuNm": "",
        "MgnRat40OrdAbleQty": 0,
        "RecCnt": 1,
        "AcntNm": "우우돌",
        "MnyoutAbleAmt": 79759742,
        "MnyMgn": 240000,
        "SubstAmt": 0,
        "MgnRat100pctOrdAbleAmt": 79744009,
        "MgnRat20pctOrdAbleAmt": 398800000,
        "MnyRuseObjAmt": 0,
        "MgnRat30pctRuseAbleAmt": 0,
        "MgnRat40pctOrdAbleAmt": 199400000
    },
    "rsp_msg": "조회가 완료되었습니다.",
    "CSPBQ00200OutBlock1": {
        "RecCnt": 1,
        "RegCommdaCode": "40",
        "BnsTpCode": "1",
        "OrdPrc": "0.00",
        "IsuNo": "KR7000020008",
        "AcntNo": "20011132702",
        "InptPwd": "********"
    }
}
```

---

<a id="tr-FOCCQ33600"></a>
## `FOCCQ33600` 주식계좌 기간별수익률 상세

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
| `FOCCQ33600InBlock1` | FOCCQ33600InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TermTp` | 기간구분 | String | Y | 1 | 1:일별, 2:주별, 3:월별 |


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
| `FOCCQ33600OutBlock1` | FOCCQ33600OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TermTp` | 기간구분 | String | Y | 1 | - |
| `FOCCQ33600OutBlock2` | FOCCQ33600OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsctrAmt` | 매매약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyinAmt` | 입금금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAmt` | 출금금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstAvrbalPramt` | 투자원금평잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstPlAmt` | 투자손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstErnrat` | 투자수익률 | Number | Y | 9.2 | - |
| `FOCCQ33600OutBlock3` | FOCCQ33600OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-BaseDt` | 기준일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FdEvalAmt` | 기초평가금액 | Number | Y | 19 | - |
| `&nbsp;&nbsp;-EotEvalAmt` | 기말평가금액 | Number | Y | 19 | - |
| `&nbsp;&nbsp;-InvstAvrbalPramt` | 투자원금평잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BnsctrAmt` | 매매약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyinSecinAmt` | 입금고액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutSecoutAmt` | 출금고액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalPnlAmt` | 평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TermErnrat` | 기간수익률 | Number | Y | 11.3 | - |
| `&nbsp;&nbsp;-Idx` | 지수 | Number | Y | 13.2 | - |


### 요청 Example

```json
{
  "FOCCQ33600InBlock1" : {
    "RecCnt" : 1,
    "QrySrtDt" : "20230101",
    "QryEndDt" : "20230615",
    "TermTp" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00133",
    "FOCCQ33600OutBlock3": [
        {
            "FdEvalAmt": 17176098,
            "EotEvalAmt": 17176098,
            "MnyinSecinAmt": 0,
            "InvstAvrbalPramt": 17176098,
            "BnsctrAmt": 0,
            "MnyoutSecoutAmt": 0,
            "EvalPnlAmt": 0,
            "Idx": "0.00",
            "BaseDt": "20200101",
            "TermErnrat": "0.000"
        },
        {
            "FdEvalAmt": 17176098,
            "EotEvalAmt": 17525323,
            "MnyinSecinAmt": 0,
            "InvstAvrbalPramt": 17176098,
            "BnsctrAmt": 0,
            "MnyoutSecoutAmt": 0,
            "EvalPnlAmt": 349225,
            "Idx": "0.00",
            "BaseDt": "20200102",
            "TermErnrat": "2.033"
        }
    ],
    "FOCCQ33600OutBlock2": {
        "InvstPlAmt": 10393928,
        "RecCnt": 1,
        "InvstErnrat": "38.14",
        "AcntNm": "가차금",
        "InvstAvrbalPramt": 27249892,
        "BnsctrAmt": 0,
        "MnyinAmt": 42106357,
        "MnyoutAmt": 60182733
    },
    "FOCCQ33600OutBlock1": {
        "RecCnt": 1,
        "TermTp": "1",
        "AcntNo": "10011700251",
        "QrySrtDt": "20200101",
        "Pwd": "********",
        "QryEndDt": "20230101"
    },
    "rsp_msg": "조회가 계속 됩니다. 계속하시려면 연속버튼을 누르십시오."
}
```

---

<a id="tr-t0150"></a>
## `t0150` 주식당일매매일지/수수료

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
| `t0150InBlock` | t0150InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_medosu` | CTS_매매구분 | String | Y | 1 | 연속조회시 OutBlock의 동일필드 입력 |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 12 | 연속조회시 OutBlock의 동일필드 입력 |
| `&nbsp;&nbsp;-cts_price` | CTS_단가 | String | Y | 9 | 연속조회시 OutBlock의 동일필드 입력 |
| `&nbsp;&nbsp;-cts_middiv` | CTS_매체 | String | Y | 2 | 연속조회시 OutBlock의 동일필드 입력 |


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
| `t0150OutBlock` | t0150OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mdqty` | 매도수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-mdamt` | 매도약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdfee` | 매도수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdtax` | 매도거래세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdargtax` | 매도농특세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tmdtax` | 매도제비용합 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdadjamt` | 매도정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-msqty` | 매수수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-msamt` | 매수약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-msfee` | 매수수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tmstax` | 매수제비용합 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-msadjamt` | 매수정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tqty` | 합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-tamt` | 합계약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tfee` | 합계수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tottax` | 합계거래세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-targtax` | 합계농특세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-ttax` | 합계제비용합 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tadjamt` | 합계정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-cts_medosu` | CTS_매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-cts_price` | CTS_단가 | String | Y | 9 | - |
| `&nbsp;&nbsp;-cts_middiv` | CTS_매체 | String | Y | 2 | - |
| `t0150OutBlock1` | t0150OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-medosu` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-qty` | 수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-price` | 단가 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-amt` | 약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-fee` | 수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tax` | 거래세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-argtax` | 농특세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-adjamt` | 정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-middiv` | 매체 | String | Y | 20 | - |


### 요청 Example

```json
{
  "t0150InBlock": {
    "cts_medosu": "1",
    "cts_expcode": "1",
    "cts_price": "1",
    "cts_middiv": "1"
  }
}
```

### 응답 Example

```json
{
  "rsp_cd": "00000",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-t0151"></a>
## `t0151` 주식당일매매일지/수수료(전일)

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
| `t0151InBlock` | t0151InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_medosu` | CTS_매매구분 | String | Y | 1 | 연속조회시 OutBlock의 동일필드 입력 |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 12 | 연속조회시 OutBlock의 동일필드 입력 |
| `&nbsp;&nbsp;-cts_price` | CTS_단가 | String | Y | 9 | 연속조회시 OutBlock의 동일필드 입력 |
| `&nbsp;&nbsp;-cts_middiv` | CTS_매체 | String | Y | 2 | 연속조회시 OutBlock의 동일필드 입력 |


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
| `t0151OutBlock` | t0151OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mdqty` | 매도수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-mdamt` | 매도약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdfee` | 매도수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdtax` | 매도거래세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdargtax` | 매도농특세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tmdtax` | 매도제비용합 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdadjamt` | 매도정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-msqty` | 매수수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-msamt` | 매수약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-msfee` | 매수수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tmstax` | 매수제비용합 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-msadjamt` | 매수정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tqty` | 합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-tamt` | 합계약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tfee` | 합계수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tottax` | 합계거래세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-targtax` | 합계농특세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-ttax` | 합계제비용합 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tadjamt` | 합계정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-cts_medosu` | CTS_매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-cts_price` | CTS_단가 | String | Y | 9 | - |
| `&nbsp;&nbsp;-cts_middiv` | CTS_매체 | String | Y | 2 | - |
| `t0151OutBlock1` | t0151OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-medosu` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-qty` | 수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-price` | 단가 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-amt` | 약정금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-fee` | 수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tax` | 거래세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-argtax` | 농특세 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-adjamt` | 정산금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-middiv` | 매체 | String | Y | 20 | - |


### 요청 Example

```json
{
  "t0151InBlock" : {
    "date" : "20230609",
    "cts_medosu" : "",
    "cts_expcode" : "",
    "cts_price" : "",
    "cts_middiv" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t0151OutBlock1": [
        {
            "price": 60000,
            "qty": 4,
            "fee": 0,
            "argtax": 0,
            "expcode": "005930",
            "amt": 240000,
            "adjamt": 240000,
            "tax": 0,
            "medosu": "매수",
            "middiv": "OPEN API"
        },
        {
            "price": 60000,
            "qty": 4,
            "fee": 36,
            "argtax": 0,
            "expcode": "",
            "amt": 240000,
            "adjamt": 240036,
            "tax": 0,
            "medosu": "종목소계",
            "middiv": ""
        }
    ],
    "rsp_msg": "조회가 완료되었습니다.",
    "t0151OutBlock": {
        "mdfee": 0,
        "mdargtax": 0,
        "tmdtax": 0,
        "ttax": 36,
        "msadjamt": 240036,
        "tamt": 240000,
        "tfee": 36,
        "msqty": 4,
        "targtax": 0,
        "cts_price": "",
        "mdqty": 0,
        "mdadjamt": 0,
        "cts_middiv": "",
        "tqty": 4,
        "cts_expcode": "",
        "msfee": 36,
        "tottax": 0,
        "msamt": 240000,
        "tmstax": 36,
        "mdtax": 0,
        "cts_medosu": "",
        "tadjamt": -240036,
        "mdamt": 0
    }
}
```

---

<a id="tr-t0424"></a>
## `t0424` 주식잔고2

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
| `t0424InBlock` | t0424InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-prcgb` | 단가구분 | String | Y | 1 | 1 : 평균단가<br/>2 : BEP단가 |
| `&nbsp;&nbsp;-chegb` | 체결구분 | String | Y | 1 | 0 : 결제기준잔고<br/>2 : 체결기준(잔고가 0이 아닌 종목만 조회) |
| `&nbsp;&nbsp;-dangb` | 단일가구분 | String | Y | 1 | 0 : 정규장<br/>1 : 시간외단일가 |
| `&nbsp;&nbsp;-charge` | 제비용포함여부 | String | Y | 1 | 0 : 제비용미포함<br/>1 : 제비용포함 |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 22 | 연속조회시 OutBlock의 동일필드 입력 |


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
| `t0424OutBlock` | t0424OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-sunamt` | 추정순자산 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dtsunik` | 실현손익 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mamt` | 매입금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sunamt1` | 추정D2예수금 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 22 | - |
| `&nbsp;&nbsp;-tappamt` | 평가금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tdtsunik` | 평가손익 | Number | Y | 18 | - |
| `t0424OutBlock1` | t0424OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-jangb` | 잔고구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-janqty` | 잔고수량 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdposqt` | 매도가능수량 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-pamt` | 평균단가 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mamt` | 매입금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sinamt` | 대출금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-lastdt` | 만기일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-msat` | 당일매수금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mpms` | 당일매수단가 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mdat` | 당일매도금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-mpmd` | 당일매도단가 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-jsat` | 전일매수금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-jpms` | 전일매수단가 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-jdat` | 전일매도금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-jpmd` | 전일매도단가 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sysprocseq` | 처리순번 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-loandt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-marketgb` | 시장구분 | String | Y | 1 | 1 : 주식<br/>2 : 채권 |
| `&nbsp;&nbsp;-jonggb` | 종목구분 | String | Y | 1 | '1':프리보드<br/>'2':코스닥<br/>'3':거래소<br/>'Z':상장폐지<br/>' ':비상장<br/>'8':코넥스<br/>'9':CMA&RP |
| `&nbsp;&nbsp;-janrt` | 보유비중 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-appamt` | 평가금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dtsunik` | 평가손익 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sunikrt` | 수익율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-fee` | 수수료 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-tax` | 제세금 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-sininter` | 신용이자 | Number | Y | 10 | - |


### 요청 Example

```json
{
  "t0424InBlock": {
    "prcgb": "",
    "chegb": "",
    "dangb": "",
    "charge": "",
    "cts_expcode": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t0424OutBlock": {
        "dtsunik": 0,
        "cts_expcode": "",
        "mamt": 120013,
        "sunamt1": 80000000,
        "tappamt": 150283,
        "sunamt": 80030265,
        "tdtsunik": 30270
    },
    "t0424OutBlock1": [
        {
            "sininter": 0,
            "fee": 30,
            "mamt": 120000,
            "sinamt": 0,
            "mpmd": 0,
            "mdposqt": 2,
            "jsat": 0,
            "janqty": 2,
            "loandt": "",
            "sysprocseq": 4,
            "price": 75300,
            "janrt": "100.00",
            "jdat": 0,
            "jpms": 0,
            "hname": "삼성전자",
            "appamt": 150283,
            "sunikrt": "25.22",
            "jonggb": "3",
            "msat": 2,
            "tax": 300,
            "pamt": 60000,
            "jpmd": 0,
            "marketgb": "",
            "jangb": "",
            "dtsunik": 30270,
            "expcode": "005930",
            "mdat": 0,
            "mpms": 60000,
            "lastdt": ""
        }
    ],
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-t0425"></a>
## `t0425` 주식체결/미체결

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
| `t0425InBlock` | t0425InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-chegb` | 체결구분 | String | Y | 1 | 0;전체<br/>1:체결<br/>2:미체결 |
| `&nbsp;&nbsp;-medosu` | 매매구분 | String | Y | 1 | 0:전체<br/>1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-sortgb` | 정렬순서 | String | Y | 1 | 1:주문번호 역순<br/>2:주문번호 순 |
| `&nbsp;&nbsp;-cts_ordno` | 주문번호 | String | Y | 10 | 연속조회시 OutBlock의 동일필드 입력 |


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
| `t0425OutBlock` | t0425OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-tqty` | 총주문수량 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tcheqty` | 총체결수량 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tordrem` | 총미체결수량 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-cmss` | 추정수수료 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tamt` | 총주문금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tmdamt` | 총매도체결금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tmsamt` | 총매수체결금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tax` | 추정제세금 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-cts_ordno` | 주문번호 | String | Y | 10 | - |
| `t0425OutBlock1` | t0425OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-ordno` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-medosu` | 구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-qty` | 주문수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-price` | 주문가격 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-cheqty` | 체결수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-cheprice` | 체결가격 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-ordrem` | 미체결잔량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-cfmqty` | 확인수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-status` | 상태 | String | Y | 20 | - |
| `&nbsp;&nbsp;-orgordno` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ordgb` | 유형 | String | Y | 20 | - |
| `&nbsp;&nbsp;-ordtime` | 주문시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ordermtd` | 주문매체 | String | Y | 10 | - |
| `&nbsp;&nbsp;-sysprocseq` | 처리순번 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-hogagb` | 호가유형 | String | Y | 2 | - |
| `&nbsp;&nbsp;-price1` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-orggb` | 주문구분 | String | Y | 2 | - |
| `&nbsp;&nbsp;-singb` | 신용구분 | String | Y | 2 | - |
| `&nbsp;&nbsp;-loandt` | 대출일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
  "t0425InBlock": {
    "expcode": "005930",
    "chegb": "0",
    "medosu": "0",
    "sortgb": "2",
    "cts_ordno": " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t0425OutBlock1": [
        {
            "orgordno": 0,
            "ordrem": 2,
            "cfmqty": 0,
            "ordgb": "보통",
            "cheqty": 0,
            "orggb": "02",
            "ordno": 84,
            "loandt": "",
            "price": 60000,
            "sysprocseq": 88,
            "singb": "00",
            "qty": 2,
            "hogagb": "00",
            "expcode": "005930",
            "medosu": "매수",
            "cheprice": 0,
            "ordtime": "08410730",
            "ordermtd": "씽(Xing)-F",
            "price1": 71900,
            "status": "접수"
        }
    ],
    "t0425OutBlock": {
        "tcheqty": 0,
        "tamt": 0,
        "tqty": 2,
        "cmss": 0,
        "tmsamt": 0,
        "tax": 0,
        "tmdamt": 0,
        "cts_ordno": "",
        "tordrem": 2
    },
    "rsp_msg": "조회가 완료되었습니다."
}
```
