import os
import json

# URLs for Nifty Indices Constituents
# Can be overridden by env var 'INDICES_URLS' (JSON string)
INDICES_URLS = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

if os.environ.get('INDICES_URLS'):
    try:
        INDICES_URLS = json.loads(os.environ['INDICES_URLS'])
    except json.JSONDecodeError:
        print("Warning: Failed to parse INDICES_URLS from environment variable.")

# Momentum Strategy Constants
# Windows in days (approx trading days: 1m=21, 3m=63, etc.)
# Can be overridden by env var 'MOMENTUM_WINDOWS' (JSON list of ints)
MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]
if os.environ.get('MOMENTUM_WINDOWS'):
    try:
        MOMENTUM_WINDOWS = json.loads(os.environ['MOMENTUM_WINDOWS'])
    except json.JSONDecodeError:
        print("Warning: Failed to parse MOMENTUM_WINDOWS from environment variable.")

# Weights corresponding to the windows
# Can be overridden by env var 'MOMENTUM_WEIGHTS' (JSON list of floats)
MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]
if os.environ.get('MOMENTUM_WEIGHTS'):
    try:
        MOMENTUM_WEIGHTS = json.loads(os.environ['MOMENTUM_WEIGHTS'])
    except json.JSONDecodeError:
        print("Warning: Failed to parse MOMENTUM_WEIGHTS from environment variable.")

# Minimum history required (days)
# Can be overridden by env var 'MIN_HISTORY_DAYS' (int)
MIN_HISTORY_DAYS = int(os.environ.get('MIN_HISTORY_DAYS', 260))
