"""
Professional expense analysis module for LocalBudgetAI.

This module provides comprehensive data analysis functions for financial data,
including category-wise expense analysis, visualization, and trend analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging
from typing import Union, Optional, Tuple, List
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseAnalyzer:
    """
    Professional expense analyzer class with comprehensive error handling.
    """
    
    def __init__(self, data_validation: bool = True):
        """
        Initialize the ExpenseAnalyzer.
        
        Args:
            data_validation (bool): Whether to perform strict data validation
        """
        self.data_validation = data_validation
        self.required_columns = {'Category', 'Amount', 'Date'}
    
    def validate_dataframe(self, df: pd.DataFrame, required_cols: List[str]) -> bool:
        """
        Validate DataFrame structure and data quality.
        
        Args:
            df (pd.DataFrame): Input DataFrame to validate
            required_cols (List[str]): List of required column names
            
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails and data_validation is True
        """
        if df.empty:
            error_msg = "DataFrame is empty"
            if self.data_validation:
                raise ValueError(error_msg)
            logger.warning(error_msg)
            return False
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            error_msg = f"Missing required columns: {missing_cols}"
            if self.data_validation:
                raise ValueError(error_msg)
            logger.warning(error_msg)
            return False
        
        return True

def analyze_expenses_by_category(df: pd.DataFrame, 
                               include_income: bool = False,
                               min_amount_threshold: float = 0.01) -> pd.Series:
    """
    Analyze expenses by category with professional-grade error handling.
    
    Args:
        df (pd.DataFrame): Input DataFrame with 'Category' and 'Amount' columns
        include_income (bool): Whether to include positive amounts (income)
        min_amount_threshold (float): Minimum amount threshold to include
        
    Returns:
        pd.Series: Series indexed by category with total amounts
        
    Raises:
        ValueError: If required columns are missing
        TypeError: If input is not a pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    analyzer = ExpenseAnalyzer()
    analyzer.validate_dataframe(df, ['Category', 'Amount'])
    
    # Create a copy to avoid modifying original data
    df_clean = df.copy()
    
    # Convert Amount to numeric, handling errors gracefully
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')
    
    # Remove rows with invalid amounts
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['Amount'])
    dropped_count = initial_count - len(df_clean)
    
    if dropped_count > 0:
        logger.warning(f"Dropped {dropped_count} rows with invalid amounts")
    
    # Filter by amount type (expenses vs income)
    if not include_income:
        df_clean = df_clean[df_clean['Amount'] < 0]
        df_clean['Amount'] = df_clean['Amount'].abs()  # Convert to positive for readability
    
    # Apply minimum threshold
    df_clean = df_clean[df_clean['Amount'] >= min_amount_threshold]
    
    if df_clean.empty:
        logger.warning("No valid expense data found after filtering")
        return pd.Series(dtype=float)
    
    # Group by category and sum amounts
    result = df_clean.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    
    logger.info(f"Analyzed {len(result)} expense categories totaling ${result.sum():.2f}")
    return result

