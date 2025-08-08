# Руководство по развертыванию Aaadviser на Amvera

## Обзор проекта

Это Telegram WebApp для анализа недвижимости в Турции. Проект включает:
- Flask-приложение с API для работы с базой данных Supabase
- HTML-страницы для WebApp интерфейса
- JavaScript утилиты для UX
- Конфигурация для развертывания на Amvera

## Структура проекта

```
Aaadviser/
├── app.py                 # Основное Flask-приложение
├── amvera.yaml           # Конфигурация для Amvera
├── requirements.txt       # Python зависимости
├── locales.py            # Локализация
├── ux-utils.js           # JavaScript утилиты
├── styles.css            # Основные стили
├── design-system.css     # Дизайн-система
├── fonts/                # Шрифты для PDF
├── webapp_*.html         # HTML страницы WebApp
└── src/                  # Дополнительные ресурсы
```

## Обновление файлов

### 1. Локальная разработка

```bash
# Клонирование репозитория
git clone <your-repo-url>
cd Aaadviser

# Установка зависимостей
pip install -r requirements.txt

# Создание .env файла (не коммитится в Git)
cp .env.example .env
# Отредактируйте .env с вашими ключами
```

### 2. Внесение изменений

#### Основные файлы для редактирования:

- **`app.py`** - основная логика приложения, API endpoints
- **`webapp_*.html`** - интерфейс WebApp
- **`ux-utils.js`** - JavaScript утилиты
- **`styles.css`** - стили
- **`locales.py`** - переводы

#### Добавление новых страниц:

1. Создайте HTML файл: `webapp_newpage.html`
2. Добавьте маршрут в `app.py`:
```python
@app.route('/webapp_newpage')
def webapp_newpage():
    with open('webapp_newpage.html', 'r', encoding='utf-8') as f:
        return f.read()
```

#### Добавление новых API endpoints:

```python
@app.route('/api/new_endpoint', methods=['POST'])
def api_new_endpoint():
    data = request.json or {}
    # Ваша логика
    return jsonify({'success': True})
```

### 3. Тестирование локально

```bash
# Запуск локального сервера
python app.py

# Приложение будет доступно на http://localhost:8080
```

## Развертывание на Amvera

### 1. Подготовка к деплою

Убедитесь, что все файлы готовы:
- `amvera.yaml` настроен правильно
- `requirements.txt` содержит все зависимости
- Все необходимые файлы в репозитории

### 2. Загрузка на GitHub

```bash
# Добавление изменений
git add .

# Коммит
git commit -m "Update: описание изменений"

# Пуш в репозиторий
git push origin main
```

### 3. Автоматический деплой

Amvera автоматически обнаружит изменения в GitHub и запустит новый деплой.

### 4. Проверка деплоя

После деплоя проверьте:
- Статус приложения в панели Amvera
- Логи на предмет ошибок
- Работоспособность API endpoints

## Конфигурация Amvera

### amvera.yaml

```yaml
name: telegram-webapp-bot
runtime: python
version: "3.11"

build:
  commands:
    - pip install -r requirements.txt

run:
  command: python app.py
  port: 8080

env:
  - name: TELEGRAM_BOT_TOKEN
    value: YOUR_BOT_TOKEN
  - name: SUPABASE_URL
    value: YOUR_SUPABASE_URL
  - name: SUPABASE_KEY
    value: YOUR_SUPABASE_KEY
```

### Переменные окружения

В `amvera.yaml` указаны основные переменные:
- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `SUPABASE_URL` - URL базы данных Supabase
- `SUPABASE_KEY` - ключ доступа к Supabase

## Мониторинг и логи

### Просмотр логов в Amvera

1. Откройте панель управления Amvera
2. Выберите ваше приложение
3. Перейдите в раздел "Логи"
4. Проверьте логи на предмет ошибок

### Основные эндпоинты для проверки

- `/health` - проверка работоспособности
- `/webapp` - главная страница WebApp
- `/api/user` - API пользователей

## Обновление зависимостей

### Добавление новых пакетов

1. Установите пакет локально:
```bash
pip install new-package
```

2. Обновите `requirements.txt`:
```bash
pip freeze > requirements.txt
```

3. Зафиксируйте изменения:
```bash
git add requirements.txt
git commit -m "Add new dependency: new-package"
git push
```

## Безопасность

### API ключи

⚠️ **ВАЖНО**: Не храните API ключи в коде или .env файлах!

Используйте:
- GitHub Secrets для CI/CD
- Amvera Environment Variables
- Внешние менеджеры секретов

### Обновление токенов

1. Обновите токены в панели Amvera
2. Перезапустите приложение
3. Проверьте работоспособность

## Устранение неполадок

### Частые проблемы

1. **Ошибка импорта модулей**
   - Проверьте `requirements.txt`
   - Убедитесь, что все зависимости указаны

2. **Ошибки подключения к базе данных**
   - Проверьте переменные окружения
   - Убедитесь в правильности URL и ключей Supabase

3. **Ошибки Telegram API**
   - Проверьте токен бота
   - Убедитесь в правильности WebApp URL

### Отладка

1. Проверьте логи в Amvera
2. Добавьте логирование в код:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

## Структура API

### Основные endpoints

- `/api/user` - работа с пользователями
- `/api/generate_report` - генерация отчетов
- `/api/full_report` - полные отчеты
- `/api/user_reports` - управление отчетами
- `/api/user_balance` - работа с балансом

### Формат запросов

Все API endpoints ожидают JSON:
```json
{
  "telegram_id": 123456789,
  "language": "ru",
  "data": "..."
}
```

## Производительность

### Оптимизация

1. **Кэширование** - используйте кэш для часто запрашиваемых данных
2. **Пагинация** - для больших списков
3. **Асинхронные запросы** - для внешних API

### Мониторинг

- Следите за временем ответа API
- Мониторьте использование памяти
- Проверяйте количество запросов

## Резервное копирование

### База данных

- Настройте автоматическое резервное копирование в Supabase
- Регулярно экспортируйте важные данные

### Код

- Используйте Git для версионирования
- Создавайте теги для релизов
- Ведите changelog

## Контакты и поддержка

При возникновении проблем:
1. Проверьте логи в Amvera
2. Изучите документацию Flask и Supabase
3. Обратитесь к команде разработки

---

**Последнее обновление**: Декабрь 2024
**Версия**: 1.0 