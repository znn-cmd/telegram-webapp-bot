#!/usr/bin/env python3
"""
Детальная отладка таблицы locations
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

supabase: Client = create_client(supabase_url, supabase_key)

def debug_locations_table():
    """
    Детальная отладка таблицы locations
    """
    print("🔍 ДЕТАЛЬНАЯ ОТЛАДКА ТАБЛИЦЫ LOCATIONS")
    print("=" * 60)
    
    try:
        # Получаем все записи из таблицы locations
        result = supabase.table('locations').select('*').execute()
        
        if result.data:
            print(f"✅ Таблица locations найдена, записей: {len(result.data)}")
            print(f"\n📋 СТРУКТУРА ДАННЫХ:")
            print("-" * 40)
            
            for i, record in enumerate(result.data):
                print(f"Запись {i+1}:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
                print()
        else:
            print("⚠️  Таблица locations пуста")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке таблицы locations: {e}")

def test_specific_search():
    """
    Тестирует поиск конкретных значений
    """
    print("\n🎯 ТЕСТ ПОИСКА КОНКРЕТНЫХ ЗНАЧЕНИЙ")
    print("=" * 50)
    
    # Тестовые значения
    test_values = [
        {'city_name': 'Antalya', 'district_name': 'Avsallar', 'county_name': 'Alanya'},
        {'city_name': 'Alanya', 'district_name': 'Avsallar', 'county_name': 'Antalya'},
        {'city_name': 'Antalya', 'district_name': None, 'county_name': None},
        {'city_name': None, 'district_name': 'Avsallar', 'county_name': None},
        {'city_name': None, 'district_name': None, 'county_name': 'Alanya'},
    ]
    
    for i, test_case in enumerate(test_values):
        print(f"\n🔍 Тест {i+1}: {test_case}")
        
        try:
            query = supabase.table('locations').select('*')
            
            if test_case['city_name']:
                query = query.eq('city_name', test_case['city_name'])
            if test_case['district_name']:
                query = query.eq('district_name', test_case['district_name'])
            if test_case['county_name']:
                query = query.eq('county_name', test_case['county_name'])
                
            result = query.execute()
            
            if result.data:
                print(f"  ✅ Найдено записей: {len(result.data)}")
                for j, record in enumerate(result.data):
                    print(f"    Запись {j+1}: {record}")
            else:
                print(f"  ❌ Записи не найдены")
                
        except Exception as e:
            print(f"  ❌ Ошибка поиска: {e}")

def test_partial_search():
    """
    Тестирует частичный поиск
    """
    print("\n🔍 ТЕСТ ЧАСТИЧНОГО ПОИСКА")
    print("=" * 40)
    
    search_terms = ['Antalya', 'Alanya', 'Avsallar', 'Istanbul', 'Ankara']
    
    for term in search_terms:
        print(f"\n🔍 Поиск по термину: '{term}'")
        
        try:
            # Поиск по city_name
            city_result = supabase.table('locations').select('*').eq('city_name', term).execute()
            if city_result.data:
                print(f"  ✅ Найдено в city_name: {len(city_result.data)} записей")
                for record in city_result.data:
                    print(f"    {record}")
            
            # Поиск по district_name
            district_result = supabase.table('locations').select('*').eq('district_name', term).execute()
            if district_result.data:
                print(f"  ✅ Найдено в district_name: {len(district_result.data)} записей")
                for record in district_result.data:
                    print(f"    {record}")
            
            # Поиск по county_name
            county_result = supabase.table('locations').select('*').eq('county_name', term).execute()
            if county_result.data:
                print(f"  ✅ Найдено в county_name: {len(county_result.data)} записей")
                for record in county_result.data:
                    print(f"    {record}")
                    
        except Exception as e:
            print(f"  ❌ Ошибка поиска: {e}")

def test_like_search():
    """
    Тестирует поиск с LIKE (частичное совпадение)
    """
    print("\n🔍 ТЕСТ ПОИСКА С LIKE")
    print("=" * 40)
    
    search_terms = ['Antalya', 'Alanya', 'Avsallar']
    
    for term in search_terms:
        print(f"\n🔍 Поиск LIKE по термину: '{term}'")
        
        try:
            # Поиск с LIKE по всем полям
            result = supabase.table('locations').select('*').or_(f'city_name.ilike.%{term}%,district_name.ilike.%{term}%,county_name.ilike.%{term}%').execute()
            
            if result.data:
                print(f"  ✅ Найдено записей: {len(result.data)}")
                for record in result.data:
                    print(f"    {record}")
            else:
                print(f"  ❌ Записи не найдены")
                
        except Exception as e:
            print(f"  ❌ Ошибка поиска: {e}")

if __name__ == "__main__":
    debug_locations_table()
    test_specific_search()
    test_partial_search()
    test_like_search() 