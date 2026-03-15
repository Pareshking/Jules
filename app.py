import streamlit as st
import pandas as pd
from core.config import INDICES_URLS
from core.fetcher import fetch_constituents, fetch_historical_prices
from core.momentum import calculate_momentum

# Streamlit App Configuration
st.set_page_config(page_title="Momentum Quant Framework", layout="wide")

# Title and Description
st.title("📈 Momentum Quant Framework")
st.markdown("A quantitative momentum investing framework focused on Relative Strength and Rank Velocity.")

# Sidebar for Index Selection
st.sidebar.header("Configuration")
st.sidebar.markdown("Select one or a combination of NSE market cap indices to scan:")
selected_indices = st.sidebar.multiselect(
    "Select Indices",
    options=list(INDICES_URLS.keys()),
    default=["NIFTY 50"]
)

# Caching data fetching functions
@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def cached_fetch_constituents(indices):
    return fetch_constituents(indices)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_fetch_prices(symbols):
    # Fetch 3 years of data to ensure enough history for 52W high and 12m momentum
    return fetch_historical_prices(symbols, period='3y', interval='1d')

def color_rank_velocity(val):
    """Conditional formatting for Rank Velocity"""
    if pd.isna(val):
        return ''
    if val > 0:
        return 'color: green'
    elif val < 0:
        return 'color: red'
    else:
        return 'color: black'

def format_rank_velocity(val):
    """Format Rank Velocity with + or - sign"""
    if pd.isna(val):
        return ""
    if val > 0:
        return f"+{int(val)}"
    elif val < 0:
        return f"{int(val)}"
    else:
        return "0"

if st.sidebar.button("Scan Momentum"):
    if not selected_indices:
        st.warning("Please select at least one index to scan.")
    else:
        with st.spinner("Fetching constituents..."):
            symbols = cached_fetch_constituents(selected_indices)

        if not symbols:
            st.error("Could not fetch constituents. Please check the index URLs or your internet connection.")
        else:
            st.info(f"Scanning {len(symbols)} symbols from selected indices...")

            with st.spinner("Fetching historical prices (this may take a minute)..."):
                prices_df = cached_fetch_prices(symbols)

            if prices_df.empty:
                st.error("Could not fetch historical prices.")
            else:
                with st.spinner("Calculating Momentum..."):
                    results_df = calculate_momentum(prices_df)

                if results_df.empty:
                    st.warning("No stocks passed the momentum filters.")
                else:
                    st.success(f"Momentum scan complete! {len(results_df)} stocks passed the filters.")

                    # Prepare dataframe for display
                    display_df = results_df.copy()

                    # Ensure NaNs are filled before applying styling to prevent silent rendering failures
                    display_df = display_df.fillna(0)

                    # Format columns
                    # Momentum Score, Price, 50 EMA, 52W High to 2 decimal places
                    # Ranks as integer
                    # Rank Velocity with sign

                    # Apply styling
                    styled_df = display_df.style\
                        .format({
                            'Momentum_Score': '{:.2f}',
                            'Price': '{:.2f}',
                            '50_EMA': '{:.2f}',
                            '52W_High': '{:.2f}',
                            'Rank': '{:.0f}',
                            'Rank_Velocity': format_rank_velocity
                        })\
                        .map(color_rank_velocity, subset=['Rank_Velocity'])

                    st.dataframe(styled_df, use_container_width=True, hide_index=True)

                    # CSV Export
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name='momentum_results.csv',
                        mime='text/csv',
                    )
