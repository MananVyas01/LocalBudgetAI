#!/usr/bin/env python3
"""
Test script for AI Assistant functionality in LocalBudgetAI.
This script tests all the core AI assistant functions to ensure they work properly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from llm_helper import (
    check_ollama_status, 
    get_available_models, 
    query_expense_ai,
    get_expense_context,
    get_full_model_name
)

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    print("🔍 Testing Ollama connection...")
    is_available, message = check_ollama_status()
    print(f"   Status: {'✅ Connected' if is_available else '❌ Failed'}")
    print(f"   Message: {message}")
    return is_available

def test_model_availability():
    """Test if AI models are available."""
    print("\n🧠 Testing model availability...")
    models = get_available_models()
    print(f"   Available models: {models}")
    
    # Test full model name resolution
    for model in models:
        full_name = get_full_model_name(model)
        print(f"   {model} -> {full_name}")
    
    return len(models) > 0

def test_ai_query():
    """Test AI query functionality."""
    print("\n💬 Testing AI query functionality...")
    
    test_context = """📊 **Expense Summary**
Total Records: 6
Date Range: 2024-01-01 to 2024-12-31
Total Expenses: $450.00
Total Income: $0.00
Net Savings: $-450.00

📈 **Top Spending Categories:**
Groceries    150.00
Gas          100.00
Restaurant    75.00
Entertainment 50.00
Utilities     75.00"""
    
    test_query = "What are my top spending categories and how can I save money?"
    
    try:
        response, model_used = query_expense_ai(test_query, test_context, 'mistral')
        
        if model_used:
            print(f"   ✅ AI Response received from {model_used}")
            print(f"   Response preview: {response[:100]}...")
            return True
        else:
            print(f"   ❌ AI query failed: {response}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception during AI query: {e}")
        return False

def test_context_generation():
    """Test expense context generation."""
    print("\n📊 Testing context generation...")
    
    try:
        import pandas as pd
        
        # Create sample data
        sample_data = {
            'date': pd.date_range('2024-01-01', periods=5, freq='D'),
            'amount': [-50.0, -25.0, -100.0, -30.0, -75.0],
            'description': ['Groceries', 'Gas', 'Restaurant', 'Coffee', 'Utilities'],
            'category': ['Food', 'Transport', 'Dining', 'Food', 'Bills']
        }
        
        df = pd.DataFrame(sample_data)
        context = get_expense_context(df)
        
        print(f"   ✅ Context generated successfully")
        print(f"   Context preview: {context[:150]}...")
        return True
        
    except Exception as e:
        print(f"   ❌ Context generation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 LocalBudgetAI - AI Assistant Test Suite")
    print("=" * 50)
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Model Availability", test_model_availability),
        ("Context Generation", test_context_generation),
        ("AI Query", test_ai_query)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The AI Assistant is working correctly.")
        print("\nYou can now use the AI Assistant in your LocalBudgetAI application.")
        print("Start the app with: streamlit run app/main.py")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please check the issues above.")

if __name__ == "__main__":
    main()
