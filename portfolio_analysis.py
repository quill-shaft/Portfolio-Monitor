import numpy as np
import yfinance as yf
import pandas as pd

from config import PORTFOLIO_QUANTITIES, ROLLING_WINDOW, TRADING_DAYS_PER_YEAR


def convert_portfolio_eur(portfolio_price, eurusd):
    portfolio_eur = portfolio_price.copy()
    eurusd_aligned = eurusd.reindex(portfolio_price.index).ffill(limit=3)
    for ticker in PORTFOLIO_QUANTITIES.keys():
        devise_ticker = yf.Ticker(ticker).info["currency"]
        if devise_ticker == "USD":
            portfolio_eur[ticker] = portfolio_price[ticker] / eurusd_aligned
    return portfolio_eur

def convert_portfolio_usd(portfolio_price, eurusd):
    portfolio_usd = portfolio_price.copy()
    eurusd_aligned = eurusd.reindex(portfolio_price.index).ffill(limit=3)
    for ticker in PORTFOLIO_QUANTITIES.keys():
        devise_ticker = yf.Ticker(ticker).info["currency"]
        if devise_ticker == "EUR":
            portfolio_usd[ticker] = portfolio_price[ticker] * eurusd_aligned
    return portfolio_usd

def portfolio_value(portfolio):
    portfolio_value = portfolio.mul(PORTFOLIO_QUANTITIES).sum(axis=1)
    return portfolio_value

def convert_base100(base100):
    return base100 / base100.iloc[0] *100

def calculate_returns(values):
    values = values.pct_change(fill_method=None).dropna()
    return values

def aligned_data(returns, to_aligned):
    aligned_data = pd.concat([returns, to_aligned], axis=1, join="inner").dropna()
    return aligned_data

def calculate_excess_returns(returns, rf):
    rf_aligned = (rf.reindex(returns.index).ffill(limit=3))
    excess_returns = returns - rf_aligned
    excess_returns = excess_returns.dropna()
    return excess_returns

def calculate_annualized_sharpe_ratio(excess_returns):
    annualized_sharpe_ratio = excess_returns.mean()/excess_returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    return annualized_sharpe_ratio

def calculate_rolling_sharpe_ratio(excess_returns):
    rolling_sharpe_ration = excess_returns.rolling(window=ROLLING_WINDOW).mean() / excess_returns.rolling(window=ROLLING_WINDOW).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    return rolling_sharpe_ration