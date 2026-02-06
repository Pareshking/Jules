import streamlit as st
import pandas as pd
import momentum

st.set_page_config(page_title="Nifty 750 Momentum Ranking", layout="wide")

st.title("Nifty 750 Momentum Ranking System")

st.markdown("""
This application ranks Nifty Total Market stocks based on a multi-timeframe volatility-adjusted momentum strategy.

**Methodology:**
- **Universe:** Nifty Total Market (~750 stocks)
- **Score:** Weighted Average of Z-Scores of Sharpe Ratios (1m, 3m, 6m, 9m, 12m)
- **Weights:** 10% (1m), 30% (3m), 30% (6m), 20% (9m), 10% (12m)
- **Filters:**
    - Price > 50 EMA
    - Price >= 0.8 * 52-Week High
""")

# Sidebar
st.sidebar.header("Configuration")

use_full_universe = st.sidebar.checkbox("Use Full Universe (Nifty Total Market)", value=True)
subset_size = None if use_full_universe else 20

if 'results' not in st.session_state:
    st.session_state.results = None

if st.sidebar.button("Run Analysis"):
    with st.spinner("Fetching data and calculating momentum scores... This may take a few minutes for the full universe."):
        try:
            df = momentum.generate_full_ranking(subset_size=subset_size)

            if df.empty:
                st.error("No data found or calculation failed. Please check logs.")
                st.session_state.results = None
            else:
                st.session_state.results = df
                st.success(f"Analysis complete! processed {len(df)} stocks.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.exception(e)
            st.session_state.results = None

if st.session_state.results is not None:
    df = st.session_state.results

    # Display Top 50
    st.subheader("Top Ranked Stocks")

    # Format columns
    display_cols = [
        'Current Rank', 'Symbol', 'Momentum Score',
        'Price', 'Filters Passed',
        'Above 50 EMA', 'Near 52W High',
        'Rank 1M Ago', 'Rank 2M Ago', 'Rank 3M Ago'
    ]

    # Ensure columns exist
    display_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(df[display_cols].style.format({
        'Momentum Score': '{:.2f}',
        'Price': '{:.2f}',
        'Current Rank': '{:.0f}',
        'Rank 1M Ago': '{:.0f}',
        'Rank 2M Ago': '{:.0f}',
        'Rank 3M Ago': '{:.0f}'
    }))

    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Full Results as CSV",
        csv,
        "nifty_momentum_ranking.csv",
        "text/csv",
        key='download-csv'
    )
