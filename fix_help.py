#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления файла webapp_help.html
Добавляет правильные атрибуты data-i18n для мультиязычности
"""

import re
from bs4 import BeautifulSoup

def fix_help_file():
    """Исправляет файл webapp_help.html"""
    
    filename = 'webapp_help.html'
    
    print(f"🔍 Исправляем файл: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Добавляем атрибуты data-i18n к элементам
        translations_map = {
            'help_title': 'common.help',
            'about_app_btn': 'common.about_app',
            'instruction_btn': 'common.instruction',
            'geography_btn': 'common.our_geography',
            'support_btn': 'common.technical_support',
            'back_btn': 'common.back'
        }
        
        # Добавляем атрибуты data-i18n к элементам по классу и тексту
        # Находим заголовок "Помощь"
        title_element = soup.find('div', class_='title')
        if title_element and not title_element.get('data-i18n'):
            title_element['data-i18n'] = 'common.help'
            print(f"  ✅ Добавлен атрибут data-i18n: title → common.help")
        
        # Находим кнопки по тексту и добавляем атрибуты
        buttons = soup.find_all('button', class_='help-btn')
        for button in buttons:
            button_text = button.get_text(strip=True)
            if 'О приложении' in button_text and not button.get('data-i18n'):
                button['data-i18n'] = 'common.about_app'
                print(f"  ✅ Добавлен атрибут data-i18n: about_app_btn → common.about_app")
            elif 'Инструкция' in button_text and not button.get('data-i18n'):
                button['data-i18n'] = 'common.instruction'
                print(f"  ✅ Добавлен атрибут data-i18n: instruction_btn → common.instruction")
            elif 'Наша география' in button_text and not button.get('data-i18n'):
                button['data-i18n'] = 'common.our_geography'
                print(f"  ✅ Добавлен атрибут data-i18n: geography_btn → common.our_geography")
            elif 'Техническая поддержка' in button_text and not button.get('data-i18n'):
                button['data-i18n'] = 'common.technical_support'
                print(f"  ✅ Добавлен атрибут data-i18n: support_btn → common.technical_support")
        
        # Находим кнопку "Вернуться в главное меню"
        back_button = soup.find('button', class_='back-btn')
        if back_button and not back_button.get('data-i18n'):
            back_button['data-i18n'] = 'common.back'
            print(f"  ✅ Добавлен атрибут data-i18n: back_btn → common.back")
        
        # Сохраняем файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"  ✅ Файл {filename} исправлен")
        print("  ✅ Добавлены атрибуты data-i18n")
        print("  ✅ Все кнопки раздела помощи теперь поддерживают мультиязычность")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {filename}: {e}")

if __name__ == "__main__":
    fix_help_file()
