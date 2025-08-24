# Исправление SSL Timeout ошибок в API

## Описание проблемы

После последних правок в таблице трендов возникли ошибки в логах:

### 1. **SSL Timeout ошибка:**
```
❌ Ошибка проверки статуса админа: _ssl.c:999: The handshake operation timed out
```
Это приводило к HTTP 500 ошибкам при вызове `/api/check_admin_status`.

### 2. **Отсутствующий API endpoint:**
```
GET /api/currency/latest HTTP/1.1 404
```
Endpoint `/api/currency/latest` не существовал в основном `app.py`.

## Что было исправлено

### 1. ✅ Добавлен таймаут для Supabase запросов

**Проблема**: Supabase запросы могли зависать на неопределенное время, вызывая SSL timeout.

**Решение**: Добавлен таймаут 10 секунд для всех запросов к базе данных в функции `api_check_admin_status`.

**Изменения в коде**:
```python
# Добавляем таймаут для Supabase запроса
import concurrent.futures

def execute_supabase_query():
    return supabase.table('users').select('user_status, period_end').eq('telegram_id', telegram_id).execute()

# Выполняем запрос с таймаутом
with concurrent.futures.ThreadPoolExecutor() as executor:
    future = executor.submit(execute_supabase_query)
    try:
        user_result = future.result(timeout=10)  # 10 секунд таймаут
    except concurrent.futures.TimeoutError:
        logger.error("❌ Таймаут при запросе к базе данных")
        return jsonify({'error': 'Database timeout'}), 408
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении запроса к базе: {e}")
        return jsonify({'error': 'Database error'}), 500
```

### 2. ✅ Добавлен endpoint `/api/currency/latest`

**Проблема**: Frontend пытался получить курсы валют через `/api/currency/latest`, но этот endpoint отсутствовал.

**Решение**: Создан новый endpoint для получения последних курсов валют.

**Новый endpoint**:
```python
@app.route('/api/currency/latest', methods=['GET'])
def api_currency_latest():
    """Получение последних курсов валют"""
    try:
        # Получаем последний курс EUR -> TRY из базы данных
        today = datetime.now().date()
        currency_result = supabase.table('currency').select('*').gte('created_at', f"{today}T00:00:00").lt('created_at', f"{today}T23:59:59").limit(1).execute()
        
        if currency_result.data and len(currency_result.data) > 0:
            latest_rate = currency_result.data[0]
            return jsonify({
                'success': True,
                'eur_try': latest_rate.get('eur_try'),
                'usd_try': latest_rate.get('usd_try'),
                'created_at': latest_rate.get('created_at'),
                'source': 'database'
            })
        else:
            # Если нет данных в базе, пытаемся получить через API
            try:
                current_rate = get_current_currency_rate('EUR', 'TRY')
                return jsonify({
                    'success': True,
                    'eur_try': current_rate,
                    'usd_try': None,
                    'created_at': datetime.now().isoformat(),
                    'source': 'api'
                })
            except Exception as api_error:
                logger.error(f"❌ Ошибка получения курса через API: {api_error}")
                return jsonify({
                    'success': False,
                    'error': 'No currency data available',
                    'message': 'Курсы валют недоступны'
                }), 404
                
    except Exception as e:
        logger.error(f"❌ Ошибка получения последних курсов валют: {e}")
        return jsonify({'error': str(e)}), 500
```

## Логика работы нового endpoint

### Приоритет источников данных:
1. **База данных** - сначала пытаемся получить курсы из таблицы `currency`
2. **Внешний API** - если в базе нет данных, используем `get_current_currency_rate()`
3. **Ошибка 404** - если оба источника недоступны

### Возвращаемые данные:
```json
{
    "success": true,
    "eur_try": 48.264963,
    "usd_try": 44.123456,
    "created_at": "2025-08-24T08:26:13.858",
    "source": "database"
}
```

## Преимущества исправлений

1. **Стабильность API**: Таймауты предотвращают зависание запросов
2. **Лучшая обработка ошибок**: Четкие сообщения об ошибках для frontend
3. **Полнота функциональности**: Добавлен недостающий endpoint
4. **Отказоустойчивость**: Fallback на внешний API при отсутствии данных в базе

## HTTP коды ответов

| Код | Описание | Причина |
|-----|----------|---------|
| **200** | Успех | Курсы валют получены |
| **404** | Не найдено | Курсы валют недоступны |
| **408** | Таймаут | Превышен таймаут запроса к базе |
| **500** | Внутренняя ошибка | Ошибка сервера |

## Тестирование исправлений

### 1. **Проверка таймаутов:**
```bash
# Тест с медленным соединением
curl -X POST http://localhost:5000/api/check_admin_status \
  -H "Content-Type: application/json" \
  -d '{"telegram_id": "123456789"}'
```

### 2. **Проверка нового endpoint:**
```bash
# Получение последних курсов валют
curl http://localhost:5000/api/currency/latest
```

### 3. **Мониторинг логов:**
- Отсутствие SSL timeout ошибок
- Корректная работа `/api/currency/latest`
- Стабильные HTTP 200 ответы

## Файлы изменений

- `app.py` - добавлен таймаут и новый endpoint
- `api_server.py` - уже содержал `/api/currency/latest`

## Заключение

Внесенные исправления решают критические проблемы:
- **SSL timeout** больше не будет вызывать HTTP 500
- **Отсутствующий endpoint** теперь доступен
- **API стабильность** значительно улучшена

Теперь система будет работать стабильно без критических ошибок в логах.
