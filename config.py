# Yahoo Finance tickers and share quantities.
PORTFOLIO_QUANTITIES = {
    "GOOGL": 37,
    "NVDA": 54,
    "ANAV.DE": 467,
    "META": 15,
    "AAPL": 37,
    "AMZN": 43,
    "MSFT": 19,
    "RMS.PA": 2,
    "MC.PA": 5,
    "TSLA": 5,
    "BRK-B": 3,
    "ASML.AS": 1,
    "KER.PA": 4,
    "CDI.PA": 2,
    "ADYEN.AS": 1,
    "NFLX": 10,
    #"SPCX": 9
}

TIMEZONE = "Europe/Paris"
EURUSD = "EURUSD=X"
CACHE_SECONDS = 3600
MAX_MISSING_DAYS = 3

PERIOD_MONTHS = {"2 years": 24, "1 year": 12, "6 months": 6, "3 months": 3, "YTD": 0}
DEFAULT_PERIOD = "2 years"
HISTORY_BUFFER_DAYS = 120  # Earlier prices for the rolling Sharpe ratio.

DEFAULT_RISK_FREE_RATE = 3.0  # Annual rate in percent.
TRADING_DAYS = 252
MIN_RISK_DAYS = 21
MIN_REGRESSION_DAYS = 50
ROLLING_WINDOW_QUARTER = 63

BENCHMARK_ETFS = {
    "CSPX.AS": {
        "label": "S&P 500",
        "name": "iShares Core S&P 500 UCITS ETF USD (Acc)",
        "currency": "EUR",
        "isin": "IE00B5BMR087",
        "url": "https://www.ishares.com/uk/professionals/en/products/253743/ishares-core-s-p-500-ucits-etf",
    },
    "SXRV.DE": {
        "label": "Nasdaq-100",
        "name": "iShares Nasdaq 100 UCITS ETF USD (Acc)",
        "currency": "EUR",
        "isin": "IE00B53SZB19",
        "url": "https://www.ishares.com/de/professionelle-anleger/de/produkte/253741/",
    },
}
BENCHMARKS = {ticker: etf["label"] for ticker, etf in BENCHMARK_ETFS.items()}
