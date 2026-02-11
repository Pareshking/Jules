import os
import json

# URLs for Nifty Indices Constituents
# Allow overriding individual URLs via environment variables like NIFTY_50_URL
INDICES_URLS = {
    "NIFTY 50": os.getenv("NIFTY_50_URL", "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv"),
    "NIFTY NEXT 50": os.getenv("NIFTY_NEXT_50_URL", "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv"),
    "NIFTY MIDCAP 150": os.getenv("NIFTY_MIDCAP_150_URL", "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv"),
    "NIFTY SMALLCAP 250": os.getenv("NIFTY_SMALLCAP_250_URL", "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv"),
    "NIFTY MICROCAP 250": os.getenv("NIFTY_MICROCAP_250_URL", "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv"),
    "NIFTY TOTAL MARKET": os.getenv("NIFTY_TOTAL_MARKET_URL", "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv")
}

# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
# Can be overridden by passing a JSON list string, e.g. "[21, 63, ...]"
momentum_windows_env = os.getenv("MOMENTUM_WINDOWS")
if momentum_windows_env:
    try:
        MOMENTUM_WINDOWS = json.loads(momentum_windows_env)
    except json.JSONDecodeError:
        print("Warning: Invalid JSON for MOMENTUM_WINDOWS, using default.")
        MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]
else:
    MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
momentum_weights_env = os.getenv("MOMENTUM_WEIGHTS")
if momentum_weights_env:
    try:
        MOMENTUM_WEIGHTS = json.loads(momentum_weights_env)
    except json.JSONDecodeError:
        print("Warning: Invalid JSON for MOMENTUM_WEIGHTS, using default.")
        MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]
else:
    MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]

# Minimum history required (days)
MIN_HISTORY_DAYS = int(os.getenv("MIN_HISTORY_DAYS", 260))
