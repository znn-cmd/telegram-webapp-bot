#!/usr/bin/env python3
"""
Скрипт для проверки данных в таблицах рынка недвижимости
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Загружаем переменные окружения
load_dotenv()

# Инициализация Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def check_market_tables():
    """Проверяет данные в таблицах рынка недвижимости"""
    
    # Тестовые коды локаций
    location_codes = {
        'country_id': 1,
        'city_id': 7,
        'district_id': 2409,
        'county_id': 2039
    }
    
    print("🔍 ПРОВЕРКА ДАННЫХ В ТАБЛИЦАХ РЫНКА НЕДВИЖИМОСТИ")
    print("=" * 80)
    print(f"Коды локаций: {location_codes}")
    print("=" * 80)
    
    # Список таблиц для проверки
    tables = [
        'property_trends',
        'age_data', 
        'floor_segment_data',
        'general_data',
        'heating_data'
    ]
    
    for table_name in tables:
        print(f"\n📊 ТАБЛИЦА: {table_name}")
        print("-" * 40)
        
        try:
            # Проверяем структуру таблицы
            result = supabase.table(table_name).select('*').limit(1).execute()
            
            if result.data:
                print(f"✅ Таблица {table_name} существует")
                print(f"Количество записей: {len(result.data)}")
                
                # Показываем структуру первой записи
                if result.data:
                    first_record = result.data[0]
                    print(f"Поля таблицы: {list(first_record.keys())}")
                    
                    # Ищем записи с нашими кодами локаций
                    query = supabase.table(table_name).select('*')
                    if location_codes.get('country_id'):
                        query = query.eq('country_id', location_codes['country_id'])
                    if location_codes.get('city_id'):
                        query = query.eq('city_id', location_codes['city_id'])
                    if location_codes.get('district_id'):
                        query = query.eq('district_id', location_codes['district_id'])
                    if location_codes.get('county_id'):
                        query = query.eq('county_id', location_codes['county_id'])
                    
                    # Ищем за текущий год и месяц
                    from datetime import datetime
                    now = datetime.now()
                    query = query.eq('year', now.year).eq('month', now.month)
                    
                    result = query.execute()
                    
                    if result.data:
                        print(f"✅ Найдены записи для локации: {len(result.data)}")
                        for record in result.data:
                            print(f"  - ID: {record.get('id')}, Год: {record.get('year')}, Месяц: {record.get('month')}")
                    else:
                        print("❌ Записи для данной локации не найдены")
                        
                        # Проверим, есть ли вообще записи в таблице
                        all_records = supabase.table(table_name).select('*').limit(5).execute()
                        if all_records.data:
                            print("Примеры записей в таблице:")
                            for record in all_records.data:
                                print(f"  - ID: {record.get('id')}, Country: {record.get('country_id')}, City: {record.get('city_id')}, District: {record.get('district_id')}, County: {record.get('county_id')}, Year: {record.get('year')}, Month: {record.get('month')}")
                        else:
                            print("❌ Таблица пуста")
            else:
                print(f"❌ Таблица {table_name} не существует или пуста")
                
        except Exception as e:
            print(f"❌ Ошибка при проверке таблицы {table_name}: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    check_market_tables() 