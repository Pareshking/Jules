---
title: Nifty Momentum
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: app.py
pinned: false
---

# Nifty Momentum Ranking System 🇮🇳

This application ranks Indian stocks based on a **Volatility-Adjusted Momentum** strategy, designed for the Indian equity market (NSE).

## Strategy Overview

The core logic evaluates momentum using a weighted average of Z-Scores of Sharpe Ratios over multiple timeframes.

*   **Timeframes:** 1m, 3m, 6m, 9m, 12m
*   **Weights:** 10%, 30%, 30%, 20%, 10%
*   **Rank Velocity:** Tracks the change in rank compared to 1 month ago.

## Features

*   **Customizable Universe:** Select from NIFTY 50, NIFTY NEXT 50, MIDCAP 150, SMALLCAP 250, MICROCAP 250, and TOTAL MARKET.
*   **Filtering:** Hard filters for stocks below 50 EMA or far from 52-Week Highs.
*   **Data Source:** Fetches real-time/delayed data using `yfinance` and official NSE constituent lists.
*   **Export:** Download full rankings as CSV.

## Deployment

This app is designed to run on **Hugging Face Spaces**.

### Configuration (Optional)

You can override default configuration by setting Environment Variables in the Space settings:

*   `NIFTY_50_URL`, `NIFTY_NEXT_50_URL`, etc.: Override CSV URLs for indices.
*   `MOMENTUM_WINDOWS`: JSON string for lookback periods (e.g., `[21, 63, 126]`).
*   `MOMENTUM_WEIGHTS`: JSON string for weights (e.g., `[0.2, 0.4, 0.4]`).
