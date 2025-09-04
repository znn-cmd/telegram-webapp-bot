import time
import json
import logging
import threading
from functools import wraps
from typing import Any, Dict, Optional, Callable
from collections import OrderedDict

logger = logging.getLogger(__name__)

class TTLCache:
    """Кэш с временем жизни (TTL) и автоматической очисткой"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.RLock()
        
        # Запускаем очистку устаревших записей
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Запуск фонового потока для очистки устаревших записей"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Проверяем каждые 5 минут
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Ошибка в потоке очистки кэша: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired(self):
        """Удаление устаревших записей"""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, (value, timestamp, ttl) in self.cache.items():
                if current_time - timestamp > ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
        
        if expired_keys:
            logger.info(f"Удалено {len(expired_keys)} устаревших записей из кэша")
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кэша"""
        with self.lock:
            if key in self.cache:
                value, timestamp, ttl = self.cache[key]
                if time.time() - timestamp < ttl:
                    # Перемещаем в конец (LRU)
                    self.cache.move_to_end(key)
                    return value
                else:
                    # Удаляем устаревшую запись
                    del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установка значения в кэш"""
        if ttl is None:
            ttl = self.default_ttl
        
        with self.lock:
            # Если ключ уже существует, удаляем его
            if key in self.cache:
                del self.cache[key]
            
            # Если кэш полон, удаляем самую старую запись
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            # Добавляем новую запись
            self.cache[key] = (value, time.time(), ttl)
    
    def delete(self, key: str) -> bool:
        """Удаление записи из кэша"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
        return False
    
    def clear(self) -> None:
        """Очистка всего кэша"""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Размер кэша"""
        with self.lock:
            return len(self.cache)
    
    def keys(self) -> list:
        """Список ключей в кэше"""
        with self.lock:
            return list(self.cache.keys())
    
    def stats(self) -> Dict[str, Any]:
        """Статистика кэша"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'keys': list(self.cache.keys())
            }

class CacheManager:
    """Менеджер кэширования с различными стратегиями"""
    
    def __init__(self):
        # Кэши для разных типов данных с обновленными TTL
        self.location_cache = TTLCache(max_size=500, default_ttl=604800)  # 1 неделя (7 дней)
        self.currency_cache = TTLCache(max_size=100, default_ttl=86400)    # 1 день (24 часа)
        self.market_cache = TTLCache(max_size=200, default_ttl=604800)     # 1 неделя (7 дней)
        self.user_cache = TTLCache(max_size=300, default_ttl=604800)       # 1 неделя (7 дней)
        
        logger.info("CacheManager инициализирован с обновленными TTL")
    
    def cache_decorator(self, cache_name: str, ttl: Optional[int] = None):
        """Декоратор для автоматического кэширования функций"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Создаем ключ кэша на основе аргументов функции
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # Выбираем нужный кэш
                cache = getattr(self, f"{cache_name}_cache")
                
                # Пытаемся получить из кэша
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Кэш HIT для {func.__name__}")
                    return cached_result
                
                # Выполняем функцию
                logger.debug(f"Кэш MISS для {func.__name__}")
                result = func(*args, **kwargs)
                
                # Сохраняем результат в кэш
                cache.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
    
    def get_location_data(self, country_id: int, city_id: Optional[int] = None, 
                          county_id: Optional[int] = None) -> Optional[Dict]:
        """Получение данных локации с кэшированием"""
        cache_key = f"location:{country_id}:{city_id}:{county_id}"
        return self.location_cache.get(cache_key)
    
    def set_location_data(self, country_id: int, city_id: Optional[int] = None,
                          county_id: Optional[int] = None, data: Any = None) -> None:
        """Сохранение данных локации в кэш"""
        cache_key = f"location:{country_id}:{city_id}:{county_id}"
        self.location_cache.set(cache_key, data)
    
    def get_currency_rates(self) -> Optional[Dict]:
        """Получение курсов валют из кэша"""
        return self.currency_cache.get("latest_rates")
    
    def set_currency_rates(self, rates: Dict) -> None:
        """Сохранение курсов валют в кэш"""
        self.currency_cache.set("latest_rates", rates)
    
    def get_market_data(self, location_codes: Dict) -> Optional[Dict]:
        """Получение рыночных данных из кэша"""
        cache_key = f"market:{hash(json.dumps(location_codes, sort_keys=True))}"
        return self.market_cache.get(cache_key)
    
    def set_market_data(self, location_codes: Dict, data: Any) -> None:
        """Сохранение рыночных данных в кэш"""
        cache_key = f"market:{hash(json.dumps(location_codes, sort_keys=True))}"
        self.market_cache.set(cache_key, data)
    
    def get_user_data(self, telegram_id: int) -> Optional[Dict]:
        """Получение данных пользователя из кэша"""
        cache_key = f"user:{telegram_id}"
        return self.user_cache.get(cache_key)
    
    def set_user_data(self, telegram_id: int, data: Any) -> None:
        """Сохранение данных пользователя в кэш"""
        cache_key = f"user:{telegram_id}"
        self.user_cache.set(cache_key, data)
    
    def invalidate_user_cache(self, telegram_id: int) -> None:
        """Инвалидация кэша пользователя"""
        cache_key = f"user:{telegram_id}"
        self.user_cache.delete(cache_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики всех кэшей"""
        return {
            'location_cache': self.location_cache.stats(),
            'currency_cache': self.currency_cache.stats(),
            'market_cache': self.market_cache.stats(),
            'user_cache': self.user_cache.stats()
        }
    
    def clear_all(self) -> None:
        """Очистка всех кэшей"""
        self.location_cache.clear()
        self.currency_cache.clear()
        self.market_cache.clear()
        self.user_cache.clear()
        logger.info("Все кэши очищены")

# Глобальный экземпляр менеджера кэширования
cache_manager = CacheManager()
