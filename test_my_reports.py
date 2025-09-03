#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности "Мои отчеты"
"""

import requests
import json

# URL вашего приложения
BASE_URL = "http://localhost:5000"  # Измените на ваш URL

def test_user_reports():
    """Тестирует API для получения отчетов пользователя"""
    
    # Тестовые данные
    test_telegram_id = 123456789  # Замените на реальный telegram_id
    
    print("🧪 Тестирование API /api/user_reports")
    print(f"📱 Telegram ID: {test_telegram_id}")
    
    try:
        # Тест получения отчетов
        response = requests.post(
            f"{BASE_URL}/api/user_reports",
            json={"telegram_id": test_telegram_id},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            reports = data.get('reports', [])
            print(f"✅ Успешно получено отчетов: {len(reports)}")
            
            for i, report in enumerate(reports, 1):
                print(f"  📋 Отчет {i}:")
                print(f"    ID: {report.get('id')}")
                print(f"    Название: {report.get('title')}")
                print(f"    Тип: {report.get('report_type')}")
                print(f"    Адрес: {report.get('address')}")
                print(f"    Цена: {report.get('price')}")
                print(f"    Создан: {report.get('created_at')}")
                print(f"    URL: {report.get('report_url')}")
                print()
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def test_delete_report():
    """Тестирует API для удаления отчета"""
    
    test_telegram_id = 123456789  # Замените на реальный telegram_id
    test_report_id = 1  # Замените на реальный ID отчета
    
    print("\n🧪 Тестирование API /api/delete_report")
    print(f"📱 Telegram ID: {test_telegram_id}")
    print(f"🗑️ Report ID: {test_report_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/delete_report",
            json={
                "telegram_id": test_telegram_id,
                "report_id": test_report_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Отчет успешно удален")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def test_user_language():
    """Тестирует получение языка пользователя"""
    
    test_telegram_id = 123456789  # Замените на реальный telegram_id
    
    print("\n🧪 Тестирование API /api/user")
    print(f"📱 Telegram ID: {test_telegram_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/user",
            json={
                "telegram_id": test_telegram_id,
                "username": "test_user",
                "tg_name": "Test User",
                "last_name": "Test",
                "language_code": "ru"
            },
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            language = data.get('language', 'ru')
            print(f"✅ Язык пользователя: {language}")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов функциональности 'Мои отчеты'")
    print("=" * 50)
    
    test_user_language()
    test_user_reports()
    test_delete_report()
    
    print("\n✅ Тестирование завершено")
