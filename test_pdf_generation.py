#!/usr/bin/env python3
"""
Test script for PDF generation to identify issues
"""

import os
import sys
import requests
import json

# Set environment variables
os.environ['SUPABASE_URL'] = "https://dzllnnohurlzjyabgsft.supabase.co"
os.environ['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ"

def test_pdf_generation():
    """Test PDF generation with sample data"""
    print("🧪 Testing PDF Generation")
    print("=" * 50)
    
    # Sample report data
    report_data = {
        "report": {
            "object": {
                "address": "Zerdalilik, 07100 Muratpaşa/Antalya, Türkiye",
                "bedrooms": "3",
                "purchase_price": 11144411
            },
            "roi": {
                "short_term": {"roi": 81.5},
                "long_term": {"roi": 130.5},
                "no_rent": {"roi": 23}
            },
            "macro": {
                "inflation": 35.9,
                "refi_rate": 45,
                "gdp_growth": 2.7
            },
            "economic_charts": {
                "country_code": "TUR",
                "country_name": "Türkiye, Republic of",
                "gdp_chart": {
                    "datasets": [{
                        "data": [0.8, 1.9, 11.4, 5.5, 5.1, 3.2, 2.7],
                        "label": "Рост ВВП (%)"
                    }],
                    "labels": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]
                },
                "inflation_chart": {
                    "datasets": [{
                        "data": [15.2, 12.3, 19.6, 72.3, 53.9, 58.5, 35.9],
                        "label": "Инфляция (%)"
                    }],
                    "labels": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"]
                }
            },
            "taxes": {
                "transfer_tax": 0.04,
                "stamp_duty": 0.015,
                "notary": 1200
            },
            "alternatives": [
                {"name": "Банковский депозит", "yield": 0.128},
                {"name": "Облигации Турции", "yield": 0.245}
            ],
            "risks": ["Валютный: TRY/EUR ▲23% за 3 года"],
            "liquidity": "Среднее время продажи: 68 дней",
            "district": "Новый трамвай до пляжа (2026)"
        },
        "report_id": 999,
        "telegram_id": "1952374904"
    }
    
    try:
        # Test the PDF generation endpoint
        response = requests.post(
            "http://localhost:5000/api/generate_pdf_report",
            json=report_data,
            timeout=60
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PDF Generation Successful")
            print(f"PDF Path: {result.get('pdf_path', 'N/A')}")
            print(f"Success: {result.get('success', 'N/A')}")
        else:
            print(f"❌ PDF Generation Failed")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: PDF generation took too long")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing Module Imports")
    print("=" * 30)
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib imported successfully")
    except Exception as e:
        print(f"❌ matplotlib import failed: {e}")
    
    try:
        import matplotlib.font_manager as fm
        print("✅ matplotlib.font_manager imported successfully")
    except Exception as e:
        print(f"❌ matplotlib.font_manager import failed: {e}")
    
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
        print("✅ fpdf2 imported successfully")
    except Exception as e:
        print(f"❌ fpdf2 import failed: {e}")
    
    try:
        from io import BytesIO
        print("✅ BytesIO imported successfully")
    except Exception as e:
        print(f"❌ BytesIO import failed: {e}")

if __name__ == "__main__":
    test_imports()
    test_pdf_generation() 