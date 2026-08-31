# [선물/옵션] 계좌

> LS증권 OPEN API 정의서 · 그룹: **선물/옵션** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=2f1eea77-5606-4512-93c6-31b21d2ece90&api_id=09a668df-d7e8-4b5c-977f-91d1429b931a)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `09a668df-d7e8-4b5c-977f-91d1429b931a` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/futureoption/accno` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 주간/야간 선물옵션 계좌별 거래내역 및 잔고 등 계좌에 관련된 서비스를 확인할 수 있습니다. |

## TR 목록 (13건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 선물옵션 계좌 주문체결내역 조회 | [CFOAQ00600](account.md#tr-CFOAQ00600) | 1 | 1 | 10 |
| 선물옵션 계좌잔고 및 평가현황3 | [CFOAQ50600](account.md#tr-CFOAQ50600) | 1 | 1 | - |
| 선물옵션 주문가능수량조회 | [CFOAQ10100](account.md#tr-CFOAQ10100) | 1 | 1 | 10 |
| 선물옵션 계좌예탁금증거금조회 | [CFOBQ10500](account.md#tr-CFOBQ10500) | 1 | 1 | 10 |
| 선물옵션가정산예탁금상세 | [CFOEQ11100](account.md#tr-CFOEQ11100) | 1 | 1 | 5 |
| 선물옵션 일별 계좌손익내역 | [CFOEQ82600](account.md#tr-CFOEQ82600) | 1 | 1 | 10 |
| 계좌 미결제 약정현황(평균가) | [CFOFQ02400](account.md#tr-CFOFQ02400) | 1 | 1 | 10 |
| 선물/옵션체결/미체결 | [t0434](account.md#tr-t0434) | 2 | 1 | 10 |
| 선물/옵션잔고평가(이동평균) | [t0441](account.md#tr-t0441) | 2 | 1 | 10 |
| KRX야간파생 주문가능수량 조회 | [CCENQ10100](account.md#tr-CCENQ10100) | 1 | 1 | 10 |
| KRX야간파생 주문/체결내역 조회 | [CCENQ30100](account.md#tr-CCENQ30100) | 1 | 1 | 3 |
| KRX야간파생 잔고조회 | [CCENQ90200](account.md#tr-CCENQ90200) | 1 | 1 | 1 |
| 선물옵션 기간별 계좌 수익률 현황 | [FOCCQ33700](account.md#tr-FOCCQ33700) | 1 | 1 | 10 |

---

<a id="tr-CFOAQ00600"></a>
## `CFOAQ00600` 선물옵션 계좌 주문체결내역 조회

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
| `CFOAQ00600InBlock1` | CFOAQ00600InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoClssCode` | 선물옵션분류코드 | String | Y | 2 | 00@전체<br/>11@선물<br/>12@옵션 |
| `&nbsp;&nbsp;-PrdgrpCode` | 상품군코드 | String | Y | 2 | 00:전체<br/>01:주가지수<br/>02:개별주식<br/>03:가공채권<br/>04:통화<br/>05:상품<br/>06:금리 |
| `&nbsp;&nbsp;-PrdtExecTpCode` | 체결구분 | String | Y | 1 | 0:전체<br/>1:체결<br/>2:미체결 |
| `&nbsp;&nbsp;-StnlnSeqTp` | 정렬순서구분 | String | Y | 1 | 3:역순<br/>4:정순 |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | 99 |


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
| `CFOAQ00600OutBlock1` | CFOAQ00600OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoClssCode` | 선물옵션분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-PrdgrpCode` | 상품군코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-PrdtExecTpCode` | 체결구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-StnlnSeqTp` | 정렬순서구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `CFOAQ00600OutBlock2` | CFOAQ00600OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-FutsOrdQty` | 선물주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsExecQty` | 선물체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptOrdQty` | 옵션주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptExecQty` | 옵션체결수량 | Number | Y | 16 | - |
| `CFOAQ00600OutBlock3` | CFOAQ00600OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-OrdTime` | 주문시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-MrcTpNm` | 정정취소구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnNm` | 선물옵션호가유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdPrc` | 주문가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdTpNm` | 주문구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExecTpNm` | 체결구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExecPrc` | 체결가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CtrctTime` | 약정시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-CtrctNo` | 약정번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ExecNo` | 체결번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BnsplAmt` | 매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UserId` | 사용자ID | String | Y | 16 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-CommdaCodeNm` | 통신매체코드명 | String | Y | 40 | - |


### 요청 Example

```json
{
  "CFOAQ00600InBlock1": {
    "RecCnt": 1,
    "QrySrtDt": "20230426",
    "QryEndDt": "20230426",
    "FnoClssCode": "00",
    "PrdgrpCode": "00",
    "PrdtExecTpCode": "0",
    "StnlnSeqTp": "4",
    "CommdaCode": "99"
  }
}
```

### 응답 Example

```json
{
  "CFOAQ00600OutBlock1": {
    "RecCnt": 1,
    "AcntNo": "20277932702",
    "InptPwd": "********",
    "QrySrtDt": "20230426",
    "QryEndDt": "20230426",
    "FnoClssCode": "00",
    "PrdgrpCode": "00",
    "PrdtExecTpCode": "0",
    "StnlnSeqTp": "4",
    "CommdaCode": "99"
  },
  "CFOAQ00600OutBlock2": {
    "RecCnt": 1,
    "AcntNm": "충조감",
    "FutsOrdQty": 0,
    "FutsExecQty": 0,
    "OptOrdQty": 0,
    "OptExecQty": 0
  },
  "CFOAQ00600OutBlock3": [],
  "rsp_cd": "00200",
  "rsp_msg": "조회내역이 없습니다."
}
```

---

<a id="tr-CFOAQ50600"></a>
## `CFOAQ50600` 선물옵션 계좌잔고 및 평가현황3

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CFOAQ50600InBlock1` | CFOAQ50600InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BalEvalTp` | 잔고평가구분 | String | Y | 1 | 0@기본설정<br/>1@이동평균법<br/>2@선입선출법 |
| `&nbsp;&nbsp;-FutsPrcEvalTp` | 선물가격평가구분 | String | Y | 1 | 1@당초가<br/>2@전일종가<br/> |
| `&nbsp;&nbsp;-LqdtQtyQryTp` | 청산수량조회구분 | String | Y | 1 | 1@청산수량산출 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `CFOAQ50600OutBlock1` | CFOAQ50600OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-LqdtQtyQryTp` | 청산수량조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FutsPrcEvalTp` | 선물가격평가구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BalEvalTp` | 잔고평가구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `CFOAQ50600OutBlock2` | CFOAQ50600OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-EvalRat` | 평가비율 | String | Y | 7.2 | - |
| `&nbsp;&nbsp;-BaseEvalAmt` | 기준평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NetPnlAmt` | 순손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TotPnlAmt` | 총손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBnsAmt` | 옵션매매금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsAdjstDfamt` | 선물정산차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBnsplAmt` | 옵션매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalAmt` | 옵션평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalPnlAmt` | 옵션평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsEvalPnlAmt` | 선물평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblOdpnt` | 미수연체료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RcvblAmt` | 미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CmsnAmt` | 수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyAddMgn` | 현금추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMgnTotamt` | 추가증거금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-MnyMaintMgn` | 현금유지증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MtmgnTotamt` | 유지증거금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-MnyCsgnMgn` | 현금위탁증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CsgnMgnTotamt` | 위탁증거금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleTotAmt` | 주문가능총금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-PsnOutAbleSubstAmt` | 인출가능대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PsnOutAbleCurAmt` | 인출가능현금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PsnOutAbleTotAmt` | 인출가능총금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrSubstAmt` | 외화대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpstgSubst` | 예탁대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpstgMny` | 예탁현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpsamtTotamt` | 예탁금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyEvalDpstgAmt` | 현금평가예탁금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-EvalDpsamtTotamt` | 평가예탁금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcntEvalRat` | 계좌평가비율 | String | Y | 7.2 | - |
| `CFOAQ50600OutBlock3` | CFOAQ50600OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-BnsplAmt` | 매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LqdtAbleQty` | 청산가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalRat` | 평가비율 | String | Y | 7.2 | - |
| `&nbsp;&nbsp;-EvalPnl` | 평가손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalAmt` | 평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoCmpPrc` | 선물옵션대비가 | String | Y | 27.8 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | String | Y | 18.6 | - |
| `&nbsp;&nbsp;-FnoNowPrc` | 선물옵션현재가 | String | Y | 27.8 | - |
| `&nbsp;&nbsp;-FnoAvrPrc` | 평균가 | String | Y | 19.8 | - |
| `&nbsp;&nbsp;-UnsttQty` | 미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |


