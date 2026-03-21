"""
app.py
AI Candlestick Pattern Analyzer — Ultra-High Fidelity Quant Terminal
----------------------------------------------------------------------
UI redesign only. All backend logic (data loading, pattern detection,
profitability analysis) is untouched.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Backend imports (unchanged) ──────────────────────────────────────────────
from data_loader      import load_stock_data, get_ticker_info
from pattern_detector import get_latest_patterns, PATTERNS
from pattern_analysis import analyse_all_patterns, build_ai_explanation


# ════════════════════════════════════════════════════════════════════════════
# 1. PAGE CONFIG
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Neural Terminal | AI Pattern Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════════════
# 2. VECTOR ART REPOSITORY (SVG Definitions)
# ════════════════════════════════════════════════════════════════════════════
SVG_ICONS = {
    "Hammer": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 2h8v4H8z"/></svg>',
    "Doji": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M4 12h16"/></svg>',
    "Bullish Engulfing": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="10" width="6" height="10" fill="currentColor"/><rect x="14" y="4" width="6" height="18" fill="none" stroke="currentColor"/></svg>',
    "Bearish Engulfing": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="6" height="18" fill="none" stroke="currentColor"/><rect x="14" y="10" width="6" height="10" fill="currentColor"/></svg>',
    "Shooting Star": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M8 18h8v4H8z"/></svg>',
    "Default": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
    "Logo": '<svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 3V21H21" stroke="url(#logo_grad)" stroke-width="2" stroke-linecap="round"/><path d="M7 14L11 10L15 14L20 9" stroke="url(#logo_grad_2)" stroke-width="2" stroke-linecap="round"/><defs><linearGradient id="logo_grad" x1="3" y1="3" x2="21" y2="21" gradientUnits="userSpaceOnUse"><stop stop-color="#3B82F6"/><stop offset="1" stop-color="#10B981"/></linearGradient><linearGradient id="logo_grad_2" x1="7" y1="14" x2="20" y2="9" gradientUnits="userSpaceOnUse"><stop stop-color="#60A5FA"/><stop offset="1" stop-color="#34D399"/></linearGradient></defs></svg>'
}

# ════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL CSS (Animations & Theming)
# ════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

/* ── Base Theme ── */
html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    background-color: #020617;
    color: #f8fafc;
}}

/* ── Custom Cards ── */
.quant-card {{
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.3), rgba(15, 23, 42, 0.4));
    backdrop-filter: blur(12px);
    border: 1px solid rgba(51, 65, 85, 0.4);
    border-radius: 16px;
    padding: 1.5rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}}
.quant-card:hover {{
    border-color: #3b82f6;
    background: rgba(30, 41, 59, 0.5);
    transform: translateY(-4px);
    box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.5);
}}

/* ── Typography ── */
.mono {{ font-family: 'JetBrains Mono', monospace; }}
.label {{ font-size: 0.725rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.5rem; }}
.value {{ font-size: 1.85rem; font-weight: 800; color: #f1f5f9; }}

/* ── Pattern Badges ── */
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 12px;
}}
.bullish-badge {{ background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }}
.bearish-badge {{ background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }}
.neutral-badge {{ background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }}

/* ── Animations ── */
@keyframes scan {{
    0% {{ transform: translateX(-100%); }}
    100% {{ transform: translateX(100%); }}
}}
.scan-container {{
    position: relative;
    height: 2px;
    background: rgba(30, 41, 59, 0.5);
    overflow: hidden;
    margin: 1.5rem 0;
}}
.scan-line {{
    position: absolute;
    width: 40%;
    height: 100%;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    animation: scan 3s linear infinite;
}}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {{
    background-color: #020617;
    border-right: 1px solid #1e293b;
}}
.stButton > button {{
    width: 100%;
    background: linear-gradient(135deg, #2563eb 0%, #10b981 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 800 !important;
    padding: 0.75rem !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
}}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 4. SIDEBAR USER CONTROLS
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding:1.5rem 0;">{SVG_ICONS["Logo"]}</div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; font-size:1.1rem; letter-spacing:0.1em;'>QUANT ENGINE</h2>", unsafe_allow_html=True)
    st.markdown("<div class='scan-container'><div class='scan-line'></div></div>", unsafe_allow_html=True)
    
    ticker = st.text_input("INSTRUMENT SYMBOL", value="AAPL").upper().strip()
    period = st.selectbox("LOOKBACK PERIOD", options=["6mo", "1y", "2y", "5y"], index=1)
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    analyse = st.button("RUN NEURAL ANALYSIS")

    st.markdown("<div class='label' style='margin-top:2.5rem'>Vector Legend</div>", unsafe_allow_html=True)
    legend_items = [
        ("Hammer", "#10b981"), 
        ("Doji", "#f59e0b"), 
        ("Bullish Engulfing", "#3b82f6"), 
        ("Bearish Engulfing", "#ef4444")
    ]
    for p_name, color in legend_items:
        st.markdown(f"""
            <div style='display:flex; align-items:center; gap:12px; margin-top:12px; opacity:0.7;'>
                <div style='color:{color}; transform:scale(0.8)'>{SVG_ICONS.get(p_name, SVG_ICONS["Default"])}</div>
                <span style='font-size:0.75rem;'>{p_name}</span>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 5. HEADER & INITIAL STATE
