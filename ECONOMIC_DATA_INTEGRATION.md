# Интеграция экономических данных в отчеты Aaadviser

## 📊 Обзор

Добавлена функциональность для получения реальных экономических данных из таблицы `imf_economic_data` в Supabase и их интеграции в полные отчеты по недвижимости.

## 🔧 Реализованные функции

### 1. `get_economic_data(country_code='TUR', years_back=10)`

**Назначение:** Получение экономических данных из базы данных

**Параметры:**
- `country_code` (str): Код страны (по умолчанию 'TUR' для Турции)
- `years_back` (int): Количество лет назад для получения данных

**Возвращает:**
```python
{
    'gdp_data': [
        {
            'year': 2023,
            'value': 4.1,              # Рост ВВП в процентах
            'indicator_code': 'NGDP_RPCH',
            'indicator_name': 'Real GDP growth (Annual percent change)'
        }
    ],
    'inflation_data': [
        {
            'year': 2023,
            'value': 64.8,             # Уровень инфляции в процентах
            'indicator_code': 'PCPIPCH',
            'indicator_name': 'Inflation rate, average consumer prices'
        }
    ],
    'country_code': 'TUR',
    'country_name': 'Turkey',
    'gdp_trend': 0.041,               # Тренд ВВП
    'inflation_trend': 0.15,          # Тренд инфляции
    'latest_gdp': {...},              # Последние данные ВВП
    'latest_inflation': {...},        # Последние данные инфляции
    'data_years': '2014-2024'
}
```

### 2. `calculate_trend(values)`

**Назначение:** Вычисление тренда для ряда значений

**Параметры:**
- `values` (list): Список числовых значений

**Возвращает:**
- `float`: Коэффициент тренда (положительный = рост, отрицательный = падение)

### 3. `create_economic_chart_data(economic_data)`

**Назначение:** Создание данных для построения графиков

**Параметры:**
- `economic_data` (dict): Данные из `get_economic_data()`

**Возвращает:**
```python
{
    'gdp_chart': {
        'labels': ['2014', '2015', ...],
        'datasets': [{
            'label': 'Рост ВВП (%) - Turkey',
            'data': [4.1, 5.6, ...],
            'borderColor': '#667eea',
            'backgroundColor': 'rgba(102, 126, 234, 0.1)',
            'tension': 0.4,
            'fill': False
        }]
    },
    'inflation_chart': {
        'labels': ['2014', '2015', ...],
        'datasets': [{
            'label': 'Инфляция (%) - Turkey',
            'data': [64.8, 72.3, ...],
            'borderColor': '#dc3545',
            'backgroundColor': 'rgba(220, 53, 69, 0.1)',
            'tension': 0.4,
            'fill': False
        }]
    },
    'trends': {
        'gdp_trend': 0.041,
        'inflation_trend': 0.15
    },
    'latest': {
        'gdp': {...},
        'inflation': {...}
    },
    'country_name': 'Turkey',
    'country_code': 'TUR'
}
```

## 🔌 API Endpoints

### `/api/economic_data` (POST)

**Назначение:** Получение экономических данных для построения графиков

**Параметры запроса:**
```json
{
    "country_code": "TUR",
    "years_back": 10
}
```

**Ответ:**
```json
{
    "success": true,
    "economic_data": {
        "gdp_data": [...],
        "inflation_data": [...],
        "country_code": "TUR",
        "country_name": "Turkey",
        "gdp_trend": 0.041,
        "inflation_trend": 0.15,
        "latest_gdp": {...},
        "latest_inflation": {...},
        "data_years": "2014-2024"
    },
    "chart_data": {
        "gdp_chart": {...},
        "inflation_chart": {...},
        "trends": {...},
        "latest": {...},
        "country_name": "Turkey",
        "country_code": "TUR"
    },
    "country_code": "TUR",
    "years_back": 10
}
```

## 📊 Структура таблицы `imf_economic_data`

### Поля таблицы:
- `id` (int8) - Уникальный идентификатор
- `country_code` (varchar) - Код страны (TUR, USA, DEU, ABW, etc.)
- `country_name` (varchar) - Название страны
- `indicator_code` (varchar) - Код показателя
- `indicator_name` (varchar) - Название показателя
- `year` (int4) - Год данных
- `value` (numeric) - Значение показателя
- `created_at` (timestamp) - Дата создания записи

### Типы показателей:
- `NGDP_RPCH` - "Real GDP growth (Annual percent change)" - Рост реального ВВП (%)
- `PCPIPCH` - "Inflation rate, average consumer prices" - Уровень инфляции (%)

