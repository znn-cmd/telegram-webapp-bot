#!/usr/bin/env python3
"""
Тестовый скрипт для проверки с данными Google Places API
"""

import requests
import json

def test_with_google_data():
    """Тестирует с данными Google Places API"""
    
    # URL API
    url = "http://localhost:5000/api/generate_report"
    
    # Тестовые данные с компонентами Google Places API
    test_data = {
        "address": "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 52000,
        "language": "ru",
        "lat": 36.8969,
        "lng": 30.7133,
        "location_components": {
            "country": "Turkey",
            "country_code": "TR",
            "city": "Antalya",
            "district": "Baraj",
            "county": "Kepez",
            "postal_code": "07320"
        },
        "location_codes": {
            "country_id": 1,
            "city_id": 7,
            "district_id": 2279,
            "county_id": 2037,
            "country_name": "Türkiye",
            "city_name": "Antalya",
            "district_name": "Ahatlı",
            "county_name": "Kepez"
        }
    }
    
    print("🧪 Тестирование с данными Google Places API")
    print("=" * 80)
    print(f"Тестовый адрес: {test_data['address']}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n✅ УСПЕШНЫЙ ОТВЕТ:")
                
                if result.get('report_text'):
                    print("\n📝 ТЕКСТ ОТЧЕТА:")
                    print(result['report_text'])
            else:
                print(f"\n❌ Ошибка: {result.get('error')}")
        else:
            print(f"\n❌ HTTP ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    test_with_google_data() 