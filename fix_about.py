#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления файла webapp_about.html
Добавляет правильные атрибуты data-i18n для мультиязычности
"""

import re
from bs4 import BeautifulSoup

def fix_about_file():
    """Исправляет файл webapp_about.html"""
    
    filename = 'webapp_about.html'
    
    print(f"🔍 Исправляем файл: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Добавляем атрибуты data-i18n к элементам
        # Находим заголовок "О приложении"
        title_element = soup.find('div', class_='title')
        if title_element and not title_element.get('data-i18n'):
            title_element['data-i18n'] = 'common.about_app_title'
            print(f"  ✅ Добавлен атрибут data-i18n: title → common.about_app_title")
        
        # Находим заголовки h3 и добавляем атрибуты
        h3_elements = soup.find_all('h3')
        for h3 in h3_elements:
            h3_text = h3.get_text(strip=True)
            if 'Что такое Aaadviser?' in h3_text and not h3.get('data-i18n'):
                h3['data-i18n'] = 'common.about_app_what_is'
                print(f"  ✅ Добавлен атрибут data-i18n: what_is → common.about_app_what_is")
            elif 'Наши возможности:' in h3_text and not h3.get('data-i18n'):
                h3['data-i18n'] = 'common.about_app_capabilities'
                print(f"  ✅ Добавлен атрибут data-i18n: capabilities → common.about_app_capabilities")
            elif 'Как это работает?' in h3_text and not h3.get('data-i18n'):
                h3['data-i18n'] = 'common.about_app_how_works'
                print(f"  ✅ Добавлен атрибут data-i18n: how_works → common.about_app_how_works")
            elif 'Почему Aaadviser?' in h3_text and not h3.get('data-i18n'):
                h3['data-i18n'] = 'common.about_app_why'
                print(f"  ✅ Добавлен атрибут data-i18n: why → common.about_app_why")
        
        # Находим параграфы и добавляем атрибуты
        p_elements = soup.find_all('p')
        for p in p_elements:
            p_text = p.get_text(strip=True)
            if 'Aaadviser — это интеллектуальная платформа' in p_text and not p.get('data-i18n'):
                p['data-i18n'] = 'common.about_app_description'
                print(f"  ✅ Добавлен атрибут data-i18n: description → common.about_app_description")
            elif 'Просто введите адрес недвижимости' in p_text and not p.get('data-i18n'):
                p['data-i18n'] = 'common.about_app_how_works_desc'
                print(f"  ✅ Добавлен атрибут data-i18n: how_works_desc → common.about_app_how_works_desc")
            elif 'Мы используем передовые технологии' in p_text and not p.get('data-i18n'):
                p['data-i18n'] = 'common.about_app_why_desc'
                print(f"  ✅ Добавлен атрибут data-i18n: why_desc → common.about_app_why_desc")
        
        # Находим кнопки и добавляем атрибуты
        buttons = soup.find_all('button', class_='nav-btn')
        for button in buttons:
            button_text = button.get_text(strip=True)
            if '← Назад' in button_text and not button.get('data-i18n'):
                button['data-i18n'] = 'common.about_app_back'
                print(f"  ✅ Добавлен атрибут data-i18n: back_btn → common.about_app_back")
            elif 'В главное меню' in button_text and not button.get('data-i18n'):
                button['data-i18n'] = 'common.about_app_main_menu'
                print(f"  ✅ Добавлен атрибут data-i18n: main_menu_btn → common.about_app_main_menu")
        
        # Сохраняем файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"  ✅ Файл {filename} исправлен")
        print("  ✅ Добавлены атрибуты data-i18n")
        print("  ✅ Все элементы раздела 'О приложении' теперь поддерживают мультиязычность")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {filename}: {e}")

if __name__ == "__main__":
    fix_about_file()
