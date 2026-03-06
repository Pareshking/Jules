import pandas as pd
import numpy as np
from core.config import MOMENTUM_WEIGHTS

def calculate_momentum(prices_df):
    """
    Calculates momentum scores, ranks, and applies hard filters.

    Args:
        prices_df (pd.DataFrame): DataFrame of historical closing prices.

    Returns:
        pd.DataFrame: DataFrame with calculated momentum metrics.
    """
    if prices_df.empty:
        return pd.DataFrame()

    # Calculate daily returns
    daily_returns = prices_df.pct_change()

    # Define lookback periods in trading days (approx 21 days per month)
    periods = {
        '1m': 21,
        '3m': 63,
        '6m': 126,
        '9m': 189,
        '12m': 252
    }

    # Store Sharpe Ratios for each period
    sharpes = {}

    for period_name, days in periods.items():
        if len(prices_df) >= days:
            # Calculate return over the period
            period_returns = prices_df.pct_change(periods=days)
            # Annualized volatility over the period
            volatility = daily_returns.rolling(window=days).std() * np.sqrt(252)

            # Use latest values
            latest_return = period_returns.iloc[-1]
            latest_vol = volatility.iloc[-1]

            # Avoid division by zero
            latest_vol = latest_vol.replace(0, np.nan)

            # Assuming risk-free rate is 0 for simplicity, adjust if needed
            sharpe_ratio = latest_return / latest_vol
            sharpes[period_name] = sharpe_ratio
        else:
            # Not enough data for this period
            sharpes[period_name] = pd.Series(index=prices_df.columns, dtype=float)

    # Convert sharpes dictionary to DataFrame
    sharpes_df = pd.DataFrame(sharpes)

    # Drop rows where all sharpe ratios are NaN
    sharpes_df.dropna(how='all', inplace=True)

    # Calculate Z-scores for each period's Sharpe ratio across all stocks
    z_scores = (sharpes_df - sharpes_df.mean()) / sharpes_df.std()

    # Calculate Momentum Score as weighted average of Z-scores
    # Handle cases where some Z-scores might be missing due to lack of history
    weighted_sum = pd.Series(0, index=z_scores.index, dtype=float)
    total_weights = pd.Series(0, index=z_scores.index, dtype=float)

    for period, weight in MOMENTUM_WEIGHTS.items():
        if period in z_scores.columns:
            valid_z = z_scores[period].notna()
            weighted_sum[valid_z] += z_scores[period][valid_z] * weight
            total_weights[valid_z] += weight

    # Calculate final score, dividing by total weight to account for missing periods
    momentum_scores = weighted_sum / total_weights.replace(0, np.nan)

    # Calculate hard filters
    latest_prices = prices_df.iloc[-1]
    ema_50 = prices_df.ewm(span=50, adjust=False).mean().iloc[-1]
    high_52w = prices_df.rolling(window=252).max().iloc[-1]

    # Create results DataFrame
    results = pd.DataFrame({
        'Momentum Score': momentum_scores,
        'Price': latest_prices,
        '50 EMA': ema_50,
        '52W High': high_52w
    })

    # Rename index to Symbol
    results.index.name = 'Symbol'
    results.reset_index(inplace=True)

    # Apply hard filters: Price > 50 EMA and Price >= 80% of 52-Week High
    mask = (results['Price'] > results['50 EMA']) & (results['Price'] >= 0.8 * results['52W High'])
    results = results[mask].copy()

    # Calculate Current Rank (higher score is better, so rank 1 is highest score)
    results['Current Rank'] = results['Momentum Score'].rank(ascending=False, method='min')

    # Calculate Rank Velocity (Past Rank - Current Rank)
    # To get Past Rank, we need to calculate momentum scores 1 month ago
    # For simplicity in this function without fetching full history, we assume
    # the user will calculate past rank if needed, or we implement a simplified past rank
    # Let's calculate past rank using prices from 1 month ago (approx 21 trading days)

    if len(prices_df) >= 21 + 252:
        # We have enough data to calculate past score
        past_prices_df = prices_df.iloc[:-21]

        # Recalculate everything for past date
        past_daily_returns = past_prices_df.pct_change()
        past_sharpes = {}
        for period_name, days in periods.items():
            if len(past_prices_df) >= days:
                past_period_returns = past_prices_df.pct_change(periods=days)
                past_volatility = past_daily_returns.rolling(window=days).std() * np.sqrt(252)
                past_latest_return = past_period_returns.iloc[-1]
                past_latest_vol = past_volatility.iloc[-1].replace(0, np.nan)
                past_sharpes[period_name] = past_latest_return / past_latest_vol
            else:
                past_sharpes[period_name] = pd.Series(index=past_prices_df.columns, dtype=float)

        past_sharpes_df = pd.DataFrame(past_sharpes).dropna(how='all')
        past_z_scores = (past_sharpes_df - past_sharpes_df.mean()) / past_sharpes_df.std()

        past_weighted_sum = pd.Series(0, index=past_z_scores.index, dtype=float)
        past_total_weights = pd.Series(0, index=past_z_scores.index, dtype=float)
        for period, weight in MOMENTUM_WEIGHTS.items():
            if period in past_z_scores.columns:
                valid_z = past_z_scores[period].notna()
                past_weighted_sum[valid_z] += past_z_scores[period][valid_z] * weight
                past_total_weights[valid_z] += weight

        past_momentum_scores = past_weighted_sum / past_total_weights.replace(0, np.nan)

        # We only need ranks for the symbols that passed the current filters
        past_scores_filtered = past_momentum_scores.reindex(results['Symbol'])
        # Rank among all stocks in the past (or just the filtered ones? Usually rank among all)
        # Let's rank among all available past scores
        past_ranks = past_momentum_scores.rank(ascending=False, method='min')

        # Map past ranks to our filtered results
        results['Past Rank'] = results['Symbol'].map(past_ranks)

        # Calculate Rank Velocity
        # Positive velocity means rank improved (past rank > current rank)
        results['Rank Velocity'] = results['Past Rank'] - results['Current Rank']
    else:
        results['Past Rank'] = np.nan
        results['Rank Velocity'] = np.nan

    # Sort by Momentum Score descending
    results.sort_values(by='Momentum Score', ascending=False, inplace=True)
    results.reset_index(drop=True, inplace=True)

    return results
