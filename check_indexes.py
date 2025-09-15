#!/usr/bin/env python3
"""
Скрипт для проверки существующих индексов в базе данных
Помогает понять, какие индексы уже созданы
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

def check_table_exists(supabase: Client, table_name: str) -> bool:
    """Проверка существования таблицы"""
    try:
        result = supabase.table(table_name).select('*').limit(1).execute()
        return True
    except Exception as e:
        logger.warning(f"⚠️ Таблица {table_name} не существует: {e}")
        return False

def check_indexes_for_table(supabase: Client, table_name: str):
    """Проверка индексов для конкретной таблицы"""
    try:
        # Запрос к системной таблице pg_indexes
        query = f"""
        SELECT 
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE tablename = '{table_name}' 
        ORDER BY indexname;
        """
        
        result = supabase.rpc('exec_sql', {'sql_query': query}).execute()
        
        if result.data:
            logger.info(f"📋 Индексы для таблицы {table_name}:")
            for index in result.data:
                logger.info(f"  - {index['indexname']}")
                logger.debug(f"    {index['indexdef']}")
        else:
            logger.warning(f"⚠️ Индексы для таблицы {table_name} не найдены")
            
    except Exception as e:
        logger.error(f"❌ Ошибка проверки индексов для {table_name}: {e}")

def check_table_structure(supabase: Client, table_name: str):
    """Проверка структуры таблицы"""
    try:
        query = f"""
        SELECT 
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = '{table_name}' 
        ORDER BY ordinal_position;
        """
        
        result = supabase.rpc('exec_sql', {'sql_query': query}).execute()
        
        if result.data:
            logger.info(f"📊 Структура таблицы {table_name}:")
            for column in result.data:
                nullable = "NULL" if column['is_nullable'] == 'YES' else "NOT NULL"
                logger.info(f"  - {column['column_name']}: {column['data_type']} {nullable}")
        else:
            logger.warning(f"⚠️ Структура таблицы {table_name} не найдена")
            
    except Exception as e:
        logger.error(f"❌ Ошибка проверки структуры {table_name}: {e}")

def main():
    """Основная функция"""
    logger.info("🔍 Проверка индексов и структуры базы данных")
    
    try:
        # Создаем клиент Supabase
        supabase = create_supabase_client()
        
        # Проверяем подключение
        try:
            result = supabase.table('users').select('id').limit(1).execute()
            logger.info("✅ Подключение к Supabase работает")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Supabase: {e}")
            return False
        
        # Проверяем таблицы
        tables_to_check = ['users', 'locations']
        
        for table_name in tables_to_check:
            logger.info(f"\n{'='*50}")
            logger.info(f"Проверка таблицы: {table_name}")
            logger.info(f"{'='*50}")
            
            if check_table_exists(supabase, table_name):
                check_table_structure(supabase, table_name)
                check_indexes_for_table(supabase, table_name)
            else:
                logger.warning(f"⚠️ Таблица {table_name} не существует, пропускаем")
        
        logger.info(f"\n{'='*50}")
        logger.info("✅ Проверка завершена!")
        logger.info(f"{'='*50}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
