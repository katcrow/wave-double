# [주식] 시세

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=54a99b02-dbba-4057-8756-9ac759c9a2ed)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `54a99b02-dbba-4057-8756-9ac759c9a2ed` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/market-data` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 개별종목 현재가 및 기간별 시세 등 종목별 시세를 확인할 수 있습니다. |

## TR 목록 (25건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 주식현재가호가조회 | [t1101](market-data.md#tr-t1101) | 10 | 10 | 5 |
| 주식현재가(시세)조회 | [t1102](market-data.md#tr-t1102) | 10 | 10 | 5 |
| 주식현재가시세메모 | [t1104](market-data.md#tr-t1104) | 3 | 3 | 5 |
| 주식피봇/디마크조회 | [t1105](market-data.md#tr-t1105) | 3 | 3 | 5 |
| 시간외체결량 | [t1109](market-data.md#tr-t1109) | 1 | 1 | 1 |
| 주식시간대별체결조회 | [t1301](market-data.md#tr-t1301) | 2 | 2 | 3 |
| 주식분별주가조회 | [t1302](market-data.md#tr-t1302) | 1 | 1 | 3 |
| 기간별주가 | [t1305](market-data.md#tr-t1305) | 1 | 1 | 3 |
| 주식시간대별체결조회챠트 | [t1308](market-data.md#tr-t1308) | 1 | 1 | 3 |
| 주식당일전일분틱조회 | [t1310](market-data.md#tr-t1310) | 2 | 2 | 3 |
| 관리/불성실/투자유의조회 | [t1404](market-data.md#tr-t1404) | 1 | 1 | 3 |
| 투자경고/매매정지/정리매매조회 | [t1405](market-data.md#tr-t1405) | 1 | 1 | 3 |
| 초저유동성조회 | [t1410](market-data.md#tr-t1410) | 1 | 1 | 1 |
| 상/하한 | [t1422](market-data.md#tr-t1422) | 2 | 2 | 3 |
| 상/하한가직전 | [t1427](market-data.md#tr-t1427) | 2 | 2 | 3 |
| 신고/신저가 | [t1442](market-data.md#tr-t1442) | 2 | 2 | 3 |
| 가격대별매매비중조회 | [t1449](market-data.md#tr-t1449) | 1 | 1 | 3 |
| 시간대별호가잔량추이 | [t1471](market-data.md#tr-t1471) | 1 | 1 | 3 |
| 체결강도추이 | [t1475](market-data.md#tr-t1475) | 1 | 1 | 2 |
| 시간별예상체결가 | [t1486](market-data.md#tr-t1486) | 2 | 2 | 3 |
| 예상체결가등락율상위조회 | [t1488](market-data.md#tr-t1488) | 2 | 2 | 3 |
| API용주식멀티현재가조회 | [t8407](market-data.md#tr-t8407) | 5 | 5 | 3 |
| (통합)주식현재가호가조회2 API용 | [t8450](market-data.md#tr-t8450) | 10 | 10 | 3 |
| (통합)주식시간대별체결2 API용 | [t8454](market-data.md#tr-t8454) | 1 | 1 | 1 |
| 주식마스터조회API용 | [t9945](market-data.md#tr-t9945) | 2 | 2 | 3 |

---

<a id="tr-t1101"></a>
## `t1101` 주식현재가호가조회

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
| `t1101InBlock` | t1101InBlock | Object | Y | - | - |
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
| `t1101OutBlock` | t1101OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha1` | 직전매도대비수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha1` | 직전매수대비수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha2` | 직전매도대비수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha2` | 직전매수대비수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha3` | 직전매도대비수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha3` | 직전매수대비수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha4` | 직전매도대비수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha4` | 직전매수대비수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha5` | 직전매도대비수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha5` | 직전매수대비수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho6` | 매도호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho6` | 매수호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem6` | 매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem6` | 매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha6` | 직전매도대비수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha6` | 직전매수대비수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho7` | 매도호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho7` | 매수호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem7` | 매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem7` | 매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha7` | 직전매도대비수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha7` | 직전매수대비수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho8` | 매도호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho8` | 매수호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem8` | 매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem8` | 매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha8` | 직전매도대비수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha8` | 직전매수대비수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho9` | 매도호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho9` | 매수호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem9` | 매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem9` | 매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-preoffercha9` | 직전매도대비수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha9` | 직전매수대비수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho10` | 매도호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho10` | 매수호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem10` | 매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem10` | 매수호가수량10 | Number | Y | 12 | - |
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
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-krx_midprice` | KRX중간가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-krx_offermidsumrem` | KRX매도중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-krx_bidmidsumrem` | KRX매수중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-krx_midsumrem` | KRX중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-krx_midsumremgubun` | KRX중간가잔량구분 | String | Y | 1 | - |


### 요청 Example

