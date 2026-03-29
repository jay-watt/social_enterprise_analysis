import numpy as np
import pandas as pd

from analysis.utils import (
    print_process_heading,
    print_processing_results,
    save_and_print_table
)

def normalise_string_values(df):
    print('\nNormalising string values')
    
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    
    for col in object_cols:
        unique_before = df[col].nunique()
        
        if unique_before < 10:
            df[col] = df[col].str.strip().str.capitalize()
            unique_after = df[col].nunique()
            if unique_before != unique_after:
                print_processing_results(f'{col} unique values', 'uppercase conversion', unique_before, unique_after)

    return df

def drop_high_missing_columns(df, threshold):
    before_cols = len(df.columns)
    missing_pct = (df.isnull().sum() / len(df)) * 100
    cols_to_drop = missing_pct[missing_pct > threshold].index.tolist()
    
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    
    return df

def drop_redundant_columns(df, corr_threshold):
    missing_corr = df.isnull().corr()
    corr_unstacked = missing_corr.unstack()
    high_corr_pairs = corr_unstacked[(1 > corr_unstacked) & (corr_unstacked > corr_threshold)].sort_values(ascending=False)
    
    corr_df = high_corr_pairs.to_frame(name='Correlation')

    save_and_print_table('highly correlated missing values', corr_df)

    important_cols = {'charity size', 'registration status', 'total gross income', 'total revenue'}
    
    cols_to_drop = set()
    for (col_a, col_b), _ in high_corr_pairs.items():
        if (col_a == col_b):
            continue

        # If either is important, drop the OTHER one
        if col_a.lower() in important_cols:
            cols_to_drop.add(col_b)
            continue
        if col_b.lower() in important_cols:
            cols_to_drop.add(col_a)
            continue

        missing_a = (df[col_a].isnull().sum() / len(df)) * 100
        missing_b = (df[col_b].isnull().sum() / len(df)) * 100

        # Drop the one with more missing
        if missing_a > missing_b:
            cols_to_drop.add(col_a)
        elif missing_b > missing_a:
            cols_to_drop.add(col_b)
        else:
            # If equal, drop text/descriptive, keep numeric/actionable
            if 'description' in col_a.lower() or 'consolidated' in col_a.lower():
                cols_to_drop.add(col_a)
            else:
                cols_to_drop.add(col_b)
    
    df = df.drop(columns=list(cols_to_drop))
    print(f'Dropped {len(cols_to_drop)} redundant columns: {", ".join(cols_to_drop)}')
    
    return df

def impute_remaining_missing_values(df):
    cols_with_missing = df.columns[df.isnull().any()].tolist()
    
    for col in cols_with_missing:
        mode_val = df[col].mode()
        fill_val = mode_val[0]
        df[col] = df[col].fillna(fill_val)
    
    return df

def handle_missing_values(df, corr_threshold=0.95, missing_threshold=70):
    print(f'\nDropping columns with high ratios of missing values (>{missing_threshold}%)')
    before = df.isnull().sum().sum()
    df = drop_high_missing_columns(df, missing_threshold)
    after = df.isnull().sum().sum()
    print_processing_results('missing values', f'dropping columns', before, after)

    print(f'\nDropping columns with correlation > {corr_threshold}')
    before = df.isnull().sum().sum()
    df = drop_redundant_columns(df, corr_threshold)
    after = df.isnull().sum().sum()
    print_processing_results('missing values', f'dropping columns', before, after)
    
    print(f'\nImputing remaining missing values with mode')
    before = df.isnull().sum().sum()
    df = impute_remaining_missing_values(df)
    after = df.isnull().sum().sum()
    print_processing_results('missing values', 'imputing with mode', before, after)

    return df

def convert_boolean_categorical_columns(df):
    print('\nConverting boolean categorical columns to numerical')
    
    object_cols = df.select_dtypes(include=['object']).columns.tolist()

    before = len(object_cols)
    
    for col in object_cols:
        unique_vals = set(df[col].unique())
        if unique_vals <= {'YES', 'NO', 'Y', 'N', 'Cash', 'Accrual'}:
            df[col] = df[col].replace({'YES': 1, 'Y': 1, 'NO': 0, 'N': 0, 'Cash': 1, 'Accrual': 0})
            df[col] = df[col].astype('int64')
    
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    after = len(object_cols)

    print_processing_results('categorical columns', 'conversion', before, after)
    
    return df

def convert_date_columns(df):
    print('\nConverting date categorical columns to datetime')
    
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    before = len(object_cols)
    
    for col in object_cols:
        first_val = df[col].iloc[0]
        try:
            format = '%d/%m/%Y'
            result = pd.to_datetime(first_val, format=format, errors='raise', dayfirst=True)
            df[col] = pd.to_datetime(df[col], errors='coerce', format=format, dayfirst=True)
            df[col] = df[col].astype('int64')
        except Exception:
            continue
    
    object_cols_after = df.select_dtypes(include=['object']).columns.tolist()
    after = len(object_cols_after)

    print_processing_results('object columns', 'date conversion', before, after)
    
    return df

def drop_high_unique_categorical_columns(df, threshold = 10000):
    print(f'\nDropping categorical columns with very high cardinality (>{threshold} unique values)')
    
    object_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    before = len(object_cols)
    
    for col in object_cols:
        unique_vals = len(df[col].unique())
        if unique_vals > threshold:
            df.drop(columns=[col], inplace=True)

    object_cols_after = df.select_dtypes(include=['object']).columns.tolist()
    after = len(object_cols_after)

    print_processing_results('categorical columns', 'dropping redundant', before, after)
    
    return df

def generate_class_column(df):
    print('\nGenerating class column (is_se)')
    services_pct = np.where(
        df['total revenue'] > 0,
        (df['revenue from goods and services'] / df['total revenue'] * 100),
        0
    )
    df['is_se'] = (services_pct > 50).astype('int64')
    print(df['is_se'].value_counts())
    return df

def map_ordinal_size(df):
    print('\nMapping ordinal charity size column')
    size_mapping = {
        'Small': 1,
        'Medium': 2,
        'Large': 3
    }
    df['charity size'] = df['charity size'].map(size_mapping)
    df['charity size'] = df['charity size'].astype('int64')
    return df

def encode(df):
    print('\nEncoding registration status column')
    df = pd.get_dummies(df, columns=['registration status'], drop_first=True)
    return df

def run_cleaning(df):
    print_process_heading('cleaning data')
    df = normalise_string_values(df)
    df = handle_missing_values(df)
    df = convert_boolean_categorical_columns(df)
    df = convert_date_columns(df)
    df = drop_high_unique_categorical_columns(df, threshold=10000)
    df = generate_class_column(df)
    df = map_ordinal_size(df)
    df = encode(df)

    return df