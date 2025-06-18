"""
LLM Helper module for LocalBudgetAI - Dual Model Support with Ollama.

This module provides AI assistant functionality with support for both
mistral and llama3 models through Ollama, with automatic fallback.
"""

import logging
from typing import Tuple, Optional, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

def query_expense_ai(query: str, context: str, model_choice: str = 'mistral') -> Tuple[str, Optional[str]]:
    """
    Query the AI assistant with expense data context using Ollama.
    
    Args:
        query (str): User's question about expenses
        context (str): Expense data context (summary, categories, etc.)
        model_choice (str): Primary model to use ('mistral' or 'llama3')
        
    Returns:
        Tuple[str, Optional[str]]: (AI response, model_used)
    """
    try:
        import ollama
    except ImportError:
        return ("❌ Error: Ollama package not installed. Please install with: pip install ollama", None)
    
    # System prompt for expense analysis
    system_prompt = """You are LocalBudgetAI, a helpful AI assistant for personal expense analysis. 
    
    Your role:
    - Analyze spending patterns and provide insights
    - Answer questions about expenses, categories, and trends
    - Give practical budgeting advice
    - Be concise but informative
    - Use emojis to make responses engaging
    
    Response format:
    - Start with a relevant emoji
    - Give a direct answer
    - Include specific numbers when available
    - End with a practical tip or insight
    
    Remember: All data is private and local to the user."""
      # Primary model attempt
    try:
        logger.info(f"Attempting to query {model_choice} model")
        
        # Get the full model name for Ollama
        full_model_name = get_full_model_name(model_choice)
        
        response = ollama.chat(
            model=full_model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Expense Data Summary:\n{context}\n\nUser Question: {query}"}
            ]
        )
        
        ai_response = response['message']['content']
        logger.info(f"Successfully got response from {model_choice}")
        return ai_response, model_choice
        
    except Exception as e:
        logger.warning(f"Primary model {model_choice} failed: {e}")
        
        # Fallback to alternative model
        fallback_model = 'llama3' if model_choice == 'mistral' else 'mistral'
        
        try:
            logger.info(f"Attempting fallback to {fallback_model} model")
            
            # Get the full model name for fallback
            full_fallback_name = get_full_model_name(fallback_model)
            
            response = ollama.chat(
                model=full_fallback_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Expense Data Summary:\n{context}\n\nUser Question: {query}"}
                ]
            )
            
            ai_response = response['message']['content']
            logger.info(f"Successfully got response from fallback model {fallback_model}")
            return ai_response, fallback_model
            
        except Exception as e2:
            logger.error(f"Both models failed. Primary: {e}, Fallback: {e2}")
            
            # Provide helpful error message
            error_msg = f"""❌ **AI Assistant Unavailable**

**Issue:** Could not connect to Ollama models.

**Possible solutions:**
1. **Start Ollama service:** `ollama serve`
2. **Install required models:**
   - `ollama pull mistral`
   - `ollama pull llama3`
3. **Check Ollama status:** `ollama list`

**Error details:**
- Primary model ({model_choice}): {str(e)}
- Fallback model ({fallback_model}): {str(e2)}

💡 **Tip:** Make sure Ollama is running before using the AI assistant."""
            
            return error_msg, None

