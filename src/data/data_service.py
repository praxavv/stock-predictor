import yfinance as yf
import pandas as pd
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600, show_spinner="Fetching market data...")
def get_stock_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical stock data from yfinance with caching.
    """
    try:
        logger.info(f"Downloading data for {ticker} (Period: {period}, Interval: {interval})")
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)

        if data.empty:
            logger.warning(f"No data found for ticker: {ticker}")
            return pd.DataFrame()

        # Handle MultiIndex columns (yfinance 0.2.x quirk)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Standardize columns
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)
        
        # Ensure standard OHLCV columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
             logger.error(f"Missing required columns in data for {ticker}")
             return pd.DataFrame()

        return data

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()

def validate_ticker(ticker: str) -> bool:
    """Check if a ticker exists and has recent data."""
    if not ticker:
        return False
    data = yf.download(ticker, period="5d", progress=False)
    return not data.empty
