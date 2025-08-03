#!/usr/bin/env python3
"""
Simple syntax check for app.py
"""

import ast
import sys

def check_syntax(filename):
    """Check Python syntax of a file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the source code
        ast.parse(source)
        print(f"✅ Syntax check passed for {filename}")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"  Line {e.lineno}: {e.text}")
        print(f"  Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ Error checking {filename}: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Python syntax...")
    
    success = check_syntax('app.py')
    
    if success:
        print("\n🎉 Syntax check passed!")
        print("✅ app.py has valid Python syntax")
    else:
        print("\n⚠️ Syntax check failed!")
        print("❌ Please fix the syntax errors in app.py") 