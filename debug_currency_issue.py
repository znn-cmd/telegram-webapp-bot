#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с валютными курсами
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import get_currency_rate_for_date, fetch_and_save_currency_rates, supabase
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def debug_currency_issue():
    """Диагностирует проблемы с валютными курсами"""
    
    print("🔍 Диагностика проблем с валютными курсами")
    print("=" * 50)
    
    # Проверяем текущую дату
    current_date = datetime.now()
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"📅 Текущая дата: {date_str}")
    
    # Проверяем существующие записи в базе
    print("\n1️⃣ Проверка существующих записей в базе:")
    try:
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(5).execute()
        if result.data:
            print(f"✅ Найдено {len(result.data)} записей:")
            for i, record in enumerate(result.data, 1):
                print(f"   {i}. ID: {record.get('id')}, Дата: {record.get('created_at')}, TRY: {record.get('try')}")
        else:
            print("❌ Записи не найдены")
    except Exception as e:
        print(f"❌ Ошибка при получении записей: {e}")
    
    # Проверяем записи за сегодня
    print(f"\n2️⃣ Проверка записей за сегодня ({date_str}):")
    try:
        today_query = supabase.table('currency').select('*').gte('created_at', f'{date_str} 00:00:00').lt('created_at', f'{date_str} 23:59:59').execute()
        if today_query.data:
            print(f"✅ Найдено {len(today_query.data)} записей за сегодня:")
            for record in today_query.data:
                print(f"   ID: {record.get('id')}, TRY: {record.get('try')}, USD: {record.get('usd')}, RUB: {record.get('rub')}")
        else:
            print("❌ Записей за сегодня не найдено")
    except Exception as e:
        print(f"❌ Ошибка при проверке записей за сегодня: {e}")
    
    # Тестируем получение курса валют
    print(f"\n3️⃣ Тестирование получения курса валют:")
    try:
        currency_rate = get_currency_rate_for_date()
        if currency_rate:
            print(f"✅ Курс валют получен:")
            print(f"   EUR: {currency_rate.get('euro')}")
            print(f"   TRY: {currency_rate.get('try')}")
            print(f"   USD: {currency_rate.get('usd')}")
            print(f"   RUB: {currency_rate.get('rub')}")
            print(f"   AED: {currency_rate.get('aed')}")
            print(f"   THB: {currency_rate.get('thb')}")
        else:
            print("❌ Не удалось получить курс валют")
    except Exception as e:
        print(f"❌ Ошибка при получении курса валют: {e}")
    
    # Тестируем API напрямую
    print(f"\n4️⃣ Тестирование API currencylayer.com:")
    try:
        import requests
        url = "http://api.currencylayer.com/historical"
        params = {
            'access_key': 'c61dddb55d93e77ce5a2c8b91fb22694',
            'date': date_str,
            'base': 'USD',
            'currencies': 'EUR,RUB,TRY,AED,THB'
        }
        
        print(f"📡 Запрос к API: {url}")
        print(f"📋 Параметры: {params}")
        
        response = requests.get(url, params=params)
        print(f"📊 Статус ответа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                quotes = data.get('quotes', {})
                print(f"✅ API ответ успешен:")
                for quote, rate in quotes.items():
                    print(f"   {quote}: {rate}")
            else:
                print(f"❌ API ошибка: {data.get('error', {})}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"📋 Текст ответа: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
    
    # Проверяем структуру таблицы
    print(f"\n5️⃣ Проверка структуры таблицы currency:")
    try:
        # Пытаемся получить одну запись для анализа структуры
        sample = supabase.table('currency').select('*').limit(1).execute()
        if sample.data:
            record = sample.data[0]
            print(f"✅ Структура таблицы:")
            for key, value in record.items():
                print(f"   {key}: {type(value).__name__} = {value}")
        else:
            print("❌ Не удалось получить образец записи")
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Диагностика завершена!")

if __name__ == "__main__":
    debug_currency_issue()
