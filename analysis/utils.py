import os

from tabulate import tabulate

def print_process_heading(process):
    print()
    print('=' * 50)
    print(f'{process.upper()}')
    print('=' * 50)

def print_processing_results(attribute, process, before, after):
    before_str = f'{attribute} before {process}: {before}'
    after_str = f'{attribute} after {process}: {after}'
    print('  - ', before_str)
    print('  - ', after_str)

def save_and_print_table(title, df):
    title_words = title.split()
    while True:
        sheet_name = '_'.join(title_words)

        if len(sheet_name) <= 31:
            break

        title_words = title_words[:-1]

    os.makedirs('../output', exist_ok=True)
    df.to_excel(f'../output/{sheet_name}.xlsx')

    formatted_title = ' '.join(word.capitalize() for word in title.split())
    formatted_table = tabulate(
        df.round(2),
        headers=[df.index.name] + list(df.columns),
        tablefmt='fancy_grid',
        showindex='always',
        maxcolwidths=[50] * (len(df.columns) + 1),
    )
    print(f'\n{formatted_title}')
    print(formatted_table, '\n')