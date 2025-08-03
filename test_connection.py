#!/usr/bin/env python3
"""
Тестирование подключения к базе данных
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

print("🔧 ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ")
print("=" * 50)
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY: {'*' * 20 if supabase_key else 'НЕ НАЙДЕН'}")

if not supabase_url or not supabase_key:
    print("❌ SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
    sys.exit(1)

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Подключение к Supabase создано")
    
    # Проверяем доступ к таблице locations
    print("\n🔍 ПРОВЕРКА ДОСТУПА К ТАБЛИЦЕ LOCATIONS")
    print("-" * 40)
    
    result = supabase.table('locations').select('*').limit(1).execute()
    print(f"✅ Запрос выполнен успешно")
    print(f"📊 Результат: {len(result.data) if result.data else 0} записей")
    
    if result.data:
        print(f"📋 Первая запись: {result.data[0]}")
    else:
        print("⚠️  Данных нет")
        
    # Проверяем другие таблицы
    print("\n🔍 ПРОВЕРКА ДРУГИХ ТАБЛИЦ")
    print("-" * 30)
    
    tables_to_check = ['users', 'property_sales', 'short_term_rentals', 'long_term_rentals']
    
    for table_name in tables_to_check:
        try:
            table_result = supabase.table(table_name).select('*').limit(1).execute()
            print(f"✅ Таблица {table_name}: {len(table_result.data) if table_result.data else 0} записей")
        except Exception as e:
            print(f"❌ Таблица {table_name}: ошибка - {e}")
    
except Exception as e:
    print(f"❌ Ошибка подключения к Supabase: {e}")
    sys.exit(1) 