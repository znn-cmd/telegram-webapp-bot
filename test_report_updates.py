#!/usr/bin/env python3
"""
Тестовый файл для проверки обновлений отчета
"""

import requests
import json

def test_admin_status_check():
    """Тест проверки статуса администратора"""
    url = "http://localhost:8080/api/check_admin_status"
    data = {
        "telegram_id": 123456789  # Тестовый ID
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_generate_report():
    """Тест генерации отчета"""
    url = "http://localhost:8080/api/generate_report"
    data = {
        "address": "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 111000,
        "lat": 36.8969,
        "lng": 30.7133,
        "language": "ru",
        "telegram_id": 123456789
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Report generated successfully!")
            print(f"Report text length: {len(result.get('report_text', ''))}")
            # Проверяем наличие новых разделов
            report_text = result.get('report_text', '')
            sections = [
                '=== ОБЩИЙ ТРЕНД ===',
                '=== ТРЕНД ПО ТИПУ ОБЪЕКТА ===',
                '=== ТРЕНД ПО ВОЗРАСТУ ОБЪЕКТА ===',
                '=== ТРЕНД ПО ЭТАЖУ ОБЪЕКТА ===',
                '=== ТРЕНД ПО ТИПУ ОТОПЛЕНИЯ ==='
            ]
            for section in sections:
                if section in report_text:
                    print(f"✅ {section} found in report")
                else:
                    print(f"❌ {section} not found in report")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing report updates...")
    print("\n1. Testing admin status check:")
    test_admin_status_check()
    
    print("\n2. Testing report generation:")
    test_generate_report() 