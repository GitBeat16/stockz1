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

# Initialize Session State keys
if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'current_page' not in st.session_state: st.session_state.current_page = "DASHBOARD"

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
    "Logo": '<svg width="35" height="35" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" cy="16" x2="12" y2="12"/><line x1="12" cy="8" x2="12.01" y2="8"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. STYLING ENGINE
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
    margin-bottom: 1rem;
}}

.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

/* Navigation Button Styling */
div[data-testid="column"] button {{
    background: transparent !important;
    border: none !important;
    color: #64748b !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    font-size: 0.7rem !important;
    padding: 0 !important;
}}
div[data-testid="column"] button:hover {{ color: #3b82f6 !important; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. TOP NAVIGATION BAR (FUNCTIONAL)
# ════════════════════════════════════════════════════════════════════════════
nav_container = st.container()
with nav_container:
    col_logo, col_dash, col_port, col_sett, col_spacer, col_status = st.columns([0.5, 1, 1, 1, 4, 1.5])
    with col_logo: st.markdown(SVG_ICONS["Logo"], unsafe_allow_html=True)
    with col_dash: 
        if st.button("DASHBOARD"): st.session_state.current_page = "DASHBOARD"
    with col_port: 
        if st.button("PORTFOLIO"): st.session_state.current_page = "PORTFOLIO"
    with col_sett: 
        if st.button("SETTINGS"): st.session_state.current_page = "SETTINGS"
    with col_status:
        st.markdown('<div style="display:flex; align-items:center; gap:8px;"><div class="live-dot" style="height:8px; width:8px; background:#10b981; border-radius:50%;"></div><span class="label" style="color:#10b981;">CORE_STABLE</span></div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 0 0 25px 0; border-color: rgba(59,130,246,0.1);'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("---")
    st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} PAPER BALANCE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="value mono" style="font-size:1.5rem; color:#10b981;">${st.session_state.cash_balance:,.2f}</div>', unsafe_allow_html=True)
    
    analyse = st.button("RUN ENGINE SCAN", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 6. ROUTING LOGIC
# ════════════════════════════════════════════════════════════════════════════

# --- VIEW: DASHBOARD ---
if st.session_state.current_page == "DASHBOARD":
    if not analyse and 'last_df' not in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
            st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>SYSTEM READY. AWAITING INPUT...</p>", unsafe_allow_html=True)
    else:
        if analyse:
            with st.spinner("Decoding Market Fractals..."):
                df = load_stock_data(ticker, period)
                info = get_ticker_info(ticker)
                st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

        df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
        latest_close = float(df["Close"].iloc[-1])
        
        # Header & KPIs
        st.markdown(f"<div class='label'>SCANNING: {info['name']}</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="quant-card"><div class="label">Price</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="quant-card"><div class="label">Balance</div><div class="value mono">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)
        
        # Chart
        fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Trade Actions
        if st.button(f"BUY 10 SHARES OF {active_ticker}"):
            cost = 10 * latest_close
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + 10
                st.success("Trade Executed")
                st.rerun()

# --- VIEW: PORTFOLIO ---
elif st.session_state.current_page == "PORTFOLIO":
    st.markdown("### Asset Allocation")
    if not st.session_state.portfolio:
        st.info("No active positions in current session.")
    else:
        for sym, qty in st.session_state.portfolio.items():
            if qty > 0:
                st.markdown(f"""
                <div class="quant-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span class="value mono">{sym}</span>
                        <span class="label">{qty} Shares Held</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- VIEW: SETTINGS ---
elif st.session_state.current_page == "SETTINGS":
    st.markdown("### System Configuration")
    st.markdown('<div class="quant-card">', unsafe_allow_html=True)
    st.toggle("High Frequency Mode", value=True)
    st.toggle("Dark Theme Lock", value=True)
    if st.button("Reset Session Balance"):
        st.session_state.cash_balance = 100000.0
        st.session_state.portfolio = {}
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Performance Expander (Always visible at bottom)
with st.expander("SYSTEM PROTOCOLS", expanded=False):
    g1, g2, g3 = st.columns(3)
    with g1: st.markdown(f"{SVG_ICONS['Shield']} **Integrity**: Signal matching active.", unsafe_allow_html=True)
    with g2: st.markdown(f"{SVG_ICONS['Logo']} **Node**: CORE_STABLE_01", unsafe_allow_html=True)
    with g3: st.markdown(f"{SVG_ICONS['Info']} **Mode**: Simulation", unsafe_allow_html=True)
