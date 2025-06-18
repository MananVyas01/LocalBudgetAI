"""
Advanced LLM Helper module for LocalBudgetAI with Enhanced NLP and Financial Intelligence.

This module provides sophisticated AI assistant functionality with:
- Advanced financial analysis and insights
- Natural Language Processing for expense categorization
- Predictive budgeting and trend analysis
- Personalized financial recommendations
- Advanced context understanding
"""

import logging
import json
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any, List
import pandas as pd
import numpy as np

# Configure logging
logger = logging.getLogger(__name__)


class AdvancedFinancialAI:
    """Advanced Financial AI Assistant with NLP capabilities"""

    def __init__(self):
        self.financial_keywords = {
            "spending_patterns": ["pattern", "trend", "habit", "behavior", "recurring"],
            "budgeting": ["budget", "allocate", "limit", "save", "target", "goal"],
            "investment": ["invest", "portfolio", "return", "profit", "growth"],
            "debt": ["debt", "loan", "credit", "payment", "interest"],
            "savings": ["save", "emergency", "fund", "reserve", "accumulate"],
            "cash_flow": ["income", "expense", "flow", "balance", "net"],
            "forecasting": ["predict", "forecast", "future", "projection", "estimate"],
        }

        self.expense_categories = {
            "essential": [
                "groceries",
                "utilities",
                "rent",
                "mortgage",
                "insurance",
                "healthcare",
            ],
            "lifestyle": ["dining", "entertainment", "shopping", "travel", "hobbies"],
            "transport": ["gas", "fuel", "transportation", "car", "uber", "taxi"],
            "investment": ["investment", "stocks", "bonds", "retirement", "savings"],
            "debt": ["loan", "credit card", "debt payment", "interest"],
        }

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze the user's query to understand intent and context"""
        query_lower = query.lower()

        intent_analysis = {
            "primary_intent": "general",
            "financial_domain": [],
            "time_reference": None,
            "numerical_context": [],
            "comparison_request": False,
            "prediction_request": False,
            "recommendation_request": False,
        }

        # Detect financial domains
        for domain, keywords in self.financial_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                intent_analysis["financial_domain"].append(domain)

        # Detect time references
        time_patterns = {
            "month": r"\b(this month|last month|monthly|per month)\b",
            "year": r"\b(this year|last year|yearly|annual)\b",
            "week": r"\b(this week|weekly|per week)\b",
            "future": r"\b(next|future|upcoming|will|predict)\b",
            "past": r"\b(last|previous|before|history)\b",
        }

        for time_type, pattern in time_patterns.items():
            if re.search(pattern, query_lower):
                intent_analysis["time_reference"] = time_type
                break

        # Detect numerical context (amounts, percentages)
        numbers = re.findall(r"\$?(\d+(?:,\d{3})*(?:\.\d{2})?)", query)
        percentages = re.findall(r"(\d+(?:\.\d+)?%)", query)
        intent_analysis["numerical_context"] = numbers + percentages

        # Detect request types
        if any(
            word in query_lower for word in ["compare", "vs", "versus", "difference"]
        ):
            intent_analysis["comparison_request"] = True

        if any(
            word in query_lower for word in ["predict", "forecast", "future", "will"]
        ):
            intent_analysis["prediction_request"] = True

        if any(
            word in query_lower
            for word in ["recommend", "suggest", "advice", "should", "how to"]
        ):
            intent_analysis["recommendation_request"] = True

        return intent_analysis

    def generate_advanced_context(
        self, df: pd.DataFrame, query_intent: Dict[str, Any]
    ) -> str:
        """Generate sophisticated context based on query intent and data analysis"""
        if df.empty:
            return "No expense data available for analysis."

        try:
            # Convert amount to numeric
            df_copy = df.copy()
            df_copy["amount"] = pd.to_numeric(df_copy["amount"], errors="coerce")

            # Advanced financial metrics
            context_parts = []

            # 1. Basic Financial Overview
            total_expenses = df_copy[df_copy["amount"] < 0]["amount"].abs().sum()
            total_income = df_copy[df_copy["amount"] > 0]["amount"].sum()
            net_cash_flow = total_income - total_expenses

            context_parts.append(
                f"""💰 **Financial Overview**
Total Income: ${total_income:,.2f}
Total Expenses: ${total_expenses:,.2f}
Net Cash Flow: ${net_cash_flow:,.2f}
Savings Rate: {(net_cash_flow/total_income*100 if total_income > 0 else 0):.1f}%"""
            )

            # 2. Advanced Spending Analysis
            expenses_df = df_copy[df_copy["amount"] < 0].copy()
            expenses_df["amount"] = expenses_df["amount"].abs()

            if not expenses_df.empty:
                # Category analysis with financial intelligence
                category_analysis = self._analyze_categories(expenses_df)
                context_parts.append(category_analysis)

                # Temporal analysis
                temporal_analysis = self._analyze_temporal_patterns(expenses_df)
                context_parts.append(temporal_analysis)

                # Spending behavior insights
                behavior_analysis = self._analyze_spending_behavior(expenses_df)
                context_parts.append(behavior_analysis)

            # 3. Predictive insights (if requested)
            if query_intent.get("prediction_request"):
                prediction_analysis = self._generate_predictions(df_copy)
                context_parts.append(prediction_analysis)

            # 4. Budgeting insights (if relevant)
            if "budgeting" in query_intent.get("financial_domain", []):
                budget_analysis = self._generate_budget_insights(expenses_df)
                context_parts.append(budget_analysis)

            return "\n\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error generating advanced context: {e}")
            return f"Error processing expense data: {str(e)}"

    def _analyze_categories(self, expenses_df: pd.DataFrame) -> str:
        """Analyze spending categories with financial intelligence"""
        category_summary = (
            expenses_df.groupby("category")["amount"]
            .agg(["sum", "count", "mean"])
            .round(2)
        )
        category_summary["percentage"] = (
            category_summary["sum"] / category_summary["sum"].sum() * 100
        ).round(1)
        category_summary = category_summary.sort_values("sum", ascending=False)

        # Categorize expenses by type
        essential_spending = 0
        lifestyle_spending = 0

        for category in category_summary.index:
            amount = category_summary.loc[category, "sum"]
            if any(
                essential in category.lower()
                for essential in self.expense_categories["essential"]
            ):
                essential_spending += amount
            elif any(
                lifestyle in category.lower()
                for lifestyle in self.expense_categories["lifestyle"]
            ):
                lifestyle_spending += amount

        total_spending = category_summary["sum"].sum()

        analysis = f"""📊 **Category Analysis**
Top 5 Categories:
{category_summary.head().to_string()}

🏠 Essential Spending: ${essential_spending:,.2f} ({essential_spending/total_spending*100:.1f}%)
🎯 Lifestyle Spending: ${lifestyle_spending:,.2f} ({lifestyle_spending/total_spending*100:.1f}%)

💡 Spending Distribution Insight:
- Recommended essential spending: 50-60% of income
- Your essential spending ratio: {essential_spending/total_spending*100:.1f}%"""

        return analysis

    def _analyze_temporal_patterns(self, expenses_df: pd.DataFrame) -> str:
        """Analyze temporal spending patterns"""
        if "date" not in expenses_df.columns:
            return ""

        expenses_df["date"] = pd.to_datetime(expenses_df["date"])
        expenses_df["day_of_week"] = expenses_df["date"].dt.day_name()
        expenses_df["month"] = expenses_df["date"].dt.month_name()

        # Weekly patterns
        weekly_spending = expenses_df.groupby("day_of_week")["amount"].sum().round(2)
        peak_day = weekly_spending.idxmax()

        # Monthly trends (if enough data)
        monthly_trend = ""
        if len(expenses_df) > 30:
            expenses_df["month_year"] = expenses_df["date"].dt.to_period("M")
            monthly_spending = expenses_df.groupby("month_year")["amount"].sum()
            if len(monthly_spending) > 1:
                trend = (
                    "increasing"
                    if monthly_spending.iloc[-1] > monthly_spending.iloc[-2]
                    else "decreasing"
                )
                change = (
                    (monthly_spending.iloc[-1] - monthly_spending.iloc[-2])
                    / monthly_spending.iloc[-2]
                    * 100
                )
                monthly_trend = f"Monthly Trend: {trend} by {abs(change):.1f}%"

        return f"""📈 **Temporal Patterns**
Peak Spending Day: {peak_day} (${weekly_spending[peak_day]:,.2f})
Weekly Pattern: {weekly_spending.to_dict()}
{monthly_trend}"""

    def _analyze_spending_behavior(self, expenses_df: pd.DataFrame) -> str:
        """Analyze spending behavior patterns"""
        # Transaction frequency and sizes
        avg_transaction = expenses_df["amount"].mean()
        median_transaction = expenses_df["amount"].median()
        large_transactions = expenses_df[expenses_df["amount"] > avg_transaction * 2]

        # Spending consistency
        std_dev = expenses_df["amount"].std()
        cv = (
            std_dev / avg_transaction if avg_transaction > 0 else 0
        )  # Coefficient of variation

        consistency = (
            "Consistent" if cv < 0.5 else "Variable" if cv < 1.0 else "Highly Variable"
        )

        return f"""🎯 **Spending Behavior**
Average Transaction: ${avg_transaction:.2f}
Median Transaction: ${median_transaction:.2f}
Large Transactions (>2x avg): {len(large_transactions)} transactions
Spending Consistency: {consistency} (CV: {cv:.2f})

💡 Behavior Insight: {'Your spending is quite predictable.' if cv < 0.5 else 'Your spending varies significantly - consider budgeting for irregular expenses.'}"""

    def _generate_predictions(self, df: pd.DataFrame) -> str:
        """Generate predictive insights"""
        if len(df) < 30:  # Need sufficient data for predictions
            return "📮 **Predictions**: Insufficient data for reliable predictions (need 30+ transactions)"

        # Simple trend analysis for next month prediction
        df_copy = df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        df_copy = df_copy.sort_values("date")

        # Monthly aggregation
        monthly_data = df_copy.groupby(df_copy["date"].dt.to_period("M"))[
            "amount"
        ].sum()

        if len(monthly_data) >= 3:
            # Simple linear trend
            recent_months = monthly_data.tail(3)
            trend = recent_months.diff().mean()
            next_month_prediction = recent_months.iloc[-1] + trend

            return f"""🔮 **Predictive Insights**
Predicted Next Month Net: ${next_month_prediction:.2f}
Trend: {'Improving' if trend > 0 else 'Declining'} by ${abs(trend):.2f}/month
Confidence: {'High' if len(monthly_data) >= 6 else 'Medium'}

📊 Recent 3-Month Pattern: {recent_months.round(2).to_dict()}"""

        return "📮 **Predictions**: Building predictive model (need 3+ months of data)"

    def _generate_budget_insights(self, expenses_df: pd.DataFrame) -> str:
        """Generate personalized budgeting insights"""
        if expenses_df.empty:
            return ""

        total_expenses = expenses_df["amount"].sum()
        category_breakdown = (
            expenses_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        )

        # Budget recommendations based on 50/30/20 rule
        recommendations = []

        # Find categories that exceed typical percentages
        for category, amount in category_breakdown.head(5).items():
            percentage = (amount / total_expenses) * 100
            if "food" in category.lower() or "groceries" in category.lower():
                if percentage > 15:
                    recommendations.append(
                        f"🍽️ Food spending is {percentage:.1f}% (recommended: 10-15%)"
                    )
            elif "entertainment" in category.lower():
                if percentage > 10:
                    recommendations.append(
                        f"🎉 Entertainment is {percentage:.1f}% (recommended: 5-10%)"
                    )
            elif "transport" in category.lower():
                if percentage > 20:
                    recommendations.append(
                        f"🚗 Transportation is {percentage:.1f}% (recommended: 10-20%)"
                    )

        budget_analysis = f"""💡 **Smart Budget Insights**
Monthly Expense Total: ${total_expenses:,.2f}

🎯 **Category Optimization:**
{chr(10).join(recommendations) if recommendations else '✅ Your spending categories look well-balanced!'}

📋 **Recommended Budget Allocation:**
- Housing/Essentials: 50% (${total_expenses * 0.5:.2f})
- Wants/Lifestyle: 30% (${total_expenses * 0.3:.2f})
- Savings/Debt: 20% (${total_expenses * 0.2:.2f})"""

        return budget_analysis

    def create_advanced_system_prompt(self, query_intent: Dict[str, Any]) -> str:
        """Create a sophisticated system prompt based on query intent"""
        base_prompt = """You are LocalBudgetAI Pro, an advanced AI financial advisor with expertise in:
- Personal finance management and budgeting
- Spending pattern analysis and behavioral insights
- Financial planning and goal setting
- Investment and savings strategies
- Debt management and cash flow optimization

Your advanced capabilities:
- Analyze complex financial data with contextual understanding
- Provide personalized recommendations based on spending patterns
- Offer predictive insights and trend analysis
- Give actionable advice for financial optimization
- Use financial domain knowledge for accurate insights"""

        # Customize prompt based on intent
        if query_intent.get("prediction_request"):
            base_prompt += "\n\nFocus on: Provide forward-looking insights, trend analysis, and predictive recommendations."

        if query_intent.get("recommendation_request"):
            base_prompt += "\n\nFocus on: Give specific, actionable financial advice and step-by-step recommendations."

        if "budgeting" in query_intent.get("financial_domain", []):
            base_prompt += "\n\nFocus on: Budget optimization, expense allocation, and financial goal setting."

        if query_intent.get("comparison_request"):
            base_prompt += "\n\nFocus on: Comparative analysis, benchmarking, and relative performance insights."

        base_prompt += """

Response Guidelines:
- Use specific numbers and percentages from the data
- Provide actionable insights, not just descriptions
- Include relevant financial concepts and terminology
- Structure responses with clear sections and emojis
- End with a practical, personalized recommendation
- Be concise but comprehensive in your analysis"""

        return base_prompt


