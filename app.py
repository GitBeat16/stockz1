import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# ── Backend imports (unchanged) ──────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & PERSISTENCE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'trade_history' not in st.session_state:
    st.session_state.trade_history = []

WATCHLIST = ["AAPL", "TSLA", "NVDA", "BTC-USD", "ETH-USD", "AMD", "MSFT"]

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════².
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. UNIFIED GLOBAL CSS (Alignment & Theme Sync)
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

/* Main Body & Sidebar Sync */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #020617 !important;
    color: #f8fafc;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    border-right: 1px solid #1e293b;
    padding-top: 2rem;
}

/* Unified Button Alignment & Animation */
.stButton > button {
    width: 100%;
    background: linear-gradient(90deg, #2563eb, #10b981) !important;
    color: white !important;
    font-weight: 800 !important;
    padding: 0.7rem !important;
    border-radius: 10px !important;
    border: none !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
    display: flex;
    justify-content: center;
    align-items: center;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4);
    filter: brightness(1.1);
}

/* Containers */
.quant-card { background: rgba(30, 41, 59, 0.4); border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; }
.portfolio-card { background: rgba(30, 41, 59, 0.3); border: 1px dashed #334155; border-radius: 10px; padding: 15px; margin-bottom: 25px; }

/* Text & Typography */
.mono { font-family: 'JetBrains Mono', monospace; }
.label { font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 4px; }
.badge { display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; }
.bullish-badge { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.bearish-badge { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }

/* Ledger Row */
.ledger-row { border-bottom: 1px solid #1e293b; padding: 10px 0; font-size: 0.8rem; display: flex; justify-content: space-between; align-items: center; }

/* Input Alignment */
.stTextInput > div > div > input { background-color: #0f172a !important; color: white !important; border: 1px solid #1e293b !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR (Navigation Terminal)
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1.5rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    
    # Unified Wallet View
    total_val = sum([c * (st.session_state.last_df['Close'].iloc[-1] if 'last_df' in st.session_state else 0) for t, c in st.session_state.portfolio.items()])
    st.markdown(f"""<div class="portfolio-card">
        <div style="display:flex; align-items:center; gap:8px;">{SVG_ICONS['Wallet']} <span class="label">Net Liquidity</span></div>
        <div class="mono" style="font-size:1.4rem; font-weight:800; color:#f8fafc; margin-top:5px;">${(st.session_state.cash_balance + total_val):,.2f}</div>
        <div class="label" style="margin-top:10px; color:#3b82f6;">Cash: ${st.session_state.cash_balance:,.2f}</div>
    </div>""", unsafe_allow_html=True)
    
    ticker = st.text_input("ENTER TICKER", value="TSLA").upper().strip()
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
    
    # Sidebar Buttons Aligned in Columns
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1: analyze_click = st.button("RUN AI")
    with btn_col2: scan_click = st.button("SCAN")

# ════════════════════════════════════════════════════════════════════════════
# 5. MARKET SCANNER 
# ════════════════════════════════════════════════════════════════════════════
if scan_click:
    st.markdown("### 📡 Market Intelligence Scanner")
    for t in WATCHLIST:
        scan_df = load_stock_data(t, "1y")
        patterns = get_latest_patterns(scan_df)
        if patterns:
            sig = PATTERNS[patterns[0]]['signal']
            st.markdown(f"<div class='ledger-row'><span class='mono' style='font-weight:700; color:#3b82f6;'>{t}</span> <span class='badge {sig}-badge'>{patterns[0]}</span></div>", unsafe_allow_html=True)
    st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# 6. MAIN TERMINAL DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
if analyze_click or 'last_df' in st.session_state:
    if analyze_click:
        df = load_stock_data(ticker, "1y")
        st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, get_ticker_info(ticker), ticker

    df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
    latest_price = float(df["Close"].iloc[-1])
    patterns = get_latest_patterns(df)
    primary_p = patterns[0] if patterns else None
    shares_owned = st.session_state.portfolio.get(active_ticker, 0)

    # Risk Management Calculation
    sl_price = float(df["Low"].iloc[-1]) * 0.99
    risk_dollars = st.session_state.cash_balance * (risk_pct / 100)
    qty_calc = int(risk_dollars / (latest_price - sl_price)) if (latest_price - sl_price) > 0 else 0

    # Header Row
    st.markdown(f"""<div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1.5rem;">
        <div><div class="label">{info.get('sector', 'Quant Asset')}</div><h1 style="margin:0; font-size:2.8rem;">{info.get('name', active_ticker)}</h1></div>
        <div style="text-align:right;"><div class="label">Shares Held</div><div class="mono" style="font-size:1.5rem; color:#10b981;">{shares_owned}</div></div>
    </div>""", unsafe_allow_html=True)

    # Unified Action Console
    act1, act2, act3 = st.columns([1.5, 1, 1])
    with act1:
        st.markdown(f"""<div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); border-radius:12px; padding:15px; height:100%; display:flex; flex-direction:column; justify-content:center;">
            <div style="display:flex; align-items:center; gap:8px;">{SVG_ICONS['Shield']} <span class="label" style="color:#3b82f6;">Risk Sizer</span></div>
            <div class="mono" style="font-size:1.1rem; margin-top:5px;">Buy <b>{qty_calc}</b> | SL @ ${sl_price:.2f}</div>
        </div>""", unsafe_allow_html=True)
    with act2:
        if st.button(f"EXECUTE BUY ORDER"):
            total_cost = latest_price * qty_calc
            if st.session_state.cash_balance >= total_cost:
                st.session_state.cash_balance -= total_cost
                st.session_state.portfolio[active_ticker] = shares_owned + qty_calc
                st.session_state.trade_history.append({"time": datetime.now().strftime("%H:%M"), "t": active_ticker, "type": "BUY", "qty": qty_calc, "px": latest_price})
                st.rerun()
    with act3:
        if st.button("LIQUIDATE TOTAL"):
            if shares_owned > 0:
                st.session_state.cash_balance += (latest_price * shares_owned)
                st.session_state.portfolio[active_ticker] = 0
                st.session_state.trade_history.append({"time": datetime.now().strftime("%H:%M"), "t": active_ticker, "type": "SELL", "qty": shares_owned, "px": latest_price})
                st.rerun()

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Chart & Analytics Section
    col_chart, col_intel = st.columns([2, 1])
    with col_chart:
        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.add_hline(y=sl_price, line_dash="dash", line_color="#ef4444", annotation_text="QUANT SL")
        fig.update_layout(template="plotly_dark", height=420, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_intel:
        st.markdown("<div class='label' style='margin-bottom:10px;'>Active Intelligence</div>", unsafe_allow_html=True)
        if patterns:
            for p in patterns:
                sig = PATTERNS[p]['signal']
                st.markdown(f'<div class="badge {sig}-badge" style="margin-bottom:10px;">{p} Signal Found</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='background:rgba(30,41,59,0.3); padding:15px; border-radius:10px; border-left:4px solid #3b82f6;'><div class='label' style='color:#3b82f6;'>AI Explanation</div><div style='font-size:0.85rem; line-height:1.6; color:#cbd5e1;'>{build_ai_explanation(primary_p, analyse_all_patterns(df)[primary_p])}</div></div>", unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top:20px;' class='label'>Recent Session History</div>", unsafe_allow_html=True)
        for trade in reversed(st.session_state.trade_history[-5:]):
            c = "#10b981" if trade['type'] == "BUY" else "#ef4444"
            st.markdown(f"<div class='ledger-row'><span class='mono'>{trade['time']}</span> <span class='mono' style='font-weight:700;'>{trade['t']}</span> <span class='mono' style='color:{c}'>{trade['type']}</span> <span class='mono'>${trade['px']:.0f}</span></div>", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:3rem; color:#334155; font-size:0.65rem; letter-spacing:0.2em;'>QUANT TERMINAL V8.0 • FULLY ALIGNED CORE</div>", unsafe_allow_html=True)
