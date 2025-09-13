#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обновленной системы регистрации пользователей
"""

import requests
import json
from datetime import datetime, timedelta

# URL вашего приложения (замените на актуальный)
BASE_URL = "http://localhost:5000"  # или ваш URL

def test_user_registration():
    """Тестирует регистрацию нового пользователя"""
    print("🧪 Тестирование регистрации нового пользователя...")
    
    # Тестовые данные
    test_data = {
        "telegram_id": 999999999,  # Используйте уникальный ID для теста
        "username": "test_user",
        "tg_name": "Тестовый",
        "last_name": "Пользователь",
        "language_code": "ru"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/user", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Регистрация успешна!")
            print(f"   - Новый пользователь: {result.get('is_new_user')}")
            print(f"   - Язык: {result.get('language')}")
            print(f"   - Период начала: {result.get('period_start')}")
            print(f"   - Период окончания: {result.get('period_end')}")
            print(f"   - Полное имя: {result.get('full_name')}")
            print(f"   - Код приглашения: {result.get('invite_code')}")
            return result.get('telegram_id')
        else:
            print(f"❌ Ошибка регистрации: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return None

def test_user_login(telegram_id):
    """Тестирует вход существующего пользователя"""
    print(f"\n🧪 Тестирование входа пользователя {telegram_id}...")
    
    test_data = {
        "telegram_id": telegram_id,
        "username": "test_user",
        "tg_name": "Тестовый",
        "last_name": "Пользователь",
        "language_code": "ru"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/user", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Вход успешен!")
            print(f"   - Существующий пользователь: {not result.get('is_new_user')}")
            print(f"   - Язык: {result.get('language')}")
            print(f"   - Последняя активность: {result.get('last_activity')}")
            print(f"   - Период окончания: {result.get('period_end')}")
            return True
        else:
            print(f"❌ Ошибка входа: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def test_trial_status(telegram_id):
    """Тестирует проверку статуса пробного периода"""
    print(f"\n🧪 Тестирование статуса пробного периода для пользователя {telegram_id}...")
    
    test_data = {
        "telegram_id": telegram_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/user/trial_status", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                trial_status = result.get('trial_status')
                print("✅ Статус пробного периода получен!")
                print(f"   - Статус: {trial_status.get('status')}")
                print(f"   - Сообщение: {trial_status.get('message')}")
                if 'days_left' in trial_status:
                    print(f"   - Дней осталось: {trial_status.get('days_left')}")
                if 'days_expired' in trial_status:
                    print(f"   - Дней истекло: {trial_status.get('days_expired')}")
                return True
            else:
                print(f"❌ Ошибка получения статуса: {result.get('error')}")
                return False
        else:
            print(f"❌ Ошибка запроса: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования системы регистрации пользователей")
    print("=" * 60)
    
    # Тест 1: Регистрация нового пользователя
    telegram_id = test_user_registration()
    
    if telegram_id:
        # Тест 2: Вход существующего пользователя
        test_user_login(telegram_id)
        
        # Тест 3: Проверка статуса пробного периода
        test_trial_status(telegram_id)
    
    print("\n" + "=" * 60)
    print("🏁 Тестирование завершено")
    
    print("\n📝 Инструкции по использованию:")
    print("1. Убедитесь, что ваше приложение запущено")
    print("2. Измените BASE_URL на актуальный адрес вашего приложения")
    print("3. Используйте уникальный telegram_id для каждого теста")
    print("4. Проверьте логи приложения для детальной информации")

if __name__ == "__main__":
    main()
