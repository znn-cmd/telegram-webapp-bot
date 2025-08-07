#!/usr/bin/env python3
"""
Скрипт для проверки данных валют в базе данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import supabase
import requests
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_currency_data():
    """Проверяет данные валют в базе данных"""
    
    print("🔍 Проверка данных валют в базе данных")
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
        else:
            print("❌ Записи валют не найдены")
    
    except Exception as e:
        print(f"❌ Ошибка при получении данных: {e}")

def test_currency_api():
    """Тестирует API currencylayer.com"""
    
    print("\n🔍 Тестирование API currencylayer.com")
    print("=" * 50)
    
    # API ключ
    CURRENCYLAYER_API_KEY = "c61dddb55d93e77ce5a2c8b91fb22694"
    
    try:
        # Запрос к API
        url = "http://api.currencylayer.com/historical"
        params = {
            'access_key': CURRENCYLAYER_API_KEY,
            'date': '2025-08-07',
            'base': 'EUR',
            'currencies': 'RUB,USD,TRY,AED,THB'
        }
        
        print(f"📡 Запрос к API: {url}")
        print(f"📋 Параметры: {params}")
        
        response = requests.get(url, params=params)
        
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешный ответ от API")
            print(f"📋 Данные ответа: {data}")
            
            if data.get('success'):
                quotes = data.get('quotes', {})
                print(f"\n💱 Полученные курсы:")
                for quote, rate in quotes.items():
                    print(f"   {quote}: {rate}")
            else:
                print(f"❌ Ошибка API: {data.get('error', {})}")
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"📋 Текст ответа: {response.text}")
    
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")

if __name__ == "__main__":
    check_currency_data()
    test_currency_api()

