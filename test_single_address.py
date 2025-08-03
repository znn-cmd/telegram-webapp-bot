#!/usr/bin/env python3
"""
Тестовый скрипт для проверки одного адреса с детальным выводом
"""

import requests
import json

def test_single_address():
    """Тестирует один адрес с детальным выводом"""
    
    # URL API
    url = "http://localhost:5000/api/geocode"
    
    # Тестовый адрес
    test_address = "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye"
    
    print("🧪 Тестирование одного адреса с детальным выводом")
    print("=" * 80)
    print(f"Тестовый адрес: {test_address}")
    print("=" * 80)
    
    try:
        response = requests.post(url, json={'address': test_address})
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n✅ УСПЕШНЫЙ ОТВЕТ:")
                print(f"Formatted Address: {result.get('formatted_address')}")
                print(f"Lat: {result.get('lat')}")
                print(f"Lng: {result.get('lng')}")
                
                if result.get('location_components'):
                    components = result['location_components']
                    print("\n📊 ИЗВЛЕЧЕННЫЕ КОМПОНЕНТЫ:")
                    print(f"  - Country: {components.get('country')}")
                    print(f"  - Country Code: {components.get('country_code')}")
                    print(f"  - City: {components.get('city')}")
                    print(f"  - District: {components.get('district')}")
                    print(f"  - County: {components.get('county')}")
                    print(f"  - Postal Code: {components.get('postal_code')}")
                
                if result.get('location_codes'):
                    codes = result['location_codes']
                    print("\n🎯 НАЙДЕННЫЕ КОДЫ ЛОКАЦИЙ:")
                    print(f"  - Country ID: {codes.get('country_id')}")
                    print(f"  - City ID: {codes.get('city_id')}")
                    print(f"  - District ID: {codes.get('district_id')}")
                    print(f"  - County ID: {codes.get('county_id')}")
                    print(f"  - Country: {codes.get('country_name')}")
                    print(f"  - City: {codes.get('city_name')}")
                    print(f"  - District: {codes.get('district_name')}")
                    print(f"  - County: {codes.get('county_name')}")
                else:
                    print("\n❌ Коды локаций не найдены")
            else:
                print(f"\n❌ Ошибка: {result.get('error')}")
        else:
            print(f"\n❌ HTTP ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    test_single_address() 