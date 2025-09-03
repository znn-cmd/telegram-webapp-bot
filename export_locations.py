#!/usr/bin/env python3
"""
Скрипт для выгрузки всех локаций из Supabase в JSON файл
"""

import os
import json
import csv
from datetime import datetime
from supabase import create_client, Client

def load_supabase_credentials():
    """Загружает учетные данные Supabase из переменных окружения"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Ошибка: SUPABASE_URL или SUPABASE_KEY не установлены")
        print("Установите переменные окружения или создайте файл .env")
        return None, None
    
    return supabase_url, supabase_key

def export_locations_from_supabase():
    """Выгружает все локации из Supabase в JSON файл"""
    
    print("📊 ВЫГРУЗКА ЛОКАЦИЙ ИЗ SUPABASE")
    print("=" * 50)
    
    # Подключение к Supabase
    supabase_url, supabase_key = load_supabase_credentials()
    if not supabase_url or not supabase_key:
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Подключение к Supabase установлено")
        
        # Получаем все записи с помощью пагинации
        all_records = []
        page = 0
        page_size = 1000
        
        print("🔄 Загрузка данных из таблицы locations...")
        
        while True:
            result = supabase.table('locations').select('*').range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
                
            all_records.extend(result.data)
            page += 1
            
            print(f"   Загружено страниц: {page}, записей: {len(all_records)}")
            
            # Защита от бесконечного цикла
            if page > 20:  # Максимум 20 страниц
                print("⚠️ Достигнут лимит страниц (20)")
                break
        
        print(f"📊 Всего загружено записей: {len(all_records)}")
        
        if not all_records:
            print("❌ Нет данных для выгрузки")
            return False
        
        # Обрабатываем данные
        print("🔄 Обработка данных...")
        
        countries = set()
        cities = {}  # country_id -> [(city_id, city_name), ...]
        counties = {}  # city_id -> [(county_id, county_name), ...]
        districts = {}  # county_id -> [(district_id, district_name), ...]
        
        for item in all_records:
            # Страны
            if item.get('country_id') and item.get('country_name'):
                countries.add((item['country_id'], item['country_name']))
            
            # Города
            if item.get('country_id') and item.get('city_id') and item.get('city_name'):
                country_id = item['country_id']
                if country_id not in cities:
                    cities[country_id] = set()
                cities[country_id].add((item['city_id'], item['city_name']))
            
            # Округа
            if item.get('city_id') and item.get('county_id') and item.get('county_name'):
                city_id = item['city_id']
                if city_id not in counties:
                    counties[city_id] = set()
                counties[city_id].add((item['county_id'], item['county_name']))
            
            # Районы
            if item.get('county_id') and item.get('district_id') and item.get('district_name'):
                county_id = item['county_id']
                if county_id not in districts:
                    districts[county_id] = set()
                districts[county_id].add((item['district_id'], item['district_name']))
        
        # Преобразуем в списки и сортируем
        countries_list = sorted(list(countries), key=lambda x: x[1])
        
        cities_dict = {}
        for country_id in cities:
            cities_dict[country_id] = sorted(list(cities[country_id]), key=lambda x: x[1])
        
        counties_dict = {}
        for city_id in counties:
            counties_dict[city_id] = sorted(list(counties[city_id]), key=lambda x: x[1])
        
        districts_dict = {}
        for county_id in districts:
            districts_dict[county_id] = sorted(list(districts[county_id]), key=lambda x: x[1])
        
        # Создаем структуру данных
        locations_data = {
            'countries': countries_list,
            'cities': cities_dict,
            'counties': counties_dict,
            'districts': districts_dict,
            'metadata': {
                'total_countries': len(countries_list),
                'total_cities': sum(len(cities) for cities in cities_dict.values()),
                'total_counties': sum(len(counties) for counties in counties_dict.values()),
                'total_districts': sum(len(districts) for districts in districts_dict.values()),
                'total_raw_records': len(all_records),
                'exported_at': datetime.now().isoformat(),
                'source': 'supabase'
            }
        }
        
        # Сохраняем в JSON файл
        json_file = "static_locations.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(locations_data, f, ensure_ascii=False, indent=2)
        
        # Сохраняем также полные данные для резервной копии
        backup_file = f"locations_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                'raw_data': all_records,
                'processed_data': locations_data,
                'exported_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Создан файл: {json_file}")
        print(f"✅ Создан бэкап: {backup_file}")
        print(f"📊 Статистика:")
        print(f"   Страны: {len(countries_list)}")
        print(f"   Города: {sum(len(cities) for cities in cities_dict.values())}")
        print(f"   Округа: {sum(len(counties) for counties in counties_dict.values())}")
        print(f"   Районы: {sum(len(districts) for districts in districts_dict.values())}")
        
        # Показываем примеры данных
        print(f"\n📋 Примеры данных:")
        print(f"   Страны: {countries_list[:3]}")
        if cities_dict:
            first_country = list(cities_dict.keys())[0]
            print(f"   Города (страна {first_country}): {list(cities_dict[first_country])[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при выгрузке данных: {e}")
        return False

def export_from_csv_fallback():
    """Альтернативная выгрузка из CSV файла, если Supabase недоступен"""
    csv_file = "temp/locations_rows (1).csv"
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV файл {csv_file} не найден")
        return False
    
    print("📄 Используем резервный метод - выгрузка из CSV файла")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Собираем данные
            countries = set()
            cities = {}  # country_id -> [(city_id, city_name), ...]
            counties = {}  # city_id -> [(county_id, county_name), ...]
            districts = {}  # county_id -> [(district_id, district_name), ...]
            
            for row in reader:
                # Страны
                if row.get('country_id') and row.get('country_name'):
                    countries.add((int(row['country_id']), row['country_name']))
                
                # Города
                if row.get('country_id') and row.get('city_id') and row.get('city_name'):
                    country_id = int(row['country_id'])
                    city_id = int(row['city_id'])
                    if country_id not in cities:
                        cities[country_id] = set()
                    cities[country_id].add((city_id, row['city_name']))
                
                # Округа
                if row.get('city_id') and row.get('county_id') and row.get('county_name'):
                    city_id = int(row['city_id'])
                    county_id = int(row['county_id'])
                    if city_id not in counties:
                        counties[city_id] = set()
                    counties[city_id].add((county_id, row['county_name']))
                
                # Районы
                if row.get('county_id') and row.get('district_id') and row.get('district_name'):
                    county_id = int(row['county_id'])
                    district_id = int(row['district_id'])
                    if county_id not in districts:
                        districts[county_id] = set()
                    districts[county_id].add((district_id, row['district_name']))
            
            # Преобразуем в списки и сортируем
            countries_list = sorted(list(countries), key=lambda x: x[1])
            
            cities_dict = {}
            for country_id in cities:
                cities_dict[country_id] = sorted(list(cities[country_id]), key=lambda x: x[1])
            
            counties_dict = {}
            for city_id in counties:
                counties_dict[city_id] = sorted(list(counties[city_id]), key=lambda x: x[1])
            
            districts_dict = {}
            for county_id in districts:
                districts_dict[county_id] = sorted(list(districts[county_id]), key=lambda x: x[1])
            
            # Создаем структуру данных
            locations_data = {
                'countries': countries_list,
                'cities': cities_dict,
                'counties': counties_dict,
                'districts': districts_dict,
                'metadata': {
                    'total_countries': len(countries_list),
                    'total_cities': sum(len(cities) for cities in cities_dict.values()),
                    'total_counties': sum(len(counties) for counties in counties_dict.values()),
                    'total_districts': sum(len(districts) for districts in districts_dict.values()),
                    'exported_at': datetime.now().isoformat(),
                    'source': 'csv_backup'
                }
            }
            
            # Сохраняем в JSON файл
            json_file = "static_locations.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(locations_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Создан файл: {json_file} (из CSV)")
            print(f"📊 Статистика:")
            print(f"   Страны: {len(countries_list)}")
            print(f"   Города: {sum(len(cities) for cities in cities_dict.values())}")
            print(f"   Округа: {sum(len(counties) for counties in counties_dict.values())}")
            print(f"   Районы: {sum(len(districts) for districts in districts_dict.values())}")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при обработке CSV файла: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 ЗАПУСК СКРИПТА ВЫГРУЗКИ ЛОКАЦИЙ")
    print("=" * 50)
    
    # Пытаемся выгрузить из Supabase
    success = export_locations_from_supabase()
    
    # Если не получилось, используем CSV как резервный вариант
    if not success:
        print("\n🔄 Пробуем резервный метод...")
        success = export_from_csv_fallback()
    
    if success:
        print("\n✅ Выгрузка завершена успешно!")
        print("📁 Файл static_locations.json готов к использованию")
        print("🔄 Теперь можно перезапустить приложение для использования статических данных")
    else:
        print("\n❌ Выгрузка не удалась")
        print("Проверьте подключение к Supabase или наличие CSV файла")

if __name__ == "__main__":
    main()
