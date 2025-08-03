#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции с Nominatim
"""

import requests
import json

def test_nominatim_integration():
    """Тестирует интеграцию с Nominatim"""
    
    # URL API
    url = "http://localhost:5000/api/geocode"
    
    # Тестовые адреса
    test_addresses = [
        "Zerdalilik, 07100 Muratpaşa/Antalya, Türkiye",
        "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye",
        "Avsallar, Cengiz Akay Sk. No:12, 07410 Alanya/Antalya, Türkiye"
    ]
    
    print("🧪 Тестирование интеграции с Nominatim")
    print("=" * 80)
    
    for i, address in enumerate(test_addresses, 1):
        print(f"\nТест {i}: {address}")
        print("-" * 60)
        
        try:
            response = requests.post(url, json={'address': address})
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    print("✅ УСПЕШНЫЙ ОТВЕТ:")
                    print(f"Formatted Address: {result.get('formatted_address')}")
                    print(f"Lat: {result.get('lat')}")
                    print(f"Lng: {result.get('lng')}")
                    
                    if result.get('location_components'):
                        components = result['location_components']
                        print("\n📊 КОМПОНЕНТЫ (Google + Nominatim):")
                        print(f"  - Country: {components.get('country')}")
                        print(f"  - Country Code: {components.get('country_code')}")
                        print(f"  - City: {components.get('city')}")
                        print(f"  - District: {components.get('district')}")
                        print(f"  - County: {components.get('county')}")
                        print(f"  - Postal Code: {components.get('postal_code')}")
                        
                        # Показываем данные Nominatim
                        if components.get('nominatim_data'):
                            nominatim = components['nominatim_data']
                            print("\n🗺️  ДАННЫЕ NOMINATIM:")
                            print(f"  - Display Name: {nominatim.get('display_name')}")
                            print(f"  - District: {nominatim.get('district')}")
                            print(f"  - County: {nominatim.get('county')}")
                            print(f"  - Road: {nominatim.get('road')}")
                    
                    if result.get('location_codes'):
                        codes = result['location_codes']
                        print("\n🎯 КОДЫ ЛОКАЦИЙ:")
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
                    print(f"❌ Ошибка: {result.get('error')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Ошибка соединения: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    test_nominatim_integration() 