# 🧪 Pranav's Lab | Next-Gen Alpha Generation & Risk Management

**Pranav's Lab** is a sophisticated, high-performance financial research environment designed for quantitative analysis, strategy validation, and experimental market intelligence. It bridges the gap between raw data engineering and institutional-grade trading insights through a modular, scalable Python architecture.

---

## 🚀 Key Innovation: Hybrid AI Orchestration

The platform employs a multi-layered AI approach, moving beyond simple automation to contextual market reasoning:

1.  **Alpha Prediction Engine (ML)**:
    - **Algorithmic Core**: Utilizes a `RandomForestClassifier` (via Scikit-Learn) with optimized hyperparameters for binary classification of price direction.
    - **High-Dimensional Feature Engineering**: Data is molded through an 8-feature vector calculation including **MA20/50**, **RSI (14)**, **MACD/Signal Line**, and **Bollinger Band** volatility metrics.
    - **Validation Strategy**: Implements a strict time-based split (non-shuffled) for training, ensuring zero look-ahead bias and realistic historical accuracy metrics.

2.  **Contextual Reasoning (LLM)**:
    - **Integration**: Local LLM orchestration via **Ollama (Gemma:2B)**.
    - **Function**: Interprets high-density technical datasets into human-readable narrative analysis, providing a virtual "AI Analyst" layer that bridges the gap between metrics and conviction.

---

## 🏗️ System Architecture & Data Engineering

Built with a focus on data integrity and modularity:

### 📡 Resilient Data Pipeline
- **API Integration**: Deeply integrated with `yfinance` for global market coverage (US & India).
- **Fault-Tolerant Ingestion**: Features a multi-stage fallback mechanism (Download -> History -> Period Scaling) to ensure data continuity even during API instability.
- **High-Efficiency Caching**: Leverages Streamlit's `@st.cache_data` with TTL-based management for optimized memory usage and sub-second dashboard refreshes.

### 🧪 Algorithmic & Paper Trading Engine
- **Vectorized Analytics**: All technical indicators and strategy returns are computed using vectorized **Pandas** and **NumPy** operations for maximum performance on large datasets.
- **Backtesting Suite**: Institutional-grade evaluation engine calculating **Sharpe Ratio**, **Max Drawdown**, **Win Rate**, and **Annualized Volatility**.
- **Paper Trading Stack**: A full-stack simulator featuring:
    - **Persistence**: Custom SQLite-backed database (`trading_lab.db`) with hashed authentication and JSON-serialized portfolio states.
    - **Real-time P&L**: Dynamic calculation of unrealized gains/losses against live batch-fetched market prices.

---

## 📊 Dashboard & Quantitative Interface

- **Market Intelligence Dashboard**: Real-time signal tracking with interactive Plotly candlestick overlays and technical metric cards.
- **Institutional Treemaps**: Sector-wide performance visualization with dynamic sizing (Market Cap vs. Cash Value) for US and Indian indices.
- **Strategy Lab**: A dedicated environment for simulating `MA_CROSS` and `BUY_AND_HOLD` strategies across 1y to 10y historical lookbacks.
- **Account Management**: Secure, persistent user sessions with encrypted credential handling.

---

## 🛠️ Tech Stack

- **Core**: Python 3.9+
- **Frontend**: [Streamlit](https://streamlit.io/) (VC-Polish Dark Theme)
- **Data & Algos**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [yfinance](https://github.com/ranaroussi/yfinance)
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/)
- **AI Engine**: [Ollama](https://ollama.ai/) (Gemma:2B)
- **Visuals**: [Plotly](https://plotly.com/python/)
- **Persistence**: SQLite (v3)

---

## 🚀 Getting Started

1.  **Environment Setup**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **AI Analyst (Optional)**:
    - Install [Ollama](https://ollama.ai/)
    - Run `ollama run gemma:2b`

3.  **Launch the Lab**:
    ```bash
    streamlit run app/app.py
    ```

---
*Developed by Pranav as a rigorous environment for financial innovation and experimental data science.*
