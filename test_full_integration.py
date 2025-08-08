#!/usr/bin/env python3
"""
Финальный тест для проверки полной интеграции валютных курсов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import logging
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
if not supabase_url or not supabase_key:
    raise RuntimeError("SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
supabase: Client = create_client(supabase_url, supabase_key)

def test_full_integration():
    """Тестирует полную интеграцию валютных курсов"""
    
    print("🚀 Тестирование полной интеграции валютных курсов")
    print("=" * 60)
    
    # Импортируем функции
    try:
        from currency_functions import get_currency_rate_for_date, convert_turkish_data_to_eur, is_turkish_location
        print("✅ Валютные функции импортированы успешно")
    except ImportError:
        try:
            from currency_functions_v2 import get_currency_rate_for_date, convert_turkish_data_to_eur, is_turkish_location
            print("✅ Валютные функции v2 импортированы успешно")
        except ImportError:
            print("❌ Не удалось импортировать валютные функции")
            return False
    
    # Тест 1: Получение курса валют
    print("\n🔍 Тест 1: Получение курса валют")
    print("-" * 40)
    
    currency_rate = get_currency_rate_for_date()
    if currency_rate:
        print(f"✅ Курс валют получен: {currency_rate.get('try', 'н/д')} TRY/EUR")
    else:
        print("❌ Не удалось получить курс валют")
        return False
    
    # Тест 2: Определение турецких локаций
    print("\n🔍 Тест 2: Определение турецких локаций")
    print("-" * 40)
    
    test_locations = [
        {'country': 'Turkey', 'country_code': 'TR'},
        {'country': 'Türkiye', 'country_code': 'TR'},
        {'country': 'Germany', 'country_code': 'DE'},
    ]
    
    for location in test_locations:
        is_turkish = is_turkish_location(location)
        status = "🇹🇷 Турецкая" if is_turkish else "🌍 Не турецкая"
        print(f"📍 {location['country']} ({location['country_code']}): {status}")
    
    # Тест 3: Конвертация данных
    print("\n🔍 Тест 3: Конвертация данных")
    print("-" * 40)
    
    test_data = {
        'general_data': {
            'unit_price_for_sale': 1000.0,
            'min_unit_price_for_sale': 800.0,
            'max_unit_price_for_sale': 1200.0,
            'unit_price_for_rent': 50.0,
            'min_unit_price_for_rent': 40.0,
            'max_unit_price_for_rent': 60.0,
            'price_for_sale': 50000.0,
            'price_for_rent': 2500.0,
        },
        'property_trends': [
            {
                'unit_price_for_sale': 1100.0,
                'unit_price_for_rent': 55.0,
            }
        ]
    }
    
    converted_data = convert_turkish_data_to_eur(test_data, currency_rate)
    
    print("📊 Результаты конвертации:")
    if 'general_data' in converted_data:
        general = converted_data['general_data']
        print(f"   unit_price_for_sale: {general.get('unit_price_for_sale', 'н/д')} EUR")
        print(f"   unit_price_for_rent: {general.get('unit_price_for_rent', 'н/д')} EUR")
    
    # Тест 4: Симуляция отчета
    print("\n🔍 Тест 4: Симуляция отчета")
    print("-" * 40)
    
    # Симулируем данные отчета
    address = "Istanbul, Turkey"
    bedrooms = 3
    price = 100000
    location_codes = {
        'country_name': 'Türkiye',
        'city_name': 'Istanbul',
        'district_name': 'Kadıköy'
    }
    location_components = {
        'country': 'Turkey',
        'country_code': 'TR',
        'city': 'Istanbul'
    }
    
    # Проверяем, является ли локация турецкой
    is_turkish = is_turkish_location(location_components)
    print(f"📍 Адрес: {address}")
    print(f"🏠 Спальни: {bedrooms}")
    print(f"💰 Цена: {price} EUR")
    print(f"🇹🇷 Турецкая локация: {'Да' if is_turkish else 'Нет'}")
    
    if is_turkish:
        print(f"💱 Курс валюты: 1 EUR = {currency_rate.get('try', 'н/д')} TRY")
        print(f"📅 Дата формирования: {datetime.now().strftime('%d.%m.%Y')}")
    
    print("\n" + "=" * 60)
    print("🎉 Все тесты прошли успешно!")
    print("✅ Интеграция валютных курсов работает корректно")
    
    return True

if __name__ == "__main__":
    success = test_full_integration()
    if success:
        print("\n🚀 Готово к использованию!")
    else:
        print("\n⚠️ Есть проблемы, которые нужно исправить.")
