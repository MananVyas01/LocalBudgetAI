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

def plot_expense_bar_chart(expense_summary: pd.Series, ax=None):
    """
    Plot a bar chart of total spending by category.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))
    expense_summary.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
    ax.set_title('Total Spending by Category')
    ax.set_xlabel('Category')
    ax.set_ylabel('Total Spent')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
    plt.tight_layout()
    return ax

def plot_expense_pie_chart(expense_summary: pd.Series, ax=None):
    """
    Plot a pie chart of percentage distribution of expenses by category.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    expense_summary.plot(
        kind='pie',
        ax=ax,
        autopct='%1.1f%%',
        startangle=90,
        counterclock=False,
        legend=False,
        wedgeprops={'edgecolor': 'white'}
    )
    ax.set_ylabel('')
    ax.set_title('Expense Distribution by Category')
    plt.tight_layout()
    return ax
