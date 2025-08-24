#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрая проверка данных property_trends для district_id 2279
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def quick_test():
    """Быстрый тест данных"""
    
    print("🔍 Быстрая проверка property_trends для district_id 2279")
    print("=" * 50)
    
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(
            host="localhost",
            database="aaadviser",
            user="postgres",
            password="postgres",
            port="5432"
        )
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        
        # 1. Общее количество записей
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM property_trends 
            WHERE district_id = 2279
        """)
        
        total = cursor.fetchone()['total']
        print(f"📊 Всего записей для district_id 2279: {total}")
        
        if total == 0:
            print("❌ Нет данных!")
            return
        
        # 2. Диапазон лет
        cursor.execute("""
            SELECT 
                MIN(property_year) as min_year,
                MAX(property_year) as max_year
            FROM property_trends 
            WHERE district_id = 2279
        """)
        
        years = cursor.fetchone()
        print(f"📅 Диапазон лет: {years['min_year']} - {years['max_year']}")
        
        # 3. Последние 10 записей
        print("\n📋 Последние 10 записей:")
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
            LIMIT 10
        """)
        
        records = cursor.fetchall()
        month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
        
        for record in records:
            month = month_names[record['property_month'] - 1]
            print(f"   {month} {record['property_year']} | "
                  f"Продажа: {record['unit_price_for_sale']:8.2f} ₺/м² "
                  f"(+{record['price_change_sale']:5.2f}%) | "
                  f"Аренда: {record['unit_price_for_rent']:6.2f} ₺/м² "
                  f"(+{record['price_change_rent']:5.2f}%) | "
                  f"Доходность: {record['yield']:4.1f}%")
        
        # 4. Проверка NULL значений
        cursor.execute("""
            SELECT 
                COUNT(unit_price_for_sale) as sale_count,
                COUNT(price_change_sale) as change_sale_count,
                COUNT(unit_price_for_rent) as rent_count,
                COUNT(price_change_rent) as change_rent_count,
                COUNT(yield) as yield_count
            FROM property_trends 
            WHERE district_id = 2279
        """)
        
        null_check = cursor.fetchone()
        print(f"\n⚠️  Проверка NULL значений:")
        print(f"   Цена продажи: {null_check['sale_count']}/{total}")
        print(f"   Изменение продажи: {null_check['change_sale_count']}/{total}")
        print(f"   Цена аренды: {null_check['rent_count']}/{total}")
        print(f"   Изменение аренды: {null_check['change_rent_count']}/{total}")
        print(f"   Доходность: {null_check['yield_count']}/{total}")
        
        print("\n✅ Быстрая проверка завершена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    quick_test()
