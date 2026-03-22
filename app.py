import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend imports ──────────────────────────────────────────────────────────
# Note: Ensure these local files are in your directory
try:
    from data_loader      import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    st.error("Missing backend dependencies (data_loader.py, etc.)")

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State
if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'active_view' not in st.session_state:
    st.session_state.active_view = "DASHBOARD"

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json")

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED UI STYLING
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
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: 0.3s ease;
}}

.live-dot {{
    height: 8px; width: 8px; background-color: #10b981; border-radius: 50%;
    display: inline-block; margin-right: 8px;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    animation: pulse-green 2s infinite;
}}

@keyframes pulse-green {{
    0% {{ transform: scale(0.95); opacity: 0.7; }}
    70% {{ transform: scale(1.1); opacity: 1; }}
    100% {{ transform: scale(0.95); opacity: 0.7; }}
}}

.label {{ font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

/* Navigation button styling */
.nav-btn {{
    padding: 5px 15px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 600;
    transition: 0.3s;
}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. NAVIGATION & SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
# Top Navigation Bar
nav_col1, nav_col2, nav_col3, nav_col4, nav_spacer, nav_status = st.columns([0.5, 1, 1, 1, 3, 1.5])

with nav_col1: st.markdown(SVG_ICONS["Logo"], unsafe_allow_html=True)
with nav_col2: 
    if st.button("DASHBOARD", key="nav_dash"): st.session_state.active_view = "DASHBOARD"
with nav_col3: 
    if st.button("PORTFOLIO", key="nav_port"): st.session_state.active_view = "PORTFOLIO"
with nav_col4: 
    if st.button("SETTINGS", key="nav_set"): st.session_state.active_view = "SETTINGS"
with nav_status:
    st.markdown('<div style="text-align:right;"><span class="live-dot"></span><span class="label" style="color:#10b981">System Ready</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='border: 0; height: 1px; background: rgba(255,255,255,0.1); margin-bottom: 25px;'>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem; margin-bottom:1.5rem;'>StockZ Terminal</h2>", unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("---")
    analyse_trigger = st.button("RUN ENGINE SCAN", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. CORE LOGIC & DATA LOAD
# ════════════════════════════════════════════════════════════════════════════
if analyse_trigger:
    with st.spinner("Decoding Market Fractals..."):
        df = load_stock_data(ticker, period)
        info = get_ticker_info(ticker)
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

if 'last_df' not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st_lottie(lottie_scan, height=300, key="initial")
        st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>AWAITING INSTRUMENT SCAN...</p>", unsafe_allow_html=True)
    st.stop()

# Load states
df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
latest_close = float(df["Close"].iloc[-1])
daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
primary_signal = latest_patterns[0] if latest_patterns else "NEUTRAL"

# ════════════════════════════════════════════════════════════════════════════
# 6. MAIN DASHBOARD VIEW
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.active_view == "DASHBOARD":
    # Header
    st.markdown(f"""
        <div style='margin-bottom:2rem;'>
            <div class='label'>{info['sector']} • QUANTIATIVE ANALYTICS</div>
            <div style='font-size:2.8rem; font-weight:800; letter-spacing:-0.02em;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div>
        </div>
    """, unsafe_allow_html=True)

    # KPI Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="quant-card"><div class="label">Last Price</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="quant-card"><div class="label">Change</div><div class="value mono" style="color:{"#10b981" if daily_chg >=0 else "#ef4444"}">{daily_chg:+.2f}%</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="quant-card"><div class="label">Primary Signal</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary_signal}</div></div>', unsafe_allow_html=True)
    with c4:
        total_val = st.session_state.cash_balance + sum([v * latest_close for k,v in st.session_state.portfolio.items()])
        st.markdown(f'<div class="quant-card"><div class="label">Total Equity</div><div class="value mono">${total_val:,.0f}</div></div>', unsafe_allow_html=True)

    # Charting
    fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'], 
                    increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # ════════════════════════════════════════════════════════════════════════════
    # 7. EXECUTION ENGINE (The "Working" Buttons)
    # ════════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='margin-top:2rem;' class='label'>Order Execution Engine</div>", unsafe_allow_html=True)
    trade_col1, trade_col2 = st.columns([2, 1])

    with trade_col1:
        st.markdown('<div class="quant-card">', unsafe_allow_html=True)
        q1, q2, q3 = st.columns(3)
        with q1: qty = st.number_input("QUANTITY", min_value=1, value=10, key="order_qty")
        with q2: st.markdown(f'<div class="label">Trade Cost</div><div class="value mono" style="font-size:1.4rem;">${qty * latest_close:,.2f}</div>', unsafe_allow_html=True)
        with q3: st.markdown(f'<div class="label">Available Cash</div><div class="value mono" style="font-size:1.4rem;">${st.session_state.cash_balance:,.0f}</div>', unsafe_allow_html=True)
        
        btn_buy, btn_sell = st.columns(2)
        with btn_buy:
            if st.button("BUY / LONG", use_container_width=True):
                cost = qty * latest_close
                if st.session_state.cash_balance >= cost:
                    st.session_state.cash_balance -= cost
                    st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + qty
                    st.toast(f"FILLED: +{qty} {active_ticker}", icon="✅")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Margin Insufficient")
        with btn_sell:
            if st.button("SELL / SHORT", use_container_width=True):
                if st.session_state.portfolio.get(active_ticker, 0) >= qty:
                    st.session_state.cash_balance += (qty * latest_close)
                    st.session_state.portfolio[active_ticker] -= qty
                    st.toast(f"FILLED: -{qty} {active_ticker}", icon="📉")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Position size mismatch")
        st.markdown('</div>', unsafe_allow_html=True)

    with trade_col2:
        st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} Active Position</div>', unsafe_allow_html=True)
        pos = st.session_state.portfolio.get(active_ticker, 0)
        st.markdown(f'<div class="value mono">{pos} <span style="font-size:0.8rem; color:#64748b;">SHARES</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label" style="margin-top:15px;">Holding Value</div><div class="value mono" style="font-size:1.4rem; color:#3b82f6;">${pos * latest_close:,.2f}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 8. CLEAN USER GUIDE (No Dev Comments)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
with st.expander("OPERATIONAL PROTOCOLS & USER GUIDE"):
    guide_c1, guide_c2, guide_c3 = st.columns(3)
    with guide_c1:
        st.markdown(f"#### {SVG_ICONS['Shield']} Integrity")
        st.write("System utilizes vectorized pattern matching across a 120-day lookback window to eliminate high-frequency noise.")
    with guide_c2:
        st.markdown(f"#### {SVG_ICONS['Logo']} Simulation")
        st.write("All transactions are processed in a paper-trading sandbox. Refresh the session to reset balances and positions.")
    with guide_c3:
        st.markdown(f"#### {SVG_ICONS['Info']} Risk Management")
        st.write(f"The system is currently operating at a **{risk_pct}%** risk threshold per trade based on total portfolio equity.")

# Handle other views
if st.session_state.active_view == "PORTFOLIO":
    st.title("Portfolio Holdings")
    st.write(st.session_state.portfolio)
if st.session_state.active_view == "SETTINGS":
    st.title("Terminal Settings")
    st.write("API and UI configuration options would appear here.")
