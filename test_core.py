import pandas as pd
import pytest
from core.fetcher import get_constituents, fetch_price_data
from core.momentum import MomentumAnalyzer

def test_fetch_constituents():
    # Test with NIFTY 50
    indices = ["NIFTY 50"]
    tickers = get_constituents(indices)
    assert len(tickers) > 0
    assert all(t.endswith(".NS") for t in tickers)

def test_momentum_logic():
    # Use a hardcoded subset of well-known NIFTY 50 tickers to test logic reliably
    subset = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS"]

    prices = fetch_price_data(subset, period="2y") # 2y is enough for calculation

    if prices.empty:
        pytest.skip("Prices empty due to yfinance fetching error, skipping logic test.")

    analyzer = MomentumAnalyzer(prices)
    df = analyzer.get_rankings()

    assert not df.empty
    assert 'Momentum Score' in df.columns
    assert 'Current Rank' in df.columns
    assert 'Filters Passed' in df.columns
    assert 'Rank Velocity' in df.columns
    assert 'Symbol' in df.columns
