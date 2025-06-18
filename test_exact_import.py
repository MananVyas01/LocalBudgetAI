#!/usr/bin/env python3
"""
Minimal test to replicate the exact Streamlit import scenario
"""

import sys
import os

# Set up path exactly like Streamlit does
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

print("Testing exact Streamlit import scenario...")
print(f"Current directory: {current_dir}")
print(f"App directory: {app_dir}")
print(f"App dir exists: {os.path.exists(app_dir)}")

# List files in app directory
if os.path.exists(app_dir):
    print(f"Files in app directory: {os.listdir(app_dir)}")

# Try to import exactly like main.py does
try:
    print("\nTesting import like main.py...")
    from llm_helper import check_ollama_status
    print("✅ Import successful")
    
    # Test the function
    result = check_ollama_status()
    print(f"✅ Function result: {result}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

# Test specific ollama import that might be failing
print("\n" + "="*50)
print("Testing ollama import specifically...")

try:
    import ollama
    print("✅ Ollama import in test context successful")
    print(f"✅ Ollama version: {getattr(ollama, '__version__', 'Unknown')}")
    
    # Test basic functionality
    models = ollama.list()
    print(f"✅ Models: {[m.model for m in models.models]}")
    
except Exception as e:
    print(f"❌ Ollama import/test failed: {e}")
    import traceback
    traceback.print_exc()
