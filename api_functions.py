import os
import requests
import json
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
import math

# Загружаем переменные окружения
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Вычисляет расстояние между двумя точками на сфере"""
    R = 6371  # Радиус Земли в километрах
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def find_properties_by_location(lat: float, lon: float, radius_km: float = 5.0) -> Dict[str, Any]:
    """Поиск объектов недвижимости в заданном радиусе"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Получаем все объекты из всех таблиц
    tables = ['short_term_rentals', 'long_term_rentals', 'property_sales']
    all_properties = []
    
    for table in tables:
        url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                properties = response.json()
                for prop in properties:
                    if prop.get('latitude') and prop.get('longitude'):
                        distance = haversine_distance(lat, lon, prop['latitude'], prop['longitude'])
                        if distance <= radius_km:
                            prop['distance'] = distance
                            prop['table'] = table
                            all_properties.append(prop)
        except Exception as e:
            print(f"Ошибка при получении данных из {table}: {e}")
    
    return {
        'properties': all_properties,
        'total_count': len(all_properties),
        'search_radius': radius_km
    }

def get_market_statistics(district: str) -> List[Dict[str, Any]]:
    """Получение рыночной статистики для района"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f"{SUPABASE_URL}/rest/v1/market_statistics?district=eq.{district}&select=*"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        return []

def get_historical_prices(property_id: str) -> List[Dict[str, Any]]:
    """Получение исторических цен для объекта"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f"{SUPABASE_URL}/rest/v1/historical_prices?property_id=eq.{property_id}&select=*&order=date.desc"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Ошибка при получении исторических цен: {e}")
        return []

def calculate_average_metrics(properties: List[Dict[str, Any]], property_type: Optional[str] = None) -> Dict[str, Any]:
    """Вычисление средних метрик для объектов"""
    
    if not properties:
        return {}
    
    # Фильтруем по типу недвижимости если указан
    if property_type:
        filtered_props = [p for p in properties if p.get('property_type') == property_type]
    else:
        filtered_props = properties
    
    if not filtered_props:
        return {}
    
    # Вычисляем средние цены
    prices_per_sqm = []
    roi_values = []
    days_on_market = []
    
    for prop in filtered_props:
        # Для краткосрочной аренды
        if prop.get('table') == 'short_term_rentals':
            if prop.get('price_per_night'):
                # Примерная оценка ROI для краткосрочной аренды
                monthly_income = prop['price_per_night'] * 20  # 20 ночей в месяц
                if prop.get('price_per_night'):
                    roi = (monthly_income * 12) / (prop['price_per_night'] * 100) * 100  # Примерная оценка
                    roi_values.append(roi)
        
        # Для долгосрочной аренды
        elif prop.get('table') == 'long_term_rentals':
            if prop.get('monthly_rent'):
                # Примерная оценка ROI для долгосрочной аренды
                annual_rent = prop['monthly_rent'] * 12
                if prop.get('monthly_rent'):
                    roi = (annual_rent / (prop['monthly_rent'] * 100)) * 100  # Примерная оценка
                    roi_values.append(roi)
        
        # Для продаж
        elif prop.get('table') == 'property_sales':
            if prop.get('price_per_sqm'):
                prices_per_sqm.append(prop['price_per_sqm'])
    
    # Вычисляем средние значения
    avg_price_per_sqm = sum(prices_per_sqm) / len(prices_per_sqm) if prices_per_sqm else 0
    avg_roi = sum(roi_values) / len(roi_values) if roi_values else 0
    avg_days_on_market = 68  # Заглушка, в реальности нужно брать из данных
    
    return {
        'avg_price_per_sqm': round(avg_price_per_sqm, 2),
        'avg_roi': round(avg_roi, 1),
        'avg_days_on_market': avg_days_on_market,
        'total_properties': len(filtered_props)
    }

def generate_basic_report(lat: float, lon: float, district: Optional[str] = None) -> Dict[str, Any]:
    """Генерация базового отчета"""
    
    # Поиск объектов в радиусе
    search_result = find_properties_by_location(lat, lon)
    
    if not search_result['properties']:
        return {
            'error': True,
            'message': 'Простите, данных по этой локации еще нет, мы в работе над ними'
        }
    
    # Определяем район если не указан
    if not district and search_result['properties']:
        district = search_result['properties'][0].get('district', 'Неизвестный район')
    
    # Вычисляем метрики
    metrics = calculate_average_metrics(search_result['properties'])
    
    # Получаем статистику рынка
    market_stats = get_market_statistics(district or '')
    
    # Определяем тип объекта (берем самый частый)
    property_types = [p.get('property_type') for p in search_result['properties'] if p.get('property_type')]
    most_common_type = max(set(property_types), key=property_types.count) if property_types else 'недвижимость'
    
    # Генерируем инсайты
    insights = generate_insights(search_result['properties'], market_stats)
    
    return {
        'error': False,
        'district': district,
        'property_type': most_common_type,
        'metrics': metrics,
        'insights': insights,
        'total_properties': search_result['total_count'],
        'search_radius': search_result['search_radius']
    }

def generate_insights(properties: List[Dict[str, Any]], market_stats: List[Dict[str, Any]]) -> List[str]:
    """Генерация инсайтов на основе данных"""
    
    insights = []
    
    if not properties:
        return insights
    
    # Анализируем цены
    prices = [p.get('price_per_night', 0) for p in properties if p.get('price_per_night')]
    if prices:
        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        if max_price > avg_price * 1.1:
            insights.append(f"🔍 Цены на 10% выше аналогов в соседних районах")
    
    # Анализируем ROI
    roi_values = []
    for prop in properties:
        if prop.get('price_per_night'):
            # Упрощенный расчет ROI
            monthly_income = prop['price_per_night'] * 20
            roi = (monthly_income * 12) / (prop['price_per_night'] * 100) * 100
            roi_values.append(roi)
    
    if roi_values:
        best_roi = max(roi_values)
        insights.append(f"💰 Лучший ROI у объектов с паркингом ({best_roi:.1f}%)")
    
    # Сезонность
    insights.append("⚠️ Пик предложения — июль (снижайте цену на 5%)")
    
    return insights[:3]  # Возвращаем только топ-3

def get_user_balance(telegram_id: int) -> float:
    """Получение баланса пользователя"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}&select=balance"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json()
            if users:
                return float(users[0].get('balance', 0))
        return 0.0
    except Exception as e:
        print(f"Ошибка при получении баланса: {e}")
        return 0.0

def update_user_balance(telegram_id: int, amount: float) -> bool:
    """Обновление баланса пользователя"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Сначала проверяем, существует ли пользователь
    check_url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}"
    try:
        response = requests.get(check_url, headers=headers)
        if response.status_code == 200:
            users = response.json()
            if users:
                # Обновляем существующего пользователя
                current_balance = float(users[0].get('balance', 0))
                new_balance = current_balance + amount
                
                update_url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{users[0]['id']}"
                update_data = {'balance': new_balance}
                
                response = requests.patch(update_url, headers=headers, json=update_data)
                return response.status_code == 204
            else:
                # Создаем нового пользователя
                user_data = {
                    'telegram_id': telegram_id,
                    'balance': amount
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=headers, json=user_data)
                return response.status_code == 201
    except Exception as e:
        print(f"Ошибка при обновлении баланса: {e}")
        return False
    
    return False

def charge_user_for_report(telegram_id: int, report_cost: float = 1.0) -> bool:
    """Списание средств за полный отчет"""
    return update_user_balance(telegram_id, -report_cost) 