def get_expense_context(df, filters: Dict[str, Any] = None) -> str:
    """
    Generate context string from expense data for AI analysis.
    
    Args:
        df: Expense DataFrame
        filters: Applied filters dictionary
        
    Returns:
        str: Formatted context for AI
    """
    if df.empty:
        return "No expense data available."
    
    try:
        # Convert amount to numeric if needed
        df_copy = df.copy()
        df_copy['amount'] = pd.to_numeric(df_copy['amount'], errors='coerce')
        
        # Basic statistics
        total_records = len(df_copy)
        total_expenses = df_copy[df_copy['amount'] < 0]['amount'].abs().sum()
        total_income = df_copy[df_copy['amount'] > 0]['amount'].sum()
        net_savings = total_income - total_expenses
        
        # Category breakdown
        expenses_by_category = df_copy[df_copy['amount'] < 0].groupby('category')['amount'].apply(lambda x: x.abs().sum()).sort_values(ascending=False)
        
        # Date range
        date_range = f"{df_copy['date'].min().strftime('%Y-%m-%d')} to {df_copy['date'].max().strftime('%Y-%m-%d')}"
        
        # Monthly trend (if enough data)
        monthly_trend = ""
        if len(df_copy) > 1:
            df_copy['month'] = df_copy['date'].dt.to_period('M')
            monthly_expenses = df_copy[df_copy['amount'] < 0].groupby('month')['amount'].apply(lambda x: x.abs().sum())
            if len(monthly_expenses) > 1:
                latest_month = monthly_expenses.iloc[-1]
                previous_month = monthly_expenses.iloc[-2] if len(monthly_expenses) > 1 else latest_month
                change = ((latest_month - previous_month) / previous_month * 100) if previous_month != 0 else 0
                monthly_trend = f"\nMonthly Trend: {change:+.1f}% change from previous month"
        
        # Filter status
        filter_info = ""
        if filters and any(filters.values()):
            filter_info = f"\n\nActive Filters:"
            if filters.get('date_range'):
                start, end = filters['date_range']
                filter_info += f"\n- Date Range: {start} to {end}"
            if filters.get('categories'):
                filter_info += f"\n- Categories: {', '.join(filters['categories'])}"
            if filters.get('amount_range'):
                min_amt, max_amt = filters['amount_range']
                filter_info += f"\n- Amount Range: ${min_amt:.0f} to ${max_amt:.0f}"
        
        context = f"""📊 **Expense Summary**
Total Records: {total_records}
Date Range: {date_range}
Total Expenses: ${total_expenses:.2f}
Total Income: ${total_income:.2f}
Net Savings: ${net_savings:.2f}

📈 **Top Spending Categories:**
{expenses_by_category.head(5).to_string()}
{monthly_trend}
{filter_info}"""
        
        return context
        
    except Exception as e:
        logger.error(f"Error generating expense context: {e}")
        return f"Error processing expense data: {str(e)}"

def get_available_models() -> list:
    """
    Get list of available Ollama models.
    
    Returns:
        list: Available model names (without tags)
    """
    try:
        import ollama
        models = ollama.list()
        model_names = []
        for model in models.models:
            # Strip version tags (e.g., ":latest") to get base model name
            base_name = model.model.split(':')[0]
            model_names.append(base_name)
        return model_names
    except Exception as e:
        logger.warning(f"Could not get available models: {e}")
        return ['mistral', 'llama3']  # Default options

def check_ollama_status() -> Tuple[bool, str]:
    """
    Check if Ollama service is running and models are available.
    
    Returns:
        Tuple[bool, str]: (is_available, status_message)
    """
    import time
    logger.info(f"Checking Ollama status at {time.time()}")
    
    try:
        import ollama
        logger.info("✅ Ollama package imported successfully")
        models = ollama.list()
        logger.info(f"✅ Ollama.list() returned: {type(models)}")
        available_models = []
        for model in models.models:
            # Strip version tags (e.g., ":latest") to get base model name
            base_name = model.model.split(':')[0]
            available_models.append(base_name)
        
        logger.info(f"✅ Found models: {available_models}")
        
        if not available_models:
            return False, "Ollama is running but no models are installed."
        
        return True, f"Ollama is running with {len(available_models)} models available."
        
    except ImportError as e:
        logger.error(f"❌ ImportError: {e}")
        return False, "Ollama package not installed."
    except Exception as e:
        logger.error(f"❌ Other exception: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False, f"Ollama service not available: {str(e)}"

def get_full_model_name(base_name: str) -> str:
    """
    Get the full model name (with tag) for a base model name.
    
    Args:
        base_name (str): Base model name like 'mistral' or 'llama3'
        
    Returns:
        str: Full model name like 'mistral:latest' or 'llama3:latest'
    """
    try:
        import ollama
        models = ollama.list()
        for model in models.models:
            if model.model.startswith(base_name + ':'):
                return model.model
        # If not found with tag, return base name (might work for some models)
        return base_name
    except Exception:
        # Fallback to common pattern
        return f"{base_name}:latest"

# Import pandas for context generation
try:
    import pandas as pd
except ImportError:
    pd = None

def debug_ollama_import():
    """Debug function to check ollama import status"""
    try:
        import ollama
        return f"✅ Ollama imported successfully"
    except ImportError as e:
        return f"❌ Import error: {e}"
    except Exception as e:
        return f"❌ Other error: {e}"
