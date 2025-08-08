#!/usr/bin/env python3
"""
Тест интеграции с валютными курсами (улучшенная версия)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions_v2 import (
    get_currency_rate_for_date,
    fetch_and_save_currency_rates,
    convert_turkish_data_to_eur,
    is_turkish_location,
    get_latest_currency_rate
)
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_currency_functions():
    """Тестирует функции работы с валютными курсами"""
    
    print("🧪 Тестирование функций валютных курсов (улучшенная версия)...")
    
    # Тест 1: Получение последней записи курса валют
    print("\n1. Тест получения последней записи курса валют:")
    try:
        latest_rate = get_latest_currency_rate()
        if latest_rate:
            print(f"✅ Последняя запись курса валют: {latest_rate}")
            print(f"   TRY/EUR: {latest_rate.get('try', 'н/д')}")
            print(f"   USD/EUR: {latest_rate.get('usd', 'н/д')}")
            print(f"   RUB/EUR: {latest_rate.get('rub', 'н/д')}")
        else:
            print("❌ Нет доступных записей курса валют")
    except Exception as e:
        print(f"❌ Ошибка при получении последней записи: {e}")
    
    # Тест 2: Получение курса валюты для сегодняшней даты
    print("\n2. Тест получения курса валюты для сегодняшней даты:")
    try:
        currency_rate = get_currency_rate_for_date()
        if currency_rate:
            print(f"✅ Курс валюты получен: {currency_rate}")
            print(f"   TRY/EUR: {currency_rate.get('try', 'н/д')}")
            print(f"   USD/EUR: {currency_rate.get('usd', 'н/д')}")
            print(f"   RUB/EUR: {currency_rate.get('rub', 'н/д')}")
        else:
            print("❌ Не удалось получить курс валюты")
    except Exception as e:
        print(f"❌ Ошибка при получении курса валюты: {e}")
    
    # Тест 3: Проверка турецкой локации
    print("\n3. Тест определения турецкой локации:")
    
    # Турецкая локация
    turkish_components = {
        'country': 'Turkey',
        'country_code': 'TR',
        'city': 'Istanbul',
        'district': 'Kadikoy'
    }
    
    is_turkish = is_turkish_location(turkish_components)
    print(f"Турецкая локация: {is_turkish}")
    
    # Нетурецкая локация
    non_turkish_components = {
        'country': 'Germany',
        'country_code': 'DE',
        'city': 'Berlin',
        'district': 'Mitte'
    }
    
    is_turkish = is_turkish_location(non_turkish_components)
    print(f"Нетурецкая локация: {is_turkish}")
    
    # Тест 4: Конвертация турецких данных в евро
    print("\n4. Тест конвертации турецких данных в евро:")
    
    # Пример турецких данных
    turkish_market_data = {
        'general_data': {
            'unit_price_for_sale': 50000,  # TRY за м²
            'unit_price_for_rent': 2500,   # TRY за м²
            'price_for_sale': 1000000,     # TRY
            'price_for_rent': 50000        # TRY
        },
        'house_type_data': [
            {
                'listing_type': '2+1',
                'unit_price_for_sale': 45000,
                'unit_price_for_rent': 2200
            }
        ]
    }
    
    # Получаем курс валюты для конвертации
    currency_rate = get_currency_rate_for_date()
    if currency_rate and currency_rate.get('try'):
        converted_data = convert_turkish_data_to_eur(turkish_market_data, currency_rate)
        print(f"✅ Данные конвертированы в EUR:")
        print(f"   Курс TRY/EUR: {currency_rate['try']}")
        print(f"   Цена продажи за м²: {converted_data['general_data']['unit_price_for_sale']:.2f} EUR")
        print(f"   Цена аренды за м²: {converted_data['general_data']['unit_price_for_rent']:.2f} EUR")
        print(f"   Цена продажи: {converted_data['general_data']['price_for_sale']:.2f} EUR")
        print(f"   Цена аренды: {converted_data['general_data']['price_for_rent']:.2f} EUR")
    else:
        print("❌ Не удалось получить курс валюты для конвертации")
    
    # Тест 5: Проверка API currencylayer.com (с обработкой ошибок)
    print("\n5. Тест API currencylayer.com (с обработкой ошибок):")
    try:
        # Получаем курсы валют напрямую с API
        currency_data = fetch_and_save_currency_rates()
        if currency_data:
            print(f"✅ Курсы валют получены с API:")
            print(f"   TRY/EUR: {currency_data.get('try', 'н/д')}")
            print(f"   USD/EUR: {currency_data.get('usd', 'н/д')}")
            print(f"   RUB/EUR: {currency_data.get('rub', 'н/д')}")
            print(f"   AED/EUR: {currency_data.get('aed', 'н/д')}")
            print(f"   THB/EUR: {currency_data.get('thb', 'н/д')}")
        else:
            print("❌ Не удалось получить курсы валют с API")
    except Exception as e:
        print(f"❌ Ошибка при получении курсов валют с API: {e}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_currency_functions()
