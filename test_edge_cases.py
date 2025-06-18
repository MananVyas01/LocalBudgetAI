#!/usr/bin/env python3
"""
Edge case and error handling tests for analyzer.py
"""
import sys
import os
sys.path.append('/workspaces/LocalBudgetAI/app')

import pandas as pd
import numpy as np
from analyzer import analyze_expenses_by_category, analyze_monthly_trend

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("=== Testing Edge Cases and Error Handling ===")
    
    # Test 1: Empty DataFrame
    print("\n1. Testing empty DataFrame...")
    try:
        empty_df = pd.DataFrame()
        result = analyze_expenses_by_category(empty_df)
        print("❌ Should have raised error for empty DataFrame")
        return False
    except (ValueError, TypeError) as e:
        print(f"✅ Correctly handled empty DataFrame: {type(e).__name__}")
    
    # Test 2: Missing columns
    print("\n2. Testing missing required columns...")
    try:
        bad_df = pd.DataFrame({'Wrong': [1, 2, 3], 'Columns': [4, 5, 6]})
        result = analyze_expenses_by_category(bad_df)
        print("❌ Should have raised error for missing columns")
        return False
    except ValueError as e:
        print(f"✅ Correctly handled missing columns: {e}")
    
    # Test 3: Invalid data types
    print("\n3. Testing invalid data types...")
    try:
        invalid_df = pd.DataFrame({
            'Category': ['Food', 'Transport', 'Food'],
            'Amount': ['not_a_number', 'also_invalid', -50.0],
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        result = analyze_expenses_by_category(invalid_df)
        print(f"✅ Gracefully handled invalid amounts, got {len(result)} categories")
    except Exception as e:
        print(f"❌ Should handle invalid amounts gracefully: {e}")
        return False
    
    # Test 4: Invalid dates
    print("\n4. Testing invalid dates...")
    try:
        date_df = pd.DataFrame({
            'Category': ['Food', 'Transport', 'Food'],
            'Amount': [-30.0, -20.0, -40.0],
            'Date': ['invalid_date', '2024-01-02', 'another_bad_date']
        })
        result = analyze_monthly_trend(date_df)
        print(f"✅ Gracefully handled invalid dates, got {len(result)} months")
    except Exception as e:
        print(f"❌ Should handle invalid dates gracefully: {e}")
        return False
    
    # Test 5: All positive amounts (no expenses)
    print("\n5. Testing all positive amounts...")
    try:
        income_df = pd.DataFrame({
            'Category': ['Salary', 'Bonus', 'Investment'],
            'Amount': [1000.0, 500.0, 200.0],
            'Date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        result = analyze_expenses_by_category(income_df)
        if len(result) == 0:
            print("✅ Correctly returned empty result for no expenses")
        else:
            print(f"❌ Should return empty for no expenses, got {len(result)}")
            return False
    except Exception as e:
        print(f"❌ Should handle no expenses gracefully: {e}")
        return False
    
    # Test 6: Mixed valid and invalid data
    print("\n6. Testing mixed valid/invalid data...")
    try:
        mixed_df = pd.DataFrame({
            'Category': ['Food', 'Transport', None, 'Entertainment', 'Food'],
            'Amount': [-30.0, 'invalid', -40.0, -25.0, np.nan],
            'Date': ['2024-01-01', '2024-13-45', '2024-01-03', '2024-01-04', '2024-01-05']
        })
        category_result = analyze_expenses_by_category(mixed_df)
        monthly_result = analyze_monthly_trend(mixed_df)
        print(f"✅ Handled mixed data: {len(category_result)} categories, {len(monthly_result)} months")
    except Exception as e:
        print(f"❌ Should handle mixed data gracefully: {e}")
        return False
    
    print("\n🎉 === ALL EDGE CASE TESTS PASSED! ===")
    print("✅ Robust error handling for empty data")
    print("✅ Proper validation of required columns")
    print("✅ Graceful handling of invalid data types")
    print("✅ Resilient date parsing with fallbacks")
    print("✅ Appropriate responses to edge cases")
    return True

if __name__ == "__main__":
    success = test_edge_cases()
    sys.exit(0 if success else 1)
