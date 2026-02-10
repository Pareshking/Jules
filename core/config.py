import os
import json

# URLs for Nifty Indices Constituents
# Allow overriding via environment variables.
# For example, export NIFTY_50_URL="http://example.com/nifty50.csv"
INDICES_URLS = {
    "NIFTY 50": os.environ.get("NIFTY_50_URL", "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv"),
    "NIFTY NEXT 50": os.environ.get("NIFTY_NEXT_50_URL", "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv"),
    "NIFTY MIDCAP 150": os.environ.get("NIFTY_MIDCAP_150_URL", "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv"),
    "NIFTY SMALLCAP 250": os.environ.get("NIFTY_SMALLCAP_250_URL", "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"),
    "NIFTY MICROCAP 250": os.environ.get("NIFTY_MICROCAP_250_URL", "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv"),
    "NIFTY TOTAL MARKET": os.environ.get("NIFTY_TOTAL_MARKET_URL", "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv")
}

# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
# Allow overriding via JSON string in env var MOMENTUM_WINDOWS
_windows_env = os.environ.get("MOMENTUM_WINDOWS")
if _windows_env:
    try:
        MOMENTUM_WINDOWS = json.loads(_windows_env)
    except json.JSONDecodeError:
        print("Warning: Invalid JSON for MOMENTUM_WINDOWS. Using default.")
        MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]
else:
    MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
# Allow overriding via JSON string in env var MOMENTUM_WEIGHTS
_weights_env = os.environ.get("MOMENTUM_WEIGHTS")
if _weights_env:
    try:
        MOMENTUM_WEIGHTS = json.loads(_weights_env)
    except json.JSONDecodeError:
        print("Warning: Invalid JSON for MOMENTUM_WEIGHTS. Using default.")
        MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]
else:
    MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]

# Minimum history required (days)
MIN_HISTORY_DAYS = int(os.environ.get("MIN_HISTORY_DAYS", 260))
