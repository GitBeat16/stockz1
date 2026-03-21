"""
app.py
AI Candlestick Pattern Analyzer — Monaco Quant Terminal (v5.0)
----------------------------------------------------------------------
UI redesign only. All backend logic (data loading, pattern detection,
profitability analysis) is untouched.
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
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="StockZ | Neural Terminal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Professional Finance SVGs)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Hammer": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 4v16M8 4h8v4H8z"/></svg>',
    "Doji": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M4 12h16"/></svg>',
    "Bullish Engulfing": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="11" width="7" height="9" fill="currentColor"/><rect x="14" y="4" width="7" height="16" stroke="currentColor"/></svg>',
    "Bearish Engulfing": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="7" height="16" stroke="currentColor"/><rect x="14" y="11" width="7" height="9" fill="currentColor"/></svg>',
    "Shooting Star": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 4v16M8 16h8v4H8z"/></svg>',
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="4" y="4" width="16" height="16" rx="2" stroke="white" stroke-width="2"/><path d="M8 12L12 8L16 12" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "Pulse": '<svg width="12" height="12" viewBox="0 0 12 12"><circle cx="6" cy="6" r="4" fill="#10b981"><animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/></circle></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. SOPHISTICATED GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Styles ── */
html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', sans-serif;
    background-color: #050505;
    color: #a3a3a3;
}}

/* ── The "Ghost" Card ── */
.ghost-card {{
    background: #0a0a0a;
    border: 1px solid #171717;
    border-radius: 12px;
    padding: 1.25rem;
    transition: all 0.2s ease-in-out;
}}
.ghost-card:hover {{
    border-color: #262626;
    background: #0f0f0f;
}}

/* ── Sophisticated Typography ── */
.terminal-label {{
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #525252;
    margin-bottom: 0.25rem;
}}
.terminal-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: #ffffff;
}}
.ticker-title {{
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.03em;
}}

/* ── Live Pulse Header ── */
.live-status {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.7rem;
    color: #10b981;
    font-weight: 600;
    letter-spacing: 0.05em;
}}

/* ── Buttons & Inputs ── */
.stButton > button {{
    background: #ffffff !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    border: none !important;
    transition: opacity 0.2s;
}}
.stButton > button:hover {{ opacity: 0.8 !important; }}

/* ── Signal Badges ── */
.signal-box {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1rem;
    background: #0a0a0a;
    border: 1px solid #171717;
    border-radius: 8px;
    margin-bottom: 0.75rem;
}}
.signal-icon-bullish {{ color: #10b981; }}
.signal-icon-bearish {{ color: #ef4444; }}

</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="margin-bottom:2rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    
    ticker = st.text_input("SYMBOL", value="AAPL").upper().strip()
    period = st.selectbox("TIMEFRAME", options=["6mo", "1y", "2y", "5y"], index=1)
    
    st.markdown("---")
    analyse = st.button("RUN ANALYSIS")
    
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='terminal-label'>System Status</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='live-status'>{SVG_ICONS['Pulse']} ENGINE ONLINE</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
if not analyse:
    st.markdown("""
    <div style="height:60vh; display:flex; flex-direction:column; align-items:center; justify-content:center;">
        <div style="opacity:0.2; transform:scale(1.5)">💎</div>
        <p style="margin-top:2rem; font-size:0.8rem; letter-spacing:0.2em; color:#404040">AWAITING INSTRUMENT DEFINITION</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Backend Loading
with st.spinner(" "):
    df = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)
    if df.empty:
        st.error("SYMBOL NOT RESOLVED")
        st.stop()
    stats_all = analyse_all_patterns(df)
    latest_patterns = get_latest_patterns(df)

# Logic
latest_close = float(df["Close"].iloc[-1])
prev_close = float(df["Close"].iloc[-2])
daily_chg = (latest_close - prev_close) / prev_close * 100
primary = latest_patterns[0] if latest_patterns else None

