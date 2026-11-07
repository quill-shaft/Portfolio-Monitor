# Portfolio Monitor

A Streamlit dashboard for tracking a fixed basket of stocks in EUR and USD and comparing its performance with the S&P 500 and Nasdaq-100. It uses daily prices from Yahoo Finance.

## Run locally

Set the Yahoo Finance tickers and share quantities in `PORTFOLIO_QUANTITIES` in [config.py](config.py). Use tickers listed in EUR or USD.

```python
PORTFOLIO_QUANTITIES = {
    "AAPL": 25,
    "MC.PA": 4,
}
```

From the project directory, create a virtual environment, install the dependencies, and start the app.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Restart Streamlit after editing your holdings.

## Dashboard

- **Overview** shows the latest market value in EUR and USD, cumulative returns, and a base-100 chart comparing the two currencies.
- **Performance and Risk** compares total return, compound annual growth rate (CAGR), maximum drawdown, annualized volatility, and Sharpe. The charts show cumulative return, drawdown, and rolling Sharpe. Each ETF has its own visibility toggle. The benchmark comparison reports the portfolio's return gap in percentage points, annualized alpha, and beta. Regression details show t-statistics, p-values, and the number of return observations (`N`).
- **Positions** shows the weight of the five largest holdings and a table with quantities, prices, market values, weights, and each holding's P&L over the selected period.

## How the numbers are calculated

Market value uses closing prices and the share quantities in `config.py`. Performance starts with those quantities at the beginning of the selected period and grows each position using adjusted closing prices, which account for splits and reinvested dividends. The result is a simulation of the configured basket. It excludes actual trades, cash balances, and brokerage fees.

The portfolio and both benchmark ETFs are compared on common dates in the selected currency. Closing prices are converted using the EUR/USD exchange rate before returns are calculated. The default benchmarks are the iShares Core S&P 500 UCITS ETF (`CSPX.AS`) and the iShares Nasdaq 100 UCITS ETF (`SXRV.DE`).

Volatility and Sharpe use all returns in the selected period once at least 21 are available. Alpha and beta come from a separate excess-return regression against each ETF and require at least 50 observations. The rolling Sharpe uses the last 63 observations at each point. The annual risk-free rate is adjustable in the sidebar and defaults to 3%.

## Project structure

- `app.py` contains the Streamlit views and charts.
- `config.py` holds the portfolio, benchmarks, and settings.
- `data_loader.py` fetches prices, listing currencies, and exchange rates.
- `portfolio_analysis.py` handles valuation, returns, risk metrics, and regressions.

## Roadmap

- **IBKR activity statement import.** Reconstruct holdings over time from actual buys and sells, including positions sold and later repurchased. Show deposits, withdrawals, cash balances, dividends received, and the commissions and fees actually paid.
- **Cash flow and performance reporting.** Show cash movements alongside the portfolio value and calculate time-weighted returns for benchmark comparisons when there are deposits or withdrawals.
- **Stress testing.** Replay historical market drawdowns and estimate the effect of hypothetical equity and EUR/USD shocks on the portfolio.
