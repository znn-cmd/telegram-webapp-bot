#!/usr/bin/env python3
"""
Тестовый скрипт для проверки получения данных рынка недвижимости
"""

import requests
import json

def test_market_data():
    """Тестирует получение данных рынка недвижимости"""
    
    # URL API
    url = "http://localhost:5000/api/generate_report"
    
    # Тестовые данные
    test_data = {
        "address": "Zerdalilik, 07100 Muratpaşa/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 51511,
        "language": "ru",
        "lat": 36.8969,
        "lng": 30.7133,
        "location_codes": {
            "country_id": 1,
            "city_id": 7,
            "district_id": 2409,
            "county_id": 2039,
            "country_name": "Türkiye",
            "city_name": "Antalya",
            "district_name": "Zerdalilik",
            "county_name": "Muratpaşa"
        }
    }
    
    print("🧪 Тестирование получения данных рынка недвижимости")
    print("=" * 80)
    print(f"Тестовый адрес: {test_data['address']}")
    print(f"Коды локаций: {test_data['location_codes']}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n✅ УСПЕШНЫЙ ОТВЕТ:")
                
                if result.get('report_text'):
                    print("\n📝 ПОЛНЫЙ ОТЧЕТ:")
                    print(result['report_text'])
                else:
                    print("❌ Текст отчета отсутствует")
            else:
                print(f"\n❌ Ошибка: {result.get('error')}")
        else:
            print(f"\n❌ HTTP ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    test_market_data() 