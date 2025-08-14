#!/usr/bin/env python3
"""
Функции для анализа динамики цен недвижимости
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

logger = logging.getLogger(__name__)

# Настраиваем логирование, если оно не настроено
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def get_price_trends_data(supabase, location_codes: Dict, area: float) -> Dict:
    """
    Получает данные о динамике цен из таблицы property_trends
    
    Args:
        supabase: клиент Supabase
        location_codes: коды локации (country_id, city_id, county_id, district_id)
        area: площадь объекта в м²
    
    Returns:
        Dict с данными о трендах цен
    """
    try:
        logger.info(f"🔍 Получаем данные о трендах цен для локации: {location_codes}")
        
        # Проверяем наличие необходимых кодов локации
        required_codes = ['country_id', 'city_id', 'county_id', 'district_id']
        missing_codes = [code for code in required_codes if not location_codes.get(code)]
        
        if missing_codes:
            logger.warning(f"⚠️ Отсутствуют коды локации: {missing_codes}")
            return {
                'error': f'Отсутствуют коды локации: {", ".join(missing_codes)}',
                'trend': 'Не определен',
                'change_3y': 0,
                'forecast_3m': 0,
                'analysis': 'Недостаточно данных для анализа',
                'recommendation': 'Требуется дополнительная информация о локации',
                'chart_data': []
            }
        
        # Сначала получаем ВСЕ данные для локации без фильтров по дате
        logger.info("🔍 Получаем ВСЕ данные для локации без фильтров по дате...")
        
        # Формируем простой запрос только по кодам локации
        query = supabase.table('property_trends').select('*').eq('country_id', location_codes['country_id'])
        logger.info(f"🔍 Добавляем фильтр: country_id = {location_codes['country_id']}")
        
        if location_codes.get('city_id'):
            query = query.eq('city_id', location_codes['city_id'])
            logger.info(f"🔍 Добавляем фильтр: city_id = {location_codes['city_id']}")
        if location_codes.get('county_id'):
            query = query.eq('county_id', location_codes['county_id'])
            logger.info(f"🔍 Добавляем фильтр: county_id = {location_codes['county_id']}")
        if location_codes.get('district_id'):
            query = query.eq('district_id', location_codes['district_id'])
            logger.info(f"🔍 Добавляем фильтр: district_id = {location_codes['district_id']}")
        
        # Сортируем по дате для удобства
        query = query.order('property_year', desc=False).order('property_month', desc=False)
        
        logger.info("🔍 Выполняем запрос к базе данных...")
        logger.info(f"🔍 Параметры запроса:")
        logger.info(f"  - country_id: {location_codes.get('country_id')}")
        logger.info(f"  - city_id: {location_codes.get('city_id')}")
        logger.info(f"  - county_id: {location_codes.get('county_id')}")
        logger.info(f"  - district_id: {location_codes.get('district_id')}")
        logger.info(f"🔍 SQL запрос: {query}")
        
        try:
            response = query.execute()
            logger.info(f"✅ Запрос выполнен успешно")
            logger.info(f"🔍 Тип ответа: {type(response)}")
            if hasattr(response, 'data'):
                logger.info(f"🔍 Данные ответа: {response.data}")
                logger.info(f"🔍 Количество записей: {len(response.data) if response.data else 0}")
                if response.data:
                    logger.info(f"🔍 Первая запись: {response.data[0]}")
                    logger.info(f"🔍 Последняя запись: {response.data[-1]}")
                    logger.info(f"🔍 ВСЕ записи:")
                    for i, record in enumerate(response.data):
                        logger.info(f"  {i+1}. ID: {record.get('id')}, Год: {record.get('property_year')}, Месяц: {record.get('property_month')}, Цена продажи: {record.get('unit_price_for_sale')}, Цена аренды: {record.get('unit_price_for_rent')}")
                else:
                    logger.warning(f"⚠️ Ответ пустой - данных нет")
            else:
                logger.info(f"🔍 Ответ не содержит атрибут 'data'")
        except Exception as e:
            logger.error(f"❌ Ошибка выполнения запроса: {e}")
            logger.error(f"❌ SQL запрос: {query}")
            return {
                'error': f'Ошибка выполнения запроса: {str(e)}',
                'trend': 'Не определен',
                'change_3y': 0,
                'forecast_3m': 0,
                'analysis': 'Произошла ошибка при запросе к базе данных',
                'recommendation': 'Попробуйте позже',
                'chart_data': []
            }
        
        if response.data is None:
            logger.warning("⚠️ Нет данных о трендах цен (response.data is None)")
            return {
                'error': 'Нет данных о трендах цен для указанной локации',
                'trend': 'Не определен',
                'change_3y': 0,
                'forecast_3m': 0,
                'analysis': 'Недостаточно данных для анализа',
                'recommendation': 'Требуется дополнительная информация о локации',
                'chart_data': []
            }
        
        trends_data = response.data
        logger.info(f"📊 Получено {len(trends_data)} записей о трендах цен")
        
        if not trends_data:
            logger.warning(f"⚠️ trends_data пустой - данных нет")
            return {
                'error': 'Нет данных о трендах цен для указанной локации',
                'trend': 'Не определен',
                'change_3y': 0,
                'forecast_3m': 0,
                'analysis': 'Недостаточно данных для анализа',
                'recommendation': 'Требуется дополнительная информация о локации',
                'chart_data': []
            }
        
        # Пока просто возвращаем информацию о найденных данных
        # Позже доработаем анализ
        result = {
            'trend': 'Данные найдены',
            'change_3y': 0,
            'forecast_3m': 0,
            'analysis': f'Найдено {len(trends_data)} записей о трендах цен',
            'recommendation': 'Данные получены, анализ в разработке',
            'chart_data': [],
            'raw_data_count': len(trends_data),
            'raw_data': trends_data[:5]  # Первые 5 записей для отладки
        }
        
        logger.info(f"✅ Данные получены: {len(trends_data)} записей")
        logger.info(f"📊 Финальный результат: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения данных о трендах цен: {e}")
        logger.error(f"❌ Коды локации: {location_codes}")
        logger.error(f"❌ Площадь: {area}")
        logger.error(f"❌ Тип ошибки: {type(e)}")
        return {
            'error': f'Ошибка получения данных: {str(e)}',
            'trend': 'Не определен',
            'change_3y': 0,
            'forecast_3m': 0,
            'analysis': 'Произошла ошибка при анализе данных',
            'recommendation': 'Попробуйте позже',
            'chart_data': []
        }

def analyze_price_trend(data: List[Dict]) -> Dict:
    """
    Анализирует тренд цен на основе исторических данных
    
    Args:
        data: список записей с ценами
    
    Returns:
        Dict с анализом тренда
    """
    try:
        if len(data) < 2:
            return {
                'trend': 'Недостаточно данных',
                'analysis': 'Требуется минимум 2 точки данных для анализа тренда',
                'recommendation': 'Дождитесь накопления данных'
            }
        
        # Вычисляем средние цены по периодам
        prices = [record['total_price'] for record in data]
        avg_price = sum(prices) / len(prices)
        
        # Вычисляем тренд (линейная регрессия)
        n = len(data)
        x_values = list(range(n))
        y_values = prices
        
        # Вычисляем коэффициенты линейной регрессии
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Коэффициент наклона (slope)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Определяем направление тренда
        if abs(slope) < avg_price * 0.01:  # Изменение менее 1% от средней цены
            trend = 'Стабильный'
            analysis = 'Цены остаются относительно стабильными'
            recommendation = 'Благоприятное время для покупки'
        elif slope > 0:
            trend = 'Растущий'
            analysis = 'Цены демонстрируют устойчивый рост'
            recommendation = 'Рекомендуется покупка в ближайшее время'
        else:
            trend = 'Падающий'
            analysis = 'Цены демонстрируют тенденцию к снижению'
            recommendation = 'Можно подождать с покупкой'
        
        return {
            'trend': trend,
            'analysis': analysis,
            'recommendation': recommendation,
            'slope': slope,
            'avg_price': avg_price
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка анализа тренда: {e}")
        return {
            'trend': 'Ошибка анализа',
            'analysis': 'Не удалось проанализировать тренд',
            'recommendation': 'Требуется дополнительный анализ'
        }

def calculate_3year_change(data: List[Dict]) -> float:
    """
    Вычисляет изменение цены за 3 года в процентах
    
    Args:
        data: список записей с ценами
    
    Returns:
        float: процент изменения
    """
    try:
        if len(data) < 2:
            return 0.0
        
        # Берем первую и последнюю цену
        first_price = data[0]['total_price']
        last_price = data[-1]['total_price']
        
        if first_price == 0:
            return 0.0
        
        change_percent = ((last_price - first_price) / first_price) * 100
        return round(change_percent, 1)
        
    except Exception as e:
        logger.error(f"❌ Ошибка вычисления изменения за 3 года: {e}")
        return 0.0

def calculate_3month_forecast(data: List[Dict]) -> float:
    """
    Вычисляет прогноз изменения цены на 3 месяца вперед
    
    Args:
        data: список записей с ценами
    
    Returns:
        float: прогнозируемый процент изменения
    """
    try:
        if len(data) < 3:
            return 0.0
        
        # Берем последние 3 точки для прогноза
        recent_prices = data[-3:]
        prices = [record['total_price'] for record in recent_prices]
        
        # Вычисляем среднее изменение
        changes = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                change = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
                changes.append(change)
        
        if not changes:
            return 0.0
        
        # Среднее изменение за период
        avg_change = sum(changes) / len(changes)
        
        # Прогноз на 3 месяца (экстраполируем тренд)
        forecast_change = avg_change * 3
        
        return round(forecast_change, 1)
        
    except Exception as e:
        logger.error(f"❌ Ошибка вычисления прогноза на 3 месяца: {e}")
        return 0.0

def format_chart_data(data: List[Dict]) -> List[Dict]:
    """
    Форматирует данные для отображения на графике
    
    Args:
        data: список записей с ценами
    
    Returns:
        List[Dict]: данные для графика
    """
    try:
        chart_data = []
        
        for record in data:
            chart_data.append({
                'year': record['year'],
                'month': record['month'],
                'unit_price': record['unit_price'],
                'total_price': round(record['total_price'], 2),
                'label': f"{record['month']:02d}/{record['year']}"
            })
        
        return chart_data
        
    except Exception as e:
        logger.error(f"❌ Ошибка форматирования данных для графика: {e}")
        return []
