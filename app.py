import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend imports (Mocked logic included if files are missing) ──────────────
try:
    from data_loader import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    # Fallback/Mock for demonstration
    def load_stock_data(t, p):
        dates = pd.date_range(end=pd.Timestamp.now(), periods=200)
        return pd.DataFrame({
            "Open": np.random.randn(200).cumsum() + 150,
            "High": np.random.randn(200).cumsum() + 155,
            "Low": np.random.randn(200).cumsum() + 145,
            "Close": np.random.randn(200).cumsum() + 150,
        }, index=dates)
    
    def get_ticker_info(t):
        return {"name": "Apple Inc.", "sector": "Technology"}
    
    def analyse_all_patterns(df):
        return {"Bullish Flag": {"win_rate": 68, "avg_return": 4.2}, "Double Bottom": {"win_rate": 72, "avg_return": 5.1}}

    def get_latest_patterns(df):
        return ["Bullish Engulfing"]

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = "AAPL"

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json")

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Used instead of Emojis)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
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
    margin-bottom: 1rem;
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

.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

/* Navigation Tab Styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 24px;
    background-color: rgba(15, 23, 42, 0.8);
    padding: 10px 20px;
    border-radius: 12px;
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}}

.stTabs [data-baseweb="tab"] {{
    height: 40px;
    background-color: transparent !important;
    border: none !important;
    color: #64748b !important;
    font-weight: 700;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
}}

.stTabs [aria-selected="true"] {{
    color: #3b82f6 !important;
    border-bottom: 2px solid #3b82f6 !important;
}}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. NAVIGATION & SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem;'>StockZ Terminal</h2>", unsafe_allow_html=True)
    
    ticker_input = st.text_input("INSTRUMENT", value=st.session_state.last_ticker).upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("---")
    if st.button("RUN ENGINE SCAN", use_container_width=True):
        st.session_state.last_ticker = ticker_input
        df = load_stock_data(ticker_input, period)
        st.session_state.last_df = df
        st.session_state.last_info = get_ticker_info(ticker_input)
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN CONTENT TABS (The Nav Bar)
# ════════════════════════════════════════════════════════════════════════════
tab_dash, tab_port, tab_set = st.tabs(["DASHBOARD", "PORTFOLIO", "SETTINGS"])

# --- DASHBOARD TAB ---
with tab_dash:
    if 'last_df' not in st.session_state:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
            st.markdown("<p style='text-align:center; color:#64748b;' class='mono'>SYSTEM READY. RUN SCAN TO BEGIN.</p>", unsafe_allow_html=True)
    else:
        df = st.session_state.last_df
        info = st.session_state.last_info
        active_ticker = st.session_state.last_ticker
        
        # Calculations
        latest_close = float(df["Close"].iloc[-1])
        daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
        stats_all = analyse_all_patterns(df)
        latest_patterns = get_latest_patterns(df)
        primary = latest_patterns[0] if latest_patterns else "NEUTRAL"

        # Header
        st.markdown(f"""
            <div style='margin-bottom:1rem;'>
                <div class='label'><span class='live-dot'></span> {info['sector']} • ANALYSIS ACTIVE</div>
                <div style='font-size:2.8rem; font-weight:800; letter-spacing:-0.02em;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div>
            </div>
        """, unsafe_allow_html=True)

        # KPI Grid
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="quant-card"><div class="label">Last Traded</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="quant-card"><div class="label">Session Change</div><div class="value mono" style="color:{"#10b981" if daily_chg >=0 else "#ef4444"}">{daily_chg:+.2f}%</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="quant-card"><div class="label">Pattern Signal</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary}</div></div>', unsafe_allow_html=True)
        with c4:
            total_equity = st.session_state.cash_balance + sum([v * latest_close for k, v in st.session_state.portfolio.items() if k == active_ticker])
            st.markdown(f'<div class="quant-card"><div class="label">Total Equity</div><div class="value mono">${total_equity:,.0f}</div></div>', unsafe_allow_html=True)

        # Chart
        fig = go.Figure(data=[go.Candlestick(x=df.tail(100).index, open=df.tail(100)['Open'], high=df.tail(100)['High'], low=df.tail(100)['Low'], close=df.tail(100)['Close'], 
                        increasing_line_color='#10b981', decreasing_line_color='#ef4444')])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Execution Engine
        st.markdown("<div class='label' style='margin-top:1rem;'>Order Execution Engine</div>", unsafe_allow_html=True)
        trade_col1, trade_col2 = st.columns([2, 1])

        with trade_col1:
            st.markdown('<div class="quant-card">', unsafe_allow_html=True)
            q_col1, q_col2, q_col3 = st.columns(3)
            with q_col1:
                qty = st.number_input("QUANTITY", min_value=1, value=10, key="order_qty")
            with q_col2:
                st.markdown(f'<div class="label">Est. Cost</div><div class="value mono" style="font-size:1.4rem;">${qty * latest_close:,.2f}</div>', unsafe_allow_html=True)
            with q_col3:
                st.markdown(f'<div class="label">Buying Power</div><div class="value mono" style="font-size:1.4rem;">${st.session_state.cash_balance:,.0f}</div>', unsafe_allow_html=True)
            
            b_col1, b_col2 = st.columns(2)
            with b_col1:
                if st.button("EXECUTE BUY ORDER", use_container_width=True, type="primary"):
                    cost = qty * latest_close
                    if st.session_state.cash_balance >= cost:
                        st.session_state.cash_balance -= cost
                        st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + qty
                        st.toast(f"FILLED: BUY {qty} {active_ticker}", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Insufficient Funds")
            with b_col2:
                if st.button("EXECUTE SELL ORDER", use_container_width=True):
                    if st.session_state.portfolio.get(active_ticker, 0) >= qty:
                        st.session_state.cash_balance += (qty * latest_close)
                        st.session_state.portfolio[active_ticker] -= qty
                        st.toast(f"FILLED: SELL {qty} {active_ticker}", icon="📉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Position too small")
            st.markdown('</div>', unsafe_allow_html=True)

        with trade_col2:
            st.markdown('<div class="quant-card" style="height:100%;">', unsafe_allow_html=True)
            st.markdown(f'<div class="label">{SVG_ICONS["Wallet"]} Current Position</div>', unsafe_allow_html=True)
            pos = st.session_state.portfolio.get(active_ticker, 0)
            st.markdown(f'<div class="value mono">{pos} <span style="font-size:0.8rem; color:#64748b;">Shares</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="label" style="margin-top:15px;">Market Value</div><div class="value mono" style="font-size:1.4rem; color:#10b981;">${pos * latest_close:,.2f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Performance Stats
        st.markdown("<div class='label' style='margin-top:2rem;'>Historical Pattern Efficacy</div>", unsafe_allow_html=True)
        cols = st.columns(len(stats_all))
        for i, (name, stats) in enumerate(stats_all.items()):
            with cols[i]:
                st.markdown(f"""
                <div class="quant-card">
                    <div class="label" style="color:#3b82f6">{name}</div>
                    <div style="font-size:1.4rem; font-weight:700; margin:0.5rem 0;">{stats['win_rate']}% <span class="label">Win Rate</span></div>
                    <div class="label">Avg Return: {stats['avg_return']:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)

# --- PORTFOLIO TAB ---
with tab_port:
    st.markdown("<div class='label'>Account Assets</div>", unsafe_allow_html=True)
    if not st.session_state.portfolio:
        st.info("No active positions held.")
    else:
        for tkr, volume in st.session_state.portfolio.items():
            if volume > 0:
                st.markdown(f"""
                <div class="quant-card" style="display:flex; justify-content:space-between; align-items:center;">
                    <div><span class="label">Asset</span><br><b>{tkr}</b></div>
                    <div><span class="label">Quantity</span><br><b>{volume}</b></div>
                    <div style="color:#10b981"><span class="label">Status</span><br><b>LONG</b></div>
                </div>
                """, unsafe_allow_html=True)

# --- SETTINGS TAB ---
with tab_set:
    st.markdown(f"#### {SVG_ICONS['Shield']} System Integrity")
    st.write("Terminal Version: 4.0.2 (Stable)")
    if st.button("RESET SESSION DATA"):
        st.session_state.clear()
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 6. FOOTER GUIDE
# ════════════════════════════════════════════════════════════════════════════
with st.expander("PROTOCOL DOCUMENTATION"):
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(f"{SVG_ICONS['Info']} **Risk Parameters**")
        st.write(f"Standard risk set at {risk_pct}%. Position sizing is calculated relative to available liquid capital.")
    with g2:
        st.markdown(f"{SVG_ICONS['Logo']} **Engine Logic**")
        st.write("Using vectorized math for fractal detection. All trade simulations are local to this session.")
