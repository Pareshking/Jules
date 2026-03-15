import io
import time
import requests
import pandas as pd
import yfinance as yf
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from core.config import INDICES_URLS, HEADERS

def get_session():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def fetch_constituents(index_names):
    """Fetch and combine constituents from selected index names."""
    if not isinstance(index_names, list):
        index_names = [index_names]

    session = get_session()
    all_symbols = set()

    for name in index_names:
        if name in INDICES_URLS:
            url = INDICES_URLS[name]
            try:
                response = session.get(url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                # Parse CSV content
                df = pd.read_csv(io.StringIO(response.text))

                # Check column name (usually 'Symbol' or 'Symbol \n')
                symbol_col = next((col for col in df.columns if 'Symbol' in col), None)
                if symbol_col:
                    symbols = df[symbol_col].dropna().str.strip().tolist()
                    # Filter out symbols starting with 'DUMMY'
                    valid_symbols = [s for s in symbols if not s.startswith('DUMMY')]
                    all_symbols.update(valid_symbols)
            except Exception as e:
                print(f"Error fetching {name} from {url}: {e}")

    return sorted(list(all_symbols))

def fetch_historical_prices(symbols, period='3y', interval='1d'):
    """Fetch historical price data for symbols using yfinance."""
    # Append .NS for NSE stocks
    yf_symbols = [f"{sym}.NS" for sym in symbols]

    try:
        # Download data
        data = yf.download(
            tickers=yf_symbols,
            period=period,
            interval=interval,
            group_by='ticker',
            auto_adjust=False,
            prepost=False,
            threads=True,
            progress=False
        )

        # Flatten MultiIndex columns if necessary
        if isinstance(data.columns, pd.MultiIndex):
            # We want 'Close' prices for each ticker.
            # yfinance groups by ticker when group_by='ticker' is used
            # so columns are (Ticker, Open/High/Low/Close/Volume)
            close_data = {}
            for ticker in yf_symbols:
                if ticker in data.columns.levels[0]:
                    if 'Close' in data[ticker].columns:
                        close_data[ticker.replace('.NS', '')] = data[ticker]['Close']

            # Combine back into a DataFrame
            df = pd.DataFrame(close_data)
        else:
            # Single ticker case
            if 'Close' in data.columns:
                df = pd.DataFrame({symbols[0]: data['Close']})
            else:
                df = pd.DataFrame()

        # Remove timezone information from datetime index to ensure consistency
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        return df

    except Exception as e:
        print(f"Error fetching historical prices: {e}")
        return pd.DataFrame()
