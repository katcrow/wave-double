# [주식] ETF

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=30b6dfd6-b0bd-4e63-a510-7d5d94edc740)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `30b6dfd6-b0bd-4e63-a510-7d5d94edc740` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/etf` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | ETF 시세 및 종목별정보를 확인할 수 있습니다. |

## TR 목록 (5건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| ETF현재가(시세)조회 | [t1901](etf.md#tr-t1901) | 1 | 1 | 3 |
| ETF시간별추이 | [t1902](etf.md#tr-t1902) | 1 | 1 | 3 |
| ETF일별추이 | [t1903](etf.md#tr-t1903) | 1 | 1 | 3 |
| ETF구성종목조회 | [t1904](etf.md#tr-t1904) | 1 | 1 | 3 |
| ETFLP호가 | [t1906](etf.md#tr-t1906) | 10 | 10 | 5 |

---

<a id="tr-t1901"></a>
## `t1901` ETF현재가(시세)조회

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
| `t1901InBlock` | t1901InBlock | Object | Y | - | - |
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
| `t1901OutBlock` | t1901OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-recprice` | 기준가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-avg` | 가중평균 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-uplmtprice` | 상한가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dnlmtprice` | 하한가 | Number | Y | 8 | - |
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
| `&nbsp;&nbsp;-flmtvol` | 외국인보유수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-per` | PER | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-listing` | 상장주식수(천) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jkrate` | 증거금율 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-value` | 누적거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-highyear` | 연중최고가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-highyeardate` | 연중최고일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lowyear` | 연중최저가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-lowyeardate` | 연중최저일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-upname` | 업종명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-upprice` | 업종현재가 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-upsign` | 업종전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-upchange` | 업종전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-updiff` | 업종등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-futname` | 선물최근월물명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-futcode` | 선물최근월물코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-futprice` | 선물현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-futsign` | 선물전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-futchange` | 선물전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-futdiff` | 선물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-nav` | NAV | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-navsign` | NAV전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-navchange` | NAV전일대비 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-navdiff` | NAV등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-cocrate` | 추적오차율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-kasis` | 괴리율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-subprice` | 대용가 | Number | Y | 10 | - |
| `&nbsp;&nbsp;-offerno1` | 매도증권사코드1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno1` | 매수증권사코드1 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol1` | 총매도수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol1` | 총매수수량1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha1` | 매도증감1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha1` | 매수증감1 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff1` | 매도비율1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff1` | 매수비율1 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno2` | 매도증권사코드2 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno2` | 매수증권사코드2 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol2` | 총매도수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol2` | 총매수수량2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha2` | 매도증감2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha2` | 매수증감2 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff2` | 매도비율2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff2` | 매수비율2 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno3` | 매도증권사코드3 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno3` | 매수증권사코드3 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol3` | 총매도수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol3` | 총매수수량3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha3` | 매도증감3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha3` | 매수증감3 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff3` | 매도비율3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff3` | 매수비율3 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno4` | 매도증권사코드4 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno4` | 매수증권사코드4 | String | Y | 6 | - |
| `&nbsp;&nbsp;-dvol4` | 총매도수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svol4` | 총매수수량4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-dcha4` | 매도증감4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-scha4` | 매수증감4 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-ddiff4` | 매도비율4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-sdiff4` | 매수비율4 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-offerno5` | 매도증권사코드5 | String | Y | 6 | - |
| `&nbsp;&nbsp;-bidno5` | 매수증권사코드5 | String | Y | 6 | - |
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
| `&nbsp;&nbsp;-upname2` | 참고지수명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-upcode2` | 참고지수코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-upprice2` | 참고지수현재가 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-jnilnav` | 전일NAV | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jnilnavsign` | 전일NAV전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilnavchange` | 전일NAV전일대비 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jnilnavdiff` | 전일NAV등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-etftotcap` | 순자산총액(억원) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-spread` | 스프레드 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-leverage` | 레버리지 | Number | Y | 2 | - |
| `&nbsp;&nbsp;-taxgubun` | 과세구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-opcom_nmk` | 운용사 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_nm1` | LP1 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_nm2` | LP2 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_nm3` | LP3 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_nm4` | LP4 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lp_nm5` | LP5 | String | Y | 20 | - |
| `&nbsp;&nbsp;-etf_cp` | 복제방법 | String | Y | 10 | - |
| `&nbsp;&nbsp;-etf_kind` | 상품유형(Filler) | String | Y | 10 | - |
| `&nbsp;&nbsp;-vi_gubun` | VI발동해제 | String | Y | 10 | - |
| `&nbsp;&nbsp;-etn_kind_cd` | ETN상품분류 | String | Y | 20 | - |
| `&nbsp;&nbsp;-lastymd` | ETN만기일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-payday` | ETN지급일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lastdate` | ETN최종거래일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-issuernmk` | ETN발행시장참가자 | String | Y | 20 | - |
| `&nbsp;&nbsp;-last_sdate` | ETN만기상환가격결정시작일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-last_edate` | ETN만기상환가격결정종료일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-lp_holdvol` | ETNLP보유수량 | String | Y | 12 | - |
| `&nbsp;&nbsp;-listdate` | 상장일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-etp_gb` | ETP상품구분코드 | String | Y | 1 | - |
| `&nbsp;&nbsp;-etn_elback_yn` | ETN조기상환가능여부 | String | Y | 1 | - |
| `&nbsp;&nbsp;-settletype` | 최종결제 | String | Y | 2 | - |
| `&nbsp;&nbsp;-idx_asset_class1` | 지수자산분류코드(대분류) | String | Y | 2 | - |
| `&nbsp;&nbsp;-ty_text` | ETF/ETN투자유의 | String | Y | 8 | - |
| `&nbsp;&nbsp;-leverage2` | 추적수익률배수 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1901InBlock" : {
    "shcode" : "001200"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1901OutBlock": {
        "futcode": "101T6000",
        "jnilnavchange": "0",
        "opcom_nmk": "",
        "high52w": 3750,
        "jnilnavdiff": "0",
        "price": 3685,
        "per": "021.79",
        "hname": "유진투자증권",
        "updiff": "0",
        "futchange": "000.75",
        "nav": "00000.00",
        "issuernmk": "",
        "navchange": "00000.00",
        "diff": "000.68",
        "fwsvl": 110000,
        "low52w": 2185,
        "svol3": 24170,
        "etftotcap": 0,
        "upprice": "0",
        "futsign": "2",
        "svol2": 66206,
        "svol1": 110000,
        "svol5": 18102,
        "svol4": 20913,
        "leverage2": "000.00",
        "highyear": 3750,
        "bidno1": "에스지",
        "bidno3": "KB증권",
        "etn_elback_yn": "",
        "bidno2": "키움증",
        "bidno5": "NH투자",
        "bidno4": "신한투",
        "navsign": "3",
        "lastymd": "",
        "lastdate": "",
        "etn_kind_cd": "",
        "low": 3645,
        "ftradmsdiff": "034.14",
        "low52wdate": "20220930",
        "jnilnav": "0",
        "payday": "",
        "jkrate": 40,
        "listing": 96866,
        "upprice2": "0.00",
        "jnilnavsign": "",
        "volumediff": 951905,
        "change": 25,
        "uplmtprice": 4755,
        "futname": "F 202306",
        "lowtime": "090057",
        "settletype": "",
        "listdate": "19870824",
        "upchange": "0",
        "vi_gubun": "",
        "lp_holdvol": "000000000000",
        "fwdvl": 30884,
        "open": 3660,
        "offerno2": "미래에",
        "high52wdate": "20230605",
        "offerno1": "키움증",
        "offerno4": "삼성증",
        "offerno3": "신한투",
        "sign": "2",
        "scha4": 0,
        "navdiff": "000.00",
        "scha3": 0,
        "offerno5": "NH투자",
        "scha2": 5,
        "scha1": 0,
        "scha5": 0,
        "high": 3750,
        "last_edate": "",
        "etf_kind": "",
        "ty_text": "",
        "dvol1": 54814,
        "idx_asset_class1": "",
        "dvol2": 49011,
        "highyeardate": "20230605",
        "dvol3": 34055,
        "dvol4": 32384,
        "dvol5": 26162,
        "upname": "20230512",
        "futprice": "343.70",
        "ftradmscha": 0,
        "volume": "000000322192",
        "ftradmddiff": "009.59",
        "lp_nm1": "신영증권",
        "jnilvolume": "000001274097",
        "exhratio": "007.17",
        "lp_nm4": "",
        "lp_nm5": "",
        "lp_nm2": "eBEST 증권",
        "ddiff5": "008.12",
        "lp_nm3": "",
        "last_sdate": "",
        "ddiff4": "010.05",
        "ddiff3": "010.57",
        "ddiff2": "015.21",
        "ddiff1": "017.01",
        "lowyear": 2230,
        "leverage": 0,
        "etp_gb": "",
        "cocrate": "0",
        "dnlmtprice": 2565,
        "vol": "000.33",
        "dcha5": 0,
        "sdiff5": "005.62",
        "recprice": 3660,
        "avg": 3698,
        "dcha4": 0,
        "sdiff4": "006.49",
        "dcha3": 0,
        "sdiff3": "007.50",
        "upcode2": "",
        "dcha2": 0,
        "sdiff2": "020.55",
        "kasis": "0",
        "dcha1": 5,
        "sdiff1": "034.14",
        "value": 1192,
        "lowyeardate": "20230103",
        "upsign": "",
        "upname2": "",
        "ftradmdcha": 0,
        "shcode": "001200",
        "opentime": "090013",
        "taxgubun": "0",
        "spread": "000.14",
        "subprice": 2560,
        "hightime": "091719",
        "upcode": "000",
        "flmtvol": "000006944768",
        "futdiff": "000.22",
        "etf_cp": ""
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1902"></a>
## `t1902` ETF시간별추이

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
| `t1902InBlock` | t1902InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | 연속조회키 연속 조회시 이 값을 InBlock의 time 필드에 넣어준다. |


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
| `t1902OutBlock` | t1902OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-upname` | 업종지수명 | String | Y | 20 | - |
| `t1902OutBlock1` | t1902OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-navdiff` | NAV대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-nav` | NAV | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-navchange` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-crate` | 추적오차 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-grate` | 괴리 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jisu` | 지수 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jichange` | 전일대비 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jirate` | 전일대비율 | Number | Y | 8.2 | - |


