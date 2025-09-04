#!/usr/bin/env python3
"""
Скрипт для исправления дублированных data-i18n атрибутов в HTML файлах
"""

import os
import re
import glob

def fix_duplicate_data_i18n():
    """Исправляет дублированные data-i18n атрибуты в HTML файлах"""
    html_files = []
    html_files.extend(glob.glob("webapp_*.html"))
    
    for html_file in html_files:
        print(f"Обрабатываем файл: {html_file}")
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Исправляем дублированные data-i18n атрибуты
            content = fix_duplicate_attributes(content)
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Файл {html_file} исправлен")
        except Exception as e:
            print(f"❌ Ошибка обработки файла {html_file}: {e}")

def fix_duplicate_attributes(content):
    """Исправляет дублированные атрибуты data-i18n"""
    
    # Паттерн для поиска дублированных data-i18n атрибутов
    pattern = r'data-i18n="([^"]+)"\s+data-i18n="([^"]+)"'
    
    def replace_duplicates(match):
        # Берем первый атрибут, игнорируем дублированные
        return f'data-i18n="{match.group(1)}"'
    
    # Заменяем дублированные атрибуты
    content = re.sub(pattern, replace_duplicates, content)
    
    # Также исправляем множественные дублирования
    pattern_multiple = r'(data-i18n="[^"]+")\s+\1'
    while re.search(pattern_multiple, content):
        content = re.sub(pattern_multiple, r'\1', content)
    
    return content

def main():
    print("🔧 Исправляем дублированные data-i18n атрибуты...")
    
    if not os.path.exists('app.py'):
        print("❌ Файл app.py не найден. Убедитесь, что вы находитесь в корневой директории проекта.")
        return
    
    fix_duplicate_data_i18n()
    
    print("✅ Исправление завершено!")
    print("\n📝 Следующие шаги:")
    print("1. Проверьте исправленные HTML файлы")
    print("2. Обновите Docker образ на Amvera")
    print("3. Протестируйте мультиязычность")

if __name__ == "__main__":
    main()
