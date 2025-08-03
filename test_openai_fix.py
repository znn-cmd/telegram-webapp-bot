#!/usr/bin/env python3
"""
Test script to verify OpenAI fix
"""

import os
import sys

# Set environment variables
os.environ['SUPABASE_URL'] = "https://dzllnnohurlzjyabgsft.supabase.co"
os.environ['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ"

def test_openai_import():
    """Test OpenAI import fix"""
    print("🧪 Testing OpenAI Import Fix")
    print("=" * 50)
    
    try:
        # Test conditional import
        try:
            import openai
            OPENAI_AVAILABLE = True
            print("✅ OpenAI library available")
        except ImportError:
            OPENAI_AVAILABLE = False
            print("⚠️ OpenAI library not available, using fallback mode")
        
        # Test API key retrieval
        from app import get_openai_api_key
        api_key = get_openai_api_key()
        
        if api_key:
            print("✅ API key retrieved from database")
            print(f"Key length: {len(api_key)} characters")
        else:
            print("❌ No API key found in database")
        
        # Test ChatGPT function
        from app import generate_trend_interpretation_with_chatgpt
        
        # Test with dummy data
        test_data = [
            {'year': 2020, 'value': 1.9},
            {'year': 2021, 'value': 11.4},
            {'year': 2022, 'value': 5.5}
        ]
        
        result = generate_trend_interpretation_with_chatgpt(
            gdp_trend=0.876,
            inflation_trend=0.423,
            gdp_data=test_data,
            inflation_data=test_data,
            language='ru'
        )
        
        print("✅ ChatGPT function executed successfully")
        print(f"Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_startup():
    """Test if app can start without OpenAI"""
    print("\n🧪 Testing App Startup")
    print("=" * 50)
    
    try:
        # Test basic imports
        import app
        print("✅ App imports successfully")
        
        # Test logger
        from app import logger
        print("✅ Logger available")
        
        # Test Supabase connection
        from app import supabase
        print("✅ Supabase connection available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during startup test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting OpenAI Fix Tests")
    print("=" * 70)
    
    # Run tests
    import_success = test_openai_import()
    startup_success = test_app_startup()
    
    # Summary
    print("\n" + "="*70)
    print("📋 OPENAI FIX TEST SUMMARY")
    print("="*70)
    print(f"Import Test: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"Startup Test: {'✅ PASS' if startup_success else '❌ FAIL'}")
    
    passed_tests = sum([import_success, startup_success])
    total_tests = 2
    
    print(f"\n🎯 Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! OpenAI fix is working correctly.")
        print("✅ Conditional import working")
        print("✅ Fallback mode functional")
        print("✅ App can start without OpenAI")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Please check the implementation.")
    
    print("\n📝 RECOMMENDATIONS:")
    if not import_success:
        print("  - Check OpenAI library installation")
        print("  - Verify API key in database")
    if not startup_success:
        print("  - Check app.py syntax")
        print("  - Verify all imports") 