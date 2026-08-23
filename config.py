import pandas as pd

RISK_FREE_USD_SYMBOL = "^IRX"

TRADING_DAYS_PER_YEAR = 252

ROLLING_WINDOW_QUARTER = 63

START_DATE = pd.Timestamp.today() - pd.DateOffset(years=1)

END_DATE = pd.Timestamp.today()

BENCHMARK_TICKER_USD = "QQQ"

BENCHMARK_TICKER_EUR = "EQQQ.PA"

CURRENT_HOLDINGS = {
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
    "ASML.AS" : 1,
    "KER.PA": 4,
    "CDI.PA": 2,
    "ADYEN.AS": 1,
    "NFLX": 10,
    #"SPCX": 9
}