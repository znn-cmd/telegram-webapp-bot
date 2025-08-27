"""
Модуль с безопасными операциями для работы с базой данных
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable
from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class DatabaseOperationError(Exception):
    """Исключение для ошибок операций с базой данных"""
    pass

def safe_db_operation(operation: Callable, max_retries: int = 3, delay: int = 2) -> Any:
    """
    Выполняет операцию с базой данных с повторными попытками при ошибках
    
    Args:
        operation: Функция операции для выполнения
        max_retries: Максимальное количество попыток
        delay: Задержка между попытками в секундах
    
    Returns:
        Результат операции
    
    Raises:
        DatabaseOperationError: Если все попытки неудачны
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Получаем актуальный клиент
            supabase = get_supabase_client()
            
            # Выполняем операцию
            result = operation(supabase)
            
            if attempt > 0:
                logger.info(f"✅ Операция успешно выполнена после {attempt + 1} попыток")
            
            return result
            
        except Exception as e:
            last_error = e
            error_msg = str(e).lower()
            
            # Проверяем тип ошибки
            if "ssl" in error_msg or "handshake" in error_msg or "timeout" in error_msg:
                logger.warning(f"⚠️ SSL/Таймаут ошибка (попытка {attempt + 1}/{max_retries}): {e}")
            else:
                logger.error(f"❌ Ошибка операции с БД (попытка {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                # Прогрессивная задержка
                wait_time = delay * (attempt + 1)
                logger.info(f"⏳ Ожидание {wait_time} секунд перед повторной попыткой...")
                time.sleep(wait_time)
                
                # Если это SSL ошибка, пытаемся переподключиться
                if "ssl" in error_msg or "handshake" in error_msg:
                    try:
                        from supabase_client import supabase_connection
                        supabase_connection.reconnect()
                        logger.info("🔄 Выполнено переподключение к Supabase")
                    except:
                        pass
            else:
                logger.error(f"❌ Все {max_retries} попыток неудачны")
    
    raise DatabaseOperationError(f"Не удалось выполнить операцию после {max_retries} попыток: {last_error}")

def safe_select(table: str, columns: str = "*", filters: Optional[Dict[str, Any]] = None, 
                limit: Optional[int] = None, order: Optional[str] = None) -> List[Dict]:
    """
    Безопасное выполнение SELECT запроса
    
    Args:
        table: Название таблицы
        columns: Столбцы для выборки
        filters: Словарь с фильтрами (ключ - столбец, значение - значение для фильтрации)
        limit: Ограничение количества записей
        order: Столбец для сортировки
    
    Returns:
        Список записей
    """
    def operation(supabase):
        query = supabase.table(table).select(columns)
        
        if filters:
            for column, value in filters.items():
                if value is None:
                    query = query.is_(column, 'null')
                else:
                    query = query.eq(column, value)
        
        if order:
            query = query.order(order)
        
        if limit:
            query = query.limit(limit)
        
        response = query.execute()
        return response.data if response.data else []
    
    return safe_db_operation(operation)

def safe_insert(table: str, data: Dict[str, Any]) -> Dict:
    """
    Безопасное выполнение INSERT запроса
    
    Args:
        table: Название таблицы
        data: Данные для вставки
    
    Returns:
        Вставленная запись
    """
    def operation(supabase):
        response = supabase.table(table).insert(data).execute()
        return response.data[0] if response.data else None
    
    return safe_db_operation(operation)

def safe_update(table: str, data: Dict[str, Any], filters: Dict[str, Any]) -> List[Dict]:
    """
    Безопасное выполнение UPDATE запроса
    
    Args:
        table: Название таблицы
        data: Данные для обновления
        filters: Фильтры для определения записей для обновления
    
    Returns:
        Обновленные записи
    """
    def operation(supabase):
        query = supabase.table(table).update(data)
        
        for column, value in filters.items():
            query = query.eq(column, value)
        
        response = query.execute()
        return response.data if response.data else []
    
    return safe_db_operation(operation)

def safe_upsert(table: str, data: Dict[str, Any]) -> Dict:
    """
    Безопасное выполнение UPSERT запроса
    
    Args:
        table: Название таблицы
        data: Данные для вставки/обновления
    
    Returns:
        Вставленная/обновленная запись
    """
    def operation(supabase):
        response = supabase.table(table).upsert(data).execute()
        return response.data[0] if response.data else None
    
    return safe_db_operation(operation)

def safe_delete(table: str, filters: Dict[str, Any]) -> List[Dict]:
    """
    Безопасное выполнение DELETE запроса
    
    Args:
        table: Название таблицы
        filters: Фильтры для определения записей для удаления
    
    Returns:
        Удаленные записи
    """
    def operation(supabase):
        query = supabase.table(table).delete()
        
        for column, value in filters.items():
            query = query.eq(column, value)
        
        response = query.execute()
        return response.data if response.data else []
    
    return safe_db_operation(operation)

# Пример использования:
# from safe_db_operations import safe_select, safe_insert
# 
# # Безопасная выборка
# users = safe_select('users', filters={'telegram_id': 123456})
# 
# # Безопасная вставка
# new_user = safe_insert('users', {'telegram_id': 123456, 'username': 'test'})