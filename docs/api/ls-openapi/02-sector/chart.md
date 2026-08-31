# [업종] 차트

> LS증권 OPEN API 정의서 · 그룹: **업종** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=f82999f4-eb1a-4ead-a0b1-a4386e8721ab&api_id=5b483d74-407c-4760-8452-1b2b1dc1dcde)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `5b483d74-407c-4760-8452-1b2b1dc1dcde` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/indtp/chart` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 업종 기간별 차트를 확인할 수 있는 서비스입니다. |

## TR 목록 (3건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 업종차트(틱/n틱) | [t8408](chart.md#tr-t8408) | 1 | - | - |
| 업종차트(N분) | [t8409](chart.md#tr-t8409) | 1 | - | - |
| 업종차트(일주월) | [t8429](chart.md#tr-t8429) | 1 | - | - |

---

<a id="tr-t8408"></a>
## `t8408` 업종차트(틱/n틱)

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
| `t8408InBlock` | t8408InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n틱) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | 요청건수<br/>압축모듈인 경우 최대 2000건까지 조회가능.<br/>비압축인 경우 최대 500건까지 조회가능 |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | 0:미사용 |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 기본값 : Space<br/>(edate(필수입력) 기준으로 qrycnt 만큼 조회)<br/><br/>조회구간을 설정하여 필터링 하고 싶은 경우 입력 |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회<br/>("99999999" 혹은 '당일') |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | N:비압축 모듈<br/>Y: 압 축 모듈 |


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
| `t8408OutBlock` | t8408OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8408OutBlock1` | t8408OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8408InBlock": {
    "shcode": "001",
    "ncnt": 1,
    "qrycnt": 1,
    "nday": "0",
    "sdate": " ",
    "stime": "",
    "edate": "99999999",
    "etime": "",
    "cts_date": " ",
    "cts_time": "",
    "comp_yn": "N"
  }
}
```

### 응답 Example

```json
{
    "t8408OutBlock1": [
        {
            "date": "20230605",
            "jdiff_vol": 215,
            "high": "2610.85",
            "low": "2610.85",
            "time": "102700",
            "close": "2610.85",
            "open": "2610.85"
        }
    ],
    "rsp_cd": "00000",
    "t8408OutBlock": {
        "cts_date": "20230605",
        "shcode": "001",
        "jivolume": 569620,
        "e_time": "153000",
        "jisiga": "2586.27",
        "jilow": "2583.88",
        "diclose": "2610.85",
        "dshmin": "10",
        "disiga": "2617.43",
        "s_time": "090000",
        "dihigh": "2617.58",
        "jihigh": "2601.38",
        "rec_count": 1,
        "dilow": "2610.40",
        "jiclose": "2601.36",
        "cts_time": "102650"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8409"></a>
## `t8409` 업종차트(N분)

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
| `t8409InBlock` | t8409InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n분) | Number | Y | 4 | 0:30초<br/>1: 1분<br/>2: 2분<br/>.....<br/>n: n분 |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | 요청건수<br/>압축모듈인 경우 최대 2000건까지 조회가능.<br/>비압축인 경우 최대 500건까지 조회가능 |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | 0:미사용 |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 기본값 : Space<br/>(edate(필수입력) 기준으로 qrycnt 만큼 조회)<br/><br/>조회구간을 설정하여 필터링 하고 싶은 경우 입력 |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회<br/>("99999999" 혹은 '당일') |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | N:비압축 모듈<br/>Y: 압 축 모듈 |


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
| `t8409OutBlock` | t8409OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-disvalue` | 당일거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 업종시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 업종종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8409OutBlock1` | t8409OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8409InBlock": {
    "shcode": "001",
    "ncnt": 0,
    "qrycnt": 5,
    "nday": "0",
    "sdate": " ",
    "stime": "",
    "edate": "99999999",
    "etime": "",
    "cts_date": " ",
    "cts_time": "",
    "comp_yn": "N"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8409OutBlock": {
        "cts_date": "20230605",
        "shcode": "001",
        "jivolume": 569620,
        "e_time": "153000",
        "disvalue": 3886266,
        "jisiga": "2586.27",
        "jilow": "2583.88",
        "diclose": "2610.85",
        "dshmin": "10",
        "disiga": "2617.43",
        "s_time": "090000",
        "dihigh": "2617.58",
        "jihigh": "2601.38",
        "rec_count": 5,
        "dilow": "2610.40",
        "jiclose": "2601.36",
        "cts_time": "102300"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t8409OutBlock1": [
        {
            "date": "20230605",
            "jdiff_vol": 1673,
            "high": "2611.59",
            "low": "2610.75",
            "time": "102400",
            "close": "2610.97",
            "value": 19176,
            "open": "2611.42"
        },
        {
            "date": "20230605",
            "jdiff_vol": 1509,
            "high": "2611.75",
            "low": "2610.70",
            "time": "102500",
            "close": "2611.50",
            "value": 15544,
            "open": "2610.70"
        },
        {
            "date": "20230605",
            "jdiff_vol": 1316,
            "high": "2611.97",
            "low": "2610.80",
            "time": "102600",
            "close": "2610.80",
            "value": 18831,
            "open": "2611.97"
        },
        {
            "date": "20230605",
            "jdiff_vol": 1418,
            "high": "2611.45",
            "low": "2610.53",
            "time": "102700",
            "close": "2610.85",
            "value": 15265,
            "open": "2611.30"
        },
        {
            "date": "20230605",
            "jdiff_vol": 0,
            "high": "2610.85",
            "low": "2610.85",
            "time": "102800",
            "close": "2610.85",
            "value": 0,
            "open": "2610.85"
        }
    ]
}
```

---

<a id="tr-t8429"></a>
## `t8429` 업종차트(일주월)

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
| `t8429InBlock` | t8429InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분(2:일3:주4:월) | String | Y | 1 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | 요청건수<br/>압축모듈인 경우 최대 2000건까지 조회가능.<br/>비압축인 경우 최대 500건까지 조회가능 |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 기본값 : Space<br/>(edate(필수입력) 기준으로 qrycnt 만큼 조회)<br/><br/>조회구간을 설정하여 필터링 하고 싶은 경우 입력 |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회<br/>("99999999" 혹은 '당일') |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | N:비압축 모듈<br/>Y: 압 축 모듈 |


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
| `t8429OutBlock` | t8429OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-disvalue` | 당일거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-s_time` | 업종시작시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 업종종료시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8429OutBlock1` | t8429OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8429InBlock": {
    "shcode": "001",
    "gubun": "2",
    "qrycnt": 5,
    "sdate": " ",
    "edate": "99999999",
    "cts_date": " ",
    "comp_yn": "N"
  }
}
```

### 응답 Example

```json
{
    "t8429OutBlock": {
        "cts_date": "20230526",
        "shcode": "001",
        "jivolume": 569620,
        "e_time": "153000",
        "disvalue": 3886266,
        "jisiga": "2586.27",
        "jilow": "2583.88",
        "diclose": "2610.85",
        "dshmin": "10",
        "disiga": "2617.43",
        "s_time": "090000",
        "dihigh": "2617.58",
        "jihigh": "2601.38",
        "rec_count": 5,
        "dilow": "2610.40",
        "jiclose": "2601.36"
    },
    "rsp_cd": "00000",
    "t8429OutBlock1": [
        {
            "date": "20230530",
            "jdiff_vol": 641647,
            "high": "2586.22",
            "low": "2574.82",
            "close": "2585.52",
            "value": 11066254,
            "open": "2582.41"
        },
        {
            "date": "20230531",
            "jdiff_vol": 686187,
            "high": "2596.31",
            "low": "2575.98",
            "close": "2577.12",
            "value": 15135111,
            "open": "2586.03"
        },
        {
            "date": "20230601",
            "jdiff_vol": 675233,
            "high": "2580.15",
            "low": "2565.00",
            "close": "2569.17",
            "value": 9168502,
            "open": "2572.56"
        },
        {
            "date": "20230602",
            "jdiff_vol": 569620,
            "high": "2601.38",
            "low": "2583.88",
            "close": "2601.36",
            "value": 9383535,
            "open": "2586.27"
        },
        {
            "date": "20230605",
            "jdiff_vol": 263380,
            "high": "2617.58",
            "low": "2610.40",
            "close": "2610.85",
            "value": 3886266,
            "open": "2617.43"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
