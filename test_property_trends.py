#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки содержимого таблицы property_trends
Проверяет количество записей для указанной локации и их распределение по месяцам
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime
import json

# Загружаем переменные окружения
load_dotenv()

def get_db_connection():
    """Создает соединение с базой данных PostgreSQL"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        return connection
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None

def test_property_trends_table():
    """Тестирует содержимое таблицы property_trends для указанной локации"""
    
    # Параметры локации из запроса
    country_id = 1
    city_id = 7
    county_id = 2038
    district_id = 2339
    
    print(f"🔍 Тестирование таблицы property_trends")
    print(f"📍 Локация: country_id={country_id}, city_id={city_id}, county_id={county_id}, district_id={district_id}")
    print("=" * 80)
    
    # Подключаемся к базе данных
    connection = get_db_connection()
    if not connection:
        print("❌ Не удалось подключиться к базе данных")
        return
    
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            
            # 1. Проверяем общее количество записей в таблице
            print("📊 1. Общая статистика таблицы property_trends:")
            cursor.execute("SELECT COUNT(*) as total_count FROM property_trends")
            total_count = cursor.fetchone()['total_count']
            print(f"   Всего записей в таблице: {total_count}")
            
            # 2. Проверяем количество записей для указанной локации
            print(f"\n📊 2. Записи для указанной локации:")
            cursor.execute("""
                SELECT COUNT(*) as location_count 
                FROM property_trends 
                WHERE country_id = %s AND city_id = %s AND county_id = %s AND district_id = %s
            """, (country_id, city_id, county_id, district_id))
            location_count = cursor.fetchone()['location_count']
            print(f"   Записей для локации: {location_count}")
            
            # 3. Проверяем количество записей для подтвержденных пользователей
            print(f"\n📊 3. Записи для подтвержденных пользователей:")
            cursor.execute("""
                SELECT COUNT(*) as confirmed_count 
                FROM property_trends pt
                INNER JOIN users u ON pt.user_id = u.id
                WHERE pt.country_id = %s 
                    AND pt.city_id = %s 
                    AND pt.county_id = %s 
                    AND pt.district_id = %s
                    AND u.is_confirmed = true
            """, (country_id, city_id, county_id, district_id))
            confirmed_count = cursor.fetchone()['confirmed_count']
            print(f"   Записей для подтвержденных пользователей: {confirmed_count}")
            
            # 4. Получаем детальную информацию о записях для подтвержденных пользователей
            print(f"\n📊 4. Детальная информация о записях:")
            cursor.execute("""
                SELECT 
                    pt.id,
                    pt.date,
                    pt.unit_price_for_sale,
                    pt.price_change_sale,
                    pt.unit_price_for_rent,
                    pt.price_change_rent,
                    pt.yield,
                    pt.property_year,
                    pt.property_month,
                    u.is_confirmed,
                    u.username
                FROM property_trends pt
                INNER JOIN users u ON pt.user_id = u.id
                WHERE pt.country_id = %s 
                    AND pt.city_id = %s 
                    AND pt.county_id = %s 
                    AND pt.district_id = %s
                    AND u.is_confirmed = true
                ORDER BY pt.property_year DESC, pt.property_month DESC
            """, (country_id, city_id, county_id, district_id))
            
            trends = cursor.fetchall()
            print(f"   Получено записей: {len(trends)}")
            
            if trends:
                print(f"\n📋 Детали записей:")
                for i, trend in enumerate(trends):
                    print(f"   {i+1:2d}. ID: {trend['id']:4d} | "
                          f"Дата: {trend['date']} | "
                          f"Год-месяц: {trend['property_year']}-{trend['property_month']:02d} | "
                          f"Продажа: {trend['unit_price_for_sale']:8.2f} | "
                          f"Аренда: {trend['unit_price_for_rent']:6.2f} | "
                          f"Доходность: {trend['yield']:5.2f}% | "
                          f"Пользователь: {trend['username']}")
            
            # 5. Анализируем распределение по месяцам
            print(f"\n📊 5. Распределение по месяцам:")
            month_distribution = {}
            for trend in trends:
                key = f"{trend['property_year']}-{trend['property_month']:02d}"
                if key not in month_distribution:
                    month_distribution[key] = 0
                month_distribution[key] += 1
            
            for month in sorted(month_distribution.keys(), reverse=True):
                print(f"   {month}: {month_distribution[month]} записей")
            
            # 6. Проверяем текущую дату и фильтрацию
            current_date = datetime.now()
            current_year = current_date.year
            current_month = current_date.month
            
            print(f"\n📊 6. Анализ фильтрации:")
            print(f"   Текущая дата: {current_date.strftime('%Y-%m-%d')}")
            print(f"   Текущий год-месяц: {current_year}-{current_month:02d}")
            
            # Подсчитываем записи, которые должны отображаться (до текущего месяца включительно)
            visible_count = 0
            future_count = 0
            
            for trend in trends:
                if trend['property_year'] < current_year:
                    visible_count += 1  # Прошлые годы - показываем
                elif trend['property_year'] == current_year:
                    if trend['property_month'] <= current_month:
                        visible_count += 1  # Текущий год, месяц <= текущего - показываем
                    else:
                        future_count += 1  # Текущий год, месяц > текущего - не показываем
                else:
                    future_count += 1  # Будущие годы - не показываем
            
            print(f"   Записей для отображения (до текущего месяца): {visible_count}")
            print(f"   Записей будущих месяцев (скрыто): {future_count}")
            
            # 7. Проверяем структуру таблицы
            print(f"\n📊 7. Структура таблицы property_trends:")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'property_trends'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"   {col['column_name']:20s} | {col['data_type']:15s} | {col['is_nullable']}")
            
            # 8. Проверяем индексы
            print(f"\n📊 8. Индексы таблицы property_trends:")
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'property_trends'
            """)
            
            indexes = cursor.fetchall()
            if indexes:
                for idx in indexes:
                    print(f"   {idx['indexname']}: {idx['indexdef']}")
            else:
                print("   Индексы не найдены")
            
            # 9. Проверяем размер таблицы
            print(f"\n📊 9. Размер таблицы:")
            cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size('property_trends')) as total_size,
                    pg_size_pretty(pg_relation_size('property_trends')) as table_size
            """)
            
            size_info = cursor.fetchone()
            print(f"   Общий размер: {size_info['total_size']}")
            print(f"   Размер таблицы: {size_info['table_size']}")
            
            # 10. Проверяем последние обновления
            print(f"\n📊 10. Последние обновления:")
            cursor.execute("""
                SELECT 
                    MAX(created_at) as last_created,
                    MAX(updated_at) as last_updated
                FROM property_trends
            """)
            
            update_info = cursor.fetchone()
            if update_info['last_created']:
                print(f"   Последнее создание: {update_info['last_created']}")
            if update_info['last_updated']:
                print(f"   Последнее обновление: {update_info['last_updated']}")
            
            print("\n" + "=" * 80)
            print("✅ Тестирование завершено")
            
            # Выводим итоговую сводку
            print(f"\n📋 ИТОГОВАЯ СВОДКА:")
            print(f"   Всего записей в таблице: {total_count}")
            print(f"   Записей для локации: {location_count}")
            print(f"   Записей для подтвержденных пользователей: {confirmed_count}")
            print(f"   Записей для отображения: {visible_count}")
            print(f"   Записей будущих месяцев (скрыто): {future_count}")
            
            if confirmed_count > visible_count:
                print(f"\n⚠️  ВНИМАНИЕ: В таблице отображается {visible_count} записей из {confirmed_count} доступных!")
                print(f"   Это означает, что {confirmed_count - visible_count} записей скрыто фильтром по датам.")
            
    except Exception as e:
        print(f"❌ Ошибка при выполнении запросов: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        connection.close()
        print(f"\n🔌 Соединение с базой данных закрыто")

if __name__ == "__main__":
    test_property_trends_table()

