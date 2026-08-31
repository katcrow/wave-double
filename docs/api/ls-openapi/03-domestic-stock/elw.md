# [주식] ELW

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=3d58c125-8b45-46b4-baf2-6f98d0373131)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `3d58c125-8b45-46b4-baf2-6f98d0373131` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/elw` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | ELW 시세 및 종목별정보를 호출하여 ELW 상세정보를 확인할 수 있습니다. |

## TR 목록 (20건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| ELW현재가(시세)조회 | [t1950](elw.md#tr-t1950) | 10 | 10 | 5 |
| ELW시간대별체결조회 | [t1951](elw.md#tr-t1951) | 2 | 2 | 3 |
| ELW일별주가 | [t1954](elw.md#tr-t1954) | 1 | 1 | 3 |
| ELW현재가(확정지급액)조회 | [t1956](elw.md#tr-t1956) | 10 | 10 | 5 |
| ELW종목비교 | [t1958](elw.md#tr-t1958) | 2 | 2 | 5 |
| LP대상종목정보조회 | [t1959](elw.md#tr-t1959) | 2 | 2 | 5 |
| ELW등락율상위 | [t1960](elw.md#tr-t1960) | 2 | 2 | 5 |
| ELW거래량상위 | [t1961](elw.md#tr-t1961) | 2 | 2 | 5 |
| ELW전광판 | [t1964](elw.md#tr-t1964) | 2 | 2 | 5 |
| ELW거래대금상위 | [t1966](elw.md#tr-t1966) | 2 | 2 | 5 |
| ELW지표검색 | [t1969](elw.md#tr-t1969) | 2 | 2 | 3 |
| ELW현재가호가조회 | [t1971](elw.md#tr-t1971) | 10 | 10 | 5 |
| ELW현재가(거래원)조회 | [t1972](elw.md#tr-t1972) | 2 | 2 | 3 |
| ELW시간대별예상체결조회 | [t1973](elw.md#tr-t1973) | 2 | 2 | 3 |
| ELW기초자산동일종목 | [t1974](elw.md#tr-t1974) | 2 | 2 | 3 |
| 기초자산리스트조회 | [t1988](elw.md#tr-t1988) | 2 | 2 | 3 |
| ELW종목조회 | [t8431](elw.md#tr-t8431) | 2 | 2 | 3 |
| 기초자산리스트조회 | [t9905](elw.md#tr-t9905) | 2 | 2 | 5 |
| 만기월조회 | [t9907](elw.md#tr-t9907) | 2 | 2 | 5 |
| ELW마스터조회API용 | [t9942](elw.md#tr-t9942) | 2 | 2 | 3 |

---

<a id="tr-t1950"></a>
## `t1950` ELW현재가(시세)조회

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
| `t1950InBlock` | t1950InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | ELW단축코드 | String | Y | 6 | - |


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
| `t1950OutBlock` | t1950OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-chetime` | 체결시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-avg` | 가중평균 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jvolume` | 전일동시간거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volumechg` | 거래량차 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volumediff` | 거래량차등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-odiff` | 시가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-opentime` | 시가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-hdiff` | 고가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-hightime` | 고가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ldiff` | 저가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-lowtime` | 저가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-high52w` | 52최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high52wdiff` | 52최고가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high52wdate` | 52최고가일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-low52w` | 52최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low52wdiff` | 52최저가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low52wdate` | 52최저가일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-exhratio` | 소진율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-listing` | 상장주식수(천) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-memedan` | 수량단위 | String | Y | 5 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-issueprice` | 발행가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-lastdate` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-capt` | 자본지지 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-egearing` | e.기어링 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-premium` | 프리미엄 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-spread` | 스프레드 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-espread` | 최대스프레드 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-impv` | 내재변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-moneyness` | 상태 | String | Y | 1 | - |
| `&nbsp;&nbsp;-delt` | 델타 | Number | Y | 8.6 | - |
| `&nbsp;&nbsp;-gama` | 감마 | Number | Y | 8.6 | - |
| `&nbsp;&nbsp;-vega` | 베가 | Number | Y | 13.6 | - |
| `&nbsp;&nbsp;-ceta` | 쎄타 | Number | Y | 13.6 | - |
| `&nbsp;&nbsp;-rhox` | 로 | Number | Y | 13.6 | - |
| `&nbsp;&nbsp;-bjandatecnt` | 잔존일수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-mmsdate` | 행사개시일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-mmedate` | 행사종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-payday` | 지급일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-listdate` | 발행일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lpmem` | LP회원사 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_holdvol` | LP보유수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcode` | 기초자산코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bgubun` | 기초자산구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bprice` | 기초자산현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bsign` | 기초자산전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bchange` | 기초자산전일비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bvolume` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-info1` | 락구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info2` | 관리/급등구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info3` | 정지/연장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info4` | 투자/불성실구분 | String | Y | 12 | - |
| `&nbsp;&nbsp;-janginfo` | 장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-basketgb` | 바스켓구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-basketcnt` | 바스켓갯수 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-elwtype` | ELW권리행사방식 | String | Y | 2 | - |
| `&nbsp;&nbsp;-settletype` | ELW결제방법 | String | Y | 2 | - |
| `&nbsp;&nbsp;-lpord` | LP사주문가능여부 | String | Y | 2 | - |
| `&nbsp;&nbsp;-elwdetail` | 권리내용 | String | Y | 100 | - |
| `&nbsp;&nbsp;-valuation` | 만기평가가격방식 | String | Y | 100 | - |
| `t1950OutBlock1` | t1950OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-bskcode` | 기초자산코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bskbno` | 기초자산비율 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-bskprice` | 기초자산현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bsksign` | 기초자산전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bskchange` | 기초자산전일비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bskdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bskvolume` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bskjnilclose` | 기초자산전일종가 | Number | Y | 8 | - |


### 요청 Example

```json
{
   "t1950InBlock" :{
      "shcode" : "52L007"
   }
}
```

### 응답 Example

```json
{
    "t1950OutBlock": {
        "hname": "미래L007삼성전자콜",
        "chetime": "1421418337",
        "price": 50,
        "sign": "5",
        "change": 5,
        "diff": "-9.09",
        "cvolume": 20000,
        "volume": "160020",
        "recprice": 55,
        "avg": 50,
        "jnilvolume": "60320",
        "jvolume": "0",
        "jnilclose": 55,
        "volumechg": "-99700",
        "volumediff": "165.29",
        "open": 55,
        "odiff": "0.00",
        "opentime": "090502",
        "high": 55,
        "hdiff": "0.00",
        "hightime": "090502",
        "low": 50,
        "ldiff": "-9.09",
        "lowtime": "092418",
        "high52w": 70,
        "high52wdiff": "-28.57",
        "high52wdate": "20250527",
        "low52w": 20,
        "low52wdiff": "150.00",
        "low52wdate": "20250527",
        "exhratio": "0.00",
        "listing": "27800",
        "memedan": "00010",
        "vol": "0.58",
        "parity": "104.69",
        "berate": "3.82",
        "gearing": "12.04",
        "elwexec": "57500.00",
        "issueprice": 36,
        "convrate": "0.0100",
        "lastdate": "20250814",
        "capt": "4.10",
        "egearing": "7.96",
        "premium": "3.82",
        "spread": "-0.01",
        "espread": "-0.01",
        "theoryprice": "42.24",
        "impv": "38.29",
        "moneyness": "2",
        "delt": "0.661195",
        "gama": "0.000042",
        "vega": "0.824216",
        "ceta": "-0.484881",
        "rhox": "0.487255",
        "bjandatecnt": 50,
        "mmsdate": "20250819",
        "mmedate": "20250819",
        "payday": "20250821",
        "listdate": "20250115",
        "lpmem": "미래에셋증권",
        "lp_holdvol": "27799970",
        "bcode": "005930",
        "bgubun": "2",
        "bprice": 60200,
        "bsign": "5",
        "bchange": 1100,
        "bdiff": "-1.79",
        "bvolume": "19217977",
        "info1": "",
        "info2": "",
        "info3": "",
        "info4": "",
        "janginfo": "02 01 03",
        "basketgb": "N",
        "basketcnt": 1,
        "elwtype": "01",
        "settletype": "01",
        "lpord": "01",
        "elwdetail": "만기평가가격이 행사가격 초과인 경우, 1워런트당 (만기평가가격-행사가격)*전환비율",
        "valuation": "최종거래일포함 직전 5영업일 종가의 산술평균",
        "value": "8001050"
    },
    "t1950OutBlock1": [
        {
            "bskcode": "005930",
            "bskbno": 0,
            "bskprice": 60200,
            "bsksign": "5",
            "bskchange": 1100,
            "bskdiff": "-1.79",
            "bskvolume": "19217977",
            "bskjnilclose": 61300
        }
    ],
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1951"></a>
## `t1951` ELW시간대별체결조회

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
| `t1951InBlock` | t1951InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | 체결량 > 특이체결량인 종목 |
| `&nbsp;&nbsp;-starttime` | 시작시간 | String | Y | 4 | - |
| `&nbsp;&nbsp;-endtime` | 종료시간 | String | Y | 4 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 8 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |


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
| `t1951OutBlock` | t1951OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 8 | - |
| `t1951OutBlock1` | t1951OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdchecnt` | 매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mschecnt` | 매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-revolume` | 순체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rechecnt` | 순체결건수 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t1951InBlock": {
    "shcode": "58HL94",
    "cvolume": 0,
    "starttime": "0830",
    "endtime": "1600",
    "cts_time": " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1951OutBlock": {
        "cts_time": ""
    },
    "t1951OutBlock1": [
        {
            "change": 60,
            "mdchecnt": 1,
            "sign": "2",
            "rechecnt": -1,
            "diff": "40.00",
            "mschecnt": 0,
            "chetime": "13432468",
            "mdvolume": 30,
            "revolume": -30,
            "cvolume": 30,
            "volume": 30,
            "chdegree": "0.00",
            "price": 210,
            "msvolume": 0
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1954"></a>
## `t1954` ELW일별주가

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
| `t1954InBlock` | t1954InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 사용안함 |
| `&nbsp;&nbsp;-cnt` | 건수 | Number | Y | 3 | 조회개수 |


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
| `t1954OutBlock` | t1954OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-bsjgubun` | 기초자산구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bscode` | 기초자산코드(현물) | String | Y | 6 | - |
| `&nbsp;&nbsp;-bjcode` | 기초자산코드(지수) | String | Y | 3 | - |
| `t1954OutBlock1` | t1954OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bsprice` | 기초자산(현물) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bjprice` | 기초자산(지수) | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-bsign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bschange` | 전일대비(현물) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bjchange` | 전일대비(지수) | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-bdiff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bvolume` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-egearing` | e.기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-premium` | 프리미엄 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-capt` | 자본지지 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-mness` | Moneyness | String | Y | 1 | - |


### 요청 Example

