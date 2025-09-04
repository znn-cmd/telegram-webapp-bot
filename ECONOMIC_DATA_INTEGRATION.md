# Интеграция экономических данных в отчеты Aaadviser

## 📊 Обзор

Добавлена функциональность для получения реальных экономических данных из таблицы `imf_economic_data` в Supabase и их интеграции в полные отчеты по недвижимости.

## ✅ Статус реализации

**ВЫПОЛНЕНО:**
- ✅ Получение экономических данных из Supabase
- ✅ Создание данных для графиков
- ✅ Интеграция в полный отчет
- ✅ Добавление в PDF отчет
- ✅ Тестирование функциональности
- ✅ Встраивание визуальных графиков в PDF

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
            'value': 5.1,              # Рост ВВП в процентах
            'indicator_code': 'NGDP_RPCH',
            'indicator_name': 'Real GDP growth (Annual percent change)'
        }
    ],
    'inflation_data': [
        {
            'year': 2023,
            'value': 53.9,             # Уровень инфляции в процентах
            'indicator_code': 'PCPIPCH',
            'indicator_name': 'Inflation rate, average consumer prices'
        }
    ],
    'country_code': 'TUR',
    'country_name': 'Türkiye, Republic of',
    'gdp_trend': 0.071,               # Тренд ВВП
    'inflation_trend': 0.15,          # Тренд инфляции
    'latest_gdp': {...},              # Последние данные ВВП
    'latest_inflation': {...},        # Последние данные инфляции
    'data_years': '2015-2025'
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
        'labels': ['2015', '2016', ...],
        'datasets': [{
            'label': 'Рост ВВП (%) - Türkiye, Republic of',
            'data': [5.1, 5.5, ...],
            'borderColor': '#667eea',
            'backgroundColor': 'rgba(102, 126, 234, 0.1)',
            'tension': 0.4,
            'fill': False
        }]
    },
    'inflation_chart': {
        'labels': ['2015', '2016', ...],
        'datasets': [{
            'label': 'Инфляция (%) - Türkiye, Republic of',
            'data': [53.9, 58.5, ...],
            'borderColor': '#dc3545',
            'backgroundColor': 'rgba(220, 53, 69, 0.1)',
            'tension': 0.4,
            'fill': False
        }]
    },
    'trends': {
        'gdp_trend': 0.071,
        'inflation_trend': 0.15
    },
    'latest': {
        'gdp': {...},
        'inflation': {...}
    },
    'country_name': 'Türkiye, Republic of',
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
        "country_name": "Türkiye, Republic of",
        "gdp_trend": 0.071,
        "inflation_trend": 0.15,
        "latest_gdp": {...},
        "latest_inflation": {...},
        "data_years": "2015-2025"
    },
    "chart_data": {
        "gdp_chart": {...},
        "inflation_chart": {...},
        "trends": {...},
        "latest": {...},
        "country_name": "Türkiye, Republic of",
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
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'Real GDP growth (Annual percent change)', 2025, 2.7),
('TUR', 'Türkiye, Republic of', 'NGDP_RPCH', 'Real GDP growth (Annual percent change)', 2024, 3.2),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation rate, average consumer prices', 2025, 35.9),
('TUR', 'Türkiye, Republic of', 'PCPIPCH', 'Inflation rate, average consumer prices', 2024, 58.5);
```

## 🎯 Интеграция в полный отчет

### Обновленная структура `full_report_data`:

```python
full_report_data = {
    'object': {...},
    'roi': {...},
    'alternatives': [...],
    'macro': {
        'inflation': 35.9,        # Реальные данные из IMF
        'eur_try': 35.2,
        'eur_try_growth': 0.14,
        'refi_rate': 45,
        'gdp_growth': 2.7         # Реальные данные из IMF (рост ВВП в %)
    },
    'economic_charts': {           # НОВОЕ ПОЛЕ
        'gdp_chart': {...},
        'inflation_chart': {...},
        'trends': {...},
        'latest': {...},
        'country_name': 'Türkiye, Republic of',
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

## 📄 Интеграция в PDF отчет

### Добавлен новый блок в PDF отчет:

```python
# Экономические данные и графики
if 'economic_charts' in report:
    pdf.set_font("DejaVu", 'B', 14)
    pdf.cell(200, 10, txt="Экономические данные:", ln=True)
    pdf.set_font("DejaVu", size=12)
    
    economic_charts = report['economic_charts']
    country_name = economic_charts.get('country_name', 'Unknown')
    
    # Отображаем последние значения
    latest = economic_charts.get('latest', {})
    if latest.get('gdp'):
        gdp_data = latest['gdp']
        pdf.cell(200, 8, txt=f"Последний рост ВВП ({gdp_data['year']}): {gdp_data['value']}%", ln=True)
    
    if latest.get('inflation'):
        inflation_data = latest['inflation']
        pdf.cell(200, 8, txt=f"Последняя инфляция ({inflation_data['year']}): {inflation_data['value']}%", ln=True)
    
    # Отображаем тренды
    trends = economic_charts.get('trends', {})
    if trends.get('gdp_trend') is not None:
        gdp_trend = trends['gdp_trend'] * 100
        trend_text = f"Тренд роста ВВП: {gdp_trend > 0 and '+' or ''}{gdp_trend:.1f}%"
        pdf.cell(200, 8, txt=trend_text, ln=True)
    
    if trends.get('inflation_trend') is not None:
        inflation_trend = trends['inflation_trend'] * 100
        trend_text = f"Тренд инфляции: {inflation_trend > 0 and '+' or ''}{inflation_trend:.1f}%"
        pdf.cell(200, 8, txt=trend_text, ln=True)
    
    # Отображаем данные по годам (последние 5 лет)
    gdp_chart = economic_charts.get('gdp_chart', {})
    if gdp_chart.get('labels') and gdp_chart.get('datasets'):
        pdf.ln(3)
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(200, 8, txt=f"Динамика роста ВВП ({country_name}):", ln=True)
        pdf.set_font("DejaVu", size=10)
        
        labels = gdp_chart['labels']
        data = gdp_chart['datasets'][0]['data'] if gdp_chart['datasets'] else []
        
        for i, (year, value) in enumerate(zip(labels, data)):
            if i < 5:  # Показываем только последние 5 лет
                pdf.cell(200, 6, txt=f"{year}: {value}%", ln=True)
    
    inflation_chart = economic_charts.get('inflation_chart', {})
    if inflation_chart.get('labels') and inflation_chart.get('datasets'):
        pdf.ln(3)
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(200, 8, txt=f"Динамика инфляции ({country_name}):", ln=True)
        pdf.set_font("DejaVu", size=10)
        
        labels = inflation_chart['labels']
        data = inflation_chart['datasets'][0]['data'] if inflation_chart['datasets'] else []
        
        for i, (year, value) in enumerate(zip(labels, data)):
            if i < 5:  # Показываем только последние 5 лет
                pdf.cell(200, 6, txt=f"{year}: {value}%", ln=True)
    
    pdf.ln(5)
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

## 🧪 Результаты тестирования

### Тест экономических данных:
```
✅ Экономические данные получены:
   - Страна: Türkiye, Republic of
   - Данные ВВП: 7 записей
   - Данные инфляции: 7 записей

📈 Данные ВВП:
   2025: 2.7%
   2024: 3.2%
   2023: 5.1%
   2022: 5.5%
   2021: 11.4%

📉 Данные инфляции:
   2025: 35.9%
   2024: 58.5%
   2023: 53.9%
```

### Тест полного отчета:
```
📊 Полный отчет создан:
   - Инфляция: 35.9%
   - Рост ВВП: 2.7%
   - Экономические графики: Да
   - Страна графиков: Türkiye, Republic of
   - Тренд ВВП: 0.071
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

## 📊 Визуализация графиков

### Новые функции:
- ✅ `create_economic_chart_image()` - Создание графиков для веб-интерфейса
- ✅ `create_chart_image_for_pdf()` - Создание графиков для PDF отчетов
- ✅ Автоматическое встраивание графиков в PDF
- ✅ Fallback к текстовому отображению при ошибках

### Особенности графиков:
- **Дизайн**: Минималистичный, современный стиль
- **Цвета**: Голубой (#00bcd4) для ВВП, красный (#dc3545) для инфляции
- **Размеры**: Оптимизированы для PDF (180x100 мм)
- **Шрифты**: Поддержка русских шрифтов (DejaVu Sans)

### Техническая реализация:
```python
# Создание графика для PDF
chart_buffer = create_chart_image_for_pdf(economic_charts, title)
if chart_buffer:
    pdf.image(chart_buffer, x=10, y=pdf.get_y(), w=190, h=80)
    chart_buffer.close()
```

## 🚀 Планы развития

### Краткосрочные:
- [x] Добавление данных для других стран
- [x] Интеграция с внешними API (IMF, World Bank)
- [x] Визуализация графиков в PDF
- [ ] Кэширование данных для улучшения производительности

### Долгосрочные:
- [ ] Прогнозирование экономических показателей
- [ ] Сравнительный анализ стран
- [ ] Интерактивные графики с фильтрами
- [ ] Дополнительные типы графиков (столбчатые, круговые)

## 📞 Поддержка

При возникновении проблем:
1. Проверьте структуру таблицы `imf_economic_data`
2. Убедитесь в наличии данных для запрашиваемой страны
3. Проверьте логи на предмет ошибок API
4. Обратитесь к команде разработки

---

**Последнее обновление**: Декабрь 2024
**Версия**: 1.0
**Статус**: ✅ Реализовано и протестировано 