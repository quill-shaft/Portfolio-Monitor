import numpy as np
import yfinance as yf
import pandas as pd

from config import CURRENT_HOLDINGS, ROLLING_WINDOW_QUARTER, TRADING_DAYS_PER_YEAR


def convert_prices_to_eur(portfolio_price, eurusd):
    portfolio_eur = portfolio_price.copy()
    eurusd_aligned = eurusd.reindex(portfolio_price.index).ffill(limit=3)
    for ticker in CURRENT_HOLDINGS.keys():
        devise_ticker = yf.Ticker(ticker).info["currency"]
        if devise_ticker == "USD":
            portfolio_eur[ticker] = portfolio_price[ticker] / eurusd_aligned
    return portfolio_eur

def convert_prices_to_usd(portfolio_price, eurusd):
    portfolio_usd = portfolio_price.copy()
    eurusd_aligned = eurusd.reindex(portfolio_price.index).ffill(limit=3)
    for ticker in CURRENT_HOLDINGS.keys():
        devise_ticker = yf.Ticker(ticker).info["currency"]
        if devise_ticker == "EUR":
            portfolio_usd[ticker] = portfolio_price[ticker] * eurusd_aligned
    return portfolio_usd

def calculate_portfolio_value(portfolio):
    portfolio_value = portfolio.mul(CURRENT_HOLDINGS).sum(axis=1)
    return portfolio_value

def convert_to_base_100(base100):
    return base100 / base100.iloc[0] *100

def prepare_performance_analysis(portfolio_values, benchmark_values, risk_free_returns):

    # 1. Aligner les niveaux avant de calculer les rendements
    performance_values = pd.concat({"portfolio": portfolio_values, "benchmark": benchmark_values}, axis=1, join="inner").sort_index().dropna()

    # 2. Calculer les rendements sur le calendrier commun
    asset_returns = performance_values.pct_change(fill_method=None).dropna()

     # 3. Aligner le taux sans risque avec ces rendements
    risk_free =  risk_free_returns.reindex(asset_returns.index).ffill(limit=3).rename("risk_free_return")
    performance_returns = asset_returns.join(risk_free, how="inner").dropna()

    # 4. Calculer les rendements excédentaires
    performance_returns["portfolio_excess"] = performance_returns["portfolio"] - performance_returns["risk_free_return"]
    performance_returns["benchmark_excess"] = performance_returns["benchmark"] - performance_returns["risk_free_return"]
    return performance_values, performance_returns

def calculate_total_return(values):
    returns = values.iloc[-1]/values.iloc[0] - 1
    return returns

def calculate_annualized_sharpe_ratio(excess_returns):
    annualized_sharpe_ratio = excess_returns.mean()/excess_returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    return annualized_sharpe_ratio

def calculate_rolling_sharpe_ratio(excess_returns, window):
    rolling_sharpe_ratio = excess_returns.rolling(window=window).mean() / excess_returns.rolling(window=ROLLING_WINDOW_QUARTER).std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    return rolling_sharpe_ratio

def calculate_annualized_volatility(returns):
    annual_volatility = returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)
    return annual_volatility

def calculate_cagr(value):
    year = (value.index[-1]-value.index[0]).days / 365.25
    growth = value.iloc[-1]/value.iloc[0]
    CAGR = growth**(1/year) -1
    return CAGR

def drawdown(values):
    running_peak = values.cummax()
    DD = values/running_peak - 1
    return DD

def maximum_drawdown(values):
    max_DD = min(drawdown(values))
    return max_DD