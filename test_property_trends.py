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

def test_property_trends():
    """
    Тестовый скрипт для проверки содержимого таблицы property_trends
    """
    print("🔍 ТЕСТИРОВАНИЕ ТАБЛИЦЫ property_trends")
    print("=" * 50)
    
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
        
        # 1. Проверим общее количество записей
        print("\n📊 1. ОБЩЕЕ КОЛИЧЕСТВО ЗАПИСЕЙ")
        print("-" * 30)
        try:
            total_count_query = supabase.table('property_trends').select('id', count='exact')
            total_count_response = total_count_query.execute()
            total_count = total_count_response.count if hasattr(total_count_response, 'count') else 'неизвестно'
            print(f"🔍 Общее количество записей в таблице property_trends: {total_count}")
        except Exception as e:
            print(f"❌ Ошибка подсчета общего количества записей: {e}")
        
        # 2. Получим первые 10 записей для анализа структуры
        print("\n📋 2. СТРУКТУРА ДАННЫХ (первые 10 записей)")
        print("-" * 30)
        try:
            sample_query = supabase.table('property_trends').select('*').limit(10)
            sample_response = sample_query.execute()
            
            if sample_response.data and len(sample_response.data) > 0:
                print(f"✅ Найдено {len(sample_response.data)} записей")
                print("\n🔍 Структура первой записи:")
                first_record = sample_response.data[0]
                for key, value in first_record.items():
                    print(f"  {key}: {value} (тип: {type(value).__name__})")
                
                print("\n📊 Примеры данных:")
                for i, record in enumerate(sample_response.data[:3]):
                    print(f"\n  Запись {i+1}:")
                    print(f"    ID: {record.get('id')}")
                    print(f"    country_id: {record.get('country_id')}")
                    print(f"    city_id: {record.get('city_id')}")
                    print(f"    county_id: {record.get('county_id')}")
                    print(f"    district_id: {record.get('district_id')}")
                    print(f"    property_year: {record.get('property_year')}")
                    print(f"    property_month: {record.get('property_month')}")
                    print(f"    unit_price_for_sale: {record.get('unit_price_for_sale')}")
                    print(f"    unit_price_for_rent: {record.get('unit_price_for_rent')}")
            else:
                print("⚠️ Таблица пуста или не содержит данных")
        except Exception as e:
            print(f"❌ Ошибка получения образцов данных: {e}")
        
        # 3. Проверим уникальные значения country_id
        print("\n🌍 3. УНИКАЛЬНЫЕ ЗНАЧЕНИЯ country_id")
        print("-" * 30)
        try:
            countries_query = supabase.table('property_trends').select('country_id').limit(100)
            countries_response = countries_query.execute()
            
            if countries_response.data:
                unique_countries = list(set([r.get('country_id') for r in countries_response.data if r.get('country_id') is not None]))
                print(f"🔍 Найденные country_id: {sorted(unique_countries)}")
                
                # Подсчитаем количество для каждого country_id
                country_counts = {}
                for record in countries_response.data:
                    country_id = record.get('country_id')
                    if country_id is not None:
                        country_counts[country_id] = country_counts.get(country_id, 0) + 1
                
                print("\n📊 Количество записей по странам:")
                for country_id, count in sorted(country_counts.items()):
                    print(f"  country_id={country_id}: {count} записей")
            else:
                print("⚠️ Не удалось получить country_id из таблицы")
        except Exception as e:
            print(f"❌ Ошибка получения country_id: {e}")
        
        # 4. Проверим данные для конкретной локации (из лога)
        print("\n🎯 4. ПРОВЕРКА КОНКРЕТНОЙ ЛОКАЦИИ")
        print("-" * 30)
        target_location = {
            'country_id': 1,
            'city_id': 7,
            'county_id': 2037,
            'district_id': 2285
        }
        
        print(f"🔍 Ищем данные для локации: {target_location}")
        
        # Проверяем пошагово
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
        
        # 5. Попробуем найти любые данные для Турции
        print("\n🇹🇷 5. ПОИСК ДАННЫХ ДЛЯ ТУРЦИИ")
        print("-" * 30)
        try:
            # Ищем любые данные для country_id = 1
            turkey_query = supabase.table('property_trends').select('*').eq('country_id', 1).limit(10)
            turkey_response = turkey_query.execute()
            
            if turkey_response.data and len(turkey_response.data) > 0:
                print(f"✅ Найдено {len(turkey_response.data)} записей для Турции")
                print("\n📋 Примеры записей:")
                for i, record in enumerate(turkey_response.data[:3]):
                    print(f"\n  Запись {i+1}:")
                    print(f"    ID: {record.get('id')}")
                    print(f"    city_id: {record.get('city_id')}")
                    print(f"    county_id: {record.get('county_id')}")
                    print(f"    district_id: {record.get('district_id')}")
                    print(f"    property_year: {record.get('property_year')}")
                    print(f"    property_month: {record.get('property_month')}")
                    print(f"    unit_price_for_sale: {record.get('unit_price_for_sale')}")
            else:
                print("⚠️ Для Турции (country_id=1) данных не найдено")
        except Exception as e:
            print(f"❌ Ошибка поиска данных для Турции: {e}")
        
        # 6. Проверим, есть ли данные с другими значениями
        print("\n🔍 6. ПОИСК АЛЬТЕРНАТИВНЫХ ЗНАЧЕНИЙ")
        print("-" * 30)
        try:
            # Ищем любые данные с непустыми city_id
            cities_query = supabase.table('property_trends').select('city_id').not_.is_('city_id', 'null').limit(20)
            cities_response = cities_query.execute()
            
            if cities_response.data:
                unique_cities = list(set([r.get('city_id') for r in cities_response.data if r.get('city_id') is not None]))
                print(f"🔍 Найденные city_id: {sorted(unique_cities)}")
                
                # Проверим, есть ли city_id = 7
                if 7 in unique_cities:
                    print("✅ city_id = 7 найден в таблице!")
                else:
                    print("⚠️ city_id = 7 НЕ найден в таблице")
            else:
                print("⚠️ Не удалось получить city_id из таблицы")
        except Exception as e:
            print(f"❌ Ошибка поиска city_id: {e}")
        
        print("\n" + "=" * 50)
        print("🏁 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_property_trends()

