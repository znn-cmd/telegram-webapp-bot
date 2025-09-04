#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления файла webapp_object_evaluation.html
Удаляет конфликтующий код переводов и добавляет правильные атрибуты data-i18n
"""

import re
from bs4 import BeautifulSoup

def fix_object_evaluation_file():
    """Исправляет файл webapp_object_evaluation.html"""
    
    filename = 'webapp_object_evaluation.html'
    
    print(f"🔍 Исправляем файл: {filename}")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсим HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Добавляем атрибуты data-i18n к элементам
        translations_map = {
            'pageTitle': 'reports.object_evaluation_title',
            'pageDescription': 'reports.object_evaluation_description',
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
            'listingTypeTitle': 'reports.listing_type_title',
            'houseTypeSubtitle': 'reports.house_type_subtitle',
            'floorSegmentSubtitle': 'reports.floor_segment_subtitle',
            'ageDataSubtitle': 'reports.age_data_subtitle',
            'heatingDataSubtitle': 'reports.heating_data_subtitle',
            'priceObjectSubtitle': 'reports.price_object_subtitle',
            'areaObjectSubtitle': 'reports.area_object_subtitle',
            'selectBedrooms': 'reports.select_bedrooms',
            'selectFloor': 'reports.select_floor',
            'selectAge': 'reports.select_age',
            'selectHeating': 'reports.select_heating',
            'propertyTypesTitle': 'reports.property_types_title',
            'bedroomsLabel': 'reports.bedrooms_label',
            'floorLabel': 'reports.floor_label',
            'ageLabel': 'reports.age_label',
            'heatingLabel': 'reports.heating_label',
            'marketIndicatorsTitle': 'reports.market_indicators_title',
            'marketTrendsTitle': 'reports.market_trends_title',
            'saleHeader': 'reports.sale_header',
            'rentHeader': 'reports.rent_header',
            'currencyTitle': 'reports.currency_title',
            'saveShareButtonText': 'reports.save_share_button_text',
            'modalTitle': 'reports.modal_title',
            'modalDescription': 'reports.modal_description',
            'copyButtonText': 'reports.copy_button_text',
            'closeButtonText': 'reports.close_button_text',
            'linkCopied': 'reports.link_copied',
            'savingReport': 'reports.saving_report',
            'errorSaving': 'reports.error_saving',
            'pricePlaceholder': 'reports.price_placeholder',
            'areaPlaceholder': 'reports.area_placeholder',
            'trendsFilterInfo': 'reports.trends_filter_info',
            'marketComparisonTitle': 'reports.market_comparison_title',
            'pricePerM2Label': 'reports.price_per_m2_label',
            'areaLabel': 'reports.area_label',
            'priceComparisonLabel': 'reports.price_comparison_label',
            'areaComparisonLabel': 'reports.area_comparison_label',
            'priceCloseToMarket': 'reports.price_close_to_market',
            'priceAboveMarket': 'reports.price_above_market',
            'priceBelowMarket': 'reports.price_below_market',
            'areaMatchesMarket': 'reports.area_matches_market',
            'areaBelowMarket': 'reports.area_below_market',
            'areaAboveMarket': 'reports.area_above_market',
            'houseTypeDataTitle': 'reports.house_type_data_title',
            'floorSegmentDataTitle': 'reports.floor_segment_data_title',
            'ageDataTitle': 'reports.age_data_title',
            'heatingDataTitle': 'reports.heating_data_title',
            'consolidatedAssessmentTitle': 'reports.consolidated_assessment_title',
            'salePriceTitle': 'reports.sale_price_title',
            'rentPriceTitle': 'reports.rent_price_title',
            'yieldTitle': 'reports.yield_title',
            'consolidatedAverageLabel': 'reports.consolidated_average_label',
            'indicatorLabel': 'reports.indicator_label',
            'minValueLabel': 'reports.min_value_label',
            'maxValueLabel': 'reports.max_value_label',
            'avgValueLabel': 'reports.avg_value_label',
            'countLabel': 'reports.count_label',
            'percentageLabel': 'reports.percentage_label'
        }
        
        # Добавляем атрибуты data-i18n к элементам по ID
        for element_id, translation_key in translations_map.items():
            element = soup.find(id=element_id)
            if element and not element.get('data-i18n'):
                element['data-i18n'] = translation_key
                print(f"  ✅ Добавлен атрибут data-i18n: {element_id} → {translation_key}")
        
        # Удаляем конфликтующий JavaScript код переводов
        # Ищем и удаляем функцию updatePageText и связанный код
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
                
                # Обновляем содержимое script тега
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
    fix_object_evaluation_file()
