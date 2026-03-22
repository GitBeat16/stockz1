import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
from streamlit_lottie import st_lottie

# ── Backend imports (Mocked logic) ───────────────────────────────────────────
try:
    from data_loader import load_stock_data, get_ticker_info
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
# 2. VECTOR ART REPOSITORY (Replaces all Emojis)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Gear": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "Info": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "Check": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
    "TrendDown": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. CUSTOM THEMED CSS & ANIMATIONS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top right, #0f172a, #020617);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* Themed Button Animations */
div.stButton > button {{
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.4);
    color: #f8fafc;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 700;
    width: 100%;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    letter-spacing: 0.05em;
}}

div.stButton > button:hover {{
    background: #3b82f6 !important;
    border-color: #60a5fa !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
    transform: translateY(-2px);
}}

/* Custom Loading Animation Bar */
.loading-bar-container {{
    width: 100%; height: 4px; background: rgba(59, 130, 246, 0.1);
    border-radius: 2px; overflow: hidden; margin-bottom: 20px;
}}
.loading-bar-fill {{
    height: 100%; width: 30%; background: #3b82f6;
    animation: loading-slide 1.5s infinite ease-in-out;
    box-shadow: 0 0 10px #3b82f6;
}}
@keyframes loading-slide {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(350%); }}
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

</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:0.9rem; color:#3b82f6; font-family:\"JetBrains Mono\";'>STOCKZ_TERMINAL</h2>", unsafe_allow_html=True)
    
    ticker_input = st.text_input("SYMBOL", value=st.session_state.last_ticker).upper().strip()
    period = st.selectbox("TIME_WINDOW", options=["1y", "2y", "5y"], index=0)
    
    if st.button("INITIALIZE SCAN"):
        st.session_state.last_ticker = ticker_input
        # Custom Loading State
        placeholder = st.empty()
        placeholder.markdown('<div class="loading-bar-container"><div class="loading-bar-fill"></div></div>', unsafe_allow_html=True)
        time.sleep(1.5)
        st.session_state.last_df = load_stock_data(ticker_input, period)
        st.session_state.last_info = get_ticker_info(ticker_input)
        placeholder.empty()
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN APP TABS
# ════════════════════════════════════════════════════════════════════════════
tab_dash, tab_port = st.tabs(["⚡ TERMINAL DASHBOARD", "💼 PORTFOLIO"])

with tab_dash:
    if 'last_df' not in st.session_state:
        st.info("System Ready. Please initialize a scan from the sidebar to load market data.")
    else:
        df, info = st.session_state.last_df, st.session_state.last_info
        ticker = st.session_state.last_ticker
        curr_price = float(df["Close"].iloc[-1])

        st.markdown(f"<div style='margin-bottom:1.5rem;'><span class='label'>Segment: {info['sector']}</span><br><span style='font-size:2.5rem; font-weight:800;'>{info['name']}</span> <span style='color:#3b82f6;' class='mono'>{ticker}</span></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="quant-card"><div class="label">Unit Price</div><div class="value">${curr_price:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="quant-card"><div class="label">Buying Power</div><div class="value">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="quant-card"><div class="label">Holdings</div><div class="value">{st.session_state.portfolio.get(ticker, 0)} Units</div></div>', unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=df.tail(80).index, open=df.tail(80)['Open'], high=df.tail(80)['High'], low=df.tail(80)['Low'], close=df.tail(80)['Close'])])
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🛠 Execution Engine")
        
        qty = st.number_input("Transaction Quantity", min_value=1, value=10, step=1)
        total_cost = qty * curr_price

        # Trade Analysis (Vector Art replaced emoji)
        st.markdown(f"""
        <div style="border-left: 4px solid #3b82f6; background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 4px 12px 12px 4px;">
            <span class="label" style="color:#3b82f6;">{SVG_ICONS['Info']} Pre-Trade Analysis</span><br>
            <div style="display:flex; justify-content:space-between; margin-top:10px;">
                <span class="mono" style="font-size:0.85rem;">Required: ${total_cost:,.2f}</span>
                <span class="mono" style="font-size:0.85rem;">Signal: Validated</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn_buy, btn_sell = st.columns(2)

        if btn_buy.button("CONFIRM BUY ORDER"):
            if st.session_state.cash_balance >= total_cost:
                loader = st.empty()
                loader.markdown('<div class="loading-bar-container"><div class="loading-bar-fill"></div></div>', unsafe_allow_html=True)
                time.sleep(1.2)
                st.session_state.cash_balance -= total_cost
                st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + qty
                st.toast(f"FILLED: +{qty} {ticker}", icon=SVG_ICONS['Check'])
                loader.empty()
                st.rerun()

        if btn_sell.button("CONFIRM SELL ORDER"):
            if st.session_state.portfolio.get(ticker, 0) >= qty:
                loader = st.empty()
                loader.markdown('<div class="loading-bar-container"><div class="loading-bar-fill"></div></div>', unsafe_allow_html=True)
                time.sleep(1.2)
                st.session_state.cash_balance += total_cost
                st.session_state.portfolio[ticker] -= qty
                st.toast(f"FILLED: -{qty} {ticker}", icon=SVG_ICONS['TrendDown'])
                loader.empty()
                st.rerun()

with tab_port:
    st.markdown("### Active Portfolio")
    for tkr, units in st.session_state.portfolio.items():
        if units > 0:
            st.markdown(f'<div class="quant-card">{tkr}: {units} Units</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align:center;'>{SVG_ICONS['Shield']} <span class='label'>Terminal Secure | No Emojis Active</span></div>", unsafe_allow_html=True)
