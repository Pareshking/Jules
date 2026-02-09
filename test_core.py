import pandas as pd
from core.fetcher import get_constituents, fetch_price_data
from core.momentum import MomentumAnalyzer

def test_fetch_constituents():
    print("Testing get_constituents...")
    # Test with NIFTY 50
    indices = ["NIFTY 50"]
    tickers = get_constituents(indices)
    print(f"Fetched {len(tickers)} tickers from {indices}.")
    assert len(tickers) > 0
    assert all(t.endswith(".NS") for t in tickers)
    print("get_constituents Passed.")
    return tickers

def test_momentum_logic(tickers):
    print("Testing Momentum Logic...")
    # Use a subset to save time if list is long
    subset = tickers[:10] if len(tickers) > 10 else tickers
    print(f"Fetching price data for {len(subset)} tickers...")

    prices = fetch_price_data(subset, period="2y") # 2y is enough for calculation (need > 1y for 12m momentum)
    print(f"Price data shape: {prices.shape}")

    if prices.empty:
        print("Prices empty, skipping logic test.")
        return

    analyzer = MomentumAnalyzer(prices)
    df = analyzer.get_rankings()

    print("Rankings Preview:")
    print(df.head())

    assert not df.empty
    assert 'Momentum Score' in df.columns
    assert 'Current Rank' in df.columns
    assert 'Filters Passed' in df.columns
    assert 'Rank Velocity' in df.columns # New Check
    print("Momentum Logic Passed.")

if __name__ == "__main__":
    tickers = test_fetch_constituents()
    test_momentum_logic(tickers)
