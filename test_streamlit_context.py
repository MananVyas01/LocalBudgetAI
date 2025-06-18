#!/usr/bin/env python3
"""
Test script to replicate the Streamlit environment and test AI Assistant status
"""

import sys
import os

# Add the app directory to path (like Streamlit does)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

print("Testing AI Assistant in Streamlit-like environment...")
print("Python path:", sys.path[-2:])

try:
    from app.llm_helper import check_ollama_status
    
    print("\n✅ Successfully imported check_ollama_status")
    
    # Test the function
    is_available, status_msg = check_ollama_status()
    
    print(f"\n📊 Status Check Results:")
    print(f"   Available: {is_available}")
    print(f"   Message: {status_msg}")
    
    if is_available:
        print("\n🎉 AI Assistant should be working in Streamlit!")
    else:
        print(f"\n❌ AI Assistant issue: {status_msg}")
        
except Exception as e:
    print(f"\n❌ Error testing AI Assistant: {e}")
    import traceback
    traceback.print_exc()

# Also test direct import
print("\n" + "="*50)
print("Testing direct ollama import...")

try:
    import ollama
    print("✅ Direct ollama import successful")
    models = ollama.list()
    print(f"✅ Models found: {[m.model for m in models.models]}")
except Exception as e:
    print(f"❌ Direct ollama import failed: {e}")
