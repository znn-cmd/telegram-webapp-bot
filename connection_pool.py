import threading
import time
import logging
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue, Empty
import asyncio

logger = logging.getLogger(__name__)

class SupabaseConnectionPool:
    """Пул соединений для Supabase с оптимизацией запросов"""
    
    def __init__(self, max_workers: int = 10, max_connections: int = 20):
        self.max_workers = max_workers
        self.max_connections = max_connections
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.connection_queue = Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.RLock()
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'active_connections': 0
        }
        
        logger.info(f"SupabaseConnectionPool инициализирован: {max_workers} workers, {max_connections} connections")
    
    def execute_query(self, query_func, *args, **kwargs) -> Future:
        """Выполнение запроса через пул соединений"""
        start_time = time.time()
        
        def wrapped_query():
            try:
                with self.lock:
                    self.active_connections += 1
                    self.stats['active_connections'] = self.active_connections
                
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
                    self.stats['failed_requests'] += 1
                    self.stats['total_requests'] += 1
                    self.active_connections -= 1
                    self.stats['active_connections'] = self.active_connections
                
                logger.error(f"Ошибка выполнения запроса: {e}")
                raise e
        
        return self.executor.submit(wrapped_query)
    
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
        
        return self.pool.execute_query(query_func)
    
    def batch_query(self, queries: list) -> list:
        """Выполнение нескольких запросов в пакете"""
        futures = []
        
        for query_info in queries:
            table = query_info['table']
            fields = query_info.get('fields')
            conditions = query_info.get('conditions', {})
            limit = query_info.get('limit')
            order_by = query_info.get('order_by')
            
            future = self.optimized_select(table, fields, conditions, limit, order_by)
            futures.append(future)
        
        # Ждем завершения всех запросов
        results = []
        for future in futures:
            try:
                result = future.result(timeout=30)  # 30 секунд таймаут
                results.append(result)
            except Exception as e:
                logger.error(f"Ошибка в batch запросе: {e}")
                results.append(None)
        
        return results
    
    def get_locations_optimized(self, country_id: int, city_id: Optional[int] = None,
                               county_id: Optional[int] = None) -> Future:
        """Оптимизированное получение данных локаций"""
        
        def query_func():
            # Выбираем только нужные поля
            fields = 'country_id,city_id,county_id,district_id,country_name,city_name,county_name,district_name'
            
            query = self.supabase.table('locations').select(fields)
            
            # Добавляем условия в порядке индексов
            if country_id:
                query = query.eq('country_id', country_id)
            if city_id:
                query = query.eq('city_id', city_id)
            if county_id:
                query = query.eq('county_id', county_id)
            
            # Сортируем для лучшей производительности
            query = query.order('country_id').order('city_id').order('county_id')
            
            return query.execute()
        
        return self.pool.execute_query(query_func)
    
    def get_market_data_optimized(self, location_codes: Dict) -> Future:
        """Оптимизированное получение рыночных данных"""
        
        def query_func():
            # Выбираем только нужные поля для анализа
            fields = 'country_id,city_id,county_id,district_id,avg_price_for_sale,avg_price_for_rent,count_for_sale,count_for_rent,yield'
            
            query = self.supabase.table('general_data').select(fields)
            
            # Добавляем условия локации
            if location_codes.get('country_id'):
                query = query.eq('country_id', location_codes['country_id'])
            if location_codes.get('city_id'):
                query = query.eq('city_id', location_codes['city_id'])
            if location_codes.get('county_id'):
                query = query.eq('county_id', location_codes['county_id'])
            if location_codes.get('district_id'):
                query = query.eq('district_id', location_codes['district_id'])
            
            return query.execute()
        
        return self.pool.execute_query(query_func)
    
    def get_currency_rates_optimized(self) -> Future:
        """Оптимизированное получение курсов валют"""
        
        def query_func():
            # Получаем только последние курсы
            fields = 'rub,usd,euro,try,aed,thb,created_at'
            return self.supabase.table('currency').select(fields).order('created_at', desc=True).limit(1).execute()
        
        return self.pool.execute_query(query_func)
    
    def get_user_data_optimized(self, telegram_id: int) -> Future:
        """Оптимизированное получение данных пользователя"""
        
        def query_func():
            # Выбираем только нужные поля
            fields = 'id,telegram_id,username,tg_name,last_name,language,balance,user_status,period_end'
            return self.supabase.table('users').select(fields).eq('telegram_id', telegram_id).limit(1).execute()
        
        return self.pool.execute_query(query_func)
    
    def shutdown(self):
        """Завершение работы оптимизатора"""
        self.pool.shutdown()
        logger.info("QueryOptimizer завершен")

# Глобальный экземпляр оптимизатора запросов
query_optimizer = None

def init_query_optimizer(supabase_client):
    """Инициализация глобального оптимизатора запросов"""
    global query_optimizer
    query_optimizer = QueryOptimizer(supabase_client)
    return query_optimizer
