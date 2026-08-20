# Portfolio Monitor

A Python-based portfolio monitoring prototype for tracking portfolio performance, comparing it with a benchmark, and calculating basic risk-adjusted return metrics.

> This project is currently under active development.

## Features

- Downloads historical adjusted market prices using Yahoo Finance
- Calculates the value of an equity portfolio from asset quantities
- Converts portfolio values between EUR and USD
- Compares portfolio performance against a benchmark
- Calculates daily returns and excess returns
- Calculates the annualized Sharpe ratio
- Generates basic performance charts with Matplotlib

## Project Structure

```text
portfolio-monitor/
├── app.py                  # Main application entry point
├── config.py               # Portfolio and application settings
├── data_loader.py          # Market data download functions
├── portfolio_analysis.py   # Portfolio and risk metric calculations
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10 or later
- Internet connection for market data downloads

## Installation

Clone the repository:

```bash
git clone https://github.com/quill-shaft/portfolio-monitor.git
cd portfolio-monitor
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Configuration

Portfolio assets, quantities, benchmark settings, dates, and risk-free rate settings are defined in `config.py`.

Example:

```python
PORTFOLIO_QUANTITIES = {
    "AAPL": 10,
    "MSFT": 5,
    "NVDA": 8,
}
```

The portfolio positions included in this repository are illustrative examples only and do not represent a real investment portfolio.

## Usage

Run the application from the project directory:

```bash
python app.py
```

The script downloads market data, calculates portfolio and benchmark performance, displays charts, and prints selected metrics in the terminal.

## Metrics

The current version includes:

- Portfolio market value
- Daily returns
- Excess returns over the risk-free rate
- Annualized Sharpe ratio
- Portfolio versus benchmark performance comparison

The annualized Sharpe ratio is calculated as:

```text
Sharpe Ratio = Mean Excess Return / Standard Deviation of Excess Returns × √252
```

## Data Sources

Market data is retrieved through the [`yfinance`](https://github.com/ranaroussi/yfinance) package, which accesses Yahoo Finance data.

## Disclaimer

This project is for educational and personal research purposes only. It does not constitute investment advice, financial advice, or a recommendation to buy or sell any security.

Market data may be incomplete, delayed, or inaccurate. Always verify information independently before making financial decisions.

## Roadmap

Planned improvements include:

- Rolling Sharpe ratio visualisation
- Drawdown analysis
- Improved chart formatting
- Error handling for unavailable tickers or missing data
- Unit tests for portfolio calculations
- Streamlit dashboard interface
- Export of performance reports

## License

No license has been selected yet. All rights reserved.
