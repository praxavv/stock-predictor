# 📈 AlphaStream | Institutional-Grade Stock Intelligence

AlphaStream is a high-performance stock market analysis and strategy validation platform designed for quantitative analysts and institutional-grade traders. Built with a modular, scalable architecture, it provides real-time alpha generation, advanced technical analysis, and robust risk auditing.

## 💎 Core Capabilities

- **Alpha Generation Engine**: Leverages Random Forest machine learning to predict next-day price direction with confidence scoring.
- **Deep Technical Analysis**: Interactive Plotly-based charting with 10+ standard technical indicators (MAs, RSI, MACD, Bollinger Bands).
- **Strategy Backtester**: Professional-grade backtesting engine calculating Sharpe Ratio, Max Drawdown, Win Rate, and Annualized Volatility.
- **Multi-Market Support**: Built-in support for US (NASDAQ/NYSE) and Indian (NSE) market segments.
- **High-Fidelity UI**: Dark-themed, VC-ready interface optimized for clarity and rapid insight.

## 🏗 Architecture

The platform follows a clean, decoupled architecture:

- `app.py`: Main orchestration and entry point.
- `src/data/`: High-performance data fetching layer with memory-efficient caching.
- `src/indicators/`: Modular technical analysis and metric calculation.
- `src/models/`: Machine learning models for alpha prediction.
- `src/backtest/`: Quantitative strategy simulation and risk engine.
- `src/ui/`: Standardized component library and professional visualizations.

## 🚀 Getting Started

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Launch the Platform**:
    ```bash
    streamlit run app.py
    ```

## 🧪 Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Data Engine**: [Pandas](https://pandas.pydata.org/), [yfinance](https://github.com/ranaroussi/yfinance)
- **Visuals**: [Plotly](https://plotly.com/python/)
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/)

---
*Developed for excellence in financial technology.*
