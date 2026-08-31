"""KOSPI200 대표 종목 리스트 + 일봉 데이터 수집"""

import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

# KOSPI200 전체 종목 리스트 (2026년 기준)
# 형식: "티커.KS" (KS = 한국거래소 KOSPI)
KOSPI200代表性 = [
    # 시가총액 상위 (대형주)
    "005930.KS",  # 삼성전자
    "000660.KS",  # SK하이닉스
    "035420.KS",  # NAVER
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "028260.KS",  # 삼성물산
    "012330.KS",  # 현대모비스
    "068270.KS",  # 셀트리온
    "105560.KS",  # KB금융
    "055550.KS",  # 신한지주
    "032640.KS",  # LG유플러스
    "000270.KS",  # 기아
    "015760.KS",  # 한국전력
    "010130.KS",  # 고려아연
    "000810.KS",  # 삼성화재
    "017670.KS",  # SK텔레콤
    "034730.KS",  # SK
    "009540.KS",  # HD현대중공업
    "000100.KS",  # 유한양행
    "090430.KS",  # 아모레퍼시픽
    "003550.KS",  # LG
    "024110.KS",  # 기업은행
    "005490.KS",  # POSCO홀딩스
    "051900.KS",  # LG생활건강
    "009160.KS",  # SIMPAC
    "035720.KS",  # 카카오
    "005380.KS",  # 현대차
    "016360.KS",  # 삼성증권
    "030210.KS",  # 다올투자증권
    "005830.KS",  # DB손해보험
    "032830.KS",  # 삼성생명
    "017900.KS",  # AUK
    "011150.KS",  # CJ씨푸드
    "071050.KS",  # 한국금융지주
    "005940.KS",  # NH투자증권
    "078930.KS",  # GS
    "023160.KS",  # 023160(삭제)
    # 중형주
    "009150.KS",  # 삼성전기
    "373220.KS",  # LG에너지솔루션
    "329180.KS",  # HD현대중공업
    "402340.KS",  # SK스퀘어
    "207940.KS",  # 삼성바이오로직스
    "032830.KS",  # 삼성생명
    "055550.KS",  # 신한지주
    "105560.KS",  # KB금융
    "086790.KS",  # 하나금융지주
    "032640.KS",  # LG유플러스
    "000660.KS",  # SK하이닉스
    "005930.KS",  # 삼성전자
    "005380.KS",  # 현대차
    "012330.KS",  # 현대모비스
    "000270.KS",  # 기아
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "035420.KS",  # NAVER
    "035720.KS",  # 카카오
    "017670.KS",  # SK텔레콤
    "009540.KS",  # HD현대중공업
    "000810.KS",  # 삼성화재
    "028260.KS",  # 삼성물산
    "010130.KS",  # 고려아연
    "015760.KS",  # 한국전력
    "090430.KS",  # 아모레퍼시픽
    "068270.KS",  # 셀트리온
    # 업종 대표
    "011210.KS",  # 현대위아
    "016360.KS",  # 삼성증권
    "030210.KS",  # 다올투자증권
    "034730.KS",  # SK
    "005830.KS",  # DB손해보험
    "003550.KS",  # LG
    "024110.KS",  # 기업은행
    "005490.KS",  # POSCO홀딩스
    "017900.KS",  # AUK
    "011150.KS",  # CJ씨푸드
    "071050.KS",  # 한국금융지주
    "005940.KS",  # NH투자증권
    "078930.KS",  # GS
    "000100.KS",  # 유한양행
    "009160.KS",  # SIMPAC
    "051900.KS",  # LG생활건강
    # 확장 종목
    "001450.KS",  # 현대해상
    "033230.KS",  # 033230(삭제)
    "018260.KS",  # 삼성SDS
    "006980.KS",  # 우성
    "036570.KS",  # NC
    "069960.KS",  # 현대백화점
    "099750.KS",  # 이지케어텍
    "003410.KS",  # LS
    "003490.KS",  # 대한항공
    "012270.KS",  # LS
    "009830.KS",  # 한화솔루션
    "060980.KS",  # HL홀딩스
    "032830.KS",  # 삼성생명
    "000060.KS",  # 대림산업
    "069620.KS",  # 대웅제약
    "023160.KS",  # 023160(삭제)
    # 추가 대형/중형주
    "005380.KS",  # 현대차
    "000270.KS",  # 기아
    "010130.KS",  # 고려아연
    "015760.KS",  # 한국전력
    "090430.KS",  # 아모레퍼시픽
    "068270.KS",  # 셀트리온
    "032640.KS",  # LG유플러스
    "009150.KS",  # 삼성전기
    "373220.KS",  # LG에너지솔루션
    "329180.KS",  # HD현대중공업
    "402340.KS",  # SK스퀘어
    "086790.KS",  # 하나금융지주
    "035420.KS",  # NAVER
    "035720.KS",  # 카카오
    "000660.KS",  # SK하이닉스
    "005930.KS",  # 삼성전자
    "005380.KS",  # 현대차
    "012330.KS",  # 현대모비스
    "000270.KS",  # 기아
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "017670.KS",  # SK텔레콤
    "009540.KS",  # HD현대중공업
    "000810.KS",  # 삼성화재
    "028260.KS",  # 삼성물산
    "010130.KS",  # 고려아연
    "015760.KS",  # 한국전력
    "090430.KS",  # 아모레퍼시픽
    "068270.KS",  # 셀트리온
    "105560.KS",  # KB금융
    "055550.KS",  # 신한지주
    "032640.KS",  # LG유플러스
    "034730.KS",  # SK
    "005830.KS",  # DB손해보험
    "003550.KS",  # LG
    "024110.KS",  # 기업은행
    "005490.KS",  # POSCO홀딩스
    "017900.KS",  # AUK
    "011150.KS",  # CJ씨푸드
    "071050.KS",  # 한국금융지주
    "005940.KS",  # NH투자증권
    "078930.KS",  # GS
    "000100.KS",  # 유한양행
    "009160.KS",  # SIMPAC
    "051900.KS",  # LG생활건강
    "016360.KS",  # 삼성증권
    "030210.KS",  # 다올투자증권
    # 신규 편입/확장 종목
    "001450.KS",  # 현대해상
    "033230.KS",  # 033230(삭제)
    "018260.KS",  # 삼성SDS
    "006980.KS",  # 우성
    "036570.KS",  # NC
    "069960.KS",  # 현대백화점
    "099750.KS",  # 이지케어텍
    "003410.KS",  # LS
    "003490.KS",  # 대한항공
    "012270.KS",  # LS
    "009830.KS",  # 한화솔루션
    "060980.KS",  # HL홀딩스
    "000060.KS",  # 대림산업
    "069620.KS",  # 대웅제약
    "023160.KS",  # 023160(삭제)
    # KOSPI200 신규 편입 종목 (2025-2026)
    "011210.KS",  # 현대위아
    "329180.KS",  # HD현대중공업
    "402340.KS",  # SK스퀘어
    "373220.KS",  # LG에너지솔루션
    "009150.KS",  # 삼성전기
    "086790.KS",  # 하나금융지주
    "035420.KS",  # NAVER
    "035720.KS",  # 카카오
    "000660.KS",  # SK하이닉스
    "005930.KS",  # 삼성전자
    "005380.KS",  # 현대차
    "012330.KS",  # 현대모비스
    "000270.KS",  # 기아
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "017670.KS",  # SK텔레콤
    "009540.KS",  # HD현대중공업
    "000810.KS",  # 삼성화재
    "028260.KS",  # 삼성물산
    "010130.KS",  # 고려아연
    "015760.KS",  # 한국전력
    "090430.KS",  # 아모레퍼시픽
    "068270.KS",  # 셀트리온
    "105560.KS",  # KB금융
    "055550.KS",  # 신한지주
    "032640.KS",  # LG유플러스
    "034730.KS",  # SK
    "005830.KS",  # DB손해보험
    "003550.KS",  # LG
    "024110.KS",  # 기업은행
    "005490.KS",  # POSCO홀딩스
    "017900.KS",  # AUK
    "011150.KS",  # CJ씨푸드
    "071050.KS",  # 한국금융지주
    "005940.KS",  # NH투자증권
    "078930.KS",  # GS
    "000100.KS",  # 유한양행
    "009160.KS",  # SIMPAC
    "051900.KS",  # LG생활건강
    "016360.KS",  # 삼성증권
    "030210.KS",  # 다올투자증권
    # 추가 KOSPI200 종목
    "001450.KS",  # 현대해상
    "033230.KS",  # 033230(삭제)
    "018260.KS",  # 삼성SDS
    "006980.KS",  # 우성
    "036570.KS",  # NC
    "069960.KS",  # 현대백화점
    "099750.KS",  # 이지케어텍
    "003410.KS",  # LS
    "003490.KS",  # 대한항공
    "012270.KS",  # LS
    "009830.KS",  # 한화솔루션
    "060980.KS",  # HL홀딩스
    "000060.KS",  # 대림산업
    "069620.KS",  # 대웅제약
    "023160.KS",  # 023160(삭제)
    # 2026년 KOSPI200 편입 종목 추가
    "011210.KS",  # 현대위아
    "329180.KS",  # HD현대중공업
    "402340.KS",  # SK스퀘어
    "373220.KS",  # LG에너지솔루션
    "009150.KS",  # 삼성전기
    "086790.KS",  # 하나금융지주
    "035420.KS",  # NAVER
    "035720.KS",  # 카카오
    "000660.KS",  # SK하이닉스
    "005930.KS",  # 삼성전자
    "005380.KS",  # 현대차
    "012330.KS",  # 현대모비스
    "000270.KS",  # 기아
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "017670.KS",  # SK텔레콤
    "009540.KS",  # HD현대중공업
    "000810.KS",  # 삼성화재
    "028260.KS",  # 삼성물산
    "010130.KS",  # 고려아연
    "015760.KS",  # 한국전력
    "090430.KS",  # 아모레퍼시픽
    "068270.KS",  # 셀트리온
    "105560.KS",  # KB금융
    "055550.KS",  # 신한지주
    "032640.KS",  # LG유플러스
    "034730.KS",  # SK
    "005830.KS",  # DB손해보험
    "003550.KS",  # LG
    "024110.KS",  # 기업은행
    "005490.KS",  # POSCO홀딩스
    "017900.KS",  # AUK
    "011150.KS",  # CJ씨푸드
    "071050.KS",  # 한국금융지주
    "005940.KS",  # NH투자증권
    "078930.KS",  # GS
    "000100.KS",  # 유한양행
    "009160.KS",  # SIMPAC
    "051900.KS",  # LG생활건강
    "016360.KS",  # 삼성증권
    "030210.KS",  # 다올투자증권
    # ===== 유니버스 확장 (KOSPI 대표주 추가) =====
    "066570.KS",  # LG전자
    "051600.KS",  # 한전KPS
    "096770.KS",  # SK이노베이션
    "010140.KS",  # 삼성중공업
    "042660.KS",  # 한화오션
    "012450.KS",  # 한화에어로스페이스
    "028050.KS",  # 삼성E&A
    "011200.KS",  # HMM
    "002380.KS",  # KCC
    "004020.KS",  # 현대제철
    "001040.KS",  # CJ
    "004990.KS",  # 롯데지주
    "034020.KS",  # 두산에너빌리티
    "241560.KS",  # 두산밥캣
    "006280.KS",  # GC녹십자
    "000150.KS",  # 두산
    "042700.KS",  # 한미반도체
    "000990.KS",  # DB하이텍
    "247540.KS",  # 에코프로비엠
    "086520.KS",  # 086520(삭제)
    "011070.KS",  # LG이노텍
    "035510.KS",  # 신세계인터내셔날
    "000070.KS",  # 삼양홀딩스
    "002790.KS",  # 아모레G
    "003090.KS",  # 대웅
    "011810.KS",  # STX
    "012510.KS",  # 더존비즈온
    "018880.KS",  # 한온시스템
    "021050.KS",  # Seowon
    "028100.KS",  # 동아지질
    "039490.KS",  # 키움증권
    "047040.KS",  # 대우건설
    "047810.KS",  # 한국항공우주
    "078000.KS",  # 텔코웨어
    "092730.KS",  # 네오팜
    "103140.KS",  # 풍산
    "105630.KS",  # 한세실업
    "161390.KS",  # 한국타이어
    "180640.KS",  # 한진칼
    "192080.KS",  # 더블유게임즈
    "097950.KS",  # CJ제일제당
    "298040.KS",  # 효성중공업
    "302440.KS",  # SK바이오사이언스
    "032980.KS",  # 032980(삭제)
    "091810.KS",  # 에어프레미아
    "023770.KS",  # 023770(삭제)
    "004310.KS",  # 현대약품
    "000720.KS",  # 현대건설
    "007070.KS",  # GS리테일
    "069500.KS",  # KODEX200
]

