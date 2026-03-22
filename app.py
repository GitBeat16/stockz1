import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend Mock ──────────────────────────────────────────────────────────
try:
    from data_loader import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_latest_patterns(df): return ["BULLISH_ENGULFING", "SUPPORT_REJECTION"]
    def analyse_all_patterns(df): return {"Win_Rate": "68%", "Avg_Return": "+2.4%"}

# ════════════════════════════════════════════════════════════════════════════
# 1. THEME & ADVANCED CSS
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="StockZ Terminal v7", layout="wide")

if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'active_ticker' not in st.session_state: st.session_state.active_ticker = None
if 'processing' not in st.session_state: st.session_state.processing = False

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_trade = load_lottieurl("https://lottie.host/8172906e-4458-450b-8012-d04b868e42f9/Y96e6a1N0K.json")

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
    .value { color: #f8fafc; font-size: 2rem; font-weight: 800; font-family: 'JetBrains Mono'; }
    .pattern-tag { background: rgba(59, 130, 246, 0.2); color: #3b82f6; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 0.8rem; }

    /* FORCED BUTTON THEMING */
    button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        border: none !important; width: 100% !important; border-radius: 12px !important; height: 50px !important; font-weight: 700 !important; color: white !important;
    }
    button[kind="secondary"] {
        background: linear-gradient(135deg, #10b981 0%, #065f46 100%) !important;
        border: none !important; width: 100% !important; border-radius: 12px !important; height: 50px !important; font-weight: 700 !important; color: white !important;
    }
    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px -5px rgba(0,0,0,0.5); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 2. TRADE PROCESSING OVERLAY
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.processing:
    placeholder = st.empty()
    with placeholder.container():
        c1, c2, c3 = st.columns([1,1,1])
        with c2:
            if lottie_trade: st_lottie(lottie_trade, height=300, key="trade_anim")
            else: st.markdown("<h2 style='text-align:center;'>🔄 PROCESSING...</h2>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; color:#3b82f6;'>ORDER CONFIRMED</h3>", unsafe_allow_html=True)
        time.sleep(1.5)
    st.session_state.processing = False
    st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 3. HEADER & ACCOUNT OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
head_1, head_2 = st.columns([2, 1])
with head_1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:15px; margin-bottom:10px;">
        <svg width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
        <h1 style="margin:0; font-weight:800; letter-spacing:-1px;">STOCKZ <span style="color:#3b82f6;">PRO</span></h1>
    </div>
    """, unsafe_allow_html=True)

with head_2:
    st.markdown(f'<div class="terminal-card" style="padding:10px 20px; text-align:right;"><div class="label">Paper Money Balance</div><div class="value" style="font-size:1.4rem;">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. MAIN LAYOUT
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='label'>Market Scan</div>", unsafe_allow_html=True)
    ticker_input = st.text_input("SYMBOL", "AAPL").upper()
    if st.button("RUN ANALYSIS", use_container_width=True, type="primary"):
        with st.spinner("Analyzing Market Fractals..."):
            st.session_state.last_df = load_stock_data(ticker_input, "1y")
            st.session_state.active_ticker = ticker_input
            st.rerun()

if st.session_state.active_ticker:
    df = st.session_state.last_df
    price = float(df["Close"].iloc[-1])
    shares = st.session_state.portfolio.get(st.session_state.active_ticker, 0)
    
    # ── Intelligence Section (New!) ──
    patterns = get_latest_patterns(df)
    stats = analyse_all_patterns(df)
    
    col_intel, col_chart = st.columns([1, 2])
    
    with col_intel:
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Pattern Intelligence</div>', unsafe_allow_html=True)
        for p in patterns:
            st.markdown(f'<span class="pattern-tag">{p.replace("_", " ")}</span>', unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f'<div class="label">Win Probability</div><div class="value" style="color:#10b981;">{stats["Win_Rate"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="label">Avg Return</div><div class="value">{stats["Avg_Return"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Trade Actions
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.markdown('<div class="label">Quick Execution</div>', unsafe_allow_html=True)
        qty = st.number_input("Shares", min_value=1, value=10, label_visibility="collapsed")
        
        if st.button("BUY ORDER", type="primary"):
            cost = qty * price
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[st.session_state.active_ticker] = shares + qty
                st.session_state.processing = True
                st.rerun()
        
        if st.button("SELL ORDER", type="secondary"):
            if shares >= qty:
                st.session_state.cash_balance += (qty * price)
                st.session_state.portfolio[st.session_state.active_ticker] = shares - qty
                st.session_state.processing = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], low=df['Low'][-60:], close=df['Close'][-60:], 
                                            increasing_line_color='#10b981', decreasing_line_color='#f43f5e')])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Position Card
        st.markdown(f'<div class="terminal-card" style="display:flex; justify-content:space-around; align-items:center; text-align:center;">'
                    f'<div><div class="label">Current Position</div><div class="value" style="font-size:1.5rem;">{shares} Units</div></div>'
                    f'<div><div class="label">Equity Value</div><div class="value" style="font-size:1.5rem;">${(shares*price):,.2f}</div></div>'
                    f'</div>', unsafe_allow_html=True)
else:
    st.info("Terminal Locked. Use the sidebar to initiate a Market Scan.")
