"""
pattern_detector.py
Uses TA-Lib to detect candlestick patterns on OHLCV data.
"""

import pandas as pd
import numpy as np

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("[pattern_detector] TA-Lib not found — using fallback pure-Python detectors.")


# ── Pattern registry ────────────────────────────────────────────────────────
# Maps a human-readable name to:
#   - talib_func : the TA-Lib function name (CDL prefix)
#   - signal     : "bullish" or "bearish"
#   - description: one-liner meaning

PATTERNS = {
    "Hammer": {
        "talib_func": "CDLHAMMER",
        "signal": "bullish",
        "description": (
            "A small body near the top of the candle with a long lower shadow. "
            "Suggests buyers pushed prices back up after sellers drove them lower — "
            "often signals a potential bullish reversal at the end of a downtrend."
        ),
    },
    "Doji": {
        "talib_func": "CDLDOJI",
        "signal": "neutral",
        "description": (
            "Open and close prices are nearly equal, forming a cross shape. "
            "Reflects market indecision; the current trend may be losing momentum."
        ),
    },
    "Bullish Engulfing": {
        "talib_func": "CDLENGULFING",
        "signal": "bullish",
        "description": (
            "A large green candle completely engulfs the previous red candle. "
            "Indicates a strong shift from selling to buying pressure."
        ),
    },
    "Bearish Engulfing": {
        "talib_func": "CDLENGULFING",
        "signal": "bearish",
        "description": (
            "A large red candle completely engulfs the previous green candle. "
            "Indicates a strong shift from buying to selling pressure."
        ),
    },
    "Shooting Star": {
        "talib_func": "CDLSHOOTINGSTAR",
        "signal": "bearish",
        "description": (
            "A small body near the bottom with a long upper shadow. "
            "Buyers attempted to push prices higher but failed; "
            "often signals a bearish reversal near the top of an uptrend."
        ),
    },
}


# ── Pure-Python fallback detectors ──────────────────────────────────────────

def _body(df):
    return abs(df["Close"] - df["Open"])

def _range(df):
    return df["High"] - df["Low"]

def _fallback_hammer(df: pd.DataFrame) -> pd.Series:
    body = _body(df)
    rng  = _range(df)
    lower_shadow = df[["Open", "Close"]].min(axis=1) - df["Low"]
    upper_shadow = df["High"] - df[["Open", "Close"]].max(axis=1)
    signal = (
        (lower_shadow >= 2 * body) &
        (upper_shadow <= 0.1 * rng) &
        (rng > 0)
    )
    return signal.astype(int) * 100

def _fallback_doji(df: pd.DataFrame) -> pd.Series:
    body = _body(df)
    rng  = _range(df)
    signal = (rng > 0) & (body / rng < 0.1)
    return signal.astype(int) * 100

def _fallback_bullish_engulfing(df: pd.DataFrame) -> pd.Series:
    result = pd.Series(0, index=df.index)
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        if (prev["Close"] < prev["Open"] and        # prev red
            curr["Close"] > curr["Open"] and        # curr green
            curr["Open"]  < prev["Close"] and
            curr["Close"] > prev["Open"]):
            result.iloc[i] = 100
    return result

def _fallback_bearish_engulfing(df: pd.DataFrame) -> pd.Series:
    result = pd.Series(0, index=df.index)
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]
        if (prev["Close"] > prev["Open"] and        # prev green
            curr["Close"] < curr["Open"] and        # curr red
            curr["Open"]  > prev["Close"] and
            curr["Close"] < prev["Open"]):
            result.iloc[i] = -100
    return result

def _fallback_shooting_star(df: pd.DataFrame) -> pd.Series:
    body = _body(df)
    rng  = _range(df)
    upper_shadow = df["High"] - df[["Open", "Close"]].max(axis=1)
    lower_shadow = df[["Open", "Close"]].min(axis=1) - df["Low"]
    signal = (
        (upper_shadow >= 2 * body) &
        (lower_shadow <= 0.1 * rng) &
        (rng > 0)
    )
    return signal.astype(int) * -100   # bearish


FALLBACK_FUNCS = {
    "Hammer":            _fallback_hammer,
    "Doji":              _fallback_doji,
    "Bullish Engulfing": _fallback_bullish_engulfing,
    "Bearish Engulfing": _fallback_bearish_engulfing,
    "Shooting Star":     _fallback_shooting_star,
}


# ── Public API ───────────────────────────────────────────────────────────────

def detect_all_patterns(df: pd.DataFrame) -> dict[str, pd.Series]:
    """
    Run every pattern detector over df.

    Returns
    -------
    dict mapping pattern name → boolean Series (True where pattern fired)
    """
    o = df["Open"].values.astype(float)
    h = df["High"].values.astype(float)
    l = df["Low"].values.astype(float)
    c = df["Close"].values.astype(float)

    results: dict[str, pd.Series] = {}

    for name, meta in PATTERNS.items():
        func_name = meta["talib_func"]
        signal    = meta["signal"]

        if TALIB_AVAILABLE:
            raw = getattr(talib, func_name)(o, h, l, c)
            raw_series = pd.Series(raw, index=df.index)
        else:
            raw_series = FALLBACK_FUNCS[name](df)

        # TA-Lib returns >0 for bullish, <0 for bearish, 0 for no pattern.
        # For Engulfing we split on sign.
        if name == "Bullish Engulfing":
            fired = raw_series > 0
        elif name == "Bearish Engulfing":
            fired = raw_series < 0
        else:
            fired = raw_series != 0

        results[name] = fired

    return results


def get_latest_patterns(df: pd.DataFrame) -> list[str]:
    """Return the list of pattern names that fired on the most recent candle."""
    all_patterns = detect_all_patterns(df)
    latest_date  = df.index[-1]
    detected     = []
    for name, series in all_patterns.items():
        if series.loc[latest_date]:
            detected.append(name)
    return detected


def get_pattern_meta(name: str) -> dict:
    """Return description / signal metadata for a pattern name."""
    return PATTERNS.get(name, {})
