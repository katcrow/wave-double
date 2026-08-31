# [선물/옵션] 시세

> LS증권 OPEN API 정의서 · 그룹: **선물/옵션** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=2f1eea77-5606-4512-93c6-31b21d2ece90&api_id=9f467798-6ce6-4d31-ab93-5a0e2860f89f)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `9f467798-6ce6-4d31-ab93-5a0e2860f89f` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/futureoption/market-data` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 주간/야간 선물옵션 종목별 시세 및 미결제약정 등시세관련 데이터를 확인할 수 있습니다. |

## TR 목록 (30건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 선물/옵션현재가(시세)조회 | [t2111](market-data.md#tr-t2111) | 10 | 10 | 5 |
| 선물/옵션현재가호가조회 | [t2112](market-data.md#tr-t2112) | 10 | 10 | 5 |
| 선물/옵션현재가시세메모 | [t2106](market-data.md#tr-t2106) | 1 | 1 | 3 |
| 선물옵션시간대별체결조회 | [t2212](market-data.md#tr-t2212) | 2 | 2 | 3 |
| 기간별주가 | [t2214](market-data.md#tr-t2214) | 1 | 1 | 3 |
| 선물옵션시간대별체결조회(단일출력용) | [t2210](market-data.md#tr-t2210) | 2 | 2 | 3 |
| 옵션전광판 | [t2301](market-data.md#tr-t2301) | 2 | 2 | 3 |
| 선물옵션호가잔량비율챠트 | [t2407](market-data.md#tr-t2407) | 1 | 1 | 3 |
| 미결제약정추이 | [t2424](market-data.md#tr-t2424) | 1 | 1 | 3 |
| 주식선물기초자산조회 | [t2522](market-data.md#tr-t2522) | 2 | 2 | 3 |
| 주식선물마스터조회(API용) | [t8401](market-data.md#tr-t8401) | 2 | 2 | 3 |
| 주식선물현재가조회(API용) | [t8402](market-data.md#tr-t8402) | 10 | 10 | 2 |
| 주식선물호가조회(API용) | [t8403](market-data.md#tr-t8403) | 10 | 10 | 2 |
| 주식선물시간대별체결조회(API용) | [t8404](market-data.md#tr-t8404) | 2 | 2 | 3 |
| 주식선물기간별주가(API용) | [t8405](market-data.md#tr-t8405) | 1 | 1 | 3 |
| 주식선물틱분별체결조회(API용) | [t8406](market-data.md#tr-t8406) | 1 | 1 | 3 |
| 상품선물마스터조회(API용) | [t8426](market-data.md#tr-t8426) | 1 | 1 | 3 |
| 과거데이터시간대별조회 | [t8427](market-data.md#tr-t8427) | 1 | 1 | 3 |
| 지수선물마스터조회API용 | [t8467](market-data.md#tr-t8467) | 2 | 2 | 3 |
| 지수옵션마스터조회API용 | [t8433](market-data.md#tr-t8433) | 2 | 2 | 3 |
| 선물/옵션멀티현재가조회 | [t8434](market-data.md#tr-t8434) | 3 | 3 | 5 |
| 파생종목마스터조회API용 | [t8435](market-data.md#tr-t8435) | 2 | 2 | 3 |
| 지수선물마스터조회API용 | [t9943](market-data.md#tr-t9943) | 2 | 2 | 3 |
| 지수옵션마스터조회API용 | [t9944](market-data.md#tr-t9944) | 2 | 2 | 3 |
| KRX야간파생 마스터조회(API용) | [t8455](market-data.md#tr-t8455) | 2 | 2 | 3 |
| KRX야간파생 시세조회(API용) | [t8456](market-data.md#tr-t8456) | 10 | 10 | 3 |
| KRX야간파생 호가조회(API용) | [t8457](market-data.md#tr-t8457) | 10 | 2 | 3 |
| KRX야간파생 시간대별체결(API용) | [t8458](market-data.md#tr-t8458) | 2 | 2 | 3 |
| KRX야간파생 기간별주가(API용) | [t8459](market-data.md#tr-t8459) | 1 | 1 | 3 |
| KRX야간파생 옵션 전광판 | [t8460](market-data.md#tr-t8460) | 2 | 2 | 3 |

---

<a id="tr-t2111"></a>
## `t2111` 선물/옵션현재가(시세)조회

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
| `t2111InBlock` | t2111InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |


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
| `t2111OutBlock` | t2111OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mgjv` | 미결제량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mgjvdiff` | 미결제증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high52w` | 52최고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low52w` | 52최저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-basis` | 베이시스 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-glyl` | 괴리율 | Number | Y | 6.3 | - |
| `&nbsp;&nbsp;-cbhprice` | CB상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-cblprice` | CB하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-lastmonth` | 만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jandatecnt` | 잔여일 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-pricejisu` | 종합지수 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jisusign` | 종합지수전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-jisuchange` | 종합지수전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jisudiff` | 종합지수등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-kospijisu` | KOSPI200지수 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-kospisign` | KOSPI200전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-kospichange` | KOSPI200전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-kospidiff` | KOSPI200등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-listhprice` | 상장최고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-listlprice` | 상장최저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-delt` | 델타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-gama` | 감마 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-ceta` | 세타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-vega` | 베가 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-rhox` | 로우 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-gmprice` | 근월물현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-gmsign` | 근월물전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-gmchange` | 근월물전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-gmdiff` | 근월물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-theorypriceg` | 이론가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-histimpv` | 역사적변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-impv` | 내재변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sbasis` | 시장BASIS | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-ibasis` | 이론BASIS | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-gmfutcode` | 근월물종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-greeks_time` | 거래소민감도수신시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-greeks_confirm` | 거래소민감도확정여부 | String | Y | 8 | - |
| `&nbsp;&nbsp;-danhochk` | 단일가호가여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-yeprice` | 예상체결가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilychange` | 예상체결가전일종가대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jnilydrate` | 예상체결가전일종가등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-alloc_gubun` | 배분구분(1:배분개시2:배분해제0:미발생) | String | Y | 1 | - |
| `&nbsp;&nbsp;-bjandatecnt` | 잔여일(영업일) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-focode` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-dy_gubun` | 실시간가격제한여부(0:대상아님1:적용중2:미적용중3:일시해제) | String | Y | 1 | - |
| `&nbsp;&nbsp;-dy_uplmtprice` | 실시간상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dy_dnlmtprice` | 실시간하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-updnstep_gubun` | 가격제한폭확대(0:미확대1:확대2:대상아님) | String | Y | 1 | - |
| `&nbsp;&nbsp;-upstep` | 상한적용단계 | String | Y | 2 | - |
| `&nbsp;&nbsp;-dnstep` | 하한적용단계 | String | Y | 2 | - |
| `&nbsp;&nbsp;-uplmtprice_3rd` | 3단계상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dnlmtprice_3rd` | 3단계하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-expct_ccls_q` | 예상체결수량 | Number | Y | 9 | - |


### 요청 Example

```json
{
  "t2111InBlock" : {
    "focode" : "A0166000"
  }
}
```

### 응답 Example

```json
{
	"t2111OutBlock": {
		"hname": "코스피200 F 202606",
		"price": "1046.10",
		"sign": "5",
		"change": "78.70",
		"jnilclose": "1124.80",
		"diff": "-7.00",
		"volume": 940,
		"value": 258542,
		"mgjv": 320623,
		"mgjvdiff": 30,
		"open": "1124.95",
		"high": "1124.95",
		"low": "1034.90",
		"uplmtprice": "1214.75",
		"dnlmtprice": "1034.85",
		"high52w": "0",
		"low52w": "0",
		"basis": "0",
		"recprice": "1124.80",
		"theoryprice": "974.86",
		"glyl": "7.308",
		"cbhprice": "0.00",
		"cblprice": "0.00",
		"lastmonth": "20260611",
		"jandatecnt": 49,
		"pricejisu": "6475.63",
		"jisusign": "5",
		"jisuchange": "0.18",
		"jisudiff": "0.00",
		"kospijisu": "971.87",
		"kospisign": "5",
		"kospichange": "3.75",
		"kospidiff": "-0.38",
		"listhprice": "1141.50",
		"listlprice": "538.30",
		"delt": "0",
		"gama": "0",
		"ceta": "0",
		"vega": "0",
		"rhox": "0",
		"gmprice": "0",
		"gmsign": "",
		"gmchange": "0",
		"gmdiff": "0",
		"theorypriceg": "0",
		"histimpv": "0",
		"impv": "0",
		"sbasis": "74.23",
		"ibasis": "2.99",
		"gmfutcode": "",
		"actprice": "0",
		"greeks_time": "",
		"greeks_confirm": "",
		"danhochk": "0",
		"yeprice": "0.00",
		"jnilysign": "3",
		"jnilychange": "0.00",
		"jnilydrate": "0.00",
		"alloc_gubun": "",
		"bjandatecnt": 32,
		"focode": "A0166000",
		"dy_gubun": "2",
		"dy_uplmtprice": "1214.75",
		"dy_dnlmtprice": "1034.85",
		"updnstep_gubun": "0",
		"upstep": "01",
		"dnstep": "01",
		"uplmtprice_3rd": "1349.75",
		"dnlmtprice_3rd": "899.85",
		"expct_ccls_q": 0
	},
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-t2112"></a>
## `t2112` 선물/옵션현재가호가조회

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
| `t2112InBlock` | t2112InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |


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
| `t2112OutBlock` | t2112OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한<br/>2:상승<br/>3:보합<br/>4:하한<br/>5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stimeqrt` | 거래량전일동시간비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt1` | 매도호가건수1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt1` | 매수호가건수1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt2` | 매도호가건수2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt2` | 매수호가건수2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt3` | 매도호가건수3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt3` | 매수호가건수3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt4` | 매도호가건수4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt4` | 매수호가건수4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt5` | 매도호가건수5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt5` | 매수호가건수5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dvol` | 매도호가총수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol` | 매수호가총수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-toffernum` | 총매도호가건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tbidnum` | 총매수호가건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 수신시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |


### 요청 Example

```json
{
	"t2112InBlock": {
		"shcode": "A0166000"
	}
}
```

### 응답 Example

```json
{
	"t2112OutBlock": {
		"hname": "코스피200 F 202606",
		"price": "996.95",
		"sign": "2",
		"change": "23.00",
		"diff": "2.36",
		"volume": 133033,
		"stimeqrt": "116.80",
		"jnilclose": "973.95",
		"offerho1": "996.95",
		"bidho1": "996.75",
		"offerrem1": 15,
		"bidrem1": 1,
		"dcnt1": 1,
		"scnt1": 1,
		"offerho2": "997.00",
		"bidho2": "996.70",
		"offerrem2": 65,
		"bidrem2": 1,
		"dcnt2": 11,
		"scnt2": 1,
		"offerho3": "997.05",
		"bidho3": "996.65",
		"offerrem3": 3,
		"bidrem3": 1,
		"dcnt3": 2,
		"scnt3": 1,
		"offerho4": "997.10",
		"bidho4": "996.50",
		"offerrem4": 7,
		"bidrem4": 1,
		"dcnt4": 2,
		"scnt4": 1,
		"offerho5": "997.15",
		"bidho5": "996.35",
		"offerrem5": 23,
		"bidrem5": 1,
		"dcnt5": 2,
		"scnt5": 1,
		"dvol": 2837,
		"svol": 2988,
		"toffernum": 477,
		"tbidnum": 602,
		"time": "154500",
		"shcode": "A0166000"
	},
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-t2106"></a>
## `t2106` 선물/옵션현재가시세메모

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
| `t2106InBlock` | t2106InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-code` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-nrec` | 건수 | String | Y | 2 | t2106InBlock1 의 개수 |
| `t2106InBlock1` | t2106InBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-indx` | 인덱스 | String | Y | 1 | t2106InBlock1 의 Occurs 순서(0부터 시작) |
| `&nbsp;&nbsp;-gubn` | 조건구분 | String | Y | 1 | 1:시세 2:최고저가 3:Pivot 4:이동평균선 |
| `&nbsp;&nbsp;-dat1` | 데이타1 | String | Y | 1 | 1:시가 2:고가 3:저가 4:가중평균가 |
| `&nbsp;&nbsp;-dat2` | 데이타2 | String | Y | 8 | 1:당일 2:전일 |


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
| `t2106OutBlock` | t2106OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-nrec` | 출력건수 | String | Y | 2 | t2106OutBlock1 의 개수 |
| `t2106OutBlock1` | t2106OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-indx` | 인덱스 | String | Y | 1 | t2106InBlock1 의 indx와 동일 |
| `&nbsp;&nbsp;-gubn` | 조건구분 | String | Y | 1 | 1:시세 2:최고저가 3:Pivot 4:이동평균선 t2106InBlock1의 gubn과 동일 |
| `&nbsp;&nbsp;-vals` | 출력값 | String | Y | 8 | - |


### 요청 Example

```json
{
  "t2106InBlock": {
    "code": "101T6000",
    "nrec": ""
  }
}
```

### 응답 Example

```json
{
  "rsp_cd": "00000",
  "rsp_msg": "입력조건을 확인하세요"
}
```

---

<a id="tr-t2212"></a>
## `t2212` 선물옵션시간대별체결조회

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
| `t2212InBlock` | t2212InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | 체결수량 >= cvolume |
| `&nbsp;&nbsp;-stime` | 시작시간 | String | Y | 4 | 체결시간 >= stime(hhmm)<br/> |
| `&nbsp;&nbsp;-etime` | 종료시간 | String | Y | 4 | 체결시간 <= etime(hhmm)<br/> |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |


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
| `t2212OutBlock` | t2212OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 연속조회키<br/>연속 조회시 이 값을 InBlock의 cts_time 필드에 넣어준다. |
| `t2212OutBlock1` | t2212OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-openyak` | 미결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilopenupdn` | 미결전일증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ibasis` | 이론BASIS | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sbasis` | 시장BASIS | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-kasis` | 괴리율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-j_openupdn` | 미결직전증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-n_msvolume` | 누적매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_mdvolume` | 누적매도체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-s_msvolume` | 누적순매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_mschecnt` | 누적매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-n_mdchecnt` | 누적매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschecnt` | 누적순매수체결건수 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t2212InBlock": {
    "focode": "A0166000",
    "cvolume": 0,
    "stime": "0900",
    "etime": "1600",
    "cts_time": ""
  }
}
```

### 응답 Example

```json
{
	"t2212OutBlock": {
		"cts_time": "1534063596"
	},
	"t2212OutBlock1": [
		{
			"chetime": "1545000435",
			"price": "996.95",
			"sign": "2",
			"change": "23.00",
			"cvolume": 3089,
			"chdegree": "99.36",
			"offerho": "996.95",
			"bidho": "996.75",
			"volume": "133033",
			"openyak": 207914,
			"jnilopenupdn": 7285,
			"ibasis": "2.85",
			"sbasis": "1.62",
			"kasis": "-0.12",
			"value": "33131071",
			"j_openupdn": 1037,
			"n_msvolume": "64639",
			"n_mdvolume": "65057",
			"s_msvolume": "-418",
			"n_mschecnt": 50336,
			"n_mdchecnt": 51284,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534596460",
			"price": "996.00",
			"sign": "2",
			"change": "22.05",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "996.00",
			"bidho": "995.90",
			"volume": "129944",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.67",
			"kasis": "-0.22",
			"value": "32361176",
			"j_openupdn": 0,
			"n_msvolume": "64639",
			"n_mdvolume": "65057",
			"s_msvolume": "-418",
			"n_mschecnt": 50336,
			"n_mdchecnt": 51284,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534593228",
			"price": "995.90",
			"sign": "2",
			"change": "21.95",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "996.00",
			"bidho": "995.90",
			"volume": "129943",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.57",
			"kasis": "-0.23",
			"value": "32360927",
			"j_openupdn": 0,
			"n_msvolume": "64638",
			"n_mdvolume": "65057",
			"s_msvolume": "-419",
			"n_mschecnt": 50335,
			"n_mdchecnt": 51284,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534585977",
			"price": "996.00",
			"sign": "2",
			"change": "22.05",
			"cvolume": 7,
			"chdegree": "99.36",
			"offerho": "996.05",
			"bidho": "995.75",
			"volume": "129942",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.67",
			"kasis": "-0.22",
			"value": "32360678",
			"j_openupdn": 0,
			"n_msvolume": "64638",
			"n_mdvolume": "65056",
			"s_msvolume": "-418",
			"n_mschecnt": 50335,
			"n_mdchecnt": 51283,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534585975",
			"price": "995.95",
			"sign": "2",
			"change": "22.00",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.90",
			"bidho": "995.75",
			"volume": "129935",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.62",
			"kasis": "-0.22",
			"value": "32358935",
			"j_openupdn": 0,
			"n_msvolume": "64631",
			"n_mdvolume": "65056",
			"s_msvolume": "-425",
			"n_mschecnt": 50334,
			"n_mdchecnt": 51283,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534585974",
			"price": "995.95",
			"sign": "2",
			"change": "22.00",
			"cvolume": 2,
			"chdegree": "99.35",
			"offerho": "995.95",
			"bidho": "995.75",
			"volume": "129934",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.62",
			"kasis": "-0.22",
			"value": "32358686",
			"j_openupdn": 0,
			"n_msvolume": "64630",
			"n_mdvolume": "65056",
			"s_msvolume": "-426",
			"n_mschecnt": 50333,
			"n_mdchecnt": 51283,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534585974",
			"price": "995.90",
			"sign": "2",
			"change": "21.95",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "996.00",
			"bidho": "995.75",
			"volume": "129932",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.57",
			"kasis": "-0.23",
			"value": "32358188",
			"j_openupdn": 0,
			"n_msvolume": "64628",
			"n_mdvolume": "65056",
			"s_msvolume": "-428",
			"n_mschecnt": 50332,
			"n_mdchecnt": 51283,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534585973",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 3,
			"chdegree": "99.34",
			"offerho": "995.90",
			"bidho": "995.75",
			"volume": "129931",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32357939",
			"j_openupdn": 0,
			"n_msvolume": "64627",
			"n_mdvolume": "65056",
			"s_msvolume": "-429",
			"n_mschecnt": 50331,
			"n_mdchecnt": 51283,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534581178",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.85",
			"bidho": "995.65",
			"volume": "129928",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32357193",
			"j_openupdn": 0,
			"n_msvolume": "64624",
			"n_mdvolume": "65056",
			"s_msvolume": "-432",
			"n_mschecnt": 50330,
			"n_mdchecnt": 51283,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534574111",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129927",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32356944",
			"j_openupdn": 0,
			"n_msvolume": "64624",
			"n_mdvolume": "65055",
			"s_msvolume": "-431",
			"n_mschecnt": 50330,
			"n_mdchecnt": 51282,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534570757",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.85",
			"bidho": "995.50",
			"volume": "129926",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32356695",
			"j_openupdn": 0,
			"n_msvolume": "64624",
			"n_mdvolume": "65054",
			"s_msvolume": "-430",
			"n_mschecnt": 50330,
			"n_mdchecnt": 51281,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534570720",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 6,
			"chdegree": "99.34",
			"offerho": "995.85",
			"bidho": "995.55",
			"volume": "129925",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32356446",
			"j_openupdn": 0,
			"n_msvolume": "64624",
			"n_mdvolume": "65053",
			"s_msvolume": "-429",
			"n_mschecnt": 50330,
			"n_mdchecnt": 51280,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534570696",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 3,
			"chdegree": "99.35",
			"offerho": "995.85",
			"bidho": "995.80",
			"volume": "129919",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32354952",
			"j_openupdn": 0,
			"n_msvolume": "64624",
			"n_mdvolume": "65047",
			"s_msvolume": "-423",
			"n_mschecnt": 50330,
			"n_mdchecnt": 51279,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534570695",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.55",
			"volume": "129916",
			"openyak": 206877,
			"jnilopenupdn": 6248,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32354205",
			"j_openupdn": 1,
			"n_msvolume": "64621",
			"n_mdvolume": "65047",
			"s_msvolume": "-426",
			"n_mschecnt": 50329,
			"n_mdchecnt": 51279,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534568818",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.70",
			"bidho": "995.55",
			"volume": "129915",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32353956",
			"j_openupdn": 0,
			"n_msvolume": "64620",
			"n_mdvolume": "65047",
			"s_msvolume": "-427",
			"n_mschecnt": 50328,
			"n_mdchecnt": 51279,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534567645",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.50",
			"volume": "129914",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32353707",
			"j_openupdn": 0,
			"n_msvolume": "64620",
			"n_mdvolume": "65046",
			"s_msvolume": "-426",
			"n_mschecnt": 50328,
			"n_mdchecnt": 51278,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534559174",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.50",
			"volume": "129913",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32353459",
			"j_openupdn": 0,
			"n_msvolume": "64620",
			"n_mdvolume": "65045",
			"s_msvolume": "-425",
			"n_mschecnt": 50328,
			"n_mdchecnt": 51277,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534559121",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.60",
			"bidho": "995.50",
			"volume": "129912",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32353210",
			"j_openupdn": 0,
			"n_msvolume": "64620",
			"n_mdvolume": "65044",
			"s_msvolume": "-424",
			"n_mschecnt": 50328,
			"n_mdchecnt": 51276,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534559120",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.60",
			"bidho": "995.50",
			"volume": "129911",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32352961",
			"j_openupdn": 0,
			"n_msvolume": "64619",
			"n_mdvolume": "65044",
			"s_msvolume": "-425",
			"n_mschecnt": 50327,
			"n_mdchecnt": 51276,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534559120",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 2,
			"chdegree": "99.35",
			"offerho": "995.60",
			"bidho": "995.50",
			"volume": "129910",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32352712",
			"j_openupdn": 0,
			"n_msvolume": "64618",
			"n_mdvolume": "65044",
			"s_msvolume": "-426",
			"n_mschecnt": 50326,
			"n_mdchecnt": 51276,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534559120",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 4,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.50",
			"volume": "129908",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32352214",
			"j_openupdn": 0,
			"n_msvolume": "64616",
			"n_mdvolume": "65044",
			"s_msvolume": "-428",
			"n_mschecnt": 50325,
			"n_mdchecnt": 51276,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534557716",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.45",
			"volume": "129904",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32351219",
			"j_openupdn": 0,
			"n_msvolume": "64612",
			"n_mdvolume": "65044",
			"s_msvolume": "-432",
			"n_mschecnt": 50324,
			"n_mdchecnt": 51276,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534556592",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 2,
			"chdegree": "99.33",
			"offerho": "995.55",
			"bidho": "995.45",
			"volume": "129903",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32350970",
			"j_openupdn": 0,
			"n_msvolume": "64611",
			"n_mdvolume": "65044",
			"s_msvolume": "-433",
			"n_mschecnt": 50323,
			"n_mdchecnt": 51276,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534554146",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.50",
			"bidho": "995.45",
			"volume": "129901",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32350472",
			"j_openupdn": 0,
			"n_msvolume": "64609",
			"n_mdvolume": "65044",
			"s_msvolume": "-435",
			"n_mschecnt": 50322,
			"n_mdchecnt": 51276,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534550990",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.45",
			"bidho": "995.25",
			"volume": "129900",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32350223",
			"j_openupdn": 0,
			"n_msvolume": "64608",
			"n_mdvolume": "65044",
			"s_msvolume": "-436",
			"n_mschecnt": 50321,
			"n_mdchecnt": 51276,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534550847",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129899",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32349974",
			"j_openupdn": 0,
			"n_msvolume": "64608",
			"n_mdvolume": "65043",
			"s_msvolume": "-435",
			"n_mschecnt": 50321,
			"n_mdchecnt": 51275,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534550706",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129898",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32349725",
			"j_openupdn": 0,
			"n_msvolume": "64608",
			"n_mdvolume": "65042",
			"s_msvolume": "-434",
			"n_mschecnt": 50321,
			"n_mdchecnt": 51274,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534550377",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129897",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32349477",
			"j_openupdn": 0,
			"n_msvolume": "64608",
			"n_mdvolume": "65041",
			"s_msvolume": "-433",
			"n_mschecnt": 50321,
			"n_mdchecnt": 51273,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534550318",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.30",
			"volume": "129896",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32349228",
			"j_openupdn": 0,
			"n_msvolume": "64608",
			"n_mdvolume": "65040",
			"s_msvolume": "-432",
			"n_mschecnt": 50321,
			"n_mdchecnt": 51272,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534550307",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129895",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32348979",
			"j_openupdn": 0,
			"n_msvolume": "64608",
			"n_mdvolume": "65039",
			"s_msvolume": "-431",
			"n_mschecnt": 50321,
			"n_mdchecnt": 51271,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534550306",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129894",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32348730",
			"j_openupdn": 0,
			"n_msvolume": "64607",
			"n_mdvolume": "65039",
			"s_msvolume": "-432",
			"n_mschecnt": 50320,
			"n_mdchecnt": 51271,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534550218",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129893",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32348481",
			"j_openupdn": 0,
			"n_msvolume": "64607",
			"n_mdvolume": "65038",
			"s_msvolume": "-431",
			"n_mschecnt": 50320,
			"n_mdchecnt": 51270,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534550199",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129892",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32348232",
			"j_openupdn": 0,
			"n_msvolume": "64606",
			"n_mdvolume": "65038",
			"s_msvolume": "-432",
			"n_mschecnt": 50319,
			"n_mdchecnt": 51270,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534550186",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129891",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32347984",
			"j_openupdn": 0,
			"n_msvolume": "64606",
			"n_mdvolume": "65037",
			"s_msvolume": "-431",
			"n_mschecnt": 50319,
			"n_mdchecnt": 51269,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534541484",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129890",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32347735",
			"j_openupdn": 0,
			"n_msvolume": "64606",
			"n_mdvolume": "65036",
			"s_msvolume": "-430",
			"n_mschecnt": 50319,
			"n_mdchecnt": 51268,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534534099",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129889",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32347486",
			"j_openupdn": 0,
			"n_msvolume": "64606",
			"n_mdvolume": "65035",
			"s_msvolume": "-429",
			"n_mschecnt": 50319,
			"n_mdchecnt": 51267,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534533397",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129888",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32347237",
			"j_openupdn": 0,
			"n_msvolume": "64605",
			"n_mdvolume": "65035",
			"s_msvolume": "-430",
			"n_mschecnt": 50318,
			"n_mdchecnt": 51267,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534533393",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129887",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32346988",
			"j_openupdn": 0,
			"n_msvolume": "64604",
			"n_mdvolume": "65035",
			"s_msvolume": "-431",
			"n_mschecnt": 50317,
			"n_mdchecnt": 51267,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534531481",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129886",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32346739",
			"j_openupdn": 0,
			"n_msvolume": "64603",
			"n_mdvolume": "65035",
			"s_msvolume": "-432",
			"n_mschecnt": 50316,
			"n_mdchecnt": 51267,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534531124",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 2,
			"chdegree": "99.33",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129885",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32346491",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65035",
			"s_msvolume": "-433",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51267,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534530487",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129883",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32345993",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65033",
			"s_msvolume": "-431",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51266,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534517207",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129882",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32345744",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65032",
			"s_msvolume": "-430",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51265,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534511483",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129881",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32345495",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65031",
			"s_msvolume": "-429",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51264,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534498867",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.30",
			"volume": "129880",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32345246",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65030",
			"s_msvolume": "-428",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51263,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534498108",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 2,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.35",
			"volume": "129879",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32344998",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65029",
			"s_msvolume": "-427",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51262,
			"s_mschecnt": -947
		},
		{
			"chetime": "1534487993",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.55",
			"bidho": "995.35",
			"volume": "129877",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32344500",
			"j_openupdn": 0,
			"n_msvolume": "64602",
			"n_mdvolume": "65027",
			"s_msvolume": "-425",
			"n_mschecnt": 50315,
			"n_mdchecnt": 51261,
			"s_mschecnt": -946
		},
		{
			"chetime": "1534487764",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.30",
			"volume": "129876",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32344251",
			"j_openupdn": 0,
			"n_msvolume": "64601",
			"n_mdvolume": "65027",
			"s_msvolume": "-426",
			"n_mschecnt": 50314,
			"n_mdchecnt": 51261,
			"s_mschecnt": -947
		},
		{
			"chetime": "1534487764",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129875",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32344002",
			"j_openupdn": 0,
			"n_msvolume": "64600",
			"n_mdvolume": "65027",
			"s_msvolume": "-427",
			"n_mschecnt": 50313,
			"n_mdchecnt": 51261,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534487763",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129874",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32343753",
			"j_openupdn": 0,
			"n_msvolume": "64599",
			"n_mdvolume": "65027",
			"s_msvolume": "-428",
			"n_mschecnt": 50312,
			"n_mdchecnt": 51261,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534486345",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 3,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.30",
			"volume": "129873",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32343504",
			"j_openupdn": 0,
			"n_msvolume": "64598",
			"n_mdvolume": "65027",
			"s_msvolume": "-429",
			"n_mschecnt": 50311,
			"n_mdchecnt": 51261,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534486244",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.30",
			"volume": "129870",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32342758",
			"j_openupdn": 0,
			"n_msvolume": "64598",
			"n_mdvolume": "65024",
			"s_msvolume": "-426",
			"n_mschecnt": 50311,
			"n_mdchecnt": 51260,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534486244",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 2,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129869",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32342509",
			"j_openupdn": 0,
			"n_msvolume": "64597",
			"n_mdvolume": "65024",
			"s_msvolume": "-427",
			"n_mschecnt": 50310,
			"n_mdchecnt": 51260,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534486243",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129867",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32342011",
			"j_openupdn": 0,
			"n_msvolume": "64595",
			"n_mdvolume": "65024",
			"s_msvolume": "-429",
			"n_mschecnt": 50309,
			"n_mdchecnt": 51260,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534484853",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.30",
			"volume": "129866",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32341762",
			"j_openupdn": 0,
			"n_msvolume": "64594",
			"n_mdvolume": "65024",
			"s_msvolume": "-430",
			"n_mschecnt": 50308,
			"n_mdchecnt": 51260,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534484456",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.30",
			"volume": "129865",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32341514",
			"j_openupdn": 0,
			"n_msvolume": "64594",
			"n_mdvolume": "65023",
			"s_msvolume": "-429",
			"n_mschecnt": 50308,
			"n_mdchecnt": 51259,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534482300",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 2,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.30",
			"volume": "129864",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32341265",
			"j_openupdn": 0,
			"n_msvolume": "64593",
			"n_mdvolume": "65023",
			"s_msvolume": "-430",
			"n_mschecnt": 50307,
			"n_mdchecnt": 51259,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534482299",
			"price": "995.40",
			"sign": "2",
			"change": "21.45",
			"cvolume": 2,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.40",
			"volume": "129862",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.07",
			"kasis": "-0.28",
			"value": "32340767",
			"j_openupdn": 0,
			"n_msvolume": "64593",
			"n_mdvolume": "65021",
			"s_msvolume": "-428",
			"n_mschecnt": 50307,
			"n_mdchecnt": 51258,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534482271",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 4,
			"chdegree": "99.34",
			"offerho": "995.55",
			"bidho": "995.40",
			"volume": "129860",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32340269",
			"j_openupdn": 0,
			"n_msvolume": "64593",
			"n_mdvolume": "65019",
			"s_msvolume": "-426",
			"n_mschecnt": 50307,
			"n_mdchecnt": 51257,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534482228",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 2,
			"chdegree": "99.35",
			"offerho": "995.60",
			"bidho": "995.50",
			"volume": "129856",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32339274",
			"j_openupdn": 0,
			"n_msvolume": "64593",
			"n_mdvolume": "65015",
			"s_msvolume": "-422",
			"n_mschecnt": 50307,
			"n_mdchecnt": 51256,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534481978",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.60",
			"bidho": "995.50",
			"volume": "129854",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32338776",
			"j_openupdn": 0,
			"n_msvolume": "64593",
			"n_mdvolume": "65013",
			"s_msvolume": "-420",
			"n_mschecnt": 50307,
			"n_mdchecnt": 51255,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534470521",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.65",
			"bidho": "995.50",
			"volume": "129853",
			"openyak": 206876,
			"jnilopenupdn": 6247,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32338527",
			"j_openupdn": -6,
			"n_msvolume": "64592",
			"n_mdvolume": "65013",
			"s_msvolume": "-421",
			"n_mschecnt": 50306,
			"n_mdchecnt": 51255,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534463469",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.50",
			"volume": "129852",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32338278",
			"j_openupdn": 0,
			"n_msvolume": "64591",
			"n_mdvolume": "65013",
			"s_msvolume": "-422",
			"n_mschecnt": 50305,
			"n_mdchecnt": 51255,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534463239",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.55",
			"volume": "129851",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32338029",
			"j_openupdn": 0,
			"n_msvolume": "64590",
			"n_mdvolume": "65013",
			"s_msvolume": "-423",
			"n_mschecnt": 50304,
			"n_mdchecnt": 51255,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534462878",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.50",
			"volume": "129850",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32337780",
			"j_openupdn": 0,
			"n_msvolume": "64590",
			"n_mdvolume": "65012",
			"s_msvolume": "-422",
			"n_mschecnt": 50304,
			"n_mdchecnt": 51254,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534460255",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.50",
			"volume": "129849",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32337532",
			"j_openupdn": 0,
			"n_msvolume": "64589",
			"n_mdvolume": "65012",
			"s_msvolume": "-423",
			"n_mschecnt": 50303,
			"n_mdchecnt": 51254,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534457943",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.65",
			"bidho": "995.50",
			"volume": "129848",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32337283",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65012",
			"s_msvolume": "-424",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51254,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534456852",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.70",
			"bidho": "995.65",
			"volume": "129847",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32337034",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65011",
			"s_msvolume": "-423",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51253,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534456838",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.75",
			"bidho": "995.65",
			"volume": "129846",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32336785",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65010",
			"s_msvolume": "-422",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51252,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534456837",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.75",
			"bidho": "995.65",
			"volume": "129845",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32336536",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65009",
			"s_msvolume": "-421",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51251,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534442059",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.75",
			"bidho": "995.70",
			"volume": "129844",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32336287",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65008",
			"s_msvolume": "-420",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51250,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534442055",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.75",
			"bidho": "995.70",
			"volume": "129843",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32336038",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65007",
			"s_msvolume": "-419",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51249,
			"s_mschecnt": -947
		},
		{
			"chetime": "1534434567",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129842",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32335789",
			"j_openupdn": 0,
			"n_msvolume": "64588",
			"n_mdvolume": "65006",
			"s_msvolume": "-418",
			"n_mschecnt": 50302,
			"n_mdchecnt": 51248,
			"s_mschecnt": -946
		},
		{
			"chetime": "1534433091",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129841",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32335540",
			"j_openupdn": 0,
			"n_msvolume": "64587",
			"n_mdvolume": "65006",
			"s_msvolume": "-419",
			"n_mschecnt": 50301,
			"n_mdchecnt": 51248,
			"s_mschecnt": -947
		},
		{
			"chetime": "1534431200",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129839",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32335042",
			"j_openupdn": 0,
			"n_msvolume": "64587",
			"n_mdvolume": "65004",
			"s_msvolume": "-417",
			"n_mschecnt": 50301,
			"n_mdchecnt": 51247,
			"s_mschecnt": -946
		},
		{
			"chetime": "1534422643",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129838",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32334793",
			"j_openupdn": 0,
			"n_msvolume": "64587",
			"n_mdvolume": "65003",
			"s_msvolume": "-416",
			"n_mschecnt": 50301,
			"n_mdchecnt": 51246,
			"s_mschecnt": -945
		},
		{
			"chetime": "1534421509",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129837",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32334545",
			"j_openupdn": 0,
			"n_msvolume": "64587",
			"n_mdvolume": "65002",
			"s_msvolume": "-415",
			"n_mschecnt": 50301,
			"n_mdchecnt": 51245,
			"s_mschecnt": -944
		},
		{
			"chetime": "1534420261",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129836",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32334296",
			"j_openupdn": 0,
			"n_msvolume": "64587",
			"n_mdvolume": "65001",
			"s_msvolume": "-414",
			"n_mschecnt": 50301,
			"n_mdchecnt": 51244,
			"s_mschecnt": -943
		},
		{
			"chetime": "1534420252",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129835",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32334047",
			"j_openupdn": 0,
			"n_msvolume": "64587",
			"n_mdvolume": "65000",
			"s_msvolume": "-413",
			"n_mschecnt": 50301,
			"n_mdchecnt": 51243,
			"s_mschecnt": -942
		},
		{
			"chetime": "1534410799",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129834",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32333798",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "65000",
			"s_msvolume": "-414",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51243,
			"s_mschecnt": -943
		},
		{
			"chetime": "1534405927",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129833",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32333549",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64999",
			"s_msvolume": "-413",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51242,
			"s_mschecnt": -942
		},
		{
			"chetime": "1534402028",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.37",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129832",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32333300",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64998",
			"s_msvolume": "-412",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51241,
			"s_mschecnt": -941
		},
		{
			"chetime": "1534400291",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129830",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32332802",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64996",
			"s_msvolume": "-410",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51240,
			"s_mschecnt": -940
		},
		{
			"chetime": "1534385022",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.80",
			"bidho": "995.75",
			"volume": "129829",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32332553",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64995",
			"s_msvolume": "-409",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51239,
			"s_mschecnt": -939
		},
		{
			"chetime": "1534384981",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.80",
			"bidho": "995.75",
			"volume": "129828",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32332304",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64994",
			"s_msvolume": "-408",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51238,
			"s_mschecnt": -938
		},
		{
			"chetime": "1534383240",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.37",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129827",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32332055",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64993",
			"s_msvolume": "-407",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51237,
			"s_mschecnt": -937
		},
		{
			"chetime": "1534369801",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129825",
			"openyak": 206882,
			"jnilopenupdn": 6253,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32331557",
			"j_openupdn": 15,
			"n_msvolume": "64586",
			"n_mdvolume": "64991",
			"s_msvolume": "-405",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51236,
			"s_mschecnt": -936
		},
		{
			"chetime": "1534367133",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.70",
			"volume": "129824",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32331308",
			"j_openupdn": 0,
			"n_msvolume": "64586",
			"n_mdvolume": "64990",
			"s_msvolume": "-404",
			"n_mschecnt": 50300,
			"n_mdchecnt": 51235,
			"s_mschecnt": -935
		},
		{
			"chetime": "1534359806",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.70",
			"volume": "129823",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32331059",
			"j_openupdn": 0,
			"n_msvolume": "64585",
			"n_mdvolume": "64990",
			"s_msvolume": "-405",
			"n_mschecnt": 50299,
			"n_mdchecnt": 51235,
			"s_mschecnt": -936
		},
		{
			"chetime": "1534356361",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 5,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.70",
			"volume": "129822",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32330810",
			"j_openupdn": 0,
			"n_msvolume": "64584",
			"n_mdvolume": "64990",
			"s_msvolume": "-406",
			"n_mschecnt": 50298,
			"n_mdchecnt": 51235,
			"s_mschecnt": -937
		},
		{
			"chetime": "1534353215",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.80",
			"volume": "129817",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32329566",
			"j_openupdn": 0,
			"n_msvolume": "64584",
			"n_mdvolume": "64985",
			"s_msvolume": "-401",
			"n_mschecnt": 50298,
			"n_mdchecnt": 51234,
			"s_mschecnt": -936
		},
		{
			"chetime": "1534351035",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 2,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.80",
			"volume": "129816",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32329317",
			"j_openupdn": 0,
			"n_msvolume": "64583",
			"n_mdvolume": "64985",
			"s_msvolume": "-402",
			"n_mschecnt": 50297,
			"n_mdchecnt": 51234,
			"s_mschecnt": -937
		},
		{
			"chetime": "1534331092",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.70",
			"volume": "129814",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32328819",
			"j_openupdn": 0,
			"n_msvolume": "64581",
			"n_mdvolume": "64985",
			"s_msvolume": "-404",
			"n_mschecnt": 50296,
			"n_mdchecnt": 51234,
			"s_mschecnt": -938
		},
		{
			"chetime": "1534331092",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129813",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32328570",
			"j_openupdn": 0,
			"n_msvolume": "64580",
			"n_mdvolume": "64985",
			"s_msvolume": "-405",
			"n_mschecnt": 50295,
			"n_mdchecnt": 51234,
			"s_mschecnt": -939
		},
		{
			"chetime": "1534325202",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129812",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32328321",
			"j_openupdn": 0,
			"n_msvolume": "64579",
			"n_mdvolume": "64985",
			"s_msvolume": "-406",
			"n_mschecnt": 50294,
			"n_mdchecnt": 51234,
			"s_mschecnt": -940
		},
		{
			"chetime": "1534325202",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129811",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32328072",
			"j_openupdn": 0,
			"n_msvolume": "64579",
			"n_mdvolume": "64984",
			"s_msvolume": "-405",
			"n_mschecnt": 50294,
			"n_mdchecnt": 51233,
			"s_mschecnt": -939
		},
		{
			"chetime": "1534325202",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129810",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32327823",
			"j_openupdn": 0,
			"n_msvolume": "64579",
			"n_mdvolume": "64983",
			"s_msvolume": "-404",
			"n_mschecnt": 50294,
			"n_mdchecnt": 51232,
			"s_mschecnt": -938
		},
		{
			"chetime": "1534325202",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.75",
			"volume": "129809",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32327574",
			"j_openupdn": 0,
			"n_msvolume": "64579",
			"n_mdvolume": "64982",
			"s_msvolume": "-403",
			"n_mschecnt": 50294,
			"n_mdchecnt": 51231,
			"s_mschecnt": -937
		},
		{
			"chetime": "1534324887",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129808",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32327325",
			"j_openupdn": 0,
			"n_msvolume": "64579",
			"n_mdvolume": "64981",
			"s_msvolume": "-402",
			"n_mschecnt": 50294,
			"n_mdchecnt": 51230,
			"s_mschecnt": -936
		},
		{
			"chetime": "1534322826",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129807",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32327076",
			"j_openupdn": 0,
			"n_msvolume": "64578",
			"n_mdvolume": "64981",
			"s_msvolume": "-403",
			"n_mschecnt": 50293,
			"n_mdchecnt": 51230,
			"s_mschecnt": -937
		},
		{
			"chetime": "1534316256",
			"price": "995.85",
			"sign": "2",
			"change": "21.90",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129806",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.52",
			"kasis": "-0.23",
			"value": "32326827",
			"j_openupdn": 0,
			"n_msvolume": "64577",
			"n_mdvolume": "64981",
			"s_msvolume": "-404",
			"n_mschecnt": 50292,
			"n_mdchecnt": 51230,
			"s_mschecnt": -938
		},
		{
			"chetime": "1534295160",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.70",
			"volume": "129805",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32326578",
			"j_openupdn": 0,
			"n_msvolume": "64576",
			"n_mdvolume": "64981",
			"s_msvolume": "-405",
			"n_mschecnt": 50291,
			"n_mdchecnt": 51230,
			"s_mschecnt": -939
		},
		{
			"chetime": "1534288330",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.65",
			"volume": "129803",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32326080",
			"j_openupdn": 0,
			"n_msvolume": "64576",
			"n_mdvolume": "64979",
			"s_msvolume": "-403",
			"n_mschecnt": 50291,
			"n_mdchecnt": 51229,
			"s_mschecnt": -938
		},
		{
			"chetime": "1534285793",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.85",
			"bidho": "995.65",
			"volume": "129802",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32325832",
			"j_openupdn": 0,
			"n_msvolume": "64576",
			"n_mdvolume": "64978",
			"s_msvolume": "-402",
			"n_mschecnt": 50291,
			"n_mdchecnt": 51228,
			"s_mschecnt": -937
		},
		{
			"chetime": "1534285625",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.80",
			"bidho": "995.60",
			"volume": "129801",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32325583",
			"j_openupdn": 0,
			"n_msvolume": "64575",
			"n_mdvolume": "64978",
			"s_msvolume": "-403",
			"n_mschecnt": 50290,
			"n_mdchecnt": 51228,
			"s_mschecnt": -938
		},
		{
			"chetime": "1534285123",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.75",
			"bidho": "995.60",
			"volume": "129800",
			"openyak": 206867,
			"jnilopenupdn": 6238,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32325334",
			"j_openupdn": -6,
			"n_msvolume": "64574",
			"n_mdvolume": "64978",
			"s_msvolume": "-404",
			"n_mschecnt": 50289,
			"n_mdchecnt": 51228,
			"s_mschecnt": -939
		},
		{
			"chetime": "1534268660",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.38",
			"offerho": "995.70",
			"bidho": "995.60",
			"volume": "129799",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32325085",
			"j_openupdn": 0,
			"n_msvolume": "64573",
			"n_mdvolume": "64978",
			"s_msvolume": "-405",
			"n_mschecnt": 50288,
			"n_mdchecnt": 51228,
			"s_mschecnt": -940
		},
		{
			"chetime": "1534268659",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 2,
			"chdegree": "99.38",
			"offerho": "995.70",
			"bidho": "995.60",
			"volume": "129798",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32324836",
			"j_openupdn": 0,
			"n_msvolume": "64572",
			"n_mdvolume": "64978",
			"s_msvolume": "-406",
			"n_mschecnt": 50287,
			"n_mdchecnt": 51228,
			"s_mschecnt": -941
		},
		{
			"chetime": "1534268659",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 2,
			"chdegree": "99.37",
			"offerho": "995.65",
			"bidho": "995.60",
			"volume": "129796",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32324338",
			"j_openupdn": 0,
			"n_msvolume": "64570",
			"n_mdvolume": "64978",
			"s_msvolume": "-408",
			"n_mschecnt": 50286,
			"n_mdchecnt": 51228,
			"s_mschecnt": -942
		},
		{
			"chetime": "1534263877",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.65",
			"bidho": "995.55",
			"volume": "129794",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32323840",
			"j_openupdn": 0,
			"n_msvolume": "64568",
			"n_mdvolume": "64978",
			"s_msvolume": "-410",
			"n_mschecnt": 50285,
			"n_mdchecnt": 51228,
			"s_mschecnt": -943
		},
		{
			"chetime": "1534263873",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.60",
			"bidho": "995.55",
			"volume": "129793",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32323591",
			"j_openupdn": 0,
			"n_msvolume": "64567",
			"n_mdvolume": "64978",
			"s_msvolume": "-411",
			"n_mschecnt": 50284,
			"n_mdchecnt": 51228,
			"s_mschecnt": -944
		},
		{
			"chetime": "1534258230",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.60",
			"bidho": "995.55",
			"volume": "129792",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32323342",
			"j_openupdn": 0,
			"n_msvolume": "64566",
			"n_mdvolume": "64978",
			"s_msvolume": "-412",
			"n_mschecnt": 50283,
			"n_mdchecnt": 51228,
			"s_mschecnt": -945
		},
		{
			"chetime": "1534257270",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 3,
			"chdegree": "99.37",
			"offerho": "995.60",
			"bidho": "995.55",
			"volume": "129791",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32323093",
			"j_openupdn": 0,
			"n_msvolume": "64566",
			"n_mdvolume": "64977",
			"s_msvolume": "-411",
			"n_mschecnt": 50283,
			"n_mdchecnt": 51227,
			"s_mschecnt": -944
		},
		{
			"chetime": "1534257201",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.60",
			"bidho": "995.55",
			"volume": "129788",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32322347",
			"j_openupdn": 0,
			"n_msvolume": "64566",
			"n_mdvolume": "64974",
			"s_msvolume": "-408",
			"n_mschecnt": 50283,
			"n_mdchecnt": 51226,
			"s_mschecnt": -943
		},
		{
			"chetime": "1534253100",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.55",
			"bidho": "995.45",
			"volume": "129787",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32322098",
			"j_openupdn": 0,
			"n_msvolume": "64565",
			"n_mdvolume": "64974",
			"s_msvolume": "-409",
			"n_mschecnt": 50282,
			"n_mdchecnt": 51226,
			"s_mschecnt": -944
		},
		{
			"chetime": "1534253100",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.50",
			"bidho": "995.45",
			"volume": "129786",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32321849",
			"j_openupdn": 0,
			"n_msvolume": "64564",
			"n_mdvolume": "64974",
			"s_msvolume": "-410",
			"n_mschecnt": 50281,
			"n_mdchecnt": 51226,
			"s_mschecnt": -945
		},
		{
			"chetime": "1534253100",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.50",
			"bidho": "995.45",
			"volume": "129785",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32321600",
			"j_openupdn": 0,
			"n_msvolume": "64563",
			"n_mdvolume": "64974",
			"s_msvolume": "-411",
			"n_mschecnt": 50280,
			"n_mdchecnt": 51226,
			"s_mschecnt": -946
		},
		{
			"chetime": "1534253093",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.37",
			"offerho": "995.50",
			"bidho": "995.40",
			"volume": "129784",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32321351",
			"j_openupdn": 0,
			"n_msvolume": "64562",
			"n_mdvolume": "64974",
			"s_msvolume": "-412",
			"n_mschecnt": 50279,
			"n_mdchecnt": 51226,
			"s_mschecnt": -947
		},
		{
			"chetime": "1534226619",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.50",
			"bidho": "995.40",
			"volume": "129783",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32321102",
			"j_openupdn": 0,
			"n_msvolume": "64561",
			"n_mdvolume": "64974",
			"s_msvolume": "-413",
			"n_mschecnt": 50278,
			"n_mdchecnt": 51226,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534226619",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129782",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32320854",
			"j_openupdn": 0,
			"n_msvolume": "64560",
			"n_mdvolume": "64974",
			"s_msvolume": "-414",
			"n_mschecnt": 50277,
			"n_mdchecnt": 51226,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534226618",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.36",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129781",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32320605",
			"j_openupdn": 0,
			"n_msvolume": "64559",
			"n_mdvolume": "64974",
			"s_msvolume": "-415",
			"n_mschecnt": 50276,
			"n_mdchecnt": 51226,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534226615",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 4,
			"chdegree": "99.36",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129780",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32320356",
			"j_openupdn": 0,
			"n_msvolume": "64558",
			"n_mdvolume": "64974",
			"s_msvolume": "-416",
			"n_mschecnt": 50275,
			"n_mdchecnt": 51226,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534224516",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129776",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32319360",
			"j_openupdn": 0,
			"n_msvolume": "64554",
			"n_mdvolume": "64974",
			"s_msvolume": "-420",
			"n_mschecnt": 50274,
			"n_mdchecnt": 51226,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534217579",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129775",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32319112",
			"j_openupdn": 0,
			"n_msvolume": "64553",
			"n_mdvolume": "64974",
			"s_msvolume": "-421",
			"n_mschecnt": 50273,
			"n_mdchecnt": 51226,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534208668",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 3,
			"chdegree": "99.35",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129774",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32318863",
			"j_openupdn": 0,
			"n_msvolume": "64553",
			"n_mdvolume": "64973",
			"s_msvolume": "-420",
			"n_mschecnt": 50273,
			"n_mdchecnt": 51225,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534206113",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129771",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32318116",
			"j_openupdn": 0,
			"n_msvolume": "64550",
			"n_mdvolume": "64973",
			"s_msvolume": "-423",
			"n_mschecnt": 50272,
			"n_mdchecnt": 51225,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534193621",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129770",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32317867",
			"j_openupdn": 0,
			"n_msvolume": "64549",
			"n_mdvolume": "64973",
			"s_msvolume": "-424",
			"n_mschecnt": 50271,
			"n_mdchecnt": 51225,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534188800",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.55",
			"bidho": "995.35",
			"volume": "129769",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32317618",
			"j_openupdn": 0,
			"n_msvolume": "64548",
			"n_mdvolume": "64973",
			"s_msvolume": "-425",
			"n_mschecnt": 50270,
			"n_mdchecnt": 51225,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534187098",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129768",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32317370",
			"j_openupdn": 0,
			"n_msvolume": "64548",
			"n_mdvolume": "64972",
			"s_msvolume": "-424",
			"n_mschecnt": 50270,
			"n_mdchecnt": 51224,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534187098",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 4,
			"chdegree": "99.35",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129767",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32317121",
			"j_openupdn": 0,
			"n_msvolume": "64547",
			"n_mdvolume": "64972",
			"s_msvolume": "-425",
			"n_mschecnt": 50269,
			"n_mdchecnt": 51224,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534186478",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129763",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32316125",
			"j_openupdn": 0,
			"n_msvolume": "64543",
			"n_mdvolume": "64972",
			"s_msvolume": "-429",
			"n_mschecnt": 50268,
			"n_mdchecnt": 51224,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534179505",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129762",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32315876",
			"j_openupdn": 0,
			"n_msvolume": "64543",
			"n_mdvolume": "64971",
			"s_msvolume": "-428",
			"n_mschecnt": 50268,
			"n_mdchecnt": 51223,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534176922",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.35",
			"volume": "129761",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32315627",
			"j_openupdn": 0,
			"n_msvolume": "64542",
			"n_mdvolume": "64971",
			"s_msvolume": "-429",
			"n_mschecnt": 50267,
			"n_mdchecnt": 51223,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534176163",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 3,
			"chdegree": "99.34",
			"offerho": "995.50",
			"bidho": "995.45",
			"volume": "129760",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32315379",
			"j_openupdn": 0,
			"n_msvolume": "64542",
			"n_mdvolume": "64970",
			"s_msvolume": "-428",
			"n_mschecnt": 50267,
			"n_mdchecnt": 51222,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534176095",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.50",
			"bidho": "995.45",
			"volume": "129757",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32314632",
			"j_openupdn": 0,
			"n_msvolume": "64542",
			"n_mdvolume": "64967",
			"s_msvolume": "-425",
			"n_mschecnt": 50267,
			"n_mdchecnt": 51221,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534175617",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 3,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129756",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32314383",
			"j_openupdn": 0,
			"n_msvolume": "64541",
			"n_mdvolume": "64967",
			"s_msvolume": "-426",
			"n_mschecnt": 50266,
			"n_mdchecnt": 51221,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534169866",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.25",
			"volume": "129753",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32313637",
			"j_openupdn": 0,
			"n_msvolume": "64538",
			"n_mdvolume": "64967",
			"s_msvolume": "-429",
			"n_mschecnt": 50265,
			"n_mdchecnt": 51221,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534169671",
			"price": "995.25",
			"sign": "2",
			"change": "21.30",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.25",
			"volume": "129752",
			"openyak": 206873,
			"jnilopenupdn": 6244,
			"ibasis": "2.85",
			"sbasis": "-0.08",
			"kasis": "-0.29",
			"value": "32313388",
			"j_openupdn": 14,
			"n_msvolume": "64537",
			"n_mdvolume": "64967",
			"s_msvolume": "-430",
			"n_mschecnt": 50264,
			"n_mdchecnt": 51221,
			"s_mschecnt": -957
		},
		{
			"chetime": "1534166743",
			"price": "995.40",
			"sign": "2",
			"change": "21.45",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129751",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.07",
			"kasis": "-0.28",
			"value": "32313139",
			"j_openupdn": 0,
			"n_msvolume": "64537",
			"n_mdvolume": "64966",
			"s_msvolume": "-429",
			"n_mschecnt": 50264,
			"n_mdchecnt": 51220,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534166733",
			"price": "995.40",
			"sign": "2",
			"change": "21.45",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.40",
			"volume": "129750",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.07",
			"kasis": "-0.28",
			"value": "32312890",
			"j_openupdn": 0,
			"n_msvolume": "64537",
			"n_mdvolume": "64965",
			"s_msvolume": "-428",
			"n_mschecnt": 50264,
			"n_mdchecnt": 51219,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534166732",
			"price": "995.40",
			"sign": "2",
			"change": "21.45",
			"cvolume": 2,
			"chdegree": "99.34",
			"offerho": "995.40",
			"bidho": "995.25",
			"volume": "129749",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.07",
			"kasis": "-0.28",
			"value": "32312641",
			"j_openupdn": 0,
			"n_msvolume": "64536",
			"n_mdvolume": "64965",
			"s_msvolume": "-429",
			"n_mschecnt": 50263,
			"n_mdchecnt": 51219,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534162145",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.25",
			"volume": "129747",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32312144",
			"j_openupdn": 0,
			"n_msvolume": "64534",
			"n_mdvolume": "64965",
			"s_msvolume": "-431",
			"n_mschecnt": 50262,
			"n_mdchecnt": 51219,
			"s_mschecnt": -957
		},
		{
			"chetime": "1534161936",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129746",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32311895",
			"j_openupdn": 0,
			"n_msvolume": "64534",
			"n_mdvolume": "64964",
			"s_msvolume": "-430",
			"n_mschecnt": 50262,
			"n_mdchecnt": 51218,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534160986",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129745",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32311646",
			"j_openupdn": 0,
			"n_msvolume": "64534",
			"n_mdvolume": "64963",
			"s_msvolume": "-429",
			"n_mschecnt": 50262,
			"n_mdchecnt": 51217,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534160115",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129744",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32311397",
			"j_openupdn": 0,
			"n_msvolume": "64534",
			"n_mdvolume": "64962",
			"s_msvolume": "-428",
			"n_mschecnt": 50262,
			"n_mdchecnt": 51216,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534158801",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.30",
			"bidho": "995.25",
			"volume": "129743",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32311148",
			"j_openupdn": 0,
			"n_msvolume": "64533",
			"n_mdvolume": "64962",
			"s_msvolume": "-429",
			"n_mschecnt": 50261,
			"n_mdchecnt": 51216,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534157737",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.30",
			"bidho": "995.25",
			"volume": "129742",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32310899",
			"j_openupdn": 0,
			"n_msvolume": "64532",
			"n_mdvolume": "64962",
			"s_msvolume": "-430",
			"n_mschecnt": 50260,
			"n_mdchecnt": 51216,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534156844",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.25",
			"volume": "129741",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32310651",
			"j_openupdn": 0,
			"n_msvolume": "64531",
			"n_mdvolume": "64962",
			"s_msvolume": "-431",
			"n_mschecnt": 50259,
			"n_mdchecnt": 51216,
			"s_mschecnt": -957
		},
		{
			"chetime": "1534156844",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129740",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32310402",
			"j_openupdn": 0,
			"n_msvolume": "64531",
			"n_mdvolume": "64961",
			"s_msvolume": "-430",
			"n_mschecnt": 50259,
			"n_mdchecnt": 51215,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534147110",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129739",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32310153",
			"j_openupdn": 0,
			"n_msvolume": "64531",
			"n_mdvolume": "64960",
			"s_msvolume": "-429",
			"n_mschecnt": 50259,
			"n_mdchecnt": 51214,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534146582",
			"price": "995.30",
			"sign": "2",
			"change": "21.35",
			"cvolume": 3,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129738",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "-0.03",
			"kasis": "-0.29",
			"value": "32309904",
			"j_openupdn": 0,
			"n_msvolume": "64530",
			"n_mdvolume": "64960",
			"s_msvolume": "-430",
			"n_mschecnt": 50258,
			"n_mdchecnt": 51214,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534146246",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129735",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32309158",
			"j_openupdn": 0,
			"n_msvolume": "64530",
			"n_mdvolume": "64957",
			"s_msvolume": "-427",
			"n_mschecnt": 50258,
			"n_mdchecnt": 51213,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534145877",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.35",
			"volume": "129734",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32308909",
			"j_openupdn": 0,
			"n_msvolume": "64530",
			"n_mdvolume": "64956",
			"s_msvolume": "-426",
			"n_mschecnt": 50258,
			"n_mdchecnt": 51212,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534145363",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 1,
			"chdegree": "99.35",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129733",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32308660",
			"j_openupdn": 0,
			"n_msvolume": "64530",
			"n_mdvolume": "64955",
			"s_msvolume": "-425",
			"n_mschecnt": 50258,
			"n_mdchecnt": 51211,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534145354",
			"price": "995.40",
			"sign": "2",
			"change": "21.45",
			"cvolume": 2,
			"chdegree": "99.34",
			"offerho": "995.45",
			"bidho": "995.30",
			"volume": "129732",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.07",
			"kasis": "-0.28",
			"value": "32308411",
			"j_openupdn": 0,
			"n_msvolume": "64529",
			"n_mdvolume": "64955",
			"s_msvolume": "-426",
			"n_mschecnt": 50257,
			"n_mdchecnt": 51211,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534145351",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.40",
			"bidho": "995.30",
			"volume": "129730",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32307913",
			"j_openupdn": 0,
			"n_msvolume": "64527",
			"n_mdvolume": "64955",
			"s_msvolume": "-428",
			"n_mschecnt": 50256,
			"n_mdchecnt": 51211,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534145350",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129729",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32307664",
			"j_openupdn": 0,
			"n_msvolume": "64526",
			"n_mdvolume": "64955",
			"s_msvolume": "-429",
			"n_mschecnt": 50255,
			"n_mdchecnt": 51211,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534145350",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129728",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32307416",
			"j_openupdn": 0,
			"n_msvolume": "64525",
			"n_mdvolume": "64955",
			"s_msvolume": "-430",
			"n_mschecnt": 50254,
			"n_mdchecnt": 51211,
			"s_mschecnt": -957
		},
		{
			"chetime": "1534145343",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.34",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129727",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32307167",
			"j_openupdn": 0,
			"n_msvolume": "64524",
			"n_mdvolume": "64955",
			"s_msvolume": "-431",
			"n_mschecnt": 50253,
			"n_mdchecnt": 51211,
			"s_mschecnt": -958
		},
		{
			"chetime": "1534145338",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.60",
			"bidho": "995.30",
			"volume": "129726",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32306918",
			"j_openupdn": 0,
			"n_msvolume": "64523",
			"n_mdvolume": "64955",
			"s_msvolume": "-432",
			"n_mschecnt": 50252,
			"n_mdchecnt": 51211,
			"s_mschecnt": -959
		},
		{
			"chetime": "1534145312",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 1,
			"chdegree": "99.33",
			"offerho": "995.35",
			"bidho": "995.30",
			"volume": "129725",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32306669",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64955",
			"s_msvolume": "-433",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51211,
			"s_mschecnt": -960
		},
		{
			"chetime": "1534145178",
			"price": "995.35",
			"sign": "2",
			"change": "21.40",
			"cvolume": 6,
			"chdegree": "99.33",
			"offerho": "995.85",
			"bidho": "995.30",
			"volume": "129724",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.02",
			"kasis": "-0.28",
			"value": "32306420",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64954",
			"s_msvolume": "-432",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51210,
			"s_mschecnt": -959
		},
		{
			"chetime": "1534145177",
			"price": "995.40",
			"sign": "2",
			"change": "21.45",
			"cvolume": 6,
			"chdegree": "99.34",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129718",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.07",
			"kasis": "-0.28",
			"value": "32304927",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64948",
			"s_msvolume": "-426",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51209,
			"s_mschecnt": -958
		},
		{
			"chetime": "1534145177",
			"price": "995.45",
			"sign": "2",
			"change": "21.50",
			"cvolume": 8,
			"chdegree": "99.35",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129712",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.12",
			"kasis": "-0.27",
			"value": "32303434",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64942",
			"s_msvolume": "-420",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51208,
			"s_mschecnt": -957
		},
		{
			"chetime": "1534145176",
			"price": "995.50",
			"sign": "2",
			"change": "21.55",
			"cvolume": 18,
			"chdegree": "99.37",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129704",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.17",
			"kasis": "-0.27",
			"value": "32301443",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64934",
			"s_msvolume": "-412",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51207,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534145175",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 10,
			"chdegree": "99.39",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129686",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32296964",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64916",
			"s_msvolume": "-394",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51206,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534145175",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 6,
			"chdegree": "99.41",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129676",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32294475",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64906",
			"s_msvolume": "-384",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51205,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534145175",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 10,
			"chdegree": "99.42",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129670",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32292981",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64900",
			"s_msvolume": "-378",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51204,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534145174",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 6,
			"chdegree": "99.43",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129660",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32290492",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64890",
			"s_msvolume": "-368",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51203,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534145173",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 3,
			"chdegree": "99.44",
			"offerho": "995.85",
			"bidho": "995.75",
			"volume": "129654",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32288999",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64884",
			"s_msvolume": "-362",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51202,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534144624",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 2,
			"chdegree": "99.45",
			"offerho": "995.85",
			"bidho": "995.70",
			"volume": "129651",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32288252",
			"j_openupdn": 0,
			"n_msvolume": "64522",
			"n_mdvolume": "64881",
			"s_msvolume": "-359",
			"n_mschecnt": 50251,
			"n_mdchecnt": 51201,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534144623",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129649",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32287754",
			"j_openupdn": 0,
			"n_msvolume": "64520",
			"n_mdvolume": "64881",
			"s_msvolume": "-361",
			"n_mschecnt": 50250,
			"n_mdchecnt": 51201,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534144623",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129648",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32287505",
			"j_openupdn": 0,
			"n_msvolume": "64519",
			"n_mdvolume": "64881",
			"s_msvolume": "-362",
			"n_mschecnt": 50249,
			"n_mdchecnt": 51201,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534144623",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129647",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32287256",
			"j_openupdn": 0,
			"n_msvolume": "64518",
			"n_mdvolume": "64881",
			"s_msvolume": "-363",
			"n_mschecnt": 50248,
			"n_mdchecnt": 51201,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534144623",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129646",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32287007",
			"j_openupdn": 0,
			"n_msvolume": "64517",
			"n_mdvolume": "64881",
			"s_msvolume": "-364",
			"n_mschecnt": 50247,
			"n_mdchecnt": 51201,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534144619",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129645",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32286758",
			"j_openupdn": 0,
			"n_msvolume": "64516",
			"n_mdvolume": "64881",
			"s_msvolume": "-365",
			"n_mschecnt": 50246,
			"n_mdchecnt": 51201,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534123488",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.60",
			"volume": "129644",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32286509",
			"j_openupdn": 0,
			"n_msvolume": "64515",
			"n_mdvolume": "64881",
			"s_msvolume": "-366",
			"n_mschecnt": 50245,
			"n_mdchecnt": 51201,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534123110",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129643",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32286260",
			"j_openupdn": 0,
			"n_msvolume": "64515",
			"n_mdvolume": "64880",
			"s_msvolume": "-365",
			"n_mschecnt": 50245,
			"n_mdchecnt": 51200,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534123093",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129641",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32285762",
			"j_openupdn": 0,
			"n_msvolume": "64515",
			"n_mdvolume": "64878",
			"s_msvolume": "-363",
			"n_mschecnt": 50245,
			"n_mdchecnt": 51199,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534123044",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.44",
			"offerho": "995.75",
			"bidho": "995.70",
			"volume": "129640",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32285513",
			"j_openupdn": 0,
			"n_msvolume": "64514",
			"n_mdvolume": "64878",
			"s_msvolume": "-364",
			"n_mschecnt": 50244,
			"n_mdchecnt": 51199,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534119207",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.70",
			"bidho": "995.60",
			"volume": "129638",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32285016",
			"j_openupdn": 0,
			"n_msvolume": "64512",
			"n_mdvolume": "64878",
			"s_msvolume": "-366",
			"n_mschecnt": 50243,
			"n_mdchecnt": 51199,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534113092",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 3,
			"chdegree": "99.43",
			"offerho": "995.70",
			"bidho": "995.65",
			"volume": "129637",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32284767",
			"j_openupdn": 0,
			"n_msvolume": "64511",
			"n_mdvolume": "64878",
			"s_msvolume": "-367",
			"n_mschecnt": 50242,
			"n_mdchecnt": 51199,
			"s_mschecnt": -957
		},
		{
			"chetime": "1534112796",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.70",
			"volume": "129634",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32284020",
			"j_openupdn": 0,
			"n_msvolume": "64511",
			"n_mdvolume": "64875",
			"s_msvolume": "-364",
			"n_mschecnt": 50242,
			"n_mdchecnt": 51198,
			"s_mschecnt": -956
		},
		{
			"chetime": "1534107681",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129632",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32283522",
			"j_openupdn": 0,
			"n_msvolume": "64511",
			"n_mdvolume": "64873",
			"s_msvolume": "-362",
			"n_mschecnt": 50242,
			"n_mdchecnt": 51197,
			"s_mschecnt": -955
		},
		{
			"chetime": "1534106596",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129631",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32283273",
			"j_openupdn": 0,
			"n_msvolume": "64511",
			"n_mdvolume": "64872",
			"s_msvolume": "-361",
			"n_mschecnt": 50242,
			"n_mdchecnt": 51196,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534106337",
			"price": "995.75",
			"sign": "2",
			"change": "21.80",
			"cvolume": 1,
			"chdegree": "99.45",
			"offerho": "995.80",
			"bidho": "995.75",
			"volume": "129630",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.42",
			"kasis": "-0.24",
			"value": "32283024",
			"j_openupdn": 0,
			"n_msvolume": "64511",
			"n_mdvolume": "64871",
			"s_msvolume": "-360",
			"n_mschecnt": 50242,
			"n_mdchecnt": 51195,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534106249",
			"price": "995.80",
			"sign": "2",
			"change": "21.85",
			"cvolume": 2,
			"chdegree": "99.45",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129629",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.47",
			"kasis": "-0.24",
			"value": "32282775",
			"j_openupdn": 0,
			"n_msvolume": "64511",
			"n_mdvolume": "64870",
			"s_msvolume": "-359",
			"n_mschecnt": 50242,
			"n_mdchecnt": 51194,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534105357",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 2,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.60",
			"volume": "129627",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32282277",
			"j_openupdn": 0,
			"n_msvolume": "64509",
			"n_mdvolume": "64870",
			"s_msvolume": "-361",
			"n_mschecnt": 50241,
			"n_mdchecnt": 51194,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534103139",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.70",
			"bidho": "995.55",
			"volume": "129625",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32281779",
			"j_openupdn": 0,
			"n_msvolume": "64507",
			"n_mdvolume": "64870",
			"s_msvolume": "-363",
			"n_mschecnt": 50240,
			"n_mdchecnt": 51194,
			"s_mschecnt": -954
		},
		{
			"chetime": "1534102467",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.70",
			"bidho": "995.60",
			"volume": "129624",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32281531",
			"j_openupdn": 0,
			"n_msvolume": "64507",
			"n_mdvolume": "64869",
			"s_msvolume": "-362",
			"n_mschecnt": 50240,
			"n_mdchecnt": 51193,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534101998",
			"price": "995.70",
			"sign": "2",
			"change": "21.75",
			"cvolume": 5,
			"chdegree": "99.44",
			"offerho": "995.70",
			"bidho": "995.55",
			"volume": "129623",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.37",
			"kasis": "-0.25",
			"value": "32281282",
			"j_openupdn": 0,
			"n_msvolume": "64507",
			"n_mdvolume": "64868",
			"s_msvolume": "-361",
			"n_mschecnt": 50240,
			"n_mdchecnt": 51192,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534098850",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.70",
			"bidho": "995.55",
			"volume": "129618",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32280037",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64868",
			"s_msvolume": "-366",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51192,
			"s_mschecnt": -953
		},
		{
			"chetime": "1534084545",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.55",
			"volume": "129617",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32279788",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64867",
			"s_msvolume": "-365",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51191,
			"s_mschecnt": -952
		},
		{
			"chetime": "1534082712",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 4,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.55",
			"volume": "129616",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32279539",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64866",
			"s_msvolume": "-364",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51190,
			"s_mschecnt": -951
		},
		{
			"chetime": "1534082190",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 2,
			"chdegree": "99.44",
			"offerho": "995.80",
			"bidho": "995.55",
			"volume": "129612",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32278544",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64862",
			"s_msvolume": "-360",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51189,
			"s_mschecnt": -950
		},
		{
			"chetime": "1534082189",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.45",
			"offerho": "995.80",
			"bidho": "995.60",
			"volume": "129610",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32278046",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64860",
			"s_msvolume": "-358",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51188,
			"s_mschecnt": -949
		},
		{
			"chetime": "1534075314",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 1,
			"chdegree": "99.45",
			"offerho": "995.80",
			"bidho": "995.55",
			"volume": "129609",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32277797",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64859",
			"s_msvolume": "-357",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51187,
			"s_mschecnt": -948
		},
		{
			"chetime": "1534070085",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 4,
			"chdegree": "99.45",
			"offerho": "995.80",
			"bidho": "995.60",
			"volume": "129608",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32277548",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64858",
			"s_msvolume": "-356",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51186,
			"s_mschecnt": -947
		},
		{
			"chetime": "1534070081",
			"price": "995.65",
			"sign": "2",
			"change": "21.70",
			"cvolume": 1,
			"chdegree": "99.46",
			"offerho": "995.80",
			"bidho": "995.65",
			"volume": "129604",
			"openyak": 206859,
			"jnilopenupdn": 6230,
			"ibasis": "2.85",
			"sbasis": "0.32",
			"kasis": "-0.25",
			"value": "32276552",
			"j_openupdn": 17,
			"n_msvolume": "64502",
			"n_mdvolume": "64854",
			"s_msvolume": "-352",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51185,
			"s_mschecnt": -946
		},
		{
			"chetime": "1534065920",
			"price": "995.60",
			"sign": "2",
			"change": "21.65",
			"cvolume": 2,
			"chdegree": "99.46",
			"offerho": "995.80",
			"bidho": "995.55",
			"volume": "129603",
			"openyak": 206842,
			"jnilopenupdn": 6213,
			"ibasis": "2.85",
			"sbasis": "0.27",
			"kasis": "-0.26",
			"value": "32276304",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64853",
			"s_msvolume": "-351",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51184,
			"s_mschecnt": -945
		},
		{
			"chetime": "1534063596",
			"price": "995.55",
			"sign": "2",
			"change": "21.60",
			"cvolume": 1,
			"chdegree": "99.46",
			"offerho": "995.80",
			"bidho": "995.55",
			"volume": "129601",
			"openyak": 206842,
			"jnilopenupdn": 6213,
			"ibasis": "2.85",
			"sbasis": "0.22",
			"kasis": "-0.26",
			"value": "32275806",
			"j_openupdn": 0,
			"n_msvolume": "64502",
			"n_mdvolume": "64851",
			"s_msvolume": "-349",
			"n_mschecnt": 50239,
			"n_mdchecnt": 51183,
			"s_mschecnt": -944
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t2214"></a>
## `t2214` 기간별주가

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
| `t2214InBlock` | t2214InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-futcheck` | 선물최근월물 | String | Y | 1 | 0:default<br/>1:최근월물만연결 |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 date 값으로 설정 |
| `&nbsp;&nbsp;-cts_code` | CTS종목코드 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_code 값으로 설정 |
| `&nbsp;&nbsp;-lastdate` | 전종목만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cnt` | 조회요청건수 | Object | Y | 3 | - |


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
| `t2214OutBlock` | t2214OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 연속조회키<br/>연속 조회시 이 값을 InBlock의 date 필드에 넣어준다. |
| `&nbsp;&nbsp;-cts_code` | CTS종목코드 | String | Y | 8 | 연속조회키<br/>연속 조회시 이 값을 InBlock의 cts_code 필드에 넣어준다. |
| `&nbsp;&nbsp;-lastdate` | 전종목만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-nowfutyn` | 최근월선물여부 | String | Y | 1 | - |
| `t2214OutBlock1` | t2214OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한<br/>2:상승<br/>3:보합<br/>4:하한<br/>5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-openyak` | 미결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-openyakupdn` | 미결증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
   "t2214InBlock" :{
      "shcode" : "A0166000",
      "futcheck" : "0",
      "date" : "",
      "cts_code" : "",
      "lastdate" : "",
      "cnt" : 20
   }
}
```

### 응답 Example

```json
{
	"t2214OutBlock": {
		"date": "20260327",
		"cts_code": "A0166000",
		"lastdate": "",
		"nowfutyn": "Y"
	},
	"t2214OutBlock1": [
		{
			"date": "20260424",
			"open": "978.70",
			"high": "985.25",
			"low": "963.65",
			"close": "973.95",
			"sign": "5",
			"change": "6.00",
			"diff": "-0.61",
			"volume": 113902,
			"diff_vol": "-38.60",
			"openyak": 200629,
			"openyakupdn": 1751,
			"value": "27747091"
		},
		{
			"date": "20260423",
			"open": "978.55",
			"high": "993.75",
			"low": "951.15",
			"close": "979.95",
			"sign": "2",
			"change": "12.30",
			"diff": "1.27",
			"volume": 185513,
			"diff_vol": "53.38",
			"openyak": 198878,
			"openyakupdn": -534,
			"value": "45289018"
		},
		{
			"date": "20260422",
			"open": "964.95",
			"high": "969.05",
			"low": "953.25",
			"close": "967.65",
			"sign": "2",
			"change": "2.55",
			"diff": "0.26",
			"volume": 120950,
			"diff_vol": "4.82",
			"openyak": 199412,
			"openyakupdn": -3137,
			"value": "29108610"
		},
		{
			"date": "20260421",
			"open": "952.20",
			"high": "965.25",
			"low": "950.60",
			"close": "965.10",
			"sign": "2",
			"change": "25.75",
			"diff": "2.74",
			"volume": 115386,
			"diff_vol": "-3.93",
			"openyak": 202549,
			"openyakupdn": 10,
			"value": "27705728"
		},
		{
			"date": "20260420",
			"open": "936.60",
			"high": "949.50",
			"low": "932.70",
			"close": "939.35",
			"sign": "2",
			"change": "3.60",
			"diff": "0.38",
			"volume": 120106,
			"diff_vol": "17.01",
			"openyak": 202539,
			"openyakupdn": 1744,
			"value": "28298309"
		},
		{
			"date": "20260417",
			"open": "945.80",
			"high": "946.35",
			"low": "931.40",
			"close": "935.75",
			"sign": "5",
			"change": "8.05",
			"diff": "-0.85",
			"volume": 102648,
			"diff_vol": "-21.05",
			"openyak": 200795,
			"openyakupdn": -134,
			"value": "24048874"
		},
		{
			"date": "20260416",
			"open": "925.95",
			"high": "943.80",
			"low": "925.15",
			"close": "943.80",
			"sign": "2",
			"change": "19.05",
			"diff": "2.06",
			"volume": 130019,
			"diff_vol": "-9.74",
			"openyak": 200929,
			"openyakupdn": -173,
			"value": "30449963"
		},
		{
			"date": "20260415",
			"open": "933.10",
			"high": "937.60",
			"low": "917.55",
			"close": "924.75",
			"sign": "2",
			"change": "22.85",
			"diff": "2.53",
			"volume": 144054,
			"diff_vol": "17.87",
			"openyak": 201102,
			"openyakupdn": -2002,
			"value": "33478609"
		},
		{
			"date": "20260414",
			"open": "900.15",
			"high": "911.70",
			"low": "894.85",
			"close": "901.90",
			"sign": "2",
			"change": "29.90",
			"diff": "3.43",
			"volume": 122216,
			"diff_vol": "10.28",
			"openyak": 203104,
			"openyakupdn": 4440,
			"value": "27619780"
		},
		{
			"date": "20260413",
			"open": "856.25",
			"high": "876.40",
			"low": "856.15",
			"close": "872.00",
			"sign": "5",
			"change": "11.50",
			"diff": "-1.30",
			"volume": 110822,
			"diff_vol": "-3.47",
			"openyak": 198664,
			"openyakupdn": -2725,
			"value": "24106991"
		},
		{
			"date": "20260410",
			"open": "885.00",
			"high": "893.80",
			"low": "880.90",
			"close": "883.50",
			"sign": "2",
			"change": "16.45",
			"diff": "1.90",
			"volume": 114810,
			"diff_vol": "-24.52",
			"openyak": 201389,
			"openyakupdn": 125,
			"value": "25449664"
		},
		{
			"date": "20260409",
			"open": "878.30",
			"high": "883.25",
			"low": "866.20",
			"close": "867.05",
			"sign": "5",
			"change": "17.50",
			"diff": "-1.98",
			"volume": 152104,
			"diff_vol": "-28.47",
			"openyak": 201264,
			"openyakupdn": -3276,
			"value": "33188618"
		},
		{
			"date": "20260408",
			"open": "879.00",
			"high": "896.90",
			"low": "871.10",
			"close": "884.55",
			"sign": "2",
			"change": "60.45",
			"diff": "7.34",
			"volume": 212657,
			"diff_vol": "34.18",
			"openyak": 204540,
			"openyakupdn": 1206,
			"value": "46918786"
		},
		{
			"date": "20260407",
			"open": "834.05",
			"high": "839.40",
			"low": "812.20",
			"close": "824.10",
			"sign": "2",
			"change": "11.90",
			"diff": "1.47",
			"volume": 158485,
			"diff_vol": "2.19",
			"openyak": 203334,
			"openyakupdn": -2941,
			"value": "32667128"
		},
		{
			"date": "20260406",
			"open": "805.00",
			"high": "824.45",
			"low": "804.45",
			"close": "812.20",
			"sign": "2",
			"change": "8.75",
			"diff": "1.09",
			"volume": 155092,
			"diff_vol": "14.58",
			"openyak": 206275,
			"openyakupdn": -1111,
			"value": "31561710"
		},
		{
			"date": "20260403",
			"open": "800.20",
			"high": "807.60",
			"low": "791.50",
			"close": "803.45",
			"sign": "2",
			"change": "24.00",
			"diff": "3.08",
			"volume": 135359,
			"diff_vol": "-52.28",
			"openyak": 207386,
			"openyakupdn": 2610,
			"value": "27111479"
		},
		{
			"date": "20260402",
			"open": "826.15",
			"high": "833.35",
			"low": "765.55",
			"close": "779.45",
			"sign": "5",
			"change": "32.60",
			"diff": "-4.01",
			"volume": 283623,
			"diff_vol": "24.20",
			"openyak": 204776,
			"openyakupdn": -4253,
			"value": "56402560"
		},
		{
			"date": "20260401",
			"open": "791.55",
			"high": "823.70",
			"low": "783.90",
			"close": "812.05",
			"sign": "2",
			"change": "62.80",
			"diff": "8.38",
			"volume": 228360,
			"diff_vol": "-4.11",
			"openyak": 209029,
			"openyakupdn": -1787,
			"value": "45933302"
		},
		{
			"date": "20260331",
			"open": "757.00",
			"high": "775.85",
			"low": "746.20",
			"close": "749.25",
			"sign": "5",
			"change": "32.45",
			"diff": "-4.15",
			"volume": 238148,
			"diff_vol": "46.33",
			"openyak": 210816,
			"openyakupdn": 3117,
			"value": "45121382"
		},
		{
			"date": "20260330",
			"open": "770.00",
			"high": "786.65",
			"low": "761.15",
			"close": "781.70",
			"sign": "5",
			"change": "23.75",
			"diff": "-2.95",
			"volume": 162751,
			"diff_vol": "-1.50",
			"openyak": 207699,
			"openyakupdn": 7059,
			"value": "31621616"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t2210"></a>
## `t2210` 선물옵션시간대별체결조회(단일출력용)

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
| `t2210InBlock` | t2210InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | 체결수량 >= cvolume |
| `&nbsp;&nbsp;-stime` | 시작시간 | String | Y | 4 | 체결시간 >= stime(hhmm) |
| `&nbsp;&nbsp;-etime` | 종료시간 | String | Y | 4 | 체결시간 <= etime(hhmm) |


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
| `t2210OutBlock` | t2210OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mdchecnt` | 매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mschecnt` | 매수체결건수 | Number | Y | 8 | - |


### 요청 Example

```json
{
   "t2210InBlock" :{
      "focode" : "101T6000",
      "cvolume" : 0,
      "stime" : "0900",
      "etime" : "1600"
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t2210OutBlock": {
        "mdchecnt": 26165,
        "msvolume": 58080,
        "mschecnt": 25591,
        "mdvolume": 60493
    }
}
```

---

<a id="tr-t2301"></a>
## `t2301` 옵션전광판

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
| `t2301InBlock` | t2301InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-yyyymm` | 월물 | String | Y | 6 | ex) 미니,정규 : '200604' 위클리 : 'W1 ' |
| `&nbsp;&nbsp;-gubun` | 미니구분(M:미니G:정규) | String | Y | 1 | M: 미니 G: 정규 W: 위클리 |


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
| `t2301OutBlock` | t2301OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-histimpv` | 역사적변동성 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-jandatecnt` | 옵션잔존일 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cimpv` | 콜옵션대표IV | Number | Y | 6.3 | - |
| `&nbsp;&nbsp;-pimpv` | 풋옵션대표IV | Number | Y | 6.3 | - |
| `&nbsp;&nbsp;-gmprice` | 근월물현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gmsign` | 근월물전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-gmchange` | 근월물전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gmdiff` | 근월물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gmvolume` | 근월물거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gmshcode` | 근월물선물코드 | String | Y | 8 | - |
| `t2301OutBlock1` | t2301OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-optcode` | 콜옵션코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-iv` | IV | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-mgjv` | 미결제약정 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mgjvupdn` | 미결제약정증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-delt` | 델타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-gama` | 감마 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-vega` | 베가 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-ceta` | 쎄타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-rhox` | 로우 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-impv` | 내재가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-timevl` | 시간가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jvolume` | 잔고수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-parpl` | 평가손익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jngo` | 청산가능수량 | Number | Y | 6 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-atmgubun` | ATM구분 | String | Y | 1 | 0:선물 1:ATM 2:ITM 3:OTM |
| `&nbsp;&nbsp;-jisuconv` | 지수환산 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `t2301OutBlock2` | t2301OutBlock2 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-optcode` | 풋옵션코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-iv` | IV | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-mgjv` | 미결제약정 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mgjvupdn` | 미결제약정증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-delt` | 델타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-gama` | 감마 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-vega` | 베가 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-ceta` | 쎄타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-rhox` | 로우 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-impv` | 내재가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-timevl` | 시간가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jvolume` | 잔고수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-parpl` | 평가손익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jngo` | 청산가능수량 | Number | Y | 6 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-atmgubun` | ATM구분 | String | Y | 1 | 0:선물 1:ATM 2:ITM 3:OTM |
| `&nbsp;&nbsp;-jisuconv` | 지수환산 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t2301InBlock": {
    "yyyymm": "",
    "gubun": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t2301OutBlock2": [
        {
            "parpl": 0,
            "offerrem1": 2,
            "sign": "5",
            "cvolume": 1,
            "mgjvupdn": 0,
            "bidrem1": 7,
            "high": "175.70",
            "jisuconv": "3951.92",
            "mgjv": 471,
            "low": "175.50",
            "price": "175.70",
            "actprice": "520.00",
            "impv": "176.46",
            "bidho1": "175.50",
            "jngo": 0,
            "value": "000000000176",
            "gama": "0.0000",
            "offerho1": "176.55",
            "ceta": "0.0535",
            "optcode": "301T6520",
            "change": "1.40",
            "delt": "-1.0000",
            "diff": "-0.79",
            "rhox": "-0.0570",
            "iv": "0.01",
            "timevl": "-0.76",
            "volume": 4,
            "atmgubun": "2",
            "jvolume": 0,
            "theoryprice": "176.08",
            "vega": "0.0000",
            "open": "175.50"
        }
    ],
    "t2301OutBlock": {
        "pimpv": "12.763",
        "gmchange": "0.70",
        "gmprice": "343.65",
        "histimpv": 0,
        "cimpv": "11.681",
        "gmdiff": "0.20",
        "gmsign": "2",
        "jandatecnt": 4,
        "gmvolume": 65769,
        "gmshcode": "101T6000"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t2407"></a>
## `t2407` 선물옵션호가잔량비율챠트

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
| `t2407InBlock` | t2407InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-bgubun` | 분구분 | String | Y | 1 | 0:30초<br/>1:분 |
| `&nbsp;&nbsp;-nmin` | N분 | Object | Y | 2 | bgubun = 1 인 경우 N분 입력값 |
| `&nbsp;&nbsp;-etime` | 종료시간 | String | Y | 4 | etime 이전 시간대를 조회함 |
| `&nbsp;&nbsp;-hgubun` | 호가구분 | String | Y | 1 | 0@총 호가잔량<br/>1@1차 호가잔량<br/>2@2차 호가잔량<br/>3@3차 호가잔량<br/>4@4차 호가잔량<br/>5@5차 호가잔량 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 6 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |


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
| `t2407OutBlock` | t2407OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdchecnt` | 매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mschecnt` | 매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 6 | 연속조회키<br/>연속 조회시 이 값을 InBlock의 cts_time 필드에 넣어준다. |
| `t2407OutBlock1` | t2407OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한<br/>2:상승<br/>3:보합<br/>4:하한<br/>5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho1` | 매도1호가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수1호가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-offerrem` | 매도수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem` | 매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offercnt` | 매도건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidcnt` | 매수건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-c_offerrem` | 매도증감수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-c_bidrem` | 매수증감수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-c_offercnt` | 매도증감건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-c_bidcnt` | 매수증감건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-r_bidrem` | 매수수량비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-r_bidcnt` | 매수건수비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-r_sign` | 매수비율구분 | String | Y | 1 | 2:매수수량비율 > 100<br/>5:매수수량비율 <= 100 |
| `&nbsp;&nbsp;-date` | 일자 | Object | Y | 8 | - |


### 요청 Example

```json
{
   "t2407InBlock" :{
      "focode" : "A0166000",
      "bgubun" : "0",
      "nmin" : 0,
      "etime" : "1600",
      "hgubun" : "0",
      "cnt" : 20,
      "cts_time" : ""
   }
}
```

### 응답 Example

```json
{
	"t2407OutBlock": {
		"mdvolume": "56528",
		"mdchecnt": 45167,
		"msvolume": "54404",
		"mschecnt": 42502,
		"cts_time": "152600"
	},
	"t2407OutBlock1": [
		{
			"time": "154500",
			"price": "973.95",
			"sign": "5",
			"change": "-6.00",
			"volume": "113902",
			"cvolume": 2810,
			"offerho1": "973.95",
			"bidho1": "973.90",
			"offerrem": 2969,
			"bidrem": 2800,
			"offercnt": 554,
			"bidcnt": 526,
			"c_offerrem": 2127,
			"c_bidrem": 1803,
			"c_offercnt": 88,
			"c_bidcnt": 19,
			"r_bidrem": "94.31",
			"r_bidcnt": "94.95",
			"r_sign": "5",
			"date": "20260424"
		},
		{
			"time": "153500",
			"price": "974.30",
			"sign": "5",
			"change": "-5.65",
			"volume": "111092",
			"cvolume": 94,
			"offerho1": "974.30",
			"bidho1": "974.00",
			"offerrem": 842,
			"bidrem": 997,
			"offercnt": 466,
			"bidcnt": 507,
			"c_offerrem": -72,
			"c_bidrem": 51,
			"c_offercnt": -55,
			"c_bidcnt": 10,
			"r_bidrem": "118.41",
			"r_bidcnt": "108.80",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153430",
			"price": "973.80",
			"sign": "5",
			"change": "-6.15",
			"volume": "110998",
			"cvolume": 106,
			"offerho1": "973.90",
			"bidho1": "973.80",
			"offerrem": 914,
			"bidrem": 946,
			"offercnt": 521,
			"bidcnt": 497,
			"c_offerrem": -8,
			"c_bidrem": 0,
			"c_offercnt": -8,
			"c_bidcnt": -1,
			"r_bidrem": "103.50",
			"r_bidcnt": "95.39",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153400",
			"price": "973.80",
			"sign": "5",
			"change": "-6.15",
			"volume": "110892",
			"cvolume": 150,
			"offerho1": "973.85",
			"bidho1": "973.75",
			"offerrem": 922,
			"bidrem": 946,
			"offercnt": 529,
			"bidcnt": 498,
			"c_offerrem": -27,
			"c_bidrem": -11,
			"c_offercnt": -18,
			"c_bidcnt": -7,
			"r_bidrem": "102.60",
			"r_bidcnt": "94.14",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153330",
			"price": "973.70",
			"sign": "5",
			"change": "-6.25",
			"volume": "110742",
			"cvolume": 140,
			"offerho1": "973.80",
			"bidho1": "973.75",
			"offerrem": 949,
			"bidrem": 957,
			"offercnt": 547,
			"bidcnt": 505,
			"c_offerrem": 39,
			"c_bidrem": -56,
			"c_offercnt": 26,
			"c_bidcnt": -16,
			"r_bidrem": "100.84",
			"r_bidcnt": "92.32",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153300",
			"price": "974.10",
			"sign": "5",
			"change": "-5.85",
			"volume": "110602",
			"cvolume": 111,
			"offerho1": "974.15",
			"bidho1": "974.00",
			"offerrem": 910,
			"bidrem": 1013,
			"offercnt": 521,
			"bidcnt": 521,
			"c_offerrem": -12,
			"c_bidrem": 35,
			"c_offercnt": -16,
			"c_bidcnt": 3,
			"r_bidrem": "111.32",
			"r_bidcnt": "100.00",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153230",
			"price": "973.95",
			"sign": "5",
			"change": "-6.00",
			"volume": "110491",
			"cvolume": 96,
			"offerho1": "974.00",
			"bidho1": "973.90",
			"offerrem": 922,
			"bidrem": 978,
			"offercnt": 537,
			"bidcnt": 518,
			"c_offerrem": -2,
			"c_bidrem": -4,
			"c_offercnt": 12,
			"c_bidcnt": -9,
			"r_bidrem": "106.07",
			"r_bidcnt": "96.46",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153200",
			"price": "974.10",
			"sign": "5",
			"change": "-5.85",
			"volume": "110395",
			"cvolume": 109,
			"offerho1": "974.20",
			"bidho1": "974.05",
			"offerrem": 924,
			"bidrem": 982,
			"offercnt": 525,
			"bidcnt": 527,
			"c_offerrem": 3,
			"c_bidrem": 0,
			"c_offercnt": 3,
			"c_bidcnt": -5,
			"r_bidrem": "106.28",
			"r_bidcnt": "100.38",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153130",
			"price": "974.30",
			"sign": "5",
			"change": "-5.65",
			"volume": "110286",
			"cvolume": 99,
			"offerho1": "974.30",
			"bidho1": "974.20",
			"offerrem": 921,
			"bidrem": 982,
			"offercnt": 522,
			"bidcnt": 532,
			"c_offerrem": 10,
			"c_bidrem": -28,
			"c_offercnt": 8,
			"c_bidcnt": -10,
			"r_bidrem": "106.62",
			"r_bidcnt": "101.92",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153100",
			"price": "974.55",
			"sign": "5",
			"change": "-5.40",
			"volume": "110187",
			"cvolume": 139,
			"offerho1": "974.50",
			"bidho1": "974.40",
			"offerrem": 911,
			"bidrem": 1010,
			"offercnt": 514,
			"bidcnt": 542,
			"c_offerrem": 50,
			"c_bidrem": -31,
			"c_offercnt": 21,
			"c_bidcnt": -15,
			"r_bidrem": "110.87",
			"r_bidcnt": "105.45",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153030",
			"price": "974.65",
			"sign": "5",
			"change": "-5.30",
			"volume": "110048",
			"cvolume": 381,
			"offerho1": "974.70",
			"bidho1": "974.65",
			"offerrem": 861,
			"bidrem": 1041,
			"offercnt": 493,
			"bidcnt": 557,
			"c_offerrem": -51,
			"c_bidrem": 18,
			"c_offercnt": -41,
			"c_bidcnt": 25,
			"r_bidrem": "120.91",
			"r_bidcnt": "112.98",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "153000",
			"price": "974.10",
			"sign": "5",
			"change": "-5.85",
			"volume": "109667",
			"cvolume": 580,
			"offerho1": "974.10",
			"bidho1": "973.95",
			"offerrem": 912,
			"bidrem": 1023,
			"offercnt": 534,
			"bidcnt": 532,
			"c_offerrem": -30,
			"c_bidrem": 63,
			"c_offercnt": -39,
			"c_bidcnt": 42,
			"r_bidrem": "112.17",
			"r_bidcnt": "99.63",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152930",
			"price": "973.45",
			"sign": "5",
			"change": "-6.50",
			"volume": "109087",
			"cvolume": 247,
			"offerho1": "973.60",
			"bidho1": "973.55",
			"offerrem": 942,
			"bidrem": 960,
			"offercnt": 573,
			"bidcnt": 490,
			"c_offerrem": -1,
			"c_bidrem": 0,
			"c_offercnt": 8,
			"c_bidcnt": -14,
			"r_bidrem": "101.91",
			"r_bidcnt": "85.51",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152900",
			"price": "973.75",
			"sign": "5",
			"change": "-6.20",
			"volume": "108840",
			"cvolume": 276,
			"offerho1": "973.90",
			"bidho1": "973.85",
			"offerrem": 943,
			"bidrem": 960,
			"offercnt": 565,
			"bidcnt": 504,
			"c_offerrem": 7,
			"c_bidrem": -49,
			"c_offercnt": 16,
			"c_bidcnt": -36,
			"r_bidrem": "101.80",
			"r_bidcnt": "89.20",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152830",
			"price": "974.15",
			"sign": "5",
			"change": "-5.80",
			"volume": "108564",
			"cvolume": 119,
			"offerho1": "974.35",
			"bidho1": "974.30",
			"offerrem": 936,
			"bidrem": 1009,
			"offercnt": 549,
			"bidcnt": 540,
			"c_offerrem": 11,
			"c_bidrem": -14,
			"c_offercnt": 3,
			"c_bidcnt": -1,
			"r_bidrem": "107.80",
			"r_bidcnt": "98.36",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152800",
			"price": "974.35",
			"sign": "5",
			"change": "-5.60",
			"volume": "108445",
			"cvolume": 80,
			"offerho1": "974.45",
			"bidho1": "974.35",
			"offerrem": 925,
			"bidrem": 1023,
			"offercnt": 546,
			"bidcnt": 541,
			"c_offerrem": 16,
			"c_bidrem": -21,
			"c_offercnt": 15,
			"c_bidcnt": -23,
			"r_bidrem": "110.59",
			"r_bidcnt": "99.08",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152730",
			"price": "974.65",
			"sign": "5",
			"change": "-5.30",
			"volume": "108365",
			"cvolume": 86,
			"offerho1": "974.65",
			"bidho1": "974.60",
			"offerrem": 909,
			"bidrem": 1044,
			"offercnt": 531,
			"bidcnt": 564,
			"c_offerrem": 8,
			"c_bidrem": -12,
			"c_offercnt": 12,
			"c_bidcnt": -10,
			"r_bidrem": "114.85",
			"r_bidcnt": "106.21",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152700",
			"price": "974.70",
			"sign": "5",
			"change": "-5.25",
			"volume": "108279",
			"cvolume": 67,
			"offerho1": "974.75",
			"bidho1": "974.65",
			"offerrem": 901,
			"bidrem": 1056,
			"offercnt": 519,
			"bidcnt": 574,
			"c_offerrem": -2,
			"c_bidrem": 20,
			"c_offercnt": -1,
			"c_bidcnt": 10,
			"r_bidrem": "117.20",
			"r_bidcnt": "110.60",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152630",
			"price": "974.60",
			"sign": "5",
			"change": "-5.35",
			"volume": "108212",
			"cvolume": 84,
			"offerho1": "974.70",
			"bidho1": "974.60",
			"offerrem": 903,
			"bidrem": 1036,
			"offercnt": 520,
			"bidcnt": 564,
			"c_offerrem": -7,
			"c_bidrem": 2,
			"c_offercnt": -11,
			"c_bidcnt": 2,
			"r_bidrem": "114.73",
			"r_bidcnt": "108.46",
			"r_sign": "2",
			"date": "20260424"
		},
		{
			"time": "152600",
			"price": "974.55",
			"sign": "5",
			"change": "-5.40",
			"volume": "108128",
			"cvolume": 62,
			"offerho1": "974.55",
			"bidho1": "974.50",
			"offerrem": 910,
			"bidrem": 1034,
			"offercnt": 531,
			"bidcnt": 562,
			"c_offerrem": 8,
			"c_bidrem": -6,
			"c_offercnt": 4,
			"c_bidcnt": -6,
			"r_bidrem": "113.63",
			"r_bidcnt": "105.84",
			"r_sign": "2",
			"date": "20260424"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-t2424"></a>
## `t2424` 미결제약정추이

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
| `t2424InBlock` | t2424InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-focode` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-bdgubun` | 분일구분 | String | Y | 1 | 0:30초<br/>1:분<br/>2:일 |
| `&nbsp;&nbsp;-nmin` | N분 | Object | Y | 3 | t2424InBlock.bdgubun 이 1인 경우 N분 |
| `&nbsp;&nbsp;-tcgubun` | 당일연결구분 | String | Y | 1 | 0:전체<br/>1:당일 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 4 | - |


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
| `t2424OutBlock` | t2424OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한<br/>2:상승<br/>3:보합<br/>4:하한<br/>5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 15 | - |
| `&nbsp;&nbsp;-openyak` | 미결제수량 | Number | Y | 8 | - |
| `t2424OutBlock1` | t2424OutBlock1 | Object Array | Y | null | - |
| `&nbsp;&nbsp;-dt` | 일자시간 | String | Y | 14 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-openopenyak` | 미결제시량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highopenyak` | 미결제고량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowopenyak` | 미결제저량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-closeopenyak` | 미결제종량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-openupdn` | 미결증감 | Number | Y | 8 | - |


### 요청 Example

```json
{
   "t2424InBlock" :{
      "focode" : "A0166000",
      "bdgubun" : "0",
      "nmin" : 0,
      "tcgubun" : "0",
      "cnt" : 20
   }
}
```

### 응답 Example

```json
{
	"t2424OutBlock": {
		"price": "973.95",
		"sign": "5",
		"change": "6.00",
		"diff": "-0.61",
		"cvolume": 2810,
		"volume": "113902",
		"openyak": 200629
	},
	"t2424OutBlock1": [
		{
			"dt": "154500",
			"open": "973.95",
			"high": "973.95",
			"low": "973.95",
			"close": "973.95",
			"openopenyak": 199879,
			"highopenyak": 200629,
			"lowopenyak": 199879,
			"closeopenyak": 200629,
			"openupdn": 766
		},
		{
			"dt": "153500",
			"open": "973.80",
			"high": "974.30",
			"low": "973.80",
			"close": "974.30",
			"openopenyak": 199886,
			"highopenyak": 199886,
			"lowopenyak": 199860,
			"closeopenyak": 199863,
			"openupdn": -23
		},
		{
			"dt": "153430",
			"open": "973.75",
			"high": "973.90",
			"low": "973.55",
			"close": "973.80",
			"openopenyak": 199938,
			"highopenyak": 199938,
			"lowopenyak": 199886,
			"closeopenyak": 199886,
			"openupdn": -52
		},
		{
			"dt": "153400",
			"open": "973.70",
			"high": "973.90",
			"low": "973.55",
			"close": "973.80",
			"openopenyak": 199972,
			"highopenyak": 199972,
			"lowopenyak": 199938,
			"closeopenyak": 199938,
			"openupdn": -34
		},
		{
			"dt": "153330",
			"open": "974.10",
			"high": "974.10",
			"low": "973.70",
			"close": "973.70",
			"openopenyak": 200005,
			"highopenyak": 200005,
			"lowopenyak": 199972,
			"closeopenyak": 199972,
			"openupdn": -33
		},
		{
			"dt": "153300",
			"open": "973.90",
			"high": "974.20",
			"low": "973.75",
			"close": "974.10",
			"openopenyak": 199998,
			"highopenyak": 200020,
			"lowopenyak": 199998,
			"closeopenyak": 200005,
			"openupdn": 7
		},
		{
			"dt": "153230",
			"open": "974.20",
			"high": "974.25",
			"low": "973.90",
			"close": "973.95",
			"openopenyak": 200032,
			"highopenyak": 200032,
			"lowopenyak": 199998,
			"closeopenyak": 199998,
			"openupdn": -34
		},
		{
			"dt": "153200",
			"open": "974.25",
			"high": "974.40",
			"low": "974.00",
			"close": "974.10",
			"openopenyak": 200049,
			"highopenyak": 200049,
			"lowopenyak": 200029,
			"closeopenyak": 200032,
			"openupdn": -17
		},
		{
			"dt": "153130",
			"open": "974.45",
			"high": "974.45",
			"low": "974.05",
			"close": "974.30",
			"openopenyak": 200063,
			"highopenyak": 200063,
			"lowopenyak": 200049,
			"closeopenyak": 200049,
			"openupdn": -14
		},
		{
			"dt": "153100",
			"open": "974.65",
			"high": "974.85",
			"low": "974.30",
			"close": "974.55",
			"openopenyak": 200074,
			"highopenyak": 200082,
			"lowopenyak": 200063,
			"closeopenyak": 200063,
			"openupdn": -11
		},
		{
			"dt": "153030",
			"open": "974.10",
			"high": "974.70",
			"low": "973.80",
			"close": "974.65",
			"openopenyak": 200228,
			"highopenyak": 200228,
			"lowopenyak": 200036,
			"closeopenyak": 200074,
			"openupdn": -154
		},
		{
			"dt": "153000",
			"open": "973.45",
			"high": "974.30",
			"low": "973.45",
			"close": "974.10",
			"openopenyak": 200260,
			"highopenyak": 200260,
			"lowopenyak": 200228,
			"closeopenyak": 200228,
			"openupdn": -32
		},
		{
			"dt": "152930",
			"open": "973.75",
			"high": "973.75",
			"low": "973.45",
			"close": "973.45",
			"openopenyak": 200341,
			"highopenyak": 200354,
			"lowopenyak": 200260,
			"closeopenyak": 200260,
			"openupdn": -81
		},
		{
			"dt": "152900",
			"open": "974.15",
			"high": "974.15",
			"low": "973.70",
			"close": "973.75",
			"openopenyak": 200333,
			"highopenyak": 200341,
			"lowopenyak": 200328,
			"closeopenyak": 200341,
			"openupdn": 8
		},
		{
			"dt": "152830",
			"open": "974.35",
			"high": "974.45",
			"low": "974.15",
			"close": "974.15",
			"openopenyak": 200325,
			"highopenyak": 200336,
			"lowopenyak": 200325,
			"closeopenyak": 200333,
			"openupdn": 8
		},
		{
			"dt": "152800",
			"open": "974.65",
			"high": "974.65",
			"low": "974.30",
			"close": "974.35",
			"openopenyak": 200320,
			"highopenyak": 200328,
			"lowopenyak": 200320,
			"closeopenyak": 200325,
			"openupdn": 5
		},
		{
			"dt": "152730",
			"open": "974.65",
			"high": "974.80",
			"low": "974.55",
			"close": "974.65",
			"openopenyak": 200329,
			"highopenyak": 200329,
			"lowopenyak": 200320,
			"closeopenyak": 200320,
			"openupdn": -9
		},
		{
			"dt": "152700",
			"open": "974.60",
			"high": "974.75",
			"low": "974.60",
			"close": "974.70",
			"openopenyak": 200340,
			"highopenyak": 200340,
			"lowopenyak": 200329,
			"closeopenyak": 200329,
			"openupdn": -11
		},
		{
			"dt": "152630",
			"open": "974.50",
			"high": "974.75",
			"low": "974.45",
			"close": "974.60",
			"openopenyak": 200331,
			"highopenyak": 200340,
			"lowopenyak": 200330,
			"closeopenyak": 200340,
			"openupdn": 9
		},
		{
			"dt": "152600",
			"open": "974.65",
			"high": "974.65",
			"low": "974.45",
			"close": "974.55",
			"openopenyak": 200351,
			"highopenyak": 200354,
			"lowopenyak": 200331,
			"closeopenyak": 200331,
			"openupdn": -20
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t2522"></a>
## `t2522` 주식선물기초자산조회

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
| `t2522InBlock` | t2522InBlock | Object | Y | - | - |
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
| `t2522OutBlock` | t2522OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-cnt` | 건수 | Number | Y | 5 | - |
| `t2522OutBlock1` | 출력1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-bsc_asts_nm` | 기초자산명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-bsc_asts_is_cd` | 기초자산종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bsc_asts_id` | 기초자산ID | String | Y | 3 | - |
| `&nbsp;&nbsp;-nmc_is_shrt_cd` | 최근월물종목코드 | String | Y | 8 | - |


### 요청 Example

```json
{
	"t2522InBlock": {
		"dummy": ""
	}
}
```

### 응답 Example

```
{
	"t2522OutBlock": {
		"cnt": 285
	},
	"t2522OutBlock1": [
		{
			"bsc_asts_nm": "전체",
			"bsc_asts_is_cd": "999999",
			"bsc_asts_id": "JFU",
			"nmc_is_shrt_cd": "99999999"
		},
		{
			"bsc_asts_nm": "TKG휴켐스",
			"bsc_asts_is_cd": "069260",
			"bsc_asts_id": "S0A",
			"nmc_is_shrt_cd": "A0A65000"
		},
		{
			"bsc_asts_nm": "녹십자홀딩스",
			"bsc_asts_is_cd": "005250",
			"bsc_asts_id": "S0B",
			"nmc_is_shrt_cd": "A0B65000"
		},
... 생략
		{
			"bsc_asts_nm": "TIGER 반도체TOP10",
			"bsc_asts_is_cd": "396500",
			"bsc_asts_id": "SM8",
			"nmc_is_shrt_cd": "AM866000"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8401"></a>
## `t8401` 주식선물마스터조회(API용)

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
| `t8401InBlock` | t8401InBlock | Object | Y | null | - |
| `dummy` | Dummy | String | Y | 1 | - |


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
| `t8401OutBlock` | t8401OutBlock | Object Array | Y | null | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-basecode` | 기초자산코드 | String | Y | 9 | - |


### 요청 Example

```json
{
  "t8401InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8401OutBlock": [
        {
            "basecode": "A005930",
            "shcode": "111T7000",
            "expcode": "KR4111T70004",
            "hname": "삼성전자   F 202307"
        },
        {
            "basecode": "A000810",
            "shcode": "1CTWC000",
            "expcode": "KR41CTWC0007",
            "hname": "삼성화재   F 202512"
        },
        {
            "basecode": "A008930",
            "shcode": "1CVT7000",
            "expcode": "KR41CVT70007",
            "hname": "한미사이언 F 202307"
        },
        {
            "basecode": "A008930",
            "shcode": "1CVT8000",
            "expcode": "KR41CVT80006",
            "hname": "한미사이언 F 202308"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8402"></a>
## `t8402` 주식선물현재가조회(API용)

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
| `t8402InBlock` | t8402InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |


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
| `t8402OutBlock` | t8402OutBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stimeqrt` | 거래량전일동시간비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mgjv` | 미결제량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mgjvdiff` | 미결제증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high52w` | 52최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low52w` | 52최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-basis` | 베이시스 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-glyl` | 괴리율 | Number | Y | 6.3 | - |
| `&nbsp;&nbsp;-lastmonth` | 만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jandatecnt` | 잔여일 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-pricejisu` | 종합지수 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jisusign` | 종합지수전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jisuchange` | 종합지수전일대비 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-jisudiff` | 종합지수등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-kospijisu` | KOSPI200지수 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-kospisign` | KOSPI200전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-kospichange` | KOSPI200전일대비 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-kospidiff` | KOSPI200등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-listhprice` | 상장최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-listlprice` | 상장최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-delt` | 델타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-gama` | 감마 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-ceta` | 세타 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-vega` | 베가 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-rhox` | 로우 | Number | Y | 6.4 | - |
| `&nbsp;&nbsp;-gmprice` | 근월물현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gmsign` | 근월물전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-gmchange` | 근월물전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gmdiff` | 근월물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-theorypriceg` | 이론가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-histimpv` | 역사적변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-impv` | 내재변동성 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sbasis` | 시장BASIS | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ibasis` | 이론BASIS | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gmfutcode` | 근월물종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-shcode` | 기초자산단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-basehname` | 기초자산한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-baseprice` | 기초자산현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-basesign` | 기초자산현재가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-basechange` | 기초자산현재가전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-basediff` | 기초자산등락률 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-basevol` | 기초자산거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-baseprevol` | 기초자산전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-basebidprc` | 기초자산매수호가 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-baseaskprc` | 기초자산매도호가 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-basefornetbid` | 기초자산외국계회원사순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prodgrp` | 상품군 | String | Y | 20 | - |
| `&nbsp;&nbsp;-mulcnt` | 승수 | Number | Y | 12.8 | - |
| `&nbsp;&nbsp;-danhochk` | 단일가호가여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-yeprice` | 예상체결가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilysign` | 예상체결가전일종가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilychange` | 예상체결가전일종가대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilydrate` | 예상체결가전일종가등락율 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
   "t8402InBlock" :{
      "focode" : "111T6000"
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t8402OutBlock": {
        "jnilysign": "5",
        "mulcnt": "10.00000000",
        "jnilclose": 71200,
        "sign": "5",
        "high52w": 0,
        "glyl": "0.132",
        "kospichange": "0.47",
        "baseaskprc": 70900,
        "basefornetbid": 547559,
        "jisusign": "5",
        "gmfutcode": "",
        "high": 70800,
        "price": 70700,
        "gmdiff": "0",
        "danhochk": "0",
        "jandatecnt": 1,
        "impv": "0",
        "hname": "삼성전자   F 202306",
        "basechange": 100,
        "listhprice": 72800,
        "gmprice": 0,
        "prodgrp": "",
        "diff": "-0.70",
        "rhox": "0",
        "basis": "0",
        "basebidprc": 70800,
        "volume": 811347,
        "baseprice": 70900,
        "yeprice": 70500,
        "low52w": 0,
        "basediff": "-0.14",
        "kospisign": "5",
        "listlprice": 55200,
        "ibasis": -93,
        "dnlmtprice": 64100,
        "basevol": 19157578,
        "recprice": 71200,
        "mgjv": 0,
        "low": 70000,
        "theorypriceg": 0,
        "jnilychange": 700,
        "gmsign": "",
        "actprice": 0,
        "value": 570684700,
        "gama": "0",
        "jisuchange": "4.75",
        "jisudiff": "-0.15",
        "ceta": "0",
        "gmchange": 0,
        "stimeqrt": "106.86",
        "change": 500,
        "delt": "75.9257",
        "shcode": "005930",
        "uplmtprice": 78300,
        "kospijisu": "342.75",
        "lastmonth": "20230608",
        "jnilydrate": "-0.98",
        "kospidiff": "0.00",
        "histimpv": "0",
        "basehname": "삼성전자",
        "mgjvdiff": -539300,
        "sbasis": -200,
        "basesign": "5",
        "theoryprice": 70607,
        "baseprevol": 14796613,
        "open": 70500,
        "vega": "0",
        "pricejisu": "2610.85"
    }
}
```

---

<a id="tr-t8403"></a>
## `t8403` 주식선물호가조회(API용)

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
| `t8403InBlock` | t8403InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |


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
| `t8403OutBlock` | t8403OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stimeqrt` | 거래량전일동시간비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt1` | 매도호가건수1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt1` | 매수호가건수1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt2` | 매도호가건수2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt2` | 매수호가건수2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt3` | 매도호가건수3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt3` | 매수호가건수3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt4` | 매도호가건수4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt4` | 매수호가건수4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt5` | 매도호가건수5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt5` | 매수호가건수5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho6` | 매도호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho6` | 매수호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem6` | 매도호가수량6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem6` | 매수호가수량6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt6` | 매도호가건수6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt6` | 매수호가건수6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho7` | 매도호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho7` | 매수호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem7` | 매도호가수량7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem7` | 매수호가수량7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt7` | 매도호가건수7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt7` | 매수호가건수7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho8` | 매도호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho8` | 매수호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem8` | 매도호가수량8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem8` | 매수호가수량8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt8` | 매도호가건수8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt8` | 매수호가건수8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho9` | 매도호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho9` | 매수호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem9` | 매도호가수량9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem9` | 매수호가수량9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt9` | 매도호가건수9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt9` | 매수호가건수9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho10` | 매도호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho10` | 매수호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem10` | 매도호가수량10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem10` | 매수호가수량10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt10` | 매도호가건수10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt10` | 매수호가건수10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dvol` | 매도호가총수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol` | 매수호가총수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-toffernum` | 총매도호가건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tbidnum` | 총매수호가건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 수신시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |


### 요청 Example

```json
{
   "t8403InBlock" :{
      "shcode" : "111T6000"
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8403OutBlock": {
        "offerho4": 71100,
        "offerho3": 71000,
        "offerho6": 71300,
        "offerho5": 71200,
        "offerho8": 71500,
        "offerho7": 71400,
        "jnilclose": 71200,
        "offerho9": 71600,
        "sign": "5",
        "price": 70700,
        "hname": "삼성전자   F 202306",
        "offerho2": 70900,
        "offerho1": 70800,
        "diff": "-0.70",
        "toffernum": 91,
        "dcnt10": 2,
        "volume": 811347,
        "offerho10": 71700,
        "svol": 62353,
        "offerrem2": 1286,
        "bidho5": 70300,
        "dvol": 38649,
        "offerrem3": 117,
        "bidho4": 70400,
        "offerrem4": 25,
        "bidho7": 70100,
        "offerrem5": 25,
        "bidho6": 70200,
        "bidho9": 69900,
        "bidho8": 70000,
        "offerrem1": 1079,
        "offerrem6": 1,
        "offerrem7": 2000,
        "offerrem8": 2042,
        "offerrem9": 2001,
        "bidrem3": 2800,
        "bidrem4": 7281,
        "scnt10": 7,
        "bidrem1": 833,
        "bidrem2": 5198,
        "scnt1": 4,
        "tbidnum": 131,
        "bidrem9": 3162,
        "bidho1": 70700,
        "scnt5": 12,
        "bidrem7": 1371,
        "scnt4": 10,
        "bidrem8": 2062,
        "bidho3": 70500,
        "scnt3": 7,
        "bidrem5": 6304,
        "bidho2": 70600,
        "scnt2": 18,
        "bidrem6": 5160,
        "dcnt4": 4,
        "scnt9": 13,
        "bidrem10": 2143,
        "dcnt3": 3,
        "scnt8": 9,
        "dcnt2": 17,
        "scnt7": 10,
        "bidho10": 69800,
        "dcnt1": 14,
        "scnt6": 13,
        "stimeqrt": "106.86",
        "change": 500,
        "shcode": "111T60",
        "offerrem10": 2000,
        "dcnt9": 3,
        "time": "152000",
        "dcnt8": 5,
        "dcnt7": 2,
        "dcnt6": 1,
        "dcnt5": 3
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8404"></a>
## `t8404` 주식선물시간대별체결조회(API용)

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
| `t8404InBlock` | t8404InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | 거래량 > 특이거래량 |
| `&nbsp;&nbsp;-stime` | 시작시간 | String | Y | 4 | 장시작시간 이후 |
| `&nbsp;&nbsp;-etime` | 종료시간 | String | Y | 4 | 장종료시간 이전 |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |


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
| `t8404OutBlock` | t8404OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 연속조회키 연속 조회시 이 값을 InBlock의 cts_time 필드에 넣어준다. |
| `t8404OutBlock1` | t8404OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-openyak` | 미결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilopenupdn` | 미결전일증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ibasis` | 이론BASIS | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sbasis` | 시장BASIS | Number | Y | 8 | - |
| `&nbsp;&nbsp;-kasis` | 괴리율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-j_openupdn` | 미결직전증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-n_msvolume` | 누적매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_mdvolume` | 누적매도체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-s_msvolume` | 누적순매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_mschecnt` | 누적매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-n_mdchecnt` | 누적매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschecnt` | 누적순매수체결건수 | Number | Y | 8 | - |


### 요청 Example

```json
{
   "t8404InBlock" :{
      "focode" : "111T6000",
      "cvolume" : 0,
      "stime" : "0900",
      "etime" : "1600",
      "cts_time" : ""
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8404OutBlock1": [
        {
            "change": "00000500",
            "sign": "5",
            "ibasis": 7,
            "n_mdchecnt": 3991,
            "chetime": "1519494834",
            "offerho": 70800,
            "openyak": 291595,
            "j_openupdn": 0,
            "cvolume": 197,
            "n_mdvolume": "000000443424",
            "volume": "000000811347",
            "chdegree": "82.82",
            "bidho": 70700,
            "s_mschecnt": -2445,
            "price": 70700,
            "kasis": "0.13",
            "s_msvolume": "-00000076196",
            "n_mschecnt": 1546,
            "jnilopenupdn": -247705,
            "n_msvolume": "000000367228",
            "sbasis": 100,
            "value": "000570684700"
        },
        {
            "change": "00000500",
            "sign": "5",
            "ibasis": 7,
            "n_mdchecnt": 3991,
            "chetime": "1519470921",
            "offerho": 70700,
            "openyak": 291595,
            "j_openupdn": -7739,
            "cvolume": 3,
            "n_mdvolume": "000000443424",
            "volume": "000000811150",
            "chdegree": "82.77",
            "bidho": 70600,
            "s_mschecnt": -2446,
            "price": 70700,
            "kasis": "-0.01",
            "s_msvolume": "-00000076393",
            "n_mschecnt": 1545,
            "jnilopenupdn": -247705,
            "n_msvolume": "000000367031",
            "sbasis": 0,
            "value": "000570545421"
        }
    ],
    "t8404OutBlock": {
        "cts_time": "1514124266"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8405"></a>
## `t8405` 주식선물기간별주가(API용)

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
| `t8405InBlock` | t8405InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-futcheck` | 선물최근월물 | String | Y | 1 | 0:default 1:최근월물만연결 |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 date 값으로 설정 |
| `&nbsp;&nbsp;-cts_code` | CTS종목코드 | String | Y | 8 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 cts_code 값으로 설정 |
| `&nbsp;&nbsp;-lastdate` | 전종목만기일 | String | Y | 8 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 lastdate 값으로 설정 |
| `&nbsp;&nbsp;-cnt` | 조회요청건수 | Object | Y | 3 | - |


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
| `t8405OutBlock` | t8405OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 연속조회키 연속 조회시 이 값을 InBlock의 date 필드에 넣어준다. |
| `&nbsp;&nbsp;-cts_code` | CTS종목코드 | String | Y | 8 | 연속조회키 연속 조회시 이 값을 InBlock의 cts_code 필드에 넣어준다. |
| `&nbsp;&nbsp;-lastdate` | 전종목만기일 | String | Y | 8 | 연속조회키 연속 조회시 이 값을 InBlock의 lastdate 필드에 넣어준다. |
| `&nbsp;&nbsp;-nowfutyn` | 최근월선물여부 | String | Y | 1 | - |
| `t8405OutBlock1` | t8405OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-openyak` | 미결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-openyakupdn` | 미결증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
   "t8405InBlock" :{
      "shcode" : "111T6000",
      "futcheck" : "0",
      "date" : "",
      "cts_code" : "",
      "lastdate" : "",
      "cnt" : 20
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8405OutBlock": {
        "date": "20230509",
        "cts_code": "111T6000",
        "nowfutyn": "Y",
        "lastdate": ""
    },
    "t8405OutBlock1": [
        {
            "date": "20230608",
            "openyakupdn": -539300,
            "diff_vol": "-4.73",
            "change": 500,
            "sign": "5",
            "diff": "-0.70",
            "openyak": 0,
            "volume": 811347,
            "high": 70800,
            "low": 70000,
            "close": 70700,
            "value": "000570684700",
            "open": 70500
        },
        {
            "date": "20230607",
            "openyakupdn": -400372,
            "diff_vol": "-4.48",
            "change": 400,
            "sign": "5",
            "diff": "-0.56",
            "openyak": 539300,
            "volume": 851670,
            "high": 71600,
            "low": 70900,
            "close": 71200,
            "value": "000606460142",
            "open": 71300
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8406"></a>
## `t8406` 주식선물틱분별체결조회(API용)

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
| `t8406InBlock` | t8406InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cgubun` | 챠트구분 | String | Y | 1 | T:틱차트 B:분차트 |
| `&nbsp;&nbsp;-bgubun` | 분구분 | Object | Y | 3 | 차트구분이 'B'일때만 체크 0: 30초 0초과 : n분 |
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
| `t8406OutBlock1` | t8406OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | 1:상한 2:상승 3:보합 4:하한 5:하락 |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
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
   "t8406InBlock" :{
      "focode" : "111T6000",
      "cgubun" : "T",
      "bgubun" : 0,
      "cnt" : 20
   }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8406OutBlock1": [
        {
            "s_mdchecnt": 0,
            "change": 500,
            "sign": "5",
            "chdegcnt": "38.74",
            "ss_mschecnt": 1,
            "chetime": "151949",
            "openyak": 291595,
            "s_mschevol": "000000000197",
            "cvolume": 197,
            "volume": "000000811347",
            "high": 0,
            "chdegvol": "82.82",
            "s_mschecnt": 1,
            "low": 0,
            "openupdn": 0,
            "price": 70700,
            "value": "570684700000",
            "s_mdchevol": "000000000000",
            "ss_mschevol": "000000000197",
            "open": 0
        },
        {
            "s_mdchecnt": 0,
            "change": 500,
            "sign": "5",
            "chdegcnt": "38.71",
            "ss_mschecnt": 1,
            "chetime": "151947",
            "openyak": 291595,
            "s_mschevol": "000000000003",
            "cvolume": 3,
            "volume": "000000811150",
            "high": 0,
            "chdegvol": "82.77",
            "s_mschecnt": 1,
            "low": 0,
            "openupdn": -7739,
            "price": 70700,
            "value": "570545421000",
            "s_mdchevol": "000000000000",
            "ss_mschevol": "000000000003",
            "open": 0
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8426"></a>
## `t8426` 상품선물마스터조회(API용)

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
| `t8426InBlock` | t8426InBlock | Object | Y | - | - |
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
| `t8426OutBlock` | t8426OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |


### 요청 Example

```json
{
  "t8426InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```json
{
    "t8426OutBlock": [
        {
            "shcode": "165T6000",
            "expcode": "KR4165T60001",
            "hname": "3년국채    F 202306"
        },
        {
            "shcode": "165T9000",
            "expcode": "KR4165T90008",
            "hname": "3년국채    F 202309"
        },
        {
            "shcode": "166T6000",
            "expcode": "KR4166T60009",
            "hname": "5년국채    F 202306"
        }
    ],
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8427"></a>
## `t8427` 과거데이터시간대별조회

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
| `t8427InBlock` | t8427InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-fo_gbn` | 선물옵션구분 | String | Y | 1 | F:선물 O:옵션 |
| `&nbsp;&nbsp;-yyyy` | 조회년도 | String | Y | 4 | YYYY |
| `&nbsp;&nbsp;-mm` | 조회월 | String | Y | 2 | MM |
| `&nbsp;&nbsp;-cp_gbn` | 옵션콜풋구분 | String | Y | 1 | 2:콜 3:풋 |
| `&nbsp;&nbsp;-actprice` | 옵션행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-focode` | 선물옵션코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-dt_gbn` | 일분구분 | String | Y | 1 | D:일 M:분 |
| `&nbsp;&nbsp;-min_term` | 분간격 | String | Y | 2 | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 다음 조회시 OutBlock의 date 값 입력 처음 조회시 Space |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | 다음 조회시 OutBlock의 time 값 입력 처음 조회시 Space |


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
| `t8427OutBlock` | t8427OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 선물옵션코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `t8427OutBlock1` | t8427OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-openyak` | 미결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-openyakupdn` | 미결증감 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8427InBlock": {
    "fo_gbn": "F",
    "yyyy": "2023",
    "mm": "05",
    "cp_gbn": "2",
    "actprice": 0.00,
    "focode": "101T6000",
    "dt_gbn": "D",
    "min_term": "",
    "date": "",
    "time": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t8427OutBlock": {
        "date": "20230209",
        "time": "",
        "focode": "101T3000"
    },
    "t8427OutBlock1": [
        {
            "date": "20230309",
            "openyakupdn": -118144,
            "diff_vol": "-36.42",
            "change": "0.70",
            "sign": "5",
            "diff": "-0.22",
            "openyak": 0,
            "volume": 127279,
            "high": "316.85",
            "low": "313.70",
            "time": "",
            "close": "313.95",
            "value": "10030940",
            "open": "316.50"
        },
        {
            "date": "20230308",
            "openyakupdn": -46160,
            "diff_vol": "4.24",
            "change": "4.75",
            "sign": "5",
            "diff": "-1.48",
            "openyak": 118144,
            "volume": 200201,
            "high": "316.70",
            "low": "314.25",
            "time": "",
            "close": "314.65",
            "value": "15783656",
            "open": "316.20"
        }
    ]
}
```

---

<a id="tr-t8467"></a>
## `t8467` 지수선물마스터조회API용

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
| `t8467InBlock` | t8467InBlock | Object | Y | null | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | V:변동성지수선물<br/>S:섹터지수선물<br/>Q:코스닥150지수선물<br/>그 이외의 값은 코스피200지수선물 |


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
| `t8467OutBlock` | t8467OutBlock | Object Array | Y | null | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jnilhigh` | 전일고가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jnillow` | 전일저가 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 9.2 | - |


### 요청 Example

```json
{
  "t8467InBlock": {
    "gubun": ""
  }
}
```

### 응답 Example

```json
{
	"t8467OutBlock": [
		{
			"hname": "F 2606",
			"shcode": "A0166000",
			"expcode": "KR4A01660005",
			"uplmtprice": "1214.75",
			"dnlmtprice": "1034.85",
			"jnilclose": "1124.80",
			"jnilhigh": "1125.65",
			"jnillow": "1124.55",
			"recprice": "1124.80"
		},
		{
			"hname": "F 2609",
			"shcode": "A0169000",
			"expcode": "KR4A01690002",
			"uplmtprice": "972.05",
			"dnlmtprice": "828.05",
			"jnilclose": "900.05",
			"jnilhigh": "900.20",
			"jnillow": "900.05",
			"recprice": "900.05"
		},
		{
			"hname": "F 2612",
			"shcode": "A016C000",
			"expcode": "KR4A016C0004",
			"uplmtprice": "1226.10",
			"dnlmtprice": "1044.50",
			"jnilclose": "1135.30",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "1135.30"
		},
		{
			"hname": "F 2703",
			"shcode": "A0173000",
			"expcode": "KR4A01730006",
			"uplmtprice": "1080.00",
			"dnlmtprice": "920.00",
			"jnilclose": "1000.00",
			"jnilhigh": "1000.00",
			"jnillow": "1000.00",
			"recprice": "1000.00"
		},
		{
			"hname": "F 2706",
			"shcode": "A0176000",
			"expcode": "KR4A01760003",
			"uplmtprice": "1235.10",
			"dnlmtprice": "1052.20",
			"jnilclose": "1143.65",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "1143.65"
		},
		{
			"hname": "F 2712",
			"shcode": "A017C000",
			"expcode": "KR4A017C0003",
			"uplmtprice": "1249.10",
			"dnlmtprice": "1064.10",
			"jnilclose": "1156.60",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "1156.60"
		},
		{
			"hname": "F 2812",
			"shcode": "A018C000",
			"expcode": "KR4A018C0002",
			"uplmtprice": "1283.10",
			"dnlmtprice": "1093.10",
			"jnilclose": "1188.10",
			"jnilhigh": "1188.10",
			"jnillow": "1188.10",
			"recprice": "1188.10"
		},
		{
			"hname": "F SP 06-2609",
			"shcode": "D016669S",
			"expcode": "KR4D016669S5",
			"uplmtprice": "-168.55",
			"dnlmtprice": "-280.95",
			"jnilclose": "0.00",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "0.00"
		},
		{
			"hname": "F SP 06-2612",
			"shcode": "D01666CS",
			"expcode": "KR4D01666CS5",
			"uplmtprice": "66.70",
			"dnlmtprice": "-45.70",
			"jnilclose": "-328.40",
			"jnilhigh": "-328.40",
			"jnillow": "-328.40",
			"recprice": "0.00"
		},
		{
			"hname": "F SP 06-2703",
			"shcode": "D016673S",
			"expcode": "KR4D016673S7",
			"uplmtprice": "-68.60",
			"dnlmtprice": "-181.00",
			"jnilclose": "0.00",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "0.00"
		},
		{
			"hname": "F SP 06-2706",
			"shcode": "D016676S",
			"expcode": "KR4D016676S0",
			"uplmtprice": "75.05",
			"dnlmtprice": "-37.35",
			"jnilclose": "0.00",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "0.00"
		},
		{
			"hname": "F SP 06-2712",
			"shcode": "D01667CS",
			"expcode": "KR4D01667CS3",
			"uplmtprice": "88.00",
			"dnlmtprice": "-24.40",
			"jnilclose": "0.00",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "0.00"
		},
		{
			"hname": "F SP 06-2812",
			"shcode": "D01668CS",
			"expcode": "KR4D01668CS1",
			"uplmtprice": "119.50",
			"dnlmtprice": "7.10",
			"jnilclose": "0.00",
			"jnilhigh": "0.00",
			"jnillow": "0.00",
			"recprice": "0.00"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8433"></a>
## `t8433` 지수옵션마스터조회API용

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
| `t8433InBlock` | t8433InBlock | Object | Y | - | - |
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
| `t8433OutBlock` | t8433OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-hprice` | 상한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-lprice` | 하한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilhigh` | 전일고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnillow` | 전일저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t8433InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```json
{
    "t8433OutBlock": [
        {
            "jnilhigh": "0.00",
            "recprice": "127.95",
            "hprice": "175.80",
            "lprice": "102.90",
            "shcode": "201T7185",
            "jnilclose": "127.95",
            "expcode": "KR4201T71852",
            "hname": "C 2307 185.0",
            "jnillow": "0.00"
        },
        {
            "jnilhigh": "0.00",
            "recprice": "62.00",
            "hprice": "159.20",
            "lprice": "0.01",
            "shcode": "201V6330",
            "jnilclose": "62.00",
            "expcode": "KR4201V63301",
            "hname": "C 2406 330.0",
            "jnillow": "0.00"
        },
        {
            "jnilhigh": "0.00",
            "recprice": "54.05",
            "hprice": "145.30",
            "lprice": "0.01",
            "shcode": "201V6335",
            "jnilclose": "54.05",
            "expcode": "KR4201V63350",
            "hname": "C 2406 335.0",
            "jnillow": "0.00"
        }
    ],
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8434"></a>
## `t8434` 선물/옵션멀티현재가조회

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
| `t8434InBlock` | t8434InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-qrycnt` | 건수 | Number | Y | 3 | 최대50개까지 |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 400 | 구분자 없이 종목코드를 붙여서 입력 |


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
| `t8434OutBlock1` | t8434OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-checnt` | 체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |


### 요청 Example

```json
{
  "t8434InBlock": {
    "qrycnt": 1,
    "focode": "101T6000"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8434OutBlock1": [
        {
            "volume": 119523,
            "checnt": 51756,
            "price": "342.30",
            "change": "0.95",
            "sign": "5",
            "diff": "0.28",
            "hname": "코스피200 F 202306",
            "focode": "101T6000"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8435"></a>
## `t8435` 파생종목마스터조회API용

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
| `t8435InBlock` | t8435InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분(MF/MO) | String | Y | 2 | MF : 미니선물<br/>MO : 미니옵션<br/>WK : 코스피200위클리옵션<br/>SF : 코스닥150선물<br/>QW : 코스닥150위클리옵션 |


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
| `t8435OutBlock` | t8435OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilhigh` | 전일고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnillow` | 전일저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t8435InBlock": {
    "gubun": "SF"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8435OutBlock": [
        {
            "jnilhigh": "1349.8",
            "recprice": "1348.7",
            "shcode": "106T6000",
            "jnilclose": "1348.7",
            "uplmtprice": "1456.5",
            "expcode": "KR4106T60005",
            "hname": "KQF 2306",
            "jnillow": "1323.9",
            "dnlmtprice": "1240.9"
        },
        {
            "jnilhigh": "1348.5",
            "recprice": "1348.5",
            "shcode": "106T9000",
            "jnilclose": "1348.5",
            "uplmtprice": "1456.3",
            "expcode": "KR4106T90002",
            "hname": "KQF 2309",
            "jnillow": "1320.2",
            "dnlmtprice": "1240.7"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t9943"></a>
## `t9943` 지수선물마스터조회API용

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
| `t9943InBlock` | t9943InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | V:변동성지수선물 S:섹터지수선물 그 이외의 값은 코스피200지수선물 |


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
| `t9943OutBlock` | t9943OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |


### 요청 Example

```json
{
  "t9943InBlock": {
    "gubun": "V"
  }
}
```

### 응답 Example

```json
{
    "t9943OutBlock": [
        {
            "shcode": "104T6000",
            "expcode": "KR4104T60000",
            "hname": "VF 2306"
        },
        {
            "shcode": "104T7000",
            "expcode": "KR4104T70009",
            "hname": "VF 2307"
        },
        {
            "shcode": "104T8000",
            "expcode": "KR4104T80008",
            "hname": "VF 2308"
        },
        {
            "shcode": "104T9000",
            "expcode": "KR4104T90007",
            "hname": "VF 2309"
        },
        {
            "shcode": "104TA000",
            "expcode": "KR4104TA0007",
            "hname": "VF 2310"
        },
        {
            "shcode": "104TB000",
            "expcode": "KR4104TB0006",
            "hname": "VF 2311"
        },
        {
            "shcode": "404T6T7S",
            "expcode": "KR4404T6T7S7",
            "hname": "VF SP 06-2307"
        },
        {
            "shcode": "404T6T8S",
            "expcode": "KR4404T6T8S5",
            "hname": "VF SP 06-2308"
        },
        {
            "shcode": "404T6T9S",
            "expcode": "KR4404T6T9S3",
            "hname": "VF SP 06-2309"
        },
        {
            "shcode": "404T6TAS",
            "expcode": "KR4404T6TAS2",
            "hname": "VF SP 06-2310"
        },
        {
            "shcode": "404T6TBS",
            "expcode": "KR4404T6TBS0",
            "hname": "VF SP 06-2311"
        }
    ],
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t9944"></a>
## `t9944` 지수옵션마스터조회API용

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
| `t9944InBlock` | t9944InBlock | Object | Y | - | - |
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
| `t9944OutBlock` | t9944OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |


### 요청 Example

```json
{
  "t9944InBlock": {
    "dummy": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t9944OutBlock": [
        {
            "shcode": "201T6160",
            "expcode": "KR4201T61606",
            "hname": "C 2306 160.0"
        },
        {
            "shcode": "201T6162",
            "expcode": "KR4201T61622",
            "hname": "C 2306 162.5"
        },
        {
            "shcode": "201T6165",
            "expcode": "KR4201T61655",
            "hname": "C 2306 165.0"
        },
        {
            "shcode": "201T6167",
            "expcode": "KR4201T61671",
            "hname": "C 2306 167.5"
        },
        {
            "shcode": "201T6170",
            "expcode": "KR4201T61705",
            "hname": "C 2306 170.0"
        },
        {
            "shcode": "201T6172",
            "expcode": "KR4201T61721",
            "hname": "C 2306 172.5"
        }
  ]
}
```

---

<a id="tr-t8455"></a>
## `t8455` KRX야간파생 마스터조회(API용)

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
| `t8455InBlock` | t8455InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분(NF/NC/NM/NO) | String | Y | 2 | - 선물 gubun<br/>NFU : KOSPI200선물<br/>NMF : 미니선물<br/>NQF : 코스닥150선물<br/>NCF : 상품선물<br/>- 옵션 gubun<br/>NOP : KOSPI200옵션<br/>NMO : 미니옵션<br/>NQO : 코스닥150옵션<br/>NWO : 위클리옵션 |


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
| `t8455OutBlock` | t8455OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-expcode` | 표준코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-tradeunit` | 거래승수 | Number | Y | 21.8 | - |
| `&nbsp;&nbsp;-atmgb` | ATM구분(1:ATM2:ITM3:OTM) | String | Y | 1 | - |


### 요청 Example

```json
{
  "t8455InBlock": {
    "gubun": "NFU"
  }
}
```

### 응답 Example

```json
{
	"t8455OutBlock": [
		{
			"hname": "F 2506",
			"shcode": "101W6000",
			"expcode": "KR4101W60000",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F 2509",
			"shcode": "101W9000",
			"expcode": "KR4101W90007",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F 2512",
			"shcode": "101WC000",
			"expcode": "KR4101WC0003",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F 2603",
			"shcode": "A0163000",
			"expcode": "KR4A01630008",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F 2606",
			"shcode": "A0166000",
			"expcode": "KR4A01660005",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F 2612",
			"shcode": "A016C000",
			"expcode": "KR4A016C0004",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F 2712",
			"shcode": "A017C000",
			"expcode": "KR4A017C0003",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F SP 06-2509",
			"shcode": "401W6W9S",
			"expcode": "KR4401W6W9S8",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F SP 06-2512",
			"shcode": "401W6WCS",
			"expcode": "KR4401W6WCS0",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F SP 06-2603",
			"shcode": "401W663S",
			"expcode": "KR4401W663S0",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F SP 06-2606",
			"shcode": "401W666S",
			"expcode": "KR4401W666S3",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F SP 06-2612",
			"shcode": "401W66CS",
			"expcode": "KR4401W66CS7",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		},
		{
			"hname": "F SP 06-2712",
			"shcode": "401W67CS",
			"expcode": "KR4401W67CS5",
			"tradeunit": "250000.00000000",
			"atmgb": ""
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8456"></a>
## `t8456` KRX야간파생 시세조회(API용)

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
| `t8456InBlock` | t8456InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |


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
| `t8456OutBlock` | t8456OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-theoryprice` | 이론가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-impv` | 내재가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-timevl` | 시간가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-kospijisu` | KOSPI200지수 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-kospisign` | KOSPI200전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-kospichange` | KOSPI200전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-kospidiff` | KOSPI200등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cmeprice` | CME야간선물현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cmesign` | CME야간선물전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-cmechange` | CME야간선물전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cmediff` | CME야간선물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cmefocode` | CME야간선물종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-uplmtprice` | 정규장적용상한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 정규장적용하한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-yeprice` | 예상체결가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-ysign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-ychange` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-ydiff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-danhochk` | 단일가호가여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilvalue` | 전일거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-uplmtprice_3rd` | 정규장3단계상한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-dnlmtprice_3rd` | 정규장3단계하한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-ndv_uplmtprice` | 야간장_적용상한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-ndv_dnlmtprice` | 야간장_적용하한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-ndv_rt_uplmtprice` | 야간장_실시간상한가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-ndv_rt_dnlmtprice` | 야간장_실시간하한가 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t8456InBlock": {
    "focode": "101W9000"
  }
}
```

### 응답 Example

```json
{
	"t8456OutBlock": {
		"hname": "코스피200 F 202509",
		"price": "424.70",
		"sign": "5",
		"change": "0.70",
		"jnilclose": "425.40",
		"diff": "-0.16",
		"volume": 11275,
		"value": 1196821488,
		"open": "425.05",
		"high": "425.30",
		"low": "423.60",
		"recprice": "425.40",
		"theoryprice": "0",
		"actprice": "0.00",
		"impv": "0.00",
		"timevl": "-3.97",
		"kospijisu": "428.67",
		"kospisign": "2",
		"kospichange": "4.26",
		"kospidiff": "1.00",
		"cmeprice": "424.70",
		"cmesign": "5",
		"cmechange": "0.70",
		"cmediff": "-0.16",
		"cmefocode": "101W9000",
		"uplmtprice": "459.40",
		"dnlmtprice": "391.40",
		"focode": "101W9000",
		"yeprice": "424.70",
		"ysign": "5",
		"ychange": "0.70",
		"ydiff": "-0.16",
		"danhochk": "0",
		"jnilvolume": 15296,
		"jnilvalue": 1621978500,
		"uplmtprice_3rd": "510.45",
		"dnlmtprice_3rd": "340.35",
		"ndv_uplmtprice": "459.40",
		"ndv_dnlmtprice": "391.40",
		"ndv_rt_uplmtprice": "459.40",
		"ndv_rt_dnlmtprice": "391.40"
	},
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-t8457"></a>
## `t8457` KRX야간파생 호가조회(API용)

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
| `t8457InBlock` | t8457InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |


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
| `t8457OutBlock` | t8457OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt1` | 매도호가건수1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt1` | 매수호가건수1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt2` | 매도호가건수2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt2` | 매수호가건수2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt3` | 매도호가건수3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt3` | 매수호가건수3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt4` | 매도호가건수4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt4` | 매수호가건수4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcnt5` | 매도호가건수5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scnt5` | 매수호가건수5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dvol` | 매도호가총수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol` | 매수호가총수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-toffernum` | 총매도호가건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tbidnum` | 총매수호가건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 수신시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |


### 요청 Example

```json
{
  "t8457InBlock": {
    "shcode": "101W6000"
  }
}
```

### 응답 Example

```json
{
	"t8457OutBlock": {
		"hname": "코스피200 F 202506",
		"price": "407.50",
		"sign": "2",
		"change": "1.35",
		"diff": "0.33",
		"volume": 6969,
		"jnilclose": "406.15",
		"offerho1": "410.00",
		"bidho1": "407.50",
		"offerrem1": 5,
		"bidrem1": 75,
		"dcnt1": 1,
		"scnt1": 4,
		"offerho2": "430.00",
		"bidho2": "406.50",
		"offerrem2": 500,
		"bidrem2": 11,
		"dcnt2": 1,
		"scnt2": 2,
		"offerho3": "435.00",
		"bidho3": "406.45",
		"offerrem3": 500,
		"bidrem3": 2,
		"dcnt3": 1,
		"scnt3": 2,
		"offerho4": "0.00",
		"bidho4": "406.40",
		"offerrem4": 0,
		"bidrem4": 370,
		"dcnt4": 0,
		"scnt4": 3,
		"offerho5": "0.00",
		"bidho5": "406.30",
		"offerrem5": 0,
		"bidrem5": 10,
		"dcnt5": 0,
		"scnt5": 1,
		"dvol": 1005,
		"svol": 789,
		"toffernum": 3,
		"tbidnum": 122,
		"time": "160931",
		"shcode": "101W6000"
	},
	"rsp_cd": "00000",
	"rsp_msg": "조회완료"
}
```

---

<a id="tr-t8458"></a>
## `t8458` KRX야간파생 시간대별체결(API용)

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
| `t8458InBlock` | t8458InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-focode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stime` | 시작시간 | String | Y | 4 | - |
| `&nbsp;&nbsp;-etime` | 종료시간 | String | Y | 4 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |


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
| `t8458OutBlock` | t8458OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |
| `t8458OutBlock1` | t8458OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_msvolume` | 누적매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_mdvolume` | 누적매도체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-s_msvolume` | 누적순매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-n_mschecnt` | 누적매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-n_mdchecnt` | 누적매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-s_mschecnt` | 누적순매수체결건수 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t8458InBlock": {
    "focode": "101W6000",
    "cvolume": 0,
    "stime": "",
    "etime": "",
    "cts_time": ""
  }
}
```

### 응답 Example

```json
{
	"t8458OutBlock": {
		"cts_time": "1609311813"
	},
	"t8458OutBlock1": [
		{
			"chetime": "1609471992",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 9,
			"chdegree": "144.55",
			"offerho": "407.50",
			"bidho": "406.50",
			"volume": "7045",
			"n_msvolume": "3063",
			"n_mdvolume": "2119",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 174,
			"s_mschecnt": 18
		},
		{
			"chetime": "1609464045",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 10,
			"chdegree": "145.17",
			"offerho": "407.95",
			"bidho": "407.50",
			"volume": "7036",
			"n_msvolume": "3063",
			"n_mdvolume": "2110",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 173,
			"s_mschecnt": 19
		},
		{
			"chetime": "1609460283",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 10,
			"chdegree": "145.86",
			"offerho": "407.95",
			"bidho": "407.50",
			"volume": "7026",
			"n_msvolume": "3063",
			"n_mdvolume": "2100",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 172,
			"s_mschecnt": 20
		},
		{
			"chetime": "1609455185",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 10,
			"chdegree": "146.56",
			"offerho": "407.95",
			"bidho": "407.50",
			"volume": "7016",
			"n_msvolume": "3063",
			"n_mdvolume": "2090",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 171,
			"s_mschecnt": 21
		},
		{
			"chetime": "1609446411",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 10,
			"chdegree": "147.26",
			"offerho": "407.95",
			"bidho": "407.50",
			"volume": "7006",
			"n_msvolume": "3063",
			"n_mdvolume": "2080",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 170,
			"s_mschecnt": 22
		},
		{
			"chetime": "1609442580",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 9,
			"chdegree": "147.97",
			"offerho": "407.90",
			"bidho": "407.50",
			"volume": "6996",
			"n_msvolume": "3063",
			"n_mdvolume": "2070",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 169,
			"s_mschecnt": 23
		},
		{
			"chetime": "1609370811",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 10,
			"chdegree": "148.62",
			"offerho": "407.90",
			"bidho": "407.50",
			"volume": "6987",
			"n_msvolume": "3063",
			"n_mdvolume": "2061",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 168,
			"s_mschecnt": 24
		},
		{
			"chetime": "1609327291",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.34",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6977",
			"n_msvolume": "3063",
			"n_mdvolume": "2051",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 167,
			"s_mschecnt": 25
		},
		{
			"chetime": "1609326459",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.41",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6976",
			"n_msvolume": "3063",
			"n_mdvolume": "2050",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 166,
			"s_mschecnt": 26
		},
		{
			"chetime": "1609324709",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.49",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6975",
			"n_msvolume": "3063",
			"n_mdvolume": "2049",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 165,
			"s_mschecnt": 27
		},
		{
			"chetime": "1609323787",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.56",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6974",
			"n_msvolume": "3063",
			"n_mdvolume": "2048",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 164,
			"s_mschecnt": 28
		},
		{
			"chetime": "1609321985",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.63",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6973",
			"n_msvolume": "3063",
			"n_mdvolume": "2047",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 163,
			"s_mschecnt": 29
		},
		{
			"chetime": "1609321137",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.71",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6972",
			"n_msvolume": "3063",
			"n_mdvolume": "2046",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 162,
			"s_mschecnt": 30
		},
		{
			"chetime": "1609319271",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.78",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6971",
			"n_msvolume": "3063",
			"n_mdvolume": "2045",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 161,
			"s_mschecnt": 31
		},
		{
			"chetime": "1609318470",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.85",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6970",
			"n_msvolume": "3063",
			"n_mdvolume": "2044",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 160,
			"s_mschecnt": 32
		},
		{
			"chetime": "1609316740",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "149.93",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6969",
			"n_msvolume": "3063",
			"n_mdvolume": "2043",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 159,
			"s_mschecnt": 33
		},
		{
			"chetime": "1609315925",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "150.00",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6968",
			"n_msvolume": "3063",
			"n_mdvolume": "2042",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 158,
			"s_mschecnt": 34
		},
		{
			"chetime": "1609314037",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "150.07",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6967",
			"n_msvolume": "3063",
			"n_mdvolume": "2041",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 157,
			"s_mschecnt": 35
		},
		{
			"chetime": "1609313226",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "150.15",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6966",
			"n_msvolume": "3063",
			"n_mdvolume": "2040",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 156,
			"s_mschecnt": 36
		},
		{
			"chetime": "1609311813",
			"price": "407.50",
			"sign": "2",
			"change": "1.35",
			"cvolume": 1,
			"chdegree": "150.22",
			"offerho": "410.00",
			"bidho": "407.50",
			"volume": "6965",
			"n_msvolume": "3063",
			"n_mdvolume": "2039",
			"s_msvolume": "0",
			"n_mschecnt": 192,
			"n_mdchecnt": 155,
			"s_mschecnt": 37
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8459"></a>
## `t8459` KRX야간파생 기간별주가(API용)

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
| `t8459InBlock` | t8459InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-futcheck` | 선물최근월물 | String | Y | 1 | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_code` | CTS종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lastdate` | 전종목만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cnt` | 조회요청건수 | Object | Y | 3 | - |


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
| `t8459OutBlock` | t8459OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_code` | CTS종목코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lastdate` | 전종목만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-nowfutyn` | 최근월선물여부 | String | Y | 1 | - |
| `t8459OutBlock1` | t8459OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |


### 요청 Example

```json
{
   "t8459InBlock" :{
      "shcode" : "201W7342",
      "futcheck" : "",
      "date" : "",
      "cts_code" : "",
      "lastdate" : "",
      "cnt" : 20
   }
}
```

### 응답 Example

```json
{
	"t8459OutBlock": {
		"date": "",
		"cts_code": "201W7342",
		"lastdate": "",
		"nowfutyn": "N"
	},
	"t8459OutBlock1": [
		{
			"date": "20250610",
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"close": "33.70",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"diff_vol": "0.00"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8460"></a>
## `t8460` KRX야간파생 옵션 전광판

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
| `t8460InBlock` | t8460InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-yyyymm` | 월물(혹은주물WN) | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun` | 구분(G:원지수W:위클리) | String | Y | 1 | M:미니<br/>G:원지수<br/>Q:코스닥<br/>W:위클리 |


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
| `t8460OutBlock` | t8460OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gmprice` | 근월물현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gmsign` | 근월물전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-gmchange` | 근월물전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gmdiff` | 근월물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-gmvolume` | 근월물거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gmshcode` | 근월물선물코드 | String | Y | 8 | - |
| `t8460OutBlock1` | t8460OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-optcode` | 콜옵션코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-impv` | 내재가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-timevl` | 시간가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-atmgubun` | ATM구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jisuconv` | 지수환산 | Number | Y | 6.2 | - |
| `t8460OutBlock2` | t8460OutBlock2 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-actprice` | 행사가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-optcode` | 풋옵션코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-impv` | 내재가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-timevl` | 시간가치 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-atmgubun` | ATM구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jisuconv` | 지수환산 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t8460InBlock": {
    "yyyymm": "202506",
    "gubun": "M"
  }
}
```

### 응답 Example

```json
{
	"t8460OutBlock": {
		"gmprice": "434.75",
		"gmsign": "2",
		"gmchange": "28.60",
		"gmdiff": "7.04",
		"gmvolume": 8274,
		"gmshcode": "101W6000"
	},
	"t8460OutBlock1": [
		{
			"actprice": "457.50",
			"optcode": "205W6457",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3416.67"
		},
		{
			"actprice": "455.00",
			"optcode": "205W6455",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3398.00"
		},
		{
			"actprice": "452.50",
			"optcode": "205W6452",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3379.33"
		},
		{
			"actprice": "450.00",
			"optcode": "205W6450",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3360.66"
		},
		{
			"actprice": "447.50",
			"optcode": "205W6447",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3341.99"
		},
		{
			"actprice": "445.00",
			"optcode": "205W6445",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3323.32"
		},
		{
			"actprice": "442.50",
			"optcode": "205W6442",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3304.65"
		},
		{
			"actprice": "440.00",
			"optcode": "205W6440",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3285.98"
		},
		{
			"actprice": "437.50",
			"optcode": "205W6437",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3267.31"
		},
		{
			"actprice": "435.00",
			"optcode": "205W6435",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3248.64"
		},
		{
			"actprice": "432.50",
			"optcode": "205W6432",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3229.97"
		},
		{
			"actprice": "430.00",
			"optcode": "205W6430",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3211.30"
		},
		{
			"actprice": "427.50",
			"optcode": "205W6427",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3192.63"
		},
		{
			"actprice": "425.00",
			"optcode": "205W6425",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3173.96"
		},
		{
			"actprice": "422.50",
			"optcode": "205W6422",
			"price": "0.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3155.29"
		},
		{
			"actprice": "420.00",
			"optcode": "205W6420",
			"price": "0.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3136.61"
		},
		{
			"actprice": "417.50",
			"optcode": "205W6417",
			"price": "0.09",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.09",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3117.94"
		},
		{
			"actprice": "415.00",
			"optcode": "205W6415",
			"price": "0.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3099.27"
		},
		{
			"actprice": "412.50",
			"optcode": "205W6412",
			"price": "0.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3080.60"
		},
		{
			"actprice": "410.00",
			"optcode": "205W6410",
			"price": "0.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3061.93"
		},
		{
			"actprice": "407.50",
			"optcode": "205W6407",
			"price": "0.04",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.04",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3043.26"
		},
		{
			"actprice": "405.00",
			"optcode": "205W6405",
			"price": "0.04",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.04",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3024.59"
		},
		{
			"actprice": "402.50",
			"optcode": "205W6402",
			"price": "0.04",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.04",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "3005.92"
		},
		{
			"actprice": "400.00",
			"optcode": "205W6400",
			"price": "0.13",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.13",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2987.25"
		},
		{
			"actprice": "397.50",
			"optcode": "205W6397",
			"price": "0.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2968.58"
		},
		{
			"actprice": "395.00",
			"optcode": "205W6395",
			"price": "0.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.02",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2949.91"
		},
		{
			"actprice": "392.50",
			"optcode": "205W6392",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2931.24"
		},
		{
			"actprice": "390.00",
			"optcode": "205W6390",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2912.57"
		},
		{
			"actprice": "387.50",
			"optcode": "205W6387",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2893.90"
		},
		{
			"actprice": "385.00",
			"optcode": "205W6385",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2875.23"
		},
		{
			"actprice": "382.50",
			"optcode": "205W6382",
			"price": "1.75",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "1.76",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "1.75",
			"offerrem1": 0,
			"bidrem1": 1,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2856.56"
		},
		{
			"actprice": "380.00",
			"optcode": "205W6380",
			"price": "7.24",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "7.24",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2837.89"
		},
		{
			"actprice": "377.50",
			"optcode": "205W6377",
			"price": "10.00",
			"sign": "5",
			"change": "6.00",
			"diff": "-37.50",
			"volume": 75,
			"offerho1": "10.00",
			"bidho1": "9.92",
			"cvolume": 13,
			"impv": "0.00",
			"timevl": "10.00",
			"offerrem1": 45,
			"bidrem1": 2,
			"open": "10.00",
			"high": "10.00",
			"low": "9.98",
			"atmgubun": "1",
			"jisuconv": "2819.22"
		},
		{
			"actprice": "375.00",
			"optcode": "205W6375",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 3,
			"offerho1": "0.01",
			"bidho1": "0.00",
			"cvolume": 3,
			"impv": "1.54",
			"timevl": "-1.53",
			"offerrem1": 2,
			"bidrem1": 0,
			"open": "0.01",
			"high": "0.01",
			"low": "0.01",
			"atmgubun": "2",
			"jisuconv": "2800.55"
		},
		{
			"actprice": "372.50",
			"optcode": "205W6372",
			"price": "11.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "4.04",
			"timevl": "6.96",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2781.88"
		},
		{
			"actprice": "370.00",
			"optcode": "205W6370",
			"price": "10.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "6.54",
			"timevl": "3.56",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2763.21"
		},
		{
			"actprice": "367.50",
			"optcode": "205W6367",
			"price": "10.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "9.04",
			"timevl": "0.96",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2744.54"
		},
		{
			"actprice": "365.00",
			"optcode": "205W6365",
			"price": "11.65",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "11.54",
			"timevl": "0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2725.87"
		},
		{
			"actprice": "362.50",
			"optcode": "205W6362",
			"price": "14.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "14.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2707.20"
		},
		{
			"actprice": "360.00",
			"optcode": "205W6360",
			"price": "16.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "16.54",
			"timevl": "-0.54",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2688.53"
		},
		{
			"actprice": "357.50",
			"optcode": "205W6357",
			"price": "19.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "19.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2669.86"
		},
		{
			"actprice": "355.00",
			"optcode": "205W6355",
			"price": "21.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "21.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2651.19"
		},
		{
			"actprice": "352.50",
			"optcode": "205W6352",
			"price": "24.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "24.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2632.52"
		},
		{
			"actprice": "350.00",
			"optcode": "205W6350",
			"price": "26.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "26.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2613.85"
		},
		{
			"actprice": "347.50",
			"optcode": "205W6347",
			"price": "29.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "29.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2595.18"
		},
		{
			"actprice": "345.00",
			"optcode": "205W6345",
			"price": "31.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "31.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2576.51"
		},
		{
			"actprice": "342.50",
			"optcode": "205W6342",
			"price": "34.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "34.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2557.83"
		},
		{
			"actprice": "340.00",
			"optcode": "205W6340",
			"price": "36.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "36.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2539.16"
		},
		{
			"actprice": "337.50",
			"optcode": "205W6337",
			"price": "39.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "39.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2520.49"
		},
		{
			"actprice": "335.00",
			"optcode": "205W6335",
			"price": "41.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "41.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2501.82"
		},
		{
			"actprice": "332.50",
			"optcode": "205W6332",
			"price": "44.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "44.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2483.15"
		},
		{
			"actprice": "330.00",
			"optcode": "205W6330",
			"price": "46.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "46.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2464.48"
		},
		{
			"actprice": "327.50",
			"optcode": "205W6327",
			"price": "49.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "49.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2445.81"
		},
		{
			"actprice": "325.00",
			"optcode": "205W6325",
			"price": "51.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "51.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2427.14"
		},
		{
			"actprice": "322.50",
			"optcode": "205W6322",
			"price": "54.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "54.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2408.47"
		},
		{
			"actprice": "320.00",
			"optcode": "205W6320",
			"price": "56.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "56.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2389.80"
		},
		{
			"actprice": "317.50",
			"optcode": "205W6317",
			"price": "59.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "59.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2371.13"
		},
		{
			"actprice": "315.00",
			"optcode": "205W6315",
			"price": "61.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "61.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2352.46"
		},
		{
			"actprice": "312.50",
			"optcode": "205W6312",
			"price": "64.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "64.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2333.79"
		},
		{
			"actprice": "310.00",
			"optcode": "205W6310",
			"price": "66.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "66.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2315.12"
		},
		{
			"actprice": "307.50",
			"optcode": "205W6307",
			"price": "69.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "69.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2296.45"
		},
		{
			"actprice": "305.00",
			"optcode": "205W6305",
			"price": "71.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "71.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2277.78"
		},
		{
			"actprice": "302.50",
			"optcode": "205W6302",
			"price": "74.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "74.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2259.11"
		},
		{
			"actprice": "300.00",
			"optcode": "205W6300",
			"price": "76.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "76.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2240.44"
		},
		{
			"actprice": "297.50",
			"optcode": "205W6297",
			"price": "79.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "79.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2221.77"
		},
		{
			"actprice": "295.00",
			"optcode": "205W6295",
			"price": "81.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "81.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2203.10"
		},
		{
			"actprice": "292.50",
			"optcode": "205W6292",
			"price": "84.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "84.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2184.43"
		},
		{
			"actprice": "290.00",
			"optcode": "205W6290",
			"price": "86.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "86.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2165.76"
		},
		{
			"actprice": "287.50",
			"optcode": "205W6287",
			"price": "89.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "89.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2147.09"
		},
		{
			"actprice": "285.00",
			"optcode": "205W6285",
			"price": "91.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "91.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2128.42"
		},
		{
			"actprice": "282.50",
			"optcode": "205W6282",
			"price": "94.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "94.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2109.75"
		},
		{
			"actprice": "280.00",
			"optcode": "205W6280",
			"price": "96.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "96.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2091.08"
		},
		{
			"actprice": "277.50",
			"optcode": "205W6277",
			"price": "99.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "99.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2072.41"
		},
		{
			"actprice": "275.00",
			"optcode": "205W6275",
			"price": "101.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "101.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2053.74"
		},
		{
			"actprice": "272.50",
			"optcode": "205W6272",
			"price": "104.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "104.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2035.07"
		},
		{
			"actprice": "270.00",
			"optcode": "205W6270",
			"price": "106.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "106.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2016.40"
		},
		{
			"actprice": "267.50",
			"optcode": "205W6267",
			"price": "109.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "109.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1997.73"
		},
		{
			"actprice": "265.00",
			"optcode": "205W6265",
			"price": "111.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "111.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1979.05"
		},
		{
			"actprice": "262.50",
			"optcode": "205W6262",
			"price": "114.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "114.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1960.38"
		},
		{
			"actprice": "260.00",
			"optcode": "205W6260",
			"price": "116.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "116.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1941.71"
		},
		{
			"actprice": "257.50",
			"optcode": "205W6257",
			"price": "119.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "119.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1923.04"
		},
		{
			"actprice": "255.00",
			"optcode": "205W6255",
			"price": "121.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "121.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1904.37"
		},
		{
			"actprice": "252.50",
			"optcode": "205W6252",
			"price": "124.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "124.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1885.70"
		},
		{
			"actprice": "250.00",
			"optcode": "205W6250",
			"price": "126.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "126.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1867.03"
		},
		{
			"actprice": "247.50",
			"optcode": "205W6247",
			"price": "129.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "129.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1848.36"
		},
		{
			"actprice": "245.00",
			"optcode": "205W6245",
			"price": "131.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "131.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1829.69"
		},
		{
			"actprice": "242.50",
			"optcode": "205W6242",
			"price": "134.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "134.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1811.02"
		},
		{
			"actprice": "240.00",
			"optcode": "205W6240",
			"price": "136.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "136.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1792.35"
		},
		{
			"actprice": "237.50",
			"optcode": "205W6237",
			"price": "139.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "139.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1773.68"
		},
		{
			"actprice": "235.00",
			"optcode": "205W6235",
			"price": "141.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "141.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1755.01"
		},
		{
			"actprice": "232.50",
			"optcode": "205W6232",
			"price": "144.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "144.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1736.34"
		},
		{
			"actprice": "230.00",
			"optcode": "205W6230",
			"price": "146.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "146.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1717.67"
		},
		{
			"actprice": "227.50",
			"optcode": "205W6227",
			"price": "149.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "149.04",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1699.00"
		},
		{
			"actprice": "225.00",
			"optcode": "205W6225",
			"price": "151.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "151.54",
			"timevl": "0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "1680.33"
		}
	],
	"t8460OutBlock2": [
		{
			"actprice": "457.50",
			"optcode": "305W6457",
			"price": "80.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "80.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3416.67"
		},
		{
			"actprice": "455.00",
			"optcode": "305W6455",
			"price": "78.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "78.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3398.00"
		},
		{
			"actprice": "452.50",
			"optcode": "305W6452",
			"price": "75.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "75.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3379.33"
		},
		{
			"actprice": "450.00",
			"optcode": "305W6450",
			"price": "73.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "73.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3360.66"
		},
		{
			"actprice": "447.50",
			"optcode": "305W6447",
			"price": "70.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "70.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3341.99"
		},
		{
			"actprice": "445.00",
			"optcode": "305W6445",
			"price": "68.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "68.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3323.32"
		},
		{
			"actprice": "442.50",
			"optcode": "305W6442",
			"price": "65.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "65.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3304.65"
		},
		{
			"actprice": "440.00",
			"optcode": "305W6440",
			"price": "63.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "63.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3285.98"
		},
		{
			"actprice": "437.50",
			"optcode": "305W6437",
			"price": "60.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "60.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3267.31"
		},
		{
			"actprice": "435.00",
			"optcode": "305W6435",
			"price": "58.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "58.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3248.64"
		},
		{
			"actprice": "432.50",
			"optcode": "305W6432",
			"price": "55.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "55.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3229.97"
		},
		{
			"actprice": "430.00",
			"optcode": "305W6430",
			"price": "53.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "53.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3211.30"
		},
		{
			"actprice": "427.50",
			"optcode": "305W6427",
			"price": "50.85",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "50.96",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3192.63"
		},
		{
			"actprice": "425.00",
			"optcode": "305W6425",
			"price": "48.35",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "48.46",
			"timevl": "-0.11",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3173.96"
		},
		{
			"actprice": "422.50",
			"optcode": "305W6422",
			"price": "45.90",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "45.96",
			"timevl": "-0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3155.29"
		},
		{
			"actprice": "420.00",
			"optcode": "305W6420",
			"price": "43.40",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "43.46",
			"timevl": "-0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3136.61"
		},
		{
			"actprice": "417.50",
			"optcode": "305W6417",
			"price": "40.90",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "40.96",
			"timevl": "-0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3117.94"
		},
		{
			"actprice": "415.00",
			"optcode": "305W6415",
			"price": "38.40",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "38.46",
			"timevl": "-0.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3099.27"
		},
		{
			"actprice": "412.50",
			"optcode": "305W6412",
			"price": "35.95",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "35.96",
			"timevl": "-0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3080.60"
		},
		{
			"actprice": "410.00",
			"optcode": "305W6410",
			"price": "33.45",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "33.46",
			"timevl": "-0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3061.93"
		},
		{
			"actprice": "407.50",
			"optcode": "305W6407",
			"price": "31.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "30.96",
			"timevl": "0.04",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3043.26"
		},
		{
			"actprice": "405.00",
			"optcode": "305W6405",
			"price": "28.60",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "28.46",
			"timevl": "0.14",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3024.59"
		},
		{
			"actprice": "402.50",
			"optcode": "305W6402",
			"price": "26.20",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "25.96",
			"timevl": "0.24",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "3005.92"
		},
		{
			"actprice": "400.00",
			"optcode": "305W6400",
			"price": "24.25",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "23.46",
			"timevl": "0.79",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2987.25"
		},
		{
			"actprice": "397.50",
			"optcode": "305W6397",
			"price": "21.40",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "20.96",
			"timevl": "0.44",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2968.58"
		},
		{
			"actprice": "395.00",
			"optcode": "305W6395",
			"price": "19.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "18.46",
			"timevl": "0.54",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2949.91"
		},
		{
			"actprice": "392.50",
			"optcode": "305W6392",
			"price": "16.70",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "15.96",
			"timevl": "0.74",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2931.24"
		},
		{
			"actprice": "390.00",
			"optcode": "305W6390",
			"price": "14.40",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "13.46",
			"timevl": "0.94",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2912.57"
		},
		{
			"actprice": "387.50",
			"optcode": "305W6387",
			"price": "12.20",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "10.96",
			"timevl": "1.24",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2893.90"
		},
		{
			"actprice": "385.00",
			"optcode": "305W6385",
			"price": "10.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "8.46",
			"timevl": "1.54",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2875.23"
		},
		{
			"actprice": "382.50",
			"optcode": "305W6382",
			"price": "8.02",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "5.96",
			"timevl": "2.06",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2856.56"
		},
		{
			"actprice": "380.00",
			"optcode": "305W6380",
			"price": "6.16",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "3.46",
			"timevl": "2.70",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "2",
			"jisuconv": "2837.89"
		},
		{
			"actprice": "377.50",
			"optcode": "305W6377",
			"price": "3.22",
			"sign": "5",
			"change": "1.84",
			"diff": "-36.36",
			"volume": 2,
			"offerho1": "10.00",
			"bidho1": "0.00",
			"cvolume": 1,
			"impv": "0.96",
			"timevl": "2.26",
			"offerrem1": 1,
			"bidrem1": 0,
			"open": "3.56",
			"high": "3.56",
			"low": "3.22",
			"atmgubun": "1",
			"jisuconv": "2819.22"
		},
		{
			"actprice": "375.00",
			"optcode": "305W6375",
			"price": "1.80",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "1.80",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2800.55"
		},
		{
			"actprice": "372.50",
			"optcode": "305W6372",
			"price": "2.80",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "2.80",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "2.80",
			"offerrem1": 2,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2781.88"
		},
		{
			"actprice": "370.00",
			"optcode": "305W6370",
			"price": "2.03",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "2.03",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2763.21"
		},
		{
			"actprice": "367.50",
			"optcode": "305W6367",
			"price": "1.10",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "1.10",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2744.54"
		},
		{
			"actprice": "365.00",
			"optcode": "305W6365",
			"price": "2.98",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "2.98",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2725.87"
		},
		{
			"actprice": "362.50",
			"optcode": "305W6362",
			"price": "5.44",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "5.44",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2707.20"
		},
		{
			"actprice": "360.00",
			"optcode": "305W6360",
			"price": "10.00",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "10.00",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2688.53"
		},
		{
			"actprice": "357.50",
			"optcode": "305W6357",
			"price": "6.72",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "6.72",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2669.86"
		},
		{
			"actprice": "355.00",
			"optcode": "305W6355",
			"price": "5.54",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "5.54",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2651.19"
		},
		{
			"actprice": "352.50",
			"optcode": "305W6352",
			"price": "4.42",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "4.42",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2632.52"
		},
		{
			"actprice": "350.00",
			"optcode": "305W6350",
			"price": "3.56",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "3.56",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2613.85"
		},
		{
			"actprice": "347.50",
			"optcode": "305W6347",
			"price": "2.55",
			"sign": "5",
			"change": "0.14",
			"diff": "-5.20",
			"volume": 10,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 10,
			"impv": "0.00",
			"timevl": "2.55",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "2.55",
			"high": "2.55",
			"low": "2.55",
			"atmgubun": "3",
			"jisuconv": "2595.18"
		},
		{
			"actprice": "345.00",
			"optcode": "305W6345",
			"price": "2.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 10,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 10,
			"impv": "0.00",
			"timevl": "2.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "2.01",
			"high": "2.01",
			"low": "2.01",
			"atmgubun": "3",
			"jisuconv": "2576.51"
		},
		{
			"actprice": "342.50",
			"optcode": "305W6342",
			"price": "1.42",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "1.42",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2557.83"
		},
		{
			"actprice": "340.00",
			"optcode": "305W6340",
			"price": "0.98",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.98",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2539.16"
		},
		{
			"actprice": "337.50",
			"optcode": "305W6337",
			"price": "0.51",
			"sign": "5",
			"change": "0.09",
			"diff": "-15.00",
			"volume": 10,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 10,
			"impv": "0.00",
			"timevl": "0.51",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.51",
			"high": "0.51",
			"low": "0.51",
			"atmgubun": "3",
			"jisuconv": "2520.49"
		},
		{
			"actprice": "335.00",
			"optcode": "305W6335",
			"price": "0.37",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.37",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2501.82"
		},
		{
			"actprice": "332.50",
			"optcode": "305W6332",
			"price": "0.20",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.20",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2483.15"
		},
		{
			"actprice": "330.00",
			"optcode": "305W6330",
			"price": "0.09",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.09",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2464.48"
		},
		{
			"actprice": "327.50",
			"optcode": "305W6327",
			"price": "0.04",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.04",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2445.81"
		},
		{
			"actprice": "325.00",
			"optcode": "305W6325",
			"price": "0.05",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.05",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2427.14"
		},
		{
			"actprice": "322.50",
			"optcode": "305W6322",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2408.47"
		},
		{
			"actprice": "320.00",
			"optcode": "305W6320",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2389.80"
		},
		{
			"actprice": "317.50",
			"optcode": "305W6317",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2371.13"
		},
		{
			"actprice": "315.00",
			"optcode": "305W6315",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2352.46"
		},
		{
			"actprice": "312.50",
			"optcode": "305W6312",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2333.79"
		},
		{
			"actprice": "310.00",
			"optcode": "305W6310",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2315.12"
		},
		{
			"actprice": "307.50",
			"optcode": "305W6307",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2296.45"
		},
		{
			"actprice": "305.00",
			"optcode": "305W6305",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2277.78"
		},
		{
			"actprice": "302.50",
			"optcode": "305W6302",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2259.11"
		},
		{
			"actprice": "300.00",
			"optcode": "305W6300",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2240.44"
		},
		{
			"actprice": "297.50",
			"optcode": "305W6297",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2221.77"
		},
		{
			"actprice": "295.00",
			"optcode": "305W6295",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2203.10"
		},
		{
			"actprice": "292.50",
			"optcode": "305W6292",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2184.43"
		},
		{
			"actprice": "290.00",
			"optcode": "305W6290",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2165.76"
		},
		{
			"actprice": "287.50",
			"optcode": "305W6287",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2147.09"
		},
		{
			"actprice": "285.00",
			"optcode": "305W6285",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2128.42"
		},
		{
			"actprice": "282.50",
			"optcode": "305W6282",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2109.75"
		},
		{
			"actprice": "280.00",
			"optcode": "305W6280",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2091.08"
		},
		{
			"actprice": "277.50",
			"optcode": "305W6277",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2072.41"
		},
		{
			"actprice": "275.00",
			"optcode": "305W6275",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2053.74"
		},
		{
			"actprice": "272.50",
			"optcode": "305W6272",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2035.07"
		},
		{
			"actprice": "270.00",
			"optcode": "305W6270",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "2016.40"
		},
		{
			"actprice": "267.50",
			"optcode": "305W6267",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1997.73"
		},
		{
			"actprice": "265.00",
			"optcode": "305W6265",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1979.05"
		},
		{
			"actprice": "262.50",
			"optcode": "305W6262",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1960.38"
		},
		{
			"actprice": "260.00",
			"optcode": "305W6260",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1941.71"
		},
		{
			"actprice": "257.50",
			"optcode": "305W6257",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1923.04"
		},
		{
			"actprice": "255.00",
			"optcode": "305W6255",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1904.37"
		},
		{
			"actprice": "252.50",
			"optcode": "305W6252",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1885.70"
		},
		{
			"actprice": "250.00",
			"optcode": "305W6250",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1867.03"
		},
		{
			"actprice": "247.50",
			"optcode": "305W6247",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1848.36"
		},
		{
			"actprice": "245.00",
			"optcode": "305W6245",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1829.69"
		},
		{
			"actprice": "242.50",
			"optcode": "305W6242",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1811.02"
		},
		{
			"actprice": "240.00",
			"optcode": "305W6240",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1792.35"
		},
		{
			"actprice": "237.50",
			"optcode": "305W6237",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1773.68"
		},
		{
			"actprice": "235.00",
			"optcode": "305W6235",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1755.01"
		},
		{
			"actprice": "232.50",
			"optcode": "305W6232",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1736.34"
		},
		{
			"actprice": "230.00",
			"optcode": "305W6230",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1717.67"
		},
		{
			"actprice": "227.50",
			"optcode": "305W6227",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1699.00"
		},
		{
			"actprice": "225.00",
			"optcode": "305W6225",
			"price": "0.01",
			"sign": "3",
			"change": "0.00",
			"diff": "0.00",
			"volume": 0,
			"offerho1": "0.00",
			"bidho1": "0.00",
			"cvolume": 0,
			"impv": "0.00",
			"timevl": "0.01",
			"offerrem1": 0,
			"bidrem1": 0,
			"open": "0.00",
			"high": "0.00",
			"low": "0.00",
			"atmgubun": "3",
			"jisuconv": "1680.33"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
