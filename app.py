import matplotlib.pyplot as plt
import pandas as pd

from data_loader import download_close_prices, download_daily_risk_free_return
from portfolio_analysis import convert_prices_to_usd, calculate_portfolio_value, prepare_performance_analysis, calculate_cagr, calculate_annualized_volatility, calculate_annualized_sharpe_ratio, calculate_rolling_sharpe_ratio, maximum_drawdown, drawdown, calculate_total_return, convert_to_base_100
from config import CURRENT_HOLDINGS, BENCHMARK_TICKER_USD, RISK_FREE_USD_SYMBOL, ROLLING_WINDOW_QUARTER

tickers = list(CURRENT_HOLDINGS.keys())
asset_prices_local = download_close_prices(tickers)
eurusd_rate = download_close_prices("EURUSD=X")
asset_prices_usd = convert_prices_to_usd(asset_prices_local, eurusd_rate)
portfolio_value_usd = calculate_portfolio_value(asset_prices_usd)
risk_free_returns_usd = download_daily_risk_free_return(RISK_FREE_USD_SYMBOL)
benchmark_price_usd = download_close_prices(BENCHMARK_TICKER_USD)
performance_values, performance_returns = (prepare_performance_analysis(portfolio_value_usd, benchmark_price_usd, risk_free_returns_usd,))

portfolio_cagr = calculate_cagr(performance_values["portfolio"])
portfolio_annualized_volatility = calculate_annualized_volatility(performance_returns["portfolio"])
portfolio_annualized_sharp_ratio = calculate_annualized_sharpe_ratio(performance_returns["portfolio"])
portfolio_rolling_sharp_ratio = calculate_rolling_sharpe_ratio(performance_returns["portfolio"], ROLLING_WINDOW_QUARTER)
portfolio_maximum_drawdown = maximum_drawdown(performance_values["portfolio"])
portfolio_drawdown = drawdown(performance_values["portfolio"])
portfolio_value_usd = performance_values["portfolio"].iloc[-1]
portfolio_return_usd = calculate_total_return(performance_values["portfolio"])

print(f"Valeur du portefeuille : {portfolio_value_usd:,.0f} $".replace(","," "))
print(f"Rendement du portefeuille : {portfolio_return_usd:,.2%}")
print(f"CAGR portefeuille : {portfolio_cagr:.2%}")
print(f"Sharpe ratio annuelle portefeuille : {portfolio_annualized_sharp_ratio:.2}")
print(f"Volatilité annuelle du portefeuille : {portfolio_annualized_volatility:.2%}")
print(f"Maximum drawdown du portefeuille : {portfolio_maximum_drawdown:.2%}")

performance_values["portfolio"].plot()
plt.show()

comparaison = performance_values.apply(convert_to_base_100)
comparaison.plot()
plt.show()