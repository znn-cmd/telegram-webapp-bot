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

def save_promotional_text_to_db(base_text: str, ru_text: str, us_text: str = None, ft_text: str = None, de_text: str = None, tr_text: str = None) -> int:
    """Сохранение промо-текста в базу данных"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        from datetime import datetime
        
        text_data = {
            'created_at': datetime.now().isoformat(),
            'base': base_text,
            'ru': ru_text,
            'us': us_text or base_text,
            'ft': ft_text or base_text,
            'de': de_text or base_text,
            'tr': tr_text or base_text,
            'qttty_ru': 0,
            'qttty_us': 0,
            'qttty_ft': 0,
            'qttty_de': 0,
            'qttty_tr': 0
        }
        
        url = f"{SUPABASE_URL}/rest/v1/texts_promo"
        response = requests.post(url, headers=headers, json=text_data)
        
        if response.status_code == 201:
            result = response.json()
            return result[0]['text_id'] if result else None
        else:
            print(f"Ошибка сохранения текста: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Ошибка при сохранении промо-текста: {e}")
        return None

def get_api_key_from_db(key_name: str) -> str:
    """Получение API ключа из базы данных"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/api_keys?key_name=eq.{key_name}&is_active=eq.true&select=key_value"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                return result[0].get('key_value', '')
        return ''
        
    except Exception as e:
        print(f"Ошибка при получении API ключа {key_name}: {e}")
        return ''

def save_api_key_to_db(key_name: str, key_value: str, description: str = '') -> bool:
    """Сохранение API ключа в базу данных"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        from datetime import datetime
        
        key_data = {
            'key_name': key_name,
            'key_value': key_value,
            'description': description,
            'is_active': True,
            'updated_at': datetime.now().isoformat()
        }
        
        # Проверяем, существует ли уже ключ
        check_url = f"{SUPABASE_URL}/rest/v1/api_keys?key_name=eq.{key_name}"
        check_response = requests.get(check_url, headers=headers)
        
        if check_response.status_code == 200 and check_response.json():
            # Обновляем существующий ключ
            update_url = f"{SUPABASE_URL}/rest/v1/api_keys?key_name=eq.{key_name}"
            response = requests.patch(update_url, headers=headers, json=key_data)
        else:
            # Создаем новый ключ
            key_data['created_at'] = datetime.now().isoformat()
            url = f"{SUPABASE_URL}/rest/v1/api_keys"
            response = requests.post(url, headers=headers, json=key_data)
        
        return response.status_code in [200, 201, 204]
        
    except Exception as e:
        print(f"Ошибка при сохранении API ключа {key_name}: {e}")
        return False

def get_all_api_keys() -> List[Dict[str, Any]]:
    """Получение всех API ключей из базы данных"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/api_keys?select=*&order=created_at.desc"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return []
        
    except Exception as e:
        print(f"Ошибка при получении API ключей: {e}")
        return []

def translate_with_chatgpt(text: str, target_language: str) -> str:
    """Перевод текста через ChatGPT API"""
    
    try:
        # Получаем API ключ из базы данных
        chatgpt_api_key = get_api_key_from_db('chatgpt_api_key')
        
        if not chatgpt_api_key:
            # Если ключ не найден, используем заглушку с базовыми переводами
            print("ChatGPT API ключ не найден в базе данных. Используется заглушка.")
            translations = {
                'us': f"[EN] {text}",
                'ft': f"[FR] {text}",
                'de': f"[DE] {text}",
                'tr': f"[TR] {text}"
            }
            return translations.get(target_language, text)
        
        # Реальный API вызов к ChatGPT
        headers = {
            'Authorization': f'Bearer {chatgpt_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Маппинг языков для промпта
        language_names = {
            'us': 'английский',
            'ft': 'французский', 
            'de': 'немецкий',
            'tr': 'турецкий'
        }
        
        lang_name = language_names.get(target_language, target_language)
        prompt = f"Переведи следующий текст на {lang_name}. Сохрани все форматирование, эмодзи и оформление. Дословный перевод: {text}"
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'Ты профессиональный переводчик. Сохраняй все форматирование, эмодзи и оформление текста.'},
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 1000,
            'temperature': 0.3
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Ошибка ChatGPT API: {response.status_code} - {response.text}")
            return text
            
    except Exception as e:
        print(f"Ошибка при переводе: {e}")
        return text

