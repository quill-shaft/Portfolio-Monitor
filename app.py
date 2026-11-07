import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    BENCHMARK_ETFS, BENCHMARKS, CACHE_SECONDS, DEFAULT_PERIOD, DEFAULT_RISK_FREE_RATE,
    HISTORY_BUFFER_DAYS, MAX_MISSING_DAYS,
    PERIOD_MONTHS, PORTFOLIO_QUANTITIES, ROLLING_WINDOW_QUARTER, TIMEZONE,
)
from data_loader import download_market
from portfolio_analysis import (
    calculate_excess_returns, calculate_portfolio, calculate_returns,
    calculate_rolling_sharpe_ratio, calculate_total_return, common_closes, compare_currencies,
    convert_prices, drawdown, performance_metrics, regression_metrics,
)

st.set_page_config(page_title="Portfolio Monitor", layout="wide")
st.html("""
<style>
.stApp { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
[data-testid="stMainBlockContainer"] { max-width: 1320px; padding-top: 2rem; }
[data-testid="stAppDeployButton"] { display: none; }
h1 { font-size: 2rem !important; letter-spacing: -.045em; font-weight: 650 !important; }
h2 { font-size: 1.4rem !important; letter-spacing: -.025em; }
h3 { font-size: 1.05rem !important; letter-spacing: -.015em; }
[data-testid="stMetricValue"] { font-size: 2rem; letter-spacing: -.035em; font-weight: 600; }
.st-key-portfolio_value [data-testid="stMetricValue"] { font-size: 3.2rem; letter-spacing: -.05em; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius: 9px; padding: .35rem .5rem; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: rgba(0,122,255,.10);
}
</style>
""")

BLUE, GRAY, ORANGE = "#007AFF", "#8E8E93", "#D97706"
LINE_COLORS = {"Portfolio": BLUE, "EUR": BLUE, "USD": GRAY,
               **dict(zip(BENCHMARKS.values(), [GRAY, ORANGE]))}
get_market = st.cache_data(ttl=CACHE_SECONDS, show_spinner=False)(download_market)


def number(value, digits=2, suffix=""):
    if pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}" + suffix


def percent(value, digits=1):
    return number(value * 100, digits, "%")


def show_chart(chart, height=340, key=None):
    chart.update_layout(height=height, separators=".,", paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
                                  color="#48484A", size=12))
    st.plotly_chart(chart, key=key, config={"displayModeBar": False, "scrollZoom": False})


def line_chart(frame, tickformat, ticksuffix="", key=None):
    chart = px.line(frame, color_discrete_map=LINE_COLORS, markers=len(frame) == 1)
    for i, trace in enumerate(chart.data):
        trace.update(line=dict(width=2.5, dash="solid" if i == 0 else "dot"))
    span = (frame.index[-1] - frame.index[0]).days
    date_format = "%b %Y" if span > 120 else "%b %d"
    chart.update_layout(margin=dict(l=8, r=12, t=30, b=8), hovermode="x unified",
                        showlegend=len(frame.columns) > 1,
                        legend=dict(title="", orientation="h", yanchor="bottom", y=1.02),
                        xaxis=dict(title="", showgrid=False, tickformat=date_format, hoverformat="%b %d, %Y"),
                        yaxis=dict(title="", gridcolor="rgba(142,142,147,.14)",
                                   tickformat=tickformat, ticksuffix=ticksuffix))
    show_chart(chart, key=key)


with st.sidebar:
    st.subheader("Portfolio")
    page = st.radio("Navigation", ["Overview", "Performance and Risk", "Positions"],
                    label_visibility="collapsed")
    st.divider()
    currency = st.selectbox("Currency", ["EUR", "USD"])
    risk_free_rate = st.number_input("Annual risk-free rate (%)", value=DEFAULT_RISK_FREE_RATE,
                                     min_value=-99.99, step=0.25, format="%.2f") / 100
    with st.expander("Benchmark ETFs"):
        for ticker, etf in BENCHMARK_ETFS.items():
            st.markdown(f"**{etf['label']} · `{ticker}`**\n\n[{etf['name']}]({etf['url']})\n\n"
                        f"{etf['isin']} · Listed in {etf['currency']}")
        st.caption("Returns use adjusted closing prices for stocks and ETFs (Adj Close).")

st.title(page)
period = st.segmented_control("Period", list(PERIOD_MONTHS), default=DEFAULT_PERIOD,
                              label_visibility="collapsed") or DEFAULT_PERIOD
symbol = " €" if currency == "EUR" else " $"

try:
    quantities = pd.Series(PORTFOLIO_QUANTITIES, dtype=float)
    if quantities.empty or not quantities.between(0, float("inf"), inclusive="neither").all():
        raise ValueError("Add at least one position with a positive quantity in config.py.")
    tickers = tuple(quantities.index)
    end = pd.Timestamp.now(tz=TIMEZONE).tz_localize(None).normalize()
    start = end - pd.DateOffset(months=max(PERIOD_MONTHS.values())) - pd.Timedelta(days=HISTORY_BUFFER_DAYS)
    with st.spinner("Loading market data…"):
        close, adjusted, currencies, fx = get_market(tickers, start, end)
except Exception as error:
    st.error(str(error))
    st.stop()

fx_dates = fx.index.union(close.index).sort_values()
eurusd = fx.reindex(fx_dates).ffill(limit=MAX_MISSING_DAYS).reindex(close.index)
close = convert_prices(close, currencies, eurusd, currency)
adjusted = convert_prices(adjusted, currencies, eurusd, currency)
available_dates = common_closes(close, adjusted, eurusd)
if len(available_dates) == 0:
    st.info("No common closing dates for the holdings, both ETFs and the EUR/USD exchange rate.")
    st.stop()

