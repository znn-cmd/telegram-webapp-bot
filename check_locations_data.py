#!/usr/bin/env python3
"""
Проверка данных в таблице locations с правильной структурой
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

def check_locations_data():
    """
    Проверяет данные в таблице locations
    """
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Подключение к Supabase создано")
        
        # Проверяем данные в таблице locations
        print("\n🔍 ПРОВЕРКА ДАННЫХ В ТАБЛИЦЕ LOCATIONS")
        print("=" * 50)
        
        try:
            # Получаем все записи
            result = supabase.table('locations').select('*').execute()
            print(f"📊 Всего записей: {len(result.data) if result.data else 0}")
            
            if result.data:
                print(f"\n📋 ПЕРВЫЕ 5 ЗАПИСЕЙ:")
                print("-" * 60)
                
                for i, record in enumerate(result.data[:5]):
                    print(f"Запись {i+1}:")
                    print(f"  id: {record.get('id')}")
                    print(f"  city_id: {record.get('city_id')}")
                    print(f"  county_id: {record.get('county_id')}")
                    print(f"  district_id: {record.get('district_id')}")
                    print(f"  country_id: {record.get('country_id')}")
                    print(f"  country_name: {record.get('country_name')}")
                    print(f"  city_name: {record.get('city_name')}")
                    print(f"  county_name: {record.get('county_name')}")
                    print(f"  district_name: {record.get('district_name')}")
                    print()
                
                # Анализируем уникальные значения
                print(f"\n📊 АНАЛИЗ УНИКАЛЬНЫХ ЗНАЧЕНИЙ:")
                print("-" * 40)
                
                city_names = set()
                county_names = set()
                district_names = set()
                country_names = set()
                
                for record in result.data:
                    if record.get('city_name'):
                        city_names.add(record.get('city_name'))
                    if record.get('county_name'):
                        county_names.add(record.get('county_name'))
                    if record.get('district_name'):
                        district_names.add(record.get('district_name'))
                    if record.get('country_name'):
                        country_names.add(record.get('country_name'))
                
                print(f"Уникальные страны: {sorted(country_names)}")
                print(f"Уникальные города: {sorted(list(city_names)[:10])}")
                print(f"Уникальные округа: {sorted(list(county_names)[:10])}")
                print(f"Уникальные районы (первые 10): {sorted(list(district_names)[:10])}")
                
                # Ищем записи с "Avsallar" или "Alanya"
                print(f"\n🔍 ПОИСК ЗАПИСЕЙ С 'AVSALLAR' ИЛИ 'ALANYA':")
                print("-" * 50)
                
                avsallar_found = False
                alanya_found = False
                
                for record in result.data:
                    district = record.get('district_name', '').lower()
                    county = record.get('county_name', '').lower()
                    city = record.get('city_name', '').lower()
                    
                    if 'avsallar' in district or 'avsallar' in county or 'avsallar' in city:
                        print(f"✅ Найдено совпадение с Avsallar: {record}")
                        avsallar_found = True
                    elif 'alanya' in district or 'alanya' in county or 'alanya' in city:
                        print(f"✅ Найдено совпадение с Alanya: {record}")
                        alanya_found = True
                
                if not avsallar_found:
                    print("❌ Записей с 'Avsallar' не найдено")
                if not alanya_found:
                    print("❌ Записей с 'Alanya' не найдено")
                    
            else:
                print("⚠️  Таблица locations пуста")
                
        except Exception as e:
            print(f"❌ Ошибка при проверке таблицы locations: {e}")
    
    except Exception as e:
        print(f"❌ Ошибка подключения к Supabase: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_locations_data() 