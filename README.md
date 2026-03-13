# 📈 Stock Predictor (Streamlit App) - Testing

A simple, lightweight Streamlit app that lets you fetch stock data, engineer features, visualize price trends, and run a **Random Forest Regressor** to predict future prices.
Supports **Indian & US stock tickers**.

---

## 🚀 Features

### ✅ Stock Data Fetching

* Uses **yfinance** for historical data
* Automatically cleans + adjusts stock prices
* Supports flexible `period` and `interval` selection

### ✅ Feature Engineering

* Uses custom feature functions from `features.py` (MA, RSI, etc.)
* Automatically merges engineered features into the dataset

### ✅ Machine Learning

* Random Forest Regressor for prediction
* Automatic train/test split
* Predicts future closing prices

### ✅ Visualizations

* Candlestick chart using **Plotly**
* Trendlines and predictions
* Streamlit UI with real-time inputs

---

## 📂 Project Structure

```
sp/
├── base.py
├── core.py
├── features.py
├── stock.py
├── pages/
│   └── charts.py
├── myenv/ (virtual environment)
└── README.md
```

---

## 🛠️ Setup Instructions

### **1️⃣ Clone the repository**

```bash
git clone https://github.com/praxavv/stock-predictor.git
cd stock-predictor
```

---

### **2️⃣ Create a virtual environment**

Linux/macOS:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

Windows:

```bash
python -m venv myenv
myenv\Scripts\activate
```

---

### **3️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

---

### **4️⃣ Run the Streamlit App**

```bash
streamlit run stock.py
```

This will open the app in your browser automatically.

---

## 🧠 How It Works

### **📦 core.py**

* Downloads stock data
* Cleans + formats it
* Contains Random Forest training logic

### **📦 features.py**

* Technical indicators
* Moving Averages
* Momentum indicators
* Trend features

### **📦 stock.py**

* Main Streamlit UI
* Input fields + charts + predictions

### **📦 pages/charts.py**

* Dedicated charting page
* Comparison plots + candlesticks

---

## 📌 Example Tickers

| Exchange  | Example Tickers                    |
| --------- | ---------------------------------- |
| NSE India | `TCS.NS`, `RELIANCE.NS`, `INFY.NS` |
| US Stocks | `AAPL`, `MSFT`, `AMZN`             |

---

## 📄 License

MIT License — free to use, modify, distribute.


