# Aaadviser - Система анализа недвижимости

## Обзор системы

Система состоит из:
- **База данных Supabase** - хранение данных о недвижимости и пользователях
- **API сервер** - обработка запросов от WebApp
- **Telegram WebApp** - интерфейс для пользователей
- **Telegram Bot** - интеграция с Telegram

## Установка и настройка

### 1. Подготовка базы данных

Выполните SQL скрипты в Supabase Dashboard:

```sql
-- Обновление схемы
\i update_schema_users.sql
\i fix_missing_columns.sql
```

### 2. Загрузка тестовых данных

```bash
# Установка зависимостей
pip install -r requirements.txt

# Загрузка данных в Supabase
python load_test_data_supabase.py
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
TELEGRAM_BOT_TOKEN=your-bot-token
WEBAPP_URL=https://your-domain.com/webapp_real_data.html
```

### 4. Запуск API сервера

```bash
# Установка зависимостей
pip install flask flask-cors requests python-dotenv

# Запуск сервера
python api_server.py
```

Сервер будет доступен на `http://localhost:5000`

### 5. Размещение WebApp

Загрузите файл `webapp_real_data.html` на ваш веб-сервер или используйте GitHub Pages.

### 6. Настройка Telegram Bot

Обновите бота для работы с новой системой:

```python
# В вашем боте добавьте обработку координат
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    lat = location.latitude
    lon = location.longitude
    
    # Создаем WebApp URL с координатами
    webapp_url = f"{WEBAPP_URL}?lat={lat}&lon={lon}"
    
    # Отправляем WebApp
    await update.message.reply_text(
        "Анализируем рынок недвижимости...",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Открыть анализ", web_app=WebAppInfo(url=webapp_url))
        ]])
    )
```

## Структура API

### Эндпоинты:

1. **POST /api/generate-report**
   - Генерация базового отчета по координатам
   - Параметры: `lat`, `lon`, `telegram_id`

2. **POST /api/user-balance**
   - Получение баланса пользователя
   - Параметры: `telegram_id`

3. **POST /api/full-report**
   - Получение полного отчета (платный)
   - Параметры: `telegram_id`, `report_data`

4. **POST /api/top-up-balance**
   - Пополнение баланса пользователя
   - Параметры: `telegram_id`, `amount`

## Функциональность

### Базовый отчет (бесплатный):
- Средние цены за м²
- ROI аренды
- Ликвидность (дни на рынке)
- Топ-3 инсайта
- Информация о районе

### Полный отчет ($15):
- Прогноз цен на 2025 год
- Анализ 20+ конкурентов
- Кастомные рекомендации
- Детальная аналитика

### Система баланса:
- Автоматическое создание пользователей
- Списание средств за полные отчеты
- Пополнение баланса (заглушка)

## Тестирование

### 1. Проверка данных в базе:

```bash
python check_data.py
```

### 2. Тестирование API:

```bash
# Проверка здоровья API
curl http://localhost:5000/health

# Генерация отчета
curl -X POST http://localhost:5000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{"lat": 36.8841, "lon": 30.7056, "telegram_id": 123456}'
```

### 3. Тестирование WebApp:

Откройте `webapp_real_data.html?lat=36.8841&lon=30.7056` в браузере.

## Развертывание в продакшене

### 1. Настройка домена

Убедитесь, что ваш домен добавлен в настройки Telegram Bot.

### 2. SSL сертификат

WebApp требует HTTPS. Настройте SSL сертификат.

### 3. Балансировщик нагрузки

Для высоких нагрузок используйте:
- Nginx для статических файлов
- Gunicorn для API сервера
- Redis для кэширования

### 4. Мониторинг

Добавьте логирование и мониторинг:
- Логи API запросов
- Мониторинг баланса пользователей
- Алерты при ошибках

## Безопасность

### 1. Валидация данных
- Проверка координат
- Валидация telegram_id
- Защита от SQL инъекций

### 2. Rate Limiting
- Ограничение запросов на пользователя
- Защита от DDoS атак

### 3. Аутентификация
- Проверка подписи Telegram
- Валидация токенов

## Масштабирование

### 1. Кэширование
- Redis для кэширования отчетов
- CDN для статических файлов

### 2. База данных
- Репликация Supabase
- Оптимизация запросов

### 3. API
- Микросервисная архитектура
- Контейнеризация с Docker

## Поддержка

При возникновении проблем:

1. Проверьте логи API сервера
2. Убедитесь в корректности данных в Supabase
3. Проверьте настройки Telegram Bot
4. Протестируйте API эндпоинты

## Дальнейшее развитие

1. **Интеграция с платежными системами**
2. **Расширенная аналитика**
3. **Уведомления о новых объектах**
4. **Мобильное приложение**
5. **Интеграция с CRM системами** 