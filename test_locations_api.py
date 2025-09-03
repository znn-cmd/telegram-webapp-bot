#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений API локаций
"""

import requests
import json

def test_locations_api():
    """Тестирует API локаций"""
    base_url = "http://localhost:5000"
    
    print("🧪 ТЕСТИРОВАНИЕ API ЛОКАЦИЙ")
    print("=" * 50)
    
    # Тест 1: Получение стран
    print("\n1️⃣ ТЕСТ ПОЛУЧЕНИЯ СТРАН")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/locations/countries")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                countries = data.get('countries', [])
                print(f"✅ Получено стран: {len(countries)}")
                for i, (country_id, country_name) in enumerate(countries[:5]):
                    print(f"   {i+1}. {country_name} (ID: {country_id})")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 2: Получение городов для Турции (country_id = 1)
    print("\n2️⃣ ТЕСТ ПОЛУЧЕНИЯ ГОРОДОВ ТУРЦИИ")
    print("-" * 40)
    
    try:
        response = requests.post(f"{base_url}/api/locations/cities", 
                                json={"country_id": 1})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cities = data.get('cities', [])
                print(f"✅ Получено городов: {len(cities)}")
                print("📋 Первые 10 городов:")
                for i, (city_id, city_name) in enumerate(cities[:10]):
                    print(f"   {i+1}. {city_name} (ID: {city_id})")
                
                if len(cities) > 10:
                    print(f"   ... и еще {len(cities) - 10} городов")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 3: Получение округов для конкретного города
    print("\n3️⃣ ТЕСТ ПОЛУЧЕНИЯ ОКРУГОВ")
    print("-" * 30)
    
    try:
        # Используем первый город из предыдущего теста
        response = requests.post(f"{base_url}/api/locations/counties", 
                                json={"city_id": 81})  # Düzce
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                counties = data.get('counties', [])
                print(f"✅ Получено округов: {len(counties)}")
                print("📋 Округа:")
                for i, (county_id, county_name) in enumerate(counties):
                    print(f"   {i+1}. {county_name} (ID: {county_id})")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 4: Получение районов для конкретного округа
    print("\n4️⃣ ТЕСТ ПОЛУЧЕНИЯ РАЙОНОВ")
    print("-" * 30)
    
    try:
        response = requests.post(f"{base_url}/api/locations/districts", 
                                json={"county_id": 1794})  # Gölyaka
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                districts = data.get('districts', [])
                print(f"✅ Получено районов: {len(districts)}")
                print("📋 Первые 10 районов:")
                for i, (district_id, district_name) in enumerate(districts[:10]):
                    print(f"   {i+1}. {district_name} (ID: {district_id})")
                
                if len(districts) > 10:
                    print(f"   ... и еще {len(districts) - 10} районов")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

if __name__ == "__main__":
    test_locations_api()
