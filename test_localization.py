#!/usr/bin/env python3
"""
Тестовый скрипт для проверки локализации главной страницы
"""

import requests
import json
from locales import locales

def test_localization():
    """Тестирует локализацию главной страницы"""
    
    print("🧪 Тестирование локализации главной страницы...")
    
    # Проверяем, что все необходимые ключи есть в locales.py
    required_keys = [
        'main.slogan',
        'main.balance', 
        'main.title',
        'main.region_analytics',
        'main.object_evaluation',
        'main.my_reports',
        'main.profile',
        'main.help',
        'admin.title',
        'admin.user_management',
        'common.loading',
        'common.language',
        'common.confirm',
        'reports.region_analytics',
        'reports.property_evaluation',
        'reports.my_reports',
        'profile.title',
        'help.title'
    ]
    
    print("\n📋 Проверка ключей локализации:")
    
    for lang in ['ru', 'en', 'de', 'fr', 'tr']:
        print(f"\n🌐 Язык: {lang}")
        missing_keys = []
        
        for key in required_keys:
            keys = key.split('.')
            current = locales[lang]
            
            try:
                for k in keys:
                    current = current[k]
                print(f"  ✅ {key}: {current}")
            except KeyError:
                missing_keys.append(key)
                print(f"  ❌ {key}: ОТСУТСТВУЕТ")
        
        if missing_keys:
            print(f"  ⚠️  Отсутствующие ключи: {missing_keys}")
        else:
            print(f"  ✅ Все ключи присутствуют!")
    
    print("\n🔍 Проверка API endpoints:")
    
    # Тестируем API endpoint для получения переводов
    try:
        response = requests.post('http://localhost:5000/api/translations', 
                               json={'language': 'ru'}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ /api/translations работает")
            print(f"  📊 Получено {len(data)} ключей для русского языка")
        else:
            print(f"  ❌ /api/translations вернул статус {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Ошибка подключения к /api/translations: {e}")
    
    # Тестируем API endpoint для получения языка пользователя
    try:
        response = requests.post('http://localhost:5000/api/get_user_language', 
                               json={'telegram_id': 123456789, 'telegram_language': 'ru'}, 
                               timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ /api/get_user_language работает")
            print(f"  📊 Ответ: {data}")
        else:
            print(f"  ❌ /api/get_user_language вернул статус {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Ошибка подключения к /api/get_user_language: {e}")
    
    print("\n🎯 Тестирование главной страницы:")
    
    try:
        response = requests.get('http://localhost:5000/webapp_main', timeout=5)
        if response.status_code == 200:
            print("  ✅ Главная страница загружается")
            
            # Проверяем, что в HTML есть data-i18n атрибуты
            content = response.text
            i18n_attributes = content.count('data-i18n=')
            print(f"  📊 Найдено {i18n_attributes} атрибутов data-i18n")
            
            # Проверяем, что подключен i18n-manager.js
            if 'i18n-manager.js' in content:
                print("  ✅ i18n-manager.js подключен")
            else:
                print("  ❌ i18n-manager.js НЕ подключен")
                
        else:
            print(f"  ❌ Главная страница вернула статус {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Ошибка подключения к главной странице: {e}")
    
    print("\n✨ Тестирование завершено!")

if __name__ == "__main__":
    test_localization()
