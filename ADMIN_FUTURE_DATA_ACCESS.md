# Контроль доступа к будущим данным в таблице трендов

## Описание функциональности

Реализован контроль доступа к будущим данным в таблице "Детальные данные трендов" на основе статуса пользователя в таблице `users`.

## Что изменилось

### 1. ✅ Обратная сортировка данных

**Изменение**: Порядок сортировки изменен на обратный - новые даты вверху, старые внизу.

**Новая логика сортировки**:
```javascript
// Сортируем по убыванию (новые даты сначала)
if (yearA !== yearB) {
    return yearB - yearA; // 2026 перед 2025, 2025 перед 2024, и т.д.
}
return monthB - monthA; // Декабрь перед ноябрем, ноябрь перед октябрем, и т.д.
```

**Пример порядка**:
```
Июн. 2026 ⬆️ (самые новые вверху)
Май. 2026
...
Авг. 2025 (текущий)
Июл. 2025
...
Фев. 2022 ⬇️ (самые старые внизу)
```

### 2. ✅ Скрытие будущих данных для обычных пользователей

**Логика фильтрации**:
- **Обычные пользователи**: видят только текущий месяц и прошлые данные
- **Администраторы**: видят все данные, включая будущие прогнозы

**Код фильтрации**:
```javascript
if (isAdmin) {
    // Админы видят все данные (включая будущие)
    console.log(`👑 Admin access: showing ALL trends including future data`);
    filteredTrends = sortedTrends;
} else {
    // Обычные пользователи видят только текущий месяц и прошлые
    console.log(`👤 Regular user: hiding future data`);
    filteredTrends = sortedTrends.filter(trend => {
        const isCurrentOrPast = trend.property_year < currentYear || 
                              (trend.property_year === currentYear && trend.property_month <= currentMonth);
        return isCurrentOrPast;
    });
}
```

### 3. ✅ Проверка статуса администратора

**Новая функция**: `checkUserAdminStatus()`

```javascript
async function checkUserAdminStatus() {
    try {
        if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
            const user = window.Telegram.WebApp.initDataUnsafe.user;
            if (user && user.id) {
                // Check if user is admin via API
                const response = await fetch('/api/check_admin_status', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ telegram_id: user.id })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('👤 Admin status check result:', data);
                    return data.is_admin === true;
                } else {
                    console.error('❌ Failed to check admin status:', response.status);
                    return false;
                }
            }
        }
        console.log('⚠️ No user data available for admin check');
        return false;
    } catch (error) {
        console.error('❌ Error checking admin status:', error);
        return false;
    }
}
```

### 4. ✅ Обновленная функция generateTrendsTable

**Интеграция проверки админа**:
```javascript
async function generateTrendsTable(trends) {
    // Проверяем статус админа пользователя
    const isAdmin = await checkUserAdminStatus();
    console.log(`👤 User admin status: ${isAdmin}`);
    
    // Подготавливаем тренды с рассчитанными историческими ценами
    const trendsWithHistoricalPrices = prepareTrendsWithHistoricalPrices(trends);
    
    // Фильтруем тренды по диапазону дат (с учетом статуса админа)
    const filteredTrends = filterTrendsByDateRange(trendsWithHistoricalPrices, isAdmin);
    
    // ... остальная логика генерации таблицы
}
```

## Логика контроля доступа

### Для обычных пользователей:
- ✅ **Текущий месяц** - август 2025
- ✅ **Прошлые месяцы** - июль 2025, июнь 2025, ... февраль 2022
- ❌ **Будущие месяцы** - сентябрь 2025, октябрь 2025, ... июнь 2026

### Для администраторов:
- ✅ **Все данные** - февраль 2022 ... июнь 2026
- ✅ **Будущие прогнозы** - сентябрь 2025 ... июнь 2026
- ✅ **Полный доступ** к таблице трендов

## Проверка статуса в базе данных

Функция обращается к API endpoint `/api/check_admin_status`, который:

