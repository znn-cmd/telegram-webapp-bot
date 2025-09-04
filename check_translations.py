#!/usr/bin/env python3
"""
Скрипт для проверки переводов в i18n-manager.js
"""

import re
import os

def extract_translation_keys():
    """Извлекает все ключи переводов из HTML файлов"""
    keys = set()
    
    # Поиск всех data-i18n атрибутов
    html_files = [f for f in os.listdir('.') if f.endswith('.html')]
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Находим все data-i18n атрибуты
            matches = re.findall(r'data-i18n="([^"]+)"', content)
            keys.update(matches)
            
        except Exception as e:
            print(f"Ошибка чтения {html_file}: {e}")
    
    return sorted(list(keys))

def check_translation_exists(key, content):
    """Проверяет, существует ли перевод для ключа"""
    # Разбиваем ключ на части (например, 'main.title' -> ['main', 'title'])
    parts = key.split('.')
    
    # Ищем секцию для каждого языка
    languages = ['ru', 'en', 'de', 'fr', 'tr']
    
    for lang in languages:
        # Ищем секцию языка
        lang_pattern = rf"'{lang}': \{{([^}}]*)\}}"
        lang_match = re.search(lang_pattern, content, re.DOTALL)
        
        if lang_match:
            lang_content = lang_match.group(1)
            
            # Ищем первую категорию
            if len(parts) >= 2:
                category = parts[0]
                subkey = parts[1]
                
                # Ищем секцию категории
                category_pattern = rf"'{category}': \{{([^}}]*)\}}"
                category_match = re.search(category_pattern, lang_content, re.DOTALL)
                
                if category_match:
                    category_content = category_match.group(1)
                    
                    # Ищем ключ в категории
                    key_pattern = rf"'{subkey}': '[^']*'"
                    if re.search(key_pattern, category_content):
                        return True
    
    return False

def main():
    print("🔍 Проверяем переводы в i18n-manager.js...")
    
    # Получаем все ключи из HTML
    all_keys = extract_translation_keys()
    
    # Читаем i18n-manager.js
    try:
        with open('i18n-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Ошибка чтения i18n-manager.js: {e}")
        return
    
    print(f"Найдено {len(all_keys)} ключей переводов в HTML файлах")
    
    # Проверяем каждый ключ
    missing_keys = []
    existing_keys = []
    
    for key in all_keys:
        if check_translation_exists(key, content):
            existing_keys.append(key)
        else:
            missing_keys.append(key)
    
    print(f"✅ Существует: {len(existing_keys)} ключей")
    print(f"❌ Отсутствует: {len(missing_keys)} ключей")
    
    if missing_keys:
        print("\n📝 Отсутствующие ключи:")
        for key in missing_keys:
            print(f"  - {key}")
    
    # Проверяем конкретные ключи из скриншота
    screenshot_keys = [
        'main.title',
        'reports.region_analytics', 
        'reports.property_evaluation',
        'reports.title',
        'profile.title',
        'common.help'
    ]
    
    print(f"\n🔍 Проверка ключей из скриншота:")
    for key in screenshot_keys:
        exists = check_translation_exists(key, content)
        status = "✅" if exists else "❌"
        print(f"  {status} {key}")

if __name__ == "__main__":
    main()
