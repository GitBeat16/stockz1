import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend imports (unchanged) ──────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

# Robust Lottie Loader to prevent API Crashes
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Using a stable Lottie Host URL
lottie_scan = load_lottieurl("https://lottie.host/86877843-085e-4977-8321-72f1279a5015/GvAonT49u6.json")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED ANIMATED CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }}
.quant-card {{ background: rgba(30, 41, 59, 0.4); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 1.5rem; transition: all 0.3s; animation: fadeIn 0.8s ease-out; }}
.quant-card:hover {{ transform: translateY(-5px); border-color: #3b82f6; }}
.live-dot {{ height: 8px; width: 8px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.guide-panel {{ background: rgba(30, 41, 59, 0.2); border: 1px solid #1e293b; border-radius: 12px; padding: 2rem; margin-top: 3rem; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    analyse = st.button("RUN ENGINE SCAN")

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN UI LOGIC
# ════════════════════════════════════════════════════════════════════════════
if not analyse and 'last_df' not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
        else: st.markdown(f'<div style="text-align:center; padding:5rem 0;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>SYSTEM READY. AWAITING INPUT...</p>", unsafe_allow_html=True)
    st.stop()

if analyse:
    with st.spinner("Decoding Market Fractals..."):
        df = load_stock_data(ticker, period)
        info = get_ticker_info(ticker)
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
latest_close = float(df["Close"].iloc[-1])
daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
primary = latest_patterns[0] if latest_patterns else None

# Header
st.markdown(f"<div><div class='label'><span class='live-dot'></span>{info['sector']}</div><div style='font-size:2.5rem; font-weight:800;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div></div>", unsafe_allow_html=True)

# KPI Grid
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="quant-card"><div class="label">Price</div><div class="value mono">{latest_close:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="quant-card"><div class="label">24H Delta</div><div class="value mono" style="color:{"#10b981" if daily_chg >=0 else "#ef4444"}">{daily_chg:.2f}%</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="quant-card"><div class="label">Active Pattern</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary if primary else "NONE"}</div></div>', unsafe_allow_html=True)
with c4:
    total_val = st.session_state.cash_balance + sum([v * latest_close for v in st.session_state.portfolio.values()])
    st.markdown(f'<div class="quant-card"><div class="label">Net Worth</div><div class="value mono">${total_val:,.0f}</div></div>', unsafe_allow_html=True)

# Chart
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
chart_df = df.tail(120)
fig = go.Figure(data=[go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# ── ADVANCED BACKTEST STATS ──
st.markdown("<div style='height:40px'></div><div class='label'>Quant Performance Metrics</div>", unsafe_allow_html=True)
for name, stats in stats_all.items():
    with st.expander(f"{name} Analysis"):
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='label'>Signals</div><div class='mono'>{stats['occurrences']}</div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='label'>Win Rate</div><div class='mono' style='color:#10b981'>{stats['win_rate']}%</div>", unsafe_allow_html=True)
        avg_r = stats.get('avg_return', 0)
        m3.markdown(f"<div class='label'>Avg 3D Edge</div><div class='mono'>{avg_r:+.2f}%</div>", unsafe_allow_html=True)
        expectancy = (stats['win_rate']/100 * avg_r) - ((1 - stats['win_rate']/100) * abs(avg_r * 0.5))
        m4.markdown(f"<div class='label'>Expectancy</div><div class='mono' style='color:{'#10b981' if expectancy > 0 else '#ef4444'}'>{expectancy:.2f}R</div>", unsafe_allow_html=True)
        st.progress(stats['win_rate'] / 100)

# ── PRODUCT GUIDE ──
st.markdown(f"""
<div class="guide-panel">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.5rem;">{SVG_ICONS['Info']} <span style="font-weight:800; font-size:1.1rem;">TERMINAL USER GUIDE</span></div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:30px;">
        <div style="font-size:0.85rem; color:#94a3b8;">
            <p style="color:#f8fafc; font-weight:600;">1. SCANNING</p>
            The engine scans historical data for technical price action patterns. A "Hammer" or "Engulfing" candle identifies potential institutional shifts.
        </div>
        <div style="font-size:0.85rem; color:#94a3b8;">
            <p style="color:#f8fafc; font-weight:600;">2. QUANT METRICS</p>
            <b>Expectancy (R):</b> Projected return per dollar risked. <b>Win Rate:</b> The historical frequency of profit over a 3-day holding period.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:4rem 0; color:#334155; font-size:0.65rem;'>QUANT ANALYZER CORE v5.0 • ANIMATION ENGINE ENABLED</div>",
