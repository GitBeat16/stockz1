"""
app.py
AI Candlestick Pattern Analyzer — Professional Financial Dashboard UI
----------------------------------------------------------------------
UI redesign only. All backend logic (data loading, pattern detection,
profitability analysis) is untouched and imported from:
  - data_loader.py
  - pattern_detector.py
  - pattern_analysis.py

Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Backend imports (unchanged) ──────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation


# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
#    layout="wide" gives us the full browser width — essential for a dashboard
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Candlestick Pattern Analyzer",
    page_icon="📊",
    layout="wide",                      # <-- required for dashboard feel
    initial_sidebar_state="expanded",
)


# ════════════════════════════════════════════════════════════════════════════
# 2. GLOBAL CSS
#    We inject a small stylesheet to:
#      - Set a dark background matching a trading terminal
#      - Style "dashboard cards" with rounded borders & subtle gradient tops
#      - Style pattern badges, section headings, and the explanation box
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Font (Inter — clean, modern, finance-friendly) ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base background & text ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f19;
    color: #d1d5db;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0f1623;
    border-right: 1px solid #1e2d40;
}
[data-testid="stSidebar"] * { color: #9ca3af; }
[data-testid="stSidebar"] h2 { color: #f9fafb !important; }

/* ── Main content padding ── */
[data-testid="block-container"] {
    padding: 2rem 2.5rem 3rem 2.5rem;
}

/* ── Dashboard header ── */
.dash-header {
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid #1e2d40;
    margin-bottom: 1.5rem;
}
.dash-header h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #f9fafb;
    margin: 0 0 0.3rem 0;
}
.dash-header p {
    font-size: 0.875rem;
    color: #6b7280;
    margin: 0;
}

/* ── Stock title & subtitle ── */
.stock-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #f9fafb;
    margin-bottom: 0.1rem;
}
.stock-sub {
    font-size: 0.8rem;
    color: #6b7280;
    margin-bottom: 1.25rem;
}

/* ══ DASHBOARD METRIC CARDS ══
   These give the "rounded card with darker background" look requested.
   The ::before pseudo-element adds a coloured top border stripe.        */
.metric-card {
    background: #111827;
    border: 1px solid #1e2d40;
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
/* Default top stripe — blue */
.metric-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #2563eb, #0ea5e9);
    border-radius: 10px 10px 0 0;
}
/* Coloured stripe variants */
.metric-card.bullish-card::before { background: linear-gradient(90deg, #059669, #34d399); }
.metric-card.bearish-card::before { background: linear-gradient(90deg, #dc2626, #f87171); }
.metric-card.neutral-card::before { background: linear-gradient(90deg, #b45309, #fbbf24); }

.metric-label {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b7280;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #f9fafb;
    line-height: 1.1;
}
.metric-sub {
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.35rem;
}

/* ── Colour helpers ── */
.bullish { color: #34d399; }
.bearish { color: #f87171; }
.neutral { color: #fbbf24; }

/* ── Section headings (divider labels) ── */
.section-heading {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4b5563;
    margin: 1.75rem 0 0.75rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e2d40;
}

/* ── Pattern badges (pill-shaped coloured labels) ── */
.badge-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.25rem; }
.pattern-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
}
.badge-bullish { background: #052e16; color: #34d399; border: 1px solid #065f46; }
.badge-bearish { background: #2d0a0a; color: #f87171; border: 1px solid #7f1d1d; }
.badge-neutral { background: #1c1408; color: #fbbf24; border: 1px solid #78350f; }
.badge-none    { color: #4b5563; font-size: 0.85rem; font-style: italic; }

/* ── AI explanation box ── */
.explanation-box {
    background: #111827;
    border: 1px solid #1e2d40;
    border-left: 3px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    font-size: 0.85rem;
    line-height: 1.75;
    white-space: pre-wrap;
    color: #d1d5db;
}

/* ── Expander styling ── */
div[data-testid="stExpander"] {
    background: #111827;
    border: 1px solid #1e2d40 !important;
    border-radius: 8px;
}

/* ── Analyse button ── */
.stButton > button {
    background: #1d4ed8;
    color: #fff;
    border: none;
    border-radius: 7px;
    font-weight: 600;
    font-size: 0.875rem;
    padding: 0.55rem 1.5rem;
    width: 100%;
    transition: background 0.15s;
}
.stButton > button:hover { background: #2563eb; }

/* ── Footer ── */
.dash-footer {
    font-size: 0.75rem;
    color: #374151;
    text-align: center;
    padding-top: 1.5rem;
    border-top: 1px solid #1e2d40;
    margin-top: 2rem;
}

/* ── Streamlit heading overrides ── */
h1, h2, h3, h4 { color: #f9fafb !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 3. SIDEBAR — user controls
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Pattern Analyzer")
    st.markdown("<hr style='border-color:#1e2d40;margin:0.75rem 0'>", unsafe_allow_html=True)

    # Stock ticker input
    ticker = st.text_input(
        "Stock Ticker",
        value="AAPL",
        help="Enter any Yahoo Finance symbol, e.g. AAPL, MSFT, TSLA, ^GSPC",
    ).upper().strip()

    # Time range selector
    period = st.selectbox(
        "Time Range",
        options=["6mo", "1y", "2y", "5y"],
        index=1,
        format_func=lambda x: {
            "6mo": "6 Months",
            "1y":  "1 Year",
            "2y":  "2 Years",
            "5y":  "5 Years",
        }[x],
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    analyse = st.button("🔍  Run Analysis")

    # Pattern legend in sidebar
    st.markdown("<hr style='border-color:#1e2d40;margin:1rem 0 0.75rem 0'>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.72rem;color:#4b5563;font-weight:600;"
        "text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem'>"
        "Patterns Tracked</div>",
        unsafe_allow_html=True,
    )
    legend = {
        "Hammer":            ("#34d399", "↑ Bullish"),
        "Doji":              ("#fbbf24", "— Neutral"),
        "Bullish Engulfing": ("#34d399", "↑ Bullish"),
        "Bearish Engulfing": ("#f87171", "↓ Bearish"),
        "Shooting Star":     ("#f87171", "↓ Bearish"),
    }
    for p_name, (p_color, p_label) in legend.items():
        st.markdown(
            f"<div style='font-size:0.8rem;padding:3px 0;color:{p_color}'>"
            f"{p_label} &nbsp;·&nbsp; {p_name}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<hr style='border-color:#1e2d40;margin:1rem 0 0.5rem 0'>", unsafe_allow_html=True)
    st.caption("Data: Yahoo Finance · Patterns: TA-Lib")


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER A — Dashboard header (always visible)
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown("""
    <div class="dash-header">
        <h1>📊 AI Candlestick Pattern Analyzer</h1>
        <p>
            Identify classic candlestick patterns in historical stock data and evaluate
            how profitable those signals have been over the selected time period.
            Patterns are detected using TA-Lib; profitability is measured as the
            3-day forward price change after each signal.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Show a friendly placeholder if no analysis has been run yet ──────────────
