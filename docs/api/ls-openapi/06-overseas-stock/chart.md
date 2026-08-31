# [해외주식] 차트

> LS증권 OPEN API 정의서 · 그룹: **해외주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=cdb7e1bc-f7c5-425c-8248-aa83dbb6919f&api_id=4903400b-731d-42b0-98c7-6d50fc504894)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `4903400b-731d-42b0-98c7-6d50fc504894` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/overseas-stock/chart` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 해외주식 기간별 차트를 확인할 수 있습니다. |

## TR 목록 (4건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 해외주식 API 일주월 조회 | [g3103](chart.md#tr-g3103) | 1 | 1 | 10 |
| 해외주식 API 차트NTICK 조회 | [g3202](chart.md#tr-g3202) | 1 | 1 | 10 |
| 해외주식 API 차트NMIN 조회 | [g3203](chart.md#tr-g3203) | 1 | 1 | 10 |
| 해외주식 API 차트일주월년별 조회 | [g3204](chart.md#tr-g3204) | 1 | 1 | 10 |

---

<a id="tr-g3103"></a>
## `g3103` 해외주식 API 일주월 조회

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
| `&nbsp;&nbsp;-g3103InBlock` | g3103InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-date` | 조회일자 | String | Y | 8 | - |


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
| `&nbsp;&nbsp;-g3103OutBlock` | g3103OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-date` | 조회일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-g3103OutBlock1` | g3103OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-chedate` | 영업일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Object | Y | 15.6 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-diff` | 전일대비 | Object | Y | 15.6 | - |
| `&nbsp;&nbsp;-rate` | 등락률 | Object | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-open` | 시가 | Object | Y | 15.6 | - |
| `&nbsp;&nbsp;-high` | 고가 | Object | Y | 15.6 | - |
| `&nbsp;&nbsp;-low` | 저가 | Object | Y | 15.6 | - |
| `&nbsp;&nbsp;-floatpoint` | 소숫점자릿수 | String | Y | 1 | - |


### 요청 Example

```json
{
  "g3103InBlock": {
    "delaygb": "R",
    "keysymbol": "82TSLA",
    "exchcd": "82",
    "symbol": "TSLA",
    "gubun": "4",
    "date": "20250120"
  }
}
```

### 응답 Example

```json
{
	"g3103OutBlock": {
		"delaygb": "R",
		"keysymbol": "82TSLA",
		"exchcd": "82",
		"symbol": "TSLA",
		"gubun": "4",
		"date": "20221031"
	},
	"g3103OutBlock1": [
		{
			"chedate": "20250428",
			"price": "283.4300",
			"sign": "2",
			"diff": "24.2700",
			"rate": "9.36",
			"volume": 2568819717,
			"open": "263.8000",
			"high": "286.8500",
			"low": "214.2500",
			"floatpoint": "4"
		},
		{
			"chedate": "20250331",
			"price": "259.1600",
			"sign": "5",
			"diff": "33.8200",
			"rate": "-11.54",
			"volume": 2721582212,
			"open": "300.3400",
			"high": "303.9400",
			"low": "217.0200",
			"floatpoint": "4"
		},
		{
			"chedate": "20250228",
			"price": "292.9800",
			"sign": "5",
			"diff": "111.6200",
			"rate": "-27.59",
			"volume": 1582390013,
			"open": "386.6800",
			"high": "394.0000",
			"low": "273.6000",
			"floatpoint": "4"
		},
		{
			"chedate": "20250131",
			"price": "404.6000",
			"sign": "2",
			"diff": "0.7600",
			"rate": "0.19",
			"volume": 1510656740,
			"open": "390.1000",
			"high": "439.7400",
			"low": "373.0400",
			"floatpoint": "4"
		},
		{
			"chedate": "20241231",
			"price": "403.8400",
			"sign": "2",
			"diff": "58.6800",
			"rate": "17.00",
			"volume": 1903650512,
			"open": "352.3800",
			"high": "488.5399",
			"low": "348.2000",
			"floatpoint": "4"
		},
		{
			"chedate": "20241129",
			"price": "345.1600",
			"sign": "2",
			"diff": "95.3100",
			"rate": "38.15",
			"volume": 2091913770,
			"open": "252.0430",
			"high": "361.9300",
			"low": "238.8800",
			"floatpoint": "4"
		},
		{
			"chedate": "20241031",
			"price": "249.8500",
			"sign": "5",
			"diff": "11.7800",
			"rate": "-4.50",
			"volume": 1910960826,
			"open": "262.6700",
			"high": "273.5360",
			"low": "212.1100",
			"floatpoint": "4"
		},
		{
			"chedate": "20240930",
			"price": "261.6300",
			"sign": "2",
			"diff": "47.5200",
			"rate": "22.19",
			"volume": 1611441082,
			"open": "215.2600",
			"high": "264.8600",
			"low": "209.6400",
			"floatpoint": "4"
		},
		{
			"chedate": "20240830",
			"price": "214.1100",
			"sign": "5",
			"diff": "17.9600",
			"rate": "-7.74",
			"volume": 1618373088,
			"open": "227.6900",
			"high": "231.8670",
			"low": "182.0000",
			"floatpoint": "4"
		},
		{
			"chedate": "20240731",
			"price": "232.0700",
			"sign": "2",
			"diff": "34.1900",
			"rate": "17.28",
			"volume": 2946645956,
			"open": "201.0200",
			"high": "271.0000",
			"low": "200.8500",
			"floatpoint": "4"
		},
		{
			"chedate": "20240628",
			"price": "197.8800",
			"sign": "2",
			"diff": "19.8000",
			"rate": "11.12",
			"volume": 1407037303,
			"open": "178.1300",
			"high": "203.2000",
			"low": "167.4100",
			"floatpoint": "4"
		},
		{
			"chedate": "20240531",
			"price": "178.0800",
			"sign": "5",
			"diff": "5.2000",
			"rate": "-2.84",
			"volume": 1668285761,
			"open": "182.0000",
			"high": "187.5600",
			"low": "167.7500",
			"floatpoint": "4"
		},
		{
			"chedate": "20240430",
			"price": "183.2800",
			"sign": "2",
			"diff": "7.4900",
			"rate": "4.26",
			"volume": 2481733196,
			"open": "176.1700",
			"high": "198.8700",
			"low": "138.8025",
			"floatpoint": "4"
		},
		{
			"chedate": "20240328",
			"price": "175.7900",
			"sign": "5",
			"diff": "26.0900",
			"rate": "-12.92",
			"volume": 1899578482,
			"open": "200.5200",
			"high": "204.5200",
			"low": "160.5100",
			"floatpoint": "4"
		},
		{
			"chedate": "20240229",
			"price": "201.8800",
			"sign": "2",
			"diff": "14.5900",
			"rate": "7.79",
			"volume": 2020188307,
			"open": "188.5000",
			"high": "205.6000",
			"low": "175.0100",
			"floatpoint": "4"
		},
		{
			"chedate": "20240131",
			"price": "187.2900",
			"sign": "5",
			"diff": "61.1900",
			"rate": "-24.63",
			"volume": 2344213702,
			"open": "250.0800",
			"high": "251.2500",
			"low": "180.0600",
			"floatpoint": "4"
		},
		{
			"chedate": "20231229",
			"price": "248.4800",
			"sign": "2",
			"diff": "8.4000",
			"rate": "3.50",
			"volume": 2295511890,
			"open": "233.1400",
			"high": "265.1300",
			"low": "228.2000",
			"floatpoint": "4"
		},
		{
			"chedate": "20231130",
			"price": "240.0800",
			"sign": "2",
			"diff": "39.2400",
			"rate": "19.54",
			"volume": 2652010569,
			"open": "204.0400",
			"high": "252.7500",
			"low": "197.8500",
			"floatpoint": "4"
		},
		{
			"chedate": "20231031",
			"price": "200.8400",
			"sign": "5",
			"diff": "49.3800",
			"rate": "-19.73",
			"volume": 2591243998,
			"open": "244.8100",
			"high": "268.9400",
			"low": "194.0700",
			"floatpoint": "4"
		},
		{
			"chedate": "20230929",
			"price": "250.2200",
			"sign": "5",
			"diff": "7.8600",
			"rate": "-3.05",
			"volume": 2440633653,
			"open": "257.2600",
			"high": "278.9800",
			"low": "234.5800",
			"floatpoint": "4"
		},
		{
			"chedate": "20230831",
			"price": "258.0800",
			"sign": "5",
			"diff": "9.3500",
			"rate": "-3.50",
			"volume": 2503253508,
			"open": "266.2600",
			"high": "266.4700",
			"low": "212.3600",
			"floatpoint": "4"
		},
		{
			"chedate": "20230731",
			"price": "267.4300",
			"sign": "2",
			"diff": "5.6600",
			"rate": "2.16",
			"volume": 2394275082,
			"open": "276.4900",
			"high": "299.2900",
			"low": "254.1200",
			"floatpoint": "4"
		},
		{
			"chedate": "20230630",
			"price": "261.7700",
			"sign": "2",
			"diff": "57.8400",
			"rate": "28.36",
			"volume": 3443091887,
			"open": "202.5900",
			"high": "276.9900",
			"low": "199.3700",
			"floatpoint": "4"
		},
		{
			"chedate": "20230531",
			"price": "203.9300",
			"sign": "2",
			"diff": "39.6200",
			"rate": "24.11",
			"volume": 2682606426,
			"open": "163.1700",
			"high": "204.4800",
			"low": "158.8300",
			"floatpoint": "4"
		},
		{
			"chedate": "20230428",
			"price": "164.3100",
			"sign": "5",
			"diff": "43.1500",
			"rate": "-20.80",
			"volume": 2505176293,
			"open": "199.9100",
			"high": "202.6897",
			"low": "152.3700",
			"floatpoint": "4"
		},
		{
			"chedate": "20230331",
			"price": "207.4600",
			"sign": "2",
			"diff": "1.7500",
			"rate": "0.85",
			"volume": 3312555115,
			"open": "206.2100",
			"high": "207.7900",
			"low": "163.9100",
			"floatpoint": "4"
		},
		{
			"chedate": "20230228",
			"price": "205.7100",
			"sign": "2",
			"diff": "32.4900",
			"rate": "18.76",
			"volume": 3625947459,
			"open": "173.8900",
			"high": "217.6500",
			"low": "169.9300",
			"floatpoint": "4"
		},
		{
			"chedate": "20230131",
			"price": "173.2200",
			"sign": "2",
			"diff": "50.0400",
			"rate": "40.62",
			"volume": 3897499392,
			"open": "118.4700",
			"high": "180.6800",
			"low": "101.8100",
			"floatpoint": "4"
		},
		{
			"chedate": "20221230",
			"price": "123.1800",
			"sign": "5",
			"diff": "71.5200",
			"rate": "-36.73",
			"volume": 2944247785,
			"open": "197.0800",
			"high": "198.9200",
			"low": "108.2400",
			"floatpoint": "4"
		},
		{
			"chedate": "20221130",
			"price": "194.7000",
			"sign": "5",
			"diff": "32.8400",
			"rate": "-14.43",
			"volume": 1885408367,
			"open": "234.0500",
			"high": "237.3951",
			"low": "166.1850",
			"floatpoint": "4"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-g3202"></a>
## `g3202` 해외주식 API 차트NTICK 조회

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
| `&nbsp;&nbsp;-g3202InBlock` | g3202InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n틱) | Object | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:5 | Object | Y | 4 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_seq` | 연속시퀀스 | Object | Y | 17 | - |


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
| `&nbsp;&nbsp;-g3202OutBlock` | g3202OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-cts_seq` | 연속시퀀스 | Object | Y | 17 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Object | Y | 7 | - |
| `&nbsp;&nbsp;-preopen` | 전일시가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-prehigh` | 전일고가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-prelow` | 전일저가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-preclose` | 전일종가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-prevolume` | 전일거래량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-open` | 당일시가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-high` | 당일고가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-low` | 당일저가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-close` | 당일종가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-last_count` | 마지막Tick건수 | String | Y | 4 | - |
| `&nbsp;&nbsp;-timediff` | 시차 | String | Y | 4 | - |
| `&nbsp;&nbsp;-prtt_rate` | 수정비율 | Object | Y | 6.2 | - |
| `&nbsp;&nbsp;-g3202OutBlock1` | g3202OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-loctime` | 현지시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-exevol` | 체결량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Object | Y | 13 | - |
| `&nbsp;&nbsp;-pricechk` | 수정주가반영항목 | Object | Y | 13 | - |
| `&nbsp;&nbsp;-sign` | 종가등락구분(1:상한2:상승3:보합 | String | Y | 1 | - |


### 요청 Example

```json
{
  "g3202InBlock": {
    "delaygb": "R",
    "keysymbol": "82TSLA",
    "exchcd": "82",
    "symbol": "TSLA",
    "ncnt": 5,
    "qrycnt":5,
    "comp_yn": "N",
    "sdate": "20250414",
    "edate": ""

  }
}
```

### 응답 Example

```json
{
	"g3202OutBlock": {
		"delaygb": "R",
		"keysymbol": "82TSLA",
		"exchcd": "82",
		"symbol": "TSLA",
		"cts_seq": 20250428014650000,
		"rec_count": 5,
		"preopen": "261.6900",
		"prehigh": "286.8500",
		"prelow": "259.6300",
		"preclose": "284.9500",
		"prevolume": 167560688,
		"open": "285.0900",
		"high": "285.3100",
		"low": "281.8400",
		"close": "283.1300",
		"s_time": "200000",
		"e_time": "180000",
		"last_count": "",
		"timediff": "-13"
	},
	"g3202OutBlock1": [
		{
			"date": "20250428",
			"loctime": "014721",
			"open": "283.1600",
			"high": "283.1600",
			"low": "283.1000",
			"close": "283.1000",
			"exevol": 25,
			"jongchk": 0,
			"prtt_rate": "0",
			"pricechk": 0,
			"sign": "5"
		},
		{
			"date": "20250428",
			"loctime": "014730",
			"open": "283.1000",
			"high": "283.1200",
			"low": "283.0200",
			"close": "283.1200",
			"exevol": 111,
			"jongchk": 0,
			"prtt_rate": "0",
			"pricechk": 0,
			"sign": "5"
		},
		{
			"date": "20250428",
			"loctime": "014739",
			"open": "283.0500",
			"high": "283.0500",
			"low": "283.0200",
			"close": "283.0500",
			"exevol": 340,
			"jongchk": 0,
			"prtt_rate": "0",
			"pricechk": 0,
			"sign": "5"
		},
		{
			"date": "20250428",
			"loctime": "014739",
			"open": "283.0300",
			"high": "283.1200",
			"low": "283.0300",
			"close": "283.1200",
			"exevol": 435,
			"jongchk": 0,
			"prtt_rate": "0",
			"pricechk": 0,
			"sign": "5"
		},
		{
			"date": "20250428",
			"loctime": "014743",
			"open": "283.1200",
			"high": "283.1300",
			"low": "283.0200",
			"close": "283.1300",
			"exevol": 307,
			"jongchk": 0,
			"prtt_rate": "0",
			"pricechk": 0,
			"sign": "5"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-g3203"></a>
## `g3203` 해외주식 API 차트NMIN 조회

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
| `g3203InBlock` | g3203InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n분) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:5 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 6 | - |


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
| `g3203OutBlock` | g3203OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `&nbsp;&nbsp;-preopen` | 전일시가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-prehigh` | 전일고가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-prelow` | 전일저가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-preclose` | 전일종가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-prevolume` | 전일거래량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-open` | 당일시가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-high` | 당일고가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-low` | 당일저가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-close` | 당일종가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-timediff` | 시차 | String | Y | 4 | - |
| `g3203OutBlock1` | g3203OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-loctime` | 현지시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 15.8 | - |
| `&nbsp;&nbsp;-exevol` | 체결량 | Number | Y | 16 | - |
| `&nbsp;&nbsp;-amount` | 거래대금 | Number | Y | 16 | - |


### 요청 Example

```json
{
  "g3203InBlock": {
    "delaygb": "R",
    "keysymbol": "82TSLA",
    "exchcd": "82",
    "symbol": "TSLA",
    "ncnt": 10,
    "qrycnt":5,
    "comp_yn": "N",
    "sdate": "20250414",
    "edate": ""

  }
}
```

### 응답 Example

```json
{
	"g3203OutBlock": {
		"delaygb": "R",
		"keysymbol": "82TSLA",
		"exchcd": "82",
		"symbol": "TSLA",
		"cts_date": "20250428",
		"cts_time": "010000",
		"rec_count": 5,
		"preopen": "261.6900",
		"prehigh": "286.8500",
		"prelow": "259.6300",
		"preclose": "284.9500",
		"prevolume": 167560688,
		"open": "285.0900",
		"high": "285.3100",
		"low": "281.8400",
		"close": "283.4900",
		"s_time": "200000",
		"e_time": "180000",
		"timediff": "-13"
	},
	"g3203OutBlock1": [
		{
			"date": "20250428",
			"loctime": "011000",
			"open": "282.3600",
			"high": "282.8300",
			"low": "282.3200",
			"close": "282.8000",
			"exevol": 8016,
			"amount": 0
		},
		{
			"date": "20250428",
			"loctime": "012000",
			"open": "282.8200",
			"high": "283.5500",
			"low": "282.8000",
			"close": "283.5500",
			"exevol": 13514,
			"amount": 0
		},
		{
			"date": "20250428",
			"loctime": "013000",
			"open": "283.5000",
			"high": "283.8000",
			"low": "283.4300",
			"close": "283.7500",
			"exevol": 9463,
			"amount": 0
		},
		{
			"date": "20250428",
			"loctime": "014000",
			"open": "283.7100",
			"high": "283.9500",
			"low": "283.4300",
			"close": "283.9500",
			"exevol": 10848,
			"amount": 0
		},
		{
			"date": "20250428",
			"loctime": "015000",
			"open": "283.9000",
			"high": "284.0500",
			"low": "283.0200",
			"close": "283.4900",
			"exevol": 17615,
			"amount": 0
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-g3204"></a>
## `g3204` 해외주식 API 차트일주월년별 조회

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
| `&nbsp;&nbsp;-g3204InBlock` | g3204InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-sujung` | 수정주가여부(Y:적용N:비적용) | String | Y | 1 | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분(5:년) | String | Y | 1 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:5 | Object | Y | 4 | - |
| `&nbsp;&nbsp;-comp_yn` | 압축여부(Y:압축N:비압축) | String | Y | 1 | - |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_info` | 연속정보 | String | Y | 6 | - |


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
| `&nbsp;&nbsp;-g3204OutBlock` | g3204OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-delaygb` | 지연구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-keysymbol` | KEY종목코드 | String | Y | 18 | - |
| `&nbsp;&nbsp;-exchcd` | 거래소코드 | String | Y | 2 | - |
| `&nbsp;&nbsp;-symbol` | 종목코드 | String | Y | 16 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_info` | 연속정보 | String | Y | 6 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Object | Y | 7 | - |
| `&nbsp;&nbsp;-preopen` | 전일시가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-prehigh` | 전일고가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-prelow` | 전일저가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-preclose` | 전일종가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-prevolume` | 전일거래량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-open` | 당일시가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-high` | 당일고가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-low` | 당일저가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-close` | 당일종가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-uplimit` | 상한가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-dnlimit` | 하한가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-g3204OutBlock1` | g3204OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Object | Y | 15.8 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-amount` | 거래대금 | Object | Y | 16 | - |
| `&nbsp;&nbsp;-jongchk` | 수정구분 | Object | Y | 13 | - |
| `&nbsp;&nbsp;-prtt_rate` | 수정비율 | Object | Y | 6.2 | - |
| `&nbsp;&nbsp;-pricechk` | 수정주가반영항목 | Object | Y | 13 | - |
| `&nbsp;&nbsp;-ratevalue` | 수정비율반영거래대금 | Object | Y | 12 | - |
| `&nbsp;&nbsp;-sign` | 종가등락구분(1:상한2:상승3:보합 | String | Y | 1 | - |


### 요청 Example

```json
{
  "g3204InBlock": {
    "delaygb": "R",
    "keysymbol": "82TSLA",
    "exchcd": "82",
    "symbol": "TSLA",
    "gubun": "2",
    "qrycnt":5,
    "comp_yn": "N",
    "sdate": "20250203",
    "edate": ""
  }
}
```

### 응답 Example

```json
{
	"g3204OutBlock": {
		"delaygb": "R",
		"keysymbol": "82TSLA",
		"exchcd": "82",
		"symbol": "TSLA",
		"cts_date": "20250421",
		"cts_info": "999999",
		"rec_count": 5,
		"preopen": "0",
		"prehigh": "0",
		"prelow": "0",
		"preclose": "0",
		"prevolume": 0,
		"open": "0",
		"high": "0",
		"low": "0",
		"close": "0",
		"uplimit": "0",
		"dnlimit": "0",
		"s_time": "200000",
		"e_time": "180000",
		"dshmin": ""
	},
	"g3204OutBlock1": [
		{
			"date": "20250422",
			"open": "230.9600",
			"high": "242.7900",
			"low": "229.8501",
			"close": "237.9700",
			"volume": 120858452,
			"amount": 28669416641,
			"jongchk": 0,
			"prtt_rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250423",
			"open": "254.8600",
			"high": "259.4499",
			"low": "244.4300",
			"close": "250.7400",
			"volume": 150381903,
			"amount": 38245448524,
			"jongchk": 0,
			"prtt_rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250424",
			"open": "250.5000",
			"high": "259.5400",
			"low": "249.2000",
			"close": "259.5100",
			"volume": 94464195,
			"amount": 24123135539,
			"jongchk": 0,
			"prtt_rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250425",
			"open": "261.6900",
			"high": "286.8500",
			"low": "259.6300",
			"close": "284.9500",
			"volume": 167560688,
			"amount": 46683748618,
			"jongchk": 0,
			"prtt_rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "2"
		},
		{
			"date": "20250428",
			"open": "285.0900",
			"high": "285.3100",
			"low": "281.8400",
			"close": "283.5000",
			"volume": 434208,
			"amount": 122919696,
			"jongchk": 0,
			"prtt_rate": "0.00",
			"pricechk": 0,
			"ratevalue": 0,
			"sign": "5"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```
