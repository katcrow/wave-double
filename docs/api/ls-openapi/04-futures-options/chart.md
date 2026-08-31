# [선물/옵션] 차트

> LS증권 OPEN API 정의서 · 그룹: **선물/옵션** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=2f1eea77-5606-4512-93c6-31b21d2ece90&api_id=a9b39b08-25c2-427d-848b-675c6228a92b)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `a9b39b08-25c2-427d-848b-675c6228a92b` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/futureoption/chart` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 주간/야간 선물옵션 기간별 차트를 확인할 수 있습니다. |

## TR 목록 (5건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 선물옵션틱분별체결조회차트 | [t2216](chart.md#tr-t2216) | 1 | 1 | 3 |
| 선물옵션차트(틱/n틱) | [t8464](chart.md#tr-t8464) | 1 | 1 | 3 |
| 선물/옵션차트(N분) | [t8465](chart.md#tr-t8465) | 1 | 1 | 3 |
| 선물/옵션차트(일주월) | [t8466](chart.md#tr-t8466) | 1 | 1 | 3 |
| KRX야간파생 틱분별조회(API용) | [t8461](chart.md#tr-t8461) | 1 | 1 | 1 |

---

<a id="tr-t2216"></a>
## `t2216` 선물옵션틱분별체결조회차트

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
| `t2216InBlock` | t2216InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cgubun` | 챠트구분 | String | Y | 1 | T:틱차트<br/>B:분차트 |
| `&nbsp;&nbsp;-bgubun` | 분구분 | Object | Y | 3 | 차트구분이 'B'일때만 체크<br/>0: 30초<br/>0초과 : n분 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |


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
| `t2216OutBlock1` | t2216OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-openyak` | 미결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-openupdn` | 미결증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschecnt` | 매수순간체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mdchecnt` | 매도순간체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ss_mschecnt` | 순매수순간체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschevol` | 매수순간체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-s_mdchevol` | 매도순간체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ss_mschevol` | 순매수순간체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-chdegvol` | 체결강도(거래량) | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-chdegcnt` | 체결강도(건수) | Number | Y | 8.2 | - |


### 요청 Example

```json
{
   "t2216InBlock" :{
      "focode" : "A0166000",
      "cgubun" : "T",
      "bgubun" : 0,
      "cnt" : 0
   }
}
```

### 응답 Example

