import streamlit as st

# -------------------- MARKET CONFIG --------------------

MARKET_SEGMENTS = {
    "INDIA": [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS"
    ],
    "USA": [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",
        "TSLA", "NVDA", "BRK-B", "JPM", "V"
    ]
}

# -------------------- UI CONFIG --------------------

APP_TITLE = "Pranav's Lab"
APP_ICON = "🧪"

CHART_THEME = "plotly_dark"
COLOR_PALETTE = {
    "primary": "#00FFA3",
    "secondary": "#FF00E5",
    "background": "#0E1117",
    "text": "#E0E0E0"
}

# -------------------- ANALYTICS CONFIG --------------------

DEFAULT_PERIOD = "1mo"
DEFAULT_INTERVAL = "1d"
RSI_PERIOD = 14
MA_SHORT = 20
MA_LONG = 50