# ════════════════════════════════════════════════════════════════════════════
if not analyse:
    st.markdown(f"""
    <div style="height:75vh; display:flex; flex-direction:column; align-items:center; justify-content:center; opacity:0.4">
        {SVG_ICONS['Logo']}
        <p class='label' style='margin-top:1.5rem'>Ready for Deployment</p>
        <p style='font-size:0.8rem; color:#475569;'>Enter a ticker symbol to initialize analysis</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Backend Execution ────────────────────────────────────────────────────────
with st.spinner("Synchronizing with Neural Market Feed..."):
    df = load_stock_data(ticker, period)
    info = get_ticker_info(ticker)
    
    if df.empty:
        st.error("Connection Interrupted. Target Symbol Not Resolved.")
        st.stop()
        
    stats_all = analyse_all_patterns(df)
    latest_patterns = get_latest_patterns(df)

# ── KPI Calculations ────────────────────────────────────────────────────────
latest_close = float(df["Close"].iloc[-1])
prev_close = float(df["Close"].iloc[-2])
daily_chg = (latest_close - prev_close) / prev_close * 100
primary = latest_patterns[0] if latest_patterns else None

# Header Display
st.markdown(f"""
    <div style='margin-bottom:2.5rem;'>
        <div class='label'>{info['sector']} • {info['currency']} • {period} INTERVAL</div>
        <div style='font-size:2.25rem; font-weight:800; letter-spacing:-0.02em;'>
            {info['name']} <span style='color:#3b82f6; font-family:JetBrains Mono; font-weight:400;'>{ticker}</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 6. KPI DASHBOARD GRID
# ════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="quant-card">
        <div class="label">Settlement Price</div>
        <div class="value mono">{latest_close:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    color = "#10b981" if daily_chg >= 0 else "#ef4444"
    st.markdown(f"""<div class="quant-card">
        <div class="label">24H Volatility</div>
        <div class="value mono" style="color:{color}">{'+' if daily_chg > 0 else ''}{daily_chg:.2f}%</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="quant-card">
        <div class="label">Primary Signal</div>
        <div class="value" style="font-size:1.3rem; color:#3b82f6;">{primary if primary else "NEUTRAL"}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    accuracy = f"{stats_all[primary]['win_rate']}%" if primary else "N/A"
    st.markdown(f"""<div class="quant-card">
        <div class="label">Backtest Accuracy</div>
        <div class="value mono">{accuracy}</div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 7. INTERACTIVE CHARTING & ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
col_chart, col_intel = st.columns([2.2, 1])

with col_chart:
    st.markdown("<div class='label' style='margin-bottom:1rem'>Neural Price Action Feed</div>", unsafe_allow_html=True)
    chart_df = df.tail(120)
    
    fig = go.Figure()

    # 1. Main Candlestick with "Luminous" styling
    fig.add_trace(go.Candlestick(
        x=chart_df.index,
        open=chart_df['Open'], high=chart_df['High'],
        low=chart_df['Low'], close=chart_df['Close'],
        increasing_line_color='#10b981', decreasing_line_color='#ef4444',
        increasing_fillcolor='rgba(16, 185, 129, 0.2)', decreasing_fillcolor='rgba(239, 68, 68, 0.2)',
        name="Price Action",
        hovertemplate="<b>O:</b> %{open:.2f}<br><b>H:</b> %{high:.2f}<br><b>L:</b> %{low:.2f}<br><b>C:</b> %{close:.2f}<extra></extra>"
    ))

    # 2. Hover Interactions & Animations
    fig.update_layout(
        template="plotly_dark", height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.2)',
        xaxis=dict(
            rangeslider_visible=False, showgrid=True, gridcolor='rgba(51, 65, 85, 0.2)',
            showspikes=True, spikemode='across', spikesnap='cursor', spikedash='dash', spikecolor='#3b82f6', spikethickness=1,
        ),
        yaxis=dict(
            side="right", showgrid=True, gridcolor='rgba(51, 65, 85, 0.2)',
            showspikes=True, spikemode='across', spikesnap='cursor', spikedash='dash', spikecolor='#3b82f6', spikethickness=1,
            tickfont=dict(family='JetBrains Mono', size=10, color="#64748b")
        ),
        hoverlabel=dict(bgcolor="#1e293b", bordercolor="#3b82f6", font_size=13, font_family="JetBrains Mono"),
        hovermode="x unified",
    )

    # 3. Pattern Overlay Markers
    for name, stats in stats_all.items():
        fired = stats["fired_series"].loc[chart_df.index]
        hit_dates = fired[fired].index
        if not hit_dates.empty:
            fig.add_trace(go.Scatter(
                x=hit_dates, y=chart_df.loc[hit_dates, "High"] * 1.015,
                mode="markers",
                marker=dict(symbol="triangle-down", size=10, color="#3b82f6", line=dict(width=1, color="#ffffff")),
                name=name,
                hovertemplate=f"<b>{name}</b><br>Win Rate: {stats['win_rate']}%<extra></extra>"
            ))

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_intel:
    st.markdown("<div class='label' style='margin-bottom:1rem'>Live Signal Matrix</div>", unsafe_allow_html=True)
    if latest_patterns:
        for p in latest_patterns:
            sig = PATTERNS[p]["signal"]
            icon_svg = SVG_ICONS.get(p, SVG_ICONS["Default"])
            st.markdown(f'<div class="badge {sig}-badge">{icon_svg} {p} DETECTED</div>', unsafe_allow_html=True)
        
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        explanation = build_ai_explanation(primary, stats_all[primary])
        st.markdown(f"""
            <div style='background:rgba(30,41,59,0.3); padding:1.5rem; border-radius:16px; border-left:4px solid #3b82f6; border:1px solid rgba(51, 65, 85, 0.3);'>
                <div class='label' style='color:#3b82f6; margin-bottom:8px'>AI Interpretation</div>
                <div style='font-size:0.875rem; line-height:1.7; color:#cbd5e1'>{explanation}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='padding:3rem 1rem; text-align:center; color:#475569; border:1px dashed #1e293b; border-radius:16px;'>
                {SVG_ICONS["Default"]}
                <div style='font-size:0.8rem; margin-top:15px'>Scanning for Market Patterns...</div>
            </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# 8. BACKTEST STATISTICS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
st.markdown("<div class='label'>Historical Performance Ledger</div>", unsafe_allow_html=True)

for name, stats in stats_all.items():
    is_today = name in latest_patterns
    # Color-coded indicator for the expander
    color_border = "#3b82f6" if is_today else "rgba(51, 65, 85, 0.2)"
    
    with st.expander(f"{name.upper()} BACKTEST DATA {' (ACTIVE SIGNAL)' if is_today else ''}", expanded=is_today):
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<div class='label'>Signals Found</div><div class='mono' style='font-size:1.2rem'>{stats['occurrences']}</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<div class='label'>Win Rate</div><div class='mono' style='font-size:1.2rem; color:#10b981'>{stats['win_rate']}%</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<div class='label'>Avg 3D Return</div><div class='mono' style='font-size:1.2rem'>{stats['avg_return']:.2f}%</div>", unsafe_allow_html=True)
        
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.8rem; color:#94a3b8; font-style:italic;'>Insight: {build_ai_explanation(name, stats)}</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
    <div style='text-align:center; padding:5rem 0 3rem 0; color:#334155; font-size:0.65rem; letter-spacing:0.15em;'>
        NEURAL PATTERN ANALYZER v4.2.0 • TERMINAL ACCESS GRANTED • NO FINANCIAL ADVICE
    </div>
""", unsafe_allow_html=True)
