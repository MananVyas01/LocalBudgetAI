import pandas as pd
import matplotlib.pyplot as plt
from typing import Union

def analyze_expenses_by_category(df: pd.DataFrame) -> pd.Series:
    """
    Calculate total amount spent per category.
    Returns a Series indexed by category with summed amounts.
    Ignores non-numeric or missing 'Amount' values.
    """
    if 'Category' not in df.columns or 'Amount' not in df.columns:
        raise ValueError("DataFrame must contain 'Category' and 'Amount' columns.")
    # Ensure 'Amount' is numeric
    df = df.copy()
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    # Only consider negative amounts as expenses
    expenses = df[df['Amount'] < 0]
    return expenses.groupby('Category')['Amount'].sum().abs().sort_values(ascending=False)
