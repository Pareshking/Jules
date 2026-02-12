---
title: Nifty Momentum Ranking
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Nifty Momentum Ranking System

This application implements a quantitative momentum investing strategy for the Indian Stock Market (Nifty Indices).

## Methodology

The ranking is based on a **Volatility-Adjusted Momentum** score calculated as the weighted average of Z-Scores of Sharpe Ratios across multiple timeframes:
- **1 Month** (10% weight)
- **3 Months** (30% weight)
- **6 Months** (30% weight)
- **9 Months** (20% weight)
- **12 Months** (10% weight)

**Hard Filters:**
- Price must be above the **50-day EMA**.
- Price must be within **20% of the 52-Week High**.

## Features

- **Custom Universe Selection**: Choose from NIFTY 50, NEXT 50, MIDCAP 150, SMALLCAP 250, MICROCAP 250, or the entire TOTAL MARKET.
- **Live Data**: Fetches real-time market data using `yfinance`.
- **Downloadable Results**: Export the full ranked list to CSV.
- **Rank Velocity**: Tracks rank improvement over the last month.

## Project Structure

- `app.py`: Streamlit application entry point.
- `core/`: Modular logic for data fetching and momentum calculation.
    - `fetcher.py`: Handles fetching constituents and price data.
    - `momentum.py`: Contains the `MomentumAnalyzer` class logic.
    - `config.py`: Configuration for indices URLs and strategy parameters.

## Configuration (Environment Variables)

You can override the default configuration by setting the following environment variables:

- `NIFTY_50_URL`: URL for NIFTY 50 CSV.
- `NIFTY_NEXT_50_URL`: URL for NIFTY NEXT 50 CSV.
- `NIFTY_MIDCAP_150_URL`: URL for NIFTY MIDCAP 150 CSV.
- `NIFTY_SMALLCAP_250_URL`: URL for NIFTY SMALLCAP 250 CSV.
- `NIFTY_MICROCAP_250_URL`: URL for NIFTY MICROCAP 250 CSV.
- `NIFTY_TOTAL_MARKET_URL`: URL for NIFTY TOTAL MARKET CSV.
- `MOMENTUM_WEIGHTS`: Comma-separated weights (e.g., `0.1,0.3,0.3,0.2,0.1`).
- `MIN_HISTORY_DAYS`: Minimum history required (default: 260).
