#!/usr/bin/env python3
"""
Скрипт для добавления тестовых отчетов в базу данных
"""

import requests
import json
from datetime import datetime

# URL вашего приложения
BASE_URL = "http://localhost:5000"  # Измените на ваш URL

def add_test_reports():
    """Добавляет тестовые отчеты для пользователя"""
    
    # Используем telegram_id из логов
    test_telegram_id = 1952374904
    
    print("🧪 Добавление тестовых отчетов")
    print(f"📱 Telegram ID: {test_telegram_id}")
    
    # Тестовые отчеты
    test_reports = [
        {
            "title": "Анализ квартиры в центре",
            "report_type": "property_analysis",
            "description": "Детальный анализ квартиры в центре города",
            "address": "ул. Ленина, 15, Москва",
            "price": 8500000,
            "area": 75.5,
            "bedrooms": 2,
            "report_url": "https://example.com/report1.html"
        },
        {
            "title": "Оценка дома в пригороде",
            "report_type": "property_evaluation",
            "description": "Оценка загородного дома",
            "address": "Подмосковье, д. Иваново, ул. Садовая, 8",
            "price": 25000000,
            "area": 150.0,
            "bedrooms": 4,
            "report_url": "https://example.com/report2.html"
        },
        {
            "title": "Рыночный анализ района",
            "report_type": "market_analysis",
            "description": "Анализ рынка недвижимости в районе",
            "address": "Центральный район, Москва",
            "price": None,
            "area": None,
            "bedrooms": None,
            "report_url": "https://example.com/report3.html"
        }
    ]
    
    try:
        # Сначала получаем user_id
        user_response = requests.post(
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
        
        if user_response.status_code != 200:
            print(f"❌ Ошибка получения пользователя: {user_response.text}")
            return
            
        user_data = user_response.json()
        print(f"✅ Пользователь найден: {user_data.get('tg_name')}")
        
        # Добавляем тестовые отчеты
        for i, report_data in enumerate(test_reports, 1):
            print(f"\n📋 Добавление отчета {i}...")
            
            # Здесь нужно использовать API для сохранения отчета
            # Поскольку у нас нет прямого API для добавления отчетов,
            # мы можем использовать существующий endpoint или создать новый
            
            # Для демонстрации просто выводим данные
            print(f"  Название: {report_data['title']}")
            print(f"  Тип: {report_data['report_type']}")
            print(f"  Адрес: {report_data['address']}")
            print(f"  Цена: {report_data['price']}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def check_existing_reports():
    """Проверяет существующие отчеты"""
    
    test_telegram_id = 1952374904
    
    print("\n🔍 Проверка существующих отчетов")
    print(f"📱 Telegram ID: {test_telegram_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/user_reports",
            json={"telegram_id": test_telegram_id},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            reports = data.get('reports', [])
            print(f"✅ Найдено отчетов: {len(reports)}")
            
            if reports:
                for i, report in enumerate(reports, 1):
                    print(f"  📋 Отчет {i}:")
                    print(f"    ID: {report.get('id')}")
                    print(f"    Название: {report.get('title')}")
                    print(f"    Тип: {report.get('report_type')}")
                    print(f"    Адрес: {report.get('address')}")
                    print()
            else:
                print("ℹ️ Отчетов пока нет")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("🚀 Скрипт для работы с тестовыми отчетами")
    print("=" * 50)
    
    check_existing_reports()
    # add_test_reports()  # Раскомментируйте для добавления тестовых данных
    
    print("\n✅ Работа завершена")
