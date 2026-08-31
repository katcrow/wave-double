# [주식] 투자정보

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=580d2770-a7a9-49e3-9ec1-49ed8bc734a2)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `580d2770-a7a9-49e3-9ec1-49ed8bc734a2` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/investinfo` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 투자정보에 대한 서비스로 종목별 정보를 확인할 수 있습니다. |

## TR 목록 (8건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 뉴스본문 | [t3102](investment-info.md#tr-t3102) | 1 | 1 | 3 |
| 종목별증시일정 | [t3202](investment-info.md#tr-t3202) | 1 | 1 | 3 |
| FNG_요약 | [t3320](investment-info.md#tr-t3320) | 1 | 1 | 3 |
| 재무순위종합 | [t3341](investment-info.md#tr-t3341) | 1 | 1 | 3 |
| 투자의견 | [t3401](investment-info.md#tr-t3401) | 1 | 1 | 3 |
| 해외실시간지수 | [t3518](investment-info.md#tr-t3518) | 1 | 1 | 3 |
| 해외지수조회(API용) | [t3521](investment-info.md#tr-t3521) | 1 | 1 | 3 |
| 증시주변자금추이 | [t8428](investment-info.md#tr-t8428) | 1 | 1 | 3 |

---

<a id="tr-t3102"></a>
## `t3102` 뉴스본문

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
| `t3102InBlock` | t3102InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-sNewsno` | 뉴스번호 | String | Y | 24 | - |


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
| `t3102OutBlock` | t3102OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-sJongcode` | 뉴스종목 | String | Y | 6 | - |
| `t3102OutBlock1` | t3102OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-sBody` | 뉴스본문 | String | Y | 100 | - |
| `t3102OutBlock2` | t3102OutBlock2 | Object | Y | - | - |
| `&nbsp;&nbsp;-sTitle` | 뉴스타이틀 | String | Y | 300 | - |


### 요청 Example

```json
{
  "t3102InBlock": {
    "sNewsno": "2023051510383935PL7HQ87D"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t3102OutBlock1": [
        {
            "sBody": "<p>[서울경제TV=김혜영기자]<span stockcode='192820'>코스맥스(192820)<\/span>가 중국 리오프닝 수혜가 본"
        },
        {
            "sBody": "격적으로 \r\n반영되는 시기라는 증권가 호평에 강세다. 증권사들은 코스맥스의 목표주가를 줄줄\r\n이 높여잡？"
        },
        {
            "sBody": "？ 있다.<\/p>\n<p> <\/p>\n<p>코스맥스는 15일 오전 10시 25분 현 전 거래일 대비 3.50% 오른 8만5,800원을 기？"
        },
        {
            "sBody": "？\r\n하고 있다.<\/p>\n<p> <\/p>\n<p>증권가는 코스맥스에 대해 장밋빛 전망을 내놓으며 줄줄이 목표주가를 높여"
        },
        {
            "sBody": "잡고 \r\n있다. 메리츠증권은 코스맥스를 화장품 최선호주로 적극 매수 접근을 추전한다며 목\r\n표주가를 14？"
        },
        {
            "sBody": "맙坪막？ 상향 조정했다. 이어 한국투자증권(9만5,000원→11만원), 하나\r\n증권(10만원→12만원), NH투자증권"
        },
        {
            "sBody": "(10만원→11만5000원), 키움증권(10만원→11만원)\r\n 등도 목표가를 올렸다.<\/p>\n<p> <\/p>\n<p>증권가는 중국"
        },
        {
            "sBody": "리오프닝(경제활동 재개) 본격화로 코스맥스의 실적 개선을 예상하\r\n고 있다. 박현진 신한투자증권 연구원"
        },
        {
            "sBody": "은 \"중국 로컬 수요 회복에 가장 밀접한 수혜\r\n주라는 점에서 올해 2분기부터 실적 회복 강도는 강해질 전？"
        },
        {
            "sBody": "？\"이라고 강조했다. <\/p>\n<p> <\/p>\n<p>김명주 한국투자증권 연구원은 \u201C올해 1분기 중국 법인 매출은 중국"
        },
        {
            "sBody": "내 코로나19 \r\n재확산 등으로 전년 동기 대비 17.8% 감소했다\u201D면서도 \u201C올해 2분기부터는 중국 매\r\n출도 ？"
        },
        {
            "sBody": "봉凉섭？ 돌아설 것\u201D이라고 설명했다.<\/p>\n<p> <\/p>\n<p>박은정 하나증권 연구원도 \u201C중국 법인은 낮은 가동"
        },
        {
            "sBody": "률로 수익성이 하락했으나, 지\r\n난 3월부터 수주 회복과 생산 정상화가 진행 중\u201D이라며 \u201C2분기부터 중국"
        },
        {
            "sBody": "수요 정\r\n상화, 방한 외국인 증가로 수주 급증이 예상된다\u201D고 내다봤다.<\/p>\n<p> <\/p>\n<p>하누리 메리츠증"
        },
        {
            "sBody": "권 연구원은 \u201C코스맥스는 성장주이자 가치주로 국내는 중소형 브\r\n랜드 증가로 전방 파편화, 대일·대미·"
        },
        {
            "sBody": "대동남아 등 수출 다변화, 중국은 가동 정상\r\n화, 미국은 공정 효율화, 동남아는 경제 정상화로 고성장할 ？"
        },
        {
            "sBody": "桓？\"이라며 \"12개월 선\r\n행 주가수익비율(PER)은 10배로 글로벌 1위 화장품 제조사라는 위상에 걸맞지 않다"
        },
        {
            "sBody": "\"\r\n고 평가했다.<\/p>\n<p> <\/p>\n<p>한편, 코스맥스는 1분기 연결기준 매출액과 영업이익이 각각 4,,033억 원"
        },
        {
            "sBody": ", 138억 \r\n원을 기록했다. 이는 전년 동기보다 각각 1.4%, 0.5% 증가한 수치로, 영업이익은 시\r\n장 전망치？"
        },
        {
            "sBody": "？ 웃돌았다. \/hyk@seadaily.com<\/p>\/김혜영 기자 hyk@sedaily.com<br \/><br \/>[ⓒ 서울\r\n경제, 무단 전재 ？"
        },
        {
            "sBody": "？ 재배포 금지]<br \/><br \/>"
        }
    ],
    "t3102OutBlock": [
        {
            "sJongcode": "192820"
        }
    ],
    "rsp_msg": "조회완료"
}
```

