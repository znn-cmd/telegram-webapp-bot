# Aaadviser Telegram WebApp

Telegram WebApp для анализа недвижимости с админ панелью.

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Настройка API ключей

### Способ 1: Через админ панель (рекомендуется)

1. Запустите приложение
2. Откройте админ панель
3. Нажмите кнопку "🔑 API Ключи"
4. Добавьте необходимые ключи:
   - **ChatGPT API Key** - для переводов
   - **Telegram Bot Token** - для отправки сообщений

### Способ 2: Через базу данных

1. Создайте таблицу `api_keys` в Supabase:
   ```sql
   CREATE TABLE api_keys (
       id SERIAL PRIMARY KEY,
       key_name VARCHAR(50) NOT NULL UNIQUE,
       key_value TEXT NOT NULL,
       description TEXT,
       is_active BOOLEAN DEFAULT true,
       created_at TIMESTAMPTZ DEFAULT NOW(),
       updated_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

2. Добавьте ключи вручную:
   ```sql
   INSERT INTO api_keys (key_name, key_value, description) VALUES
   ('chatgpt_api_key', 'ваш_chatgpt_api_ключ', 'OpenAI ChatGPT API ключ для переводов'),
   ('telegram_bot_token', 'ваш_telegram_bot_token', 'Telegram Bot Token для отправки сообщений');
   ```

### Получение API ключей

**ChatGPT API Key:**
- Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
- Перейдите в раздел API Keys
- Создайте новый API ключ

**Telegram Bot Token:**
- Создайте бота через [@BotFather](https://t.me/botfather)
- Получите токен бота

## Запуск

```bash
python app.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

## Функции

### Основное приложение
- Анализ недвижимости
- Генерация отчетов
- Управление балансом

### Админ панель
- Установка баланса пользователей
- Статистика пользователей
- Многоязычные публикации с переводами

## Безопасность

⚠️ **ВАЖНО**: 
- API ключи теперь хранятся в базе данных, а не в коде
- Ключи защищены от попадания в Git репозиторий
- Используйте админ панель для управления ключами
- Регулярно обновляйте API ключи через админ панель

## Структура проекта

```
Aaadviser/
├── app.py                 # Основное приложение
├── api_functions.py       # API функции
├── webapp_*.html         # HTML страницы
├── .env                  # Переменные окружения (не в Git)
├── .env.example          # Пример переменных окружения
├── API_SETUP.md          # Инструкции по настройке API
└── requirements.txt      # Зависимости Python
```

## Подробная документация

См. файл `API_SETUP.md` для подробных инструкций по настройке API ключей. 