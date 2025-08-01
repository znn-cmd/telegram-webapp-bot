#!/usr/bin/env python3
"""
Тестовый скрипт для проверки полного отчета с экономическими данными
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
        
        # Запрос к таблице imf_economic_data для ВВП (NGDP_RPCH)
        gdp_query = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'NGDP_RPCH').gte('year', start_year).order('year', desc=True)
        gdp_result = gdp_query.execute()
        
        # Запрос к таблице imf_economic_data для инфляции (PCPIPCH)
        inflation_query = supabase.table('imf_economic_data').select('*').eq('country_code', country_code).eq('indicator_code', 'PCPIPCH').gte('year', start_year).order('year', desc=True)
        inflation_result = inflation_query.execute()
        
        if not gdp_result.data and not inflation_result.data:
            return {
                'gdp_data': [],
                'inflation_data': [],
                'country_code': country_code,
                'country_name': 'Unknown',
                'error': 'No data available'
            }
        
        # Обрабатываем данные ВВП
        gdp_data = []
        for record in gdp_result.data:
            year = record.get('year')
            value = record.get('value')
            if year and value is not None:
                gdp_data.append({
                    'year': year,
                    'value': float(value),
                    'indicator_code': record.get('indicator_code'),
                    'indicator_name': record.get('indicator_name')
                })
        
        # Обрабатываем данные инфляции
        inflation_data = []
        for record in inflation_result.data:
            year = record.get('year')
            value = record.get('value')
            if year and value is not None:
                inflation_data.append({
                    'year': year,
                    'value': float(value),
                    'indicator_code': record.get('indicator_code'),
                    'indicator_name': record.get('indicator_name')
                })
        
        # Сортируем по году (от старых к новым для графиков)
        gdp_data.sort(key=lambda x: x['year'])
        inflation_data.sort(key=lambda x: x['year'])
        
        # Вычисляем тренды
        gdp_values = [d['value'] for d in gdp_data]
        inflation_values = [d['value'] for d in inflation_data]
        
        gdp_trend = calculate_trend(gdp_values) if gdp_values else 0
        inflation_trend = calculate_trend(inflation_values) if inflation_values else 0
        
        # Получаем название страны из первой записи
        country_name = gdp_result.data[0].get('country_name') if gdp_result.data else 'Unknown'
        
        return {
            'gdp_data': gdp_data,
            'inflation_data': inflation_data,
            'country_code': country_code,
            'country_name': country_name,
            'gdp_trend': gdp_trend,
            'inflation_trend': inflation_trend,
            'latest_gdp': gdp_data[-1] if gdp_data else None,
            'latest_inflation': inflation_data[-1] if inflation_data else None,
            'data_years': f"{start_year}-{current_year}"
        }
        
    except Exception as e:
        return {
            'gdp_data': [],
            'inflation_data': [],
            'country_code': country_code,
            'country_name': 'Unknown',
            'error': str(e)
        }

def calculate_trend(values):
    """Вычисление тренда для ряда значений"""
    if len(values) < 2:
        return 0
    
    # Простая линейная регрессия
    n = len(values)
    x_sum = sum(range(n))
    y_sum = sum(values)
    xy_sum = sum(i * val for i, val in enumerate(values))
    x2_sum = sum(i * i for i in range(n))
    
    # Вычисляем коэффициент наклона
    slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
    
    return slope

def create_economic_chart_data(economic_data):
    """Создание данных для построения графиков"""
    gdp_data = economic_data.get('gdp_data', [])
    inflation_data = economic_data.get('inflation_data', [])
    country_name = economic_data.get('country_name', 'Unknown')
    
    # Подготавливаем данные для графиков ВВП (рост в процентах)
    gdp_chart = {
        'labels': [str(d['year']) for d in gdp_data],
        'datasets': [
            {
                'label': f'Рост ВВП (%) - {country_name}',
                'data': [d['value'] for d in gdp_data],
                'borderColor': '#667eea',
                'backgroundColor': 'rgba(102, 126, 234, 0.1)',
                'tension': 0.4,
                'fill': False
            }
        ]
    }
    
    # Подготавливаем данные для графиков инфляции
    inflation_chart = {
        'labels': [str(d['year']) for d in inflation_data],
        'datasets': [
            {
                'label': f'Инфляция (%) - {country_name}',
                'data': [d['value'] for d in inflation_data],
                'borderColor': '#dc3545',
                'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                'tension': 0.4,
                'fill': False
            }
        ]
    }
    
    return {
        'gdp_chart': gdp_chart,
        'inflation_chart': inflation_chart,
        'trends': {
            'gdp_trend': economic_data.get('gdp_trend', 0),
            'inflation_trend': economic_data.get('inflation_trend', 0)
        },
        'latest': {
            'gdp': economic_data.get('latest_gdp'),
            'inflation': economic_data.get('latest_inflation')
        },
        'country_name': country_name,
        'country_code': economic_data.get('country_code', 'Unknown')
    }

def test_full_report():
    """Тестируем полный отчет с экономическими данными"""
    print("🔍 Тестирование полного отчета с экономическими данными...")
    
    # Получаем экономические данные
    economic_data = get_economic_data_simple('TUR', 10)
    
    if 'error' in economic_data:
        print(f"❌ Ошибка получения данных: {economic_data['error']}")
        return
    
    print(f"✅ Экономические данные получены:")
    print(f"   - Страна: {economic_data.get('country_name', 'Unknown')}")
    print(f"   - Данные ВВП: {len(economic_data.get('gdp_data', []))} записей")
    print(f"   - Данные инфляции: {len(economic_data.get('inflation_data', []))} записей")
    
    # Создаем данные для графиков
    chart_data = create_economic_chart_data(economic_data)
    
    print(f"✅ Данные графиков созданы:")
    print(f"   - Название страны: {chart_data.get('country_name', 'Unknown')}")
    print(f"   - Данные ВВП: {len(chart_data.get('gdp_chart', {}).get('labels', []))} точек")
    print(f"   - Данные инфляции: {len(chart_data.get('inflation_chart', {}).get('labels', []))} точек")
    
    # Создаем полный отчет
    full_report_data = {
        'object': {
            'address': 'Test Address, Istanbul',
            'bedrooms': 2,
            'purchase_price': 150000,
            'avg_price_per_sqm': 2500
        },
        'roi': {
            'short_term': {
                'monthly_income': 1200,
                'net_income': 800,
                'five_year_income': 93600,
                'final_value': 180000,
                'roi': 81.5
            },
            'long_term': {
                'annual_income': 14400,
                'net_income': 9600,
                'five_year_income': 172000,
                'final_value': 180000,
                'roi': 130.5
            },
            'no_rent': {
                'final_value': 180000,
                'roi': 23
            },
            'price_growth': 0.20
        },
        'alternatives': [
            {'name': 'Банковский депозит', 'yield': 0.25, 'source': 'TCMB API'},
            {'name': 'Облигации Турции', 'yield': 0.35, 'source': 'Investing.com API'},
            {'name': 'Акции (BIST30)', 'yield': 0.45, 'source': 'Alpha Vantage API'},
            {'name': 'REITs (фонды)', 'yield': 0.55, 'source': 'Financial Modeling Prep'},
            {'name': 'Недвижимость', 'yield': 0.815, 'source': 'Ваш объект'}
        ],
        'macro': {
            'inflation': economic_data.get('latest_inflation', {}).get('value', 0) if economic_data.get('latest_inflation') else 0,
            'eur_try': 35.2,
            'eur_try_growth': 0.14,
            'refi_rate': 45,
            'gdp_growth': economic_data.get('latest_gdp', {}).get('value', 0) if economic_data.get('latest_gdp') else 0
        },
        'economic_charts': chart_data,  # Добавляем данные для графиков
        'taxes': {
            'transfer_tax': 0.04,
            'stamp_duty': 0.01,
            'notary': 500
        },
        'risks': [
            'Валютные риски',
            'Политические риски',
            'Риски ликвидности'
        ],
        'liquidity': 'Средняя ликвидность',
        'district': 'Развивающийся район',
        'yield': 0.081,
        'price_index': 1.23,
        'mortgage_rate': 0.32,
        'global_house_price_index': 1.12,
        'summary': 'Полный отчёт с реальными экономическими данными из IMF.'
    }
    
    print(f"\n📊 Полный отчет создан:")
    print(f"   - Инфляция: {full_report_data['macro']['inflation']}%")
    print(f"   - Рост ВВП: {full_report_data['macro']['gdp_growth']}%")
    print(f"   - Экономические графики: {'Да' if 'economic_charts' in full_report_data else 'Нет'}")
    
    if full_report_data.get('economic_charts'):
        charts = full_report_data['economic_charts']
        print(f"   - Страна графиков: {charts.get('country_name', 'Unknown')}")
        print(f"   - Тренд ВВП: {charts.get('trends', {}).get('gdp_trend', 0):.3f}")
        print(f"   - Тренд инфляции: {charts.get('trends', {}).get('inflation_trend', 0):.3f}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_full_report() 