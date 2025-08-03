#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений в app.py
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_economic_data():
    """Тест функции получения экономических данных"""
    try:
        from app import get_economic_data
        
        print("Тестирование функции get_economic_data...")
        economic_data = get_economic_data('TUR', 5)
        
        print(f"Код страны: {economic_data.get('country_code')}")
        print(f"Название страны: {economic_data.get('country_name')}")
        print(f"Данные ВВП: {len(economic_data.get('gdp_data', []))} записей")
        print(f"Данные инфляции: {len(economic_data.get('inflation_data', []))} записей")
        print(f"Тренд ВВП: {economic_data.get('gdp_trend', 0)}")
        print(f"Тренд инфляции: {economic_data.get('inflation_trend', 0)}")
        
        if economic_data.get('gdp_data') and economic_data.get('inflation_data'):
            print("✅ Экономические данные загружены успешно")
            return True
        else:
            print("❌ Экономические данные не загружены")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании экономических данных: {e}")
        return False

def test_trends_data():
    """Тест функции получения трендов недвижимости"""
    try:
        from app import get_property_trends_data
        
        print("\nТестирование функции get_property_trends_data...")
        trends_data, message = get_property_trends_data('Alanya', '07410 Alanya/Antalya', 'Cengiz Akay Sk. No:12')
        
        print(f"Сообщение: {message}")
        if trends_data:
            print(f"Средняя цена за м²: {trends_data.get('avg_price_per_sqm', 0)}")
            print(f"Изменение цен: {trends_data.get('price_change_percent', 0)}%")
            print(f"Доходность аренды: {trends_data.get('rental_yield', 0)}%")
            print("✅ Данные трендов получены успешно")
            return True
        else:
            print("❌ Данные трендов не получены")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании трендов: {e}")
        return False

def test_chart_creation():
    """Тест создания графиков"""
    try:
        from app import create_economic_chart_data, create_chart_image_for_pdf
        
        print("\nТестирование создания графиков...")
        
        # Создаем тестовые данные
        test_economic_data = {
            'gdp_data': [
                {'year': 2020, 'value': -1.2},
                {'year': 2021, 'value': 11.4},
                {'year': 2022, 'value': 5.6},
                {'year': 2023, 'value': 4.5},
                {'year': 2024, 'value': 4.1}
            ],
            'inflation_data': [
                {'year': 2020, 'value': 12.3},
                {'year': 2021, 'value': 19.6},
                {'year': 2022, 'value': 72.3},
                {'year': 2023, 'value': 64.8},
                {'year': 2024, 'value': 58.2}
            ],
            'country_name': 'Turkey',
            'country_code': 'TUR',
            'gdp_trend': 2.1,
            'inflation_trend': -5.2
        }
        
        # Создаем данные для графиков
        chart_data = create_economic_chart_data(test_economic_data)
        print(f"Создан график ВВП: {len(chart_data['gdp_chart']['labels'])} точек")
        print(f"Создан график инфляции: {len(chart_data['inflation_chart']['labels'])} точек")
        
        # Тестируем создание изображения для PDF
        chart_image = create_chart_image_for_pdf(chart_data, "Тестовый график")
        if chart_image:
            print("✅ Изображение графика создано успешно")
            return True
        else:
            print("❌ Изображение графика не создано")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при создании графиков: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование исправлений в app.py")
    print("=" * 50)
    
    tests = [
        test_economic_data,
        test_trends_data,
        test_chart_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте: {e}")
    
    print("\n" + "=" * 50)
    print(f"Результаты тестирования: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 Все тесты прошли успешно!")
        return True
    else:
        print("⚠️ Некоторые тесты не прошли")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 