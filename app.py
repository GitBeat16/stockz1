"""
app.py
AI Candlestick Pattern Analyzer — Ultra-Modern Finance UI
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
    page_title="Terminal | AI Pattern Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ════════════════════════════════════════════════════════════════════════════
# 2. ENHANCED GLOBAL CSS (Animations & Vector Aesthetics)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* ── Base Theme ── */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #05070a;
    color: #e2e8f0;
}

/* ── Vector Art Logo Placeholder ── */
.vector-logo {
    width: 45px;
    height: 45px;
    background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M13 21h8c.6 0 1-.4 1-1V4c0-.6-.4-1-1-1h-8v18zm-2 0V3H3c-.6 0-1 .4-1 1v16c0 .6.4 1 1 1h8z'/%3E%3C/svg%3E") no-repeat center;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M13 21h8c.6 0 1-.4 1-1V4c0-.6-.4-1-1-1h-8v18zm-2 0V3H3c-.6 0-1 .4-1 1v16c0 .6.4 1 1 1h8z'/%3E%3C/svg%3E") no-repeat center;
    margin-bottom: 10px;
}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {
    background-color: #090c14;
    border-right: 1px solid #1e293b;
}

/* ── Animations ── */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.stContainer {
    animation: fadeIn 0.6s ease-out forwards;
}

/* ── Dashboard Metric Cards ── */
.metric-card {
    background: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}
.metric-card:hover {
    border-color: #3b82f6;
    transform: translateY(-4px);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 0.5rem;
}

/* ── Typography & Headings ── */
.dash-header h1 {
    background: linear-gradient(90deg, #fff, #94a3b8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    letter-spacing: -0.02em;
}

.section-heading {
    font-size: 0.85rem;
    font-weight: 700;
    color: #3b82f6;
    margin: 2rem 0 1rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-heading::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e293b, transparent);
}

/* ── Pattern Badges ── */
.pattern-badge {
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid transparent;
}
.badge-bullish { background: rgba(16, 185, 129, 0.1); color: #10b981; border-color: rgba(16, 185, 129, 0.2); }
.badge-bearish { background: rgba(239, 68, 68, 0.1); color: #ef4444; border-color: rgba(239, 68, 68, 0.2); }
.badge-neutral { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border-color: rgba(245, 158, 11, 0.2); }

/* ── Form Inputs ── */
.stTextInput>div>div>input, .stSelectbox>div>div>div {
    background-color: #0f172a !important;
    border-color: #1e293b !important;
    border-radius: 8px !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 3. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="vector-logo"></div>', unsafe_allow_html=True)
    st.markdown("## Terminal v2.0")
    
    ticker = st.text_input("SYMBOL", value="AAPL").upper().strip()
    period = st.selectbox("TIMEFRAME", options=["6mo", "1y", "2y", "5y"], index=1)
    
    st.markdown("---")
    analyse = st.button("RUN QUANT ANALYSIS")

    # Vector-style legend
    st.markdown("<br><div style='font-size:0.7rem; color:#64748b'>CORE SIGNALS</div>", unsafe_allow_html=True)
    legend = {
        "Bullish": "#10b981",
        "Bearish": "#ef4444",
        "Neutral": "#f59e0b"
    }
    for label, color in legend.items():
        st.markdown(f"""
            <div style='display:flex; align-items:center; gap:8px; margin-bottom:4px;'>
                <div style='width:8px; height:8px; border-radius:50%; background:{color}'></div>
                <div style='font-size:0.8rem; color:#94a3b8'>{label}</div>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER A — Header
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown("""
    <div class="dash-header">
        <h1>AI Quant Pattern Engine</h1>
        <p style="color:#64748b; font-size:0.9rem; max-width:800px;">
            Institutional-grade candlestick recognition and backtested profitability analysis. 
            Utilizing TA-Lib and 3-day forward return metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

if not analyse:
    st.markdown("""
    <div style="background:rgba(15, 23, 42, 0.5); border:1px solid #1e293b; border-radius:20px;
                padding:5rem; text-align:center; margin-top:2rem;">
        <div style="font-size:3rem; margin-bottom:1rem; opacity:0.5;">📡</div>
        <h3 style="margin-bottom:0.5rem">Awaiting Input</h3>
        <p style="color:#64748b">Select a ticker to initialize the neural pattern detector.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING (Backend calls - Unchanged)
# ════════════════════════════════════════════════════════════════════════════
with st.spinner("Synchronizing with market data..."):
    df = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)