```json
{
  "t1101InBlock" : {
    "shcode" : "078020"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1101OutBlock": {
        "offerho4": 4570,
        "offerho3": 4565,
        "offerho6": 4580,
        "offerho5": 4575,
        "offerho8": 4590,
        "offerho7": 4585,
        "jnilclose": 4525,
        "offerho9": 4595,
        "ho_status": "1",
        "sign": "2",
        "offer": 5762,
        "preoffercha": -283,
        "high": 4600,
        "price": 4545,
        "tmoffer": 0,
        "hname": "LS증권",
        "offerho2": 4560,
        "hotime": "10061477",
        "offerho1": 4550,
        "yechange": 0,
        "yediff": "000.00",
        "diff": "000.44",
        "prebidcha10": 0,
        "volume": 4937,
        "offerho10": 4600,
        "yeprice": 0,
        "preoffercha10": 0,
        "offerrem2": 126,
        "bidho5": 4525,
        "offerrem3": 1,
        "bidho4": 4530,
        "preoffercha9": 0,
        "offerrem4": 574,
        "bidho7": 4515,
        "preoffercha8": 0,
        "offerrem5": 759,
        "bidho6": 4520,
        "preoffercha7": 0,
        "preoffercha6": 0,
        "bidho9": 4505,
        "preoffercha5": 0,
        "bidho8": 4510,
        "preoffercha4": 0,
        "offerrem1": 83,
        "preoffercha3": 0,
        "yevolume": 0,
        "offerrem6": 459,
        "offerrem7": 700,
        "offerrem8": 805,
        "offerrem9": 884,
        "dnlmtprice": 3170,
        "bidrem3": 31,
        "bidrem4": 312,
        "bidrem1": 448,
        "bidrem2": 1319,
        "low": 4540,
        "preoffercha2": 0,
        "preoffercha1": -283,
        "bidrem9": 34,
        "bidho1": 4545,
        "bidrem7": 5,
        "bidrem8": 23,
        "bidho3": 4535,
        "bidrem5": 1199,
        "bidho2": 4540,
        "bidrem6": 253,
        "prebidcha": -283,
        "prebidcha2": 0,
        "bidrem10": 126,
        "prebidcha3": 0,
        "prebidcha4": 0,
        "bidho10": 4500,
        "prebidcha5": 0,
        "prebidcha6": 0,
        "prebidcha7": 0,
        "prebidcha8": 0,
        "change": 20,
        "prebidcha9": 0,
        "shcode": "078020",
        "uplmtprice": 5880,
        "tmbid": 0,
        "yesign": "3",
        "offerrem10": 1371,
        "bid": 3750,
        "open": 4550,
        "prebidcha1": -283
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1102"></a>
## `t1102` 주식현재가(시세)조회

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
| `t1102InBlock` | t1102InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;- exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t1102OutBlock` | t1102OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-recprice` | 기준가(평가가격) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-avg` | 가중평균 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가(최고호가가격) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가(최저호가가격) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-volumediff` | 거래량차 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-opentime` | 시가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-hightime` | 고가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowtime` | 저가시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-high52w` | 52최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high52wdate` | 52최고가일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-low52w` | 52최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low52wdate` | 52최저가일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-exhratio` | 소진율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-per` | PER | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-pbrx` | PBRX | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-listing` | 상장주식수(천) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jkrate` | 증거금율 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-memedan` | 수량단위 | String | Y | 5 | - |
| `&nbsp;&nbsp;-offernocd1` | 매도증권사코드1 | String | Y | 3 | - |
| `&nbsp;&nbsp;-bidnocd1` | 매수증권사코드1 | String | Y | 3 | - |
| `&nbsp;&nbsp;-offerno1` | 매도증권사명1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno1` | 매수증권사명1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol1` | 총매도수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol1` | 총매수수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha1` | 매도증감1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha1` | 매수증감1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff1` | 매도비율1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff1` | 매수비율1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offernocd2` | 매도증권사코드2 | String | Y | 3 | - |
| `&nbsp;&nbsp;-bidnocd2` | 매수증권사코드2 | String | Y | 3 | - |
| `&nbsp;&nbsp;-offerno2` | 매도증권사명2 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno2` | 매수증권사명2 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol2` | 총매도수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol2` | 총매수수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha2` | 매도증감2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha2` | 매수증감2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff2` | 매도비율2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff2` | 매수비율2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offernocd3` | 매도증권사코드3 | String | Y | 3 | - |
| `&nbsp;&nbsp;-bidnocd3` | 매수증권사코드3 | String | Y | 3 | - |
| `&nbsp;&nbsp;-offerno3` | 매도증권사명3 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno3` | 매수증권사명3 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol3` | 총매도수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol3` | 총매수수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha3` | 매도증감3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha3` | 매수증감3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff3` | 매도비율3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff3` | 매수비율3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offernocd4` | 매도증권사코드4 | String | Y | 3 | - |
| `&nbsp;&nbsp;-bidnocd4` | 매수증권사코드4 | String | Y | 3 | - |
| `&nbsp;&nbsp;-offerno4` | 매도증권사명4 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno4` | 매수증권사명4 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol4` | 총매도수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol4` | 총매수수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha4` | 매도증감4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha4` | 매수증감4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff4` | 매도비율4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff4` | 매수비율4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offernocd5` | 매도증권사코드5 | String | Y | 3 | - |
| `&nbsp;&nbsp;-bidnocd5` | 매수증권사코드5 | String | Y | 3 | - |
| `&nbsp;&nbsp;-offerno5` | 매도증권사명5 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno5` | 매수증권사명5 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol5` | 총매도수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol5` | 총매수수량5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha5` | 매도증감5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha5` | 매수증감5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff5` | 매도비율5 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff5` | 매수비율5 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-fwdvl` | 외국계매도합계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ftradmdcha` | 외국계매도직전대비 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ftradmddiff` | 외국계매도비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-fwsvl` | 외국계매수합계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ftradmscha` | 외국계매수직전대비 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ftradmsdiff` | 외국계매수비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jvolume` | 전일동시간거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-highyear` | 연중최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highyeardate` | 연중최고일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lowyear` | 연중최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowyeardate` | 연중최저일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-target` | 목표가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-capital` | 자본금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-abscnt` | 유동주식수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-parprice` | 액면가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-gsmm` | 결산월 | String | Y | 2 | - |
| `&nbsp;&nbsp;-subprice` | 대용가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-total` | 시가총액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-listdate` | 상장일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-name` | 전분기명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-bfsales` | 전분기매출액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfoperatingincome` | 전분기영업이익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfordinaryincome` | 전분기경상이익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfnetincome` | 전분기순이익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfeps` | 전분기EPS | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-name2` | 전전분기명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-bfsales2` | 전전분기매출액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfoperatingincome2` | 전전분기영업이익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfordinaryincome2` | 전전분기경상이익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfnetincome2` | 전전분기순이익 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bfeps2` | 전전분기EPS | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-salert` | 전년대비매출액 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-opert` | 전년대비영업이익 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-ordrt` | 전년대비경상이익 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-netrt` | 전년대비순이익 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-epsrt` | 전년대비EPS | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-info1` | 락구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info2` | 관리/급등구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info3` | 정지/연장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-info4` | 투자/불성실구분 | String | Y | 12 | - |
| `&nbsp;&nbsp;-janginfo` | 장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-t_per` | T.PER | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-tonghwa` | 통화ISO코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-dval1` | 총매도대금1 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sval1` | 총매수대금1 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dval2` | 총매도대금2 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sval2` | 총매수대금2 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dval3` | 총매도대금3 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sval3` | 총매수대금3 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dval4` | 총매도대금4 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sval4` | 총매수대금4 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-dval5` | 총매도대금5 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-sval5` | 총매수대금5 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-davg1` | 총매도평단가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-savg1` | 총매수평단가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-davg2` | 총매도평단가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-savg2` | 총매수평단가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-davg3` | 총매도평단가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-savg3` | 총매수평단가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-davg4` | 총매도평단가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-savg4` | 총매수평단가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-davg5` | 총매도평단가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-savg5` | 총매수평단가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ftradmdval` | 외국계매도대금 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-ftradmsval` | 외국계매수대금 | Number | Y | 18 | - |
| `&nbsp;&nbsp;-ftradmdvag` | 외국계매도평단가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ftradmsvag` | 외국계매수평단가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-info5` | 투자주의환기 | String | Y | 8 | - |
| `&nbsp;&nbsp;-spac_gubun` | 기업인수목적회사여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-issueprice` | 발행가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-alloc_gubun` | 배분적용구분코드(1:배분발생2:배분해제그외:미발생) | String | Y | 1 | - |
| `&nbsp;&nbsp;-alloc_text` | 배분적용구분 | String | Y | 8 | - |
| `&nbsp;&nbsp;-shterm_text` | 단기과열/VI발동 | String | Y | 10 | - |
| `&nbsp;&nbsp;-svi_uplmtprice` | 정적VI상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svi_dnlmtprice` | 정적VI하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low_lqdt_gu` | 저유동성종목여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-abnormal_rise_gu` | 이상급등종목여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-lend_text` | 대차불가표시 | String | Y | 8 | - |
| `&nbsp;&nbsp;-ty_text` | ETF/ETN투자유의 | String | Y | 8 | - |
| `&nbsp;&nbsp;-nxt_janginfo` | NXT장구분 | String | Y | 10 | - |
| `&nbsp;&nbsp;-nxt_shterm_text` | NXT단기과열/VI발동 | String | Y | 10 | - |
| `&nbsp;&nbsp;-nxt_svi_uplmtprice` | NXT정적VI상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-nxt_svi_dnlmtprice` | NXT정적VI하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
  "t1102InBlock" : {
    "shcode" : "078020"
  }
}
```

### 응답 Example

