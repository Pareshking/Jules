import pandas as pd
import yfinance as yf
import requests
import io
import time
from typing import List
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .config import INDICES_URLS

def get_session():
    """
    Creates a requests session with retry logic.
    """
    session = requests.Session()
    retry = Retry(
        total=3,
        read=3,
        connect=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_constituents(indices_names: List[str]) -> List[str]:
    """
    Fetches constituents for the selected indices from the NSE website.
    Returns a list of unique symbols with '.NS' appended.
    Filters out symbols starting with 'DUMMY'.
    """
    all_symbols = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    session = get_session()

    for index_name in indices_names:
        url = INDICES_URLS.get(index_name)
        if not url:
            print(f"Warning: URL for {index_name} not found.")
            continue

        print(f"Fetching {index_name} from {url}...")
        try:
            response = session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            csv_content = response.content.decode('utf-8')

            # Read CSV
            df = pd.read_csv(io.StringIO(csv_content), sep=",")

            # Normalize column names
            df.columns = [c.strip() for c in df.columns]

            # Identify Symbol column
            symbol_col = None
            possible_names = ['Symbol', 'symbol', 'SYMBOL', 'Ticker', 'ticker']
            for col in df.columns:
                if col in possible_names:
                    symbol_col = col
                    break

            if not symbol_col:
                # Fallback: check if 'Symbol' is part of any column name or try 3rd column
                for col in df.columns:
                    if 'symbol' in col.lower():
                        symbol_col = col
                        break

                if not symbol_col and len(df.columns) > 2:
                     # Usually 3rd column in Nifty CSVs
                    symbol_col = df.columns[2]

            if symbol_col:
                symbols = df[symbol_col].dropna().astype(str).tolist()
                # Clean and filter
                for sym in symbols:
                    s = sym.strip()
                    if s and not s.upper().startswith("DUMMY"):
                        all_symbols.add(s)
            else:
                print(f"Warning: Could not identify Symbol column for {index_name}")

        except Exception as e:
            print(f"Error fetching {index_name}: {e}")

    # Clean and append .NS
    cleaned_symbols = [f"{sym}.NS" for sym in all_symbols]
    return sorted(list(set(cleaned_symbols)))

def fetch_price_data(tickers: List[str], period: str = "3y") -> pd.DataFrame:
    """
    Fetches OHLCV data for the given tickers using yfinance.
    Returns a DataFrame of Close prices.
    Handles MultiIndex columns returned by yfinance.
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
    # If multiple tickers, 'Close' is a DataFrame. If single, Series.
    # yfinance output structure changed recently, 'Close' might be top level or under Price type

    # Check if MultiIndex columns (Price, Ticker)
    # yfinance typically returns:
    #                 Close
    # Ticker      AAPL  MSFT
    # Date

    close_data = None

    if isinstance(data.columns, pd.MultiIndex):
        # Try to access 'Close' level 0
        try:
            close_data = data['Close']
        except KeyError:
            # Maybe it's flattened already or structured differently?
            # Check levels
            if 'Close' in data.columns.get_level_values(0):
                 # This is tricky without knowing exact structure, but usually data['Close'] works if level 0 is Price
                 pass
            elif 'Close' in data.columns.get_level_values(1):
                # Swap levels?
                close_data = data.xs('Close', axis=1, level=1)
            else:
                # Just take the dataframe if it's already close prices? Unlikely.
                print("Warning: 'Close' column not found in MultiIndex data.")
                return pd.DataFrame()
    elif 'Close' in data.columns:
        close_data = data['Close']
    else:
        # Assuming single ticker and data IS the OHLCV for that ticker
        # Or maybe it returned just Close data?
        # Let's assume data is OHLCV for single ticker if columns are Open, High, Low, Close...
        if 'Close' not in data.columns:
             # Fallback
             close_data = data
        else:
            close_data = data['Close']

    # If close_data is None, something went wrong
    if close_data is None:
         return pd.DataFrame()

    # Ensure it's a DataFrame (dates x tickers)
    if isinstance(close_data, pd.Series):
        close_data = close_data.to_frame()
        # If it's a series, the column name might be 'Close', rename to ticker
        if len(tickers) == 1:
            close_data.columns = tickers

    # Validation: Columns should be tickers
    # If we requested multiple tickers, close_data columns should be ticker names.

    return close_data
