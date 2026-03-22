import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend imports ──────────────────────────────────────────────────────────
try:
    from data_loader      import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns, PATTERNS
    from pattern_analysis import analyse_all_patterns, build_ai_explanation
except ImportError:
    st.error("Backend modules missing. Please ensure data_loader, pattern_detector, and pattern_analysis are in the root.")

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json")

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" cy="16" x2="12" y2="12"/><line x1="12" cy="8" x2="12.01" y2="8"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED ANIMATED CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top right, #0f172a, #020617);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

.quant-card {{
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    animation: fadeIn 0.8s ease-out;
    margin-bottom: 1rem;
}}

.quant-card:hover {{
    transform: translateY(-5px);
    border-color: rgba(59, 130, 246, 0.5);
}}

.live-dot {{
    height: 8px; width: 8px; background-color: #10b981; border-radius: 50%;
    display: inline-block; margin-right: 8px;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 1);
    animation: pulse-green 2s infinite;
}}

@keyframes pulse-green {{
    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
    70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
}}

@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}

.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

.stButton > button {{
    border-radius: 12px !important;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    transition: 0.4s !important;
}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem; margin-bottom:20px;'>StockZ Terminal</h2>", unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("---")
    
    # Persistent Account Visibility
    st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} PAPER BALANCE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="value mono" style="font-size:1.5rem; color:#10b981;">${st.session_state.cash_balance:,.2f}</div>', unsafe_allow_html=True)
    
    if st.session_state.portfolio:
        st.markdown('<div class="label" style="margin-top:15px; border-top: 1px solid #1e293b; padding-top:10px;">ACTIVE POSITIONS</div>', unsafe_allow_html=True)
        for sym, q in st.session_state.portfolio.items():
            if q > 0:
                st.markdown(f'<div class="mono" style="font-size:0.85rem; color:#3b82f6;">{sym}: {q} Shares</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    analyse = st.button("RUN ENGINE SCAN", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN UI LOGIC
# ════════════════════════════════════════════════════════════════════════════
if not analyse and 'last_df' not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
        st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>SYSTEM READY. AWAITING INPUT...</p>", unsafe_allow_html=True)
    st.stop()

if analyse:
    with st.spinner("Decoding Market Fractals..."):
        time.sleep(0.8)
        df = load_stock_data(ticker, period)
        info = get_ticker_info(ticker)
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

# Data Extraction
df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
latest_close = float(df["Close"].iloc[-1])
daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
primary = latest_patterns[0] if latest_patterns else None

# Header
st.markdown(f"""
    <div style='margin-bottom:2rem;'>
        <div class='label'><span class='live-dot'></span> {info['sector']} • LIVE FEED</div>
        <div style='font-size:2.8rem; font-weight:800; letter-spacing:-0.02em;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div>
    </div>
""", unsafe_allow_html=True)

# KPI Grid
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="quant-card"><div class="label">Last Price</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="quant-card"><div class="label">Paper Money</div><div class="value mono" style="color:#10b981;">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="quant-card"><div class="label">Signal</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary if primary else "NEUTRAL"}</div></div>', unsafe_allow_html=True)
with c4:
    total_val = st.session_state.cash_balance + sum([v * latest_close for v in st.session_state.portfolio.values()])
    st.markdown(f'<div class="quant-card"><div class="label">Total Equity</div><div class="value mono">${total_val:,.0f}</div></div>', unsafe_allow_html=True)

# Charting
fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'], 
                increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 6. TRADE EXECUTION MODULE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:2rem;' class='label'>Order Execution Engine</div>", unsafe_allow_html=True)
trade_col1, trade_col2 = st.columns([2, 1])

with trade_col1:
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    q_col1, q_col2, q_col3 = st.columns(3)
    with q_col1:
        qty = st.number_input("QUANTITY", min_value=1, value=10)
    with q_col2:
        st.markdown(f'<div class="label">Est. Cost</div><div class="value mono" style="font-size:1.4rem;">${qty * latest_close:,.2f}</div>', unsafe_allow_html=True)
    with q_col3:
        st.markdown(f'<div class="label">Buying Power</div><div class="value mono" style="font-size:1.4rem;">${st.session_state.cash_balance:,.0f}</div>', unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("EXECUTE BUY ORDER", use_container_width=True):
            cost = qty * latest_close
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + qty
                st.success(f"Filled: +{qty} {active_ticker}")
                time.sleep(1)
                st.rerun()
            else: st.error("Margin Insufficient")
    with b_col2:
        if st.button("EXECUTE SELL ORDER", use_container_width=True):
            if st.session_state.portfolio.get(active_ticker, 0) >= qty:
                st.session_state.cash_balance += (qty * latest_close)
                st.session_state.portfolio[active_ticker] -= qty
                st.warning(f"Filled: -{qty} {active_ticker}")
                time.sleep(1)
                st.rerun()
            else: st.error("Position Size Mismatch")
    st.markdown('</div>', unsafe_allow_html=True)

with trade_col2:
    st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} Net Position</div>', unsafe_allow_html=True)
    pos = st.session_state.portfolio.get(active_ticker, 0)
    st.markdown(f'<div class="value mono">{pos} <span style="font-size:0.8rem; color:#64748b;">Shares</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="label" style="margin-top:15px;">Market Value</div><div class="value mono" style="font-size:1.4rem; color:#10b981;">${pos * latest_close:,.2f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 7. SYSTEM PROTOCOLS & USER GUIDE
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:3rem;' class='label'>Protocol Overview</div>", unsafe_allow_html=True)

with st.expander("OPEN SYSTEM DOCUMENTATION", expanded=False):
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                {SVG_ICONS['Shield']} <span style="font-weight:700; color:#f8fafc;">Integrity</span>
            </div>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.4;">
                Engine utilizes vectorized pattern matching with a 120-day historical window to filter signal noise.
            </p>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                {SVG_ICONS['Logo']} <span style="font-weight:700; color:#f8fafc;">Deployment</span>
            </div>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.4;">
                Trades are simulated via session-state memory. Paper Money resets on browser refresh.
            </p>
        """, unsafe_allow_html=True)
    with g3:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                {SVG_ICONS['Info']} <span style="font-weight:700; color:#f8fafc;">Risk Level</span>
            </div>
            <p style="font-size: 0.85rem; color: #94a3b8; line-height: 1.4;">
                Risk Profile: {risk_pct}%. Position sizing is relative to total equity.
            </p>
        """, unsafe_allow_html=True)
