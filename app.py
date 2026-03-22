import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend Mock (Replace with your actual imports) ──────────────────────────
try:
    from data_loader      import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns
except ImportError:
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_ticker_info(t): return {"sector": "FINANCIAL TECH", "name": "Digital Asset Terminal"}

# ════════════════════════════════════════════════════════════════════════════
# 1. GLOBAL SETTINGS & CSS
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="StockZ Terminal", layout="wide", initial_sidebar_state="expanded")

# Initialize Session State safely
if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'current_page' not in st.session_state: st.session_state.current_page = "DASHBOARD"
if 'active_ticker' not in st.session_state: st.session_state.active_ticker = None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Plus+Jakarta+Sans:wght@300;400;700&display=swap');
    [data-testid="stAppViewContainer"] { background: radial-gradient(circle at 0% 0%, #0f172a 0%, #020617 100%); font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Glassmorphism Cards */
    .terminal-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .terminal-card:hover { transform: translateY(-5px); border-color: #3b82f6; }

    /* KPI Styling */
    .kpi-label { color: #64748b; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
    .kpi-value { color: #f8fafc; font-size: 1.8rem; font-weight: 800; font-family: 'JetBrains Mono'; }

    /* Button Hover Effects */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART ICONS
# ════════════════════════════════════════════════════════════════════════════
SVG = {
    "Logo": '<svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>',
    "Wallet": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4M4 6v12c0 1.1.9 2 2 2h14v-4M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
}

# ════════════════════════════════════════════════════════════════════════════
# 3. NAVIGATION & HEADER
# ════════════════════════════════════════════════════════════════════════════
nav_col1, nav_col2 = st.columns([1, 2])
with nav_col1:
    st.markdown(f'<div style="display:flex; align-items:center; gap:10px;">{SVG["Logo"]} <h2 style="margin:0;">TERMINAL</h2></div>', unsafe_allow_html=True)
with nav_col2:
    st.session_state.current_page = st.radio("NAV", ["DASHBOARD", "PORTFOLIO", "SETTINGS"], horizontal=True, label_visibility="collapsed")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# 4. DASHBOARD VIEW
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.current_page == "DASHBOARD":
    with st.sidebar:
        st.subheader("Engine Config")
        ticker_input = st.text_input("SYMBOL", "AAPL").upper()
        timeframe = st.selectbox("TIMEFRAME", ["1y", "2y", "5y"])
        
        if st.button("RUN SCAN", use_container_width=True):
            with st.status("Initializing Neural Engine...", expanded=False):
                st.session_state.last_df = load_stock_data(ticker_input, timeframe)
                st.session_state.last_info = get_ticker_info(ticker_input)
                st.session_state.active_ticker = ticker_input
                st.rerun()

    # Safety Check: Only show dashboard if a ticker has been scanned
    if st.session_state.active_ticker:
        df = st.session_state.last_df
        info = st.session_state.last_info
        price = float(df["Close"].iloc[-1])
        shares = st.session_state.portfolio.get(st.session_state.active_ticker, 0)

        # KPI Metrics Row
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">Paper Money</div><div class="kpi-value">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">{st.session_state.active_ticker} Price</div><div class="kpi-value">${price:,.2f}</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">Current Position</div><div class="kpi-value">{shares} Units</div></div>', unsafe_allow_html=True)

        # Charting
        fig = go.Figure(data=[go.Candlestick(x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], low=df['Low'][-60:], close=df['Close'][-60:])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Execution Panel
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="kpi-label">Trade Execution</div>', unsafe_allow_html=True)
        t_col1, t_col2, t_col3 = st.columns([1, 1, 1])
        
        trade_qty = t_col1.number_input("Quantity", min_value=1, value=10)
        
        if t_col2.button("BUY ORDER", use_container_width=True):
            cost = trade_qty * price
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[st.session_state.active_ticker] = shares + trade_qty
                st.toast(f"Bought {trade_qty} {st.session_state.active_ticker}", icon="🚀")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Insufficient Funds")

        if t_col3.button("SELL ORDER", use_container_width=True):
            if shares >= trade_qty:
                st.session_state.cash_balance += (trade_qty * price)
                st.session_state.portfolio[st.session_state.active_ticker] = shares - trade_qty
                st.toast(f"Sold {trade_qty} {st.session_state.active_ticker}", icon="📉")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Not enough shares")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("System Standby. Use the sidebar to scan a ticker and initialize the terminal.")

# ════════════════════════════════════════════════════════════════════════════
# 5. PORTFOLIO & SETTINGS
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "PORTFOLIO":
    st.markdown("### Portfolio Inventory")
    st.markdown(f'<div class="terminal-card"><div class="kpi-label">Total Cash Available</div><div class="kpi-value">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    
    if any(v > 0 for v in st.session_state.portfolio.values()):
        for tick, qty in st.session_state.portfolio.items():
            if qty > 0:
                st.write(f"**{tick}**: {qty} Units")
    else:
        st.write("No active positions.")

elif st.session_state.current_page == "SETTINGS":
    if st.button("Factory Reset Terminal"):
        st.session_state.clear()
        st.rerun()
