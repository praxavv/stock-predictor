# -------------------- MARKET CONFIG --------------------

MARKET_SEGMENTS = {
    "USA": {
        "Information Technology": ["AAPL", "MSFT", "NVDA", "AVGO", "ADBE", "CRM", "AMD", "QCOM"],
        "Financials": ["JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "BLK"],
        "Health Care": ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "PFE"],
        "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX"],
        "Consumer Staples": ["WMT", "PG", "COST", "KO", "PEP", "PM"],
        "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "TMUS", "VZ"],
        "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
        "Industrials": ["GE", "CAT", "HON", "UPS", "BA", "UNP"],
        "Materials": ["LIN", "SHW", "FCX", "APD", "NEM"],
        "Utilities": ["NEE", "SO", "DUK", "SRE", "AEP"],
        "Real Estate": ["PLD", "AMT", "EQIX", "CCI", "SPG"]
    },

    "INDIA": {
        "Information Technology": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS"],
        "Financials": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS"],
        "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "COALINDIA.NS", "BPCL.NS", "IOC.NS"],
        "Consumer Staples": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "VBL.NS", "TATACONSUM.NS"],
        "Consumer Discretionary": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "TITAN.NS", "ASIANPAINT.NS", "EICHERMOT.NS"],
        "Health Care": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS"],
        "Communication Services": ["BHARTIARTL.NS", "JIOFIN.NS", "IDEA.NS", "TATACOMM.NS"],
        "Materials": ["TATASTEEL.NS", "JSWSTEEL.NS", "ULTRACEMCO.NS", "HINDALCO.NS", "GRASIM.NS"],
        "Industrials": ["LT.NS", "ADANIENT.NS", "HAL.NS", "BEL.NS", "SIEMENS.NS", "ABB.NS"],
        "Utilities": ["ADANIGREEN.NS", "POWERGRID.NS", "ADANIPORTS.NS", "TATAPOWER.NS"],
        "Real Estate": ["DLF.NS", "LODHA.NS", "GODREJPROP.NS"]
    }
}

SECTOR_ORDER = [
    "Information Technology",
    "Financials",
    "Health Care",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Industrials",
    "Communication Services",
    "Utilities",
    "Real Estate",
    "Materials"
]

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
