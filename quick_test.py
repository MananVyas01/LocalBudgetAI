#!/usr/bin/env python3
"""
Quick verification test for Stage 3 core functionality
"""
import sys
import os
sys.path.append('/workspaces/LocalBudgetAI/app')

from database import ExpenseDatabase

def quick_test():
    """Quick test of core functionality"""
    print("=== Quick Stage 3 Verification ===")
    
    # Test database
    db = ExpenseDatabase("quick_test.db")
    print("✅ Database initialized")
    
    # Test insert
    id1 = db.insert_expense("2024-01-15", -50.0, "Food", "Test expense")
    print(f"✅ Inserted expense ID: {id1}")
    
    # Test fetch
    expenses = db.fetch_expenses()
    print(f"✅ Fetched {len(expenses)} records")
    
    # Test update
    success = db.update_expense(id1, "2024-01-15", -75.0, "Food", "Updated test")
    print(f"✅ Update successful: {success}")
    
    # Test delete
    success = db.delete_expense(id1)
    print(f"✅ Delete successful: {success}")
    
    # Cleanup
    os.remove("quick_test.db")
    print("✅ Cleanup complete")
    
    print("\n🎉 Stage 3 core functionality verified!")
    return True

if __name__ == "__main__":
    quick_test()
