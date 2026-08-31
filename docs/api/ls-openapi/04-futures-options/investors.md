# [선물/옵션] 투자자

> LS증권 OPEN API 정의서 · 그룹: **선물/옵션** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=2f1eea77-5606-4512-93c6-31b21d2ece90&api_id=47005ce6-8500-4a3d-ad6c-f96ec3251669)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `47005ce6-8500-4a3d-ad6c-f96ec3251669` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/futureoption/investor` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 상품선물 투자자별 데이터를 확인할 수 있습니다. |

## TR 목록 (4건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 상품선물투자자매매동향(실시간) | [t2541](investors.md#tr-t2541) | 1 | 1 | 3 |
| 상품선물투자자매매동향(챠트용) | [t2545](investors.md#tr-t2545) | 1 | 1 | 3 |
| KRX야간파생 투자자기간별(API용) | [t8462](investors.md#tr-t8462) | 1 | 1 | 3 |
| KRX야간파생 투자자시간대별(API용) | [t8463](investors.md#tr-t8463) | 1 | 1 | 3 |

---

<a id="tr-t2541"></a>
## `t2541` 상품선물투자자매매동향(실시간)

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
| `t2541InBlock` | t2541InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-eitem` | 상품ID | String | Y | 2 | 01@KTB 02@5TB 03@LKTB 04@USD 05@JPY 06@EUR 07@GOLD 08@LH 09@MGD |
| `&nbsp;&nbsp;-market` | 시장구분 | String | Y | 1 | 0@선물 1@콜 2@풋 |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-gubun1` | 수량구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-gubun2` | 전일분구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-cts_time` | CTSTIME | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | - |
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
| `t2541OutBlock` | t2541OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-eitem` | 상품ID | String | Y | 2 | - |
| `&nbsp;&nbsp;-sgubun` | 시장구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-cts_time` | CTSTIME | String | Y | 8 | - |
| `&nbsp;&nbsp;-tjjcode_08` | 개인투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_08` | 개인매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_08` | 개인매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_08` | 개인증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_08` | 개인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_17` | 외국인투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_17` | 외국인매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_17` | 외국인매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_17` | 외국인증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_17` | 외국인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_18` | 기관계투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_18` | 기관계매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_18` | 기관계매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_18` | 기관계증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_18` | 기관계순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_01` | 증권투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_01` | 증권매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_01` | 증권매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_01` | 증권증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_01` | 증권순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_03` | 투신투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_03` | 투신매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_03` | 투신매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_03` | 투신증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_03` | 투신순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_04` | 은행투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_04` | 은행매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_04` | 은행매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_04` | 은행증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_04` | 은행순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_02` | 보험투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_02` | 보험매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_02` | 보험매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_02` | 보험증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_02` | 보험순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_05` | 종금투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_05` | 종금매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_05` | 종금매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_05` | 종금증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_05` | 종금순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_06` | 기금투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_06` | 기금매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_06` | 기금매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_06` | 기금증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_06` | 기금순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_11` | 국가투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |
| `t2541OutBlock1` | t2541OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-sv_08` | 개인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_17` | 외국인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_18` | 기관계순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_01` | 증권순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_03` | 투신순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_04` | 은행순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_02` | 보험순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_05` | 종금순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_06` | 기금순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_00` | 사모펀드순매수 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t2541InBlock": {
    "eitem": "1",
    "market": "1",
    "upcode": "001",
    "gubun1": "1",
    "gubun2": "1",
    "cts_time": "1",
    "cts_idx": 0,
    "cnt": 1
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t2541OutBlock": {
        "md_06": 1155,
        "md_07": 77,
        "md_04": 8194,
        "md_05": 520,
        "md_02": 430,
        "md_03": 2466,
        "md_00": 0,
        "md_01": 55704,
        "ms_04": 14002,
        "ms_03": 2931,
        "ms_06": 284,
        "ms_05": 640,
        "ms_00": 0,
        "ms_02": 1664,
        "ms_01": 46738,
        "svolume_00": 0,
        "svolume_01": -8966,
        "svolume_04": 5808,
        "svolume_05": 120,
        "svolume_02": 1234,
        "svolume_03": 465,
        "svolume_08": 5903,
        "svolume_06": -871,
        "tjjcode_08": "",
        "svolume_07": -50,
        "md_08": 664,
        "rate_00": 0,
        "sgubun": "1",
        "eitem": "1",
        "rate_11": 0,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 66259,
        "rate_07": 0,
        "rate_08": 0,
        "rate_05": 0,
        "rate_06": 0,
        "rate_03": 0,
        "rate_04": 0,
        "rate_01": 0,
        "cts_time": "18100000",
        "rate_02": 0,
        "md_17": 47217,
        "jjcode_03": "",
        "md_18": 68469,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 43574,
        "jjcode_07": "",
        "ms_11": 0,
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 6567,
        "ms_07": 27,
        "rate_18": 0,
        "svolume_17": -3643,
        "rate_17": 0,
        "svolume_18": -2210
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t2541OutBlock1": [
        {
            "sv_18": -2210,
            "sv_07": -50,
            "sv_17": -3643,
            "sv_06": -871,
            "sv_05": 120,
            "sv_04": 5808,
            "sv_08": 5903,
            "sv_03": 465,
            "sv_02": 1234,
            "sv_01": -8966,
            "sv_11": 0,
            "sv_00": 0,
            "time": "18103000"
        }
    ]
}
```

---

<a id="tr-t2545"></a>
## `t2545` 상품선물투자자매매동향(챠트용)

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
| `t2545InBlock` | t2545InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-eitem` | 상품ID | String | Y | 2 | 01@KTB 02@5TB 03@LKTB 04@USD 05@JPY 06@EUR 07@GOLD 08@LH 09@MGD |
| `&nbsp;&nbsp;-sgubun` | 시장구분 | String | Y | 1 | 0@선물 1@콜 2@풋 |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-nmin` | N분 | Object | Y | 2 | - |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |
| `&nbsp;&nbsp;-bgubun` | 전일분 | String | Y | 1 | - |


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
| `t2545OutBlock` | t2545OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-eitem` | 상품ID | String | Y | 2 | - |
| `&nbsp;&nbsp;-sgubun` | 시장구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-indcode` | 개인투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-forcode` | 외국인투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-syscode` | 기관계투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-stocode` | 증권투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-invcode` | 투신투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-bancode` | 은행투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-inscode` | 보험투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-fincode` | 종금투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-moncode` | 기금투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-etccode` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-natcode` | 국가투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-pefcode` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-jisucd` | 기준지수코드 | String | Y | 8 | - |
| `&nbsp;&nbsp;-jisunm` | 기준지수명 | String | Y | 20 | - |
| `t2545OutBlock1` | t2545OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-datetime` | 일자시간 | String | Y | 14 | - |
| `&nbsp;&nbsp;-indmsvol` | 개인순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-indmsamt` | 개인순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-formsvol` | 외국인순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-formsamt` | 외국인순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sysmsvol` | 기관계순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sysmsamt` | 기관계순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stomsvol` | 증권순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-stomsamt` | 증권순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-invmsvol` | 투신순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-invmsamt` | 투신순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-banmsvol` | 은행순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-banmsamt` | 은행순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-insmsvol` | 보험순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-insmsamt` | 보험순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-finmsvol` | 종금순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-finmsamt` | 종금순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-monmsvol` | 기금순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-monmsamt` | 기금순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-etcmsvol` | 기타순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-etcmsamt` | 기타순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-natmsvol` | 국가순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-natmsamt` | 국가순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-pefmsvol` | 사모펀드순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-pefmsamt` | 사모펀드순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-upclose` | 기준지수 | Number | Y | 6.2 | - |
| `&nbsp;&nbsp;-upcvolume` | 기준체결거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-upvolume` | 기준누적거래량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-upvalue` | 기준거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t2545InBlock": {
    "eitem": "04",
    "sgubun": "0",
    "upcode": "",
    "nmin": 0,
    "cnt": 1,
    "bgubun": ""
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

