import unittest
import pandas as pd
import numpy as np
import momentum
from unittest.mock import patch

class TestMomentum(unittest.TestCase):

    def setUp(self):
        # Create dummy price data for 3 stocks over 300 days
        dates = pd.date_range(start='2022-01-01', periods=300, freq='B')
        self.tickers_list = ['STOCKA.NS', 'STOCKB.NS', 'STOCKC.NS']
        self.tickers_dict = {
            'STOCKA.NS': 'Stock A Ltd',
            'STOCKB.NS': 'Stock B Corp',
            'STOCKC.NS': 'Stock C Inc'
        }

        # Stock A: Uptrend
        price_a = np.linspace(100, 200, 300) + np.random.normal(0, 2, 300)
        # Stock B: Downtrend
        price_b = np.linspace(200, 100, 300) + np.random.normal(0, 2, 300)
        # Stock C: Flat
        price_c = np.linspace(150, 150, 300) + np.random.normal(0, 2, 300)

        data = pd.DataFrame({
            'STOCKA.NS': price_a,
            'STOCKB.NS': price_b,
            'STOCKC.NS': price_c
        }, index=dates)

        self.prices = data

    def test_calculate_momentum_metrics(self):
        scores = momentum.calculate_momentum_metrics(self.prices)
        self.assertIsNotNone(scores)
        self.assertEqual(scores.shape, self.prices.shape)

        # Last score
        last_scores = scores.iloc[-1]

        # Stock A (Uptrend) should have higher score than Stock B (Downtrend)
        self.assertGreater(last_scores['STOCKA.NS'], last_scores['STOCKB.NS'])

    def test_filters(self):
        # Create a scenario for filters
        # Stock A: Price > 50 EMA (200 > ~190) -> True
        # Stock B: Price < 50 EMA (100 < ~110) -> False

        # 50 EMA
        ema = self.prices.ewm(span=50, adjust=False).mean().iloc[-1]
        current = self.prices.iloc[-1]

        self.assertTrue(current['STOCKA.NS'] > ema['STOCKA.NS'])
        self.assertTrue(current['STOCKB.NS'] < ema['STOCKB.NS'])

    @patch('momentum.get_nifty_constituents')
    @patch('momentum.fetch_data')
    def test_generate_full_ranking(self, mock_fetch, mock_tickers):
        mock_tickers.return_value = self.tickers_dict
        mock_fetch.return_value = self.prices

        df = momentum.generate_full_ranking()

        self.assertFalse(df.empty)
        self.assertIn('Momentum Score', df.columns)
        self.assertIn('Current Rank', df.columns)
        self.assertIn('Filters Passed', df.columns)
        self.assertIn('Company Name', df.columns)

        # Check mapping
        self.assertEqual(df[df['Symbol'] == 'STOCKA.NS']['Company Name'].values[0], 'Stock A Ltd')

        # Check if Stock A is ranked higher (lower rank number) than Stock B
        # Extract rows
        row_a = df[df['Symbol'] == 'STOCKA.NS'].iloc[0]
        row_b = df[df['Symbol'] == 'STOCKB.NS'].iloc[0]

        self.assertLess(row_a['Current Rank'], row_b['Current Rank'])

        # Check Filters
        # Stock A should pass filters (assuming it's near high, which it is, 200 is max)
        self.assertTrue(row_a['Filters Passed'])

        # Stock B is at low, so it should fail 52W high and 50 EMA
        self.assertFalse(row_b['Filters Passed'])

    @patch('requests.get')
    def test_get_nifty_constituents_dummy_filter(self, mock_get):
        # Mock CSV content
        csv_content = """Company Name,Industry,Symbol,Series,ISIN Code
        Valid Co,Ind,VALID,EQ,INE123
        Dummy Co,Ind,DUMMY001,EQ,INE456
        Another Co,Ind,DUMMYTEST,EQ,INE789
        """

        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.content = csv_content.encode('utf-8')
        mock_get.return_value = mock_response

        constituents = momentum.get_nifty_constituents()

        self.assertIn('VALID.NS', constituents)
        self.assertNotIn('DUMMY001.NS', constituents)
        self.assertNotIn('DUMMYTEST.NS', constituents)

if __name__ == '__main__':
    unittest.main()
