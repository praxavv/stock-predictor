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
    """Add technical indicators safely, handle small datasets."""
    if data.empty:
        return data

    # Use shorter windows for small datasets
    ma_short = min(20, len(data)//2) if len(data) >= 5 else 2
    ma_long = min(50, len(data)//2) if len(data) >= 10 else 5
    rsi_period = min(14, len(data)-1)

    # Moving averages
    data['MA20'] = data['Close'].rolling(ma_short).mean()
    data['MA50'] = data['Close'].rolling(ma_long).mean()

    # Bollinger Bands
    rolling_std = data['Close'].rolling(ma_short).std()
    data['BB_upper'] = data['MA20'] + 2 * rolling_std
    data['BB_lower'] = data['MA20'] - 2 * rolling_std

    # RSI
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
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

    # Drop only rows where all indicators are NaN
    data.dropna(subset=['MA20', 'MA50', 'RSI', 'MACD', 'Signal_Line', 'Momentum', 'Volatility'], inplace=True)
    return data

def predict_next_close(data):
    """Predict next closing price using Random Forest."""
    if data.empty or len(data) < 2:
        return None  # Not enough data

    features = ['MA20', 'MA50', 'RSI', 'MACD', 'Signal_Line', 'Momentum', 'Volatility']
    df = data.dropna(subset=features).copy()
    
    if len(df) < 2:
        # Fallback: use last close
        return float(df['Close'].iloc[-1])

    # Target = tomorrow's close
    df['Target'] = df['Close'].shift(-1)
    df = df.dropna(subset=['Target'])

    if df.empty:
        return float(data['Close'].iloc[-1])

    X = df[features]
    y = df['Target']

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)

    next_features = X.iloc[[-1]]
    predicted_price = model.predict(next_features)[0]
    return float(predicted_price)

def get_signal(data):
    """Generate Buy/Sell/Hold signal safely."""
    if data.empty or len(data) < 1:
        return "No Signal"

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

def intraday_net_profit(buy_price, sell_price, qty):
    turnover = (buy_price + sell_price) * qty

    # Brokerage (₹20 or 0.03% per order)
    brokerage_buy = min(20, 0.0003 * (buy_price * qty))
    brokerage_sell = min(20, 0.0003 * (sell_price * qty))
    brokerage = brokerage_buy + brokerage_sell

    # STT (0.025% on SELL only)
    stt = 0.00025 * (sell_price * qty)

    # Exchange Transaction Charges (~0.00345% total)
    etc = 0.0000345 * turnover

    # SEBI turnover fee (₹10 per crore = 0.000001)
    sebi = 0.000001 * turnover

    # Stamp duty (0.003% on buy side only)
    stamp_duty = 0.00003 * (buy_price * qty)

    # GST (18% on brokerage + etc + sebi)
    gst = 0.18 * (brokerage + etc + sebi)

    charges = brokerage + stt + etc + sebi + stamp_duty + gst

    gross_profit = (sell_price - buy_price) * qty
    net_profit = gross_profit - charges

    return {
        "gross_profit": round(gross_profit, 2),
        "charges": round(charges, 2),
        "net_profit": round(net_profit, 2)
    }
    
