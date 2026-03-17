"""
pattern_analysis.py
Calculates historical profitability statistics for each detected pattern.
"""

import pandas as pd
import numpy as np
from pattern_detector import detect_all_patterns, get_pattern_meta


FORWARD_DAYS = 3   # how many trading days to look ahead


def analyse_pattern(
    df: pd.DataFrame,
    fired: pd.Series,
    signal: str,
) -> dict:
    """
    Given a boolean Series of pattern occurrences, calculate stats.

    For bullish patterns  → profitable if Close[+3] > Close[0]
    For bearish patterns  → profitable if Close[+3] < Close[0]
    For neutral (Doji)    → use absolute move > 0 as 'win'

    Returns dict with keys: occurrences, win_rate, avg_return, returns
    """
    close = df["Close"]
    indices = np.where(fired.values)[0]

    # Exclude the last FORWARD_DAYS rows — no future data to evaluate
    valid_indices = [i for i in indices if i + FORWARD_DAYS < len(df)]

    if not valid_indices:
        return {"occurrences": 0, "win_rate": 0.0, "avg_return": 0.0, "returns": []}

    returns = []
    for i in valid_indices:
        entry = float(close.iloc[i])
        exit_ = float(close.iloc[i + FORWARD_DAYS])
        pct   = (exit_ - entry) / entry * 100
        returns.append(pct)

    returns_arr = np.array(returns)

    if signal == "bullish":
        wins = np.sum(returns_arr > 0)
    elif signal == "bearish":
        wins = np.sum(returns_arr < 0)
    else:                           # neutral / doji
        wins = np.sum(np.abs(returns_arr) > 0.5)

    win_rate   = wins / len(returns_arr) * 100
    avg_return = float(np.mean(returns_arr))

    return {
        "occurrences": len(returns_arr),
        "win_rate":    round(win_rate, 1),
        "avg_return":  round(avg_return, 2),
        "returns":     returns_arr.tolist(),
    }


def analyse_all_patterns(df: pd.DataFrame) -> dict[str, dict]:
    """
    Run detect + analyse for every pattern.

    Returns
    -------
    dict: pattern_name → {occurrences, win_rate, avg_return, returns, signal, description, fired_series}
    """
    all_fired = detect_all_patterns(df)
    results   = {}

    for name, fired in all_fired.items():
        meta  = get_pattern_meta(name)
        stats = analyse_pattern(df, fired, meta.get("signal", "neutral"))

        results[name] = {
            **stats,
            "signal":      meta.get("signal", "neutral"),
            "description": meta.get("description", ""),
            "fired_series": fired,      # keep for chart highlighting
        }

    return results


def build_ai_explanation(name: str, stats: dict) -> str:
    """
    Compose a plain-English explanation of the pattern and its statistics.
    This function is intentionally simple — no ML, just template logic.
    """
    signal      = stats["signal"].capitalize()
    occ         = stats["occurrences"]
    win_rate    = stats["win_rate"]
    avg_ret     = stats["avg_return"]
    description = stats["description"]

    # Qualitative verdict
    if occ == 0:
        verdict = "No historical data available for this pattern in the selected period."
        suggestion = ""
    else:
        if win_rate >= 60:
            strength = "a strong"
        elif win_rate >= 50:
            strength = "a moderate"
        else:
            strength = "a weak or unreliable"

        direction = stats["signal"]
        ret_str   = f"+{avg_ret:.2f}%" if avg_ret >= 0 else f"{avg_ret:.2f}%"

        verdict = (
            f"Historical results: Occurrences: {occ} | "
            f"Win rate: {win_rate}% | "
            f"Average return after {FORWARD_DAYS} days: {ret_str}"
        )
        suggestion = (
            f"This pattern historically shows {strength} {direction} bias "
            f"with an average {FORWARD_DAYS}-day return of {ret_str}."
        )

    lines = [
        f"Pattern detected: {name}",
        f"Signal: {signal}",
        f"Meaning: {description}",
        verdict,
    ]
    if suggestion:
        lines.append(f"Suggestion: {suggestion}")

    return "\n".join(lines)
