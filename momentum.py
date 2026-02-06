import pandas as pd
import yfinance as yf
import requests
import io
import numpy as np
from datetime import datetime, timedelta

def get_nifty_constituents():
    """
    Fetches the Nifty Total Market constituents from the NSE website.
    Returns a dictionary of {Symbol: Company Name}.
    Symbol keys have '.NS' appended.
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

        # Identify Company Name column
        name_col = None
        for col in df.columns:
            if col.lower() in ['company name', 'security name', 'companyname']:
                name_col = col
                break

        if not name_col:
            # Fallback, maybe first column
            name_col = df.columns[0]

        df = df.dropna(subset=[symbol_col])

        symbols = df[symbol_col].astype(str).tolist()
        names = df[name_col].astype(str).tolist()

        # Create dictionary with .NS appended to symbol
        result = {}
        for sym, name in zip(symbols, names):
            clean_sym = f"{sym.strip()}.NS"
            result[clean_sym] = name.strip()

        return result

    except Exception as e:
        print(f"Error fetching Nifty constituents: {e}")
        return {}

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
        weighted_z_score = weighted_z_score.add(z_score.fillna(0) * weight, fill_value=0)

    return weighted_z_score

def generate_full_ranking(subset_size=None):
    """
    Orchestrates the data fetching, calculation, and report generation.
    """
    # 1. Fetch Tickers and Names
    tickers_dict = get_nifty_constituents()
    all_tickers = list(tickers_dict.keys())

    if subset_size:
        all_tickers = all_tickers[:subset_size]

    if not all_tickers:
        print("No tickers found.")
        return pd.DataFrame()

    # 2. Fetch Data
    prices = fetch_data(all_tickers, period="3y")

    # Filter valid stocks
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
    current_prices = prices.iloc[-1]
    ema_50 = prices.ewm(span=50, adjust=False).mean().iloc[-1]
    high_52 = prices.rolling(window=252).max().iloc[-1]

    # 5. Build Result DataFrame
    indices = {
        'Current': -1,
        '1M Ago': -22,
        '2M Ago': -43,
        '3M Ago': -64
    }

    max_idx = len(momentum_scores)

    def get_rank_series(offset_idx):
        if abs(offset_idx) >= max_idx:
            return pd.Series(np.nan, index=momentum_scores.columns)
        scores = momentum_scores.iloc[offset_idx]
        return scores.rank(ascending=False)

    df = pd.DataFrame(index=prices.columns)

    try:
        df['Momentum Score'] = momentum_scores.iloc[indices['Current']]
    except IndexError:
        df['Momentum Score'] = np.nan

    # Add Company Name using the mapping
    # Note: prices.columns are the symbols
    df['Company Name'] = df.index.map(tickers_dict)

    df['Price'] = current_prices
    df['50 EMA'] = ema_50
    df['52W High'] = high_52

    df['Current Rank'] = get_rank_series(indices['Current'])
    df['Rank 1M Ago'] = get_rank_series(indices['1M Ago'])
    df['Rank 2M Ago'] = get_rank_series(indices['2M Ago'])
    df['Rank 3M Ago'] = get_rank_series(indices['3M Ago'])

    df['Above 50 EMA'] = df['Price'] > df['50 EMA']
    df['Near 52W High'] = df['Price'] >= (0.8 * df['52W High'])
    df['Filters Passed'] = df['Above 50 EMA'] & df['Near 52W High']

    df = df.sort_values('Current Rank')
    df = df.reset_index().rename(columns={'index': 'Symbol'})

    return df

if __name__ == "__main__":
    print("Running Analysis...")
    df = generate_full_ranking(subset_size=20)
    print(df.head())
