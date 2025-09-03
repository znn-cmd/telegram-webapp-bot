#!/usr/bin/env python3
"""
Оптимизированный API для работы со статическим файлом локаций
"""

import json
import os
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# Глобальная переменная с данными
locations_data = None
last_load_time = None

def load_static_locations():
    """Загружает данные из статического JSON файла"""
    global locations_data, last_load_time
    
    try:
        json_file = "static_locations.json"
        
        if not os.path.exists(json_file):
            print(f"❌ Файл {json_file} не найден")
            print("Запустите скрипт export_locations.py для создания файла")
            return None
        
        # Проверяем время последнего изменения файла
        file_mtime = os.path.getmtime(json_file)
        
        # Если файл изменился или данные не загружены, перезагружаем
        if (last_load_time is None or 
            file_mtime > last_load_time or 
            locations_data is None):
            
            with open(json_file, 'r', encoding='utf-8') as f:
                locations_data = json.load(f)
            
            last_load_time = file_mtime
            
            print(f"✅ Загружены данные: {locations_data['metadata']['total_countries']} стран, {locations_data['metadata']['total_cities']} городов")
            print(f"📅 Данные обновлены: {locations_data['metadata']['exported_at']}")
        
        return locations_data
        
    except FileNotFoundError:
        print(f"❌ Файл static_locations.json не найден")
        return None
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла: {e}")
        return None

def get_locations_data():
    """Получает данные локаций, загружая их при необходимости"""
    if locations_data is None:
        return load_static_locations()
    return locations_data

@app.route('/api/locations/countries', methods=['GET'])
def api_locations_countries():
    """Получение списка стран из статического файла"""
    data = get_locations_data()
    if not data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    try:
        countries = data['countries']
        return jsonify({
            'success': True, 
            'countries': countries,
            'metadata': {
                'total': len(countries),
                'source': data['metadata']['source'],
                'exported_at': data['metadata']['exported_at']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/cities', methods=['POST'])
def api_locations_cities():
    """Получение списка городов по country_id из статического файла"""
    data = get_locations_data()
    if not data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    request_data = request.json or {}
    country_id = request_data.get('country_id')
    
    if not country_id:
        return jsonify({'error': 'country_id required'}), 400
    
    try:
        cities = data['cities'].get(str(country_id), [])
        return jsonify({
            'success': True, 
            'cities': cities,
            'metadata': {
                'total': len(cities),
                'country_id': country_id,
                'source': data['metadata']['source'],
                'exported_at': data['metadata']['exported_at']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/counties', methods=['POST'])
def api_locations_counties():
    """Получение списка округов по city_id из статического файла"""
    data = get_locations_data()
    if not data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    request_data = request.json or {}
    city_id = request_data.get('city_id')
    
    if not city_id:
        return jsonify({'error': 'city_id required'}), 400
    
    try:
        counties = data['counties'].get(str(city_id), [])
        return jsonify({
            'success': True, 
            'counties': counties,
            'metadata': {
                'total': len(counties),
                'city_id': city_id,
                'source': data['metadata']['source'],
                'exported_at': data['metadata']['exported_at']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/districts', methods=['POST'])
def api_locations_districts():
    """Получение списка районов по county_id из статического файла"""
    data = get_locations_data()
    if not data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    request_data = request.json or {}
    county_id = request_data.get('county_id')
    
    if not county_id:
        return jsonify({'error': 'county_id required'}), 400
    
    try:
        districts = data['districts'].get(str(county_id), [])
        return jsonify({
            'success': True, 
            'districts': districts,
            'metadata': {
                'total': len(districts),
                'county_id': county_id,
                'source': data['metadata']['source'],
                'exported_at': data['metadata']['exported_at']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/status', methods=['GET'])
def api_locations_status():
    """Статус данных локаций"""
    data = get_locations_data()
    if not data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    json_file = "static_locations.json"
    file_size = os.path.getsize(json_file) if os.path.exists(json_file) else 0
    
    return jsonify({
        'success': True,
        'status': {
            'loaded': True,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'metadata': data['metadata'],
            'last_load_time': last_load_time.isoformat() if last_load_time else None
        }
    })

@app.route('/api/locations/reload', methods=['POST'])
def api_locations_reload():
    """Принудительная перезагрузка данных"""
    global locations_data, last_load_time
    
    try:
        locations_data = None
        last_load_time = None
        
        data = load_static_locations()
        if data:
            return jsonify({
                'success': True, 
                'message': 'Data reloaded successfully',
                'metadata': data['metadata']
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to reload data'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/search', methods=['POST'])
def api_locations_search():
    """Поиск локаций по названию"""
    data = get_locations_data()
    if not data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    request_data = request.json or {}
    query = request_data.get('query', '').lower()
    limit = request_data.get('limit', 10)
    
    if not query or len(query) < 2:
        return jsonify({'error': 'Query must be at least 2 characters'}), 400
    
    try:
        results = []
        
        # Поиск по странам
        for country_id, country_name in data['countries']:
            if query in country_name.lower():
                results.append({
                    'type': 'country',
                    'id': country_id,
                    'name': country_name,
                    'country_id': country_id
                })
        
        # Поиск по городам
        for country_id, cities in data['cities'].items():
            for city_id, city_name in cities:
                if query in city_name.lower():
                    results.append({
                        'type': 'city',
                        'id': city_id,
                        'name': city_name,
                        'country_id': country_id,
                        'city_id': city_id
                    })
        
        # Поиск по округам
        for city_id, counties in data['counties'].items():
            for county_id, county_name in counties:
                if query in county_name.lower():
                    results.append({
                        'type': 'county',
                        'id': county_id,
                        'name': county_name,
                        'city_id': city_id,
                        'county_id': county_id
                    })
        
        # Сортируем результаты и ограничиваем количество
        results = sorted(results, key=lambda x: x['name'])[:limit]
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'query': query
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Запуск оптимизированного API локаций...")
    print("📁 Используется статический файл static_locations.json")
    
    # Предварительная загрузка данных
    if load_static_locations():
        print("✅ Данные загружены успешно")
    else:
        print("⚠️ Данные не загружены. API может работать некорректно")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
