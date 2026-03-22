import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Hammer": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 2h8v4H8z"/></svg>',
    "Doji": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M4 12h16"/></svg>',
    "Bullish Engulfing": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="10" width="6" height="10" fill="currentColor"/><rect x="14" y="4" width="6" height="18" fill="none" stroke="currentColor"/></svg>',
    "Bearish Engulfing": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="6" height="18" fill="none" stroke="currentColor"/><rect x="14" y="10" width="6" height="10" fill="currentColor"/></svg>',
    "Shooting Star": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 18h8v4H8z"/></svg>',
    "Default": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 3V21H21" stroke="url(#paint0_linear)" stroke-width="2" stroke-linecap="round"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#paint1_linear)" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="paint0_linear" x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="paint1_linear" x1="7" y1="14" x2="20" y2="9" gradientUnits="userSpaceOnUse"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Wallet": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12c0 1.1.9 2 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z"/></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "Info": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. ADVANCED GLOBAL CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Plus Jakarta Sans', sans-serif; background-color: #020617; color: #f8fafc; }}
.quant-card {{ background: linear-gradient(145deg, rgba(30, 41, 59, 0.4), rgba(15, 23, 42, 0.4)); border: 1px solid rgba(51, 65, 85, 0.5); border-radius: 12px; padding: 1.5rem; height: 100%; }}
.portfolio-box {{ background: rgba(30, 41, 59, 0.3); border: 1px dashed #334155; border-radius: 10px; padding: 12px; margin-bottom: 20px; }}
.risk-panel {{ background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 1.2rem; margin-bottom: 1rem; }}
.guide-panel {{ background: rgba(30, 41, 59, 0.2); border: 1px solid #1e293b; border-radius: 12px; padding: 2rem; margin-top: 3rem; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.label {{ font-size: 0.7rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; }}
.value {{ font-size: 1.75rem; font-weight: 800; margin-top: 0.25rem; }}
.stButton > button {{ width: 100%; background: linear-gradient(90deg, #2563eb, #10b981) !important; border: none !important; color: white !important; font-weight: 800 !important; padding: 0.6rem !important; border-radius: 8px !important; transition: all 0.2s; text-transform: uppercase; }}
.stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }}
.badge {{ display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; margin-bottom: 10px; }}
.bullish-badge {{ background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
.bearish-badge {{ background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
[data-testid="stSidebar"] {{ background-color: #020617; border-right: 1px solid #1e293b; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1rem;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.2rem;'>StockZ Terminal</h2>", unsafe_allow_html=True)
    
    st.markdown(f'<div class="portfolio-box"><div style="display:flex; align-items:center; gap:8px;">{SVG_ICONS["Wallet"]} <span class="label">Balance</span></div><div class="mono" style="font-size:1.2rem;">${st.session_state.cash_balance:,.2f}</div></div>', unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT", value="AAPL").upper().strip()
    period = st.selectbox("HISTORY", options=["6mo", "1y", "2y", "5y"], index=1)
    
    # RISK SETTINGS
    st.markdown("<div class='label' style='margin-top:1rem'>Risk Management</div>", unsafe_allow_html=True)
    risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    analyse = st.button("EXECUTE ANALYSIS")

# ════════════════════════════════════════════════════════════════════════════
# 5. MAIN UI LOGIC
# ════════════════════════════════════════════════════════════════════════════
if not analyse and 'last_df' not in st.session_state:
    st.markdown(f'<div style="height:70vh; display:flex; flex-direction:column; align-items:center; justify-content:center; opacity:0.6">{SVG_ICONS["Logo"]}<p class="label" style="margin-top:1rem">Awaiting Signal...</p></div>', unsafe_allow_html=True)
    st.stop()

if analyse or 'last_df' not in st.session_state:
    df = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)
    st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker = df, info, ticker

df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
stats_all = analyse_all_patterns(df)
latest_patterns = get_latest_patterns(df)
latest_close = float(df["Close"].iloc[-1])
daily_chg = (latest_close - float(df["Close"].iloc[-2])) / float(df["Close"].iloc[-2]) * 100
primary = latest_patterns[0] if latest_patterns else None
shares_owned = st.session_state.portfolio.get(active_ticker, 0)

# ── RISK CALCULATION ENGINE ──
current_low = float(df["Low"].iloc[-1])
stop_loss = current_low * 0.995 
risk_per_share = latest_close - stop_loss
dollar_risk = st.session_state.cash_balance * (risk_pct / 100)
suggested_shares = int(dollar_risk / risk_per_share) if risk_per_share > 0 else 0

# ── Header ──
st.markdown(f"<div><div class='label'>{info['sector']}</div><div style='font-size:2.5rem; font-weight:800;'>{info['name']} <span style='color:#3b82f6' class='mono'>{active_ticker}</span></div></div>", unsafe_allow_html=True)

# ── SMART RISK PANEL ──
r_col1, r_col2 = st.columns([2, 1])
with r_col1:
    st.markdown(f"""
    <div class="risk-panel">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">{SVG_ICONS['Shield']} <span class="label" style="color:#10b981;">Risk-Adjusted Sizing</span></div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:20px;">
            <div><div class="label">Suggested Shares</div><div class="mono" style="font-size:1.2rem; font-weight:700;">{suggested_shares}</div></div>
            <div><div class="label">Stop Loss</div><div class="mono" style="font-size:1.2rem; color:#ef4444;">${stop_loss:.2f}</div></div>
            <div><div class="label">Risk Amount</div><div class="mono" style="font-size:1.2rem;">${dollar_risk:,.2f}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with r_col2:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button(f"EXECUTE QUANT SIZE ({suggested_shares})"):
        cost = latest_close * suggested_shares
        if st.session_state.cash_balance >= cost:
            st.session_state.cash_balance -= cost
            st.session_state.portfolio[active_ticker] = shares_owned + suggested_shares
            st.rerun()
        else: st.warning("Insufficient Funds for this Risk Profile")
    if st.button("EXIT ALL POSITION"):
        st.session_state.cash_balance += (latest_close * shares_owned)
        st.session_state.portfolio[active_ticker] = 0
        st.rerun()

# ── KPI GRID ──
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="quant-card"><div class="label">Price</div><div class="value mono">{latest_close:,.2f}</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="quant-card"><div class="label">24H Delta</div><div class="value mono" style="color:{"#10b981" if daily_chg >=0 else "#ef4444"}">{daily_chg:.2f}%</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="quant-card"><div class="label">Active Pattern</div><div class="value" style="font-size:1.2rem; color:#3b82f6;">{primary if primary else "NONE"}</div></div>', unsafe_allow_html=True)
with c4:
    total_eq = sum([count * latest_close for t, count in st.session_state.portfolio.items()])
    st.markdown(f'<div class="quant-card"><div class="label">Net Worth</div><div class="value mono">${(st.session_state.cash_balance + total_eq):,.0f}</div></div>', unsafe_allow_html=True)

# ── Charts & Analysis ──
st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
col_left, col_right = st.columns([2, 1])
with col_left:
    chart_df = df.tail(120)
    fig = go.Figure(data=[go.Candlestick(x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444', increasing_fillcolor='rgba(16, 185, 129, 0.4)', decreasing_fillcolor='rgba(239, 68, 68, 0.4)')])
    fig.add_hline(y=stop_loss, line_dash="dash", line_color="#ef4444", annotation_text="Suggested SL")
    fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, yaxis=dict(side="right", gridcolor="#1e293b"))
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    if latest_patterns:
        for p in latest_patterns: st.markdown(f'<div class="badge {PATTERNS[p]["signal"]}-badge">{SVG_ICONS.get(p, SVG_ICONS["Default"])} {p}</div>', unsafe_allow_html=True)
        st.markdown(f"<div style='background:rgba(30,41,59,0.3); padding:1.2rem; border-radius:12px; border-left:4px solid #3b82f6;'><div class='label' style='color:#3b82f6;'>Quant Insight</div><div style='font-size:0.85rem; line-height:1.6; color:#cbd5e1'>{build_ai_explanation(primary, stats_all[primary])}</div></div>", unsafe_allow_html=True)
    else: st.markdown('<div style="padding:2rem; text-align:center; color:#475569;">No patterns detected</div>', unsafe_allow_html=True)

# ── ADVANCED BACKTEST STATS ──
st.markdown("<div style='height:40px'></div><div class='label'>Quant Performance Metrics</div>", unsafe_allow_html=True)
for name, stats in stats_all.items():
    with st.expander(f"{name} Analysis"):
        m1, m2, m3, m4 = st.columns(4)
        
        # 1. Occurrence Tracking
        m1.markdown(f"<div class='label'>Signals</div><div class='mono'>{stats['occurrences']}</div>", unsafe_allow_html=True)
        
        # 2. Win Rate
        m2.markdown(f"<div class='label'>Win Rate</div><div class='mono' style='color:#10b981'>{stats['win_rate']}%</div>", unsafe_allow_html=True)
        
        # 3. Average Return (Alpha)
        avg_r = stats.get('avg_return', 0)
        m3.markdown(f"<div class='label'>Avg 3D Edge</div><div class='mono'>{avg_r:+.2f}%</div>", unsafe_allow_html=True)
        
        # 4. Expectancy (E = (W * AvgW) - (L * AvgL))
        # Logic: Estimate Loss as 50% of the gain for rough expectancy modeling
        expectancy = (stats['win_rate']/100 * avg_r) - ((1 - stats['win_rate']/100) * abs(avg_r * 0.5))
        m4.markdown(f"<div class='label'>Expectancy</div><div class='mono' style='color:{'#10b981' if expectancy > 0 else '#ef4444'}'>{expectancy:.2f}R</div>", unsafe_allow_html=True)
        
        st.progress(stats['win_rate'] / 100)

# ════════════════════════════════════════════════════════════════════════════
# 6. PRODUCT GUIDE
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="guide-panel">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.5rem;">
        {SVG_ICONS['Info']}
        <span style="font-weight:800; font-size:1.1rem; letter-spacing:0.05em;">TERMINAL USER GUIDE</span>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:30px;">
        <div style="font-size:0.85rem; color:#94a3b8;">
            <p style="color:#f8fafc; font-weight:600; margin-bottom:8px;">1. SCANNING & ANALYSIS</p>
            Enter a ticker in the sidebar and click <b>EXECUTE ANALYSIS</b>. The system scans the chart for technical patterns like Hammers or Engulfing candles.
            <br><br>
            <p style="color:#f8fafc; font-weight:600; margin-bottom:8px;">2. RISK MANAGEMENT</p>
            The terminal calculates a technical <b>Stop Loss</b> based on the pattern low. Use the slider to define what % of your total cash you are willing to lose on one trade.
        </div>
        <div style="font-size:0.85rem; color:#94a3b8;">
            <p style="color:#f8fafc; font-weight:600; margin-bottom:8px;">3. PERFORMANCE PARAMETERS</p>
            <b>Expectancy:</b> The projected return per dollar risked. Values > 0 indicate a mathematically profitable strategy over time.
            <br><br>
            <p style="color:#f8fafc; font-weight:600; margin-bottom:8px;">4. EXECUTION</p>
            The <b>QUANT SIZE</b> button fills your order using the suggested shares. Tracking "Net Worth" allows you to see the real-time impact of volatility on your portfolio.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='text-align:center; padding:4rem 0; color:#334155; font-size:0.65rem;'>QUANT ANALYZER CORE v5.0 • POSITION SIZER ENABLED</div>", unsafe_allow_html=True)
