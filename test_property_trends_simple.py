#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный тестовый скрипт для проверки API endpoint /api/property_trends
Проверяет количество записей через HTTP запрос
"""

import requests
import json
from datetime import datetime

def test_property_trends_api():
    """Тестирует API endpoint /api/property_trends"""
    
    # URL API (замените на ваш)
    api_url = "http://localhost:5000/api/property_trends"
    
    # Параметры локации из запроса
    location_data = {
        "country_id": 1,
        "city_id": 7,
        "county_id": 2038,
        "district_id": 2339
    }
    
    print(f"🔍 Тестирование API endpoint /api/property_trends")
    print(f"📍 Локация: {json.dumps(location_data, indent=2)}")
    print(f"🌐 API URL: {api_url}")
    print("=" * 80)
    
    try:
        # Отправляем POST запрос
        print("📡 Отправка POST запроса...")
        response = requests.post(
            api_url,
            json=location_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📊 Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Успешный ответ от API")
            print(f"📊 Данные ответа:")
            print(f"   success: {data.get('success')}")
            print(f"   count: {data.get('count')}")
            
            trends = data.get('trends', [])
            print(f"   trends array length: {len(trends)}")
            
            if trends:
                print(f"\n📋 Детали записей:")
                for i, trend in enumerate(trends):
                    print(f"   {i+1:2d}. ID: {trend.get('id', 'N/A')} | "
                          f"Дата: {trend.get('date', 'N/A')} | "
                          f"Год-месяц: {trend.get('property_year', 'N/A')}-{trend.get('property_month', 'N/A'):02d} | "
                          f"Продажа: {trend.get('unit_price_for_sale', 0):8.2f} | "
                          f"Аренда: {trend.get('unit_price_for_rent', 0):6.2f} | "
                          f"Доходность: {trend.get('yield', 0):5.2f}%")
                
                # Анализируем распределение по месяцам
                print(f"\n📊 Распределение по месяцам:")
                month_distribution = {}
                for trend in trends:
                    year = trend.get('property_year')
                    month = trend.get('property_month')
                    if year and month:
                        key = f"{year}-{month:02d}"
                        if key not in month_distribution:
                            month_distribution[key] = 0
                        month_distribution[key] += 1
                
                for month in sorted(month_distribution.keys(), reverse=True):
                    print(f"   {month}: {month_distribution[month]} записей")
                
                # Проверяем текущую дату и фильтрацию
                current_date = datetime.now()
                current_year = current_date.year
                current_month = current_date.month
                
                print(f"\n📊 Анализ фильтрации:")
                print(f"   Текущая дата: {current_date.strftime('%Y-%m-%d')}")
                print(f"   Текущий год-месяц: {current_year}-{current_month:02d}")
                
                # Подсчитываем записи, которые должны отображаться
                visible_count = 0
                future_count = 0
                
                for trend in trends:
                    year = trend.get('property_year')
                    month = trend.get('property_month')
                    
                    if year and month:
                        if year < current_year:
                            visible_count += 1  # Прошлые годы
                        elif year == current_year:
                            if month <= current_month:
                                visible_count += 1  # Текущий год, месяц <= текущего
                            else:
                                future_count += 1  # Текущий год, месяц > текущего
                        else:
                            future_count += 1  # Будущие годы
                
                print(f"   Записей для отображения (до текущего месяца): {visible_count}")
                print(f"   Записей будущих месяцев (скрыто): {future_count}")
                
                # Итоговая сводка
                print(f"\n📋 ИТОГОВАЯ СВОДКА:")
                print(f"   Всего записей от API: {len(trends)}")
                print(f"   Записей для отображения: {visible_count}")
                print(f"   Записей будущих месяцев (скрыто): {future_count}")
                
                if len(trends) > visible_count:
                    print(f"\n⚠️  ВНИМАНИЕ: В таблице отображается {visible_count} записей из {len(trends)} доступных!")
                    print(f"   Это означает, что {len(trends) - visible_count} записей скрыто фильтром по датам.")
                
            else:
                print("⚠️ Массив trends пуст или отсутствует")
                
        else:
            print(f"❌ Ошибка API: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📊 Детали ошибки: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📊 Текст ошибки: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения: Не удается подключиться к API серверу")
        print("💡 Убедитесь, что API сервер запущен и доступен по адресу:", api_url)
        
    except requests.exceptions.Timeout:
        print("❌ Ошибка таймаута: Запрос превысил время ожидания")
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ Тестирование завершено")

if __name__ == "__main__":
    test_property_trends_api()

