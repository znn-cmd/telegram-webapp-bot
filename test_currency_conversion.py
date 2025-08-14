#!/usr/bin/env python3
"""
Тест конвертации валют для объектов в Турции
"""

import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import is_turkish_location, get_current_currency_rate, convert_turkish_data_to_eur

def test_turkish_location_detection():
    """Тест определения турецкой локации"""
    print("🧪 Тест определения турецкой локации")
    
    # Тестовые данные
    test_cases = [
        {'country': 'Turkey', 'country_code': 'TR'},
        {'country': 'Türkiye', 'country_code': 'TR'},
        {'country': 'Germany', 'country_code': 'DE'},
        {'country': 'France', 'country_code': 'FR'},
        {'country': '', 'country_code': ''},
        None
    ]
    
    for i, test_case in enumerate(test_cases):
        result = is_turkish_location(test_case)
        print(f"  Тест {i+1}: {test_case} -> {'🇹🇷 Турция' if result else '🌍 Другая страна'}")
    
    print()

def test_currency_rate_retrieval():
    """Тест получения курса валют"""
    print("💱 Тест получения курса валют")
    
    try:
        currency_rate = get_current_currency_rate()
        if currency_rate:
            print(f"  ✅ Курс валют получен:")
            print(f"    - Дата: {currency_rate.get('created_at', 'Не указана')}")
            print(f"    - TRY/EUR: {currency_rate.get('try', 'Не указан')}")
            print(f"    - USD/EUR: {currency_rate.get('usd', 'Не указан')}")
            print(f"    - RUB/EUR: {currency_rate.get('rub', 'Не указан')}")
        else:
            print("  ❌ Не удалось получить курс валют")
    except Exception as e:
        print(f"  ❌ Ошибка получения курса валют: {e}")
    
    print()

def test_currency_conversion():
    """Тест конвертации данных из TRY в EUR"""
    print("🔄 Тест конвертации данных из TRY в EUR")
    
    # Тестовые данные (цены в турецких лирах)
    test_data = {
        'unit_price_for_sale': 50000,  # 50,000 TRY за м²
        'min_unit_price_for_sale': 40000,  # 40,000 TRY за м²
        'max_unit_price_for_sale': 60000,  # 60,000 TRY за м²
        'unit_price_for_rent': 2000,  # 2,000 TRY за м²
        'nested_data': {
            'price_for_sale': 5000000,  # 5,000,000 TRY
            'price_for_rent': 200000   # 200,000 TRY
        }
    }
    
    # Тестовый курс валют (1 EUR = 35 TRY)
    test_currency_rate = {
        'try': 35.0,
        'usd': 1.08,
        'euro': 1.0,
        'created_at': '2024-01-01T00:00:00Z'
    }
    
    try:
        converted_data = convert_turkish_data_to_eur(test_data, test_currency_rate)
        
        print(f"  📊 Исходные данные (TRY):")
        print(f"    - Цена продажи за м²: {test_data['unit_price_for_sale']:,} TRY")
        print(f"    - Мин. цена за м²: {test_data['min_unit_price_for_sale']:,} TRY")
        print(f"    - Макс. цена за м²: {test_data['max_unit_price_for_sale']:,} TRY")
        print(f"    - Цена аренды за м²: {test_data['unit_price_for_rent']:,} TRY")
        print(f"    - Цена продажи: {test_data['nested_data']['price_for_sale']:,} TRY")
        print(f"    - Цена аренды: {test_data['nested_data']['price_for_rent']:,} TRY")
        
        print(f"  💱 Конвертированные данные (EUR):")
        print(f"    - Цена продажи за м²: €{converted_data['unit_price_for_sale']:,.2f}")
        print(f"    - Мин. цена за м²: €{converted_data['min_unit_price_for_sale']:,.2f}")
        print(f"    - Макс. цена за м²: €{converted_data['max_unit_price_for_sale']:,.2f}")
        print(f"    - Цена аренды за м²: €{converted_data['unit_price_for_rent']:,.2f}")
        print(f"    - Цена продажи: €{converted_data['nested_data']['price_for_sale']:,.2f}")
        print(f"    - Цена аренды: €{converted_data['nested_data']['price_for_rent']:,.2f}")
        
        # Проверяем корректность конвертации
        expected_price = 50000 / 35.0
        actual_price = converted_data['unit_price_for_sale']
        if abs(expected_price - actual_price) < 0.01:
            print("  ✅ Конвертация корректна")
        else:
            print(f"  ❌ Ошибка конвертации: ожидалось {expected_price:.2f}, получено {actual_price:.2f}")
            
    except Exception as e:
        print(f"  ❌ Ошибка конвертации: {e}")
    
    print()

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов конвертации валют")
    print("=" * 50)
    
    test_turkish_location_detection()
    test_currency_rate_retrieval()
    test_currency_conversion()
    
    print("🏁 Тестирование завершено")

if __name__ == "__main__":
    main()