```json
{
    "t1102OutBlock": {
        "high52w": 7110,
        "bfnetincome": 150,
        "shterm_text": "",
        "salert": "-27.07",
        "savg1": 4554,
        "savg2": 4551,
        "alloc_text": "",
        "savg5": 4598,
        "price": 4535,
        "savg3": 4549,
        "savg4": 4551,
        "per": "011.14",
        "hname": "LS증권",
        "dval5": 4,
        "bfordinaryincome2": 405,
        "svi_dnlmtprice": 4095,
        "diff": "000.22",
        "dval1": 9,
        "fwsvl": 109,
        "dval2": 6,
        "ftradmsvag": 4543,
        "dval3": 6,
        "dval4": 5,
        "bfnetincome2": 296,
        "ftradmsval": 0,
        "low52w": 4135,
        "svol3": 1017,
        "svol2": 1647,
        "bidnocd1": "005",
        "svol1": 1824,
        "bidnocd2": "050",
        "bidnocd3": "017",
        "name2": "2212 결산",
        "bidnocd4": "030",
        "bidnocd5": "003",
        "svol5": 529,
        "svol4": 813,
        "bidno1": "미래에",
        "highyear": 5480,
        "bidno3": "KB증권",
        "bidno2": "키움증",
        "bidno5": "한국증",
        "bidno4": "삼성증",
        "bfeps2": "406.95",
        "low": 4535,
        "ftradmsdiff": "001.57",
        "low52wdate": "20230328",
        "jkrate": 40,
        "listing": 55481,
        "t_per": "014.75",
        "bfsales2": 2116,
        "volumediff": 25407,
        "ftradmdvag": 4560,
        "change": 10,
        "uplmtprice": 5880,
        "lowtime": "100906",
        "alloc_gubun": "",
        "listdate": "20070221",
        "abnormal_rise_gu": "0",
        "fwdvl": 2,
        "open": 4550,
        "capital": 2774,
        "offerno2": "키움증",
        "high52wdate": "20220607",
        "offerno1": "유안타",
        "offerno4": "KB증권",
        "offerno3": "삼성증",
        "sign": "2",
        "scha4": 0,
        "scha3": 402,
        "offerno5": "신한투",
        "scha2": 1031,
        "spac_gubun": "N",
        "scha1": 219,
        "pbrx": "000.26",
        "bfoperatingincome": 257,
        "scha5": 1,
        "high": 4600,
        "abscnt": 15778,
        "ftradmdval": 0,
        "ty_text": "",
        "dvol1": 1886,
        "dvol2": 1273,
        "dvol3": 1261,
        "highyeardate": "20230202",
        "dvol4": 1026,
        "dvol5": 777,
        "netrt": "-32.49",
        "sval1": 8,
        "davg5": 4557,
        "epsrt": "-32.50",
        "davg4": 4580,
        "davg3": 4550,
        "davg2": 4560,
        "sval5": 2,
        "davg1": 4542,
        "ftradmscha": 0,
        "sval4": 4,
        "sval3": 5,
        "sval2": 7,
        "volume": 6929,
        "svi_uplmtprice": 5010,
        "ftradmddiff": "000.03",
        "ordrt": "-21.61",
        "jnilvolume": 32336,
        "opert": "-18.43",
        "exhratio": "0.78",
        "name": "2303 1분기",
        "info1": "",
        "bfordinaryincome": 240,
        "ddiff5": "11.21",
        "ddiff4": "14.81",
        "gsmm": "12",
        "info5": "",
        "ddiff3": "18.20",
        "info4": "",
        "ddiff2": "18.37",
        "info3": "",
        "ddiff1": "27.22",
        "info2": "",
        "offernocd2": "050",
        "offernocd3": "030",
        "lowyear": 4135,
        "offernocd4": "017",
        "offernocd5": "002",
        "tonghwa": "KRW",
        "lend_text": "",
        "offernocd1": "024",
        "dnlmtprice": 3170,
        "dcha5": 0,
        "sdiff5": "7.63",
        "vol": "000.01",
        "total": 2516,
        "recprice": 4525,
        "avg": 4555,
        "dcha4": 0,
        "sdiff4": "11.73",
        "dcha3": 0,
        "sdiff3": "14.68",
        "janginfo": "KOSDAQ",
        "dcha2": 0,
        "sdiff2": "23.77",
        "dcha1": 1866,
        "sdiff1": "26.32",
        "value": 31,
        "lowyeardate": "20230328",
        "parprice": 5000,
        "ftradmdcha": 0,
        "issueprice": 0,
        "shcode": "078020",
        "opentime": "090030",
        "target": 0,
        "bfeps": "206.51",
        "memedan": "00001",
        "subprice": 3160,
        "low_lqdt_gu": "0",
        "hightime": "092645",
        "bfoperatingincome2": 416,
        "jvolume": 6899,
        "bfsales": 605
    },
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1104"></a>
## `t1104` 주식현재가시세메모

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
| `t1104InBlock` | t1104InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-code` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-nrec` | 건수 | String | Y | 2 | t1104InBlock1 의 개수 |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/> N: NXT<br/> U:통합<br/>그외 입력값은 KRX로 처리 |
| `t1104InBlock1` | t1104InBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-indx` | 인덱스 | String | Y | 1 | t1104InBlock1 의 Occurs Index(0부터 시작) |
| `&nbsp;&nbsp;-gubn` | 조건구분 | String | Y | 1 | 1:시세<br/>2:최고저가<br/>3:Pivot<br/>4:이동평균선 |
| `&nbsp;&nbsp;-dat1` | 데이타1 | String | Y | 1 | 1:시가<br/>2:고가<br/>3:저가<br/>4:가중평균가 |
| `&nbsp;&nbsp;-dat2` | 데이타2 | String | Y | 8 | 1:당일<br/>2:전일 |


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
| `t1104OutBlock` | t1104OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-nrec` | 출력건수 | String | Y | 2 | - |
| `t1104OutBlock1` | t1104OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-indx` | 인덱스 | String | Y | 1 | - |
| `&nbsp;&nbsp;-gubn` | 조건구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-vals` | 출력값 | String | Y | 8 | - |


### 요청 Example

```json
{
   "t1104InBlock" :{
      "code" : "078020",
      "nrec" : ""
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

<a id="tr-t1105"></a>
## `t1105` 주식피봇/디마크조회

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
| `t1105InBlock` | t1105InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
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
| `t1105OutBlock` | t1105OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-pbot` | 피봇 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offer1` | 1차저항 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-supp1` | 1차지지 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offer2` | 2차저항 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-supp2` | 2차지지 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-stdprc` | 기준가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerd` | D저항 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-suppd` | D지지 | Number | Y | 8 | - |


### 요청 Example

```json
{  "t1105InBlock" : {    
"shcode" : "001200"  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1105OutBlock": {
        "offer2": 3883,
        "stdprc": 7182,
        "offer1": 3771,
        "pbot": 3563,
        "supp1": 3451,
        "shcode": "001200",
        "suppd": 3507,
        "supp2": 3243,
        "offerd": 3827
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1109"></a>
## `t1109` 시간외체결량

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
| `t1109InBlock` | t1109InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dan_chetime` | 체결cts | String | Y | 10 | 연속조회시 OutBlock의 동일필드 입력 |
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
| `t1109OutBlock` | t1109OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-ctsshcode` | 종목cts | String | Y | 6 | - |
| `&nbsp;&nbsp;-ctschetime` | 체결cts | String | Y | 10 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1109OutBlock1` | t1109OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-dan_chetime` | 시간 | String | Y | 10 | - |
| `&nbsp;&nbsp;-dan_price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dan_sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-dan_change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-dan_cvolume` | 체결량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-dan_volume` | 누적거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1109InBlock" : {
    "shcode" : "001200",
    "dan_chetime" : "",
    "idx" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1109OutBlock1": [
        {
            "chdegree": "000000.00",
            "dan_volume": 1791,
            "dan_chetime": "1800300943",
            "dan_change": 0,
            "diff": "000.00",
            "dan_cvolume": 500,
            "dan_sign": "3",
            "dan_price": 3660
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 1291,
            "dan_chetime": "1750307180",
            "dan_change": 0,
            "diff": "000.00",
            "dan_cvolume": 1002,
            "dan_sign": "3",
            "dan_price": 3660
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 289,
            "dan_chetime": "1730305708",
            "dan_change": 0,
            "diff": "000.00",
            "dan_cvolume": 1,
            "dan_sign": "3",
            "dan_price": 3660
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 288,
            "dan_chetime": "1700308255",
            "dan_change": 0,
            "diff": "000.00",
            "dan_cvolume": 147,
            "dan_sign": "3",
            "dan_price": 3660
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 141,
            "dan_chetime": "1640306509",
            "dan_change": 5,
            "diff": "000.14",
            "dan_cvolume": 27,
            "dan_sign": "2",
            "dan_price": 3665
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 114,
            "dan_chetime": "1630297536",
            "dan_change": 5,
            "diff": "000.14",
            "dan_cvolume": 12,
            "dan_sign": "2",
            "dan_price": 3665
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 102,
            "dan_chetime": "1620305084",
            "dan_change": 15,
            "diff": "000.41",
            "dan_cvolume": 100,
            "dan_sign": "2",
            "dan_price": 3675
        },
        {
            "chdegree": "000000.00",
            "dan_volume": 2,
            "dan_chetime": "1610309356",
            "dan_change": 15,
            "diff": "-00.41",
            "dan_cvolume": 2,
            "dan_sign": "5",
            "dan_price": 3645
        }
    ],
    "t1109OutBlock": {
        "ctsshcode": "",
        "idx": 0,
        "ctschetime": ""
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1301"></a>
## `t1301` 주식시간대별체결조회

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
| `t1301InBlock` | t1301InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | 거래량 > 특이거래량 |
| `&nbsp;&nbsp;-starttime` | 시작시간 | String | Y | 4 | 장시작시간 이후 |
| `&nbsp;&nbsp;-endtime` | 종료시간 | String | Y | 4 | 장종료시간 이전 |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 연속조회시 OutBlock의 동일필드 입력 |


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
| `t1301OutBlock` | t1301OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |
| `t1301OutBlock1` | t1301OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
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
  "t1301InBlock" : {
    "shcode" : "001200",
    "cvolume" : 0,
    "starttime" : "",
    "endtime" : "",
    "cts_time" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1301OutBlock1": [
        {
            "change": 25,
            "mdchecnt": 256,
            "sign": "2",
            "rechecnt": -17,
            "diff": "000.68",
            "mschecnt": 239,
            "chetime": "102626",
            "mdvolume": 119531,
            "revolume": 76077,
            "cvolume": 5,
            "volume": 321201,
            "chdegree": "00163.65",
            "price": 3685,
            "msvolume": 195608
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1301OutBlock": {
        "cts_time": "1013130002"
    }
}
```

---

<a id="tr-t1302"></a>
## `t1302` 주식분별주가조회

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
| `t1302InBlock` | t1302InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun` | 작업구분 | String | Y | 1 | 0:30초<br/>1:1분<br/>2:3분<br/>3:5분<br/>4:10분<br/>5:30분<br/>6:60분 |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |
| `&nbsp;&nbsp;-cnt` | 건수 | Number | Y | 3 | 1이상 900 이하 |
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
| `t1302OutBlock` | t1302OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 6 | - |
| `t1302OutBlock1` | t1302OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-revolume` | 순매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdchecnt` | 매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mschecnt` | 매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-rechecnt` | 순체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdchecnttm` | 매도체결건수(시간) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mschecnttm` | 매수체결건수(시간) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-totofferrem` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totbidrem` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdvolumetm` | 시간별매도체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-msvolumetm` | 시간별매수체결량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1302InBlock" : {
    "shcode" : "001200",
    "gubun" : "0",
    "time" : "",
    "cnt" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1302OutBlock": {
        "cts_time": "101700"
    },
    "t1302OutBlock1": [
        {
            "mdchecnttm": 0,
            "mdvolumetm": 0,
            "change": 25,
            "mdchecnt": 256,
            "sign": "2",
            "rechecnt": -18,
            "msvolumetm": 0,
            "diff": "000.68",
            "mschecnt": 238,
            "chetime": "102700",
            "mdvolume": 119531,
            "revolume": 76076,
            "cvolume": 0,
            "volume": 321201,
            "chdegree": "163.65",
            "high": 3685,
            "low": 3685,
            "msvolume": 195607,
            "mschecnttm": 0,
            "totofferrem": 18352,
            "close": 3685,
            "open": 3685,
            "totbidrem": 35195
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1305"></a>
## `t1305` 기간별주가

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
| `t1305InBlock` | t1305InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dwmcode` | 일주월구분 | Number | Y | 1 | 1@일, 2@주, 3@월 |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 date 값으로 설정<br/> |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 사용안함(Space) |
| `&nbsp;&nbsp;-cnt` | 건수 | Number | Y | 4 | 1 이상 |
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
| `t1305OutBlock` | t1305OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | CNT | Number | Y | 4 | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `t1305OutBlock1` | t1305OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sojinrate` | 소진율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-changerate` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-fpvolume` | 외인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-covolume` | 기관순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금(단위:백만) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ppvolume` | 개인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-o_sign` | 시가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-o_change` | 시가대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-o_diff` | 시가기준등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-h_sign` | 고가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-h_change` | 고가대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-h_diff` | 고가기준등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-l_sign` | 저가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-l_change` | 저가대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-l_diff` | 저가기준등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-marketcap` | 시가총액(단위:백만) | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1305InBlock" : {
    "shcode" : "001200",
    "dwmcode" : 1,
    "date" : "",
    "idx" : 0,
    "cnt" : 1
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1305OutBlock": {
        "date": "20230605",
        "cnt": 1,
        "idx": 0
    },
    "t1305OutBlock1": [
        {
            "date": "20230605",
            "marketcap": 356953,
            "o_diff": "0.00",
            "sign": "2",
            "l_sign": "5",
            "l_diff": "-0.41",
            "high": 3750,
            "covolume": 0,
            "low": 3645,
            "o_sign": "3",
            "h_sign": "2",
            "close": 3685,
            "value": 1188,
            "h_diff": "2.46",
            "diff_vol": "-74.79",
            "h_change": 90,
            "l_change": -15,
            "change": 25,
            "shcode": "001200",
            "o_change": 0,
            "diff": "0.68",
            "changerate": "0.33",
            "volume": 321201,
            "chdegree": "163.65",
            "ppvolume": 0,
            "sojinrate": "7.17",
            "fpvolume": 0,
            "open": 3660
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1308"></a>
## `t1308` 주식시간대별체결조회챠트

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
| `t1308InBlock` | t1308InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-starttime` | 시작시간 | String | Y | 4 | 장시작시간 이후(hhmm) |
| `&nbsp;&nbsp;-endtime` | 종료시간 | String | Y | 4 | 장종료시간 이전(hhmm) |
| `&nbsp;&nbsp;-bun_term` | 분간격 | String | Y | 2 | - |
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
| `t1308OutBlock` | t1308OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `t1308OutBlock1` | t1308OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-chdegvol` | 체결강도(거래량) | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-chdegcnt` | 체결강도(건수) | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdchecnt` | 매도체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mschecnt` | 매수체결건수 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t1308InBlock" : {
    "shcode" : "001200",
    "starttime" : "",
    "endtime" : "",
    "bun_term" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1308OutBlock1": [
        {
            "change": 25,
            "mdchecnt": 256,
            "sign": "2",
            "chdegcnt": "92.97",
            "diff": "0.69",
            "mschecnt": 238,
            "chetime": "102700",
            "mdvolume": 119531,
            "cvolume": 0,
            "volume": 321201,
            "chdegvol": "163.65",
            "high": 3685,
            "low": 3685,
            "price": 3685,
            "msvolume": 195607,
            "open": 3685
        },
        {
            "change": 0,
            "mdchecnt": 14,
            "sign": "3",
            "chdegcnt": "14.29",
            "diff": "0.01",
            "mschecnt": 2,
            "chetime": "090030",
            "mdvolume": 12895,
            "cvolume": 19856,
            "volume": 19857,
            "chdegvol": "6.97",
            "high": 3660,
            "low": 3660,
            "price": 3660,
            "msvolume": 899,
            "open": 3660
        }
    ]
}
```

---

<a id="tr-t1310"></a>
## `t1310` 주식당일전일분틱조회

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
| `t1310InBlock` | t1310InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-daygb` | 당일전일구분 | String | Y | 1 | 0:당일<br/>1:전일 |
| `&nbsp;&nbsp;-timegb` | 분틱구분 | String | Y | 1 | 0:분<br/>1:틱 |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-endtime` | 종료시간 | String | Y | 4 | 처음 조회시 시간 입력값.<br/>t1310OutBlock1.chetime <= endtime 인 데이터 조회됨. |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 처음 조회시 Space<br/>다음 조회시 t1310OutBlock.cts_time 값 입력 |
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
| `t1310OutBlock` | t1310OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |
| `t1310OutBlock1` | t1310OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
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
| `&nbsp;&nbsp;-exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
  "t1310InBlock" : {
    "daygb" : "0",
    "timegb" : "0",
    "shcode" : "001200",
    "endtime" : "",
    "cts_time" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1310OutBlock": {
        "cts_time": "100700\u0000000"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1310OutBlock1": [
        {
            "change": 25,
            "mdchecnt": 256,
            "sign": "2",
            "rechecnt": -18,
            "diff": "000.68",
            "mschecnt": 238,
            "chetime": "102700",
            "mdvolume": 119531,
            "revolume": 76076,
            "cvolume": 5,
            "volume": 321201,
            "chdegree": "00163.65",
            "price": 3685,
            "msvolume": 195607
        },
        {
            "change": 25,
            "mdchecnt": 237,
            "sign": "2",
            "rechecnt": -20,
            "diff": "000.68",
            "mschecnt": 217,
            "chetime": "100800\u0000000",
            "mdvolume": 115072,
            "revolume": 64440,
            "cvolume": 69,
            "volume": 300647,
            "chdegree": "00156.00",
            "price": 3685,
            "msvolume": 179512
        }
    ]
}
```

---

<a id="tr-t1404"></a>
## `t1404` 관리/불성실/투자유의조회

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
| `t1404InBlock` | t1404InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-jongchk` | 종목체크 | String | Y | 1 | 1:관리 2:불성실공시 3:투자유의 4.투자환기 |
| `&nbsp;&nbsp;-cts_shcode` | 종목코드_CTS | String | Y | 6 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 cts_shcode 값으로 설정 |


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
| `t1404OutBlock` | t1404OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_shcode` | 종목코드_CTS | String | Y | 6 | - |
| `t1404OutBlock1` | t1404OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-date` | 지정일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tprice` | 지정일주가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tchange` | 지정일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tdiff` | 대비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-reason` | 사유 | String | Y | 4 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-edate` | 해제일 | String | Y | 8 | - |


### 요청 Example

```json
{
  "t1404InBlock" : {
    "gubun" : "0",
    "jongchk" : "1",
    "cts_shcode" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1404OutBlock1": [
        {
            "date": "20230102",
            "reason": "5102",
            "tprice": 16200,
            "change": 260,
            "shcode": "000547",
            "sign": "5",
            "tdiff": "001.85",
            "diff": "-01.55",
            "tchange": 300,
            "edate": "",
            "volume": 216,
            "price": 16500,
            "hname": "흥국화재2우B"
        },
        {
            "date": "20220530",
            "reason": "6024",
            "tprice": 3780,
            "change": 70,
            "shcode": "950170",
            "sign": "2",
            "tdiff": "003.70",
            "diff": "001.82",
            "tchange": 140,
            "edate": "",
            "volume": 5492,
            "price": 3920,
            "hname": "JTC"
        }
    ],
    "t1404OutBlock": {
        "cts_shcode": ""
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1405"></a>
## `t1405` 투자경고/매매정지/정리매매조회

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
| `t1405InBlock` | t1405InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체<br/>1:코스피<br/>2:코스닥 |
| `&nbsp;&nbsp;-jongchk` | 종목체크 | String | Y | 1 | 1 : 투자경고<br/>2 : 매매정지<br/>3 : 정리매매<br/>4 : 투자주의<br/>5 : 투자위험<br/>6 : 위험예고<br/>7 : 단기과열지정<br/>8 : 이상급등종목<br/>9 : 상장주식수 부족 |
| `&nbsp;&nbsp;-cts_shcode` | 종목코드_CTS | String | Y | 6 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_shcode 값으로 설정 |


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
| `t1405OutBlock` | t1405OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_shcode` | 종목코드_CTS | String | Y | 6 | - |
| `t1405OutBlock1` | t1405OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-date` | 지정일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-edate` | 해제일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1405InBlock" : {
    "gubun" : "0",
    "jongchk" : "1",
    "cts_shcode" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1405OutBlock1": [
        {
            "volume": 27964262,
            "date": "20230525",
            "price": 2215,
            "change": 35,
            "shcode": "001470",
            "sign": "2",
            "diff": "001.61",
            "edate": "",
            "hname": "삼부토건"
        },
        {
            "volume": 195211,
            "date": "20230518",
            "price": 22750,
            "change": 550,
            "shcode": "290690",
            "sign": "5",
            "diff": "-02.36",
            "edate": "",
            "hname": "소룩스"
        },
        {
            "volume": 1577455,
            "date": "20230530",
            "price": 3945,
            "change": 30,
            "shcode": "388790",
            "sign": "2",
            "diff": "000.77",
            "edate": "",
            "hname": "라이콤"
        }
    ],
    "t1405OutBlock": {
        "cts_shcode": ""
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1410"></a>
## `t1410` 초저유동성조회

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
| `t1410InBlock` | t1410InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-cts_shcode` | 종목코드_CTS | String | Y | 6 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 cts_shcode 값으로 설정 |


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
| `t1410OutBlock` | t1410OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_shcode` | 종목코드_CTS | String | Y | 6 | - |
| `t1410OutBlock1` | t1410OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t1410InBlock" : {
    "gubun" : "0",
    "cts_shcode" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1410OutBlock": {
        "cts_shcode": ""
    },
    "t1410OutBlock1": [
        {
            "volume": 22,
            "price": 5620,
            "change": 50,
            "shcode": "000545",
            "sign": "5",
            "diff": "-00.88",
            "hname": "흥국화재우"
        },
        {
            "volume": 140,
            "price": 2175,
            "change": 0,
            "shcode": "168490",
            "sign": "3",
            "diff": "000.00",
            "hname": "한국패러랠"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1422"></a>
## `t1422` 상/하한

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
| `t1422InBlock` | t1422InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-qrygb` | 조회구분 | String | Y | 1 | 1:20종목씩 조회<br/>2:전체조회 |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체<br/>1:코스피<br/>2:코스닥 |
| `&nbsp;&nbsp;-jnilgubun` | 전일구분 | String | Y | 1 | 0:당일<br/>1:전일 |
| `&nbsp;&nbsp;-sign` | 상하한구분 | String | Y | 1 | 1:상한<br/>4:하한 |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값(설정시 저장됨)<br/>증거금50 : 0x00400000<br/>증거금100 : 0x00800000<br/>증거금50/100 : 0x00200000<br/>관리종목 : 0x00000080<br/>시장경보 : 0x00000100<br/>거래정지 : 0x00000200<br/>우선주 : 0x00004000<br/>투자유의 : 0x04000000<br/>정리매매 : 0x01000000<br/>불성실공시 : 0x80000000 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
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
| `t1422OutBlock` | t1422OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | CNT | Number | Y | 4 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1422OutBlock1` | t1422OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-last` | 최종진입 | String | Y | 6 | - |
| `&nbsp;&nbsp;-lmtdaycnt` | 연속 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |


### 요청 Example

```json
{
   "t1422InBlock" :{
      "qrygb" : "1",
      "gubun" : "0",
      "jnilgubun" : "0",
      "sign" : "1",
      "jc_num" : 8,
      "sprice" : 0,
      "eprice" : 0,
      "volume" : 0,
      "idx" : 0
   }
}
```

### 응답 Example

```json
{
    "t1422OutBlock": {
        "cnt": 8,
        "idx": 8
    },
    "rsp_cd": "00000",
    "t1422OutBlock1": [
        {
            "last": "160238",
            "diff_vol": "0.00",
            "lmtdaycnt": 1,
            "change": 3070,
            "offerrem1": 300,
            "shcode": "950210",
            "sign": "1",
            "diff": "29.95",
            "volume": 402800,
            "bidrem1": 100,
            "price": 13320,
            "jnilvolume": 0,
            "hname": "프레스티지바이오파마"
        },
        {
            "last": "",
            "diff_vol": "0.00",
            "lmtdaycnt": 1,
            "change": 63000,
            "offerrem1": 0,
            "shcode": "470320",
            "sign": "1",
            "diff": "300.00",
            "volume": 0,
            "bidrem1": 7,
            "price": 84000,
            "jnilvolume": 0,
            "hname": "주권5B"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1427"></a>
## `t1427` 상/하한가직전

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
| `t1427InBlock` | t1427InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-qrygb` | 조회구분 | String | Y | 1 | 1:20종목씩 조회<br/>그외:전체조회 |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체<br/>1:코스피<br/>2:코스닥 |
| `&nbsp;&nbsp;-signgubun` | 상하한가구분 | String | Y | 1 | 1:상한직전<br/>2:하한직전 |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 3 | 등락율<br/>signgubun 이 '1'(상한직전)인 경우 diff 이상<br/>signgubun 이 '1'(상한직전)인 경우 -diff 이하 |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값(설정시 저장됨)<br/>Default:000000000000<br/>000000000128(0x00000080):관리종목<br/>000000000256(0x00000100):시장경보<br/>000000000512(0x00000200):거래정지<br/>000000016384(0x00004000):우선주<br/>000002097152(0x00200000):증거금50/100<br/>000004194304(0x00400000):증거금50<br/>000008388608(0x00800000):증거금100<br/>000016777216(0x01000000):정리매매<br/>000067108864(0x04000000):투자유의<br/>002147483648(0x80000000):불성실공시<br/>ex) 관리종목, 시장경보 종목 제외시 : 000000000384( 128 + 256 ) |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
| `&nbsp;&nbsp;-jshex` | 전일상하한제외 | String | Y | 1 | c' or 'C' 입력시<br/>전일 상/하한가 제외 |


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
| `t1427OutBlock` | t1427OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | CNT | Number | Y | 4 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1427OutBlock1` | t1427OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff_vol` | 거래증가율 | Number | Y | 10.2 | - |
| `&nbsp;&nbsp;-lmtprice` | 상한가/하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-rate` | 대비율 | Number | Y | 12.2 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lmtdaycnt` | 연속 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-total` | 시가총액 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1427InBlock" : {
    "qrygb" : "1",
    "gubun" : "0",
    "signgubun" : "1",
    "diff" : 0,
    "jc_num" : 0,
    "sprice" : 0,
    "eprice" : 0,
    "volume" : 0,
    "idx" : 0,
    "jshex" : "c"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1427OutBlock": {
        "cnt": 2447,
        "idx": 20
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1427OutBlock1": [
        {
            "diff_vol": "0001456.56",
            "lmtdaycnt": 0,
            "change": 319,
            "shcode": "328380",
            "sign": "2",
            "diff": "026.34",
            "lmtprice": 1574,
            "volume": 30556301,
            "high": 1572,
            "total": 524,
            "rate": "-00000002.80",
            "low": 1251,
            "price": 1530,
            "jnilvolume": 1963072,
            "value": 44062,
            "hname": "솔트웨어",
            "open": 1251
        },
        {
            "diff_vol": "0000101.36",
            "lmtdaycnt": 0,
            "change": 295,
            "shcode": "377630",
            "sign": "2",
            "diff": "007.31",
            "lmtprice": 5240,
            "volume": 202798,
            "high": 4330,
            "total": 174,
            "rate": "-00000017.37",
            "low": 4030,
            "price": 4330,
            "jnilvolume": 100713,
            "value": 855,
            "hname": "삼성스팩4호",
            "open": 4100
        }
    ]
}
```

---

<a id="tr-t1442"></a>
## `t1442` 신고/신저가

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
| `t1442InBlock` | t1442InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 0:전체<br/>1:코스피<br/>2:코스닥 |
| `&nbsp;&nbsp;-type1` | 신고신저 | String | Y | 1 | 0:신고<br/>1:신저 |
| `&nbsp;&nbsp;-type2` | 기간 | String | Y | 1 | 0@전일<br/>1@5일<br/>2@10일<br/>3@20일<br/>4@60일<br/>5@90일<br/>6@52주<br/>7@년중 |
| `&nbsp;&nbsp;-type3` | 유지여부 | String | Y | 1 | 0:일시돌파<br/>1:돌파유지 |
| `&nbsp;&nbsp;-jc_num` | 대상제외 | Number | Y | 12 | 대상제외값(설정시 저장됨)<br/>증거금50 : 0x00400000<br/>증거금100 : 0x00800000<br/>증거금50/100 : 0x00200000<br/>관리종목 : 0x00000080<br/>시장경보 : 0x00000100<br/>거래정지 : 0x00000200<br/>우선주 : 0x00004000<br/>투자유의 : 0x04000000<br/>정리매매 : 0x01000000<br/>불성실공시 : 0x80000000 |
| `&nbsp;&nbsp;-sprice` | 시작가격 | Number | Y | 8 | 현재가 >= sprice |
| `&nbsp;&nbsp;-eprice` | 종료가격 | Number | Y | 8 | 현재가 <= eprice |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | 거래량 >= volume |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
| `&nbsp;&nbsp;-jc_num2` | 대상제외2 | Number | Y | 12 | 기본 => 000000000000<br/>상장지수펀드 => 000000000001<br/>선박투자회사 => 000000000002<br/>스펙 => 000000000004<br/>ETN => 000000000008(0x00000008)<br/>투자주의 => 000000000016(0x00000010)<br/>투자위험 => 000000000032(0x00000020)<br/>위험예고 => 000000000064(0x00000040)<br/>담보불가 => 000000000128(0x00000080)<br/>두개 이상 제외시 해당 값을 합산한다. |


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
| `t1442OutBlock` | t1442OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1442OutBlock1` | t1442OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-pastprice` | 이전가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-pastsign` | 이전가대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-pastchange` | 이전가대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-pastdiff` | 이전가대비율 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1442InBlock" : {
    "gubun" : "0",
    "type1" : "0",
    "type2" : "0",
    "type3" : "0",
    "jc_num" : 8,
    "sprice" : 0,
    "eprice" : 0,
    "volume" : 0,
    "idx" : 0,
    "jc_num2" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1442OutBlock1": [
        {
            "volume": 3117636,
            "pastchange": 2560,
            "price": 10580,
            "pastprice": 8600,
            "shcode": "171120",
            "change": 1990,
            "sign": "2",
            "pastdiff": "29.77",
            "diff": "23.17",
            "pastsign": "2",
            "hname": "라이온켐텍"
        },
        {
            "volume": 1248,
            "pastchange": 825,
            "price": 8585,
            "pastprice": 8315,
            "shcode": "530098",
            "change": 270,
            "sign": "2",
            "pastdiff": "9.92",
            "diff": "3.25",
            "pastsign": "2",
            "hname": "삼성 블룸버그 WTI원"
        }
    ],
    "rsp_msg": "조회완료",
    "t1442OutBlock": {
        "idx": 20
    }
}
```

---

<a id="tr-t1449"></a>
## `t1449` 가격대별매매비중조회

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
| `t1449InBlock` | t1449InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dategb` | 일자구분 | String | Y | 1 | 1@당일 2@전일 3@당일+전일 |


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
| `t1449OutBlock` | t1449OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결량 | Number | Y | 12 | - |
| `t1449OutBlock1` | t1449OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-price` | 체결가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-tickdiff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-diff` | 비중 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-mdvolume` | 매도체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-msvolume` | 매수체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-msdiff` | 매수비율 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1449InBlock" : {
    "shcode" : "001200",
    "dategb" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1449OutBlock": {
        "volume": 322192,
        "price": 3685,
        "change": 25,
        "msvolume": 195607,
        "sign": "2",
        "diff": "0.68",
        "mdvolume": 120522
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1449OutBlock1": [
        {
            "price": 3750,
            "change": 90,
            "msvolume": 22107,
            "sign": "2",
            "msdiff": "100.00",
            "diff": "6.86",
            "tickdiff": "2.46",
            "mdvolume": 0,
            "cvolume": 22107
        },
        {
            "price": 3645,
            "change": -15,
            "msvolume": 0,
            "sign": "5",
            "msdiff": "0.00",
            "diff": "0.05",
            "tickdiff": "-0.41",
            "mdvolume": 147,
            "cvolume": 147
        }
    ]
}
```

---

<a id="tr-t1471"></a>
## `t1471` 시간대별호가잔량추이

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
| `t1471InBlock` | t1471InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gubun` | 분구분 | String | Y | 2 | 00:30초<br/>01:1분<br/>02:2분<br/>03:3분<br/>..... |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | 기본값 : Space, 현재시간을 기준으로 함<br/>연속조회시에 직전 조회결과인<br/>OutBlock의 time 값으로 설정 |
| `&nbsp;&nbsp;-cnt` | 자료개수 | String | Y | 3 | 요청건수( 1 이상 500 이하값만 유효)<br/>ex) 10건 요청시 "010" |
| `exchgubun` | 거래소구분코드 | String | Y | 1 | K: KRX<br/>N: NXT<br/>U:통합<br/>그외 입력값은 KRX로 처리<br/> |


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
| `t1471OutBlock1` | t1471OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간CTS | String | Y | 6 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `t1471OutBlock1` | t1471OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-time` | 체결시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-preoffercha1` | 메도증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도우선잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도우선호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho1` | 매수우선호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수우선잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-prebidcha1` | 매수증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totofferrem` | 총매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totbidrem` | 총매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totsun` | 순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-msrate` | 매수비율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-close` | 종가 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t1471InBlock" : {
    "shcode" : "001200",
    "gubun" : "00",
    "time" : " ",
    "cnt" : "010"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1471OutBlock": {
        "volume": 0,
        "price": 3550,
        "change": 0,
        "sign": "3",
        "diff": "0.00",
        "time": "154530"
    },
    "t1471OutBlock1": [
        {
            "bidrem1": 0,
            "offerrem1": 0,
            "totsun": 0,
            "preoffercha1": 0,
            "time": "160000",
            "totofferrem": 0,
            "bidho1": 0,
            "msrate": "9999.9",
            "close": 3550,
            "offerho1": 0,
            "prebidcha1": 0,
            "totbidrem": 0
        },
        {
            "bidrem1": 0,
            "offerrem1": 0,
            "totsun": 0,
            "preoffercha1": 0,
            "time": "154600",
            "totofferrem": 0,
            "bidho1": 0,
            "msrate": "9999.9",
            "close": 3550,
            "offerho1": 0,
            "prebidcha1": 0,
            "totbidrem": 0
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1475"></a>
## `t1475` 체결강도추이

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
| `t1475InBlock` | t1475InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-vptype` | 상승하락 | String | Y | 1 | 시간별/일별 구분 0 : 시간별 1 : 일별 |
| `&nbsp;&nbsp;-datacnt` | 데이터개수 | Number | Y | 4 | 스페이스 입력시 최대 20개 데이터 조회됨. |
| `&nbsp;&nbsp;-date` | 기준일자 | Number | Y | 8 | 다음 조회시 입력. 이전 조회시 OutBlock.date값 입력 |
| `&nbsp;&nbsp;-time` | 기준시간 | Number | Y | 6 | 다음 조회시 입력. 이전 조회시 OutBlock.time값 입력 |
| `&nbsp;&nbsp;-rankcnt` | 랭크카운터 | Number | Y | 3 | 미사용 필드. |
| `&nbsp;&nbsp;-gubun` | 조회구분 | String | Y | 1 | 일반 조회 : 0 차트 조회 : 1 OutBlock1의 volume 필드 값 구분함. 일반 : 누적거래량, 차트 : 체결량 |


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
| `t1475OutBlock` | t1475OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 기준일자 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 기준시간 | Number | Y | 6 | - |
| `&nbsp;&nbsp;-rankcnt` | 랭크카운터 | Number | Y | 3 | - |
| `t1475OutBlock1` | t1475OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-datetime` | 일자 | String | Y | 10 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-todayvp` | 당일VP | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-ma5vp` | 5일MAVP | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-ma20vp` | 20일MAVP | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-ma60vp` | 60일MAVP | Number | Y | 8.2 | - |


### 요청 Example

```json
{
  "t1475InBlock" : {
    "shcode" : "001200",
    "vptype" : "0",
    "datacnt" : 0,
    "date" : 0,
    "time" : 0,
    "rankcnt" : 0,
    "gubun" : "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1475OutBlock": {
        "date": 20230605,
        "rankcnt": 0,
        "time": 100700
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1475OutBlock1": [
        {
            "volume": 322192,
            "todayvp": "162.30",
            "datetime": "102700",
            "ma20vp": "164.67",
            "price": 3685,
            "change": 25,
            "ma5vp": "165.09",
            "sign": "2",
            "ma60vp": "174.61",
            "diff": "0.68"
        },
        {
            "volume": 300647,
            "todayvp": "156.00",
            "datetime": "100800",
            "ma20vp": "164.01",
            "price": 3685,
            "change": 25,
            "ma5vp": "156.03",
            "sign": "2",
            "ma60vp": "179.55",
            "diff": "0.68"
        }
    ]
}
```

---

<a id="tr-t1486"></a>
## `t1486` 시간별예상체결가

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
| `t1486InBlock` | t1486InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 4 | 0020 |
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
| `t1486OutBlock` | t1486OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `t1486OutBlock1` | t1486OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 예상체결가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cvolume` | 예상체결량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
  "t1486InBlock"  :{
    "shcode" : "001200",
    "cts_time" : " ",
    "cnt" : 20
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1486OutBlock1": [
        {
            "bidrem1": 8713,
            "price": 3660,
            "change": 0,
            "offerrem1": 956,
            "sign": "3",
            "diff": "0.00",
            "chetime": "09000854",
            "bidho1": 3660,
            "cvolume": 6062,
            "offerho1": 3665
        },
        {
            "bidrem1": 1270,
            "price": 3680,
            "change": 20,
            "offerrem1": 191,
            "sign": "2",
            "diff": "0.55",
            "chetime": "08594423",
            "bidho1": 3665,
            "cvolume": 1552,
            "offerho1": 3680
        }
    ],
    "t1486OutBlock": {
        "cts_time": "08594423 0"
    },
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t1488"></a>
## `t1488` 예상체결가등락율상위조회

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
| `t1488InBlock` | t1488InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 거래소구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-sign` | 상하락구분 | String | Y | 1 | 1:상승 2:하락 |
| `&nbsp;&nbsp;-jgubun` | 장구분 | String | Y | 1 | 1:장전 2:장후 3:직전대비 |
| `&nbsp;&nbsp;-jongchk` | 종목체크 | String | Y | 12 | 대상제외값 0x00000080:관리종목 0x00000100:시장경보 0x00000200:거래정지 0x00004000:우선주 0x00200000:증거금50/100 0x00400000:증거금50 0x00800000:증거금100 0x01000000:정리매매 0x04000000:투자유의 0x80000000:불성실공시 |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | 처음 조회시는 Space 연속 조회시에 이전 조회한 OutBlock의 idx 값으로 설정 |
| `&nbsp;&nbsp;-volume` | 거래량 | String | Y | 1 | 전체@0 1만주이상@1 5만주이상@2 10만주이상@3 50만주이상@4 백만주이상@5 |
| `&nbsp;&nbsp;-yesprice` | 예상체결시작가격 | Number | Y | 8 | yesprice <= 예상체결가 인 종목 |
| `&nbsp;&nbsp;-yeeprice` | 예상체결종료가격 | Number | Y | 8 | 예상체결가 <= yeeprice 인 종목 |
| `&nbsp;&nbsp;-yevolume` | 예상체결량 | Number | Y | 12 | 예상체결량 >= yevolume 인 종목 |


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
| `t1488OutBlock` | t1488OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t1488OutBlock1` | t1488OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidrem` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cnt` | 연속일수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-jkrate` | 증거금율 | String | Y | 3 | - |
| `&nbsp;&nbsp;-jnilvolume` | 전일거래량 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1488InBlock" : {
    "gubun" : "0",
    "sign" : "1",
    "jgubun" : "1",
    "jongchk" : "0x00000080",
    "idx" : 0,
    "volume" : "0",
    "yesprice" : 0, 
    "yeeprice" : 0,
    "yevolume" : 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1488OutBlock1": [
        {
            "change": 1320,
            "shcode": "203690",
            "sign": "2",
            "cnt": 1,
            "diff": "029.01",
            "offerho": 5870,
            "bidrem": 19,
            "offerrem": 504,
            "volume": 48087,
            "bidho": 5860,
            "price": 5870,
            "jnilvolume": 390674,
            "jkrate": "100",
            "hname": "프로스테믹스"
        },
        {
            "change": 144,
            "shcode": "007460",
            "sign": "2",
            "cnt": 1,
            "diff": "009.66",
            "offerho": 1636,
            "bidrem": 2924,
            "offerrem": 3009,
            "volume": 142226,
            "bidho": 1635,
            "price": 1635,
            "jnilvolume": 6923364,
            "jkrate": "100",
            "hname": "에이프로젠"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1488OutBlock": {
        "idx": 20
    }
}
```

---

<a id="tr-t8407"></a>
## `t8407` API용주식멀티현재가조회

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
| `t8407InBlock` | t8407InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-nrec` | 건수 | Number | Y | 3 | 최대 50개까지 |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 300 | 구분자 없이 종목코드를 붙여서 입력<br/>078020, 000660, 005930 을 전송시 '078020000660005930' 을 입력 |


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
| `t8407OutBlock1` | t8407OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-cvolume` | 체결수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-chdegree` | 체결강도 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-value` | 거래대금(백만) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem` | 우선매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem` | 우선매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totofferrem` | 총매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totbidrem` | 총매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t8407InBlock" : {
    "nrec" : 3,
    "shcode" : "078020000660005930"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t8407OutBlock1": [
        {
            "shcode": "078020",
            "change": 5,
            "jnilclose": 4525,
            "sign": "2",
            "uplmtprice": 5880,
            "diff": "000.11",
            "offerho": 4540,
            "bidrem": 143,
            "cvolume": 202,
            "offerrem": 57,
            "dnlmtprice": 3170,
            "volume": 33764,
            "chdegree": "000020.91",
            "bidho": 4530,
            "high": 4600,
            "low": 4520,
            "price": 4530,
            "totofferrem": 3928,
            "value": 153,
            "hname": "이베스트투자증권",
            "open": 4550,
            "totbidrem": 5901
        },
        {
            "shcode": "000660",
            "change": 1600,
            "jnilclose": 110300,
            "sign": "5",
            "uplmtprice": 143300,
            "diff": "-01.45",
            "offerho": 108800,
            "bidrem": 25011,
            "cvolume": 459,
            "offerrem": 248,
            "dnlmtprice": 77300,
            "volume": 3086217,
            "chdegree": "000072.05",
            "bidho": 108700,
            "high": 110500,
            "low": 108500,
            "price": 108700,
            "totofferrem": 126172,
            "value": 337018,
            "hname": "SK하이닉스",
            "open": 110100,
            "totbidrem": 172000
        },
        {
            "shcode": "005930",
            "change": 500,
            "jnilclose": 72200,
            "sign": "5",
            "uplmtprice": 93800,
            "diff": "-00.69",
            "offerho": 71700,
            "bidrem": 31934,
            "cvolume": 25,
            "offerrem": 58968,
            "dnlmtprice": 50600,
            "volume": 12640775,
            "chdegree": "000056.80",
            "bidho": 71600,
            "high": 72700,
            "low": 71400,
            "price": 71700,
            "totofferrem": 1498765,
            "value": 908016,
            "hname": "삼성전자",
            "open": 72700,
            "totbidrem": 880412
        }
    ]
}
```

---

<a id="tr-t8450"></a>
## `t8450` (통합)주식현재가호가조회2 API용

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
| `t8450InBlock` | t8450InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
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
| `t8450OutBlock` | t8450OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가(기준가) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerho1` | 매도호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho1` | 매수호가1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem1` | 매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem1` | 매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho2` | 매도호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho2` | 매수호가2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem2` | 매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem2` | 매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho3` | 매도호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho3` | 매수호가3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem3` | 매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem3` | 매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho4` | 매도호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho4` | 매수호가4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem4` | 매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem4` | 매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho5` | 매도호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho5` | 매수호가5 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem5` | 매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem5` | 매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho6` | 매도호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho6` | 매수호가6 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem6` | 매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem6` | 매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho7` | 매도호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho7` | 매수호가7 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem7` | 매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem7` | 매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho8` | 매도호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho8` | 매수호가8 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem8` | 매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem8` | 매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho9` | 매도호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho9` | 매수호가9 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem9` | 매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem9` | 매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerho10` | 매도호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bidho10` | 매수호가10 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-offerrem10` | 매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidrem10` | 매수호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offer` | 매도호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bid` | 매수호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-hotime` | 수신시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-yeprice` | 예상체결가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yevolume` | 예상체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-yesign` | 예상체결전일구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-yechange` | 예상체결전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-yediff` | 예상체결등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-tmoffer` | 시간외매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tmbid` | 시간외매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ho_status` | 동시구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-nxt_offerrem1` | NXT매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem1` | NXT매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem2` | NXT매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem2` | NXT매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem3` | NXT매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem3` | NXT매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem4` | NXT매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem4` | NXT매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem5` | NXT매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem5` | NXT매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem6` | NXT매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem6` | NXT매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem7` | NXT매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem7` | NXT매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem8` | NXT매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem8` | NXT매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem9` | NXT매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem9` | NXT매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offerrem10` | NXT매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bidrem10` | NXT매수호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_offer` | NXT매도호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_bid` | NXT매수호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_yeprice` | NXT예상체결가격 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_yevolume` | NXT예상체결수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nxt_yesign` | NXT예상체결전일구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-nxt_yechange` | NXT예상체결전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-nxt_yediff` | NXT예상체결등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-nxt_ho_status` | NXT동시구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-unx_offerrem1` | 통합매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem1` | 통합매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem2` | 통합매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem2` | 통합매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem3` | 통합매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem3` | 통합매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem4` | 통합매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem4` | 통합매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem5` | 통합매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem5` | 통합매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem6` | 통합매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem6` | 통합매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem7` | 통합매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem7` | 통합매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem8` | 통합매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem8` | 통합매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem9` | 통합매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem9` | 통합매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offerrem10` | 통합매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bidrem10` | 통합매수호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_offer` | 통합매도호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-unx_bid` | 통합매수호가수량합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-krx_midprice` | KRX중간가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-krx_offermidsumrem` | KRX매도중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-krx_bidmidsumrem` | KRX매수중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-nxt_midprice` | NXT중간가격 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-nxt_offermidsumrem` | NXT매도중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-nxt_bidmidsumrem` | NXT매수중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `&nbsp;&nbsp;-krx_midsumrem` | KRX중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-krx_midsumremgubun` | KRX중간가잔량구분(''없음'1'매도'2'매수) | String | Y | 1 | - |
| `&nbsp;&nbsp;-nxt_midsumrem` | NXT중간가잔량합계수량 | Number | Y | 9 | - |
| `&nbsp;&nbsp;-nxt_midsumremgubun` | NXT중간가잔량구분(''없음'1'매도'2'매수) | String | Y | 1 | - |


### 요청 Example

```json
{
  "t8450InBlock" : {
    "shcode" : "010950",
    "exchgubun" : "N"
  }
}
```

### 응답 Example

```json
{
	"t8450OutBlock": {
		"hname": "S-Oil",
		"price": 60600,
		"sign": "2",
		"change": 400,
		"diff": "0.66",
		"volume": 26815,
		"jnilclose": 60200,
		"offerho1": 60700,
		"bidho1": 60600,
		"offerrem1": 0,
		"bidrem1": 0,
		"offerho2": 60800,
		"bidho2": 60500,
		"offerrem2": 0,
		"bidrem2": 0,
		"offerho3": 60900,
		"bidho3": 60400,
		"offerrem3": 0,
		"bidrem3": 0,
		"offerho4": 61000,
		"bidho4": 60300,
		"offerrem4": 0,
		"bidrem4": 0,
		"offerho5": 61100,
		"bidho5": 60200,
		"offerrem5": 0,
		"bidrem5": 0,
		"offerho6": 61200,
		"bidho6": 60100,
		"offerrem6": 0,
		"bidrem6": 0,
		"offerho7": 61300,
		"bidho7": 60000,
		"offerrem7": 0,
		"bidrem7": 0,
		"offerho8": 61400,
		"bidho8": 59900,
		"offerrem8": 0,
		"bidrem8": 0,
		"offerho9": 61500,
		"bidho9": 59800,
		"offerrem9": 0,
		"bidrem9": 0,
		"offerho10": 61600,
		"bidho10": 59700,
		"offerrem10": 0,
		"bidrem10": 0,
		"offer": 0,
		"bid": 0,
		"hotime": "14162900",
		"yeprice": 0,
		"yevolume": 0,
		"yesign": "3",
		"yechange": 0,
		"yediff": "-100.0",
		"tmoffer": 0,
		"tmbid": 0,
		"ho_status": "",
		"shcode": "010950",
		"uplmtprice": 78200,
		"dnlmtprice": 42200,
		"open": 60400,
		"high": 62700,
		"low": 60300,
		"nxt_offerrem1": 39,
		"nxt_bidrem1": 105,
		"nxt_offerrem2": 419,
		"nxt_bidrem2": 815,
		"nxt_offerrem3": 22,
		"nxt_bidrem3": 343,
		"nxt_offerrem4": 402,
		"nxt_bidrem4": 461,
		"nxt_offerrem5": 1053,
		"nxt_bidrem5": 609,
		"nxt_offerrem6": 822,
		"nxt_bidrem6": 122,
		"nxt_offerrem7": 574,
		"nxt_bidrem7": 525,
		"nxt_offerrem8": 423,
		"nxt_bidrem8": 282,
		"nxt_offerrem9": 870,
		"nxt_bidrem9": 199,
		"nxt_offerrem10": 379,
		"nxt_bidrem10": 45,
		"nxt_offer": 5003,
		"nxt_bid": 3506,
		"nxt_yeprice": 0,
		"nxt_yevolume": 0,
		"nxt_yesign": "0",
		"nxt_yechange": 0,
		"nxt_yediff": "0.00",
		"nxt_ho_status": "1",
		"unx_offerrem1": 39,
		"unx_bidrem1": 105,
		"unx_offerrem2": 419,
		"unx_bidrem2": 815,
		"unx_offerrem3": 22,
		"unx_bidrem3": 343,
		"unx_offerrem4": 402,
		"unx_bidrem4": 461,
		"unx_offerrem5": 1053,
		"unx_bidrem5": 609,
		"unx_offerrem6": 822,
		"unx_bidrem6": 122,
		"unx_offerrem7": 574,
		"unx_bidrem7": 525,
		"unx_offerrem8": 423,
		"unx_bidrem8": 282,
		"unx_offerrem9": 870,
		"unx_bidrem9": 199,
		"unx_offerrem10": 379,
		"unx_bidrem10": 45,
		"unx_offer": 5003,
		"unx_bid": 3506,
		"krx_midprice": 0,
		"krx_offermidsumrem": 0,
		"krx_bidmidsumrem": 0,
		"nxt_midprice": 60650,
		"nxt_offermidsumrem": 0,
		"nxt_bidmidsumrem": 0,
		"ex_shcode": "N010950",
		"krx_midsumrem": 0,
		"krx_midsumremgubun": "",
		"nxt_midsumrem": 0,
		"nxt_midsumremgubun": ""
	},
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8454"></a>
## `t8454` (통합)주식시간대별체결2 API용

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
| `t8454InBlock` | t8454InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-cvolume` | 특이거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-starttime` | 시작시간 | String | Y | 4 | - |
| `&nbsp;&nbsp;-endtime` | 종료시간 | String | Y | 4 | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |
| `&nbsp;&nbsp;-exchgubun` | 거래소구분코드 | String | Y | 1 | - |


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
| `t8454OutBlock` | t8454OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_time` | 시간CTS | String | Y | 10 | - |
| `&nbsp;&nbsp;-ex_shcode` | 거래소별단축코드 | String | Y | 10 | - |
| `t8454OutBlock1` | t8454OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-chetime` | 시간 | String | Y | 10 | - |
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
| `&nbsp;&nbsp;-exchname` | 거래소명 | String | Y | 3 | - |


### 요청 Example

```json
{
  "t8454InBlock" : {
    "shcode" : "010950",
    "starttime" : "",
    "endtime" : "",
    "bun_term" : "",
    "exchgubun" : "N"
  }
}
```

### 응답 Example

```json
{
	"t8454OutBlock": {
		"cts_time": "1358200001",
		"ex_shcode": "N010950"
	},
	"t8454OutBlock1": [
		{
			"chetime": "141715",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 1,
			"chdegree": "62.76",
			"volume": 26816,
			"mdvolume": 16476,
			"mdchecnt": 651,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -6136,
			"rechecnt": -46,
			"exchname": "NXT"
		},
		{
			"chetime": "141309",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 3,
			"chdegree": "62.76",
			"volume": 26815,
			"mdvolume": 16475,
			"mdchecnt": 650,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -6135,
			"rechecnt": -45,
			"exchname": "NXT"
		},
		{
			"chetime": "141307",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 50,
			"chdegree": "62.77",
			"volume": 26812,
			"mdvolume": 16472,
			"mdchecnt": 649,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -6132,
			"rechecnt": -44,
			"exchname": "NXT"
		},
		{
			"chetime": "141105",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 80,
			"chdegree": "62.96",
			"volume": 26762,
			"mdvolume": 16422,
			"mdchecnt": 648,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -6082,
			"rechecnt": -43,
			"exchname": "NXT"
		},
		{
			"chetime": "141010",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 12,
			"chdegree": "63.27",
			"volume": 26682,
			"mdvolume": 16342,
			"mdchecnt": 647,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -6002,
			"rechecnt": -42,
			"exchname": "NXT"
		},
		{
			"chetime": "140902",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 1,
			"chdegree": "63.32",
			"volume": 26670,
			"mdvolume": 16330,
			"mdchecnt": 646,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -5990,
			"rechecnt": -41,
			"exchname": "NXT"
		},
		{
			"chetime": "140900",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 1,
			"chdegree": "63.32",
			"volume": 26669,
			"mdvolume": 16329,
			"mdchecnt": 645,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -5989,
			"rechecnt": -40,
			"exchname": "NXT"
		},
		{
			"chetime": "140808",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 16,
			"chdegree": "63.33",
			"volume": 26668,
			"mdvolume": 16328,
			"mdchecnt": 644,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -5988,
			"rechecnt": -39,
			"exchname": "NXT"
		},
		{
			"chetime": "140800",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 2,
			"chdegree": "63.39",
			"volume": 26652,
			"mdvolume": 16312,
			"mdchecnt": 643,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -5972,
			"rechecnt": -38,
			"exchname": "NXT"
		},
		{
			"chetime": "140756",
			"price": 60700,
			"sign": "2",
			"change": 500,
			"diff": "0.83",
			"cvolume": 1,
			"chdegree": "63.40",
			"volume": 26650,
			"mdvolume": 16310,
			"mdchecnt": 642,
			"msvolume": 10340,
			"mschecnt": 605,
			"revolume": -5970,
			"rechecnt": -37,
			"exchname": "NXT"
		},
		{
			"chetime": "140703",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 10,
			"chdegree": "63.39",
			"volume": 26649,
			"mdvolume": 16310,
			"mdchecnt": 642,
			"msvolume": 10339,
			"mschecnt": 604,
			"revolume": -5971,
			"rechecnt": -38,
			"exchname": "NXT"
		},
		{
			"chetime": "140611",
			"price": 60700,
			"sign": "2",
			"change": 500,
			"diff": "0.83",
			"cvolume": 1,
			"chdegree": "63.43",
			"volume": 26639,
			"mdvolume": 16300,
			"mdchecnt": 641,
			"msvolume": 10339,
			"mschecnt": 604,
			"revolume": -5961,
			"rechecnt": -37,
			"exchname": "NXT"
		},
		{
			"chetime": "140413",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 25,
			"chdegree": "63.42",
			"volume": 26638,
			"mdvolume": 16300,
			"mdchecnt": 641,
			"msvolume": 10338,
			"mschecnt": 603,
			"revolume": -5962,
			"rechecnt": -38,
			"exchname": "NXT"
		},
		{
			"chetime": "140346",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 1,
			"chdegree": "63.52",
			"volume": 26613,
			"mdvolume": 16275,
			"mdchecnt": 640,
			"msvolume": 10338,
			"mschecnt": 603,
			"revolume": -5937,
			"rechecnt": -37,
			"exchname": "NXT"
		},
		{
			"chetime": "140245",
			"price": 60700,
			"sign": "2",
			"change": 500,
			"diff": "0.83",
			"cvolume": 1,
			"chdegree": "63.52",
			"volume": 26612,
			"mdvolume": 16274,
			"mdchecnt": 639,
			"msvolume": 10338,
			"mschecnt": 603,
			"revolume": -5936,
			"rechecnt": -36,
			"exchname": "NXT"
		},
		{
			"chetime": "140219",
			"price": 60700,
			"sign": "2",
			"change": 500,
			"diff": "0.83",
			"cvolume": 1,
			"chdegree": "63.52",
			"volume": 26611,
			"mdvolume": 16274,
			"mdchecnt": 639,
			"msvolume": 10337,
			"mschecnt": 602,
			"revolume": -5937,
			"rechecnt": -37,
			"exchname": "NXT"
		},
		{
			"chetime": "140150",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 1,
			"chdegree": "63.51",
			"volume": 26610,
			"mdvolume": 16274,
			"mdchecnt": 639,
			"msvolume": 10336,
			"mschecnt": 601,
			"revolume": -5938,
			"rechecnt": -38,
			"exchname": "NXT"
		},
		{
			"chetime": "140026",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 33,
			"chdegree": "63.52",
			"volume": 26609,
			"mdvolume": 16273,
			"mdchecnt": 638,
			"msvolume": 10336,
			"mschecnt": 601,
			"revolume": -5937,
			"rechecnt": -37,
			"exchname": "NXT"
		},
		{
			"chetime": "140007",
			"price": 60600,
			"sign": "2",
			"change": 400,
			"diff": "0.66",
			"cvolume": 50,
			"chdegree": "63.65",
			"volume": 26576,
			"mdvolume": 16240,
			"mdchecnt": 637,
			"msvolume": 10336,
			"mschecnt": 601,
			"revolume": -5904,
			"rechecnt": -36,
			"exchname": "NXT"
		},
		{
			"chetime": "135820",
			"price": 60700,
			"sign": "2",
			"change": 500,
			"diff": "0.83",
			"cvolume": 1,
			"chdegree": "63.84",
			"volume": 26526,
			"mdvolume": 16190,
			"mdchecnt": 636,
			"msvolume": 10336,
			"mschecnt": 601,
			"revolume": -5854,
			"rechecnt": -35,
			"exchname": "NXT"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t9945"></a>
## `t9945` 주식마스터조회API용

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
| `t9945InBlock` | t9945InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 구분(KSP:1KSD:2) | String | Y | 1 | - |


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
| `t9945OutBlock` | t9945OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-expcode` | 확장코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-etfchk` | ETF구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-nxt_chk` | NXT상장구분 | String | Y | 1 | 1:NXT 거래소 제공<br/>0:NXT 거래소 미제공 |
| `&nbsp;&nbsp;-filler` | filler | String | Y | 4 | - |


### 요청 Example

```json
{
  "t9945InBlock" : {
    "gubun" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t9945OutBlock": [
        {
            "etfchk": "0",
            "shcode": "000020",
            "filler": "",
            "expcode": "KR7000020008",
            "hname": "동화약품"
        },
        {
            "etfchk": "0",
            "shcode": "000040",
            "filler": "",
            "expcode": "KR7000040006",
            "hname": "KR모터스"
        },
        {
            "etfchk": "1",
            "shcode": "238720",
            "filler": "",
            "expcode": "KR7238720007",
            "hname": "ACE 일본Nikkei225(H)"
        }
    ]
}
```
