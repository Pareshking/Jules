---
title: Momentum Investing Framework
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# Momentum Investing Quant Framework

This is a Python-based momentum investing framework designed to rank stocks from selected NIFTY indices based on their momentum score (a weighted average of Z-scores of Sharpe Ratios across 1m, 3m, 6m, 9m, and 12m lookbacks). It includes filters to only include stocks where Price > 50 EMA and Price >= 80% of 52-Week High.

## Features
- **Modular Core:** Momentum logic, configuration, and data fetching are modularized under the `core/` package.
- **Web Interface:** Built with Streamlit for seamless configuration and analysis.
- **Data Fetching:** Automatically fetches the latest constituent symbols for NSE indices directly from niftyindices.com.
- **Resilient Connectivity:** Uses retry logic (3 retries, backoff factor 0.3) for stability.
- **Caching:** Uses `st.cache_data` to minimize repetitive data downloading.
- **Export:** Easily export the final ranked DataFrame as a CSV directly from the browser.
- **Hugging Face Ready:** Includes a `Dockerfile` and `requirements.txt` specifically optimized for deployment on Hugging Face Spaces using the Docker SDK.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tests
python -m pytest test_core.py

# Run the application
streamlit run app.py
```
