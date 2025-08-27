"""
Конфигурация SSL для решения проблем с handshake timeout
"""

import ssl
import certifi
import os

def get_ssl_context():
    """Создает SSL контекст с оптимизированными настройками"""
    
    # Создаем контекст с настройками
    context = ssl.create_default_context(cafile=certifi.where())
    
    # Отключаем проверку hostname для отладки (включить в продакшене!)
    # context.check_hostname = False
    
    # Устанавливаем протокол TLS
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    
    # Оптимизация для производительности
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1
    
    # Включаем сжатие (может помочь при медленном соединении)
    # context.options &= ~ssl.OP_NO_COMPRESSION
    
    return context

# Переменные окружения для отладки SSL
os.environ['PYTHONHTTPSVERIFY'] = '1'  # Включить проверку сертификатов

# Для отладки SSL проблем
# import logging
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('httpx').setLevel(logging.DEBUG)
# logging.getLogger('httpcore').setLevel(logging.DEBUG)