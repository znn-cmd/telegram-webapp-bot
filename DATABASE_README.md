# База данных системы недвижимости

Этот проект содержит полную схему базы данных для системы анализа недвижимости с поддержкой краткосрочной аренды, долгосрочной аренды и продаж.

## Структура файлов

- `database_schema.sql` - Основная схема базы данных с таблицами и индексами
- `database_functions.sql` - Полезные функции и процедуры для работы с данными

## Установка и настройка

### 1. Создание базы данных

```sql
-- Создайте новую базу данных
CREATE DATABASE real_estate_db;

-- Подключитесь к базе данных
\c real_estate_db;
```

### 2. Выполнение скриптов

```bash
# Выполните основной скрипт схемы
psql -d real_estate_db -f database_schema.sql

# Выполните скрипт с функциями
psql -d real_estate_db -f database_functions.sql
```

## Структура таблиц

### Основные таблицы

#### 1. Краткосрочная аренда (`short_term_rentals`)
- Объявления с Airbnb, Booking.com, VRBO
- Поля: адрес, координаты, цена за ночь, рейтинг, отзывы
- Индексы для быстрого поиска по локации, цене, рейтингу

#### 2. Долгосрочная аренда (`long_term_rentals`)
- Объявления долгосрочной аренды
- Поля: адрес, координаты, месячная аренда, площадь, этаж
- Индексы для поиска по району, цене, количеству комнат

#### 3. Продажи недвижимости (`property_sales`)
- Объявления продажи недвижимости
- Поля: адрес, координаты, цена продажи, цена за кв.м
- Индексы для анализа цен и локаций

### Исторические данные

#### 1. История краткосрочной аренды (`short_term_rental_history`)
- Ежедневные данные о ценах и занятости
- Связь с основной таблицей через `property_id`

#### 2. История долгосрочной аренды (`long_term_rental_history`)
- Ежемесячные данные об арендных ставках
- Отслеживание изменений цен

#### 3. История продаж (`property_sales_history`)
- Данные об изменении цен продажи
- Анализ трендов рынка

### Аналитические таблицы

#### Ежедневные метрики (`daily_district_metrics`)
- Агрегированные данные по районам
- Средние, медианные цены, количество объявлений
- Автоматическое обновление через процедуру

### Пользовательские данные

#### Пользователи (`users`)
- Данные пользователей Telegram бота
- Настройки языка и активности

#### Отчеты пользователей (`user_reports`)
- Сохраненные отчеты пользователей
- Параметры поиска и анализа

## Полезные функции

### 1. Расчет ROI

```sql
-- ROI краткосрочной аренды
SELECT calculate_short_term_roi(200000, 1500, 150, 75);

-- ROI долгосрочной аренды
SELECT calculate_long_term_roi(200000, 800, 2500);
```

### 2. Поиск недвижимости по радиусу

```sql
-- Найти все объекты в радиусе 5 км от центра
SELECT * FROM find_properties_in_radius(40.7128, -74.0060, 5.0);

-- Только краткосрочная аренда
SELECT * FROM find_properties_in_radius(40.7128, -74.0060, 5.0, 'short_term');
```

### 3. Статистика по району

```sql
-- Получить статистику по району
SELECT * FROM get_district_statistics('Downtown', 'New York');
```

### 4. История цен

```sql
-- История цен за последние 30 дней
SELECT * FROM get_price_history('property_123', 30);
```

### 5. Поиск похожих объектов

```sql
-- Найти похожие объекты
SELECT * FROM find_similar_properties(2, 100, 200, 'New York', 'Downtown', 'short_term');
```

### 6. Обновление метрик

```sql
-- Обновить ежедневные метрики
CALL update_daily_metrics(CURRENT_DATE);
```

## Представления (Views)

### 1. Активные объявления
- `active_short_term_rentals` - активные объявления краткосрочной аренды
- `active_long_term_rentals` - активные объявления долгосрочной аренды
- `active_property_sales` - активные объявления продаж

```sql
-- Получить все активные объявления краткосрочной аренды
SELECT * FROM active_short_term_rentals WHERE city = 'New York';
```

## Индексы