def advanced_query_expense_ai(
    query: str, df: pd.DataFrame, model_choice: str = "mistral"
) -> Tuple[str, Optional[str]]:
    """
    Advanced AI query with enhanced NLP and financial intelligence

    Args:
        query (str): User's financial question
        df (pd.DataFrame): Expense data
        model_choice (str): Model to use ('mistral' or 'llama3')

    Returns:
        Tuple[str, Optional[str]]: (AI response, model_used)
    """
    try:
        import ollama
    except ImportError:
        return (
            "❌ Error: Ollama package not installed. Please install with: pip install ollama",
            None,
        )

    # Initialize advanced AI
    ai_assistant = AdvancedFinancialAI()

    # Analyze query intent
    query_intent = ai_assistant.analyze_query_intent(query)
    logger.info(f"Query intent analysis: {query_intent}")

    # Generate advanced context
    advanced_context = ai_assistant.generate_advanced_context(df, query_intent)

    # Create sophisticated system prompt
    system_prompt = ai_assistant.create_advanced_system_prompt(query_intent)

    # Get full model name
    from llm_helper import get_full_model_name

    # Primary model attempt
    try:
        logger.info(f"Attempting advanced query with {model_choice} model")

        full_model_name = get_full_model_name(model_choice)

        response = ollama.chat(
            model=full_model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"""Financial Data Analysis:
{advanced_context}

Query Intent Analysis:
- Primary Domain: {', '.join(query_intent.get('financial_domain', ['general']))}
- Time Context: {query_intent.get('time_reference', 'current')}
- Request Type: {'Prediction' if query_intent.get('prediction_request') else 'Recommendation' if query_intent.get('recommendation_request') else 'Analysis'}

User Question: {query}

Please provide a comprehensive financial analysis addressing the user's specific needs.""",
                },
            ],
        )

        ai_response = response["message"]["content"]
        logger.info(f"Successfully got advanced response from {model_choice}")
        return ai_response, model_choice

    except Exception as e:
        logger.warning(f"Advanced query failed with {model_choice}: {e}")

        # Fallback to alternative model
        fallback_model = "llama3" if model_choice == "mistral" else "mistral"

        try:
            logger.info(f"Attempting fallback to {fallback_model}")

            full_fallback_name = get_full_model_name(fallback_model)

            response = ollama.chat(
                model=full_fallback_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"""Financial Data Analysis:
{advanced_context}

User Question: {query}""",
                    },
                ],
            )

            ai_response = response["message"]["content"]
            logger.info(
                f"Successfully got response from fallback model {fallback_model}"
            )
            return ai_response, fallback_model

        except Exception as e2:
            logger.error(f"Both models failed. Primary: {e}, Fallback: {e2}")

            error_msg = f"""❌ **Advanced AI Assistant Unavailable**

**Issue:** Could not connect to Ollama models for advanced analysis.

**Basic Analysis Available:**
Based on your query: "{query}"

{advanced_context}

**To enable full AI capabilities:**
1. Start Ollama: `ollama serve`
2. Ensure models are available: `ollama list`
3. Try your query again

💡 **Note:** The data analysis above provides insights even without AI assistance."""

            return error_msg, None


