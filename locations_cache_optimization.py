#!/usr/bin/env python3
"""
Оптимизация API локаций с кэшированием в памяти
"""

import json
from functools import lru_cache
from datetime import datetime, timedelta

# Глобальный кэш для локаций
locations_cache = {
    'countries': None,
    'cities': None,
    'counties': None,
    'districts': None,
    'last_update': None,
    'cache_duration': timedelta(hours=24)  # Кэш на 24 часа
}

def load_locations_to_cache():
    """Загружает все локации в кэш один раз"""
    try:
        logger.info("🔄 Загрузка локаций в кэш...")
        
        # Получаем все записи с помощью пагинации
        all_records = []
        page = 0
        page_size = 1000
        
        while True:
            result = supabase.table('locations').select('*').range(page * page_size, (page + 1) * page_size - 1).execute()
            
            if not result.data:
                break
                
            all_records.extend(result.data)
            page += 1
            
            # Защита от бесконечного цикла
            if page > 10:
                break
        
        logger.info(f"📊 Загружено записей в кэш: {len(all_records)}")
        
        # Обрабатываем данные
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
        locations_cache['countries'] = sorted(list(countries), key=lambda x: x[1])
        
        for country_id in cities:
            cities[country_id] = sorted(list(cities[country_id]), key=lambda x: x[1])
        locations_cache['cities'] = cities
        
        for city_id in counties:
            counties[city_id] = sorted(list(counties[city_id]), key=lambda x: x[1])
        locations_cache['counties'] = counties
        
        for county_id in districts:
            districts[county_id] = sorted(list(districts[county_id]), key=lambda x: x[1])
        locations_cache['districts'] = districts
        
        locations_cache['last_update'] = datetime.now()
        
        logger.info(f"✅ Кэш обновлен: {len(locations_cache['countries'])} стран, {sum(len(cities) for cities in locations_cache['cities'].values())} городов")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке кэша: {e}")

def is_cache_valid():
    """Проверяет, актуален ли кэш"""
    if not locations_cache['last_update']:
        return False
    
    return datetime.now() - locations_cache['last_update'] < locations_cache['cache_duration']

def get_cached_locations():
    """Получает локации из кэша или обновляет кэш"""
    if not is_cache_valid():
        load_locations_to_cache()
    
    return locations_cache

# Оптимизированные API функции
@app.route('/api/locations/countries', methods=['GET'])
def api_locations_countries():
    """Получение списка стран из кэша"""
    try:
        logger.info("🔍 Запрос списка стран (из кэша)")
        
        cache = get_cached_locations()
        countries = cache['countries']
        
        logger.info(f"✅ Получено стран: {len(countries)}")
        return jsonify({'success': True, 'countries': countries})
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении стран: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/cities', methods=['POST'])
def api_locations_cities():
    """Получение списка городов по country_id из кэша"""
    data = request.json or {}
    country_id = data.get('country_id')
    
    if not country_id:
        return jsonify({'error': 'country_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос городов для country_id: {country_id} (из кэша)")
        
        cache = get_cached_locations()
        cities = cache['cities'].get(country_id, [])
        
        logger.info(f"✅ Получено городов: {len(cities)}")
        return jsonify({'success': True, 'cities': cities})
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении городов: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/counties', methods=['POST'])
def api_locations_counties():
    """Получение списка округов по city_id из кэша"""
    data = request.json or {}
    city_id = data.get('city_id')
    
    if not city_id:
        return jsonify({'error': 'city_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос округов для city_id: {city_id} (из кэша)")
        
        cache = get_cached_locations()
        counties = cache['counties'].get(city_id, [])
        
        logger.info(f"✅ Получено округов: {len(counties)}")
        return jsonify({'success': True, 'counties': counties})
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении округов: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/districts', methods=['POST'])
def api_locations_districts():
    """Получение списка районов по county_id из кэша"""
    data = request.json or {}
    county_id = data.get('county_id')
    
    if not county_id:
        return jsonify({'error': 'county_id required'}), 400
    
    try:
        logger.info(f"🔍 Запрос районов для county_id: {county_id} (из кэша)")
        
        cache = get_cached_locations()
        districts = cache['districts'].get(county_id, [])
        
        logger.info(f"✅ Получено районов: {len(districts)}")
        return jsonify({'success': True, 'districts': districts})
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении районов: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# API для управления кэшем
@app.route('/api/locations/refresh_cache', methods=['POST'])
def api_refresh_locations_cache():
    """Принудительное обновление кэша локаций"""
    try:
        load_locations_to_cache()
        return jsonify({'success': True, 'message': 'Cache refreshed successfully'})
    except Exception as e:
        logger.error(f"❌ Ошибка при обновлении кэша: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/cache_status', methods=['GET'])
def api_locations_cache_status():
    """Статус кэша локаций"""
    cache = get_cached_locations()
    return jsonify({
        'success': True,
        'cache_status': {
            'last_update': cache['last_update'].isoformat() if cache['last_update'] else None,
            'countries_count': len(cache['countries']) if cache['countries'] else 0,
            'cities_count': sum(len(cities) for cities in cache['cities'].values()) if cache['cities'] else 0,
            'counties_count': sum(len(counties) for counties in cache['counties'].values()) if cache['counties'] else 0,
            'districts_count': sum(len(districts) for districts in cache['districts'].values()) if cache['districts'] else 0,
            'is_valid': is_cache_valid()
        }
    })
