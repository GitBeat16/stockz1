<img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/chart-line.svg" width="32" height="32" /> StockZ Terminal
StockZ Terminal is a high-fidelity quantitative trading dashboard built with Streamlit. It merges real-time market data visualization with automated fractal pattern recognition and a simulated order execution engine.

Designed with a "Quant-Noir" aesthetic, the terminal provides a seamless interface for technical analysis, news sentiment tracking, and portfolio management.

⚡ Key Features
Fractal Pattern Engine: Automatically decodes market structures (Bullish Engulfing, Hammers, etc.) using historical OHLCV data.

Live Order Execution: A fully functional paper trading system with session-state persistence for tracking cash balances and positions.

AI Quant Suite: * Exposure Gauge: Dynamic visualization of portfolio risk.

Sentiment Analysis: Simulated news engine providing bullish/bearish scoring.

Statistical Backing: Real-time win-rate calculations for detected patterns.

Modern UX: Glass-morphism UI, custom SVG vector iconography, and smooth Lottie animations.

🛠️ Tech Stack
Frontend: Streamlit (Custom CSS3 & Glass-morphism)

Charts: Plotly Graph Objects

Analysis: Pandas, NumPy

Animation: Streamlit Lottie

Timezone: Pytz (Sync to IST/Asia Kolkata)

📂 Project Architecture
Plaintext
├── app.py                # Main Streamlit Dashboard logic
├── data_loader.py        # Financial data ingestion (yfinance/API)
├── pattern_detector.py   # Technical analysis & fractal logic
├── pattern_analysis.py   # AI reasoning & statistical win-rates
└── requirements.txt      # Project dependencies

🚀 Getting Started
1. Clone the repository
Bash
git clone https://github.com/GitBeat16/stockz1.git
cd stockz1
2. Install dependencies
Bash
pip install -r requirements.txt
3. Run the Terminal
Bash
streamlit run app.py

🛡️ System Protocols
Integrity: Pattern matching utilizes a 120-day fractal window.

Risk Management: Default risk profile is set to 1.0% per trade (adjustable in sidebar).

Vector Art: The system uses high-resolution inline SVGs for all telemetry and navigation icons.

📝 License
Distributed under the MIT License. See LICENSE for more information.

Note: This terminal is a simulation tool. All trading activity is performed with virtual "Paper Money" for educational and analytical purposes.
