#!/usr/bin/env python3
"""
Скрипт для загрузки тестовых данных в Supabase
"""

import csv
import os
import sys
from datetime import datetime
import requests
import json
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')

def check_supabase_config():
    """Проверка конфигурации Supabase"""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Ошибка: Не настроены переменные окружения Supabase")
        print("Установите переменные окружения:")
        print("export SUPABASE_URL='your_supabase_url'")
        print("export SUPABASE_ANON_KEY='your_supabase_anon_key'")
        print("\nИли создайте файл .env с содержимым:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_ANON_KEY=your_supabase_anon_key")
        sys.exit(1)

def make_supabase_request(endpoint, method='GET', data=None, upsert=False):
    """Выполнение запроса к Supabase API"""
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    if method == 'POST' and upsert:
        headers['Prefer'] = 'resolution=merge-duplicates'
    elif method == 'POST':
        headers['Prefer'] = 'return=minimal'
    
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        if response.status_code >= 400:
            print(f"\n--- Подробная ошибка Supabase ---")
            print(f"Статус: {response.status_code}")
            print(f"URL: {response.url}")
            print(f"Текст ответа: {response.text}")
            print(f"Заголовки: {dict(response.headers)}")
            if data:
                print(f"Отправленные данные: {data}")
            print("-------------------------------\n")
            return None
        
        # Для успешных запросов возвращаем True (даже если ответ пустой)
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса к Supabase: {e}")
        return None

def load_short_term_rentals():
    """Загрузка данных краткосрочной аренды"""
    print("📥 Загрузка данных краткосрочной аренды...")
    
    with open('test_data_short_term_rentals_full.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data = {
                'property_id': row['property_id'],
                'address': row['address'],
                'latitude': float(row['latitude']) if row['latitude'] else None,
                'longitude': float(row['longitude']) if row['longitude'] else None,
                'city': row['city'],
                'district': row['district'],
                'property_type': row['property_type'],
                'bedrooms': int(row['bedrooms']) if row['bedrooms'] else None,
                'bathrooms': int(row['bathrooms']) if row['bathrooms'] else None,
                'max_guests': int(row['max_guests']) if row['max_guests'] else None,
                'amenities': [a.strip() for a in row['amenities'].split(',')] if row['amenities'] else [],
                'description': row['description'] or None,
                'photos': [p.strip() for p in row['photos'].split(',')] if row['photos'] else [],
                'source': row['source'],
                'source_url': row['source_url'] or None,
                'source_id': row['source_id'] or None,
                'price_per_night': float(row['price_per_night']) if row['price_per_night'] else None,
                'price_currency': row['price_currency'],
                'availability_rate': float(row['availability_rate']) if row['availability_rate'] else None,
                'avg_rating': float(row['avg_rating']) if row['avg_rating'] else None,
                'review_count': int(row['review_count']) if row['review_count'] else None,
                'host_name': row['host_name'] or None,
                'host_rating': float(row['host_rating']) if row['host_rating'] else None,
                'host_review_count': int(row['host_review_count']) if row['host_review_count'] else None,
                'instant_bookable': True if row['instant_bookable'].lower() == 'true' else False,
                'superhost': True if row['superhost'].lower() == 'true' else False,
                'is_active': True if row['is_active'].lower() == 'true' else False
            }
            # Не отправляем поля created_at, updated_at, last_scraped_at
            # Удаляем ключи с None (кроме NOT NULL)
            data = {k: v for k, v in data.items() if v is not None or k in [
                'property_id','address','latitude','longitude','city','district','property_type','bedrooms','bathrooms','max_guests','price_per_night','price_currency','source']}
            
            result = make_supabase_request(
                'short_term_rentals',
                method='POST',
                data=data,
                upsert=True
            )
            
            if result is None:
                print(f"❌ Ошибка загрузки записи {row['property_id']}")
            else:
                print(f"✅ Загружена запись {row['property_id']}")
    
    print("✅ Данные краткосрочной аренды загружены успешно!")

