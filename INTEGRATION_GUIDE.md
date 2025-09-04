# 📊 Руководство по интеграции экономических графиков

## 🎯 Цель

Преобразовать текстовые данные "Динамика роста ВВП" и "Динамика инфляции" из PDF отчета в интерактивные графики в WebApp.

## ✅ Что уже готово

1. **Backend API** - `/api/economic_data` возвращает данные для графиков
2. **PDF отчет** - уже включает экономические данные
3. **Компонент графиков** - `economic_charts_component.js`
4. **Демо страница** - `economic_charts_demo.html`

## 🔧 Интеграция в WebApp

### Шаг 1: Подключение компонента

Добавьте в HTML файл WebApp (например, `webapp_real_data.html`):

```html
<!-- В секции head -->
<script src="economic_charts_component.js"></script>

<!-- В секции body, где должен отображаться отчет -->
<div id="economic-charts-placeholder"></div>
```

### Шаг 2: Инициализация в JavaScript

Добавьте в существующий JavaScript код:

```javascript
// Глобальная переменная для компонента
let economicChartsComponent = null;

// Функция для инициализации графиков
async function initEconomicCharts() {
    if (!economicChartsComponent) {
        economicChartsComponent = new EconomicChartsComponent();
    }
    
    const container = document.getElementById('economic-charts-placeholder');
    if (container) {
        await economicChartsComponent.init(container, 'TUR');
    }
}

// Вызывайте эту функцию после загрузки отчета
function onReportLoaded() {
    // ... существующий код ...
    
    // Добавляем графики
    initEconomicCharts();
}
```

### Шаг 3: Интеграция с существующим кодом

Найдите функцию, которая обрабатывает полный отчет, и добавьте:

```javascript
// В функции обработки полного отчета
async function handleFullReport(reportData) {
    // ... существующий код отображения отчета ...
    
    // Добавляем экономические графики
    if (reportData.economic_charts) {
        await initEconomicCharts();
    }
}
```

## 📱 Пример интеграции

### В `webapp_real_data.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Существующие стили -->
    <script src="economic_charts_component.js"></script>
</head>
<body>
    <!-- Существующий контент -->
    
    <!-- Место для графиков -->
    <div id="economic-charts-placeholder"></div>
    
    <!-- Существующие скрипты -->
    <script>
        // Глобальная переменная
        let economicChartsComponent = null;
        
        // Функция инициализации графиков
        async function initEconomicCharts() {
            if (!economicChartsComponent) {
                economicChartsComponent = new EconomicChartsComponent();
            }
            
            const container = document.getElementById('economic-charts-placeholder');
            if (container) {
                await economicChartsComponent.init(container, 'TUR');
            }
        }
        
        // Интеграция с существующей функцией отчета
        async function downloadPDF() {
            // ... существующий код ...
            
            // После успешной генерации отчета
            if (data.success) {
                // ... существующий код ...
                
                // Добавляем графики
                await initEconomicCharts();
            }
        }
        
        // Очистка при переходе на другую страницу
        function cleanupCharts() {
            if (economicChartsComponent) {
                economicChartsComponent.destroy();
                economicChartsComponent = null;
            }
        }
    </script>
</body>
</html>
```

## 🎨 Кастомизация стилей

### Изменение цветов:

```css
/* В economic_charts_component.js или отдельном CSS файле */
.stat-card.gdp {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
}

.stat-card.inflation {
    background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
}
```

### Изменение размеров:

```css
.chart-container {
    height: 250px; /* Уменьшить высоту */
}

.stat-value {
    font-size: 18px; /* Уменьшить размер шрифта */
}
```

## 🔄 Обновление данных

### Автоматическое обновление:

```javascript
// Обновление каждые 5 минут
setInterval(async () => {
    if (economicChartsComponent) {
        await economicChartsComponent.updateData('TUR');
    }
}, 5 * 60 * 1000);
```

### Ручное обновление:

```javascript
// Кнопка обновления
function refreshCharts() {
    if (economicChartsComponent) {
        economicChartsComponent.updateData('TUR');
    }
}
```

## 📊 Структура данных

### API ответ:

```json
{
    "success": true,
    "chart_data": {
        "gdp_chart": {
            "labels": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            "datasets": [{
                "label": "Рост ВВП (%) - Türkiye, Republic of",
                "data": [0.9, 1.9, 11.4, 5.5, 5.1, 3.2, 2.7],
                "borderColor": "#667eea",
                "backgroundColor": "rgba(102, 126, 234, 0.1)"
            }]
        },
        "inflation_chart": {
            "labels": ["2019", "2020", "2021", "2022", "2023", "2024", "2025"],
            "datasets": [{
                "label": "Инфляция (%) - Türkiye, Republic of",
                "data": [15.2, 12.3, 19.6, 72.3, 53.9, 58.5, 35.9],
                "borderColor": "#dc3545",
                "backgroundColor": "rgba(220, 53, 69, 0.1)"
            }]
        },
        "trends": {
            "gdp_trend": 0.071,
            "inflation_trend": -0.226
        },
        "latest": {
            "gdp": {"year": 2025, "value": 2.7},
            "inflation": {"year": 2025, "value": 35.9}
        },
        "country_name": "Türkiye, Republic of",
        "country_code": "TUR"
    }
}
```

## 🚀 Преимущества графиков

### По сравнению с текстовым списком:

1. **Визуальность** - сразу видно тренды и изменения
2. **Интерактивность** - можно навести курсор для деталей
3. **Компактность** - больше данных в меньшем пространстве
4. **Профессиональность** - современный вид отчета
5. **Адаптивность** - графики подстраиваются под размер экрана

## 🔧 Тестирование

### Проверка работы:

1. Откройте `economic_charts_demo.html` в браузере
2. Убедитесь, что графики отображаются корректно
3. Проверьте адаптивность на мобильных устройствах
4. Протестируйте API `/api/economic_data`

### Отладка:

```javascript
// В консоли браузера
console.log('Chart.js загружен:', typeof Chart !== 'undefined');
console.log('Компонент создан:', economicChartsComponent);

// Проверка данных
fetch('/api/economic_data', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({country_code: 'TUR', years_back: 10})
}).then(r => r.json()).then(console.log);
```

## 📈 Результат

После интеграции вместо текстового списка:

```
Динамика роста ВВП (Türkiye, Republic of):
2025: 2.7%
2024: 3.2%
2023: 5.1%
2022: 5.5%
2021: 11.4%

Динамика инфляции (Türkiye, Republic of):
2025: 35.9%
2024: 58.5%
2023: 53.9%
```

Будет отображаться интерактивный график с:
- Линейными графиками ВВП и инфляции
- Статистическими карточками с последними значениями
- Индикаторами трендов
- Адаптивным дизайном

## 🎯 Следующие шаги

1. **Интеграция** - добавить компонент в существующий WebApp
2. **Тестирование** - проверить работу на разных устройствах
3. **Оптимизация** - настроить производительность
4. **Расширение** - добавить графики для других стран

---

**Статус**: ✅ Готово к интеграции
**Сложность**: Средняя
**Время интеграции**: 1-2 часа 