import numpy as np
import pandas as pd
from core.config import MOMENTUM_WEIGHTS

def calculate_returns_volatility(prices, periods_days):
    """
    Calculate annualized returns and volatility for given periods.
    prices: DataFrame of daily closing prices.
    periods_days: dictionary of label to number of trading days.
    """
    metrics = {}
    for label, days in periods_days.items():
        if len(prices) > days:
            # Calculate return over the period
            period_return = (prices.iloc[-1] / prices.iloc[-days-1]) - 1

            # Calculate daily returns for the period to find volatility
            period_prices = prices.iloc[-days-1:]
            daily_returns = period_prices.pct_change().dropna()

            # Annualize return and volatility
            ann_return = period_return * (252 / days)
            ann_vol = daily_returns.std() * np.sqrt(252)

            # Calculate Sharpe ratio (assuming 0 risk-free rate for simplicity, typical in momentum)
            sharpe = ann_return / ann_vol

            metrics[f'{label}_return'] = ann_return
            metrics[f'{label}_vol'] = ann_vol
            metrics[f'{label}_sharpe'] = sharpe
        else:
            # Not enough data for this period
            metrics[f'{label}_return'] = pd.Series(np.nan, index=prices.columns)
            metrics[f'{label}_vol'] = pd.Series(np.nan, index=prices.columns)
            metrics[f'{label}_sharpe'] = pd.Series(np.nan, index=prices.columns)

    return pd.DataFrame(metrics)

def calculate_ema(prices, window=50):
    """Calculate Exponential Moving Average."""
    return prices.ewm(span=window, adjust=False).mean()

def calculate_momentum_score(metrics_df):
    """Calculate the final momentum score using weighted Z-scores of Sharpe ratios."""
    score = pd.Series(0.0, index=metrics_df.index)
    total_weight = 0

    for label, weight in MOMENTUM_WEIGHTS.items():
        sharpe_col = f'{label}_sharpe'
        if sharpe_col in metrics_df.columns:
            # Calculate Z-score for the Sharpe ratio
            # Ignore NaNs during standard deviation calculation
            sharpe_values = metrics_df[sharpe_col]
            z_score = (sharpe_values - sharpe_values.mean()) / sharpe_values.std()

            # Fill NaNs with 0 (average Z-score) so missing data doesn't break everything,
            # or could drop. We'll fill with 0 to penalize less.
            z_score = z_score.fillna(0)

            score += z_score * weight
            total_weight += weight

    # Normalize score if weights don't sum to exactly 1
    if total_weight > 0:
        score = score / total_weight

    return score

def calculate_momentum(prices_df):
    """
    Main function to calculate momentum rankings and apply filters.
    """
    if prices_df.empty:
        return pd.DataFrame()

    # Periods in trading days (approximate)
    periods = {
        '1m': 21,
        '3m': 63,
        '6m': 126,
        '9m': 189,
        '12m': 252
    }

    # 1. Calculate metrics (Returns, Volatility, Sharpe)
    metrics_df = calculate_returns_volatility(prices_df, periods)

    # 2. Calculate current indicators for filtering
    current_price = prices_df.iloc[-1]

    # 50 EMA
    ema_50 = calculate_ema(prices_df, 50).iloc[-1]

    # 52-Week High (approx 252 trading days)
    if len(prices_df) >= 252:
        high_52w = prices_df.iloc[-252:].max()
    else:
        high_52w = prices_df.max()

    # Combine into a single DataFrame
    results = pd.DataFrame({
        'Price': current_price,
        '50_EMA': ema_50,
        '52W_High': high_52w
    })

    # Add metrics
    results = pd.concat([results, metrics_df], axis=1)

    # 3. Apply Hard Filters: Price > 50 EMA and Price >= 80% of 52-Week High
    filter_mask = (results['Price'] > results['50_EMA']) & (results['Price'] >= 0.8 * results['52W_High'])
    filtered_results = results[filter_mask].copy()

    if filtered_results.empty:
        return pd.DataFrame()

    # 4. Calculate Momentum Score on filtered universe
    momentum_score = calculate_momentum_score(filtered_results)
    filtered_results['Momentum_Score'] = momentum_score

    # 5. Rank Current
    # Sort descending by Momentum Score
    filtered_results = filtered_results.sort_values(by='Momentum_Score', ascending=False)
    filtered_results['Rank'] = np.arange(1, len(filtered_results) + 1)

    # 6. Calculate Past Rank (1 month ago)
    # We need to simulate the exact same process 21 trading days ago
    if len(prices_df) > 21:
        past_prices_df = prices_df.iloc[:-21]

        # Calculate past metrics
        past_metrics_df = calculate_returns_volatility(past_prices_df, periods)

        past_current_price = past_prices_df.iloc[-1]
        past_ema_50 = calculate_ema(past_prices_df, 50).iloc[-1]

        if len(past_prices_df) >= 252:
            past_high_52w = past_prices_df.iloc[-252:].max()
        else:
            past_high_52w = past_prices_df.max()

        past_results = pd.DataFrame({
            'Price': past_current_price,
            '50_EMA': past_ema_50,
            '52W_High': past_high_52w
        })
        past_results = pd.concat([past_results, past_metrics_df], axis=1)

        # Apply past filters
        past_filter_mask = (past_results['Price'] > past_results['50_EMA']) & (past_results['Price'] >= 0.8 * past_results['52W_High'])
        past_filtered_results = past_results[past_filter_mask].copy()

        if not past_filtered_results.empty:
            past_momentum_score = calculate_momentum_score(past_filtered_results)
            past_filtered_results['Momentum_Score'] = past_momentum_score
            past_filtered_results = past_filtered_results.sort_values(by='Momentum_Score', ascending=False)
            past_filtered_results['Past_Rank'] = np.arange(1, len(past_filtered_results) + 1)

            # Map past rank to current results
            filtered_results['Past_Rank'] = past_filtered_results['Past_Rank']
        else:
            filtered_results['Past_Rank'] = np.nan
    else:
        filtered_results['Past_Rank'] = np.nan

    # Fill missing past ranks with len+1 (meaning it wasn't ranked)
    max_rank = len(filtered_results) + 1
    filtered_results['Past_Rank'] = filtered_results['Past_Rank'].fillna(max_rank)

    # 7. Calculate Rank Velocity
    # Positive means improvement (Past Rank > Current Rank)
    filtered_results['Rank_Velocity'] = filtered_results['Past_Rank'] - filtered_results['Rank']

    # Clean up dataframe structure
    # Reset index and rename index column to 'Symbol'
    filtered_results = filtered_results.reset_index()
    filtered_results = filtered_results.rename(columns={'index': 'Symbol', 'ticker': 'Symbol'})

    # Select columns to display
    display_cols = ['Symbol', 'Momentum_Score', 'Rank', 'Rank_Velocity', 'Price', '50_EMA', '52W_High']
    # Add returns if needed, but keeping it focused on core framework

    return filtered_results[display_cols].copy()