def load_long_term_rentals():
    """Загрузка данных долгосрочной аренды"""
    print("📥 Загрузка данных долгосрочной аренды...")
    
    with open('test_data_long_term_rentals.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data = {
                'property_id': row['property_id'],
                'address': row['address'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'city': row['city'],
                'district': row['district'],
                'property_type': row['property_type'],
                'bedrooms': int(row['bedrooms']),
                'bathrooms': int(row['bathrooms']),
                'floor_area_sqm': float(row['floor_area_sqm']),
                'land_area_sqm': float(row['land_area_sqm']),
                'amenities': [a.strip() for a in row['amenities'].split(',')] if row['amenities'] else [],
                'description': row['description'],
                'photos': [p.strip() for p in row['photos'].split(',')] if row['photos'] else [],
                'source': row['source'],
                'source_url': row['source_url'],
                'source_id': row['source_id'],
                'monthly_rent': float(row['monthly_rent']),
                'rent_currency': row['rent_currency'],
                'deposit_amount': float(row['deposit_amount']),
                'deposit_currency': row['deposit_currency'],
                'utilities_included': row['utilities_included'] == 'true',
                'pet_friendly': row['pet_friendly'] == 'true',
                'furnished': row['furnished'] == 'true',
                'available_from': row['available_from'],
                'lease_term_months': int(row['lease_term_months']),
                'agent_name': row['agent_name'],
                'agent_rating': float(row['agent_rating']),
                'agent_review_count': int(row['agent_review_count']),
                'is_active': row['is_active'] == 'true'
            }
            
            result = make_supabase_request(
                'long_term_rentals',
                method='POST',
                data=data,
                upsert=True
            )
            
            if result is None:
                print(f"❌ Ошибка загрузки записи {row['property_id']}")
            else:
                print(f"✅ Загружена запись {row['property_id']}")
    
    print("✅ Данные долгосрочной аренды загружены успешно!")

def load_property_sales():
    """Загрузка данных продажи недвижимости"""
    print("📥 Загрузка данных продажи недвижимости...")
    
    with open('test_data_property_sales.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data = {
                'property_id': row['property_id'],
                'address': row['address'],
                'latitude': float(row['latitude']),
                'longitude': float(row['longitude']),
                'city': row['city'],
                'district': row['district'],
                'property_type': row['property_type'],
                'bedrooms': int(row['bedrooms']),
                'bathrooms': int(row['bathrooms']),
                'floor_area_sqm': float(row['floor_area_sqm']),
                'land_area_sqm': float(row['land_area_sqm']),
                'amenities': [a.strip() for a in row['amenities'].split(',')] if row['amenities'] else [],
                'description': row['description'],
                'photos': [p.strip() for p in row['photos'].split(',')] if row['photos'] else [],
                'source': row['source'],
                'source_url': row['source_url'],
                'source_id': row['source_id'],
                'asking_price': float(row['asking_price']),
                'price_currency': row['price_currency'],
                'price_per_sqm': float(row['price_per_sqm']),
                'property_age_years': int(row['property_age_years']),
                'construction_status': row['construction_status'],
                'ownership_type': row['ownership_type'],
                'agent_name': row['agent_name'],
                'agent_rating': float(row['agent_rating']),
                'agent_review_count': int(row['agent_review_count']),
                'is_active': row['is_active'] == 'true'
            }
            
            result = make_supabase_request(
                'property_sales',
                method='POST',
                data=data,
                upsert=True
            )
            
            if result is None:
                print(f"❌ Ошибка загрузки записи {row['property_id']}")
            else:
                print(f"✅ Загружена запись {row['property_id']}")
    
    print("✅ Данные продажи недвижимости загружены успешно!")

def load_historical_prices():
    """Загрузка исторических данных цен"""
    print("📥 Загрузка исторических данных цен...")
    
    with open('test_data_historical_prices.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data = {
                'property_id': row['property_id'],
                'date': row['date'],
                'price': float(row['price']),
                'price_currency': row['price_currency'],
                'price_type': row['price_type'],
                'source': row['source']
            }
            
            result = make_supabase_request(
                'historical_prices',
                method='POST',
                data=data,
                upsert=True
            )
            
            if result is None:
                print(f"❌ Ошибка загрузки записи {row['property_id']} - {row['date']}")
            else:
                print(f"✅ Загружена запись {row['property_id']} - {row['date']}")
    
    print("✅ Исторические данные цен загружены успешно!")

def load_market_statistics():
    """Загрузка рыночной статистики"""
    print("📥 Загрузка рыночной статистики...")
    
    with open('test_data_market_statistics.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            data = {
                'district': row['district'],
                'date': row['date'],
                'avg_sale_price_per_sqm': float(row['avg_sale_price_per_sqm']),
                'avg_rent_price_per_month': float(row['avg_rent_price_per_month']),
                'avg_short_term_price_per_night': float(row['avg_short_term_price_per_night']),
                'property_count': int(row['property_count']),
                'avg_property_age': float(row['avg_property_age']),
                'avg_bedrooms': float(row['avg_bedrooms']),
                'avg_bathrooms': float(row['avg_bathrooms']),
                'avg_floor_area': float(row['avg_floor_area']),
                'avg_land_area': float(row['avg_land_area']),
                'price_change_1y': float(row['price_change_1y']),
                'price_change_3y': float(row['price_change_3y']),
                'price_change_5y': float(row['price_change_5y']),
                'rent_yield_avg': float(row['rent_yield_avg']),
                'occupancy_rate_short_term': float(row['occupancy_rate_short_term']),
                'days_on_market_avg': float(row['days_on_market_avg'])
            }
            
            result = make_supabase_request(
                'market_statistics',
                method='POST',
                data=data,
                upsert=True
            )
            
            if result is None:
                print(f"❌ Ошибка загрузки записи {row['district']} - {row['date']}")
            else:
                print(f"✅ Загружена запись {row['district']} - {row['date']}")
    
    print("✅ Рыночная статистика загружена успешно!")

def get_statistics():
    """Получение статистики загруженных данных"""
    print("\n📊 Статистика загруженных данных:")
    
    tables = ['short_term_rentals', 'long_term_rentals', 'property_sales', 'historical_prices', 'market_statistics']
    
    for table in tables:
        result = make_supabase_request(f'{table}?select=count')
        if result:
            count = len(result) if isinstance(result, list) else 0
            print(f"  - {table}: {count} записей")
        else:
            print(f"  - {table}: ошибка получения данных")

def clear_supabase_tables():
    """Удаляет все записи из всех таблиц перед загрузкой данных"""
    tables = [
        'short_term_rentals',
        'long_term_rentals',
        'property_sales',
        'historical_prices',
        'market_statistics'
    ]
    print("🧹 Очищаю все таблицы...")
    for table in tables:
        result = make_supabase_request(table, method='DELETE')
        if result is not None:
            print(f"✅ Таблица {table} очищена")
        else:
            print(f"❌ Ошибка очистки таблицы {table}")


def main():
    check_supabase_config()
    clear_supabase_tables()
    print("\n🚀 Начинаем загрузку тестовых данных в Supabase...")
    load_short_term_rentals()
    load_long_term_rentals()
    load_property_sales()
    load_historical_prices()
    load_market_statistics()
    print("\n✅ Все тестовые данные успешно загружены!")
    get_statistics()

if __name__ == "__main__":
    main() 