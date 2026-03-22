import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend Mock / Imports ──────────────────────────────────────────────────
try:
    from data_loader      import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_ticker_info(t): return {"sector": "TECHNOLOGY", "name": "Apple Inc."}
    def analyse_all_patterns(df): return {"Bullish": {"win_rate": 65, "avg_return": 1.2}}
    def get_latest_patterns(df): return ["BULLISH_ENGULFING"]

# ════════════════════════════════════════════════════════════════════════════
# 1. GLOBAL CONFIG & STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {} # Format: {"TICKER": quantity}
if 'nav_sync' not in st.session_state:
    st.session_state.nav_sync = "DASHBOARD"

SVG_ICONS = {
    "Logo": '<svg width="30" height="30" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="#3B82F6" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="#10B981" stroke-width="2"/></svg>',
    "Wallet": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Chart": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 2. DYNAMIC NAVIGATION BAR
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stRadio [data-testid="stWidgetLabel"] { display: none; }
    .stRadio div[role="radiogroup"] { flex-direction: row; gap: 20px; }
    div.st-emotion-cache-1kyx606 { margin-top: -50px; } /* Clean up spacing */
</style>
""", unsafe_allow_html=True)

# Top Bar Container
with st.container():
    col_logo, col_nav, col_status = st.columns([1, 4, 2])
    with col_logo:
        st.markdown(f'<div>{SVG_ICONS["Logo"]} <b style="color:#3b82f6; font-size:1.2rem;">TERMINAL</b></div>', unsafe_allow_html=True)
    with col_nav:
        # Actual functional navigation
        st.session_state.nav_sync = st.radio(
            "NAV", ["DASHBOARD", "PORTFOLIO", "SETTINGS"], 
            horizontal=True, label_visibility="collapsed"
        )
    with col_status:
        st.markdown(f'<div style="text-align:right;"><span class="live-dot"></span> <span class="label" style="color:#10b981;">SYSTEM_ONLINE</span></div>', unsafe_allow_html=True)
st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# 3. ROUTING LOGIC
# ════════════════════════════════════════════════════════════════════════════

# --- VIEW 1: DASHBOARD (The Trading Engine) ---
if st.session_state.nav_sync == "DASHBOARD":
    with st.sidebar:
        ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
        period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
        st.markdown("---")
        if st.button("RUN ENGINE SCAN", use_container_width=True):
            with st.status("Fetching Fractals...", expanded=False):
                st.session_state.last_df = load_stock_data(ticker, period)
                st.session_state.last_info = get_ticker_info(ticker)
                st.session_state.last_ticker = ticker

    if 'last_df' in st.session_state:
        df, info = st.session_state.last_df, st.session_state.last_info
        last_price = float(df["Close"].iloc[-1])
        
        # Dashboard KPIs
        k1, k2, k3 = st.columns(3)
        k1.metric("CASH BALANCE", f"${st.session_state.cash_balance:,.2f}")
        k2.metric(f"CURRENT {st.session_state.last_ticker}", f"${last_price:,.2f}")
        k3.metric("SHARES HELD", st.session_state.portfolio.get(st.session_state.last_ticker, 0))

        # Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], low=df['Low'][-60:], close=df['Close'][-60:])])
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Execution
        st.markdown('<div class="quant-card">', unsafe_allow_html=True)
        ex1, ex2 = st.columns(2)
        qty = ex1.number_input("QUANTITY", min_value=1, value=10)
        if ex2.button("EXECUTE BUY", use_container_width=True):
            cost = qty * last_price
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[st.session_state.last_ticker] = st.session_state.portfolio.get(st.session_state.last_ticker, 0) + qty
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Select an instrument in the sidebar to begin scanning.")

# --- VIEW 2: PORTFOLIO (Where you see your money) ---
elif st.session_state.nav_sync == "PORTFOLIO":
    st.subheader("Asset Allocation & Paper Money")
    
    # Calculate Total Portfolio Value
    # (Note: In a real app, you would iterate through all keys in portfolio and fetch current prices)
    p_val = 0
    if 'last_df' in st.session_state:
        p_val = st.session_state.portfolio.get(st.session_state.last_ticker, 0) * st.session_state.last_df["Close"].iloc[-1]
    
    total_equity = st.session_state.cash_balance + p_val
    
    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        st.markdown(f'<div class="quant-card"><div class="label">{SVG_ICONS["Wallet"]} Total Equity</div><div class="value">${total_equity:,.2f}</div></div>', unsafe_allow_html=True)
    with pc2:
        st.markdown(f'<div class="quant-card"><div class="label">Available Cash</div><div class="value">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    with pc3:
        st.markdown(f'<div class="quant-card"><div class="label">{SVG_ICONS["Chart"]} Market Value</div><div class="value">${p_val:,.2f}</div></div>', unsafe_allow_html=True)

    # Holdings Table
    if st.session_state.portfolio:
        st.markdown("### Active Holdings")
        holdings_data = []
        for tick, amt in st.session_state.portfolio.items():
            if amt > 0:
                holdings_data.append({"Ticker": tick, "Quantity": amt, "Type": "Equity"})
        st.table(pd.DataFrame(holdings_data))
    else:
        st.write("No active positions found.")

# --- VIEW 3: SETTINGS ---
elif st.session_state.nav_sync == "SETTINGS":
    st.subheader("System Configuration")
    if st.button("RESET ALL DATA"):
        st.session_state.cash_balance = 100000.0
        st.session_state.portfolio = {}
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 4. CSS (Unified)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700&display=swap');
[data-testid="stAppViewContainer"] { background: #020617; font-family: 'Plus Jakarta Sans', sans-serif; }
.quant-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; margin-bottom: 10px; }
.label { font-size: 0.75rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.value { font-size: 1.8rem; font-weight: 800; color: #f8fafc; }
.live-dot { height: 10px; width: 10px; background-color: #10b981; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)
