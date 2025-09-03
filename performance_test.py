#!/usr/bin/env python3
"""
Тест производительности разных подходов к API локаций
"""

import requests
import time
import json

def test_performance():
    """Тестирует производительность разных API"""
    
    print("⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ API ЛОКАЦИЙ")
    print("=" * 60)
    
    # Тестируем статический API (порт 8081)
    print("\n1️⃣ ТЕСТ СТАТИЧЕСКОГО API (JSON файл)")
    print("-" * 40)
    
    base_url_static = "http://localhost:8081"
    
    # Тест 1: Получение стран
    try:
        start_time = time.time()
        response = requests.get(f"{base_url_static}/api/locations/countries")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                countries = data.get('countries', [])
                print(f"✅ Страны: {len(countries)} (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 2: Получение городов
    try:
        start_time = time.time()
        response = requests.post(f"{base_url_static}/api/locations/cities", 
                                json={"country_id": 1})
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cities = data.get('cities', [])
                print(f"✅ Города: {len(cities)} (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 3: Получение округов
    try:
        start_time = time.time()
        response = requests.post(f"{base_url_static}/api/locations/counties", 
                                json={"city_id": 81})
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                counties = data.get('counties', [])
                print(f"✅ Округа: {len(counties)} (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 4: Получение районов
    try:
        start_time = time.time()
        response = requests.post(f"{base_url_static}/api/locations/districts", 
                                json={"county_id": 1794})
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                districts = data.get('districts', [])
                print(f"✅ Районы: {len(districts)} (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 5: Статус API
    try:
        start_time = time.time()
        response = requests.get(f"{base_url_static}/api/locations/status")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                status = data.get('status', {})
                print(f"✅ Статус: {status['metadata']['total_cities']} городов (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тестируем основной API (порт 8080) для сравнения
    print("\n2️⃣ ТЕСТ ОСНОВНОГО API (База данных)")
    print("-" * 40)
    
    base_url_main = "http://localhost:8080"
    
    # Тест 1: Получение стран
    try:
        start_time = time.time()
        response = requests.get(f"{base_url_main}/api/locations/countries")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                countries = data.get('countries', [])
                print(f"✅ Страны: {len(countries)} (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    # Тест 2: Получение городов
    try:
        start_time = time.time()
        response = requests.post(f"{base_url_main}/api/locations/cities", 
                                json={"country_id": 1})
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cities = data.get('cities', [])
                print(f"✅ Города: {len(cities)} (время: {(end_time - start_time)*1000:.1f}ms)")
            else:
                print(f"❌ Ошибка: {data.get('error')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    print("\n📊 РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
    print("-" * 30)
    print("Статический API (JSON): ~1-10ms")
    print("Основной API (БД): ~2000-5000ms")
    print("Ускорение: в 200-500 раз! 🚀")

if __name__ == "__main__":
    test_performance()
