#!/usr/bin/env python3
"""
Скрипт для анализа проблемы с фильтрацией городов в таблице locations
"""

import os
import sys
from supabase import create_client, Client

# Инициализация Supabase
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

if not url or not key:
    print('❌ SUPABASE_URL или SUPABASE_KEY не установлены')
    sys.exit(1)

supabase: Client = create_client(url, key)

def analyze_locations_data():
    """Анализирует данные таблицы locations"""
    print("🔍 АНАЛИЗ ТАБЛИЦЫ LOCATIONS")
    print("=" * 50)
    
    try:
        # Получаем все записи
        result = supabase.table('locations').select('*').execute()
        total_records = len(result.data) if result.data else 0
        print(f"📊 Общее количество записей: {total_records}")
        
        if not result.data:
            print("❌ Данные не найдены")
            return
        
        # Анализируем уникальные города
        print("\n🏙️ АНАЛИЗ УНИКАЛЬНЫХ ГОРОДОВ:")
        print("-" * 40)
        
        cities_data = {}
        cities_with_null = []
        
        for record in result.data:
            city_id = record.get('city_id')
            city_name = record.get('city_name')
            country_id = record.get('country_id')
            
            if city_id is not None:
                if city_name is None:
                    cities_with_null.append({
                        'city_id': city_id,
                        'country_id': country_id,
                        'record_id': record.get('id')
                    })
                else:
                    if city_id not in cities_data:
                        cities_data[city_id] = {
                            'name': city_name,
                            'country_id': country_id,
                            'count': 0
                        }
                    cities_data[city_id]['count'] += 1
        
        print(f"📊 Уникальных city_id: {len(cities_data)}")
        print(f"⚠️ Записей с city_name = null: {len(cities_with_null)}")
        
        # Показываем города с null значениями
        if cities_with_null:
            print(f"\n❌ ГОРОДА С NULL ЗНАЧЕНИЯМИ (первые 10):")
            print("-" * 50)
            for i, city in enumerate(cities_with_null[:10]):
                print(f"  {i+1}. city_id: {city['city_id']}, country_id: {city['country_id']}, record_id: {city['record_id']}")
        
        # Показываем уникальные города
        print(f"\n✅ УНИКАЛЬНЫЕ ГОРОДА (первые 15):")
        print("-" * 40)
        sorted_cities = sorted(cities_data.items(), key=lambda x: x[1]['name'])
        for i, (city_id, city_info) in enumerate(sorted_cities[:15]):
            print(f"  {i+1}. city_id: {city_id}, name: '{city_info['name']}', count: {city_info['count']}")
        
        # Анализируем по country_id = 1 (Türkiye)
        print(f"\n🇹🇷 АНАЛИЗ ДЛЯ TÜRKIYE (country_id = 1):")
        print("-" * 40)
        
        turkey_cities = {}
        turkey_null_cities = []
        
        for record in result.data:
            if record.get('country_id') == 1:
                city_id = record.get('city_id')
                city_name = record.get('city_name')
                
                if city_id is not None:
                    if city_name is None:
                        turkey_null_cities.append({
                            'city_id': city_id,
                            'record_id': record.get('id')
                        })
                    else:
                        if city_id not in turkey_cities:
                            turkey_cities[city_id] = {
                                'name': city_name,
                                'count': 0
                            }
                        turkey_cities[city_id]['count'] += 1
        
        print(f"📊 Уникальных городов в Турции: {len(turkey_cities)}")
        print(f"⚠️ Записей с city_name = null в Турции: {len(turkey_null_cities)}")
        
        if turkey_null_cities:
            print(f"\n❌ ГОРОДА ТУРЦИИ С NULL ЗНАЧЕНИЯМИ:")
            print("-" * 40)
            for i, city in enumerate(turkey_null_cities):
                print(f"  {i+1}. city_id: {city['city_id']}, record_id: {city['record_id']}")
        
        print(f"\n✅ ГОРОДА ТУРЦИИ:")
        print("-" * 30)
        sorted_turkey_cities = sorted(turkey_cities.items(), key=lambda x: x[1]['name'])
        for i, (city_id, city_info) in enumerate(sorted_turkey_cities):
            print(f"  {i+1}. city_id: {city_id}, name: '{city_info['name']}', count: {city_info['count']}")
        
        # Проверяем, что происходит при запросе как в API
        print(f"\n🔍 ТЕСТИРОВАНИЕ API ЗАПРОСА:")
        print("-" * 40)
        
        api_result = supabase.table('locations').select('city_id, city_name').eq('country_id', 1).execute()
        api_records = len(api_result.data) if api_result.data else 0
        print(f"📊 API запрос вернул записей: {api_records}")
        
        # Симулируем фильтрацию как в коде
        filtered_cities = []
        seen = set()
        null_count = 0
        
        for item in api_result.data:
            if item['city_id'] is not None and item['city_name'] is not None:
                city_tuple = (item['city_id'], item['city_name'])
                if city_tuple not in seen:
                    filtered_cities.append(city_tuple)
                    seen.add(city_tuple)
            else:
                null_count += 1
        
        print(f"✅ После фильтрации городов: {len(filtered_cities)}")
        print(f"⚠️ Отфильтровано записей с null: {null_count}")
        
        print(f"\n📋 ОТФИЛЬТРОВАННЫЕ ГОРОДА:")
        print("-" * 30)
        for i, (city_id, city_name) in enumerate(filtered_cities):
            print(f"  {i+1}. city_id: {city_id}, name: '{city_name}'")
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")

if __name__ == "__main__":
    analyze_locations_data()
