---
title: Momentum Quant Framework
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Momentum Quant Framework

This is a Python-based quantitative momentum investing framework, optimized for deployment on Hugging Face Spaces.

## Features
- Calculates Relative Strength based on multiple timeframes (1m, 3m, 6m, 9m, 12m).
- Computes Rank Velocity to identify positive/negative momentum shifts.
- Applies hard filters: Price > 50 EMA and Price >= 80% of 52-Week High.
- Fetches index constituents dynamically from NSE indices.
- Responsive Streamlit UI with dataframe styling and CSV export.

## Deployment on Hugging Face
This repository is configured to run as a Docker Space on Hugging Face.
- Uses Python 3.10 slim.
- Runs as an unprivileged user (UID 1000).
- Exposes port 7860.

## Local Setup
1. Create a virtual environment: `python3 -m venv venv`
2. Activate it: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the app: `streamlit run app.py`
