#!/usr/bin/env python3
"""
Тестовый скрипт для диагностики проблем с SSL подключением к Supabase
"""

import os
import sys
import logging
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.client import ClientOptions
import ssl
import socket

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

def test_basic_connection():
    """Тест базового подключения к Supabase"""
    logger.info("=" * 50)
    logger.info("Тест 1: Базовое подключение")
    logger.info("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL и SUPABASE_ANON_KEY должны быть заданы!")
        return False
    
    logger.info(f"URL: {supabase_url}")
    logger.info(f"Key: {supabase_key[:10]}...")
    
    try:
        # Извлекаем хост из URL
        from urllib.parse import urlparse
        parsed = urlparse(supabase_url)
        host = parsed.hostname
        port = parsed.port or 443
        
        logger.info(f"Проверяем подключение к {host}:{port}")
        
        # Тест TCP подключения
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            logger.info("✅ TCP подключение успешно")
        else:
            logger.error(f"❌ TCP подключение не удалось: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке подключения: {e}")
        return False
    
    return True

def test_ssl_connection():
    """Тест SSL подключения"""
    logger.info("=" * 50)
    logger.info("Тест 2: SSL подключение")
    logger.info("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(supabase_url)
        host = parsed.hostname
        port = parsed.port or 443
        
        # Создаем SSL контекст
        context = ssl.create_default_context()
        
        # Тестируем SSL handshake
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                logger.info(f"✅ SSL версия: {ssock.version()}")
                logger.info(f"✅ Шифр: {ssock.cipher()}")
                cert = ssock.getpeercert()
                logger.info(f"✅ Сертификат выдан для: {cert.get('subject')}")
                
    except ssl.SSLError as e:
        logger.error(f"❌ SSL ошибка: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Ошибка подключения: {e}")
        return False
    
    return True

def test_httpx_connection():
    """Тест подключения через httpx"""
    logger.info("=" * 50)
    logger.info("Тест 3: HTTPX подключение")
    logger.info("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    
    try:
        # Тест с разными настройками
        configs = [
            {"verify": True, "http2": True, "timeout": 30.0},
            {"verify": True, "http2": False, "timeout": 30.0},
            {"verify": False, "http2": True, "timeout": 30.0},
        ]
        
        for i, config in enumerate(configs, 1):
            logger.info(f"\nКонфигурация {i}: {config}")
            try:
                with httpx.Client(**config) as client:
                    response = client.get(f"{supabase_url}/rest/v1/")
                    logger.info(f"✅ Статус: {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка с конфигурацией {i}: {e}")
        
    except Exception as e:
        logger.error(f"❌ Общая ошибка HTTPX: {e}")
        return False
    
    return True

def test_supabase_client():
    """Тест создания Supabase клиента"""
    logger.info("=" * 50)
    logger.info("Тест 4: Supabase клиент")
    logger.info("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    # Попытка 1: С настройками по умолчанию
    logger.info("\nПопытка 1: Настройки по умолчанию")
    try:
        client = create_client(supabase_url, supabase_key)
        logger.info("✅ Клиент создан успешно")
        
        # Пробуем простой запрос
        result = client.table('users').select('telegram_id').limit(1).execute()
        logger.info(f"✅ Запрос выполнен, получено записей: {len(result.data) if result.data else 0}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
    
    # Попытка 2: С кастомными настройками
    logger.info("\nПопытка 2: Кастомные настройки")
    try:
        client_options = ClientOptions(
            timeout=60,
            httpx_client=httpx.Client(
                timeout=httpx.Timeout(60.0, connect=20.0),
                verify=True,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                http2=True,
            )
        )
        
        client = create_client(supabase_url, supabase_key, client_options)
        logger.info("✅ Клиент с кастомными настройками создан успешно")
        
        # Пробуем простой запрос
        result = client.table('users').select('telegram_id').limit(1).execute()
        logger.info(f"✅ Запрос выполнен, получено записей: {len(result.data) if result.data else 0}")
    except Exception as e:
        logger.error(f"❌ Ошибка с кастомными настройками: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

def main():
    """Основная функция"""
    logger.info("🚀 Запуск диагностики SSL подключения к Supabase")
    
    # Выполняем тесты
    tests = [
        test_basic_connection,
        test_ssl_connection,
        test_httpx_connection,
        test_supabase_client
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка в тесте {test.__name__}: {e}")
            results.append(False)
    
    # Итоги
    logger.info("\n" + "=" * 50)
    logger.info("ИТОГИ ТЕСТИРОВАНИЯ")
    logger.info("=" * 50)
    
    if all(results):
        logger.info("✅ Все тесты пройдены успешно!")
    else:
        logger.error("❌ Некоторые тесты не прошли")
        logger.info("\n🔧 Рекомендации:")
        logger.info("1. Проверьте правильность SUPABASE_URL и SUPABASE_ANON_KEY")
        logger.info("2. Убедитесь, что сервер имеет доступ к интернету")
        logger.info("3. Проверьте настройки файрвола/прокси")
        logger.info("4. Попробуйте временно отключить SSL проверку: export SUPABASE_SSL_VERIFY=false")
        logger.info("5. Обновите сертификаты системы: apt-get update && apt-get install ca-certificates")

if __name__ == "__main__":
    main()