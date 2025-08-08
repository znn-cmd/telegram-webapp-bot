#!/usr/bin/env python3
"""
Полный тест для проверки работы валютных функций
Проверяет заполнение всех полей валют и корректность данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from datetime import datetime
from currency_functions_v2 import (
    get_currency_rate_for_date,
    fetch_and_save_currency_rates,
    get_latest_currency_rate
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_currency_complete():
    """Полный тест валютных функций"""
    
    print("🔍 Полный тест валютных функций")
    print("=" * 50)
    
    # Тест 1: Получение последней записи
    print("\n1️⃣ Тест получения последней записи валют")
    print("-" * 30)
    
    latest_rate = get_latest_currency_rate()
    if latest_rate:
        print("✅ Последняя запись получена успешно")
        required_fields = ['rub', 'usd', 'euro', 'try', 'aed', 'thb']
        for field in required_fields:
            if field in latest_rate and latest_rate[field] is not None:
                print(f"   ✅ {field}: {latest_rate[field]} ({type(latest_rate[field]).__name__})")
            else:
                print(f"   ❌ {field}: отсутствует или NULL")
    else:
        print("❌ Не удалось получить последнюю запись")
    
    # Тест 2: Получение курса для текущей даты
    print("\n2️⃣ Тест получения курса для текущей даты")
    print("-" * 30)
    
    current_rate = get_currency_rate_for_date()
    if current_rate:
        print("✅ Курс для текущей даты получен успешно")
        required_fields = ['rub', 'usd', 'euro', 'try', 'aed', 'thb']
        for field in required_fields:
            if field in current_rate and current_rate[field] is not None:
                print(f"   ✅ {field}: {current_rate[field]} ({type(current_rate[field]).__name__})")
            else:
                print(f"   ❌ {field}: отсутствует или NULL")
    else:
        print("❌ Не удалось получить курс для текущей даты")
    
    # Тест 3: Принудительное получение новых курсов
    print("\n3️⃣ Тест принудительного получения новых курсов")
    print("-" * 30)
    
    new_rate = fetch_and_save_currency_rates()
    if new_rate:
        print("✅ Новые курсы получены успешно")
        required_fields = ['rub', 'usd', 'euro', 'try', 'aed', 'thb']
        for field in required_fields:
            if field in new_rate and new_rate[field] is not None:
                print(f"   ✅ {field}: {new_rate[field]} ({type(new_rate[field]).__name__})")
            else:
                print(f"   ❌ {field}: отсутствует или NULL")
    else:
        print("❌ Не удалось получить новые курсы")
    
    # Тест 4: Валидация данных
    print("\n4️⃣ Тест валидации данных")
    print("-" * 30)
    
    test_data = new_rate if new_rate else current_rate if current_rate else latest_rate
    
    if test_data:
        print("✅ Данные для валидации получены")
        
        # Проверяем все обязательные поля
        required_fields = ['rub', 'usd', 'euro', 'try', 'aed', 'thb']
        missing_fields = []
        null_fields = []
        invalid_fields = []
        
        for field in required_fields:
            if field not in test_data:
                missing_fields.append(field)
            elif test_data[field] is None:
                null_fields.append(field)
            elif not isinstance(test_data[field], (int, float)) or test_data[field] <= 0:
                invalid_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ Отсутствующие поля: {missing_fields}")
        else:
            print("   ✅ Все обязательные поля присутствуют")
        
        if null_fields:
            print(f"   ❌ NULL значения в полях: {null_fields}")
        else:
            print("   ✅ Все поля заполнены")
        
        if invalid_fields:
            print(f"   ❌ Некорректные значения в полях: {invalid_fields}")
        else:
            print("   ✅ Все значения корректные")
        
        # Проверяем типы данных
        print("   📋 Типы данных:")
        for field in required_fields:
            if field in test_data:
                value = test_data[field]
                value_type = type(value).__name__
                print(f"      {field}: {value_type} = {value}")
        
        # Проверяем логику курсов валют
        if all(field in test_data for field in ['euro', 'try', 'usd', 'rub', 'aed', 'thb']):
            euro = test_data['euro']
            if euro != 1.0:
                print(f"   ⚠️ EUR не равен 1.0: {euro}")
            else:
                print(f"   ✅ EUR = 1.0 (базовая валюта)")
    else:
        print("❌ Нет данных для валидации")
    
    print("\n" + "=" * 50)
    print("🏁 Тест завершен")

if __name__ == "__main__":
    test_currency_complete()
