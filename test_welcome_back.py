#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_welcome_back():
    """Тестируем исправление ошибки welcome_back"""
    print("🧪 Тестирование исправления ошибки welcome_back...")
    
    # Тестируем API endpoint /api/user
    url = "http://localhost:8080/api/user"
    
    # Данные для тестирования
    test_data = {
        "telegram_id": 1952374904,
        "telegram_language": "ru"
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API /api/user работает корректно!")
            print(f"📊 Ответ: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # Проверяем наличие ключа welcome
            if 'welcome' in data:
                print(f"✅ Ключ 'welcome' присутствует: {data['welcome']}")
            else:
                print("❌ Ключ 'welcome' отсутствует!")
                
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения к серверу")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_welcome_back()