<a id="tr-t8462"></a>
## `t8462` KRX야간파생 투자자기간별(API용)

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
| `t8462InBlock` | t8462InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-tm_rng` | 시간대(D/N/U) | String | Y | 1 | - |
| `&nbsp;&nbsp;-fot_clsf_cd` | 선물옵션구분 | String | Y | 1 | F : 선물<br/>C : 콜옵션<br/>P : 풋옵션<br/>S : 스프레드 |
| `&nbsp;&nbsp;-bsc_asts_id` | 기초자산코드 | String | Y | 3 | K2I : KP200선물/옵션<br/>MKI : 미니KP200선물/옵션<br/>KQI : 코스닥150선물/옵션<br/>WKM : 위클리옵션-월<br/>WKI : 위클리옵션-목<br/>BM3 : 국채3년선물<br/>BMA : 국채10년선물<br/>USD : 미국달러선물 |
| `&nbsp;&nbsp;-gubun2` | 수치구분(1:수치2:누적) | String | Y | 1 | - |
| `&nbsp;&nbsp;-gubun3` | 단위구분(1:일2:주3:월) | String | Y | 1 | - |
| `&nbsp;&nbsp;-from_date` | 시작날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-to_date` | 종료날짜 | String | Y | 8 | - |


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
| `t8462OutBlock` | t8462OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-tm_rng` | 시간대(D/N/U) | String | Y | 1 | - |
| `&nbsp;&nbsp;-fot_clsf_cd` | 선물옵션구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-bsc_asts_id` | 기초자산코드 | String | Y | 3 | - |
| `t8462OutBlock1` | t8462OutBlock1 | Object | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-sv_08` | 개인수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_17` | 외국인수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_18` | 기관계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_01` | 증권수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_03` | 투신수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_04` | 은행수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_02` | 보험수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_05` | 종금수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_06` | 기금수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_07` | 기타수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_15` | 선물수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_00` | 사모펀드수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_08` | 개인금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_17` | 외국인금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_18` | 기관계금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_01` | 증권금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_03` | 투신금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_04` | 은행금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_02` | 보험금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_05` | 종금금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_06` | 기금금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_07` | 기타금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_15` | 선물금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sa_00` | 사모펀드금액 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8462InBlock": {
    "tm_rng": "N",
    "fot_clsf_cd": "F",
    "bsc_asts_id": "K2I",
    "gubun2": "1",
    "gubun3": "1",
    "from_date": "20250609",
    "to_date": "20250610"
  }
}
```

### 응답 Example

```json
{
	"t8462OutBlock": {
		"tm_rng": "N",
		"fot_clsf_cd": "F",
		"bsc_asts_id": "K2I"
	},
	"t8462OutBlock1": [
		{
			"date": "20250610",
			"sv_08": -299,
			"sv_17": 335,
			"sv_18": -69,
			"sv_01": -69,
			"sv_03": 0,
			"sv_04": 0,
			"sv_02": 0,
			"sv_05": 0,
			"sv_06": 0,
			"sv_07": 33,
			"sv_15": 0,
			"sv_00": 0,
			"sa_08": "-287",
			"sa_17": "321",
			"sa_18": "-66",
			"sa_01": "-66",
			"sa_03": "0",
			"sa_04": "0",
			"sa_02": "0",
			"sa_05": "0",
			"sa_06": "0",
			"sa_07": "32",
			"sa_15": "0",
			"sa_00": "0"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t8463"></a>
## `t8463` KRX야간파생 투자자시간대별(API용)

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
| `t8463InBlock` | t8463InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-tm_rng` | 시간대(D/N/U) | String | Y | 1 | - |
| `&nbsp;&nbsp;-fot_clsf_cd` | 선물옵션구분 | String | Y | 1 | F : 선물<br/>C : 콜옵션<br/>P : 풋옵션<br/>S : 스프레드 |
| `&nbsp;&nbsp;-bsc_asts_id` | 기초자산코드 | String | Y | 3 | K2I : KP200선물/옵션<br/>MKI : 미니KP200선물/옵션<br/>KQI : 코스닥150선물/옵션<br/>WKM : 위클리옵션-월<br/>WKI : 위클리옵션-목<br/>BM3 : 국채3년선물<br/>BMA : 국채10년선물<br/>USD : 미국달러선물 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |
| `&nbsp;&nbsp;-bgubun` | 전일분 | String | Y | 1 | - |


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
| `t8463OutBlock` | t8463OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-tm_rng` | 시간대(D/N/U) | String | Y | 1 | - |
| `&nbsp;&nbsp;-fot_clsf_cd` | 선물옵션구분 | String | Y | 1 | - |
| `&nbsp;&nbsp;-indcode` | 개인투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-forcode` | 외국인투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-syscode` | 기관계투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-stocode` | 증권투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-invcode` | 투신투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-bancode` | 은행투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-inscode` | 보험투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-fincode` | 종금투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-moncode` | 기금투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-etccode` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-natcode` | 국가투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-pefcode` | 사모펀드투자자코드 | String | Y | 4 | - |
| `t8463OutBlock1` | t8463OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 일자 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 6 | - |
| `&nbsp;&nbsp;-datetime` | 일자시간 | String | Y | 14 | - |
| `&nbsp;&nbsp;-bsc_asts_id` | 기초자산코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-indmsvol` | 개인순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-indmsamt` | 개인순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-formsvol` | 외국인순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-formsamt` | 외국인순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sysmsvol` | 기관계순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-sysmsamt` | 기관계순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-stomsvol` | 증권순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-stomsamt` | 증권순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-invmsvol` | 투신순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-invmsamt` | 투신순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-banmsvol` | 은행순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-banmsamt` | 은행순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-insmsvol` | 보험순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-insmsamt` | 보험순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-finmsvol` | 종금순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-finmsamt` | 종금순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-monmsvol` | 기금순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-monmsamt` | 기금순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-etcmsvol` | 기타순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-etcmsamt` | 기타순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-natmsvol` | 국가순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-natmsamt` | 국가순매수거래대금 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-pefmsvol` | 사모펀드순매수거래량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-pefmsamt` | 사모펀드순매수거래대금 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t8463InBlock": {
    "tm_rng": "U",
    "fot_clsf_cd": "F",
    "bsc_asts_id": "K2I",
    "cnt": 10,
    "bgubun": "0"
  }
}
```

### 응답 Example

```json
{
	"t8463OutBlock": {
		"tm_rng": "U",
		"fot_clsf_cd": "F",
		"bsc_asts_id": "K2I",
		"indcode": "0008",
		"forcode": "0009",
		"syscode": "0018",
		"stocode": "0001",
		"invcode": "0003",
		"bancode": "0004",
		"inscode": "0002",
		"fincode": "0005",
		"moncode": "0006",
		"etccode": "0007",
		"natcode": "0011",
		"pefcode": "0000"
	},
	"t8463OutBlock1": [
		{
			"date": "20250609",
			"time": "194600",
			"datetime": "20250609",
			"indmsvol": -275,
			"indmsamt": "-263",
			"formsvol": 308,
			"formsamt": "295",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 33,
			"etcmsamt": "31",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194530",
			"datetime": "20250609",
			"indmsvol": -276,
			"indmsamt": "-264",
			"formsvol": 309,
			"formsamt": "296",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 33,
			"etcmsamt": "31",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194500",
			"datetime": "20250609",
			"indmsvol": -275,
			"indmsamt": "-263",
			"formsvol": 308,
			"formsamt": "295",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 33,
			"etcmsamt": "31",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194430",
			"datetime": "20250609",
			"indmsvol": -274,
			"indmsamt": "-262",
			"formsvol": 308,
			"formsamt": "295",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194400",
			"datetime": "20250609",
			"indmsvol": -274,
			"indmsamt": "-262",
			"formsvol": 308,
			"formsamt": "295",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194330",
			"datetime": "20250609",
			"indmsvol": -274,
			"indmsamt": "-262",
			"formsvol": 308,
			"formsamt": "295",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194300",
			"datetime": "20250609",
			"indmsvol": -274,
			"indmsamt": "-262",
			"formsvol": 308,
			"formsamt": "295",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194230",
			"datetime": "20250609",
			"indmsvol": -273,
			"indmsamt": "-261",
			"formsvol": 307,
			"formsamt": "294",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194200",
			"datetime": "20250609",
			"indmsvol": -273,
			"indmsamt": "-261",
			"formsvol": 307,
			"formsamt": "294",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		},
		{
			"date": "20250609",
			"time": "194130",
			"datetime": "20250609",
			"indmsvol": -273,
			"indmsamt": "-261",
			"formsvol": 307,
			"formsamt": "294",
			"sysmsvol": -66,
			"sysmsamt": "-63",
			"stomsvol": -66,
			"stomsamt": "-63",
			"invmsvol": 0,
			"invmsamt": "0",
			"banmsvol": 0,
			"banmsamt": "0",
			"insmsvol": 0,
			"insmsamt": "0",
			"finmsvol": 0,
			"finmsamt": "0",
			"monmsvol": 0,
			"monmsamt": "0",
			"etcmsvol": 32,
			"etcmsamt": "30",
			"natmsvol": 0,
			"natmsamt": "0",
			"pefmsvol": 0,
			"pefmsamt": "0"
		}
	],
	"rsp_cd": "00000",
	"rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```
