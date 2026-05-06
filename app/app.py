import streamlit as st
import sys
import os

# Add the project root and app directory to the python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'app'))

from core.config import APP_TITLE, APP_ICON
from components.components import render_sidebar

# Page Configuration
st.set_page_config(
    page_title="Pranav's Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for VC-polish
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #161A23;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1E2430;
    }
    [data-testid="stSidebar"] {
        background-color: #11141C;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        background-color: #00FFA3;
        color: black;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Render Sidebar
    render_sidebar()

    # Home Page Content
    st.title(f"Pranav's Analysis Lab")
    st.subheader("Next-Gen Alpha Generation & Risk Management")
    
    st.markdown("""
    
    *A personal research environment for stock market intelligence, quantitative finance, and strategic analysis.*
    
    This workspace is built to explore markets through data, logic, and experimentation. Combining technical analysis, financial modeling, machine learning signals, and backtesting into one analytical lab.
    
    Whether studying Indian equities, analyzing US markets, testing strategies, or building valuation models, the objective remains simple:
    
    > Find clarity through data. Build conviction through analysis.
    
    ---
    
    ### 🚀 Explore the Lab
    
    1. **📊 Dashboard** — Monitor market trends, sentiment, and live analytical signals.
    2. **🔍 Deep Analysis** — Interactive technical analysis with indicators and chart overlays.
    3. **🧪 Backtester** — Evaluate trading strategies with historical simulations and risk metrics.
    4. **🤖 Quant Research** — Experimental models and data-driven market insights.
    
    ---
    
    ### 💡 Core Philosophy
    
    - Data over hype
    - Systems over emotion
    - Consistency over prediction
    - Learning through experimentation
    
    ---
    
    *Built independently by Pranav as an evolving financial research and analysis workspace.*
    """)

    # High-level Market Recap (Optional - Placeholder for now)
    st.info("💡 **Pro Tip**: Check the 'Deep Analysis' page for real-time Bollinger Band breakouts.")

if __name__ == "__main__":
    main()
