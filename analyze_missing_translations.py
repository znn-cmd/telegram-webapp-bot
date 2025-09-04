#!/usr/bin/env python3
"""
Скрипт для добавления недостающих переводов в i18n-manager.js
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

def get_existing_keys():
    """Получает существующие ключи из i18n-manager.js"""
    existing_keys = set()
    
    try:
        with open('i18n-manager.js', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Находим все ключи в формате 'key': 'value'
        matches = re.findall(r"'([^']+)': '[^']*'", content)
        existing_keys.update(matches)
        
    except Exception as e:
        print(f"Ошибка чтения i18n-manager.js: {e}")
    
    return existing_keys

def generate_missing_translations():
    """Генерирует недостающие переводы"""
    all_keys = extract_translation_keys()
    existing_keys = get_existing_keys()
    
    missing_keys = [key for key in all_keys if key not in existing_keys]
    
    print(f"Найдено {len(all_keys)} ключей переводов")
    print(f"Существует {len(existing_keys)} ключей")
    print(f"Отсутствует {len(missing_keys)} ключей")
    
    # Группируем ключи по категориям
    categories = {}
    for key in missing_keys:
        if '.' in key:
            category, subkey = key.split('.', 1)
            if category not in categories:
                categories[category] = []
            categories[category].append(subkey)
        else:
            if 'common' not in categories:
                categories['common'] = []
            categories['common'].append(key)
    
    return categories

def main():
    print("🔍 Анализируем недостающие переводы...")
    
    categories = generate_missing_translations()
    
    print("\n📝 Недостающие ключи по категориям:")
    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            print(f"  '{key}': 'НЕОБХОДИМ ПЕРЕВОД',")
    
    print(f"\n✅ Анализ завершен!")
    print("Добавьте недостающие переводы в i18n-manager.js")

if __name__ == "__main__":
    main()
