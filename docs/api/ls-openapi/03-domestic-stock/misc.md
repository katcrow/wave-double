# [주식] 기타

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=316495d3-6109-45a6-baaf-9e8a0261f30a)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `316495d3-6109-45a6-baaf-9e8a0261f30a` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/etc` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 신용잔고 및 신규상장종목 등 종목별 기타정보를 확인할 수 있는 서비스입니다. |

## TR 목록 (10건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 예탁담보융자가능종목현황조회 | [CLNAQ00100](misc.md#tr-CLNAQ00100) | 1 | 1 | 30 |
| 신규상장종목조회 | [t1403](misc.md#tr-t1403) | 1 | 1 | 1 |
| 증거금율별종목조회 | [t1411](misc.md#tr-t1411) | 1 | 1 | 3 |
| 종목별잔량/사전공시 | [t1638](misc.md#tr-t1638) | 1 | 1 | 1 |
| 신용거래동향 | [t1921](misc.md#tr-t1921) | 1 | 1 | 3 |
| 종목별신용정보 | [t1926](misc.md#tr-t1926) | 1 | 1 | 3 |
| 공매도일별추이 | [t1927](misc.md#tr-t1927) | 1 | 1 | 3 |
| 종목별대차거래일간추이 | [t1941](misc.md#tr-t1941) | 1 | 1 | 3 |
| 주식종목조회 | [t8430](misc.md#tr-t8430) | 2 | 2 | 5 |
| 주식종목조회 API용 | [t8436](misc.md#tr-t8436) | 2 | 2 | 5 |

---

<a id="tr-CLNAQ00100"></a>
## `CLNAQ00100` 예탁담보융자가능종목현황조회

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
| `CLNAQ00100InBlock1` | CLNAQ00100InBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | 0@전체, 1@가능, 2@불가능 |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-SecTpCode` | 유가증권구분 | String | Y | 1 | 0@전체, 3@거래소, 4@코스닥, 1@주식(거래소+코스닥) |
| `&nbsp;&nbsp;-LoanIntrstGrdCode` | 대출이자등급코드 | String | Y | 2 | 00 |
| `&nbsp;&nbsp;-LoanTp` | 대출구분 | String | Y | 1 | 1@예탁증권담보융자, 3@융자, 4@유통대주, 5@자기대주 |


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
| `CLNAQ00100OutBlock1` | CLNAQ00100OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-QryTp` | 조회구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-SecTpCode` | 유가증권구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-LoanIntrstGrdCode` | 대출이자등급코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-LoanTp` | 대출구분 | String | Y | 1 | - |
| `CLNAQ00100OutBlock2` | CLNAQ00100OutBlock2 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-IsuNo` | 종목번호 | String | Y | 12 | - |
| `&nbsp;&nbsp;-IsuNm` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-Parprc` | 액면가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-PrdayCprc` | 전일종가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-RatVal` | 비율값 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-SubstPrc` | 대용가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-RegTpNm` | 등록구분 | String | Y | 20 | - |
| `&nbsp;&nbsp;-SpotMgnLevyClssNm` | 현물증거금징수분류명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-FnoTrdStopRsnCnts` | 거래정지사유 | String | Y | 40 | - |
| `&nbsp;&nbsp;-DgrsPtnNm` | 요주의유형명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-AcdPtnNm` | 사고유형 | String | Y | 40 | - |
| `&nbsp;&nbsp;-MktTpNm` | 시장구분 | String | Y | 20 | - |
| `&nbsp;&nbsp;-LmtVal` | 한도값 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-AcntLmtVal` | 계좌한도값 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-LoanGrdCode` | 대출등급코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-LoanAmt` | 대출금액 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-LoanAbleRat` | 대출가능율 | Number | Y | 26.9 | - |
| `&nbsp;&nbsp;-LoanIntrat1` | 대출이율1 | Number | Y | 14.4 | - |
| `&nbsp;&nbsp;-RegPsnId` | 등록자ID | String | Y | 16 | - |
| `&nbsp;&nbsp;-Rat01` | 비율값 | Number | Y | 19.8 | - |
| `&nbsp;&nbsp;-Rat02` | 비율값 | Number | Y | 19.8 | - |
| `CLNAQ00100OutBlock3` | CLNAQ00100OutBlock3 | Object | Y | - | - |
| `&nbsp;&nbsp;-RecCnt` | 레코드갯수 | Number | Y | 5 | - |
| `&nbsp;&nbsp;-LrgMnyoutSumAmt` | 대출금합계금액 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "CLNAQ00100InBlock1": {
    "RecCnt": 1,
    "QryTp": "0",
    "IsuNo": "A005930",
    "SecTpCode": "0",
    "LoanIntrstGrdCode": "00",
    "LoanTp": "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00133",
    "CLNAQ00100OutBlock3": {
        "LrgMnyoutSumAmt": 2000000,
        "RecCnt": 1
    },
    "CLNAQ00100OutBlock2": [
        {
            "SubstPrc": "40080.00",
            "AcntLmtVal": 0,
            "SpotMgnLevyClssNm": "징수",
            "DgrsPtnNm": "정상",
            "RegTpNm": "불가능",
            "RegPsnId": "CLNEB17800",
            "RatVal": "99.99000000",
            "LoanGrdCode": "",
            "LoanAbleRat": "0.000000000",
            "LmtVal": 0,
            "LoanIntrat1": "0.0000",
            "IsuNm": "삼성전자",
            "Parprc": "100.00",
            "AcdPtnNm": "일반",
            "MktTpNm": "KOSPI 50",
            "LoanAmt": 0,
            "IsuNo": "A005930",
            "Rat02": "0.00000000",
            "Rat01": "0.00000000",
            "FnoTrdStopRsnCnts": "주식:정상, 채권:거래중단",
            "PrdayCprc": "68500.00"
        },
        {
            "SubstPrc": "77370.00",
            "AcntLmtVal": 200000000,
            "SpotMgnLevyClssNm": "",
            "DgrsPtnNm": "정상",
            "RegTpNm": "가능",
            "RegPsnId": "30788",
            "RatVal": "99.99000000",
            "LoanGrdCode": "D1",
            "LoanAbleRat": "60.000000000",
            "LmtVal": 500000000,
            "LoanIntrat1": "9.8000",
            "IsuNm": "삼아알미늄",
            "Parprc": "500.00",
            "AcdPtnNm": "일반",
            "MktTpNm": "기타",
            "LoanAmt": 0,
            "IsuNo": "A006110",
            "Rat02": "0.00000000",
            "Rat01": "0.00000000",
            "FnoTrdStopRsnCnts": "주식:정상, 채권:거래중단",
            "PrdayCprc": "74300.00"
        }
    ],
    "CLNAQ00100OutBlock1": {
        "RecCnt": 1,
        "IsuNo": "KR7005930003",
        "LoanTp": "1",
        "SecTpCode": "0",
        "LoanIntrstGrdCode": "00",
        "QryTp": "0"
    },
    "rsp_msg": "조회가 계속 됩니다. 계속하시려면 연속버튼을 누르십시오."
}
```

---

<a id="tr-t1403"></a>
## `t1403` 신규상장종목조회

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
| `t1403InBlock` | t1403InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0: 전체, 1:코스피, 2:코스닥 |
| `&nbsp;&nbsp;-styymm` | 시작상장월 | String | Y | 6 | YYYYMM |
| `&nbsp;&nbsp;-enyymm` | 종료상장월 | String | Y | 6 | YYYYMM |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 연속조회시 OutBlock의 동일필드 입력 |


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
| `t1403OutBlock` | t1403OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1403OutBlock1` | t1403OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-kmprice` | 공모가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-date` | 등록일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-recprice` | 등록일기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-kmdiff` | 기준가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-close` | 등록일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-recdiff` | 등록일등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1403InBlock" : {
    "gubun" : "1",
    "styymm" : "1",
    "enyymm" : "1",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1403OutBlock": {
        "idx": 0
    },
    "t1403OutBlock1": [
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1411"></a>
## `t1411` 증거금율별종목조회

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
| `t1411InBlock` | t1411InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 시장구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-jongchk` | 위탁신용구분 | String | Y | 1 | 1:위탁 2:신용 |
| `&nbsp;&nbsp;-jkrate` | 증거금율구분 | String | Y | 1 | 2:20% 3:30% 5:40% 1:100% |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
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
| `t1411OutBlock` | t1411OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-jkrate` | 위탁증거금율 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-sjkrate` | 신용증거금율 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1411OutBlock1` | t1411OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-jkrate` | 위탁증거금율 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-sjkrate` | 신용증거금율 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-subprice` | 대용가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-recprice` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1411InBlock" : {
    "gubun" : "0",
    "jongchk" : "1",
    "jkrate" : "1",
    "shcode" : "005930",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1411OutBlock1": [
        {
            "volume": 298,
            "sjkrate": 100,
            "subprice": 440,
            "recprice": 661,
            "price": 661,
            "shcode": "000040",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "jkrate": 100,
            "hname": "KR모터스"
        },
        {
            "volume": 0,
            "sjkrate": 100,
            "subprice": 10000,
            "recprice": 15160,
            "price": 15160,
            "shcode": "002025",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "jkrate": 100,
            "hname": "코오롱우"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1411OutBlock": {
        "sjkrate": 45,
        "jkrate": 20,
        "idx": 40
    }
}
```

---

<a id="tr-t1638"></a>
## `t1638` 종목별잔량/사전공시

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
| `t1638InBlock` | t1638InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 구분 | String | Y | 1 | 1 : 코스피<br/>2 : 코스닥 |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun2` | 정렬 | String | Y | 1 | 1 : 시가총액비중<br/>2 : 순매수잔량상위<br/>3 : 순매수잔량하위<br/>4 : 매수잔량<br/>5 : 매수공시수량<br/>6 : 매도잔량<br/>7 : 매도공시수량 |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리 |


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
| `t1638OutBlock` | t1638OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-rank` | 순위 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sigatotrt` | 시총비중 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-obuyvol` | 순매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-buyrem` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-psgvolume` | 매수공시수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sellrem` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-pdgvolume` | 매도공시수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sigatot` | 시가총액 | Number | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1638InBlock" : {
    "gubun1" : "1",
    "shcode" : "",
    "gubun2" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1638OutBlock": [
        {
            "sellrem": 0,
            "obuyvol": 100000,
            "change": 15000,
            "shcode": "005930",
            "sign": "1",
            "diff": "29.94",
            "buyrem": 100000,
            "sigatotrt": "78.06",
            "price": 65100,
            "rank": 1,
            "psgvolume": 0,
            "sigatot": 388632844005000,
            "hname": "삼성전자",
            "pdgvolume": 0
        },
        {
            "sellrem": 0,
            "obuyvol": 999,
            "change": 31400,
            "shcode": "000660",
            "sign": "5",
            "diff": "-20.89",
            "buyrem": 999,
            "sigatotrt": "17.39",
            "price": 118900,
            "rank": 2,
            "psgvolume": 0,
            "sigatot": 86559481198500,
            "hname": "SK하이닉스",
            "pdgvolume": 0
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1921"></a>
## `t1921` 신용거래동향

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
| `t1921InBlock` | t1921InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun` | 융자대주구분 | String | Y | 1 | 1:융자 2:대주 |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 다음 조회시 사용 OutBlock의 date 필드를 입력함. |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 사용안함 |


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
| `t1921OutBlock` | t1921OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | CNT | Number | Y | 4 | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1921OutBlock1` | t1921OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-mmdate` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jchange` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-nvolume` | 신규 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svolume` | 상환 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jvolume` | 잔고 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gyrate` | 공여율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jkrate` | 잔고율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1921InBlock" : {
    "shcode" : "005930",
    "gubun" : "1",
    "date" : "",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1921OutBlock": {
        "date": "20230508",
        "cnt": 21,
        "idx": 19
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1921OutBlock1": [
        {
            "mmdate": "20230607",
            "change": -185642,
            "shcode": "005930",
            "sign": "5",
            "diff": "-0.98",
            "nvolume": 152082,
            "jchange": 700,
            "gyrate": "1.29",
            "price": 267837,
            "svolume": 335820,
            "jvolume": 4208557,
            "jkrate": "0.07",
            "close": 71000
        },
        {
            "mmdate": "20230605",
            "change": 186226,
            "shcode": "005930",
            "sign": "5",
            "diff": "-0.69",
            "nvolume": 348101,
            "jchange": 500,
            "gyrate": "2.39",
            "price": 279201,
            "svolume": 161531,
            "jvolume": 4394199,
            "jkrate": "0.07",
            "close": 71700
        }
    ]
}
```

---

<a id="tr-t1926"></a>
## `t1926` 종목별신용정보

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
| `t1926InBlock` | t1926InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


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
| `t1926OutBlock` | t1926OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-ynvolume` | 융자신규수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ysvolume` | 융자상환수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yjvolume` | 융자잔고수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yvchange` | 융자수량대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ygrate` | 융자공여율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-yjrate` | 융자잔고율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-ynprice` | 융자신규금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ysprice` | 융자상환금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yjprice` | 융자잔고금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yachange` | 융자금액대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnvolume` | 대주신규수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dsvolume` | 대주상환수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-djvolume` | 대주잔고수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dvchange` | 대주수량대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dgrate` | 대주공여율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-djrate` | 대주잔고율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dnprice` | 대주신규금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dsprice` | 대주상환금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-djprice` | 대주잔고금액 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dachange` | 대주금액대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mmdate` | 결제일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 결제일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 결제일거래량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-value` | 결제일거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-pr5days` | 주가5일증가율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-pr20days` | 주가20일증가율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-yj5days` | 융자5일증가율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-yj20days` | 융자20일증가율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dj5days` | 대주5일증가율 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dj20days` | 대주20일증가율 | Number | Y | 9.2 | - |


### 요청 Example

```json
{
  "t1926InBlock" : {
    "shcode" : "005930"
  }
}
```

### 응답 Example

```json
{
    "t1926OutBlock": {
        "ysprice": 20523,
        "yjvolume": 4208557,
        "djrate": "0.00",
        "yjprice": 267837,
        "yj20days": "-5.91",
        "djvolume": 45936,
        "dsprice": 109,
        "pr5days": "-0.56",
        "yj5days": "0.36",
        "close": 71000,
        "value": 1049990,
        "mmdate": "20230607",
        "dsvolume": 1520,
        "dachange": 187,
        "dgrate": "0.03",
        "ynvolume": 152082,
        "yvchange": -185642,
        "dnvolume": 4105,
        "dvchange": 2585,
        "dj5days": "12.67",
        "volume": 14755937,
        "ysvolume": 335820,
        "ynprice": 9288,
        "djprice": 3062,
        "yjrate": "0.07",
        "dj20days": "41.57",
        "ygrate": "1.29",
        "pr20days": "8.73",
        "yachange": -11364,
        "dnprice": 283
    },
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1927"></a>
## `t1927` 공매도일별추이

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
| `t1927InBlock` | t1927InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | 다음 조회시 사용. OutBlock의 date 필드 값을 입력함. |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |


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
| `t1927OutBlock` | t1927OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자CTS | String | Y | 8 | - |
| `t1927OutBlock1` | t1927OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_vo` | 공매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_va` | 공매도대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_per` | 공매도거래비중 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gm_avg` | 평균공매도단가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_vo_sum` | 누적공매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_vo1` | 업틱룰적용공매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_va1` | 업틱룰적용공매도대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_vo2` | 업틱룰예외공매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gm_va2` | 업틱룰예외공매도대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1927InBlock" : {
    "shcode" : "005930",
    "date" : "",
    "sdate" : "20230501",
    "edate" : "20230601"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1927OutBlock1": [
        {
            "date": "20230601",
            "gm_vo_sum": 15254680,
            "change": 500,
            "sign": "5",
            "diff": "-0.70",
            "gm_vo": 315193,
            "gm_vo1": 207440,
            "volume": 14566407,
            "gm_vo2": 107753,
            "gm_per": "2.16",
            "price": 70900,
            "gm_avg": 71158,
            "gm_va": 22428,
            "value": 1034489,
            "gm_va1": 14743,
            "gm_va2": 7686
        },
        {
            "date": "20230531",
            "gm_vo_sum": 14939487,
            "change": 900,
            "sign": "5",
            "diff": "-1.24",
            "gm_vo": 856055,
            "gm_vo1": 526062,
            "volume": 24153085,
            "gm_vo2": 329993,
            "gm_per": "3.54",
            "price": 71400,
            "gm_avg": 71964,
            "gm_va": 61605,
            "value": 1732624,
            "gm_va1": 37825,
            "gm_va2": 23780
        }
    ],
    "t1927OutBlock": {
        "date": "20230502"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1941"></a>
## `t1941` 종목별대차거래일간추이

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
| `t1941InBlock` | t1941InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |


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
| `t1941OutBlock1` | t1941OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-upvolume` | 당일체결 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dnvolume` | 당일상환 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tovolume` | 당일잔고 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tovalue` | 잔고금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-tovoldif` | 대차증감 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1941InBlock" : {
    "shcode" : "078020",
    "sdate" : "20230102",
    "edate" : "20230602"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1941OutBlock1": [
        {
            "date": "20230602",
            "volume": 32336,
            "tovolume": 270304,
            "price": 4525,
            "change": 25,
            "shcode": "078020",
            "sign": "2",
            "dnvolume": 0,
            "diff": "0.56",
            "upvolume": 0,
            "tovalue": 1223,
            "tovoldif": 0
        },
        {
            "date": "20230102",
            "volume": 61901,
            "tovolume": 178947,
            "price": 4845,
            "change": 155,
            "shcode": "078020",
            "sign": "5",
            "dnvolume": 155,
            "diff": "-3.10",
            "upvolume": 0,
            "tovalue": 867,
            "tovoldif": -155
        }
    ]
}
```

---

<a id="tr-t8430"></a>
## `t8430` 주식종목조회

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
| `t8430InBlock` | t8430InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분(0:전체1:코스피2:코스닥) | String | Y | 1 | - |


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
| `t8430OutBlock` | t8430OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-etfgubun` | ETF구분(1:ETF) | String | Y | 1 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-memedan` | 주문수량단위 | String | Y | 5 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gubun` | 구분(1:코스피2:코스닥) | String | Y | 1 | - |


### 요청 Example

```json
{
  "t8430InBlock" : {
    "gubun" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t8430OutBlock": [
        {
            "memedan": "00001",
            "recprice": 10550,
            "shcode": "000020",
            "jnilclose": 10550,
            "uplmtprice": 13710,
            "expcode": "KR7000020008",
            "hname": "동화약품",
            "etfgubun": "0",
            "dnlmtprice": 7390,
            "gubun": "1"
        },
        {
            "memedan": "00001",
            "recprice": 22750,
            "shcode": "006740",
            "jnilclose": 22750,
            "uplmtprice": 29550,
            "expcode": "KR7006740005",
            "hname": "영풍제지",
            "etfgubun": "0",
            "dnlmtprice": 15950,
            "gubun": "1"
        }
    ]
}
```

---

<a id="tr-t8436"></a>
## `t8436` 주식종목조회 API용

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
| `t8436InBlock` | t8436InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분(0:전체1:코스피2:코스닥) | String | Y | 1 | - |


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
| `t8436OutBlock` | t8436OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-etfgubun` | ETF구분(1:ETF2:ETN) | String | Y | 1 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-memedan` | 주문수량단위 | String | Y | 5 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gubun` | 구분(1:코스피2:코스닥) | String | Y | 1 | - |
| `&nbsp;&nbsp;-bu12gubun` | 증권그룹 | String | Y | 2 | - |
| `&nbsp;&nbsp;-spac_gubun` | 기업인수목적회사여부(Y/N) | String | Y | 1 | - |
| `&nbsp;&nbsp;-filler` | filler(미사용) | String | Y | 32 | - |


### 요청 Example

```json
{
  "t8436InBlock" : {
    "gubun" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t8436OutBlock": [
        {
            "shcode": "000020",
            "jnilclose": 10550,
            "uplmtprice": 13710,
            "spac_gubun": "N",
            "etfgubun": "0",
            "dnlmtprice": 7390,
            "gubun": "1",
            "memedan": "00001",
            "recprice": 10550,
            "bu12gubun": "01",
            "filler": "",
            "expcode": "KR7000020008",
            "hname": "동화약품"
        },
        {
            "shcode": "005385",
            "jnilclose": 107900,
            "uplmtprice": 140200,
            "spac_gubun": "N",
            "etfgubun": "0",
            "dnlmtprice": 75600,
            "gubun": "1",
            "memedan": "00001",
            "recprice": 107900,
            "bu12gubun": "01",
            "filler": "",
            "expcode": "KR7005381009",
            "hname": "현대차우"
        }
    ]
}
```
