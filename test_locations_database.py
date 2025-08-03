#!/usr/bin/env python3
"""
Тестовый скрипт для проверки поиска локаций в базе данных
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Загружаем переменные окружения
load_dotenv()

# Инициализация Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

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
            'country_name': 'Turkey'
        }
        
        if len(address_parts) >= 3:
            if 'Muratpaşa/Antalya' in address_parts[1]:
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Muratpaşa'
                location_data['district_name'] = address_parts[0].strip()
            elif 'Alanya/Antalya' in address_parts[2]:
                location_data['city_name'] = 'Antalya'
                location_data['county_name'] = 'Alanya'
                location_data['district_name'] = address_parts[0].strip()
            else:
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
            'county_name': 'Antalya'
        }

def get_location_codes_from_address(address):
    """Получает коды локаций из таблицы locations по адресу"""
    try:
        location_info = extract_location_from_address(address)
        if not location_info:
            return None
        
        # Исправляем названия для соответствия с базой данных
        if location_info.get('country_name') == 'Turkey':
            location_info['country_name'] = 'Türkiye'
        
        print(f"Ищем локацию в базе: {location_info}")
        
        # Ищем в таблице locations - сначала по точному совпадению
        query = supabase.table('locations').select('*')
        
        if location_info.get('city_name'):
            query = query.eq('city_name', location_info['city_name'])
        if location_info.get('county_name'):
            query = query.eq('county_name', location_info['county_name'])
        if location_info.get('district_name'):
            query = query.eq('district_name', location_info['district_name'])
        if location_info.get('country_name'):
            query = query.eq('country_name', location_info['country_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            print(f"✅ Найдена локация (точное совпадение): {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если точное совпадение не найдено, пробуем найти по district_name и city_name
        print("Точное совпадение не найдено, ищем по district_name и city_name")
        query = supabase.table('locations').select('*')
        if location_info.get('district_name'):
            query = query.eq('district_name', location_info['district_name'])
        if location_info.get('city_name'):
            query = query.eq('city_name', location_info['city_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            print(f"✅ Найдена локация по district_name и city_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        # Если и это не помогло, ищем только по district_name
        print("Ищем только по district_name")
        query = supabase.table('locations').select('*')
        if location_info.get('district_name'):
            query = query.eq('district_name', location_info['district_name'])
        
        result = query.execute()
        
        if result.data and len(result.data) > 0:
            location = result.data[0]
            print(f"✅ Найдена локация по district_name: {location}")
            return {
                'city_id': location['city_id'],
                'county_id': location['county_id'],
                'district_id': location['district_id'],
                'country_id': location['country_id'],
                'city_name': location['city_name'],
                'county_name': location['county_name'],
                'district_name': location['district_name'],
                'country_name': location['country_name']
            }
        
        print(f"❌ Локация не найдена для: {location_info}")
        return None
            
    except Exception as e:
        print(f"❌ Ошибка получения кодов локаций: {e}")
        return None

def test_locations_search():
    """Тестирует поиск локаций в базе данных"""
    
    test_addresses = [
        "Avsallar, Cengiz Akay Sk. No:12, 07410 Alanya/Antalya, Türkiye",
        "Zerdalilik, 07100 Muratpaşa/Antalya, Türkiye"
    ]
    
    print("🧪 Тестирование поиска локаций в базе данных\n")
    
    for i, address in enumerate(test_addresses, 1):
        print(f"Тест {i}: {address}")
        print("-" * 60)
        
        result = get_location_codes_from_address(address)
        
        if result:
            print(f"✅ Результат:")
            print(f"  - Country ID: {result.get('country_id')}")
            print(f"  - City ID: {result.get('city_id')}")
            print(f"  - District ID: {result.get('district_id')}")
            print(f"  - County ID: {result.get('county_id')}")
            print(f"  - Country: {result.get('country_name')}")
            print(f"  - City: {result.get('city_name')}")
            print(f"  - District: {result.get('district_name')}")
            print(f"  - County: {result.get('county_name')}")
        else:
            print("❌ Локация не найдена")
        
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    test_locations_search() 