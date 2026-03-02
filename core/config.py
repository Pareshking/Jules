
import os
import json

# URLs for Nifty Indices Constituents
default_indices_urls = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

env_indices_urls = os.environ.get("INDICES_URLS_JSON")
if env_indices_urls:
    try:
        INDICES_URLS = json.loads(env_indices_urls)
    except json.JSONDecodeError:
        INDICES_URLS = default_indices_urls
else:
    INDICES_URLS = default_indices_urls

# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
default_momentum_weights = [0.1, 0.3, 0.3, 0.2, 0.1]

env_momentum_weights = os.environ.get("MOMENTUM_WEIGHTS_JSON")
if env_momentum_weights:
    try:
        MOMENTUM_WEIGHTS = json.loads(env_momentum_weights)
    except json.JSONDecodeError:
        MOMENTUM_WEIGHTS = default_momentum_weights
else:
    MOMENTUM_WEIGHTS = default_momentum_weights

# Minimum history required (days)
MIN_HISTORY_DAYS = 260
