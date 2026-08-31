# [해외선물] 계좌

> LS증권 OPEN API 정의서 · 그룹: **해외선물** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=c1ef0e8b-4666-4d8c-a77f-6ab488cfdb39&api_id=44c1c082-c899-48fb-bc66-bb5be2f0ab4e)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `44c1c082-c899-48fb-bc66-bb5be2f0ab4e` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/overseas-futureoption/accno` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외선물옵션 계좌별 거래내역 및 잔고 등 계좌에 관련된 서비스를 확인할 수 있습니다. |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외선물 체결내역개별 조회(주문가능수량) | [CIDBQ01400](account.md#tr-CIDBQ01400) | 1 | 1 | 10 |
| 해외선물 미결제잔고내역 조회 | [CIDBQ01500](account.md#tr-CIDBQ01500) | 1 | 1 | 10 |
| 해외선물 주문내역 조회 | [CIDBQ01800](account.md#tr-CIDBQ01800) | 1 | 1 | 10 |
| 해외선물 주문체결내역 상세 조회 | [CIDBQ02400](account.md#tr-CIDBQ02400) | 1 | 1 | 10 |
| 해외선물 예수금/잔고현황 | [CIDBQ03000](account.md#tr-CIDBQ03000) | 1 | 1 | 10 |
| 해외선물 예탁자산 조회 | [CIDBQ05300](account.md#tr-CIDBQ05300) | 1 | 1 | 10 |
| 일자별 미결제 잔고내역 | [CIDEQ00800](account.md#tr-CIDEQ00800) | 1 | 1 | 10 |

---

<a id="tr-CIDBQ01400"></a>
## `CIDBQ01400` 해외선물 체결내역개별 조회(주문가능수량)

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
| `CIDBQ01400InBlock1` | CIDBQ01400InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | 1:신규 2:청산 3:총가능 |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 1:매도 2:매수 |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | 지정가 (시장가인경우 0) |
| `&nbsp;&nbsp;-AbrdFutsOrdPtnCode` | 해외선물주문유형코드 | String | Y | 1 | 1: 시장가 2: 지정가 |


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
| `CIDBQ01400OutBlock1` | CIDBQ01400OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 18 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-AbrdFutsOrdPtnCode` | 해외선물주문유형코드 | String | Y | 1 | - |
| `CIDBQ01400OutBlock2` | CIDBQ01400OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OrdAbleQty` | 주문가능수량 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CIDBQ01400InBlock1": {
    "RecCnt": 1,
    "QryTpCode": "1",
    "IsuCodeVal": "ADM23",
    "BnsTpCode": "2",
    "OvrsDrvtOrdPrc": 1.0,
    "AbrdFutsOrdPtnCode": "1"
  }
}
```

### 응답 Example

