import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Backend imports (unchanged) ──────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | AI Pattern Analyzer", layout="wide", initial_sidebar_state="expanded")

if 'cash_balance' not in st.session_state:
    st.session_state.cash_balance = 100000.0
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# Watchlist for the Scanner
WATCHLIST = ["AAPL", "MSFT", "TSLA", "NVDA", "GOOGL", "AMZN", "META", "AMD", "BTC-USD", "ETH-USD"]

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Hammer": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M8 2h8v4H8z"/></svg>',
    "Doji": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M4 12h16"/></svg>',
    "Bullish Engulfing": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="10" width="6" height="10" fill="currentColor"/><rect x="14" y="4" width="6" height="18" fill="none" stroke="currentColor"/></svg>',
    "Bearish Engulfing": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="6" height="18" fill="none" stroke="currentColor"/><rect x="14" y="10" width="6" height="10" fill="currentColor"/></svg>',
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Scanner": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3M11 8v6M8 11h6"/></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }
.quant-card { background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(51, 65, 85, 0.5); border-radius: 12px; padding: 1.5rem; }
.scan-row { background: rgba(30, 41, 59, 0.2); border: 1px solid rgba(51, 65, 85, 0.3); border-radius: 8px; padding: 10px; margin-bottom: 8px; transition: 0.2s; }
.scan-row:hover { border-color: #3b82f6; background: rgba(30, 41, 59, 0.4); }
.mono { font-family: 'JetBrains Mono', monospace; }
.label { font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }
.stButton > button { width: 100%; background: linear-gradient(90deg, #2563eb, #10b981) !important; border: none !important; color: white !important; font-weight: 800 !important; border-radius: 8px !important; transition: 0.2s; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }
.badge { display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }
.bullish-badge { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
.bearish-badge { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(30,41,59,0.3); border:1px dashed #334155; border-radius:10px; padding:12px; margin-bottom:20px;"><div style="display:flex; align-items:center; gap:8px; color:#64748b;">{SVG_ICONS["Wallet"]} <span class="label">Balance</span></div><div class="mono" style="font-size:1.2rem; color:#f8fafc;">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    
    ticker = st.text_input("SINGLE INSTRUMENT", value="AAPL").upper().strip()
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    run_analysis = st.button("ANALYZE TICKER")
    
    st.markdown("---")
    st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:10px;'>{SVG_ICONS['Scanner']} <span class='label'>Market Scanner</span></div>", unsafe_allow_html=True)
    run_scan = st.button("SCAN WATCHLIST")

# ════════════════════════════════════════════════════════════════════════════
# 5. SCANNER LOGIC
# ════════════════════════════════════════════════════════════════════════════
if run_scan:
    st.markdown("### 📡 Global Market Intelligence")
    cols = st.columns(1)
    with st.status("Scanning Liquidity Pools...", expanded=True) as status:
        found_signals = []
        for t in WATCHLIST:
            scan_df = load_stock_data(t, "1y")
            if not scan_df.empty:
                patterns = get_latest_patterns(scan_df)
                if patterns:
                    found_signals.append({"ticker": t, "price": scan_df['Close'].iloc[-1], "patterns": patterns})
        status.update(label="Scan Complete", state="complete", expanded=False)

    if found_signals:
        for s in found_signals:
            p_name = s['patterns'][0]
            sig_type = PATTERNS[p_name]['signal']
            st.markdown(f"""
            <div class="scan-row" style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:20px;">
                    <b class="mono" style="font-size:1.1rem; color:#3b82f6; width:80px;">{s['ticker']}</b>
                    <span class="mono" style="color:#64748b;">${s['price']:.2f}</span>
                </div>
                <div class="badge {sig_type}-badge">{p_name} detected</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No patterns detected in current watchlist candle.")
    st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# 6. MAIN ANALYSIS LOGIC
# ════════════════════════════════════════════════════════════════════════════
if run_analysis or 'last_df' in st.session_state:
    if run_analysis:
        with st.spinner("Decoding Ticker..."):
            df = load_stock_data(ticker, "1y")
            info = get_ticker_info(ticker)
            st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

    df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
    latest_patterns = get_latest_patterns(df)
    latest_close = float(df["Close"].iloc[-1])
    primary = latest_patterns[0] if latest_patterns else None
    shares_owned = st.session_state.portfolio.get(active_ticker, 0)
    
    # Position Sizing Logic
    stop_loss = float(df["Low"].iloc[-1]) * 0.99
    risk_amt = st.session_state.cash_balance * (risk_pct / 100)
    pos_size = int(risk_amt / (latest_close - stop_loss)) if latest_close > stop_loss else 0

    # UI Layout
    st.markdown(f"<div><div class='label'>{info.get('sector', 'Asset')}</div><div style='font-size:2rem; font-weight:800;'>{info.get('name', active_ticker)} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div></div>", unsafe_allow_html=True)
    
    # Risk Console
    t1, t2 = st.columns([2, 1])
    with t1:
        st.markdown(f"""<div style="background:rgba(16,185,129,0.05); border:1px solid rgba(16,185,129,0.2); border-radius:12px; padding:15px; display:flex; justify-content:space-around; align-items:center;">
            <div><div class='label'>Quant Size</div><div class='mono' style='font-size:1.2rem;'>{pos_size} Units</div></div>
            <div><div class='label'>Stop Loss</div><div class='mono' style='font-size:1.2rem; color:#ef4444;'>${stop_loss:.2f}</div></div>
            <div><div class='label'>Risk Per Trade</div><div class='mono' style='font-size:1.2rem;'>${risk_amt:,.2f}</div></div>
        </div>""", unsafe_allow_html=True)
    with t2:
        if st.button(f"EXECUTE BUY ({pos_size})"):
            if st.session_state.cash_balance >= (latest_close * pos_size):
                st.session_state.cash_balance -= (latest_close * pos_size)
                st.session_state.portfolio[active_ticker] = shares_owned + pos_size
                st.rerun()
        if st.button("LIQUIDATE POSITION"):
            st.session_state.cash_balance += (latest_close * shares_owned)
            st.session_state.portfolio[active_ticker] = 0
            st.rerun()

    # Chart & Intelligence
    c_left, c_right = st.columns([2, 1])
    with c_left:
        fig = go.Figure(data=[go.Candlestick(x=df.tail(60).index, open=df.tail(60)['Open'], high=df.tail(60)['High'], low=df.tail(60)['Low'], close=df.tail(60)['Close'])])
        fig.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444")
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
    with c_right:
        st.markdown("<div class='label'>Intelligence Feed</div>", unsafe_allow_html=True)
        if latest_patterns:
            for p in latest_patterns: st.markdown(f'<div class="badge {PATTERNS[p]["signal"]}-badge" style="margin-bottom:8px;">{p}</div>', unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.85rem; color:#cbd5e1; background:rgba(30,41,59,0.3); padding:10px; border-radius:8px;'>{build_ai_explanation(primary, analyse_all_patterns(df)[primary])}</div>", unsafe_allow_html=True)
        else: st.markdown("<div style='color:#475569; font-size:0.8rem;'>Scanning for alpha...</div>", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding-top:40px; color:#334155; font-size:0.6rem;'>TERMINAL v6.0 • MULTI-TICKER SCANNER ENABLED</div>", unsafe_allow_html=True)
