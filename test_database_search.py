#!/usr/bin/env python3
"""
Тестовый скрипт для проверки поиска адресов в базе данных
"""

import os
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import supabase
    print("✅ Подключение к Supabase успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)

def test_database_search():
    """Тестирует поиск адресов в базе данных"""
    print("🔍 Тестирование поиска в базе данных")
    print("=" * 50)
    
    # Тестовый адрес
    test_address = "Baraj, 5890. Sk. No:584, 07320 Kepez/Antalya, Турция"
    print(f"📍 Тестовый адрес: {test_address}")
    
    try:
        # Извлекаем ключевые слова
        search_terms = [word.strip() for word in test_address.replace(',', ' ').replace('.', ' ').split() if len(word.strip()) > 2]
        print(f"🔍 Поисковые термины: {search_terms}")
        
        # Ищем в таблице locations
        search_query = supabase.table('locations').select('*')
        
        # Фильтруем по ключевым словам
        for term in search_terms[:3]:
            if term.lower() not in ['турция', 'türkiye', 'antalya', 'kepez']:
                print(f"🔍 Ищем термин: {term}")
                search_query = search_query.or_(f"district_name.ilike.%{term}%,county_name.ilike.%{term}%,city_name.ilike.%{term}%")
        
        # Выполняем поиск
        print("🔍 Выполняем поиск в базе данных...")
        search_result = search_query.execute()
        
        print(f"📊 Результат поиска: {len(search_result.data)} записей")
        
        if search_result.data:
            print("✅ Найдены локации:")
            for i, location in enumerate(search_result.data[:3]):  # Показываем первые 3
                print(f"  {i+1}. {location.get('district_name', 'N/A')}, {location.get('county_name', 'N/A')}, {location.get('city_name', 'N/A')}")
                print(f"     Координаты: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
                print(f"     ID: {location.get('id', 'N/A')}")
                print()
        else:
            print("❌ Локации не найдены")
            
            # Попробуем более широкий поиск
            print("🔍 Попробуем более широкий поиск...")
            wide_search = supabase.table('locations').select('*').eq('country_name', 'Türkiye').eq('city_name', 'Antalya').execute()
            print(f"📊 Найдено локаций в Анталье: {len(wide_search.data)}")
            
            if wide_search.data:
                print("📍 Примеры локаций в Анталье:")
                for i, location in enumerate(wide_search.data[:5]):
                    print(f"  {i+1}. {location.get('district_name', 'N/A')}, {location.get('county_name', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")
        import traceback
        traceback.print_exc()

def test_specific_search():
    """Тестирует поиск конкретных локаций"""
    print("\n🎯 Тестирование конкретных локаций")
    print("=" * 50)
    
    try:
        # Поиск по району Baraj
        print("🔍 Поиск по району 'Baraj'...")
        baraj_search = supabase.table('locations').select('*').ilike('district_name', '%Baraj%').execute()
        print(f"📊 Найдено локаций с 'Baraj': {len(baraj_search.data)}")
        
        if baraj_search.data:
            for location in baraj_search.data:
                print(f"  ✅ {location.get('district_name')}, {location.get('county_name')}, {location.get('city_name')}")
        
        # Поиск по городу Antalya
        print("\n🔍 Поиск по городу 'Antalya'...")
        antalya_search = supabase.table('locations').select('*').eq('city_name', 'Antalya').execute()
        print(f"📊 Найдено локаций в Анталье: {len(antalya_search.data)}")
        
        if antalya_search.data:
            print("📍 Районы в Анталье:")
            districts = set()
            for location in antalya_search.data:
                district = location.get('district_name')
                if district:
                    districts.add(district)
            
            for district in sorted(list(districts))[:10]:  # Показываем первые 10
                print(f"  • {district}")
    
    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")

def main():
    """Основная функция"""
    print("🚀 Тестирование поиска адресов в базе данных")
    print("=" * 60)
    
    # Тестируем поиск
    test_database_search()
    test_specific_search()
    
    print("\n📋 Рекомендации:")
    print("1. Если локации не найдены, проверьте правильность написания")
    print("2. Попробуйте использовать более общие термины")
    print("3. Убедитесь, что данные загружены в таблицу locations")

if __name__ == "__main__":
    main()
