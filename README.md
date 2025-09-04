# Aaadvisor - Аналитика недвижимости

Веб-приложение для анализа рынка недвижимости с прогнозами цен и рентабельности.

## Основные функции

- 📊 Анализ рынка недвижимости по регионам
- 🏠 Оценка объектов недвижимости
- 💱 Конвертация валют (EUR, TRY, USD, RUB)
- 📈 Прогнозы цен и трендов
- 🌍 Поддержка 5 языков (RU, EN, DE, FR, TR)
- 📱 Telegram WebApp интерфейс

## Структура проекта

### Основные файлы
- `app.py` - главное Flask приложение
- `locales.py` - локализация (5 языков)
- `currency_functions.py` - функции для работы с валютой
- `price_trends_functions.py` - анализ трендов цен
- `static_locations.json` - база данных локаций

### Веб-интерфейс
- `webapp_*.html` - страницы веб-приложения
- `styles.css`, `design-system.css` - стили
- `ux-utils.js`, `economic_charts_component.js` - JavaScript утилиты
- `logo-*.png` - логотипы

### Конфигурация
- `requirements.txt` - Python зависимости
- `Dockerfile` - конфигурация Docker
- `.env.example` - пример переменных окружения

### Папки
- `reports/` - сохраненные отчеты
- `landing/` - лендинг страница
- `fonts/` - шрифты для PDF отчетов

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения (см. `.env.example`)

3. Запустите приложение:
```bash
python app.py
```

## Docker

```bash
docker build -t aaadvisor .
docker run -p 8080:8080 aaadvisor
```

## Технологии

- **Backend**: Flask, Python 3.11
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **APIs**: Google Maps, CurrencyLayer, OpenAI
- **Deployment**: Docker, Amvera
