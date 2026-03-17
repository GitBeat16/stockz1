"""
data_loader.py
Fetches historical OHLCV stock data using yfinance.
"""

import yfinance as yf
import pandas as pd


def load_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Download historical OHLCV data for a given ticker.

    Args:
        ticker: Stock symbol, e.g. "AAPL"
        period: yfinance period string — "6mo", "1y", "2y", "5y"

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
        Returns an empty DataFrame if the ticker is invalid or data unavailable.
    """
    try:
        df = yf.download(ticker, period=period, auto_adjust=True, progress=False)

        if df.empty:
            return pd.DataFrame()

        # Flatten MultiIndex columns that yfinance sometimes returns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Keep only the columns we need
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)

        return df

    except Exception as e:
        print(f"[data_loader] Error fetching {ticker}: {e}")
        return pd.DataFrame()


def get_ticker_info(ticker: str) -> dict:
    """Return a small info dict (name, sector) for display purposes."""
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "currency": info.get("currency", "USD"),
        }
    except Exception:
        return {"name": ticker, "sector": "N/A", "currency": "USD"}
