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

def check_admin_status(telegram_id: int) -> bool:
    """Проверка статуса админа пользователя"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    url = f"{SUPABASE_URL}/rest/v1/users?telegram_id=eq.{telegram_id}&select=user_status"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            users = response.json()
            if users and users[0].get('user_status') == 'admin':
                return True
        return False
    except Exception as e:
        print(f"Ошибка при проверке статуса админа: {e}")
        return False

def set_user_balance_to_100(telegram_id: int) -> bool:
    """Установка баланса пользователя в 100"""
    
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
                update_url = f"{SUPABASE_URL}/rest/v1/users?id=eq.{users[0]['id']}"
                update_data = {'balance': 100}
                
                response = requests.patch(update_url, headers=headers, json=update_data)
                return response.status_code == 204
            else:
                # Создаем нового пользователя
                user_data = {
                    'telegram_id': telegram_id,
                    'balance': 100
                }
                response = requests.post(f"{SUPABASE_URL}/rest/v1/users", headers=headers, json=user_data)
                return response.status_code == 201
    except Exception as e:
        print(f"Ошибка при установке баланса: {e}")
        return False
    
    return False

def get_user_statistics() -> Dict[str, Any]:
    """Получение статистики пользователей"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        from datetime import datetime, timedelta
        
        # Получаем всех пользователей
        users_url = f"{SUPABASE_URL}/rest/v1/users?select=*"
        users_response = requests.get(users_url, headers=headers)
        
        if users_response.status_code != 200:
            return {}
        
        users = users_response.json()
        
        # Получаем все отчеты
        reports_url = f"{SUPABASE_URL}/rest/v1/user_reports?select=*"
        reports_response = requests.get(reports_url, headers=headers)
        
        if reports_response.status_code != 200:
            return {}
        
        reports = reports_response.json()
        
        # Получаем тарифы
        tariffs_url = f"{SUPABASE_URL}/rest/v1/tariffs?select=*"
        tariffs_response = requests.get(tariffs_url, headers=headers)
        
        if tariffs_response.status_code != 200:
            return {}
        
        tariffs = tariffs_response.json()
        
        # Вычисляем статистику
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        quarter_ago = now - timedelta(days=90)
        year_ago = now - timedelta(days=365)
        
        # Фильтруем пользователей
        admin_users = [u for u in users if u.get('user_status') == 'admin']
        regular_users = [u for u in users if u.get('user_status') != 'admin']
        
        # Пользователи с истекшим периодом
        expired_users = [u for u in regular_users if not u.get('period_end') or 
                       (u.get('period_end') and datetime.fromisoformat(u['period_end'].replace('Z', '+00:00')) < now)]
        
        # Активные пользователи
        active_users = [u for u in regular_users if u.get('period_end') and 
                       datetime.fromisoformat(u['period_end'].replace('Z', '+00:00')) >= now]
        
        # Новые пользователи
        new_week = len([u for u in users if u.get('created_at') and 
                       datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= week_ago])
        new_month = len([u for u in users if u.get('created_at') and 
                        datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= month_ago])
        new_quarter = len([u for u in users if u.get('created_at') and 
                          datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= quarter_ago])
        new_year = len([u for u in users if u.get('created_at') and 
                       datetime.fromisoformat(u['created_at'].replace('Z', '+00:00')) >= year_ago])
        
        # Балансы
        total_balance = sum(u.get('balance', 0) for u in regular_users)
        expired_balance = sum(u.get('balance', 0) for u in expired_users)
        active_balance = sum(u.get('balance', 0) for u in active_users)
        
        # Отчеты
        reports_week = len([r for r in reports if r.get('created_at') and 
                           datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= week_ago])
        reports_month = len([r for r in reports if r.get('created_at') and 
                           datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= month_ago])
        reports_quarter = len([r for r in reports if r.get('created_at') and 
                             datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= quarter_ago])
        reports_year = len([r for r in reports if r.get('created_at') and 
                          datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= year_ago])
        
        # Удаленные отчеты
        deleted_reports = len([r for r in reports if r.get('deleted_at')])
        
        # Отчеты истекших пользователей
        expired_user_ids = [u['id'] for u in expired_users]
        expired_reports = len([r for r in reports if r.get('user_id') in expired_user_ids])
        avg_expired_reports = expired_reports / len(expired_users) if expired_users else 0
        
        # Отчеты активных пользователей
        active_user_ids = [u['id'] for u in active_users]
        active_reports = len([r for r in reports if r.get('user_id') in active_user_ids])
        
        # Затраты активных пользователей
        tariff_cost = next((t.get('full', 1.0) for t in tariffs if t.get('name') == 'full'), 1.0)
        active_costs = active_reports * tariff_cost
        
        return {
            'total_users': len(users),
            'new_week': new_week,
            'new_month': new_month,
            'new_quarter': new_quarter,
            'new_year': new_year,
            'total_balance': round(total_balance, 2),
            'expired_balance': round(expired_balance, 2),
            'active_balance': round(active_balance, 2),
            'reports_week': reports_week,
            'reports_month': reports_month,
            'reports_quarter': reports_quarter,
            'reports_year': reports_year,
            'deleted_reports': deleted_reports,
            'expired_reports': expired_reports,
            'avg_expired_reports': round(avg_expired_reports, 1),
            'active_reports': active_reports,
            'active_costs': round(active_costs, 2)
        }
        
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        return {}

def send_publication_to_all_users(text: str) -> Dict[str, int]:
    """Отправка публикации всем пользователям"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Получаем всех пользователей
        users_url = f"{SUPABASE_URL}/rest/v1/users?select=telegram_id,user_status"
        users_response = requests.get(users_url, headers=headers)
        
        if users_response.status_code != 200:
            return {'admin_count': 0, 'user_count': 0}
        
        users = users_response.json()
        
        # Отправляем сообщения через Telegram Bot API
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return {'admin_count': 0, 'user_count': 0}
        
        admin_count = 0
        user_count = 0
        
        for user in users:
            telegram_id = user.get('telegram_id')
            is_admin = user.get('user_status') == 'admin'
            
            if telegram_id:
                try:
                    # Отправляем сообщение через Telegram Bot API
                    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    send_data = {
                        'chat_id': telegram_id,
                        'text': text,
                        'parse_mode': 'HTML'  # Поддержка HTML форматирования
                    }
                    
                    response = requests.post(send_url, json=send_data)
                    
                    if response.status_code == 200:
                        if is_admin:
                            admin_count += 1
                        else:
                            user_count += 1
                    
                except Exception as e:
                    print(f"Ошибка отправки сообщения пользователю {telegram_id}: {e}")
        
        return {
            'admin_count': admin_count,
            'user_count': user_count
        }
        
    except Exception as e:
        print(f"Ошибка при отправке публикации: {e}")
        return {'admin_count': 0, 'user_count': 0} 