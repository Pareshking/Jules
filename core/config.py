import os

# URLs for Nifty Indices Constituents
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
# Allow override via env var as comma-separated string
momentum_windows_env = os.environ.get("MOMENTUM_WINDOWS")
if momentum_windows_env:
    MOMENTUM_WINDOWS = [int(w.strip()) for w in momentum_windows_env.split(",")]
else:
    MOMENTUM_WINDOWS = [21, 63, 126, 189, 252]

# Weights corresponding to the windows
# Allow override via env var as comma-separated string
momentum_weights_env = os.environ.get("MOMENTUM_WEIGHTS")
if momentum_weights_env:
    MOMENTUM_WEIGHTS = [float(w.strip()) for w in momentum_weights_env.split(",")]
else:
    MOMENTUM_WEIGHTS = [0.1, 0.3, 0.3, 0.2, 0.1]

# Minimum history required (days)
MIN_HISTORY_DAYS = int(os.environ.get("MIN_HISTORY_DAYS", 260))
