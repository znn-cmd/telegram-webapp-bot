#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import json
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

def test_property_trends_detailed():
    """
    Детальный тестовый скрипт для анализа таблицы property_trends
    """
    print("🔍 ДЕТАЛЬНЫЙ АНАЛИЗ ТАБЛИЦЫ property_trends")
    print("=" * 60)
    
    # Получаем данные из .env
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Ошибка: не найдены переменные окружения SUPABASE_URL или SUPABASE_ANON_KEY")
        return
    
    print(f"🔗 Подключение к: {supabase_url}")
    
    try:
        # Создаем клиент Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Подключение к Supabase успешно")
        
        # 1. Получим первые 5 записей для анализа структуры
        print("\n📋 1. СТРУКТУРА ДАННЫХ (первые 5 записей)")
        print("-" * 40)
        try:
            sample_query = supabase.table('property_trends').select('*').limit(5)
            sample_response = sample_query.execute()
            
            if sample_response.data and len(sample_response.data) > 0:
                print(f"✅ Найдено {len(sample_response.data)} записей")
                
                # Показываем все поля первой записи
                first_record = sample_response.data[0]
                print(f"\n🔍 ПОЛНАЯ СТРУКТУРА ПЕРВОЙ ЗАПИСИ:")
                print(f"  ID: {first_record.get('id')}")
                print(f"  country_id: {first_record.get('country_id')} (тип: {type(first_record.get('country_id')).__name__})")
                print(f"  city_id: {first_record.get('city_id')} (тип: {type(first_record.get('city_id')).__name__})")
                print(f"  county_id: {first_record.get('county_id')} (тип: {type(first_record.get('county_id')).__name__})")
                print(f"  district_id: {first_record.get('district_id')} (тип: {type(first_record.get('district_id')).__name__})")
                print(f"  property_year: {first_record.get('property_year')} (тип: {type(first_record.get('property_year')).__name__})")
                print(f"  property_month: {first_record.get('property_month')} (тип: {type(first_record.get('property_month')).__name__})")
                print(f"  unit_price_for_sale: {first_record.get('unit_price_for_sale')} (тип: {type(first_record.get('unit_price_for_sale')).__name__})")
                print(f"  unit_price_for_rent: {first_record.get('unit_price_for_rent')} (тип: {type(first_record.get('unit_price_for_rent')).__name__})")
                
                # Показываем все остальные поля
                print(f"\n🔍 ВСЕ ПОЛЯ ЗАПИСИ:")
                for key, value in first_record.items():
                    print(f"  {key}: {value} (тип: {type(value).__name__})")
                
            else:
                print("⚠️ Таблица пуста или не содержит данных")
        except Exception as e:
            print(f"❌ Ошибка получения образцов данных: {e}")
        
        # 2. Проверим данные для конкретной локации (из лога)
        print("\n🎯 2. ПРОВЕРКА КОНКРЕТНОЙ ЛОКАЦИИ")
        print("-" * 40)
        target_location = {
            'city_id': 7,
            'county_id': 2037,
            'district_id': 2285
        }
        
        print(f"🔍 Ищем данные для локации: {target_location}")
        
        # Проверяем пошагово БЕЗ country_id
        for level, (key, value) in enumerate(target_location.items()):
            print(f"\n  Уровень {level+1}: {key} = {value}")
            
            # Формируем запрос с накоплением фильтров
            query = supabase.table('property_trends').select('*')
            for i, (k, v) in enumerate(list(target_location.items())[:level+1]):
                query = query.eq(k, v)
            
            try:
                response = query.limit(5).execute()
                count = len(response.data) if response.data else 0
                print(f"    ✅ Найдено записей: {count}")
                
                if response.data and count > 0:
                    print(f"    📋 Пример записи:")
                    sample = response.data[0]
                    print(f"      ID: {sample.get('id')}")
                    print(f"      country_id: {sample.get('country_id')}")
                    print(f"      city_id: {sample.get('city_id')}")
                    print(f"      county_id: {sample.get('county_id')}")
                    print(f"      district_id: {sample.get('district_id')}")
                    print(f"      property_year: {sample.get('property_year')}")
                    print(f"      property_month: {sample.get('property_month')}")
                    print(f"      unit_price_for_sale: {sample.get('unit_price_for_sale')}")
            except Exception as e:
                print(f"    ❌ Ошибка запроса: {e}")
        
        # 3. Попробуем найти данные для city_id = 7
        print("\n🏙️ 3. ПОИСК ДАННЫХ ДЛЯ CITY_ID = 7")
        print("-" * 40)
        try:
            city_query = supabase.table('property_trends').select('*').eq('city_id', 7).limit(10)
            city_response = city_query.execute()
            
            if city_response.data and len(city_response.data) > 0:
                print(f"✅ Найдено {len(city_response.data)} записей для city_id=7")
                print("\n📋 Примеры записей:")
                for i, record in enumerate(city_response.data[:3]):
                    print(f"\n  Запись {i+1}:")
                    print(f"    ID: {record.get('id')}")
                    print(f"    country_id: {record.get('country_id')}")
                    print(f"    city_id: {record.get('city_id')}")
                    print(f"    county_id: {record.get('county_id')}")
                    print(f"    district_id: {record.get('district_id')}")
                    print(f"    property_year: {record.get('property_year')}")
                    print(f"    property_month: {record.get('property_month')}")
                    print(f"    unit_price_for_sale: {record.get('unit_price_for_sale')}")
            else:
                print("⚠️ Для city_id=7 данных не найдено")
        except Exception as e:
            print(f"❌ Ошибка поиска данных для city_id=7: {e}")
        
        # 4. Проверим, есть ли поле country_id вообще
        print("\n🌍 4. АНАЛИЗ ПОЛЯ COUNTRY_ID")
        print("-" * 40)
        try:
            # Ищем любые записи с непустым country_id
            country_query = supabase.table('property_trends').select('country_id').not_.is_('country_id', 'null').limit(20)
            country_response = country_query.execute()
            
            if country_response.data:
                unique_countries = list(set([r.get('country_id') for r in country_response.data if r.get('country_id') is not None]))
                print(f"🔍 Найденные country_id: {sorted(unique_countries)}")
                
                # Проверим, есть ли country_id = 1
                if 1 in unique_countries:
                    print("✅ country_id = 1 найден в таблице!")
                else:
                    print("⚠️ country_id = 1 НЕ найден в таблице")
                    
                # Проверим, есть ли country_id = None или пустые значения
                null_country_query = supabase.table('property_trends').select('country_id').is_('country_id', 'null').limit(5)
                null_country_response = null_country_query.execute()
                if null_country_response.data:
                    print(f"⚠️ Найдено {len(null_country_response.data)} записей с country_id = NULL")
            else:
                print("⚠️ Не удалось получить country_id из таблицы")
        except Exception as e:
            print(f"❌ Ошибка анализа country_id: {e}")
        
        # 5. Попробуем найти данные для county_id = 2037
        print("\n🏘️ 5. ПОИСК ДАННЫХ ДЛЯ COUNTY_ID = 2037")
        print("-" * 40)
        try:
            county_query = supabase.table('property_trends').select('*').eq('county_id', 2037).limit(5)
            county_response = county_query.execute()
            
            if county_response.data and len(county_response.data) > 0:
                print(f"✅ Найдено {len(county_response.data)} записей для county_id=2037")
                print("\n📋 Примеры записей:")
                for i, record in enumerate(county_response.data[:3]):
                    print(f"\n  Запись {i+1}:")
                    print(f"    ID: {record.get('id')}")
                    print(f"    country_id: {record.get('country_id')}")
                    print(f"    city_id: {record.get('city_id')}")
                    print(f"    county_id: {record.get('county_id')}")
                    print(f"    district_id: {record.get('district_id')}")
                    print(f"    property_year: {record.get('property_year')}")
                    print(f"    property_month: {record.get('property_month')}")
                    print(f"    unit_price_for_sale: {record.get('unit_price_for_sale')}")
            else:
                print("⚠️ Для county_id=2037 данных не найдено")
        except Exception as e:
            print(f"❌ Ошибка поиска данных для county_id=2037: {e}")
        
        # 6. Попробуем найти данные для district_id = 2285
        print("\n📍 6. ПОИСК ДАННЫХ ДЛЯ DISTRICT_ID = 2285")
        print("-" * 40)
        try:
            district_query = supabase.table('property_trends').select('*').eq('district_id', 2285).limit(5)
            district_response = district_query.execute()
            
            if district_response.data and len(district_response.data) > 0:
                print(f"✅ Найдено {len(district_response.data)} записей для district_id=2285")
                print("\n📋 Примеры записей:")
                for i, record in enumerate(district_response.data[:3]):
                    print(f"\n  Запись {i+1}:")
                    print(f"    ID: {record.get('id')}")
                    print(f"    country_id: {record.get('country_id')}")
                    print(f"    city_id: {record.get('city_id')}")
                    print(f"    county_id: {record.get('county_id')}")
                    print(f"    district_id: {record.get('district_id')}")
                    print(f"    property_year: {record.get('property_year')}")
                    print(f"    property_month: {record.get('property_month')}")
                    print(f"    unit_price_for_sale: {record.get('unit_price_for_sale')}")
            else:
                print("⚠️ Для district_id=2285 данных не найдено")
        except Exception as e:
            print(f"❌ Ошибка поиска данных для district_id=2285: {e}")
        
        # 7. Попробуем найти данные БЕЗ фильтра по country_id
        print("\n🔍 7. ПОИСК ДАННЫХ БЕЗ ФИЛЬТРА ПО COUNTRY_ID")
        print("-" * 40)
        try:
            # Ищем данные для city_id=7, county_id=2037, district_id=2285 БЕЗ country_id
            no_country_query = supabase.table('property_trends').select('*').eq('city_id', 7).eq('county_id', 2037).eq('district_id', 2285).limit(10)
            no_country_response = no_country_query.execute()
            
            if no_country_response.data and len(no_country_response.data) > 0:
                print(f"✅ Найдено {len(no_country_response.data)} записей БЕЗ фильтра по country_id!")
                print("\n📋 Примеры записей:")
                for i, record in enumerate(no_country_response.data[:3]):
                    print(f"\n  Запись {i+1}:")
                    print(f"    ID: {record.get('id')}")
                    print(f"    country_id: {record.get('country_id')}")
                    print(f"    city_id: {record.get('city_id')}")
                    print(f"    county_id: {record.get('county_id')}")
                    print(f"    district_id: {record.get('district_id')}")
                    print(f"    property_year: {record.get('property_year')}")
                    print(f"    property_month: {record.get('property_month')}")
                    print(f"    unit_price_for_sale: {record.get('unit_price_for_sale')}")
            else:
                print("⚠️ Без фильтра по country_id данных не найдено")
        except Exception as e:
            print(f"❌ Ошибка поиска данных без country_id: {e}")
        
        print("\n" + "=" * 60)
        print("🏁 ДЕТАЛЬНЫЙ АНАЛИЗ ЗАВЕРШЕН")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_property_trends_detailed()

