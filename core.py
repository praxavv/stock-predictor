# core.py
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def get_stock_data(ticker, period, interval):
    """Fetch clean, adjusted stock data."""
    data = yf.download(ticker, period=period, interval=interval, auto_adjust=True)
    if data.empty:
        return None
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data.dropna(inplace=True)
    return data

def calculate_indicators(data):
    """Add richer technical indicators."""
    # Moving averages
    data['MA20'] = data['Close'].rolling(20).mean()
    data['MA50'] = data['Close'].rolling(50).mean()

    # Bollinger Bands
    rolling_std = data['Close'].rolling(20).std()
    data['BB_upper'] = data['MA20'] + 2 * rolling_std
    data['BB_lower'] = data['MA20'] - 2 * rolling_std

    # RSI
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # MACD and Signal Line
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Momentum and Volatility
    data['Momentum'] = data['Close'].pct_change(4)
    data['Volatility'] = data['Close'].pct_change().rolling(10).std()

    data.dropna(inplace=True)
    return data

def predict_next_close(data):
    """Predict next closing price using Random Forest on technical indicators."""
    features = ['MA20', 'MA50', 'RSI', 'MACD', 'Signal_Line', 'Momentum', 'Volatility']
    data = data.dropna(subset=features)
    X = data[features]
    y = data['Close']
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    next_features = X.iloc[[-1]]
    predicted_price = model.predict(next_features)[0]
    return predicted_price

def get_signal(data):
    """Improved signal logic: blend of trend, RSI, MACD."""
    latest = data.iloc[-1]
    signals = []

    if latest['MA20'] > latest['MA50']:
        signals.append("Buy")
    if latest['MACD'] > latest['Signal_Line']:
        signals.append("Buy")
    if latest['RSI'] < 30:
        signals.append("Buy")

    if latest['MA20'] < latest['MA50']:
        signals.append("Sell")
    if latest['MACD'] < latest['Signal_Line']:
        signals.append("Sell")
    if latest['RSI'] > 70:
        signals.append("Sell")

    if not signals:
        return "Hold"
    return max(set(signals), key=signals.count)
