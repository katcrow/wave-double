# [주식] 차트

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=12320341-ad85-429a-90bd-5b3771c5e89f)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `12320341-ad85-429a-90bd-5b3771c5e89f` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/chart` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 개별종목 시세차트 및 기간별투자자매매 차트를 확인할 수 있는 서비스입니다. |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 기간별투자자매매추이(차트) | [t1665](chart.md#tr-t1665) | 1 | 1 | 3 |
| API전용주식차트(일주월년) | [t8410](chart.md#tr-t8410) | 1 | 1 | 3 |
| 주식차트(틱/n틱) | [t8411](chart.md#tr-t8411) | 1 | 1 | 3 |
| 주식차트(N분) | [t8412](chart.md#tr-t8412) | 1 | 1 | 3 |
| (통합)주식챠트(일주월년) API용 | [t8451](chart.md#tr-t8451) | 1 | 1 | 3 |
| (통합)주식챠트(N분) API용 | [t8452](chart.md#tr-t8452) | 1 | 1 | 3 |
| (통합)주식챠트(틱/N틱) API용 | [t8453](chart.md#tr-t8453) | 1 | 1 | 3 |

---

<a id="tr-t1665"></a>
## `t1665` 기간별투자자매매추이(차트)

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
| `t1665InBlock` | t1665InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-market` | 시장구분 | String | Y | 1 | 1@코스피<br/>2@KP200<br/>3@코스닥<br/>4@선물<br/>5@풋옵션<br/>6@콜옵션 |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-gubun2` | 수치구분(1:수치2:누적) | String | Y | 1 | - |
| `&nbsp;&nbsp;-gubun3` | 단위구분(1:일2:주3:월) | String | Y | 1 | - |
| `&nbsp;&nbsp;-from_date` | 시작날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-to_date` | 종료날짜 | String | Y | 8 | - |
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
| `t1665OutBlock` | t1665OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mcode` | 시장코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-mname` | 시장명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |
| `t1665OutBlock1` | t1665OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-sv_08` | 개인수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_17` | 외인계수량(등록+미등록) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_18` | 기관계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_01` | 증권수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_03` | 투신수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_04` | 은행수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_02` | 보험수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_05` | 종금수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_06` | 기금수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_07` | 기타수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_00` | 사모펀드수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_09` | 등록외국인수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_10` | 미등록외국인수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_11` | 국가수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_99` | 기타계수량(기타+국가) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_08` | 개인금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_17` | 외인계금액(등록+미등록) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_18` | 기관계금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_01` | 증권금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_03` | 투신금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_04` | 은행금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_02` | 보험금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_05` | 종금금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_06` | 기금금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_07` | 기타금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_00` | 사모펀드금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_09` | 등록외국인금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_10` | 미등록외국인금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_11` | 국가금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_99` | 기타계금액(기타+국가) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jisu` | 시장지수 | Number | Y | 7.2 | - |


### 요청 Example

```json
{
  "t1665InBlock" : {
    "market" : "1",
    "upcode" : "001",
    "gubun2" : "1",
    "gubun3" : "1",
    "from_date" : "20230101",
    "to_date" : "20230619"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1665OutBlock": {
        "mcode": "001KGG01",
        "mname": "종       합"
    },
    "t1665OutBlock1": [
        {
            "date": "20230619",
            "sv_18": -2,
            "sv_17": 2,
            "sa_01": "3",
            "jisu": "252618.00",
            "sa_02": "0",
            "sa_00": "-4",
            "sv_03": 0,
            "sa_05": "0",
            "sv_02": 1,
            "sa_06": "-5",
            "sv_01": 9,
            "sa_03": "0",
            "sv_00": -10,
            "sa_04": "3",
            "sa_09": "1",
            "sa_07": "2",
            "sa_08": "1",
            "sv_07": 0,
            "sv_06": -9,
            "sv_05": 0,
            "sv_04": 6,
            "sv_09": 2,
            "sv_08": 0,
            "sv_10": 0,
            "sa_10": "0",
            "sa_11": "0",
            "sa_99": "2",
            "sa_17": "1",
            "sv_11": 0,
            "sv_99": 0,
            "sa_18": "-3"
        },
        {
            "date": "20230616",
            "sv_18": -243,
            "sv_17": 3,
            "sa_01": "-160",
            "jisu": "262579.00",
            "sa_02": "-1",
            "sa_00": "6",
            "sv_03": 0,
            "sa_05": "0",
            "sv_02": -1,
            "sa_06": "2",
            "sv_01": -277,
            "sa_03": "0",
            "sv_00": 23,
            "sa_04": "11",
            "sa_09": "2",
            "sa_07": "1",
            "sa_08": "139",
            "sv_07": 2,
            "sv_06": 3,
            "sv_05": 0,
            "sv_04": 10,
            "sv_09": 3,
            "sv_08": 238,
            "sv_10": -1,
            "sa_10": "0",
            "sa_11": "0",
            "sa_99": "1",
            "sa_17": "2",
            "sv_11": 0,
            "sv_99": 2,
            "sa_18": "-142"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8410"></a>
## `t8410` API전용주식차트(일주월년)

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
| `t8410InBlock` | t8410InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분(2:일3:주4:월5:년) | String | Y | 1 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | OPENAPI에서는 압축 미제공 |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 조회구간종료일<br/>Space:기본값 |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회 |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | OPENAPI에서는 압축 미제공 |
| `&nbsp;&nbsp;-sujung` | 수정주가여부(Y:적용N:비적용) | String | Y | 1 | - |


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
| `t8410OutBlock` | t8410OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-svi_uplmtprice` | 정적VI상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svi_dnlmtprice` | 정적VI하한가 | Number | Y | 8 | - |
| `t8410OutBlock1` | t8410OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-rate` | 수정비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-pricechk` | 수정주가반영항목 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-ratevalue` | 수정비율반영거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sign` | 종가등락구분(1:상한2:상승3:보합4:하한5:하락주식일만사용) | String | Y | 1 | - |


### 요청 Example

```json
{
  "t8410InBlock" : {
    "shcode" : "078020",
    "gubun" : "2",
    "qrycnt" : 200,
    "sdate" : "",
    "edate" : "",
    "cts_date" : "",
    "comp_yn" : "N",
    "sujung" : "Y"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8410OutBlock": {
        "cts_date": "",
        "shcode": "078020",
        "highend": 5880,
        "svi_dnlmtprice": 4095,
        "jivolume": 32336,
        "e_time": "153000",
        "jisiga": 4500,
        "svi_uplmtprice": 5010,
        "jilow": 4470,
        "diclose": 4530,
        "dshmin": "10",
        "disiga": 4550,
        "s_time": "090000",
        "lowend": 3170,
        "dihigh": 4600,
        "jihigh": 4565,
        "rec_count": 1,
        "dilow": 4520,
        "jiclose": 4525
    },
    "t8410OutBlock1": [
        {
            "date": "20230605",
            "jdiff_vol": 33764,
            "high": 4600,
            "jongchk": 0,
            "pricechk": 0,
            "low": 4520,
            "rate": "000.00",
            "ratevalue": 0,
            "sign": "2",
            "close": 4530,
            "value": 153,
            "open": 4550
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8411"></a>
## `t8411` 주식차트(틱/n틱)

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
| `t8411InBlock` | t8411InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n틱) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 기본값 : Space<br/>(edate(필수입력) 기준으로 qrycnt 만큼 조회)<br/>조회구간을 설정하여 필터링 하고 싶은 경우 입력 |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회<br/>("99999999" 혹은 '당일') |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | - |


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
| `t8411OutBlock` | t8411OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8411OutBlock1` | t8411OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-rate` | 수정비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-pricechk` | 수정주가반영항목 | Number | Y | 13 | - |


### 요청 Example

```json
{
  "t8411InBlock" : {
    "shcode" : "078020",
    "ncnt" : 1,
    "qrycnt" : 200,
    "nday" : "0",
    "sdate" : "",
    "stime" : "",
    "edate" : "",
    "etime" : "",
    "cts_date" : "",
    "cts_time" : "",
    "comp_yn" : "N"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "해당자료가 없습니다."
}
```

---

<a id="tr-t8412"></a>
## `t8412` 주식차트(N분)

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
| `t8412InBlock` | t8412InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n분) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 기본값 : Space<br/>(edate(필수입력) 기준으로 qrycnt 만큼 조회)<br/>조회구간을 설정하여 필터링 하고 싶은 경우 입력 |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회<br/>("99999999" 혹은 '당일') |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | - |


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
| `t8412OutBlock` | t8412OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8412OutBlock1` | t8412OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-rate` | 수정비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 종가등락구분(1:상한2:상승3:보합4:하한5:하락) | String | Y | 1 | - |


### 요청 Example

```json
{
  "t8412InBlock" : {
    "shcode" : "078020",
    "ncnt" : 1,
    "qrycnt" : 500,
    "nday" : "0",
    "sdate" : "",
    "stime" : "",
    "edate" : "99999999",
    "etime" : "",
    "cts_date" : "",
    "cts_time" : "",
    "comp_yn" : "N"
  }
}
```

### 응답 Example

```json
{
    "t8412OutBlock": {
        "shcode": "078020",
        "jisiga": 4550,
        "jihigh": 4610,
        "jilow": 4320,
        "jiclose": 4555,
        "jivolume": 49742,
        "disiga": 4495,
        "dihigh": 4540,
        "dilow": 4280,
        "diclose": 4515,
        "highend": 5920,
        "lowend": 3190,
        "cts_date": "20240906",
        "cts_time": "111200",
        "s_time": "090000",
        "e_time": "153000",
        "dshmin": "10",
        "rec_count": 500
    },
    "t8412OutBlock1": [
        {
            "date": "20240906",
            "time": "111300",
            "open": 4445,
            "high": 4470,
            "low": 4445,
            "close": 4470,
            "jdiff_vol": 2317,
            "value": 10,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "111400",
            "open": 4470,
            "high": 4470,
            "low": 4445,
            "close": 4470,
            "jdiff_vol": 8301,
            "value": 37,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "111500",
            "open": 4440,
            "high": 4465,
            "low": 4440,
            "close": 4465,
            "jdiff_vol": 1130,
            "value": 5,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "111600",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 321,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "111700",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "111800",
            "open": 4470,
            "high": 4505,
            "low": 4470,
            "close": 4505,
            "jdiff_vol": 4100,
            "value": 18,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "111900",
            "open": 4480,
            "high": 4540,
            "low": 4475,
            "close": 4540,
            "jdiff_vol": 2791,
            "value": 13,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "112000",
            "open": 4550,
            "high": 4550,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "112100",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 8,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "112200",
            "open": 4545,
            "high": 4550,
            "low": 4545,
            "close": 4550,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "112300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 50,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "112400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "112500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "112600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "112700",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 200,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "112800",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "112900",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113000",
            "open": 4545,
            "high": 4550,
            "low": 4545,
            "close": 4550,
            "jdiff_vol": 4001,
            "value": 18,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 555,
            "value": 3,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 5,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113500",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113600",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 52,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "113700",
            "open": 4550,
            "high": 4610,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 168,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "113800",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "113900",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114000",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114100",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114200",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114300",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114400",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114500",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114600",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114700",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114800",
            "open": 4530,
            "high": 4530,
            "low": 4530,
            "close": 4530,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "114900",
            "open": 4505,
            "high": 4505,
            "low": 4505,
            "close": 4505,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "115000",
            "open": 4505,
            "high": 4505,
            "low": 4505,
            "close": 4505,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "115100",
            "open": 4570,
            "high": 4575,
            "low": 4570,
            "close": 4575,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115200",
            "open": 4575,
            "high": 4575,
            "low": 4575,
            "close": 4575,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115300",
            "open": 4575,
            "high": 4575,
            "low": 4575,
            "close": 4575,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115400",
            "open": 4575,
            "high": 4575,
            "low": 4575,
            "close": 4575,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115500",
            "open": 4505,
            "high": 4505,
            "low": 4490,
            "close": 4495,
            "jdiff_vol": 651,
            "value": 3,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "115600",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115700",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115800",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "115900",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "120000",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "120100",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "120200",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "120300",
            "open": 4570,
            "high": 4570,
            "low": 4570,
            "close": 4570,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "120400",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 44,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "120500",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 44,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "120600",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 5,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "120700",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "120800",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "120900",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "121000",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "121100",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "121200",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "121300",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 500,
            "value": 2,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "121400",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "121500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "121600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "121700",
            "open": 4545,
            "high": 4555,
            "low": 4545,
            "close": 4555,
            "jdiff_vol": 42,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "121800",
            "open": 4555,
            "high": 4555,
            "low": 4555,
            "close": 4555,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "121900",
            "open": 4555,
            "high": 4560,
            "low": 4555,
            "close": 4560,
            "jdiff_vol": 344,
            "value": 2,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122000",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122100",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122200",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 66,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122300",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122400",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122500",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122600",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122700",
            "open": 4555,
            "high": 4560,
            "low": 4555,
            "close": 4560,
            "jdiff_vol": 9,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122800",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "122900",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123000",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123100",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123200",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123300",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123400",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123500",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123600",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123700",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123800",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "123900",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124000",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124100",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124200",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124300",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124400",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124500",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124600",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124700",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124800",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "124900",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125000",
            "open": 4560,
            "high": 4560,
            "low": 4560,
            "close": 4560,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125500",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125600",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 30,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125700",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125800",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "125900",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "130000",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "130100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "130200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "130300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "130400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 11,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "130500",
            "open": 4520,
            "high": 4520,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 594,
            "value": 3,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "130600",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "130700",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "130800",
            "open": 4520,
            "high": 4520,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 184,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "130900",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 55,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131000",
            "open": 4505,
            "high": 4505,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 113,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131200",
            "open": 4495,
            "high": 4495,
            "low": 4495,
            "close": 4495,
            "jdiff_vol": 45,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131300",
            "open": 4495,
            "high": 4495,
            "low": 4495,
            "close": 4495,
            "jdiff_vol": 70,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131400",
            "open": 4535,
            "high": 4540,
            "low": 4535,
            "close": 4540,
            "jdiff_vol": 52,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131500",
            "open": 4540,
            "high": 4540,
            "low": 4540,
            "close": 4540,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131600",
            "open": 4540,
            "high": 4540,
            "low": 4540,
            "close": 4540,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131700",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131800",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "131900",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 17,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132000",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132100",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132200",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132300",
            "open": 4525,
            "high": 4525,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 30,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132400",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132500",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132600",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132700",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132800",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "132900",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133000",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133100",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133200",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133300",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133400",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133500",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133600",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133700",
            "open": 4525,
            "high": 4525,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 329,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133800",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 105,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "133900",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134000",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134100",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134200",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134300",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134400",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134500",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134600",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 555,
            "value": 3,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134700",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134800",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 65,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "134900",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135000",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135100",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135200",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135300",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135400",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135500",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135600",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135700",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135800",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "135900",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "140000",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 100,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 100,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140500",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140600",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140700",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140800",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "140900",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141000",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141500",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141600",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141700",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141800",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "141900",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142000",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142500",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142600",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142700",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142800",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "142900",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "143000",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "143100",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "143200",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "143300",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "143400",
            "open": 4550,
            "high": 4550,
            "low": 4550,
            "close": 4550,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240906",
            "time": "143500",
            "open": 4550,
            "high": 4550,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 11,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "143600",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "143700",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "143800",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "143900",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144000",
            "open": 4525,
            "high": 4525,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 304,
            "value": 1,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144100",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144200",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144300",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144400",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144500",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144600",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144700",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144800",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "144900",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "145000",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "145100",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "145200",
            "open": 4525,
            "high": 4525,
            "low": 4525,
            "close": 4525,
            "jdiff_vol": 34,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "145300",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 26,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "145400",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "145500",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "145600",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "145700",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "145800",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "145900",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150000",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150100",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150200",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 352,
            "value": 2,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150300",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150400",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150500",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150600",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150700",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150800",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "150900",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 5,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151000",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151100",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151200",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 14,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151300",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151400",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151500",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151600",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151700",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151800",
            "open": 4545,
            "high": 4545,
            "low": 4520,
            "close": 4545,
            "jdiff_vol": 7,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "151900",
            "open": 4545,
            "high": 4545,
            "low": 4545,
            "close": 4545,
            "jdiff_vol": 1100,
            "value": 5,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "3"
        },
        {
            "date": "20240906",
            "time": "152000",
            "open": 4520,
            "high": 4550,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 92,
            "value": 0,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "5"
        },
        {
            "date": "20240906",
            "time": "153000",
            "open": 4555,
            "high": 4555,
            "low": 4555,
            "close": 4555,
            "jdiff_vol": 2235,
            "value": 10,
            "jongchk": 0,
            "rate": "0.00",
            "sign": "2"
        },
        {
            "date": "20240909",
            "time": "090100",
            "open": 4495,
            "high": 4500,
            "low": 4280,
            "close": 4500,
            "jdiff_vol": 2024,
            "value": 9,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090300",
            "open": 4495,
            "high": 4495,
            "low": 4495,
            "close": 4495,
            "jdiff_vol": 60,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090400",
            "open": 4450,
            "high": 4450,
            "low": 4450,
            "close": 4450,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090500",
            "open": 4420,
            "high": 4420,
            "low": 4420,
            "close": 4420,
            "jdiff_vol": 18,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090600",
            "open": 4440,
            "high": 4440,
            "low": 4425,
            "close": 4425,
            "jdiff_vol": 30,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090700",
            "open": 4420,
            "high": 4420,
            "low": 4410,
            "close": 4410,
            "jdiff_vol": 82,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090800",
            "open": 4405,
            "high": 4405,
            "low": 4405,
            "close": 4405,
            "jdiff_vol": 27,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "090900",
            "open": 4405,
            "high": 4405,
            "low": 4405,
            "close": 4405,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091000",
            "open": 4435,
            "high": 4435,
            "low": 4435,
            "close": 4435,
            "jdiff_vol": 1061,
            "value": 5,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091100",
            "open": 4435,
            "high": 4435,
            "low": 4435,
            "close": 4435,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091200",
            "open": 4495,
            "high": 4540,
            "low": 4495,
            "close": 4515,
            "jdiff_vol": 925,
            "value": 4,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091300",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 71,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091400",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 3,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091500",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 200,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091800",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 8,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "091900",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092000",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092100",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092200",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092300",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092400",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 6,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092700",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092800",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "092900",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093000",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093100",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093200",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093300",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093400",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093500",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093600",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093700",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 7,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093800",
            "open": 4485,
            "high": 4490,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 131,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "093900",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 72,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094000",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 50,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094100",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094200",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 4,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094300",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094400",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094500",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 7,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094600",
            "open": 4475,
            "high": 4475,
            "low": 4475,
            "close": 4475,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094700",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 7,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094800",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "094900",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095000",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095100",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095200",
            "open": 4480,
            "high": 4480,
            "low": 4480,
            "close": 4480,
            "jdiff_vol": 80,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095300",
            "open": 4480,
            "high": 4480,
            "low": 4480,
            "close": 4480,
            "jdiff_vol": 6,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095400",
            "open": 4480,
            "high": 4480,
            "low": 4480,
            "close": 4480,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095500",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 41,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095600",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095700",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095800",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "095900",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 61,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100000",
            "open": 4460,
            "high": 4460,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100100",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 8,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100200",
            "open": 4465,
            "high": 4465,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 21,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100300",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 27,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100400",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100500",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100600",
            "open": 4470,
            "high": 4470,
            "low": 4470,
            "close": 4470,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100700",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 24,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100800",
            "open": 4470,
            "high": 4470,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 46,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "100900",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 47,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101000",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101100",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101200",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 30,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101300",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101400",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101500",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 21,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101600",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 21,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101700",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101800",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 55,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "101900",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 5,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102000",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102100",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102200",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102300",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102400",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102500",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102600",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102700",
            "open": 4455,
            "high": 4455,
            "low": 4455,
            "close": 4455,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102800",
            "open": 4455,
            "high": 4465,
            "low": 4455,
            "close": 4465,
            "jdiff_vol": 297,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "102900",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103000",
            "open": 4465,
            "high": 4465,
            "low": 4465,
            "close": 4465,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103100",
            "open": 4465,
            "high": 4470,
            "low": 4465,
            "close": 4470,
            "jdiff_vol": 939,
            "value": 4,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103200",
            "open": 4480,
            "high": 4510,
            "low": 4480,
            "close": 4510,
            "jdiff_vol": 100,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103300",
            "open": 4505,
            "high": 4515,
            "low": 4505,
            "close": 4515,
            "jdiff_vol": 980,
            "value": 4,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103400",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103500",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103600",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103700",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103800",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "103900",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104000",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104100",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104200",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104300",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 20,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104400",
            "open": 4515,
            "high": 4515,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 250,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104800",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "104900",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105000",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105100",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105200",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105300",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105400",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 2,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105700",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 51,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105800",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "105900",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110000",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110100",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110200",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110300",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110400",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 53,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110700",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110800",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "110900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 51,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111300",
            "open": 4500,
            "high": 4500,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 21,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111400",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111500",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111600",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111700",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111800",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "111900",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112000",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112100",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112200",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112300",
            "open": 4505,
            "high": 4510,
            "low": 4505,
            "close": 4510,
            "jdiff_vol": 100,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112400",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112700",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112800",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "112900",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113000",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113100",
            "open": 4510,
            "high": 4515,
            "low": 4510,
            "close": 4515,
            "jdiff_vol": 472,
            "value": 2,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113200",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 31,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113300",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113400",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113500",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 18,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113600",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113700",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113800",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "113900",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114000",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114100",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114200",
            "open": 4510,
            "high": 4510,
            "low": 4510,
            "close": 4510,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114300",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114400",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114500",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114600",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114700",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 12,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114800",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "114900",
            "open": 4520,
            "high": 4520,
            "low": 4520,
            "close": 4520,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115000",
            "open": 4510,
            "high": 4510,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 1232,
            "value": 6,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115100",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 200,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115200",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115300",
            "open": 4490,
            "high": 4490,
            "low": 4490,
            "close": 4490,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 1,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 112,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "115900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 287,
            "value": 1,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120300",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "120900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121300",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "121900",
            "open": 4505,
            "high": 4505,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 5,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122300",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 34,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 18,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "122900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123300",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 10,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "123900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124300",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "124900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125300",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125800",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "125900",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130000",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130100",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130200",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130300",
            "open": 4505,
            "high": 4505,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 40,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130400",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 550,
            "value": 2,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130500",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 100,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130600",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130700",
            "open": 4500,
            "high": 4500,
            "low": 4500,
            "close": 4500,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130800",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 100,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "130900",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "131000",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        },
        {
            "date": "20240909",
            "time": "131100",
            "open": 4515,
            "high": 4515,
            "low": 4515,
            "close": 4515,
            "jdiff_vol": 0,
            "value": 0,
            "jongchk": 0,
            "rate": "0",
            "sign": "5"
        }
    ],
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8451"></a>
## `t8451` (통합)주식챠트(일주월년) API용

### 요청 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `authorization` | 접근토큰 | String | Y | 1000 | OAuth 토큰이 필요한 API 경우 발급한 Access Token을 설정하기 위한 Request Heaeder Parameter |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |
| `mac_address` | MAC 주소 | String | Y | 12 | 법인인 경우 필수 세팅 |


### 요청 Body / Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `t8451InBlock` | t8451InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분(2:일3:주4:월5:년) | String | Y | 1 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대:500) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(N:비압축) | String | Y | 1 | N:비압축<br/>OPEN API 압축 미제공 |
| `&nbsp;&nbsp;-sujung` | 수정주가여부(Y:적용N:비적용) | String | Y | 1 | - |
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
| `t8451OutBlock` | 단축코드t8451OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | - | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-svi_uplmtprice` | 정적VI상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svi_dnlmtprice` | 정적VI하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-nxt_fm_s_time` | NXT프리마켓장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_fm_e_time` | NXT프리마켓장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_fm_dshmin` | NXT프리마켓동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-nxt_am_s_time` | NXT에프터마켓장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_am_e_time` | NXT에프터마켓장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_am_dshmin` | NXT에프터마켓동시호가처리시간(MM:분) | String | Y | 2 | - |
| `t8451OutBlock1` | t8451OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-rate` | 수정비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-pricechk` | 수정주가반영항목 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-ratevalue` | 수정비율반영거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sign` | 종가등락구분(1:상한2:상승3:보합4:하한5:하락주식일만사용) | String | Y | 1 | 1:상한2:상승3:보합4:하한5:하락주식일만사용 |


### 요청 Example

```json
{
  "t8451InBlock" : {
    "shcode" : "010950",
    "gubun" : "2",
    "qrycnt" : 10,
    "sdate" : "",
    "edate" : "99999999",
    "cts_date" : "",
    "comp_yn" : "N",
    "sujung" : "N",
    "exchgubun" : "N"
  }
}
```

### 응답 Example

```json
{
	"t8451OutBlock": {
		"shcode": "010950",
		"jisiga": 62200,
		"jihigh": 62200,
		"jilow": 59700,
		"jiclose": 60500,
		"jivolume": 55839,
		"disiga": 60400,
		"dihigh": 62700,
		"dilow": 60300,
		"diclose": 60600,
		"highend": 78200,
		"lowend": 42200,
		"cts_date": "",
		"s_time": "090000",
		"e_time": "152000",
		"dshmin": "00",
		"rec_count": 7,
		"svi_uplmtprice": 66300,
		"svi_dnlmtprice": 54100,
		"nxt_fm_s_time": "080000",
		"nxt_fm_e_time": "085000",
		"nxt_fm_dshmin": "00",
		"nxt_am_s_time": "154000",
		"nxt_am_e_time": "200000",
		"nxt_am_dshmin": "00"
	},
	"t8451OutBlock1": [
		{
			"date": "20250304",
			"open": 57100,
			"high": 57350,
			"low": 55800,
			"close": 56000,
			"jdiff_vol": 14583,
			"value": 817,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "5"
		},
		{
			"date": "20250305",
			"open": 55700,
			"high": 57200,
			"low": 55500,
			"close": 57200,
			"jdiff_vol": 17087,
			"value": 971,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250306",
			"open": 57400,
			"high": 58500,
			"low": 56500,
			"close": 57100,
			"jdiff_vol": 12561,
			"value": 715,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250307",
			"open": 57100,
			"high": 57400,
			"low": 56500,
			"close": 57400,
			"jdiff_vol": 15994,
			"value": 914,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250310",
			"open": 57400,
			"high": 62300,
			"low": 57400,
			"close": 61800,
			"jdiff_vol": 168115,
			"value": 10209,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250311",
			"open": 62200,
			"high": 62200,
			"low": 59700,
			"close": 60500,
			"jdiff_vol": 55839,
			"value": 3374,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "5"
		},
		{
			"date": "20250312",
			"open": 60400,
			"high": 62700,
			"low": 60300,
			"close": 60600,
			"jdiff_vol": 26988,
			"value": 1651,
			"jongchk": 0,
			"rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8452"></a>
## `t8452` (통합)주식챠트(N분) API용

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
| `t8452InBlock` | t8452InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n분) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대:500) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(N:비압축) | String | Y | 1 | N:비압축<br/>OPEN API 압축 미제공 |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t8452OutBlock` | t8452OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jiclosev` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-nxt_fm_s_time` | NXT프리마켓장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_fm_e_time` | NXT프리마켓장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_fm_dshmin` | NXT프리마켓동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-nxt_am_s_time` | NXT에프터마켓장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_am_e_time` | NXT에프터마켓장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_am_dshmin` | NXT에프터마켓동시호가처리시간(MM:분) | String | Y | 2 | - |
| `t8452OutBlock1` | t8452OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-rate` | 수정비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 종가등락구분(1:상한2:상승3:보합4:하한5:하락) | String | Y | 1 | 1:상한2:상승3:보합4:하한5:하락 |


### 요청 Example

```json
{
  "t8452InBlock" : {
    "shcode" : "010950",
    "ncnt" : 1,
    "qrycnt" : 10,
    "nday" : "0",
    "sdate" : "",
    "stime" : "",
    "edate" : "99999999",
    "etime" : "",
    "cts_date" : "",
    "cts_time" : "",
    "comp_yn" : "N",
    "exchgubun" : "K"

  }
}
```

### 응답 Example

```json
{
	"t8452OutBlock": {
		"shcode": "010950",
		"jisiga": 60900,
		"jihigh": 61100,
		"jilow": 59500,
		"jiclose": 60200,
		"jivolume": 264237,
		"disiga": 60700,
		"dihigh": 61300,
		"dilow": 60300,
		"diclose": 60500,
		"highend": 78200,
		"lowend": 42200,
		"cts_date": "20250312",
		"cts_time": "141800",
		"s_time": "090000",
		"e_time": "153000",
		"dshmin": "10",
		"rec_count": 10,
		"nxt_fm_s_time": "080000",
		"nxt_fm_e_time": "085000",
		"nxt_fm_dshmin": "00",
		"nxt_am_s_time": "154000",
		"nxt_am_e_time": "200000",
		"nxt_am_dshmin": "00"
	},
	"t8452OutBlock1": [
		{
			"date": "20250312",
			"time": "141900",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 288,
			"value": 17,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142000",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60700,
			"jdiff_vol": 80,
			"value": 5,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142100",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 158,
			"value": 10,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142200",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60700,
			"jdiff_vol": 396,
			"value": 24,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142300",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 237,
			"value": 14,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142400",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 101,
			"value": 6,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142500",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 268,
			"value": 16,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142600",
			"open": 60700,
			"high": 60700,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 158,
			"value": 10,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142700",
			"open": 60600,
			"high": 60700,
			"low": 60500,
			"close": 60500,
			"jdiff_vol": 276,
			"value": 17,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		},
		{
			"date": "20250312",
			"time": "142800",
			"open": 60700,
			"high": 60700,
			"low": 60500,
			"close": 60500,
			"jdiff_vol": 36,
			"value": 2,
			"jongchk": 0,
			"rate": "0.00",
			"sign": "2"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8453"></a>
## `t8453` (통합)주식챠트(틱/N틱) API용

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
| `t8453InBlock` | t8453InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n틱) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대:500) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(N:비압축) | String | Y | 1 | N:비압축<br/>OPEN API 압축 미제공 |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t8453OutBlock` | t8453OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jicloseㅍ` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-nxt_fm_s_time` | NXT프리마켓장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_fm_e_time` | NXT프리마켓장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_fm_dshmin` | NXT프리마켓동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-nxt_am_s_time` | NXT에프터마켓장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_am_e_time` | NXT에프터마켓장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-nxt_am_dshmin` | NXT에프터마켓동시호가처리시간(MM:분) | String | Y | 2 | - |
| `t8453OutBlock1` | t8453OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Number | Y | 13 | - |
| `&nbsp;&nbsp;-rate` | 수정비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-pricechk` | 수정주가반영항목 | Number | Y | 13 | - |


### 요청 Example

```json
{
  "t8453InBlock" : {
    "shcode" : "010950",
    "ncnt" : 1,
    "qrycnt" : 10,
    "nday" : "0",
    "sdate" : "",
    "stime" : "",
    "edate" : "99999999",
    "etime" : "",
    "cts_date" : "",
    "cts_time" : "",
    "comp_yn" : "N",
    "exchgubun" : "N"
  }
}
```

### 응답 Example

```json
{
	"t8453OutBlock": {
		"shcode": "010950",
		"jisiga": 62200,
		"jihigh": 62200,
		"jilow": 59700,
		"jiclose": 60500,
		"jivolume": 55839,
		"disiga": 60400,
		"dihigh": 62700,
		"dilow": 60300,
		"diclose": 60600,
		"highend": 78200,
		"lowend": 42200,
		"cts_date": "20250312",
		"cts_time": "1421271843",
		"s_time": "090000",
		"e_time": "152000",
		"dshmin": "00",
		"rec_count": 10,
		"nxt_fm_s_time": "080000",
		"nxt_fm_e_time": "085000",
		"nxt_fm_dshmin": "00",
		"nxt_am_s_time": "154000",
		"nxt_am_e_time": "200000",
		"nxt_am_dshmin": "00"
	},
	"t8453OutBlock1": [
		{
			"date": "20250312",
			"time": "142127",
			"open": 60700,
			"high": 60700,
			"low": 60700,
			"close": 60700,
			"jdiff_vol": 1,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "142134",
			"open": 60700,
			"high": 60700,
			"low": 60700,
			"close": 60700,
			"jdiff_vol": 68,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "142324",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 1,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "142648",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 80,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "142738",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 16,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "142747",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 1,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "142757",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 1,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "143004",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 1,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "143024",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 20,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		},
		{
			"date": "20250312",
			"time": "143040",
			"open": 60600,
			"high": 60600,
			"low": 60600,
			"close": 60600,
			"jdiff_vol": 36,
			"jongchk": 0,
			"rate": "0",
			"pricechk": 0
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