def plot_expense_bar_chart(expense_summary: pd.Series, 
                         ax: Optional[plt.Axes] = None,
                         title: str = "Total Spending by Category",
                         color_palette: str = 'viridis',
                         show_values: bool = True) -> plt.Axes:
    """
    Create a professional bar chart of expenses by category.
    
    Args:
        expense_summary (pd.Series): Series with categories as index and amounts as values
        ax (Optional[plt.Axes]): Matplotlib axes object. If None, creates new figure
        title (str): Chart title
        color_palette (str): Color palette for the bars
        show_values (bool): Whether to show values on top of bars
        
    Returns:
        plt.Axes: The matplotlib axes object
        
    Raises:
        ValueError: If expense_summary is empty
    """
    if expense_summary.empty:
        raise ValueError("Cannot plot empty expense summary")
    
    # Create figure if axes not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create the bar chart with professional styling
    colors = plt.cm.get_cmap(color_palette)(np.linspace(0, 1, len(expense_summary)))
    bars = expense_summary.plot(kind='bar', ax=ax, color=colors, 
                               edgecolor='white', linewidth=0.8, alpha=0.8)
    
    # Professional styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.tick_params(axis='y', labelsize=10)
    
    # Add value labels on bars if requested
    if show_values:
        for i, (category, value) in enumerate(expense_summary.items()):
            ax.text(i, value + max(expense_summary) * 0.01, f'${value:.0f}', 
                   ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    # Add grid for better readability
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Format y-axis to show currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    logger.info(f"Generated bar chart for {len(expense_summary)} categories")
    return ax

def plot_expense_pie_chart(expense_summary: pd.Series, 
                         ax: Optional[plt.Axes] = None,
                         title: str = "Expense Distribution by Category",
                         min_percentage: float = 2.0,
                         explode_max: bool = True) -> plt.Axes:
    """
    Create a professional pie chart of expense distribution.
    
    Args:
        expense_summary (pd.Series): Series with categories as index and amounts as values
        ax (Optional[plt.Axes]): Matplotlib axes object. If None, creates new figure
        title (str): Chart title
        min_percentage (float): Minimum percentage to show separately (others grouped)
        explode_max (bool): Whether to explode the largest slice
        
    Returns:
        plt.Axes: The matplotlib axes object
        
    Raises:
        ValueError: If expense_summary is empty
    """
    if expense_summary.empty:
        raise ValueError("Cannot plot empty expense summary")
    
    # Create figure if axes not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    
    # Group small categories
    total = expense_summary.sum()
    percentages = (expense_summary / total) * 100
    
    # Separate large and small categories
    large_categories = expense_summary[percentages >= min_percentage]
    small_categories = expense_summary[percentages < min_percentage]
    
    # Combine data for plotting
    plot_data = large_categories.copy()
    if not small_categories.empty:
        plot_data['Others'] = small_categories.sum()
    
    # Set up explode effect for largest category
    explode = None
    if explode_max and len(plot_data) > 1:
        explode = [0.1 if i == 0 else 0 for i in range(len(plot_data))]
    
    # Create professional color palette
    colors = plt.cm.Set3(np.linspace(0, 1, len(plot_data)))
    
    # Create the pie chart
    wedges, texts, autotexts = ax.pie(plot_data.values, 
                                     labels=plot_data.index,
                                     autopct='%1.1f%%',
                                     startangle=90,
                                     explode=explode,
                                     colors=colors,
                                     wedgeprops={'edgecolor': 'white', 'linewidth': 2},
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})
    
    # Style the percentage labels
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Add legend with amounts
    legend_labels = [f'{cat}: ${amt:.0f}' for cat, amt in plot_data.items()]
    ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    
    plt.tight_layout()
    logger.info(f"Generated pie chart for {len(plot_data)} categories")
    return ax

