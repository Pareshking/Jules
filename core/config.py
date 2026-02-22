import os
import json

# URLs for Nifty Indices Constituents
INDICES_URLS_DEFAULT = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

# Override from environment variable if available
indices_env = os.environ.get("INDICES_URLS_JSON")
if indices_env:
    try:
        INDICES_URLS = json.loads(indices_env)
    except json.JSONDecodeError:
        print("Warning: Failed to parse INDICES_URLS_JSON. Using defaults.")
        INDICES_URLS = INDICES_URLS_DEFAULT
else:
    INDICES_URLS = INDICES_URLS_DEFAULT


# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
MOMENTUM_WEIGHTS_DEFAULT = [0.1, 0.3, 0.3, 0.2, 0.1]

# Override from environment variable if available
weights_env = os.environ.get("MOMENTUM_WEIGHTS_JSON")
if weights_env:
    try:
        MOMENTUM_WEIGHTS = json.loads(weights_env)
    except json.JSONDecodeError:
        print("Warning: Failed to parse MOMENTUM_WEIGHTS_JSON. Using defaults.")
        MOMENTUM_WEIGHTS = MOMENTUM_WEIGHTS_DEFAULT
else:
    MOMENTUM_WEIGHTS = MOMENTUM_WEIGHTS_DEFAULT

# Minimum history required (days)
MIN_HISTORY_DAYS = 260