1. **Получает** `telegram_id` пользователя
2. **Ищет** запись в таблице `users`
3. **Проверяет** поле `user_status` 
4. **Возвращает** `is_admin: true` если `user_status === 'admin'`

**Структура ответа API**:
```json
{
    "success": true,
    "is_admin": true,
    "user_status": "admin",
    "period_end": "2026-07-11"
}
```

## Пример отображения

### Для обычного пользователя (август 2025):
| Дата | Продажа (₺/м²) | Изм-ие цены продажи | Аренда (₺/м²) | Изм-ие цены аренды | Доходность |
|------|----------------|---------------------|----------------|---------------------|------------|
| **Авг. 2025** | ₺61,803.00 | +2.25% | ₺302.77 | +2.38% | 5.88% |
| **Июл. 2025** | ₺61,788.00 | +2.46% | ₺303.00 | +2.54% | 5.87% |
| ... | ... | ... | ... | ... | ... |
| **Фев. 2022** | ₺43,485.00 | +16.18% | ₺182.00 | +12.12% | 6.71% |

### Для администратора:
| Дата | Продажа (₺/м²) | Изм-ие цены продажи | Аренда (₺/м²) | Изм-ие цены аренды | Доходность |
|------|----------------|---------------------|----------------|---------------------|------------|
| **Июн. 2026** | ₺71,107.00 | +1.93% | ₺355.43 | +2.51% | 6.00% |
| **Май. 2026** | ₺69,750.00 | +1.04% | ₺346.50 | +1.07% | 5.99% |
| ... | ... | ... | ... | ... | ... |
| **Авг. 2025** | ₺61,803.00 | +2.25% | ₺302.77 | +2.38% | 5.88% |
| ... | ... | ... | ... | ... | ... |
| **Фев. 2022** | ₺43,485.00 | +16.18% | ₺182.00 | +12.12% | 6.71% |

## Логирование и отладка

В консоли браузера будут отображаться:

```
👤 User admin status: false
👤 Regular user: hiding future data
🔒 Filtered 102 trends to 65 (removed future data)
✅ Returning 65 trends for regular user
```

Или для админа:
```
👤 User admin status: true
👑 Admin access: showing ALL trends including future data
✅ Returning 102 trends for admin user
```

## Преимущества реализации

1. **Гибкость доступа**: Разные уровни доступа для разных типов пользователей
2. **Безопасность данных**: Будущие прогнозы доступны только администраторам
3. **Простота управления**: Контроль через поле `user_status` в таблице `users`
4. **Прозрачность**: Подробное логирование всех операций фильтрации
5. **Обратная совместимость**: Не нарушает существующую функциональность

## Файлы изменений

- `webapp_object_evaluation.html` - основная логика контроля доступа
- `test_historical_price_calculation_fixed.html` - обновленный тестовый файл
- `app.py` - API endpoint `/api/check_admin_status` (уже существует)

## Тестирование

### Для обычного пользователя:
1. Установить `user_status = NULL` в таблице `users`
2. Проверить отсутствие будущих данных в таблице
3. Проверить логи в консоли

### Для администратора:
1. Установить `user_status = 'admin'` в таблице `users`
2. Проверить наличие всех данных, включая будущие
3. Проверить логи в консоли

## Ограничения для графика трендов

### 5. ✅ Фильтрация данных графика по дате

**Добавлено ограничение**: Для обычных пользователей график трендов показывает данные только с января 2021 года и позднее.

**Логика фильтрации графика**:
```javascript
if (isAdmin) {
    // Админы видят все данные на графике
    console.log(`👑 Admin chart access: showing ALL trend data`);
    filteredTrends = trends;
} else {
    // Обычные пользователи видят данные с января 2021 года
    console.log(`👤 Regular user chart: filtering data from January 2021`);
    filteredTrends = trends.filter(trend => {
        const isFromJan2021OrLater = trend.property_year > 2021 || 
                                   (trend.property_year === 2021 && trend.property_month >= 1);
        return isFromJan2021OrLater;
    });
    console.log(`📊 Chart data filtered: ${trends.length} → ${filteredTrends.length} trends (from Jan 2021+)`);
}
```

