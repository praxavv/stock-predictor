import pandas as pd
import numpy as np

def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate common technical indicators for stock data.
    """
    if data.empty:
        return data

    df = data.copy()

    # Trend Indicators: Moving Averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # Momentum: RSI
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / (avg_loss + 1e-10) # Avoid division by zero
    df['RSI'] = 100 - (100 / (1 + rs))

    # Trend: MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Volatility: Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_std'] = df['Close'].rolling(window=20).std()
    df['BB_upper'] = df['BB_middle'] + (df['BB_std'] * 2)
    df['BB_lower'] = df['BB_middle'] - (df['BB_std'] * 2)

    # Returns & Performance
    df['Return_1D'] = df['Close'].pct_change(1)
    df['Cumulative_Return'] = (1 + df['Return_1D']).cumprod() - 1

    # Cleanup: remove initial NaN rows from rolling windows
    # df.dropna(inplace=True)

    return df

def get_latest_metrics(data: pd.DataFrame) -> dict:
    """Extract latest values for quick metrics."""
    if data.empty:
        return {}
    
    latest = data.iloc[-1]
    return {
        "price": latest['Close'],
        "change": latest['Return_1D'],
        "rsi": latest['RSI'],
        "macd": latest['MACD'],
        "ma20": latest['MA20'],
        "ma50": latest['MA50']
    }
