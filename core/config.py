import os
import json

# URLs for Nifty Indices Constituents
DEFAULT_INDICES_URLS = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

# Load from environment variable if present (JSON string)
env_indices = os.environ.get("INDICES_URLS")
if env_indices:
    try:
        INDICES_URLS = json.loads(env_indices)
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in INDICES_URLS environment variable. Using defaults.")
        INDICES_URLS = DEFAULT_INDICES_URLS
else:
    INDICES_URLS = DEFAULT_INDICES_URLS


# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
DEFAULT_MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]

env_weights = os.environ.get("MOMENTUM_WEIGHTS")
if env_weights:
    try:
        MOMENTUM_WEIGHTS = json.loads(env_weights)
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in MOMENTUM_WEIGHTS environment variable. Using defaults.")
        MOMENTUM_WEIGHTS = DEFAULT_MOMENTUM_WEIGHTS
else:
    MOMENTUM_WEIGHTS = DEFAULT_MOMENTUM_WEIGHTS

# Minimum history required (days)
MIN_HISTORY_DAYS = 260
