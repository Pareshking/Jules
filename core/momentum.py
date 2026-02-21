import pandas as pd
import numpy as np
from .config import MOMENTUM_WINDOWS, MOMENTUM_WEIGHTS

class MomentumAnalyzer:
    def __init__(self, prices: pd.DataFrame):
        self.prices = prices
        self.momentum_scores = None

    def calculate_momentum_score(self) -> pd.DataFrame:
        """
        Calculates the momentum scores and ranks for the entire history (vectorized).
        Returns a DataFrame of Weighted Momentum Scores (index=Date, columns=Tickers).
        """
        if self.prices.empty:
            return None

        # Daily Returns
        daily_returns = self.prices.pct_change(fill_method=None)

        # Initialize Score DataFrame
        weighted_z_score = pd.DataFrame(0.0, index=self.prices.index, columns=self.prices.columns)

        for w, weight in zip(MOMENTUM_WINDOWS, MOMENTUM_WEIGHTS):
            # Rolling Return
            # (Price_t / Price_{t-w}) - 1
            period_ret = (self.prices / self.prices.shift(w)) - 1

            # Rolling Volatility (Daily Std Dev over window)
            period_vol = daily_returns.rolling(window=w).std()

            # Sharpe Ratio
            # Avoid division by zero
            sharpe = period_ret.div(period_vol.replace(0, np.nan))

            # Z-Score (Cross-sectional per day)
            # Calculate mean and std for each row (date)
            mean_sharpe = sharpe.mean(axis=1)
            std_sharpe = sharpe.std(axis=1)

            # Broadcast subtraction and division
            # (sharpe - mean) / std
            z_score = sharpe.sub(mean_sharpe, axis=0).div(std_sharpe, axis=0)

            # Handle NaNs: If a stock has NaN Sharpe (e.g. newly listed), Z-Score is NaN.
            # We fill NaN with 0 (neutral score) so it doesn't break the sum.
            weighted_z_score = weighted_z_score.add(z_score.fillna(0) * weight, fill_value=0)

        self.momentum_scores = weighted_z_score
        return weighted_z_score

    def get_rankings(self) -> pd.DataFrame:
        """
        Generates the final ranking DataFrame with filters.
        """
        if self.momentum_scores is None:
            self.calculate_momentum_score()

        if self.momentum_scores is None or self.prices.empty:
            return pd.DataFrame()

        # Current Data (Last available row)
        current_prices = self.prices.iloc[-1]

        # 50 EMA
        ema_50 = self.prices.ewm(span=50, adjust=False).mean().iloc[-1]

        # 52 Week High (max of last 252 days)
        high_52 = self.prices.rolling(window=252).max().iloc[-1]

        # Indices for T, T-1m, T-2m, T-3m
        # We use negative indexing based on trading days approx (21 days/month)
        max_idx = len(self.momentum_scores)

        indices = {
            'Current': -1,
            '1M Ago': -22,
            '2M Ago': -43,
            '3M Ago': -64
        }

        # Helper to get rank series for a specific time offset
        def get_rank_series(offset_idx):
            # Check bounds (if history is shorter than offset)
            if abs(offset_idx) > max_idx:
                return pd.Series(np.nan, index=self.momentum_scores.columns)

            # Get scores at that index
            scores = self.momentum_scores.iloc[offset_idx]

            # Rank descending (Higher score = Rank 1)
            return scores.rank(ascending=False)

        # Base DataFrame
        df = pd.DataFrame(index=self.prices.columns)

        # Add Score
        try:
            df['Momentum Score'] = self.momentum_scores.iloc[indices['Current']]
        except IndexError:
            df['Momentum Score'] = np.nan

        df['Price'] = current_prices
        df['50 EMA'] = ema_50
        df['52W High'] = high_52

        # Add Ranks
        df['Current Rank'] = get_rank_series(indices['Current'])
        df['Rank 1M Ago'] = get_rank_series(indices['1M Ago'])
        df['Rank 2M Ago'] = get_rank_series(indices['2M Ago'])
        df['Rank 3M Ago'] = get_rank_series(indices['3M Ago'])

        # Calculate Rank Velocity (Positive is good: Rank 10 -> Rank 5 = 10 - 5 = 5)
        df['Rank Velocity'] = df['Rank 1M Ago'] - df['Current Rank']

        # Apply Filters
        df['Above 50 EMA'] = df['Price'] > df['50 EMA']
        df['Near 52W High'] = df['Price'] >= (0.8 * df['52W High'])
        df['Filters Passed'] = df['Above 50 EMA'] & df['Near 52W High']

        # Sort
        df = df.sort_values('Current Rank')

        # Reset index to make Symbol a column
        df = df.reset_index().rename(columns={'index': 'Symbol', 'Ticker': 'Symbol'})

        return df
