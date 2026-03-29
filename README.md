# Social Enterprise Analysis

## Quickstart
```bash
python main.py
```

This runs the full analysis pipeline and generates:
- Cleaned dataset
- Analysis table results (.xlsx)
- Visualisations (.png)


## SE Definition
Charities deriving >50% of revenue from earned income (goods & services).


## Dataset
- Source: ACNC Register (AIS 2023)
- Records: 53,285 charities
- Columns: 61 (after cleaning)


## Data Cleaning
- Removed columns >80% missing (4 columns)
- Imputed remaining missing values with mode
- Converted dates to numerical format
- Encoded categorical variables


## Analysis Approach
- Feature importance (Random Forest regression)
- Revenue composition analysis
- Staffing patterns by size/type
- Financial comparison (SEs vs traditional)