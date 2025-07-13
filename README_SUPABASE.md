# Telegram Bot для недвижимости в Анталии с Supabase

Бот для анализа рынка недвижимости в Анталии, Турция, с интеграцией WebApp и базой данных Supabase.

## 🚀 Быстрый старт

### 1. Настройка Supabase

1. Создайте проект на [supabase.com](https://supabase.com)
2. Получите URL и ключи в **Settings** → **API**
3. Создайте файл `.env`:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

### 2. Создание таблиц

В Supabase Dashboard → **SQL Editor** выполните содержимое файла `supabase_schema.sql`

### 3. Загрузка тестовых данных

```bash
pip install requests
python load_test_data_supabase.py
```

### 4. Запуск бота

```bash
python bot.py
```

## 📁 Структура проекта

```
Aaadviser/
├── bot.py                          # Основной файл бота
├── app.py                          # Flask API для WebApp
├── supabase_schema.sql             # SQL схема для Supabase
├── load_test_data_supabase.py      # Скрипт загрузки данных
├── SUPABASE_SETUP.md              # Подробная инструкция по Supabase
├── test_data_*.csv                # Тестовые данные
├── webapp/                        # WebApp интерфейс
│   ├── index.html
│   ├── script.js
│   └── style.css
└── requirements.txt
```

## 🗄️ Структура базы данных

### Таблицы

1. **short_term_rentals** - Краткосрочная аренда (Airbnb, Booking.com)
2. **long_term_rentals** - Долгосрочная аренда (Sahibinden)
3. **property_sales** - Продажа недвижимости
4. **historical_prices** - Исторические цены для ROI анализа
5. **market_statistics** - Рыночная статистика по районам

### Основные поля

- `property_id` - Уникальный идентификатор
- `address`, `latitude`, `longitude` - Адрес и координаты
- `district` - Район Анталии
- `property_type` - Тип недвижимости
- `bedrooms`, `bathrooms` - Количество комнат
- Цены в разных валютах (USD, TRY)
- Рейтинги и отзывы
- Источники данных и ссылки

## 🔧 Функции бота

### Основные команды

- `/start` - Приветствие и главное меню
- `/help` - Справка по командам
- `/language` - Смена языка (RU/EN/TR)

### WebApp функции

- **Поиск недвижимости** по району, цене, количеству комнат
- **ROI калькулятор** для анализа инвестиций
- **Рыночная статистика** по районам
- **Карта** с отображением объектов
- **Фильтры** по типу недвижимости и цене

### API эндпоинты

```bash
# Краткосрочная аренда
GET /api/properties/short-term?district=Lara&min_price=100&max_price=200

# Долгосрочная аренда
GET /api/properties/long-term?district=Konyaalti&min_price=5000

# Продажа недвижимости
GET /api/properties/sales?district=Muratpasa&min_price=1000000

# Рыночная статистика
GET /api/market/stats/Lara

# Расчет ROI
POST /api/roi/calculate
```

## 📊 Тестовые данные

Скрипт создает реалистичные данные для Анталии:

- **100+ записей** краткосрочной аренды
- **100+ записей** долгосрочной аренды  
- **100+ записей** продажи недвижимости
- **500+ записей** исторических цен
- **50+ записей** рыночной статистики

### Районы Анталии

- Lara
- Konyaalti
- Muratpasa
- Aksu
- Dosemealti
- Kepez
- Döşemealtı
- Serik

## 🛠️ Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Aaadviser
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env`:

```bash
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
WEBAPP_URL=https://your-webapp-url.com
```

### 4. Создание таблиц в Supabase

1. Откройте Supabase Dashboard
2. Перейдите в **SQL Editor**
3. Скопируйте содержимое `supabase_schema.sql`
4. Выполните запрос

### 5. Загрузка тестовых данных

```bash
python load_test_data_supabase.py
```

### 6. Запуск бота

```bash
python bot.py
```

## 🌐 Развертывание

### Локальный запуск

```bash
python bot.py
```

### Развертывание на Amvera Cloud

1. Создайте аккаунт на [amvera.ru](https://amvera.ru)
2. Подключите Git репозиторий
3. Настройте переменные окружения
4. Запустите деплой

### Переменные окружения для Amvera

```bash
BOT_TOKEN=your_telegram_bot_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
WEBAPP_URL=https://your-app.amvera.app
```

## 📈 Мониторинг и аналитика

### Supabase Dashboard

- **Table Editor** - просмотр и редактирование данных
- **SQL Editor** - выполнение запросов
- **Logs** - мониторинг запросов
- **Analytics** - статистика использования

### Полезные SQL запросы

```sql
-- Топ районов по средней цене
SELECT district, AVG(price_per_night) as avg_price
FROM short_term_rentals 
GROUP BY district 
ORDER BY avg_price DESC;

-- Динамика цен по месяцам
SELECT DATE_TRUNC('month', date) as month, AVG(price) as avg_price
FROM historical_prices 
WHERE price_type = 'short_term'
GROUP BY month 
ORDER BY month;

-- ROI анализ
SELECT * FROM calculate_roi('property_id', 1000000, 8000, 12000);
```

## 🔒 Безопасность

- Row Level Security (RLS) включен
- Публичный доступ только для чтения
- Ключи хранятся в переменных окружения
- Валидация входных данных
- Логирование ошибок

## 🚀 Производительность

### Оптимизация запросов

- Индексы на часто используемых полях
- Партиционирование по датам
- Кэширование результатов
- Ограничение выборки

### Масштабирование

- Supabase автоматически масштабируется
- До 500MB бесплатно
- Автоматические бэкапы
- Репликация данных

## 🐛 Отладка

### Логи Supabase

```bash
# В Dashboard → Logs
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

### Проверка подключения

```python
import requests

response = requests.get(
    f"{SUPABASE_URL}/rest/v1/short_term_rentals?select=count",
    headers={'apikey': SUPABASE_ANON_KEY}
)
print(response.json())
```

### Тестирование API

```bash
# Проверка эндпоинтов
curl "https://your-app.amvera.app/api/properties/short-term?district=Lara"
```

## 📝 Лицензия

MIT License

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи в Supabase Dashboard
2. Убедитесь в правильности переменных окружения
3. Проверьте создание таблиц
4. Посмотрите примеры в документации

## 🔄 Обновления

### Версия 2.0
- ✅ Интеграция с Supabase
- ✅ Тестовые данные для Анталии
- ✅ ROI калькулятор
- ✅ Рыночная статистика
- ✅ Многоязычная поддержка

### Планы развития
- 🔄 Интеграция с реальными API (Airbnb, Booking.com)
- 🔄 Машинное обучение для прогнозирования цен
- 🔄 Уведомления об изменениях цен
- 🔄 Расширенная аналитика 