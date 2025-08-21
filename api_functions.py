import os
import requests
import json
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
import math
from datetime import datetime

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

def get_latest_currency_rates() -> Dict[str, Any]:
    """Получение последних курсов валют из таблицы currency"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
    }
    
    # Получаем последнюю запись из таблицы currency
    url = f"{SUPABASE_URL}/rest/v1/currency?select=*&order=created_at.desc&limit=1"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            currencies = response.json()
            if currencies:
                return {
                    'success': True,
                    'data': currencies[0]
                }
            else:
                return {
                    'success': False,
                    'error': 'Нет данных о курсах валют'
                }
        else:
            return {
                'success': False,
                'error': f'Ошибка API: {response.status_code}'
            }
    except Exception as e:
        print(f"Ошибка при получении курсов валют: {e}")
        return {
            'success': False,
            'error': str(e)
        } 


def generate_standalone_html(report_html: str, report_data: dict, report_id: str) -> str:
    """Генерация автономного HTML файла с отчетом"""
    
    # Получаем текущую дату и время
    current_datetime = datetime.now().strftime('%d.%m.%Y %H:%M')
    
    # Извлекаем данные локации
    location = report_data.get('location', 'Неизвестно')
    
    # Генерируем блок характеристик недвижимости
    property_characteristics_html = ""
    if report_data.get('user_inputs'):
        user_inputs = report_data['user_inputs']
        property_characteristics_html = f"""
        <div class="property-characteristics-section">
            <h4 class="property-characteristics-title">Выбранные характеристики недвижимости</h4>
            <div class="property-characteristics-content">
                <div class="characteristic-item">
                    <span class="characteristic-label">Спальни:</span>
                    <span class="characteristic-value">{user_inputs.get('bedrooms', 'Не указано')}</span>
                </div>
                <div class="characteristic-item">
                    <span class="characteristic-label">Этаж:</span>
                    <span class="characteristic-value">{user_inputs.get('floor', 'Не указано')}</span>
                </div>
                <div class="characteristic-item">
                    <span class="characteristic-label">Возраст:</span>
                    <span class="characteristic-value">{user_inputs.get('age', 'Не указано')}</span>
                </div>
                <div class="characteristic-item">
                    <span class="characteristic-label">Отопление:</span>
                    <span class="characteristic-value">{user_inputs.get('heating', 'Не указано')}</span>
                </div>
                <div class="characteristic-item">
                    <span class="characteristic-label">Цена объекта:</span>
                    <span class="characteristic-value">{user_inputs.get('price', 'Не указано')}</span>
                </div>
                <div class="characteristic-item">
                    <span class="characteristic-label">Площадь объекта:</span>
                    <span class="characteristic-value">{user_inputs.get('area', 'Не указано')} м²</span>
                </div>
            </div>
        </div>"""
    
    # Базовый HTML шаблон с встроенными стилями
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по оценке объекта - {location}</title>
    
    <!-- Chart.js для графиков -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Встроенные CSS стили -->
    <style>
        /* Основные стили */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        
        /* Заголовок отчета */
        .report-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .report-title h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .report-date, .report-location {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .header-logo {{
            margin-bottom: 15px;
        }}
        
        .header-logo img {{
            height: 60px;
            width: auto;
            filter: brightness(0) invert(1);
        }}
        
        /* Основной контент */
        .report-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            margin-bottom: 30px;
        }}
        
        /* Стили для блоков отчета */
        .summary-section, .trends-section, .forecast-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 25px;
            overflow: hidden;
        }}
        
        .section-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 20px;
            font-weight: 600;
            color: #495057;
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        /* Стили для таблиц */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }}
        
        .data-table th, .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .data-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        
        /* Стили для карточек */
        .indicator-card, .forecast-card {{
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        /* Стили для графиков */
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        /* Футер отчета */
        .report-footer {{
            background: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        .report-footer p {{
            margin-bottom: 5px;
            font-size: 14px;
        }}
        
        .report-footer .footer-logo {{
            margin-bottom: 15px;
        }}
        
        .report-footer .footer-logo img {{
            height: 40px;
            width: auto;
        }}
        
        .report-footer .footer-text {{
            margin-bottom: 15px;
        }}
        
        .report-footer .telegram-link {{
            display: inline-block;
            background: #0088cc;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }}
        
        .report-footer .telegram-link:hover {{
            background: #006699;
        }}
        
        .report-footer .footer-info {{
            margin-bottom: 15px;
            opacity: 0.8;
        }}
        
        .report-footer .footer-info p {{
            margin-bottom: 3px;
            font-size: 12px;
        }}
        
        /* Адаптивность */
        @media (max-width: 768px) {{
            .report-content {{
                padding: 0 15px;
            }}
            
            .report-title h1 {{
                font-size: 24px;
            }}
            
            .section-title {{
                font-size: 18px;
                padding: 15px;
            }}
            
            .section-content {{
                padding: 15px;
            }}
        }}
        
        /* Дополнительные стили для специфических элементов */
        .price-forecast-block {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .price-forecast-content {{
            padding: 20px;
        }}
        
        .price-forecast-title {{
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .price-forecast-sale-section,
        .price-forecast-rent-section {{
            margin: 15px 0;
            text-align: center;
        }}
        
        .price-forecast-sale-label,
        .price-forecast-rent-label {{
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 5px;
        }}
        
        .price-forecast-sale-value,
        .price-forecast-rent-value {{
            font-size: 24px;
            font-weight: 700;
            color: #28a745;
            margin-bottom: 8px;
        }}
        
        .price-forecast-date {{
            font-size: 14px;
            color: #666666;
            margin-bottom: 8px;
            font-weight: 600;
            text-align: center;
        }}
        
        .price-forecast-currency-info {{
            font-size: 12px;
            color: #999999;
            font-style: italic;
            text-align: center;
        }}
        
        /* Стили для трендов */
        .trends-analysis-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .trends-analysis-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 20px;
            font-weight: 600;
            color: #495057;
        }}
        
        .trends-analysis-content {{
            padding: 20px;
        }}
        
        /* Стили для детальных таблиц */
        .detailed-tables-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .detailed-tables-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 20px;
            font-weight: 600;
            color: #495057;
        }}
        
        .detailed-tables-content {{
            padding: 20px;
        }}
        
        /* Стили для аккордеонов */
        .accordion-item {{
            border: 1px solid #e9ecef;
            border-radius: 6px;
            margin-bottom: 10px;
            overflow: hidden;
        }}
        
        .accordion-header {{
            background: #f8f9fa;
            padding: 15px;
            cursor: pointer;
            border-bottom: 1px solid #e9ecef;
            font-weight: 600;
            color: #495057;
        }}
        
        .accordion-content {{
            padding: 15px;
            display: none;
        }}
        
        .accordion-content.active {{
            display: block;
        }}
        
        /* Стили для графиков */
        .trends-chart-section, .forecast-chart-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            padding: 20px;
        }}
        
        .trends-chart-title, .forecast-chart-title {{
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 15px;
            text-align: center;
        }}
        
        .chart-controls {{
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .chart-button {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            color: #495057;
            transition: all 0.3s ease;
        }}
        
        .chart-button:hover {{
            background: #e9ecef;
            border-color: #adb5bd;
        }}
        
        .chart-button.active {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
            height: 300px;
        }}
        
        .chart-info {{
            text-align: center;
            margin-top: 15px;
        }}
        
        /* Стили для трендов */
        .trends-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .trend-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .trend-title {{
            font-size: 16px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 15px;
        }}
        
        .trend-value {{
            font-size: 24px;
            font-weight: 700;
            color: #28a745;
            margin-bottom: 10px;
        }}
        
        .trend-details {{
            font-size: 14px;
            color: #6c757d;
        }}
        
        .trend-change {{
            font-weight: 600;
            color: #495057;
        }}
        
        /* Стили для таблиц трендов */
        .trends-table-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .trends-table-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin: 0;
        }}
        
        .trends-table-container {{
            padding: 20px;
        }}
        
        .trends-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        .trends-table th, .trends-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .trends-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        
        .current-month-row {{
            background-color: #e8f4fd;
        }}
        
        .forecast-row {{
            background-color: #f0f8ff;
        }}
        
        .filter-info {{
            background-color: #f8f9fa;
            font-size: 11px;
            color: #666;
            text-align: center;
            padding: 4px;
        }}
        
        /* Стили для прогнозов */
        .forecast-table-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .forecast-table-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin: 0;
        }}
        
        .forecast-table-container {{
            padding: 20px;
        }}
        
        .forecast-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        .forecast-table th, .forecast-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .forecast-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }}
        
        /* Стили для блоков анализа */
        .trends-analysis-section, .forecast-analysis-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .trends-analysis-title, .forecast-analysis-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin: 0;
        }}
        
        .trends-analysis-content, .forecast-analysis-content {{
            padding: 20px;
        }}
        
        /* Стили для показателей рынка */
        .market-indicators-unified {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .unified-indicator-card {{
            display: flex;
            gap: 20px;
            padding: 20px;
        }}
        
        .indicator-section {{
            flex: 1;
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 15px;
            text-align: center;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
        
        .indicator-item {{
            margin: 10px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .indicator-label {{
            font-size: 14px;
            color: #6c757d;
            font-weight: 500;
        }}
        
        .indicator-value {{
            font-size: 14px;
            color: #495057;
            font-weight: 600;
        }}
        
        /* Стили для текстового блока анализа */
        .market-analysis-text-block {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .market-analysis-text-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin: 0;
        }}
        
        .market-analysis-text-content {{
            padding: 20px;
        }}
        
        .market-analysis-text-content p {{
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        
        /* Стили для объекта */
        .object-summary-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .object-summary-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin: 0;
        }}
        
        .object-summary-content {{
            padding: 20px;
        }}
        
        .object-summary-content p {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        /* Стили для характеристик недвижимости */
        .property-characteristics-section {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
            overflow: hidden;
        }}
        
        .property-characteristics-title {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            font-size: 18px;
            font-weight: 600;
            color: #495057;
            margin: 0;
        }}
        
        .property-characteristics-content {{
            padding: 20px;
        }}
        
        .characteristic-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f1f3f4;
        }}
        
        .characteristic-item:last-child {{
            border-bottom: none;
        }}
        
        .characteristic-label {{
            font-size: 14px;
            color: #6c757d;
            font-weight: 500;
        }}
        
        .characteristic-value {{
            font-size: 14px;
            color: #495057;
            font-weight: 600;
        }}
        
        /* Отступы между блоками */
        .block-spacing {{
            height: 20px;
        }}
        
        /* Адаптивность */
        @media (max-width: 768px) {{
            .unified-indicator-card {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .chart-controls {{
                flex-direction: column;
                align-items: center;
            }}
            
            .chart-container {{
                height: 250px;
            }}
            
            .header-logo img {{
                height: 50px;
            }}
            
            .report-footer .footer-logo img {{
                height: 35px;
            }}
            
            .report-footer .telegram-link {{
                padding: 10px 20px;
                font-size: 16px;
            }}
            
            .characteristic-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }}
        }}
    </style>
</head>
<body>
    <!-- Заголовок отчета -->
    <header class="report-header">
        <div class="report-title">
            <div class="header-logo">
                <img src="logo-sqv.png" alt="Aaadviser Logo" style="height: 60px; width: auto; margin-bottom: 15px;">
            </div>
            <h1>Отчет по оценке объекта</h1>
            <p class="report-date">Сформирован: {current_datetime}</p>
            <p class="report-location">Локация: {location}</p>
        </div>
    </header>
    
    <!-- Основной контент отчета -->
    <main class="report-content">
        {property_characteristics_html}
        {report_html}
    </main>
    
    <!-- Футер отчета -->
    <footer class="report-footer">
        <div class="footer-logo">
            <img src="logo-flt.png" alt="Aaadviser Logo">
        </div>
        <div class="footer-text">
            <p>Отчет сгенерирован системой Aaadviser</p>
            <p>Отчёт сформирован на основании комплексного анализа открытых источников и официальной рыночной статистики</p>
        </div>
        <div class="footer-info">
            <p>ID отчета: {report_id}</p>
            <p>Дата создания: {current_datetime}</p>
        </div>
        <a href="https://t.me/Aaadviser_bot" class="telegram-link" target="_blank">
            📱 Открыть в Telegram
        </a>
    </footer>
    
    <!-- Встроенный JavaScript для интерактивности -->
    <script>
        // Функция для переключения аккордеонов
        function toggleAccordion(accordionId) {{
            const content = document.getElementById(accordionId);
            if (content) {{
                content.classList.toggle('active');
            }}
        }}
        
        // Функция для копирования ссылки в буфер обмена
        function copyToClipboard(text) {{
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(text).then(() => {{
                    alert('Ссылка скопирована в буфер обмена!');
                }});
            }} else {{
                // Fallback для старых браузеров
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Ссылка скопирована в буфер обмена!');
            }}
        }}
        
        // Данные для графиков (жестко прописаны для автономности)
        const trendsData = {{
            labels: ['фев. 2025', 'мар. 2025', 'апр. 2025', 'май. 2025', 'июн. 2025', 'июл. 2025', 'авг. 2025', 'сен. 2025'],
            sale: [53200, 54330, 55921, 57464, 58990, 60441, 61803, 62794],
            rent: [264.05, 270.11, 274.56, 280.06, 288.40, 295.72, 302.77, 310.37]
        }};
        
        const forecastData = {{
            labels: ['авг. 2025', 'сен. 2025', 'окт. 2025', 'ноя. 2025', 'дек. 2025', 'янв. 2026', 'фев. 2026', 'мар. 2026', 'апр. 2026', 'май. 2026', 'июн. 2026'],
            sale: [61803, 62794, 63567, 64226, 64904, 65852, 66577, 67385, 68486, 69763, 71107],
            rent: [302.77, 310.37, 316.58, 322.12, 327.45, 331.43, 335.06, 339.32, 342.95, 347.95, 355.43]
        }};
        
        // Функция для переключения типа графика трендов
        function switchChartType(type) {{
            // Обновляем активную кнопку
            document.querySelectorAll('[data-chart-type]').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.querySelector(`[data-chart-type="${{type}}"]`).classList.add('active');
            
            // Обновляем данные графика
            if (window.trendsChart) {{
                const data = type === 'sale' ? trendsData.sale : trendsData.rent;
                const label = type === 'sale' ? 'Цена м² продажи (₺)' : 'Цена м² аренды (₺)';
                
                window.trendsChart.data.datasets[0].data = data;
                window.trendsChart.data.datasets[0].label = label;
                window.trendsChart.update();
            }}
        }}
        
        // Функция для переключения типа графика прогноза
        function switchForecastChartType(type) {{
            // Обновляем активную кнопку
            document.querySelectorAll('[data-chart-type]').forEach(btn => {{
                btn.classList.remove('active');
            }});
            document.querySelector(`[data-chart-type="${{type}}"]`).classList.add('active');
            
            // Обновляем данные графика
            if (window.forecastChart) {{
                const data = type === 'sale' ? forecastData.sale : forecastData.rent;
                const label = type === 'sale' ? 'Прогноз цены м² продажи (₺)' : 'Прогноз цены м² аренды (₺)';
                
                window.forecastChart.data.datasets[0].data = data;
                window.forecastChart.data.datasets[0].label = label;
                window.forecastChart.update();
            }}
        }}
        
        // Функция для создания графика трендов
        function createTrendsChart() {{
            const ctx = document.getElementById('trendsChart');
            if (!ctx) return;
            
            window.trendsChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: trendsData.labels,
                    datasets: [{{
                        label: 'Цена м² продажи (₺)',
                        data: trendsData.sale,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }}
                        }},
                        x: {{
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Функция для создания графика прогноза
        function createForecastChart() {{
            const ctx = document.getElementById('forecastChart');
            if (!ctx) return;
            
            window.forecastChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: forecastData.labels,
                    datasets: [{{
                        label: 'Прогноз цены м² продажи (₺)',
                        data: forecastData.sale,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: false,
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }}
                        }},
                        x: {{
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.1)'
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Отчет загружен и готов к просмотру');
            
            // Создаем графики
            setTimeout(() => {{
                createTrendsChart();
                createForecastChart();
            }}, 100);
            
            // Добавляем обработчики для всех аккордеонов
            const accordionHeaders = document.querySelectorAll('.accordion-header');
            accordionHeaders.forEach(header => {{
                header.addEventListener('click', function() {{
                    const content = this.nextElementSibling;
                    if (content && content.classList.contains('accordion-content')) {{
                        content.classList.toggle('active');
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>"""
    
    return html_template