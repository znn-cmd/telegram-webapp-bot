#!/usr/bin/env python3
"""
Тест генерации отчета для администратора
"""

import requests
import json

def test_report_generation_with_admin():
    """Тест генерации отчета с администратором"""
    url = "http://localhost:8080/api/generate_report"
    
    # Данные для теста (замените на реальные)
    data = {
        "address": "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Türkiye",
        "bedrooms": 3,
        "price": 111000,
        "lat": 36.8969,
        "lng": 30.7133,
        "language": "ru",
        "telegram_id": 1952374904  # Ваш telegram_id
    }
    
    try:
        print(f"🔍 Тестируем генерацию отчета для админа")
        print(f"📋 Данные запроса: {data}")
        
        response = requests.post(url, json=data)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            report_text = result.get('report_text', '')
            
            print(f"✅ Отчет сгенерирован успешно")
            print(f"📊 Размер отчета: {len(report_text)} символов")
            
            # Проверяем наличие кодов локаций в отчете
            if "=== КОДЫ ЛОКАЦИЙ (только для администраторов) ===" in report_text:
                print("✅ Коды локаций найдены в отчете")
                
                # Ищем строки с кодами локаций
                lines = report_text.split('\n')
                location_lines = [line for line in lines if 'ID:' in line]
                print(f"📋 Найдено строк с кодами локаций: {len(location_lines)}")
                for line in location_lines:
                    print(f"  - {line.strip()}")
                    
                # Проверяем, что есть реальные коды, а не заглушка
                if "Локация не найдена в базе данных" not in report_text:
                    print("✅ Реальные коды локаций присутствуют")
                else:
                    print("❌ Только заглушка кодов локаций")
            else:
                print("❌ Коды локаций НЕ найдены в отчете")
                
            # Показываем первые 500 символов отчета для отладки
            print(f"\n📄 Начало отчета:")
            print(report_text[:500])
            print("...")
                
        else:
            print(f"❌ Ошибка: {response.json()}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_admin_status_specific():
    """Тест статуса администратора для конкретного ID"""
    url = "http://localhost:8080/api/check_admin_status"
    data = {"telegram_id": 1952374904}
    
    try:
        print(f"\n🔍 Тестируем статус админа для telegram_id: 1952374904")
        
        response = requests.post(url, json=data)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Полный ответ: {result}")
            
            if result.get('is_admin'):
                print("✅ Пользователь является администратором")
            else:
                print("❌ Пользователь НЕ является администратором")
                print(f"💡 user_status: {result.get('user_status', 'не указан')}")
        else:
            print(f"❌ Ошибка: {response.json()}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🔧 Тестирование генерации отчета для администратора")
    print("=" * 60)
    
    test_admin_status_specific()
    test_report_generation_with_admin()
    
    print("\n📝 Инструкции:")
    print("1. Проверьте логи сервера на наличие сообщений с эмодзи")
    print("2. Убедитесь, что коды локаций присутствуют в отчете")
    print("3. Проверьте в браузере, отображается ли кнопка") 