```json
{
  "t1954InBlock": {
    "shcode": "58HL94",
    "date": "",
    "cnt": 100
  }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "t1954OutBlock1": [
        {
            "date": "20230608",
            "bjprice": "0",
            "bsign": "2",
            "bjchange": "0",
            "parity": "171.65",
            "change": 60,
            "bsprice": 38500,
            "sign": "2",
            "diff": "40.00",
            "capt": "-19.80",
            "volume": "000000000030",
            "egearing": "0.73",
            "bvolume": "000013270059",
            "high": 210,
            "bdiff": "15.44",
            "premium": "-14.43",
            "gearing": "3.66",
            "low": 210,
            "bschange": 5150,
            "mness": "2",
            "berate": "-14.43",
            "close": 210,
            "open": 210
        },
        {
            "date": "20230607",
            "bjprice": "0",
            "bsign": "2",
            "bjchange": "0",
            "parity": "148.88",
            "change": 0,
            "bsprice": 33350,
            "sign": "3",
            "diff": "0.00",
            "capt": "-13.30",
            "volume": "000000000000",
            "egearing": "1.78",
            "bvolume": "000002240263",
            "high": 150,
            "bdiff": "1.06",
            "premium": "-10.34",
            "gearing": "4.44",
            "low": 150,
            "bschange": 350,
            "mness": "1",
            "berate": "-10.34",
            "close": 150,
            "open": 150
        },
    "t1954OutBlock": {
        "date": "20230111",
        "bscode": "",
        "bsjgubun": "1",
        "bjcode": ""
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1956"></a>
## `t1956` ELW현재가(확정지급액)조회

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
| `t1956InBlock` | t1956InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |


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
| `t1956OutBlock` | t1956OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-chetime` | 체결시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-avg` | 가중평균 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jvolume` | 전일동시간거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volumechg` | 거래량차 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volumediff` | 거래량차등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-odiff` | 시가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-opentime` | 시가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-hdiff` | 고가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-hightime` | 고가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ldiff` | 저가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-lowtime` | 저가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-high52w` | 52최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high52wdiff` | 52최고가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high52wdate` | 52최고가일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-low52w` | 52최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low52wdiff` | 52최저가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low52wdate` | 52최저가일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-exhratio` | 소진율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-listing` | 상장주식수(천) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-memedan` | 수량단위 | String | Y | 5 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-issueprice` | 발행가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-lastdate` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-capt` | 자본지지 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-egearing` | e.기어링 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-premium` | 프리미엄 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-spread` | 스프레드 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-espread` | 최대스프레드 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-impv` | 내재변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-moneyness` | 상태 | String | Y | 1 | - |
| `&nbsp;&nbsp;-delt` | 델타 | Number | Y | 8.6 | - |
| `&nbsp;&nbsp;-gama` | 감마 | Number | Y | 8.6 | - |
| `&nbsp;&nbsp;-vega` | 베가 | Number | Y | 13.6 | - |
| `&nbsp;&nbsp;-ceta` | 쎄타 | Number | Y | 13.6 | - |
| `&nbsp;&nbsp;-rhox` | 로 | Number | Y | 13.6 | - |
| `&nbsp;&nbsp;-bjandatecnt` | 잔존일수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-mmsdate` | 행사개시일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-mmedate` | 행사종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-payday` | 지급일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-listdate` | 발행일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lpmem` | LP회원사 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_holdvol` | LP보유수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bcode` | 기초자산코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bgubun` | 기초자산구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bprice` | 기초자산현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bsign` | 기초자산전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bchange` | 기초자산전일비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bvolume` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-info1` | 락구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info2` | 관리/급등구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info3` | 정지/연장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info4` | 투자/불성실구분 | String | Y | 12 | - |
| `&nbsp;&nbsp;-janginfo` | 장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-basketgb` | 바스켓구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-basketcnt` | 바스켓갯수 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-elwtype` | ELW권리행사방식 | String | Y | 2 | - |
| `&nbsp;&nbsp;-settletype` | ELW결제방법 | String | Y | 2 | - |
| `&nbsp;&nbsp;-lpord` | LP사주문가능여부 | String | Y | 2 | - |
| `&nbsp;&nbsp;-elwdetail` | 권리내용 | String | Y | 100 | - |
| `&nbsp;&nbsp;-valuation` | 만기평가가격방식 | String | Y | 100 | - |
| `&nbsp;&nbsp;-givemoney` | 확정지급액 | Number | Y | 8.3 | - |
| `&nbsp;&nbsp;-intrns_wth_p2` | 내재가치 | Number | Y | 6.2 | 2026.01.15 16시 이후 적용예정 |
| `t1956OutBlock1` | t1956OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-bskcode` | 기초자산코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bskbno` | 기초자산비율 | Number | Y | 3 | - |
| `&nbsp;&nbsp;-bskprice` | 기초자산현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bsksign` | 기초자산전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bskchange` | 기초자산전일비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bskdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bskvolume` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bskjnilclose` | 기초자산전일종가 | Number | Y | 8 | - |


### 요청 Example

```json
{
   "t1956InBlock" :{
      "shcode" : "52HAAM"
   }
}
```

### 응답 Example

```json
{
    "t1956OutBlock": {
        "hdiff": "0.00",
        "high52wdate": "20230213",
        "bsign": "5",
        "jnilclose": 250,
        "sign": "3",
        "high52w": 330,
        "mmsdate": "20230918",
        "cvolume": 10,
        "elwtype": "01",
        "high": 250,
        "price": 250,
        "impv": "87.44",
        "elwexec": "173500.0",
        "hname": "미래HAAM네이버콜",
        "low52wdiff": "78.57",
        "diff": "0.00",
        "rhox": "1.285828",
        "chetime": "1530301080",
        "basketcnt": 1,
        "volume": "000000002830",
        "egearing": "2.86",
        "bvolume": "000000716792",
        "valuation": "최종거래일포함 직전 5영업일 종가의 산술평균",
        "jnilvolume": "000000000050",
        "mmedate": "20230918",
        "bgubun": "2",
        "low52w": 140,
        "exhratio": "0.00",
        "info1": "",
        "bprice": 200500,
        "info4": "",
        "info3": "",
        "odiff": "-28.00",
        "info2": "",
        "convrate": "0.0050",
        "parity": "115.56",
        "capt": "15.20",
        "bjandatecnt": 99,
        "lastdate": "20230914",
        "ldiff": "-30.00",
        "vol": "0.03",
        "recprice": 250,
        "avg": 177,
        "premium": "11.47",
        "janginfo": "",
        "low": 175,
        "low52wdate": "20230425",
        "payday": "20230920",
        "listing": "000000011200",
        "berate": "11.47",
        "bcode": "035420",
        "high52wdiff": "-24.24",
        "gama": "0.000003",
        "givemoney": "0.000",
        "ceta": "-1.199383",
        "basketgb": "N",
        "volumediff": "5660.0",
        "issueprice": 90,
        "change": 0,
        "delt": "0.714094",
        "espread": "0.00",
        "bchange": 4500,
        "volumechg": "000000002780",
        "opentime": "090935",
        "lowtime": "130819",
        "spread": "0.00",
        "settletype": "01",
        "elwdetail": "만기평가가격이 행사가격 초과인 경우, 1워런트당 (만기평가가격-행사가격)*전환비율",
        "listdate": "20221115",
        "memedan": "00010",
        "bdiff": "-2.20",
        "hightime": "153030",
        "gearing": "4.01",
        "lp_holdvol": "000011170810",
        "lpmem": "미래에셋증권",
        "jvolume": "000000000050",
        "lpord": "01",
        "theoryprice": "157.53",
        "open": 180,
        "moneyness": "2",
        "vega": "1.790751"
    },
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1956OutBlock1": [
        {
            "bskchange": 4500,
            "bskjnilclose": 205000,
            "bskcode": "035420",
            "bskbno": 0,
            "bskprice": 200500,
            "bskvolume": "000000716792",
            "bskdiff": "-2.20",
            "bsksign": "5"
        }
    ]
}
```

---

<a id="tr-t1958"></a>
## `t1958` ELW종목비교

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
| `t1958InBlock` | t1958InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode1` | 종목코드1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-shcode2` | 종목코드2 | String | Y | 6 | - |


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
| `t1958OutBlock` | t1958OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-item1` | 기초자산 | String | Y | 12 | - |
| `&nbsp;&nbsp;-issuernmk` | 발행사 | String | Y | 40 | - |
| `&nbsp;&nbsp;-elwopt` | 콜풋구분 | String | Y | 2 | - |
| `&nbsp;&nbsp;-elwtype` | 행사방식 | String | Y | 2 | - |
| `&nbsp;&nbsp;-settletype` | 결제방법 | String | Y | 2 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-listing` | 발행수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mmsdate` | 행사개시일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lastdate` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-nofdays` | 거래잔존일수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-payday` | 지급일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-premium` | 프리미엄 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-capt` | 자본지지 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-egearing` | e.기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-price` | 가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `t1958OutBlock1` | t1958OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-item1` | 기초자산 | String | Y | 12 | - |
| `&nbsp;&nbsp;-issuernmk` | 발행사 | String | Y | 40 | - |
| `&nbsp;&nbsp;-elwopt` | 콜풋구분 | String | Y | 2 | - |
| `&nbsp;&nbsp;-elwtype` | 행사방식 | String | Y | 2 | - |
| `&nbsp;&nbsp;-settletype` | 결제방법 | String | Y | 2 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-listing` | 발행수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mmsdate` | 행사개시일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lastdate` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-nofdays` | 거래잔존일수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-payday` | 지급일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-premium` | 프리미엄 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-capt` | 자본지지 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-egearing` | e.기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-price` | 가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `t1958OutBlock2` | t1958OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-hnamecmp` | 종목명비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-item1cmp` | 기초자산비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-issuernmkcmp` | 발행사비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-elwoptcmp` | 콜풋구분비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-elwtypecmp` | 행사방식비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-settlecmp` | 결제방법비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-elwexeccmp` | 행사가비교 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-convcmp` | 전환비율비교 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-listingcmp` | 발행수량비교 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mmsdatecmp` | 행사개시일비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-lastdatecmp` | 최종거래일비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-nofdayscmp` | 거래잔존일수비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-paydaycmp` | 지급일비교 | String | Y | 6 | - |
| `&nbsp;&nbsp;-paritycmp` | 패리티비교 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-premiumcmp` | 프리미엄비교 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-beratecmp` | 손익분기비교 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-captcmp` | 자본지지비교 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gearingcmp` | 기어링비교 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-egearingcmp` | e.기어링비교 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-pricecmp` | 가격비교 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volumecmp` | 거래량비교 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diffcmp` | 등락율비교 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
   "t1958InBlock" :{
      "shcode1" : "52HAAM",
      "shcode2" : "52HAAA"
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1958OutBlock1": {
        "elwopt": "01",
        "issuernmk": "미래에셋증권 주식회사",
        "item1": "KR7015760002",
        "convrate": "0.0500",
        "parity": "102.16",
        "diff": "5.26",
        "mmsdate": "20230918",
        "capt": "9.10",
        "elwtype": "01",
        "lastdate": "20230914",
        "settletype": "01",
        "egearing": "5.78",
        "volume": "000000000090",
        "premium": "8.23",
        "gearing": "9.65",
        "price": 100,
        "payday": "20230920",
        "elwexec": "18900.00",
        "listing": "000008200000",
        "berate": "8.23",
        "hname": "미래HAAA한국전력콜",
        "nofdays": 70
    },
    "t1958OutBlock": {
        "elwopt": "01",
        "issuernmk": "미래에셋증권 주식회사",
        "item1": "KR7035420009",
        "convrate": "0.0050",
        "parity": "115.56",
        "diff": "0.00",
        "mmsdate": "20230918",
        "capt": "15.20",
        "elwtype": "01",
        "lastdate": "20230914",
        "settletype": "01",
        "egearing": "2.86",
        "volume": "000000002830",
        "premium": "11.47",
        "gearing": "4.01",
        "price": 250,
        "payday": "20230920",
        "elwexec": "173500.0",
        "listing": "000011200000",
        "berate": "11.47",
        "hname": "미래HAAM네이버콜",
        "nofdays": 70
    },
    "rsp_msg": "조회완료",
    "t1958OutBlock2": {
        "settlecmp": "동  일",
        "beratecmp": "3.24",
        "pricecmp": 150,
        "premiumcmp": "3.24",
        "diffcmp": "-5.26",
        "paritycmp": "13.40",
        "volumecmp": "000000002740",
        "convcmp": "0.0000",
        "captcmp": "6.10",
        "nofdayscmp": "동  일",
        "elwoptcmp": "동  일",
        "hnamecmp": "불일치",
        "listingcmp": "000003000000",
        "issuernmkcmp": "동  일",
        "egearingcmp": "-2.92",
        "mmsdatecmp": "동  일",
        "item1cmp": "불일치",
        "elwtypecmp": "동  일",
        "elwexeccmp": "154600.0",
        "paydaycmp": "동  일",
        "gearingcmp": "-5.64",
        "lastdatecmp": "동  일"
    }
}
```

---

<a id="tr-t1959"></a>
## `t1959` LP대상종목정보조회

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
| `t1959InBlock` | t1959InBlock | Object | Y | - | - |
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
| `t1959OutBlock1` | t1959OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-price` | 현재가 | String | Y | 12 | - |
| `&nbsp;&nbsp;-sign` | 부호 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | String | Y | 12 | - |
| `&nbsp;&nbsp;-rate` | 등락율 | Number | Y | 5.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | String | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | String | Y | 12 | - |
| `&nbsp;&nbsp;-lp_gb` | LP주문가능여부 | String | Y | 4 | - |
| `&nbsp;&nbsp;-lp_mem_nm1` | LP회원사명1 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_mem_nm2` | LP회원사명2 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_mem_nm3` | LP회원사명3 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_mem_nm4` | LP회원사명4 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_mem_nm5` | LP회원사명5 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_min_qty` | LP최소호가수량 | String | Y | 10 | - |
| `&nbsp;&nbsp;-lp_st_date` | LP시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lp_end_date` | LP종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lp_spread` | LP스프레드 | Number | Y | 5.2 | - |


### 요청 Example

```json
{
  "t1959InBlock": {
    "shcode": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1959OutBlock1": [
        {
            "lp_spread": "4.00",
            "lp_mem_nm1": "교보증권",
            "lp_min_qty": "0000000000",
            "lp_mem_nm3": "미래에셋증권",
            "shcode": "000250",
            "change": "-00000000200",
            "lp_mem_nm2": "신한투자",
            "sign": "5",
            "volume": "000000097361",
            "lp_gb": "가능",
            "rate": "-0.32",
            "lp_st_date": "20230102",
            "price": "000000061900",
            "lp_mem_nm5": "NH투자증권\u0000？",
            "lp_mem_nm4": "신영증권\u0000超？",
            "lp_end_date": "20231228",
            "value": "006010435800",
            "hname": "삼천당제약"
        },
        {
            "lp_spread": "4.00",
            "lp_mem_nm1": "한국IMC",
            "lp_min_qty": "0000000000",
            "lp_mem_nm3": "",
            "shcode": "088390",
            "change": "-00000000150",
            "lp_mem_nm2": "",
            "sign": "5",
            "volume": "000000019443",
            "lp_gb": "가능",
            "rate": "-0.42",
            "lp_st_date": "20230102",
            "price": "000000035950",
            "lp_mem_nm5": "",
            "lp_mem_nm4": "",
            "lp_end_date": "20231228",
            "value": "000704468650",
            "hname": "이녹스"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1960"></a>
## `t1960` ELW등락율상위

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
| `t1960InBlock` | t1960InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 상승하락(0:상승1:하락) | String | Y | 1 | 0:상승율 1:하락율 |
| `&nbsp;&nbsp;-ggubun` | 권리유형구분(00:EX01:콜02:풋'':전체) | String | Y | 2 | @콜/풋/EX 01@콜 02@풋 00@EX |
| `&nbsp;&nbsp;-itemcode` | 기초자산종목 | String | Y | 12 | 기초자산 종목코드 - 스페이스:전체 - basket:BASKET 기초자산 종목 - 종목코드(12자리 표준코드) |
| `&nbsp;&nbsp;-lastdate` | 조회만기일 | String | Y | 8 | YYYYMM 스페이스:전체 |
| `&nbsp;&nbsp;-exgubun` | 대상제외 | String | Y | 6 | 1번째Byte > '0' : 결제제외 - 현금결제 2번째Byte > '0' : 결제제외 - 실물결제 3번재Byte > '0' : 권리행사방식- 유럽형 제외 4번째Byte > '0' : 권리행사방식- 미국형 제외 5번째Byte 1 : 비표준형 제외 2 : 표준형 제외 3 : 비표준형, 표준형 제외 4 : 디지털형 제외 5 : 비표준형, 디지털형 제외 6 : 표준형, 디지털형 제외 7 : 비표준형, 표준형 디지털형 제외 6번째Byte > '0' : Basket종목 제외 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-sjanday` | 잔존시작일수 | Number | Y | 8 | 잔존일수 >= sjanday |
| `&nbsp;&nbsp;-ejanday` | 잔존종료일수 | Number | Y | 8 | 잔존일수 <= ejanday |
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
| `t1960OutBlock` | t1960OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1960OutBlock1` | t1960OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-lastdate` | 만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-itemcode` | 기초자산종목코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-itemshcode` | 기초자산단축코드 | String | Y | 9 | - |
| `&nbsp;&nbsp;-itemname` | 기초자산종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-itemprice` | 기초자산현재가 | String | Y | 10 | - |
| `&nbsp;&nbsp;-itemsign` | 기초자산대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-itemchange` | 기초자산전일대비 | String | Y | 10 | - |
| `&nbsp;&nbsp;-itemdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-elwshcode` | ELW종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bepoint` | 손익분기점 | Number | Y | 12.2 | - |


### 요청 Example

```json
{
  "t1960InBlock": {
    "gubun": "0",
    "ggubun": "01",
    "itemcode": "",
    "lastdate": "",
    "exgubun": "0",
    "sprice": 0,
    "eprice": 0,
    "volume": 0,
    "sjanday": 0,
    "ejanday": 0,
    "idx": 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1960OutBlock1": [
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 875,
            "sign": "2",
            "diff": "150.86",
            "itemsign": "2",
            "lastdate": "20230914",
            "itemdiff": "0.25",
            "volume": "000000000100",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 1455,
            "itemcode": "101K2G01P",
            "bepoint": "352.05",
            "itemprice": "343.51",
            "elwshcode": "57HAFG",
            "elwexec": "337.50",
            "hname": "한국HAFGKOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 5,
            "sign": "2",
            "diff": "100.00",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000000669890",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 10,
            "itemcode": "101K2G01P",
            "bepoint": "352.60",
            "itemprice": "343.51",
            "elwshcode": "57HS69",
            "elwexec": "352.50",
            "hname": "한국HS69KOSPI200콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "아모레퍼시픽",
            "change": 5,
            "sign": "2",
            "diff": "100.00",
            "itemsign": "2",
            "lastdate": "20231214",
            "itemdiff": "2.30",
            "volume": "000000054000",
            "itemshcode": "A09",
            "itemchange": "2,400",
            "price": 10,
            "itemcode": "KR7090430000",
            "bepoint": "168000.00",
            "itemprice": "106,900",
            "elwshcode": "57J743",
            "elwexec": "166000.00",
            "hname": "한국J743아모레콜"
        },
        {
            "convrate": "0.0020",
            "itemname": "현대모비스",
            "change": 10,
            "sign": "2",
            "diff": "66.67",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "0.90",
            "volume": "000000000010",
            "itemshcode": "A01",
            "itemchange": "2,000",
            "price": 25,
            "itemcode": "KR7012330007",
            "bepoint": "238000.00",
            "itemprice": "225,000",
            "elwshcode": "52J654",
            "elwexec": "225500.00",
            "hname": "미래J654모비스콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "SK이노베이션",
            "change": 45,
            "sign": "2",
            "diff": "60.00",
            "itemsign": "2",
            "lastdate": "20230914",
            "itemdiff": "0.05",
            "volume": "000000001200",
            "itemshcode": "A09",
            "itemchange": "100",
            "price": 120,
            "itemcode": "KR7096770003",
            "bepoint": "206500.00",
            "itemprice": "198,100",
            "elwshcode": "57J669",
            "elwexec": "182500.00",
            "hname": "한국J669SK이노콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "LG전자",
            "change": 35,
            "sign": "2",
            "diff": "53.85",
            "itemsign": "2",
            "lastdate": "20230914",
            "itemdiff": "3.17",
            "volume": "000000000050",
            "itemshcode": "A06",
            "itemchange": "3,900",
            "price": 100,
            "itemcode": "KR7066570003",
            "bepoint": "135000.00",
            "itemprice": "127,000",
            "elwshcode": "57J899",
            "elwexec": "115000.00",
            "hname": "한국J899엘지전자콜"
        },
        {
            "convrate": "0.0500",
            "itemname": "우리금융지주",
            "change": 10,
            "sign": "2",
            "diff": "50.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "1.09",
            "volume": "000000005010",
            "itemshcode": "A31",
            "itemchange": "130",
            "price": 30,
            "itemcode": "KR7316140003",
            "bepoint": "12800.00",
            "itemprice": "12,020",
            "elwshcode": "52J526",
            "elwexec": "12200.00",
            "hname": "미래J526우리금융콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "롯데케미칼",
            "change": 10,
            "sign": "2",
            "diff": "50.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "4.23",
            "volume": "000000012520",
            "itemshcode": "A01",
            "itemchange": "7,100",
            "price": 30,
            "itemcode": "KR7011170008",
            "bepoint": "196000.00",
            "itemprice": "175,100",
            "elwshcode": "57J696",
            "elwexec": "190000.00",
            "hname": "한국J696롯데케미콜"
        },
        {
            "convrate": "0.0100",
            "itemname": "현대미포조선",
            "change": 40,
            "sign": "2",
            "diff": "50.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "5.71",
            "volume": "000000000040",
            "itemshcode": "A01",
            "itemchange": "4,400",
            "price": 120,
            "itemcode": "KR7010620003",
            "bepoint": "87500.00",
            "itemprice": "81,500",
            "elwshcode": "58J192",
            "elwexec": "75500.00",
            "hname": "KBJ192현대미포콜"
        },
        {
            "convrate": "0.0200",
            "itemname": "삼성엔지니어링",
            "change": 10,
            "sign": "2",
            "diff": "50.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "2.64",
            "volume": "000000000010",
            "itemshcode": "A02",
            "itemchange": "750",
            "price": 30,
            "itemcode": "KR7028050003",
            "bepoint": "31500.00",
            "itemprice": "29,150",
            "elwshcode": "58J209",
            "elwexec": "30000.00",
            "hname": "KBJ209삼성엔지콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "F&F",
            "change": 10,
            "sign": "2",
            "diff": "50.00",
            "itemsign": "5",
            "lastdate": "20230713",
            "itemdiff": "0.38",
            "volume": "000000000010",
            "itemshcode": "A38",
            "itemchange": "500",
            "price": 30,
            "itemcode": "KR7383220001",
            "bepoint": "154500.00",
            "itemprice": "132,300",
            "elwshcode": "58J219",
            "elwexec": "148500.00",
            "hname": "KBJ219에프앤에콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 105,
            "sign": "2",
            "diff": "43.75",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "0.25",
            "volume": "000000007160",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 345,
            "itemcode": "101K2G01P",
            "bepoint": "353.45",
            "itemprice": "343.51",
            "elwshcode": "58J098",
            "elwexec": "350.00",
            "hname": "KBJ098KOSPI200콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "롯데케미칼",
            "change": 15,
            "sign": "2",
            "diff": "42.86",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "4.23",
            "volume": "000000511000",
            "itemshcode": "A01",
            "itemchange": "7,100",
            "price": 50,
            "itemcode": "KR7011170008",
            "bepoint": "188500.00",
            "itemprice": "175,100",
            "elwshcode": "52J290",
            "elwexec": "178500.00",
            "hname": "미래J290롯데케미콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "LG전자",
            "change": 15,
            "sign": "2",
            "diff": "42.86",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "3.17",
            "volume": "000000467250",
            "itemshcode": "A06",
            "itemchange": "3,900",
            "price": 50,
            "itemcode": "KR7066570003",
            "bepoint": "133000.00",
            "itemprice": "127,000",
            "elwshcode": "52J658",
            "elwexec": "123000.00",
            "hname": "미래J658엘지전자콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 695,
            "sign": "2",
            "diff": "40.76",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000000000010",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 2400,
            "itemcode": "101K2G01P",
            "bepoint": "344.00",
            "itemprice": "343.51",
            "elwshcode": "52J536",
            "elwexec": "320.00",
            "hname": "미래J536KOSPI200콜"
        },
        {
            "convrate": "0.0020",
            "itemname": "현대모비스",
            "change": 10,
            "sign": "2",
            "diff": "40.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "0.90",
            "volume": "000000000010",
            "itemshcode": "A01",
            "itemchange": "2,000",
            "price": 35,
            "itemcode": "KR7012330007",
            "bepoint": "240000.00",
            "itemprice": "225,000",
            "elwshcode": "52J229",
            "elwexec": "222500.00",
            "hname": "미래J229모비스콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "롯데케미칼",
            "change": 10,
            "sign": "2",
            "diff": "40.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "4.23",
            "volume": "000000002000",
            "itemshcode": "A01",
            "itemchange": "7,100",
            "price": 35,
            "itemcode": "KR7011170008",
            "bepoint": "201000.00",
            "itemprice": "175,100",
            "elwshcode": "52J532",
            "elwexec": "194000.00",
            "hname": "미래J532롯데케미콜"
        },
        {
            "convrate": "0.0200",
            "itemname": "KB금융",
            "change": 10,
            "sign": "2",
            "diff": "40.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "2.63",
            "volume": "000000121020",
            "itemshcode": "A10",
            "itemchange": "1,250",
            "price": 35,
            "itemcode": "KR7105560007",
            "bepoint": "51750.00",
            "itemprice": "48,700",
            "elwshcode": "52J700",
            "elwexec": "50000.00",
            "hname": "미래J700KB금융콜"
        },
        {
            "convrate": "0.0200",
            "itemname": "KB금융",
            "change": 10,
            "sign": "2",
            "diff": "40.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "2.63",
            "volume": "000000001210",
            "itemshcode": "A10",
            "itemchange": "1,250",
            "price": 35,
            "itemcode": "KR7105560007",
            "bepoint": "53750.00",
            "itemprice": "48,700",
            "elwshcode": "52J701",
            "elwexec": "52000.00",
            "hname": "미래J701KB금융콜"
        },
        {
            "convrate": "0.0200",
            "itemname": "하나금융지주",
            "change": 10,
            "sign": "2",
            "diff": "40.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "1.68",
            "volume": "000000281420",
            "itemshcode": "A08",
            "itemchange": "700",
            "price": 35,
            "itemcode": "KR7086790003",
            "bepoint": "44850.00",
            "itemprice": "42,350",
            "elwshcode": "52J723",
            "elwexec": "43100.00",
            "hname": "미래J723하나금융콜"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1960OutBlock": {
        "idx": 20
    }
}
```

---

<a id="tr-t1961"></a>
## `t1961` ELW거래량상위

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
| `t1961InBlock` | t1961InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 당일전일(0:당일1:전일) | String | Y | 1 | 0:당일 1:전일 |
| `&nbsp;&nbsp;-ggubun` | 권리유형구분(00:EX01:콜02:풋'':전체) | String | Y | 2 | @콜/풋/EX 01@콜 02@풋 00@EX |
| `&nbsp;&nbsp;-itemcode` | 기초자산종목 | String | Y | 12 | 기초자산 표준코드(12자리) |
| `&nbsp;&nbsp;-lastdate` | 조회만기일 | String | Y | 8 | YYYYMMDD |
| `&nbsp;&nbsp;-exgubun` | 대상제외 | String | Y | 6 | 1번째Byte > '0' : 결제제외 - 현금결제 2번째Byte > '0' : 결제제외 - 실물결제 3번재Byte > '0' : 권리행사방식- 유럽형 제외 4번째Byte > '0' : 권리행사방식- 미국형 제외 5번째Byte 1 : 비표준형 제외 2 : 표준형 제외 3 : 비표준형, 표준형 제외 4 : 디지털형 제외 5 : 비표준형, 디지털형 제외 6 : 표준형, 디지털형 제외 7 : 비표준형, 표준형 디지털형 제외 6번째Byte > '0' : Basket종목 제외 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-sjanday` | 잔존시작일수 | Number | Y | 8 | 잔존일수 >= sjanday |
| `&nbsp;&nbsp;-ejanday` | 잔존종료일수 | Number | Y | 8 | 잔존일수 <= ejanday |
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
| `t1961OutBlock` | t1961OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 연속조회키 연속 조회시 이 값을 InBlock의 idx 필드에 넣어준다. |
| `t1961OutBlock1` | t1961OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-lastdate` | 만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-itemcode` | 기초자산종목코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-itemshcode` | 기초자산단축코드 | String | Y | 9 | - |
| `&nbsp;&nbsp;-itemname` | 기초자산종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-itemprice` | 기초자산현재가 | String | Y | 10 | - |
| `&nbsp;&nbsp;-itemsign` | 기초자산대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-itemchange` | 기초자산전일대비 | String | Y | 10 | - |
| `&nbsp;&nbsp;-itemdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-elwshcode` | ELW종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1961InBlock": {
    "gubun": "0",
    "ggubun": "01",
    "itemcode": "",
    "lastdate": "",
    "exgubun": "0",
    "sprice": 0,
    "eprice": 0,
    "volume": 0,
    "sjanday": 0,
    "ejanday": 0,
    "idx": 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1961OutBlock1": [
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 25,
            "sign": "2",
            "diff": "22.73",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000047033630",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 135,
            "jnilvolume": "000041749770",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "57HS72",
            "elwexec": "345.00",
            "hname": "한국HS72KOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 25,
            "sign": "2",
            "diff": "11.36",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000031205250",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 245,
            "jnilvolume": "000081182750",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "57HS73",
            "elwexec": "342.50",
            "hname": "한국HS73KOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000017757300",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 55,
            "jnilvolume": "000010982920",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "57HS71",
            "elwexec": "347.50",
            "hname": "한국HS71KOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 45,
            "sign": "2",
            "diff": "12.16",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000010963170",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 415,
            "jnilvolume": "000098401640",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "57HS74",
            "elwexec": "340.00",
            "hname": "한국HS74KOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 75,
            "sign": "2",
            "diff": "13.51",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000004387580",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 630,
            "jnilvolume": "000033478760",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "57HP64",
            "elwexec": "337.50",
            "hname": "한국HP64KOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 5,
            "sign": "5",
            "diff": "-20.00",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000003463120",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 20,
            "jnilvolume": "000003337900",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "57HS70",
            "elwexec": "350.00",
            "hname": "한국HS70KOSPI200콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 5,
            "sign": "2",
            "diff": "11.11",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000002924110",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 50,
            "jnilvolume": "000003561130",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "52J325",
            "elwexec": "347.50",
            "hname": "미래J325KOSPI200콜"
        },
        {
            "convrate": "0.0020",
            "itemname": "POSCO홀딩스",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "1.33",
            "volume": "000002649540",
            "itemshcode": "A005490",
            "itemchange": "5,000",
            "price": 60,
            "jnilvolume": "000001025480",
            "itemcode": "KR7005490008",
            "itemprice": "381,500",
            "elwshcode": "57J923",
            "elwexec": "368500.00",
            "hname": "한국J923POSCO홀콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000002157320",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 20,
            "jnilvolume": "000002887620",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "52J326",
            "elwexec": "350.00",
            "hname": "미래J326KOSPI200콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "SK",
            "change": 5,
            "sign": "2",
            "diff": "20.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "1.00",
            "volume": "000002043000",
            "itemshcode": "A034730",
            "itemchange": "1,700",
            "price": 30,
            "jnilvolume": "000000000020",
            "itemcode": "KR7034730002",
            "itemprice": "171,300",
            "elwshcode": "58J215",
            "elwexec": "189000.00",
            "hname": "KBJ215SK콜"
        },
        {
            "convrate": "0.0020",
            "itemname": "POSCO홀딩스",
            "change": 10,
            "sign": "2",
            "diff": "28.57",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "1.33",
            "volume": "000001909820",
            "itemshcode": "A005490",
            "itemchange": "5,000",
            "price": 45,
            "jnilvolume": "000000000020",
            "itemcode": "KR7005490008",
            "itemprice": "381,500",
            "elwshcode": "58J302",
            "elwexec": "410500.00",
            "hname": "KBJ302POSCO홀콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "LG전자",
            "change": 10,
            "sign": "2",
            "diff": "20.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "3.17",
            "volume": "000001883340",
            "itemshcode": "A066570",
            "itemchange": "3,900",
            "price": 60,
            "jnilvolume": "000000533850",
            "itemcode": "KR7066570003",
            "itemprice": "127,000",
            "elwshcode": "58J170",
            "elwexec": "123000.00",
            "hname": "KBJ170엘지전자콜"
        },
        {
            "convrate": "0.0100",
            "itemname": "기아",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "itemsign": "2",
            "lastdate": "20230914",
            "itemdiff": "0.59",
            "volume": "000001809480",
            "itemshcode": "A000270",
            "itemchange": "500",
            "price": 40,
            "jnilvolume": "000000369070",
            "itemcode": "KR7000270009",
            "itemprice": "85,700",
            "elwshcode": "57JC39",
            "elwexec": "89000.00",
            "hname": "한국JC39기아콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 10,
            "sign": "2",
            "diff": "9.52",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000001783870",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 115,
            "jnilvolume": "000004006070",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "52J324",
            "elwexec": "345.00",
            "hname": "미래J324KOSPI200콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "LG전자",
            "change": 10,
            "sign": "2",
            "diff": "25.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "3.17",
            "volume": "000001294330",
            "itemshcode": "A066570",
            "itemchange": "3,900",
            "price": 50,
            "jnilvolume": "000000685730",
            "itemcode": "KR7066570003",
            "itemprice": "127,000",
            "elwshcode": "57J895",
            "elwexec": "123000.00",
            "hname": "한국J895엘지전자콜"
        },
        {
            "convrate": "100.0000",
            "itemname": "KOSPI200",
            "change": 20,
            "sign": "2",
            "diff": "9.30",
            "itemsign": "2",
            "lastdate": "20230608",
            "itemdiff": "0.25",
            "volume": "000001244240",
            "itemshcode": "101",
            "itemchange": "0.84",
            "price": 235,
            "jnilvolume": "000003069170",
            "itemcode": "101K2G01P",
            "itemprice": "343.51",
            "elwshcode": "52J323",
            "elwexec": "342.50",
            "hname": "미래J323KOSPI200콜"
        },
        {
            "convrate": "0.0200",
            "itemname": "현대건설",
            "change": 10,
            "sign": "2",
            "diff": "40.00",
            "itemsign": "2",
            "lastdate": "20230713",
            "itemdiff": "3.14",
            "volume": "000001095020",
            "itemshcode": "A000720",
            "itemchange": "1,200",
            "price": 35,
            "jnilvolume": "000000000020",
            "itemcode": "KR7000720003",
            "itemprice": "39,400",
            "elwshcode": "58J205",
            "elwexec": "40800.00",
            "hname": "KBJ205현대건설콜"
        },
        {
            "convrate": "0.0100",
            "itemname": "S-Oil",
            "change": 10,
            "sign": "2",
            "diff": "33.33",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "2.46",
            "volume": "000001081190",
            "itemshcode": "A010950",
            "itemchange": "1,800",
            "price": 40,
            "jnilvolume": "000000080400",
            "itemcode": "KR7010950004",
            "itemprice": "74,900",
            "elwshcode": "52J957",
            "elwexec": "76500.00",
            "hname": "미래J957S-OIL콜"
        },
        {
            "convrate": "0.0050",
            "itemname": "LG전자",
            "change": 15,
            "sign": "2",
            "diff": "33.33",
            "itemsign": "2",
            "lastdate": "20230914",
            "itemdiff": "3.17",
            "volume": "000000990410",
            "itemshcode": "A066570",
            "itemchange": "3,900",
            "price": 60,
            "jnilvolume": "000000697940",
            "itemcode": "KR7066570003",
            "itemprice": "127,000",
            "elwshcode": "57JB70",
            "elwexec": "127000.00",
            "hname": "한국JB70엘지전자콜"
        },
        {
            "convrate": "0.0010",
            "itemname": "LG화학",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "itemsign": "2",
            "lastdate": "20230810",
            "itemdiff": "0.28",
            "volume": "000000984450",
            "itemshcode": "A051910",
            "itemchange": "2,000",
            "price": 40,
            "jnilvolume": "000000091800",
            "itemcode": "KR7051910008",
            "itemprice": "723,000",
            "elwshcode": "52J692",
            "elwexec": "764000.00",
            "hname": "미래J692LG화학콜"
        }
    ],
    "t1961OutBlock": {
        "idx": 20
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1964"></a>
## `t1964` ELW전광판

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
| `t1964InBlock` | t1964InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-item` | 기초자산코드 | String | Y | 12 | 0:전체 basket:기초자산이 BASKET 종목 종목코드(12자리 표준코드) |
| `&nbsp;&nbsp;-issuercd` | 발행사 | String | Y | 12 | 000000000000:전체 발행사코드(3자리) 002 신한금융투자 033 JP모간 004 대신 005 대우 048 SG 030 삼성 006 신영 012 우리투자증권 003 한국 017 현대 049 미래에셋 035 맥쿼리 024 동양 031 동부 056 하나대투 054 노무라 034 KB 투자 067 BNP 파리바 |
| `&nbsp;&nbsp;-lastmonth` | 만기월물 | String | Y | 6 | 전체@000000 |
| `&nbsp;&nbsp;-elwopt` | 콜풋구분 | String | Y | 1 | 전체@0 콜@1 풋@2 |
| `&nbsp;&nbsp;-atmgubun` | 머니구분 | String | Y | 1 | 전체@0 ATM@1 ITM@2 OTM@3 |
| `&nbsp;&nbsp;-elwtype` | 권리행사방식 | String | Y | 2 | 권리전체@00 유럽형@01 미국형@02 |
| `&nbsp;&nbsp;-settletype` | 결제방법 | String | Y | 2 | 결제방법전체@00 현금결제@01 실물결제@02 |
| `&nbsp;&nbsp;-elwexecgubun` | 행사기초자산구분 | String | Y | 1 | 행사가/기초자산가격 검색 적용 여부(1이면 적용) |
| `&nbsp;&nbsp;-fromrat` | 시작비율 | String | Y | 5 | 행사가/기초자산가격 * 100 >= fromrat |
| `&nbsp;&nbsp;-torat` | 종료비율 | String | Y | 5 | 행사가/기초자산가격 * 100 <= torat |
| `&nbsp;&nbsp;-volume` | 거래량 | String | Y | 12 | 거래량 >= volume |


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
| `t1964OutBlock1` | t1964OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | ELW코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-item1` | 기초자산코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-itemnm` | 기초자산명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-issuernmk` | 발행사 | String | Y | 40 | - |
| `&nbsp;&nbsp;-elwopt` | 콜풋구분 | String | Y | 4 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jandatecnt` | 잔존일수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 8.4 | - |
| `&nbsp;&nbsp;-lastdate` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-mmsdate` | 행사개시일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-payday` | 지급일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-listing` | 발행수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-atmgbnm` | 머니구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-preminum` | 프리미엄 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-spread` | 스프래드 | Number | Y | 3.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-capt` | 자본지지율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-egearing` | e기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-itemprice` | 기초자산현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-itemsign` | 기초자산전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-itemchange` | 기초자산전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-itemdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-itemvolume` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-lp_rate` | LP보유비율 | Number | Y | 5.2 | - |
| `&nbsp;&nbsp;-impv` | 내재변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-delta` | 델타 | Number | Y | 10.6 | - |
| `&nbsp;&nbsp;-theta` | 쎄타 | Number | Y | 10.6 | - |


### 요청 Example

```json
{
  "t1964InBlock" : {
    "item" : "KR7035420009",
    "issuercd" : "000000000000",
    "lastmonth" : "202309",
    "elwopt" : "0",
    "atmgubun" : "0",
    "elwtype" : "00",
    "settletype" : "00",
    "elwexecgubun" : "",
    "fromrat" : "",
    "torat" : "",
    "volume" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1964OutBlock1": [
        {
            "elwopt": "CALL",
            "item1": "035420",
            "convrate": "50.0000",
            "parity": "11556.00",
            "itemvolume": 25504,
            "sign": "3",
            "delta": "809886.000000",
            "mmsdate": "20230918",
            "capt": "480.00",
            "theta": "-493644.000000",
            "lastdate": "20230914",
            "lp_rate": "9972.00",
            "itemchange": 1300,
            "price": 175,
            "itemprice": 200500,
            "payday": "20230920",
            "jandatecnt": 92,
            "impv": "3796.00",
            "elwexec": "17350000.00",
            "listing": 11200000,
            "berate": "399.00",
            "hname": "미래HAAM네이버콜",
            "issuernmk": "미래에셋증권 주식회사",
            "shcode": "52HAAM",
            "change": 0,
            "diff": "0.00",
            "atmgbnm": "ATM",
            "itemnm": "NAVER",
            "itemsign": "2",
            "itemdiff": "65.00",
            "spread": "0.00",
            "volume": 0,
            "egearing": "463.00",
            "preminum": "425.00",
            "gearing": "572.00",
            "jnilvolume": 60,
            "theoryprice": "15222.00"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1966"></a>
## `t1966` ELW거래대금상위

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
| `t1966InBlock` | t1966InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 당일전일(0:당일1:전일) | String | Y | 1 | 0:당일 1:전일 |
| `&nbsp;&nbsp;-ggubun` | 권리유형구분(00:EX01:콜02:풋'':전체) | String | Y | 2 | @콜/풋/EX 01@콜 02@풋 00@EX |
| `&nbsp;&nbsp;-itemcode` | 기초자산종목 | String | Y | 12 | 기초자산 표준코드(12자리) |
| `&nbsp;&nbsp;-lastdate` | 조회만기일 | String | Y | 8 | YYYYMMDD |
| `&nbsp;&nbsp;-exgubun` | 대상제외 | String | Y | 6 | 1번째Byte > '0' : 결제제외 - 현금결제 2번째Byte > '0' : 결제제외 - 실물결제 3번재Byte > '0' : 권리행사방식- 유럽형 제외 4번째Byte > '0' : 권리행사방식- 미국형 제외 5번째Byte 1 : 비표준형 제외 2 : 표준형 제외 3 : 비표준형, 표준형 제외 4 : 디지털형 제외 5 : 비표준형, 디지털형 제외 6 : 표준형, 디지털형 제외 7 : 비표준형, 표준형 디지털형 제외 6번째Byte > '0' : Basket종목 제외 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-sjanday` | 잔존시작일수 | Number | Y | 8 | 잔존일수 >= sjanday |
| `&nbsp;&nbsp;-ejanday` | 잔존종료일수 | Number | Y | 8 | 잔존일수 <= ejanday |
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
| `t1966OutBlock` | t1966OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 연속조회키 연속 조회시 이 값을 InBlock의 idx 필드에 넣어준다. |
| `t1966OutBlock1` | t1966OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilvalue` | 전일거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 12.4 | - |
| `&nbsp;&nbsp;-lastdate` | 만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-itemcode` | 기초자산종목코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-itemshcode` | 기초자산단축코드 | String | Y | 9 | - |
| `&nbsp;&nbsp;-itemname` | 기초자산종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-itemprice` | 기초자산현재가 | String | Y | 10 | - |
| `&nbsp;&nbsp;-itemsign` | 기초자산대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-itemchange` | 기초자산전일대비 | String | Y | 10 | - |
| `&nbsp;&nbsp;-itemdiff` | 기초자산등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-elwshcode` | ELW종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1966InBlock": {
    "gubun": "0",
    "ggubun": "01",
    "itemcode": "",
    "lastdate": "",
    "exgubun": "0",
    "sprice": 0,
    "eprice": 0,
    "volume": 0,
    "sjanday": 0,
    "ejanday": 0,
    "idx": 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1966OutBlock1": [
        {
            "convrate": "500.0000",
            "itemname": "한국전력",
            "change": 0,
            "sign": "3",
            "diff": "0.00",
            "itemsign": "3",
            "lastdate": "20230914",
            "itemdiff": "0.00",
            "itemshcode": "A015760",
            "itemchange": "0",
            "price": 100,
            "itemcode": "KR7015760002",
            "jnilvalue": "0",
            "itemprice": "19,080",
            "elwshcode": "52HAAA",
            "elwexec": "1890000.00",
            "value": "0",
            "hname": "미래HAAA한국전력콜"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1966OutBlock": {
        "idx": 20
    }
}
```

---

<a id="tr-t1969"></a>
## `t1969` ELW지표검색

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
| `t1969InBlock` | t1969InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-chkitem` | 기초자산chk구분 | String | Y | 1 | 0:기초자산 검색 안함 1:기초자산 검색 |
| `&nbsp;&nbsp;-cbitem` | 기초자산코드 | String | Y | 12 | 전체''@000000000000 basket:기초자산이 BASKET 종목 종목코드(12자리 표준코드) |
| `&nbsp;&nbsp;-chkissuer` | 발행사chk구분 | String | Y | 1 | 0:발행사 검색 안함 1:발행사 검색 |
| `&nbsp;&nbsp;-cbissuer` | 발행사 | String | Y | 12 | 전체''@000000000000 |
| `&nbsp;&nbsp;-chkcallput` | 권리chk구분 | String | Y | 1 | 0:권리구분 검색 안함 1:권리구분 검색 |
| `&nbsp;&nbsp;-cbcallput` | 권리(call:01.put:02) | String | Y | 2 | 전체@00 콜@01 풋@02 EX@03 |
| `&nbsp;&nbsp;-chkexec` | 행사가chk구분 | String | Y | 1 | 0:행사가/기초자산 비교 검색 안함 1:행사가/기초자산 비교 검색 |
| `&nbsp;&nbsp;-cbexec` | 행사가(>=:1.<=:2) | String | Y | 1 | >=@1 <=@2 |
| `&nbsp;&nbsp;-chktype` | 행사방식chk구분 | String | Y | 1 | 0:행사방식 검색 안함 1:행사방식 검색 |
| `&nbsp;&nbsp;-cbtype` | 행사방식 | String | Y | 2 | 전체@00 유럽형@01 미국형@02 기타@03 |
| `&nbsp;&nbsp;-chksettle` | 결제방법chk구분 | String | Y | 1 | 0:결제방법 검색 안함 1:결제방법 검색 |
| `&nbsp;&nbsp;-cbsettle` | 결제방법 | String | Y | 2 | 전체@00 현금결제@01 실물결제@02 현금+실물@03 |
| `&nbsp;&nbsp;-chklast` | 만기chk구분 | String | Y | 1 | 0:만기월 검색 안함 1:만기월 검색 |
| `&nbsp;&nbsp;-cblast` | 만기월별 | String | Y | 6 | 전체@000000 |
| `&nbsp;&nbsp;-chkelwexec` | 행사가격chk구분 | String | Y | 1 | 0:행사가 검색 안함 1:행사가 검색 |
| `&nbsp;&nbsp;-elwexecs` | 행사가이상 | Number | Y | 10.2 | 행사가 >= elwexecs |
| `&nbsp;&nbsp;-elwexece` | 행사가이하 | Number | Y | 10.2 | 행사가 <= elwexece |
| `&nbsp;&nbsp;-chkvolume` | 거래량chk구분 | String | Y | 1 | 0:거래량 검색 안함 1:거래량 검색 |
| `&nbsp;&nbsp;-volumes` | 거래량이상 | Number | Y | 12 | 거래량 >= volumes |
| `&nbsp;&nbsp;-volumee` | 거래량이하 | Number | Y | 12 | 거래량 <= volumee |
| `&nbsp;&nbsp;-chkrate` | 등락율chk구분 | String | Y | 1 | 0:등락율 검색 안함 1:등락율 검색 |
| `&nbsp;&nbsp;-rates` | 등락율이상 | Number | Y | 6.2 | 등락율 >= rates |
| `&nbsp;&nbsp;-ratee` | 등락율이하 | Number | Y | 6.2 | 등락율 <= ratee |
| `&nbsp;&nbsp;-chkpremium` | 프리미엄chk구분 | String | Y | 1 | 0:프리미엄 검색 안함 1:프리미엄 검색 |
| `&nbsp;&nbsp;-premiums` | 프리미엄이상 | Number | Y | 6.2 | 프리미엄 >= premiums |
| `&nbsp;&nbsp;-premiume` | 프리미엄이하 | Number | Y | 6.2 | 프리미엄 <= premiume |
| `&nbsp;&nbsp;-chkparity` | 패리티chk구분 | String | Y | 1 | 0:패리티 검색 안함 1:패리티 검색 |
| `&nbsp;&nbsp;-paritys` | 패리티이상 | Number | Y | 6.2 | 패리티 >= paritys |
| `&nbsp;&nbsp;-paritye` | 패리티이하 | Number | Y | 6.2 | 패리티 <= paritye |
| `&nbsp;&nbsp;-chkberate` | 손익분기chk구분 | String | Y | 1 | 0:손익분기 검색 안함 1:손익분기 검색 |
| `&nbsp;&nbsp;-berates` | 손익분기이상 | Number | Y | 6.2 | 손익분기 >= berates |
| `&nbsp;&nbsp;-beratee` | 손익분기이하 | Number | Y | 6.2 | 손익분기 <= beratee |
| `&nbsp;&nbsp;-chkcapt` | 자본지지chk구분 | String | Y | 1 | 0:자본지지 검색 안함 1:자본지지 검색 |
| `&nbsp;&nbsp;-capts` | 자본지지이상 | Number | Y | 6.2 | 자본지지 >= capts |
| `&nbsp;&nbsp;-capte` | 자본지지이하 | Number | Y | 6.2 | 자본지지 <= capts |
| `&nbsp;&nbsp;-chkegearing` | e.기어링chk구분 | String | Y | 1 | 0:e.기어링 검색 안함 1:e.기어링 검색 |
| `&nbsp;&nbsp;-egearings` | e.기어링이상 | Number | Y | 6.2 | e.기어링 >= egearings |
| `&nbsp;&nbsp;-egearinge` | e.기어링이하 | Number | Y | 6.2 | e.기어링 <= egearinge |
| `&nbsp;&nbsp;-chkgearing` | 기어링chk구분 | String | Y | 1 | 0:기어링 검색 안함 1:기어링 검색 |
| `&nbsp;&nbsp;-gearings` | 기어링이상 | Number | Y | 6.2 | 기어링 >= gearings |
| `&nbsp;&nbsp;-gearinge` | 기어링이하 | Number | Y | 6.2 | 기어링 <= gearinge |
| `&nbsp;&nbsp;-chkdelta` | 델타chk구분 | String | Y | 1 | 0:델타 검색 안함 1:델타 검색 |
| `&nbsp;&nbsp;-deltas` | 델타이상 | Number | Y | 10.6 | 델타 >= deltas |
| `&nbsp;&nbsp;-deltae` | 델타이하 | Number | Y | 10.6 | 델타 <= deltae |
| `&nbsp;&nbsp;-chktheta` | 쎄타chk구분 | String | Y | 1 | 0:쎄타 검색 안함 1:쎄타 검색 |
| `&nbsp;&nbsp;-thetas` | 쎄타이상 | Number | Y | 10.6 | 쎄타 >= thetas |
| `&nbsp;&nbsp;-thetae` | 쎄타이하 | Number | Y | 10.6 | 쎄타 <= thetas |
| `&nbsp;&nbsp;-chkduedate` | 최종거래일chk구분 | String | Y | 1 | 0:최종거래일 검색 안함 1:최종거래일 검색 |
| `&nbsp;&nbsp;-duedates` | 최종거래일이상 | String | Y | 8 | YYYYMMDD 형식 최종거래일 >= duedates |
| `&nbsp;&nbsp;-duedatee` | 최종거래일이하 | String | Y | 8 | YYYYMMDD 형식 최종거래일 <= duedatee |
| `&nbsp;&nbsp;-onetickgubun` | LP갭1틱 | String | Y | 1 | - |
| `&nbsp;&nbsp;-lp_liquidity` | LP유동성공급 | String | Y | 1 | - |
| `&nbsp;&nbsp;-chklp_code` | LPchk구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-lp_code` | LP회원사코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-chkkoba` | 조기종료chk구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-cbkoba` | 조기종료(0:전체1:KOBA2:KOBA제외) | String | Y | 1 | 전체@0 조기종료만@1 조기종료제외@2 |


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
| `t1969OutBlock` | t1969OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | 종목갯수 | Number | Y | 4 | - |
| `t1969OutBlock1` | t1969OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-issuernmk` | 발행사 | String | Y | 40 | - |
| `&nbsp;&nbsp;-itemcode` | 기초자산코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-cpgubun` | 콜/풋구분 | String | Y | 2 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-elwexec` | 행사가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-item` | 기초자산명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-bprice` | 기초자산가 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-bsign` | 기초전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bchange` | 기초전일대비 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-bdiff` | 기초등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-premium` | 프리미엄 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-parity` | 패리티 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-berate` | 손익분기 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-capt` | 자본지지 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-egearing` | e.기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gearing` | 기어링 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-lastdate` | 최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-delta` | 델타 | Number | Y | 10.6 | - |
| `&nbsp;&nbsp;-theta` | 쎄타 | Number | Y | 10.6 | - |
| `&nbsp;&nbsp;-lpname` | LP회원사 | String | Y | 40 | - |
| `&nbsp;&nbsp;-lphold` | LP보유율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bjandatecnt` | 잔존일수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-convrate` | 전환비율 | Number | Y | 8.4 | - |
| `&nbsp;&nbsp;-tickvalue` | 1틱환산 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-kasis` | 괴리율 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1969InBlock" : {
    "chkitem" : "0",
    "cbitem" : "000000000000",
    "chkissuer" : "0",
    "cbissuer" : "000000000000",
    "chkcallput" : "0",
    "cbcallput" : "00",
    "chkexec" : "0",
    "cbexec" : "1",
    "chktype" : "0",
    "cbtype" : "00",
    "chksettle" : "0",
    "cbsettle" : "00",
    "chklast" : "0",
    "cblast" : "000000",
    "chkelwexec" : "0",
    "elwexecs" : 0.1,
    "elwexece" : 0.1,
    "chkvolume" : "0",
    "volumes" : 0,
    "volumee" : 0,
    "chkrate" : "0",
    "rates" : 0.1,
    "ratee" : 0.1,
    "chkpremium" : "0",
    "premiums" : 0.1,
    "premiume" : 0.1,
    "chkparity" : "0",
    "paritys" : 0.1,
    "paritye" : 0.1,
    "chkberate" : "0",
    "berates" : 0.1,
    "beratee" : 0.1,
    "chkcapt" : "0",
    "capts" : 0.1,
    "capte" : 0.1,
    "chkegearing" : "0",
    "egearings" : 0.1,
    "egearinge" : 0.1,
    "chkgearing" : "0",
    "gearings" : 0.1,
    "gearinge" : 0.1,
    "chkdelta" : "0",
    "deltas" : 0.1,
    "deltae" : 0.1,
    "chktheta" : "0",
    "thetas" : 0.1,
    "thetae" : 0.1,
    "chkduedate" : "0",
    "duedates" : "",
    "duedatee" : "",
    "onetickgubun" : "0",
    "lp_liquidity" : "0",
    "chklp_code" : "0",
    "lp_code" : "052",
    "chkkoba" : "0",
    "cbkoba" : "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "",
    "t1969OutBlock1": [
        {
            "bsign": "2",
            "convrate": "100.0000",
            "parity": "96.40",
            "sign": "5",
            "delta": "0.1597",
            "cpgubun": "01",
            "capt": "4.00",
            "theta": "-7.3883",
            "bjandatecnt": 30,
            "lastdate": "20230713",
            "premium": "4.00",
            "price": 95,
            "kasis": "-34.06",
            "elwexec": "357.50",
            "berate": "4.00",
            "tickvalue": "0.80",
            "hname": "한국HAPNKOSPI200콜",
            "issuernmk": "한국투자증권(주)",
            "item": "KOSPI200",
            "lphold": "13.09",
            "lpname": "한국증권",
            "shcode": "57HAPN",
            "change": 55,
            "diff": "-36.67",
            "bchange": "1.74",
            "volume": "28727650",
            "egearing": "57.95",
            "bdiff": "-0.50",
            "gearing": "362.78",
            "itemcode": "KOSPI200",
            "jnilvolume": "45698060",
            "bprice": "344.65"
        }
    ],
    "rsp_msg": "",
    "t1969OutBlock": {
        "cnt": 1148
    }
}
```

---

<a id="tr-t1971"></a>
## `t1971` ELW현재가호가조회

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
| `t1971InBlock` | t1971InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |


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
| `t1971OutBlock` | t1971OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem1` | LP매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem1` | LP매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha1` | 직전매도대비수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha1` | 직전매수대비수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem2` | LP매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem2` | LP매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha2` | 직전매도대비수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha2` | 직전매수대비수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem3` | LP매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem3` | LP매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha3` | 직전매도대비수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha3` | 직전매수대비수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem4` | LP매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem4` | LP매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha4` | 직전매도대비수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha4` | 직전매수대비수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem5` | LP매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem5` | LP매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha5` | 직전매도대비수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha5` | 직전매수대비수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho6` | 매도호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho6` | 매수호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem6` | 매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem6` | LP매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem6` | 매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem6` | LP매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha6` | 직전매도대비수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha6` | 직전매수대비수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho7` | 매도호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho7` | 매수호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem7` | 매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem7` | LP매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem7` | 매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem7` | LP매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha7` | 직전매도대비수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha7` | 직전매수대비수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho8` | 매도호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho8` | 매수호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem8` | 매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem8` | LP매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem8` | 매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem8` | LP매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha8` | 직전매도대비수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha8` | 직전매수대비수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho9` | 매도호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho9` | 매수호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem9` | 매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem9` | LP매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem9` | 매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem9` | LP매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha9` | 직전매도대비수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha9` | 직전매수대비수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho10` | 매도호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho10` | 매수호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem10` | 매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem10` | LP매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem10` | 매수호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem10` | LP매수호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha10` | 직전매도대비수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha10` | 직전매수대비수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offer` | 매도호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bid` | 매수호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha` | 직전매도대비수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha` | 직전매수대비수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-hotime` | 수신시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-yeprice` | 예상체결가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yevolume` | 예상체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-yesign` | 예상체결전일구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-yechange` | 예상체결전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yediff` | 예상체결등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-tmoffer` | 시간외매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tmbid` | 시간외매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ho_status` | 동시구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-invidx` | ELW권리형태(1:표준2:디지털3:조기종료) | String | Y | 1 | 1:표준<br/>2:디지털<br/>3:조기종료 |
| `&nbsp;&nbsp;-koba_stdprc` | KO베리어 | Number | Y | 12.2 | - |
| `&nbsp;&nbsp;-koba_acc_rt` | KO접근도 | Number | Y | 12.2 | - |
| `&nbsp;&nbsp;-koba_yn` | KO발생여부(Y/N) | String | Y | 1 | Y:Yes<br/>N:No |


### 요청 Example

```json
{
   "t1971InBlock" :{
      "shcode" : "52HAAM"
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1971OutBlock": {
        "offerho4": 0,
        "offerho3": 290,
        "offerho6": 0,
        "offerho5": 0,
        "offerho8": 0,
        "offerho7": 0,
        "koba_yn": "N",
        "offerho9": 0,
        "lp_offerrem6": 0,
        "lp_offerrem5": 0,
        "lp_bidrem10": 0,
        "lp_offerrem8": 0,
        "lp_offerrem7": 0,
        "lp_offerrem2": 0,
        "lp_offerrem1": 0,
        "lp_offerrem4": 0,
        "lp_offerrem3": 0,
        "offer": 1290,
        "price": 250,
        "lp_bidrem2": 0,
        "lp_bidrem3": 0,
        "lp_bidrem1": 0,
        "lp_bidrem6": 0,
        "tmoffer": 0,
        "lp_bidrem7": 0,
        "hname": "미래HAAM네이버콜",
        "offerho2": 260,
        "lp_bidrem4": 0,
        "offerho1": 250,
        "lp_bidrem5": 0,
        "lp_bidrem8": 0,
        "lp_bidrem9": 0,
        "yediff": "0.00",
        "diff": "0.01",
        "prebidcha10": 0,
        "offerho10": 0,
        "yeprice": 250,
        "preoffercha9": 0,
        "preoffercha8": 0,
        "preoffercha7": 0,
        "preoffercha6": 0,
        "preoffercha5": 0,
        "preoffercha4": 0,
        "preoffercha3": 0,
        "bidrem3": 55570,
        "bidrem4": 0,
        "bidrem1": 2000,
        "bidrem2": 5550,
        "low": 175,
        "koba_acc_rt": "0.00",
        "preoffercha2": 0,
        "preoffercha1": 0,
        "bidrem9": 0,
        "bidrem7": 0,
        "bidrem8": 0,
        "bidrem5": 0,
        "invidx": "0",
        "bidrem6": 0,
        "change": 0,
        "tmbid": 0,
        "lp_offerrem9": 0,
        "lp_offerrem10": 0,
        "open": 180,
        "jnilclose": 250,
        "ho_status": "1",
        "sign": "3",
        "koba_stdprc": "0.00",
        "preoffercha": 0,
        "high": 250,
        "hotime": "15303010",
        "yechange": 0,
        "volume": "000000002830",
        "preoffercha10": 0,
        "offerrem2": 500,
        "bidho5": 0,
        "offerrem3": 500,
        "bidho4": 0,
        "offerrem4": 0,
        "bidho7": 0,
        "offerrem5": 0,
        "bidho6": 0,
        "bidho9": 0,
        "bidho8": 0,
        "offerrem1": 290,
        "yevolume": "000000000010",
        "offerrem6": 0,
        "offerrem7": 0,
        "offerrem8": 0,
        "offerrem9": 0,
        "bidho1": 170,
        "bidho3": 5,
        "bidho2": 10,
        "prebidcha": 0,
        "prebidcha2": 0,
        "bidrem10": 0,
        "prebidcha3": 0,
        "prebidcha4": 0,
        "bidho10": 0,
        "prebidcha5": 0,
        "prebidcha6": 0,
        "prebidcha7": 0,
        "prebidcha8": 0,
        "prebidcha9": 0,
        "yesign": "3",
        "offerrem10": 0,
        "bid": 63120,
        "prebidcha1": 0
    }
}
```

---

<a id="tr-t1972"></a>
## `t1972` ELW현재가(거래원)조회

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
| `t1972InBlock` | t1972InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |


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
| `t1972OutBlock` | t1972OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-expcode` | 표준코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 9 | - |
| `&nbsp;&nbsp;-offerno1` | 매도증권사코드1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno1` | 매수증권사코드1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol1` | 총매도수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svol1` | 총매수수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dcha1` | 매도증감1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-scha1` | 매수증감1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ddiff1` | 매도비율1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff1` | 매수비율1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno2` | 매도증권사코드2 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno2` | 매수증권사코드2 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol2` | 총매도수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svol2` | 총매수수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dcha2` | 매도증감2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-scha2` | 매수증감2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ddiff2` | 매도비율2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff2` | 매수비율2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno3` | 매도증권사코드3 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno3` | 매수증권사코드3 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol3` | 총매도수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svol3` | 총매수수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dcha3` | 매도증감3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-scha3` | 매수증감3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ddiff3` | 매도비율3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff3` | 매수비율3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno4` | 매도증권사코드4 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno4` | 매수증권사코드4 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol4` | 총매도수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svol4` | 총매수수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dcha4` | 매도증감4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-scha4` | 매수증감4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ddiff4` | 매도비율4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff4` | 매수비율4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno5` | 매도증권사코드5 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno5` | 매수증권사코드5 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol5` | 총매도수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svol5` | 총매수수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dcha5` | 매도증감5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-scha5` | 매수증감5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ddiff5` | 매도비율5 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff5` | 매수비율5 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-fwdvl` | 외국계매도합계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-fwsvl` | 외국계매수합계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ftradmdcha` | 외국계매도직전대비 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ftradmscha` | 외국계매수직전대비 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-fwddiff` | 외국계매도합계비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-fwsdiff` | 외국계매수합계비율 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
   "t1972InBlock" :{
      "shcode" : "52HAAM"
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1972OutBlock": {
        "offerno2": "한국증",
        "offerno1": "미래에",
        "offerno4": "",
        "offerno3": "",
        "scha4": 0,
        "fwsdiff": "0.00",
        "scha3": 10,
        "offerno5": "",
        "scha2": 0,
        "scha1": 0,
        "scha5": 0,
        "dvol1": 2820,
        "dvol2": 10,
        "dvol3": 0,
        "dvol4": 0,
        "hname": "미래HAAM네이버콜",
        "dvol5": 0,
        "fwsvl": 0,
        "ftradmscha": 0,
        "svol3": 10,
        "svol2": 690,
        "svol1": 2130,
        "ddiff5": "0.00",
        "ddiff4": "0.00",
        "ddiff3": "0.00",
        "ddiff2": "0.35",
        "svol5": 0,
        "ddiff1": "99.65",
        "svol4": 0,
        "bidno1": "미래에",
        "bidno3": "키움증",
        "fwddiff": "0.00",
        "bidno2": "한국증",
        "bidno5": "",
        "bidno4": "",
        "dcha5": 0,
        "sdiff5": "0.00",
        "dcha4": 0,
        "sdiff4": "0.00",
        "dcha3": 0,
        "sdiff3": "0.35",
        "dcha2": 10,
        "sdiff2": "24.38",
        "dcha1": 0,
        "sdiff1": "75.27",
        "ftradmdcha": 0,
        "shcode": "J52HAAM",
        "expcode": "KRA521138CB0",
        "fwdvl": 0
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1973"></a>
## `t1973` ELW시간대별예상체결조회

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
| `t1973InBlock` | t1973InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 8 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |


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
| `t1973OutBlock` | t1973OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 8 | - |
| `t1973OutBlock1` | t1973OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-yeprice` | 예상체결가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yegubun` | 예상체결구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilysign` | 전일종가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilychange` | 전일종가대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yediff` | 예상체결등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-yevolume` | 예상체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ymdvolume` | 예상매도체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ymsvolume` | 예상매수체결량 | Number | Y | 12 | - |


### 요청 Example

```json
{
   "t1973InBlock" :{
      "shcode" : "52HAAM",
      "cts_time" : ""
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1973OutBlock": {
        "cts_time": ""
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1973OutBlock1": [
        {
            "jnilysign": "3",
            "yeprice": 250,
            "jnilychange": 0,
            "yevolume": 10,
            "ymdvolume": 10,
            "yediff": "0.00",
            "ymsvolume": 0,
            "chetime": "15241253",
            "yegubun": ""
        },
        {
            "jnilysign": "3",
            "yeprice": 0,
            "jnilychange": 0,
            "yevolume": 0,
            "ymdvolume": 0,
            "yediff": "-100.0",
            "ymsvolume": 0,
            "chetime": "15202195",
            "yegubun": ""
        },
        {
            "jnilysign": "3",
            "yeprice": 0,
            "jnilychange": 0,
            "yevolume": 0,
            "ymdvolume": 0,
            "yediff": "-100.0",
            "ymsvolume": 0,
            "chetime": "15200024",
            "yegubun": ""
        },
        {
            "jnilysign": "3",
            "yeprice": 0,
            "jnilychange": 0,
            "yevolume": 0,
            "ymdvolume": 0,
            "yediff": "-100.0",
            "ymsvolume": 0,
            "chetime": "08400010",
            "yegubun": ""
        }
    ]
}
```

---

<a id="tr-t1974"></a>
## `t1974` ELW기초자산동일종목

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
| `t1974InBlock` | t1974InBlock | Object | Y | - | - |
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
| `t1974OutBlock` | t1974OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | 종목갯수 | Number | Y | 4 | - |
| `t1974OutBlock1` | t1974OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-cpgubun` | 콜/풋구분 | String | Y | 2 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
   "t1974InBlock" :{
      "shcode" : "52HAAM"
   }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "t1974OutBlock1": [
        {
            "volume": "000000002830",
            "price": 250,
            "shcode": "52HAAM",
            "change": 0,
            "sign": "3",
            "cpgubun": "01",
            "diff": "0.00",
            "hname": "미래HAAM네이버콜"
        },
        {
            "volume": "000000000000",
            "price": 15,
            "shcode": "52HALF",
            "change": 0,
            "sign": "3",
            "cpgubun": "02",
            "diff": "0.00",
            "hname": "미래HALF네이버풋"
        },
        {
            "volume": "000000000000",
            "price": 5,
            "shcode": "52HN68",
            "change": 0,
            "sign": "3",
            "cpgubun": "01",
            "diff": "0.00",
            "hname": "미래HN68네이버콜"
        },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1974OutBlock": {
        "cnt": 76
    }
}
```

---

<a id="tr-t1988"></a>
## `t1988` 기초자산리스트조회

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
| `t1988InBlock` | t1988InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mkt_gb` | 시장구분(0:전체1:코스피2:코스닥) | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-chk_price` | 가격설정(0:전체1:조건설정) | String | Y | 1 | - |
| `&nbsp;&nbsp;-from_price` | 가격1 | String | Y | 12 | - |
| `&nbsp;&nbsp;-to_price` | 가격2 | String | Y | 12 | - |
| `&nbsp;&nbsp;-chk_vol` | 거래량설정(0:전체1:조건설정) | String | Y | 1 | - |
| `&nbsp;&nbsp;-from_vol` | 거래량1 | String | Y | 12 | - |
| `&nbsp;&nbsp;-to_vol` | 거래량2 | String | Y | 12 | - |
| `&nbsp;&nbsp;-chk_rate` | 등락율설정(0:전체1:조건설정) | String | Y | 1 | - |
| `&nbsp;&nbsp;-from_rate` | 등락율1 | Number | Y | 5.2 | - |
| `&nbsp;&nbsp;-to_rate` | 등락율2 | Number | Y | 5.2 | - |
| `&nbsp;&nbsp;-chk_amt` | 거래대금설정(0:전체1:조건설정) | String | Y | 1 | - |
| `&nbsp;&nbsp;-from_amt` | 거래대금1 | String | Y | 12 | - |
| `&nbsp;&nbsp;-to_amt` | 거래대금2 | String | Y | 12 | - |
| `&nbsp;&nbsp;-chk_up` | 양봉설정(0:전체1:조건설정) | String | Y | 1 | - |
| `&nbsp;&nbsp;-chk_down` | 음봉설정(0:전체1:조건설정) | String | Y | 1 | - |


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
| `t1988OutBlock` | t1988OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-ksp_cnt` | 코스피종목건수 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ksd_cnt` | 코스닥종목건수 | String | Y | 4 | - |
| `t1988OutBlock1` | t1988OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 표준코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | String | Y | 12 | - |
| `&nbsp;&nbsp;-sign` | 부호 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | String | Y | 12 | - |
| `&nbsp;&nbsp;-rate` | 등락율 | Number | Y | 5.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량(주) | String | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금(백만) | String | Y | 12 | - |
| `&nbsp;&nbsp;-mkt_gb` | 시장구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jvolume` | 전일동시간대거래량(주) | String | Y | 12 | - |


### 요청 Example

```json
{
  "t1988InBlock" : {
    "mkt_gb" : "0",
    "chk_price" : "0",
    "from_price" : "",
    "to_price" : "",
    "chk_vol" : "0",
    "from_vol" : "",
    "to_vol" : "",
    "chk_rate" : "0",
    "from_rate" : 0.1,
    "to_rate" : 0.1,
    "chk_amt" : "0",
    "from_amt" : "1",
    "to_amt" : "1",
    "chk_up" : "0",
    "chk_down" : "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1988OutBlock": {
        "ksd_cnt": "0005",
        "ksp_cnt": "0058"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1988OutBlock1": [
        {
            "volume": "000000690897",
            "rate": "0.65",
            "price": "000000061900",
            "shcode": "000990",
            "change": "000000000400",
            "sign": "2",
            "expcode": "KR7000990002",
            "jvolume": "000000596189",
            "value": "000000042406",
            "hname": "DB하이텍",
            "mkt_gb": "1"
        },
        {
            "volume": "000000106263",
            "rate": "-1.28",
            "price": "000000130600",
            "shcode": "383220",
            "change": "-00000001700",
            "sign": "5",
            "expcode": "KR7383220001",
            "jvolume": "000000074723",
            "value": "000000013901",
            "hname": "F&F",
            "mkt_gb": "1"
        },
        {
            "volume": "000000317136",
            "rate": "1.43",
            "price": "000000127300",
            "shcode": "329180",
            "change": "000000001800",
            "sign": "2",
            "expcode": "KR7329180004",
            "jvolume": "000000204842",
            "value": "000000040353",
            "hname": "HD현대중공업",
            "mkt_gb": "1"
        }
    ]
}
```

---

<a id="tr-t8431"></a>
## `t8431` ELW종목조회

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
| `t8431InBlock` | t8431InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-dummy` | Dummy | String | Y | 1 | - |


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
| `t8431OutBlock` | t8431OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t8431InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "t8431OutBlock": [
        {
            "recprice": 100,
            "shcode": "52HAAA",
            "jnilclose": 100,
            "uplmtprice": 0,
            "expcode": "KRA521127CB3",
            "hname": "미래HAAA한국전력콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 15,
            "shcode": "52HAAE",
            "jnilclose": 15,
            "uplmtprice": 0,
            "expcode": "KRA521231CB3",
            "hname": "미래HAAELG에너지풋",
            "dnlmtprice": 0
        },
        {
            "recprice": 230,
            "shcode": "52HAAM",
            "jnilclose": 230,
            "uplmtprice": 0,
            "expcode": "KRA521138CB0",
            "hname": "미래HAAM네이버콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 40,
            "shcode": "52HAAZ",
            "jnilclose": 40,
            "uplmtprice": 0,
            "expcode": "KRA521149CB7",
            "hname": "미래HAAZ카카오콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 55,
            "shcode": "52HABA",
            "jnilclose": 55,
            "uplmtprice": 0,
            "expcode": "KRA521150CB5",
            "hname": "미래HABA카카오콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 100,
            "shcode": "52HABB",
            "jnilclose": 100,
            "uplmtprice": 0,
            "expcode": "KRA521151CB3",
            "hname": "미래HABB카카오콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 160,
            "shcode": "52HABJ",
            "jnilclose": 160,
            "uplmtprice": 0,
            "expcode": "KRA521158CB8",
            "hname": "미래HABJSK하이닉콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 220,
            "shcode": "52HABK",
            "jnilclose": 220,
            "uplmtprice": 0,
            "expcode": "KRA521159CB6",
            "hname": "미래HABKSK하이닉콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 185,
            "shcode": "52HABT",
            "jnilclose": 185,
            "uplmtprice": 0,
            "expcode": "KRA521167CB9",
            "hname": "미래HABT현대차콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 55,
            "shcode": "52HABV",
            "jnilclose": 55,
            "uplmtprice": 0,
            "expcode": "KRA521168CB7",
            "hname": "미래HABV현대차콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 135,
            "shcode": "52HACC",
            "jnilclose": 135,
            "uplmtprice": 0,
            "expcode": "KRA521175CB2",
            "hname": "미래HACC기아콜",
            "dnlmtprice": 0
        },
        {
            "recprice": 140,
            "shcode": "52HACD",
            "jnilclose": 140,
            "uplmtprice": 0,
            "expcode": "KRA521176CB0",
            "hname": "미래HACD기아콜",
            "dnlmtprice": 0
        },
```

---

<a id="tr-t9905"></a>
## `t9905` 기초자산리스트조회

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
| `t9905InBlock` | t9905InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-dummy` | DUMMY | String | Y | 1 | - |


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
| `t9905OutBlock1` | t9905OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 표준코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |


### 요청 Example

```json
{
  "t9905InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "t9905OutBlock1": [
        {
            "shcode": "basket",
            "expcode": "basket",
            "hname": "BASKET"
        },
        {
            "shcode": "000990",
            "expcode": "KR7000990002",
            "hname": "DB하이텍"
        },
        {
            "shcode": "383220",
            "expcode": "KR7383220001",
            "hname": "F&F"
        },
        {
            "shcode": "329180",
            "expcode": "KR7329180004",
            "hname": "HD현대중공업"
        },
        {
            "shcode": "011200",
            "expcode": "KR7011200003",
            "hname": "HMM"
        },
        {
            "shcode": "105560",
            "expcode": "KR7105560007",
            "hname": "KB금융"
        },
        {
            "shcode": "101",
            "expcode": "101",
            "hname": "KOSPI200"
        },
        {
            "shcode": "030200",
            "expcode": "KR7030200000",
            "hname": "KT"
        },
```

---

<a id="tr-t9907"></a>
## `t9907` 만기월조회

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
| `t9907InBlock` | t9907InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-dummy` | DUMMY | String | Y | 1 | - |


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
| `t9907OutBlock1` | t9907OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-lastym` | 만기월 | String | Y | 6 | - |
| `&nbsp;&nbsp;-lastnm` | 만기월명 | String | Y | 10 | - |


### 요청 Example

```json
{
  "t9907InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t9907OutBlock1": [
        {
            "lastym": "202306",
            "lastnm": "2023년06월"
        },
        {
            "lastym": "202307",
            "lastnm": "2023년07월"
        },
        {
            "lastym": "202308",
            "lastnm": "2023년08월"
        },
        {
            "lastym": "202309",
            "lastnm": "2023년09월"
        },
        {
            "lastym": "202310",
            "lastnm": "2023년10월"
        },
        {
            "lastym": "202311",
            "lastnm": "2023년11월"
        },
        {
            "lastym": "202312",
            "lastnm": "2023년12월"
        },
        {
            "lastym": "202401",
            "lastnm": "2024년01월"
        },
        {
            "lastym": "202402",
            "lastnm": "2024년02월"
        },
        {
            "lastym": "202403",
            "lastnm": "2024년03월"
        },
        {
            "lastym": "202404",
            "lastnm": "2024년04월"
        },
        {
            "lastym": "202405",
            "lastnm": "2024년05월"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t9942"></a>
## `t9942` ELW마스터조회API용

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
| `t9942InBlock` | t9942InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-dummy` | Dummy | String | Y | 1 | - |


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
| `t9942OutBlock` | t9942OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |


### 요청 Example

```json
{
  "t9942InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t9942OutBlock": [
        {
            "shcode": "52HAAA",
            "expcode": "KRA521127CB3",
            "hname": "미래HAAA한국전력콜"
        },
        {
            "shcode": "52HAAE",
            "expcode": "KRA521231CB3",
            "hname": "미래HAAELG에너지풋"
        },
        {
            "shcode": "52HAAM",
            "expcode": "KRA521138CB0",
            "hname": "미래HAAM네이버콜"
        },
        {
            "shcode": "52HAAZ",
            "expcode": "KRA521149CB7",
            "hname": "미래HAAZ카카오콜"
        },
        {
            "shcode": "52HABA",
            "expcode": "KRA521150CB5",
            "hname": "미래HABA카카오콜"
        },
        {
            "shcode": "52HABB",
            "expcode": "KRA521151CB3",
            "hname": "미래HABB카카오콜"
        },
        {
            "shcode": "52HABJ",
            "expcode": "KRA521158CB8",
            "hname": "미래HABJSK하이닉콜"
        },
```
