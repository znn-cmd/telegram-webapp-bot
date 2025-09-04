import time
import logging
import threading
from typing import Dict, Any, Optional, Callable
from functools import wraps
from collections import defaultdict, deque
import json
import numpy as np

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Мониторинг производительности приложения"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.RLock()
        self.start_time = time.time()
        
        # Метрики по категориям
        self.query_metrics = defaultdict(list)
        self.api_metrics = defaultdict(list)
        self.cache_metrics = defaultdict(list)
        self.error_metrics = defaultdict(list)
        
        logger.info("PerformanceMonitor инициализирован")
    
    def time_function(self, category: str = "general"):
        """Декоратор для измерения времени выполнения функций"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self.record_metric(f"{category}_{func.__name__}", execution_time)
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.record_error(f"{category}_{func.__name__}", str(e), execution_time)
                    raise
            return wrapper
        return decorator
    
    def record_metric(self, name: str, value: float, metadata: Optional[Dict] = None):
        """Запись метрики"""
        with self.lock:
            timestamp = time.time()
            metric_data = {
                'timestamp': timestamp,
                'value': value,
                'metadata': metadata or {}
            }
            self.metrics[name].append(metric_data)
    
    def record_error(self, name: str, error: str, execution_time: float):
        """Запись ошибки"""
        with self.lock:
            timestamp = time.time()
            error_data = {
                'timestamp': timestamp,
                'error': error,
                'execution_time': execution_time
            }
            self.error_metrics[name].append(error_data)
    
    def record_query_metric(self, query_name: str, execution_time: float, 
                           success: bool, rows_returned: Optional[int] = None):
        """Запись метрики запроса к БД"""
        with self.lock:
            query_data = {
                'timestamp': time.time(),
                'execution_time': execution_time,
                'success': success,
                'rows_returned': rows_returned
            }
            self.query_metrics[query_name].append(query_data)
    
    def record_api_metric(self, endpoint: str, method: str, execution_time: float,
                         status_code: int, response_size: Optional[int] = None):
        """Запись метрики API"""
        with self.lock:
            api_data = {
                'timestamp': time.time(),
                'method': method,
                'execution_time': execution_time,
                'status_code': status_code,
                'response_size': response_size
            }
            self.api_metrics[endpoint].append(api_data)
    
    def record_cache_metric(self, cache_name: str, operation: str, 
                           hit: bool, execution_time: float):
        """Запись метрики кэша"""
        with self.lock:
            cache_data = {
                'timestamp': time.time(),
                'operation': operation,
                'hit': hit,
                'execution_time': execution_time
            }
            self.cache_metrics[cache_name].append(cache_data)
    
    def get_metric_stats(self, name: str, window_seconds: int = 3600) -> Dict[str, Any]:
        """Получение статистики метрики за указанный период"""
        with self.lock:
            if name not in self.metrics:
                return {}
            
            cutoff_time = time.time() - window_seconds
            recent_metrics = [
                m for m in self.metrics[name] 
                if m['timestamp'] >= cutoff_time
            ]
            
            if not recent_metrics:
                return {}
            
            values = [m['value'] for m in recent_metrics]
            
            return {
                'count': len(recent_metrics),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'total': sum(values),
                'window_seconds': window_seconds
            }
    
    def get_query_stats(self, query_name: str, window_seconds: int = 3600) -> Dict[str, Any]:
        """Получение статистики запросов"""
        with self.lock:
            if query_name not in self.query_metrics:
                return {}
            
            cutoff_time = time.time() - window_seconds
            recent_queries = [
                q for q in self.query_metrics[query_name] 
                if q['timestamp'] >= cutoff_time
            ]
            
            if not recent_queries:
                return {}
            
            execution_times = [q['execution_time'] for q in recent_queries]
            successful_queries = [q for q in recent_queries if q['success']]
            
            return {
                'total_queries': len(recent_queries),
                'successful_queries': len(successful_queries),
                'failed_queries': len(recent_queries) - len(successful_queries),
                'success_rate': (len(successful_queries) / len(recent_queries)) * 100,
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'min_execution_time': min(execution_times),
                'max_execution_time': max(execution_times),
                'window_seconds': window_seconds
            }
    
    def get_api_stats(self, endpoint: str, window_seconds: int = 3600) -> Dict[str, Any]:
        """Получение статистики API"""
        with self.lock:
            if endpoint not in self.api_metrics:
                return {}
            
            cutoff_time = time.time() - window_seconds
            recent_requests = [
                r for r in self.api_metrics[endpoint] 
                if r['timestamp'] >= cutoff_time
            ]
            
            if not recent_requests:
                return {}
            
            execution_times = [r['execution_time'] for r in recent_requests]
            status_codes = [r['status_code'] for r in recent_requests]
            
            return {
                'total_requests': len(recent_requests),
                'avg_execution_time': sum(execution_times) / len(execution_times),
                'min_execution_time': min(execution_times),
                'max_execution_time': max(execution_times),
                'status_codes': dict(zip(*np.unique(status_codes, return_counts=True))),
                'window_seconds': window_seconds
            }
    
    def get_cache_stats(self, cache_name: str, window_seconds: int = 3600) -> Dict[str, Any]:
        """Получение статистики кэша"""
        with self.lock:
            if cache_name not in self.cache_metrics:
                return {}
            
            cutoff_time = time.time() - window_seconds
            recent_operations = [
                c for c in self.cache_metrics[cache_name] 
                if c['timestamp'] >= cutoff_time
            ]
            
            if not recent_operations:
                return {}
            
            hits = [c for c in recent_operations if c['hit']]
            misses = [c for c in recent_operations if not c['hit']]
            
            return {
                'total_operations': len(recent_operations),
                'hits': len(hits),
                'misses': len(misses),
                'hit_rate': (len(hits) / len(recent_operations)) * 100,
                'avg_execution_time': sum(c['execution_time'] for c in recent_operations) / len(recent_operations),
                'window_seconds': window_seconds
            }
    
    def get_overall_stats(self, window_seconds: int = 3600) -> Dict[str, Any]:
        """Получение общей статистики"""
        with self.lock:
            cutoff_time = time.time() - window_seconds
            
            # Общая статистика метрик
            all_metrics = []
            for metric_name, metric_data in self.metrics.items():
                recent_metrics = [m for m in metric_data if m['timestamp'] >= cutoff_time]
                all_metrics.extend([m['value'] for m in recent_metrics])
            
            # Статистика ошибок
            all_errors = []
            for error_name, error_data in self.error_metrics.items():
                recent_errors = [e for e in error_data if e['timestamp'] >= cutoff_time]
                all_errors.extend(recent_errors)
            
            return {
                'uptime_seconds': time.time() - self.start_time,
                'total_metrics_recorded': len(all_metrics),
                'total_errors': len(all_errors),
                'avg_metric_value': sum(all_metrics) / len(all_metrics) if all_metrics else 0,
                'window_seconds': window_seconds,
                'cache_names': list(self.cache_metrics.keys()),
                'query_names': list(self.query_metrics.keys()),
                'api_endpoints': list(self.api_metrics.keys())
            }
    
    def export_metrics(self, filename: str = None) -> str:
        """Экспорт метрик в JSON файл"""
        with self.lock:
            export_data = {
                'timestamp': time.time(),
                'metrics': {name: list(data) for name, data in self.metrics.items()},
                'query_metrics': dict(self.query_metrics),
                'api_metrics': dict(self.api_metrics),
                'cache_metrics': dict(self.cache_metrics),
                'error_metrics': dict(self.error_metrics)
            }
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Метрики экспортированы в {filename}")
                return filename
            else:
                return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def clear_old_metrics(self, older_than_seconds: int = 86400):
        """Очистка старых метрик (старше 24 часов по умолчанию)"""
        with self.lock:
            cutoff_time = time.time() - older_than_seconds
            
            # Очищаем основные метрики
            for metric_name in list(self.metrics.keys()):
                self.metrics[metric_name] = deque(
                    [m for m in self.metrics[metric_name] if m['timestamp'] >= cutoff_time],
                    maxlen=self.max_history
                )
            
            # Очищаем метрики запросов
            for query_name in list(self.query_metrics.keys()):
                self.query_metrics[query_name] = [
                    q for q in self.query_metrics[query_name] 
                    if q['timestamp'] >= cutoff_time
                ]
            
            # Очищаем метрики API
            for endpoint in list(self.api_metrics.keys()):
                self.api_metrics[endpoint] = [
                    a for a in self.api_metrics[endpoint] 
                    if a['timestamp'] >= cutoff_time
                ]
            
            # Очищаем метрики кэша
            for cache_name in list(self.cache_metrics.keys()):
                self.cache_metrics[cache_name] = [
                    c for c in self.cache_metrics[cache_name] 
                    if c['timestamp'] >= cutoff_time
                ]
            
            # Очищаем метрики ошибок
            for error_name in list(self.error_metrics.keys()):
                self.error_metrics[error_name] = [
                    e for e in self.error_metrics[error_name] 
                    if e['timestamp'] >= cutoff_time
                ]
            
            logger.info(f"Очищены метрики старше {older_than_seconds} секунд")

# Глобальный экземпляр монитора производительности
performance_monitor = PerformanceMonitor()

# Декораторы для удобного использования
def monitor_performance(category: str = "general"):
    """Декоратор для мониторинга производительности"""
    return performance_monitor.time_function(category)

def monitor_query(query_name: str):
    """Декоратор для мониторинга запросов к БД"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                rows_returned = len(result.data) if hasattr(result, 'data') else None
                performance_monitor.record_query_metric(query_name, execution_time, True, rows_returned)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_query_metric(query_name, execution_time, False)
                raise
        return wrapper
    return decorator

def monitor_api(endpoint: str):
    """Декоратор для мониторинга API endpoints"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                # Определяем размер ответа
                response_size = len(str(result)) if result else 0
                performance_monitor.record_api_metric(endpoint, "GET", execution_time, 200, response_size)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_monitor.record_api_metric(endpoint, "GET", execution_time, 500)
                raise
        return wrapper
    return decorator
