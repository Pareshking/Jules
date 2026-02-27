import pandas as pd
import yfinance as yf
import requests
import io
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import List
from .config import INDICES_URLS

def get_session():
    """
    Creates a requests session with retry logic.
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_constituents(indices_names: List[str]) -> List[str]:
    """
    Fetches constituents for the selected indices from the NSE website.
    Returns a list of unique symbols with '.NS' appended.
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
            for col in df.columns:
                if col.lower().strip() == 'symbol':
                    symbol_col = col
                    break

            # Fallback for some files where it might be 'Symbol ' or similar
            if not symbol_col:
                for col in df.columns:
                    if 'symbol' in col.lower():
                        symbol_col = col
                        break

            if not symbol_col:
                # Fallback: usually 3rd column
                if len(df.columns) > 2:
                    symbol_col = df.columns[2]
                    print(f"Warning: Could not identify Symbol column for {index_name}. Using 3rd column: {symbol_col}")

            if symbol_col:
                symbols = df[symbol_col].dropna().astype(str).tolist()
                # Filter out dummy/invalid symbols
                valid_symbols = [s.strip() for s in symbols if s.strip().upper() != 'SYMBOL' and not s.strip().startswith('DUMMY')]
                all_symbols.update(valid_symbols)
            else:
                print(f"Error: Could not identify Symbol column for {index_name}")

        except Exception as e:
            print(f"Error fetching {index_name}: {e}")

    # Clean and append .NS
    cleaned_symbols = [f"{sym}.NS" for sym in all_symbols if sym]
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
    close_data = None

    # Handle MultiIndex columns (Price, Ticker)
    if isinstance(data.columns, pd.MultiIndex):
        try:
            # Try to get 'Close' level
            if 'Close' in data.columns.get_level_values(0):
                 close_data = data['Close']
            else:
                # Maybe checking levels differently
                # yfinance often returns (Price, Ticker)
                # Ensure we get the Close price
                close_data = data.xs('Close', axis=1, level=0, drop_level=True)
        except KeyError:
            # Fallback: if structure is different
            pass

    if close_data is None:
        if 'Close' in data.columns:
            close_data = data['Close']
        else:
            # Assume it's already Close data if single column per ticker or just one ticker
            close_data = data

    # Ensure it's a DataFrame (dates x tickers)
    if isinstance(close_data, pd.Series):
        close_data = close_data.to_frame()
        if len(tickers) == 1:
            close_data.columns = tickers

    # Clean Index (Timezone)
    if isinstance(close_data.index, pd.DatetimeIndex):
         if close_data.index.tz is not None:
             close_data.index = close_data.index.tz_localize(None)

    return close_data
