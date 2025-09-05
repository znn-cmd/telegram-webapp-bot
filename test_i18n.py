#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API локализации
"""

import requests
import json

def test_language_api():
    """Тестирует API получения языка пользователя"""
    
    # Тестовые данные
    test_cases = [
        {
            "name": "Обычный пользователь с русским языком",
            "telegram_id": 123456789,
            "telegram_language": "ru",
            "expected_language": "ru"
        },
        {
            "name": "Обычный пользователь с английским языком",
            "telegram_id": 987654321,
            "telegram_language": "en",
            "expected_language": "en"
        },
        {
            "name": "Обычный пользователь с неподдерживаемым языком",
            "telegram_id": 555666777,
            "telegram_language": "zh",
            "expected_language": "en"
        },
        {
            "name": "Несуществующий пользователь",
            "telegram_id": 999888777,
            "telegram_language": "de",
            "expected_language": "de"
        }
    ]
    
    print("🧪 Тестирование API локализации...")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\n📋 Тест: {test_case['name']}")
        
        try:
            # Отправляем запрос к API
            response = requests.post(
                'http://localhost:5000/api/get_user_language',
                json={
                    'telegram_id': test_case['telegram_id'],
                    'telegram_language': test_case['telegram_language']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    actual_language = data.get('language')
                    is_admin = data.get('is_admin', False)
                    
                    print(f"   ✅ Успешно получен язык: {actual_language}")
                    print(f"   📊 Админ статус: {is_admin}")
                    
                    if actual_language == test_case['expected_language']:
                        print(f"   ✅ Язык соответствует ожидаемому: {test_case['expected_language']}")
                    else:
                        print(f"   ⚠️  Язык не соответствует ожидаемому. Ожидался: {test_case['expected_language']}")
                else:
                    print(f"   ❌ API вернул ошибку: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP ошибка: {response.status_code}")
                print(f"   📄 Ответ: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Не удалось подключиться к серверу. Убедитесь, что приложение запущено.")
        except requests.exceptions.Timeout:
            print("   ❌ Таймаут запроса")
        except Exception as e:
            print(f"   ❌ Неожиданная ошибка: {e}")

def test_translations_api():
    """Тестирует API получения переводов"""
    
    languages = ['ru', 'en', 'de', 'fr', 'tr']
    
    print("\n🌐 Тестирование API переводов...")
    print("=" * 50)
    
    for lang in languages:
        print(f"\n📋 Тест языка: {lang}")
        
        try:
            response = requests.post(
                'http://localhost:5000/api/translations',
                json={'language': lang},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    print(f"   ✅ Получены переводы для языка {lang}")
                    print(f"   📊 Количество ключей: {len(data)}")
                    
                    # Проверяем наличие основных ключей
                    required_keys = ['common', 'profile', 'main', 'admin']
                    missing_keys = [key for key in required_keys if key not in data]
                    
                    if missing_keys:
                        print(f"   ⚠️  Отсутствуют ключи: {missing_keys}")
                    else:
                        print(f"   ✅ Все основные ключи присутствуют")
                else:
                    print(f"   ❌ Получены некорректные данные")
            else:
                print(f"   ❌ HTTP ошибка: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Не удалось подключиться к серверу")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

def main():
    """Основная функция"""
    print("🚀 Запуск тестов локализации")
    print("=" * 50)
    
    # Тестируем API языка
    test_language_api()
    
    # Тестируем API переводов
    test_translations_api()
    
    print("\n🎉 Тестирование завершено!")
    print("\n💡 Для полного тестирования:")
    print("   1. Запустите приложение: python app.py")
    print("   2. Откройте браузер и перейдите на http://localhost:5000/webapp")
    print("   3. Проверьте переключение языков")
    print("   4. Проверьте работу для админов и обычных пользователей")

if __name__ == "__main__":
    main()
