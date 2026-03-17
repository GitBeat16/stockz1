# 🕯️ Candlestick Pattern Analyser

An educational Streamlit app that detects candlestick patterns in stock data
and shows whether those patterns have historically been profitable.

---

## Project Structure

```
candlestick_ai/
├── app.py               # Streamlit UI
├── data_loader.py       # Yahoo Finance data fetching
├── pattern_detector.py  # TA-Lib pattern detection (with pure-Python fallback)
├── pattern_analysis.py  # Historical profitability stats
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1 — Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows cmd
```

### 2 — Install TA-Lib C library (required before pip install)

TA-Lib has a C dependency that must be installed first.

**macOS**
```bash
brew install ta-lib
```

**Ubuntu / Debian**
```bash
sudo apt-get install libta-lib-dev
```

**Windows**
Download the pre-built wheel from:
https://github.com/cgohlke/talib-build/releases
Then install with:
```bash
pip install TA_Lib‑0.4.xx‑cpXX‑cpXX‑win_amd64.whl
```

### 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

> **No TA-Lib?** The app includes pure-Python fallback detectors for all five
> patterns. Everything still works; you'll just see a console notice.

### 4 — Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## How It Works

| Module | Responsibility |
|---|---|
| `data_loader.py` | Downloads OHLCV data via `yfinance` |
| `pattern_detector.py` | Detects 5 patterns using TA-Lib (or fallback) |
| `pattern_analysis.py` | Calculates win rate, avg return, builds explanation |
| `app.py` | Streamlit UI + Plotly candlestick chart |

### Patterns Detected
- **Hammer** — bullish reversal signal
- **Doji** — indecision / neutral
- **Bullish Engulfing** — strong bullish reversal
- **Bearish Engulfing** — strong bearish reversal
- **Shooting Star** — bearish reversal signal

### Profitability Metric
For every pattern occurrence, the app calculates the **3-day forward return**:

```
return = (Close[day+3] - Close[day]) / Close[day] * 100
```

- **Bullish patterns** → win if return > 0
- **Bearish patterns** → win if return < 0
- **Neutral (Doji)**   → win if |return| > 0.5%

---

## Example Output

```
Pattern detected: Hammer
Signal: Bullish
Meaning: A small body near the top of the candle with a long lower shadow.
         Suggests buyers pushed prices back up after sellers drove them lower.
Historical results: Occurrences: 84 | Win rate: 59% | Avg return after 3 days: +1.1%
Suggestion: This pattern historically shows a moderate bullish bias with an
            average 3-day return of +1.1%.
```

---

## Notes

- This is **not** a trading system. It is an educational tool.
- Pattern profitability varies by stock, sector, and time period.
- A win rate above 50% does not guarantee future profits.
- Always combine technical analysis with fundamental research.