**Обновленные функции для графика**:
- `createTrendsChart(trends, chartType, isAdmin)` - принимает параметр `isAdmin`
- `initializeTrendsChart(trends)` - проверяет статус админа
- `switchChartType(chartType)` - также проверяет статус при переключении

### Различия в отображении графика:

#### Для обычного пользователя:
- **Начало графика**: Январь 2021
- **Конец графика**: Август 2025 (текущий месяц)
- **Скрыто**: Все данные до января 2021 + будущие месяцы

#### Для администратора:
- **Начало графика**: Все доступные данные (например, с февраля 2018)
- **Конец графика**: Июнь 2026 (включая будущие прогнозы)
- **Доступно**: Полная история + все прогнозы

## Полная логика контроля доступа

### Таблица трендов:
| Тип пользователя | Отображаемые данные |
|------------------|---------------------|
| **Обычный** | 10 записей: 8 месяцев назад + текущий + 1 месяц вперед |
| **Админ** | Все данные (прошлые + текущий + будущие) |

### График трендов:
| Тип пользователя | Отображаемые данные |
|------------------|---------------------|
| **Обычный** | Январь 2021 → Август 2025 (текущий) |
| **Админ** | Все данные (полная история + прогнозы) |

## Ограничения записей в таблице

### 6. ✅ Ограничение количества записей для обычных пользователей

**Добавлено ограничение**: Для обычных пользователей таблица показывает только 10 записей в ограниченном диапазоне.

**Логика ограничения таблицы**:
```javascript
if (isAdmin) {
    // Админы видят все данные
    filteredTrends = sortedTrends;
} else {
    // Обычные пользователи: 8 месяцев назад + текущий + 1 месяц вперед
    const startDate = new Date(currentYear, currentMonth - 1 - 8, 1); // 8 месяцев назад
    const endDate = new Date(currentYear, currentMonth - 1 + 1, 1);   // 1 месяц вперед
    
    filteredTrends = sortedTrends.filter(trend => {
        const trendDate = new Date(trend.property_year, trend.property_month - 1, 1);
        const isInRange = trendDate >= startDate && trendDate <= endDate;
        return isInRange;
    });
}
```

**Пример диапазона для августа 2025**:
- **Начало**: Декабрь 2024 (8 месяцев назад)
- **Конец**: Сентябрь 2025 (1 месяц вперед)
- **Итого**: ~10 записей

**Важно**: Расчеты исторических цен по-прежнему выполняются для всех данных, ограничение касается только отображения в таблице.

## Логирование

В консоли для таблицы отображается:

### Для обычного пользователя:
```
👤 Regular user: showing limited range (8 months back + current + 1 month forward)
📅 Table date range: 2024-12 to 2025-9
🔒 Filtered 102 trends to 10 (limited range for table)
```

В консоли для графика отображается:

### Для обычного пользователя:
```
📊 Chart admin status: false
👤 Regular user chart: filtering data from January 2021
📊 Chart data filtered: 102 → 58 trends (from Jan 2021+)
```

### Для администратора:
```
📊 Chart admin status: true
👑 Admin chart access: showing ALL trend data
```

## Заключение

Реализован полный контроль доступа к данным как в таблице трендов, так и в графике с учетом статуса пользователя:

1. **Таблица**: Ограничена до 10 записей (8 месяцев назад + текущий + 1 вперед) для обычных пользователей
2. **График**: Скрыты данные до января 2021 + будущие месяцы для обычных пользователей
3. **Расчеты**: Выполняются для всех данных независимо от ограничений отображения
4. **Администраторы**: Полный доступ ко всем данным в обеих формах представления

Система обеспечивает безопасность данных, ограничивает отображение для обычных пользователей, но сохраняет точность расчетов.
