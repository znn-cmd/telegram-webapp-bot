#!/usr/bin/env python3
"""
Создание статического JSON файла с локациями
"""

import json
import csv

def create_static_locations_file():
    """Создает статический JSON файл с локациями"""
    csv_file = "temp/locations_rows (1).csv"
    json_file = "static_locations.json"
    
    print("📊 СОЗДАНИЕ СТАТИЧЕСКОГО ФАЙЛА ЛОКАЦИЙ")
    print("=" * 50)
    
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
                    'created_at': '2025-09-03T12:00:00Z'
                }
            }
            
            # Сохраняем в JSON файл
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(locations_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Создан файл: {json_file}")
            print(f"📊 Статистика:")
            print(f"   Страны: {len(countries_list)}")
            print(f"   Города: {sum(len(cities) for cities in cities_dict.values())}")
            print(f"   Округа: {sum(len(counties) for counties in counties_dict.values())}")
            print(f"   Районы: {sum(len(districts) for districts in districts_dict.values())}")
            
            # Показываем примеры данных
            print(f"\n📋 Примеры данных:")
            print(f"   Страны: {countries_list[:3]}")
            print(f"   Города Турции: {list(cities_dict.get(1, []))[:5]}")
            
    except FileNotFoundError:
        print(f"❌ Файл {csv_file} не найден")
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")

if __name__ == "__main__":
    create_static_locations_file()
