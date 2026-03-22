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
# 2. VECTOR ART REPOSITORY (Fixed Missing Keys)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Gear": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "Info": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED THEMED CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top right, #0f172a, #020617);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

[data-testid="stSidebar"] {{
    background-color: #020617 !important;
    border-right: 1px solid rgba(59, 130, 246, 0.1);
}}

[data-testid="stSidebar"] .stTextInput input, 
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
    background-color: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    color: #f8fafc !important;
    border-radius: 8px !important;
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
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

.stTabs [data-baseweb="tab-list"] {{
    gap: 24px;
    background-color: rgba(15, 23, 42, 0.8);
    padding: 10px 20px;
    border-radius: 12px;
    border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}}

.stTabs [data-baseweb="tab"] {{
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
# 4. SIDEBAR (Themed)
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding-bottom:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:0.9rem; color:#3b82f6; font-family:\"JetBrains Mono\";'>STOCKZ_V4.0</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<div class='label'>Terminal Config</div>", unsafe_allow_html=True)
    ticker_input = st.text_input("INSTRUMENT", value=st.session_state.last_ticker).upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    
    st.markdown("<div style='margin-top:20px;' class='label'>Risk Tolerance</div>", unsafe_allow_html=True)
    risk_pct = st.slider("MAX_RISK", 0.5, 5.0, 1.0, 0.5)
    
    if st.button("RUN ENGINE SCAN", use_container_width=True, type="primary"):
        st.session_state.last_ticker = ticker_input
        df = load_stock_data(ticker_input, period)
        st.session_state.last_df, st.session_state.last_info = df, get_ticker_info(ticker_input)
        st.rerun()
    
    st.markdown(f"<div style='margin-top:2rem;' class='label'>{SVG_ICONS['Gear']} SYSTEM: ONLINE</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN CONTENT TABS
# ════════════════════════════════════════════════════════════════════════════
tab_dash, tab_port, tab_set = st.tabs(["DASHBOARD", "PORTFOLIO", "SETTINGS"])

with tab_dash:
    if 'last_df' not in st.session_state:
        st_lottie(lottie_scan, height=300) if lottie_scan else st.write("Awaiting Scan...")
    else:
        df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
        latest_close = float(df["Close"].iloc[-1])
        daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
        stats_all = analyse_all_patterns(df)

        st.markdown(f"<div class='label'>ANALYSIS ACTIVE</div><div style='font-size:2.5rem; font-weight:800;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="quant-card"><div class="label">Last Traded</div><div class="value">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="quant-card"><div class="label">Change</div><div class="value" style="color:#10b981">{daily_chg:+.2f}%</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="quant-card"><div class="label">Buying Power</div><div class="value">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div class='label'>Order Execution</div>", unsafe_allow_html=True)
        qty = st.number_input("QUANTITY", min_value=1, value=10)
        col_b, col_s = st.columns(2)
        if col_b.button("BUY", use_container_width=True):
            st.session_state.cash_balance -= (qty * latest_close)
            st.session_state.portfolio[active_ticker] = st.session_state.portfolio.get(active_ticker, 0) + qty
            st.toast("BUY Order Filled")
            st.rerun()
        if col_s.button("SELL", use_container_width=True):
            if st.session_state.portfolio.get(active_ticker, 0) >= qty:
                st.session_state.cash_balance += (qty * latest_close)
                st.session_state.portfolio[active_ticker] -= qty
                st.toast("SELL Order Filled")
                st.rerun()

with tab_port:
    st.markdown("<div class='label'>Current Holdings</div>", unsafe_allow_html=True)
    for tkr, vol in st.session_state.portfolio.items():
        if vol > 0: st.write(f"**{tkr}:** {vol} shares")

with tab_set:
    if st.button("RESET DATA"):
        st.session_state.clear()
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 6. FOOTER GUIDE
# ════════════════════════════════════════════════════════════════════════════
with st.expander("PROTOCOL DOCUMENTATION"):
    g1, g2 = st.columns(2)
    with g1:
        st.markdown(f"{SVG_ICONS['Info']} **Risk Parameters**", unsafe_allow_html=True)
        st.write(f"Max Risk Limit: {risk_pct}%")
    with g2:
        st.markdown(f"{SVG_ICONS['Shield']} **Engine Security**", unsafe_allow_html=True)
        st.write("All pattern matching is vectorized and local to this session.")