---

<a id="tr-t3202"></a>
## `t3202` 종목별증시일정

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
| `t3202InBlock` | t3202InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-date` | 조회일자 | String | Y | 8 | - |


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
| `t3202OutBlock` | t3202OutBlock | Object Array | Y | - | - |
| `&nbsp;&nbsp;-recdt` | 기준일 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tableid` | 테이블아이디 | String | Y | 6 | - |
| `&nbsp;&nbsp;-upgu` | 업무구분 | String | Y | 2 | 01:유상증자 02:무상증가 03:배당 04:감자 05:합병/분할 06:매수청구 07:실권주 08:액면교체 09:주주총회 10:상호변경 11:국내CB전환 12:해외CB전환 13:해외BW행사 14:스톡옵션행사 |
| `&nbsp;&nbsp;-custno` | 발행체번호 | String | Y | 5 | - |
| `&nbsp;&nbsp;-custnm` | 발행회사명 | String | Y | 80 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-upunm` | 업무명 | String | Y | 20 | - |


### 요청 Example

```json
{
  "t3202InBlock": {
    "shcode": "001200",
    "date": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t3202OutBlock": [
        {
            "custno": "00120",
            "custnm": "유진투자증권(주)",
            "recdt": "00000000",
            "shcode": "001200",
            "tableid": "SA02BS",
            "upunm": "주주총회",
            "upgu": "09"
        },
        {
            "custno": "00120",
            "custnm": "유진투자증권(주)",
            "recdt": "20000527",
            "shcode": "001200",
            "tableid": "SA02BS",
            "upunm": "주주총회",
            "upgu": "09"
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t3320"></a>
## `t3320` FNG_요약

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
| `t3320InBlock` | t3320InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gicode` | 종목코드 | String | Y | 7 | - |


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
| `t3320OutBlock` | t3320OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-upgubunnm` | 업종구분명 | String | Y | 40 | - |
| `&nbsp;&nbsp;-sijangcd` | 시장구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-marketnm` | 시장구분명 | String | Y | 10 | - |
| `&nbsp;&nbsp;-company` | 한글기업명 | String | Y | 100 | - |
| `&nbsp;&nbsp;-baddress` | 본사주소 | String | Y | 100 | - |
| `&nbsp;&nbsp;-btelno` | 본사전화번호 | String | Y | 20 | - |
| `&nbsp;&nbsp;-gsyyyy` | 최근결산년도 | String | Y | 4 | - |
| `&nbsp;&nbsp;-gsmm` | 결산월 | String | Y | 2 | - |
| `&nbsp;&nbsp;-gsym` | 최근결산년월 | String | Y | 6 | - |
| `&nbsp;&nbsp;-lstprice` | 주당액면가 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-gstock` | 주식수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-homeurl` | Homepage | String | Y | 50 | - |
| `&nbsp;&nbsp;-grdnm` | 그룹명 | String | Y | 30 | - |
| `&nbsp;&nbsp;-foreignratio` | 외국인 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-irtel` | 주담전화 | String | Y | 30 | - |
| `&nbsp;&nbsp;-capital` | 자본금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sigavalue` | 시가총액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cashsis` | 배당금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cashrate` | 배당수익율 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-jnilclose` | 전일종가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-notice1` | 위험고지구분1_정리매매 | String | Y | 1 | - |
| `&nbsp;&nbsp;-notice2` | 위험고지구분2_투자위험 | String | Y | 1 | - |
| `&nbsp;&nbsp;-notice3` | 위험고지구분3_단기과열 | String | Y | 1 | - |
| `t3320OutBlock1` | t3320OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-gicode` | 기업코드 | String | Y | 7 | - |
| `&nbsp;&nbsp;-gsym` | 결산년월 | String | Y | 6 | - |
| `&nbsp;&nbsp;-gsgb` | 결산구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-per` | PER | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-eps` | EPS | Number | Y | 13 | - |
| `&nbsp;&nbsp;-pbr` | PBR | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-roa` | ROA | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-roe` | ROE | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-ebitda` | EBITDA | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-evebitda` | EVEBITDA | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-par` | 액면가 | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-sps` | SPS | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-cps` | CPS | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-bps` | BPS | Number | Y | 13 | - |
| `&nbsp;&nbsp;-t_per` | T.PER | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-t_eps` | T.EPS | Number | Y | 13 | - |
| `&nbsp;&nbsp;-peg` | PEG | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-t_peg` | T.PEG | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-t_gsym` | 최근분기년도 | String | Y | 6 | - |


### 요청 Example

```json
{
  "t3320InBlock": {
    "gicode": "001200"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t3320OutBlock": {
        "lstprice": 5000,
        "gstock": 96866418,
        "capital": "000000005376",
        "marketnm": "거래소",
        "sijangcd": "1",
        "jnilclose": 3625,
        "sigavalue": "000000003497",
        "irtel": "02-368-6000",
        "cashrate": "1.66",
        "gsym": "202212",
        "notice3": "0",
        "homeurl": "www.eugenefn.com",
        "notice2": "0",
        "notice1": "0",
        "price": 3610,
        "btelno": "02-368-6000",
        "baddress": "서울시 영등포구 국제금융로 24 (여의도동, 유진그룹빌딩)",
        "grdnm": "유진",
        "company": "유진투자증권(주)",
        "foreignratio": "7.06",
        "gsyyyy": "2022",
        "gsmm": "12",
        "upgubunnm": "증권업",
        "cashsis": "000000000060"
    },
    "t3320OutBlock1": {
        "par": "5000.00",
        "pbr": "0.36",
        "bps": "0000000009905",
        "roa": "0.05",
        "cps": "240.59",
        "t_peg": "0.00",
        "eps": "0000000000038",
        "roe": "0.39",
        "ebitda": "0.00",
        "gsym": "202212",
        "t_eps": "0000000000157",
        "evebitda": "0.00",
        "peg": "0.00",
        "gicode": "A001200",
        "t_gsym": "202303",
        "gsgb": "D",
        "sps": "2268.19",
        "per": "95.10",
        "t_per": "23.03"
    }
}
```

---

<a id="tr-t3341"></a>
## `t3341` 재무순위종합

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
| `t3341InBlock` | t3341InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun` | 시장구분 | String | Y | 1 | 0:전체 1:코스피 2:코스닥 |
| `&nbsp;&nbsp;-gubun1` | 순위구분(1:매출액증가율2:영업이익증가율 3:세전계속이익증가율4:부채비율5:유보율 6:EPS7:BPS8:ROE9:PERa:PBRb:PEG) | String | Y | 1 | 1@매출액증가율 2@영업이익증가율 3@세전계속이익증가율 4@부채비율 5@유보율 6@EPS 7@BPS 8@ROE 9@PER : 오름차순 a@PBR : 오름차순 b@PEG : 오름차순 |
| `&nbsp;&nbsp;-gubun2` | 대비구분 | String | Y | 1 | 1 고정 |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | idx 첫조회시 space 연속조회시 Outblock의 idx 값 세팅 |


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
| `t3341OutBlock` | t3341OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cnt` | CNT | Number | Y | 4 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t3341OutBlock1` | t3341OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-rank` | 순위 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-hname` | 기업명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-salesgrowth` | 매출액증가율 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-operatingincomegrowt` | 영업이익증가율 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ordinaryincomegrowth` | 경상이익증가율 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-liabilitytoequity` | 부채비율 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-enterpriseratio` | 유보율 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-eps` | EPS | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bps` | BPS | Number | Y | 12 | - |
| `&nbsp;&nbsp;-roe` | ROE | Number | Y | 12 | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 6 | - |
| `&nbsp;&nbsp;-per` | PER | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-pbr` | PBR | Number | Y | 13.2 | - |
| `&nbsp;&nbsp;-peg` | PEG | Number | Y | 13.2 | - |


### 요청 Example

```json
{
  "t3341InBlock": {
    "gubun": "0",
    "gubun1": "1",
    "gubun2": "1",
    "idx": 0
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t3341OutBlock1": [
        {
            "pbr": "0.41",
            "salesgrowth": 1358.39,
            "liabilitytoequity": 0.44,
            "bps": 49296.05,
            "shcode": "007700",
            "eps": 606.83,
            "roe": 1.24,
            "ordinaryincomegrowth": 77.98,
            "enterpriseratio": 9759.21,
            "peg": "0.00",
            "operatingincomegrowt": 2452.03,
            "rank": 1,
            "per": "33.62",
            "hname": "F&F홀딩스"
        },
        {
            "pbr": "3.31",
            "salesgrowth": 639.2,
            "liabilitytoequity": 66.05,
            "bps": 14035.43,
            "shcode": "138040",
            "eps": 831.04,
            "roe": 6.72,
            "ordinaryincomegrowth": -47.18,
            "enterpriseratio": 2406.23,
            "peg": "0.00",
            "operatingincomegrowt": -47.11,
            "rank": 2,
            "per": "55.83",
            "hname": "메리츠금융지주"
        }
    ],
    "t3341OutBlock": {
        "cnt": 1341,
        "idx": 100
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t3401"></a>
## `t3401` 투자의견

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
| `t3401InBlock` | t3401InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 9 | - |
| `&nbsp;&nbsp;-gubun1` | 구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-tradno` | 회원사코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-cts_date` | IDXDATE | String | Y | 8 | - |


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
| `t3401OutBlock` | t3401OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_date` | IDXDATE | String | Y | 8 | - |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sign` | 대비속성 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-value` | 거래대금 | Number | Y | 12 | - |
| `t3401OutBlock1` | t3401OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-shcode` | 종목코드 | String | Y | 9 | - |
| `&nbsp;&nbsp;-tradno` | 회원사코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-date` | 의견일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tradname` | 회원사명 | String | Y | 30 | - |
| `&nbsp;&nbsp;-bopn` | 투자의견변경후 | String | Y | 30 | - |
| `&nbsp;&nbsp;-nopn` | 투자의견변경전 | String | Y | 30 | - |
| `&nbsp;&nbsp;-boga` | 목표가변경전 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-noga` | 목표가변경후 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-close` | 의견일종가 | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t3401InBlock": {
    "shcode": "011200",
    "gubun1": "",
    "tradno": "",
    "cts_date": ""
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t3401OutBlock1": [
        {
            "date": "20230209",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 24000,
            "boga": 0,
            "nopn": "",
            "close": 21700
        },
        {
            "date": "20230208",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 24000,
            "boga": 27000,
            "nopn": "HOLD",
            "close": 22050
        },
        {
            "date": "20221110",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 20000,
            "boga": 30000,
            "nopn": "HOLD",
            "close": 20250
        },
        {
            "date": "20221102",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 22000,
            "boga": 29000,
            "nopn": "HOLD",
            "close": 19000
        },
        {
            "date": "20220811",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 27000,
            "boga": 0,
            "nopn": "BUY",
            "close": 25300
        },
        {
            "date": "20220811",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 29000,
            "boga": 0,
            "nopn": "",
            "close": 25300
        },
        {
            "date": "20220623",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 30000,
            "boga": 0,
            "nopn": "",
            "close": 24000
        },
        {
            "date": "20220531",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 29000,
            "boga": 30000,
            "nopn": "HOLD",
            "close": 32450
        },
        {
            "date": "20220516",
            "tradno": "063",
            "tradname": "eBEST 증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 36000,
            "boga": 32000,
            "nopn": "BUY",
            "close": 30200
        },
        {
            "date": "20220516",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 42000,
            "boga": 0,
            "nopn": "",
            "close": 30200
        },
        {
            "date": "20220218",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 36000,
            "boga": 36000,
            "nopn": "BUY",
            "close": 29600
        },
        {
            "date": "20220215",
            "tradno": "063",
            "tradname": "eBEST 증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 32000,
            "boga": 32000,
            "nopn": "BUY",
            "close": 25250
        },
        {
            "date": "20220215",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 0,
            "boga": 30000,
            "nopn": "HOLD",
            "close": 25250
        },
        {
            "date": "20220215",
            "tradno": "008",
            "tradname": "유진증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 31000,
            "boga": 41000,
            "nopn": "HOLD",
            "close": 25250
        },
        {
            "date": "20220215",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 36000,
            "boga": 36000,
            "nopn": "BUY",
            "close": 25250
        },
        {
            "date": "20220127",
            "tradno": "010",
            "tradname": "메리츠",
            "bopn": "HOLD",
            "shcode": "011200",
            "noga": 30000,
            "boga": 0,
            "nopn": "",
            "close": 21900
        },
        {
            "date": "20211228",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 36000,
            "boga": 48000,
            "nopn": "BUY",
            "close": 25500
        },
        {
            "date": "20211203",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 48000,
            "boga": 48000,
            "nopn": "BUY",
            "close": 26800
        },
        {
            "date": "20211115",
            "tradno": "063",
            "tradname": "eBEST 증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 32000,
            "boga": 47000,
            "nopn": "BUY",
            "close": 27500
        },
        {
            "date": "20211111",
            "tradno": "004",
            "tradname": "대신증권",
            "bopn": "BUY",
            "shcode": "011200",
            "noga": 48000,
            "boga": 48000,
            "nopn": "BUY",
            "close": 27450
        }
    ],
    "t3401OutBlock": {
        "volume": 650972,
        "cts_date": "20211109",
        "price": 17800,
        "change": 240,
        "sign": "2",
        "diff": "001.37",
        "value": 11639
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t3518"></a>
## `t3518` 해외실시간지수

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
| `t3518InBlock` | t3518InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-kind` | 종목종류 | String | Y | 1 | S:해외지수 F:해외선물 R:환율/금리 |
| `&nbsp;&nbsp;-symbol` | SYMBOL | String | Y | 16 | - |
| `&nbsp;&nbsp;-cnt` | 입력건수 | Number | Y | 4 | - |
| `&nbsp;&nbsp;-jgbn` | 조회구분 | String | Y | 1 | 0:일 1:주 2:월 3:분 4:틱 |
| `&nbsp;&nbsp;-nmin` | N분 | Number | Y | 3 | jgbn이 3인 경우에 n분 |
| `&nbsp;&nbsp;-cts_date` | CTS_DATE | String | Y | 8 | 다음 조회시 OutBlock의 cts_date 입력 처음 조회시 스페이스 |
| `&nbsp;&nbsp;-cts_time` | CTS_TIME | String | Y | 6 | 다음 조회시 OutBlock의 cts_time 입력 처음 조회시 스페이스 |


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
| `t3518OutBlock` | t3518OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_date` | CTS_DATE | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | CTS_TIME | String | Y | 6 | - |
| `t3518OutBlock1` | t3518OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-open` | 시가 | Number | Y | 9.4 | ※ 종목종류별 가격 소수점 자리수 - S(해외지수) : 9.2 - F(해외선물) : 9.2 - R(환율/금리) : 9.4 |
| `&nbsp;&nbsp;-high` | 고가 | Number | Y | 9.4 | ※ 종목종류별 가격 소수점 자리수 - S(해외지수) : 9.2 - F(해외선물) : 9.2 - R(환율/금리) : 9.4 |
| `&nbsp;&nbsp;-low` | 저가 | Number | Y | 9.4 | ※ 종목종류별 가격 소수점 자리수 - S(해외지수) : 9.2 - F(해외선물) : 9.2 - R(환율/금리) : 9.4 |
| `&nbsp;&nbsp;-price` | 현재가 | Number | Y | 9.4 | - |
| `&nbsp;&nbsp;-sign` | 전일대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 전일대비 | Number | Y | 9.4 | - |
| `&nbsp;&nbsp;-uprate` | 등락율 | Number | Y | 9.4 | - |
| `&nbsp;&nbsp;-volume` | 누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bidho` | 매수호가 | Number | Y | 9.4 | - |
| `&nbsp;&nbsp;-offerho` | 매도호가 | Number | Y | 9.4 | - |
| `&nbsp;&nbsp;-bidrem` | 매수잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-offerrem` | 매도잔량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-kind` | 종목종류 | String | Y | 1 | - |
| `&nbsp;&nbsp;-symbol` | SYMBOL | String | Y | 16 | - |
| `&nbsp;&nbsp;-exid` | EXID | String | Y | 4 | - |
| `&nbsp;&nbsp;-kodate` | 한국일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-kotime` | 한국시간 | String | Y | 8 | - |


### 요청 Example

```json
{
  "t3518InBlock": {
    "kind": "S",
    "symbol": "NAS@IXIC",
    "cnt": 20,
    "jgbn": "4",
    "nmin": 0,
    "cts_date": " ",
    "cts_time": " "
  }
}
```

### 응답 Example

```
{
    "rsp_cd": "00000",
    "t3518OutBlock": {
        "cts_date": "20230602",
        "cts_time": "161540"
    },
    "rsp_msg": "조회완료",
    "t3518OutBlock1": [
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051559",
            "time": "16155900",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051558",
            "time": "16155800",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051557",
            "time": "16155700",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051556",
            "time": "16155600",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051555",
            "time": "16155500",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051554",
            "time": "16155400",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051553",
            "time": "16155300",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051552",
            "time": "16155200",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051551",
            "time": "16155100",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051550",
            "time": "16155000",
            "uprate": "0.0107",
            "open": "131.9048"
        },
        {
            "date": "20230602",
            "symbol": "",
            "exid": "",
            "kind": "",
            "change": "1.3979",
            "sign": "2",
            "offerho": "0.0000",
            "bidrem": "000000000000",
            "offerrem": "000000000000",
            "volume": "000000000000",
            "high": "132.5621",
            "bidho": "0.0000",
            "kodate": "20230603",
            "low": "131.2586",
            "price": "132.4077",
            "kotime": "051549",
            "time": "16154900",
            "uprate": "0.0107",
            "open": "131.9048"
        },
```

---

<a id="tr-t3521"></a>
## `t3521` 해외지수조회(API용)

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
| `t3521InBlock` | t3521InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-kind` | 종목종류 | String | Y | 1 | S : 해외지수<br/>R : 해외환율<br/>F : 해외선물 |
| `&nbsp;&nbsp;-symbol` | SYMBOL | String | Y | 16 | 해외지수/환율/선물 SYMBOL<br/>----- 주요해외지수 SYMBOL -----<br/>DJI@DJI : 다우산업<br/>NAS@IXIC : 나스닥 종합<br/>SPI@SPX : S&P 500<br/>USI@SOXX : 필라델피아 반도체<br/>NII@NI225 : 니케이 225<br/>TWS@TI01 : 대만 가권<br/>SHS@000002 : 상해 A<br/>SHS@000003 : 상해 B<br/>SGI@STI : 싱가폴 STI<br/>HSI@HSI : 항셍<br/>PAS@CAC40 : 프랑스 CAC 40<br/>LNS@FTSE100 : 영국 FTSE 100<br/>XTR@DAX30 : 독일 DAX 30<br/>----- 주요해외환율 SYMBOL -----<br/>USDKRWSMBS : 원/달러<br/>USDJPYCOMP : 일본 엔/달러<br/>EURUSDCOMP : 달러/유로<br/>JPYKRWCOMP : 한국 원/일본 엔<br/>USDCNYCOMP : 중국 위안/달러<br/>----- 주요해외선물 SYMBOL -----<br/>SPT@DU : 두바이유 현물<br/>NYM@CL : WTI 11-10<br/>COM@GC : 금 11-09<br/>LME@ZDA : 아연 3M<br/>LME@CDA : 전기동 3M |


### 응답 Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| `content-type` | 컨텐츠타입 | String | Y | 100 | LS증권 제공 API를 호출하기 위한 Request Body 데이터 포맷으로 "application/json; charset=utf-8 설정" |
| `tr_cd` | 거래 CD | String | Y | 10 | LS증권 거래코드 |
| `tr_cont` | 연속 거래 여부 | String | Y | 1 | 연속거래 여부<br/>Y:연속○<br/>N:연속× |
| `tr_cont_key` | 연속 거래 Key | String | Y | 18 | 연속일 경우 그전에 내려온 연속키 값 올림 |


### 응답 Body

_해당 항목 없음_

### 요청 Example

```json
{
  "t3521InBlock": {
    "kind": "S",
    "symbol": "DJI@DJI"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "조회완료",
    "t3521OutBlock": {
        "date": "20230602",
        "symbol": "DJI@DJI",
        "change": "701.19",
        "sign": "2",
        "diff": "2.12",
        "close": "33762.76",
        "hname": "다우 산업"
    }
}
```

---

<a id="tr-t8428"></a>
## `t8428` 증시주변자금추이

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
| `t8428InBlock` | t8428InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-fdate` | from일자 | String | Y | 8 | 출력 기간의 시작일 |
| `&nbsp;&nbsp;-tdate` | to일자 | String | Y | 8 | 출력 기간의 종료일 |
| `&nbsp;&nbsp;-gubun` | 구분 | String | Y | 1 | 1:예탁금 2:수익증권 |
| `&nbsp;&nbsp;-key_date` | 날짜 | String | Y | 8 | 다음 조회시 사용함. 다음 조회시 OutBlock의 date 필드값 입력. 처음 조회시 Space |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | 001:코스피 301:코스닥 |
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
| `t8428OutBlock` | t8428OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜CTS | String | Y | 8 | - |
| `&nbsp;&nbsp;-idx` | IDX | Number | Y | 4 | - |
| `t8428OutBlock1` | t8428OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jisu` | 지수 | Number | Y | 7.2 | - |
| `&nbsp;&nbsp;-sign` | 대비구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-change` | 대비 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-diff` | 등락율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-volume` | 거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-custmoney` | 고객예탁금_억원 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-yecha` | 예탁증감_억원 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-vol` | 회전율 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-outmoney` | 미수금_억원 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-trjango` | 신용잔고_억원 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-futymoney` | 선물예수금_억원 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stkmoney` | 주식형_억원 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mstkmoney` | 혼합형_억원(주식) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mbndmoney` | 혼합형_억원(채권) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bndmoney` | 채권형_억원 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-bndsmoney` | 필러(구.단기채권) | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mmfmoney` | MMF_억원(주식) | Number | Y | 8 | - |


### 요청 Example

```json
{
  "t8428InBlock": {
    "fdate": "",
    "tdate": "",
    "gubun": "1",
    "key_date": " ",
    "upcode": "001",
    "cnt": 1
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t8428OutBlock1": [
        {
            "date": "20230601",
            "futymoney": 117372,
            "mstkmoney": 98234,
            "change": "7.95",
            "sign": "5",
            "yecha": 7795,
            "mbndmoney": 160565,
            "diff": "-0.31",
            "jisu": "2569.17",
            "volume": 675233,
            "bndmoney": 1227608,
            "bndsmoney": 0,
            "vol": "31.04",
            "stkmoney": 973287,
            "outmoney": 4571,
            "mmfmoney": 1757638,
            "custmoney": 527348,
            "trjango": 185961
        }
    ],
    "t8428OutBlock": {
        "date": "20230601",
        "idx": 1
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
