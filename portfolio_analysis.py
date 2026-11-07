from math import sqrt

import pandas as pd
import statsmodels.api as sm

from config import MAX_MISSING_DAYS, MIN_REGRESSION_DAYS, MIN_RISK_DAYS, TRADING_DAYS


def convert_prices(prices, currencies, eurusd, currency):
    prices = prices.copy()
    for ticker in prices.columns:
        if currencies[ticker] != currency:
            prices[ticker] = prices[ticker] * eurusd if currency == "USD" else prices[ticker] / eurusd
    return prices


def common_closes(close, adjusted, eurusd):
    available = close.gt(0).all(axis=1) & adjusted.gt(0).all(axis=1) & eurusd.gt(0)
    # Keep the latest stretch of history after any long gap in prices.
    gap_length = MAX_MISSING_DAYS + 1
    gap = (~available).rolling(gap_length).sum().eq(gap_length)
    if gap.any():
        available = available.loc[gap[gap].index[-1]:]
    return available[available].index


def convert_base100(values, first_date=None):
    initial = values.iloc[0] if first_date is None else values.loc[first_date]
    return values / initial * 100


def compare_currencies(value, portfolio, eurusd, currency):
    if currency == "USD":
        value = value / eurusd
        portfolio = portfolio / eurusd
    values = pd.DataFrame({"EUR": value, "USD": value * eurusd})
    curves = pd.DataFrame({"EUR": portfolio, "USD": portfolio * eurusd})
    return values, convert_base100(curves)


def calculate_portfolio(close, adjusted, quantities, benchmarks, first_date=None):
    if first_date is None:
        first_date = close.index[0]
    tickers = quantities.index
    prices = close[tickers]
    values = prices.mul(quantities)
    value = values.sum(axis=1).rename("Portfolio")
    # Grow each opening position using its adjusted price return.
    adjusted_prices = adjusted[tickers]
    simulated = adjusted_prices / adjusted_prices.loc[first_date] * values.loc[first_date]
    wealth = pd.concat([simulated.sum(axis=1).rename("Portfolio"),
                        adjusted[list(benchmarks)].rename(columns=benchmarks)], axis=1)
    positions = pd.DataFrame({
        "Quantity": quantities, "Price": prices.iloc[-1],
        "Value": values.iloc[-1], "Weight": values.iloc[-1] / value.iloc[-1],
        "P&L": simulated.iloc[-1] - simulated.loc[first_date],
    }).sort_values("Value", ascending=False)
    return value, convert_base100(wealth, first_date), positions


def calculate_returns(values):
    return values.pct_change(fill_method=None).dropna()


def calculate_total_return(values):
    return values.iloc[-1] / values.iloc[0] - 1


def calculate_cagr(values):
    years = (values.index[-1] - values.index[0]).days / 365.25
    growth = values.iloc[-1] / values.iloc[0]
    return growth ** (1 / years) - 1


def drawdown(values):
    running_peak = values.cummax()
    return values / running_peak - 1


def maximum_drawdown(values):
    return drawdown(values).min()


def calculate_excess_returns(returns, risk_free_rate):
    daily_rate = (1 + risk_free_rate) ** (1 / TRADING_DAYS) - 1
    return returns - daily_rate


def calculate_annualized_sharpe_ratio(excess_returns):
    volatility = excess_returns.std(ddof=1).where(excess_returns.nunique() > 1)
    return excess_returns.mean() / volatility * sqrt(TRADING_DAYS)


def calculate_rolling_sharpe_ratio(excess_returns, window):
    rolling = excess_returns.rolling(window)
    volatility = rolling.std(ddof=1)
    return rolling.mean() / volatility.where(volatility > 0) * sqrt(TRADING_DAYS)


def calculate_annualized_volatility(returns):
    return returns.std(ddof=1) * sqrt(TRADING_DAYS)


def performance_metrics(base100, returns, excess_returns):
    volatility = sharpe = float("nan")
    if len(returns) >= MIN_RISK_DAYS:
        volatility = calculate_annualized_volatility(returns)
        sharpe = calculate_annualized_sharpe_ratio(excess_returns)
    return pd.DataFrame({"Total return": calculate_total_return(base100), "CAGR": calculate_cagr(base100),
                         "Max drawdown": maximum_drawdown(base100),
                         "Annualized volatility": volatility, "Annualized Sharpe": sharpe}).T


def regression_metrics(excess_returns):
    rows = []
    n = len(excess_returns)
    for benchmark in excess_returns.columns.drop("Portfolio"):
        row = {"Benchmark": benchmark, "N": n}
        if n >= MIN_REGRESSION_DAYS and excess_returns[benchmark].nunique() > 1:
            x = sm.add_constant(excess_returns[benchmark].rename("benchmark"))
            model = sm.OLS(excess_returns["Portfolio"], x).fit(cov_type="HAC", cov_kwds={"maxlags": 5}, use_t=True)
            row["Annualized alpha"] = model.params["const"] * TRADING_DAYS
            row["Beta"] = model.params["benchmark"]
            # t-statistics and p-values are undefined for a perfect fit.
            if model.resid.abs().max() > 1e-12:
                row.update({"t (α)": model.tvalues["const"], "p (α)": model.pvalues["const"],
                            "t (β)": model.tvalues["benchmark"], "p (β)": model.pvalues["benchmark"]})
        rows.append(row)
    columns = ["Benchmark", "Annualized alpha", "t (α)", "p (α)", "Beta", "t (β)", "p (β)", "N"]
    return pd.DataFrame(rows, columns=columns).set_index("Benchmark")
