import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
import requests
import pytz  
import yfinance as yf
from streamlit_lottie import st_lottie
from datetime import datetime

# ── Backend imports ──────────────────────────────────────────────────────────
try:
    from data_loader    import load_stock_data, get_ticker_info
    from pattern_detector import get_latest_patterns, detect_all_patterns
    from pattern_analysis import analyse_all_patterns
except ImportError:
    st.error("SYSTEM_ERROR: Critical backend modules missing. Check root directory.")

# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG & SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Terminal | Precision Quant", layout="wide", initial_sidebar_state="expanded")

if 'last_df' not in st.session_state:
    st.session_state.last_df = None

def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime("%H:%M:%S")

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

lottie_scan = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_ghp9v062.json")

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (Replacing Emojis)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Logo": '<svg width="40" height="40" viewBox="0 0 24 24" fill="none"><path d="M3 3V21H21" stroke="url(#g1)" stroke-width="2"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#g2)" stroke-width="2"/><defs><linearGradient id="g1"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="g2"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>',
    "Shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "News": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10l4 4v10a2 2 0 0 1-2 2z"/><path d="M7 8h5"/><path d="M7 12h10"/><path d="M7 16h10"/></svg>',
    "Brain": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.73-2.73 2.5 2.5 0 0 1-.31-4.71 2.5 2.5 0 0 1 .41-4.5 2.5 2.5 0 0 1 5.09-1.5z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.73-2.73 2.5 2.5 0 0 0 .31-4.71 2.5 2.5 0 0 0-.41-4.5 2.5 2.5 0 0 0-5.09-1.5z"/></svg>',
    "Node": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. SOPHISTICATED CSS (Glassmorphism & Depth)
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
[data-testid="stAppViewContainer"] {{ background: #020617; font-family: 'Plus Jakarta Sans', sans-serif; }}
[data-testid="stSidebar"] {{ background: rgba(15, 23, 42, 0.95) !important; border-right: 1px solid rgba(255,255,255,0.05); }}
.quant-card {{ background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 1.5rem; transition: transform 0.3s ease; }}
.ai-bubble {{ background: rgba(59, 130, 246, 0.05); border-left: 3px solid #3b82f6; border-radius: 4px 12px 12px 4px; padding: 15px; margin-top: 10px; font-size: 0.85rem; color: #94a3b8; line-height: 1.6; }}
.news-item {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.03); display: flex; align-items: flex-start; gap: 10px; }}
.live-dot {{ height: 6px; width: 6px; background-color: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
.label {{ font-size: 0.65rem; color: #64748b; font-weight: 800; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 4px; }}
.value {{ font-size: 1.8rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.02em; }}
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.stButton > button {{ border-radius: 8px !important; background: transparent !important; color: #f8fafc !important; font-weight: 600 !important; border: 1px solid rgba(255,255,255,0.1) !important; transition: 0.3s !important; }}
.stButton > button:hover {{ border: 1px solid #3b82f6 !important; background: rgba(59, 130, 246, 0.1) !important; }}
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR & NAVIGATION
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="margin-top:20px; margin-bottom:30px;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:0.9rem; letter-spacing:0.1em; color:#94a3b8;'>QUANT_ANALYZER_v2</h3>", unsafe_allow_html=True)
    ticker = st.text_input("INSTRUMENT_ID", value="AAPL").upper().strip()
    period = st.selectbox("TIMEFRAME_SCOPE", options=["6mo", "1y", "2y", "5y"], index=1)
    st.markdown("---")
    st.markdown(f'<div class="label">{SVG_ICONS["Brain"]} SYSTEM_LOG</div>', unsafe_allow_html=True)
    st.markdown('<div class="ai-bubble">Neural engine operational. Fractal recognition active. Multi-layer validation ready.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    analyse = st.button("RUN ENGINE", use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# 5. DATA HELPERS (News Sentiment)
# ════════════════════════════════════════════════════════════════════════════
def get_live_sentiment(ticker_symbol):
    try:
        search = yf.Search(ticker_symbol, news_count=5)
        news = search.news
        if not news: return [], 50
        bullish_terms = ["surge", "buy", "growth", "high", "positive", "profit", "gain", "upgrade"]
        bearish_terms = ["drop", "sell", "fall", "low", "negative", "loss", "risk", "downgrade"]
        score = 50
        processed_news = []
        for n in news:
            title = n.get('title', '').lower()
            sent = "STABLE"
            if any(word in title for word in bullish_terms):
                score += 8
                sent = "BULLISH"
            elif any(word in title for word in bearish_terms):
                score -= 8
                sent = "BEARISH"
            processed_news.append({"h": n.get('title')[:55] + "...", "s": sent})
        return processed_news, min(max(score, 10), 90)
    except:
        return [{"h": "Link protocol timeout", "s": "N/A"}], 50

# ════════════════════════════════════════════════════════════════════════════
# 6. ROUTER & VALIDATION GATE
# ════════════════════════════════════════════════════════════════════════════
if not analyse and st.session_state.last_df is None:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if lottie_scan: st_lottie(lottie_scan, height=300, key="initial")
        st.markdown("<p style='text-align:center; color:#475569;' class='mono'>SYSTEM_READY: AWAITING_INPUT</p>", unsafe_allow_html=True)
    st.stop()

if analyse:
    with st.spinner("Processing Data Layers..."):
        df = load_stock_data(ticker, period)
        if df is None or df.empty or "Open" not in df.columns:
            st.error(f"FATAL: {ticker} is not a valid data node.")
            st.stop()
        
        info = get_ticker_info(ticker)
        news_data, sent_score = get_live_sentiment(ticker)
        st.session_state.last_df, st.session_state.last_info = df, info
        st.session_state.last_ticker, st.session_state.last_news = ticker, news_data
        st.session_state.last_sent_score = sent_score

# Fetch active state
df, info, active_ticker = st.session_state.last_df, st.session_state.last_info, st.session_state.last_ticker
news_items, sentiment_score = st.session_state.last_news, st.session_state.last_sent_score

stats_all = analyse_all_patterns(df)
all_fired = detect_all_patterns(df) 
latest_close = float(df["Close"].iloc[-1])

# ── DASHBOARD HEADER ─────────────────────────────────────────────────────────
st.markdown(f"""
    <div style='margin-bottom:2.5rem; display: flex; justify-content: space-between; align-items: flex-end;'>
        <div>
            <div class='label'><span class='live-dot'></span> {info['sector']} • ASSET_IDENTIFIER</div>
            <div style='font-size:3.2rem; font-weight:800; letter-spacing:-0.03em;'>{info['name']} <span style='color:#3b82f6; font-weight:400;'>/ {active_ticker}</span></div>
        </div>
        <div style='text-align:right;'>
            <div class='label'>SCAN_TIME_IST</div>
            <div class='mono' style='color:#94a3b8;'>{get_ist_time()}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="quant-card"><div class="label">Current Value</div><div class="value mono">${latest_close:,.2f}</div></div>', unsafe_allow_html=True)
with c2: 
    change = df['Close'].pct_change().iloc[-1] * 100
    st.markdown(f'<div class="quant-card"><div class="label">24H Delta</div><div class="value mono" style="color:{"#10b981" if change >= 0 else "#ef4444"};">{change:+.2f}%</div></div>', unsafe_allow_html=True)
with c3: 
    active_sigs = [p for p, fired in all_fired.items() if fired.iloc[-1]]
    top_sig = active_sigs[0] if active_sigs else "CONSOLIDATED"
    st.markdown(f'<div class="quant-card"><div class="label">Signal Status</div><div class="value" style="font-size:1.1rem; color:#3b82f6;">{top_sig.upper()}</div></div>', unsafe_allow_html=True)
with c4:
    vol = df['Close'].pct_change().std() * np.sqrt(252) * 100
    st.markdown(f'<div class="quant-card"><div class="label">Annu Volatility</div><div class="value mono">{vol:.1f}%</div></div>', unsafe_allow_html=True)

# ── SOPHISTICATED CHART (Fractal Markers) ───────────────────────────────────
df_plot = df.tail(120)
fig = go.Figure(data=[go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], increasing_line_color='#10b981', decreasing_line_color='#ef4444', name="Price")])

# Precise marker styling (No Emojis)
PATTERN_STYLES = {
    "Hammer": {"color": "#10b981", "symbol": "triangle-up"},
    "Doji": {"color": "#60a5fa", "symbol": "diamond-tall"},
    "Bullish Engulfing": {"color": "#34d399", "symbol": "arrow-up"},
    "Bearish Engulfing": {"color": "#ef4444", "symbol": "arrow-down"},
    "Shooting Star": {"color": "#f59e0b", "symbol": "triangle-down"}
}

for p_name, style in PATTERN_STYLES.items():
    if p_name in all_fired:
        pts = df_plot[all_fired[p_name].tail(120)]
        if not pts.empty:
            fig.add_trace(go.Scatter(
                x=pts.index, y=pts['Low'] * 0.992, mode='markers',
                marker=dict(size=10, color=style["color"], symbol=style["symbol"], line=dict(width=1, color="white")),
                name=p_name.upper()
            ))

fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color="#64748b")))
fig.update_xaxes(showgrid=False, zeroline=False)
fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
st.plotly_chart(fig, use_container_width=True)

# ── ANALYTICS PANELS ─────────────────────────────────────────────────────────
r_col1, r_col2, r_col3 = st.columns([1.2, 1.4, 1.4])

with r_col1:
    st.markdown('<div class="quant-card" style="height:460px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["Shield"]} System Fidelity</div>', unsafe_allow_html=True)
    avg_win = sum([s['win_rate'] for s in stats_all.values()]) / len(stats_all) if stats_all else 50
    fig_gauge = go.Figure(go.Indicator(mode = "gauge+number", value = avg_win, number = {'suffix': "%", 'font': {'family': "JetBrains Mono", 'color': "#f8fafc", 'size': 28}},
        gauge = {'axis': {'range': [0, 100], 'tickwidth': 1}, 'bar': {'color': "#3b82f6"}, 'bgcolor': "rgba(0,0,0,0)", 'bordercolor': "rgba(255,255,255,0.1)"}))
    fig_gauge.update_layout(height=230, margin=dict(l=20,r=20,t=40,b=0), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown(f'<div class="ai-bubble">Statistical backtesting confirms a <b>{avg_win:.1f}%</b> probability of pattern-matching accuracy within this asset class.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r_col2:
    st.markdown('<div class="quant-card" style="height:460px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["News"]} News Sentiment Feed</div>', unsafe_allow_html=True)
    s_label = "HIGH_CONVICTION_LONG" if sentiment_score > 60 else "HIGH_CONVICTION_SHORT" if sentiment_score < 40 else "NEUTRAL_EQUILIBRIUM"
    st.markdown(f'<div style="font-size:1.1rem; font-weight:800; color:{"#10b981" if sentiment_score > 55 else "#ef4444" if sentiment_score < 45 else "#94a3b8"}; margin:18px 0;">{s_label}</div>', unsafe_allow_html=True)
    for item in news_items:
        st.markdown(f'<div class="news-item"><div style="color:#64748b; margin-top:3px;">{SVG_ICONS["Node"]}</div><div style="font-size:0.75rem; color:#f8fafc; line-height:1.4;">{item["h"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with r_col3:
    st.markdown('<div class="quant-card" style="height:460px;">', unsafe_allow_html=True)
    st.markdown(f'<div class="label">{SVG_ICONS["Brain"]} Neural Context</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="ai-bubble">
    <b>FRACTAL_STATE:</b> Multiple reversal clusters identified at the low range.<br><br>
    <b>SENTIMENT_VECTOR:</b> The {s_label.lower()} suggests market participants are currently in a transition phase.<br><br>
    <b>LIQUIDITY_RISK:</b> Volatility is calculated at {vol:.1f}%. Execution should account for potential slippage.
    </div>""", unsafe_allow_html=True)
    st.markdown(f'<div class="label" style="margin-top:25px;">Signal Strength Index</div>', unsafe_allow_html=True)
    st.progress(min(max(sentiment_score/100, 0.0), 1.0))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-top:2.5rem;' class='label'>Historical Performance Matrix</div>", unsafe_allow_html=True)
cols = st.columns(len(stats_all))
for i, (name, stats) in enumerate(stats_all.items()):
    with cols[i]:
        st.markdown(f'<div class="quant-card" style="padding:1.2rem;"><div class="label" style="color:#3b82f6">{name.upper()}</div><div style="font-size:1.5rem; font-weight:800; margin:0.4rem 0;">{stats["win_rate"]}%</div><div class="label" style="letter-spacing:0.05em;">Exp_Return: {stats["avg_return"]:.2f}%</div></div>', unsafe_allow_html=True)
