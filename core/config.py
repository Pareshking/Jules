import os
import json

# URLs for Nifty Indices Constituents
# Allow overriding via environment variable INDICES_URLS (as JSON string)
_indices_urls_env = os.environ.get("INDICES_URLS")
if _indices_urls_env:
    try:
        INDICES_URLS = json.loads(_indices_urls_env)
    except json.JSONDecodeError:
        print("Warning: Failed to parse INDICES_URLS from environment. Using defaults.")
        INDICES_URLS = {
            "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
            "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
            "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
            "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
            "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
            "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
        }
else:
    INDICES_URLS = {
        "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
        "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
        "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
        "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
        "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
        "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
    }

# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
# Allow overriding via environment variable MOMENTUM_WEIGHTS (as JSON string)
_momentum_weights_env = os.environ.get("MOMENTUM_WEIGHTS")
if _momentum_weights_env:
    try:
        MOMENTUM_WEIGHTS = json.loads(_momentum_weights_env)
    except json.JSONDecodeError:
        print("Warning: Failed to parse MOMENTUM_WEIGHTS from environment. Using defaults.")
        MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]
else:
    MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]

# Minimum history required (days)
MIN_HISTORY_DAYS = 260
