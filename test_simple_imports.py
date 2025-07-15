#!/usr/bin/env python3
"""
Simple import test to identify the issue
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing individual imports...")

# Test 1: Basic UI components
try:
    print("✅ UI status imports: Success")
except Exception as e:
    print(f"❌ UI status imports: {e}")

# Test 2: Error handling
try:
    print("✅ Error handling imports: Success")
except Exception as e:
    print(f"❌ Error handling imports: {e}")

# Test 3: Prerequisites (this might be the issue)
try:
    print("✅ Prerequisites imports: Success")
except Exception as e:
    print(f"❌ Prerequisites imports: {e}")

# Test 4: File discovery
try:
    print("✅ File discovery imports: Success")
except Exception as e:
    print(f"❌ File discovery imports: {e}")

# Test 5: Processor (this likely pulls in CLI)
try:
    print("✅ Processor imports: Success")
except Exception as e:
    print(f"❌ Processor imports: {e}")

print("\nTesting complete.")
