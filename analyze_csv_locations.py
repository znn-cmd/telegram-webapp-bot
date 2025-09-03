#!/usr/bin/env python3
"""
Скрипт для анализа CSV файла с локациями
"""

import csv
import sys

def analyze_csv_locations():
    """Анализирует CSV файл с локациями"""
    csv_file = "temp/locations_rows (1).csv"
    
    print("📊 АНАЛИЗ CSV ФАЙЛА С ЛОКАЦИЯМИ")
    print("=" * 50)
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            
            # Собираем данные
            total_records = 0
            countries = set()
            cities = set()
            counties = set()
            districts = set()
            
            # Собираем уникальные города для Турции
            turkey_cities = set()
            
            for row in reader:
                total_records += 1
                
                # Общие данные
                if row.get('country_name'):
                    countries.add(row['country_name'])
                if row.get('city_name'):
                    cities.add(row['city_name'])
                if row.get('county_name'):
                    counties.add(row['county_name'])
                if row.get('district_name'):
                    districts.add(row['district_name'])
                
                # Города Турции
                if row.get('country_id') == '1' and row.get('city_name'):
                    turkey_cities.add(row['city_name'])
            
            print(f"📊 Общая статистика:")
            print(f"   Всего записей: {total_records}")
            print(f"   Уникальных стран: {len(countries)}")
            print(f"   Уникальных городов: {len(cities)}")
            print(f"   Уникальных округов: {len(counties)}")
            print(f"   Уникальных районов: {len(districts)}")
            
            print(f"\n🇹🇷 Статистика для Турции:")
            print(f"   Уникальных городов в Турции: {len(turkey_cities)}")
            
            print(f"\n📋 Города Турции (первые 20):")
            sorted_cities = sorted(list(turkey_cities))
            for i, city in enumerate(sorted_cities[:20]):
                print(f"   {i+1}. {city}")
            
            if len(sorted_cities) > 20:
                print(f"   ... и еще {len(sorted_cities) - 20} городов")
            
            print(f"\n📋 Все страны:")
            for i, country in enumerate(sorted(countries)):
                print(f"   {i+1}. {country}")
                
    except FileNotFoundError:
        print(f"❌ Файл {csv_file} не найден")
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")

if __name__ == "__main__":
    analyze_csv_locations()
