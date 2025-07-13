# Тестовые данные для бота недвижимости

Этот набор файлов содержит тестовые данные для города Анталия в Турции, которые можно использовать для тестирования функциональности бота недвижимости.

## Содержимое файлов

### 1. CSV файлы с данными

- **`test_data_short_term_rentals_full.csv`** - 45 записей краткосрочной аренды (Airbnb, Booking.com, VRBO)
- **`test_data_long_term_rentals.csv`** - 30 записей долгосрочной аренды (Sahibinden)
- **`test_data_property_sales.csv`** - 35 записей продажи недвижимости (Sahibinden)
- **`test_data_historical_prices.csv`** - 150+ исторических записей цен для анализа ROI
- **`test_data_market_statistics.csv`** - 56 записей рыночной статистики по районам

### 2. Скрипт загрузки

- **`load_test_data.py`** - Python скрипт для автоматической загрузки всех данных в базу данных

## Структура данных

### Краткосрочная аренда
- Источники: Airbnb, Booking.com, VRBO
- Районы: Kaleiçi, Lara, Konyaaltı, Muratpaşa, Kepez, Döşemealtı, Aksu
- Цены: $65-$450 за ночь
- Рейтинги: 4.4-4.9
- Количество спален: 1-6

### Долгосрочная аренда
- Источник: Sahibinden
- Районы: те же
- Цены: 2,500-15,000 TRY в месяц
- Площадь: 40-220 кв.м
- Депозит: 5,000-30,000 TRY

### Продажа недвижимости
- Источник: Sahibinden
- Цены: 700,000-6,000,000 TRY
- Цена за кв.м: 14,000-21,000 TRY
- Возраст: 1-12 лет

### Исторические цены
- Период: 2020-2024
- Типы: продажа, аренда, краткосрочная аренда
- Валюты: TRY, USD

### Рыночная статистика
- Данные по районам
- Средние цены
- Изменения цен (1, 3, 5 лет)
- Доходность от аренды
- Загрузка краткосрочной аренды

## Инструкции по загрузке

### Предварительные требования

1. Установите PostgreSQL
2. Создайте базу данных `real_estate_bot`
3. Выполните SQL скрипты:
   - `database_schema_safe.sql`
   - `database_functions_safe.sql`

### Настройка переменных окружения

Создайте файл `.env` или установите переменные окружения:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=real_estate_bot
export DB_USER=postgres
export DB_PASSWORD=your_password
```

### Загрузка данных

1. Установите зависимости:
```bash
pip install psycopg2-binary
```

2. Запустите скрипт загрузки:
```bash
python load_test_data.py
```

### Ручная загрузка через psql

Если предпочитаете загружать данные вручную:

```bash
# Краткосрочная аренда
psql -d real_estate_bot -c "\COPY short_term_rentals FROM 'test_data_short_term_rentals_full.csv' WITH CSV HEADER;"

# Долгосрочная аренда
psql -d real_estate_bot -c "\COPY long_term_rentals FROM 'test_data_long_term_rentals.csv' WITH CSV HEADER;"

# Продажа недвижимости
psql -d real_estate_bot -c "\COPY property_sales FROM 'test_data_property_sales.csv' WITH CSV HEADER;"

# Исторические цены
psql -d real_estate_bot -c "\COPY historical_prices FROM 'test_data_historical_prices.csv' WITH CSV HEADER;"

# Рыночная статистика
psql -d real_estate_bot -c "\COPY market_statistics FROM 'test_data_market_statistics.csv' WITH CSV HEADER;"
```

## Проверка загрузки

После загрузки данных можно проверить их наличие:

```sql
-- Проверка количества записей
SELECT 
    'short_term_rentals' as table_name, COUNT(*) as count FROM short_term_rentals
UNION ALL
SELECT 'long_term_rentals', COUNT(*) FROM long_term_rentals
UNION ALL
SELECT 'property_sales', COUNT(*) FROM property_sales
UNION ALL
SELECT 'historical_prices', COUNT(*) FROM historical_prices
UNION ALL
SELECT 'market_statistics', COUNT(*) FROM market_statistics;

-- Проверка данных по районам
SELECT district, COUNT(*) as count 
FROM short_term_rentals 
GROUP BY district 
ORDER BY count DESC;

-- Проверка цен
SELECT 
    district,
    AVG(price_per_night) as avg_price,
    MIN(price_per_night) as min_price,
    MAX(price_per_night) as max_price
FROM short_term_rentals 
GROUP BY district 
ORDER BY avg_price DESC;
```

## Особенности данных

### Географическое распределение
- **Kaleiçi**: Исторический центр, старые здания, высокие цены
- **Lara**: Пляжный район, новые здания, премиум цены
- **Konyaaltı**: Пляжный район, средние цены
- **Muratpaşa**: Центр города, доступные цены
- **Kepez**: Жилой район, семейные квартиры
- **Döşemealtı**: Загородные виллы, высокие цены
- **Aksu**: Смешанный район, средние цены

### Тренды цен
- Рост цен на 10-18% в год
- Более высокий рост в премиум сегменте
- Стабильный рост доходности от аренды

### Качество данных
- Реалистичные координаты
- Разнообразные аменities
- Правдоподобные рейтинги и отзывы
- Корректные связи между таблицами

## Использование в боте

Эти данные можно использовать для тестирования:

1. **Поиск недвижимости** - фильтрация по району, цене, количеству спален
2. **Анализ ROI** - расчет доходности на основе исторических данных
3. **Рыночная статистика** - отображение трендов по районам
4. **Похожие объекты** - поиск аналогичных предложений
5. **Калькулятор инвестиций** - оценка потенциальной доходности

## Обновление данных

Для обновления данных можно:

1. Изменить CSV файлы
2. Запустить скрипт загрузки повторно (он использует ON CONFLICT для обновления)
3. Или очистить таблицы и загрузить заново:

```sql
TRUNCATE TABLE short_term_rentals, long_term_rentals, property_sales, historical_prices, market_statistics;
```

## Поддержка

При возникновении проблем:

1. Проверьте подключение к базе данных
2. Убедитесь, что таблицы созданы
3. Проверьте права доступа пользователя
4. Проверьте формат CSV файлов (UTF-8, запятые как разделители) 