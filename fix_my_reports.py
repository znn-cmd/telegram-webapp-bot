#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления файла webapp_my_reports.html
Удаляет конфликтующий код переводов и добавляет правильные атрибуты data-i18n
"""

import re
from bs4 import BeautifulSoup

def fix_my_reports_file():
    """Исправляет файл webapp_my_reports.html"""
    
    filename = 'webapp_my_reports.html'
    
    print(f"🔍 Исправляем файл: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Добавляем атрибуты data-i18n к элементам
        translations_map = {
            'pageTitle': 'reports.my_reports_title',
            'pageSubtitle': 'reports.my_reports_subtitle',
            'loadingText': 'reports.my_reports_loading',
            'emptyTitle': 'reports.my_reports_empty_title',
            'emptyDescription': 'reports.my_reports_empty_description',
            'backBtn': 'reports.my_reports_back_btn',
            'viewReport': 'reports.my_reports_view_report',
            'deleteReport': 'reports.my_reports_delete_report',
            'copyLink': 'reports.my_reports_copy_link',
            'deleteModalTitle': 'reports.my_reports_delete_modal_title',
            'deleteModalMessage': 'reports.my_reports_delete_modal_message',
            'cancelDeleteBtn': 'reports.my_reports_cancel_delete_btn',
            'confirmDeleteBtn': 'reports.my_reports_confirm_delete_btn',
            'linkCopied': 'reports.my_reports_link_copied',
            'reportDeleted': 'reports.my_reports_report_deleted',
            'errorLoading': 'reports.my_reports_error_loading',
            'errorDeleting': 'reports.my_reports_error_deleting',
            'noAddress': 'reports.my_reports_no_address',
            'noPrice': 'reports.my_reports_no_price',
            'noArea': 'reports.my_reports_no_area',
            'noBedrooms': 'reports.my_reports_no_bedrooms'
        }
        
        # Добавляем атрибуты data-i18n к элементам по ID
        for element_id, translation_key in translations_map.items():
            element = soup.find(id=element_id)
            if element and not element.get('data-i18n'):
                element['data-i18n'] = translation_key
                print(f"  ✅ Добавлен атрибут data-i18n: {element_id} → {translation_key}")
        
        # Удаляем конфликтующий JavaScript код переводов
        script_tags = soup.find_all('script')
        
        for script_tag in script_tags:
            if script_tag.string:
                script_content = str(script_tag.string)
                
                # Удаляем функцию updatePageText
                script_content = re.sub(r'function updatePageText\(\) \{.*?\}', '', script_content, flags=re.DOTALL)
                
                # Удаляем вызовы updatePageText
                script_content = re.sub(r'updatePageText\(\);', '', script_content)
                
                # Удаляем объект locales
                script_content = re.sub(r'const locales = \{.*?\};', '', script_content, flags=re.DOTALL)
                
                # Удаляем функцию getText
                script_content = re.sub(r'function getText\(key\) \{.*?\}', '', script_content, flags=re.DOTALL)
                
                # Заменяем хардкод "Оценка объекта" на вызов i18n
                script_content = re.sub(
                    r"'property_evaluation': 'Оценка объекта'",
                    "'property_evaluation': window.i18nManager ? window.i18nManager.getTranslation('reports.my_reports_property_evaluation') : 'Object Evaluation'",
                    script_content
                )
                
                # Заменяем хардкод "Анализ объекта" на вызов i18n
                script_content = re.sub(
                    r"'property_analysis': 'Анализ объекта'",
                    "'property_analysis': window.i18nManager ? window.i18nManager.getTranslation('reports.my_reports_property_analysis') : 'Object Analysis'",
                    script_content
                )
                
                # Заменяем хардкод "Анализ рынка" на вызов i18n
                script_content = re.sub(
                    r"'market_analysis': 'Анализ рынка'",
                    "'market_analysis': window.i18nManager ? window.i18nManager.getTranslation('reports.my_reports_market_analysis') : 'Market Analysis'",
                    script_content
                )
                
                # Заменяем вызовы getText на вызовы i18nManager
                script_content = re.sub(
                    r'getText\([\'"]([^\'"]+)[\'"]\)',
                    r'window.i18nManager ? window.i18nManager.getTranslation("reports.my_reports_\1") : "\1"',
                    script_content
                )
                
                # Обновляем содержимое script тега
                script_tag.string = script_content
        
        # Сохраняем файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"  ✅ Файл {filename} исправлен")
        print("  ✅ Удален конфликтующий код переводов")
        print("  ✅ Добавлены атрибуты data-i18n")
        print("  ✅ Заменены хардкод переводы на вызовы i18nManager")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {filename}: {e}")

if __name__ == "__main__":
    fix_my_reports_file()
