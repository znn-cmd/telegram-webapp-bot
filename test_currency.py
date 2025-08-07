#!/usr/bin/env python3
"""
Тестовый файл для проверки функций работы с валютами
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_currency_functions():
    """Тестирует функции работы с валютами"""
    
    try:
        # Импортируем функции из currency_functions
        from currency_functions import (
            get_currency_rates, 
            format_currency_rates_for_report, 
            convert_market_data_to_euro,
            convert_to_euro
        )
        
        print("🔄 Тестирование функций работы с валютами...")
        
        # Тест 1: Получение курсов валют
        print("\n1️⃣ Тест получения курсов валют:")
        currency_rates = get_currency_rates()
        if currency_rates:
            print(f"✅ Курсы валют получены: {currency_rates}")
        else:
            print("❌ Не удалось получить курсы валют")
            return
        
        # Тест 2: Форматирование курсов валют
        print("\n2️⃣ Тест форматирования курсов валют:")
        formatted_rates = format_currency_rates_for_report(currency_rates)
        print(f"✅ Отформатированные курсы: {formatted_rates}")
        
        # Тест 3: Конвертация в евро
        print("\n3️⃣ Тест конвертации в евро:")
        test_value = 1000  # 1000 TRY
        converted_value = convert_to_euro(test_value, 'TRY', currency_rates)
        print(f"✅ {test_value} TRY = {converted_value:.2f} EUR")
        
        # Тест 4: Конвертация данных рынка
        print("\n4️⃣ Тест конвертации данных рынка:")
        test_market_data = {
            'general_data': {
                'unit_price_for_sale': 5000,  # 5000 TRY/м²
                'unit_price_for_rent': 200,   # 200 TRY/м²
                'price_for_sale': 500000,     # 500000 TRY
                'price_for_rent': 20000       # 20000 TRY
            }
        }
        
        converted_market_data = convert_market_data_to_euro(test_market_data, currency_rates)
        print("✅ Конвертированные данные рынка:")
        for key, value in converted_market_data['general_data'].items():
            print(f"   {key}: {value}")
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    test_currency_functions()
