"""
Interactive Plotly visualization module for LocalBudgetAI.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import logging
from typing import List
from analyzer import analyze_expenses_by_category, analyze_monthly_trend

logger = logging.getLogger(__name__)

def create_interactive_bar_chart(expense_summary: pd.Series, 
                                title: str = "Total Spending by Category") -> go.Figure:
    """Create an interactive bar chart using Plotly."""
    if expense_summary.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    fig = px.bar(
        x=expense_summary.index,
        y=expense_summary.values,
        title=title,
        labels={'x': 'Category', 'y': 'Amount ($)'},
        color=expense_summary.values,
        color_continuous_scale='viridis',
        text=expense_summary.values
    )
    
    fig.update_traces(
        texttemplate='$%{text:.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Amount: $%{y:.2f}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        font=dict(size=12),
        height=500,
        margin=dict(t=80, b=100)
    )
    
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    logger.info(f"Created interactive bar chart for {len(expense_summary)} categories")
    return fig

def create_interactive_pie_chart(expense_summary: pd.Series,
                                title: str = "Expense Distribution by Category") -> go.Figure:
    """Create an interactive pie chart using Plotly."""
    if expense_summary.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    fig = px.pie(
        values=expense_summary.values,
        names=expense_summary.index,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>',
        pull=[0.1 if i == 0 else 0 for i in range(len(expense_summary))]
    )
    
    fig.update_layout(
        font=dict(size=12),
        height=500,
        margin=dict(t=80, b=50, l=50, r=150)
    )
    
    logger.info(f"Created interactive pie chart for {len(expense_summary)} categories")
    return fig

def create_interactive_line_chart(monthly_data: pd.Series,
                                title: str = "Monthly Expense Trend") -> go.Figure:
    """Create an interactive line chart using Plotly."""
    if monthly_data.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_data.index,
        y=monthly_data.values,
        mode='lines+markers',
        name='Monthly Expenses',
        line=dict(color='#2E86AB', width=3),
        marker=dict(size=8, color='#A23B72', line=dict(width=2, color='white')),
        hovertemplate='<b>%{x}</b><br>Amount: $%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Month',
        yaxis_title='Amount ($)',
        font=dict(size=12),
        height=500,
        margin=dict(t=80, b=80)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', tickformat='$,.0f')
    
    logger.info(f"Created interactive line chart for {len(monthly_data)} months")
    return fig

def create_dashboard_overview(df: pd.DataFrame) -> go.Figure:
    """Create a comprehensive dashboard overview."""
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for dashboard",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    try:
        category_summary = analyze_expenses_by_category(df)
        monthly_trend = analyze_monthly_trend(df)
    except Exception as e:
        logger.error(f"Error analyzing data for dashboard: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error analyzing data: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=14)
        )
        return fig
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Category Breakdown', 'Distribution', 'Monthly Trend', 'Summary'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"colspan": 2, "type": "scatter"}, None]],
        horizontal_spacing=0.1,
        vertical_spacing=0.15
    )
    
    if not category_summary.empty:
        fig.add_trace(
            go.Bar(
                x=category_summary.index,
                y=category_summary.values,
                name="Categories",
                hovertemplate='<b>%{x}</b><br>Amount: $%{y:.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Pie(
                labels=category_summary.index,
                values=category_summary.values,
                name="Distribution",
                hovertemplate='<b>%{label}</b><br>Amount: $%{value:.2f}<br>Percentage: %{percent}<extra></extra>'
            ),
            row=1, col=2
        )
    
    if not monthly_trend.empty:
        fig.add_trace(
            go.Scatter(
                x=monthly_trend.index,
                y=monthly_trend.values,
                mode='lines+markers',
                name='Monthly Trend',
                line=dict(color='#2E86AB', width=3),
                marker=dict(size=6),
                hovertemplate='<b>%{x}</b><br>Amount: $%{y:.2f}<extra></extra>'
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=800,
        showlegend=False,
        title_text="Financial Dashboard Overview",
        title_x=0.5,
        font=dict(size=10)
    )
    
    fig.update_xaxes(tickangle=-45, row=1, col=1)
    
    logger.info("Created comprehensive dashboard overview")
    return fig

def create_category_comparison(df: pd.DataFrame, categories: List[str]) -> go.Figure:
    """Create a comparison chart for selected categories over time."""
    if df.empty or not categories:
        fig = go.Figure()
        fig.add_annotation(
            text="No data or categories selected",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        return fig
    
    fig = go.Figure()
    
    df_copy = df.copy()
    df_copy['Amount'] = pd.to_numeric(df_copy['Amount'], errors='coerce')
    df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')
    df_copy = df_copy.dropna(subset=['Amount', 'Date'])
    
    df_copy = df_copy[(df_copy['Amount'] < 0) & (df_copy['Category'].isin(categories))]
    df_copy['Amount'] = df_copy['Amount'].abs()
    
    df_copy['Month'] = df_copy['Date'].dt.to_period('M').astype(str)
    monthly_by_category = df_copy.groupby(['Month', 'Category'])['Amount'].sum().reset_index()
    
    colors = px.colors.qualitative.Set1
    for i, category in enumerate(categories):
        cat_data = monthly_by_category[monthly_by_category['Category'] == category]
        
        if not cat_data.empty:
            fig.add_trace(go.Scatter(
                x=cat_data['Month'],
                y=cat_data['Amount'],
                mode='lines+markers',
                name=category,
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6),
                hovertemplate=f'<b>{category}</b><br>Month: %{{x}}<br>Amount: $%{{y:.2f}}<extra></extra>'
            ))
    
    fig.update_layout(
        title="Category Comparison Over Time",
        xaxis_title="Month",
        yaxis_title="Amount ($)",
        height=500,
        showlegend=True
    )
    
    fig.update_yaxes(tickformat='$,.0f')
    
    logger.info(f"Created category comparison chart for {len(categories)} categories")
    return fig
