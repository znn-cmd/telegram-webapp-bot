#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы Aaadviser
"""

import os
import requests
import json
from dotenv import load_dotenv
from api_functions import (
    find_properties_by_location,
    generate_basic_report,
    get_user_balance,
    update_user_balance
)

# Загружаем переменные окружения
load_dotenv()

def test_supabase_connection():
    """Тест подключения к Supabase"""
    print("🔍 Тестирование подключения к Supabase...")
    
    try:
        from api_functions import SUPABASE_URL, SUPABASE_ANON_KEY
        
        headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json',
        }
        
        # Тестируем подключение к таблице users
        url = f"{SUPABASE_URL}/rest/v1/users?select=count"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ Подключение к Supabase успешно")
            return True
        else:
            print(f"❌ Ошибка подключения: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        return False

def test_data_availability():
    """Тест доступности данных"""
    print("\n📊 Тестирование доступности данных...")
    
    # Координаты центра Анталии
    test_coords = [
        (36.8841, 30.7056, "Kaleiçi"),
        (36.8572, 30.8491, "Lara"),
        (36.8969, 30.7133, "Muratpaşa")
    ]
    
    for lat, lon, district in test_coords:
        print(f"\n📍 Тестирование координат {district}: {lat}, {lon}")
        
        # Поиск объектов
        result = find_properties_by_location(lat, lon, radius_km=5.0)
        
        if result['properties']:
            print(f"✅ Найдено {len(result['properties'])} объектов")
            
            # Анализируем типы объектов
            types = {}
            for prop in result['properties']:
                prop_type = prop.get('property_type', 'unknown')
                types[prop_type] = types.get(prop_type, 0) + 1
            
            print(f"📋 Типы объектов: {types}")
        else:
            print("❌ Объекты не найдены")

def test_report_generation():
    """Тест генерации отчетов"""
    print("\n📈 Тестирование генерации отчетов...")
    
    # Тестовые координаты
    lat, lon = 36.8841, 30.7056
    
    try:
        report = generate_basic_report(lat, lon)
        
        if report.get('error'):
            print(f"❌ Ошибка генерации отчета: {report['message']}")
            return False
        else:
            print("✅ Отчет сгенерирован успешно")
            print(f"📍 Район: {report.get('district')}")
            print(f"🏠 Тип: {report.get('property_type')}")
            print(f"📊 Метрики: {report.get('metrics')}")
            print(f"💡 Инсайты: {report.get('insights')}")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка генерации отчета: {e}")
        return False

def test_user_balance_system():
    """Тест системы баланса пользователей"""
    print("\n💰 Тестирование системы баланса...")
    
    test_telegram_id = 123456789
    
    try:
        # Получаем текущий баланс
        balance = get_user_balance(test_telegram_id)
        print(f"💳 Текущий баланс: ${balance}")
        
        # Пополняем баланс
        top_up_amount = 50.0
        if update_user_balance(test_telegram_id, top_up_amount):
            new_balance = get_user_balance(test_telegram_id)
            print(f"✅ Баланс пополнен на ${top_up_amount}")
            print(f"💳 Новый баланс: ${new_balance}")
            
            # Тестируем списание
            charge_amount = 15.0
            if update_user_balance(test_telegram_id, -charge_amount):
                final_balance = get_user_balance(test_telegram_id)
                print(f"✅ Списано ${charge_amount}")
                print(f"💳 Финальный баланс: ${final_balance}")
                return True
            else:
                print("❌ Ошибка списания средств")
                return False
        else:
            print("❌ Ошибка пополнения баланса")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка системы баланса: {e}")
        return False

def test_api_endpoints():
    """Тест API эндпоинтов"""
    print("\n🌐 Тестирование API эндпоинтов...")
    
    base_url = "http://localhost:5000"
    
    # Тест health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check работает")
        else:
            print(f"❌ Health check не работает: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API сервер не запущен")
        return False
    
    # Тест генерации отчета
    try:
        data = {
            "lat": 36.8841,
            "lon": 30.7056,
            "telegram_id": 123456789
        }
        
        response = requests.post(
            f"{base_url}/api/generate-report",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if not result.get('error'):
                print("✅ API генерации отчета работает")
            else:
                print(f"❌ Ошибка API: {result.get('message')}")
                return False
        else:
            print(f"❌ API ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False
    
    return True

def test_webapp_functionality():
    """Тест функциональности WebApp"""
    print("\n📱 Тестирование WebApp...")
    
    # Проверяем наличие файла
    webapp_file = "webapp_real_data.html"
    if os.path.exists(webapp_file):
        print("✅ WebApp файл найден")
        
        # Проверяем содержимое файла
        with open(webapp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_elements = [
            'Telegram.WebApp',
            'generateDemoReport',
            'showReport',
            'getFullReport'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"❌ Отсутствуют элементы: {missing_elements}")
            return False
        else:
            print("✅ WebApp содержит все необходимые функции")
            return True
    else:
        print("❌ WebApp файл не найден")
        return False

def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 Запуск тестов системы Aaadviser")
    print("=" * 50)
    
    tests = [
        ("Подключение к Supabase", test_supabase_connection),
        ("Доступность данных", test_data_availability),
        ("Генерация отчетов", test_report_generation),
        ("Система баланса", test_user_balance_system),
        ("API эндпоинты", test_api_endpoints),
        ("WebApp функциональность", test_webapp_functionality)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Ошибка в тесте {test_name}: {e}")
            results[test_name] = False
    
    # Выводим итоговые результаты
    print("\n" + "=" * 50)
    print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Итого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Система готова к работе.")
    else:
        print("⚠️ Некоторые тесты не пройдены. Проверьте настройки.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 