end = available_dates[-1]
months = PERIOD_MONTHS[period]
start = end - pd.DateOffset(months=months) if months else end.replace(month=1, day=1)
dates = available_dates[available_dates >= start]
st.caption(f"Yahoo Finance · {dates[0]:%Y-%m-%d} to {end:%Y-%m-%d} · {currency} · Returns based on adjusted closes")
value, history, positions = calculate_portfolio(close.loc[available_dates], adjusted.loc[available_dates],
                                               quantities, BENCHMARKS, first_date=dates[0])
value, base100 = value.loc[dates], history.loc[dates]

if page == "Overview":
    values, currency_base100 = compare_currencies(value, base100["Portfolio"], eurusd.loc[dates], currency)
    total_returns = calculate_total_return(currency_base100)
    with st.container(key="portfolio_value"):
        left, right = st.columns(2)
        left.metric("Value in EUR", number(values["EUR"].iloc[-1], 0, " €"),
                    f"{percent(total_returns['EUR'], 2)} over the period")
        right.metric("Value in USD", number(values["USD"].iloc[-1], 0, " $"),
                     f"{percent(total_returns['USD'], 2)} over the period")
    value_tab, fx_tab = st.tabs(["Value", "EUR vs USD (Base 100)"])
    with value_tab:
        line_chart(value.to_frame(), ",.0f", symbol)
    with fx_tab:
        line_chart(currency_base100, ".1f")
        gap = (total_returns["USD"] - total_returns["EUR"]) * 100
        st.caption(f"USD minus EUR return over the period · {number(gap, 2, ' pp')}")

elif page == "Performance and Risk":
    if len(base100) < 2:
        st.info("At least two common closing dates are needed to calculate a return.")
        st.stop()
    # Keep earlier returns for the rolling chart and slice the tables to the selected period.
    history_returns = calculate_returns(history)
    history_excess = calculate_excess_returns(history_returns, risk_free_rate)
    returns = history_returns.loc[history_returns.index > dates[0]]
    excess_returns = history_excess.loc[returns.index]
    stats = performance_metrics(base100, returns, excess_returns)
    regression = regression_metrics(excess_returns)
    table = stats.map(percent)
    table.loc["Annualized Sharpe"] = stats.loc["Annualized Sharpe"].map(number)

    st.table(table)

    chart_columns = ["Portfolio"]
    for column, label in zip(st.columns(len(BENCHMARKS)), BENCHMARKS.values()):
        if column.checkbox(label, value=True):
            chart_columns.append(label)
    perf_tab, drawdown_tab, sharpe_tab = st.tabs(["Cumulative Return", "Drawdown", "Rolling Sharpe"])
    with perf_tab:
        line_chart(base100[chart_columns] / 100 - 1, ".0%", key="performance")
    with drawdown_tab:
        line_chart(drawdown(base100[chart_columns]), ".0%", key="drawdown")
    with sharpe_tab:
        rolling_sharpe = calculate_rolling_sharpe_ratio(history_excess[chart_columns], ROLLING_WINDOW_QUARTER)
        rolling_sharpe = rolling_sharpe.loc[dates[0]:].dropna(how="all")
        st.caption(f"Annualized Sharpe over the trailing {ROLLING_WINDOW_QUARTER} observations.")
        if rolling_sharpe.empty:
            st.info("Insufficient data for the rolling Sharpe ratio.")
        else:
            line_chart(rolling_sharpe, ".2f", key="rolling_sharpe")

    st.subheader("Portfolio vs Benchmarks")
    total_returns = stats.loc["Total return"]
    return_gap = total_returns["Portfolio"] - total_returns[regression.index]
    regression["Return gap"] = return_gap.map(lambda gap: number(gap * 100, suffix=" pp"))
    regression.index = ("Portfolio vs " + regression.index).rename("Comparison")
    comparison = regression[["Return gap", "Annualized alpha", "Beta"]].copy()
    comparison["Annualized alpha"] = comparison["Annualized alpha"].map(lambda alpha: percent(alpha, 2))
    comparison["Beta"] = comparison["Beta"].map(number)
    st.table(comparison)

    st.subheader("Regression Details")
    details = regression[["t (α)", "p (α)", "t (β)", "p (β)", "N"]].copy()
    for column in ["t (α)", "t (β)"]:
        details[column] = details[column].map(number)
    for column in ["p (α)", "p (β)"]:
        details[column] = details[column].map(lambda p: "<0.001" if p < .001 else number(p, 3))
    st.table(details)

else:
    top = positions["Weight"].head(5)
    st.metric("Weight of top 5 holdings", percent(top.sum()))
    bars = px.bar(top.rename_axis("Ticker").reset_index(), x="Weight", y="Ticker", orientation="h", text="Weight",
                  color_discrete_sequence=[BLUE])
    bars.update_traces(texttemplate="%{x:.1%}", textposition="outside", cliponaxis=False)
    bars.update_layout(margin=dict(l=8, r=55, t=8, b=8),
                       xaxis=dict(title="", tickformat=".0%", range=[0, top.max() * 1.25]),
                       yaxis=dict(title="", autorange="reversed"))
    show_chart(bars, height=245)
    positions.index.name = "Ticker"
    st.dataframe(positions.style.format({
        "Quantity": "{:g}", "Price": lambda x: number(x, 2, symbol),
        "Value": lambda x: number(x, 0, symbol), "Weight": percent,
        "P&L": lambda x: number(x, 0, symbol)
    }), width="stretch")
