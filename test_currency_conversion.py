#!/usr/bin/env python3
"""
Тестовый скрипт для проверки конвертации валют с евро как базовой валютой
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import get_currency_rate_for_date, convert_turkish_data_to_eur, is_turkish_location
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_currency_conversion():
    """Тестирует конвертацию валют с евро как базовой валютой"""
    
    print("🧪 Тестирование конвертации валют с евро как базовой валютой")
    print("=" * 60)
    
    # Тест 1: Получение курса валют
    print("\n1️⃣ Получение курса валют:")
    currency_rate = get_currency_rate_for_date()
    if currency_rate:
        print(f"✅ Курс валют получен:")
        print(f"   EUR (базовая): {currency_rate.get('euro', 'н/д')}")
        print(f"   TRY: {currency_rate.get('try', 'н/д')} (1 EUR = {currency_rate.get('try', 'н/д')} TRY)")
        print(f"   USD: {currency_rate.get('usd', 'н/д')} (1 EUR = {currency_rate.get('usd', 'н/d')} USD)")
        print(f"   RUB: {currency_rate.get('rub', 'н/d')} (1 EUR = {currency_rate.get('rub', 'н/d')} RUB)")
    else:
        print("❌ Не удалось получить курс валют")
        return
    
    # Тест 2: Проверка формулы конвертации
    print("\n2️⃣ Проверка формулы конвертации:")
    if currency_rate and 'try' in currency_rate:
        try_rate = currency_rate['try']
        test_price_try = 100000  # 100,000 TRY
        expected_price_eur = test_price_try / try_rate
        
        print(f"📊 Тестовая цена: {test_price_try:,} TRY")
        print(f"💱 Курс TRY/EUR: {try_rate}")
        print(f"🧮 Формула: {test_price_try:,} TRY / {try_rate} = {expected_price_eur:.2f} EUR")
        print(f"✅ Ожидаемый результат: {expected_price_eur:.2f} EUR")
    
    # Тест 3: Конвертация турецких данных
    print("\n3️⃣ Конвертация турецких данных:")
    
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
        ]
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
    
    # Тест 4: Проверка определения турецкой локации
    print("\n4️⃣ Проверка определения турецкой локации:")
    
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
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    test_currency_conversion()

