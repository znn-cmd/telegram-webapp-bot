#!/usr/bin/env python3
"""
Скрипт для проверки таблиц в Supabase
"""

import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def check_supabase_connection():
    """Проверка подключения к Supabase"""
    print("🔍 Проверка подключения к Supabase...")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_ANON_KEY[:20]}..." if SUPABASE_ANON_KEY else "Key: НЕ НАЙДЕН")
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Ошибка: Не настроены переменные окружения")
        return False
    
    return True

def check_table_exists(table_name):
    """Проверка существования таблицы"""
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=count"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Таблица {table_name} существует")
            return True
        elif response.status_code == 404:
            print(f"❌ Таблица {table_name} НЕ существует")
            return False
        else:
            print(f"⚠️ Таблица {table_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке таблицы {table_name}: {e}")
        return False

def test_simple_insert(table_name):
    """Тест простой вставки данных"""
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    
    # Тестовые данные для short_term_rentals
    if table_name == 'short_term_rentals':
        test_data = {
            'property_id': 'test_001',
            'address': 'Test Address',
            'latitude': 36.8969,
            'longitude': 30.7133,
            'city': 'Antalya',
            'district': 'Lara',
            'property_type': 'Apartment',
            'bedrooms': 2,
            'bathrooms': 1,
            'max_guests': 4,
            'price_per_night': 100.00,
            'price_currency': 'USD',
            'source': 'test'
        }
    else:
        print(f"⚠️ Тест вставки для {table_name} не реализован")
        return False
    
    try:
        response = requests.post(url, headers=headers, json=test_data)
        if response.status_code == 201:
            print(f"✅ Тест вставки в {table_name} успешен")
            return True
        else:
            print(f"❌ Ошибка вставки в {table_name}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании {table_name}: {e}")
        return False

def check_rls_policies():
    """Проверка политик RLS"""
    print("\n🔒 Проверка политик RLS...")
    
    # Проверяем, можем ли мы читать данные
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    tables = ['short_term_rentals', 'long_term_rentals', 'property_sales', 'historical_prices', 'market_statistics']
    
    for table in tables:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=count"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                print(f"✅ RLS политика для {table} работает")
            else:
                print(f"❌ RLS политика для {table} не работает: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка проверки RLS для {table}: {e}")

def main():
    """Основная функция"""
    print("🚀 Проверка настроек Supabase...\n")
    
    # Проверка подключения
    if not check_supabase_connection():
        return
    
    # Проверка таблиц
    print("\n📋 Проверка существования таблиц...")
    tables = ['short_term_rentals', 'long_term_rentals', 'property_sales', 'historical_prices', 'market_statistics']
    
    all_tables_exist = True
    for table in tables:
        if not check_table_exists(table):
            all_tables_exist = False
    
    # Проверка RLS
    check_rls_policies()
    
    # Тест вставки
    if all_tables_exist:
        print("\n🧪 Тестирование вставки данных...")
        test_simple_insert('short_term_rentals')
    
    print("\n📝 Рекомендации:")
    if not all_tables_exist:
        print("1. Выполните SQL скрипт supabase_schema_safe.sql в Supabase Dashboard")
        print("2. Убедитесь, что все таблицы созданы в Table Editor")
    else:
        print("✅ Все таблицы существуют, можно загружать данные")

if __name__ == "__main__":
    main() 