if not analyse:
    st.markdown("""
    <div style="background:#111827;border:1px dashed #1e2d40;border-radius:10px;
                padding:3rem;text-align:center;margin-top:2rem;">
        <div style="font-size:2.5rem;margin-bottom:0.75rem">🕯️</div>
        <div style="font-size:1rem;font-weight:600;color:#f9fafb;margin-bottom:0.4rem">
            Ready to analyze
        </div>
        <div style="font-size:0.875rem;color:#4b5563">
            Enter a stock ticker in the sidebar and click
            <strong style="color:#9ca3af">Run Analysis</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# LOAD DATA  (calls backend — no changes here)
# ════════════════════════════════════════════════════════════════════════════
with st.spinner(f"Fetching data for {ticker} …"):
    df   = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)

if df.empty:
    st.error(f"❌  Could not load data for **{ticker}**. Check the symbol and try again.")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# RUN ANALYSIS  (calls backend — no changes here)
# ════════════════════════════════════════════════════════════════════════════
with st.spinner("Detecting patterns and calculating historical statistics …"):
    stats_all       = analyse_all_patterns(df)
    latest_patterns = get_latest_patterns(df)


# ── Convenience variables derived from data ──────────────────────────────────
latest_close = float(df["Close"].iloc[-1])
prev_close   = float(df["Close"].iloc[-2])
daily_chg    = (latest_close - prev_close) / prev_close * 100
chg_color    = "bullish" if daily_chg >= 0 else "bearish"
chg_arrow    = "▲"       if daily_chg >= 0 else "▼"

# Primary pattern = the first one detected today (used for headline KPIs)
primary = latest_patterns[0] if latest_patterns else None


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER B — Stock identity + price KPI row
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(
        f"<div class='stock-title'>{info['name']} &nbsp;"
        f"<code style='font-size:0.9rem'>{ticker}</code></div>"
        f"<div class='stock-sub'>{info['sector']} · {info['currency']} · {period} lookback</div>",
        unsafe_allow_html=True,
    )

    # ── METRICS ROW (4 cards) ─────────────────────────────────────────────
    # Card 1: Latest close price
    # Card 2: Daily % change (green/red)
    # Card 3: Detected pattern win rate   ← key requirement
    # Card 4: Average 3-day return         ← key requirement
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Latest Close</div>
            <div class="metric-value">{latest_close:.2f}</div>
            <div class="metric-sub">{info['currency']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        cc = "bullish-card" if daily_chg >= 0 else "bearish-card"
        st.markdown(f"""
        <div class="metric-card {cc}">
            <div class="metric-label">Daily Change</div>
            <div class="metric-value {chg_color}">{chg_arrow} {abs(daily_chg):.2f}%</div>
            <div class="metric-sub">vs prior close</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        # Show win rate of today's primary pattern, or a placeholder
        if primary:
            p_wr     = stats_all[primary]["win_rate"]
            p_sig    = stats_all[primary]["signal"]
            wr_cls   = p_sig                           # bullish / bearish / neutral
            card_cls = f"{p_sig}-card"
            wr_disp  = f"{p_wr}%"
        else:
            wr_cls   = "neutral"
            card_cls = ""
            wr_disp  = "—"

        st.markdown(f"""
        <div class="metric-card {card_cls}">
            <div class="metric-label">Detected Pattern</div>
            <div class="metric-value {wr_cls}">{primary if primary else "None"}</div>
            <div class="metric-sub">historical win rate: {wr_disp}</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        if primary:
            p_ar   = stats_all[primary]["avg_return"]
            ar_str = f"+{p_ar:.2f}%" if p_ar >= 0 else f"{p_ar:.2f}%"
            ar_cls = "bullish" if p_ar >= 0 else "bearish"
        else:
            ar_str = "—"
            ar_cls = "neutral"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Return (3 Days)</div>
            <div class="metric-value {ar_cls}">{ar_str}</div>
            <div class="metric-sub">{primary if primary else "No pattern today"}</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER C — Today's signals (pattern badges)
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(
        "<div class='section-heading'>Today's Signals</div>",
        unsafe_allow_html=True,
    )

    if latest_patterns:
        html = "<div class='badge-row'>"
        for p in latest_patterns:
            sig   = PATTERNS[p]["signal"]
            arrow = "↑" if sig == "bullish" else ("↓" if sig == "bearish" else "—")
            html += f"<span class='pattern-badge badge-{sig}'>{arrow}&nbsp;{p}</span>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(
            "<span class='badge-none'>No candlestick patterns detected on the most recent candle.</span>",
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER D — Candlestick chart
#   - Plotly dark theme  (template="plotly_dark")
#   - Range slider disabled  (rangeslider_visible=False)
#   - Full width  (use_container_width=True)
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(
        "<div class='section-heading'>Price Chart — Last 120 Candles</div>",
        unsafe_allow_html=True,
    )

    chart_df = df.tail(120)

    fig = go.Figure()

    # Main candlestick trace
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df["Open"],
        high=chart_df["High"],
        low=chart_df["Low"],
        close=chart_df["Close"],
        name="Price",
        increasing_line_color="#34d399",   # green for up candles
        decreasing_line_color="#f87171",   # red  for down candles
        increasing_fillcolor="#34d399",
        decreasing_fillcolor="#f87171",
    ))

    # Overlay triangle markers wherever each pattern was detected
    MARKER_COLORS = {
        "Hammer":            "#60a5fa",
        "Doji":              "#fbbf24",
        "Bullish Engulfing": "#34d399",
        "Bearish Engulfing": "#f87171",
        "Shooting Star":     "#c084fc",
    }
    for name, stats in stats_all.items():
        fired_in_window = stats["fired_series"].loc[chart_df.index]
        hit_dates = fired_in_window[fired_in_window].index
        if len(hit_dates) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=hit_dates,
            y=chart_df.loc[hit_dates, "Low"] * 0.993,
            mode="markers",
            marker=dict(
                symbol="triangle-up",
                size=11,
                color=MARKER_COLORS.get(name, "#ffffff"),
                line=dict(color="#0b0f19", width=1),
            ),
            name=name,
            hovertemplate=f"<b>{name}</b><br>%{{x}}<extra></extra>",
        ))

    # Chart layout — dark theme, no range slider
    fig.update_layout(
        template="plotly_dark",                # dark Plotly theme
        height=500,
        plot_bgcolor="#0f1623",
        paper_bgcolor="#0f1623",
        font=dict(family="Inter, sans-serif", color="#9ca3af", size=12),
        xaxis=dict(
            gridcolor="#1e2d40",
            showgrid=True,
            rangeslider_visible=False,         # range slider disabled
            tickfont=dict(color="#4b5563"),
        ),
        yaxis=dict(
            gridcolor="#1e2d40",
            showgrid=True,
            tickfont=dict(color="#4b5563"),
            side="right",                      # price axis on the right (like trading platforms)
        ),
        legend=dict(
            bgcolor="#111827",
            bordercolor="#1e2d40",
            borderwidth=1,
            font=dict(size=11),
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=0, r=0, t=36, b=0),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2d40", font_size=12),
    )

    st.plotly_chart(fig, use_container_width=True)   # full width


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER E — Pattern explanation for today's primary signal
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    if primary:
        st.markdown(
            "<div class='section-heading'>Pattern Explanation</div>",
            unsafe_allow_html=True,
        )
        p_stats     = stats_all[primary]
        explanation = build_ai_explanation(primary, p_stats)
        p_sig       = p_stats["signal"]
        sig_color   = {"bullish": "#34d399", "bearish": "#f87171", "neutral": "#fbbf24"}[p_sig]

        st.markdown(
            f"<div style='font-size:0.75rem;font-weight:600;color:{sig_color};"
            f"text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem'>"
            f"● {p_sig.capitalize()} signal — {primary}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="explanation-box">{explanation}</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER F — Historical statistics (one expandable section per pattern)
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(
        "<div class='section-heading'>Historical Statistics by Pattern</div>",
        unsafe_allow_html=True,
    )

    for name, stats in stats_all.items():
        sig    = stats["signal"]
        occ    = stats["occurrences"]
        wr     = stats["win_rate"]
        ar     = stats["avg_return"]
        ar_str = f"+{ar:.2f}%" if ar >= 0 else f"{ar:.2f}%"
        ar_cls = "bullish" if ar >= 0 else "bearish"
        wr_cls = "bullish" if wr >= 55 else ("bearish" if wr < 45 else "neutral")
        dot    = {"bullish": "🟢", "bearish": "🔴", "neutral": "🟡"}[sig]

        # Auto-expand the expander for patterns detected today
        is_today = name in latest_patterns

        with st.expander(
            f"{dot}  {name}" + ("  ← detected today" if is_today else ""),
            expanded=is_today,
        ):
            # 3 metric cards inside the expander
            sc1, sc2, sc3 = st.columns(3)

            with sc1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Occurrences</div>
                    <div class="metric-value">{occ}</div>
                    <div class="metric-sub">in selected period</div>
                </div>""", unsafe_allow_html=True)

            with sc2:
                wc = "bullish-card" if wr >= 55 else ("bearish-card" if wr < 45 else "neutral-card")
                st.markdown(f"""
                <div class="metric-card {wc}">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value {wr_cls}">{wr}%</div>
                    <div class="metric-sub">of trades profitable</div>
                </div>""", unsafe_allow_html=True)

            with sc3:
                ac = "bullish-card" if ar >= 0 else "bearish-card"
                st.markdown(f"""
                <div class="metric-card {ac}">
                    <div class="metric-label">Avg Return (3 Days)</div>
                    <div class="metric-value {ar_cls}">{ar_str}</div>
                    <div class="metric-sub">mean forward return</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Plain-English explanation (generated by pattern_analysis.py)
            explanation = build_ai_explanation(name, stats)
            st.markdown(
                f'<div class="explanation-box">{explanation}</div>',
                unsafe_allow_html=True,
            )

            # ── Detailed statistics (nested expandable section) ──────────
            if stats["returns"] and len(stats["returns"]) >= 5:
                with st.expander("📊  Detailed return distribution", expanded=False):
                    ret_series = pd.Series(stats["returns"])

                    # 4 summary stat mini-cards
                    d1, d2, d3, d4 = st.columns(4)
                    detail_stats = [
                        ("Median Return", f"{ret_series.median():+.2f}%"),
                        ("Std Deviation", f"{ret_series.std():.2f}%"),
                        ("Best Trade",    f"{ret_series.max():+.2f}%"),
                        ("Worst Trade",   f"{ret_series.min():+.2f}%"),
                    ]
                    for col, (label, val) in zip([d1, d2, d3, d4], detail_stats):
                        with col:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">{label}</div>
                                <div class="metric-value" style="font-size:1.2rem">{val}</div>
                            </div>""", unsafe_allow_html=True)

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                    # Return distribution histogram
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=ret_series,
                        nbinsx=20,
                        marker_color="#2563eb",
                        marker_line_color="#1e2d40",
                        marker_line_width=1,
                        opacity=0.85,
                        name="3-day returns",
                    ))
                    # Vertical breakeven line
                    fig_hist.add_vline(
                        x=0,
                        line_color="#f87171",
                        line_dash="dash",
                        line_width=1.5,
                        annotation_text=" breakeven",
                        annotation_font_color="#6b7280",
                        annotation_font_size=11,
                    )
                    fig_hist.update_layout(
                        template="plotly_dark",
                        height=220,
                        plot_bgcolor="#0f1623",
                        paper_bgcolor="#0f1623",
                        font=dict(family="Inter", color="#6b7280", size=11),
                        xaxis=dict(
                            title="3-day return (%)",
                            gridcolor="#1e2d40",
                            tickfont=dict(color="#4b5563"),
                        ),
                        yaxis=dict(
                            title="Count",
                            gridcolor="#1e2d40",
                            tickfont=dict(color="#4b5563"),
                        ),
                        margin=dict(l=0, r=0, t=10, b=0),
                        showlegend=False,
                        bargap=0.05,
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='dash-footer'>"
    "⚠️ <strong>Educational use only.</strong> "
    "Past pattern performance does not guarantee future results. "
    "This tool is designed to help students explore technical analysis concepts."
    "</div>",
    unsafe_allow_html=True,
)
