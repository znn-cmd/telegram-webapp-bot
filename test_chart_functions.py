#!/usr/bin/env python3
"""
Test chart creation functions directly
"""

import os
import sys

# Set environment variables
os.environ['SUPABASE_URL'] = "https://dzllnnohurlzjyabgsft.supabase.co"
os.environ['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ"

def test_chart_creation():
    """Test chart creation functions"""
    print("🧪 Testing Chart Creation Functions")
    print("=" * 50)
    
    try:
        # Import the functions
        from app import create_property_trends_chart, create_chart_image_for_pdf
        
        # Test data
        historical_data = {
            'years': [2021, 2022, 2023, 2024, 2025],
            'sale_prices': [1000, 1100, 1200, 1300, 1400],
            'rent_prices': [10, 11, 12, 13, 14]
        }
        
        # Test property trends chart
        print("Testing property trends chart creation...")
        sale_chart = create_property_trends_chart(historical_data, 'sale', 180, 80)
        if sale_chart:
            print("✅ Sale chart created successfully")
        else:
            print("❌ Sale chart creation failed")
        
        rent_chart = create_property_trends_chart(historical_data, 'rent', 180, 80)
        if rent_chart:
            print("✅ Rent chart created successfully")
        else:
            print("❌ Rent chart creation failed")
        
        # Test economic chart
        print("\nTesting economic chart creation...")
        chart_data = {
            'labels': ['2019', '2020', '2021', '2022', '2023', '2024', '2025'],
            'gdp_chart': {
                'datasets': [{
                    'data': [0.8, 1.9, 11.4, 5.5, 5.1, 3.2, 2.7],
                    'label': 'Рост ВВП (%)'
                }]
            },
            'inflation_chart': {
                'datasets': [{
                    'data': [15.2, 12.3, 19.6, 72.3, 53.9, 58.5, 35.9],
                    'label': 'Инфляция (%)'
                }]
            }
        }
        
        economic_chart = create_chart_image_for_pdf(chart_data, "Economic Data", 180, 100)
        if economic_chart:
            print("✅ Economic chart created successfully")
        else:
            print("❌ Economic chart creation failed")
        
    except Exception as e:
        print(f"❌ Error during chart creation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chart_creation() 