#!/usr/bin/env python3
"""
Тестовый файл для отладки проблемы с кнопкой администратора
"""

import requests
import json

def test_admin_status():
    """Тест проверки статуса администратора"""
    url = "http://localhost:8080/api/check_admin_status"
    
    # Тестовые telegram_id (замените на реальные)
    test_ids = [
        123456789,  # Тестовый ID
        987654321,  # Другой тестовый ID
    ]
    
    for telegram_id in test_ids:
        print(f"\n🔍 Тестируем telegram_id: {telegram_id}")
        data = {
            "telegram_id": telegram_id
        }
        
        try:
            response = requests.post(url, json=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Полный ответ: {result}")
                if result.get('is_admin'):
                    print("✅ Пользователь является администратором")
                else:
                    print("❌ Пользователь НЕ является администратором")
                    print(f"💡 user_status: {result.get('user_status', 'не указан')}")
            else:
                print("❌ Ошибка запроса")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")

def test_report_generation():
    """Тест генерации отчета с кодами локаций"""
    url = "http://localhost:8080/api/generate_report"
    data = {
        "address": "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 111000,
        "lat": 36.8969,
        "lng": 30.7133,
        "language": "ru",
        "telegram_id": 123456789  # Замените на ваш telegram_id
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"\n📊 Тест генерации отчета:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            report_text = result.get('report_text', '')
            
            # Проверяем наличие кодов локаций в отчете
            if "=== КОДЫ ЛОКАЦИЙ (только для администраторов) ===" in report_text:
                print("✅ Коды локаций найдены в отчете")
                
                # Ищем строки с кодами локаций
                lines = report_text.split('\n')
                location_lines = [line for line in lines if 'ID:' in line]
                print(f"📋 Найдено строк с кодами локаций: {len(location_lines)}")
                for line in location_lines:
                    print(f"  - {line.strip()}")
            else:
                print("❌ Коды локаций НЕ найдены в отчете")
                
        else:
            print(f"❌ Ошибка: {response.json()}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🔧 Тестирование функциональности администратора")
    print("=" * 50)
    
    test_admin_status()
    test_report_generation()
    
    print("\n📝 Инструкции для отладки:")
    print("1. Замените telegram_id в test_admin_status() на ваш реальный ID")
    print("2. Запустите тест и проверьте результаты")
    print("3. Откройте консоль браузера (F12) и проверьте логи")
    print("4. Проверьте логи сервера на наличие ошибок") 