### 요청 Example

```json
{
  "CFOAQ50600InBlock1": {
    "RecCnt" : 1,
    "OrdDt" : "20240626",
    "BalEvalTp" : "1",
    "FutsPrcEvalTp" : "1",
    "LqtQtyQryTp" : "1"
  }
}
```

### 응답 Example

```json
{
    "CFOAQ50600OutBlock1": {
        "RecCnt": 1,
        "AcntNo": "20277932702",
        "InptPwd": "********",
        "OrdDt": "20240626",
        "BalEvalTp": "1",
        "FutsPrcEvalTp": "1",
        "LqdtQtyQryTp": ""
    },
    "CFOAQ50600OutBlock2": {
        "RecCnt": 1,
        "AcntNm": "충조감",
        "EvalDpsamtTotamt": -2579000,
        "MnyEvalDpstgAmt": -2579000,
        "DpsamtTotamt": -2579000,
        "DpstgMny": -2579000,
        "DpstgSubst": 0,
        "FcurrSubstAmt": 0,
        "PsnOutAbleTotAmt": 0,
        "PsnOutAbleCurAmt": 0,
        "PsnOutAbleSubstAmt": 0,
        "OrdAbleTotAmt": 0,
        "MnyOrdAbleAmt": 0,
        "CsgnMgnTotamt": 1742759,
        "MnyCsgnMgn": 0,
        "MtmgnTotamt": 1161839,
        "MnyMaintMgn": 0,
        "AddMgnTotamt": 4321759,
        "MnyAddMgn": 3450380,
        "CmsnAmt": 0,
        "RcvblAmt": 2579000,
        "RcvblOdpnt": 13887,
        "FutsEvalPnlAmt": 0,
        "OptEvalPnlAmt": 0,
        "OptEvalAmt": 0,
        "OptBnsplAmt": 0,
        "FutsAdjstDfamt": 0,
        "OptBnsAmt": 0,
        "TotPnlAmt": 0,
        "NetPnlAmt": 0,
        "BaseEvalAmt": 0,
        "AcntEvalRat": "0.00",
        "EvalRat": "0.00"
    },
    "CFOAQ50600OutBlock3": [],
    "rsp_cd": "00136",
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CFOAQ10100"></a>
## `CFOAQ10100` 선물옵션 주문가능수량조회

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
| `CFOAQ10100InBlock1` | CFOAQ10100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | 1@일반<br/>2@금액<br/>3@비율 |
| `&nbsp;&nbsp;-OrdAmt` | 주문금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RatVal` | 비율값 | Number | Y | 19.8 | 0 |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | 1@매도<br/>2@매수 |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | 00@지정가<br/>03@시장가<br/>05@조건부지정가<br/>06@최유리지정가 |


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
| `CFOAQ10100OutBlock1` | CFOAQ10100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdAmt` | 주문금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RatVal` | 비율값 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `CFOAQ10100OutBlock2` | CFOAQ10100OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-QryDt` | 조회일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoNowPrc` | 선물옵션현재가 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NewOrdAbleQty` | 신규주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LqdtOrdAbleQty` | 청산주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UsePreargMgn` | 사용예정증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UsePreargMnyMgn` | 사용예정현금증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOAQ10100InBlock1": {
    "RecCnt": 1,
    "QryTp": "1",
    "OrdAmt": 0,
    "RatVal": 0.0,
    "FnoIsuNo": "101T6000",
    "BnsTpCode": "1",
    "FnoOrdPrc": 0.0,
    "FnoOrdprcPtnCode": "00"
  }
}
```

### 응답 Example

```json
{
  "CFOAQ10100OutBlock1": {
    "RecCnt": 1,
    "AcntNo": "20277932702",
    "Pwd": "********",
    "QryTp": "1",
    "OrdAmt": 0,
    "RatVal": "0.00000000",
    "FnoIsuNo": "101T6000",
    "BnsTpCode": "1",
    "FnoOrdPrc": "0.00000000",
    "FnoOrdprcPtnCode": "00"
  },
  "CFOAQ10100OutBlock2": {
    "RecCnt": 1,
    "AcntNm": "충조감",
    "QryDt": "20230609",
    "FnoNowPrc": "0.00000000",
    "OrdAbleQty": 38,
    "NewOrdAbleQty": 36,
    "LqdtOrdAbleQty": 2,
    "UsePreargMgn": 228367620,
    "UsePreargMnyMgn": 114183792,
    "OrdAbleAmt": 230782886,
    "MnyOrdAbleAmt": 230782886
  },
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CFOBQ10500"></a>
## `CFOBQ10500` 선물옵션 계좌예탁금증거금조회

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
| `CFOBQ10500InBlock1` | CFOBQ10500InBlock1 | Object | Y | - | - |


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
| `CFOBQ10500OutBlock1` | CFOBQ10500OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `CFOBQ10500OutBlock2` | CFOBQ10500OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-DpsamtTotamt` | 예탁금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstAmt` | 대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FilupDpsamtTotamt` | 충당예탁금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FilupDps` | 충당예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsPnlAmt` | 선물손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-WthdwAbleAmt` | 인출가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PsnOutAbleCurAmt` | 인출가능현금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PsnOutAbleSubstAmt` | 인출가능대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Mgn` | 증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyMgn` | 현금증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMgn` | 추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyAddMgn` | 현금추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AmtPrdayChckInAmt` | 금전일수표입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoPrdaySubstSellAmt` | 선물옵션전일대용매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoCrdaySubstSellAmt` | 선물옵션금일대용매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoPrdayFdamt` | 선물옵션전일가입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoCrdayFdamt` | 선물옵션금일가입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FcurrSubstAmt` | 외화대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoAcntAfmgnNm` | 선물옵션계좌사후증거금명 | String | Y | 20 | - |
| `CFOBQ10500OutBlock3` | CFOBQ10500OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-PdGrpCodeNm` | 상품군코드명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-NetRiskMgn` | 순위험증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrcMgn` | 가격증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SprdMgn` | 스프레드증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PrcFlctMgn` | 가격변동증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MinMgn` | 최소증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdMgn` | 주문증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptNetBuyAmt` | 옵션순매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CsgnMgn` | 위탁증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MaintMgn` | 유지증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyExecAmt` | 선물매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSellExecAmt` | 선물매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyExecAmt` | 옵션매수체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSellExecAmt` | 옵션매도체결금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsPnlAmt` | 선물손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TotRiskCsgnMgn` | 총위험위탁증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UndCsgnMgn` | 인수도위탁증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnRdctAmt` | 증거금감면금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOBQ10500InBlock1": {
    "RecCnt": 1
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CFOBQ10500OutBlock1": {
        "RecCnt": 1,
        "AcntNo": "20277932702",
        "Pwd": "********"
    },
    "CFOBQ10500OutBlock3": [
    ],
    "CFOBQ10500OutBlock2": {
        "PsnOutAbleSubstAmt": 0,
        "FnoPrdayFdamt": 0,
        "OrdAbleAmt": 262440611,
        "MnyOrdAbleAmt": 262440611,
        "FcurrSubstAmt": 0,
        "Dps": 262500611,
        "MnyAddMgn": 0,
        "FnoCrdaySubstSellAmt": 0,
        "AddMgn": 0,
        "AmtPrdayChckInAmt": 0,
        "FnoAcntAfmgnNm": "사전증거금 계좌",
        "RecCnt": 1,
        "FilupDps": 262500611,
        "Mgn": 60000,
        "AcntNm": "",
        "DpsamtTotamt": 262500611,
        "MnyMgn": 60000,
        "SubstAmt": 0,
        "FilupDpsamtTotamt": 262500611,
        "FnoPrdaySubstSellAmt": 0,
        "FutsPnlAmt": 0,
        "WthdwAbleAmt": 262440611,
        "FnoCrdayFdamt": 0,
        "PsnOutAbleCurAmt": 262440611
    },
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CFOEQ11100"></a>
## `CFOEQ11100` 선물옵션가정산예탁금상세

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
| `CFOEQ11100InBlock1` | CFOEQ11100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-BnsDt` | 매매일 | String | Y | 8 | - |


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
| `CFOEQ11100OutBlock1` | CFOEQ11100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BnsDt` | 매매일 | String | Y | 8 | - |
| `CFOEQ11100OutBlock2` | CFOEQ11100OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OpnmkDpsamtTotamt` | 개장시예탁금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OpnmkDps` | 개장시예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OpnmkMnyrclAmt` | 개장시현금미수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OpnmkSubstAmt` | 개장시대용금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TotAmt` | 총금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyrclAmt` | 현금미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstDsgnAmt` | 대용지정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CsgnMgn` | 위탁증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyCsgnMgn` | 현금위탁증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MaintMgn` | 유지증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyMaintMgn` | 현금유지증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OutAbleAmt` | 출금가능총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutAbleAmt` | 출금가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SubstOutAbleAmt` | 출금가능대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMgnOcrTpCode` | 추가증거금구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AddMgn` | 추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyAddMgn` | 현금추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayTotAmt` | 익일예탁총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayDps` | 익일예탁현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMnyrclAmt` | 익일미수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdaySubstAmt` | 익일예탁대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayCsgnMgn` | 익일위탁증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMnyCsgnMgn` | 익일위탁증거금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMaintMgn` | 익일유지증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMnyMaintMgn` | 익일유지증거금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayOutAbleAmt` | 익일인출가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMnyoutAbleAmt` | 익일인출가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdaySubstOutAbleAmt` | 익일인출가능대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayOrdAbleAmt` | 익일주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMnyOrdAbleAmt` | 익일주문가능현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayAddMgnTp` | 익일추가증거금구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-NtdayAddMgn` | 익일추가증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdayMnyAddMgn` | 익일추가증거금현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NtdaySettAmt` | 익일결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalDpsamtTotamt` | 평가예탁금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-MnyEvalDpstgAmt` | 현금평가예탁금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-DpsamtUtlfeeGivPrergAmt` | 예탁금이용료지급예정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TaxAmt` | 세금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CsgnMgnrat` | 위탁증거금 비율 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-CsgnMnyMgnrat` | 위탁증거금현금비율 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-DpstgTotamtLackAmt` | 예탁총액부족금액(위탁증거금기준) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpstgMnyLackAmt` | 예탁현금부족금액(위탁증거금기준) | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RealInAmt` | 실입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InAmt` | 입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OutAmt` | 출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsAdjstDfamt` | 선물정산차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsThdayDfamt` | 선물당일차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsUpdtDfamt` | 선물갱신차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsLastSettDfamt` | 선물최종결제차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSettDfamt` | 옵션결제차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyAmt` | 옵션매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSellAmt` | 옵션매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptXrcDfamt` | 옵션행사차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptAsgnDfamt` | 옵션배정차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RealGdsUndAmt` | 실물인수도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RealGdsUndAsgnAmt` | 실물인수도배정대금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RealGdsUndXrcAmt` | 실물인수도행사대금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CmsnAmt` | 수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsCmsn` | 선물수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptCmsn` | 옵션수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsCtrctQty` | 선물약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsCtrctAmt` | 선물약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptCtrctQty` | 옵션약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptCtrctAmt` | 옵션약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsUnsttQty` | 선물미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsUnsttAmt` | 선물미결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptUnsttQty` | 옵션미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptUnsttAmt` | 옵션미결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyUnsttQty` | 선물매수미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyUnsttAmt` | 선물매수미결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSellUnsttQty` | 선물매도미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSellUnsttAmt` | 선물매도미결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyUnsttQty` | 옵션매수미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyUnsttAmt` | 옵션매수미결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSellUnsttQty` | 옵션매도미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSellUnsttAmt` | 옵션매도미결제금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyctrQty` | 선물매수약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyctrAmt` | 선물매수약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSlctrQty` | 선물매도약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSlctrAmt` | 선물매도약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyctrQty` | 옵션매수약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyctrAmt` | 옵션매수약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSlctrQty` | 옵션매도약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSlctrAmt` | 옵션매도약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBnsplAmt` | 선물매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBnsplAmt` | 옵션매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsEvalPnlAmt` | 선물평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalPnlAmt` | 옵션평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsEvalAmt` | 선물평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalAmt` | 옵션평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktEndAfMnyInAmt` | 장종료후현금입금금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktEndAfMnyOutAmt` | 장종료후현금출금금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktEndAfSubstDsgnAmt` | 장종료후대용지정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MktEndAfSubstAbndAmt` | 장종료후대용해지금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOEQ11100InBlock1": {
    "RecCnt": 1,
    "BnsDt": "20230614"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CFOEQ11100OutBlock2": {
        "FutsBnsplAmt": 0,
        "NtdayMnyrclAmt": 0,
        "OpnmkDpsamtTotamt": 256850611,
        "NtdayMnyAddMgn": 0,
        "MnyCsgnMgn": 57091905,
        "MktEndAfSubstDsgnAmt": 0,
        "OptXrcDfamt": 0,
        "MnyrclAmt": 0,
        "FutsSellUnsttAmt": 0,
        "NtdayMaintMgn": 0,
        "OptUnsttAmt": 0,
        "FutsCmsn": 17970,
        "NtdaySettAmt": -15642970,
        "MnyOrdAbleAmt": 148316801,
        "NtdayAddMgn": 0,
        "FutsSellUnsttQty": 0,
        "OptBuyUnsttAmt": 0,
        "MnyMaintMgn": 0,
        "CsgnMgnrat": "0.00",
        "DpstgTotamtLackAmt": 0,
        "OptUnsttQty": 0,
        "SubstDsgnAmt": 0,
        "OpnmkSubstAmt": 0,
        "OpnmkMnyrclAmt": 0,
        "NtdayTotAmt": 256850611,
        "NtdaySubstOutAbleAmt": 0,
        "OptEvalPnlAmt": 0,
        "MaintMgn": 0,
        "CsgnMgn": 114183810,
        "FutsAdjstDfamt": -15625000,
        "OptSlctrQty": 0,
        "OptSellUnsttAmt": 0,
        "FutsCtrctQty": 7,
        "Dps": 262500611,
        "FutsBuyctrQty": 11,
        "RealGdsUndXrcAmt": 0,
        "AddMgn": 0,
        "NtdayCsgnMgn": 0,
        "DpstgMnyLackAmt": 0,
        "FutsLastSettDfamt": 0,
        "NtdayMnyMaintMgn": 0,
        "OptSellUnsttQty": 0,
        "OptSlctrAmt": 0,
        "FutsBuyctrAmt": 941275000,
        "AddMgnOcrTpCode": "0",
        "NtdayOrdAbleAmt": 256850611,
        "OpnmkDps": 256850611,
        "TotAmt": 262500611,
        "MnyAddMgn": 0,
        "FutsBuyUnsttAmt": 941275000,
        "OptAsgnDfamt": 0,
        "RecCnt": 1,
        "InAmt": 0,
        "FutsCtrctAmt": 599025000,
        "MnyoutAbleAmt": 148298831,
        "NtdayMnyCsgnMgn": 0,
        "OptBuyctrQty": 0,
        "FutsSlctrAmt": 0,
        "FutsEvalPnlAmt": 1075000,
        "FutsUnsttQty": 11,
        "NtdaySubstAmt": 0,
        "MnyEvalDpstgAmt": 256850611,
        "OptBuyctrAmt": 0,
        "FutsUnsttAmt": 941275000,
        "FutsBuyUnsttQty": 11,
        "OptCtrctQty": 0,
        "SubstOutAbleAmt": 0,
        "MktEndAfMnyInAmt": 0,
        "NtdayMnyoutAbleAmt": 236850611,
        "MktEndAfMnyOutAmt": 0,
        "NtdayMnyOrdAbleAmt": 256850611,
        "NtdayDps": 256850611,
        "DpsamtUtlfeeGivPrergAmt": 0,
        "NtdayAddMgnTp": "0",
        "RealGdsUndAmt": 0,
        "RealInAmt": 0,
        "EvalDpsamtTotamt": 256850611,
        "OptSellAmt": 0,
        "OptBuyUnsttQty": 0,
        "OutAbleAmt": 148298831,
        "FutsEvalAmt": 925650000,
        "NtdayOutAbleAmt": 236850611,
        "RealGdsUndAsgnAmt": 0,
        "OutAmt": 0,
        "FutsThdayDfamt": -15625000,
        "OptBnsplAmt": 0,
        "OptCmsn": 0,
        "TaxAmt": 0,
        "OptSettDfamt": 0,
        "OptCtrctAmt": 0,
        "FutsUpdtDfamt": 0,
        "OrdAbleAmt": 148316801,
        "CsgnMnyMgnrat": "0.00",
        "MktEndAfSubstAbndAmt": 0,
        "OptBuyAmt": 0,
        "CmsnAmt": 17970,
        "OptEvalAmt": 0,
        "FutsSlctrQty": 0,
        "AcntNm": ""
    },
    "CFOEQ11100OutBlock1": {
        "BnsDt": "20230614",
        "RecCnt": 1,
        "AcntNo": "20277932702",
        "Pwd": "********"
    },
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CFOEQ82600"></a>
## `CFOEQ82600` 선물옵션 일별 계좌손익내역

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
| `CFOEQ82600InBlock1` | CFOEQ82600InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | 1@일자별<br/>2@월별<br/>3@주간별 |
| `&nbsp;&nbsp;-StnlnSeqTp` | 정렬순서구분 | String | Y | 1 | 1@순<br/>2@역순 |
| `&nbsp;&nbsp;-FnoBalEvalTpCode` | 선물옵션잔고평가구분코드 | String | Y | 1 | 0:계좌에 따라 다르며 기본적으로는 선입선출<br/>1:이동평균<br/>2:선입선출 |


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
| `CFOEQ82600OutBlock1` | CFOEQ82600OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-StnlnSeqTp` | 정렬순서구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FnoBalEvalTpCode` | 선물옵션잔고평가구분코드 | String | Y | 1 | - |
| `CFOEQ82600OutBlock2` | CFOEQ82600OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-FutsAdjstDfamt` | 선물정산차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBnsplAmt` | 옵션매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoCmsnAmt` | 선물옵션수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PnlSumAmt` | 손익합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyinSumAmt` | 입금합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyoutSumAmt` | 출금합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `CFOEQ82600OutBlock3` | CFOEQ82600OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-QryDt` | 조회일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-DpstgTotamt` | 예탁총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpstgMny` | 예탁현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoMgn` | 선물옵션증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsPnlAmt` | 선물손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBsnPnlAmt` | 옵션매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalPnlAmt` | 옵션평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CmsnAmt` | 수수료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SumAmt1` | 합계금액1 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SumAmt2` | 합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PnlSumAmt` | 손익합계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyAmt` | 선물매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSellAmt` | 선물매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBuyAmt` | 옵션매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptSellAmt` | 옵션매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InAmt` | 입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OutAmt` | 출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalAmt` | 평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddupEvalAmt` | 합산평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Amt2` | 금액2 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CFOEQ82600InBlock1": {
    "RecCnt": 1,
    "QrySrtDt": "20230501",
    "QryEndDt": "20230516",
    "QryTp": "1",
    "StnlnSeqTp": "1",
    "FnoBalEvalTpCode": "0"
  }
}
```

### 응답 Example

```json
{
    "CFOEQ82600OutBlock2": {
        "FutsAdjstDfamt": 0,
        "PnlSumAmt": 0,
        "RecCnt": 1,
        "OptBnsplAmt": 0,
        "FnoCmsnAmt": 0,
        "MnyinSumAmt": 0,
        "AcntNm": "충조감",
        "MnyoutSumAmt": 0
    },
    "rsp_cd": "00136",
    "CFOEQ82600OutBlock1": {
        "RecCnt": 1,
        "StnlnSeqTp": "1",
        "AcntNo": "20277932702",
        "FnoBalEvalTpCode": "0",
        "QrySrtDt": "20230516",
        "Pwd": "********",
        "QryEndDt": "20230516",
        "QryTp": "1"
    },
    "rsp_msg": "조회가 완료되었습니다.",
    "CFOEQ82600OutBlock3": [
        {
            "OptBsnPnlAmt": 0,
            "PnlSumAmt": 0,
            "QryDt": "20230516",
            "OptSellAmt": 0,
            "DpstgMny": 0,
            "OptBuyAmt": 0,
            "FutsBuyAmt": 0,
            "CmsnAmt": 0,
            "FutsSellAmt": 0,
            "AddupEvalAmt": 0,
            "OutAmt": 0,
            "InAmt": 0,
            "Amt2": 0,
            "FnoMgn": 0,
            "DpstgTotamt": 0,
            "FutsPnlAmt": 0,
            "OptEvalPnlAmt": 0,
            "SumAmt2": 0,
            "EvalAmt": 0,
            "SumAmt1": 0
        }
    ]
}
```

---

<a id="tr-CFOFQ02400"></a>
## `CFOFQ02400` 계좌 미결제 약정현황(평균가)

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
| `CFOFQ02400InBlock1` | CFOFQ02400InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RegMktCode` | 등록시장코드 | String | Y | 2 | 99@전체<br/>40@KOSPI<br/>20@KOSDAQ<br/>10@KSE<br/>50@KOFEX |
| `&nbsp;&nbsp;-BuyDt` | 매수일자 | String | Y | 8 | - |


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
| `CFOFQ02400OutBlock1` | CFOFQ02400OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-RegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-BuyDt` | 매수일자 | String | Y | 8 | - |
| `CFOFQ02400OutBlock2` | CFOFQ02400OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-FutsCtrctQty` | 선물약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptCtrctQty` | 옵션약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CtrctQty` | 약정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsCtrctAmt` | 선물약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyctrAmt` | 선물매수약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSlctrAmt` | 선물매도약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CalloptCtrctAmt` | 콜옵션약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CallBuyAmt` | 콜매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CallSellAmt` | 콜매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutoptCtrctAmt` | 풋옵션약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutBuyAmt` | 풋매수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutSellAmt` | 풋매도금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AllCtrctAmt` | 전체약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-BuyctrAsmAmt` | 매수약정누계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-SlctrAsmAmt` | 매도약정누계금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsPnlSum` | 선물손익합계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptPnlSum` | 옵션손익합계 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AllPnlSum` | 전체손익합계 | Number | Y | 16 | - |
| `CFOFQ02400OutBlock3` | CFOFQ02400OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-FnoClssCode` | 선물옵션품목구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FutsSellQty` | 선물매도수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsSellPnl` | 선물매도손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyQty` | 선물매수수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsBuyPnl` | 선물매수손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CallSellQty` | 콜매도수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CallSellPnl` | 콜매도손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CallBuyQty` | 콜매수수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CallBuyPnl` | 콜매수손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutSellQty` | 풋매도수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutSellPnl` | 풋매도손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutBuyQty` | 풋매수수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PutBuyPnl` | 풋매수손익 | Number | Y | 16 | - |
| `CFOFQ02400OutBlock4` | CFOFQ02400OutBlock4 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-BalQty` | 잔고수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoAvrPrc` | 평균가 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-BgnAmt` | 당초금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ThdayLqdtQty` | 당일청산수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Curprc` | 현재가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-EvalAmt` | 평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalPnlAmt` | 평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalErnrat` | 평가수익률 | Number | Y | 12.6 | - |


### 요청 Example

```json
{
  "CFOFQ02400InBlock1": {
    "RecCnt": 1,
    "RegMktCode": "99",
    "BuyDt": ""
  }
}
```

### 응답 Example

```json
{
  "CFOFQ02400OutBlock1": {
    "RecCnt": 1,
    "AcntNo": "20277932702",
    "Pwd": "********",
    "RegMktCode": "99",
    "BuyDt": "20230609"
  },
  "CFOFQ02400OutBlock2": {
    "RecCnt": 1,
    "AcntNm": "충조감",
    "FutsCtrctQty": 4,
    "OptCtrctQty": 0,
    "CtrctQty": 4,
    "FutsCtrctAmt": 342250000,
    "FutsBuyctrAmt": 342250000,
    "FutsSlctrAmt": 0,
    "CalloptCtrctAmt": 0,
    "CallBuyAmt": 0,
    "CallSellAmt": 0,
    "PutoptCtrctAmt": 0,
    "PutBuyAmt": 0,
    "PutSellAmt": 0,
    "AllCtrctAmt": 342250000,
    "BuyctrAsmAmt": 342250000,
    "SlctrAsmAmt": 0,
    "FutsPnlSum": -16700000,
    "OptPnlSum": 0,
    "AllPnlSum": -16700000
  },
  "CFOFQ02400OutBlock3": [
    {
      "FnoClssCode": "1",
      "FutsSellQty": 0,
      "FutsSellPnl": 0,
      "FutsBuyQty": 4,
      "FutsBuyPnl": -16700000,
      "CallSellQty": 0,
      "CallSellPnl": 0,
      "CallBuyQty": 0,
      "CallBuyPnl": 0,
      "PutSellQty": 0,
      "PutSellPnl": 0,
      "PutBuyQty": 0,
      "PutBuyPnl": 0
    },
    {
      "FnoClssCode": "2",
      "FutsSellQty": 0,
      "FutsSellPnl": 0,
      "FutsBuyQty": 0,
      "FutsBuyPnl": 0,
      "CallSellQty": 0,
      "CallSellPnl": 0,
      "CallBuyQty": 0,
      "CallBuyPnl": 0,
      "PutSellQty": 0,
      "PutSellPnl": 0,
      "PutBuyQty": 0,
      "PutBuyPnl": 0
    },
    {
      "FnoClssCode": "3",
      "FutsSellQty": 0,
      "FutsSellPnl": 0,
      "FutsBuyQty": 0,
      "FutsBuyPnl": 0,
      "CallSellQty": 0,
      "CallSellPnl": 0,
      "CallBuyQty": 0,
      "CallBuyPnl": 0,
      "PutSellQty": 0,
      "PutSellPnl": 0,
      "PutBuyQty": 0,
      "PutBuyPnl": 0
    }
  ],
  "CFOFQ02400OutBlock4": [
    {
      "IsuNo": "101T6000",
      "IsuNm": "코스피200 F 202306",
      "BnsTpCode": "2",
      "BnsTpNm": "매수",
      "BalQty": 4,
      "FnoAvrPrc": "342.25000000",
      "BgnAmt": 342250000,
      "ThdayLqdtQty": 0,
      "Curprc": "325.55",
      "EvalAmt": 325550000,
      "EvalPnlAmt": -16700000,
      "EvalErnrat": "-4.870000"
    }
  ],
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-t0434"></a>
## `t0434` 선물/옵션체결/미체결

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
| `t0434InBlock` | t0434InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-chegb` | 체결구분 | String | Y | 1 | 0;전체<br/>1:체결<br/>2:미체결 |
| `&nbsp;&nbsp;-sortgb` | 정렬순서 | String | Y | 1 | 1:주문번호 역순<br/>2:주문번호 순<br/> |
| `&nbsp;&nbsp;-cts_ordno` | CTS_주문번호 | String | Y | 7 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_ordno 값으로 설정 |


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
| `t0434OutBlock` | t0434OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_ordno` | CTS_주문번호 | String | Y | 7 | 연속조회키<br/>연속 조회시 이 값을 InBlock의 cts_ordno 필드에 넣어준다. |
| `t0434OutBlock1` | t0434OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-ordno` | 주문번호 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-orgordno` | 원주문번호 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-medosu` | 구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ordgb` | 유형 | String | Y | 20 | - |
| `&nbsp;&nbsp;-qty` | 주문수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-price` | 주문가격 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-cheqty` | 체결수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-cheprice` | 체결가격 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-ordrem` | 미체결잔량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-status` | 상태 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ordtime` | 주문시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ordermtd` | 주문매체 | String | Y | 10 | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-rtcode` | 사유코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-sysprocseq` | 처리순번 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-hogatype` | 호가타입 | String | Y | 1 | - |


### 요청 Example

```json
{
  "t0434InBlock" : {
    "expcode" : "101T9000",
    "chegb" : "0",
    "sortgb" : "2",
    "cts_ordno" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t0434OutBlock1": [
        {
            "orgordno": 0,
            "hogatype": "L",
            "ordrem": 0,
            "ordgb": "지정가",
            "cheqty": 5,
            "ordno": 69104,
            "price": "34225.00",
            "rtcode": "",
            "sysprocseq": 7,
            "qty": 5,
            "expcode": "101T9000",
            "medosu": "매수",
            "cheprice": "34225.00",
            "ordtime": "13074005",
            "ordermtd": "OPEN API",
            "status": "완료"
        },
        {
            "orgordno": 0,
            "hogatype": "L",
            "ordrem": 4,
            "ordgb": "지정가",
            "cheqty": 1,
            "ordno": 69105,
            "price": "34225.00",
            "rtcode": "",
            "sysprocseq": 9,
            "qty": 5,
            "expcode": "101T9000",
            "medosu": "매수",
            "cheprice": "34225.00",
            "ordtime": "13120288",
            "ordermtd": "OPEN API",
            "status": "접수"
        }
    ],
    "rsp_msg": "조회가 완료되었습니다.",
    "t0434OutBlock": {
        "cts_ordno": ""
    }
}
```

---

<a id="tr-t0441"></a>
## `t0441` 선물/옵션잔고평가(이동평균)

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
| `t0441InBlock` | t0441InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_medocd` | CTS_매매구분 | String | Y | 1 | - |


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
| `t0441OutBlock` | t0441OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-tdtsunik` | 매매손익합계 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-cts_expcode` | CTS_종목번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_medocd` | CTS_매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-tappamt` | 평가금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-tsunik` | 평가손익 | Number | Y | 18 | - |
| `t0441OutBlock1` | t0441OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-expcode` | 종목번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-medosu` | 구분 | String | Y | 4 | - |
| `&nbsp;&nbsp;-jqty` | 잔고수량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-cqty` | 청산가능수량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-pamt` | 평균단가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-mamt` | 총매입금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-medocd` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-dtsunik` | 매매손익 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sysprocseq` | 처리순번 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-appamt` | 평가금액 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dtsunik1` | 평가손익 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sunikrt` | 수익율 | Number | Y | 10.2 | - |


### 요청 Example

```json
{
  "t0441InBlock" : {
    "cts_expcode" : "101T9000",
    "cts_medocd" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t0441OutBlock1": [
        {
            "appamt": 850000000,
            "sunikrt": "-66.00",
            "mamt": 855625000,
            "pamt": "34225.00",
            "dtsunik": 0,
            "sysprocseq": 10,
            "price": "34000.00",
            "expcode": "101T9000",
            "dtsunik1": -5625000,
            "medocd": "2",
            "medosu": "매수",
            "jqty": 10,
            "cqty": 10
        }
    ],
    "t0441OutBlock": {
        "cts_expcode": "",
        "tsunik": -5625000,
        "tappamt": 850000000,
        "tdtsunik": 0,
        "cts_medocd": ""
    },
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CCENQ10100"></a>
## `CCENQ10100` KRX야간파생 주문가능수량 조회

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
| `CCENQ10100InBlock1` | CCENQ10100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | 1:일반<br/>2:금액<br/>3:비율 |
| `&nbsp;&nbsp;-OrdAmt` | 주문금액 | Number | Y | 16 | 조회구분이 2일경우만 사용, 그외 0 |
| `&nbsp;&nbsp;-RatVal` | 비율값 | Number | Y | 19.8 | 조회구분이 3일경우만 사용, 그외 0 |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | 1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | 00:지정가<br/>03:시장가<br/>05:조건부지정가<br/>06:최유리지정가 |


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
| `CCENQ10100OutBlock1` | CCENQ10100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdAmt` | 주문금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RatVal` | 비율값 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `CCENQ10100OutBlock2` | CCENQ10100OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-QryDt` | 조회일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoNowPrc` | 선물옵션현재가 | Number | Y | 27.8 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-NewOrdAbleQty` | 신규주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LqdtOrdAbleQty` | 청산주문가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UsePreargMgn` | 사용예정증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UsePreargMnyMgn` | 사용예정현금증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CCENQ10100InBlock1": {
    "RecCnt": 1,
    "QryTp": "1",
    "OrdAmt": 0,
    "RatVal": 0.0,
    "FnoIsuNo": "101W6000",
    "BnsTpCode": "1",
    "FnoOrdPrc": 0.0,
    "FnoOrdprcPtnCode": "00"
  }
}
```

### 응답 Example

```json
{
	"CCENQ10100OutBlock1": {
		"RecCnt": 1,
		"AcntNo": "***********",
		"Pwd": "********",
		"QryTp": "1",
		"OrdAmt": 0,
		"RatVal": "0.00000000",
		"FnoIsuNo": "101W6000",
		"BnsTpCode": "1",
		"FnoOrdPrc": "438.55000000",
		"FnoOrdprcPtnCode": "00"
	},
	"CCENQ10100OutBlock2": {
		"RecCnt": 1,
		"AcntNm": "***",
		"QryDt": "20250607",
		"FnoNowPrc": "438.55000000",
		"OrdAbleQty": 2,
		"NewOrdAbleQty": 2,
		"LqdtOrdAbleQty": 0,
		"UsePreargMgn": 20050754,
		"UsePreargMnyMgn": 10025376,
		"OrdAbleAmt": 20327175,
		"MnyOrdAbleAmt": 20327175
	},
	"rsp_cd": "00136",
	"rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CCENQ30100"></a>
## `CCENQ30100` KRX야간파생 주문/체결내역 조회

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
| `CCENQ30100InBlock1` | CCENQ30100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoClssCode` | 선물옵션분류코드 | String | Y | 2 | 00:전체<br/>11:선물<br/>12:옵션 |
| `&nbsp;&nbsp;-PrdgrpCode` | 상품군코드 | String | Y | 2 | 00:전체 |
| `&nbsp;&nbsp;-PrdtExecTpCode` | 체결구분 | String | Y | 1 | 0:전체,1:체결,2:미체결 |
| `&nbsp;&nbsp;-StnlnSeqTp` | 정렬순서구분 | String | Y | 1 | 1 : 원주문번호역순<br/>2 : 원주문번호순<br/>3 : 주문번호역순<br/>4 : 주문번호순 |
| `&nbsp;&nbsp;-MktTpCode` | 시장구분코드 | String | Y | 1 | 0 : 야간장 |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | 99 |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-FnoTrdPtnCode` | 선물옵션거래유형코드 | String | Y | 2 | 03 |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | 미사용 |
| `&nbsp;&nbsp;-UserId` | 사용자ID | String | Y | 16 | 미사용 |
| `&nbsp;&nbsp;-SrtOrdNo2` | 시작주문번호2 | Number | Y | 10 | 0 |


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
| `CCENQ30100OutBlock1` | CCENQ30100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FnoClssCode` | 선물옵션분류코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-PrdgrpCode` | 상품군코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-PrdtExecTpCode` | 체결구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-StnlnSeqTp` | 정렬순서구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-MktTpCode` | 시장구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-FnoTrdPtnCode` | 선물옵션거래유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |
| `&nbsp;&nbsp;-UserId` | 사용자ID | String | Y | 16 | - |
| `&nbsp;&nbsp;-SrtOrdNo2` | 시작주문번호2 | Number | Y | 10 | - |
| `CCENQ30100OutBlock2` | CCENQ30100OutBlock2 | Number | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-FutsOrdQty` | 선물주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsExecQty` | 선물체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptOrdQty` | 옵션주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptExecQty` | 옵션체결수량 | Number | Y | 16 | - |
| `CCENQ30100OutBlock3` | CCENQ30100OutBlock3 | Number | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdNo` | 주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-OrgOrdNo` | 원주문번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-OrdTime` | 주문시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-MrcTpNm` | 정정취소구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnCode` | 선물옵션호가유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-FnoOrdprcPtnNm` | 선물옵션호가유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-FnoOrdPrc` | 선물옵션주문가격 | Number | Y | 27 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdTpNm` | 주문구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExecTpNm` | 체결구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FnoExecPrc` | 선물옵션체결가 | Number | Y | 27 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CtrctTime` | 약정시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-CtrctNo` | 약정번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-ExecNo` | 체결번호 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-BnsplAmt` | 매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UserId` | 사용자ID | String | Y | 16 | - |
| `&nbsp;&nbsp;-MktClssCodeNm` | 시장분류코드명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-CommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-CommdaCodeNm` | 통신매체코드명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-IpAddr` | IP주소 | String | Y | 16 | - |
| `&nbsp;&nbsp;-TrdPtnTpNm` | 거래유형구분 | String | Y | 20 | - |
| `&nbsp;&nbsp;-GrpId` | 그룹ID | String | Y | 20 | - |


### 요청 Example

```json
{
  "CCENQ30100InBlock1": {
    "RecCnt": 1,
    "QrySrtDt": "00000000",
    "QryEndDt": "00000000",
    "FnoClssCode": "00",
    "PrdgrpCode": "00",
    "PrdtExecTpCode": "0",
    "StnlnSeqTp": "4",
    "MktTpCode": "0",
    "CommdaCode": "99",
    "FnoIsuNo": "",
    "FnoTrdPtnCode": "00",
    "SrtOrdNo2": 0
  }
}
```

### 응답 Example

```json
{
    "CCENQ30100OutBlock1": {
        "RecCnt": 1,
        "AcntNo": "***********",
        "InptPwd": "********",
        "QrySrtDt": "20200101",
        "QryEndDt": "20250610",
        "FnoClssCode": "00",
        "PrdgrpCode": "00",
        "PrdtExecTpCode": "0",
        "StnlnSeqTp": "4",
        "MktTpCode": "0",
        "CommdaCode": "99",
        "FnoIsuNo": "",
        "FnoTrdPtnCode": "00",
        "GrpId": "",
        "UserId": "",
        "SrtOrdNo2": 0
    },
    "CCENQ30100OutBlock2": {
        "RecCnt": 1,
        "AcntNm": "***",
        "FutsOrdQty": 22,
        "FutsExecQty": 22,
        "OptOrdQty": 24,
        "OptExecQty": 24
    },
    "CCENQ30100OutBlock3": [
        {
            "OrdDt": "20250513",
            "OrdNo": 47,
            "OrgOrdNo": 0,
            "OrdTime": "160724349",
            "FnoIsuNo": "201W6215",
            "IsuNm": "C 202506 215.0",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "126.80000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "126.80000000",
            "ExecQty": 1,
            "CtrctTime": "160724373",
            "CtrctNo": 2,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 122,
            "OrgOrdNo": 0,
            "OrdTime": "172453113",
            "FnoIsuNo": "201W6370",
            "IsuNm": "C 202506 370.0",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "0.96000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "0.96000000",
            "ExecQty": 1,
            "CtrctTime": "172453179",
            "CtrctNo": 141,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 123,
            "OrgOrdNo": 0,
            "OrdTime": "172547744",
            "FnoIsuNo": "201W6370",
            "IsuNm": "C 202506 370.0",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "1.01000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "0.96000000",
            "ExecQty": 1,
            "CtrctTime": "172547806",
            "CtrctNo": 142,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 124,
            "OrgOrdNo": 0,
            "OrdTime": "172626017",
            "FnoIsuNo": "201W6370",
            "IsuNm": "C 202506 370.0",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "1.01000000",
            "OrdQty": 13,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "0.96000000",
            "ExecQty": 5,
            "CtrctTime": "172626105",
            "CtrctNo": 144,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "",
            "OrdNo": 0,
            "OrgOrdNo": 0,
            "OrdTime": "",
            "FnoIsuNo": "",
            "IsuNm": "",
            "BnsTpNm": "",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 0,
            "OrdTpNm": "",
            "ExecTpNm": "매수",
            "FnoExecPrc": "0.97000000",
            "ExecQty": 7,
            "CtrctTime": "172626196",
            "CtrctNo": 145,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "",
            "CommdaCodeNm": "",
            "IpAddr": "",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "",
            "OrdNo": 0,
            "OrgOrdNo": 0,
            "OrdTime": "",
            "FnoIsuNo": "",
            "IsuNm": "",
            "BnsTpNm": "",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 0,
            "OrdTpNm": "",
            "ExecTpNm": "매수",
            "FnoExecPrc": "1.01000000",
            "ExecQty": 1,
            "CtrctTime": "172626236",
            "CtrctNo": 146,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "",
            "CommdaCodeNm": "",
            "IpAddr": "",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 125,
            "OrgOrdNo": 0,
            "OrdTime": "172803810",
            "FnoIsuNo": "201W6370",
            "IsuNm": "C 202506 370.0",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "1.59000000",
            "OrdQty": 4,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "1.09000000",
            "ExecQty": 1,
            "CtrctTime": "172803860",
            "CtrctNo": 147,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "",
            "OrdNo": 0,
            "OrgOrdNo": 0,
            "OrdTime": "",
            "FnoIsuNo": "",
            "IsuNm": "",
            "BnsTpNm": "",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 0,
            "OrdTpNm": "",
            "ExecTpNm": "매수",
            "FnoExecPrc": "1.25000000",
            "ExecQty": 2,
            "CtrctTime": "172803970",
            "CtrctNo": 149,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "",
            "CommdaCodeNm": "",
            "IpAddr": "",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "",
            "OrdNo": 0,
            "OrgOrdNo": 0,
            "OrdTime": "",
            "FnoIsuNo": "",
            "IsuNm": "",
            "BnsTpNm": "",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 0,
            "OrdTpNm": "",
            "ExecTpNm": "매수",
            "FnoExecPrc": "1.30000000",
            "ExecQty": 1,
            "CtrctTime": "172804035",
            "CtrctNo": 150,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "",
            "CommdaCodeNm": "",
            "IpAddr": "",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 126,
            "OrgOrdNo": 0,
            "OrdTime": "172935147",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "372.45000000",
            "OrdQty": 3,
            "OrdTpNm": "거부-0306",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 127,
            "OrgOrdNo": 0,
            "OrdTime": "172952180",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "372.40000000",
            "OrdQty": 1,
            "OrdTpNm": "거부-0306",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 128,
            "OrgOrdNo": 0,
            "OrdTime": "173011832",
            "FnoIsuNo": "165W6000",
            "IsuNm": "KTB3 2506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "105.78000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "105.78000000",
            "ExecQty": 1,
            "CtrctTime": "173011877",
            "CtrctNo": 6176,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 129,
            "OrgOrdNo": 0,
            "OrdTime": "173037287",
            "FnoIsuNo": "165W6000",
            "IsuNm": "KTB3 2506",
            "BnsTpNm": "매도",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "03",
            "FnoOrdprcPtnNm": "시장가",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "전매",
            "FnoExecPrc": "105.74000000",
            "ExecQty": 1,
            "CtrctTime": "173037349",
            "CtrctNo": 6177,
            "ExecNo": 0,
            "BnsplAmt": -40000,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250515",
            "OrdNo": 144,
            "OrgOrdNo": 0,
            "OrdTime": "174259586",
            "FnoIsuNo": "201W6360",
            "IsuNm": "C 202506 360.0",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "2.73000000",
            "OrdQty": 3,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "2.73000000",
            "ExecQty": 3,
            "CtrctTime": "174259627",
            "CtrctNo": 178,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250520",
            "OrdNo": 187,
            "OrgOrdNo": 0,
            "OrdTime": "181149619",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "373.65000000",
            "OrdQty": 1,
            "OrdTpNm": "거부-0306",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250520",
            "OrdNo": 188,
            "OrgOrdNo": 0,
            "OrdTime": "181219410",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "368.30000000",
            "OrdQty": 1,
            "OrdTpNm": "거부-0306",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250520",
            "OrdNo": 189,
            "OrgOrdNo": 0,
            "OrdTime": "181229875",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가-전환",
            "FnoOrdPrc": "364.50000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "364.50000000",
            "ExecQty": 1,
            "CtrctTime": "181231060",
            "CtrctNo": 274,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 13,
            "OrgOrdNo": 0,
            "OrdTime": "185838455",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "423.85000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "423.85000000",
            "ExecQty": 1,
            "CtrctTime": "185838478",
            "CtrctNo": 171,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 15,
            "OrgOrdNo": 0,
            "OrdTime": "185923545",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "423.85000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "423.85000000",
            "ExecQty": 1,
            "CtrctTime": "185923567",
            "CtrctNo": 174,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 16,
            "OrgOrdNo": 0,
            "OrdTime": "190041900",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "420.00000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "420.00000000",
            "ExecQty": 1,
            "CtrctTime": "190118948",
            "CtrctNo": 198,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 17,
            "OrgOrdNo": 0,
            "OrdTime": "190112042",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "420.00000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "420.00000000",
            "ExecQty": 1,
            "CtrctTime": "190118967",
            "CtrctNo": 199,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "40",
            "CommdaCodeNm": "OPEN API",
            "IpAddr": "183111090075",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 18,
            "OrgOrdNo": 0,
            "OrdTime": "190142985",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "417.00000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "40",
            "CommdaCodeNm": "OPEN API",
            "IpAddr": "183111090075",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 19,
            "OrgOrdNo": 18,
            "OrdTime": "190223839",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "정정",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "418.00000000",
            "OrdQty": 1,
            "OrdTpNm": "확인",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "40",
            "CommdaCodeNm": "OPEN API",
            "IpAddr": "183111090075",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 24,
            "OrgOrdNo": 19,
            "OrdTime": "190539234",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "취소",
            "FnoOrdprcPtnCode": "",
            "FnoOrdprcPtnNm": "",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 1,
            "OrdTpNm": "확인",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "40",
            "CommdaCodeNm": "OPEN API",
            "IpAddr": "183111090075",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 62,
            "OrgOrdNo": 0,
            "OrdTime": "194746161",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "420.75000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "420.75000000",
            "ExecQty": 1,
            "CtrctTime": "195541953",
            "CtrctNo": 2904,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 67,
            "OrgOrdNo": 0,
            "OrdTime": "194759635",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "420.85000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "420.85000000",
            "ExecQty": 1,
            "CtrctTime": "195541087",
            "CtrctNo": 2901,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 70,
            "OrgOrdNo": 0,
            "OrdTime": "194808222",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매도",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "452.25000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "전매",
            "FnoExecPrc": "452.25000000",
            "ExecQty": 1,
            "CtrctTime": "205318721",
            "CtrctNo": 4827,
            "ExecNo": 0,
            "BnsplAmt": 21937500,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250526",
            "OrdNo": 81,
            "OrgOrdNo": 0,
            "OrdTime": "195029129",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "435.00000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "435.00000000",
            "ExecQty": 1,
            "CtrctTime": "195043502",
            "CtrctNo": 2148,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250528",
            "OrdNo": 50,
            "OrgOrdNo": 0,
            "OrdTime": "181713372",
            "FnoIsuNo": "201W6352",
            "IsuNm": "C 202506 352.5",
            "BnsTpNm": "매도",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "35.00000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250528",
            "OrdNo": 170,
            "OrgOrdNo": 0,
            "OrdTime": "185329832",
            "FnoIsuNo": "201W6192",
            "IsuNm": "C 202506 192.5",
            "BnsTpNm": "매도",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "0.50000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매도",
            "FnoExecPrc": "0.50000000",
            "ExecQty": 1,
            "CtrctTime": "185744028",
            "CtrctNo": 1,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250528",
            "OrdNo": 192,
            "OrgOrdNo": 50,
            "OrdTime": "190313031",
            "FnoIsuNo": "201W6352",
            "IsuNm": "C 202506 352.5",
            "BnsTpNm": "매도",
            "MrcTpNm": "취소",
            "FnoOrdprcPtnCode": "",
            "FnoOrdprcPtnNm": "",
            "FnoOrdPrc": "0.00000000",
            "OrdQty": 1,
            "OrdTpNm": "확인",
            "ExecTpNm": "",
            "FnoExecPrc": "0.00000000",
            "ExecQty": 0,
            "CtrctTime": "",
            "CtrctNo": 0,
            "ExecNo": 0,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250528",
            "OrdNo": 220,
            "OrgOrdNo": 0,
            "OrdTime": "191032104",
            "FnoIsuNo": "101W6000",
            "IsuNm": "F 202506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "494.55000000",
            "OrdQty": 10,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "494.55000000",
            "ExecQty": 10,
            "CtrctTime": "191032141",
            "CtrctNo": 572,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        },
        {
            "OrdDt": "20250528",
            "OrdNo": 228,
            "OrgOrdNo": 0,
            "OrdTime": "191502252",
            "FnoIsuNo": "165W6000",
            "IsuNm": "KTB3 2506",
            "BnsTpNm": "매수",
            "MrcTpNm": "",
            "FnoOrdprcPtnCode": "00",
            "FnoOrdprcPtnNm": "지정가",
            "FnoOrdPrc": "105.94000000",
            "OrdQty": 1,
            "OrdTpNm": "접수",
            "ExecTpNm": "매수",
            "FnoExecPrc": "105.94000000",
            "ExecQty": 1,
            "CtrctTime": "191502275",
            "CtrctNo": 148,
            "ExecNo": 1,
            "BnsplAmt": 0,
            "UnercQty": 0,
            "UserId": "*****",
            "MktClssCodeNm": "NDV 파생야간",
            "CommdaCode": "85",
            "CommdaCodeNm": "투혼(HTS)",
            "IpAddr": "123456789000",
            "TrdPtnTpNm": "기타",
            "GrpId": ""
        }
    ],
    "rsp_cd": "00136",
    "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CCENQ90200"></a>
## `CCENQ90200` KRX야간파생 잔고조회

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
| `CCENQ90200InBlock1` | CCENQ90200InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | 1 |
| `&nbsp;&nbsp;-BalEvalTp` | 잔고평가구분 | String | Y | 1 | 0:기본설정<br/> 1:이동평균법<br/> 2:선입선출법 |
| `&nbsp;&nbsp;-FutsPrcEvalTp` | 선물가격평가구분 | String | Y | 1 | 1:당초가<br/> 2:전일종가 |


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
| `CCENQ90200OutBlock1` | CCENQ90200OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-InptPwd` | 입력비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BalEvalTp` | 잔고평가구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FutsPrcEvalTp` | 선물가격평가구분 | String | Y | 1 | - |
| `CCENQ90200OutBlock2` | CCENQ90200OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | String | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-EvalDpsamtTotamt` | 평가예탁금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-MnyEvalDpstgAmt` | 현금평가예탁금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-DpsamtTotamt` | 예탁금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpstgMny` | 예탁현금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-DpstgSubst` | 예탁대용 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PsnOutAbleTotAmt` | 인출가능총금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-PsnOutAbleCurAmt` | 인출가능현금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PsnOutAbleSubstAmt` | 인출가능대용금액 | Number | N | 16 | - |
| `&nbsp;&nbsp;-OrdAbleTotAmt` | 주문가능총금액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-MnyOrdAbleAmt` | 현금주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CsgnMgnTotamt` | 위탁증거금총액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyCsgnMgn` | 현금위탁증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MtmgnTotamt` | 유지증거금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-MnyMaintMgn` | 현금유지증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalAmtSum` | 평가금액합계 | Number | Y | 17 | - |
| `&nbsp;&nbsp;-RcvblOdpnt` | 미수연체료 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AddMgnTotamt` | 추가증거금총액 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-EvalPnlSum` | 평가손익합계 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-RcvblAmt` | 미수금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MnyAddMgn` | 현금추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsEvalPnlAmt` | 선물평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalPnlAmt` | 옵션평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalAmt` | 옵션평가금액 | Number | Y | 16 | - |
| `CCENQ90200OutBlock3` | CCENQ90200OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-FnoIsuNo` | 선물옵션종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-UnsttQty` | 미결제수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoAvrPrc` | 평균가 | Number | Y | 198 | - |
| `&nbsp;&nbsp;-FnoNowPrc` | 선물옵션현재가 | Number | Y | 278 | - |
| `&nbsp;&nbsp;-FnoCmpPrc` | 선물옵션대비가 | Number | Y | 278 | - |
| `&nbsp;&nbsp;-EvalPnl` | 평가손익 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PnlRat` | 손익율 | Number | Y | 186 | - |
| `&nbsp;&nbsp;-FnoTrdUnitAmt` | 선물옵션거래단위금액 | Number | Y | 198 | - |
| `&nbsp;&nbsp;-EvalAmt` | 평가금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EvalRat` | 평가비율 | Number | Y | 72 | - |
| `&nbsp;&nbsp;-BnsplAmt` | 매매손익금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CCENQ90200InBlock1": {
    "RecCnt": 1,
    "BalEvalTp": "0",
    "FutsPrcEvalTp": "0"
  }
}
```

### 응답 Example

```json
{
	"CCENQ90200OutBlock1": {
		"RecCnt": 1,
		"AcntNo": "***********",
		"InptPwd": "********",
		"BalEvalTp": "2",
		"FutsPrcEvalTp": "1"
	},
	"CCENQ90200OutBlock2": {
		"RecCnt": 1,
		"AcntNm": "***",
		"EvalDpsamtTotamt": 34399538,
		"MnyEvalDpstgAmt": 34399538,
		"DpsamtTotamt": 31925203,
		"DpstgMny": 31925203,
		"DpstgSubst": 0,
		"PsnOutAbleTotAmt": 20321010,
		"PsnOutAbleCurAmt": 20321010,
		"PsnOutAbleSubstAmt": 0,
		"OrdAbleTotAmt": 20327175,
		"MnyOrdAbleAmt": 20327175,
		"CsgnMgnTotamt": 11598028,
		"MnyCsgnMgn": 4580264,
		"MtmgnTotamt": 2673434,
		"MnyMaintMgn": 0,
		"EvalAmtSum": 6288000,
		"RcvblOdpnt": 0,
		"AddMgnTotamt": 0,
		"EvalPnlSum": 6288000,
		"RcvblAmt": 0,
		"MnyAddMgn": 0,
		"FutsEvalPnlAmt": 6288000,
		"OptEvalPnlAmt": 0,
		"OptEvalAmt": 0
	},
	"CCENQ90200OutBlock3": [
		{
			"FnoIsuNo": "105W6000",
			"IsuNm": "MF 2506",
			"BnsTpCode": "2",
			"BnsTpNm": "매수",
			"UnsttQty": 2,
			"FnoAvrPrc": "343.70000000",
			"FnoNowPrc": "406.58000000",
			"FnoCmpPrc": "62.88000000",
			"EvalPnl": 6288000,
			"PnlRat": "18.300000",
			"FnoTrdUnitAmt": "50000.00000000",
			"EvalAmt": 40658000,
			"EvalRat": "1.18",
			"BnsplAmt": 0
		}
	],
	"rsp_cd": "00136",
	"rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-FOCCQ33700"></a>
## `FOCCQ33700` 선물옵션 기간별 계좌 수익률 현황

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
| `FOCCQ33700InBlock1` | FOCCQ33700InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | 1.평균예탁자산기준<br/>2.투입자산기준(기초자산+입출금액)<br/>3.투입자산기준(기초자산+입금액) |
| `&nbsp;&nbsp;-BaseAmtTp` | 기준금액구분 | String | Y | 1 | 1@평균예탁자산기준<br/>2@투입자산기준(기초자산+입출금액)<br/>3@투입자산기준(기초자산+입금액) |
| `&nbsp;&nbsp;-QryTermTp` | 조회기간구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-PnlCalcTpCode` | 손익산출구분코드 | String | Y | 1 | - |


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
| `FOCCQ33700OutBlock1` | FOCCQ33700OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BaseAmtTp` | 기준금액구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-QryTermTp` | 조회기간구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-PnlCalcTpCode` | 손익산출구분코드 | String | Y | 1 | - |
| `FOCCQ33700OutBlock2` | FOCCQ33700OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNm` | 계좌명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-InAmt` | 입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OutAmt` | 출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FnoCtrctAmt` | 선물옵션약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstPramtAvrbalAmt` | 투자원금평잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-FutsAdjstDfamt` | 선물정산차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBsnPnlAmt` | 옵션매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalPnlAmt` | 옵션평가손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstPlAmt` | 투자손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-ErnRat` | 수익률 | Number | Y | 12.6 | - |
| `FOCCQ33700OutBlock3` | FOCCQ33700OutBlock3 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-FdDpsastAmt` | 기초예탁자산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-EotDpsastAmt` | 기말예탁자산금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InAmt` | 입금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OutAmt` | 출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstAvrbalPramt` | 투자원금평잔금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-InvstPlAmt` | 투자손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Ernrat` | 수익률 | Number | Y | 12.6 | - |
| `&nbsp;&nbsp;-FnoCtrctAmt` | 선물옵션약정금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-Trnrat` | 회전율 | Number | Y | 12.6 | - |
| `&nbsp;&nbsp;-FutsAdjstDfamt` | 선물정산차금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptBsnPnlAmt` | 옵션매매손익금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OptEvalPnlAmt` | 옵션평가손익금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "FOCCQ33700InBlock1" : {
    "QrySrtDt" : "20230102",
    "QryEndDt" : "20230602",
    "QryTp" : "1",
    "BaseAmtTp" : "1",
    "QryTermTp" : "1",
    "PnlCalcTpCode" : "1"
  }
}
```

### 응답 Example

```json
{
    "FOCCQ33700OutBlock3": [
        {
            "FutsAdjstDfamt": 0,
            "OptBsnPnlAmt": 0,
            "InvstPlAmt": 0,
            "TrdDt": "20230102",
            "EotDpsastAmt": 0,
            "Trnrat": "0.000000",
            "FdDpsastAmt": 0,
            "FnoCtrctAmt": 0,
            "OutAmt": 0,
            "InAmt": 0,
            "InvstAvrbalPramt": 0,
            "Ernrat": "0.000000",
            "OptEvalPnlAmt": 0
        }
    ],
    "rsp_cd": "00133",
    "FOCCQ33700OutBlock2": {
        "FutsAdjstDfamt": 0,
        "OptBsnPnlAmt": 0,
        "InvstPlAmt": 0,
        "RecCnt": 1,
        "InAmt": 0,
        "AcntNm": "",
        "FnoCtrctAmt": 0,
        "InvstPramtAvrbalAmt": 0,
        "OptEvalPnlAmt": 0,
        "ErnRat": "0.000000",
        "OutAmt": 0
    },
    "FOCCQ33700OutBlock1": {
        "BaseAmtTp": "1",
        "RecCnt": 1,
        "AcntNo": "20277932702",
        "QrySrtDt": "20230102",
        "QryTermTp": "1",
        "Pwd": "********",
        "QryEndDt": "20230602",
        "PnlCalcTpCode": "1",
        "QryTp": "1"
    },
    "rsp_msg": "조회가 계속 됩니다. 계속하시려면 연속버튼을 누르십시오."
}
```
