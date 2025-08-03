#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой логики формирования отчетов
"""

import requests
import json

def test_new_report_logic():
    """Тестирует новую логику формирования отчетов"""
    
    # URL API
    url = "http://localhost:5000/api/generate_report"
    
    # Тестовые данные
    test_data = {
        "address": "Avsallar, Cengiz Akay Sk. No:12, 07410 Alanya/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 1122211,
        "language": "ru",
        "lat": 36.8969,
        "lng": 30.7133,
        "telegram_id": 123456789
    }
    
    try:
        print("Отправляем запрос на генерацию отчета...")
        print(f"Данные: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Успешный ответ:")
            print(f"Status: {result.get('success')}")
            
            if result.get('report'):
                print("\n📊 Данные отчета:")
                report = result['report']
                if report.get('location_codes'):
                    codes = report['location_codes']
                    print(f"  - Country ID: {codes.get('country_id')}")
                    print(f"  - City ID: {codes.get('city_id')}")
                    print(f"  - District ID: {codes.get('district_id')}")
                    print(f"  - County ID: {codes.get('county_id')}")
                    print(f"  - Country: {codes.get('country_name')}")
                    print(f"  - City: {codes.get('city_name')}")
                    print(f"  - District: {codes.get('district_name')}")
                    print(f"  - County: {codes.get('county_name')}")
                else:
                    print("  - Коды локаций не найдены")
                
                if report.get('property_details'):
                    details = report['property_details']
                    print(f"  - Address: {details.get('address')}")
                    print(f"  - Bedrooms: {details.get('bedrooms')}")
                    print(f"  - Price: {details.get('price')}")
            
            if result.get('report_text'):
                print("\n📝 Текст отчета:")
                print(result['report_text'])
            
        else:
            print(f"\n❌ Ошибка: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    test_new_report_logic() 