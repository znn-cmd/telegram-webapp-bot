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
    
    # Проверяем ChatGPT API ключ
    chatgpt_key = os.getenv('CHATGPT_API_KEY')
    if chatgpt_key:
        print("✅ CHATGPT_API_KEY найден")
        print(f"   Длина ключа: {len(chatgpt_key)} символов")
        print(f"   Начинается с: {chatgpt_key[:10]}...")
    else:
        print("❌ CHATGPT_API_KEY не найден")
        print("   Используйте файл .env или системные переменные")
    
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
    
    # Тестируем функцию перевода
    from api_functions import translate_with_chatgpt
    
    test_text = "Привет, мир! 👋"
    print(f"\n🧪 Тест функции перевода:")
    print(f"   Оригинал: {test_text}")
    
    # Тестируем перевод на английский
    en_translation = translate_with_chatgpt(test_text, 'us')
    print(f"   Английский: {en_translation}")
    
    # Тестируем перевод на французский
    fr_translation = translate_with_chatgpt(test_text, 'ft')
    print(f"   Французский: {fr_translation}")
    
    print("-" * 40)
    print("✅ Тест завершен!")

if __name__ == "__main__":
    test_env_variables() 