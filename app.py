"""
app.py
AI Candlestick Pattern Analyzer — High-Fidelity Quant UI
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
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (SVG Definitions)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Hammer": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 2h8v4H8z"/></svg>',
    "Doji": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M4 12h16"/></svg>',
    "Bullish Engulfing": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="10" width="6" height="10" fill="currentColor"/><rect x="14" y="4" width="6" height="18" fill="none" stroke="currentColor"/></svg>',
    "Bearish Engulfing": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="6" height="18" fill="none" stroke="currentColor"/><rect x="14" y="10" width="6" height="10" fill="currentColor"/></svg>',
    "Shooting Star": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 18h8v4H8z"/></svg>',
    "Default": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 3V21H21" stroke="url(#paint0_linear)" stroke-width="2" stroke-linecap="round"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#paint1_linear)" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="paint0_linear" x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="paint1_linear" x1="7" y1="14" x2="20" y2="9" gradientUnits="userSpaceOnUse"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #020617;
    color: #f8fafc;
}}

/* ── Custom Cards ── */
.quant-card {{
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.4), rgba(15, 23, 42, 0.4));
    border: 1px solid rgba(51, 65, 85, 0.5);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}
.quant-card:hover {{
    border-color: #3b82f6;
    background: rgba(30, 41, 59, 0.6);
    transform: translateY(-2px);
}}

/* ── Typography ── */
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; }}

/* ── Badges with Vector Art ── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 10px;
}}
.bullish-badge {{ background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
.bearish-badge {{ background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
.neutral-badge {{ background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}

/* ── Sidebar & Inputs ── */
[data-testid="stSidebar"] {{ background-color: #020617; border-right: 1px solid #1e293b; }}
.stButton > button {{
    width: 100%;
    background: linear-gradient(90deg, #2563eb, #10b981) !important;
    border: none !important;
    color: white !important;
    font-weight: 800 !important;
    padding: 0.6rem !important;
    border-radius: 8px !important;
}}

/* ── Animations ── */
@keyframes pulse {{
    0% {{ opacity: 0.5; }}
    50% {{ opacity: 1; }}
    100% {{ opacity: 0.5; }}
}}
.scan-line {{
    height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    animation: pulse 2s infinite;
    margin-bottom: 2rem;
}}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem;'>StockZ</h2>", unsafe_allow_html=True)
    st.markdown("<div class='scan-line'></div>", unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    analyse = st.button("EXECUTE ANALYSIS")

    # Legend with SVG
    st.markdown("<div class='label' style='margin-top:2rem'>Signal Dictionary</div>", unsafe_allow_html=True)
    for p_name, color in [("Hammer", "#10b981"), ("Doji", "#f59e0b"), ("Engulfing", "#3b82f6"), ("Shooting Star", "#ef4444")]:
        st.markdown(f"""
            <div style='display:flex; align-items:center; gap:10px; margin-top:8px;'>
                <div style='color:{color}; transform:scale(0.8)'>{SVG_ICONS.get(p_name, SVG_ICONS["Default"])}</div>
                <span style='font-size:0.75rem; color:#94a3b8;'>{p_name}</span>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# MAIN UI LOGIC
