#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений геокодинга
"""

import os
import requests
import time

def test_google_maps_api():
    """Тестирует Google Maps API"""
    print("🧪 Тестируем Google Maps API...")
    
    # Тестовый адрес
    test_address = "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Турция"
    
    # Google Maps API
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': test_address,
        'key': 'AIzaSyBrDkDpNKNAIyY147MQ78hchBkeyCAxhEw'
    }
    
    try:
        print(f"📡 Отправляем запрос к Google Maps API...")
        start_time = time.time()
        
        response = requests.get(url, params=params, timeout=30)
        
        elapsed_time = time.time() - start_time
        print(f"✅ Google Maps API ответил за {elapsed_time:.2f} секунд")
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Статус ответа: {result.get('status')}")
            if result.get('results'):
                print(f"📍 Найдено результатов: {len(result['results'])}")
            return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут Google Maps API (30 секунд)")
        return False
    except Exception as e:
        print(f"❌ Ошибка Google Maps API: {e}")
        return False

def test_nominatim_api():
    """Тестирует Nominatim API"""
    print("\n🧪 Тестируем Nominatim API...")
    
    # Тестовый адрес
    test_address = "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Турция"
    
    # Nominatim API
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': test_address,
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    headers = {
        'User-Agent': 'Aaadviser/1.0'
    }
    
    try:
        print(f"📡 Отправляем запрос к Nominatim API...")
        start_time = time.time()
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        elapsed_time = time.time() - start_time
        print(f"✅ Nominatim API ответил за {elapsed_time:.2f} секунд")
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 Найдено результатов: {len(result)}")
            return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут Nominatim API (15 секунд)")
        return False
    except Exception as e:
        print(f"❌ Ошибка Nominatim API: {e}")
        return False

def test_environment_variables():
    """Тестирует переменные окружения"""
    print("\n🧪 Проверяем переменные окружения...")
    
    enable_nominatim = os.getenv('ENABLE_NOMINATIM', 'true').lower() == 'true'
    nominatim_timeout = int(os.getenv('NOMINATIM_TIMEOUT', '15'))
    
    print(f"📋 ENABLE_NOMINATIM: {enable_nominatim}")
    print(f"📋 NOMINATIM_TIMEOUT: {nominatim_timeout} секунд")
    
    if not enable_nominatim:
        print("🚫 Nominatim API отключен")
    else:
        print(f"✅ Nominatim API включен с таймаутом {nominatim_timeout}с")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования исправлений геокодинга")
    print("=" * 50)
    
    # Проверяем переменные окружения
    test_environment_variables()
    
    # Тестируем Google Maps API
    google_success = test_google_maps_api()
    
    # Тестируем Nominatim API
    nominatim_success = test_nominatim_api()
    
    # Результаты
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"🌐 Google Maps API: {'✅' if google_success else '❌'}")
    print(f"🗺️ Nominatim API: {'✅' if nominatim_success else '❌'}")
    
    if google_success and nominatim_success:
        print("\n🎉 Все API работают корректно!")
    elif google_success:
        print("\n⚠️ Google Maps API работает, но Nominatim API недоступен")
        print("💡 Рекомендуется установить ENABLE_NOMINATIM=false")
    else:
        print("\n❌ Проблемы с API - проверьте настройки")

if __name__ == "__main__":
    main()
