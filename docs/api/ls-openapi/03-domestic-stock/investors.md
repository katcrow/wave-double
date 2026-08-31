# [주식] 투자자

> LS증권 OPEN API 정의서 · 그룹: **주식** · [포털 원문](https://openapi.ls-sec.co.kr/apiservice?group_id=73142d9f-1983-48d2-8543-89b75535d34c&api_id=c148a42f-51a7-4446-b6df-10d6056dd75b)

## 기본 정보

| 항목 | 값 |
|---|---|
| API ID | `c148a42f-51a7-4446-b6df-10d6056dd75b` |
| Protocol | REST |
| Method | POST |
| Domain | `https://openapi.ls-sec.co.kr:8080` |
| URL | `/stock/investor` |
| Format | JSON |
| Content-Type | application/json; charset=UTF-8 |
| 과금 | 무과금 |
| 설명 | 투자자별 매매추이를 확인할 수 있는 서비스를 호출하여 이용가능합니다. |

## TR 목록 (7건)

| TR명 | TR코드 | 초당 전송 건수 | 개인 초당 제한 | 법인 초당 제한 |
|---|---|---|---|---|
| 투자자별종합 | [t1601](investors.md#tr-t1601) | 2 | 2 | 5 |
| 시간대별투자자매매추이 | [t1602](investors.md#tr-t1602) | 1 | 1 | 3 |
| 시간대별투자자매매추이상세 | [t1603](investors.md#tr-t1603) | 1 | 1 | 3 |
| 투자자매매종합1 | [t1615](investors.md#tr-t1615) | 1 | 1 | 3 |
| 투자자매매종합2 | [t1617](investors.md#tr-t1617) | 1 | 1 | 3 |
| 업종별분별투자자매매동향(챠트용) | [t1621](investors.md#tr-t1621) | 1 | 1 | 3 |
| 투자자매매종합(챠트) | [t1664](investors.md#tr-t1664) | 1 | 1 | 3 |

---

<a id="tr-t1601"></a>
## `t1601` 투자자별종합

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
| `t1601InBlock` | t1601InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 주식금액수량구분1 | String | Y | 1 | 1:수량<br/>2:금액 |
| `&nbsp;&nbsp;-gubun2` | 옵션금액수량구분2 | String | Y | 1 | 1:수량<br/>2:금액 |
| `&nbsp;&nbsp;-gubun3` | 금액단위 | String | Y | 1 | 사용안함 |
| `&nbsp;&nbsp;-gubun4` | 선물금액수량구분4 | String | Y | 1 | 1:수량<br/>2:금액 |
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
| `t1601OutBlock1` | t1601OutBlock1 | Object | Y | - | - |
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
| `&nbsp;&nbsp;-jjcode_11` | 국가투자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |
| `t1601OutBlock2` | t1601OutBlock2 | Object | Y | - | - |
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
| `&nbsp;&nbsp;-jjcode_11` | 국가투자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |
| `t1601OutBlock3` | t1601OutBlock3 | Object | Y | - | - |
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
| `&nbsp;&nbsp;-jjcode_11` | 국가투자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |
| `t1601OutBlock4` | t1601OutBlock4 | Object | Y | - | - |
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
| `&nbsp;&nbsp;-jjcode_11` | 국가투자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |
| `t1601OutBlock5` | t1601OutBlock5 | Object | Y | - | - |
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
| `&nbsp;&nbsp;-jjcode_11` | 국가투자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |
| `t1601OutBlock6` | t1601OutBlock6 | Object | Y | - | - |
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
| `&nbsp;&nbsp;-jjcode_11` | 국가투자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_11` | 국가매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_11` | 국가매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_11` | 국가증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_11` | 국가순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_07` | 기타투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_07` | 기타매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_07` | 기타매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_07` | 기타증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-jjcode_00` | 사모펀드투자자코드 | String | Y | 4 | - |
| `&nbsp;&nbsp;-ms_00` | 사모펀드매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_00` | 사모펀드매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-rate_00` | 사모펀드증감 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume_00` | 사모펀드순매수 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1601InBlock" : {
    "gubun1" : "1",
    "gubun2" : "1",
    "gubun3" : "",
    "gubun4" : "1"
  }
}
```

### 응답 Example

```json
{
    "t1601OutBlock5": {
        "md_06": 0,
        "md_07": 22126,
        "md_04": 30,
        "md_05": 458,
        "md_02": 0,
        "md_03": 1393,
        "md_00": 0,
        "md_01": 100419,
        "ms_04": 1,
        "ms_03": 148,
        "ms_06": 0,
        "ms_05": 161,
        "ms_00": 0,
        "ms_02": 0,
        "ms_01": 69447,
        "svolume_00": 0,
        "svolume_01": -30972,
        "svolume_04": -29,
        "svolume_05": -297,
        "svolume_02": 0,
        "svolume_03": -1245,
        "svolume_08": 13846,
        "svolume_06": 0,
        "tjjcode_08": "",
        "svolume_07": 6849,
        "md_08": 180607,
        "rate_00": 0,
        "rate_11": 3,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 69757,
        "rate_07": 10,
        "rate_08": 108,
        "rate_05": 0,
        "rate_06": 0,
        "rate_03": 0,
        "rate_04": 0,
        "rate_01": -421,
        "rate_02": 0,
        "md_17": 267628,
        "jjcode_03": "",
        "md_18": 102300,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 279476,
        "ms_11": 0,
        "jjcode_07": "",
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 194453,
        "ms_07": 28975,
        "rate_18": -421,
        "svolume_17": 11848,
        "rate_17": 303,
        "svolume_18": -32543
    },
    "rsp_cd": "00000",
    "t1601OutBlock6": {
        "md_06": 17,
        "md_07": 903,
        "md_04": 1359,
        "md_05": 57,
        "md_02": 371,
        "md_03": 206,
        "md_00": 240,
        "md_01": 14796,
        "ms_04": 655,
        "ms_03": 23,
        "ms_06": 0,
        "ms_05": 0,
        "ms_00": 379,
        "ms_02": 285,
        "ms_01": 13553,
        "svolume_00": 139,
        "svolume_01": -1243,
        "svolume_04": -704,
        "svolume_05": -56,
        "svolume_02": -86,
        "svolume_03": -183,
        "svolume_08": 1558,
        "svolume_06": -17,
        "tjjcode_08": "",
        "svolume_07": 135,
        "md_08": 39162,
        "rate_00": -1,
        "rate_11": 44,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 14896,
        "rate_07": -10,
        "rate_08": 14,
        "rate_05": 0,
        "rate_06": 0,
        "rate_03": 0,
        "rate_04": 0,
        "rate_01": -1,
        "rate_02": 2,
        "md_17": 28922,
        "jjcode_03": "",
        "md_18": 17046,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 29379,
        "ms_11": 0,
        "jjcode_07": "",
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 40720,
        "ms_07": 1038,
        "rate_18": 0,
        "svolume_17": 457,
        "rate_17": -4,
        "svolume_18": -2150
    },
    "t1601OutBlock1": {
        "md_06": 3978,
        "md_07": 983,
        "md_04": 17,
        "md_05": 61,
        "md_02": 161,
        "md_03": 433,
        "md_00": 338,
        "md_01": 2210,
        "ms_04": 8,
        "ms_03": 1240,
        "ms_06": 5928,
        "ms_05": 99,
        "ms_00": 912,
        "ms_02": 291,
        "ms_01": 3769,
        "svolume_00": 574,
        "svolume_01": 1558,
        "svolume_04": -9,
        "svolume_05": 38,
        "svolume_02": 131,
        "svolume_03": 807,
        "svolume_08": -8398,
        "svolume_06": 1950,
        "tjjcode_08": "",
        "svolume_07": -213,
        "md_08": 213937,
        "rate_00": 8,
        "rate_11": 36,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 12247,
        "rate_07": -7,
        "rate_08": -42,
        "rate_05": 1,
        "rate_06": 26,
        "rate_03": 7,
        "rate_04": 0,
        "rate_01": 25,
        "rate_02": 2,
        "md_17": 39269,
        "jjcode_03": "",
        "md_18": 7198,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 42832,
        "ms_11": 0,
        "jjcode_07": "",
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 205539,
        "ms_07": 770,
        "rate_18": 68,
        "svolume_17": 3563,
        "rate_17": -18,
        "svolume_18": 5049
    },
    "t1601OutBlock2": {
        "md_06": 123,
        "md_07": 3908,
        "md_04": 2,
        "md_05": 58,
        "md_02": 53,
        "md_03": 462,
        "md_00": 753,
        "md_01": 3691,
        "ms_04": 3,
        "ms_03": 432,
        "ms_06": 151,
        "ms_05": 8,
        "ms_00": 451,
        "ms_02": 52,
        "ms_01": 2986,
        "svolume_00": -302,
        "svolume_01": -705,
        "svolume_04": 1,
        "svolume_05": -51,
        "svolume_02": -1,
        "svolume_03": -30,
        "svolume_08": 2252,
        "svolume_06": 27,
        "tjjcode_08": "",
        "svolume_07": -2304,
        "md_08": 348693,
        "rate_00": -2,
        "rate_11": 34,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 4082,
        "rate_07": -24,
        "rate_08": -135,
        "rate_05": -2,
        "rate_06": -2,
        "rate_03": -1,
        "rate_04": 0,
        "rate_01": -10,
        "rate_02": 0,
        "md_17": 49328,
        "jjcode_03": "",
        "md_18": 5142,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 50440,
        "ms_11": 0,
        "jjcode_07": "",
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 350945,
        "ms_07": 1605,
        "rate_18": -16,
        "svolume_17": 1112,
        "rate_17": 175,
        "svolume_18": -1060
    },
    "t1601OutBlock3": {
        "md_06": 350,
        "md_07": 1173,
        "md_04": 126,
        "md_05": 1149,
        "md_02": 2651,
        "md_03": 9069,
        "md_00": 0,
        "md_01": 29110,
        "ms_04": 201,
        "ms_03": 8441,
        "ms_06": 139,
        "ms_05": 1072,
        "ms_00": 0,
        "ms_02": 2645,
        "ms_01": 28417,
        "svolume_00": 0,
        "svolume_01": -693,
        "svolume_04": 75,
        "svolume_05": -77,
        "svolume_02": -6,
        "svolume_03": -628,
        "svolume_08": -26,
        "svolume_06": -211,
        "tjjcode_08": "",
        "svolume_07": -139,
        "md_08": 14359,
        "rate_00": 0,
        "rate_11": 126,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 40915,
        "rate_07": 0,
        "rate_08": 32,
        "rate_05": 0,
        "rate_06": 0,
        "rate_03": 0,
        "rate_04": 0,
        "rate_01": 4,
        "rate_02": 0,
        "md_17": 96807,
        "jjcode_03": "",
        "md_18": 42455,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 98512,
        "ms_11": 0,
        "jjcode_07": "",
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 14333,
        "ms_07": 1034,
        "rate_18": 4,
        "svolume_17": 1705,
        "rate_17": -36,
        "svolume_18": -1540
    },
    "t1601OutBlock4": {
        "md_06": 0,
        "md_07": 33614,
        "md_04": 2,
        "md_05": 136,
        "md_02": 0,
        "md_03": 408,
        "md_00": 0,
        "md_01": 92343,
        "ms_04": 0,
        "ms_03": 671,
        "ms_06": 0,
        "ms_05": 431,
        "ms_00": 0,
        "ms_02": 0,
        "ms_01": 69755,
        "svolume_00": 0,
        "svolume_01": -22588,
        "svolume_04": -2,
        "svolume_05": 295,
        "svolume_02": 0,
        "svolume_03": 263,
        "svolume_08": 12622,
        "svolume_06": 0,
        "tjjcode_08": "",
        "svolume_07": 2296,
        "md_08": 170493,
        "rate_00": 0,
        "rate_11": 0,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 70857,
        "rate_07": -3,
        "rate_08": 55,
        "rate_05": 0,
        "rate_06": 0,
        "rate_03": 0,
        "rate_04": 0,
        "rate_01": -24,
        "rate_02": 0,
        "md_17": 285250,
        "jjcode_03": "",
        "md_18": 92889,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 292364,
        "ms_11": 0,
        "jjcode_07": "",
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 183115,
        "ms_07": 35910,
        "rate_18": -24,
        "svolume_17": 7114,
        "rate_17": -28,
        "svolume_18": -22032
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1602"></a>
## `t1602` 시간대별투자자매매추이

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
| `t1602InBlock` | t1602InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-market` | 시장구분 | String | Y | 1 | 1@코스피<br/>2@KP200<br/>3@코스닥<br/>4@선물<br/>5@콜옵션<br/>6@풋옵션<br/>7@ELW<br/>8@ETF |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | 001:코스피<br/>101:KP200<br/>301:코스닥<br/>900:선 물<br/>700:콜옵션<br/>800:풋옵션<br/>550:ELW<br/>560:ETF |
| `&nbsp;&nbsp;-gubun1` | 수량구분 | String | Y | 1 | 1:수량<br/>2:금액 |
| `&nbsp;&nbsp;-gubun2` | 전일분구분 | String | Y | 1 | 0:금일<br/>1:전일 |
| `&nbsp;&nbsp;-cts_time` | CTSTIME | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | 사용안함 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 4 | - |
| `&nbsp;&nbsp;-gubun3` | 직전대비구분(C:직전대비) | String | Y | 1 | - |
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
| `t1602OutBlock` | t1602OutBlock | Object | Y | - | - |
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
| `&nbsp;&nbsp;-ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |
| `t1602OutBlock1` | t1602OutBlock1 | Object Array | Y | - | - |
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
  "t1602InBlock" : {
    "market" : "1",
    "upcode" :"001",
    "gubun1" : "1",
    "gubun2" : "0",
    "cts_time" : " ",
    "cts_idx" : 1,
    "cnt" : 1,
    "gubun3" : "C"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1602OutBlock1": [
        {
            "sv_18": 0,
            "sv_07": 0,
            "sv_17": 0,
            "sv_06": 0,
            "sv_05": 0,
            "sv_04": 0,
            "sv_08": 0,
            "sv_03": 0,
            "sv_02": 0,
            "sv_01": 0,
            "sv_11": 0,
            "sv_00": 0,
            "time": "10263000"
        }
    ],
    "t1602OutBlock": {
        "md_06": 3978,
        "md_07": 983,
        "md_04": 17,
        "md_05": 61,
        "md_02": 161,
        "md_03": 433,
        "md_00": 338,
        "md_01": 2210,
        "ms_04": 8,
        "ms_03": 1240,
        "ms_06": 5928,
        "ms_05": 99,
        "ms_00": 912,
        "ms_02": 291,
        "ms_01": 3769,
        "svolume_00": 574,
        "svolume_01": 1558,
        "svolume_04": -9,
        "svolume_05": 38,
        "svolume_02": 131,
        "svolume_03": 807,
        "svolume_08": -8398,
        "svolume_06": 1950,
        "tjjcode_08": "",
        "svolume_07": -213,
        "md_08": 213937,
        "rate_00": 0,
        "rate_11": 0,
        "jjcode_11": "",
        "jjcode_18": "",
        "jjcode_17": "",
        "ms_18": 12247,
        "rate_07": 0,
        "rate_08": 0,
        "rate_05": 0,
        "rate_06": 0,
        "rate_03": 0,
        "rate_04": 0,
        "rate_01": 0,
        "cts_time": "10260000",
        "rate_02": 0,
        "md_17": 39269,
        "jjcode_03": "",
        "md_18": 7198,
        "jjcode_02": "",
        "jjcode_05": "",
        "jjcode_04": "",
        "jjcode_01": "",
        "md_11": 0,
        "jjcode_00": "",
        "ms_17": 42832,
        "jjcode_07": "",
        "ms_11": 0,
        "jjcode_06": "",
        "svolume_11": 0,
        "ms_08": 205539,
        "ms_07": 770,
        "rate_18": 0,
        "svolume_17": 3563,
        "rate_17": 0,
        "svolume_18": 5049
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1603"></a>
## `t1603` 시간대별투자자매매추이상세

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
| `t1603InBlock` | t1603InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-market` | 시장구분 | String | Y | 1 | 1:코스피<br/>2:코스닥<br/>3:선물<br/>4:콜옵션<br/>5:풋옵션<br/>6:ELW<br/>7:ETF |
| `&nbsp;&nbsp;-gubun1` | 투자자구분 | String | Y | 1 | 1:개인<br/>2:외인<br/>3:기관계<br/>4:증권<br/>5:투신<br/>6:은행<br/>7:보험<br/>8:종금<br/>9:기금<br/>A:국가<br/>B:기타<br/>C:사모펀드 |
| `&nbsp;&nbsp;-gubun2` | 전일분구분 | String | Y | 1 | 0:당일<br/>1:전일 |
| `&nbsp;&nbsp;-cts_time` | CTSTIME | String | Y | 8 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_time 값으로 설정 |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | 처음 조회시는 Space<br/>연속 조회시에 이전 조회한 OutBlock의 cts_idx 값으로 설정 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | 020 |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
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
| `t1603OutBlock` | t1603OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_idx` | CTSIDX | Number | Y | 4 | - |
| `&nbsp;&nbsp;-cts_time` | CTSTIME | String | Y | 8 | - |
| `&nbsp;&nbsp;-ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |
| `t1603OutBlock1` | t1603OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tjjcode` | 투자자구분 | String | Y | 4 | - |
| `&nbsp;&nbsp;-msvolume` | 매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-mdvolume` | 매도수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-msvalue` | 매수금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-mdvalue` | 매도금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-svolume` | 순매수수량 | Number | Y | 8 | - |
| `&nbsp;&nbsp;-svalue` | 순매수금액 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1603InBlock" : {
    "market" : "1",
    "gubun1" : "1",
    "gubun2" : "0",
    "cts_time" : " ",
    "cts_idx" : 0,
    "cnt" : 20,
    "upcode" : "001"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1603OutBlock1": [
        {
            "mdvalue": 24968,
            "msvolume": 205539,
            "svalue": -1499,
            "tjjcode": "",
            "msvalue": 23469,
            "svolume": -8398,
            "time": "10263000",
            "mdvolume": 213937
        },
        {
            "mdvalue": 23853,
            "msvolume": 194136,
            "svalue": -1540,
            "tjjcode": "",
            "msvalue": 22314,
            "svolume": -8068,
            "time": "10170000",
            "mdvolume": 202205
        }
    ],
    "t1603OutBlock": {
        "cts_idx": 0,
        "cts_time": "10163000"
    },
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1615"></a>
## `t1615` 투자자매매종합1

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
| `t1615InBlock` | t1615InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 주식구분 | String | Y | 1 | 1:수량<br/>2:금액 |
| `&nbsp;&nbsp;-gubun2` | 옵션구분 | String | Y | 1 | 1:수량<br/>2:금액 |
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
| `t1615OutBlock` | t1615OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-dwvolume` | 위탁매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-dwvalue` | 위탁매도금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-djvolume` | 자기매도수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-djvalue` | 자기매도금액 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sum_volume` | 합계수량 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sum_value` | 합계금액 | Number | Y | 12 | - |
| `t1615OutBlock1` | t1615OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-hname` | 시장명 | String | Y | 20 | - |
| `&nbsp;&nbsp;-sv_08` | 개인 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_17` | 외국인 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_18` | 기관계 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_07` | 증권 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1615InBlock" : {
    "gubun1" : "1",
    "gubun2" : "1"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1615OutBlock1": [
        {
            "sv_18": 5049,
            "sv_07": -213,
            "sv_17": 3563,
            "hname": "코스피",
            "sv_08": -8398
        },
        {
            "sv_18": -1060,
            "sv_07": -2304,
            "sv_17": 1112,
            "hname": "코스닥",
            "sv_08": 2252
        },
        {
            "sv_18": -1540,
            "sv_07": -139,
            "sv_17": 1705,
            "hname": "선  물",
            "sv_08": -26
        },
        {
            "sv_18": -22032,
            "sv_07": 2296,
            "sv_17": 7114,
            "hname": "콜옵션",
            "sv_08": 12622
        },
        {
            "sv_18": -32543,
            "sv_07": 6849,
            "sv_17": 11848,
            "hname": "풋옵션",
            "sv_08": 13846
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1615OutBlock": {
        "sum_volume": 3381,
        "dwvalue": 27034,
        "djvolume": 15,
        "djvalue": 862,
        "dwvolume": 3366,
        "sum_value": 27896
    }
}
```

---

<a id="tr-t1617"></a>
## `t1617` 투자자매매종합2

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
| `t1617InBlock` | t1617InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-gubun1` | 시장구분 | String | Y | 1 | 1:코스피<br/>2:코스닥<br/>3:선물<br/>4:콜옵션<br/>5:풋옵션<br/>6:주식선물<br/>7:변동성<br/>8:M선물<br/>9:M콜옵션<br/>0:M풋옵션 |
| `&nbsp;&nbsp;-gubun2` | 수량금액구분(1:수량2:금액) | String | Y | 1 | - |
| `&nbsp;&nbsp;-gubun3` | 일자구분(1:시간대별2:일별) | String | Y | 1 | - |
| `&nbsp;&nbsp;-cts_date` | CTSDATE(연속키값-일자) | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | CTSTIME(연속키값-시간) | String | Y | 8 | - |
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
| `t1617OutBlock` | t1617OutBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-cts_date` | CTSDATE | String | Y | 8 | - |
| `&nbsp;&nbsp;-cts_time` | CTSTIME | String | Y | 8 | - |
| `&nbsp;&nbsp;-ms_08` | 개인매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_08` | 개인매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_08` | 개인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ms_17` | 외국인매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_17` | 외국인매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_17` | 외국인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ms_18` | 기관계매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_18` | 기관계매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_18` | 기관계순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-ms_01` | 증권매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-md_01` | 증권매도 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_01` | 증권순매수 | Number | Y | 12 | - |
| `t1617OutBlock1` | t1617OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-date` | 날짜 | String | Y | 8 | - |
| `&nbsp;&nbsp;-time` | 시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-sv_08` | 개인 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_17` | 외국인 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_18` | 기관계 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-sv_01` | 증권 | Number | Y | 12 | - |


### 요청 Example

```json
{
  "t1617InBlock" : {
    "gubun1" : "1",
    "gubun2" : "1",
    "gubun3" : "1",
    "cts_date" : " ",
    "cts_time" : " "
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "t1617OutBlock": {
        "md_17": 154,
        "md_18": 51,
        "cts_date": "",
        "md_01": 2,
        "sv_18": -2,
        "sv_17": 2,
        "ms_17": 156,
        "sv_08": 0,
        "ms_01": 12,
        "ms_08": 33,
        "ms_18": 49,
        "sv_01": 9,
        "md_08": 33,
        "cts_time": "16360000"
    },
    "t1617OutBlock1": [
        {
            "date": "",
            "sv_01": 9,
            "sv_18": -2,
            "sv_17": 2,
            "time": "16453000",
            "sv_08": 0
        },
        {
            "date": "",
            "sv_01": 9,
            "sv_18": -2,
            "sv_17": 2,
            "time": "16360000",
            "sv_08": 0
        }
    ],
    "rsp_msg": "정상적으로 조회가 완료되었습니다."
}
```

---

<a id="tr-t1621"></a>
## `t1621` 업종별분별투자자매매동향(챠트용)

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
| `t1621InBlock` | t1621InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-upcode` | 업종코드 | String | Y | 3 | - |
| `&nbsp;&nbsp;-nmin` | N분 | Object | Y | 2 | - |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |
| `&nbsp;&nbsp;-bgubun` | 전일분 | String | Y | 1 | 0:당일<br/>1:전일 |
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
| `t1621OutBlock` | t1621OutBlock | Object | Y | - | - |
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
| `&nbsp;&nbsp;-ex_upcode` | 거래소별업종코드 | String | Y | 4 | - |
| `t1621OutBlock1` | t1621OutBlock1 | Object Array | Y | - | - |
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
  "t1621InBlock" : {
    "upcode" : "001",
    "nmin" : 0,
    "cnt" : 20,
    "bgubun" : "0"
  }
}
```

### 응답 Example

```json
{
    "rsp_cd": "00000",
    "rsp_msg": "정상적으로 조회가 완료되었습니다.",
    "t1621OutBlock": {
        "pefcode": "0000",
        "etccode": "0007",
        "natcode": "0011",
        "forcode": "0017",
        "invcode": "0003",
        "syscode": "0018",
        "stocode": "0001",
        "moncode": "0006",
        "bancode": "0004",
        "inscode": "0002",
        "fincode": "0005",
        "jisucd": "001",
        "indcode": "0008",
        "jisunm": "종       합"
    },
    "t1621OutBlock1": [
         {
            "date": "20230619",
            "indmsamt": "1",
            "upclose": "252618.00",
            "etcmsamt": "2",
            "insmsvol": 1,
            "natmsamt": "0",
            "invmsvol": 0,
            "monmsamt": "-5",
            "natmsvol": 0,
            "invmsamt": "0",
            "indmsvol": 0,
            "formsvol": 2,
            "insmsamt": "0",
            "datetime": "20230619",
            "finmsvol": 0,
            "etcmsvol": 0,
            "sysmsamt": "-3",
            "pefmsvol": -11,
            "banmsvol": 8,
            "stomsvol": 9,
            "finmsamt": "0",
            "banmsamt": "3",
            "sysmsvol": -2,
            "pefmsamt": "-4",
            "stomsamt": "3",
            "formsamt": "1",
            "upvalue": "22263",
            "time": "160500",
            "upvolume": "1042",
            "upcvolume": 201,
            "monmsvol": -9
        }
    ]
}
```

---

<a id="tr-t1664"></a>
## `t1664` 투자자매매종합(챠트)

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
| `t1664InBlock` | t1664InBlock | Object | Y | - | - |
| `&nbsp;&nbsp;-mgubun` | 시장구분 | String | Y | 1 | 1@코스피<br/>2@코스닥<br/>3@선 물<br/>4@콜옵션<br/>5@풋옵션 |
| `&nbsp;&nbsp;-vagubun` | 금액수량구분 | String | Y | 1 | 1:수량<br/>2:금액 |
| `&nbsp;&nbsp;-bdgubun` | 시간일별구분 | String | Y | 1 | 1:시간별<br/>2:일별 |
| `&nbsp;&nbsp;-cnt` | 조회건수 | Object | Y | 3 | - |
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
| `t1664OutBlock1` | t1664OutBlock1 | Object Array | Y | - | - |
| `&nbsp;&nbsp;-dt` | 일자시간 | String | Y | 8 | - |
| `&nbsp;&nbsp;-tjj01` | 증권순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj02` | 보험순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj03` | 투신순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj04` | 은행순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj05` | 종금순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj06` | 기금순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj07` | 기타순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj08` | 개인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj17` | 외국인순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-tjj18` | 기관순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-cha` | 차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-bicha` | 비차익순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-totcha` | 종합순매수 | Number | Y | 12 | - |
| `&nbsp;&nbsp;-basis` | 베이시스 | Number | Y | 6.2 | - |


### 요청 Example

```json
{
  "t1664InBlock" : {
    "mgubun" : "1",
    "vagubun" : "1",
    "bgubun" : "2",
    "cnt" : 2
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
