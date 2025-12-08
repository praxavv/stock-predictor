import streamlit as st
from core import intraday_net_profit

st.title("📉 Intraday Profit Calculator")

buy = st.number_input("Buy Price", min_value=0.0, format="%.2f")
sell = st.number_input("Sell Price", min_value=0.0, format="%.2f")
qty = st.number_input("Quantity", min_value=1, step=1)

if st.button("Calculate Net Profit"):
    result = intraday_net_profit(buy, sell, qty)
    st.subheader(f"Net Profit: ₹{result['net_profit']}")
