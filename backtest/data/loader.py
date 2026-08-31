"""일봉 데이터 로더 — backtest/data/raw/*.parquet"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "raw"


def ticker_to_file(ticker: str) -> str:
    """'005930.KS' -> '005930_KS.parquet'"""
    return ticker.replace(".", "_") + ".parquet"


def file_to_ticker(filename: str) -> str:
    """'005930_KS.parquet' -> '005930.KS'"""
    stem = Path(filename).stem
    return stem.rsplit("_", 1)[0] + "." + stem.rsplit("_", 1)[1]


def list_tickers(data_dir: Path | None = None) -> list[str]:
    """사용 가능한 종목 티커 목록"""
    data_dir = data_dir or DATA_DIR
    tickers = []
    for f in sorted(data_dir.glob("*_KS.parquet")):
        tickers.append(file_to_ticker(f.name))
    return tickers


def load_ticker(ticker: str, data_dir: Path | None = None) -> pd.DataFrame:
    """개별 종목 일봉 로드. df.index=DatetimeIndex, 컬럼 OHLCV."""
    data_dir = data_dir or DATA_DIR
    df = pd.read_parquet(data_dir / ticker_to_file(ticker))
    if df.index.name != "date" and not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df = df.sort_index()
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    return df


def load_all(
    tickers: list[str] | None = None, data_dir: Path | None = None
) -> dict[str, pd.DataFrame]:
    """여러 종목 일괄 로드 {ticker: df}"""
    data_dir = data_dir or DATA_DIR
    tickers = tickers or list_tickers(data_dir)
    return {t: load_ticker(t, data_dir) for t in tickers}