```json
{
	"t2216OutBlock1": [
		{
			"chetime": "154500",
			"price": "973.95",
			"sign": "5",
			"change": "6.00",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "113902",
			"value": "27747090550",
			"openyak": 199879,
			"openupdn": 16,
			"cvolume": 2810,
			"s_mschecnt": 0,
			"s_mdchecnt": 0,
			"ss_mschecnt": 0,
			"s_mschevol": "0",
			"s_mdchevol": "0",
			"ss_mschevol": "0",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153459",
			"price": "974.30",
			"sign": "5",
			"change": "5.65",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111092",
			"value": "27062890675",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153459",
			"price": "974.30",
			"sign": "5",
			"change": "5.65",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111091",
			"value": "27062647100",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153459",
			"price": "974.25",
			"sign": "5",
			"change": "5.70",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111090",
			"value": "27062403525",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "1",
			"ss_mschevol": "-1",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153459",
			"price": "974.25",
			"sign": "5",
			"change": "5.70",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111089",
			"value": "27062159962",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153459",
			"price": "974.05",
			"sign": "5",
			"change": "5.90",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111088",
			"value": "27061916400",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 3,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "3",
			"ss_mschevol": "-3",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153459",
			"price": "974.10",
			"sign": "5",
			"change": "5.85",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111085",
			"value": "27061185862",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "1",
			"ss_mschevol": "-1",
			"chdegvol": "96.24",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153458",
			"price": "974.10",
			"sign": "5",
			"change": "5.85",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111084",
			"value": "27060942337",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "1",
			"ss_mschevol": "-1",
			"chdegvol": "96.25",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153457",
			"price": "974.25",
			"sign": "5",
			"change": "5.70",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111083",
			"value": "27060698812",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 2,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "2",
			"ss_mschevol": "-2",
			"chdegvol": "96.25",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153457",
			"price": "974.25",
			"sign": "5",
			"change": "5.70",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111081",
			"value": "27060211687",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.25",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153457",
			"price": "974.25",
			"sign": "5",
			"change": "5.70",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111080",
			"value": "27059968125",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.25",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153456",
			"price": "974.20",
			"sign": "5",
			"change": "5.75",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111079",
			"value": "27059724562",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.25",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153455",
			"price": "974.15",
			"sign": "5",
			"change": "5.80",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111078",
			"value": "27059481012",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.25",
			"chdegcnt": "94.10"
		},
		{
			"chetime": "153455",
			"price": "974.15",
			"sign": "5",
			"change": "5.80",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111077",
			"value": "27059237475",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.09"
		},
		{
			"chetime": "153455",
			"price": "974.15",
			"sign": "5",
			"change": "5.80",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111076",
			"value": "27058993937",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.09"
		},
		{
			"chetime": "153455",
			"price": "974.15",
			"sign": "5",
			"change": "5.80",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111075",
			"value": "27058750400",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.09"
		},
		{
			"chetime": "153455",
			"price": "974.15",
			"sign": "5",
			"change": "5.80",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111074",
			"value": "27058506862",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.09"
		},
		{
			"chetime": "153455",
			"price": "974.10",
			"sign": "5",
			"change": "5.85",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111073",
			"value": "27058263325",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 1,
			"s_mdchecnt": 0,
			"ss_mschecnt": 1,
			"s_mschevol": "1",
			"s_mdchevol": "0",
			"ss_mschevol": "1",
			"chdegvol": "96.24",
			"chdegcnt": "94.09"
		},
		{
			"chetime": "153455",
			"price": "973.90",
			"sign": "5",
			"change": "6.05",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111072",
			"value": "27058019800",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "1",
			"ss_mschevol": "-1",
			"chdegvol": "96.23",
			"chdegcnt": "94.08"
		},
		{
			"chetime": "153455",
			"price": "973.90",
			"sign": "5",
			"change": "6.05",
			"open": "0",
			"high": "0",
			"low": "0",
			"volume": "111071",
			"value": "27057776325",
			"openyak": 199863,
			"openupdn": 0,
			"cvolume": 1,
			"s_mschecnt": 0,
			"s_mdchecnt": 1,
			"ss_mschecnt": -1,
			"s_mschevol": "0",
			"s_mdchevol": "1",
			"ss_mschevol": "-1",
			"chdegvol": "96.24",
			"chdegcnt": "94.09"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8464"></a>
## `t8464` 선물옵션차트(틱/n틱)

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
| `t8464InBlock` | t8464InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n틱) | Number | Y | 4 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | 요청건수<br/><br/>압축모듈인 경우 최대 2000건까지 조회가능.<br/>비압축인 경우 최대 500건까지 조회가능 |
| `&nbsp;&nbsp;-nday` | 조회영업일수(0:미사용1>=사용) | String | Y | 1 | 0:미사용 |
| `&nbsp;&nbsp;-sdate` | 시작일자 | String | Y | 8 | 기본값 : Space<br/>(edate(필수입력) 기준으로 qrycnt 만큼 조회)<br/><br/>조회구간을 설정하여 필터링 하고 싶은 경우 입력 |
| `&nbsp;&nbsp;-stime` | 시작시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 종료일자 | String | Y | 8 | 처음조회기준일(LE)<br/>처음조회일 경우 이 값 기준으로 조회<br/>("99999999" 혹은 '당일') |
| `&nbsp;&nbsp;-etime` | 종료시간(현재미사용) | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_date 값으로 설정 |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | N:비압축 |
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
| `t8464OutBlock` | t8464OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8464OutBlock1` | t8464OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-openyak` | 미결제약정 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8464InBlock": {
    "shcode": "A1166000",
    "ncnt": 1,
    "qrycnt": 200,
    "nday": "",
    "sdate": "",
    "stime": "",
    "edate": "99999999",
    "etime": "",
    "cts_date": "",
    "cts_time": "",
    "comp_yn": "N"
  }
}
```

### 응답 Example