# 중복 제거 + 정렬
KOSPI200代表性 = sorted(set(KOSPI200代表性))

DATA_DIR = Path(__file__).parent


def fetch_stock_list() -> list[str]:
    """종목 리스트 반환 (향후 외부 소스에서 로드 가능)"""
    return KOSPI200代表性


def download_daily_data(
    tickers: list[str],
    start: str = "2024-08-01",
    end: str = "2026-08-27",
    output_dir: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """여러 종목의 일봉 데이터를 일괄 다운로드"""
    if output_dir is None:
        output_dir = DATA_DIR / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    results: dict[str, pd.DataFrame] = {}
    failed: list[str] = []

    print(f"총 {len(tickers)}개 종목 다운로드 시작...")
    print(f"기간: {start} ~ {end}")

    for i, ticker in enumerate(tickers):
        try:
            df = yf.download(
                ticker,
                start=start,
                end=end,
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if df is not None and not df.empty:
                # 멀티인덱스 컬럼 정리
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.index.name = "date"
                results[ticker] = df
                print(f"  [{i+1}/{len(tickers)}] {ticker}: {len(df)}일")
            else:
                failed.append(ticker)
                print(f"  [{i+1}/{len(tickers)}] {ticker}: 데이터 없음")
        except Exception as e:
            failed.append(ticker)
            print(f"  [{i+1}/{len(tickers)}] {ticker}: 에러 - {e}")

        # yfinance rate limit 준수
        if (i + 1) % 20 == 0:
            time.sleep(1)

    print(f"\n완료: 성공 {len(results)}개, 실패 {len(failed)}개")
    if failed:
        print(f"실패 종목: {failed}")

    return results


def save_data(data: dict[str, pd.DataFrame], output_dir: Path | None = None) -> Path:
    """수집된 데이터를 parquet 파일로 저장"""
    if output_dir is None:
        output_dir = DATA_DIR / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 개별 종목 파일
    for ticker, df in data.items():
        safe_name = ticker.replace(".", "_")
        df.to_parquet(output_dir / f"{safe_name}.parquet")

    # 병합 파일 (전체 유니버스)
    all_dfs = []
    for ticker, df in data.items():
        temp = df.copy()
        temp["ticker"] = ticker
        all_dfs.append(temp)

    if all_dfs:
        combined = pd.concat(all_dfs)
        combined.to_parquet(output_dir / "all_stocks.parquet")

    # 메타데이터
    meta = {
        "tickers": list(data.keys()),
        "count": len(data),
        "date_range": {
            "start": str(min(df.index.min() for df in data.values())),
            "end": str(max(df.index.max() for df in data.values())),
        },
    }
    (output_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    print(f"저장 완료: {output_dir}")
    return output_dir


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2020-08-01", help="수집 시작일")
    ap.add_argument("--end", default="2026-08-27", help="수집 종료일")
    args = ap.parse_args()

    tickers = fetch_stock_list()
    print(f"대상 종목: {len(tickers)}개")

    data = download_daily_data(tickers, start=args.start, end=args.end)
    save_data(data)
