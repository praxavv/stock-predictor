import streamlit as st
from core import intraday_net_profit

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

st.title("📈 Welcome to Pranav's Trading Simulation")

st.write("""
Choose a market from the sidebar:

- 🇺🇸 US Stock Predictor  
- 🇮🇳 India Stock Predictor  
- 📊 Charts & Visualizations  

Use the Pages section on the left to navigate.
""")
