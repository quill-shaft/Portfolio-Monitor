import yfinance as yf
import pandas as pd

from config import START_DATE, END_DATE, TRADING_DAYS_PER_YEAR

def download_close_prices(ticker, start=START_DATE, end=END_DATE):
    data = yf.download(ticker, start, end, auto_adjust=True, progress=True, threads=False)["Close"]
    if isinstance(ticker, str) and isinstance(data, pd.DataFrame):
        data = data.squeeze("columns")
    data = data.sort_index()
    data = data.ffill(limit=3).dropna()
    return data

def download_daily_risk_free_rate(ticker, start=START_DATE, end=END_DATE):
    annual_rate = download_close_prices(ticker, start, end) /100
    daily_rate = (1 + annual_rate) ** (1 / TRADING_DAYS_PER_YEAR) - 1
    return daily_rate