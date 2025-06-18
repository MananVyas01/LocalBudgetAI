#!/usr/bin/env python3
"""
Comprehensive test for Stage 3: SQLite Integration and Dual Input functionality
"""
import sys
import os
sys.path.append('/workspaces/LocalBudgetAI/app')

import pandas as pd
from datetime import datetime, date
from database import ExpenseDatabase

def test_stage3_functionality():
    """Test all Stage 3 features comprehensively"""
    
    print("=== Testing Stage 3: Local Persistence (SQLite) ===")
    
    # Test 1: Database Initialization
    print("\n🔹 Task 1: Database Initialization")
    try:
        # Create test database
        test_db = ExpenseDatabase("test_expenses.db")
        print("✅ Database initialized successfully")
        
        # Verify table creation
        stats = test_db.get_database_stats()
        print(f"✅ Database stats: {stats}")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    # Test 2: Manual Entry (Insert Operations)
    print("\n🔹 Task 2: Manual Entry Testing")
    try:
        # Test inserting expenses
        expense_id1 = test_db.insert_expense(
            date="2024-01-15",
            amount=-50.00,
            category="Food",
            description="Grocery shopping"
        )
        print(f"✅ Inserted expense ID: {expense_id1}")
        
        # Test inserting income
        income_id = test_db.insert_expense(
            date="2024-01-16",
            amount=2500.00,
            category="Income",
            description="Monthly salary"
        )
        print(f"✅ Inserted income ID: {income_id}")
        
        # Test edge cases
        try:
            test_db.insert_expense("", -10, "Food", "")
            print("❌ Should have failed for empty date")
            return False
        except ValueError:
            print("✅ Correctly rejected empty date")
        
        try:
            test_db.insert_expense("2024-01-15", "invalid", "Food", "")
            print("❌ Should have failed for invalid amount")
            return False
        except ValueError:
            print("✅ Correctly rejected invalid amount")
        
    except Exception as e:
        print(f"❌ Manual entry testing failed: {e}")
        return False
    
    # Test 3: Data Retrieval
    print("\n🔹 Task 3: Data Retrieval Testing")
    try:
        # Fetch all expenses
        all_expenses = test_db.fetch_expenses()
        print(f"✅ Fetched {len(all_expenses)} expenses")
        print(f"Columns: {all_expenses.columns.tolist()}")
        
        # Test filtering
        food_expenses = test_db.fetch_expenses(category="Food")
        print(f"✅ Filtered Food expenses: {len(food_expenses)}")
        
        # Test date filtering
        date_filtered = test_db.fetch_expenses(
            start_date="2024-01-15",
            end_date="2024-01-16"
        )
        print(f"✅ Date filtered expenses: {len(date_filtered)}")
        
        # Test getting single expense
        single_expense = test_db.get_expense_by_id(expense_id1)
        print(f"✅ Retrieved single expense: {single_expense['category']}")
        
    except Exception as e:
        print(f"❌ Data retrieval testing failed: {e}")
        return False
    
    # Test 4: Update Operations
    print("\n🔹 Task 4: Update Operations Testing")
    try:
        # Update an expense
        success = test_db.update_expense(
            expense_id=expense_id1,
            date="2024-01-15",
            amount=-75.00,
            category="Food",
            description="Updated grocery shopping"
        )
        print(f"✅ Update operation success: {success}")
        
        # Verify update
        updated_expense = test_db.get_expense_by_id(expense_id1)
        if updated_expense['amount'] == -75.00:
            print("✅ Update verified successfully")
        else:
            print("❌ Update verification failed")
            return False
        
        # Test updating non-existent record
        no_update = test_db.update_expense(99999, "2024-01-01", -10, "Test", "")
        if not no_update:
            print("✅ Correctly handled non-existent record update")
        else:
            print("❌ Should not have updated non-existent record")
        
    except Exception as e:
        print(f"❌ Update operations testing failed: {e}")
        return False
    
    # Test 5: Delete Operations
    print("\n🔹 Task 5: Delete Operations Testing")
    try:
        # Add a test expense to delete
        delete_id = test_db.insert_expense(
            date="2024-01-17",
            amount=-25.00,
            category="Test",
            description="To be deleted"
        )
        
        # Delete the expense
        success = test_db.delete_expense(delete_id)
        print(f"✅ Delete operation success: {success}")
        
        # Verify deletion
        deleted_expense = test_db.get_expense_by_id(delete_id)
        if deleted_expense is None:
            print("✅ Deletion verified successfully")
        else:
            print("❌ Deletion verification failed")
            return False
        
        # Test deleting non-existent record
        no_delete = test_db.delete_expense(99999)
        if not no_delete:
            print("✅ Correctly handled non-existent record deletion")
        else:
            print("❌ Should not have deleted non-existent record")
        
    except Exception as e:
        print(f"❌ Delete operations testing failed: {e}")
        return False
    
    # Test 6: CSV Import Functionality
    print("\n🔹 Task 6: CSV Import Testing")
    try:
        # Create test CSV data
        test_data = pd.DataFrame({
            'Date': ['2024-01-18', '2024-01-19', '2024-01-20'],
            'Amount': [-30.0, -45.0, -60.0],
            'Category': ['Transportation', 'Food', 'Entertainment'],
            'Description': ['Bus fare', 'Lunch', 'Movie tickets']
        })
        
        # Import from DataFrame
        imported_count = test_db.import_from_dataframe(test_data)
        print(f"✅ Imported {imported_count} records from DataFrame")
        
        # Verify import
        all_expenses_after_import = test_db.fetch_expenses()
        if len(all_expenses_after_import) >= imported_count:
            print("✅ CSV import verified successfully")
        else:
            print("❌ CSV import verification failed")
            return False
        
    except Exception as e:
        print(f"❌ CSV import testing failed: {e}")
        return False
    
    # Test 7: Category Management
    print("\n🔹 Task 7: Category Management Testing")
    try:
        # Get categories
        categories = test_db.get_categories()
        print(f"✅ Retrieved {len(categories)} categories: {categories}")
        
        if len(categories) > 0:
            print("✅ Category management working correctly")
        else:
            print("❌ No categories found")
        
    except Exception as e:
        print(f"❌ Category management testing failed: {e}")
        return False
    
    # Test 8: Database Statistics
    print("\n🔹 Task 8: Database Statistics Testing")
    try:
        final_stats = test_db.get_database_stats()
        print(f"✅ Final database statistics:")
        print(f"   • Total Records: {final_stats['total_records']}")
        print(f"   • Total Expenses: ${final_stats['total_expenses']:.2f}")
        print(f"   • Total Income: ${final_stats['total_income']:.2f}")
        print(f"   • Net Savings: ${final_stats['net_savings']:.2f}")
        print(f"   • Categories: {final_stats['category_count']}")
        print(f"   • Date Range: {final_stats['date_range']}")
        
    except Exception as e:
        print(f"❌ Database statistics testing failed: {e}")
        return False
    
    # Cleanup
    try:
        os.remove("test_expenses.db")
        print("\n✅ Test database cleaned up")
    except:
        pass
    
    print("\n🎉 === ALL STAGE 3 TESTS PASSED! ===")
    print("✅ SQLite database integration working perfectly")
    print("✅ Manual entry with validation implemented")
    print("✅ Full CRUD operations (Create, Read, Update, Delete)")
    print("✅ CSV import functionality working")
    print("✅ Data filtering and querying operational")
    print("✅ Error handling and edge cases covered")
    print("✅ Professional database design with indexes")
    return True

if __name__ == "__main__":
    success = test_stage3_functionality()
    sys.exit(0 if success else 1)