def analyze_monthly_trend(df: pd.DataFrame, 
                        include_income: bool = False,
                        date_format: Optional[str] = None) -> pd.Series:
    """
    Analyze monthly expense trends with comprehensive error handling.
    
    Args:
        df (pd.DataFrame): Input DataFrame with 'Date' and 'Amount' columns
        include_income (bool): Whether to include positive amounts (income)
        date_format (Optional[str]): Specific date format to try first
        
    Returns:
        pd.Series: Series indexed by month (YYYY-MM) with total amounts
        
    Raises:
        ValueError: If required columns are missing
        TypeError: If input is not a pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")
    
    analyzer = ExpenseAnalyzer()
    analyzer.validate_dataframe(df, ['Date', 'Amount'])
    
    # Create a copy to avoid modifying original data
    df_clean = df.copy()
    
    # Convert Amount to numeric
    df_clean['Amount'] = pd.to_numeric(df_clean['Amount'], errors='coerce')
    
    # Remove rows with invalid amounts
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['Amount'])
    dropped_count = initial_count - len(df_clean)
    
    if dropped_count > 0:
        logger.warning(f"Dropped {dropped_count} rows with invalid amounts")
    
    # Parse dates with multiple strategies
    df_clean['Date_Parsed'] = None
    
    # Strategy 1: Try specific format if provided
    if date_format:
        try:
            df_clean['Date_Parsed'] = pd.to_datetime(df_clean['Date'], format=date_format)
            logger.info(f"Successfully parsed dates using format: {date_format}")
        except ValueError:
            logger.warning(f"Failed to parse dates with format: {date_format}")
    
    # Strategy 2: Try pandas automatic parsing
    if df_clean['Date_Parsed'].isna().all():
        df_clean['Date_Parsed'] = pd.to_datetime(df_clean['Date'], errors='coerce')
    
    # Strategy 3: Try common date formats
    if df_clean['Date_Parsed'].isna().any():
        common_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y']
        for fmt in common_formats:
            mask = df_clean['Date_Parsed'].isna()
            if mask.any():
                try:
                    df_clean.loc[mask, 'Date_Parsed'] = pd.to_datetime(
                        df_clean.loc[mask, 'Date'], format=fmt, errors='coerce'
                    )
                except ValueError:
                    continue
    
    # Remove rows with unparseable dates
    date_initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['Date_Parsed'])
    date_dropped_count = date_initial_count - len(df_clean)
    
    if date_dropped_count > 0:
        logger.warning(f"Dropped {date_dropped_count} rows with unparseable dates")
    
    if df_clean.empty:
        logger.warning("No valid data found after date parsing")
        return pd.Series(dtype=float)
    
    # Filter by amount type
    if not include_income:
        df_clean = df_clean[df_clean['Amount'] < 0]
        df_clean['Amount'] = df_clean['Amount'].abs()
    
    if df_clean.empty:
        logger.warning("No expense data found after filtering")
        return pd.Series(dtype=float)
    
    # Extract month-year and group
    df_clean['Month'] = df_clean['Date_Parsed'].dt.to_period('M')
    monthly_totals = df_clean.groupby('Month')['Amount'].sum().sort_index()
    
    # Convert period index to string for better compatibility
    monthly_totals.index = monthly_totals.index.astype(str)
    
    logger.info(f"Analyzed {len(monthly_totals)} months of data, "
               f"total amount: ${monthly_totals.sum():.2f}")
    
    return monthly_totals

def plot_monthly_trend(monthly_data: pd.Series, 
                      ax: Optional[plt.Axes] = None,
                      title: str = "Monthly Expense Trend",
                      show_trend_line: bool = True) -> plt.Axes:
    """
    Create a professional line chart of monthly expense trends.
    
    Args:
        monthly_data (pd.Series): Series with months as index and amounts as values
        ax (Optional[plt.Axes]): Matplotlib axes object. If None, creates new figure
        title (str): Chart title
        show_trend_line (bool): Whether to show trend line
        
    Returns:
        plt.Axes: The matplotlib axes object
        
    Raises:
        ValueError: If monthly_data is empty
    """
    if monthly_data.empty:
        raise ValueError("Cannot plot empty monthly data")
    
    # Create figure if axes not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the main line
    ax.plot(range(len(monthly_data)), monthly_data.values, 
           marker='o', linewidth=2.5, markersize=8, 
           color='#2E86AB', markerfacecolor='#A23B72', 
           markeredgecolor='white', markeredgewidth=2)
    
    # Add trend line if requested
    if show_trend_line and len(monthly_data) > 1:
        x_vals = np.arange(len(monthly_data))
        z = np.polyfit(x_vals, monthly_data.values, 1)
        p = np.poly1d(z)
        ax.plot(x_vals, p(x_vals), "--", alpha=0.7, color='red', linewidth=2,
               label=f'Trend (slope: ${z[0]:.0f}/month)')
        ax.legend()
    
    # Professional styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
    
    # Set x-axis labels
    ax.set_xticks(range(len(monthly_data)))
    ax.set_xticklabels(monthly_data.index, rotation=45, ha='right')
    
    # Format y-axis to show currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Add value annotations
    for i, (month, value) in enumerate(monthly_data.items()):
        ax.annotate(f'${value:.0f}', (i, value), 
                   textcoords="offset points", xytext=(0,10), 
                   ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    logger.info(f"Generated monthly trend chart for {len(monthly_data)} months")
    return ax

def generate_expense_summary_report(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive expense summary report.
    
    Args:
        df (pd.DataFrame): Input DataFrame with financial data
        
    Returns:
        dict: Comprehensive summary statistics
    """
    try:
        # Basic statistics
        total_records = len(df)
        
        # Category analysis
        category_summary = analyze_expenses_by_category(df)
        total_expenses = category_summary.sum()
        top_category = category_summary.index[0] if not category_summary.empty else "N/A"
        
        # Monthly analysis
        monthly_summary = analyze_monthly_trend(df)
        months_covered = len(monthly_summary)
        avg_monthly_expense = monthly_summary.mean() if not monthly_summary.empty else 0
        
        # Income analysis
        df_numeric = df.copy()
        df_numeric['Amount'] = pd.to_numeric(df_numeric['Amount'], errors='coerce')
        total_income = df_numeric[df_numeric['Amount'] > 0]['Amount'].sum()
        net_savings = total_income - total_expenses
        
        report = {
            "total_records": total_records,
            "total_expenses": total_expenses,
            "total_income": total_income,
            "net_savings": net_savings,
            "top_expense_category": top_category,
            "categories_count": len(category_summary),
            "months_covered": months_covered,
            "avg_monthly_expense": avg_monthly_expense,
            "expense_by_category": category_summary.to_dict(),
            "monthly_expenses": monthly_summary.to_dict()
        }
        
        logger.info("Generated comprehensive expense summary report")
        return report
        
    except Exception as e:
        logger.error(f"Error generating summary report: {e}")
        return {"error": str(e)}
