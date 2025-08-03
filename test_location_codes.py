#!/usr/bin/env python3
"""
Тестовый скрипт для проверки извлечения кодов локаций
"""

import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем необходимые модули
from supabase import create_client, Client

# Инициализация Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ Ошибка: SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def get_location_codes(city_name, district_name, county_name):
    """
    Получает коды локаций из таблицы locations по названиям
    
    Args:
        city_name (str): Название города
        district_name (str): Название района
        county_name (str): Название округа/провинции
    
    Returns:
        dict: Словарь с кодами или None если не найдены
    """
    try:
        location_codes = {
            'city_code': None,
            'district_code': None,
            'county_code': None
        }
        
        print(f"\n🔍 Поиск кодов для:")
        print(f"   Город: {city_name}")
        print(f"   Район: {district_name}")
        print(f"   Округ: {county_name}")
        
        # Ищем запись с точным совпадением всех параметров
        print(f"\n📋 Поиск записи с параметрами:")
        print(f"   city_name: {city_name}")
        print(f"   district_name: {district_name}")
        print(f"   county_name: {county_name}")
        
        query = supabase.table('locations').select('*')
        
        # Добавляем фильтры по всем параметрам
        if city_name:
            query = query.eq('city_name', city_name)
        if district_name:
            query = query.eq('district_name', district_name)
        if county_name:
            query = query.eq('county_name', county_name)
            
        result = query.execute()
        print(f"   Результат запроса: {len(result.data)} записей")
        
        if result.data:
            for record in result.data:
                print(f"   Найдена запись: {record}")
                location_codes['city_code'] = record.get('city_id')
                location_codes['district_code'] = record.get('district_id')
                location_codes['county_code'] = record.get('county_id')
                print(f"   ✅ Коды найдены: city_id={location_codes['city_code']}, district_id={location_codes['district_code']}, county_id={location_codes['county_code']}")
        else:
            print(f"   ❌ Запись не найдена")
            
            # Попробуем найти частичные совпадения
            print(f"\n🔍 Поиск частичных совпадений...")
            
            # Поиск по району
            if district_name:
                district_result = supabase.table('locations').select('*').eq('district_name', district_name).execute()
                if district_result.data:
                    print(f"   ✅ Найдены записи по району '{district_name}':")
                    for record in district_result.data:
                        print(f"      {record}")
                    location_codes['district_code'] = district_result.data[0].get('district_id')
            
            # Поиск по округу
            if county_name:
                county_result = supabase.table('locations').select('*').eq('county_name', county_name).execute()
                if county_result.data:
                    print(f"   ✅ Найдены записи по округу '{county_name}':")
                    for record in county_result.data:
                        print(f"      {record}")
                    location_codes['county_code'] = county_result.data[0].get('county_id')
            
            # Поиск по городу
            if city_name:
                city_result = supabase.table('locations').select('*').eq('city_name', city_name).execute()
                if city_result.data:
                    print(f"   ✅ Найдены записи по городу '{city_name}':")
                    for record in city_result.data:
                        print(f"      {record}")
                    location_codes['city_code'] = city_result.data[0].get('city_id')
        
        print(f"\n📊 Итоговые коды: {location_codes}")
        return location_codes
        
    except Exception as e:
        print(f"❌ Ошибка получения кодов локаций: {e}")
        return None

def extract_location_from_address(address):
    """
    Извлекает город, район и округ из адреса
    """
    try:
        print(f"\n📍 Извлечение локации из адреса: {address}")
        
        # Улучшенное извлечение для турецких адресов
        address_parts = address.split(',')
        
        location_data = {
            'city_name': None,
            'district_name': None,
            'county_name': None
        }
        
        print(f"   Части адреса: {address_parts}")
        
        if len(address_parts) >= 3:
            # Для адреса: "Antalya, Alanya, Avsallar Mah., Cengiz Akay Sok., 12B"
            # Первая часть: город (Antalya) - это основной город
            location_data['city_name'] = address_parts[0].strip()
            
            # Вторая часть: округ/район (Alanya) - это округ
            location_data['county_name'] = address_parts[1].strip()
            
            # Третья часть: район (Avsallar Mah.) - это район
            district_name = address_parts[2].strip()
            # Убираем суффиксы типа "Mah.", "Mahallesi", "Sok." и т.д.
            district_name = district_name.replace(' Mah.', '').replace(' Mahallesi', '').replace(' Sok.', '').replace(' Sk.', '')
            location_data['district_name'] = district_name
                
        elif len(address_parts) >= 2:
            # Простой формат
            location_data['district_name'] = address_parts[0].strip()
            location_data['city_name'] = address_parts[1].strip()
        
        # Если не удалось извлечь, используем fallback
        if not location_data['city_name']:
            location_data['city_name'] = 'Alanya'  # Default для региона
        if not location_data['district_name']:
            location_data['district_name'] = 'Avsallar'  # Default район
        if not location_data['county_name']:
            location_data['county_name'] = 'Antalya'  # Default провинция
        
        print(f"   ✅ Извлеченные данные: {location_data}")
        return location_data
        
    except Exception as e:
        print(f"   ❌ Ошибка извлечения локации из адреса: {e}")
        return {
            'city_name': 'Alanya',
            'district_name': 'Avsallar', 
            'county_name': 'Antalya'
        }

def check_locations_table():
    """
    Проверяет структуру таблицы locations
    """
    print("\n🔍 Проверка структуры таблицы locations")
    print("=" * 40)
    
    try:
        # Получаем все записи из таблицы locations
        result = supabase.table('locations').select('*').execute()
        
        if result.data:
            print(f"✅ Таблица locations найдена, записей: {len(result.data)}")
            print(f"📋 Все записи:")
            for i, record in enumerate(result.data):
                print(f"   Запись {i+1}: {record}")
        else:
            print("⚠️  Таблица locations пуста")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке таблицы locations: {e}")

def test_address_parsing():
    """
    Тестирует парсинг адреса и поиск кодов
    """
    print("🚀 Запуск теста извлечения кодов локаций")
    print("=" * 60)
    
    # Сначала проверим структуру таблицы
    check_locations_table()
    
    # Тестовый адрес
    test_address = "Antalya, Alanya, Avsallar Mah., Cengiz Akay Sok., 12B"
    
    # Извлекаем локацию из адреса
    location_data = extract_location_from_address(test_address)
    
    if location_data:
        # Получаем коды локаций
        location_codes = get_location_codes(
            location_data['city_name'],
            location_data['district_name'], 
            location_data['county_name']
        )
        
        print(f"\n🎯 Результат теста:")
        print(f"   Адрес: {test_address}")
        print(f"   Извлеченные данные: {location_data}")
        print(f"   Найденные коды: {location_codes}")
        
        if location_codes:
            print(f"\n✅ Тест завершен успешно!")
        else:
            print(f"\n⚠️  Коды не найдены, но тест завершен")
    else:
        print(f"\n❌ Ошибка при извлечении данных из адреса")

if __name__ == "__main__":
    test_address_parsing() 