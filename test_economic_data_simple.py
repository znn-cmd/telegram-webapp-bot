#!/usr/bin/env python3
"""
Упрощенный тест экономических данных из Supabase
"""

import os
import sys
import datetime
from supabase import create_client, Client

# Настройки Supabase
SUPABASE_URL = "https://dzllnnohurlzjyabgsft.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6bGxubm9odXJsemp5YWJnc2Z0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA5NDgwMjcsImV4cCI6MjA2NjUyNDAyN30.sJCIeeIm0Ye1JbAdw5HzfAMe8QLgQomArK8yoppuevQ"

def get_economic_data_simple(country_code='TUR', years_back=10):
    """Упрощенная версия получения экономических данных"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Получаем данные за последние N лет
        current_year = datetime.datetime.now().year
        start_year = current_year - years_back
        
        print(f"🔍 Поиск данных для {country_code} с {start_year} по {current_year}")
        
        # Запрос к таблице imf_economic_data для ВВП (NGDP_RPCH)
        gdp_query = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'NGDP_RPCH').gte('year', start_year).order('year', desc=True)
        gdp_result = gdp_query.execute()
        
        # Запрос к таблице imf_economic_data для инфляции (PCPIPCH)
        inflation_query = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'PCPIPCH').gte('year', start_year).order('year', desc=True)
        inflation_result = inflation_query.execute()
        
        print(f"📊 Результаты запросов:")
        print(f"   - ВВП записей: {len(gdp_result.data) if gdp_result.data else 0}")
        print(f"   - Инфляция записей: {len(inflation_result.data) if inflation_result.data else 0}")
        
        if gdp_result.data:
            print(f"   - Пример данных ВВП: {gdp_result.data[0]}")
        
        if inflation_result.data:
            print(f"   - Пример данных инфляции: {inflation_result.data[0]}")
        
        return {
            'gdp_data': gdp_result.data or [],
            'inflation_data': inflation_result.data or [],
            'country_code': country_code,
            'country_name': gdp_result.data[0].get('country_name') if gdp_result.data else 'Unknown'
        }
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return {'error': str(e)}

def test_economic_data():
    """Тестируем получение экономических данных"""
    print("🔍 Тестирование экономических данных...")
    
    # Тестируем получение данных для Турции
    print("\n📊 Получение данных для Турции (TUR):")
    economic_data = get_economic_data_simple('TUR', 10)
    
    if 'error' not in economic_data:
        print(f"✅ Данные получены:")
        print(f"   - Страна: {economic_data.get('country_name', 'Unknown')}")
        print(f"   - Код страны: {economic_data.get('country_code', 'Unknown')}")
        print(f"   - Данные ВВП: {len(economic_data.get('gdp_data', []))} записей")
        print(f"   - Данные инфляции: {len(economic_data.get('inflation_data', []))} записей")
        
        # Показываем первые несколько записей
        if economic_data.get('gdp_data'):
            print(f"\n📈 Данные ВВП:")
            for i, record in enumerate(economic_data['gdp_data'][:5]):
                print(f"   {record.get('year')}: {record.get('value')}%")
        
        if economic_data.get('inflation_data'):
            print(f"\n📉 Данные инфляции:")
            for i, record in enumerate(economic_data['inflation_data'][:5]):
                print(f"   {record.get('year')}: {record.get('value')}%")
    
    # Тестируем данные для других стран
    print("\n🌍 Тестирование других стран:")
    test_countries = ['USA', 'DEU', 'GBR', 'FRA', 'ABW']
    
    for country in test_countries:
        print(f"\n📊 {country}:")
        data = get_economic_data_simple(country, 5)
        if 'error' not in data:
            print(f"   - Данные ВВП: {len(data.get('gdp_data', []))} записей")
            print(f"   - Данные инфляции: {len(data.get('inflation_data', []))} записей")
        else:
            print(f"   ❌ Ошибка: {data['error']}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_economic_data() 