if df.empty:
    st.error("Invalid Ticker Configuration.")
    st.stop()

stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)

# Logic Prep
latest_close = float(df["Close"].iloc[-1])
prev_close = float(df["Close"].iloc[-2])
daily_chg = (latest_close - prev_close) / prev_close * 100
primary = latest_patterns[0] if latest_patterns else None


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER B — Top KPI Row
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    st.markdown(f"""
        <div style='margin-bottom:1.5rem'>
            <span style='font-size:1.5rem; font-weight:700; color:#fff'>{info['name']}</span>
            <span style='color:#3b82f6; font-family:JetBrains Mono; margin-left:10px'>{ticker}</span>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Price</div>
            <div class="metric-value">{latest_close:,.2f} <span style='font-size:0.8rem; color:#64748b'>{info['currency']}</span></div>
        </div>""", unsafe_allow_html=True)
        
    with c2:
        color = "#10b981" if daily_chg >= 0 else "#ef4444"
        arrow = "↑" if daily_chg >= 0 else "↓"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Daily Shift</div>
            <div class="metric-value" style="color:{color}">{arrow} {abs(daily_chg):.2f}%</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        p_name = primary if primary else "NO SIGNAL"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Primary Pattern</div>
            <div class="metric-value" style="font-size:1.2rem; color:#3b82f6">{p_name}</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        wr = f"{stats_all[primary]['win_rate']}%" if primary else "N/A"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value">{wr}</div>
        </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER C — Active Signals & Chart
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>Market Intelligence Terminal</div>", unsafe_allow_html=True)

col_chart, col_signals = st.columns([2.5, 1])

with col_signals:
    st.markdown("<div style='font-size:0.7rem; color:#64748b; margin-bottom:10px'>ACTIVE CANDLE SIGNALS</div>", unsafe_allow_html=True)
    if latest_patterns:
        for p in latest_patterns:
            sig = PATTERNS[p]["signal"]
            st.markdown(f"<div class='pattern-badge badge-{sig}'>{p} Detected</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='color:#475569; font-style:italic; font-size:0.8rem'>Scanning for new patterns...</div>", unsafe_allow_html=True)
    
    if primary:
        st.markdown("<br><div style='font-size:0.7rem; color:#64748b; margin-bottom:10px'>AI INTERPRETATION</div>", unsafe_allow_html=True)
        explanation = build_ai_explanation(primary, stats_all[primary])
        st.markdown(f"""<div style='background:rgba(30,41,59,0.5); padding:1rem; border-radius:12px; font-size:0.8rem; line-height:1.5; border:1px solid #334155'>
            {explanation}
        </div>""", unsafe_allow_html=True)

with col_chart:
    chart_df = df.tail(120)
    fig = go.Figure(data=[go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'], high=chart_df['High'],
        low=chart_df['Low'], close=chart_df['Close'],
        increasing_line_color='#10b981', decreasing_line_color='#ef4444'
    )])
    
    fig.update_layout(
        template="plotly_dark", height=450,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        yaxis=dict(side="right", gridcolor="#1e293b")
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# CONTAINER F — Stats Expanders
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-heading'>Pattern Backtesting Data</div>", unsafe_allow_html=True)

for name, stats in stats_all.items():
    is_today = name in latest_patterns
    with st.expander(f"{name} {' (ACTIVE)' if is_today else ''}", expanded=is_today):
        m1, m2, m3 = st.columns(3)
        m1.metric("Occurrences", stats['occurrences'])
        m2.metric("Historical Win Rate", f"{stats['win_rate']}%")
        m3.metric("Avg 3D Return", f"{stats['avg_return']:.2f}%")
        
        # Simple Sparkline or return hist could go here as per original
        if stats["returns"]:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.info(f"Insight: {build_ai_explanation(name, stats)}")


# ════════════════════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center; padding:3rem; color:#475569; font-size:0.7rem; border-top:1px solid #1e293b; margin-top:4rem;">
    <strong>PROPRIETARY QUANTITATIVE ENGINE</strong><br>
    Non-Financial Advice • For Educational Research Purposes Only • Data via Yahoo Finance
</div>
""", unsafe_allow_html=True)
