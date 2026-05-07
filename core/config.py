import streamlit as st

# -------------------- MARKET CONFIG --------------------

MARKET_SEGMENTS = {
    "USA": {
        "Technology": [
            "AAPL", "MSFT", "NVDA", "AMD", "GOOGL"
        ],
        "Finance": [
            "JPM", "BAC", "GS", "V", "MA"
        ],
        "Consumer": [
            "AMZN", "WMT", "COST", "KO"
        ],
        "EV & Auto": [
            "TSLA", "F"
        ]
    },

    "INDIA": {
        "IT": [
            "TCS.NS", "INFY.NS", "WIPRO.NS"
        ],
        "Banking": [
            "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"
        ],
        "Energy": [
            "RELIANCE.NS", "ONGC.NS"
        ],
        "Consumer": [
            "HINDUNILVR.NS", "ITC.NS"
        ]
    }
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
