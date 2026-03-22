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
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
        # Seed for reproducible patterns in mock data
        np.random.seed(42)
        df = pd.DataFrame({
            "Open": np.random.randn(100).cumsum() + 150,
            "High": np.random.randn(100).cumsum() + 155,
            "Low": np.random.randn(100).cumsum() + 145,
            "Close": np.random.randn(100).cumsum() + 150,
        }, index=dates)
        return df
    
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

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Strictly No Emojis)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="45" height="45" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "Check": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>',
    "TrendDown": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="3"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
    "Briefcase": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f8fafc" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "Terminal": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
    # Candlestick Patterns
    "Hammer": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><rect x="9" y="4" width="6" height="4" fill="#10b981"/><line x1="12" y1="8" x2="12" y2="20"/></svg>',
    "ShootingStar": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><rect x="9" y="16" width="6" height="4" fill="#ef4444"/><line x1="12" y1="4" x2="12" y2="16"/></svg>',
    "Doji": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2"><line x1="8" y1="12" x2="16" y2="12"/><line x1="12" y1="6" x2="12" y2="18"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. CUSTOM THEMED CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at top right, #0f172a, #020617);
    font-family: 'Plus Jakarta Sans', sans-serif;
}}

/* Custom Loading Animation Bar */
.loading-bar-container {{
    width: 100%; height: 4px; background: rgba(59, 130, 246, 0.1);
    border-radius: 2px; overflow: hidden; margin: 10px 0;
}}
.loading-bar-fill {{
    height: 100%; width: 40%; background: #3b82f6;
    animation: loading-slide 1.2s infinite ease-in-out;
    box-shadow: 0 0 10px #3b82f6;
}}
@keyframes loading-slide {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(300%); }}
}}

.quant-card {{
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.5rem;
}}

.pattern-chip {{
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(15, 23, 42, 0.8);
    padding: 6px 12px; border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-right: 10px;
}}

.label {{ font-size: 0.65rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.5rem; font-weight: 800; color: #f8fafc; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}

</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding: 20px 0;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:0.8rem; color:#3b82f6; font-family:\"JetBrains Mono\"; margin-bottom: 2rem;'>QUANT_v3_CORE</h2>", unsafe_allow_html=True)
    
    ticker_input = st.text_input("SYMBOL", value=st.session_state.last_ticker).upper().strip()
    
    if st.button("RUN SYSTEM SCAN"):
        st.session_state.last_ticker = ticker_input
        loader = st.empty()
        loader.markdown('<div class="loading-bar-container"><div class="loading-bar-fill"></div></div>', unsafe_allow_html=True)
        time.sleep(1.2)
        st.session_state.last_df = load_stock_data(ticker_input, "1y")
        st.session_state.last_info = get_ticker_info(ticker_input)
        loader.empty()
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN INTERFACE
# ════════════════════════════════════════════════════════════════════════════
col_t1, col_t2 = st.columns([1, 1])
t1_html = f"<div style='display:flex; align-items:center; gap:10px;'>{SVG_ICONS['Terminal']} <span>TERMINAL DASHBOARD</span></div>"
t2_html = f"<div style='display:flex; align-items:center; gap:10px;'>{SVG_ICONS['Briefcase']} <span>PORTFOLIO</span></div>"

tab_dash, tab_port = st.tabs([t1_html, t2_html])

with tab_dash:
    if 'last_df' not in st.session_state:
        st.info("System Ready. Please initialize a scan from the sidebar to load market data.")
    else:
        df, info = st.session_state.last_df, st.session_state.last_info
        ticker = st.session_state.last_ticker
        curr_price = float(df["Close"].iloc[-1])

        st.markdown(f"<div style='margin-bottom:1.5rem;'><span class='label'>{info['sector']}</span><br><span style='font-size:2rem; font-weight:800;'>{info['name']}</span> <span style='color:#3b82f6;' class='mono'>{ticker}</span></div>", unsafe_allow_html=True)

        # ── Patterns Section ──
        st.markdown("<span class='label'>AI Pattern Recognition</span>", unsafe_allow_html=True)
        p_col = st.container()
        with p_col:
            # Simple Pattern Logic Mockup
            st.markdown(f"""
            <div style="display:flex; margin-top:10px;">
                <div class="pattern-chip">{SVG_ICONS['Hammer']} <span class="mono" style="font-size:0.7rem;">Bullish Hammer</span></div>
                <div class="pattern-chip">{SVG_ICONS['ShootingStar']} <span class="mono" style="font-size:0.7rem;">Shooting Star</span></div>
                <div class="pattern-chip">{SVG_ICONS['Doji']} <span class="mono" style="font-size:0.7rem;">Neutral Doji</span></div>
            </div>
            """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="quant-card"><div class="label">Price</div><div class="value">${curr_price:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="quant-card"><div class="label">Balance</div><div class="value">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="quant-card"><div class="label">Units Owned</div><div class="value">{st.session_state.portfolio.get(ticker, 0)}</div></div>', unsafe_allow_html=True)

        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Transaction Control")
        qty = st.number_input("Unit Quantity", min_value=1, value=10)
        total_cost = qty * curr_price

        b1, b2 = st.columns(2)
        if b1.button("EXECUTE BUY ORDER"):
            if st.session_state.cash_balance >= total_cost:
                st.session_state.cash_balance -= total_cost
                st.session_state.portfolio[ticker] = st.session_state.portfolio.get(ticker, 0) + qty
                st.toast("ORDER FILLED", icon=SVG_ICONS['Check'])
                time.sleep(0.5)
                st.rerun()

        if b2.button("EXECUTE SELL ORDER"):
            if st.session_state.portfolio.get(ticker, 0) >= qty:
                st.session_state.cash_balance += total_cost
                st.session_state.portfolio[ticker] -= qty
                st.toast("ORDER FILLED", icon=SVG_ICONS['TrendDown'])
                time.sleep(0.5)
                st.rerun()

with tab_port:
    st.markdown(f"<div style='margin-bottom:1rem;'>{SVG_ICONS['Wallet']} <span class='label'>Active Assets</span></div>", unsafe_allow_html=True)
    for tkr, units in st.session_state.portfolio.items():
        if units > 0:
            st.markdown(f'<div class="quant-card" style="display:flex; justify-content:space-between; align-items:center;"><div><span class="mono" style="color:#3b82f6;">{tkr}</span></div><div class="value">{units} <span style="font-size:0.8rem; color:#64748b;">Units</span></div></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
<div style='text-align:center; opacity:0.6;'>
    <div style='display:inline-flex; align-items:center; gap:8px;'>
        {SVG_ICONS['Shield']} <span class='label' style='margin:0;'>Vector-Verified Terminal Logic</span>
    </div>
</div>
""", unsafe_allow_html=True)
