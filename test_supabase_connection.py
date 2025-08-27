#!/usr/bin/env python3
"""
Диагностический скрипт для проверки подключения к Supabase
"""

import os
import sys
import time
import logging
import ssl
import socket
from urllib.parse import urlparse
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

def test_network_connectivity():
    """Тестирует базовую сетевую связность"""
    print("\n🔍 ТЕСТ 1: Проверка сетевой связности")
    print("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        print("❌ SUPABASE_URL не найден в переменных окружения")
        return False
    
    # Извлекаем хост из URL
    parsed_url = urlparse(supabase_url)
    host = parsed_url.hostname
    port = 443  # HTTPS порт
    
    print(f"📡 Проверка подключения к {host}:{port}")
    
    try:
        # Пытаемся установить TCP соединение
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ TCP соединение с {host}:{port} установлено успешно")
            return True
        else:
            print(f"❌ Не удалось установить TCP соединение с {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ Ошибка при проверке сетевой связности: {e}")
        return False

def test_ssl_handshake():
    """Тестирует SSL handshake"""
    print("\n🔐 ТЕСТ 2: Проверка SSL handshake")
    print("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    parsed_url = urlparse(supabase_url)
    host = parsed_url.hostname
    port = 443
    
    print(f"🔒 Попытка SSL handshake с {host}:{port}")
    
    # Тест с разными таймаутами
    timeouts = [5, 10, 30, 60]
    
    for timeout in timeouts:
        print(f"\n⏱️  Попытка с таймаутом {timeout} секунд...")
        
        try:
            # Создаем SSL контекст
            context = ssl.create_default_context()
            
            # Создаем сокет
            with socket.create_connection((host, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    print(f"✅ SSL handshake успешен с таймаутом {timeout}с")
                    print(f"   Протокол: {ssock.version()}")
                    print(f"   Шифр: {ssock.cipher()}")
                    return True
                    
        except socket.timeout:
            print(f"⏱️  Таймаут при попытке с {timeout}с")
        except ssl.SSLError as e:
            print(f"❌ SSL ошибка: {e}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    return False

def test_supabase_client():
    """Тестирует подключение через Supabase клиент"""
    print("\n🔧 ТЕСТ 3: Проверка Supabase клиента")
    print("=" * 50)
    
    try:
        from supabase_client import get_supabase_client
        
        print("📡 Создание клиента Supabase...")
        client = get_supabase_client()
        
        print("📊 Выполнение тестового запроса...")
        # Простой запрос для проверки
        result = client.table('users').select('id').limit(1).execute()
        
        print("✅ Supabase клиент работает успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Supabase клиента: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dns_resolution():
    """Тестирует DNS разрешение"""
    print("\n🌐 ТЕСТ 4: Проверка DNS")
    print("=" * 50)
    
    supabase_url = os.getenv("SUPABASE_URL")
    parsed_url = urlparse(supabase_url)
    host = parsed_url.hostname
    
    try:
        ip_address = socket.gethostbyname(host)
        print(f"✅ DNS разрешение успешно: {host} -> {ip_address}")
        
        # Проверяем обратное разрешение
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            print(f"✅ Обратное DNS разрешение: {ip_address} -> {hostname}")
        except:
            print(f"⚠️  Обратное DNS разрешение недоступно для {ip_address}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка DNS разрешения: {e}")
        return False

def main():
    """Основная функция диагностики"""
    print("🚀 ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ К SUPABASE")
    print("=" * 70)
    
    # Проверяем переменные окружения
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"📋 SUPABASE_URL: {'✅ Установлен' if supabase_url else '❌ Не установлен'}")
    print(f"📋 SUPABASE_ANON_KEY: {'✅ Установлен' if supabase_key else '❌ Не установлен'}")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Необходимые переменные окружения не установлены!")
        return
    
    # Выполняем тесты
    tests = [
        ("DNS разрешение", test_dns_resolution),
        ("Сетевая связность", test_network_connectivity),
        ("SSL Handshake", test_ssl_handshake),
        ("Supabase клиент", test_supabase_client)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 70)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 70)
    
    for test_name, success in results:
        status = "✅ УСПЕШНО" if success else "❌ ОШИБКА"
        print(f"{test_name}: {status}")
    
    # Рекомендации
    failed_tests = [name for name, success in results if not success]
    if failed_tests:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        
        if "DNS разрешение" in failed_tests:
            print("- Проверьте настройки DNS")
            print("- Попробуйте использовать публичные DNS серверы (8.8.8.8, 1.1.1.1)")
        
        if "Сетевая связность" in failed_tests:
            print("- Проверьте интернет-соединение")
            print("- Проверьте настройки файрвола/прокси")
            print("- Убедитесь, что порт 443 не заблокирован")
        
        if "SSL Handshake" in failed_tests:
            print("- Попробуйте увеличить таймауты")
            print("- Проверьте системное время")
            print("- Обновите сертификаты: pip install --upgrade certifi")
        
        if "Supabase клиент" in failed_tests:
            print("- Проверьте правильность SUPABASE_URL и SUPABASE_ANON_KEY")
            print("- Попробуйте переустановить supabase-py: pip install --upgrade supabase")

if __name__ == "__main__":
    main()