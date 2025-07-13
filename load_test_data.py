#!/usr/bin/env python3
"""
Скрипт для загрузки тестовых данных в базу данных
"""

import csv
import psycopg2
import os
from datetime import datetime
import sys

# Конфигурация базы данных
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'real_estate_bot'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

def connect_db():
    """Подключение к базе данных"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        sys.exit(1)

def load_short_term_rentals(conn):
    """Загрузка данных краткосрочной аренды"""
    print("Загрузка данных краткосрочной аренды...")
    
    with open('test_data_short_term_rentals_full.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        with conn.cursor() as cur:
            for row in reader:
                cur.execute("""
                    INSERT INTO short_term_rentals (
                        property_id, address, latitude, longitude, city, district,
                        property_type, bedrooms, bathrooms, max_guests, amenities,
                        description, photos, source, source_url, source_id,
                        price_per_night, price_currency, availability_rate,
                        avg_rating, review_count, host_name, host_rating,
                        host_review_count, instant_bookable, superhost,
                        created_at, updated_at, last_scraped_at, is_active
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (property_id) DO UPDATE SET
                        address = EXCLUDED.address,
                        price_per_night = EXCLUDED.price_per_night,
                        availability_rate = EXCLUDED.availability_rate,
                        avg_rating = EXCLUDED.avg_rating,
                        updated_at = EXCLUDED.updated_at,
                        last_scraped_at = EXCLUDED.last_scraped_at
                """, (
                    row['property_id'], row['address'], float(row['latitude']),
                    float(row['longitude']), row['city'], row['district'],
                    row['property_type'], int(row['bedrooms']), int(row['bathrooms']),
                    int(row['max_guests']), row['amenities'], row['description'],
                    row['photos'], row['source'], row['source_url'], row['source_id'],
                    float(row['price_per_night']), row['price_currency'],
                    float(row['availability_rate']), float(row['avg_rating']),
                    int(row['review_count']), row['host_name'], float(row['host_rating']),
                    int(row['host_review_count']), row['instant_bookable'] == 'true',
                    row['superhost'] == 'true', row['created_at'], row['updated_at'],
                    row['last_scraped_at'], row['is_active'] == 'true'
                ))
    
    conn.commit()
    print("Данные краткосрочной аренды загружены успешно!")

def load_long_term_rentals(conn):
    """Загрузка данных долгосрочной аренды"""
    print("Загрузка данных долгосрочной аренды...")
    
    with open('test_data_long_term_rentals.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        with conn.cursor() as cur:
            for row in reader:
                cur.execute("""
                    INSERT INTO long_term_rentals (
                        property_id, address, latitude, longitude, city, district,
                        property_type, bedrooms, bathrooms, floor_area_sqm,
                        land_area_sqm, amenities, description, photos, source,
                        source_url, source_id, monthly_rent, rent_currency,
                        deposit_amount, deposit_currency, utilities_included,
                        pet_friendly, furnished, available_from, lease_term_months,
                        agent_name, agent_rating, agent_review_count,
                        created_at, updated_at, last_scraped_at, is_active
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    ) ON CONFLICT (property_id) DO UPDATE SET
                        address = EXCLUDED.address,
                        monthly_rent = EXCLUDED.monthly_rent,
                        updated_at = EXCLUDED.updated_at,
                        last_scraped_at = EXCLUDED.last_scraped_at
                """, (
                    row['property_id'], row['address'], float(row['latitude']),
                    float(row['longitude']), row['city'], row['district'],
                    row['property_type'], int(row['bedrooms']), int(row['bathrooms']),
                    float(row['floor_area_sqm']), float(row['land_area_sqm']),
                    row['amenities'], row['description'], row['photos'], row['source'],
                    row['source_url'], row['source_id'], float(row['monthly_rent']),
                    row['rent_currency'], float(row['deposit_amount']),
                    row['deposit_currency'], row['utilities_included'] == 'true',
                    row['pet_friendly'] == 'true', row['furnished'] == 'true',
                    row['available_from'], int(row['lease_term_months']),
                    row['agent_name'], float(row['agent_rating']),
                    int(row['agent_review_count']), row['created_at'],
                    row['updated_at'], row['last_scraped_at'], row['is_active'] == 'true'
                ))
    
    conn.commit()
    print("Данные долгосрочной аренды загружены успешно!")

def load_property_sales(conn):
    """Загрузка данных продажи недвижимости"""
    print("Загрузка данных продажи недвижимости...")
    
    with open('test_data_property_sales.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        with conn.cursor() as cur:
            for row in reader:
                cur.execute("""
                    INSERT INTO property_sales (
                        property_id, address, latitude, longitude, city, district,
                        property_type, bedrooms, bathrooms, floor_area_sqm,
                        land_area_sqm, amenities, description, photos, source,
                        source_url, source_id, asking_price, price_currency,
                        price_per_sqm, property_age_years, construction_status,
                        ownership_type, agent_name, agent_rating, agent_review_count,
                        created_at, updated_at, last_scraped_at, is_active
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s
                    ) ON CONFLICT (property_id) DO UPDATE SET
                        address = EXCLUDED.address,
                        asking_price = EXCLUDED.asking_price,
                        price_per_sqm = EXCLUDED.price_per_sqm,
                        updated_at = EXCLUDED.updated_at,
                        last_scraped_at = EXCLUDED.last_scraped_at
                """, (
                    row['property_id'], row['address'], float(row['latitude']),
                    float(row['longitude']), row['city'], row['district'],
                    row['property_type'], int(row['bedrooms']), int(row['bathrooms']),
                    float(row['floor_area_sqm']), float(row['land_area_sqm']),
                    row['amenities'], row['description'], row['photos'], row['source'],
                    row['source_url'], row['source_id'], float(row['asking_price']),
                    row['price_currency'], float(row['price_per_sqm']),
                    int(row['property_age_years']), row['construction_status'],
                    row['ownership_type'], row['agent_name'], float(row['agent_rating']),
                    int(row['agent_review_count']), row['created_at'],
                    row['updated_at'], row['last_scraped_at'], row['is_active'] == 'true'
                ))
    
    conn.commit()
    print("Данные продажи недвижимости загружены успешно!")

def load_historical_prices(conn):
    """Загрузка исторических данных цен"""
    print("Загрузка исторических данных цен...")
    
    with open('test_data_historical_prices.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        with conn.cursor() as cur:
            for row in reader:
                cur.execute("""
                    INSERT INTO historical_prices (
                        property_id, date, price, price_currency, price_type,
                        source, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    ) ON CONFLICT (property_id, date, price_type) DO UPDATE SET
                        price = EXCLUDED.price,
                        created_at = EXCLUDED.created_at
                """, (
                    row['property_id'], row['date'], float(row['price']),
                    row['price_currency'], row['price_type'], row['source'],
                    row['created_at']
                ))
    
    conn.commit()
    print("Исторические данные цен загружены успешно!")

def load_market_statistics(conn):
    """Загрузка рыночной статистики"""
    print("Загрузка рыночной статистики...")
    
    with open('test_data_market_statistics.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        with conn.cursor() as cur:
            for row in reader:
                cur.execute("""
                    INSERT INTO market_statistics (
                        district, date, avg_sale_price_per_sqm, avg_rent_price_per_month,
                        avg_short_term_price_per_night, property_count, avg_property_age,
                        avg_bedrooms, avg_bathrooms, avg_floor_area, avg_land_area,
                        price_change_1y, price_change_3y, price_change_5y,
                        rent_yield_avg, occupancy_rate_short_term, days_on_market_avg,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    ) ON CONFLICT (district, date) DO UPDATE SET
                        avg_sale_price_per_sqm = EXCLUDED.avg_sale_price_per_sqm,
                        avg_rent_price_per_month = EXCLUDED.avg_rent_price_per_month,
                        avg_short_term_price_per_night = EXCLUDED.avg_short_term_price_per_night,
                        property_count = EXCLUDED.property_count,
                        price_change_1y = EXCLUDED.price_change_1y,
                        price_change_3y = EXCLUDED.price_change_3y,
                        price_change_5y = EXCLUDED.price_change_5y,
                        rent_yield_avg = EXCLUDED.rent_yield_avg,
                        occupancy_rate_short_term = EXCLUDED.occupancy_rate_short_term,
                        days_on_market_avg = EXCLUDED.days_on_market_avg,
                        created_at = EXCLUDED.created_at
                """, (
                    row['district'], row['date'], float(row['avg_sale_price_per_sqm']),
                    float(row['avg_rent_price_per_month']), float(row['avg_short_term_price_per_night']),
                    int(row['property_count']), float(row['avg_property_age']),
                    float(row['avg_bedrooms']), float(row['avg_bathrooms']),
                    float(row['avg_floor_area']), float(row['avg_land_area']),
                    float(row['price_change_1y']), float(row['price_change_3y']),
                    float(row['price_change_5y']), float(row['rent_yield_avg']),
                    float(row['occupancy_rate_short_term']), float(row['days_on_market_avg']),
                    row['created_at']
                ))
    
    conn.commit()
    print("Рыночная статистика загружена успешно!")

def main():
    """Основная функция"""
    print("Начинаем загрузку тестовых данных...")
    
    # Подключение к базе данных
    conn = connect_db()
    
    try:
        # Загрузка всех типов данных
        load_short_term_rentals(conn)
        load_long_term_rentals(conn)
        load_property_sales(conn)
        load_historical_prices(conn)
        load_market_statistics(conn)
        
        print("\nВсе тестовые данные успешно загружены!")
        
        # Вывод статистики
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM short_term_rentals")
            short_term_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM long_term_rentals")
            long_term_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM property_sales")
            sales_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM historical_prices")
            historical_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM market_statistics")
            stats_count = cur.fetchone()[0]
        
        print(f"\nСтатистика загруженных данных:")
        print(f"- Краткосрочная аренда: {short_term_count} записей")
        print(f"- Долгосрочная аренда: {long_term_count} записей")
        print(f"- Продажа недвижимости: {sales_count} записей")
        print(f"- Исторические цены: {historical_count} записей")
        print(f"- Рыночная статистика: {stats_count} записей")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main() 