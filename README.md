# Telegram WebApp Bot с Supabase

Тестовый Telegram бот с WebApp интеграцией и базой данных Supabase.

## 🚀 Функциональность

- ✅ Приветствие новых пользователей
- ✅ Сохранение пользователей в Supabase
- ✅ Приветствие "С возвращением" для существующих пользователей
- ✅ WebApp интерфейс с информацией о пользователе
- ✅ Отправка данных из WebApp в бот

## 📋 Требования

- Python 3.11+
- Telegram Bot Token
- Supabase проект
- Amvera Cloud аккаунт

## 🛠️ Настройка

### 1. Создание Telegram бота

1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен

### 2. Настройка Supabase

1. Создайте проект на [supabase.com](https://supabase.com)
2. Перейдите в SQL Editor
3. Выполните SQL скрипт из файла `supabase_setup.sql`
4. Сохраните URL и anon key из настроек проекта

### 3. Настройка переменных окружения

В файле `amvera.yaml` замените следующие значения:

```yaml
env:
  - name: TELEGRAM_BOT_TOKEN
    value: "YOUR_BOT_TOKEN_HERE"  # Ваш токен бота
  - name: SUPABASE_URL
    value: "YOUR_SUPABASE_URL_HERE"  # URL вашего Supabase проекта
  - name: SUPABASE_KEY
    value: "YOUR_SUPABASE_ANON_KEY_HERE"  # Anon key из Supabase
```

### 4. Настройка WebApp URL

После деплоя на Amvera:

1. Получите URL вашего приложения (например: `https://your-app.amvera.io`)
2. В файле `app.py` замените `WEBAPP_URL`:
   ```python
   WEBAPP_URL = "https://your-app.amvera.io/webapp"
   ```

### 5. Настройка WebApp в Telegram

1. Напишите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/mybots`
3. Выберите вашего бота
4. Перейдите в "Bot Settings" → "Menu Button"
5. Установите URL: `https://your-app.amvera.io/webapp`

## 🚀 Деплой на Amvera

### Способ 1: Через Git

1. Создайте репозиторий на GitHub/GitLab
2. Загрузите файлы проекта
3. Подключите репозиторий к Amvera
4. Настройте переменные окружения в Amvera

### Способ 2: Через интерфейс Amvera

1. Создайте новый проект в Amvera
2. Загрузите файлы через интерфейс
3. Настройте переменные окружения

## 📁 Структура проекта

```
telegram-webapp-bot/
├── app.py              # Основной файл приложения
├── requirements.txt    # Python зависимости
├── amvera.yaml        # Конфигурация для Amvera
├── supabase_setup.sql # SQL для настройки базы данных
└── README.md          # Документация
```

## 🔧 API Endpoints

- `GET /webapp` - WebApp интерфейс
- `GET /health` - Проверка здоровья приложения

## 🧪 Тестирование

1. Запустите бота командой `/start`
2. Нажмите кнопку "🚀 Запустить WebApp"
3. Проверьте отображение информации о пользователе
4. Нажмите "📤 Отправить данные" для тестирования

## 📊 База данных

Таблица `users` содержит:
- `id` - автоинкрементный ID
- `telegram_id` - уникальный ID пользователя в Telegram
- `username` - username пользователя
- `first_name` - имя пользователя
- `last_name` - фамилия пользователя
- `created_at` - дата создания записи
- `updated_at` - дата последнего обновления

## 🔒 Безопасность

- Все переменные окружения хранятся в Amvera
- Supabase RLS включен для контроля доступа
- HTTPS обязателен для WebApp

## 🐛 Устранение неполадок

### Бот не отвечает
- Проверьте правильность токена
- Убедитесь, что бот запущен

### WebApp не открывается
- Проверьте правильность URL в BotFather
- Убедитесь, что приложение доступно по HTTPS

### Ошибки с базой данных
- Проверьте правильность Supabase URL и ключа
- Убедитесь, что таблица `users` создана

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Amvera
2. Убедитесь в правильности всех настроек
3. Проверьте доступность всех сервисов 