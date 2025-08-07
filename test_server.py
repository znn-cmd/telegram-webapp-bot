#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы сервера
"""

import requests
import json
import time

def test_server():
    """Тестирует работу сервера"""
    
    print("🧪 Тестирование сервера")
    print("=" * 40)
    
    # Тест 1: Проверка здоровья сервера
    print("1️⃣ Проверка здоровья сервера...")
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Сервер работает")
            print(f"   Ответ: {response.json()}")
        else:
            print(f"❌ Сервер вернул код {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен на localhost:5000")
        print("💡 Запустите сервер командой: python app.py")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # Тест 2: Тестирование геокодинга
    print("\n2️⃣ Тестирование геокодинга...")
    test_address = "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya"
    
    try:
        response = requests.post(
            'http://localhost:5000/api/geocode',
            json={'address': test_address},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Геокодинг работает")
                print(f"   Адрес: {data.get('formatted_address')}")
                print(f"   Координаты: {data.get('lat')}, {data.get('lng')}")
                if data.get('location_codes'):
                    print(f"   Коды локаций: {data.get('location_codes')}")
                else:
                    print("   ⚠️ Коды локаций не найдены")
            else:
                print("❌ Геокодинг не удался")
                print(f"   Ошибка: {data.get('error')}")
                return False
        else:
            print(f"❌ Сервер вернул код {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании геокодинга: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("✅ Все тесты пройдены успешно!")
    return True

if __name__ == "__main__":
    success = test_server()
    if not success:
        print("\n❌ Тесты не пройдены. Проверьте:")
        print("   1. Запущен ли сервер: python app.py")
        print("   2. Нет ли ошибок в логах сервера")
        print("   3. Правильно ли настроены переменные окружения")