def smart_expense_categorization(description: str, amount: float) -> str:
    """
    Use NLP to intelligently categorize expenses based on description and amount

    Args:
        description (str): Transaction description
        amount (float): Transaction amount

    Returns:
        str: Suggested category
    """
    if not description:
        return "Other"

    desc_lower = description.lower()

    # Advanced categorization rules with NLP-like patterns
    category_patterns = {
        "Groceries": [
            "grocery",
            "market",
            "food",
            "supermarket",
            "kroger",
            "walmart",
            "whole foods",
            "trader",
        ],
        "Restaurants": [
            "restaurant",
            "cafe",
            "coffee",
            "starbucks",
            "mcdonald",
            "pizza",
            "delivery",
            "uber eats",
            "doordash",
        ],
        "Transportation": [
            "gas",
            "fuel",
            "uber",
            "lyft",
            "taxi",
            "metro",
            "bus",
            "parking",
            "toll",
        ],
        "Utilities": [
            "electric",
            "water",
            "gas bill",
            "internet",
            "phone",
            "cable",
            "utility",
        ],
        "Healthcare": [
            "hospital",
            "doctor",
            "pharmacy",
            "medical",
            "dental",
            "vision",
            "cvs",
            "walgreens",
        ],
        "Entertainment": [
            "movie",
            "theater",
            "netflix",
            "spotify",
            "game",
            "concert",
            "event",
        ],
        "Shopping": [
            "amazon",
            "target",
            "mall",
            "store",
            "retail",
            "clothing",
            "shoes",
        ],
        "Home": ["rent", "mortgage", "home depot", "lowes", "furniture", "cleaning"],
        "Education": ["school", "university", "course", "book", "tuition", "education"],
        "Insurance": ["insurance", "premium", "policy"],
        "Banking": ["fee", "charge", "atm", "transfer", "interest"],
        "Income": (
            ["salary", "payroll", "deposit", "refund", "bonus"] if amount > 0 else []
        ),
    }

    # Check patterns
    for category, patterns in category_patterns.items():
        if any(pattern in desc_lower for pattern in patterns):
            return category

    # Amount-based categorization for unclear descriptions
    if amount > 1000:
        return "Large Purchase"
    elif amount < 10:
        return "Small Purchase"

    return "Other"
