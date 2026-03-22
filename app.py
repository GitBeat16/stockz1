import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend Imports ────────────────────────────────────────────────────────
try:
    from data_loader import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    # Fallback Mocks if local files are missing
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_latest_patterns(df): return ["ASCENDING_TRIANGLE", "BULLISH_DIVERGENCE"]
    def analyse_all_patterns(df): return {"Win_Rate": "72%", "Avg_Return": "+3.1%"}

# ════════════════════════════════════════════════════════════════════════════
# 1. THEME & STYLES (Blue & Emerald)
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="StockZ Terminal v8", layout="wide")

if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'active_ticker' not in st.session_state: st.session_state.active_ticker = None
if 'processing' not in st.session_state: st.session_state.processing = False

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Plus+Jakarta+Sans:wght@300;400;700&display=swap');
    
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 20% 20%, #0f172a 0%, #020617 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .terminal-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .label { color: #94a3b8; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; }
    .value { color: #f8fafc; font-size: 1.8rem; font-weight: 800; font-family: 'JetBrains Mono'; }
    .pattern-tag { background: rgba(59, 130, 246, 0.2); color: #3b82f6; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; margin-right: 5px; }

    /* BUTTONS: BLUE & EMERALD */
    div.stButton > button:first-child { 
        border-radius: 12px !important; height: 45px !important; font-weight: 700 !important; transition: all 0.3s ease !important; border: none !important;
    }
    
    /* BLUE THEME (BUY) */
    .buy-btn button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important; width: 100% !important;
    }
    
    /* EMERALD THEME (SELL) */
    .sell-btn button {
        background: linear-gradient(135deg, #10b981 0%, #065f46 100%) !important;
        color: white !important; width: 100% !important;
    }

    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 8px 15px rgba(0,0,0,0.3); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR LOGO & PAPER MONEY HEADER
# ════════════════════════════════════════════════════════════════════════════
h1, h2 = st.columns([2, 1])
with h1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:12px;">
        <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <h1 style="margin:0; font-weight:800;">STOCKZ <span style="color:#3b82f6;">PRO</span></h1>
    </div>
    """, unsafe_allow_html=True)

with h2:
    st.markdown(f'''
    <div class="terminal-card" style="padding:12px 20px; text-align:right;">
        <div class="label">Available Paper Money</div>
        <div class="value" style="color:#10b981;">${st.session_state.cash_balance:,.2f}</div>
    </div>
    ''', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 3. TRADE ANIMATION (Lottie)
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.processing:
    placeholder = st.empty()
    with placeholder.container():
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            st.markdown("<h3 style='text-align:center; color:#3b82f6;'>EXECUTING...</h3>", unsafe_allow_html=True)
            # Safe Lottie trigger
            lottie_url = "https://lottie.host/8172906e-4458-450b-8012-d04b868e42f9/Y96e6a1N0K.json"
            try:
                r = requests.get(lottie_url); data = r.json()
                st_lottie(data, height=250, key="trade_exec")
            except: st.write("🔄 Order in progress...")
        time.sleep(1.2)
    st.session_state.processing = False
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 4. MAIN ENGINE
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='label'>Analysis Console</div>", unsafe_allow_html=True)
    t_input = st.text_input("TICKER SYMBOL", "AAPL").upper()
    if st.button("RUN DEEP SCAN", use_container_width=True):
        st.session_state.last_df = load_stock_data(t_input, "1y")
        st.session_state.active_ticker = t_input
        st.rerun()

if st.session_state.active_ticker:
    df = st.session_state.last_df
    price = float(df["Close"].iloc[-1])
    shares = st.session_state.portfolio.get(st.session_state.active_ticker, 0)
    
    # SAFE ANALYTICS (Fixes KeyError)
    patterns = get_latest_patterns(df)
    stats = analyse_all_patterns(df)
    win_prob = stats.get("Win_Rate", stats.get("win_rate", "N/A"))
    avg_ret = stats.get("Avg_Return", stats.get("avg_return", "N/A"))

    col_info, col_chart = st.columns([1, 2.2])

    with col_info:
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Detected Patterns</div>', unsafe_allow_html=True)
        for p in patterns:
            st.markdown(f'<span class="pattern-tag">{p.replace("_", " ")}</span>', unsafe_allow_html=True)
        
        st.markdown(f'<br><br><div class="label">Signal Accuracy</div><div class="value" style="color:#3b82f6;">{win_prob}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label">Expectancy</div><div class="value">{avg_ret}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Action Panel
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Trade Execution</div>', unsafe_allow_html=True)
        trade_qty = st.number_input("Shares", min_value=1, value=10, label_visibility="collapsed")
        
        # BUY BUTTON (BLUE)
        st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
        if st.button("BUY ASSET"):
            if st.session_state.cash_balance >= (trade_qty * price):
                st.session_state.cash_balance -= (trade_qty * price)
                st.session_state.portfolio[st.session_state.active_ticker] = shares + trade_qty
                st.session_state.processing = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # SELL BUTTON (EMERALD)
        st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
        if st.button("SELL ASSET"):
            if shares >= trade_qty:
                st.session_state.cash_balance += (trade_qty * price)
                st.session_state.portfolio[st.session_state.active_ticker] = shares - trade_qty
                st.session_state.processing = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], low=df['Low'][-60:], close=df['Close'][-60:], 
                        increasing_line_color='#10b981', decreasing_line_color='#f43f5e')])
        fig.update_layout(template="plotly_dark", height=480, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Position Info
        st.markdown(f'''
        <div class="terminal-card" style="display:flex; justify-content:space-around; text-align:center;">
            <div><div class="label">Units Held</div><div class="value" style="font-size:1.4rem;">{shares}</div></div>
            <div><div class="label">Market Value</div><div class="value" style="font-size:1.4rem;">${(shares*price):,.2f}</div></div>
        </div>
        ''', unsafe_allow_html=True)
else:
    st.info("Terminal Ready. Awaiting Market Input.")
