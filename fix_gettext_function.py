#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления функции getText в webapp_object_evaluation.html
Заменяет все вызовы getText на вызовы i18nManager.getTranslation
"""

import re
from bs4 import BeautifulSoup

def fix_gettext_function():
    """Исправляет функцию getText в файле webapp_object_evaluation.html"""
    
    filename = 'webapp_object_evaluation.html'
    
    print(f"🔍 Исправляем функцию getText в файле: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем все вызовы getText на вызовы i18nManager.getTranslation
        # Используем регулярное выражение для замены getText('key') на window.i18nManager.getTranslation('reports.key')
        
        # Заменяем getText('key') на window.i18nManager.getTranslation('reports.key')
        content = re.sub(
            r'getText\([\'"]([^\'"]+)[\'"]\)',
            r'window.i18nManager ? window.i18nManager.getTranslation("reports.\1") : "\1"',
            content
        )
        
        # Сохраняем файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Файл {filename} исправлен")
        print("  ✅ Все вызовы getText заменены на window.i18nManager.getTranslation")
        print("  ✅ Выпадающие списки теперь должны работать корректно")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {filename}: {e}")

if __name__ == "__main__":
    fix_gettext_function()
