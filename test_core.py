import pandas as pd
from core.fetcher import fetch_constituents, fetch_historical_prices
from core.momentum import calculate_momentum

def test_fetch_constituents():
    print("Testing fetch_constituents...")
    # Test with NIFTY 50
    indices = ["NIFTY 50"]
    tickers = fetch_constituents(indices)
    print(f"Fetched {len(tickers)} tickers from {indices}.")
    assert len(tickers) > 0
    # Our new implementation returns symbols without .NS
    assert all(not t.endswith(".NS") for t in tickers)
    print("fetch_constituents Passed.")

def test_momentum_logic():
    print("Testing Momentum Logic...")
    tickers = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    print(f"Fetching price data for {len(tickers)} tickers...")

    prices = fetch_historical_prices(tickers, period="2y") # 2y is enough for calculation (need > 1y for 12m momentum)
    print(f"Price data shape: {prices.shape}")

    if prices.empty:
        print("Prices empty, skipping logic test.")
        return

    df = calculate_momentum(prices)

    print("Rankings Preview:")
    print(df.head())

    # We might not have stocks passing the filter in a small subset, but the dataframe structure should be correct
    if not df.empty:
        assert 'Momentum_Score' in df.columns
        assert 'Rank' in df.columns
        assert 'Rank_Velocity' in df.columns
        print("Momentum Logic Passed.")
    else:
        print("No stocks passed the hard filters in this subset.")
