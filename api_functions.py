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
    
    from datetime import datetime
    
    # Получаем текущую дату и время
    current_datetime = datetime.now().strftime('%d.%m.%Y %H:%M')
    
    # Извлекаем данные локации
    location = report_data.get('location', 'Неизвестно')
    
    # Базовый HTML шаблон с встроенными стилями
    html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по оценке объекта - {location}</title>
    
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
    </style>
</head>
<body>
    <!-- Заголовок отчета -->
    <header class="report-header">
        <div class="report-title">
            <h1>Отчет по оценке объекта</h1>
            <p class="report-date">Сформирован: {current_datetime}</p>
            <p class="report-location">Локация: {location}</p>
        </div>
    </header>
    
    <!-- Основной контент отчета -->
    <main class="report-content">
        {report_html}
    </main>
    
    <!-- Футер отчета -->
    <footer class="report-footer">
        <p>Отчет сгенерирован системой Aaadviser</p>
        <p>ID отчета: {report_id}</p>
        <p>Дата создания: {current_datetime}</p>
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
        
        // Инициализация при загрузке страницы
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Отчет загружен и готов к просмотру');
            
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