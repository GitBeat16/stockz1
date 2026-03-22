import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend Mock ──────────────────────────────────────────────────────────
try:
    from data_loader      import load_stock_data, get_ticker_info
except ImportError:
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_ticker_info(t): return {"sector": "FINTECH", "name": "Global Asset Terminal"}

# ════════════════════════════════════════════════════════════════════════════
# 1. THEME & ADVANCED CSS
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal v4.0", layout="wide")

if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'active_ticker' not in st.session_state: st.session_state.active_ticker = None
if 'processing' not in st.session_state: st.session_state.processing = False

def load_lottieurl(url: str):
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

# Lottie Animation URLs
lottie_trade = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_m6cu98v2.json") # Success/Trade
lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json") # Scanning

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Plus+Jakarta+Sans:wght@300;400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 20% 20%, #1e293b 0%, #020617 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Glass Cards */
    .terminal-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* KPI Typography */
    .label { color: #94a3b8; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
    .value { color: #f8fafc; font-size: 2rem; font-weight: 800; font-family: 'JetBrains Mono'; }

    /* Themed Buttons */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 50px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: none !important;
    }
    
    /* BUY BUTTON - Emerald Gradient */
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
    }
    
    /* SELL BUTTON - Rose Gradient */
    div[data-testid="column"]:nth-of-type(3) .stButton > button {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%) !important;
        color: white !important;
    }

    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px -5px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 2. LOGIC: TRADE EXECUTION OVERLAY
# ════════════════════════════════════════════════════════════════════════════
def execute_trade(type, qty, price, ticker):
    st.session_state.processing = True
    # Trigger full page rerun to show loader
    st.rerun()

# This block shows the animated loader if st.session_state.processing is True
if st.session_state.processing:
    placeholder = st.empty()
    with placeholder.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st_lottie(lottie_trade, height=400, key="trade_anim")
            st.markdown("<h2 style='text-align:center; color:#3b82f6;'>EXECUTING ORDER...</h2>", unsafe_allow_html=True)
        time.sleep(1.8) # Show animation for a realistic feel
    st.session_state.processing = False
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 3. MAIN TERMINAL UI
# ════════════════════════════════════════════════════════════════════════════
# Vector Art Logo
st.markdown("""
<div style="display:flex; align-items:center; gap:15px; margin-bottom:25px;">
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
    <h1 style="margin:0; font-weight:800; letter-spacing:-1px;">STOCKZ <span style="color:#3b82f6;">TERMINAL</span></h1>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='label'>Engine Control</div>", unsafe_allow_html=True)
    ticker_input = st.text_input("INSTRUMENT", "AAPL").upper()
    if st.button("RUN SCAN", use_container_width=True):
        st.session_state.last_df = load_stock_data(ticker_input, "1y")
        st.session_state.active_ticker = ticker_input
        st.rerun()

if st.session_state.active_ticker:
    df = st.session_state.last_df
    price = float(df["Close"].iloc[-1])
    shares = st.session_state.portfolio.get(st.session_state.active_ticker, 0)

    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="terminal-card"><div class="label">Paper Money</div><div class="value">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="terminal-card"><div class="label">{st.session_state.active_ticker} Price</div><div class="value">${price:,.2f}</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="terminal-card"><div class="label">Units Held</div><div class="value">{shares}</div></div>', unsafe_allow_html=True)

    # Chart
    fig = go.Figure(data=[go.Candlestick(x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], low=df['Low'][-60:], close=df['Close'][-60:], increasing_line_color='#10b981', decreasing_line_color='#f43f5e')])
    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

    # Themed Execution Panel
    st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
    st.markdown('<div class="label" style="margin-bottom:15px;">Order Management</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.columns([1,1,1])
    
    qty = t1.number_input("Quantity", min_value=1, value=10, label_visibility="collapsed")
    
    if t2.button("BUY", use_container_width=True):
        cost = qty * price
        if st.session_state.cash_balance >= cost:
            st.session_state.cash_balance -= cost
            st.session_state.portfolio[st.session_state.active_ticker] = shares + qty
            st.session_state.processing = True # Trigger the Lottie overlay
            st.rerun()
        else:
            st.error("Insufficient Cash")

    if t3.button("SELL", use_container_width=True):
        if shares >= qty:
            st.session_state.cash_balance += (qty * price)
            st.session_state.portfolio[st.session_state.active_ticker] = shares - qty
            st.session_state.processing = True # Trigger the Lottie overlay
            st.rerun()
        else:
            st.error("Position Limit Exceeded")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("System Standby. Initiate a scan to view data.")
