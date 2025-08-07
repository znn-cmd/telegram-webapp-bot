#!/usr/bin/env python3
"""
Комплексный тестовый скрипт для проверки функционала конвертации валют
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import get_currency_rate_for_date, convert_turkish_data_to_eur, is_turkish_location, fetch_and_save_currency_rates
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_complete_currency_functionality():
    """Тестирует полный функционал конвертации валют"""
    
    print("🧪 Комплексное тестирование функционала конвертации валют")
    print("=" * 70)
    
    # Тест 1: Получение курса валют из базы данных
    print("\n1️⃣ Получение курса валют из базы данных:")
    currency_rate = get_currency_rate_for_date()
    if currency_rate:
        print(f"✅ Курс валют получен из базы:")
        print(f"   EUR (базовая): {currency_rate.get('euro', 'н/д')}")
        print(f"   TRY: {currency_rate.get('try', 'н/д')} (1 EUR = {currency_rate.get('try', 'н/д')} TRY)")
        print(f"   USD: {currency_rate.get('usd', 'н/д')} (1 EUR = {currency_rate.get('usd', 'н/д')} USD)")
        print(f"   RUB: {currency_rate.get('rub', 'н/д')} (1 EUR = {currency_rate.get('rub', 'н/д')} RUB)")
    else:
        print("❌ Не удалось получить курс валют из базы")
        return
    
    # Тест 2: Получение свежего курса с API
    print("\n2️⃣ Получение свежего курса с API currencylayer.com:")
    try:
        fresh_rate = fetch_and_save_currency_rates()
        if fresh_rate:
            print(f"✅ Свежий курс получен с API:")
            print(f"   EUR (базовая): {fresh_rate.get('euro', 'н/д')}")
            print(f"   TRY: {fresh_rate.get('try', 'н/д')} (1 EUR = {fresh_rate.get('try', 'н/д')} TRY)")
            print(f"   USD: {fresh_rate.get('usd', 'н/д')} (1 EUR = {fresh_rate.get('usd', 'н/д')} USD)")
        else:
            print("⚠️ Не удалось получить свежий курс с API")
    except Exception as e:
        print(f"❌ Ошибка при получении свежего курса: {e}")
    
    # Тест 3: Проверка определения турецкой локации
    print("\n3️⃣ Проверка определения турецкой локации:")
    test_locations = [
        {'country': 'Turkey', 'country_code': 'TR'},
        {'country': 'Türkiye', 'country_code': 'TR'},
        {'country': 'Germany', 'country_code': 'DE'},
        {'country': 'Russia', 'country_code': 'RU'},
        None
    ]
    
    for i, location in enumerate(test_locations, 1):
        is_turkish = is_turkish_location(location)
        location_str = str(location) if location else "None"
        print(f"   {i}. {location_str} -> {'🇹🇷 Турецкая' if is_turkish else '❌ Не турецкая'}")
    
    # Тест 4: Конвертация турецких данных
    print("\n4️⃣ Конвертация турецких данных:")
    
    # Тестовые данные (турецкие цены в TRY)
    test_market_data = {
        'general_data': {
            'unit_price_for_sale': 15000,  # 15,000 TRY/м²
            'min_unit_price_for_sale': 12000,  # 12,000 TRY/м²
            'max_unit_price_for_sale': 20000,  # 20,000 TRY/м²
            'unit_price_for_rent': 800,  # 800 TRY/м²
            'price_for_sale': 1500000,  # 1,500,000 TRY
            'price_for_rent': 8000,  # 8,000 TRY
        },
        'house_type_data': [
            {
                'listing_type': '3+1',
                'unit_price_for_sale': 16000,  # 16,000 TRY/м²
                'price_for_sale': 1600000,  # 1,600,000 TRY
                'unit_price_for_rent': 900,  # 900 TRY/м²
                'price_for_rent': 9000,  # 9,000 TRY
            }
        ],
        'floor_data': {
            'listing_type': '2-5',
            'unit_price_for_sale': 15500,  # 15,500 TRY/м²
            'price_for_sale': 1550000,  # 1,550,000 TRY
        },
        'heating_data': {
            'listing_type': 'Central',
            'unit_price_for_sale': 15800,  # 15,800 TRY/м²
            'price_for_sale': 1580000,  # 1,580,000 TRY
        }
    }
    
    print("📊 Исходные данные (в TRY):")
    print(f"   Цена продажи за м²: {test_market_data['general_data']['unit_price_for_sale']:,} TRY")
    print(f"   Цена аренды за м²: {test_market_data['general_data']['unit_price_for_rent']:,} TRY")
    print(f"   Общая цена продажи: {test_market_data['general_data']['price_for_sale']:,} TRY")
    
    # Конвертируем данные
    converted_data = convert_turkish_data_to_eur(test_market_data, currency_rate)
    
    if converted_data and currency_rate and 'try' in currency_rate:
        try_rate = currency_rate['try']
        print(f"\n💱 Конвертированные данные (в EUR):")
        print(f"   Цена продажи за м²: €{converted_data['general_data']['unit_price_for_sale']:.2f}")
        print(f"   Цена аренды за м²: €{converted_data['general_data']['unit_price_for_rent']:.2f}")
        print(f"   Общая цена продажи: €{converted_data['general_data']['price_for_sale']:.2f}")
        
        # Проверяем правильность конвертации
        expected_sale_price = test_market_data['general_data']['unit_price_for_sale'] / try_rate
        expected_rent_price = test_market_data['general_data']['unit_price_for_rent'] / try_rate
        expected_total_sale = test_market_data['general_data']['price_for_sale'] / try_rate
        
        print(f"\n✅ Проверка результатов:")
        print(f"   Ожидаемая цена продажи: €{expected_sale_price:.2f}")
        print(f"   Полученная цена продажи: €{converted_data['general_data']['unit_price_for_sale']:.2f}")
        print(f"   Совпадение: {'✅' if abs(expected_sale_price - converted_data['general_data']['unit_price_for_sale']) < 0.01 else '❌'}")
        
        print(f"   Ожидаемая цена аренды: €{expected_rent_price:.2f}")
        print(f"   Полученная цена аренды: €{converted_data['general_data']['unit_price_for_rent']:.2f}")
        print(f"   Совпадение: {'✅' if abs(expected_rent_price - converted_data['general_data']['unit_price_for_rent']) < 0.01 else '❌'}")
        
        # Проверяем конвертацию вложенных данных
        if 'house_type_data' in converted_data and converted_data['house_type_data']:
            house_data = converted_data['house_type_data'][0]
            expected_house_price = test_market_data['house_type_data'][0]['unit_price_for_sale'] / try_rate
            print(f"\n   Проверка house_type_data:")
            print(f"   Ожидаемая цена: €{expected_house_price:.2f}")
            print(f"   Полученная цена: €{house_data['unit_price_for_sale']:.2f}")
            print(f"   Совпадение: {'✅' if abs(expected_house_price - house_data['unit_price_for_sale']) < 0.01 else '❌'}")
    
    # Тест 5: Симуляция полного процесса генерации отчета
    print("\n5️⃣ Симуляция полного процесса генерации отчета:")
    
    # Симулируем турецкую локацию
    turkish_location = {'country': 'Turkey', 'country_code': 'TR'}
    is_turkish = is_turkish_location(turkish_location)
    
    print(f"📍 Локация: {turkish_location}")
    print(f"🇹🇷 Турецкая локация: {'Да' if is_turkish else 'Нет'}")
    
    if is_turkish:
        print(f"💱 Получаем курс валюты...")
        currency_rate = get_currency_rate_for_date()
        
        if currency_rate:
            print(f"✅ Курс получен: 1 EUR = {currency_rate.get('try', 'н/д')} TRY")
            print(f"📊 Конвертируем данные рынка...")
            
            # Симулируем конвертацию данных
            converted_market_data = convert_turkish_data_to_eur(test_market_data, currency_rate)
            
            print(f"✅ Данные конвертированы в EUR")
            print(f"📅 Дата формирования отчета: {datetime.now().strftime('%d.%m.%Y')}")
            print(f"💱 Курс валюты (EUR/TRY): 1 EUR = {currency_rate.get('try', 0):.6f} TRY")
        else:
            print("❌ Не удалось получить курс валюты")
    else:
        print("ℹ️ Локация не турецкая, конвертация не требуется")
    
    print("\n" + "=" * 70)
    print("✅ Комплексное тестирование завершено!")

if __name__ == "__main__":
    test_complete_currency_functionality()