# ════════════════════════════════════════════════════════════════════════════
if not analyse:
    st.markdown(f"""
    <div style="height:70vh; display:flex; flex-direction:column; align-items:center; justify-content:center; opacity:0.6">
        {SVG_ICONS['Logo']}
        <p class='label' style='margin-top:1rem'>System Idle. Enter ticker to begin.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Load Data (Backend - Unchanged)
with st.spinner("Connecting to Liquidity Pools..."):
    df = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)
    if df.empty:
        st.error("Connection Failed. Ticker Not Found.")
        st.stop()
    stats_all = analyse_all_patterns(df)
    latest_patterns = get_latest_patterns(df)

# KPI Logic
latest_close = float(df["Close"].iloc[-1])
prev_close = float(df["Close"].iloc[-2])
daily_chg = (latest_close - prev_close) / prev_close * 100
primary = latest_patterns[0] if latest_patterns else None

# Header row
st.markdown(f"""
    <div style='margin-bottom:2rem;'>
        <div class='label'>{info['sector']} • {info['currency']}</div>
        <div style='font-size:2rem; font-weight:800;'>{info['name']} <span style='color:#3b82f6' class='mono'>{ticker}</span></div>
    </div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# KPI GRID
# ════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="quant-card">
        <div class="label">Live Close</div>
        <div class="value mono">{latest_close:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    color = "#10b981" if daily_chg >= 0 else "#ef4444"
    st.markdown(f"""<div class="quant-card">
        <div class="label">24H Delta</div>
        <div class="value mono" style="color:{color}">{'+' if daily_chg >0 else ''}{daily_chg:.2f}%</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="quant-card">
        <div class="label">Active Pattern</div>
        <div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary if primary else "NONE"}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    wr = f"{stats_all[primary]['win_rate']}%" if primary else "0%"
    st.markdown(f"""<div class="quant-card">
        <div class="label">Historical Accuracy</div>
        <div class="value mono">{wr}</div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PATTERN INTELLIGENCE SECTION
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("<div class='label' style='margin-bottom:1rem'>Advanced Price Action Chart</div>", unsafe_allow_html=True)
    chart_df = df.tail(120)
    fig = go.Figure(data=[go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'], high=chart_df['High'],
        low=chart_df['Low'], close=chart_df['Close'],
        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        increasing_fillcolor='rgba(16, 185, 129, 0.4)', decreasing_fillcolor='rgba(239, 68, 68, 0.4)'
    )])
    fig.update_layout(
        template="plotly_dark", height=450,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False,
        yaxis=dict(side="right", gridcolor="#1e293b", tickfont=dict(size=10, color="#64748b"))
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("<div class='label' style='margin-bottom:1rem'>Pattern Analysis</div>", unsafe_allow_html=True)
    if latest_patterns:
        for p in latest_patterns:
            sig = PATTERNS[p]["signal"]
            icon_svg = SVG_ICONS.get(p, SVG_ICONS["Default"])
            st.markdown(f"""
                <div class="badge {sig}-badge">
                    {icon_svg} {p}
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        explanation = build_ai_explanation(primary, stats_all[primary])
        st.markdown(f"""
            <div style='background:rgba(30,41,59,0.3); padding:1.2rem; border-radius:12px; border-left:4px solid #3b82f6;'>
                <div class='label' style='color:#3b82f6; margin-bottom:5px'>Quant Insight</div>
                <div style='font-size:0.85rem; line-height:1.6; color:#cbd5e1'>{explanation}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='padding:2rem; text-align:center; color:#475569;'>
                {SVG_ICONS["Default"]}
                <div style='font-size:0.8rem; margin-top:10px'>No patterns detected in current candle</div>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HISTORICAL BACKTEST DATA
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown("<div class='label'>Global Backtest Statistics</div>", unsafe_allow_html=True)

for name, stats in stats_all.items():
    is_today = name in latest_patterns
    with st.expander(f"{name} backtest results", expanded=is_today):
        m1, m2, m3 = st.columns(3)
        m1.markdown(f"<div class='label'>Signals</div><div class='mono'>{stats['occurrences']}</div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='label'>Win Rate</div><div class='mono'>{stats['win_rate']}%</div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='label'>Avg 3D Return</div><div class='mono'>{stats['avg_return']:.2f}%</div>", unsafe_allow_html=True)

st.markdown(f"""
    <div style='text-align:center; padding:4rem 0 2rem 0; color:#334155; font-size:0.65rem; letter-spacing:0.1em;'>
        QUANT ANALYZER CORE v4.0 • HIGH FIDELITY TERMINAL • NO FINANCIAL ADVICE
    </div>
""", unsafe_allow_html=True)
