import streamlit as st
import pandas as pd
from core.config import INDICES_URLS
from core.fetcher import get_nifty_constituents, get_historical_prices
from core.momentum import calculate_momentum

st.set_page_config(page_title="Momentum Investing Framework", layout="wide")

@st.cache_data(ttl=3600)
def fetch_symbols(selected_indices):
    urls = [INDICES_URLS[idx] for idx in selected_indices]
    return get_nifty_constituents(urls)

@st.cache_data(ttl=3600)
def fetch_data_and_calculate_momentum(symbols):
    prices_df = get_historical_prices(symbols, period="3y")
    return calculate_momentum(prices_df)

def color_velocity(val):
    if not isinstance(val, str):
        return ''
    if val.startswith('+'):
        return 'color: green'
    elif val.startswith('-'):
        return 'color: red'
    elif val == '0':
        return 'color: black'
    else:
        return ''

st.title("Momentum Investing Quant Framework")
st.markdown("This application ranks stocks based on a robust momentum strategy using weighted Z-scores of Sharpe Ratios.")

st.sidebar.header("Index Selection")
st.sidebar.markdown("Select one or more indices to scan:")
selected_indices = st.sidebar.multiselect(
    "Available Indices",
    list(INDICES_URLS.keys()),
    default=["NIFTY 50", "NIFTY NEXT 50"]
)

if st.sidebar.button("Run Momentum Scan"):
    if not selected_indices:
        st.warning("Please select at least one index to scan.")
    else:
        with st.spinner("Fetching index constituents..."):
            symbols = fetch_symbols(selected_indices)

        if not symbols:
            st.error("Failed to fetch symbols for the selected indices.")
        else:
            with st.spinner(f"Fetching historical data and calculating momentum for {len(symbols)} symbols..."):
                results = fetch_data_and_calculate_momentum(symbols)

            if results.empty:
                st.warning("No stocks passed the hard filters (Price > 50 EMA and Price >= 80% of 52-Week High).")
            else:
                st.success(f"Scan complete! {len(results)} stocks passed the filters.")

                # Format numerical columns
                format_dict = {
                    'Momentum Score': "{:.2f}",
                    'Price': "{:.2f}",
                    '50 EMA': "{:.2f}",
                    '52W High': "{:.2f}",
                    'Current Rank': "{:.0f}",
                    'Past Rank': "{:.0f}"
                }

                # We need to add '+' to positive rank velocity
                def format_velocity(val):
                    if pd.isna(val):
                        return "NaN"
                    if val > 0:
                        return f"+{int(val)}"
                    return f"{int(val)}"

                # Format for display
                display_df = results.copy()
                display_df['Rank Velocity'] = display_df['Rank Velocity'].apply(format_velocity)

                # Apply styling using .map() per memory
                styled_df = display_df.style.format(format_dict).map(color_velocity, subset=['Rank Velocity'])

                st.dataframe(styled_df, use_container_width=True)

                # CSV Export
                csv = results.to_csv(index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name="momentum_ranks.csv",
                    mime="text/csv",
                )
