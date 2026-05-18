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
    Fetch historical stock data from yfinance with multiple fallback mechanisms.
    Ensures that "No data available" is avoided by trying alternative fetch methods and periods.
    """
    try:
        logger.info(f"Downloading data for {ticker} (Period: {period}, Interval: {interval})")
        
        # Attempt 1: Standard yf.download
        data = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)

        # Fallback 1: If empty, try Ticker.history (sometimes more reliable for single tickers)
        if data is None or data.empty:
            logger.warning(f"yf.download returned empty for {ticker}. Trying Ticker.history fallback...")
            t = yf.Ticker(ticker)
            data = t.history(period=period, interval=interval)

        # Fallback 2: If still empty and a short period was requested, try a longer one
        if (data is None or data.empty) and period not in ["max", "10y", "5y"]:
            fallback_period = "1y" if period in ["1d", "5d", "1mo"] else "max"
            logger.warning(f"Still no data for {ticker} with {period}. Trying fallback period: {fallback_period}")
            data = yf.download(ticker, period=fallback_period, interval=interval, auto_adjust=True, progress=False)

        if data is None or data.empty:
            logger.error(f"Exhausted all fallbacks for {ticker}. No data found.")
            return pd.DataFrame()

        # Handle MultiIndex columns (yfinance 0.2.x quirk)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Standardize columns and index
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)
        
        # Clean up column names (strip any whitespace)
        data.columns = [str(col).strip() for col in data.columns]

        # Drop rows where critical data is NaN (often happens at the end of the DF for live/closed markets)
        data.dropna(subset=['Close'], inplace=True)

        # Ensure standard OHLCV columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # If some columns are missing, try to map them or fill if it's just 'Adj Close' vs 'Close'
        if 'Close' not in data.columns and 'Adj Close' in data.columns:
            data['Close'] = data['Adj Close']
            
        if not all(col in data.columns for col in required_cols):
             # Final attempt: if we have most data but missing something, don't just fail if we have Close
             if 'Close' in data.columns:
                 logger.warning(f"Missing some OHLCV columns for {ticker}, but 'Close' is present. Proceeding.")
                 # Fill missing required columns with Close price as a last resort to avoid "No data available"
                 for col in required_cols:
                     if col not in data.columns:
                         data[col] = data['Close'] if col != 'Volume' else 0
             else:
                 logger.error(f"Missing critical 'Close' column in data for {ticker}")
                 return pd.DataFrame()

        return data

    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=86400, show_spinner="Fetching company financials...")
def get_company_info(ticker_symbol: str) -> dict:
    """
    Fetch company information (Market Cap, Total Cash, etc.) with 24h caching.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        return {
            "marketCap": info.get("marketCap", 0),
            "totalCash": info.get("totalCash", 0),
            "longName": info.get("longName", ticker_symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown")
        }
    except Exception as e:
        logger.error(f"Error fetching info for {ticker_symbol}: {str(e)}")
        return {}

def validate_ticker(ticker: str) -> bool:
    """Check if a ticker exists and has recent data."""
    if not ticker:
        return False
    data = yf.download(ticker, period="5d", progress=False)
    return not data.empty
