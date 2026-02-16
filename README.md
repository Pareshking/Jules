---
title: Nifty Momentum Ranking
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Nifty Momentum Ranking System

A Python-based momentum investing framework deployed on Hugging Face Spaces.

## Features
- **Volatility-Adjusted Momentum**: Ranks stocks based on weighted Z-scores of Sharpe ratios.
- **Filters**: Price > 50 EMA and Price within 20% of 52-Week High.
- **Rank Velocity**: Tracks rank improvement over the last month.
- **Customizable**: Select from various Nifty indices (Nifty 50, Next 50, Midcap 150, Smallcap 250, etc.).

## Setup locally
1. Install requirements: `pip install -r requirements.txt`
2. Run app: `streamlit run app.py`

## Configuration
- `INDICES_URLS`: JSON string in env vars to override index CSV URLs.
- `MOMENTUM_WEIGHTS`: JSON string in env vars to override momentum weights.
