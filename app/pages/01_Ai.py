import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, "app"))

import streamlit as st

from core.analytics.data_service import get_stock_data
from core.analytics.technical import (
    calculate_technical_indicators,
    get_latest_metrics
)
from core.prediction.predictor import (
    train_alpha_model,
    predict_signal
)
from components.components import render_sidebar
from core.ai_engine import ask_ai

st.set_page_config(page_title="Pranav's Lab", layout="wide")

ticker, market = render_sidebar()

data = get_stock_data(ticker)

data = calculate_technical_indicators(data)

latest_metrics = get_latest_metrics(data)

model, model_info = train_alpha_model(data)

prediction = predict_signal(model, data)

# =========================
# AI Commentary Section
# =========================

ai_context = {
"ticker": ticker,
"market": market,
"latest_price": round(latest_metrics['price'], 2),
"rsi": round(latest_metrics['rsi'], 2),
"ma50": round(latest_metrics['ma50'], 2),
"signal": prediction['signal'],
"confidence": round(prediction['confidence'], 2),
"model_accuracy": round(model_info['accuracy'] * 100, 2)
}

ai_commentary = ask_ai(ai_context)

st.caption(f"Model accuracy: {model_info['accuracy']*100:.1f}% based on historical patterns.")

st.markdown("### 🤖 AI Market Commentary")
st.markdown(f"""
<div style="
    background-color: #161A23;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #1E2430;
    color: white;
    line-height: 1.6;
">
    <h4 style="margin-top:0;">🧠 AI Market Commentary</h4>
    <p>{ai_commentary}</p>
</div>
""", unsafe_allow_html=True)