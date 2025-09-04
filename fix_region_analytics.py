#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления файла webapp_region_analytics.html
Удаляет конфликтующий код переводов и добавляет правильные атрибуты data-i18n
"""

import re
from bs4 import BeautifulSoup

def fix_region_analytics_file():
    """Исправляет файл webapp_region_analytics.html"""
    
    filename = 'webapp_region_analytics.html'
    
    print(f"🔍 Исправляем файл: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Добавляем атрибуты data-i18n к элементам
        translations_map = {
            'pageDescription': 'reports.page_description',
            'countryLabel': 'reports.country_label',
            'cityLabel': 'reports.city_label',
            'countyLabel': 'reports.county_label',
            'districtLabel': 'reports.district_label',
            'countryPlaceholder': 'reports.country_placeholder',
            'cityPlaceholder': 'reports.city_placeholder',
            'countyPlaceholder': 'reports.county_placeholder',
            'districtPlaceholder': 'reports.district_placeholder',
            'confirmButtonText': 'reports.confirm_selection',
            'backButton': 'reports.back_to_main',
            'selectedLocationTitle': 'reports.selected_location',
            'adminIdsTitle': 'reports.admin_ids',
            'dataSectionTitle': 'reports.data_section_title',
            'generalDataTitle': 'reports.general_data_title',
            'houseTypeDataTitle': 'reports.house_type_data_title',
            'floorSegmentDataTitle': 'reports.floor_segment_data_title',
            'ageDataTitle': 'reports.age_data_title',
            'heatingDataTitle': 'reports.heating_data_title',
            'loadingText': 'reports.loading_text',
            'errorText': 'reports.error_text',
            'totalProperties': 'reports.total_properties',
            'averagePrice': 'reports.average_price',
            'priceRange': 'reports.price_range',
            'noDataAvailable': 'reports.no_data_available',
            'keyMetricsTitle': 'reports.key_metrics_title',
            'avgSalePriceLabel': 'reports.avg_sale_price_label',
            'avgRentPriceLabel': 'reports.avg_rent_price_label',
            'listingPeriodSaleLabel': 'reports.listing_period_sale_label',
            'listingPeriodRentLabel': 'reports.listing_period_rent_label',
            'yieldLabel': 'reports.yield_label',
            'insightsTitle': 'reports.insights_title',
            'insightsLoadingText': 'reports.insights_loading',
            'insightsErrorText': 'reports.insights_error'
        }
        
        # Добавляем атрибуты data-i18n к элементам по ID
        for element_id, translation_key in translations_map.items():
            element = soup.find(id=element_id)
            if element and not element.get('data-i18n'):
                element['data-i18n'] = translation_key
                print(f"  ✅ Добавлен атрибут data-i18n: {element_id} → {translation_key}")
        
        # Удаляем конфликтующий JavaScript код переводов
        # Ищем и удаляем функцию updatePageText и связанный код
        script_content = str(soup.find('script'))
        
        # Удаляем функцию updatePageText
        script_content = re.sub(r'function updatePageText\(\) \{.*?\}', '', script_content, flags=re.DOTALL)
        
        # Удаляем вызовы updatePageText
        script_content = re.sub(r'updatePageText\(\);', '', script_content)
        
        # Удаляем объект translations
        script_content = re.sub(r'const translations = \{.*?\};', '', script_content, flags=re.DOTALL)
        
        # Удаляем функцию getText
        script_content = re.sub(r'function getText\(key\) \{.*?\}', '', script_content, flags=re.DOTALL)
        
        # Обновляем script тег
        script_tag = soup.find('script')
        if script_tag:
            script_tag.string = script_content
        
        # Сохраняем файл
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"  ✅ Файл {filename} исправлен")
        print("  ✅ Удален конфликтующий код переводов")
        print("  ✅ Добавлены атрибуты data-i18n")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {filename}: {e}")

if __name__ == "__main__":
    fix_region_analytics_file()
