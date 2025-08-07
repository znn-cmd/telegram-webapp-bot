#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции валютных курсов
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

# CurrencyLayer API ключ
CURRENCYLAYER_API_KEY = "c61dddb55d93e77ce5a2c8b91fb22694"

def test_currency_api():
    """Тестирует API currencylayer.com"""
    
    print("🔍 Тестирование API currencylayer.com")
    print("=" * 50)
    
    try:
        # Запрос к API
        url = "http://api.currencylayer.com/historical"
        params = {
            'access_key': CURRENCYLAYER_API_KEY,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'base': 'USD',
            'currencies': 'EUR,RUB,TRY,AED,THB'
        }
        
        print(f"📡 Запрос к API: {url}")
        print(f"📋 Параметры: {params}")
        
        response = requests.get(url, params=params)
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешный ответ от API")
            
            if data.get('success'):
                quotes = data.get('quotes', {})
                print(f"\n💱 Полученные курсы (относительно USD):")
                for quote, rate in quotes.items():
                    print(f"   {quote}: {rate}")
                
                # Конвертируем в EUR
                usd_eur_rate = quotes.get('USDEUR', 1.0)
                print(f"\n💱 Конвертация в EUR (курс USD/EUR: {usd_eur_rate}):")
                print(f"   EUR/RUB: {quotes.get('USDRUB', 1.0) / usd_eur_rate:.6f}")
                print(f"   EUR/TRY: {quotes.get('USDTRY', 1.0) / usd_eur_rate:.6f}")
                print(f"   EUR/USD: {1.0 / usd_eur_rate:.6f}")
                print(f"   EUR/AED: {quotes.get('USDAED', 1.0) / usd_eur_rate:.6f}")
                print(f"   EUR/THB: {quotes.get('USDTHB', 1.0) / usd_eur_rate:.6f}")
                
                return True
            else:
                print(f"❌ Ошибка API: {data.get('error', {})}")
                return False
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"📋 Текст ответа: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        return False

def test_currency_table():
    """Тестирует таблицу currency в базе данных"""
    
    print("\n🔍 Тестирование таблицы currency")
    print("=" * 50)
    
    try:
        # Получаем последние записи валют
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(5).execute()
        
        if result.data:
            print(f"✅ Найдено {len(result.data)} записей валют:")
            for i, record in enumerate(result.data, 1):
                print(f"\n📊 Запись {i}:")
                print(f"   ID: {record.get('id')}")
                print(f"   Дата: {record.get('created_at')}")
                print(f"   EUR (базовая): {record.get('euro')}")
                print(f"   TRY: {record.get('try')} (1 EUR = {record.get('try')} TRY)")
                print(f"   USD: {record.get('usd')} (1 EUR = {record.get('usd')} USD)")
                print(f"   RUB: {record.get('rub')} (1 EUR = {record.get('rub')} RUB)")
                print(f"   AED: {record.get('aed')} (1 EUR = {record.get('aed')} AED)")
                print(f"   THB: {record.get('thb')} (1 EUR = {record.get('thb')} THB)")
            return True
        else:
            print("❌ Записи валют не найдены")
            return False
    
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")
        return False

def test_turkish_location_detection():
    """Тестирует определение турецких локаций"""
    
    print("\n🔍 Тестирование определения турецких локаций")
    print("=" * 50)
    
    # Импортируем функцию
    try:
        from currency_functions import is_turkish_location
    except ImportError:
        try:
            from currency_functions_v2 import is_turkish_location
        except ImportError:
            print("❌ Не удалось импортировать функцию is_turkish_location")
            return False
    
    # Тестовые данные
    test_locations = [
        {'country': 'Turkey', 'country_code': 'TR'},
        {'country': 'Türkiye', 'country_code': 'TR'},
        {'country': 'Germany', 'country_code': 'DE'},
        {'country': 'United States', 'country_code': 'US'},
        {'country': 'turkey', 'country_code': 'tr'},
        {'country': 'türkiye', 'country_code': 'tr'},
    ]
    
    for location in test_locations:
        is_turkish = is_turkish_location(location)
        print(f"📍 {location['country']} ({location['country_code']}): {'🇹🇷 Турецкая' if is_turkish else '🌍 Не турецкая'}")
    
    return True

def test_currency_conversion():
    """Тестирует конвертацию валют"""
    
    print("\n🔍 Тестирование конвертации валют")
    print("=" * 50)
    
    # Импортируем функцию
    try:
        from currency_functions import convert_turkish_data_to_eur
    except ImportError:
        try:
            from currency_functions_v2 import convert_turkish_data_to_eur
        except ImportError:
            print("❌ Не удалось импортировать функцию convert_turkish_data_to_eur")
            return False
    
    # Тестовые данные
    test_data = {
        'unit_price_for_sale': 1000.0,
        'min_unit_price_for_sale': 800.0,
        'max_unit_price_for_sale': 1200.0,
        'unit_price_for_rent': 50.0,
        'min_unit_price_for_rent': 40.0,
        'max_unit_price_for_rent': 60.0,
        'price_for_sale': 50000.0,
        'price_for_rent': 2500.0,
        'other_field': 'не конвертируется'
    }
    
    # Тестовый курс валюты (1 EUR = 30 TRY)
    currency_rate = {'try': 30.0}
    
    print(f"📊 Исходные данные (TRY):")
    for key, value in test_data.items():
        if isinstance(value, (int, float)):
            print(f"   {key}: {value} TRY")
    
    # Конвертируем
    converted_data = convert_turkish_data_to_eur(test_data, currency_rate)
    
    print(f"\n💱 Конвертированные данные (EUR):")
    for key, value in converted_data.items():
        if isinstance(value, (int, float)) and key in ['unit_price_for_sale', 'min_unit_price_for_sale', 
                                                      'max_unit_price_for_sale', 'unit_price_for_rent', 
                                                      'min_unit_price_for_rent', 'max_unit_price_for_rent',
                                                      'price_for_sale', 'price_for_rent']:
            print(f"   {key}: {value:.2f} EUR")
        else:
            print(f"   {key}: {value}")
    
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции валютных курсов")
    print("=" * 60)
    
    # Тестируем API
    api_ok = test_currency_api()
    
    # Тестируем таблицу
    table_ok = test_currency_table()
    
    # Тестируем определение турецких локаций
    location_ok = test_turkish_location_detection()
    
    # Тестируем конвертацию валют
    conversion_ok = test_currency_conversion()
    
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    print(f"   API currencylayer.com: {'✅ OK' if api_ok else '❌ FAIL'}")
    print(f"   Таблица currency: {'✅ OK' if table_ok else '❌ FAIL'}")
    print(f"   Определение турецких локаций: {'✅ OK' if location_ok else '❌ FAIL'}")
    print(f"   Конвертация валют: {'✅ OK' if conversion_ok else '❌ FAIL'}")
    
    if all([api_ok, table_ok, location_ok, conversion_ok]):
        print("\n🎉 Все тесты прошли успешно!")
    else:
        print("\n⚠️ Некоторые тесты не прошли. Проверьте логи выше.")
