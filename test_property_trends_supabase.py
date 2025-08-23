#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки данных через Supabase API
Проверяет количество записей в таблице property_trends
"""

import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def test_property_trends_supabase():
    """Тестирует Supabase API для таблицы property_trends"""
    
    # Получаем настройки Supabase из переменных окружения
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Ошибка: Не найдены переменные окружения SUPABASE_URL или SUPABASE_ANON_KEY")
        print("💡 Создайте файл .env с настройками Supabase")
        return
    
    # Параметры локации
    country_id = 1
    city_id = 7
    county_id = 2038
    district_id = 2339
    
    print(f"🔍 Тестирование Supabase API для таблицы property_trends")
    print(f"📍 Локация: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
    print(f"🌐 Supabase URL: {supabase_url}")
    print("=" * 80)
    
    # 1. Проверяем общее количество записей в таблице
    print("📊 1. Общее количество записей в таблице property_trends:")
    
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/property_trends?select=count",
            headers={
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Ответ: {data}")
        else:
            print(f"   Ошибка: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 2. Проверяем записи для указанной локации
    print(f"\n📊 2. Записи для указанной локации:")
    
    try:
        # Запрос с фильтрацией по локации
        query_params = {
            'select': '*',
            'country_id': f'eq.{country_id}',
            'city_id': f'eq.{city_id}',
            'county_id': f'eq.{county_id}',
            'district_id': f'eq.{district_id}',
            'order': 'property_date.desc'
        }
        
        # Формируем URL с параметрами
        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        url = f"{supabase_url}/rest/v1/property_trends?{query_string}"
        
        print(f"   URL запроса: {url}")
        
        response = requests.get(
            url,
            headers={
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            trends = response.json()
            print(f"   ✅ Получено записей: {len(trends)}")
            
            if trends:
                print(f"\n📋 Детали записей:")
                for i, trend in enumerate(trends):
                    print(f"   {i+1:2d}. ID: {trend.get('id', 'N/A')} | "
                          f"Дата: {trend.get('property_date', 'N/A')} | "
                          f"Год-месяц: {trend.get('property_year', 'N/A')}-{trend.get('property_month', 'N/A'):02d} | "
                          f"Продажа: {trend.get('unit_price_for_sale', 0):8.2f} | "
                          f"Аренда: {trend.get('unit_price_for_rent', 0):6.2f} | "
                          f"Доходность: {trend.get('yield', 0):5.2f}%")
                
                # Анализируем распределение по месяцам
                print(f"\n📊 Распределение по месяцам:")
                month_distribution = {}
                for trend in trends:
                    year = trend.get('property_year')
                    month = trend.get('property_month')
                    if year and month:
                        key = f"{year}-{month:02d}"
                        if key not in month_distribution:
                            month_distribution[key] = 0
                        month_distribution[key] += 1
                
                for month in sorted(month_distribution.keys(), reverse=True):
                    print(f"   {month}: {month_distribution[month]} записей")
                
                # Проверяем текущую дату и фильтрацию
                current_date = datetime.now()
                current_year = current_date.year
                current_month = current_date.month
                
                print(f"\n📊 Анализ фильтрации:")
                print(f"   Текущая дата: {current_date.strftime('%Y-%m-%d')}")
                print(f"   Текущий год-месяц: {current_year}-{current_month:02d}")
                
                # Подсчитываем записи, которые должны отображаться
                visible_count = 0
                future_count = 0
                
                for trend in trends:
                    year = trend.get('property_year')
                    month = trend.get('property_month')
                    
                    if year and month:
                        if year < current_year:
                            visible_count += 1  # Прошлые годы
                        elif year == current_year:
                            if month <= current_month:
                                visible_count += 1  # Текущий год, месяц <= текущего
                            else:
                                future_count += 1  # Текущий год, месяц > текущего
                        else:
                            future_count += 1  # Будущие годы
                
                print(f"   Записей для отображения (до текущего месяца): {visible_count}")
                print(f"   Записей будущих месяцев (скрыто): {future_count}")
                
                # Итоговая сводка
                print(f"\n📋 ИТОГОВАЯ СВОДКА:")
                print(f"   Всего записей от Supabase: {len(trends)}")
                print(f"   Записей для отображения: {visible_count}")
                print(f"   Записей будущих месяцев (скрыто): {future_count}")
                
                if len(trends) > visible_count:
                    print(f"\n⚠️  ВНИМАНИЕ: В таблице отображается {visible_count} записей из {len(trends)} доступных!")
                    print(f"   Это означает, что {len(trends) - visible_count} записей скрыто фильтром по датам.")
                
            else:
                print("   ⚠️ Записей не найдено")
                
        else:
            print(f"   ❌ Ошибка API: {response.status_code}")
            print(f"   📊 Ответ: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Проверяем структуру таблицы
    print(f"\n📊 3. Структура таблицы property_trends:")
    
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/property_trends?select=*&limit=1",
            headers={
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                sample_record = data[0]
                print(f"   Пример записи:")
                for key, value in sample_record.items():
                    print(f"     {key}: {type(value).__name__} = {value}")
            else:
                print("   Таблица пуста")
        else:
            print(f"   ❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Тестирование завершено")

if __name__ == "__main__":
    test_property_trends_supabase()

