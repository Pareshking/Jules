import pytest
import pandas as pd
import numpy as np
from core.fetcher import get_nifty_constituents, get_historical_prices
from core.momentum import calculate_momentum

def test_get_nifty_constituents_basic():
    """Test fetching from a dummy URL or mocking it to check filtering and appending .NS"""
    # For a self-contained test, we can mock the request, or we can use a small real one
    # To avoid internet dependency flakiness, let's create a mocked version for testing the logic
    # But memory says: "Test functions in test_core.py are designed to be self-contained and fetch their own required data, avoiding dependency on return values from other test functions."
    # Let's fetch NIFTY 50 since it's small and standard.
    urls = ["https://niftyindices.com/IndexConstituent/ind_nifty50list.csv"]
    symbols = get_nifty_constituents(urls)

    # Assert we got some symbols
    assert len(symbols) > 0

    # Assert they end with .NS
    assert all(s.endswith('.NS') for s in symbols)

    # Assert no DUMMY symbols (assuming nifty 50 doesn't have them, but the logic should filter)
    assert not any('DUMMY' in s for s in symbols)

def test_get_historical_prices():
    symbols = ["RELIANCE.NS", "TCS.NS"]
    df = get_historical_prices(symbols, period="1mo")

    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    # Check that columns are symbols
    assert "RELIANCE.NS" in df.columns
    assert "TCS.NS" in df.columns
    # Check timezone is removed
    if isinstance(df.index, pd.DatetimeIndex):
        assert df.index.tz is None

def test_calculate_momentum():
    # Create some dummy price data that will pass filters
    dates = pd.date_range(start="2020-01-01", periods=300, freq="B")

    # Create trending data to ensure positive momentum and passing filters
    price_a = np.linspace(100, 200, 300)
    price_b = np.linspace(100, 150, 300)

    # Add some noise
    np.random.seed(42)
    price_a += np.random.normal(0, 2, 300)
    price_b += np.random.normal(0, 2, 300)

    df = pd.DataFrame({
        "StockA.NS": price_a,
        "StockB.NS": price_b
    }, index=dates)

    results = calculate_momentum(df)

    assert not results.empty
    assert 'Momentum Score' in results.columns
    assert 'Symbol' in results.columns
    assert 'Rank Velocity' in results.columns

    # Check that StockA is ranked higher than StockB due to stronger trend
    score_a = results.loc[results['Symbol'] == 'StockA.NS', 'Momentum Score'].values[0]
    score_b = results.loc[results['Symbol'] == 'StockB.NS', 'Momentum Score'].values[0]
    assert score_a > score_b

    # Check hard filters: both should be above 50 EMA and 80% of 52W high
    # because the data is linearly increasing
    assert len(results) == 2