# ── Header ──
st.markdown(f"""
    <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:3rem;'>
        <div>
            <div class='terminal-label'>{info['sector']} / {period.upper()}</div>
            <div class='ticker-title'>{info['name']} <span style='color:#525252; font-weight:400;'>{ticker}</span></div>
        </div>
        <div style='text-align:right'>
            <div class='terminal-label'>Current Price</div>
            <div class='terminal-value' style='font-size:2rem;'>{latest_close:,.2f}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ── KPI Grid ──
c1, c2, c3 = st.columns(3)
with c1:
    color = "#10b981" if daily_chg >= 0 else "#ef4444"
    st.markdown(f"""<div class="ghost-card">
        <div class="terminal-label">24h Variance</div>
        <div class="terminal-value" style="color:{color}">{'+' if daily_chg > 0 else ''}{daily_chg:.2f}%</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="ghost-card">
        <div class="terminal-label">Detected Pattern</div>
        <div class="terminal-value" style="color:#3b82f6">{primary if primary else "NONE"}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    acc = f"{stats_all[primary]['win_rate']}%" if primary else "N/A"
    st.markdown(f"""<div class="ghost-card">
        <div class="terminal-label">Pattern Reliability</div>
        <div class="terminal-value">{acc}</div>
    </div>""", unsafe_allow_html=True)

# ── Analysis Row ──
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
col_chart, col_signals = st.columns([2.5, 1])

with col_chart:
    st.markdown("<div class='terminal-label'>Institutional Price Action</div>", unsafe_allow_html=True)
    chart_df = df.tail(100)
    fig = go.Figure(data=[go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'], high=chart_df['High'],
        low=chart_df['Low'], close=chart_df['Close'],
        increasing_line_color='#ffffff', decreasing_line_color='#3b82f6', # Minimalist Monochrome
        increasing_fillcolor='#ffffff', decreasing_fillcolor='#3b82f6',
    )])
    fig.update_layout(
        template="plotly_dark", height=450,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(rangeslider_visible=False, showgrid=True, gridcolor='#171717', showspikes=True, spikemode='across', spikedash='dot', spikecolor='#404040'),
        yaxis=dict(side="right", gridcolor='#171717', showspikes=True, spikemode='across', spikedash='dot', spikecolor='#404040')
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_signals:
    st.markdown("<div class='terminal-label'>Pattern Registry</div>", unsafe_allow_html=True)
    if latest_patterns:
        for p in latest_patterns:
            sig = PATTERNS[p]["signal"]
            icon = SVG_ICONS.get(p, SVG_ICONS["Default"])
            color_class = f"signal-icon-{sig}"
            st.markdown(f"""
                <div class="signal-box">
                    <div class="{color_class}">{icon}</div>
                    <div>
                        <div style="font-size:0.8rem; font-weight:700; color:#fff">{p}</div>
                        <div style="font-size:0.6rem; color:#525252; text-transform:uppercase;">Confirmed Signal</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        explanation = build_ai_explanation(primary, stats_all[primary])
        st.markdown(f"""
            <div style='padding:1rem; border-top:1px solid #171717;'>
                <div class="terminal-label">AI Logic Feed</div>
                <div style="font-size:0.8rem; line-height:1.6; color:#737373;">{explanation}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='padding:2rem; text-align:center; font-size:0.7rem; color:#262626;'>NO ACTIVE PATTERNS</div>", unsafe_allow_html=True)

# ── Backtest Section ──
st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
st.markdown("<div class='terminal-label'>Backtest Statistics</div>", unsafe_allow_html=True)

for name, stats in stats_all.items():
    is_today = name in latest_patterns
    with st.expander(f"{name.upper()} DATA", expanded=is_today):
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"<div class='terminal-label'>Total Instances</div><div class='terminal-value' style='font-size:1.1rem'>{stats['occurrences']}</div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='terminal-label'>Historical Win Rate</div><div class='terminal-value' style='font-size:1.1rem; color:#10b981'>{stats['win_rate']}%</div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='terminal-label'>Mean 3D Return</div><div class='terminal-value' style='font-size:1.1rem'>{stats['avg_return']:.2f}%</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
    <div style='text-align:center; padding:6rem 0 2rem 0; color:#171717; font-size:0.6rem; letter-spacing:0.3em;'>
        MONACO QUANT v5.0 // NEURAL INTERFACE // 2026
    </div>
""", unsafe_allow_html=True)
