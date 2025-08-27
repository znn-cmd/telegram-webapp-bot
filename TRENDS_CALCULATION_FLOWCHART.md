# Схема расчета данных для таблицы трендов

```mermaid
flowchart TD
    Start[Запрос данных трендов] --> GetLocation[Получение выбранной локации]
    GetLocation --> APITrends[API: /api/property_trends]
    
    APITrends --> PropertyTrends[(property_trends<br/>таблица в БД)]
    PropertyTrends --> RawData[Сырые данные:<br/>- цены<br/>- проценты изменений<br/>- доходность]
    
    RawData --> PrepareData[prepareTrendsWithHistoricalPrices]
    
    PrepareData --> GetBasePrices[Получить базовые цены<br/>для текущего месяца]
    GetBasePrices --> APIBase[API: /api/base_prices]
    
    APIBase --> Tables[(4 таблицы:<br/>age_data<br/>floor_segment_data<br/>heating_data<br/>house_type_data)]
    
    Tables --> CalcBase[Расчет средних значений:<br/>base_sale = (avg_min + avg_max) / 2<br/>base_rent = (avg_min + avg_max) / 2]
    
    CalcBase --> CurrentMonth{Текущий<br/>месяц?}
    
    CurrentMonth -->|Да| UseBase[Использовать<br/>базовые цены]
    CurrentMonth -->|Нет| CheckPeriod{Исторический<br/>или будущий?}
    
    CheckPeriod -->|Исторический| CalcHistorical[Рекурсивный расчет:<br/>price = next_month / (1 + %)]
    CheckPeriod -->|Будущий| CalcFuture[Прогрессивный расчет:<br/>price = prev_month * (1 + %)]
    
    UseBase --> CachePrice[Сохранить в кэш]
    CalcHistorical --> CachePrice
    CalcFuture --> CachePrice
    
    CachePrice --> CheckAdmin{Проверка<br/>статуса админа}
    
    CheckAdmin -->|Обычный| FilterData[Фильтрация:<br/>-8 месяцев до +1 месяц]
    CheckAdmin -->|Админ| NoFilter[Все данные]
    
    FilterData --> SortData[Сортировка:<br/>новые даты сверху]
    NoFilter --> SortData
    
    SortData --> GenerateTable[generateTrendsTable:<br/>Формирование HTML таблицы]
    
    GenerateTable --> FormatData[Форматирование:<br/>- Даты: мес. год<br/>- Цены: с разделителями<br/>- Проценты: +/-]
    
    FormatData --> DisplayTable[Отображение таблицы]
    
    SortData --> InitChart[initializeTrendsChart:<br/>Инициализация графика]
    
    InitChart --> ChartFilter{Фильтр для графика}
    ChartFilter -->|Обычный| FromJan2021[Данные с января 2021]
    ChartFilter -->|Админ| AllChartData[Все данные]
    
    FromJan2021 --> CreateChart[Создание Chart.js графика]
    AllChartData --> CreateChart
    
    CreateChart --> DisplayChart[Отображение графика]
    
    SortData --> Analysis[generateTrendsAnalysis:<br/>Анализ последних 12 месяцев]
    Analysis --> DisplayAnalysis[Отображение анализа]
```

## Ключевые функции и их роль:

### 1. `getBasePricesFromTables()`
- Запрашивает данные из 4 таблиц характеристик недвижимости
- Вычисляет средние значения min/max цен
- Возвращает базовые цены для текущего месяца

### 2. `prepareTrendsWithHistoricalPrices()`
- Основная функция расчета цен
- Определяет тип месяца (текущий/исторический/будущий)
- Применяет соответствующую формулу расчета
- Кэширует результаты для оптимизации

### 3. `calculateHistoricalPrice()`
```javascript
// Для прошлых месяцев
price = next_month_price / (1 + percentage_change)
```

### 4. `calculateFuturePrice()`
```javascript
// Для будущих месяцев
price = previous_month_price * (1 + percentage_change)
```

### 5. `filterTrendsByDateRange()`
- Применяет ограничения видимости данных
- Для обычных пользователей: 10 месяцев
- Для админов: без ограничений

### 6. `generateTrendsTable()`
- Формирует HTML таблицы
- Применяет форматирование
- Выделяет текущий месяц цветом

### 7. `initializeTrendsChart()`
- Подготавливает данные для Chart.js
- Применяет дополнительные фильтры для графика
- Создает интерактивный линейный график