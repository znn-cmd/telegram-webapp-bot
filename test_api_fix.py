#!/usr/bin/env python3
"""
Быстрый тест для проверки исправления API /api/user_reports
"""

import requests
import json

# URL вашего приложения
BASE_URL = "http://localhost:5000"  # Измените на ваш URL

def test_user_reports_fix():
    """Тестирует исправленный API для получения отчетов пользователя"""
    
    # Используем telegram_id из логов
    test_telegram_id = 1952374904
    
    print("🧪 Тестирование исправленного API /api/user_reports")
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
            
            if reports:
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
                print("ℹ️ У пользователя пока нет отчетов")
        else:
            print(f"❌ Ошибка: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("🚀 Тест исправления API /api/user_reports")
    print("=" * 50)
    
    test_user_reports_fix()
    
    print("\n✅ Тестирование завершено")
