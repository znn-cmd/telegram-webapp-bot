import requests
import json

# URL вашего сервера
BASE_URL = "http://localhost:8080"

def test_market_analysis():
    """Тест функции анализа рынка"""
    print("Тестирование функции анализа рынка...")
    
    # Тестовые данные
    test_data = {
        "lat": 36.8969,
        "lng": 30.7133,
        "bedrooms": 2,
        "target_price": 500000
    }
    
    try:
        # Создаем отчет
        response = requests.post(f"{BASE_URL}/api/generate_report", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Отчет успешно создан!")
            print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

def test_search_properties():
    """Тест функции поиска недвижимости"""
    print("\nТестирование функции поиска недвижимости...")
    
    # Тестовые данные
    test_data = {
        "lat": 36.8969,
        "lng": 30.7133,
        "radius_km": 5.0,
        "property_type": "short_term"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/search_properties", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Поиск недвижимости успешен!")
            print(f"Найдено объектов: {result.get('count', 0)}")
            if result.get('properties'):
                print(f"Первый объект: {result['properties'][0].get('address', 'N/A')}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

def test_market_statistics():
    """Тест функции статистики рынка"""
    print("\nТестирование функции статистики рынка...")
    
    # Тестовые данные
    test_data = {
        "district": "Konyaalti",
        "city": "Antalya"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/market_statistics", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Статистика рынка получена!")
            print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    print("🧪 Тестирование функций WebApp...")
    print("=" * 50)
    
    test_market_analysis()
    test_search_properties()
    test_market_statistics()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено!") 