### Пример данных:
```sql
-- Данные для Турции
INSERT INTO imf_economic_data (
    country_code, country_name, indicator_code, indicator_name, year, value
) VALUES 
('TUR', 'Turkey', 'NGDP_RPCH', 'Real GDP growth (Annual percent change)', 2023, 4.1),
('TUR', 'Turkey', 'NGDP_RPCH', 'Real GDP growth (Annual percent change)', 2022, 5.6),
('TUR', 'Turkey', 'PCPIPCH', 'Inflation rate, average consumer prices', 2023, 64.8),
('TUR', 'Turkey', 'PCPIPCH', 'Inflation rate, average consumer prices', 2022, 72.3);
```

## 🎯 Интеграция в полный отчет

### Обновленная структура `full_report_data`:

```python
full_report_data = {
    'object': {...},
    'roi': {...},
    'alternatives': [...],
    'macro': {
        'inflation': 64.8,        # Реальные данные из IMF
        'eur_try': 35.2,
        'eur_try_growth': 0.14,
        'refi_rate': 45,
        'gdp_growth': 4.1         # Реальные данные из IMF (рост ВВП в %)
    },
    'economic_charts': {           # НОВОЕ ПОЛЕ
        'gdp_chart': {...},
        'inflation_chart': {...},
        'trends': {...},
        'latest': {...},
        'country_name': 'Turkey',
        'country_code': 'TUR'
    },
    'taxes': {...},
    'risks': [...],
    'liquidity': '...',
    'district': '...',
    'yield': 0.081,
    'price_index': 1.23,
    'mortgage_rate': 0.32,
    'global_house_price_index': 1.12,
    'summary': 'Полный отчёт с реальными экономическими данными из IMF.'
}
```

## 📈 Использование в Frontend

### 1. Получение данных:
```javascript
// Получение экономических данных
const response = await fetch('/api/economic_data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        country_code: 'TUR',
        years_back: 10
    })
});

const data = await response.json();
const chartData = data.chart_data;
```

### 2. Построение графиков (Chart.js):
```javascript
// График роста ВВП
const gdpCtx = document.getElementById('gdpChart').getContext('2d');
new Chart(gdpCtx, {
    type: 'line',
    data: chartData.gdp_chart,
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: `Динамика роста ВВП - ${chartData.country_name}`
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Рост ВВП (%)'
                }
            }
        }
    }
});

// График инфляции
const inflationCtx = document.getElementById('inflationChart').getContext('2d');
new Chart(inflationCtx, {
    type: 'line',
    data: chartData.inflation_chart,
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: `Динамика инфляции - ${chartData.country_name}`
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Инфляция (%)'
                }
            }
        }
    }
});
```

### 3. Отображение трендов:
```javascript
// Отображение трендов
const trends = chartData.trends;
const gdpTrend = trends.gdp_trend * 100; // Конвертируем в проценты
const inflationTrend = trends.inflation_trend * 100;

document.getElementById('gdpTrend').textContent = 
    `Тренд роста ВВП: ${gdpTrend > 0 ? '+' : ''}${gdpTrend.toFixed(1)}%`;
document.getElementById('inflationTrend').textContent = 
    `Тренд инфляции: ${inflationTrend > 0 ? '+' : ''}${inflationTrend.toFixed(1)}%`;

// Отображение последних значений
const latest = chartData.latest;
if (latest.gdp) {
    document.getElementById('latestGdp').textContent = 
        `Последний рост ВВП: ${latest.gdp.value}% (${latest.gdp.year})`;
}
if (latest.inflation) {
    document.getElementById('latestInflation').textContent = 
        `Последняя инфляция: ${latest.inflation.value}% (${latest.inflation.year})`;
}
```

## 🔄 Обновление данных

### Автоматическое обновление:
1. Данные обновляются при каждом запросе полного отчета
2. Используются реальные данные из таблицы `imf_economic_data`
3. Тренды вычисляются автоматически

### Ручное обновление:
```python
# Обновление данных в базе
def update_economic_data():
    # Здесь можно добавить логику для обновления данных из внешних API
    # например, из IMF API или других источников
    pass
```

## 🚀 Планы развития

### Краткосрочные:
- [ ] Добавление данных для других стран
- [ ] Интеграция с внешними API (IMF, World Bank)
- [ ] Кэширование данных для улучшения производительности

### Долгосрочные:
- [ ] Прогнозирование экономических показателей
- [ ] Сравнительный анализ стран
- [ ] Интерактивные графики с фильтрами

## 📞 Поддержка

При возникновении проблем:
1. Проверьте структуру таблицы `imf_economic_data`
2. Убедитесь в наличии данных для запрашиваемой страны
3. Проверьте логи на предмет ошибок API
4. Обратитесь к команде разработки

---

**Последнее обновление**: Декабрь 2024
**Версия**: 1.0 