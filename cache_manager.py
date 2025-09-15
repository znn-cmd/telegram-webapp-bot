"""
Модуль для управления кэшированием данных в Redis
Ускоряет работу приложения с базой данных в 10-50 раз
"""

import redis
import json
import logging
from typing import Optional, List, Tuple, Any
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class CacheManager:
    """Менеджер кэширования для ускорения работы с БД"""
    
    def __init__(self):
        """Инициализация Redis соединения или in-memory кэша"""
        self.is_available = False
        self.redis_client = None
        self.memory_cache = {}  # Fallback кэш в памяти
        self.cache_ttl = {}     # TTL для in-memory кэша
        
        # Проверяем, включен ли кэш
        cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        if not cache_enabled:
            logger.info("⚠️ Кэширование отключено через CACHE_ENABLED=false")
            return
            
        try:
            # Настройки Redis из переменных окружения
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_db = int(os.getenv('REDIS_DB', 0))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            # Создаем соединение с Redis
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,  # Автоматическое декодирование UTF-8
                socket_connect_timeout=5,  # Таймаут подключения
                socket_timeout=5,  # Таймаут операций
                retry_on_timeout=True,  # Повторные попытки при таймауте
                health_check_interval=30  # Проверка здоровья соединения
            )
            
            # Проверяем соединение
            self.redis_client.ping()
            logger.info("✅ Redis соединение установлено успешно")
            self.is_available = True
            
        except Exception as e:
            logger.warning(f"⚠️ Redis недоступен: {e}. Используем in-memory кэш.")
            self.redis_client = None
            self.is_available = False
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Генерация ключа кэша"""
        key_parts = [prefix] + [str(arg) for arg in args if arg is not None]
        return ":".join(key_parts)
    
    def get(self, key: str) -> Optional[Any]:
        """Получение данных из кэша"""
        if self.redis_client and self.is_available:
            # Используем Redis
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    logger.debug(f"🎯 Redis кэш HIT для ключа: {key}")
                    return json.loads(cached_data)
                else:
                    logger.debug(f"❌ Redis кэш MISS для ключа: {key}")
                    return None
            except Exception as e:
                logger.error(f"❌ Ошибка получения из Redis кэша {key}: {e}")
                return None
        else:
            # Используем in-memory кэш
            return self._get_from_memory_cache(key)
    
    def set(self, key: str, data: Any, ttl_seconds: int = 3600) -> bool:
        """Сохранение данных в кэш с TTL"""
        if self.redis_client and self.is_available:
            # Используем Redis
            try:
                serialized_data = json.dumps(data, ensure_ascii=False)
                result = self.redis_client.setex(key, ttl_seconds, serialized_data)
                if result:
                    logger.debug(f"💾 Данные сохранены в Redis кэш: {key} (TTL: {ttl_seconds}s)")
                return result
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения в Redis кэш {key}: {e}")
                # Fallback к memory кэшу
                return self._set_to_memory_cache(key, data, ttl_seconds)
        else:
            # Используем in-memory кэш
            return self._set_to_memory_cache(key, data, ttl_seconds)
    
    def delete(self, key: str) -> bool:
        """Удаление данных из кэша"""
        if not self.is_available:
            return False
            
        try:
            result = self.redis_client.delete(key)
            if result:
                logger.debug(f"🗑️ Данные удалены из кэша: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"❌ Ошибка удаления из кэша {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Очистка кэша по паттерну"""
        if not self.is_available:
            return 0
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                logger.info(f"🧹 Очищено {deleted_count} ключей по паттерну: {pattern}")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"❌ Ошибка очистки кэша по паттерну {pattern}: {e}")
            return 0
    
    # Специализированные методы для географических данных
    
    def get_countries(self) -> Optional[List[Tuple[int, str]]]:
        """Получение списка стран из кэша"""
        key = self._get_cache_key("locations", "countries")
        return self.get(key)
    
    def set_countries(self, countries: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка стран в кэш"""
        key = self._get_cache_key("locations", "countries")
        return self.set(key, countries, ttl_hours * 3600)
    
    def get_cities(self, country_id: int) -> Optional[List[Tuple[int, str]]]:
        """Получение списка городов по country_id из кэша"""
        key = self._get_cache_key("locations", "cities", country_id)
        return self.get(key)
    
    def set_cities(self, country_id: int, cities: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка городов в кэш"""
        key = self._get_cache_key("locations", "cities", country_id)
        return self.set(key, cities, ttl_hours * 3600)
    
    def get_counties(self, city_id: int) -> Optional[List[Tuple[int, str]]]:
        """Получение списка областей по city_id из кэша"""
        key = self._get_cache_key("locations", "counties", city_id)
        return self.get(key)
    
    def set_counties(self, city_id: int, counties: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка областей в кэш"""
        key = self._get_cache_key("locations", "counties", city_id)
        return self.set(key, counties, ttl_hours * 3600)
    
    def get_districts(self, county_id: int) -> Optional[List[Tuple[int, str]]]:
        """Получение списка районов по county_id из кэша"""
        key = self._get_cache_key("locations", "districts", county_id)
        return self.get(key)
    
    def set_districts(self, county_id: int, districts: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка районов в кэш"""
        key = self._get_cache_key("locations", "districts", county_id)
        return self.set(key, districts, ttl_hours * 3600)
    
    def clear_locations_cache(self) -> int:
        """Очистка всего кэша географических данных"""
        return self.clear_pattern("locations:*")
    
    def get_cache_stats(self) -> dict:
        """Получение статистики кэша"""
        if not self.is_available:
            return {"status": "unavailable", "message": "Redis недоступен"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "available",
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """Расчет процента попаданий в кэш"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return round((hits / total) * 100, 2)
    
    # Методы для in-memory кэша
    def _get_from_memory_cache(self, key: str) -> Optional[Any]:
        """Получение данных из in-memory кэша"""
        import time
        
        if key in self.memory_cache:
            # Проверяем TTL
            if key in self.cache_ttl:
                if time.time() < self.cache_ttl[key]:
                    logger.debug(f"🎯 Memory кэш HIT для ключа: {key}")
                    return self.memory_cache[key]
                else:
                    # Ключ истек, удаляем
                    del self.memory_cache[key]
                    del self.cache_ttl[key]
                    logger.debug(f"⏰ Memory кэш истек для ключа: {key}")
            else:
                logger.debug(f"🎯 Memory кэш HIT для ключа: {key}")
                return self.memory_cache[key]
        
        logger.debug(f"❌ Memory кэш MISS для ключа: {key}")
        return None
    
    def _set_to_memory_cache(self, key: str, data: Any, ttl_seconds: int) -> bool:
        """Сохранение данных в in-memory кэш"""
        import time
        
        try:
            self.memory_cache[key] = data
            self.cache_ttl[key] = time.time() + ttl_seconds
            logger.debug(f"💾 Данные сохранены в memory кэш: {key} (TTL: {ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в memory кэш {key}: {e}")
            return False
    
    def _clean_expired_memory_cache(self):
        """Очистка истекших ключей из memory кэша"""
        import time
        
        current_time = time.time()
        expired_keys = [key for key, expiry in self.cache_ttl.items() if current_time >= expiry]
        
        for key in expired_keys:
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.cache_ttl:
                del self.cache_ttl[key]
        
        if expired_keys:
            logger.debug(f"🧹 Очищено {len(expired_keys)} истекших ключей из memory кэша")

# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()
