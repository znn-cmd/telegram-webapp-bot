# 📊 Настройка базы данных для экономических данных IMF

## 🎯 Обзор

Этот набор SQL скриптов создает и настраивает таблицу `imf_economic_data` для хранения экономических данных IMF с поддержкой интерпретаций и кэширования.

## 📁 Файлы

### 1. `create_imf_economic_data_table.sql`
**Полное создание таблицы с нуля**
- Создает таблицу со всеми необходимыми полями
- Добавляет индексы для оптимизации
- Создает триггеры для автоматического обновления
- Добавляет пример данных для тестирования

### 2. `add_interpretation_fields.sql`
**Добавление полей к существующей таблице**
- Добавляет поля интерпретаций к существующей таблице
- Безопасно работает с `IF NOT EXISTS`
- Добавляет комментарии к новым полям

## 🚀 Инструкции по использованию

### Вариант 1: Создание новой таблицы

1. **Откройте Supabase Dashboard**
2. **Перейдите в SQL Editor**
3. **Скопируйте содержимое `create_imf_economic_data_table.sql`**
4. **Выполните скрипт**

```sql
-- Выполните весь скрипт create_imf_economic_data_table.sql
```

### Вариант 2: Добавление полей к существующей таблице

1. **Откройте Supabase Dashboard**
2. **Перейдите в SQL Editor**
3. **Скопируйте содержимое `add_interpretation_fields.sql`**
4. **Выполните скрипт**

```sql
-- Выполните весь скрипт add_interpretation_fields.sql
```

## 📋 Структура таблицы

### Основные поля
```sql
id SERIAL PRIMARY KEY
country_code VARCHAR(10) NOT NULL
country_name VARCHAR(255) NOT NULL
indicator_code VARCHAR(50) NOT NULL
indicator_name VARCHAR(255) NOT NULL
year INTEGER NOT NULL
value DECIMAL(10,4) NOT NULL
```

### Поля интерпретаций ВВП
```sql
gdp_trend_interpretation_en TEXT
gdp_trend_interpretation_ru TEXT
gdp_trend_interpretation_tr TEXT
gdp_trend_interpretation_fr TEXT
gdp_trend_interpretation_de TEXT
```

### Поля интерпретаций инфляции
```sql
inflation_trend_interpretation_en TEXT
inflation_trend_interpretation_ru TEXT
inflation_trend_interpretation_tr TEXT
inflation_trend_interpretation_fr TEXT
inflation_trend_interpretation_de TEXT
```

### Поля интерпретаций сравнения
```sql
recent_comparison_interpretation_en TEXT
recent_comparison_interpretation_ru TEXT
recent_comparison_interpretation_tr TEXT
recent_comparison_interpretation_fr TEXT
recent_comparison_interpretation_de TEXT
```

### Поля детальных расчетов
```sql
gdp_calculation_details TEXT
inflation_calculation_details TEXT
```

## 🔍 Проверка установки

После выполнения скрипта проверьте:

```sql
-- Проверка структуры таблицы
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'imf_economic_data' 
ORDER BY ordinal_position;

-- Проверка данных
SELECT COUNT(*) as total_records FROM imf_economic_data;

-- Проверка индексов
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'imf_economic_data';
```

## 📊 Примеры данных

Таблица содержит примеры данных для Турции:

### ВВП (NGDP_RPCH)
- 2019: 0.8%
- 2020: 1.9%
- 2021: 11.4%
- 2022: 5.5%
- 2023: 5.1%
- 2024: 3.2%
- 2025: 2.7%

### Инфляция (PCPIPCH)
- 2019: 15.2%
- 2020: 12.3%
- 2021: 19.6%
- 2022: 72.3%
- 2023: 53.9%
- 2024: 58.5%
- 2025: 35.9%

## 🔧 Индексы и оптимизация

Создаются следующие индексы:
- `idx_imf_economic_data_country_code` - для поиска по стране
- `idx_imf_economic_data_indicator_code` - для поиска по индикатору
- `idx_imf_economic_data_year` - для поиска по году
- `idx_imf_economic_data_country_indicator` - составной индекс
- `idx_imf_economic_data_country_year` - составной индекс
- `idx_imf_economic_data_unique` - уникальный индекс

## 🚨 Важные замечания

1. **Уникальность данных**: Каждая комбинация `(country_code, indicator_code, year)` должна быть уникальной
2. **Временные метки**: Поля `created_at` и `updated_at` обновляются автоматически
3. **JSON данные**: Поля расчетов хранят JSON строки
4. **Многоязычность**: Поддерживаются 5 языков: en, ru, tr, fr, de

## 🔄 Обновление данных

Для обновления интерпретаций используйте:

```sql
UPDATE imf_economic_data 
SET 
    gdp_trend_interpretation_ru = 'Новая интерпретация ВВП',
    inflation_trend_interpretation_ru = 'Новая интерпретация инфляции',
    gdp_calculation_details = '{"calculations": [...]}',
    updated_at = CURRENT_TIMESTAMP
WHERE country_code = 'TUR' AND indicator_code = 'NGDP_RPCH';
```

## ✅ Проверка готовности

После выполнения скрипта система должна:
- ✅ Сохранять интерпретации в базу данных
- ✅ Загружать кэшированные интерпретации
- ✅ Поддерживать все 5 языков
- ✅ Работать с детальными расчетами

---

**Статус**: ✅ **Готово к использованию**

Все скрипты протестированы и готовы для выполнения в Supabase. 