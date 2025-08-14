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
        
        # Получаем текущую дату
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Вычисляем период: 12 месяцев назад + текущий месяц + 1 месяц вперед
        # Начинаем с 12 месяцев назад
        start_year = current_year
        start_month = current_month - 12
        
        # Корректируем год если месяц < 1
        if start_month < 1:
            start_year -= 1
            start_month += 12
        
        # Конечный период: текущий месяц + 1 месяц вперед
        end_year = current_year
        end_month = current_month + 1
        
        # Корректируем год если месяц > 12
        if end_month > 12:
            end_year += 1
            end_month -= 12
        
        logger.info(f"📅 Анализируем период: с {start_year}-{start_month:02d} по {end_year}-{end_month:02d}")
        logger.info(f"📅 Текущая дата: {current_year}-{current_month:02d}")
        
        # Формируем запрос к таблице property_trends
        logger.info(f"🔍 Формируем запрос к таблице property_trends")
        logger.info(f"🔍 Базовый запрос: select * from property_trends")
        
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
        
        # Фильтруем по периоду - используем отдельные поля property_year и property_month
        # Получаем данные за последние 12 месяцев + текущий месяц + 1 месяц вперед
        
        # Упрощенная логика фильтрации
        # Получаем данные за последние 12 месяцев + текущий месяц + 1 месяц вперед
        
        # Сначала получаем все данные для локации без фильтра по дате
        # Это поможет понять, есть ли вообще данные
        logger.info("🔍 Получаем все данные для локации без фильтра по дате...")
        
        # Фильтруем по годам (включая текущий и предыдущий)
        years_to_include = [start_year, end_year]
        if start_year != end_year:
            years_to_include = list(range(start_year, end_year + 1))
        
        logger.info(f"🔍 Включаем годы: {years_to_include}")
        
        # Используем простую фильтрацию: год >= start_year и год <= end_year
        logger.info(f"🔍 Добавляем фильтр по году: property_year >= {start_year}")
        query = query.gte('property_year', start_year)
        logger.info(f"🔍 Добавляем фильтр по году: property_year <= {end_year}")
        query = query.lte('property_year', end_year)
        
        # Добавляем дополнительную отладочную информацию
        logger.info(f"🔍 Фильтры запроса:")
        logger.info(f"  - country_id = {location_codes.get('country_id')}")
        logger.info(f"  - city_id = {location_codes.get('city_id')}")
        logger.info(f"  - county_id = {location_codes.get('county_id')}")
        logger.info(f"  - district_id = {location_codes.get('district_id')}")
        logger.info(f"  - период: с {start_year}-{start_month:02d} по {end_year}-{end_month:02d}")
        logger.info(f"🔍 Включаем годы: {years_to_include}")
        
        # Сортируем по дате
        query = query.order('property_year', desc=False).order('property_month', desc=False)
        
        logger.info("🔍 Выполняем запрос к базе данных...")
        logger.info(f"🔍 Параметры запроса:")
        logger.info(f"  - country_id: {location_codes.get('country_id')}")
        logger.info(f"  - city_id: {location_codes.get('city_id')}")
        logger.info(f"  - county_id: {location_codes.get('county_id')}")
        logger.info(f"  - district_id: {location_codes.get('district_id')}")
        logger.info(f"  - период: с {start_year}-{start_month:02d} по {end_year}-{end_month:02d}")
        logger.info(f"🔍 SQL запрос: {query}")
        
        try:
            response = query.execute()
            logger.info(f"✅ Запрос выполнен успешно")
            logger.info(f"🔍 Тип ответа: {type(response)}")
            logger.info(f"🔍 Атрибуты ответа: {dir(response)}")
            if hasattr(response, 'data'):
                logger.info(f"🔍 Данные ответа: {response.data}")
                logger.info(f"🔍 Количество записей: {len(response.data) if response.data else 0}")
                if response.data:
                    logger.info(f"🔍 Первая запись: {response.data[0]}")
                    logger.info(f"🔍 Последняя запись: {response.data[-1]}")
                    logger.info(f"🔍 Все записи: {response.data}")
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
            logger.warning(f"⚠️ Проверьте SQL запрос: {query}")
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
        if trends_data:
            logger.info(f"🔍 Первые 3 записи: {trends_data[:3]}")
            logger.info(f"🔍 Последние 3 записи: {trends_data[-3:]}")
        else:
            logger.warning(f"⚠️ trends_data пустой - данных нет")
            logger.warning(f"⚠️ Проверьте SQL запрос: {query}")
            logger.warning(f"⚠️ Проверьте фильтры: country_id={location_codes.get('country_id')}, city_id={location_codes.get('city_id')}, county_id={location_codes.get('county_id')}, district_id={location_codes.get('district_id')}")
        
        # Обрабатываем данные и вычисляем общие цены объектов
        processed_data = []
        logger.info(f"🔍 Обрабатываем {len(trends_data)} записей...")
        
        for i, record in enumerate(trends_data):
            try:
                unit_price = float(record.get('unit_price_for_sale', 0))
                total_price = unit_price * area
                
                processed_record = {
                    'year': record.get('property_year'),
                    'month': record.get('property_month'),
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'date_key': f"{record.get('property_year')}-{record.get('property_month'):02d}"
                }
                processed_data.append(processed_record)
                
                if i < 3:  # Логируем первые 3 записи
                    logger.info(f"🔍 Запись {i+1}: год={record.get('property_year')}, месяц={record.get('property_month')}, цена/м²={unit_price}, общая цена={total_price}")
                
            except (ValueError, TypeError) as e:
                logger.warning(f"⚠️ Ошибка обработки записи {i+1}: {e}, данные: {record}")
                continue
        
        if not processed_data:
            logger.warning("⚠️ Нет валидных данных для анализа")
            logger.warning(f"⚠️ trends_data: {trends_data}")
            logger.warning(f"⚠️ Проверьте SQL запрос: {query}")
            return {
                'error': 'Нет валидных данных о трендах цен',
                'trend': 'Не определен',
                'change_3y': 0,
                'forecast_3m': 0,
                'analysis': 'Недостаточно данных для анализа',
                'recommendation': 'Требуется дополнительная информация о локации',
                'chart_data': []
            }
        
        # Сортируем по дате
        processed_data.sort(key=lambda x: x['date_key'])
        
        # Анализируем тренд
        trend_analysis = analyze_price_trend(processed_data)
        
        # Вычисляем изменение за 3 года
        change_3y = calculate_3year_change(processed_data)
        
        # Вычисляем прогноз на 3 месяца
        forecast_3m = calculate_3month_forecast(processed_data)
        
        # Формируем данные для графика
        chart_data = format_chart_data(processed_data)
        
        result = {
            'trend': trend_analysis['trend'],
            'change_3y': change_3y,
            'forecast_3m': forecast_3m,
            'analysis': trend_analysis['analysis'],
            'recommendation': trend_analysis['recommendation'],
            'chart_data': chart_data,
            'raw_data_count': len(processed_data)
        }
        
        logger.info(f"✅ Анализ трендов завершен: {result['trend']}, изменение за 3 года: {change_3y:.1f}%")
        logger.info(f"📊 Финальный результат: {result}")
        logger.info(f"🔍 Количество обработанных записей: {len(processed_data)}")
        logger.info(f"🔍 Данные для графика: {chart_data}")
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
