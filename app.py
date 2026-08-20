import matplotlib.pyplot as plt
import pandas as pd

from data_loader import download_close_prices, download_daily_risk_free_rate
from portfolio_analysis import convert_portfolio_eur, convert_portfolio_usd, portfolio_value, calculate_returns, calculate_excess_returns, calculate_annualized_sharpe_ratio
from config import PORTFOLIO_QUANTITIES, BENCHMARK_TICKER_USD, BENCHMARK_TICKER_EUR, RISK_FREE_TICKER

tickers = list(PORTFOLIO_QUANTITIES.keys())
portfolio_price = download_close_prices(tickers)

eurusd = download_close_prices("EURUSD=X")

portfolio_eur = convert_portfolio_eur(portfolio_price, eurusd)
portfolio_usd = convert_portfolio_usd(portfolio_price, eurusd)

portfolio_value_eur = portfolio_value(portfolio_eur)
portfolio_value_usd = portfolio_value(portfolio_usd)
plt.plot(portfolio_value_usd)
plt.show()

benchmark_price = download_close_prices(BENCHMARK_TICKER_USD)
benchmark_price = download_close_prices((BENCHMARK_TICKER_EUR))

comparison = pd.concat([portfolio_value_usd, benchmark_price], axis=1, join="inner").dropna()
comparison.columns = ["Portfolio", "Benchmark"]
comparison = comparison/comparison.iloc[0] * 100
plt.plot(comparison.index, comparison["Portfolio"], label="Portfolio")
plt.plot(comparison.index, comparison["Benchmark"], label="Benchmark")
plt.legend()
plt.show()

rf_daily = download_daily_risk_free_rate(RISK_FREE_TICKER)
rf_daily

portfolio_returns_usd = calculate_returns(portfolio_value_usd)
benchmark_returns_usd = calculate_returns(benchmark_price)

portfolio_excess_return = calculate_excess_returns(portfolio_returns_usd, rf_daily)
benchmark_excess_return = calculate_excess_returns(benchmark_returns_usd, rf_daily)

portfolio_annualized_sharp_ratio = calculate_annualized_sharpe_ratio(portfolio_excess_return)
benchmark_annualized_sharp_ratio = calculate_annualized_sharpe_ratio(benchmark_excess_return)

print(portfolio_annualized_sharp_ratio)
print(benchmark_annualized_sharp_ratio)