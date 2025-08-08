#!/usr/bin/env python3
"""
Проверка структуры таблицы locations
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Загружаем переменные окружения
load_dotenv()

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
    sys.exit(1)

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Подключение к Supabase создано")
    
    # Попробуем получить все записи без лимита
    print("\n🔍 ПОПЫТКА ПОЛУЧИТЬ ВСЕ ЗАПИСИ ИЗ LOCATIONS")
    print("-" * 50)
    
    try:
        result = supabase.table('locations').select('*').execute()
        print(f"📊 Всего записей: {len(result.data) if result.data else 0}")
        
        if result.data:
            print(f"📋 Первые 3 записи:")
            for i, record in enumerate(result.data[:3]):
                print(f"  Запись {i+1}: {record}")
        else:
            print("⚠️  Данных нет")
            
    except Exception as e:
        print(f"❌ Ошибка при получении всех записей: {e}")
    
    # Попробуем получить только определенные поля
    print("\n🔍 ПОПЫТКА ПОЛУЧИТЬ ОПРЕДЕЛЕННЫЕ ПОЛЯ")
    print("-" * 40)
    
    try:
        result = supabase.table('locations').select('district_name, county_name, city_name').execute()
        print(f"📊 Записей с выбранными полями: {len(result.data) if result.data else 0}")
        
        if result.data:
            print(f"📋 Первые 3 записи:")
            for i, record in enumerate(result.data[:3]):
                print(f"  Запись {i+1}: {record}")
        else:
            print("⚠️  Данных нет")
            
    except Exception as e:
        print(f"❌ Ошибка при получении выбранных полей: {e}")
    
    # Попробуем получить только одну запись
    print("\n🔍 ПОПЫТКА ПОЛУЧИТЬ ОДНУ ЗАПИСЬ")
    print("-" * 35)
    
    try:
        result = supabase.table('locations').select('*').limit(1).execute()
        print(f"📊 Записей (лимит 1): {len(result.data) if result.data else 0}")
        
        if result.data:
            print(f"📋 Запись: {result.data[0]}")
        else:
            print("⚠️  Данных нет")
            
    except Exception as e:
        print(f"❌ Ошибка при получении одной записи: {e}")
    
    # Попробуем поиск по конкретному значению
    print("\n🔍 ПОПЫТКА ПОИСКА ПО ЗНАЧЕНИЮ")
    print("-" * 35)
    
    try:
        # Ищем запись с "Antalya"
        result = supabase.table('locations').select('*').eq('city_name', 'Antalya').execute()
        print(f"📊 Записей с city_name='Antalya': {len(result.data) if result.data else 0}")
        
        if result.data:
            print(f"📋 Первые 3 записи:")
            for i, record in enumerate(result.data[:3]):
                print(f"  Запись {i+1}: {record}")
        else:
            print("⚠️  Записей с 'Antalya' не найдено")
            
    except Exception as e:
        print(f"❌ Ошибка при поиске: {e}")
    
    # Проверим, есть ли другие таблицы с похожими названиями
    print("\n🔍 ПРОВЕРКА ДРУГИХ ТАБЛИЦ")
    print("-" * 30)
    
    other_tables = ['location', 'location_codes', 'cities', 'districts']
    
    for table_name in other_tables:
        try:
            result = supabase.table(table_name).select('*').limit(1).execute()
            print(f"✅ Таблица {table_name}: {len(result.data) if result.data else 0} записей")
        except Exception as e:
            print(f"❌ Таблица {table_name}: ошибка - {e}")
    
except Exception as e:
    print(f"❌ Ошибка подключения к Supabase: {e}")
    sys.exit(1) 