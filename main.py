import pandas as pd

from analysis.initial_analysis import run_initial_analysis
from analysis.cleaning import run_cleaning

def main():
    df = pd.read_csv('data/ais23_raw.csv')
    df = run_initial_analysis(df)
    df = run_cleaning(df)
    df.to_csv('data/ais23_cleaned.csv', index=False)

if __name__ == "__main__":
    main()