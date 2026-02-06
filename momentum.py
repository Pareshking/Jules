import pandas as pd
import yfinance as yf
import requests
import io
import numpy as np
from datetime import datetime, timedelta

def get_nifty_constituents():
    """
    Fetches the Nifty Total Market constituents from the NSE website.
    Returns a list of symbols with '.NS' appended.
    """
    url = "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        csv_content = response.content.decode('utf-8')

        # Read CSV
        # Force separator to match standard CSV
        df = pd.read_csv(io.StringIO(csv_content), sep=",")

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]

        # Identify Symbol column
        symbol_col = None
        for col in df.columns:
            if col.lower() == 'symbol':
                symbol_col = col
                break

        if not symbol_col:
            # Fallback
            symbol_col = df.columns[2] # Usually 3rd column

        symbols = df[symbol_col].dropna().astype(str).tolist()

        # Append .NS
        cleaned_symbols = [f"{sym.strip()}.NS" for sym in symbols]

        return cleaned_symbols

    except Exception as e:
        print(f"Error fetching Nifty constituents: {e}")
        return []

def fetch_data(tickers, period="3y"):
    """
    Fetches OHLCV data for the given tickers.
    Returns a DataFrame of Close prices.
    """
    if not tickers:
        return pd.DataFrame()

    print(f"Fetching data for {len(tickers)} tickers...")
    try:
        # auto_adjust=True ensures Close is adjusted for splits and dividends
        data = yf.download(tickers, period=period, auto_adjust=True, progress=False, threads=True)
    except Exception as e:
        print(f"Error fetching data via yfinance: {e}")
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()

    # Extract Close prices
    if 'Close' in data.columns:
        close_data = data['Close']
    else:
        # Sometimes yfinance returns just the price dataframe if only one type requested?
        # But with download(..., auto_adjust=True), it returns Open, High, Low, Close, Volume
        # If columns are MultiIndex, 'Close' is level 0.
        close_data = data

    # Ensure it's a DataFrame (dates x tickers)
    if isinstance(close_data, pd.Series):
        close_data = close_data.to_frame()

    return close_data

def calculate_momentum_metrics(prices):
    """
    Calculates the momentum scores and ranks for the entire history (vectorized).
    Returns a DataFrame of Weighted Momentum Scores (index=Date, columns=Tickers).
    """
    if prices.empty:
        return None

    # Constants
    windows = [21, 63, 126, 189, 252] # 1m, 3m, 6m, 9m, 12m
    weights = [0.1, 0.3, 0.3, 0.2, 0.1]

    # Daily Returns
    daily_returns = prices.pct_change(fill_method=None)

    # Initialize Score DataFrame
    weighted_z_score = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)

    for w, weight in zip(windows, weights):
        # Rolling Return
        # (Price_t / Price_{t-w}) - 1
        period_ret = (prices / prices.shift(w)) - 1

        # Rolling Volatility (Daily Std Dev over window)
        period_vol = daily_returns.rolling(window=w).std()

        # Sharpe Ratio
        # Avoid division by zero
        sharpe = period_ret.div(period_vol.replace(0, np.nan))

        # Z-Score (Cross-sectional per day)
        # Calculate mean and std for each row (date)
        mean_sharpe = sharpe.mean(axis=1)
        std_sharpe = sharpe.std(axis=1)

        # Broadcast subtraction and division
        # (sharpe - mean) / std
        z_score = sharpe.sub(mean_sharpe, axis=0).div(std_sharpe, axis=0)

        # Handle NaNs: If a stock has NaN Sharpe (e.g. newly listed), Z-Score is NaN.
        # We fill NaN with 0 (neutral score) so it doesn't break the sum.
        # However, purely relying on this might bias towards 0.
        # But for ranking, 0 is average.
        weighted_z_score = weighted_z_score.add(z_score.fillna(0) * weight, fill_value=0)

    return weighted_z_score

def generate_full_ranking(subset_size=None):
    """
    Orchestrates the data fetching, calculation, and report generation.
    """
    # 1. Fetch Tickers
    tickers = get_nifty_constituents()
    if subset_size:
        tickers = tickers[:subset_size]

    if not tickers:
        print("No tickers found.")
        return pd.DataFrame()

    # 2. Fetch Data
    # We need enough history for filters and lookbacks
    prices = fetch_data(tickers, period="3y")

    # Filter valid stocks (must have data for at least 1.5 years ideally, but let's say 300 days)
    # The longest lookback is 252 days. To calculate Z-score, we need peers.
    min_days = 260
    valid_cols = prices.notna().sum() > min_days
    prices = prices.loc[:, valid_cols]

    if prices.empty:
        print("No valid price data.")
        return pd.DataFrame()

    # 3. Calculate Momentum Scores (Vectorized)
    momentum_scores = calculate_momentum_metrics(prices)

    if momentum_scores is None:
        return pd.DataFrame()

    # 4. Filters (Current Data)
    # Use the last available row
    current_prices = prices.iloc[-1]

    # 50 EMA
    ema_50 = prices.ewm(span=50, adjust=False).mean().iloc[-1]

    # 52 Week High (max of last 252 days)
    high_52 = prices.rolling(window=252).max().iloc[-1]

    # 5. Build Result DataFrame

    # Indices for T, T-1m, T-2m, T-3m
    # We use negative indexing based on trading days approx (21 days/month)
    # Ensure we don't go out of bounds
    max_idx = len(momentum_scores)

    indices = {
        'Current': -1,
        '1M Ago': -22,
        '2M Ago': -43,
        '3M Ago': -64
    }

    # Helper to get rank series for a specific time offset
    def get_rank_series(offset_idx):
        # Check bounds
        if abs(offset_idx) >= max_idx:
            return pd.Series(np.nan, index=momentum_scores.columns)

        # Get scores at that index
        scores = momentum_scores.iloc[offset_idx]

        # Rank descending (Higher score = Rank 1)
        # Only rank valid scores (non-zero or existing)
        # Actually rank treats NaNs as lowest?
        # We filled NaNs with 0. So they are ranked as average.
        # That's acceptable.
        return scores.rank(ascending=False)

    # Base DataFrame
    df = pd.DataFrame(index=prices.columns)

    # Add Score
    try:
        df['Momentum Score'] = momentum_scores.iloc[indices['Current']]
    except IndexError:
        df['Momentum Score'] = np.nan

    df['Price'] = current_prices
    df['50 EMA'] = ema_50
    df['52W High'] = high_52

    # Add Ranks
    df['Current Rank'] = get_rank_series(indices['Current'])
    df['Rank 1M Ago'] = get_rank_series(indices['1M Ago'])
    df['Rank 2M Ago'] = get_rank_series(indices['2M Ago'])
    df['Rank 3M Ago'] = get_rank_series(indices['3M Ago'])

    # Apply Filters
    df['Above 50 EMA'] = df['Price'] > df['50 EMA']
    df['Near 52W High'] = df['Price'] >= (0.8 * df['52W High'])
    df['Filters Passed'] = df['Above 50 EMA'] & df['Near 52W High']

    # Sort
    df = df.sort_values('Current Rank')

    # Reset index to make Symbol a column
    df = df.reset_index().rename(columns={'index': 'Symbol'})

    return df

if __name__ == "__main__":
    print("Running Analysis...")
    df = generate_full_ranking(subset_size=20)
    print(df.head())