### Основные индексы
- Географические индексы для поиска по координатам
- Составные индексы для сложных запросов
- Полнотекстовые индексы для поиска по адресу и описанию
- Индексы для исторических данных

### Специальные индексы
- GIN индексы для массивов (amenities, photos)
- Частичные индексы для активных объявлений
- Геопространственные индексы для радиусного поиска

## Примеры запросов

### 1. Топ-10 самых дорогих объектов краткосрочной аренды

```sql
SELECT address, price_per_night, avg_rating, review_count
FROM active_short_term_rentals
WHERE city = 'New York'
ORDER BY price_per_night DESC
LIMIT 10;
```

### 2. Средние цены по районам

```sql
SELECT district, 
       AVG(price_per_night) as avg_price,
       COUNT(*) as listings_count
FROM active_short_term_rentals
WHERE city = 'New York'
GROUP BY district
ORDER BY avg_price DESC;
```

### 3. Объекты с высоким рейтингом и низкой ценой

```sql
SELECT address, price_per_night, avg_rating
FROM active_short_term_rentals
WHERE avg_rating >= 4.5 
  AND price_per_night <= 100
  AND review_count >= 10
ORDER BY avg_rating DESC, price_per_night ASC;
```

### 4. Анализ трендов цен

```sql
SELECT date, AVG(price_per_night) as avg_price
FROM short_term_rental_history
WHERE property_id IN (
    SELECT property_id FROM short_term_rentals WHERE city = 'New York'
)
GROUP BY date
ORDER BY date;
```

## Автоматизация

### Триггеры
- Автоматическое обновление `updated_at` при изменении записей
- Каскадное удаление исторических данных

### Процедуры
- `update_daily_metrics()` - обновление ежедневных метрик
- Можно настроить как cron job для автоматического выполнения

## Мониторинг и оптимизация

### Проверка производительности

```sql
-- Анализ использования индексов
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Размер таблиц
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Очистка старых данных

```sql
-- Удалить неактивные объявления старше 6 месяцев
DELETE FROM short_term_rentals 
WHERE is_active = false 
  AND updated_at < NOW() - INTERVAL '6 months';

-- Очистить исторические данные старше 2 лет
DELETE FROM short_term_rental_history 
WHERE date < CURRENT_DATE - INTERVAL '2 years';
```

## Безопасность

### Роли и права доступа

```sql
-- Создать роль только для чтения
CREATE ROLE readonly_user;
GRANT CONNECT ON DATABASE real_estate_db TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Создать роль для записи данных
CREATE ROLE write_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO write_user;
```

## Резервное копирование

```bash
# Создать резервную копию
pg_dump real_estate_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановить из резервной копии
psql real_estate_db < backup_20231201_143022.sql
```

## Интеграция с приложением

### Подключение из Python

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Подключение к базе данных
conn = psycopg2.connect(
    dbname="real_estate_db",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)

# Выполнение запроса
with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("SELECT * FROM get_district_statistics(%s, %s)", ('Downtown', 'New York'))
    results = cur.fetchall()
```

### Подключение из Supabase

```python
from supabase import create_client

supabase = create_client('your_supabase_url', 'your_supabase_key')

# Выполнение запроса
response = supabase.rpc('get_district_statistics', {
    'district_param': 'Downtown',
    'city_param': 'New York'
}).execute()
```

## Поддержка и обновления

### Добавление новых полей

```sql
-- Добавить новое поле в существующую таблицу
ALTER TABLE short_term_rentals 
ADD COLUMN new_field VARCHAR(100);

-- Создать индекс для нового поля
CREATE INDEX idx_short_term_rentals_new_field ON short_term_rentals(new_field);
```

### Миграции

Рекомендуется использовать инструменты миграций (например, Alembic для Python) для управления изменениями схемы базы данных.

## Заключение

Эта схема базы данных предоставляет полную основу для системы анализа недвижимости с поддержкой:

- Краткосрочной и долгосрочной аренды
- Продаж недвижимости
- Исторических данных и аналитики
- Геопространственного поиска
- Пользовательских отчетов
- Автоматических метрик

Все таблицы оптимизированы для быстрого поиска и анализа, а функции предоставляют готовые инструменты для работы с данными. 