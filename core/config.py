import os
import json

# Default configuration for Indices URLs
DEFAULT_INDICES_URLS = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

# Try to load custom URLs from environment variable
urls_json = os.environ.get("INDICES_URLS_JSON")
if urls_json:
    try:
        INDICES_URLS = json.loads(urls_json)
    except json.JSONDecodeError:
        print("Error decoding INDICES_URLS_JSON. Using default URLs.")
        INDICES_URLS = DEFAULT_INDICES_URLS
else:
    INDICES_URLS = DEFAULT_INDICES_URLS

# Default configuration for Momentum Weights
DEFAULT_MOMENTUM_WEIGHTS = {
    "1m": 0.10,
    "3m": 0.30,
    "6m": 0.30,
    "9m": 0.20,
    "12m": 0.10
}

# Try to load custom weights from environment variable
weights_json = os.environ.get("MOMENTUM_WEIGHTS_JSON")
if weights_json:
    try:
        MOMENTUM_WEIGHTS = json.loads(weights_json)
    except json.JSONDecodeError:
        print("Error decoding MOMENTUM_WEIGHTS_JSON. Using default weights.")
        MOMENTUM_WEIGHTS = DEFAULT_MOMENTUM_WEIGHTS
else:
    MOMENTUM_WEIGHTS = DEFAULT_MOMENTUM_WEIGHTS

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
