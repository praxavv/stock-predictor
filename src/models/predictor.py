import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Tuple, Dict

def prepare_features(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for training/prediction."""
    df = data.copy()
    
    # We assume indicators are already calculated in the data passed
    # If some are missing, this might fail, so we should be defensive
    required_features = [
        'MA20', 'MA50', 'RSI', 'MACD', 'Signal_Line',
        'Return_1D', 'BB_upper', 'BB_lower'
    ]
    
    # Add more features if missing but present in original core logic
    if 'Volatility' not in df.columns:
         df['Volatility'] = df['Close'].pct_change().rolling(10).std()
    
    features = required_features + ['Volatility']
    
    # Drop rows with NaNs only for these features
    df.dropna(subset=features, inplace=True)
    return df[features], df

def train_alpha_model(data: pd.DataFrame) -> Tuple[RandomForestClassifier, Dict]:
    """Train a Random Forest model for price direction."""
    if data.empty or len(data) < 100:
        return None, {}

    X_full, df = prepare_features(data)
    
    # Target: Direction (binary classification)
    # 1 if price goes up tomorrow, else 0
    y = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    # Align X and y
    X = X_full[:-1]
    y = y[:-1]
    
    # Time-based split (No shuffling)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    
    return model, {"accuracy": accuracy, "features": X.columns.tolist()}

def predict_signal(model, latest_data: pd.DataFrame) -> Dict:
    """Predict the next day's signal."""
    if model is None or latest_data.empty:
        return {"signal": "N/A", "confidence": 0.0}
    
    X_latest, _ = prepare_features(latest_data)
    if X_latest.empty:
         return {"signal": "N/A", "confidence": 0.0}
         
    latest_row = X_latest.iloc[-1:]
    
    prediction = model.predict(latest_row)[0]
    probabilities = model.predict_proba(latest_row)[0]
    
    confidence = probabilities[prediction]
    signal = "BULLISH" if prediction == 1 else "BEARISH"
    
    return {"signal": signal, "confidence": confidence}
