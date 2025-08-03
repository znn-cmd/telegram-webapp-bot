#!/usr/bin/env python3
"""
Проверка реальных данных в таблице locations
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

def check_real_data():
    """
    Проверяет реальные данные в таблице locations
    """
    print("🔍 ПРОВЕРКА РЕАЛЬНЫХ ДАННЫХ В ТАБЛИЦЕ LOCATIONS")
    print("=" * 60)
    
    try:
        # Получаем все записи из таблицы locations
        result = supabase.table('locations').select('*').execute()
        
        if result.data:
            print(f"✅ Таблица locations найдена, записей: {len(result.data)}")
            
            # Показываем первые 10 записей
            print(f"\n📋 ПЕРВЫЕ 10 ЗАПИСЕЙ:")
            print("-" * 60)
            
            for i, record in enumerate(result.data[:10]):
                print(f"Запись {i+1}:")
                print(f"  district_name: {record.get('district_name')}")
                print(f"  county_name: {record.get('county_name')}")
                print(f"  city_name: {record.get('city_name')}")
                print(f"  created_at: {record.get('created_at')}")
                print()
            
            # Анализируем уникальные значения
            print(f"\n📊 АНАЛИЗ УНИКАЛЬНЫХ ЗНАЧЕНИЙ:")
            print("-" * 40)
            
            city_names = set()
            county_names = set()
            district_names = set()
            
            for record in result.data:
                city_names.add(record.get('city_name'))
                county_names.add(record.get('county_name'))
                district_names.add(record.get('district_name'))
            
            print(f"Уникальные города: {sorted(city_names)}")
            print(f"Уникальные округа: {sorted(county_names)}")
            print(f"Уникальные районы (первые 10): {sorted(list(district_names)[:10])}")
            
            # Ищем записи с "Avsallar" или похожими названиями
            print(f"\n🔍 ПОИСК ЗАПИСЕЙ С 'AVSALLAR' ИЛИ ПОХОЖИМИ:")
            print("-" * 40)
            
            for record in result.data:
                district = record.get('district_name', '').lower()
                county = record.get('county_name', '').lower()
                city = record.get('city_name', '').lower()
                
                if 'avsallar' in district or 'avsallar' in county or 'avsallar' in city:
                    print(f"Найдено совпадение: {record}")
                elif 'alanya' in district or 'alanya' in county or 'alanya' in city:
                    print(f"Найдено совпадение с Alanya: {record}")
                    
        else:
            print("⚠️  Таблица locations пуста")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке таблицы locations: {e}")

def test_search_with_real_data():
    """
    Тестирует поиск с реальными данными из таблицы
    """
    print(f"\n🎯 ТЕСТ ПОИСКА С РЕАЛЬНЫМИ ДАННЫМИ")
    print("=" * 50)
    
    try:
        # Получаем несколько реальных записей
        result = supabase.table('locations').select('*').limit(5).execute()
        
        if result.data:
            for i, record in enumerate(result.data):
                print(f"\n🔍 Тест {i+1} с реальными данными:")
                print(f"  district_name: '{record.get('district_name')}'")
                print(f"  county_name: '{record.get('county_name')}'")
                print(f"  city_name: '{record.get('city_name')}'")
                
                # Ищем эту запись
                query = supabase.table('locations').select('*')
                
                if record.get('district_name'):
                    query = query.eq('district_name', record.get('district_name'))
                if record.get('county_name'):
                    query = query.eq('county_name', record.get('county_name'))
                if record.get('city_name'):
                    query = query.eq('city_name', record.get('city_name'))
                    
                search_result = query.execute()
                
                if search_result.data:
                    print(f"  ✅ Найдено записей: {len(search_result.data)}")
                    for found_record in search_result.data:
                        print(f"    Найдена запись: {found_record}")
                else:
                    print(f"  ❌ Записи не найдены")
                    
        else:
            print("❌ Нет данных для тестирования")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

if __name__ == "__main__":
    check_real_data()
    test_search_with_real_data() 