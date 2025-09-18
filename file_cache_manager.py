"""
Модуль для управления кэшированием данных в локальных файлах
Простая и надежная альтернатива Redis для редкого обновления данных локаций
"""

import json
import os
import logging
from typing import Optional, List, Tuple, Any
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class FileCacheManager:
    """Менеджер кэширования для работы с локальными файлами"""
    
    def __init__(self, cache_dir: str = "cache"):
        """Инициализация файлового кеш-менеджера"""
        self.cache_dir = cache_dir
        self.lock = threading.Lock()
        
        # Создаем директорию кеша если её нет
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"📁 Создана директория кеша: {self.cache_dir}")
        
        logger.info(f"✅ Файловый кеш-менеджер инициализирован: {self.cache_dir}")
    
    def _get_cache_file_path(self, key: str) -> str:
        """Получение пути к файлу кеша"""
        # Заменяем недопустимые символы в имени файла
        safe_key = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def _is_cache_valid(self, cache_data: dict, ttl_hours: int) -> bool:
        """Проверка валидности кеша по времени"""
        if 'timestamp' not in cache_data:
            return False
        
        cache_time = datetime.fromisoformat(cache_data['timestamp'])
        expiry_time = cache_time + timedelta(hours=ttl_hours)
        
        return datetime.now() < expiry_time
    
    def get(self, key: str) -> Optional[Any]:
        """Получение данных из файлового кеша"""
        try:
            cache_file = self._get_cache_file_path(key)
            
            if not os.path.exists(cache_file):
                logger.debug(f"❌ Файл кеша не найден: {key}")
                return None
            
            with self.lock:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            
            # Проверяем валидность кеша
            if 'ttl_hours' in cache_data and not self._is_cache_valid(cache_data, cache_data['ttl_hours']):
                logger.debug(f"⏰ Кеш истек для ключа: {key}")
                self.delete(key)
                return None
            
            logger.debug(f"🎯 Файловый кеш HIT для ключа: {key}")
            return cache_data.get('data')
            
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файлового кеша {key}: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl_hours: int = 24) -> bool:
        """Сохранение данных в файловый кеш с TTL"""
        try:
            cache_file = self._get_cache_file_path(key)
            
            cache_data = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'ttl_hours': ttl_hours
            }
            
            with self.lock:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 Данные сохранены в файловый кеш: {key} (TTL: {ttl_hours}h)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения в файловый кеш {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Удаление файла кеша"""
        try:
            cache_file = self._get_cache_file_path(key)
            
            if os.path.exists(cache_file):
                with self.lock:
                    os.remove(cache_file)
                logger.debug(f"🗑️ Файл кеша удален: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка удаления файлового кеша {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Очистка кеша по паттерну (удаление файлов)"""
        try:
            deleted_count = 0
            
            with self.lock:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        # Преобразуем паттерн в имя файла
                        file_pattern = pattern.replace(":", "_").replace("/", "_").replace("\\", "_")
                        
                        if file_pattern in filename:
                            file_path = os.path.join(self.cache_dir, filename)
                            os.remove(file_path)
                            deleted_count += 1
            
            logger.info(f"🧹 Очищено {deleted_count} файлов кеша по паттерну: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки файлового кеша по паттерну {pattern}: {e}")
            return 0
    
    def clear_all(self) -> int:
        """Очистка всего кеша"""
        try:
            deleted_count = 0
            
            with self.lock:
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(self.cache_dir, filename)
                        os.remove(file_path)
                        deleted_count += 1
            
            logger.info(f"🧹 Очищено {deleted_count} файлов кеша")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка очистки всего файлового кеша: {e}")
            return 0
    
    # Специализированные методы для географических данных
    
    def get_countries(self) -> Optional[List[Tuple[int, str]]]:
        """Получение списка стран из файлового кеша"""
        return self.get("locations_countries")
    
    def set_countries(self, countries: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка стран в файловый кеш"""
        return self.set("locations_countries", countries, ttl_hours)
    
    def get_cities(self, country_id: int) -> Optional[List[Tuple[int, str]]]:
        """Получение списка городов по country_id из файлового кеша"""
        return self.get(f"locations_cities_{country_id}")
    
    def set_cities(self, country_id: int, cities: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка городов в файловый кеш"""
        return self.set(f"locations_cities_{country_id}", cities, ttl_hours)
    
    def get_counties(self, city_id: int) -> Optional[List[Tuple[int, str]]]:
        """Получение списка областей по city_id из файлового кеша"""
        return self.get(f"locations_counties_{city_id}")
    
    def set_counties(self, city_id: int, counties: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка областей в файловый кеш"""
        return self.set(f"locations_counties_{city_id}", counties, ttl_hours)
    
    def get_districts(self, county_id: int) -> Optional[List[Tuple[int, str]]]:
        """Получение списка районов по county_id из файлового кеша"""
        return self.get(f"locations_districts_{county_id}")
    
    def set_districts(self, county_id: int, districts: List[Tuple[int, str]], ttl_hours: int = 24) -> bool:
        """Сохранение списка районов в файловый кеш"""
        return self.set(f"locations_districts_{county_id}", districts, ttl_hours)
    
    def clear_locations_cache(self) -> int:
        """Очистка всего кеша географических данных"""
        return self.clear_pattern("locations_")
    
    def get_cache_stats(self) -> dict:
        """Получение статистики файлового кеша"""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            
            total_size = 0
            valid_files = 0
            expired_files = 0
            
            for filename in cache_files:
                file_path = os.path.join(self.cache_dir, filename)
                total_size += os.path.getsize(file_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if 'ttl_hours' in cache_data and self._is_cache_valid(cache_data, cache_data['ttl_hours']):
                        valid_files += 1
                    else:
                        expired_files += 1
                        
                except:
                    expired_files += 1
            
            return {
                "status": "available",
                "cache_dir": self.cache_dir,
                "total_files": len(cache_files),
                "valid_files": valid_files,
                "expired_files": expired_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Глобальный экземпляр файлового менеджера кеша
file_cache_manager = FileCacheManager()
