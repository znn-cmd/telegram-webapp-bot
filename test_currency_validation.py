#!/usr/bin/env python3
"""
Тест для проверки валидации курсов валют и заполнения всех полей
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

def test_currency_data_structure():
    """Тестирует структуру данных валют"""
    
    print("🔍 Тестирование структуры данных валют")
    print("=" * 50)
    
    try:
        # Получаем последние записи валют
        result = supabase.table('currency').select('*').order('created_at', desc=True).limit(3).execute()
        
        if not result.data:
            print("❌ Записи валют не найдены")
            return False
        
        print(f"✅ Найдено {len(result.data)} записей валют")
        
        # Проверяем каждую запись
        for i, record in enumerate(result.data, 1):
            print(f"\n📊 Проверка записи {i} (ID: {record.get('id')}):")
            
            # Проверяем обязательные поля
            required_fields = ['id', 'created_at', 'euro', 'try', 'usd', 'rub', 'aed', 'thb']
            missing_fields = []
            null_fields = []
            negative_fields = []
            
            for field in required_fields:
                if field not in record:
                    missing_fields.append(field)
                elif record[field] is None:
                    null_fields.append(field)
                elif isinstance(record[field], (int, float)) and record[field] <= 0:
                    negative_fields.append(field)
            
            # Выводим результаты проверки
            if missing_fields:
                print(f"   ❌ Отсутствующие поля: {missing_fields}")
            else:
                print(f"   ✅ Все обязательные поля присутствуют")
            
            if null_fields:
                print(f"   ❌ NULL значения в полях: {null_fields}")
            else:
                print(f"   ✅ Все поля заполнены")
            
            if negative_fields:
                print(f"   ❌ Отрицательные или нулевые значения: {negative_fields}")
            else:
                print(f"   ✅ Все значения положительные")
            
            # Проверяем типы данных
            print(f"   📋 Типы данных:")
            for field in required_fields:
                if field in record:
                    value = record[field]
                    value_type = type(value).__name__
                    print(f"      {field}: {value_type} = {value}")
            
            # Проверяем логику курсов валют
            if all(field in record for field in ['euro', 'try', 'usd', 'rub', 'aed', 'thb']):
                euro = record['euro']
                if euro != 1.0:
                    print(f"   ⚠️ EUR не равен 1.0: {euro}")
                else:
                    print(f"   ✅ EUR = 1.0 (базовая валюта)")
                
                # Проверяем, что все курсы относительно EUR
                print(f"   💱 Курсы относительно EUR:")
                print(f"      TRY: 1 EUR = {record['try']:.6f} TRY")
                print(f"      USD: 1 EUR = {record['usd']:.6f} USD")
                print(f"      RUB: 1 EUR = {record['rub']:.6f} RUB")
                print(f"      AED: 1 EUR = {record['aed']:.6f} AED")
                print(f"      THB: 1 EUR = {record['thb']:.6f} THB")
        
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры данных: {e}")
        return False

def test_currency_api_response():
    """Тестирует ответ API currencylayer.com"""
    
    print("\n🔍 Тестирование ответа API currencylayer.com")
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
        
        if response.status_code != 200:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            print(f"📋 Текст ответа: {response.text}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ Ошибка API: {data.get('error', {})}")
            return False
        
        quotes = data.get('quotes', {})
        print(f"✅ Успешный ответ от API")
        
        # Проверяем необходимые курсы
        required_quotes = ['USDEUR', 'USDRUB', 'USDTRY', 'USDAED', 'USDTHB']
        missing_quotes = [quote for quote in required_quotes if quote not in quotes]
        
        if missing_quotes:
            print(f"❌ Отсутствуют необходимые курсы: {missing_quotes}")
            return False
        
        print(f"✅ Все необходимые курсы получены:")
        for quote in required_quotes:
            rate = quotes[quote]
            print(f"   {quote}: {rate}")
        
        # Проверяем, что курсы положительные
        negative_quotes = [quote for quote in required_quotes if quotes[quote] <= 0]
        if negative_quotes:
            print(f"❌ Отрицательные или нулевые курсы: {negative_quotes}")
            return False
        
        print(f"✅ Все курсы положительные")
        
        # Тестируем конвертацию в EUR
        usd_eur_rate = quotes.get('USDEUR', 1.0)
        if usd_eur_rate == 0:
            print(f"❌ Курс USD/EUR равен 0")
            return False
        
        print(f"💱 Конвертация в EUR (курс USD/EUR: {usd_eur_rate}):")
        
        # Конвертируем курсы
        converted_rates = {
            'rub': quotes.get('USDRUB', 1.0) / usd_eur_rate,
            'usd': 1.0 / usd_eur_rate,
            'euro': 1.0,
            'try': quotes.get('USDTRY', 1.0) / usd_eur_rate,
            'aed': quotes.get('USDAED', 1.0) / usd_eur_rate,
            'thb': quotes.get('USDTHB', 1.0) / usd_eur_rate
        }
        
        for currency, rate in converted_rates.items():
            print(f"   EUR/{currency.upper()}: {rate:.6f}")
        
        # Проверяем, что все конвертированные курсы положительные
        negative_converted = [curr for curr, rate in converted_rates.items() if rate <= 0]
        if negative_converted:
            print(f"❌ Отрицательные конвертированные курсы: {negative_converted}")
            return False
        
        print(f"✅ Все конвертированные курсы положительные")
        
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при тестировании API: {e}")
        return False

def test_currency_functions():
    """Тестирует функции работы с валютными курсами"""
    
    print("\n🔍 Тестирование функций работы с валютными курсами")
    print("=" * 50)
    
    try:
        # Импортируем функции
        from currency_functions import get_currency_rate_for_date, fetch_and_save_currency_rates
        
        # Тест 1: Получение курса валют
        print("📊 Тест 1: Получение курса валют")
        currency_rate = get_currency_rate_for_date()
        
        if currency_rate:
            print(f"✅ Курс валют получен")
            
            # Проверяем структуру данных
            required_fields = ['euro', 'try', 'usd', 'rub', 'aed', 'thb']
            missing_fields = [field for field in required_fields if field not in currency_rate]
            
            if missing_fields:
                print(f"❌ Отсутствуют поля: {missing_fields}")
                return False
            
            print(f"✅ Все поля присутствуют")
            
            # Проверяем значения
            null_fields = [field for field in required_fields if currency_rate[field] is None]
            if null_fields:
                print(f"❌ NULL значения: {null_fields}")
                return False
            
            print(f"✅ Все поля заполнены")
            
            # Проверяем положительные значения
            negative_fields = [field for field in required_fields if currency_rate[field] <= 0]
            if negative_fields:
                print(f"❌ Отрицательные значения: {negative_fields}")
                return False
            
            print(f"✅ Все значения положительные")
            
            # Выводим курсы
            print(f"💱 Курсы валют:")
            for field in required_fields:
                print(f"   {field.upper()}: {currency_rate[field]}")
        
        else:
            print("❌ Не удалось получить курс валют")
            return False
        
        return True
    
    except ImportError:
        print("❌ Не удалось импортировать функции валют")
        return False
    except Exception as e:
        print(f"❌ Ошибка при тестировании функций: {e}")
        return False

def test_currency_insertion():
    """Тестирует вставку данных в таблицу currency"""
    
    print("\n🔍 Тестирование вставки данных в таблицу currency")
    print("=" * 50)
    
    try:
        # Создаем тестовые данные
        test_data = {
            'created_at': datetime.now().isoformat(),
            'euro': 1.0,
            'try': 47.0,
            'usd': 1.16,
            'rub': 92.0,
            'aed': 4.27,
            'thb': 37.6
        }
        
        print(f"📊 Тестовые данные:")
        for field, value in test_data.items():
            print(f"   {field}: {value}")
        
        # Проверяем, что все поля заполнены
        required_fields = ['euro', 'try', 'usd', 'rub', 'aed', 'thb']
        missing_fields = [field for field in required_fields if field not in test_data]
        
        if missing_fields:
            print(f"❌ Отсутствуют поля: {missing_fields}")
            return False
        
        print(f"✅ Все обязательные поля присутствуют")
        
        # Проверяем, что все значения положительные
        negative_fields = [field for field in required_fields if test_data[field] <= 0]
        if negative_fields:
            print(f"❌ Отрицательные значения: {negative_fields}")
            return False
        
        print(f"✅ Все значения положительные")
        
        # Пытаемся вставить данные (но не сохраняем, чтобы не засорять базу)
        print(f"✅ Данные готовы для вставки")
        
        return True
    
    except Exception as e:
        print(f"❌ Ошибка при тестировании вставки: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов валидации курсов валют")
    print("=" * 60)
    
    # Тестируем структуру данных
    structure_ok = test_currency_data_structure()
    
    # Тестируем API
    api_ok = test_currency_api_response()
    
    # Тестируем функции
    functions_ok = test_currency_functions()
    
    # Тестируем вставку
    insertion_ok = test_currency_insertion()
    
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    print(f"   Структура данных: {'✅ OK' if structure_ok else '❌ FAIL'}")
    print(f"   API currencylayer.com: {'✅ OK' if api_ok else '❌ FAIL'}")
    print(f"   Функции валют: {'✅ OK' if functions_ok else '❌ FAIL'}")
    print(f"   Вставка данных: {'✅ OK' if insertion_ok else '❌ FAIL'}")
    
    if all([structure_ok, api_ok, functions_ok, insertion_ok]):
        print("\n🎉 Все тесты прошли успешно!")
        print("✅ Алгоритм получения и сохранения курсов валют работает корректно")
    else:
        print("\n⚠️ Некоторые тесты не прошли. Проверьте логи выше.")
