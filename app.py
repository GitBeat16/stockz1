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
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_latest_patterns(df): return ["ASCENDING_TRIANGLE", "BULLISH_DIVERGENCE"]
    def analyse_all_patterns(df): return {"Win_Rate": "72%", "Avg_Return": "+3.1%"}

# ════════════════════════════════════════════════════════════════════════════
# 1. THEME & STYLES
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
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .label { color: #94a3b8; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 8px; }
    .value { color: #f8fafc; font-size: 1.6rem; font-weight: 800; font-family: 'JetBrains Mono'; }
    .pattern-tag { background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 6px 12px; border-radius: 4px; font-weight: 700; font-size: 0.75rem; border: 1px solid rgba(59, 130, 246, 0.3); }

    /* BUTTONS: UNIFIED ALIGNMENT */
    div.stButton > button:first-child { 
        border-radius: 8px !important; 
        height: 48px !important; 
        font-weight: 700 !important; 
        transition: all 0.2s ease !important; 
        border: none !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* BUY BUTTON */
    .buy-btn button {
        background: #2563eb !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important;
        color: white !important; width: 100% !important;
    }
    
    /* SELL BUTTON */
    .sell-btn button {
        background: #059669 !important;
        box-shadow: 0 4px 14px 0 rgba(5, 150, 105, 0.39) !important;
        color: white !important; width: 100% !important;
    }

    .stButton > button:hover { transform: translateY(-2px); filter: brightness(1.1); }
    
    /* Input field styling */
    .stTextInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 2. HEADER
# ════════════════════════════════════════════════════════════════════════════
h1, h2 = st.columns([2, 1])
with h1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:16px; padding: 10px 0;">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
            <polyline points="16 7 22 7 22 13"></polyline>
        </svg>
        <h1 style="margin:0; font-weight:800; letter-spacing:-1px;">STOCKZ <span style="color:#3b82f6;">TERMINAL</span></h1>
    </div>
    """, unsafe_allow_html=True)

with h2:
    st.markdown(f'''
    <div class="terminal-card" style="padding:10px 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="label" style="margin:0;">Liquidity</div>
            <div class="value" style="color:#10b981; font-size: 1.4rem;">${st.session_state.cash_balance:,.2f}</div>
        </div>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
    </div>
    ''', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 3. PROCESSING OVERLAY
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.processing:
    with st.empty():
        c1, c2, c3 = st.columns([1,1.5,1])
        with c2:
            st.markdown("""
                <div style="text-align:center; padding: 40px;">
                    <svg width="50" height="50" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" fill="#3b82f6">
                        <style>.spinner_P7sC{transform-origin:center;animation:spinner_S7VT .75s step-end infinite}@keyframes spinner_S7VT{8.3%{transform:rotate(30deg)}16.6%{transform:rotate(60deg)}25%{transform:rotate(90deg)}33.3%{transform:rotate(120deg)}41.6%{transform:rotate(150deg)}50%{transform:rotate(180deg)}58.3%{transform:rotate(210deg)}66.6%{transform:rotate(240deg)}75%{transform:rotate(270deg)}83.3%{transform:rotate(300deg)}91.6%{transform:rotate(330deg)}100%{transform:rotate(360deg)}}</style>
                        <path d="M12,4a8,8,0,0,1,7.89,6.7A1.53,1.53,0,0,0,21.38,12h0a1.5,1.5,0,0,0,1.48-1.75,11,11,0,0,0-21.72,0A1.5,1.5,0,0,0,2.62,12h0a1.53,1.53,0,0,0,1.49-1.3A8,8,0,0,1,12,4Z" class="spinner_P7sC"/>
                    </svg>
                    <h2 style='color:#3b82f6; font-family:JetBrains Mono;'>EXECUTING ORDER</h2>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(1.5)
    st.session_state.processing = False
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 4. DASHBOARD ENGINE
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div style='padding-top:20px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='label'>Market Scan</div>", unsafe_allow_html=True)
    t_input = st.text_input("SYMBOL", "AAPL", placeholder="Enter ticker...").upper()
    
    if st.button("INITIALIZE SCAN", use_container_width=True):
        st.session_state.last_df = load_stock_data(t_input, "1y")
        st.session_state.active_ticker = t_input
        st.rerun()
    
    st.markdown("---")
    st.markdown("<div class='label'>Quick Links</div>", unsafe_allow_html=True)
    st.caption("v8.2.1 Stable Build")

if st.session_state.active_ticker:
    df = st.session_state.last_df
    price = float(df["Close"].iloc[-1])
    shares = st.session_state.portfolio.get(st.session_state.active_ticker, 0)
    
    stats = analyse_all_patterns(df)
    patterns = get_latest_patterns(df)

    col_info, col_chart = st.columns([1, 2.5], gap="medium")

    with col_info:
        # Metrics Card
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Analysis Results</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="label" style="font-size:0.6rem">Accuracy</div><div style="color:#3b82f6; font-size:1.3rem; font-weight:800;">{stats.get("Win_Rate", "N/A")}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="label" style="font-size:0.6rem">Expectancy</div><div style="color:#f8fafc; font-size:1.3rem; font-weight:800;">{stats.get("Avg_Return", "N/A")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top:20px" class="label">Identified Patterns</div>', unsafe_allow_html=True)
        html_patterns = "".join([f'<span class="pattern-tag">{p.replace("_", " ")}</span> ' for p in patterns])
        st.markdown(f'<div style="display:flex; flex-wrap:wrap; gap:8px;">{html_patterns}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Execution Card
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Order Entry</div>', unsafe_allow_html=True)
        trade_qty = st.number_input("Quantity", min_value=1, value=10)
        
        st.markdown('<div style="margin-top:10px"></div>', unsafe_allow_html=True)
        
        # BUY / SELL Side-by-side
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.markdown('<div class="buy-btn">', unsafe_allow_html=True)
            if st.button("BUY"):
                if st.session_state.cash_balance >= (trade_qty * price):
                    st.session_state.cash_balance -= (trade_qty * price)
                    st.session_state.portfolio[st.session_state.active_ticker] = shares + trade_qty
                    st.session_state.processing = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with btn_col2:
            st.markdown('<div class="sell-btn">', unsafe_allow_html=True)
            if st.button("SELL"):
                if shares >= trade_qty:
                    st.session_state.cash_balance += (trade_qty * price)
                    st.session_state.portfolio[st.session_state.active_ticker] = shares - trade_qty
                    st.session_state.processing = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], 
            low=df['Low'][-60:], close=df['Close'][-60:], 
            increasing_line_color='#10b981', decreasing_line_color='#f43f5e'
        )])
        fig.update_layout(
            template="plotly_dark", height=420, margin=dict(l=10,r=10,t=10,b=10), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Portfolio Summary Strip
        st.markdown(f'''
        <div class="terminal-card" style="display:flex; justify-content:space-around; text-align:center; padding: 15px;">
            <div><div class="label">Position Size</div><div class="value" style="font-size:1.2rem;">{shares} <span style="font-size:0.8rem; color:#94a3b8;">shares</span></div></div>
            <div style="border-left: 1px solid rgba(255,255,255,0.1); padding-left: 40px;">
                <div class="label">Market Valuation</div>
                <div class="value" style="font-size:1.2rem; color:#3b82f6;">${(shares*price):,.2f}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align:center; margin-top:150px; opacity:0.5;">
            <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <p style="font-family:'JetBrains Mono'; margin-top:20px;">SYSTEM READY. ENTER TICKER IN SIDEBAR TO START ANALYSIS.</p>
        </div>
    """, unsafe_allow_html=True)
