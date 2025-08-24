#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки данных в таблице property_trends
для district_id 2279
"""

import os
import sys
import json
from datetime import datetime

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ Ошибка: psycopg2 не установлен")
    print("Установите: pip install psycopg2-binary")
    sys.exit(1)

def get_database_connection():
    """Получение соединения с базой данных"""
    try:
        # Параметры подключения к базе данных
        connection = psycopg2.connect(
            host="localhost",
            database="aaadviser",
            user="postgres",
            password="postgres",
            port="5432"
        )
        return connection
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None

def test_property_trends_district_2279():
    """Тестирование данных property_trends для district_id 2279"""
    
    print("🔍 Тестирование данных property_trends для district_id 2279")
    print("=" * 60)
    
    connection = get_database_connection()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # 1. Проверяем общее количество записей для district_id 2279
        print("\n📊 1. Общая статистика:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT property_year) as unique_years,
                COUNT(DISTINCT property_month) as unique_months,
                MIN(property_year) as min_year,
                MAX(property_year) as max_year,
                MIN(property_month) as min_month,
                MAX(property_month) as max_month
            FROM property_trends 
            WHERE district_id = 2279
        """)
        
        stats = cursor.fetchone()
        if stats:
            print(f"   Всего записей: {stats['total_records']}")
            print(f"   Уникальных лет: {stats['unique_years']}")
            print(f"   Уникальных месяцев: {stats['unique_months']}")
            print(f"   Диапазон лет: {stats['min_year']} - {stats['max_year']}")
            print(f"   Диапазон месяцев: {stats['min_month']} - {stats['max_month']}")
        else:
            print("   ❌ Нет данных для district_id 2279")
            return
        
        # 2. Проверяем данные по годам
        print("\n📅 2. Данные по годам:")
        cursor.execute("""
            SELECT 
                property_year,
                COUNT(*) as records_count,
                MIN(property_month) as min_month,
                MAX(property_month) as max_month
            FROM property_trends 
            WHERE district_id = 2279
            GROUP BY property_year
            ORDER BY property_year DESC
        """)
        
        years_data = cursor.fetchall()
        for year_data in years_data:
            print(f"   {year_data['property_year']}: {year_data['records_count']} записей "
                  f"(месяцы {year_data['min_month']}-{year_data['max_month']})")
        
        # 3. Проверяем данные по месяцам
        print("\n📆 3. Данные по месяцам:")
        cursor.execute("""
            SELECT 
                property_month,
                COUNT(*) as records_count,
                MIN(property_year) as min_year,
                MAX(property_year) as max_year
            FROM property_trends 
            WHERE district_id = 2279
            GROUP BY property_month
            ORDER BY property_month
        """)
        
        months_data = cursor.fetchall()
        month_names = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        
        for month_data in months_data:
            month_name = month_names[month_data['property_month'] - 1]
            print(f"   {month_data['property_month']:2d} ({month_name:10s}): "
                  f"{month_data['records_count']:2d} записей "
                  f"(годы {month_data['min_year']}-{month_data['max_year']})")
        
        # 4. Проверяем детальные данные (первые 10 записей)
        print("\n📋 4. Детальные данные (первые 10 записей):")
        cursor.execute("""
            SELECT 
                id,
                property_year,
                property_month,
                unit_price_for_sale,
                price_change_sale,
                unit_price_for_rent,
                price_change_rent,
                yield,
                created_at
            FROM property_trends 
            WHERE district_id = 2279
            ORDER BY property_year DESC, property_month DESC
            LIMIT 10
        """)
        
        detailed_data = cursor.fetchall()
        for record in detailed_data:
            month_name = month_names[record['property_month'] - 1]
            print(f"   ID {record['id']:4d} | {month_name:10s} {record['property_year']} | "
                  f"Продажа: {record['unit_price_for_sale']:8.2f} ₺/м² "
                  f"(+{record['price_change_sale']:5.2f}%) | "
                  f"Аренда: {record['unit_price_for_rent']:6.2f} ₺/м² "
                  f"(+{record['price_change_rent']:5.2f}%) | "
                  f"Доходность: {record['yield']:4.1f}%")
        
        # 5. Проверяем данные за последние 12 месяцев
        print("\n🕒 5. Данные за последние 12 месяцев:")
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Вычисляем диапазон для последних 12 месяцев
        months_to_check = []
        for i in range(12):
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
            months_to_check.append((year, month))
        
        for year, month in months_to_check:
            cursor.execute("""
                SELECT 
                    unit_price_for_sale,
                    price_change_sale,
                    unit_price_for_rent,
                    price_change_rent,
                    yield
                FROM property_trends 
                WHERE district_id = 2279 
                AND property_year = %s 
                AND property_month = %s
            """, (year, month))
            
            record = cursor.fetchone()
            month_name = month_names[month - 1]
            
            if record:
                print(f"   {month_name:10s} {year}: "
                      f"Продажа {record['unit_price_for_sale']:8.2f} ₺/м² "
                      f"(+{record['price_change_sale']:5.2f}%) | "
                      f"Аренда {record['unit_price_for_rent']:6.2f} ₺/м² "
                      f"(+{record['price_change_rent']:5.2f}%) | "
                      f"Доходность {record['yield']:4.1f}%")
            else:
                print(f"   {month_name:10s} {year}: ❌ Нет данных")
        
        # 6. Проверяем наличие NULL значений
        print("\n⚠️  6. Проверка NULL значений:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(unit_price_for_sale) as sale_price_count,
                COUNT(price_change_sale) as sale_change_count,
                COUNT(unit_price_for_rent) as rent_price_count,
                COUNT(price_change_rent) as rent_change_count,
                COUNT(yield) as yield_count
            FROM property_trends 
            WHERE district_id = 2279
        """)
        
        null_stats = cursor.fetchone()
        if null_stats:
            print(f"   Всего записей: {null_stats['total_records']}")
            print(f"   Цена продажи: {null_stats['sale_price_count']} (NULL: {null_stats['total_records'] - null_stats['sale_price_count']})")
            print(f"   Изменение продажи: {null_stats['sale_change_count']} (NULL: {null_stats['total_records'] - null_stats['sale_change_count']})")
            print(f"   Цена аренды: {null_stats['rent_price_count']} (NULL: {null_stats['total_records'] - null_stats['rent_price_count']})")
            print(f"   Изменение аренды: {null_stats['rent_change_count']} (NULL: {null_stats['total_records'] - null_stats['rent_change_count']})")
            print(f"   Доходность: {null_stats['yield_count']} (NULL: {null_stats['total_records'] - null_stats['yield_count']})")
        
        # 7. Проверяем структуру таблицы
        print("\n🏗️  7. Структура таблицы property_trends:")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'property_trends'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for column in columns:
            nullable = "NULL" if column['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {column['column_default']}" if column['column_default'] else ""
            print(f"   {column['column_name']:25s} | {column['data_type']:15s} | {nullable}{default}")
        
        # 8. Проверяем индексы
        print("\n🔍 8. Индексы таблицы property_trends:")
        cursor.execute("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = 'property_trends'
            ORDER BY indexname
        """)
        
        indexes = cursor.fetchall()
        if indexes:
            for index in indexes:
                print(f"   {index['indexname']}: {index['indexdef']}")
        else:
            print("   ❌ Индексы не найдены")
        
        # 9. Проверяем ограничения
        print("\n🔒 9. Ограничения таблицы property_trends:")
        cursor.execute("""
            SELECT 
                conname as constraint_name,
                contype as constraint_type,
                pg_get_constraintdef(oid) as constraint_definition
            FROM pg_constraint 
            WHERE conrelid = 'property_trends'::regclass
            ORDER BY conname
        """)
        
        constraints = cursor.fetchall()
        if constraints:
            for constraint in constraints:
                print(f"   {constraint['constraint_name']} ({constraint['constraint_type']}): {constraint['constraint_definition']}")
        else:
            print("   ❌ Ограничения не найдены")
        
        # 10. Тестовая выборка для веб-интерфейса
        print("\n🌐 10. Тестовая выборка для веб-интерфейса:")
        cursor.execute("""
            SELECT 
                property_year,
                property_month,
                unit_price_for_sale,
                price_change_sale,
                unit_price_for_rent,
                price_change_rent,
                yield
            FROM property_trends 
            WHERE district_id = 2279
            ORDER BY property_year DESC, property_month DESC
            LIMIT 20
        """)
        
        test_data = cursor.fetchall()
        print(f"   Получено {len(test_data)} записей для тестирования")
        
        # Сохраняем тестовые данные в JSON файл
        test_data_json = []
        for record in test_data:
            test_data_json.append({
                'property_year': record['property_year'],
                'property_month': record['property_month'],
                'unit_price_for_sale': float(record['unit_price_for_sale']) if record['unit_price_for_sale'] else None,
                'price_change_sale': float(record['price_change_sale']) if record['price_change_sale'] else None,
                'unit_price_for_rent': float(record['unit_price_for_rent']) if record['unit_price_for_rent'] else None,
                'price_change_rent': float(record['price_change_rent']) if record['price_change_rent'] else None,
                'yield': float(record['yield']) if record['yield'] else None
            })
        
        with open('test_property_trends_district_2279_data.json', 'w', encoding='utf-8') as f:
            json.dump(test_data_json, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Тестовые данные сохранены в файл: test_property_trends_district_2279_data.json")
        
        # 11. Рекомендации
        print("\n💡 11. Рекомендации:")
        if stats['total_records'] == 0:
            print("   ❌ Нет данных для district_id 2279")
            print("   🔍 Проверьте:")
            print("      - Существует ли district_id 2279 в таблице districts")
            print("      - Есть ли данные в property_trends для других district_id")
            print("      - Правильно ли настроены права доступа к таблице")
        elif stats['total_records'] < 12:
            print("   ⚠️ Мало данных (менее 12 записей)")
            print("   🔍 Возможные причины:")
            print("      - Данные загружаются постепенно")
            print("      - Ограниченный период данных")
            print("      - Проблемы с загрузкой данных")
        else:
            print("   ✅ Данных достаточно для отображения")
            print("   🔍 Проверьте веб-интерфейс:")
            print("      - Правильно ли работает фильтрация")
            print("      - Корректно ли отображаются все записи")
            print("      - Нет ли ошибок в JavaScript коде")
        
        print("\n" + "=" * 60)
        print("✅ Тестирование завершено")
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении запросов: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if connection:
            connection.close()
            print("🔌 Соединение с базой данных закрыто")

if __name__ == "__main__":
    test_property_trends_district_2279()
