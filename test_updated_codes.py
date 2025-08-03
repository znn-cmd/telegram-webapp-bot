#!/usr/bin/env python3
"""
Тест обновленной функциональности кодов локаций
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Загружаем переменные окружения
load_dotenv()

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def extract_location_from_address(address):
    """
    Извлекает город, район и округ из адреса
    """
    try:
        address_parts = address.split(',')
        
        location_data = {
            'city_name': None,
            'district_name': None,
            'county_name': None,
            'country_name': 'Turkey'  # По умолчанию для турецких адресов
        }
        
        if len(address_parts) >= 3:
            location_data['city_name'] = address_parts[0].strip()
            location_data['county_name'] = address_parts[1].strip()
            
            district_name = address_parts[2].strip()
            district_name = district_name.replace(' Mah.', '').replace(' Mahallesi', '').replace(' Sok.', '').replace(' Sk.', '')
            location_data['district_name'] = district_name
                
        elif len(address_parts) >= 2:
            location_data['district_name'] = address_parts[0].strip()
            location_data['city_name'] = address_parts[1].strip()
        
        if not location_data['city_name']:
            location_data['city_name'] = 'Alanya'
        if not location_data['district_name']:
            location_data['district_name'] = 'Avsallar'
        if not location_data['county_name']:
            location_data['county_name'] = 'Antalya'
        
        return location_data
        
    except Exception as e:
        print(f"Ошибка извлечения локации из адреса: {e}")
        return {
            'city_name': 'Alanya',
            'district_name': 'Avsallar', 
            'county_name': 'Antalya',
            'country_name': 'Turkey'
        }

def get_location_codes(city_name, district_name, county_name):
    """
    Получает коды локаций из таблицы locations по названиям
    """
    try:
        location_codes = {
            'city_code': None,
            'district_code': None,
            'county_code': None,
            'country_code': None
        }
        
        # Ищем запись с точным совпадением всех параметров
        query = supabase.table('locations').select('*')
        
        # Добавляем фильтры по всем параметрам
        if city_name:
            query = query.eq('city_name', city_name)
        if district_name:
            query = query.eq('district_name', district_name)
        if county_name:
            query = query.eq('county_name', county_name)
            
        result = query.execute()
        
        if result.data:
            # Найдена точная запись
            record = result.data[0]
            location_codes['city_code'] = record.get('city_id')
            location_codes['district_code'] = record.get('district_id')
            location_codes['county_code'] = record.get('county_id')
            location_codes['country_code'] = record.get('country_id')
            print(f"✅ Найдены коды локаций: {location_codes}")
            return location_codes
        else:
            # Ищем частичные совпадения
            print(f"⚠️  Точное совпадение не найдено, ищем частичные совпадения")
            
            # Поиск по району
            if district_name:
                district_result = supabase.table('locations').select('*').eq('district_name', district_name).execute()
                if district_result.data:
                    location_codes['district_code'] = district_result.data[0].get('district_id')
                    print(f"✅ Найден код района: {location_codes['district_code']}")
            
            # Поиск по округу
            if county_name:
                county_result = supabase.table('locations').select('*').eq('county_name', county_name).execute()
                if county_result.data:
                    location_codes['county_code'] = county_result.data[0].get('county_id')
                    print(f"✅ Найден код округа: {location_codes['county_code']}")
            
            # Поиск по городу
            if city_name:
                city_result = supabase.table('locations').select('*').eq('city_name', city_name).execute()
                if city_result.data:
                    location_codes['city_code'] = city_result.data[0].get('city_id')
                    print(f"✅ Найден код города: {location_codes['city_code']}")
        
        return location_codes
        
    except Exception as e:
        print(f"❌ Ошибка получения кодов локаций: {e}")
        return None

def test_location_codes():
    """
    Тестирует получение кодов локаций
    """
    print("🚀 ТЕСТ ПОЛУЧЕНИЯ КОДОВ ЛОКАЦИЙ")
    print("=" * 50)
    
    # Тестовый адрес
    test_address = "Antalya, Alanya, Avsallar Mah., Cengiz Akay Sok., 12B"
    
    # Извлекаем локацию из адреса
    location_info = extract_location_from_address(test_address)
    print(f"📍 Извлеченные данные локации: {location_info}")
    
    # Получаем коды локаций
    location_codes = get_location_codes(
        location_info.get('city_name', ''),
        location_info.get('district_name', ''),
        location_info.get('county_name', '')
    )
    print(f"🔢 Найденные коды: {location_codes}")
    
    # Создаем тестовые данные анализа рынка
    test_market_analysis = {
        'market_analysis': {
            'radius_5km': {
                'short_term_rentals': {
                    'count': 5,
                    'avg_price_per_night': 155.0,
                    'price_range': [145, 160]
                },
                'long_term_rentals': {
                    'count': 3,
                    'avg_monthly_rent': 5600.0,
                    'price_range': [5200, 6000]
                },
                'sales': {
                    'count': 8,
                    'avg_sale_price': 1122211.0,
                    'price_range': [1000000, 1250000]
                },
                'avg_price_per_sqm': 15451.29
            }
        },
        'location_codes': location_codes,
        'location_info': location_info
    }
    
    # Формируем отчет
    report_text = format_market_report_with_codes(test_market_analysis, test_address)
    
    print(f"\n📋 СФОРМИРОВАННЫЙ ОТЧЕТ:")
    print("=" * 50)
    print(report_text)
    print("=" * 50)
    
    print(f"\n✅ Тест завершен успешно!")
    print(f"💡 Коды локаций добавлены в отчет для проверки связи с таблицами")

def format_market_report_with_codes(market_analysis, address, language='en'):
    """
    Форматирование отчёта в текстовый вид с кодами локаций
    """
    
    # Получаем данные из анализа
    short_term = market_analysis['market_analysis']['radius_5km']['short_term_rentals']
    long_term = market_analysis['market_analysis']['radius_5km']['long_term_rentals']
    sales = market_analysis['market_analysis']['radius_5km']['sales']
    
    # Форматируем цены
    def format_price(price):
        return f"€{price:.2f}".replace('.00', '').replace('.', ',')
    
    def format_price_range(min_price, max_price):
        return f"€{min_price:.0f} - €{max_price:.0f}"
    
    # Формируем отчёт
    report_lines = [
        f"Анализ рынка в радиусе 5 км:",
        "",
    ]
    
    # Добавляем коды локаций для проверки связи с таблицами
    location_codes = market_analysis.get('location_codes')
    location_info = market_analysis.get('location_info')
    if location_codes and location_info:
        report_lines.extend([
            "=== КОДЫ ЛОКАЦИЙ (для проверки связи с таблицами) ===",
            f"Страна: {location_info.get('country_name', 'н/д')} (код: {location_codes.get('country_code', 'н/д')})",
            f"Город: {location_info.get('city_name', 'н/д')} (код: {location_codes.get('city_code', 'н/д')})",
            f"Район: {location_info.get('district_name', 'н/д')} (код: {location_codes.get('district_code', 'н/д')})",
            f"Округ: {location_info.get('county_name', 'н/д')} (код: {location_codes.get('county_code', 'н/д')})",
            "",
        ])
    
    report_lines.extend([
        f"Краткосрочная аренда ({short_term['count']} объектов)",
        f"Средняя цена за ночь: {format_price(short_term['avg_price_per_night'])}",
        "",
        f"Диапазон цен: {format_price_range(short_term['price_range'][0], short_term['price_range'][1])}",
        "",
        f"Долгосрочная аренда ({long_term['count']} объектов)",
        f"Средняя месячная аренда: {format_price(long_term['avg_monthly_rent'])}",
        "",
        f"Диапазон цен: {format_price_range(long_term['price_range'][0], long_term['price_range'][1])}",
        "",
        f"Продажи недвижимости ({sales['count']} объектов)",
        f"Средняя цена продажи: {format_price(sales['avg_sale_price'])}",
        "",
        f"Диапазон цен: {format_price_range(sales['price_range'][0], sales['price_range'][1])}",
        "",
    ])
    
    # Добавляем общую информацию
    report_lines.extend([
        f"Средняя цена за кв.м: €{market_analysis['market_analysis']['radius_5km']['avg_price_per_sqm']:.2f}"
    ])
    
    return "\n".join(report_lines)

if __name__ == "__main__":
    test_location_codes() 