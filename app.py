import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & THEME INITIALIZATION
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="TERMINAL v3", layout="wide", initial_sidebar_state="expanded")

# System State
for key, val in {"cash_balance": 100000.0, "portfolio": {}, "last_ticker": "AAPL"}.items():
    if key not in st.session_state: st.session_state[key] = val

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Unified System Theme)
# ════════════════════════════════════════════════════════════════════════════
SVG_LIB = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    "Terminal": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Pattern_Bull": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="18 15 12 9 6 15"/></svg>',
    "Pattern_Bear": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>',
    "Success": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>',
}

# ════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL CSS STYLING (Terminal Noir)
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');

    /* Global Overrides */
    .stApp {{ background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }}
    
    /* Grid Cards */
    .metric-card {{
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 10px;
        padding: 1.25rem;
        text-align: left;
    }}
    
    .label {{ font-family: 'JetBrains Mono'; font-size: 0.65rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.15em; }}
    .value {{ font-family: 'Inter'; font-size: 1.6rem; font-weight: 800; color: #f1f5f9; margin-top: 4px; }}
    
    /* Order Buttons */
    div.stButton > button {{
        width: 100%; border-radius: 6px; font-family: 'JetBrains Mono';
        transition: 0.2s all ease; border: 1px solid rgba(255,255,255,0.1);
        background: #0f172a; color: #f8fafc;
    }}
    div.stButton > button:hover {{ border-color: #3b82f6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.3); }}

    /* Custom Scrollbar */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: #020617; }}
    ::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 10px; }}

    /* Sidebar Logo */
    .sidebar-logo {{ display: flex; align-items: center; gap: 12px; padding: 10px 0 30px 0; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div class="sidebar-logo">{SVG_LIB["Logo"]} <span style="font-family:JetBrains Mono; font-weight:700; color:#3b82f6;">v3.0_QUANT</span></div>', unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT_ID", value=st.session_state.last_ticker).upper()
    
    if st.button("RUN ENGINE"):
        # Simulated loading animation
        bar = st.empty()
        for i in range(1, 11):
            bar.markdown(f'<div style="width:{i*10}%; height:2px; background:#3b82f6; transition:0.3s;"></div>', unsafe_allow_html=True)
            time.sleep(0.05)
        bar.empty()
        
        st.session_state.last_ticker = ticker
        # Mocking data update
        dates = pd.date_range(end=pd.Timestamp.now(), periods=50)
        st.session_state.df = pd.DataFrame({
            "Open": np.random.randn(50).cumsum() + 150,
            "High": np.random.randn(50).cumsum() + 155,
            "Low": np.random.randn(50).cumsum() + 145,
            "Close": np.random.randn(50).cumsum() + 150,
        }, index=dates)
        st.rerun()

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN INTERFACE
# ════════════════════════════════════════════════════════════════════════════
dash_label = f'<div style="display:flex; align-items:center; gap:8px;">{SVG_LIB["Terminal"]} DASHBOARD</div>'
port_label = f'<div style="display:flex; align-items:center; gap:8px;">{SVG_LIB["Wallet"]} PORTFOLIO</div>'

tab_dash, tab_port = st.tabs([dash_label, port_label])

with tab_dash:
    if 'df' not in st.session_state:
        st.markdown(f"<div style='padding:50px; text-align:center; color:#64748b;'>{SVG_LIB['Terminal']}<br><br>SYSTEM_IDLE: AWAITING_INPUT</div>", unsafe_allow_html=True)
    else:
        df = st.session_state.df
        price = df["Close"].iloc[-1]
        
        # Header Status
        st.markdown(f"<div style='margin-bottom:20px;'><span class='label'>Active Stream</span><br><h1 style='margin:0;'>{st.session_state.last_ticker} / USD</h1></div>", unsafe_allow_html=True)
        
        # Grid Metrics
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f'<div class="metric-card"><div class="label">Last Price</div><div class="value">${price:,.2f}</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="metric-card"><div class="label">Buying Power</div><div class="value">${st.session_state.cash_balance:,.0f}</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="metric-card"><div class="label">Position</div><div class="value">{st.session_state.portfolio.get(st.session_state.last_ticker, 0)} Units</div></div>', unsafe_allow_html=True)

        # Main Chart
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), 
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # Pattern Recognition Section
        st.markdown("<div style='margin:25px 0 10px 0;' class='label'>Detected Visual Patterns</div>", unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3)
        p1.markdown(f"<div style='display:flex; align-items:center; gap:10px; background:#0f172a; padding:10px; border-radius:6px; border:1px solid rgba(16, 185, 129, 0.2);'>{SVG_LIB['Pattern_Bull']} <span style='font-family:JetBrains Mono; font-size:0.8rem;'>Hammer_Bull</span></div>", unsafe_allow_html=True)
        p2.markdown(f"<div style='display:flex; align-items:center; gap:10px; background:#0f172a; padding:10px; border-radius:6px; border:1px solid rgba(239, 68, 68, 0.2);'>{SVG_LIB['Pattern_Bear']} <span style='font-family:JetBrains Mono; font-size:0.8rem;'>Head_Shoulders</span></div>", unsafe_allow_html=True)
        p3.markdown(f"<div style='display:flex; align-items:center; gap:10px; background:#0f172a; padding:10px; border-radius:6px; border:1px solid rgba(100, 116, 139, 0.2);'>{SVG_LIB['Terminal']} <span style='font-family:JetBrains Mono; font-size:0.8rem;'>Doji_Neutral</span></div>", unsafe_allow_html=True)

        # Execution
        st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
        with st.container():
            col_buy, col_sell = st.columns(2)
            if col_buy.button("CONFIRM BUY"):
                st.toast("ORDER_EXECUTED", icon=SVG_LIB['Success'])
            if col_sell.button("CONFIRM SELL"):
                st.toast("ORDER_EXECUTED", icon=SVG_LIB['Success'])

with tab_port:
    st.markdown("<div style='padding:20px;' class='label'>Holdings Overview</div>", unsafe_allow_html=True)
    if not any(v > 0 for v in st.session_state.portfolio.values()):
        st.markdown("<div style='text-align:center; padding:40px; color:#64748b;'>NO ACTIVE POSITIONS</div>", unsafe_allow_html=True)
    else:
        for tkr, units in st.session_state.portfolio.items():
            if units > 0:
                st.markdown(f'<div class="metric-card" style="margin-bottom:10px; display:flex; justify-content:space-between;"><span>{tkr}</span><span style="color:#3b82f6;">{units} UNITS</span></div>', unsafe_allow_html=True)

# Footer
st.markdown(f"<div style='text-align:center; margin-top:50px; opacity:0.5;'>{SVG_LIB['Shield']} <span class='label'>System Secure // Vector Optimized</span></div>", unsafe_allow_html=True)
