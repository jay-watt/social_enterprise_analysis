import pandas as pd

from initial_analysis import run_initial_analysis
from cleaning import run_cleaning
from utils import load_data

def main():
    df = pd.read_csv('Data/datadotgov_ais23_raw.csv')
    df = run_initial_analysis(df)
    df = run_cleaning(df)
    df.to_csv('datadotgov_ais23_cleaned.csv', index=False)

if __name__ == "__main__":
    main()