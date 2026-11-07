import yfinance as yf

from config import BENCHMARKS, BENCHMARK_ETFS, EURUSD


def download_market(tickers, start, end):
    symbols = list(dict.fromkeys([*tickers, *BENCHMARKS]))
    data = yf.download([*symbols, EURUSD], start=start, end=end,
                       auto_adjust=False, progress=False, threads=False)
    if data is None or data.empty:
        raise ValueError("Yahoo Finance returned no price data.")
    # Use closing prices for market value and adjusted closes for returns.
    close = data["Close"].reindex(columns=symbols).dropna(how="all").sort_index()
    adjusted = data["Adj Close"].reindex(index=close.index, columns=symbols)
    missing = close.columns[close.isna().all() | adjusted.isna().all()]
    if len(missing):
        raise ValueError("No price history for " + ", ".join(missing))
    fx = data["Close"].reindex(columns=[EURUSD])[EURUSD].dropna().sort_index()
    if fx.empty:
        raise ValueError("EUR/USD exchange rate is unavailable from Yahoo Finance.")

    currencies = {ticker: etf["currency"] for ticker, etf in BENCHMARK_ETFS.items()}
    for ticker in tickers:
        if ticker not in currencies:
            currencies[ticker] = yf.Ticker(ticker).fast_info["currency"]
        if currencies[ticker] not in ("EUR", "USD"):
            raise ValueError(f"{ticker} is listed in {currencies[ticker]}. Use a listing in EUR or USD.")

    return close, adjusted, currencies, fx
