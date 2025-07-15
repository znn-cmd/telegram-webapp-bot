# Настройка базы данных для API ключей

## Создание таблицы api_keys

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

-- Индексы для быстрого поиска
CREATE INDEX idx_api_keys_name ON api_keys(key_name);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
```

## Структура таблицы

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Уникальный идентификатор |
| key_name | VARCHAR(50) | Название ключа (например: 'chatgpt_api_key', 'telegram_bot_token') |
| key_value | TEXT | Значение ключа (зашифрованное) |
| description | TEXT | Описание назначения ключа |
| is_active | BOOLEAN | Активен ли ключ |
| created_at | TIMESTAMPTZ | Дата создания |
| updated_at | TIMESTAMPTZ | Дата обновления |

## Примеры записей

```sql
INSERT INTO api_keys (key_name, key_value, description) VALUES
('chatgpt_api_key', 'encrypted_key_here', 'OpenAI ChatGPT API ключ для переводов'),
('telegram_bot_token', 'encrypted_token_here', 'Telegram Bot Token для отправки сообщений');
``` 