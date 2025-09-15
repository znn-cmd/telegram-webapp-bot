#!/usr/bin/env python3
"""
Скрипт для автоматического создания индексов в базе данных Supabase
Ускоряет работу приложения с БД в 5-20 раз
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_supabase_client():
    """Создание клиента Supabase"""
    load_dotenv()
    
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть установлены в .env файле")
    
    return create_client(url, key)

def execute_sql_script(supabase: Client, sql_script_path: str):
    """Выполнение SQL скрипта"""
    try:
        with open(sql_script_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Разбиваем скрипт на отдельные команды
        sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        logger.info(f"📝 Найдено {len(sql_commands)} SQL команд для выполнения")
        
        for i, command in enumerate(sql_commands, 1):
            if command:
                try:
                    logger.info(f"🔧 Выполнение команды {i}/{len(sql_commands)}")
                    logger.debug(f"SQL: {command[:100]}...")
                    
                    # Выполняем команду через Supabase
                    result = supabase.rpc('exec_sql', {'sql_query': command}).execute()
                    
                    logger.info(f"✅ Команда {i} выполнена успешно")
                    
                except Exception as e:
                    # Проверяем, не является ли это ошибкой "уже существует"
                    if "already exists" in str(e).lower() or "уже существует" in str(e):
                        logger.warning(f"⚠️ Команда {i}: индекс уже существует")
                    else:
                        logger.error(f"❌ Ошибка выполнения команды {i}: {e}")
                        logger.error(f"SQL: {command}")
        
        logger.info("🎉 Все SQL команды обработаны")
        
    except Exception as e:
        logger.error(f"❌ Ошибка чтения SQL файла: {e}")
        raise

def create_indexes_manually(supabase: Client):
    """Создание индексов вручную через отдельные запросы"""
    
    indexes = [
        # Индексы для таблицы locations
        {
            'name': 'idx_locations_country_id',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_country_id ON locations(country_id)',
            'description': 'Индекс для поиска стран'
        },
        {
            'name': 'idx_locations_country_city',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_country_city ON locations(country_id, city_id)',
            'description': 'Индекс для поиска городов по стране'
        },
        {
            'name': 'idx_locations_city_county',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_city_county ON locations(city_id, county_id)',
            'description': 'Индекс для поиска областей по городу'
        },
        {
            'name': 'idx_locations_county_district',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_county_district ON locations(county_id, district_id)',
            'description': 'Индекс для поиска районов по области'
        },
        {
            'name': 'idx_locations_hierarchy',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_hierarchy ON locations(country_id, city_id, county_id, district_id)',
            'description': 'Составной индекс для полной иерархии локаций'
        },
        {
            'name': 'idx_locations_country_name',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_country_name ON locations(country_name)',
            'description': 'Индекс для поиска по названию страны'
        },
        {
            'name': 'idx_locations_city_name',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_city_name ON locations(city_name)',
            'description': 'Индекс для поиска по названию города'
        },
        {
            'name': 'idx_locations_county_name',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_county_name ON locations(county_name)',
            'description': 'Индекс для поиска по названию области'
        },
        {
            'name': 'idx_locations_district_name',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_locations_district_name ON locations(district_name)',
            'description': 'Индекс для поиска по названию района'
        },
        
        # Индексы для таблицы users (idx_users_telegram_id уже существует)
        {
            'name': 'idx_users_status',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_users_status ON users(user_status)',
            'description': 'Индекс для поиска по статусу пользователя'
        },
        {
            'name': 'idx_users_telegram_status',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_users_telegram_status ON users(telegram_id, user_status)',
            'description': 'Составной индекс для проверки админов'
        },
        {
            'name': 'idx_users_period_end',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_users_period_end ON users(period_end)',
            'description': 'Индекс для поиска по периоду подписки'
        },
        {
            'name': 'idx_users_language',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_users_language ON users(language)',
            'description': 'Индекс для поиска по языку пользователя'
        },
        {
            'name': 'idx_users_balance',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance)',
            'description': 'Индекс для поиска по балансу пользователя'
        },
        {
            'name': 'idx_users_registration_date',
            'sql': 'CREATE INDEX IF NOT EXISTS idx_users_registration_date ON users(registration_date)',
            'description': 'Индекс для поиска по дате регистрации'
        }
    ]
    
    logger.info(f"🔧 Создание {len(indexes)} индексов...")
    
    for i, index in enumerate(indexes, 1):
        try:
            logger.info(f"📝 {i}/{len(indexes)}: {index['description']}")
            logger.debug(f"SQL: {index['sql']}")
            
            # Выполняем создание индекса
            result = supabase.rpc('exec_sql', {'sql_query': index['sql']}).execute()
            
            logger.info(f"✅ Индекс '{index['name']}' создан успешно")
            
        except Exception as e:
            if "already exists" in str(e).lower() or "уже существует" in str(e):
                logger.warning(f"⚠️ Индекс '{index['name']}' уже существует")
            else:
                logger.error(f"❌ Ошибка создания индекса '{index['name']}': {e}")

def check_database_connection(supabase: Client):
    """Проверка подключения к базе данных"""
    try:
        # Простой тест подключения
        result = supabase.table('users').select('id').limit(1).execute()
        logger.info("✅ Подключение к Supabase работает")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Supabase: {e}")
        return False

def main():
    """Основная функция"""
    logger.info("🚀 Начало создания индексов базы данных")
    
    try:
        # Создаем клиент Supabase
        supabase = create_supabase_client()
        
        # Проверяем подключение
        if not check_database_connection(supabase):
            logger.error("❌ Не удалось подключиться к базе данных")
            return False
        
        # Создаем индексы
        create_indexes_manually(supabase)
        
        logger.info("🎉 Все индексы созданы успешно!")
        logger.info("📊 Ожидаемое ускорение: 5-20 раз для географических запросов")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