### 요청 Example

```json
{
  "t1902InBlock" : {
    "shcode" : "448330",
    "time" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1902OutBlock": {
        "upname": "",
        "time": "152954",
        "hname": "KODEX 삼성전자채권혼"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1902OutBlock1": [
        {
            "jirate": "0.00",
            "nav": "10683.10",
            "navchange": "-18.66",
            "change": 35,
            "grate": "-0.22",
            "sign": "5",
            "navdiff": "-23.10",
            "crate": "0.04",
            "jichange": "0.00",
            "volume": "13498",
            "jisu": "0.00",
            "price": 10660,
            "time": "장:마:감"
        },
        {
            "jirate": "0.00",
            "nav": "10683.79",
            "navchange": "-17.97",
            "change": 35,
            "grate": "-0.22",
            "sign": "5",
            "navdiff": "-23.79",
            "crate": "0.03",
            "jichange": "0.00",
            "volume": "13485",
            "jisu": "0.00",
            "price": 10660,
            "time": "15:30:30"
        }
    ]
}
```

---

<a id="tr-t1903"></a>
## `t1903` ETF일별추이

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
| `t1903InBlock` | t1903InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | 연속조회키 연속 조회시 이 값을 InBlock의 date 필드에 넣어준다. |


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
| `t1903OutBlock` | t1903OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-hname` | 종목명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-upname` | 업종지수명 | String | Y | 20 | - |
| `t1903OutBlock1` | t1903OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-navdiff` | NAV대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-nav` | NAV | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-navchange` | 전일대비 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-crate` | 추적오차 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-grate` | 괴리 | Number | Y | 9.2 | - |
| `&nbsp;&nbsp;-jisu` | 지수 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jichange` | 전일대비 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jirate` | 전일대비율 | Number | Y | 8.2 | - |


### 요청 Example

```json
{
  "t1903InBlock" : {
    "shcode" : "448330",
    "date" : ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1903OutBlock": {
        "date": "20230509",
        "upname": "",
        "hname": "KODEX 삼성전자채권혼"
    },
    "t1903OutBlock1": [
        {
            "date": "20230608",
            "jirate": "0.00",
            "nav": "10683.10",
            "navchange": "18.66",
            "change": 35,
            "grate": "-0.22",
            "sign": "5",
            "navdiff": "-23.10",
            "crate": "0.04",
            "jichange": "0.00",
            "volume": "13498",
            "jisu": "0.00",
            "price": 10660
        },
        {
            "date": "20230607",
            "jirate": "0.00",
            "nav": "10701.76",
            "navchange": "-24.79",
            "change": 35,
            "grate": "-0.06",
            "sign": "5",
            "navdiff": "-6.76",
            "crate": "0.52",
            "jichange": "0.00",
            "volume": "16803",
            "jisu": "0.00",
            "price": 10695
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1904"></a>
## `t1904` ETF구성종목조회

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
| `t1904InBlock` | t1904InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | ETF단축코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-date` | PDF적용일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-sgb` | 정렬기준(1:평가금액2:증권수) | String | Y | 1 | - |


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
| `t1904OutBlock` | t1904OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-chk_tday` | 당일구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-date` | PDF적용일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | ETF현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | ETF전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | ETF전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | ETF등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | ETF누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-nav` | NAV | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-navsign` | NAV전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-navchange` | NAV전일대비 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-navdiff` | NAV등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-jnilnav` | 전일NAV | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jnilnavsign` | 전일NAV전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-jnilnavchange` | 전일NAV전일대비 | Number | Y | 8.2 | - |
| `&nbsp;&nbsp;-jnilnavdiff` | 전일NAV등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-upname` | 업종명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-upprice` | 업종현재가 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-upsign` | 업종전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-upchange` | 업종전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-updiff` | 업종등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-futname` | 선물최근월물명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-futcode` | 선물최근월물코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-futprice` | 선물현재가 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-futsign` | 선물전일비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-futchange` | 선물전일대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-futdiff` | 선물등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-upname2` | 참고지수명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-upcode2` | 참고지수코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-upprice2` | 참고지수현재가 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-etftotcap` | 순자산총액(단위:억) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-etfnum` | 구성종목수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-etfcunum` | CU주식수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cash` | 현금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-opcom_nmk` | 운용사명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-tot_pval` | 전종목평가금액합 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tot_sigatval` | 전종목구성시가총액합 | Number | Y | 12 | - |
| `t1904OutBlock1` | t1904OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 단축코드 | String | Y | 12 | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금(백만) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-icux` | 단위증권수(계약수/원화현금/USD현금/창고증권) | Number | Y | 12 | - |
| `&nbsp;&nbsp;-parprice` | 액면금액/설정현금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-pvalue` | 평가금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sigatvalue` | 구성시가총액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-profitdate` | PDF적용일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-weight` | 비중(평가금액) | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff2` | ETF종목과등락차 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1904InBlock" : {
    "shcode" : "448330",
    "date" : "20230104",
    "sgb" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1904OutBlock": {
        "date": "20230104",
        "futcode": "101T9000",
        "chk_tday": "0",
        "jnilnavchange": "-3.50",
        "opcom_nmk": "삼성자산운용(ETF)",
        "sign": "3",
        "navsign": "3",
        "navdiff": "0.00",
        "jnilnavdiff": "-0.03",
        "upcode2": "",
        "price": 10690,
        "jnilnav": "10689.10",
        "upprice2": "0",
        "cash": 0,
        "upsign": "",
        "upname2": "",
        "jnilnavsign": "5",
        "updiff": "0",
        "nav": "0.00",
        "upname": "？\u0006      p\r      鄒？",
        "futchange": "0.00",
        "navchange": "0.00",
        "etfnum": 7,
        "futprice": "351.70",
        "change": 0,
        "futname": "F 202309",
        "diff": "0.00",
        "tot_pval": 1008302135,
        "volume": 0,
        "upchange": "0",
        "upcode": "000",
        "etftotcap": 224,
        "upprice": "0",
        "futsign": "3",
        "tot_sigatval": 401022935,
        "etfcunum": 21,
        "futdiff": "0.00"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1904OutBlock1": [
        {
            "parprice": 0,
            "profitdate": "00000000",
            "shcode": "005930",
            "change": 2400,
            "sign": "2",
            "weight": "27.94",
            "diff": "4.33",
            "pvalue": 281709000,
            "icux": 5085,
            "sigatvalue": 293913000,
            "volume": 20188071,
            "price": 57800,
            "value": 1151474,
            "hname": "삼성전자",
            "diff2": "4.33"
        },
        {
            "parprice": 0,
            "profitdate": "",
            "shcode": "KR103501GC90",
            "change": 0,
            "sign": "",
            "weight": "19.57",
            "diff": "0",
            "pvalue": 0,
            "icux": 0,
            "sigatvalue": 0,
            "volume": 0,
            "price": 0,
            "value": 0,
            "hname": "국고03125-2709(22-8)",
            "diff2": "0"
        }
    ]
}
```

---

<a id="tr-t1906"></a>
## `t1906` ETFLP호가

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
| `t1906InBlock` | t1906InBlock | Object | Y | - | - |
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
| `t1906OutBlock` | t1906OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-hname` | 한글명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem1` | LP매도호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem1` | LP매수호가수량1 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem2` | LP매도호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem2` | LP매수호가수량2 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem3` | LP매도호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem3` | LP매수호가수량3 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem4` | LP매도호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem4` | LP매수호가수량4 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem5` | LP매도호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem5` | LP매수호가수량5 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem6` | LP매도호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem6` | LP매수호가수량6 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem7` | LP매도호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem7` | LP매수호가수량7 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem8` | LP매도호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem8` | LP매수호가수량8 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem9` | LP매도호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem9` | LP매수호가수량9 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_offerrem10` | LP매도호가수량10 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-lp_bidrem10` | LP매수호가수량10 | Number | Y | 12 | - |
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


### 요청 Example

```json
{
  "t1906InBlock" : {
    "shcode" : "001200"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1906OutBlock": {
        "offerho4": 3705,
        "offerho3": 3700,
        "offerho6": 3715,
        "offerho5": 3710,
        "offerho8": 3725,
        "offerho7": 3720,
        "offerho9": 3730,
        "lp_offerrem6": 0,
        "lp_offerrem5": 0,
        "lp_bidrem10": 0,
        "lp_offerrem8": 0,
        "lp_offerrem7": 0,
        "lp_offerrem2": 0,
        "lp_offerrem1": 0,
        "lp_offerrem4": 0,
        "lp_offerrem3": 0,
        "offer": 18352,
        "price": 3685,
        "lp_bidrem2": 0,
        "lp_bidrem3": 0,
        "lp_bidrem1": 0,
        "lp_bidrem6": 0,
        "tmoffer": 0,
        "lp_bidrem7": 0,
        "hname": "유진투자증권",
        "lp_bidrem4": 0,
        "offerho2": 3695,
        "lp_bidrem5": 0,
        "offerho1": 3690,
        "lp_bidrem8": 0,
        "lp_bidrem9": 0,
        "yediff": "000.00",
        "diff": "000.68",
        "prebidcha10": 0,
        "offerho10": 3735,
        "yeprice": 0,
        "preoffercha9": 0,
        "preoffercha8": 0,
        "preoffercha7": 0,
        "preoffercha6": 0,
        "preoffercha5": 0,
        "preoffercha4": 0,
        "preoffercha3": 0,
        "bidrem3": 4108,
        "bidrem4": 5458,
        "bidrem1": 2647,
        "bidrem2": 1668,
        "low": 3645,
        "preoffercha2": 0,
        "preoffercha1": 0,
        "bidrem9": 1886,
        "bidrem7": 5183,
        "bidrem8": 126,
        "bidrem5": 5181,
        "bidrem6": 6696,
        "change": 25,
        "uplmtprice": 4755,
        "tmbid": 0,
        "lp_offerrem9": 0,
        "lp_offerrem10": 0,
        "open": 3660,
        "jnilclose": 3660,
        "ho_status": "1",
        "sign": "2",
        "preoffercha": 0,
        "high": 3750,
        "hotime": "10265501",
        "yechange": 0,
        "volume": 322192,
        "preoffercha10": 0,
        "offerrem2": 1,
        "bidho5": 3665,
        "offerrem3": 21,
        "bidho4": 3670,
        "offerrem4": 528,
        "bidho7": 3655,
        "offerrem5": 8485,
        "bidho6": 3660,
        "bidho9": 3645,
        "bidho8": 3650,
        "offerrem1": 619,
        "yevolume": 0,
        "offerrem6": 1454,
        "offerrem7": 2803,
        "offerrem8": 828,
        "offerrem9": 2512,
        "dnlmtprice": 2565,
        "bidho1": 3685,
        "bidho3": 3675,
        "bidho2": 3680,
        "prebidcha": 318,
        "prebidcha2": 318,
        "bidrem10": 1569,
        "prebidcha3": 0,
        "prebidcha4": 0,
        "bidho10": 3640,
        "prebidcha5": 0,
        "prebidcha6": 0,
        "prebidcha7": 0,
        "prebidcha8": 0,
        "prebidcha9": 0,
        "shcode": "001200",
        "yesign": "3",
        "offerrem10": 1101,
        "bid": 34522,
        "prebidcha1": 0
    }
}
```
