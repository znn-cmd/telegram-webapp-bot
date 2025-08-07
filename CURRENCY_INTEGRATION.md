# Интеграция функций валют в отчеты о недвижимости

## Обзор

Данная интеграция добавляет функциональность конвертации валют в отчеты о недвижимости. Когда адрес находится в Турции, все цены автоматически конвертируются в евро с использованием актуальных курсов валют.

## Файлы

### 1. `currency_functions.py`
Основной модуль с функциями для работы с валютами:

- `get_currency_rates()` - получает курсы валют из базы данных или API
- `fetch_and_save_currency_rates()` - получает курсы с currencylayer.com и сохраняет в БД
- `format_currency_rates_for_report()` - форматирует курсы для отображения в отчете
- `convert_to_euro()` - конвертирует значение в евро
- `convert_market_data_to_euro()` - конвертирует все данные рынка в евро

### 2. `test_currency.py`
Тестовый файл для проверки функций валют.

## Интеграция в основной код

### Шаг 1: Импорт функций
Добавить в начало `app.py`:

```python
from currency_functions import get_currency_rates, format_currency_rates_for_report, convert_market_data_to_euro
```

### Шаг 2: Модификация функции `format_simple_report`
Добавить в функцию `format_simple_report` после строки `# Формируем отчёт`:

```python
# Получаем курсы валют
currency_rates = get_currency_rates()
is_turkey = False

# Проверяем, находится ли адрес в Турции
if hasattr(format_simple_report, 'last_location_components'):
    components = format_simple_report.last_location_components
    if components and components.get('country_code') == 'TR':
        is_turkey = True
        logger.info("🇹🇷 Адрес находится в Турции, применяем конвертацию валют")

# Конвертируем данные рынка в евро, если это Турция
if is_turkey and market_data and currency_rates:
    logger.info("💱 Конвертируем данные рынка в евро")
    market_data = convert_market_data_to_euro(market_data, currency_rates)

# Добавляем информацию о дате формирования отчета и курсах валют
current_date = datetime.now().strftime("%d.%m.%Y")
report_lines.extend([
    f"📅 Дата формирования отчета: {current_date}",
    "",
])

# Добавляем информацию о курсах валют, если это Турция
if is_turkey and currency_rates:
    currency_info = format_currency_rates_for_report(currency_rates)
    report_lines.extend([
        f"💱 {currency_info}",
        "",
    ])
elif is_turkey and not currency_rates:
    report_lines.extend([
        "⚠️ Курсы валют недоступны, данные отображаются в местной валюте",
        "",
    ])
```

## Структура таблицы currency

Таблица `currency` в Supabase должна содержать следующие поля:

- `id` - уникальный идентификатор
- `created_at` - дата создания записи (формат ISO)
- `euro` - курс евро (всегда 1.0)
- `rub` - курс российского рубля к евро
- `usd` - курс доллара США к евро
- `try` - курс турецкой лиры к евро
- `aed` - курс дирхама ОАЭ к евро
- `thb` - курс тайского бата к евро

## API CurrencyLayer

Используется API ключ: `c61dddb55d93e77ce5a2c8b91fb22694`

### Запрос к API:
```
GET http://api.currencylayer.com/live
Parameters:
- access_key: API ключ
- source: EUR (базовая валюта)
- currencies: RUB,USD,TRY,AED,THB
```

### Пример ответа:
```json
{
  "success": true,
  "quotes": {
    "EURRUB": 91.265035,
    "EURUSD": 1.162261,
    "EURTRY": 46.897678,
    "EURAED": 4.26841,
    "EURTHB": 37.628259
  }
}
```

## Логика работы

1. **Определение страны**: Проверяется, находится ли адрес в Турции по коду страны `TR`
2. **Получение курсов**: Если адрес в Турции, получаются курсы валют из БД или API
3. **Конвертация данных**: Все цены в данных рынка конвертируются в евро
4. **Отображение информации**: В отчет добавляется дата формирования и курсы валют

## Конвертируемые поля

В данных рынка конвертируются следующие поля:
- `unit_price_for_sale` - цена продажи за м²
- `min_unit_price_for_sale` - минимальная цена продажи за м²
- `max_unit_price_for_sale` - максимальная цена продажи за м²
- `unit_price_for_rent` - цена аренды за м²
- `min_unit_price_for_rent` - минимальная цена аренды за м²
- `max_unit_price_for_rent` - максимальная цена аренды за м²
- `price_for_sale` - общая цена продажи
- `price_for_rent` - общая цена аренды

## Тестирование

Запустить тест:
```bash
python test_currency.py
```

## Пример отчета с конвертацией

```
Анализ рынка в радиусе 5 км:

📅 Дата формирования отчета: 19.01.2025

💱 Курсы валют (EUR): RUB: 91.2650 | USD: 1.1623 | TRY: 46.8977 | AED: 4.2684 | THB: 37.6283

=== ОБЩИЙ ТРЕНД ===

📊 ПРОДАЖА НЕДВИЖИМОСТИ
Средняя цена продажи, м²: €106.63
Минимальная цена продажи, м²: €85.31
Максимальная цена продажи: €127.96
...
```

## Обработка ошибок

- Если курсы валют недоступны, данные отображаются в местной валюте
- Если API недоступен, используется последняя сохраненная запись из БД
- Все ошибки логируются для отладки
