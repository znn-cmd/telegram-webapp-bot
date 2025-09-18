#!/usr/bin/env python3
"""
Тестовый скрипт для проверки системы управления странами
"""

import requests
import json

# Конфигурация
BASE_URL = "http://localhost:5000"  # Измените на ваш URL
ADMIN_TELEGRAM_ID = 123456789  # Замените на реальный ID администратора
USER_TELEGRAM_ID = 987654321   # Замените на реальный ID обычного пользователя

def test_countries_api(telegram_id, user_type):
    """Тестирует API получения стран для пользователя"""
    print(f"\n🔍 Тестирование API стран для {user_type} (telegram_id: {telegram_id})")
    
    url = f"{BASE_URL}/api/locations/countries"
    params = {"telegram_id": telegram_id}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('success'):
            countries = data.get('countries', [])
            is_admin = data.get('is_admin', False)
            
            print(f"✅ Успешно получено {len(countries)} стран")
            print(f"👤 Статус администратора: {is_admin}")
            print("📋 Доступные страны:")
            for country_id, country_name in countries:
                print(f"   - {country_name} (ID: {country_id})")
        else:
            print(f"❌ Ошибка: {data.get('error', 'Неизвестная ошибка')}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")

def test_admin_country_settings():
    """Тестирует API настроек стран для администратора"""
    print(f"\n🔧 Тестирование API настроек стран для администратора")
    
    # Получение настроек
    url = f"{BASE_URL}/api/admin/country_settings"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('success'):
            settings = data.get('settings', [])
            print(f"✅ Успешно получено {len(settings)} настроек стран")
            print("📋 Настройки стран:")
            for setting in settings:
                status = "✅ Включено" if setting.get('is_enabled') else "❌ Выключено"
                print(f"   - {setting.get('country_name')} (ID: {setting.get('country_id')}): {status}")
        else:
            print(f"❌ Ошибка получения настроек: {data.get('error', 'Неизвестная ошибка')}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса настроек: {e}")

def test_update_country_setting():
    """Тестирует обновление настройки страны"""
    print(f"\n🔄 Тестирование обновления настройки страны")
    
    url = f"{BASE_URL}/api/admin/country_settings"
    
    # Тестовые данные - отключаем страну с ID 1
    test_data = {
        "country_id": 1,
        "is_enabled": False
    }
    
    try:
        response = requests.post(url, json=test_data)
        data = response.json()
        
        if data.get('success'):
            print("✅ Настройка страны успешно обновлена")
        else:
            print(f"❌ Ошибка обновления: {data.get('error', 'Неизвестная ошибка')}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса обновления: {e}")

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования системы управления странами")
    print("=" * 60)
    
    # Тест 1: Получение стран для администратора
    test_countries_api(ADMIN_TELEGRAM_ID, "Администратор")
    
    # Тест 2: Получение стран для обычного пользователя
    test_countries_api(USER_TELEGRAM_ID, "Обычный пользователь")
    
    # Тест 3: Получение настроек стран для администратора
    test_admin_country_settings()
    
    # Тест 4: Обновление настройки страны
    test_update_country_setting()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено")
    print("\n📝 Инструкции:")
    print("1. Убедитесь, что сервер запущен на указанном URL")
    print("2. Замените ADMIN_TELEGRAM_ID и USER_TELEGRAM_ID на реальные ID")
    print("3. Проверьте, что таблица country_settings создана в базе данных")
    print("4. Убедитесь, что пользователь с ADMIN_TELEGRAM_ID имеет статус 'admin'")

if __name__ == "__main__":
    main()
