#!/usr/bin/env python3
"""
Test script for the improved CSV validation function
"""

import pandas as pd

def validate_required_columns(df):
    """Validate that the uploaded CSV contains required columns with flexible matching"""
    # Define flexible mappings for different column name variations
    column_mappings = {
        'date': ['date', 'Date', 'DATE', 'transaction_date', 'transaction date', 'trans_date', 'time', 'Time'],
        'amount': ['amount', 'Amount', 'AMOUNT', 'value', 'Value', 'price', 'Price', 'sum', 'Sum', 'total', 'Total'],
        'category': ['category', 'Category', 'CATEGORY', 'type', 'Type', 'expense_type', 'expense type', 'class', 'Class']
    }
    
    found_columns = {}
    missing_columns = []
    
    # Check each required column
    for required_col, variations in column_mappings.items():
        found = False
        for variation in variations:
            if variation in df.columns:
                found_columns[required_col] = variation
                found = True
                break
        
        if not found:
            missing_columns.append(required_col)
    
    return missing_columns, found_columns

# Test cases
test_cases = [
    ['date', 'amount', 'category'],
    ['Date', 'Amount', 'Category'], 
    ['DATE', 'AMOUNT', 'CATEGORY'],
    ['time', 'value', 'type'],
    ['transaction_date', 'price', 'expense_type'],
    ['wrong_col1', 'wrong_col2', 'wrong_col3'],
    ['Date', 'Amount', 'Category', 'Description'],
    ['date', 'amount', 'category', 'details']
]

print("🧪 Testing CSV Column Validation")
print("=" * 50)

for i, cols in enumerate(test_cases):
    df = pd.DataFrame(columns=cols)
    missing, found = validate_required_columns(df)
    
    print(f"Test {i+1}: {cols}")
    if not missing:
        print(f"  ✅ SUCCESS - Found: {found}")
    else:
        print(f"  ❌ MISSING: {missing}")
        if found:
            print(f"     Found: {found}")
    print()

# Test with actual CSV files
print("📄 Testing with actual CSV files")
print("=" * 50)

csv_files = ['test_expenses.csv', 'test_expenses_variations.csv']

for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        missing, found = validate_required_columns(df)
        
        print(f"File: {csv_file}")
        print(f"  Columns: {list(df.columns)}")
        
        if not missing:
            print(f"  ✅ SUCCESS - Mapped: {found}")
        else:
            print(f"  ❌ MISSING: {missing}")
            if found:
                print(f"     Found: {found}")
        print()
        
    except FileNotFoundError:
        print(f"File {csv_file} not found")
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

print("✅ Validation test completed!")
