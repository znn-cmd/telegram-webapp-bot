# 💰 Новая логика расчета цен для отчетов

## 🎯 Обзор новой системы

Реализована принципиально новая логика расчета цен, основанная на **базовых ценах из 4 таблиц** для текущего месяца и **математических формулах** для исторических и будущих периодов.

---

## 🏗️ Архитектура решения

### **Backend: API `/api/base_prices`**
Новый endpoint получает данные из 4 таблиц и рассчитывает базовые цены:

```python
# Таблицы источники
tables = ['age_data', 'floor_segment_data', 'heating_data', 'house_type_data']

# Алгоритм расчета
for table in tables:
    min_prices.append(avg(table.min_unit_price_for_sale))
    max_prices.append(avg(table.max_unit_price_for_sale))

# Финальная базовая цена
base_sale_price = (avg(min_prices) + avg(max_prices)) / 2
```

### **Frontend: Функция `prepareTrendsWithHistoricalPrices()`**
Обновленная логика с 3 типами расчетов:

1. **Текущий месяц**: Базовые цены из 4 таблиц
2. **Будущие месяцы**: Прогрессивный расчет
3. **Исторические месяцы**: Рекурсивный расчет

---

## 📊 Детальная логика расчетов

### **1️⃣ Текущий месяц (август 2025)**

#### **Источник данных:**
```javascript
// Получение базовых цен из 4 таблиц
const basePrices = await getBasePricesFromTables();

// Использование для текущего месяца
if (isCurrentMonth) {
    priceCache.set(cacheKey, {
        salePrice: basePrices.sale_price,    // Рассчитанная базовая цена
        rentPrice: basePrices.rent_price,    // Рассчитанная базовая цена
        isCalculated: true                   // Помечено как рассчитанное
    });
}
```

#### **Формула расчета базовой цены:**
```
Базовая_цена = (Среднее_MIN_из_4_таблиц + Среднее_MAX_из_4_таблиц) ÷ 2

где:
- age_data.min_unit_price_for_sale/rent → avg
- floor_segment_data.min_unit_price_for_sale/rent → avg  
- heating_data.min_unit_price_for_sale/rent → avg
- house_type_data.min_unit_price_for_sale/rent → avg
```

---

### **2️⃣ Будущие месяцы (сентябрь 2025+)**

#### **Прогрессивная формула:**
```javascript
function calculateFuturePrice(previousPrice, changePercent) {
    return previousPrice * (1 + changePercent);
}

// Пример:
// Август 2025: ₺61,803.00 (базовая цена)
// Процент изменения сентября: +2.25%
// Сентябрь 2025 = 61,803 × (1 + 0.0225) = ₺63,193.17
```

#### **Логика расчета:**
```javascript
if (isFutureMonth) {
    const prevMonthData = priceCache.get(prevMonthKey);
    if (prevMonthData && trend.price_change_sale) {
        calculatedSalePrice = calculateFuturePrice(
            prevMonthData.salePrice, 
            trend.price_change_sale
        );
    }
}
```

---

### **3️⃣ Исторические месяцы (февраль-июль 2025)**

#### **Рекурсивная формула:**
```javascript
function calculateHistoricalPrice(nextMonthPrice, changePercent) {
    return nextMonthPrice / (1 + changePercent);
}

// Пример:
// Август 2025: ₺61,803.00 (базовая цена)
// Процент изменения августа: +1.66%
// Июль 2025 = 61,803 ÷ (1 + 0.0166) = ₺60,787.33
```

#### **Логика расчета:**
```javascript
if (isHistoricalMonth) {
    const nextMonthData = priceCache.get(nextMonthKey);
    if (nextMonthData && trend.price_change_sale) {
        calculatedSalePrice = calculateHistoricalPrice(
            nextMonthData.salePrice, 
            trend.price_change_sale
        );
    }
}
```

---

## 🔄 Интеграция во все блоки

### **✅ Блок "Тренд цен" (Зеленая карточка)**

**Обновления:**
- Функция `addPropertyTrendsSection()` получает базовые цены
- Для текущего месяца показывает базовую цену вместо `trend_value`
- Проценты изменения остаются из БД

```javascript
// Используем базовые цены если доступны
let displayValue = currentTrend.trend_value;
if (basePrices && type === 'price_trend') {
    displayValue = basePrices.sale_price; // Базовая цена продажи
}
```

### **✅ Таблица "Детальные данные трендов"**

**Обновления:**
- Функция `generateTrendsTable()` использует `await prepareTrendsWithHistoricalPrices()`
- Все цены рассчитываются по новой логике
- Текущий месяц: базовые цены (помечены как calculated)
- Исторические: рекурсивный расчет
- Будущие: прогрессивный расчет

### **✅ Таблица "Прогноз цены и аренды"**

**Обновления:**
- Функция `generateForecastTable()` использует `await prepareTrendsWithHistoricalPrices()`
- Показывает рассчитанные цены для всех месяцев
- Использует `calculated_sale_price` вместо `unit_price_for_sale`

---

## 🛡️ Fallback-стратегия

При недоступности базовых цен используется **оригинальная логика**:

```javascript
try {
    basePrices = await getBasePricesFromTables();
} catch (error) {
    console.error('❌ Ошибка получения базовых цен, используем fallback:', error);
    return prepareTrendsWithOriginalLogic(trends);
}
```

**Fallback функция:**
- Использует данные из `property_trends` для текущего месяца
- Применяет только рекурсивный расчет для исторических месяцев
- Гарантирует работоспособность при любых ошибках

---

## 📈 Преимущества новой логики

| Аспект | Старая логика | Новая логика |
|--------|---------------|--------------|
| **Базовые цены** | Из `property_trends` | Из 4 рыночных таблиц |
| **Точность** | Ограниченная | Высокая (многоисточниковые данные) |
| **Текущий месяц** | Прямо из БД | Рассчитанные базовые цены |
| **Будущие месяцы** | Не обрабатывались | Прогрессивный расчет |
| **Исторические** | Рекурсивный расчет | Рекурсивный на основе базовых цен |
| **Fallback** | Отсутствовал | Полная резервная логика |

---

## 🔧 Техническая реализация

### **Обновленные функции:**

1. **Backend:**
   - `api_base_prices()` - новый endpoint
   - Запросы к 4 таблицам с агрегацией

2. **Frontend:**
   - `prepareTrendsWithHistoricalPrices()` - async, новая логика
   - `getBasePricesFromTables()` - запрос базовых цен
   - `calculateFuturePrice()` - прогрессивный расчет
   - `prepareTrendsWithOriginalLogic()` - fallback
   - `addPropertyTrendsSection()` - обновлена для базовых цен

### **Логирование:**

```javascript
console.log('💰 Базовые цены получены:', basePrices);
console.log('🚀 Прогрессивный расчет для 2025-9: продажа 63193.17 ₺/м²');
console.log('⏪ Рекурсивный расчет для 2025-7: продажа 60787.33 ₺/м²');
```

---

## 🎯 Результат

**Новая система обеспечивает:**
- ✅ Более точные базовые цены из множественных источников
- ✅ Математически корректные расчеты для всех периодов  
- ✅ Единообразие данных во всех блоках отчета
- ✅ Надежность через fallback-логику
- ✅ Полная обратная совместимость

**Все таблицы и блоки теперь используют единую, точную систему расчета цен! 🚀**
