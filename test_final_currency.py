#!/usr/bin/env python3
"""
Финальный тест функционала конвертации валют
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import get_currency_rate_for_date, convert_turkish_data_to_eur, is_turkish_location
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_final_currency():
    """Финальный тест функционала конвертации валют"""
    
    print("🧪 Финальный тест функционала конвертации валют")
    print("=" * 50)
    
    # Тест 1: Получение курса валют (с fallback)
    print("\n1️⃣ Получение курса валют (с fallback):")
    currency_rate = get_currency_rate_for_date()
    if currency_rate:
        print(f"✅ Курс валют получен:")
        print(f"   EUR (базовая): {currency_rate.get('euro', 'н/д')}")
        print(f"   TRY: {currency_rate.get('try', 'н/д')} (1 EUR = {currency_rate.get('try', 'н/д')} TRY)")
        print(f"   USD: {currency_rate.get('usd', 'н/д')} (1 EUR = {currency_rate.get('usd', 'н/д')} USD)")
        print(f"   RUB: {currency_rate.get('rub', 'н/д')} (1 EUR = {currency_rate.get('rub', 'н/д')} RUB)")
        print(f"   AED: {currency_rate.get('aed', 'н/д')} (1 EUR = {currency_rate.get('aed', 'н/д')} AED)")
        print(f"   THB: {currency_rate.get('thb', 'н/д')} (1 EUR = {currency_rate.get('thb', 'н/д')} THB)")
    else:
        print("❌ Не удалось получить курс валют")
        return
    
    # Тест 2: Проверка определения турецкой локации
    print("\n2️⃣ Проверка определения турецкой локации:")
    test_locations = [
        {'country': 'Turkey', 'country_code': 'TR'},
        {'country': 'Türkiye', 'country_code': 'TR'},
        {'country': 'Germany', 'country_code': 'DE'},
        None
    ]
    
    for i, location in enumerate(test_locations, 1):
        is_turkish = is_turkish_location(location)
        location_str = str(location) if location else "None"
        print(f"   {i}. {location_str} -> {'🇹🇷 Турецкая' if is_turkish else '❌ Не турецкая'}")
    
    # Тест 3: Конвертация турецких данных
    print("\n3️⃣ Конвертация турецких данных:")
    
    test_market_data = {
        'general_data': {
            'unit_price_for_sale': 15000,  # 15,000 TRY/м²
            'unit_price_for_rent': 800,  # 800 TRY/м²
            'price_for_sale': 1500000,  # 1,500,000 TRY
        },
        'house_type_data': [
            {
                'listing_type': '3+1',
                'unit_price_for_sale': 16000,  # 16,000 TRY/м²
                'price_for_sale': 1600000,  # 1,600,000 TRY
            }
        ]
    }
    
    print("📊 Исходные данные (в TRY):")
    print(f"   Цена продажи за м²: {test_market_data['general_data']['unit_price_for_sale']:,} TRY")
    print(f"   Цена аренды за м²: {test_market_data['general_data']['unit_price_for_rent']:,} TRY")
    
    # Конвертируем данные
    converted_data = convert_turkish_data_to_eur(test_market_data, currency_rate)
    
    if converted_data and currency_rate and 'try' in currency_rate:
        try_rate = currency_rate['try']
        print(f"\n💱 Конвертированные данные (в EUR):")
        print(f"   Цена продажи за м²: €{converted_data['general_data']['unit_price_for_sale']:.2f}")
        print(f"   Цена аренды за м²: €{converted_data['general_data']['unit_price_for_rent']:.2f}")
        
        # Проверяем правильность конвертации
        expected_sale_price = test_market_data['general_data']['unit_price_for_sale'] / try_rate
        expected_rent_price = test_market_data['general_data']['unit_price_for_rent'] / try_rate
        
        print(f"\n✅ Проверка результатов:")
        print(f"   Ожидаемая цена продажи: €{expected_sale_price:.2f}")
        print(f"   Полученная цена продажи: €{converted_data['general_data']['unit_price_for_sale']:.2f}")
        print(f"   Совпадение: {'✅' if abs(expected_sale_price - converted_data['general_data']['unit_price_for_sale']) < 0.01 else '❌'}")
        
        # Проверяем конвертацию вложенных данных
        if 'house_type_data' in converted_data and converted_data['house_type_data']:
            house_data = converted_data['house_type_data'][0]
            expected_house_price = test_market_data['house_type_data'][0]['unit_price_for_sale'] / try_rate
            print(f"\n   Проверка house_type_data:")
            print(f"   Ожидаемая цена: €{expected_house_price:.2f}")
            print(f"   Полученная цена: €{house_data['unit_price_for_sale']:.2f}")
            print(f"   Совпадение: {'✅' if abs(expected_house_price - house_data['unit_price_for_sale']) < 0.01 else '❌'}")
    
    # Тест 4: Симуляция полного процесса
    print("\n4️⃣ Симуляция полного процесса генерации отчета:")
    
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
    
    print("\n" + "=" * 50)
    print("✅ Финальный тест завершен!")

if __name__ == "__main__":
    test_final_currency()
