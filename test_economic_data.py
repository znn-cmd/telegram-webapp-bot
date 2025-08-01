#!/usr/bin/env python3
"""
Тестовый скрипт для проверки экономических данных из Supabase
"""

import os
import sys
from supabase import create_client, Client

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем функции из app.py
from app import get_economic_data, create_economic_chart_data

def test_economic_data():
    """Тестируем получение экономических данных"""
    print("🔍 Тестирование экономических данных...")
    
    try:
        # Тестируем получение данных для Турции
        print("\n📊 Получение данных для Турции (TUR):")
        economic_data = get_economic_data('TUR', 10)
        
        print(f"✅ Данные получены:")
        print(f"   - Страна: {economic_data.get('country_name', 'Unknown')}")
        print(f"   - Код страны: {economic_data.get('country_code', 'Unknown')}")
        print(f"   - Данные ВВП: {len(economic_data.get('gdp_data', []))} записей")
        print(f"   - Данные инфляции: {len(economic_data.get('inflation_data', []))} записей")
        
        if economic_data.get('gdp_data'):
            print(f"   - Последний ВВП: {economic_data['latest_gdp']}")
        
        if economic_data.get('inflation_data'):
            print(f"   - Последняя инфляция: {economic_data['latest_inflation']}")
        
        print(f"   - Тренд ВВП: {economic_data.get('gdp_trend', 0):.3f}")
        print(f"   - Тренд инфляции: {economic_data.get('inflation_trend', 0):.3f}")
        
        # Тестируем создание данных для графиков
        print("\n📈 Создание данных для графиков:")
        chart_data = create_economic_chart_data(economic_data)
        
        print(f"✅ Данные графиков созданы:")
        print(f"   - Название страны: {chart_data.get('country_name', 'Unknown')}")
        print(f"   - Данные ВВП: {len(chart_data.get('gdp_chart', {}).get('labels', []))} точек")
        print(f"   - Данные инфляции: {len(chart_data.get('inflation_chart', {}).get('labels', []))} точек")
        
        if chart_data.get('gdp_chart', {}).get('labels'):
            print(f"   - Годы ВВП: {chart_data['gdp_chart']['labels'][:5]}...")
        
        if chart_data.get('inflation_chart', {}).get('labels'):
            print(f"   - Годы инфляции: {chart_data['inflation_chart']['labels'][:5]}...")
        
        # Тестируем данные для других стран
        print("\n🌍 Тестирование других стран:")
        test_countries = ['USA', 'DEU', 'GBR', 'FRA']
        
        for country in test_countries:
            print(f"\n📊 {country}:")
            try:
                data = get_economic_data(country, 5)
                print(f"   - Данные ВВП: {len(data.get('gdp_data', []))} записей")
                print(f"   - Данные инфляции: {len(data.get('inflation_data', []))} записей")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        print("\n✅ Тестирование завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_economic_data() 