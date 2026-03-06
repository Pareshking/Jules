import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd
import yfinance as yf
import io
import datetime

def get_session():
    session = requests.Session()
    # 3 retries, backoff factor 0.3
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[ 500, 502, 503, 504 ])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    # Require a User-Agent for niftyindices.com
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

def get_nifty_constituents(urls):
    """
    Fetches Nifty index constituents from a list of URLs and returns a deduplicated list of symbols.
    Filters out symbols starting with 'DUMMY'.
    Appends '.NS' to each symbol for yfinance.
    """
    session = get_session()
    all_symbols = set()

    for url in urls:
        try:
            response = session.get(url)
            response.raise_for_status()
            # Read CSV content
            df = pd.read_csv(io.StringIO(response.text))

            # Identify the symbol column
            symbol_col = None
            for col in df.columns:
                if 'symbol' in col.lower() or 'ticker' in col.lower():
                    symbol_col = col
                    break

            if symbol_col:
                symbols = df[symbol_col].dropna().astype(str).tolist()
                for symbol in symbols:
                    symbol = symbol.strip()
                    if symbol and not symbol.upper().startswith('DUMMY'):
                        all_symbols.add(symbol + '.NS')
            else:
                print(f"Warning: Could not find a symbol column in {url}. Columns found: {df.columns.tolist()}")
        except Exception as e:
            print(f"Error fetching data from {url}: {e}")

    return list(all_symbols)

def get_historical_prices(symbols, period="3y"):
    """
    Fetches historical price data from yfinance.
    Flattens MultiIndex columns if present and removes timezone info from datetime index.
    """
    if not symbols:
        return pd.DataFrame()

    try:
        # Fetch data
        data = yf.download(symbols, period=period, progress=False)

        # Get 'Close' prices
        if 'Close' in data.columns:
            df = data['Close']
        elif 'Adj Close' in data.columns:
            df = data['Adj Close']
        else:
            print("Warning: Neither 'Close' nor 'Adj Close' found in yfinance data.")
            # Return an empty dataframe to signify no usable close prices
            return pd.DataFrame()

        # Ensure it's a DataFrame, handle single symbol case
        if isinstance(df, pd.Series):
            df = df.to_frame()
            df.columns = [symbols[0]]

        # Flatten multiindex columns if present (yfinance usually returns MultiIndex columns for multiple tickers and columns)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[1] if isinstance(col, tuple) else col for col in df.columns]
        elif isinstance(data.columns, pd.MultiIndex):
            # If the original data had multiindex, df might also have inherited something weird or be a simple index.
            pass

        # Remove timezone information from index for consistency
        if isinstance(df.index, pd.DatetimeIndex) and df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        return df
    except Exception as e:
        print(f"Error fetching historical prices: {e}")
        return pd.DataFrame()