```json
{
  "CIDBQ01400OutBlock1": {
    "RecCnt": 1,
    "QryTpCode": "1",
    "AcntNo": "20629783903",
    "IsuCodeVal": "ADM23",
    "BnsTpCode": "2",
    "OvrsDrvtOrdPrc": "1.00000000000",
    "AbrdFutsOrdPtnCode": "1"
  },
  "CIDBQ01400OutBlock2": {
    "RecCnt": 1,
    "OrdAbleQty": 992
  },
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CIDBQ01500"></a>
## `CIDBQ01500` 해외선물 미결제잔고내역 조회

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
| `CIDBQ01500InBlock1` | CIDBQ01500InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-AcntTpCode` | 계좌구분코드 | String | Y | 1 | 1:위탁 |
| `&nbsp;&nbsp;-QryDt` | 조회일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BalTpCode` | 잔고구분코드 | String | Y | 1 | 1:합산<br/>2:건별 |


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
| `CIDBQ01500OutBlock1` | CIDBQ01500OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntTpCode` | 계좌구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-FcmAcntNo` | FCM계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryDt` | 조회일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-BalTpCode` | 잔고구분코드 | String | Y | 1 | - |
| `CIDBQ01500OutBlock2(Occurs)` | CIDBQ01500OutBlock2(Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-BaseDt` | 기준일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-Dps` | 예수금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LpnlAmt` | 청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FutsDueBfLpnlAmt` | 선물만기전청산손익금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-FutsDueBfCmsn` | 선물만기전수수료 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-CsgnMgn` | 위탁증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MaintMgn` | 유지증거금 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CtlmtAmt` | 신용한도금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-AddMgn` | 추가증거금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-MgnclRat` | 마진콜율 | Number | Y | 27.1 | - |
| `&nbsp;&nbsp;-OrdAbleAmt` | 주문가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-WthdwAbleAmt` | 인출가능금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-CrcyCodeVal` | 통화코드값 | String | Y | 3 | - |
| `&nbsp;&nbsp;-OvrsDrvtPrdtCode` | 해외파생상품코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-OvrsDrvtOptTpCode` | 해외파생옵션구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-DueDt` | 만기일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvrsDrvtXrcPrc` | 해외파생행사가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-CmnCodeNm` | 공통코드명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-TpCodeNm` | 구분코드명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-BalQty` | 잔고수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PchsPrc` | 매입가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OvrsDrvtNowPrc` | 해외파생현재가 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalPnlAmt` | 해외선물평가손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-CsgnCmsn` | 위탁수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-PosNo` | 포지션번호 | String | Y | 13 | - |
| `&nbsp;&nbsp;-EufOneCmsnAmt` | 거래소비용1수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-EufTwoCmsnAmt` | 거래소비용2수수료금액 | Number | Y | 19.2 | - |


### 요청 Example

```json
{
  "CIDBQ01500InBlock1": {
    "RecCnt": 1,
    "AcntTpCode": "1",
    "FcmAcntNo": " ",
    "QryDt": "20230609",
    "BalTpCode": "1"
  }
}
```

### 응답 Example

```json
{
  "CIDBQ01500OutBlock1": {
    "RecCnt": 1,
    "AcntTpCode": "1",
    "AcntNo": "20629783903",
    "FcmAcntNo": "",
    "Pwd": "********",
    "QryDt": "20230609",
    "BalTpCode": "1"
  },
  "CIDBQ01500OutBlock2": [
    {
      "BaseDt": "20230609",
      "Dps": 0,
      "LpnlAmt": "0.00",
      "FutsDueBfLpnlAmt": "0.00",
      "FutsDueBfCmsn": "0.00",
      "CsgnMgn": 0,
      "MaintMgn": 0,
      "CtlmtAmt": "0.00",
      "AddMgn": 0,
      "MgnclRat": "0.0000000000",
      "OrdAbleAmt": 0,
      "WthdwAbleAmt": 0,
      "AcntNo": "20629783903",
      "IsuCodeVal": "ADM23",
      "IsuNm": "Australian Dollar(2023.06)",
      "CrcyCodeVal": "USD",
      "OvrsDrvtPrdtCode": "AD",
      "OvrsDrvtOptTpCode": "F",
      "DueDt": "20230616",
      "OvrsDrvtXrcPrc": "0.00000000000",
      "BnsTpCode": "1",
      "CmnCodeNm": "매도",
      "TpCodeNm": "일반",
      "BalQty": 2,
      "PchsPrc": "0.67130000000",
      "OvrsDrvtNowPrc": "0.67155000000",
      "AbrdFutsEvalPnlAmt": "-50.00",
      "CsgnCmsn": "15.00",
      "PosNo": "",
      "EufOneCmsnAmt": "0.00",
      "EufTwoCmsnAmt": "0.00"
    }
  ],
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CIDBQ01800"></a>
## `CIDBQ01800` 해외선물 주문내역 조회

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
| `CIDBQ01800InBlock1` | CIDBQ01800InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | YYYYMMDD 형식 |
| `&nbsp;&nbsp;-ThdayTpCode` | 당일구분코드 | String | Y | 1 | SPACE |
| `&nbsp;&nbsp;-OrdStatCode` | 주문상태코드 | String | Y | 1 | 0:전체<br/>1:체결<br/>2:미체결 |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 0:전체<br/>1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | 1:역순<br/>2:정순 |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | 00:전체<br/>01:일반<br/>02:Average<br/>03:Spread |
| `&nbsp;&nbsp;-OvrsDrvtFnoTpCode` | 해외파생선물옵션구분코드 | String | Y | 1 | A:전체<br/>F:선물<br/>O:옵션 |


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
| `CIDBQ01800OutBlock1` | CIDBQ01800OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ThdayTpCode` | 당일구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdStatCode` | 주문상태코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OvrsDrvtFnoTpCode` | 해외파생선물옵션구분코드 | String | Y | 1 | - |
| `CIDBQ01800OutBlock2(Occurs)` | CIDBQ01800OutBlock2(Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-OvrsFutsOrdNo` | 해외선물주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo` | 해외선물원주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FcmOrdNo` | FCM주문번호 | String | Y | 15 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-AbrdFutsXrcPrc` | 해외선물행사가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-FcmAcntNo` | FCM계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FutsOrdStatCode` | 선물주문상태코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-TpCodeNm` | 구분코드명 | String | Y | 50 | 주문, 접수, 확인, 체결, 소멸, 거부 |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-TrdTpNm` | 거래구분명 | String | Y | 20 | 신규, 정정, 취소, 이관, 수관, 소멸, 장애 |
| `&nbsp;&nbsp;-AbrdFutsOrdPtnCode` | 해외선물주문유형코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdPtnNm` | 주문유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-OrdPtnTermTpCode` | 주문유형기간구분코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-CmnCodeNm` | 공통코드명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-AppSrtDt` | 적용시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-AppEndDt` | 적용종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsDrvtExecIsuCode` | 해외파생체결종목코드 | String | Y | 30 | - |
| `&nbsp;&nbsp;-ExecIsuNm` | 체결종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-ExecBnsTpCode` | 체결매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-ExecBnsTpNm` | 체결매매구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-AbrdFutsExecPrc` | 해외선물체결가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OrdCndiPrc` | 주문조건가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OvrsDrvtNowPrc` | 해외파생현재가 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-MdfyQty` | 정정수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CancQty` | 취소수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-RjtQty` | 거부수량 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-CnfQty` | 확인수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-CvrgYn` | 반대매매여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-RegTmnlNo` | 등록단말번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RegBrnNo` | 등록지점번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RegUserId` | 등록사용자ID | String | Y | 16 | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdTime` | 주문시각 | String | Y | 9 | - |
| `&nbsp;&nbsp;-OvrsOptXrcRsvTpCode` | 해외옵션행사예약구분코드 | String | Y | 1 | 1:만기행사 |
| `&nbsp;&nbsp;-OvrsDrvtOptTpCode` | 해외파생옵션구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-SprdBaseIsuYn` | 스프레드기준종목여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OvrsFutsOrdDt` | 해외선물주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvrsFutsOrdNo2` | 해외선물주문번호2 | String | Y | 10 | - |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo2` | 해외선물원주문번호2 | String | Y | 10 | - |
| `&nbsp;&nbsp;-OvrsDrvtIsuCode2` | 해외파생종목코드2 | String | Y | 30 | - |


### 요청 Example

```json
{
  "CIDBQ01800InBlock1": {
    "RecCnt": 1,
    "IsuCodeVal": "ADM23",
    "OrdDt": "20230609",
    "ThdayTpCode": " ",
    "OrdStatCode": "0",
    "BnsTpCode": "0",
    "QryTpCode": "2",
    "OrdPtnCode": "00",
    "OvrsDrvtFnoTpCode": "A"
  }
}
```

### 응답 Example

```json
{
  "CIDBQ01800OutBlock1": {
    "RecCnt": 1,
    "AcntNo": "20629783903",
    "Pwd": "********",
    "IsuCodeVal": "ADM23",
    "OrdDt": "20230609",
    "ThdayTpCode": "",
    "OrdStatCode": "0",
    "BnsTpCode": "0",
    "QryTpCode": "2",
    "OrdPtnCode": "00",
    "OvrsDrvtFnoTpCode": "A"
  },
  "CIDBQ01800OutBlock2": [
    {
      "OvrsFutsOrdNo": "0000000087",
      "OvrsFutsOrgOrdNo": "0000000000",
      "FcmOrdNo": "0000000087",
      "IsuCodeVal": "ADM23",
      "IsuNm": "Australian Dollar(2023.06)",
      "AbrdFutsXrcPrc": "0.00000000000",
      "FcmAcntNo": "LAP18968S",
      "BnsTpCode": "1",
      "BnsTpNm": "매도",
      "FutsOrdStatCode": "4",
      "TpCodeNm": "체결",
      "FutsOrdTpCode": "1",
      "TrdTpNm": "신규",
      "AbrdFutsOrdPtnCode": "1",
      "OrdPtnNm": "시장가",
      "OrdPtnTermTpCode": "01",
      "CmnCodeNm": "일반",
      "AppSrtDt": "",
      "AppEndDt": "",
      "OvrsDrvtOrdPrc": "122.00000000000",
      "OrdQty": 1,
      "OvrsDrvtExecIsuCode": "ADM23",
      "ExecIsuNm": "Australian Dollar(2023.06)",
      "ExecBnsTpCode": "1",
      "ExecBnsTpNm": "매도",
      "AbrdFutsExecPrc": "0.67070000000",
      "ExecQty": 1,
      "OrdCndiPrc": "0.66400000000",
      "OvrsDrvtNowPrc": "0.67155000000",
      "MdfyQty": 0,
      "CancQty": 0,
      "RjtQty": 0,
      "CnfQty": 0,
      "UnercQty": 0,
      "CvrgYn": "N",
      "RegTmnlNo": "",
      "RegBrnNo": "000",
      "RegUserId": "qzvjaf",
      "OrdDt": "20230609",
      "OrdTime": "150904474",
      "OvrsOptXrcRsvTpCode": "0",
      "OvrsDrvtOptTpCode": "F",
      "SprdBaseIsuYn": "",
      "OvrsFutsOrdDt": "20230609",
      "OvrsFutsOrdNo2": "0000000087",
      "OvrsFutsOrgOrdNo2": "0000000000",
      "OvrsDrvtIsuCode2": "ADM23"
    }
  ],
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CIDBQ02400"></a>
## `CIDBQ02400` 해외선물 주문체결내역 상세 조회

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
| `CIDBQ02400InBlock1` | CIDBQ02400InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일자 | String | Y | 8 | YYYYMMDD 형식<br/>과거조회시는 사용<br/>당일조회시는 공백 |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일자 | String | Y | 8 | YYYYMMDD 형식<br/>과거조회시는 사용<br/>당일조회시는 공백 |
| `&nbsp;&nbsp;-ThdayTpCode` | 당일구분코드 | String | Y | 1 | 0:과거조회<br/>1:당일조회 |
| `&nbsp;&nbsp;-OrdStatCode` | 주문상태코드 | String | Y | 1 | 0:전체<br/>1:체결<br/>2:미체결 |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 0:전체<br/>1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | 1:역순<br/>2:정순 |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | 00:전체<br/>01:일반<br/>02:Average<br/>03:Spread |
| `&nbsp;&nbsp;-OvrsDrvtFnoTpCode` | 해외파생선물옵션구분코드 | String | Y | 1 | A:전체<br/>F:선물<br/>O:옵션 |


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
| `CIDBQ02400OutBlock1` | CIDBQ02400OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-Pwd` | 비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-QrySrtDt` | 조회시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-QryEndDt` | 조회종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ThdayTpCode` | 당일구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdStatCode` | 주문상태코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-QryTpCode` | 조회구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-OvrsDrvtFnoTpCode` | 해외파생선물옵션구분코드 | String | Y | 1 | - |
| `CIDBQ02400OutBlock2(Occurs)` | CIDBQ02400OutBlock2(Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-OrdDt` | 주문일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvrsFutsOrdNo` | 해외선물주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-OvrsFutsOrgOrdNo` | 해외선물원주문번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FcmOrdNo` | FCM주문번호 | String | Y | 15 | - |
| `&nbsp;&nbsp;-ExecDt` | 체결일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OvrsFutsExecNo` | 해외선물체결번호 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FcmAcntNo` | FCM계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-AbrdFutsXrcPrc` | 해외선물행사가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-BnsTpCode` | 매매구분코드 | String | Y | 1 | 0:전체<br/>1:매도<br/>2:매수 |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-FutsOrdStatCode` | 선물주문상태코드 | String | Y | 1 | 0:전체<br/>1:체결<br/>2:미체결 |
| `&nbsp;&nbsp;-TpCodeNm` | 구분코드명 | String | Y | 50 | 신규, 정정, 취소, 이관, 수관, 소멸, 장애 |
| `&nbsp;&nbsp;-FutsOrdTpCode` | 선물주문구분코드 | String | Y | 1 | 공백 |
| `&nbsp;&nbsp;-TrdTpNm` | 거래구분명 | String | Y | 20 | 주문, 접수, 확인, 체결, 소멸, 거부 |
| `&nbsp;&nbsp;-AbrdFutsOrdPtnCode` | 해외선물주문유형코드 | String | Y | 1 | 공백 |
| `&nbsp;&nbsp;-OrdPtnNm` | 주문유형명 | String | Y | 40 | 시장가, 지정가, Stop Market, Stop Limit |
| `&nbsp;&nbsp;-OrdPtnTermTpCode` | 주문유형기간구분코드 | String | Y | 2 | 공백 |
| `&nbsp;&nbsp;-CmnCodeNm` | 공통코드명 | String | Y | 100 | 일반, Spread |
| `&nbsp;&nbsp;-AppSrtDt` | 적용시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-AppEndDt` | 적용종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-OrdQty` | 주문수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-OvrsDrvtOrdPrc` | 해외파생주문가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OvrsDrvtExecIsuCode` | 해외파생체결종목코드 | String | Y | 30 | - |
| `&nbsp;&nbsp;-ExecIsuNm` | 체결종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-ExecBnsTpCode` | 체결매매구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-ExecBnsTpNm` | 체결매매구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-ExecQty` | 체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-AbrdFutsExecPrc` | 해외선물체결가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OrdCndiPrc` | 주문조건가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OvrsDrvtNowPrc` | 해외파생현재가 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-UnercQty` | 미체결수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-TrxStatCode` | 처리상태코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-TrxStatCodeNm` | 처리상태코드명 | String | Y | 40 | 체결, 체결취소 |
| `&nbsp;&nbsp;-CsgnCmsn` | 위탁수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FcmCmsn` | FCM수수료 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-ThcoCmsn` | 당사수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-MdaCode` | 매체코드 | String | Y | 2 | 00 창구<br/>22 아이폰<br/>23 안드로이드<br/>41 API<br/>43 로보API<br/>85 HTS<br/>96 최종결제<br/>LP 로스컷<br/>SK CashCall<br/>SO 조건주문 |
| `&nbsp;&nbsp;-MdaCodeNm` | 매체코드명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-RegTmnlNo` | 등록단말번호 | String | Y | 3 | - |
| `&nbsp;&nbsp;-RegUserId` | 등록사용자ID | String | Y | 16 | - |
| `&nbsp;&nbsp;-OrdSndDttm` | 주문발송일시 | String | Y | 17 | - |
| `&nbsp;&nbsp;-ExecDttm` | 체결일시 | String | Y | 17 | - |
| `&nbsp;&nbsp;-EufOneCmsnAmt` | 거래소비용1수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-EufTwoCmsnAmt` | 거래소비용2수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-LchOneCmsnAmt` | 런던청산소1수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-LchTwoCmsnAmt` | 런던청산소2수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TrdOneCmsnAmt` | 거래1수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TrdTwoCmsnAmt` | 거래2수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TrdThreeCmsnAmt` | 거래3수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-StrmOneCmsnAmt` | 단기1수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-StrmTwoCmsnAmt` | 단기2수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-StrmThreeCmsnAmt` | 단기3수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TransOneCmsnAmt` | 전달1수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TransTwoCmsnAmt` | 전달2수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TransThreeCmsnAmt` | 전달3수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-TransFourCmsnAmt` | 전달4수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsOptXrcRsvTpCode` | 해외옵션행사예약구분코드 | String | Y | 1 | 1:만기행사 |
| `&nbsp;&nbsp;-OvrsDrvtOptTpCode` | 해외파생옵션구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-SprdBaseIsuYn` | 스프레드기준종목여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-OvrsDrvtIsuCode2` | 해외파생종목코드2 | String | Y | 30 | - |


### 요청 Example

```json
{
  "CIDBQ02400InBlock1": {
    "RecCnt": 1,
    "IsuCodeVal": "ADM23",
    "QrySrtDt": "20230516",
    "QryEndDt": "20230609",
    "ThdayTpCode": "1",
    "OrdStatCode": "0",
    "BnsTpCode": "0",
    "QryTpCode": "2",
    "OrdPtnCode": "00",
    "OvrsDrvtFnoTpCode": "A"
  }
}
```

### 응답 Example

```json
{
  "CIDBQ02400OutBlock1": {
    "RecCnt": 1,
    "AcntNo": "20629783903",
    "Pwd": "********",
    "IsuCodeVal": "ADM23",
    "QrySrtDt": "20230516",
    "QryEndDt": "20230609",
    "ThdayTpCode": "1",
    "OrdStatCode": "0",
    "BnsTpCode": "0",
    "QryTpCode": "2",
    "OrdPtnCode": "00",
    "OvrsDrvtFnoTpCode": "A"
  },
  "CIDBQ02400OutBlock2": [
    {
      "OrdDt": "20230609",
      "OvrsFutsOrdNo": "0000000087",
      "OvrsFutsOrgOrdNo": "0000000000",
      "FcmOrdNo": "0000000087",
      "ExecDt": "20230609",
      "OvrsFutsExecNo": "0000000048",
      "FcmAcntNo": "LAP18968S",
      "IsuCodeVal": "ADM23",
      "IsuNm": "Australian Dollar(2023.06)",
      "AbrdFutsXrcPrc": "0.00000000000",
      "BnsTpCode": "1",
      "BnsTpNm": "매도",
      "FutsOrdStatCode": "4",
      "TpCodeNm": "신규",
      "FutsOrdTpCode": "1",
      "TrdTpNm": "체결",
      "AbrdFutsOrdPtnCode": "1",
      "OrdPtnNm": "시장가",
      "OrdPtnTermTpCode": "01",
      "CmnCodeNm": "일반",
      "AppSrtDt": "",
      "AppEndDt": "",
      "OrdQty": 1,
      "OvrsDrvtOrdPrc": "122.00000000000",
      "OvrsDrvtExecIsuCode": "ADM23",
      "ExecIsuNm": "Australian Dollar(2023.06)",
      "ExecBnsTpCode": "1",
      "ExecBnsTpNm": "매도",
      "ExecQty": 1,
      "AbrdFutsExecPrc": "0.67070000000",
      "OrdCndiPrc": "0.66400000000",
      "OvrsDrvtNowPrc": "0.67070000000",
      "UnercQty": 0,
      "TrxStatCode": "1",
      "TrxStatCodeNm": "체결",
      "CsgnCmsn": "7.50",
      "FcmCmsn": "0.0000",
      "ThcoCmsn": "0.00",
      "MdaCode": "40",
      "MdaCodeNm": "40",
      "RegTmnlNo": "",
      "RegUserId": "qzvjaf",
      "OrdSndDttm": "20230609150904474",
      "ExecDttm": "20230609150904559",
      "EufOneCmsnAmt": "0.00",
      "EufTwoCmsnAmt": "0.00",
      "LchOneCmsnAmt": "0.00",
      "LchTwoCmsnAmt": "0.00",
      "TrdOneCmsnAmt": "0.00",
      "TrdTwoCmsnAmt": "0.00",
      "TrdThreeCmsnAmt": "0.00",
      "StrmOneCmsnAmt": "0.00",
      "StrmTwoCmsnAmt": "0.00",
      "StrmThreeCmsnAmt": "0.00",
      "TransOneCmsnAmt": "0.00",
      "TransTwoCmsnAmt": "0.00",
      "TransThreeCmsnAmt": "0.00",
      "TransFourCmsnAmt": "0.00",
      "OvrsOptXrcRsvTpCode": "0",
      "OvrsDrvtOptTpCode": "F",
      "SprdBaseIsuYn": "",
      "OvrsDrvtIsuCode2": "ADM23"
    }
  ],
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CIDBQ03000"></a>
## `CIDBQ03000` 해외선물 예수금/잔고현황

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
| `CIDBQ03000InBlock1` | CIDBQ03000InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-AcntTpCode` | 계좌구분코드 | String | Y | 1 | 1 : 위탁계좌 2 : 중개계좌 |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |


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
| `CIDBQ03000OutBlock1` | CIDBQ03000OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntTpCode` | 계좌구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-AcntPwd` | 계좌비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |
| `CIDBQ03000OutBlock2` | CIDBQ03000OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-CrcyObjCode` | 통화대상코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-OvrsFutsDps` | 해외선물예수금 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-CustmMnyioAmt` | 고객입출금금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsLqdtPnlAmt` | 해외선물청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsCmsnAmt` | 해외선물수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-PrexchDps` | 가환전예수금 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-EvalAssetAmt` | 평가자산금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsCsgnMgn` | 해외선물위탁증거금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsAddMgn` | 해외선물추가증거금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsWthdwAbleAmt` | 해외선물인출가능금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsOrdAbleAmt` | 해외선물주문가능금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalPnlAmt` | 해외선물평가손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-LastSettPnlAmt` | 최종결제손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsOptSettAmt` | 해외옵션결제금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsOptBalEvalAmt` | 해외옵션잔고평가금액 | Number | Y | 19.2 | - |


### 요청 Example

```json
{
  "CIDBQ03000InBlock1": {
    "RecCnt": 1,
    "AcntTpCode": "1",
    "TrdDt": "20230609"
  }
}
```

### 응답 Example

```json
{
  "CIDBQ03000OutBlock1": {
    "RecCnt": 1,
    "AcntTpCode": "1",
    "AcntNo": "20629783903",
    "AcntPwd": "********",
    "TrdDt": "20230609"
  },
  "CIDBQ03000OutBlock2": [
    {
      "AcntNo": "20629783903",
      "TrdDt": "20230609",
      "CrcyObjCode": "TOT(USD)",
      "OvrsFutsDps": "0.00",
      "CustmMnyioAmt": "0.00",
      "AbrdFutsLqdtPnlAmt": "0.00",
      "AbrdFutsCmsnAmt": "15.00",
      "PrexchDps": "2296914.47",
      "EvalAssetAmt": "2296849.47",
      "AbrdFutsCsgnMgn": "4400.00",
      "AbrdFutsAddMgn": "4465.00",
      "AbrdFutsWthdwAbleAmt": "2187537.60",
      "AbrdFutsOrdAbleAmt": "2183072.60",
      "AbrdFutsEvalPnlAmt": "-50.00",
      "LastSettPnlAmt": "-65.00",
      "OvrsOptSettAmt": "0.00",
      "OvrsOptBalEvalAmt": "0.00"
    }
  ],
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CIDBQ05300"></a>
## `CIDBQ05300` 해외선물 예탁자산 조회

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
| `CIDBQ05300InBlock1` | CIDBQ05300InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-OvrsAcntTpCode` | 해외계좌구분코드 | String | Y | 1 | 1:위탁 |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | ALL:전체 CAD:캐나다 달러 CHF:스위스 프랑 EUR:유럽연합 유로 GBP:영국 파운드 HKD:홍콩 달러 JPY:일본 엔 SGD:싱가포르 달러 USD:미국 달러 |


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
| `CIDBQ05300OutBlock1` | CIDBQ05300OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OvrsAcntTpCode` | 해외계좌구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-FcmAcntNo` | FCM계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-AcntPwd` | 계좌비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `CIDBQ05300OutBlock2 (Occurs)` | CIDBQ05300OutBlock2 (Occurs) | Object Array | Y | - | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-CrcyCode` | 통화코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-OvrsFutsDps` | 해외선물예수금 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-AbrdFutsCsgnMgn` | 해외선물위탁증거금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsFutsSplmMgn` | 해외선물추가증거금 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-CustmLpnlAmt` | 고객청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalPnlAmt` | 해외선물평가손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsCmsnAmt` | 해외선물수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalDpstgTotAmt` | 해외선물평가예탁총금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-Xchrat` | 환율 | Number | Y | 15.4 | - |
| `&nbsp;&nbsp;-FcurrRealMxchgAmt` | 외화실환전금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsWthdwAbleAmt` | 해외선물인출가능금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsOrdAbleAmt` | 해외선물주문가능금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FutsDueNarrvLqdtPnlAmt` | 선물만기미도래청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FutsDueNarrvCmsn` | 선물만기미도래수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsLqdtPnlAmt` | 해외선물청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsFutsDueCmsn` | 해외선물만기수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsFutsOptBuyAmt` | 해외선물옵션매수금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-OvrsFutsOptSellAmt` | 해외선물옵션매도금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-OptBuyMktWrthAmt` | 옵션매수시장가치금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OptSellMktWrthAmt` | 옵션매도시장가치금액 | Number | Y | 19.2 | - |
| `CIDBQ05300OutBlock3` | CIDBQ05300OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-OvrsFutsDps` | 해외선물예수금 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-AbrdFutsLqdtPnlAmt` | 해외선물청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FutsDueNarrvLqdtPnlAmt` | 선물만기미도래청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalPnlAmt` | 해외선물평가손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalDpstgTotAmt` | 해외선물평가예탁총금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-CustmLpnlAmt` | 고객청산손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsFutsDueCmsn` | 해외선물만기수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FcurrRealMxchgAmt` | 외화실환전금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsCmsnAmt` | 해외선물수수료금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FutsDueNarrvCmsn` | 선물만기미도래수수료 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsCsgnMgn` | 해외선물위탁증거금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsFutsMaintMgn` | 해외선물유지증거금 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsFutsOptBuyAmt` | 해외선물옵션매수금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-OvrsFutsOptSellAmt` | 해외선물옵션매도금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-CtlmtAmt` | 신용한도금액 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-OvrsFutsSplmMgn` | 해외선물추가증거금 | Number | Y | 23.2 | - |
| `&nbsp;&nbsp;-MgnclRat` | 마진콜율 | Number | Y | 27.1 | - |
| `&nbsp;&nbsp;-AbrdFutsOrdAbleAmt` | 해외선물주문가능금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-AbrdFutsWthdwAbleAmt` | 해외선물인출가능금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OptBuyMktWrthAmt` | 옵션매수시장가치금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OptSellMktWrthAmt` | 옵션매도시장가치금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsOptSettAmt` | 해외옵션결제금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-OvrsOptBalEvalAmt` | 해외옵션잔고평가금액 | Number | Y | 19.2 | - |


### 요청 Example

```json
{
  "CIDBQ05300InBlock1": {
    "RecCnt": 1,
    "OvrsAcntTpCode": "1",
    "FcmAcntNo": " ",
    "CrcyCode": "ALL"
  }
}
```

### 응답 Example

```json
{
  "CIDBQ05300OutBlock1": {
    "RecCnt": 1,
    "OvrsAcntTpCode": "1",
    "FcmAcntNo": "",
    "AcntNo": "20629783903",
    "AcntPwd": "********",
    "CrcyCode": "ALL"
  },
  "CIDBQ05300OutBlock2": [
    {
      "AcntNo": "20629783903",
      "CrcyCode": "KRW",
      "OvrsFutsDps": "3000000000.00",
      "AbrdFutsCsgnMgn": "0.00",
      "OvrsFutsSplmMgn": "0.00",
      "CustmLpnlAmt": "0.00",
      "AbrdFutsEvalPnlAmt": "0.00",
      "AbrdFutsCmsnAmt": "0.00",
      "AbrdFutsEvalDpstgTotAmt": "0.00",
      "Xchrat": "0.0000",
      "FcurrRealMxchgAmt": "2187537.60",
      "AbrdFutsWthdwAbleAmt": "2993876677.00",
      "AbrdFutsOrdAbleAmt": "3000000000.00",
      "FutsDueNarrvLqdtPnlAmt": "0.00",
      "FutsDueNarrvCmsn": "0.00",
      "AbrdFutsLqdtPnlAmt": "0.00",
      "OvrsFutsDueCmsn": "0.00",
      "OvrsFutsOptBuyAmt": "0.00",
      "OvrsFutsOptSellAmt": "0.00",
      "OptBuyMktWrthAmt": "0.00",
      "OptSellMktWrthAmt": "0.00"
    },
    {
      "AcntNo": "20629783903",
      "CrcyCode": "USD",
      "OvrsFutsDps": "0.00",
      "AbrdFutsCsgnMgn": "4400.00",
      "OvrsFutsSplmMgn": "4465.00",
      "CustmLpnlAmt": "0.00",
      "AbrdFutsEvalPnlAmt": "-50.00",
      "AbrdFutsCmsnAmt": "15.00",
      "AbrdFutsEvalDpstgTotAmt": "-65.00",
      "Xchrat": "0.0000",
      "FcurrRealMxchgAmt": "0.00",
      "AbrdFutsWthdwAbleAmt": "0.00",
      "AbrdFutsOrdAbleAmt": "2183072.60",
      "FutsDueNarrvLqdtPnlAmt": "0.00",
      "FutsDueNarrvCmsn": "0.00",
      "AbrdFutsLqdtPnlAmt": "0.00",
      "OvrsFutsDueCmsn": "0.00",
      "OvrsFutsOptBuyAmt": "0.00",
      "OvrsFutsOptSellAmt": "0.00",
      "OptBuyMktWrthAmt": "0.00",
      "OptSellMktWrthAmt": "0.00"
    }
  ],
  "CIDBQ05300OutBlock3": {
    "RecCnt": 1,
    "OvrsFutsDps": "0.00",
    "AbrdFutsLqdtPnlAmt": "0.00",
    "FutsDueNarrvLqdtPnlAmt": "0.00",
    "AbrdFutsEvalPnlAmt": "-50.00",
    "AbrdFutsEvalDpstgTotAmt": "-65.00",
    "CustmLpnlAmt": "0.00",
    "OvrsFutsDueCmsn": "0.00",
    "FcurrRealMxchgAmt": "0.00",
    "AbrdFutsCmsnAmt": "15.00",
    "FutsDueNarrvCmsn": "0.00",
    "AbrdFutsCsgnMgn": "4400.00",
    "OvrsFutsMaintMgn": "4400.00",
    "OvrsFutsOptBuyAmt": "0.00",
    "OvrsFutsOptSellAmt": "0.00",
    "CtlmtAmt": "0.00",
    "OvrsFutsSplmMgn": "4465.00",
    "MgnclRat": "0.0000000000",
    "AbrdFutsOrdAbleAmt": "2183072.60",
    "AbrdFutsWthdwAbleAmt": "0.00",
    "OptBuyMktWrthAmt": "0.00",
    "OptSellMktWrthAmt": "0.00",
    "OvrsOptSettAmt": "0.00",
    "OvrsOptBalEvalAmt": "0.00"
  },
  "rsp_cd": "00136",
  "rsp_msg": "조회가 완료되었습니다."
}
```

---

<a id="tr-CIDEQ00800"></a>
## `CIDEQ00800` 일자별 미결제 잔고내역

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
| `CIDEQ00800InBlock1` | CIDEQ00800InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |


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
| `CIDEQ00800OutBlock1` | CIDEQ00800OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-AcntPwd` | 계좌비밀번호 | String | Y | 8 | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |
| `CIDEQ00800OutBlock2` | CIDEQ00800OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-AcntNo` | 계좌번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-TrdDt` | 거래일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-IsuCodeVal` | 종목코드값 | String | Y | 30 | - |
| `&nbsp;&nbsp;-BnsTpNm` | 매매구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-BalQty` | 잔고수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LqdtAbleQty` | 청산가능수량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-PchsPrc` | 매입가격 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-OvrsDrvtNowPrc` | 해외파생현재가 | Number | Y | 30.11 | - |
| `&nbsp;&nbsp;-AbrdFutsEvalPnlAmt` | 해외선물평가손익금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-CustmBalAmt` | 고객잔고금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FcurrEvalAmt` | 외화평가금액 | Number | Y | 21.4 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 50 | - |
| `&nbsp;&nbsp;-CrcyCodeVal` | 통화코드값 | String | Y | 3 | - |
| `&nbsp;&nbsp;-OvrsDrvtPrdtCode` | 해외파생상품코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-DueDt` | 만기일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-PrcntrAmt` | 계약당금액 | Number | Y | 19.2 | - |
| `&nbsp;&nbsp;-FcurrEvalPnlAmt` | 외화평가손익금액 | Number | Y | 21.4 | - |


### 요청 Example

```json
{
  "CIDEQ00800InBlock1": {
    "RecCnt": 1,
    "TrdDt": "20241004"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00136",
    "CIDEQ00800OutBlock2": [
        {
            "BalQty": 4,
            "TrdDt": "20230609",
            "LqdtAbleQty": 4,
            "PrcntrAmt": "100000.00",
            "OvrsDrvtPrdtCode": "AD",
            "FcurrEvalPnlAmt": "12131775.0000",
            "OvrsDrvtNowPrc": "0.67410000000",
            "BnsTpNm": "매도",
            "IsuNm": "Australian Dollar(2023.06)",
            "DueDt": "20230616",
            "PchsPrc": "31.00353750000",
            "FcurrEvalAmt": "1078560.0000",
            "CustmBalAmt": "12401415.00",
            "AcntNo": "20629783903",
            "AbrdFutsEvalPnlAmt": "12131775.00",
            "IsuCodeVal": "ADM23",
            "CrcyCodeVal": "USD"
        }
    ],
    "CIDEQ00800OutBlock1": {
        "RecCnt": 1,
        "TrdDt": "20230609",
        "AcntNo": "20629783903",
        "AcntPwd": "********"
    },
    "rsp_msg": "조회가 완료되었습니다."
}
```
