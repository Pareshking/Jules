# Nifty 750 Momentum Ranking System

This project implements a volatility-adjusted momentum ranking system for the Nifty Total Market (~750 stocks).

## Features

- **Universe**: Nifty Total Market (fetched dynamically).
- **Ranking Logic**:
  - Calculates Sharpe Ratio (Return / Daily Volatility) for 1m, 3m, 6m, 9m, and 12m periods.
  - Normalizes each period's Sharpe Ratio into a Z-Score.
  - Computes a Weighted Average Score:
    - 1m: 10%
    - 3m: 30%
    - 6m: 30%
    - 9m: 20%
    - 12m: 10%
- **Filters**:
  - **Trend**: Price must be above the 50-day EMA.
  - **Highs**: Price must be within 20% of the 52-Week High (Price >= 0.8 * 52W High).
- **Output**:
  - Full ranking table with current and historical ranks (1m, 2m, 3m ago).
  - CSV Export.

## How to Run

### Option 1: Run on GitHub (No Installation Required)

You can run this analysis directly on GitHub and download the results as a CSV file.

1. Go to the **Actions** tab in this repository.
2. Select the **Run Momentum Analysis** workflow from the sidebar.
3. Click the **Run workflow** button.
4. Wait for the job to complete (approx. 3-5 minutes).
5. Click on the completed run, scroll down to the **Artifacts** section, and download `momentum-results`.
6. Extract the zip file to get `nifty_momentum_ranking.csv`.

### Option 2: Run Locally (Interactive Dashboard)

To use the interactive Streamlit dashboard:

1. **Install Python 3.8+**.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the App**:
   ```bash
   streamlit run app.py
   ```
4. The app will open in your browser at `http://localhost:8501`.

### Option 3: Run Locally (Command Line CSV Generator)

To generate the CSV without the web interface:

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Script**:
   ```bash
   python run_batch.py
   ```
3. The output will be saved to `nifty_momentum_ranking.csv`.

## File Structure

- `app.py`: Streamlit web application.
- `momentum.py`: Core logic for data fetching, calculation, and filtering.
- `run_batch.py`: Script for headless execution (used by GitHub Actions).
- `test_momentum.py`: Unit tests.
- `.github/workflows/analysis.yml`: Configuration for GitHub Actions.
