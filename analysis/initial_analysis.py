import pandas as pd

from analysis.utils import (
    print_process_heading,
    save_and_print_table
)

def get_feature_types(df):
    numerical = (df.select_dtypes(include=['number']).columns)
    categorical = (df.select_dtypes(include=['object']).columns)
    return numerical, categorical

def get_stats_by_dtype(df, dtype):
    return df.select_dtypes(include=[dtype]).describe().T

def display_stats(df):
    numerical_stats = get_stats_by_dtype(df, 'number')
    numerical_stats['variance'] = numerical_stats['std'] ** 2
    numerical_stats['range'] = numerical_stats['max'] - numerical_stats['min']
    numerical_stats.drop(columns=['25%', '50%', '75%'], inplace=True)
    numerical_stats.index.name = 'feature'

    save_and_print_table('numerical statistics', numerical_stats)

    categorical_stats = get_stats_by_dtype(df, 'object')
    categorical_stats.index.name = 'feature'

    categorical_stats['values'] = ''
    for col in categorical_stats.index:
        unique_count = df[col].nunique()
        if unique_count <= 10:
            unique_vals = df[col].dropna().unique()
            vals_str = ', '.join(map(str, unique_vals))[:100]
            categorical_stats.at[col, 'values'] = vals_str

    save_and_print_table('categorical statistics', categorical_stats)

def display_summary(df):
    numerical, categorical = get_feature_types(df)
    summary = {
        'categorical features': len(categorical),
        'numerical features': len(numerical),
        'total features': df.shape[1],
        'total instances': df.shape[0],
    }
    summary_df = pd.DataFrame({'count': summary})
    summary_df.index.name = 'attribute'

    save_and_print_table('dataset summary', summary_df)


def run_initial_analysis(df):
    print_process_heading('analysing data')

    display_summary(df)
    display_stats(df)
    
    return df