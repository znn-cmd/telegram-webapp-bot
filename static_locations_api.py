#!/usr/bin/env python3
"""
Простой API для работы со статическим файлом локаций
"""

import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Загружаем данные из статического файла
def load_static_locations():
    """Загружает данные из статического JSON файла"""
    try:
        with open('static_locations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла: {e}")
        return None

# Глобальная переменная с данными
locations_data = None

@app.before_first_request
def initialize_data():
    """Инициализация данных при первом запросе"""
    global locations_data
    locations_data = load_static_locations()
    if locations_data:
        print(f"✅ Загружены данные: {locations_data['metadata']['total_countries']} стран, {locations_data['metadata']['total_cities']} городов")

@app.route('/api/locations/countries', methods=['GET'])
def api_locations_countries():
    """Получение списка стран из статического файла"""
    if not locations_data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    try:
        countries = locations_data['countries']
        return jsonify({'success': True, 'countries': countries})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/cities', methods=['POST'])
def api_locations_cities():
    """Получение списка городов по country_id из статического файла"""
    if not locations_data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    data = request.json or {}
    country_id = data.get('country_id')
    
    if not country_id:
        return jsonify({'error': 'country_id required'}), 400
    
    try:
        cities = locations_data['cities'].get(str(country_id), [])
        return jsonify({'success': True, 'cities': cities})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/counties', methods=['POST'])
def api_locations_counties():
    """Получение списка округов по city_id из статического файла"""
    if not locations_data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    data = request.json or {}
    city_id = data.get('city_id')
    
    if not city_id:
        return jsonify({'error': 'city_id required'}), 400
    
    try:
        counties = locations_data['counties'].get(str(city_id), [])
        return jsonify({'success': True, 'counties': counties})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/districts', methods=['POST'])
def api_locations_districts():
    """Получение списка районов по county_id из статического файла"""
    if not locations_data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    data = request.json or {}
    county_id = data.get('county_id')
    
    if not county_id:
        return jsonify({'error': 'county_id required'}), 400
    
    try:
        districts = locations_data['districts'].get(str(county_id), [])
        return jsonify({'success': True, 'districts': districts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/locations/status', methods=['GET'])
def api_locations_status():
    """Статус данных локаций"""
    if not locations_data:
        return jsonify({'success': False, 'error': 'Data not loaded'}), 500
    
    return jsonify({
        'success': True,
        'status': {
            'loaded': True,
            'metadata': locations_data['metadata'],
            'file_size': os.path.getsize('static_locations.json') if os.path.exists('static_locations.json') else 0
        }
    })

if __name__ == '__main__':
    print("🚀 Запуск API со статическими данными...")
    app.run(host='0.0.0.0', port=8081, debug=True)
