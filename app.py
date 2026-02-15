import streamlit as st
import pandas as pd
from core.config import INDICES_URLS
from core.fetcher import get_constituents, fetch_price_data
from core.momentum import MomentumAnalyzer

# Page Config
st.set_page_config(
    page_title="Nifty Momentum Ranking",
    page_icon="📈",
    layout="wide"
)

# Caching wrappers
@st.cache_data(ttl=3600, show_spinner=False)
def get_tickers_cached(indices_names):
    return get_constituents(indices_names)

@st.cache_data(ttl=3600, show_spinner=False)
def get_prices_cached(tickers):
    # Fetch 3 years of data to ensure enough history for 1y momentum + lookbacks
    return fetch_price_data(tickers, period="3y")

@st.cache_data(show_spinner=False)
def calculate_rankings_cached(prices):
    analyzer = MomentumAnalyzer(prices)
    return analyzer.get_rankings()

# Main App
def main():
    st.title("🇮🇳 Nifty Momentum Ranking System")
    st.markdown("""
    This application ranks Indian stocks based on a **Volatility-Adjusted Momentum** strategy.

    **Strategy:**
    - Weighted Z-Scores of Sharpe Ratios (1m, 3m, 6m, 9m, 12m).
    - **Filters:** Price > 50 EMA and Price within 20% of 52-Week High.
    """)

    # Sidebar
    st.sidebar.header("Configuration")

    available_indices = list(INDICES_URLS.keys())
    selected_indices = st.sidebar.multiselect(
        "Select Indices to Include:",
        options=available_indices,
        default=["NIFTY 50"]
    )

    if st.sidebar.button("Run Analysis", type="primary"):
        if not selected_indices:
            st.error("Please select at least one index.")
            return

        status_text = st.empty()
        progress_bar = st.progress(0)

        try:
            # 1. Fetch Constituents
            status_text.text("Fetching Index Constituents...")
            tickers = get_tickers_cached(selected_indices)
            progress_bar.progress(25)

            if not tickers:
                st.error("No tickers found for the selected indices.")
                status_text.empty()
                progress_bar.empty()
                return

            st.info(f"Identified {len(tickers)} unique stocks from selected indices.")

            # 2. Fetch Prices
            status_text.text(f"Fetching Price Data for {len(tickers)} stocks... (This may take a moment)")
            prices = get_prices_cached(tickers)
            progress_bar.progress(75)

            if prices.empty:
                st.error("Failed to fetch price data.")
                status_text.empty()
                progress_bar.empty()
                return

            # 3. Calculate Momentum
            status_text.text("Calculating Momentum Scores and Ranks...")
            results = calculate_rankings_cached(prices)
            progress_bar.progress(100)

            status_text.empty()
            progress_bar.empty()

            if results.empty:
                st.warning("Analysis completed but returned no results (maybe no stocks passed filters or data issues).")
            else:
                st.success(f"Analysis Complete! {len(results)} stocks ranked.")

                # Display Options
                st.subheader("Ranked Results")

                # Column formatting configuration
                format_mapping = {
                    'Momentum Score': '{:.2f}',
                    'Price': '{:.2f}',
                    '50 EMA': '{:.2f}',
                    '52W High': '{:.2f}',
                    'Current Rank': '{:.0f}',
                    'Rank 1M Ago': '{:.0f}',
                    'Rank 2M Ago': '{:.0f}',
                    'Rank 3M Ago': '{:.0f}',
                    'Rank Velocity': '{:+.0f}'
                }

                # Filter columns to display
                cols_to_show = [
                    'Current Rank', 'Symbol', 'Momentum Score', 'Rank Velocity', 'Price',
                    'Filters Passed', 'Above 50 EMA', 'Near 52W High',
                    'Rank 1M Ago', 'Rank 2M Ago', 'Rank 3M Ago'
                ]

                # Ensure columns exist
                cols_to_show = [c for c in cols_to_show if c in results.columns]

                def color_velocity(val):
                    if pd.isna(val):
                        return ''
                    color = 'green' if val > 0 else 'red' if val < 0 else 'inherit'
                    return f'color: {color}'

                st.dataframe(
                    results[cols_to_show].style.format(format_mapping, na_rep="").map(color_velocity, subset=['Rank Velocity']),
                    use_container_width=True,
                    height=600
                )

                # Download CSV
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Full Results CSV",
                    data=csv,
                    file_name="nifty_momentum_ranks.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            # Raise for debugging in logs
            raise e

if __name__ == "__main__":
    main()
