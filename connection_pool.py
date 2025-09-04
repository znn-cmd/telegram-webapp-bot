import threading
import time
import logging
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import asyncio
import httpx
from functools import wraps

logger = logging.getLogger(__name__)

class SupabaseConnectionPool:
    """Пул соединений для Supabase с retry логикой и SSL timeout обработкой"""
    
    def __init__(self, max_workers: int = 10, max_connections: int = 20):
        self.max_workers = max_workers
        self.max_connections = max_connections
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_connections = 0
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'active_connections': 0
        }
        self.lock = threading.RLock()
        
        logger.info(f"SupabaseConnectionPool инициализирован: {max_workers} workers, {max_connections} connections")
    
    def execute_query(self, query_func, *args, **kwargs) -> Future:
        """Выполнение запроса с retry логикой и SSL timeout обработкой"""
        
        def wrapped_query():
            start_time = time.time()
            max_retries = 3
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    with self.lock:
                        if self.active_connections >= self.max_connections:
                            logger.warning(f"Достигнут лимит соединений ({self.max_connections}), ожидание...")
                            time.sleep(0.1)
                            # Продолжаем попытку, а не выходим из цикла
                            continue
                        
                        self.active_connections += 1
                        self.stats['active_connections'] = self.active_connections
                    
                    logger.debug(f"Выполнение запроса (попытка {attempt + 1}/{max_retries})")
                    
                    # Выполняем запрос с таймаутом
                    result = query_func(*args, **kwargs)
                    
                    with self.lock:
                        self.stats['successful_requests'] += 1
                        self.stats['total_requests'] += 1
                        self.active_connections -= 1
                        self.stats['active_connections'] = self.active_connections
                    
                    response_time = time.time() - start_time
                    self._update_average_response_time(response_time)
                    
                    logger.debug(f"Запрос выполнен успешно за {response_time:.3f}s")
                    return result
                    
                except Exception as e:
                    with self.lock:
                        self.active_connections -= 1
                        self.stats['active_connections'] = self.active_connections
                    
                    error_msg = str(e)
                    logger.warning(f"Попытка {attempt + 1}/{max_retries} не удалась: {error_msg}")
                    
                    # Проверяем, стоит ли повторять попытку
                    if "timeout" in error_msg.lower() or "handshake" in error_msg.lower():
                        if attempt < max_retries - 1:
                            logger.info(f"SSL timeout, повторная попытка через {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Экспоненциальная задержка
                            continue
                    
                    # Если это последняя попытка или ошибка не связана с сетью
                    with self.lock:
                        self.stats['failed_requests'] += 1
                        self.stats['total_requests'] += 1
                    
                    logger.error(f"Все попытки исчерпаны. Ошибка: {e}")
                    raise e
            
            # Если мы дошли сюда, значит все попытки исчерпаны из-за лимита соединений
            raise Exception("Не удалось получить соединение после всех попыток")
        
        # Всегда возвращаем Future
        logger.debug(f"SupabaseConnectionPool.execute_query: создание Future")
        future = self.executor.submit(wrapped_query)
        logger.debug(f"SupabaseConnectionPool.execute_query: Future создан: {future}")
        return future
    
    def _update_average_response_time(self, response_time: float):
        """Обновление среднего времени ответа"""
        with self.lock:
            total_requests = self.stats['total_requests']
            current_avg = self.stats['average_response_time']
            
            # Вычисляем скользящее среднее
            if total_requests == 1:
                self.stats['average_response_time'] = response_time
            else:
                self.stats['average_response_time'] = (current_avg * (total_requests - 1) + response_time) / total_requests
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики пула соединений"""
        with self.lock:
            return {
                'total_requests': self.stats['total_requests'],
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'success_rate': (self.stats['successful_requests'] / max(self.stats['total_requests'], 1)) * 100,
                'average_response_time': self.stats['average_response_time'],
                'active_connections': self.stats['active_connections'],
                'max_connections': self.max_connections,
                'max_workers': self.max_workers
            }
    
    def shutdown(self):
        """Завершение работы пула соединений"""
        self.executor.shutdown(wait=True)
        logger.info("SupabaseConnectionPool завершен")

class QueryOptimizer:
    """Оптимизатор запросов к Supabase"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.pool = SupabaseConnectionPool()
        self.query_cache = {}
        
        logger.info("QueryOptimizer инициализирован")
    
    def optimized_select(self, table: str, fields: Optional[str] = None, 
                         conditions: Optional[Dict] = None, 
                         limit: Optional[int] = None,
                         order_by: Optional[str] = None) -> Future:
        """Оптимизированный SELECT запрос"""
        
        def query_func():
            query = self.supabase.table(table)
            
            # Выбираем только нужные поля
            if fields:
                query = query.select(fields)
            else:
                query = query.select('*')
            
            # Добавляем условия
            if conditions:
                for field, value in conditions.items():
                    if isinstance(value, (list, tuple)):
                        query = query.in_(field, value)
                    else:
                        query = query.eq(field, value)
            
            # Добавляем сортировку
            if order_by:
                query = query.order(order_by)
            
            # Ограничиваем результат
            if limit:
                query = query.limit(limit)
            
            return query.execute()
        
        logger.debug(f"Выполнение optimized_select для таблицы {table}")
        future = self.pool.execute_query(query_func)
        logger.debug(f"QueryOptimizer получил Future: {future}")
        return future
    
    def batch_query(self, queries: list) -> list:
        """Выполнение batch запросов"""
        futures = []
        for query in queries:
            future = self.optimized_select(
                query['table'],
                fields=query.get('fields'),
                conditions=query.get('conditions'),
                limit=query.get('limit'),
                order_by=query.get('order_by')
            )
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=30)
                results.append(result)
            except Exception as e:
                logger.error(f"Ошибка batch запроса: {e}")
                results.append(None)
        
        return results
    
    def get_locations_optimized(self, country_id: Optional[int] = None) -> Future:
        """Оптимизированный запрос локаций"""
        conditions = {}
        if country_id is not None:
            conditions['country_id'] = country_id
        
        return self.optimized_select(
            'locations',
            fields='country_id,country_name,city_id,city_name,county_id,county_name',
            conditions=conditions,
            order_by='country_name,city_name,county_name'
        )
    
    def get_market_data_optimized(self, location_codes: Dict) -> Future:
        """Оптимизированный запрос рыночных данных"""
        conditions = {}
        if location_codes.get('country_id'):
            conditions['country_id'] = location_codes['country_id']
        if location_codes.get('city_id'):
            conditions['city_id'] = location_codes['city_id']
        if location_codes.get('county_id'):
            conditions['county_id'] = location_codes['county_id']
        
        return self.optimized_select(
            'market_data',
            conditions=conditions,
            order_by='created_at',
            limit=1
        )
    
    def get_currency_rates_optimized(self) -> Future:
        """Оптимизированный запрос курсов валют"""
        return self.optimized_select(
            'currency',
            order_by='created_at',
            limit=1
        )
    
    def get_user_data_optimized(self, telegram_id: int) -> Future:
        """Оптимизированный запрос данных пользователя"""
        return self.optimized_select(
            'users',
            conditions={'telegram_id': telegram_id},
            limit=1
        )

# Глобальный экземпляр оптимизатора запросов
query_optimizer = None

def init_query_optimizer(supabase_client):
    """Инициализация оптимизатора запросов"""
    global query_optimizer
    query_optimizer = QueryOptimizer(supabase_client)
    return query_optimizer
