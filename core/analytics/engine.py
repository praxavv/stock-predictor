import pandas as pd
import numpy as np
from typing import Dict, Tuple

def backtest_strategy(data: pd.DataFrame, strategy_type: str = "MA_CROSS") -> Tuple[pd.DataFrame, Dict]:
    """
    Backtest common strategies and calculate risk metrics.
    """
    df = data.copy()
    
    if strategy_type == "MA_CROSS":
        # MA Crossover Strategy
        df['Signal'] = 0
        df.loc[df['MA20'] > df['MA50'], 'Signal'] = 1
        df.loc[df['MA20'] < df['MA50'], 'Signal'] = -1
    else:
        # Buy and Hold (Default)
        df['Signal'] = 1

    # Calculate returns
    df['Benchmark_Return'] = df['Close'].pct_change()
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Benchmark_Return']
    
    # Cumulative returns
    df['Cum_Benchmark'] = (1 + df['Benchmark_Return']).cumprod()
    df['Cum_Strategy'] = (1 + df['Strategy_Return']).cumprod()
    
    # Metrics calculation
    total_return = df['Cum_Strategy'].iloc[-1] - 1
    benchmark_return = df['Cum_Benchmark'].iloc[-1] - 1
    
    # Annualized Return (assuming 252 trading days)
    days = (df.index[-1] - df.index[0]).days
    annualized_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
    
    # Volatility (Annualized)
    volatility = df['Strategy_Return'].std() * np.sqrt(252)
    
    # Sharpe Ratio (Assuming 2% risk-free rate)
    rf_daily = 0.02 / 252
    sharpe_ratio = (df['Strategy_Return'].mean() - rf_daily) / (df['Strategy_Return'].std() + 1e-10) * np.sqrt(252)
    
    # Max Drawdown
    peak = df['Cum_Strategy'].expanding().max()
    drawdown = (df['Cum_Strategy'] - peak) / peak
    max_drawdown = drawdown.min()
    
    # Win Rate
    wins = (df['Strategy_Return'] > 0).sum()
    total_trades = (df['Strategy_Return'] != 0).sum()
    win_rate = wins / (total_trades + 1e-10)

    metrics = {
        "Total Return": total_return,
        "Benchmark Return": benchmark_return,
        "Annualized Return": annualized_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Win Rate": win_rate
    }
    
    return df, metrics
