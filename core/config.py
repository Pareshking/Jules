import os
import json

DEFAULT_INDICES_URLS = {
    "NIFTY 50": "https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
    "NIFTY NEXT 50": "https://niftyindices.com/IndexConstituent/ind_niftynext50list.csv",
    "NIFTY MIDCAP 150": "https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
    "NIFTY SMALLCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
    "NIFTY MICROCAP 250": "https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
    "NIFTY TOTAL MARKET": "https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv"
}

DEFAULT_MOMENTUM_WEIGHTS = {
    "1m": 0.10,
    "3m": 0.30,
    "6m": 0.30,
    "9m": 0.20,
    "12m": 0.10
}

def get_indices_urls():
    urls_json = os.environ.get("INDICES_URLS_JSON")
    if urls_json:
        try:
            return json.loads(urls_json)
        except json.JSONDecodeError:
            pass
    return DEFAULT_INDICES_URLS

def get_momentum_weights():
    weights_json = os.environ.get("MOMENTUM_WEIGHTS_JSON")
    if weights_json:
        try:
            return json.loads(weights_json)
        except json.JSONDecodeError:
            pass
    return DEFAULT_MOMENTUM_WEIGHTS

INDICES_URLS = get_indices_urls()
MOMENTUM_WEIGHTS = get_momentum_weights()
