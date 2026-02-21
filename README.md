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

**Rank Velocity:**
- Calculated as: `Rank 1M Ago - Current Rank`.
- **Positive Velocity** (Green) indicates the stock is improving in rank.
- **Negative Velocity** (Red) indicates the stock is deteriorating.

**Hard Filters:**
- Price must be above the **50-day EMA**.
- Price must be within **20% of the 52-Week High**.

## Features

- **Custom Universe Selection**: Choose from NIFTY 50, NEXT 50, MIDCAP 150, SMALLCAP 250, MICROCAP 250, or the entire TOTAL MARKET.
- **Live Data**: Fetches real-time market data using `yfinance`.
- **Downloadable Results**: Export the full ranked list to CSV.
- **Rank Velocity**: Visual indicator of momentum trend.

## Project Structure

- `app.py`: Streamlit application entry point.
- `core/`: Modular logic for data fetching and momentum calculation.
    - `fetcher.py`: Handles fetching constituents and price data (robust parsing and retries).
    - `momentum.py`: Contains the `MomentumAnalyzer` class logic (including Rank Velocity).
    - `config.py`: Configuration for indices URLs and strategy parameters (Environment Variable overrides supported).
- `Dockerfile`: Deployment configuration for Hugging Face Spaces (running as non-root user).
