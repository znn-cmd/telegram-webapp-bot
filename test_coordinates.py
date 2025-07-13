#!/usr/bin/env python3
"""
Тестовый скрипт для проверки поиска недвижимости по координатам
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# URL API сервера
API_URL = "http://127.0.0.1:8080"

def test_coordinate_search():
    """Тестируем поиск по координатам"""
    
    # Координаты для тестирования (36.909100, 30.696700)
    test_coordinates = {
        'lat': 36.909100,
        'lng': 30.696700,
        'radius_km': 5.0,
        'property_type': 'short_term'
    }
    
    print("🔍 Тестируем поиск недвижимости по координатам...")
    print(f"Координаты: {test_coordinates['lat']}, {test_coordinates['lng']}")
    print(f"Радиус: {test_coordinates['radius_km']} км")
    print(f"Тип недвижимости: {test_coordinates['property_type']}")
    print("-" * 50)
    
    try:
        # Отправляем запрос на поиск
        response = requests.post(
            f"{API_URL}/api/search_properties",
            json=test_coordinates,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Успех: {data.get('success', False)}")
            print(f"Найдено объектов: {data.get('count', 0)}")
            
            if data.get('properties'):
                print("\n📋 Найденные объекты:")
                for i, prop in enumerate(data['properties'][:5], 1):  # Показываем первые 5
                    print(f"\n{i}. {prop.get('address', 'N/A')}")
                    print(f"   Координаты: {prop.get('latitude')}, {prop.get('longitude')}")
                    print(f"   Расстояние: {prop.get('distance_km', 'N/A')} км")
                    print(f"   Цена: €{prop.get('price', 'N/A')}")
                    print(f"   Спальни: {prop.get('bedrooms', 'N/A')}")
                    print(f"   Источник: {prop.get('source', 'N/A')}")
            else:
                print("❌ Объекты не найдены")
                
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"Ответ: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к API серверу")
        print("Убедитесь, что сервер запущен на http://localhost:8080")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_database_connection():
    """Тестируем подключение к базе данных"""
    
    print("\n🔍 Тестируем подключение к базе данных...")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Подключение к базе данных успешно")
        else:
            print("❌ Проблема с подключением к базе данных")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

def test_data_exists():
    """Проверяем наличие данных в базе"""
    
    print("\n🔍 Проверяем наличие данных в базе...")
    
    try:
        # Проверяем количество записей в таблицах
        tables = ['short_term_rentals', 'long_term_rentals', 'property_sales']
        
        for table in tables:
            response = requests.post(
                f"{API_URL}/api/search_properties",
                json={'property_type': table.replace('_', '_').replace('rentals', 'term').replace('sales', 'sale')},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"📊 {table}: {count} записей")
            else:
                print(f"❌ Ошибка при проверке {table}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов поиска по координатам")
    print("=" * 50)
    
    # Проверяем подключение к базе
    test_database_connection()
    
    # Проверяем наличие данных
    test_data_exists()
    
    # Тестируем поиск по координатам
    test_coordinate_search()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено") 