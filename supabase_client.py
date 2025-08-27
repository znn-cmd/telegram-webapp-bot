"""
Модуль для создания и управления подключением к Supabase с улучшенной обработкой ошибок
"""

import os
import logging
import time
import ssl
from typing import Optional
from supabase import create_client, Client
from supabase.client import ClientOptions
import httpx
from dotenv import load_dotenv
from ssl_config import get_ssl_context

# Загружаем переменные окружения
load_dotenv()

logger = logging.getLogger(__name__)

class SupabaseConnection:
    """Класс для управления подключением к Supabase с обработкой ошибок и повторными попытками"""
    
    def __init__(self, max_retries: int = 3, timeout: int = 60):
        self.max_retries = max_retries
        self.timeout = timeout
        self.client: Optional[Client] = None
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise RuntimeError("SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы в переменных окружения!")
    
    def create_client_with_timeout(self) -> Client:
        """Создает клиент Supabase с настройками таймаута и SSL"""
        
        # Создаем httpx клиент с увеличенным таймаутом
        timeout_config = httpx.Timeout(
            connect=30.0,  # Таймаут на подключение
            read=30.0,     # Таймаут на чтение
            write=30.0,    # Таймаут на запись
            pool=30.0      # Таймаут пула соединений
        )
        
        # Используем оптимизированные настройки SSL
        ssl_context = get_ssl_context()
        
        # Создаем httpx клиент с настройками
        transport = httpx.HTTPTransport(
            retries=3,
            verify=ssl_context
        )
        
        httpx_client = httpx.Client(
            timeout=timeout_config,
            transport=transport,
            follow_redirects=True
        )
        
        # Опции клиента Supabase
        options = ClientOptions(
            postgrest_client_timeout=self.timeout,
            storage_client_timeout=self.timeout,
        )
        
        # Создаем клиент Supabase
        client = create_client(
            self.supabase_url,
            self.supabase_key,
            options=options
        )
        
        # Заменяем httpx клиент на наш настроенный
        if hasattr(client.postgrest, '_client'):
            client.postgrest._client = httpx_client
        if hasattr(client.auth, '_client'):
            client.auth._client = httpx_client
        
        return client
    
    def connect(self) -> Client:
        """Подключается к Supabase с повторными попытками при ошибках"""
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"🔄 Попытка подключения к Supabase ({attempt + 1}/{self.max_retries})...")
                
                self.client = self.create_client_with_timeout()
                
                # Тестовый запрос для проверки соединения
                test_response = self.client.table('users').select('id').limit(1).execute()
                
                logger.info("✅ Успешное подключение к Supabase")
                return self.client
                
            except ssl.SSLError as e:
                logger.error(f"❌ SSL ошибка при подключении (попытка {attempt + 1}): {e}")
                if "handshake operation timed out" in str(e):
                    logger.info("⏱️ Таймаут SSL handshake, увеличиваем время ожидания...")
                    self.timeout += 30  # Увеличиваем таймаут на 30 секунд
                
            except Exception as e:
                logger.error(f"❌ Ошибка при подключении к Supabase (попытка {attempt + 1}): {e}")
            
            if attempt < self.max_retries - 1:
                wait_time = (attempt + 1) * 5  # Прогрессивная задержка
                logger.info(f"⏳ Ожидание {wait_time} секунд перед повторной попыткой...")
                time.sleep(wait_time)
            else:
                logger.error("❌ Не удалось подключиться к Supabase после всех попыток")
                raise Exception("Не удалось установить соединение с Supabase")
    
    def get_client(self) -> Client:
        """Возвращает активный клиент или создает новый при необходимости"""
        if not self.client:
            return self.connect()
        return self.client
    
    def reconnect(self) -> Client:
        """Принудительно переподключается к Supabase"""
        logger.info("🔄 Переподключение к Supabase...")
        self.client = None
        return self.connect()

# Создаем глобальный экземпляр подключения
supabase_connection = SupabaseConnection(max_retries=5, timeout=90)

def get_supabase_client() -> Client:
    """Получить клиент Supabase с автоматическим переподключением при необходимости"""
    try:
        return supabase_connection.get_client()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при получении клиента Supabase: {e}")
        # Пытаемся переподключиться
        return supabase_connection.reconnect()

# Для обратной совместимости
def create_supabase_client() -> Client:
    """Создает новый клиент Supabase (для обратной совместимости)"""
    return get_supabase_client()