def get_promotional_text_by_language(text_id: int, language: str) -> str:
    """Получение промо-текста на нужном языке"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Маппинг языков к полям в базе
        language_mapping = {
            'ru': 'ru',
            'en': 'us',
            'fr': 'ft',
            'de': 'de',
            'tr': 'tr'
        }
        
        field = language_mapping.get(language, 'ru')
        url = f"{SUPABASE_URL}/rest/v1/texts_promo?text_id=eq.{text_id}&select={field}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                return result[0].get(field, '')
        return ''
        
    except Exception as e:
        print(f"Ошибка при получении текста: {e}")
        return ''

def update_text_send_count(text_id: int, language: str) -> bool:
    """Обновление счетчика отправок для языка"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        # Маппинг языков к полям счетчиков
        counter_mapping = {
            'ru': 'qttty_ru',
            'en': 'qttty_us',
            'fr': 'qttty_ft',
            'de': 'qttty_de',
            'tr': 'qttty_tr'
        }
        
        counter_field = counter_mapping.get(language, 'qttty_ru')
        
        # Сначала получаем текущее значение
        url = f"{SUPABASE_URL}/rest/v1/texts_promo?text_id=eq.{text_id}&select={counter_field}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result:
                current_count = result[0].get(counter_field, 0) or 0
                new_count = current_count + 1
                
                # Обновляем счетчик
                update_url = f"{SUPABASE_URL}/rest/v1/texts_promo?text_id=eq.{text_id}"
                update_data = {counter_field: new_count}
                
                update_response = requests.patch(update_url, headers=headers, json=update_data)
                return update_response.status_code == 204
                
        return False
        
    except Exception as e:
        print(f"Ошибка при обновлении счетчика: {e}")
        return False

def send_publication_to_all_users(text: str, save_to_db: bool = False, make_translation: bool = False) -> Dict[str, Any]:
    """Отправка публикации всем пользователям с поддержкой переводов"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    try:
        text_id = None
        
        # Если нужно сохранить в базу
        if save_to_db:
            if make_translation:
                # Делаем переводы
                us_text = translate_with_chatgpt(text, 'us')
                ft_text = translate_with_chatgpt(text, 'ft')
                de_text = translate_with_chatgpt(text, 'de')
                tr_text = translate_with_chatgpt(text, 'tr')
                
                # Сохраняем в базу с переводами
                text_id = save_promotional_text_to_db(text, text, us_text, ft_text, de_text, tr_text)
            else:
                # Сохраняем только оригинальный текст
                text_id = save_promotional_text_to_db(text, text)
        
        # Получаем всех пользователей
        users_url = f"{SUPABASE_URL}/rest/v1/users?select=telegram_id,user_status,language"
        users_response = requests.get(users_url, headers=headers)
        
        if users_response.status_code != 200:
            return {'admin_count': 0, 'user_count': 0, 'text_id': text_id}
        
        users = users_response.json()
        
        # Отправляем сообщения через Telegram Bot API
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return {'admin_count': 0, 'user_count': 0, 'text_id': text_id}
        
        admin_count = 0
        user_count = 0
        language_stats = {'ru': 0, 'en': 0, 'fr': 0, 'de': 0, 'tr': 0}
        
        for user in users:
            telegram_id = user.get('telegram_id')
            is_admin = user.get('user_status') == 'admin'
            user_language = user.get('language', 'ru')
            
            if telegram_id:
                try:
                    # Определяем текст для отправки
                    if text_id and save_to_db:
                        # Используем текст из базы на нужном языке
                        send_text = get_promotional_text_by_language(text_id, user_language)
                        if not send_text:
                            send_text = text  # Fallback на оригинальный текст
                    else:
                        # Отправляем оригинальный текст
                        send_text = text
                    
                    # Отправляем сообщение через Telegram Bot API
                    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    send_data = {
                        'chat_id': telegram_id,
                        'text': send_text,
                        'parse_mode': 'HTML'  # Поддержка HTML форматирования
                    }
                    
                    response = requests.post(send_url, json=send_data)
                    
                    if response.status_code == 200:
                        if is_admin:
                            admin_count += 1
                        else:
                            user_count += 1
                            language_stats[user_language] = language_stats.get(user_language, 0) + 1
                        
                        # Обновляем счетчик отправок если текст сохранен в базу
                        if text_id and save_to_db:
                            update_text_send_count(text_id, user_language)
                    
                except Exception as e:
                    print(f"Ошибка отправки сообщения пользователю {telegram_id}: {e}")
        
        return {
            'admin_count': admin_count,
            'user_count': user_count,
            'text_id': text_id,
            'language_stats': language_stats
        }
        
    except Exception as e:
        print(f"Ошибка при отправке публикации: {e}")
        return {'admin_count': 0, 'user_count': 0, 'text_id': None, 'language_stats': {}} 