import os
import json

# URLs for Nifty Indices Constituents
INDICES_URLS = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

# Override from environment variable if present
if "INDICES_URLS_JSON" in os.environ:
    try:
        INDICES_URLS = json.loads(os.environ["INDICES_URLS_JSON"])
    except json.JSONDecodeError:
        print("Warning: Failed to parse INDICES_URLS_JSON environment variable.")

# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]

# Override from environment variable if present
if "MOMENTUM_WEIGHTS_JSON" in os.environ:
    try:
        MOMENTUM_WEIGHTS = json.loads(os.environ["MOMENTUM_WEIGHTS_JSON"])
    except json.JSONDecodeError:
        print("Warning: Failed to parse MOMENTUM_WEIGHTS_JSON environment variable.")

# Minimum history required (days)
MIN_HISTORY_DAYS = 260
