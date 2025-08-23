#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API endpoint получения средних цен
"""

import requests
import json

def test_average_prices_api():
    """Тестирует API endpoint для получения средних цен"""
    
    # URL API endpoint
    url = "http://localhost:5000/api/property_data/average_prices"
    
    # Тестовые данные локации (замените на реальные ID из вашей базы данных)
    test_data = {
        "country_id": 1,  # Türkiye
        "city_id": 1,     # Antalya
        "county_id": 1,   # Konyaaltı
        "district_id": 1  # Hurma
    }
    
    print("🧪 Тестирование API endpoint для получения средних цен")
    print(f"📍 URL: {url}")
    print(f"📍 Тестовые данные: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"📡 HTTP Status Code: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Успешный ответ:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if data.get('success'):
                print(f"💰 Средняя цена продажи: {data.get('avg_sale_price')} ₺/м²")
                print(f"💰 Средняя цена аренды: {data.get('avg_rent_price')} ₺/м²")
                print(f"📊 Метод расчета: {data.get('calculation_method', 'Не указан')}")
            else:
                print(f"❌ Ошибка: {data.get('message', 'Неизвестная ошибка')}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Детали ошибки: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"❌ Текст ошибки: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения: API сервер не запущен или недоступен")
        print("💡 Убедитесь, что api_server.py запущен на порту 5000")
    except requests.exceptions.Timeout:
        print("❌ Таймаут: API сервер не ответил в течение 30 секунд")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    test_average_prices_api()
