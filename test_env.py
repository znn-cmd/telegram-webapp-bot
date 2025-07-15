#!/usr/bin/env python3
"""
Тест для проверки работы с переменными окружения
"""

import os
from dotenv import load_dotenv

def test_env_variables():
    """Тестирует загрузку переменных окружения"""
    
    # Загружаем переменные из .env файла
    load_dotenv()
    
    print("🔍 Проверка переменных окружения:")
    print("-" * 40)
    
    # Проверяем ChatGPT API ключ (теперь из базы данных)
    print("ℹ️  ChatGPT API ключ теперь управляется через админ панель")
    print("   Откройте админ панель -> API Ключи для настройки")
    
    # Проверяем Supabase настройки
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        print("✅ Supabase настройки найдены")
    else:
        print("⚠️  Supabase настройки не найдены (не критично для тестирования)")
    
    # Проверяем Telegram Bot Token
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if bot_token:
        print("✅ TELEGRAM_BOT_TOKEN найден")
    else:
        print("⚠️  TELEGRAM_BOT_TOKEN не найден (не критично для тестирования)")
    
    print("-" * 40)
    
    # Тестируем функцию перевода (теперь из базы данных)
    print(f"\n🧪 Тест функции перевода:")
    print(f"   Функция перевода теперь использует ключи из базы данных")
    print(f"   Настройте ключи через админ панель для полной функциональности")
    
    print("-" * 40)
    print("✅ Тест завершен!")

if __name__ == "__main__":
    test_env_variables() 