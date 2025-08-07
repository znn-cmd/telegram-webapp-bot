#!/usr/bin/env python3
"""
Скрипт для принудительного заполнения валют на сегодняшнюю дату
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from currency_functions import fetch_and_save_currency_rates, get_currency_rate_for_date
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def fill_currency_today():
    """Принудительно заполняет валюты на сегодняшнюю дату"""
    
    print("💱 Принудительное заполнение валют на сегодняшнюю дату")
    print("=" * 60)
    
    # Получаем сегодняшнюю дату
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    
    print(f"📅 Дата: {date_str}")
    
    # Проверяем, есть ли уже запись для сегодня
    print("\n1️⃣ Проверяем существующие записи:")
    existing_rate = get_currency_rate_for_date(today)
    
    if existing_rate:
        print(f"✅ Найдена существующая запись:")
        print(f"   ID: {existing_rate.get('id', 'н/д')}")
        print(f"   EUR (базовая): {existing_rate.get('euro', 'н/д')}")
        print(f"   TRY: {existing_rate.get('try', 'н/д')} (1 EUR = {existing_rate.get('try', 'н/д')} TRY)")
        print(f"   USD: {existing_rate.get('usd', 'н/д')} (1 EUR = {existing_rate.get('usd', 'н/д')} USD)")
        print(f"   RUB: {existing_rate.get('rub', 'н/д')} (1 EUR = {existing_rate.get('rub', 'н/d')} RUB)")
        print(f"   AED: {existing_rate.get('aed', 'н/д')} (1 EUR = {existing_rate.get('aed', 'н/d')} AED)")
        print(f"   THB: {existing_rate.get('thb', 'н/д')} (1 EUR = {existing_rate.get('thb', 'н/d')} THB)")
    else:
        print("❌ Запись для сегодня не найдена")
    
    # Принудительно получаем свежие курсы
    print(f"\n2️⃣ Получаем свежие курсы валют с API:")
    fresh_rate = fetch_and_save_currency_rates(today)
    
    if fresh_rate:
        print(f"✅ Свежие курсы получены:")
        print(f"   EUR (базовая): {fresh_rate.get('euro', 'н/д')}")
        print(f"   TRY: {fresh_rate.get('try', 'н/д')} (1 EUR = {fresh_rate.get('try', 'н/d')} TRY)")
        print(f"   USD: {fresh_rate.get('usd', 'н/d')} (1 EUR = {fresh_rate.get('usd', 'н/d')} USD)")
        print(f"   RUB: {fresh_rate.get('rub', 'н/d')} (1 EUR = {fresh_rate.get('rub', 'н/d')} RUB)")
        print(f"   AED: {fresh_rate.get('aed', 'н/d')} (1 EUR = {fresh_rate.get('aed', 'н/d')} AED)")
        print(f"   THB: {fresh_rate.get('thb', 'н/d')} (1 EUR = {fresh_rate.get('thb', 'н/d')} THB)")
    else:
        print("❌ Не удалось получить свежие курсы")
        return False
    
    # Проверяем результат
    print(f"\n3️⃣ Проверяем результат:")
    final_rate = get_currency_rate_for_date(today)
    
    if final_rate:
        print(f"✅ Запись успешно создана/обновлена:")
        print(f"   ID: {final_rate.get('id', 'н/d')}")
        print(f"   Дата: {final_rate.get('created_at', 'н/d')}")
        print(f"   TRY: {final_rate.get('try', 'н/d')} (1 EUR = {final_rate.get('try', 'н/d')} TRY)")
        return True
    else:
        print("❌ Запись не найдена после создания")
        return False

if __name__ == "__main__":
    success = fill_currency_today()
    if success:
        print("\n" + "=" * 60)
        print("✅ Валюты успешно заполнены!")
    else:
        print("\n" + "=" * 60)
        print("❌ Ошибка при заполнении валют!")
