import pandas as pd
import yfinance as yf
import requests
import io
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from typing import List
from .config import INDICES_URLS

def get_constituents(indices_names: List[str]) -> List[str]:
    """
    Fetches constituents for the selected indices from the NSE website.
    Returns a list of unique symbols with '.NS' appended.
    """
    all_symbols = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Setup retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    for index_name in indices_names:
        url = INDICES_URLS.get(index_name)
        if not url:
            print(f"Warning: URL for {index_name} not found.")
            continue

        print(f"Fetching {index_name} from {url}...")
        try:
            response = http.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            csv_content = response.content.decode('utf-8')

            # Read CSV
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
                # Fallback: usually 3rd column
                if len(df.columns) > 2:
                    symbol_col = df.columns[2]

            if symbol_col:
                symbols = df[symbol_col].dropna().astype(str).tolist()
                all_symbols.update([s.strip() for s in symbols])
            else:
                print(f"Warning: Could not identify Symbol column for {index_name}")

        except Exception as e:
            print(f"Error fetching {index_name}: {e}")

    # Clean and append .NS
    cleaned_symbols = []
    for sym in all_symbols:
        if not sym:
            continue
        # Filter out dummy symbols often found in Nifty CSVs
        if sym.upper().startswith("DUMMY"):
            continue
        cleaned_symbols.append(f"{sym}.NS")

    return sorted(list(set(cleaned_symbols)))

def fetch_price_data(tickers: List[str], period: str = "3y") -> pd.DataFrame:
    """
    Fetches OHLCV data for the given tickers using yfinance.
    Returns a DataFrame of Close prices.
    """
    if not tickers:
        return pd.DataFrame()

    print(f"Fetching data for {len(tickers)} tickers...")
    try:
        # auto_adjust=True ensures Close is adjusted for splits and dividends
        # threads=True is default but good to be explicit
        data = yf.download(tickers, period=period, auto_adjust=True, progress=False, threads=True)
    except Exception as e:
        print(f"Error fetching data via yfinance: {e}")
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()

    # Extract Close prices
    close_data = pd.DataFrame()

    # Check if MultiIndex columns (Price, Ticker)
    if isinstance(data.columns, pd.MultiIndex):
        try:
            close_data = data['Close']
        except KeyError:
            # Fallback if structure is unexpected
             pass
    elif 'Close' in data.columns:
        close_data = data['Close']

    # If close_data is still empty, return empty dataframe
    if close_data.empty:
        # If passed single ticker, yfinance might just return OHLC without Ticker level
        # If 'Close' was not found above, maybe it failed
        return pd.DataFrame()

    # Handle single ticker returning Series
    if isinstance(close_data, pd.Series):
        close_data = close_data.to_frame()
        if len(tickers) == 1:
            close_data.columns = tickers

    # Ensure columns are tickers (sometimes if 1 ticker, column might be 'Close')
    if len(tickers) == 1 and close_data.shape[1] == 1 and close_data.columns[0] == 'Close':
        close_data.columns = tickers

    # Final check for MultiIndex in close_data columns (if it's not flattened)
    if isinstance(close_data.columns, pd.MultiIndex):
        close_data.columns = close_data.columns.get_level_values(0)

    return close_data
