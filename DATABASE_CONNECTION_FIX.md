# Исправление проблемы подключения к базе данных

## Проблема
После внесения изменений в локализацию приложение стало испытывать проблемы с подключением к Supabase:
- SSL handshake timeout ошибки
- Ошибка в параметрах `ClientOptions`
- Долгие таймауты при подключении

## Анализ логов
```
2025-09-09 12:06:32,793 - Database timeout on attempt 1/5: _ssl.c:999: The handshake operation timed out
2025-09-09 12:09:13,151 - ERROR - ClientOptions.__init__() got an unexpected keyword argument 'edge_function_client_timeout'
```

## Причины проблем
1. **SSL Handshake Timeout**: Сетевые задержки при установке SSL соединения с Supabase
2. **Неверные параметры ClientOptions**: Параметр `edge_function_client_timeout` не существует в текущей версии Supabase Python SDK
3. **Неиспользуемый HTTP клиент**: Создавался кастомный httpx клиент, но не передавался в Supabase

## Исправления

### 1. Упрощение инициализации Supabase
```python
# ДО (проблемное)
options = ClientOptions(
    postgrest_client_timeout=120,
    storage_client_timeout=120,
    edge_function_client_timeout=120  # ❌ Этот параметр не существует
)
supabase: Client = create_client(supabase_url, supabase_key, options=options)

# ПОСЛЕ (исправленное)
supabase: Client = create_client(supabase_url, supabase_key)
```

### 2. Улучшение обработки SSL таймаутов
```python
except (TimeoutException, ConnectTimeout, ConnectionError, OSError) as e:
    error_msg = str(e)
    if "handshake operation timed out" in error_msg or "timed out" in error_msg:
        logger.warning(f"SSL/Network timeout on attempt {attempt + 1}/{max_retries}: {error_msg}")
    else:
        logger.warning(f"Database connection error on attempt {attempt + 1}/{max_retries}: {error_msg}")
```

### 3. Удаление неиспользуемого HTTP клиента
Убран неиспользуемый `httpx.Client`, оставлены только необходимые импорты для обработки исключений.

## Результат
- ✅ Приложение успешно запускается без ошибок
- ✅ SSL таймауты обрабатываются корректно с retry логикой
- ✅ Подключение к базе устанавливается после нескольких попыток
- ✅ Локализация работает корректно

## Рекомендации
1. **Мониторинг SSL таймаутов**: Если проблемы с SSL handshake продолжаются, стоит проверить сетевое окружение
2. **Версии библиотек**: При обновлении Supabase SDK проверять актуальные параметры ClientOptions
3. **Retry логика**: Текущая настройка (5 попыток с задержкой 5 сек) показывает хорошие результаты

## Статус
🟢 **ИСПРАВЛЕНО** - База данных работает стабильно, все функции локализации работают корректно.
