import momentum
import pandas as pd
import sys

def main():
    print("Starting Nifty 750 Momentum Analysis...")

    # Use Full Universe by default
    try:
        df = momentum.generate_full_ranking()
    except Exception as e:
        print(f"Error running analysis: {e}")
        sys.exit(1)

    if df.empty:
        print("Analysis returned no data. Check connectivity or inputs.")
        sys.exit(1)

    output_file = "nifty_momentum_ranking.csv"

    # Select columns for final report
    report_cols = [
        'Current Rank', 'Symbol', 'Momentum Score',
        'Price', 'Filters Passed',
        'Above 50 EMA', 'Near 52W High',
        'Rank 1M Ago', 'Rank 2M Ago', 'Rank 3M Ago',
        '50 EMA', '52W High'
    ]

    # Ensure columns exist
    report_cols = [c for c in report_cols if c in df.columns]

    df[report_cols].to_csv(output_file, index=False)

    print(f"Analysis Complete! Saved {len(df)} rows to '{output_file}'.")

if __name__ == "__main__":
    main()
