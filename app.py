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
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    def load_stock_data(t, p): 
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        return pd.DataFrame(np.random.randn(100, 4) + 150, index=dates, columns=['Open', 'High', 'Low', 'Close'])
    def get_ticker_info(t): return {"sector": "QUANTITATIVE TECH", "name": "Global Assets"}
    def analyse_all_patterns(df): return {"Trend": {"win_rate": 68, "avg_return": 1.4}}
    def get_latest_patterns(df): return ["ASCENDING_TRIANGLE"]

# ════════════════════════════════════════════════════════════════════════════
# 1. THEME & ANIMATED CSS
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="StockZ | Terminal", layout="wide", initial_sidebar_state="expanded")

def local_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=Plus+Jakarta+Sans:wght@300;400;700&display=swap');
    
    /* Background & Global */
    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at 0% 0%, #0f172a 0%, #020617 100%);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}

    /* Glassmorphism Cards */
    .terminal-card {{
        background: rgba(30, 41, 59, 0.3);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    .terminal-card:hover {{
        transform: translateY(-8px);
        border-color: #3b82f6;
        box-shadow: 0 10px 30px -10px rgba(59, 130, 246, 0.3);
    }}

    /* Custom Button Animations */
    div.stButton > button {{
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    div.stButton > button:hover {{
        transform: scale(1.03) !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6) !important;
    }}

    /* KPI Labels */
    .kpi-label {{ color: #64748b; font-size: 0.7rem; font-weight: 800; letter-spacing: 0.1em; }}
    .kpi-value {{ color: #f8fafc; font-size: 1.8rem; font-weight: 800; font-family: 'JetBrains Mono'; }}
    
    /* Active Glow Dot */
    .glow-dot {{
        height: 10px; width: 10px; background-color: #10b981; border-radius: 50%;
        display: inline-block; box-shadow: 0 0 8px #10b981;
        animation: blink 1.5s infinite;
    }}
    @keyframes blink {{ 0% {{ opacity: 0.4; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.4; }} }}
    </style>
    """, unsafe_allow_html=True)

local_css()

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG = {
    "Dashboard": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "Portfolio": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 7h-9m3 3H4a2 2 0 0 0-2 2v5a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/></svg>',
    "Settings": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3b82f6"/><stop offset="100%" style="stop-color:#10b981"/></linearGradient></defs><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" fill="url(#g)"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. STATE MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
if 'cash_balance' not in st.session_state: st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state: st.session_state.portfolio = {}
if 'current_page' not in st.session_state: st.session_state.current_page = "DASHBOARD"

# ════════════════════════════════════════════════════════════════════════════
# 4. TOP NAVIGATION BAR (Vector Integrated)
# ════════════════════════════════════════════════════════════════════════════
with st.container():
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2.5, 1])
    with nav_col1:
        st.markdown(f'<div style="display:flex; align-items:center; gap:10px;">{SVG["Logo"]} <span style="font-weight:800; font-size:1.5rem; letter-spacing:-1px;">STOCKZ</span></div>', unsafe_allow_html=True)
    
    with nav_col2:
        # Styled Tabs using radio
        st.session_state.current_page = st.radio(
            "NAV", ["DASHBOARD", "PORTFOLIO", "SETTINGS"], 
            horizontal=True, label_visibility="collapsed"
        )
    
    with nav_col3:
        st.markdown(f'<div style="text-align:right;"><span class="kpi-label">NETWORK</span><br><span class="glow-dot"></span> <span style="font-family:\'JetBrains Mono\'; font-size:0.8rem;">CORE_STABLE</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin-top:0; border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. PAGE ROUTING
# ════════════════════════════════════════════════════════════════════════════

if st.session_state.current_page == "DASHBOARD":
    # Sidebar Controls
    with st.sidebar:
        st.markdown(f"<div style='text-align:center;'>{SVG['Logo']}</div>", unsafe_allow_html=True)
        st.subheader("Market Scanner")
        ticker = st.text_input("SYMBOL", "AAPL").upper()
        period = st.selectbox("TIMEFRAME", ["1y", "2y", "5y"])
        
        if st.button("INITIATE SCAN"):
            with st.spinner("Fractal Engine Running..."):
                time.sleep(1) # Simulated Animation
                st.session_state.last_df = load_stock_data(ticker, period)
                st.session_state.last_info = get_ticker_info(ticker)
                st.session_state.active_ticker = ticker

    if 'last_df' in st.session_state:
        df = st.session_state.last_df
        px = float(df["Close"].iloc[-1])
        
        # KPI Row
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">PAPER MONEY</div><div class="kpi-value">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">MARKET PRICE</div><div class="kpi-value">${px:,.2f}</div></div>', unsafe_allow_html=True)
        with k3:
            shares = st.session_state.portfolio.get(st.session_state.active_ticker, 0)
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">POSITION</div><div class="kpi-value">{shares} SH</div></div>', unsafe_allow_html=True)
        with k4:
            total = st.session_state.cash_balance + (shares * px)
            st.markdown(f'<div class="terminal-card"><div class="kpi-label">TOTAL EQUITY</div><div class="kpi-value">${total:,.0f}</div></div>', unsafe_allow_html=True)

        # Charting
        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure(data=[go.Candlestick(x=df.index[-60:], open=df['Open'][-60:], high=df['High'][-60:], low=df['Low'][-60:], close=df['Close'][-60:],
                        increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Unified Trade Panel
        st.markdown("<div class='terminal-card'>", unsafe_allow_html=True)
        c_tr1, c_tr2, c_tr3 = st.columns([1, 1, 1])
        order_qty = c_tr1.number_input("ORDER VOLUME", min_value=1, value=10)
        
        if c_tr2.button("BUY ASSET"):
            cost = order_qty * px
            if st.session_state.cash_balance >= cost:
                st.session_state.cash_balance -= cost
                st.session_state.portfolio[st.session_state.active_ticker] = st.session_state.portfolio.get(st.session_state.active_ticker, 0) + order_qty
                st.toast(f"Executed Buy: {order_qty} {st.session_state.active_ticker}", icon="✅")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Insufficient Funds")
        
        if c_tr3.button("SELL ASSET"):
            if st.session_state.portfolio.get(st.session_state.active_ticker, 0) >= order_qty:
                st.session_state.cash_balance += (order_qty * px)
                st.session_state.portfolio[st.session_state.active_ticker] -= order_qty
                st.toast(f"Executed Sell: {order_qty} {st.session_state.active_ticker}", icon="📉")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Insufficient Position Size")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("System Ready. Please run a scan from the sidebar to view market data.")

elif st.session_state.current_page == "PORTFOLIO":
    st.markdown(f"<h2>{SVG['Portfolio']} Portfolio Inventory</h2>", unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        st.markdown(f'<div class="terminal-card"><div class="kpi-label">CASH RESERVES</div><div class="kpi-value">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    
    if st.session_state.portfolio:
        df_p = pd.DataFrame([{"Asset": k, "Quantity": v} for k, v in st.session_state.portfolio.items() if v > 0])
        st.dataframe(df_p, use_container_width=True)
    else:
        st.warning("No active holdings found in current session.")

elif st.session_state.current_page == "SETTINGS":
    st.markdown(f"<h2>{SVG['Settings']} System Settings</h2>", unsafe_allow_html=True)
    if st.button("HARD RESET TERMINAL"):
        st.session_state.clear()
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 6. FOOTER
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<br><br><div style='text-align:center; color:#475569; font-size:0.7rem;'>PROTOTYPE TERMINAL V3.0 // ENCRYPTED CONNECTION</div>", unsafe_allow_html=True)
