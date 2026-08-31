# [해외주식] 실시간 시세

> LS증권 OPEN API 정의서 · 그룹: **해외주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=cdb7e1bc-f7c5-425c-8248-aa83dbb6919f&api_id=0c023f96-5137-48cf-8682-8dd30bbc81be)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `0c023f96-5137-48cf-8682-8dd30bbc81be` |
| Protocol | WEBSOCKET |
| Method | POST |
| Domain | `wss://openapi.ls-sec.co.kr:9443` |
| URL | `/websocket/overseas-stock` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외주식 주문현황 및 시세정보를 실시간으로 확인할 수 있습니다. |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외주식주문접수(미국) | [AS0](realtime.md#tr-AS0) | - | - | - |
| 해외주식주문체결(미국) | [AS1](realtime.md#tr-AS1) | - | - | - |
| 해외주식주문정정(미국) | [AS2](realtime.md#tr-AS2) | - | - | - |
| 해외주식주문취소(미국) | [AS3](realtime.md#tr-AS3) | - | - | - |
| 해외주식주문거부(미국) | [AS4](realtime.md#tr-AS4) | - | - | - |
| 해외주식 호가 | [GSH](realtime.md#tr-GSH) | - | - | - |
| 해외주식 체결 | [GSC](realtime.md#tr-GSC) | - | - | - |

> **WebSocket 실시간 데이터**: 접속 도메인은 위 `Domain`(`wss://`)을 사용합니다.
> 접속 시 Header에 발급받은 `token`(접근토큰)을 설정하고, 각 TR 아래의 패킷 구조로 등록/해제(`tr_type`: 1 계좌등록, 2 계좌해제, 3 실시간 시세 등록, 4 실시간 시세 해제) 요청을 보냅니다. 실제 데이터는 동일 채널로 push 수신합니다.

---

<a id="tr-AS0"></a>
## `AS0` 해외주식주문접수(미국)

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `accno` | 계좌번호 | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `trcode` | TRCODE | String | Y | 8 | - |
| `comid` | 이용사번호 | String | Y | 3 | - |
| `userid` | 사용자ID | String | Y | 16 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `filler` | 예비영역 | String | Y | 6 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `sOrdxctPtnCode` | 주문체결유형코드 | String | Y | 2 | - |
| `sOrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `sOrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `sOrgOrdNo` | 원주문번호 | String | Y | 10 | - |
| `sAcntNo` | 계좌번호 | String | Y | 20 | - |
| `sPwd` | 비밀번호 | String | Y | 8 | - |
| `sIsuNo` | 종목번호 | String | Y | 12 | - |
| `sShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `sIsuNm` | 종목명 | String | Y | 40 | - |
| `sOrdQty` | 주문수량 | String | Y | 16 | - |
| `sOrdPrc` | 주문가 | String | Y | 13 | - |
| `sOrdCndi` | 주문조건 | String | Y | 1 | - |
| `sOrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `sStrtgCode` | 전략코드 | String | Y | 6 | - |
| `sGrpId` | 그룹ID | String | Y | 20 | - |
| `sOrdSeqno` | 주문회차 | String | Y | 10 | - |
| `sCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `sOrdNo` | 주문번호 | String | Y | 10 | - |
| `sOrdTime` | 주문시각 | String | Y | 9 | - |
| `sPrntOrdNo` | 모주문번호 | String | Y | 10 | - |
| `sOrgOrdUnercQty` | 원주문미체결수량 | String | Y | 16 | - |
| `sOrgOrdMdfyQty` | 원주문정정수량 | String | Y | 16 | - |
| `sOrgOrdCancQty` | 원주문취소수량 | String | Y | 16 | - |
| `sNmcpySndNo` | 비회원사송신번호 | String | Y | 10 | - |
| `sOrdAmt` | 주문금액 | String | Y | 16 | - |
| `sBnsTp` | 매매구분 | String | Y | 1 | - |
| `sMtiordSeqno` | 복수주문일련번호 | String | Y | 10 | - |
| `sOrdUserId` | 주문사원번호 | String | Y | 16 | - |
| `sSpotOrdQty` | 실물주문수량 | String | Y | 16 | - |
| `sRuseOrdQty` | 재사용주문수량 | String | Y | 16 | - |
| `sOrdMny` | 주문현금 | String | Y | 16 | - |
| `sOrdSubstAmt` | 주문대용금액 | String | Y | 16 | - |
| `sOrdRuseAmt` | 주문재사용금액 | String | Y | 16 | - |
| `sUseCmsnAmt` | 사용수수료 | String | Y | 16 | - |
| `sSecBalQty` | 잔고수량 | String | Y | 16 | - |
| `sSpotOrdAbleQty` | 실물주문가능수량 | String | Y | 16 | - |
| `sOrdAbleRuseQty` | 주문가능재사용수량 | String | Y | 16 | - |
| `sFlctQty` | 변동수량 | String | Y | 16 | - |
| `sSecBalQtyD2` | 잔고수량(D2) | String | Y | 16 | - |
| `sSellAbleQty` | 매도주문가능수량 | String | Y | 16 | - |
| `sUnercSellOrdQty` | 미체결매도주문수량 | String | Y | 16 | - |
| `sAvrPchsPrc` | 평균매입가 | String | Y | 13 | - |
| `sPchsAmt` | 매입금액 | String | Y | 16 | - |
| `sDeposit` | 예수금 | String | Y | 16 | - |
| `sSubstAmt` | 대용금 | String | Y | 16 | - |
| `sCsgnMnyMgn` | 위탁현금증거금액 | String | Y | 16 | - |
| `sCsgnSubstMgn` | 위탁대용증거금액 | String | Y | 16 | - |
| `sOrdAbleMny` | 주문가능현금 | String | Y | 16 | - |
| `sOrdAbleSubstAmt` | 주문가능대용금액 | String | Y | 16 | - |
| `sRuseAbleAmt` | 재사용가능금액 | String | Y | 16 | - |
| `sMgntrnCode` | 신용거래코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "AS0",
  "tr_key": ""
 }
}
```

---

<a id="tr-AS1"></a>
## `AS1` 해외주식주문체결(미국)

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `accno` | 계좌번호 | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `trcode` | TRCODE | String | Y | 8 | - |
| `comid` | 이용사번호 | String | Y | 3 | - |
| `userid` | 사용자ID | String | Y | 16 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `filler` | 예비영역 | String | Y | 6 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `sOrdxctPtnCode` | 주문체결유형코드 | String | Y | 2 | - |
| `sOrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `sOrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `sMgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `sAcntNo` | 계좌번호 | String | Y | 20 | - |
| `sAcntNm` | 계좌명 | String | Y | 40 | - |
| `sIsuNo` | 종목번호 | String | Y | 12 | - |
| `sIsuNm` | 종목명 | String | Y | 40 | - |
| `sOrdNo` | 주문번호 | String | Y | 10 | - |
| `sOrgOrdNo` | 원주문번호 | String | Y | 10 | - |
| `sExecNO` | 체결번호 | String | Y | 10 | - |
| `sAbrdExecId` | 해외체결ID | String | Y | 18 | - |
| `sOrdQty` | 주문수량 | String | Y | 16 | - |
| `sOrdPrc` | 주문가 | String | Y | 13 | - |
| `sExecQty` | 체결수량 | String | Y | 16 | - |
| `sExecPrc` | 체결가 | String | Y | 13 | - |
| `sMdfyCnfQty` | 정정확인수량 | String | Y | 16 | - |
| `sMdfyCnfPrc` | 정정확인가 | String | Y | 16 | - |
| `sCancCnfQty` | 취소확인수량 | String | Y | 16 | - |
| `sRjtQty` | 거부수량 | String | Y | 16 | - |
| `sOrdTrxPtnCode` | 주문처리유형코드 | String | Y | 4 | - |
| `sMtiordSeqno` | 복수주문일련번호 | String | Y | 10 | - |
| `sOrdCndi` | 주문조건 | String | Y | 1 | - |
| `sOrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `sShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `sOpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `sUnercQty` | 미체결수량(주문) | String | Y | 16 | - |
| `sOrgOrdUnercQty` | 원주문미체결수량 | String | Y | 16 | - |
| `sOrgOrdMdfyQty` | 원주문정정수량 | String | Y | 16 | - |
| `sOrgOrdCancQty` | 원주문취소수량 | String | Y | 16 | - |
| `sOrdAvrExecPrc` | 주문평균체결가 | String | Y | 13 | - |
| `sOrdAmt` | 주문금액 | String | Y | 16 | - |
| `sStdIsuNo` | 표준종목번호 | String | Y | 12 | - |
| `sBnsTp` | 매매구분 | String | Y | 1 | - |
| `sCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `sOrdAcntNo` | 주문계좌번호 | String | Y | 20 | - |
| `sAgrgtBrnNo` | 집계지점번호 | String | Y | 3 | - |
| `sRegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `sMnyMgnRat` | 현금증거금률 | String | Y | 7 | - |
| `sSubstMgnRat` | 대용증거금률 | String | Y | 9 | - |
| `sMnyExecAmt` | 현금체결금액 | String | Y | 16 | - |
| `sSubstExecAmt` | 대용체결금액 | String | Y | 16 | - |
| `sCmsnAmtExecAmt` | 수수료체결금액 | String | Y | 16 | - |
| `sPrdayRuseExecVal` | 전일재사용체결금액 | String | Y | 16 | - |
| `sCrdayRuseExecVal` | 금일재사용체결금액 | String | Y | 16 | - |
| `sSpotExecQty` | 실물체결수량 | String | Y | 16 | - |
| `sStslExecQty` | 공매도체결수량 | String | Y | 16 | - |
| `sStrtgCode` | 전략코드 | String | Y | 6 | - |
| `sGrpId` | 그룹ID | String | Y | 20 | - |
| `sOrdSeqno` | 주문회차 | String | Y | 10 | - |
| `sOrdUserId` | 주문자ID | String | Y | 16 | - |
| `sExecTime` | 체결시각 | String | Y | 9 | - |
| `sRcptExecTime` | 거래소수신체결시각 | String | Y | 9 | - |
| `sRjtRsn` | 거부사유 | String | Y | 8 | - |
| `sSecBalQty` | 잔고수량 | String | Y | 16 | - |
| `sSpotOrdAbleQty` | 실물주문가능수량 | String | Y | 16 | - |
| `sOrdAbleRuseQty` | 주문가능재사용수량 | String | Y | 16 | - |
| `sFlctQty` | 변동수량 | String | Y | 16 | - |
| `sSecBalQtyD2` | 잔고수량(D2) | String | Y | 16 | - |
| `sSellAbleQty` | 매도주문가능수량 | String | Y | 16 | - |
| `sUnercSellOrdQty` | 미체결매도주문수량 | String | Y | 16 | - |
| `sAvrPchsPrc` | 평균매입가 | String | Y | 13 | - |
| `sPchsAmt` | 매입금액 | String | Y | 16 | - |
| `sDeposit` | 예수금 | String | Y | 16 | - |
| `sSubstAmt` | 대용금 | String | Y | 16 | - |
| `sCsgnMnyMgn` | 위탁현금증거금액 | String | Y | 16 | - |
| `sCsgnSubstMgn` | 위탁대용증거금액 | String | Y | 16 | - |
| `sOrdAbleMny` | 주문가능현금 | String | Y | 16 | - |
| `sOrdAbleSubstAmt` | 주문가능대용금액 | String | Y | 16 | - |
| `sRuseAbleAmt` | 재사용가능금액 | String | Y | 16 | - |
| `sMgntrnCode` | 신용거래코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "AS1",
  "tr_key": ""
 }
}
```

---

<a id="tr-AS2"></a>
## `AS2` 해외주식주문정정(미국)

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `accno` | 계좌번호 | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `trcode` | TRCODE | String | Y | 8 | - |
| `comid` | 이용사번호 | String | Y | 3 | - |
| `userid` | 사용자ID | String | Y | 16 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `filler` | 예비영역 | String | Y | 6 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `sOrdxctPtnCode` | 주문체결유형코드 | String | Y | 2 | - |
| `sOrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `sOrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `sMgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `sAcntNo` | 계좌번호 | String | Y | 20 | - |
| `sAcntNm` | 계좌명 | String | Y | 40 | - |
| `sIsuNo` | 종목번호 | String | Y | 12 | - |
| `sIsuNm` | 종목명 | String | Y | 40 | - |
| `sOrdNo` | 주문번호 | String | Y | 10 | - |
| `sOrgOrdNo` | 원주문번호 | String | Y | 10 | - |
| `sExecNO` | 체결번호 | String | Y | 10 | - |
| `sAbrdExecId` | 해외체결ID | String | Y | 18 | - |
| `sOrdQty` | 주문수량 | String | Y | 16 | - |
| `sOrdPrc` | 주문가 | String | Y | 13 | - |
| `sExecQty` | 체결수량 | String | Y | 16 | - |
| `sExecPrc` | 체결가 | String | Y | 13 | - |
| `sMdfyCnfQty` | 정정확인수량 | String | Y | 16 | - |
| `sMdfyCnfPrc` | 정정확인가 | String | Y | 16 | - |
| `sCancCnfQty` | 취소확인수량 | String | Y | 16 | - |
| `sRjtQty` | 거부수량 | String | Y | 16 | - |
| `sOrdTrxPtnCode` | 주문처리유형코드 | String | Y | 4 | - |
| `sMtiordSeqno` | 복수주문일련번호 | String | Y | 10 | - |
| `sOrdCndi` | 주문조건 | String | Y | 1 | - |
| `sOrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `sShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `sOpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `sUnercQty` | 미체결수량(주문) | String | Y | 16 | - |
| `sOrgOrdUnercQty` | 원주문미체결수량 | String | Y | 16 | - |
| `sOrgOrdMdfyQty` | 원주문정정수량 | String | Y | 16 | - |
| `sOrgOrdCancQty` | 원주문취소수량 | String | Y | 16 | - |
| `sOrdAvrExecPrc` | 주문평균체결가 | String | Y | 13 | - |
| `sOrdAmt` | 주문금액 | String | Y | 16 | - |
| `sStdIsuNo` | 표준종목번호 | String | Y | 12 | - |
| `sBnsTp` | 매매구분 | String | Y | 1 | - |
| `sCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `sOrdAcntNo` | 주문계좌번호 | String | Y | 20 | - |
| `sAgrgtBrnNo` | 집계지점번호 | String | Y | 3 | - |
| `sRegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `sMnyMgnRat` | 현금증거금률 | String | Y | 7 | - |
| `sSubstMgnRat` | 대용증거금률 | String | Y | 9 | - |
| `sMnyExecAmt` | 현금체결금액 | String | Y | 16 | - |
| `sSubstExecAmt` | 대용체결금액 | String | Y | 16 | - |
| `sCmsnAmtExecAmt` | 수수료체결금액 | String | Y | 16 | - |
| `sPrdayRuseExecVal` | 전일재사용체결금액 | String | Y | 16 | - |
| `sCrdayRuseExecVal` | 금일재사용체결금액 | String | Y | 16 | - |
| `sSpotExecQty` | 실물체결수량 | String | Y | 16 | - |
| `sStslExecQty` | 공매도체결수량 | String | Y | 16 | - |
| `sStrtgCode` | 전략코드 | String | Y | 6 | - |
| `sGrpId` | 그룹ID | String | Y | 20 | - |
| `sOrdSeqno` | 주문회차 | String | Y | 10 | - |
| `sOrdUserId` | 주문자ID | String | Y | 16 | - |
| `sExecTime` | 체결시각 | String | Y | 9 | - |
| `sRcptExecTime` | 거래소수신체결시각 | String | Y | 9 | - |
| `sRjtRsn` | 거부사유 | String | Y | 8 | - |
| `sSecBalQty` | 잔고수량 | String | Y | 16 | - |
| `sSpotOrdAbleQty` | 실물주문가능수량 | String | Y | 16 | - |
| `sOrdAbleRuseQty` | 주문가능재사용수량 | String | Y | 16 | - |
| `sFlctQty` | 변동수량 | String | Y | 16 | - |
| `sSecBalQtyD2` | 잔고수량(D2) | String | Y | 16 | - |
| `sSellAbleQty` | 매도주문가능수량 | String | Y | 16 | - |
| `sUnercSellOrdQty` | 미체결매도주문수량 | String | Y | 16 | - |
| `sAvrPchsPrc` | 평균매입가 | String | Y | 13 | - |
| `sPchsAmt` | 매입금액 | String | Y | 16 | - |
| `sDeposit` | 예수금 | String | Y | 16 | - |
| `sSubstAmt` | 대용금 | String | Y | 16 | - |
| `sCsgnMnyMgn` | 위탁현금증거금액 | String | Y | 16 | - |
| `sCsgnSubstMgn` | 위탁대용증거금액 | String | Y | 16 | - |
| `sOrdAbleMny` | 주문가능현금 | String | Y | 16 | - |
| `sOrdAbleSubstAmt` | 주문가능대용금액 | String | Y | 16 | - |
| `sRuseAbleAmt` | 재사용가능금액 | String | Y | 16 | - |
| `sMgntrnCode` | 신용거래코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "AS2",
  "tr_key": ""
 }
}
```

---

<a id="tr-AS3"></a>
## `AS3` 해외주식주문취소(미국)

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `accno` | 계좌번호 | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `trcode` | TRCODE | String | Y | 8 | - |
| `comid` | 이용사번호 | String | Y | 3 | - |
| `userid` | 사용자ID | String | Y | 16 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `filler` | 예비영역 | String | Y | 6 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `sOrdxctPtnCode` | 주문체결유형코드 | String | Y | 2 | - |
| `sOrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `sOrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `sMgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `sAcntNo` | 계좌번호 | String | Y | 20 | - |
| `sAcntNm` | 계좌명 | String | Y | 40 | - |
| `sIsuNo` | 종목번호 | String | Y | 12 | - |
| `sIsuNm` | 종목명 | String | Y | 40 | - |
| `sOrdNo` | 주문번호 | String | Y | 10 | - |
| `sOrgOrdNo` | 원주문번호 | String | Y | 10 | - |
| `sExecNO` | 체결번호 | String | Y | 10 | - |
| `sAbrdExecId` | 해외체결ID | String | Y | 18 | - |
| `sOrdQty` | 주문수량 | String | Y | 16 | - |
| `sOrdPrc` | 주문가 | String | Y | 13 | - |
| `sExecQty` | 체결수량 | String | Y | 16 | - |
| `sExecPrc` | 체결가 | String | Y | 13 | - |
| `sMdfyCnfQty` | 정정확인수량 | String | Y | 16 | - |
| `sMdfyCnfPrc` | 정정확인가 | String | Y | 16 | - |
| `sCancCnfQty` | 취소확인수량 | String | Y | 16 | - |
| `sRjtQty` | 거부수량 | String | Y | 16 | - |
| `sOrdTrxPtnCode` | 주문처리유형코드 | String | Y | 4 | - |
| `sMtiordSeqno` | 복수주문일련번호 | String | Y | 10 | - |
| `sOrdCndi` | 주문조건 | String | Y | 1 | - |
| `sOrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `sShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `sOpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `sUnercQty` | 미체결수량(주문) | String | Y | 16 | - |
| `sOrgOrdUnercQty` | 원주문미체결수량 | String | Y | 16 | - |
| `sOrgOrdMdfyQty` | 원주문정정수량 | String | Y | 16 | - |
| `sOrgOrdCancQty` | 원주문취소수량 | String | Y | 16 | - |
| `sOrdAvrExecPrc` | 주문평균체결가 | String | Y | 13 | - |
| `sOrdAmt` | 주문금액 | String | Y | 16 | - |
| `sStdIsuNo` | 표준종목번호 | String | Y | 12 | - |
| `sBnsTp` | 매매구분 | String | Y | 1 | - |
| `sCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `sOrdAcntNo` | 주문계좌번호 | String | Y | 20 | - |
| `sAgrgtBrnNo` | 집계지점번호 | String | Y | 3 | - |
| `sRegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `sMnyMgnRat` | 현금증거금률 | String | Y | 7 | - |
| `sSubstMgnRat` | 대용증거금률 | String | Y | 9 | - |
| `sMnyExecAmt` | 현금체결금액 | String | Y | 16 | - |
| `sSubstExecAmt` | 대용체결금액 | String | Y | 16 | - |
| `sCmsnAmtExecAmt` | 수수료체결금액 | String | Y | 16 | - |
| `sPrdayRuseExecVal` | 전일재사용체결금액 | String | Y | 16 | - |
| `sCrdayRuseExecVal` | 금일재사용체결금액 | String | Y | 16 | - |
| `sSpotExecQty` | 실물체결수량 | String | Y | 16 | - |
| `sStslExecQty` | 공매도체결수량 | String | Y | 16 | - |
| `sStrtgCode` | 전략코드 | String | Y | 6 | - |
| `sGrpId` | 그룹ID | String | Y | 20 | - |
| `sOrdSeqno` | 주문회차 | String | Y | 10 | - |
| `sOrdUserId` | 주문자ID | String | Y | 16 | - |
| `sExecTime` | 체결시각 | String | Y | 9 | - |
| `sRcptExecTime` | 거래소수신체결시각 | String | Y | 9 | - |
| `sRjtRsn` | 거부사유 | String | Y | 8 | - |
| `sSecBalQty` | 잔고수량 | String | Y | 16 | - |
| `sSpotOrdAbleQty` | 실물주문가능수량 | String | Y | 16 | - |
| `sOrdAbleRuseQty` | 주문가능재사용수량 | String | Y | 16 | - |
| `sFlctQty` | 변동수량 | String | Y | 16 | - |
| `sSecBalQtyD2` | 잔고수량(D2) | String | Y | 16 | - |
| `sSellAbleQty` | 매도주문가능수량 | String | Y | 16 | - |
| `sUnercSellOrdQty` | 미체결매도주문수량 | String | Y | 16 | - |
| `sAvrPchsPrc` | 평균매입가 | String | Y | 13 | - |
| `sPchsAmt` | 매입금액 | String | Y | 16 | - |
| `sDeposit` | 예수금 | String | Y | 16 | - |
| `sSubstAmt` | 대용금 | String | Y | 16 | - |
| `sCsgnMnyMgn` | 위탁현금증거금액 | String | Y | 16 | - |
| `sCsgnSubstMgn` | 위탁대용증거금액 | String | Y | 16 | - |
| `sOrdAbleMny` | 주문가능현금 | String | Y | 16 | - |
| `sOrdAbleSubstAmt` | 주문가능대용금액 | String | Y | 16 | - |
| `sRuseAbleAmt` | 재사용가능금액 | String | Y | 16 | - |
| `sMgntrnCode` | 신용거래코드 | String | Y | 3 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "AS3",
  "tr_key": ""
 }
}
```

---

<a id="tr-AS4"></a>
## `AS4` 해외주식주문거부(미국)

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 8 | - |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `lineseq` | 라인일련번호 | String | Y | 10 | - |
| `accno` | 계좌번호 | String | Y | 11 | - |
| `user` | 조작자ID | String | Y | 8 | - |
| `len` | 헤더길이 | String | Y | 6 | - |
| `gubun` | 헤더구분 | String | Y | 1 | - |
| `compress` | 압축구분 | String | Y | 1 | - |
| `encrypt` | 암호구분 | String | Y | 1 | - |
| `offset` | 공통시작지점 | String | Y | 3 | - |
| `trcode` | TRCODE | String | Y | 8 | - |
| `comid` | 이용사번호 | String | Y | 3 | - |
| `userid` | 사용자ID | String | Y | 16 | - |
| `media` | 접속매체 | String | Y | 2 | - |
| `ifid` | I/F일련번호 | String | Y | 3 | - |
| `seq` | 전문일련번호 | String | Y | 9 | - |
| `trid` | TR추적ID | String | Y | 16 | - |
| `pubip` | 공인IP | String | Y | 12 | - |
| `prvip` | 사설IP | String | Y | 12 | - |
| `pcbpno` | 처리지점번호 | String | Y | 3 | - |
| `bpno` | 지점번호 | String | Y | 3 | - |
| `termno` | 단말번호 | String | Y | 8 | - |
| `lang` | 언어구분 | String | Y | 1 | - |
| `proctm` | AP처리시간 | String | Y | 9 | - |
| `msgcode` | 메세지코드 | String | Y | 4 | - |
| `outgu` | 메세지출력구분 | String | Y | 1 | - |
| `compreq` | 압축요청구분 | String | Y | 1 | - |
| `funckey` | 기능키 | String | Y | 4 | - |
| `reqcnt` | 요청레코드개수 | String | Y | 4 | - |
| `filler` | 예비영역 | String | Y | 6 | - |
| `cont` | 연속구분 | String | Y | 1 | - |
| `contkey` | 연속키값 | String | Y | 18 | - |
| `varlen` | 가변시스템길이 | String | Y | 2 | - |
| `varhdlen` | 가변해더길이 | String | Y | 2 | - |
| `varmsglen` | 가변메시지길이 | String | Y | 2 | - |
| `trsrc` | 조회발원지 | String | Y | 1 | - |
| `eventid` | I/F이벤트ID | String | Y | 4 | - |
| `ifinfo` | I/F정보 | String | Y | 4 | - |
| `filler1` | 예비영역 | String | Y | 41 | - |
| `sOrdxctPtnCode` | 주문체결유형코드 | String | Y | 2 | - |
| `sOrdMktCode` | 주문시장코드 | String | Y | 2 | - |
| `sOrdPtnCode` | 주문유형코드 | String | Y | 2 | - |
| `sMgmtBrnNo` | 관리지점번호 | String | Y | 3 | - |
| `sAcntNo` | 계좌번호 | String | Y | 20 | - |
| `sAcntNm` | 계좌명 | String | Y | 40 | - |
| `sIsuNo` | 종목번호 | String | Y | 12 | - |
| `sIsuNm` | 종목명 | String | Y | 40 | - |
| `sOrdNo` | 주문번호 | String | Y | 10 | - |
| `sOrgOrdNo` | 원주문번호 | String | Y | 10 | - |
| `sExecNO` | 체결번호 | String | Y | 10 | - |
| `sAbrdExecId` | 해외체결ID | String | Y | 18 | - |
| `sOrdQty` | 주문수량 | String | Y | 16 | - |
| `sOrdPrc` | 주문가 | String | Y | 13 | - |
| `sExecQty` | 체결수량 | String | Y | 16 | - |
| `sExecPrc` | 체결가 | String | Y | 13 | - |
| `sMdfyCnfQty` | 정정확인수량 | String | Y | 16 | - |
| `sMdfyCnfPrc` | 정정확인가 | String | Y | 16 | - |
| `sCancCnfQty` | 취소확인수량 | String | Y | 16 | - |
| `sRjtQty` | 거부수량 | String | Y | 16 | - |
| `sOrdTrxPtnCode` | 주문처리유형코드 | String | Y | 4 | - |
| `sMtiordSeqno` | 복수주문일련번호 | String | Y | 10 | - |
| `sOrdCndi` | 주문조건 | String | Y | 1 | - |
| `sOrdprcPtnCode` | 호가유형코드 | String | Y | 2 | - |
| `sShtnIsuNo` | 단축종목번호 | String | Y | 9 | - |
| `sOpDrtnNo` | 운용지시번호 | String | Y | 12 | - |
| `sUnercQty` | 미체결수량(주문) | String | Y | 16 | - |
| `sOrgOrdUnercQty` | 원주문미체결수량 | String | Y | 16 | - |
| `sOrgOrdMdfyQty` | 원주문정정수량 | String | Y | 16 | - |
| `sOrgOrdCancQty` | 원주문취소수량 | String | Y | 16 | - |
| `sOrdAvrExecPrc` | 주문평균체결가 | String | Y | 13 | - |
| `sOrdAmt` | 주문금액 | String | Y | 16 | - |
| `sStdIsuNo` | 표준종목번호 | String | Y | 12 | - |
| `sBnsTp` | 매매구분 | String | Y | 1 | - |
| `sCommdaCode` | 통신매체코드 | String | Y | 2 | - |
| `sOrdAcntNo` | 주문계좌번호 | String | Y | 20 | - |
| `sAgrgtBrnNo` | 집계지점번호 | String | Y | 3 | - |
| `sRegMktCode` | 등록시장코드 | String | Y | 2 | - |
| `sMnyMgnRat` | 현금증거금률 | String | Y | 7 | - |
| `sSubstMgnRat` | 대용증거금률 | String | Y | 9 | - |
| `sMnyExecAmt` | 현금체결금액 | String | Y | 16 | - |
| `sSubstExecAmt` | 대용체결금액 | String | Y | 16 | - |
| `sCmsnAmtExecAmt` | 수수료체결금액 | String | Y | 16 | - |
| `sPrdayRuseExecVal` | 전일재사용체결금액 | String | Y | 16 | - |
| `sCrdayRuseExecVal` | 금일재사용체결금액 | String | Y | 16 | - |
| `sSpotExecQty` | 실물체결수량 | String | Y | 16 | - |
| `sStslExecQty` | 공매도체결수량 | String | Y | 16 | - |
| `sStrtgCode` | 전략코드 | String | Y | 6 | - |
| `sGrpId` | 그룹ID | String | Y | 20 | - |
| `sOrdSeqno` | 주문회차 | String | Y | 10 | - |
| `sOrdUserId` | 주문자ID | String | Y | 16 | - |
| `sExecTime` | 체결시각 | String | Y | 9 | - |
| `sRcptExecTime` | 거래소수신체결시각 | String | Y | 9 | - |
| `sRjtRsn` | 거부사유 | String | Y | 8 | - |
| `sSecBalQty` | 잔고수량 | String | Y | 16 | - |
| `sSpotOrdAbleQty` | 실물주문가능수량 | String | Y | 16 | - |
| `sOrdAbleRuseQty` | 주문가능재사용수량 | String | Y | 16 | - |
| `sFlctQty` | 변동수량 | String | Y | 16 | - |
| `sSecBalQtyD2` | 잔고수량(D2) | String | Y | 16 | - |
| `sSellAbleQty` | 매도주문가능수량 | String | Y | 16 | - |
| `sUnercSellOrdQty` | 미체결매도주문수량 | String | Y | 16 | - |
| `sAvrPchsPrc` | 평균매입가 | String | Y | 13 | - |
| `sPchsAmt` | 매입금액 | String | Y | 16 | - |
| `sDeposit` | 예수금 | String | Y | 16 | - |
| `sSubstAmt` | 대용금 | String | Y | 16 | - |
| `sCsgnMnyMgn` | 위탁현금증거금액 | String | Y | 16 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "1"
 },
 "body": {
  "tr_cd": "AS4",
  "tr_key": ""
 }
}
```

---

<a id="tr-GSH"></a>
## `GSH` 해외주식 호가

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 18 | Key 종목코드 + 남은 자릿수만큼 공백<br/>ex) '82TSLA ' <br/>'82TSLA' + 공백 12자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `symbol` | 종목코드 | String | Y | 16 | - |
| `loctime` | 현지호가시간 | String | Y | 6 | - |
| `kortime` | 한국호가시간 | String | Y | 6 | - |
| `offerho1` | 매도호가1 | String | Y | 15.6 | - |
| `bidho1` | 매수호가1 | String | Y | 15.6 | - |
| `offerrem1` | 매도호가잔량1 | String | Y | 10 | - |
| `bidrem1` | 매수호가잔량1 | String | Y | 10 | - |
| `offerno1` | 매도호가건수1 | String | Y | 10 | - |
| `bidno1` | 매수호가건수1 | String | Y | 10 | - |
| `offerho2` | 매도호가2 | String | Y | 15.6 | - |
| `bidho2` | 매수호가2 | String | Y | 15.6 | - |
| `offerrem2` | 매도호가잔량2 | String | Y | 10 | - |
| `bidrem2` | 매수호가잔량2 | String | Y | 10 | - |
| `offerno2` | 매도호가건수2 | String | Y | 10 | - |
| `bidno2` | 매수호가건수2 | String | Y | 10 | - |
| `offerho3` | 매도호가3 | String | Y | 15.6 | - |
| `bidho3` | 매수호가3 | String | Y | 15.6 | - |
| `offerrem3` | 매도호가잔량3 | String | Y | 10 | - |
| `bidrem3` | 매수호가잔량3 | String | Y | 10 | - |
| `offerno3` | 매도호가건수3 | String | Y | 10 | - |
| `bidno3` | 매수호가건수3 | String | Y | 10 | - |
| `offerho4` | 매도호가4 | String | Y | 15.6 | - |
| `bidho4` | 매수호가4 | String | Y | 15.6 | - |
| `offerrem4` | 매도호가잔량4 | String | Y | 10 | - |
| `bidrem4` | 매수호가잔량4 | String | Y | 10 | - |
| `offerno4` | 매도호가건수4 | String | Y | 10 | - |
| `bidno4` | 매수호가건수4 | String | Y | 10 | - |
| `offerho5` | 매도호가5 | String | Y | 15.6 | - |
| `bidho5` | 매수호가5 | String | Y | 15.6 | - |
| `offerrem5` | 매도호가잔량5 | String | Y | 10 | - |
| `bidrem5` | 매수호가잔량5 | String | Y | 10 | - |
| `offerno5` | 매도호가건수5 | String | Y | 10 | - |
| `bidno5` | 매수호가건수5 | String | Y | 10 | - |
| `offerho6` | 매도호가6 | String | Y | 15.6 | - |
| `bidho6` | 매수호가6 | String | Y | 15.6 | - |
| `offerrem6` | 매도호가잔량6 | String | Y | 10 | - |
| `bidrem6` | 매수호가잔량6 | String | Y | 10 | - |
| `offerno6` | 매도호가건수6 | String | Y | 10 | - |
| `bidno6` | 매수호가건수6 | String | Y | 10 | - |
| `offerho7` | 매도호가7 | String | Y | 15.6 | - |
| `bidho7` | 매수호가7 | String | Y | 15.6 | - |
| `offerrem7` | 매도호가잔량7 | String | Y | 10 | - |
| `bidrem7` | 매수호가잔량7 | String | Y | 10 | - |
| `offerno7` | 매도호가건수7 | String | Y | 10 | - |
| `bidno7` | 매수호가건수7 | String | Y | 10 | - |
| `offerho8` | 매도호가8 | String | Y | 15.6 | - |
| `bidho8` | 매수호가8 | String | Y | 15.6 | - |
| `offerrem8` | 매도호가잔량8 | String | Y | 10 | - |
| `bidrem8` | 매수호가잔량8 | String | Y | 10 | - |
| `offerno8` | 매도호가건수8 | String | Y | 10 | - |
| `bidno8` | 매수호가건수8 | String | Y | 10 | - |
| `offerho9` | 매도호가9 | String | Y | 15.6 | - |
| `bidho9` | 매수호가9 | String | Y | 15.6 | - |
| `offerrem9` | 매도호가잔량9 | String | Y | 10 | - |
| `bidrem9` | 매수호가잔량9 | String | Y | 10 | - |
| `offerno9` | 매도호가건수9 | String | Y | 10 | - |
| `bidno9` | 매수호가건수9 | String | Y | 10 | - |
| `offerho10` | 매도호가10 | String | Y | 15.6 | - |
| `bidho10` | 매수호가10 | String | Y | 15.6 | - |
| `offerrem10` | 매도호가잔량10 | String | Y | 10 | - |
| `bidrem10` | 매수호가잔량10 | String | Y | 10 | - |
| `offerno10` | 매도호가건수10 | String | Y | 10 | - |
| `bidno10` | 매수호가건수10 | String | Y | 10 | - |
| `totoffercnt` | 매도호가총건수 | String | Y | 10 | - |
| `totbidcnt` | 매수호가총건수 | String | Y | 10 | - |
| `totofferrem` | 매도호가총수량 | String | Y | 10 | - |
| `totbidrem` | 매수호가총수량 | String | Y | 10 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "GSH",
  "tr_key": "81SOXL            "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "GSH",
        "tr_key": "81SOXL            "
    },
    "body": {
        "offerho4": "12.2400",
        "symbol": "SOXL",
        "offerho3": "12.2300",
        "offerho6": "12.2600",
        "offerho5": "12.2500",
        "offerno2": "0",
        "offerho8": "12.2800",
        "offerno1": "0",
        "offerho7": "12.2700",
        "offerno4": "0",
        "offerno3": "0",
        "offerho9": "12.2900",
        "offerno6": "0",
        "offerno5": "0",
        "offerno8": "0",
        "offerno7": "0",
        "offerno9": "0",
        "offerno10": "0",
        "bidno10": "0",
        "offerho2": "12.2200",
        "offerho1": "12.2100",
        "offerho10": "12.3000",
        "loctime": "044331",
        "totofferrem": "8418",
        "totbidrem": "12760",
        "offerrem2": "0",
        "bidho5": "12.1600",
        "offerrem3": "0",
        "bidho4": "12.1700",
        "bidno1": "0",
        "offerrem4": "0",
        "bidho7": "12.1400",
        "offerrem5": "0",
        "bidho6": "12.1500",
        "bidno3": "0",
        "bidho9": "12.1200",
        "bidno2": "0",
        "bidho8": "12.1300",
        "bidno5": "0",
        "offerrem1": "8418",
        "bidno4": "0",
        "bidno7": "0",
        "bidno6": "0",
        "bidno9": "0",
        "totoffercnt": "0",
        "bidno8": "0",
        "offerrem6": "0",
        "totbidcnt": "0",
        "offerrem7": "0",
        "offerrem8": "0",
        "offerrem9": "0",
        "bidrem3": "0",
        "bidrem4": "0",
        "bidrem1": "12760",
        "bidrem2": "0",
        "bidrem9": "0",
        "bidho1": "12.2000",
        "bidrem7": "0",
        "bidrem8": "0",
        "bidho3": "12.1800",
        "bidrem5": "0",
        "bidho2": "12.1900",
        "bidrem6": "0",
        "bidrem10": "0",
        "bidho10": "12.1100",
        "kortime": "174331",
        "offerrem10": "0"
    }
}
```

---

<a id="tr-GSC"></a>
## `GSC` 해외주식 체결

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `token` | 접근토큰 | String | Y | 1000 | Access Token을 설정하기 위한 Header Parameter |
| `tr_type` | 거래 Type | String | Y | 1 | 1: 계좌등록, 2: 계좌해제, 3: 실시간 시세 등록, 4: 실시간 시세 해제 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |
| `tr_key` | 단축코드 | String | N | 18 | Key 종목코드 + 18자리에서 남은 자릿수만큼 공백<br/>ex) '82TSLA ' <br/>'82TSLA' + 공백 12자리 |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `tr_cd` | 거래 CD | String | Y | 3 | LS증권 거래코드 |


### 응답 Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `symbol` | 종목코드 | String | Y | 16 | - |
| `ovsdate` | 체결일자(현지) | String | Y | 8 | - |
| `kordate` | 체결일자(한국) | String | Y | 8 | - |
| `trdtm` | 체결시간(현지) | String | Y | 6 | - |
| `kortm` | 체결시간(한국) | String | Y | 6 | - |
| `sign` | 전일대비구분 | String | Y | 1 | - |
| `price` | 체결가격 | String | Y | 15.6 | - |
| `diff` | 전일대비 | String | Y | 15.6 | - |
| `rate` | 등락율 | String | Y | 6.2 | - |
| `open` | 시가 | String | Y | 15.6 | - |
| `high` | 고가 | String | Y | 15.6 | - |
| `low` | 저가 | String | Y | 15.6 | - |
| `trdq` | 건별체결수량 | String | Y | 10 | - |
| `totq` | 누적체결수량 | String | Y | 15 | - |
| `cgubun` | 체결구분 | String | Y | 1 | - |
| `lSeq` | 초당시퀀스 | String | Y | 3 | - |
| `amount` | 누적거래대금 | String | Y | 16 | - |
| `high52p` | 52주고가 | String | Y | 15.6 | - |
| `low52p` | 52주저가 | String | Y | 15.6 | - |


### 요청 Example

```json
{
 "header": {
  "token": "토큰",
  "tr_type": "3"
 },
 "body": {
  "tr_cd": "GSC",
  "tr_key": "81SOXL            "
 }
}
```

### 응답 Example

```json
{
    "header": {
        "tr_cd": "GSC",
        "tr_key": "81SOXL            "
    },
    "body": {
        "symbol": "SOXL",
        "lSeq": "0",
        "high52p": "70.0800",
        "low52p": "7.2250",
        "amount": "7771791",
        "kordate": "20250429",
        "trdtm": "044222",
        "sign": "5",
        "ovsdate": "20250429",
        "diff": "0.0800",
        "totq": "637963",
        "high": "12.3000",
        "rate": "-0.65",
        "low": "12.1000",
        "price": "12.2100",
        "cgubun": "+",
        "trdq": "16",
        "open": "12.3000",
        "kortm": "174222"
    }
}
```