```json
{
	"t8464OutBlock": {
		"shcode": "A1166000",
		"jisiga": "225500.00",
		"jihigh": "226500.00",
		"jilow": "217500.00",
		"jiclose": "220000.00",
		"jivolume": 42260,
		"disiga": "220500.00",
		"dihigh": "227000.00",
		"dilow": "219500.00",
		"diclose": "225000.00",
		"highend": "242000.00",
		"lowend": "198000.00",
		"cts_date": "20260427",
		"cts_time": "1449341811",
		"s_time": "084500",
		"e_time": "154500",
		"dshmin": "10",
		"rec_count": 200
	},
	"t8464OutBlock1": [
		{
			"date": "20260427",
			"time": "1449341880",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 100,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449341880",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449341880",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449341880",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 100,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449341880",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 60,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449341880",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449343131",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 10,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1449343467",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 65,
			"openyak": 407219
		},
		{
			"date": "20260427",
			"time": "1450390941",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 25,
			"openyak": 406969
		},
		{
			"date": "20260427",
			"time": "1450390941",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 25,
			"openyak": 406969
		},
		{
			"date": "20260427",
			"time": "1450390941",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 8,
			"openyak": 406969
		},
		{
			"date": "20260427",
			"time": "1450391245",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 12,
			"openyak": 406969
		},
		{
			"date": "20260427",
			"time": "1451203006",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440790",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 53,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440790",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 10,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440790",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440790",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 11,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440943",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 9,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440943",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 25,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440943",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 25,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452440943",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452441062",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452539867",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 18,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452540649",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452551181",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 6,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452551182",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 53,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452551182",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452551182",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 25,
			"openyak": 406981
		},
		{
			"date": "20260427",
			"time": "1452589328",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 10,
			"openyak": 407088
		},
		{
			"date": "20260427",
			"time": "1453067187",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 15,
			"openyak": 407088
		},
		{
			"date": "20260427",
			"time": "1453177896",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 28,
			"openyak": 407221
		},
		{
			"date": "20260427",
			"time": "1453177896",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 15,
			"openyak": 407221
		},
		{
			"date": "20260427",
			"time": "1453237639",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 10,
			"openyak": 407221
		},
		{
			"date": "20260427",
			"time": "1453237639",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 13,
			"openyak": 407221
		},
		{
			"date": "20260427",
			"time": "1504471199",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407302
		},
		{
			"date": "20260427",
			"time": "1505217814",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 11,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217814",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 2,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 5,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217815",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 12,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217854",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 8,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217854",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217854",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217854",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 17,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217855",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 3,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217855",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217855",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1505217856",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407303
		},
		{
			"date": "20260427",
			"time": "1507502156",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 2,
			"openyak": 407302
		},
		{
			"date": "20260427",
			"time": "1507513055",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 18,
			"openyak": 407302
		},
		{
			"date": "20260427",
			"time": "1507513055",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 20,
			"openyak": 407302
		},
		{
			"date": "20260427",
			"time": "1508284933",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407342
		},
		{
			"date": "20260427",
			"time": "1509280394",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 75,
			"openyak": 407343
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 222,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 10,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004777",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004778",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 20,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004778",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004778",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004778",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004778",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510004778",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 11,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510010283",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 39,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510010283",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510010283",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510010283",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510010283",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 20,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510010283",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 3,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510015396",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 2,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510015396",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510015396",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510015396",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 20,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510015397",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510022138",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510073430",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510074068",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510084951",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 25,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510117624",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 50,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510120218",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 21,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510120841",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 54,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1510131410",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 17,
			"openyak": 407418
		},
		{
			"date": "20260427",
			"time": "1511488635",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 407788
		},
		{
			"date": "20260427",
			"time": "1511488635",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 16,
			"openyak": 407788
		},
		{
			"date": "20260427",
			"time": "1512070766",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 55,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512070766",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512070766",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 19,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512103177",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512189279",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512189279",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 71,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512257070",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 20,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1512257070",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 71,
			"openyak": 407809
		},
		{
			"date": "20260427",
			"time": "1516008919",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 500,
			"openyak": 408045
		},
		{
			"date": "20260427",
			"time": "1516445195",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516445196",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 75,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516445196",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 1,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516445196",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 36,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516469262",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 39,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516469262",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 20,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516469262",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516469262",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 20,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516469263",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 5,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516469263",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 24,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1516546318",
			"open": "224000.00",
			"high": "224000.00",
			"low": "224000.00",
			"close": "224000.00",
			"jdiff_vol": 13,
			"openyak": 408048
		},
		{
			"date": "20260427",
			"time": "1518418435",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1518418435",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 3,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1518418435",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1518418435",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1518418435",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 2,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1518418435",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1518418454",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 30,
			"openyak": 407931
		},
		{
			"date": "20260427",
			"time": "1519288380",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 2,
			"openyak": 407894
		},
		{
			"date": "20260427",
			"time": "1519288380",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 26,
			"openyak": 407894
		},
		{
			"date": "20260427",
			"time": "1519380197",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 50,
			"openyak": 407894
		},
		{
			"date": "20260427",
			"time": "1519380197",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407894
		},
		{
			"date": "20260427",
			"time": "1519380206",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 67,
			"openyak": 407894
		},
		{
			"date": "20260427",
			"time": "1519584977",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 50,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1521100340",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1521384420",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1523040233",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 2,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1523480274",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314406",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314406",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314415",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 113,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314419",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314422",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 131,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314427",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 54,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314430",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314430",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 34,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314437",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314491",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314499",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314505",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 7,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314505",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 3,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314509",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 21,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314513",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314519",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314526",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 8,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314526",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 2,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314533",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314539",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314546",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314556",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314563",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314569",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314576",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314580",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 103,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314583",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314584",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 50,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314591",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314598",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314605",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314612",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314618",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314625",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314631",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314639",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314646",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314760",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527314957",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527315701",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527317108",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527317473",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527318691",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527329257",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 2,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527337166",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 8,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527337202",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 8,
			"openyak": 407855
		},
		{
			"date": "20260427",
			"time": "1527487413",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 50,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1529176400",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1529256096",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 2,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1530490102",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450263",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 52,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450263",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450264",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450264",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450326",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450331",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 18,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531450339",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 21,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1531496594",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 1,
			"openyak": 408444
		},
		{
			"date": "20260427",
			"time": "1533006726",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 18,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006726",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 2,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 10,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 1,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 49,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1533006727",
			"open": "224500.00",
			"high": "224500.00",
			"low": "224500.00",
			"close": "224500.00",
			"jdiff_vol": 96,
			"openyak": 408445
		},
		{
			"date": "20260427",
			"time": "1534075756",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 10,
			"openyak": 408417
		},
		{
			"date": "20260427",
			"time": "1545000969",
			"open": "225000.00",
			"high": "225000.00",
			"low": "225000.00",
			"close": "225000.00",
			"jdiff_vol": 17,
			"openyak": 408418
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8465"></a>
## `t8465` 선물/옵션차트(N분)

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
| `t8465InBlock` | t8465InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ncnt` | 단위(n분) | Number | Y | 4 | 0:30초<br/>1: 1분<br/>2: 2분<br/>.....<br/>n: n분 |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | 요청건수<br/><br/>압축모듈인 경우 최대 2000건까지 조회가능.<br/>비압축인 경우 최대 500건까지 조회가능 |
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
| `t8465OutBlock` | t8465OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 연속시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8465OutBlock1` | t8465OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-openyak` | 미결제약정 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8465InBlock": {
    "shcode": "A0166000",
    "ncnt": 120,
    "qrycnt": 500,
    "nday": "1",
    "sdate": "20251120",
    "edate": "20251125",
    "cts_date": "",
    "cts_time": "",
    "comp_yn": "N"
  }
}
```

### 응답 Example

```json
{
	"t8465OutBlock": {
		"shcode": "A0166000",
		"jisiga": "978.55",
		"jihigh": "993.75",
		"jilow": "951.15",
		"jiclose": "979.95",
		"jivolume": 185513,
		"disiga": "978.70",
		"dihigh": "985.25",
		"dilow": "963.65",
		"diclose": "973.95",
		"highend": "1058.30",
		"lowend": "901.60",
		"cts_date": "",
		"cts_time": "",
		"s_time": "084500",
		"e_time": "154500",
		"dshmin": "10",
		"rec_count": 4
	},
	"t8465OutBlock1": [
		{
			"date": "20251125",
			"time": "104500",
			"open": "553.75",
			"high": "553.75",
			"low": "553.00",
			"close": "553.00",
			"jdiff_vol": 2,
			"value": 277,
			"openyak": 7511
		},
		{
			"date": "20251125",
			"time": "124500",
			"open": "553.00",
			"high": "553.00",
			"low": "553.00",
			"close": "553.00",
			"jdiff_vol": 0,
			"value": 0,
			"openyak": 7529
		},
		{
			"date": "20251125",
			"time": "144500",
			"open": "553.00",
			"high": "553.00",
			"low": "553.00",
			"close": "553.00",
			"jdiff_vol": 0,
			"value": 0,
			"openyak": 7529
		},
		{
			"date": "20251125",
			"time": "154500",
			"open": "553.00",
			"high": "553.00",
			"low": "545.60",
			"close": "545.60",
			"jdiff_vol": 1,
			"value": 136,
			"openyak": 7528
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8466"></a>
## `t8466` 선물/옵션차트(일주월)

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
| `t8466InBlock` | t8466InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-gubun` | 주기구분(2:일3:주4:월) | String | Y | 1 | - |
| `&nbsp;&nbsp;-qrycnt` | 요청건수(최대-압축:2000비압축:500) | Number | Y | 4 | 요청건수<br/><br/>압축모듈인 경우 최대 2000건까지 조회가능.<br/>비압축인 경우 최대 500건까지 조회가능 |
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
| `t8466OutBlock` | t8466OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jisiga` | 전일시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jihigh` | 전일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jilow` | 전일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jiclose` | 전일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jivolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-disiga` | 당일시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dihigh` | 당일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dilow` | 당일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diclose` | 당일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-highend` | 상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-lowend` | 하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-cts_date` | 연속일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-s_time` | 장시작시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-e_time` | 장종료시간(HHMMSS) | String | Y | 6 | - |
| `&nbsp;&nbsp;-dshmin` | 동시호가처리시간(MM:분) | String | Y | 2 | - |
| `&nbsp;&nbsp;-rec_count` | 레코드카운트 | Number | Y | 7 | - |
| `t8466OutBlock1` | t8466OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jdiff_vol` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-openyak` | 미결제약정 | Number | Y | 12 | - |


### 요청 Example

```json
{
	"t8466InBlock": {
		"shcode": "A1165000",
		"gubun": "2",
		"qrycnt": 50,
		"sdate": "",
		"edate": "20260417",
		"cts_date": "",
		"comp_yn": "N"
	}
}
```

### 응답 Example

```json
{
	"t8466OutBlock": {
		"shcode": "A1165000",
		"jisiga": "220500.00",
		"jihigh": "230500.00",
		"jilow": "216500.00",
		"jiclose": "227000.00",
		"jivolume": 3095395,
		"disiga": "225000.00",
		"dihigh": "226000.00",
		"dilow": "217000.00",
		"diclose": "219500.00",
		"highend": "249500.00",
		"lowend": "204500.00",
		"cts_date": "",
		"s_time": "084500",
		"e_time": "154500",
		"dshmin": "10",
		"rec_count": 42
	},
	"t8466OutBlock1": [
		{
			"date": "20260213",
			"open": "181100.00",
			"high": "183700.00",
			"low": "181100.00",
			"close": "182000.00",
			"jdiff_vol": 4,
			"value": 7298,
			"openyak": 4
		},
		{
			"date": "20260219",
			"open": "187100.00",
			"high": "191000.00",
			"low": "187100.00",
			"close": "191000.00",
			"jdiff_vol": 44,
			"value": 83545,
			"openyak": 34
		},
		{
			"date": "20260220",
			"open": "190800.00",
			"high": "191500.00",
			"low": "189600.00",
			"close": "191000.00",
			"jdiff_vol": 138,
			"value": 262635,
			"openyak": 125
		},
		{
			"date": "20260223",
			"open": "196000.00",
			"high": "197000.00",
			"low": "191000.00",
			"close": "193400.00",
			"jdiff_vol": 61,
			"value": 118592,
			"openyak": 163
		},
		{
			"date": "20260224",
			"open": "194000.00",
			"high": "201500.00",
			"low": "193000.00",
			"close": "201000.00",
			"jdiff_vol": 361,
			"value": 716823,
			"openyak": 194
		},
		{
			"date": "20260225",
			"open": "206000.00",
			"high": "206000.00",
			"low": "202500.00",
			"close": "205500.00",
			"jdiff_vol": 27,
			"value": 55505,
			"openyak": 217
		},
		{
			"date": "20260226",
			"open": "211000.00",
			"high": "220500.00",
			"low": "211000.00",
			"close": "220500.00",
			"jdiff_vol": 21,
			"value": 45880,
			"openyak": 228
		},
		{
			"date": "20260227",
			"open": "216500.00",
			"high": "223500.00",
			"low": "212000.00",
			"close": "221000.00",
			"jdiff_vol": 174,
			"value": 376380,
			"openyak": 367
		},
		{
			"date": "20260303",
			"open": "220500.00",
			"high": "220500.00",
			"low": "195400.00",
			"close": "196000.00",
			"jdiff_vol": 698,
			"value": 1442692,
			"openyak": 1048
		},
		{
			"date": "20260304",
			"open": "187300.00",
			"high": "195000.00",
			"low": "172100.00",
			"close": "172100.00",
			"jdiff_vol": 649,
			"value": 1179723,
			"openyak": 1598
		},
		{
			"date": "20260305",
			"open": "189300.00",
			"high": "199800.00",
			"low": "189300.00",
			"close": "193400.00",
			"jdiff_vol": 344,
			"value": 663697,
			"openyak": 1642
		},
		{
			"date": "20260306",
			"open": "188100.00",
			"high": "190800.00",
			"low": "182500.00",
			"close": "190800.00",
			"jdiff_vol": 218,
			"value": 407025,
			"openyak": 1776
		},
		{
			"date": "20260309",
			"open": "176700.00",
			"high": "176700.00",
			"low": "168400.00",
			"close": "174600.00",
			"jdiff_vol": 238,
			"value": 411272,
			"openyak": 1854
		},
		{
			"date": "20260310",
			"open": "186100.00",
			"high": "192000.00",
			"low": "185600.00",
			"close": "188800.00",
			"jdiff_vol": 376,
			"value": 709912,
			"openyak": 2032
		},
		{
			"date": "20260311",
			"open": "193400.00",
			"high": "195500.00",
			"low": "189100.00",
			"close": "191000.00",
			"jdiff_vol": 241,
			"value": 465740,
			"openyak": 1960
		},
		{
			"date": "20260312",
			"open": "188700.00",
			"high": "190500.00",
			"low": "186200.00",
			"close": "188100.00",
			"jdiff_vol": 854,
			"value": 1606421,
			"openyak": 1989
		},
		{
			"date": "20260313",
			"open": "181100.00",
			"high": "186700.00",
			"low": "180300.00",
			"close": "184000.00",
			"jdiff_vol": 49265,
			"value": 90742646,
			"openyak": 14803
		},
		{
			"date": "20260316",
			"open": "185100.00",
			"high": "189700.00",
			"low": "184200.00",
			"close": "189200.00",
			"jdiff_vol": 23346,
			"value": 43554048,
			"openyak": 21739
		},
		{
			"date": "20260317",
			"open": "197100.00",
			"high": "199300.00",
			"low": "193700.00",
			"close": "194400.00",
			"jdiff_vol": 14779,
			"value": 29019093,
			"openyak": 22160
		},
		{
			"date": "20260318",
			"open": "199900.00",
			"high": "210000.00",
			"low": "199900.00",
			"close": "208500.00",
			"jdiff_vol": 22605,
			"value": 46405120,
			"openyak": 28667
		},
		{
			"date": "20260319",
			"open": "200000.00",
			"high": "205500.00",
			"low": "199800.00",
			"close": "201000.00",
			"jdiff_vol": 36659,
			"value": 74228846,
			"openyak": 51536
		},
		{
			"date": "20260320",
			"open": "203500.00",
			"high": "203500.00",
			"low": "199300.00",
			"close": "199300.00",
			"jdiff_vol": 23580,
			"value": 47355139,
			"openyak": 60198
		},
		{
			"date": "20260323",
			"open": "192600.00",
			"high": "192600.00",
			"low": "186200.00",
			"close": "186200.00",
			"jdiff_vol": 67799,
			"value": 127989135,
			"openyak": 65529
		},
		{
			"date": "20260324",
			"open": "196400.00",
			"high": "196700.00",
			"low": "185700.00",
			"close": "190600.00",
			"jdiff_vol": 75381,
			"value": 142748201,
			"openyak": 80626
		},
		{
			"date": "20260325",
			"open": "192300.00",
			"high": "196800.00",
			"low": "189700.00",
			"close": "189700.00",
			"jdiff_vol": 50568,
			"value": 98085408,
			"openyak": 86389
		},
		{
			"date": "20260326",
			"open": "186400.00",
			"high": "186400.00",
			"low": "179200.00",
			"close": "181000.00",
			"jdiff_vol": 121787,
			"value": 221625937,
			"openyak": 101509
		},
		{
			"date": "20260327",
			"open": "174800.00",
			"high": "181900.00",
			"low": "172200.00",
			"close": "180100.00",
			"jdiff_vol": 65314,
			"value": 115124850,
			"openyak": 106069
		},
		{
			"date": "20260330",
			"open": "172600.00",
			"high": "177100.00",
			"low": "171000.00",
			"close": "176700.00",
			"jdiff_vol": 49341,
			"value": 85973062,
			"openyak": 118627
		},
		{
			"date": "20260331",
			"open": "170500.00",
			"high": "175100.00",
			"low": "167200.00",
			"close": "167700.00",
			"jdiff_vol": 105441,
			"value": 179860673,
			"openyak": 130269
		},
		{
			"date": "20260401",
			"open": "178200.00",
			"high": "191400.00",
			"low": "178200.00",
			"close": "190100.00",
			"jdiff_vol": 193709,
			"value": 357580074,
			"openyak": 267703
		},
		{
			"date": "20260402",
			"open": "192900.00",
			"high": "194000.00",
			"low": "175700.00",
			"close": "179100.00",
			"jdiff_vol": 259896,
			"value": 471820892,
			"openyak": 396073
		},
		{
			"date": "20260403",
			"open": "184900.00",
			"high": "187900.00",
			"low": "183400.00",
			"close": "186600.00",
			"jdiff_vol": 131660,
			"value": 245099615,
			"openyak": 547217
		},
		{
			"date": "20260406",
			"open": "190700.00",
			"high": "195300.00",
			"low": "190100.00",
			"close": "193800.00",
			"jdiff_vol": 203643,
			"value": 392828397,
			"openyak": 908705
		},
		{
			"date": "20260407",
			"open": "204000.00",
			"high": "205000.00",
			"low": "193100.00",
			"close": "196500.00",
			"jdiff_vol": 503685,
			"value": 992096846,
			"openyak": 2106455
		},
		{
			"date": "20260408",
			"open": "209000.00",
			"high": "215500.00",
			"low": "208500.00",
			"close": "211000.00",
			"jdiff_vol": 1036426,
			"value": 2193978110,
			"openyak": 3722892
		},
		{
			"date": "20260409",
			"open": "207500.00",
			"high": "208500.00",
			"low": "202500.00",
			"close": "204500.00",
			"jdiff_vol": 1330137,
			"value": 2727453445,
			"openyak": 4108374
		},
		{
			"date": "20260410",
			"open": "209000.00",
			"high": "211500.00",
			"low": "206500.00",
			"close": "206500.00",
			"jdiff_vol": 1454074,
			"value": 3035218325,
			"openyak": 4097919
		},
		{
			"date": "20260413",
			"open": "199700.00",
			"high": "203500.00",
			"low": "198400.00",
			"close": "201500.00",
			"jdiff_vol": 1349279,
			"value": 2720529048,
			"openyak": 3977295
		},
		{
			"date": "20260414",
			"open": "208000.00",
			"high": "211000.00",
			"low": "206000.00",
			"close": "207500.00",
			"jdiff_vol": 1449355,
			"value": 3023491425,
			"openyak": 4069193
		},
		{
			"date": "20260415",
			"open": "215500.00",
			"high": "217000.00",
			"low": "211000.00",
			"close": "212000.00",
			"jdiff_vol": 1721736,
			"value": 3688605400,
			"openyak": 4120567
		},
		{
			"date": "20260416",
			"open": "213000.00",
			"high": "219000.00",
			"low": "211000.00",
			"close": "218500.00",
			"jdiff_vol": 1575576,
			"value": 3408710370,
			"openyak": 4225646
		},
		{
			"date": "20260417",
			"open": "219000.00",
			"high": "219500.00",
			"low": "215500.00",
			"close": "216500.00",
			"jdiff_vol": 1199818,
			"value": 2605047105,
			"openyak": 4236726
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8461"></a>
## `t8461` KRX야간파생 틱분별조회(API용)

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
| `t8461InBlock` | t8461InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cgubun` | 챠트구분 | String | Y | 1 | T:틱차트<br/>B:분차트 |
| `&nbsp;&nbsp;-bgubun` | 분구분 | Object | Y | 3 | 차트구분이 'B'일때만 체크<br/>0: 30초<br/>0초과 : n분 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |


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
| `t8461OutBlock1` | t8461OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschecnt` | 매수순간체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mdchecnt` | 매도순간체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ss_mschecnt` | 순매수순간체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschevol` | 매수순간체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-s_mdchevol` | 매도순간체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ss_mschevol` | 순매수순간체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-chdegvol` | 체결강도(거래량) | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-chdegcnt` | 체결강도(건수) | Number | Y | 8.2 | - |


### 요청 Example

```json
{
  "t8461InBlock": {
    "focode": "101W6000",
    "cgubun": "2",
    "bgubun": "0",
    "cnt": 20
  }
}
```

### 응답 Example

```json
{
	"t8461OutBlock1": [
		{
			"chetime": "161600",
			"price": "436.40",
			"sign": "2",
			"change": "30.25",
			"open": "436.00",
			"high": "436.45",
			"low": "436.00",
			"volume": "12436",
			"cvolume": 267,
			"s_mschecnt": 3,
			"s_mdchecnt": 22,
			"ss_mschecnt": -19,
			"s_mschevol": "76",
			"s_mdchevol": "191",
			"ss_mschevol": "-115",
			"chdegvol": "305.72",
			"chdegcnt": "155.87"
		},
		{
			"chetime": "161530",
			"price": "436.00",
			"sign": "2",
			"change": "29.85",
			"open": "435.85",
			"high": "436.10",
			"low": "435.40",
			"volume": "12169",
			"cvolume": 496,
			"s_mschecnt": 45,
			"s_mdchecnt": 16,
			"ss_mschecnt": 29,
			"s_mschevol": "385",
			"s_mdchevol": "111",
			"ss_mschevol": "274",
			"chdegvol": "326.75",
			"chdegcnt": "169.78"
		},
		{
			"chetime": "161500",
			"price": "435.35",
			"sign": "2",
			"change": "29.20",
			"open": "435.55",
			"high": "435.95",
			"low": "435.35",
			"volume": "11673",
			"cvolume": 228,
			"s_mschecnt": 8,
			"s_mdchecnt": 6,
			"ss_mschecnt": 2,
			"s_mschevol": "206",
			"s_mdchevol": "22",
			"ss_mschevol": "184",
			"chdegvol": "325.78",
			"chdegcnt": "161.24"
		},
		{
			"chetime": "161430",
			"price": "435.50",
			"sign": "2",
			"change": "29.35",
			"open": "435.35",
			"high": "435.50",
			"low": "435.35",
			"volume": "11445",
			"cvolume": 1127,
			"s_mschecnt": 12,
			"s_mdchecnt": 5,
			"ss_mschecnt": 7,
			"s_mschevol": "1102",
			"s_mdchevol": "25",
			"ss_mschevol": "1077",
			"chdegvol": "319.89",
			"chdegcnt": "162.07"
		},
		{
			"chetime": "161400",
			"price": "435.30",
			"sign": "2",
			"change": "29.15",
			"open": "435.25",
			"high": "435.30",
			"low": "435.25",
			"volume": "10318",
			"cvolume": 836,
			"s_mschecnt": 87,
			"s_mdchecnt": 0,
			"ss_mschecnt": 87,
			"s_mschevol": "836",
			"s_mdchevol": "0",
			"ss_mschevol": "836",
			"chdegvol": "274.61",
			"chdegcnt": "160.10"
		},
		{
			"chetime": "161330",
			"price": "435.30",
			"sign": "2",
			"change": "29.15",
			"open": "435.25",
			"high": "435.30",
			"low": "435.25",
			"volume": "9482",
			"cvolume": 172,
			"s_mschecnt": 18,
			"s_mdchecnt": 3,
			"ss_mschecnt": 15,
			"s_mschevol": "167",
			"s_mdchevol": "5",
			"ss_mschevol": "162",
			"chdegvol": "237.57",
			"chdegcnt": "116.16"
		},
		{
			"chetime": "161300",
			"price": "435.20",
			"sign": "2",
			"change": "29.05",
			"open": "435.00",
			"high": "435.20",
			"low": "434.95",
			"volume": "9310",
			"cvolume": 546,
			"s_mschecnt": 8,
			"s_mdchecnt": 3,
			"ss_mschecnt": 5,
			"s_mschevol": "536",
			"s_mdchevol": "10",
			"ss_mschevol": "526",
			"chdegvol": "230.68",
			"chdegcnt": "108.72"
		},
		{
			"chetime": "161230",
			"price": "435.00",
			"sign": "2",
			"change": "28.85",
			"open": "415.90",
			"high": "435.00",
			"low": "415.90",
			"volume": "8764",
			"cvolume": 1482,
			"s_mschecnt": 7,
			"s_mdchecnt": 1,
			"ss_mschecnt": 6,
			"s_mschevol": "1481",
			"s_mdchevol": "1",
			"ss_mschevol": "1480",
			"chdegvol": "207.81",
			"chdegcnt": "106.25"
		},
		{
			"chetime": "161200",
			"price": "424.00",
			"sign": "2",
			"change": "17.85",
			"open": "424.00",
			"high": "424.00",
			"low": "424.00",
			"volume": "7282",
			"cvolume": 0,
			"s_mschecnt": 0,
			"s_mdchecnt": 0,
			"ss_mschecnt": 0,
			"s_mschevol": "0",
			"s_mdchevol": "0",
			"ss_mschevol": "0",
			"chdegvol": "141.81",
			"chdegcnt": "103.14"
		},
		{
			"chetime": "161130",
			"price": "424.00",
			"sign": "2",
			"change": "17.85",
			"open": "424.00",
			"high": "424.00",
			"low": "423.70",
			"volume": "7282",
			"cvolume": 83,
			"s_mschecnt": 2,
			"s_mdchecnt": 8,
			"ss_mschecnt": -6,
			"s_mschevol": "9",
			"s_mdchevol": "74",
			"ss_mschevol": "-65",
			"chdegvol": "141.81",
			"chdegcnt": "103.14"
		},
		{
			"chetime": "161100",
			"price": "423.70",
			"sign": "2",
			"change": "17.55",
			"open": "424.00",
			"high": "424.00",
			"low": "423.70",
			"volume": "7199",
			"cvolume": 26,
			"s_mschecnt": 0,
			"s_mdchecnt": 4,
			"ss_mschecnt": -4,
			"s_mschevol": "0",
			"s_mdchevol": "26",
			"ss_mschevol": "-26",
			"chdegvol": "146.24",
			"chdegcnt": "106.56"
		},
		{
			"chetime": "161030",
			"price": "430.00",
			"sign": "2",
			"change": "23.85",
			"open": "423.70",
			"high": "430.00",
			"low": "423.70",
			"volume": "7173",
			"cvolume": 102,
			"s_mschecnt": 1,
			"s_mdchecnt": 2,
			"ss_mschecnt": -1,
			"s_mschevol": "100",
			"s_mdchevol": "2",
			"ss_mschevol": "98",
			"chdegvol": "148.01",
			"chdegcnt": "108.94"
		},
		{
			"chetime": "161000",
			"price": "415.60",
			"sign": "2",
			"change": "9.45",
			"open": "407.50",
			"high": "415.60",
			"low": "407.50",
			"volume": "7071",
			"cvolume": 107,
			"s_mschecnt": 2,
			"s_mdchecnt": 23,
			"ss_mschecnt": -21,
			"s_mschevol": "6",
			"s_mdchevol": "101",
			"ss_mschevol": "-95",
			"chdegvol": "143.48",
			"chdegcnt": "109.60"
		},
		{
			"chetime": "160930",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"open": "407.55",
			"high": "407.55",
			"low": "407.50",
			"volume": "6964",
			"cvolume": 39,
			"s_mschecnt": 0,
			"s_mdchecnt": 39,
			"ss_mschecnt": -39,
			"s_mschevol": "0",
			"s_mdchevol": "39",
			"ss_mschevol": "-39",
			"chdegvol": "150.29",
			"chdegcnt": "124.68"
		},
		{
			"chetime": "160900",
			"price": "414.25",
			"sign": "2",
			"change": "8.10",
			"open": "407.60",
			"high": "414.35",
			"low": "407.60",
			"volume": "6925",
			"cvolume": 91,
			"s_mschecnt": 5,
			"s_mdchecnt": 0,
			"ss_mschecnt": 5,
			"s_mschevol": "91",
			"s_mdchevol": "0",
			"ss_mschevol": "91",
			"chdegvol": "153.23",
			"chdegcnt": "166.96"
		},
		{
			"chetime": "160830",
			"price": "407.60",
			"sign": "2",
			"change": "1.45",
			"open": "407.60",
			"high": "407.60",
			"low": "407.60",
			"volume": "6834",
			"cvolume": 5,
			"s_mschecnt": 5,
			"s_mdchecnt": 0,
			"ss_mschecnt": 5,
			"s_mschevol": "5",
			"s_mdchevol": "0",
			"ss_mschevol": "5",
			"chdegvol": "148.67",
			"chdegcnt": "162.61"
		},
		{
			"chetime": "160800",
			"price": "407.60",
			"sign": "2",
			"change": "1.45",
			"open": "414.35",
			"high": "414.35",
			"low": "407.55",
			"volume": "6829",
			"cvolume": 501,
			"s_mschecnt": 6,
			"s_mdchecnt": 6,
			"ss_mschecnt": 0,
			"s_mschevol": "6",
			"s_mdchevol": "495",
			"ss_mschevol": "-489",
			"chdegvol": "148.42",
			"chdegcnt": "158.26"
		},
		{
			"chetime": "160730",
			"price": "408.25",
			"sign": "2",
			"change": "2.10",
			"open": "407.90",
			"high": "414.35",
			"low": "407.65",
			"volume": "6328",
			"cvolume": 1660,
			"s_mschecnt": 16,
			"s_mdchecnt": 5,
			"ss_mschecnt": 11,
			"s_mschevol": "1628",
			"s_mdchevol": "32",
			"ss_mschevol": "1596",
			"chdegvol": "196.88",
			"chdegcnt": "161.47"
		},
		{
			"chetime": "160700",
			"price": "407.85",
			"sign": "2",
			"change": "1.70",
			"open": "407.80",
			"high": "407.85",
			"low": "407.75",
			"volume": "4668",
			"cvolume": 231,
			"s_mschecnt": 4,
			"s_mdchecnt": 1,
			"ss_mschecnt": 3,
			"s_mschevol": "226",
			"s_mdchevol": "5",
			"ss_mschevol": "221",
			"chdegvol": "90.56",
			"chdegcnt": "153.85"
		},
		{
			"chetime": "160630",
			"price": "407.80",
			"sign": "2",
			"change": "1.65",
			"open": "407.80",
			"high": "407.80",
			"low": "407.80",
			"volume": "4437",
			"cvolume": 12,
			"s_mschecnt": 4,
			"s_mdchecnt": 0,
			"ss_mschecnt": 4,
			"s_mschevol": "12",
			"s_mdchevol": "0",
			"ss_mschevol": "12",
			"chdegvol": "75.46",
			"chdegcnt": "151.46"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
