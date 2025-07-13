# 🚀 Быстрый запуск Telegram WebApp Bot

## Шаг 1: Создание Telegram бота
1. Напишите [@BotFather](https://t.me/BotFather)
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. **Сохраните токен!**

## Шаг 2: Настройка Supabase
1. Зайдите на [supabase.com](https://supabase.com)
2. Создайте новый проект
3. В SQL Editor выполните код из `supabase_setup.sql`
4. **Сохраните URL и anon key!**

## Шаг 3: Настройка проекта
1. В `amvera.yaml` замените:
   - `YOUR_BOT_TOKEN_HERE` → ваш токен бота
   - `YOUR_SUPABASE_URL_HERE` → ваш Supabase URL
   - `YOUR_SUPABASE_ANON_KEY_HERE` → ваш anon key

## Шаг 4: Деплой на Amvera
1. Зайдите на [amvera.ru](https://amvera.ru)
2. Создайте новый проект
3. Загрузите файлы или подключите Git
4. Настройте переменные окружения

## Шаг 5: Настройка WebApp
1. Получите URL приложения (например: `https://your-app.amvera.io`)
2. В `app.py` замените `WEBAPP_URL` на ваш URL
3. В BotFather настройте Menu Button с URL: `https://your-app.amvera.io/webapp`

## 🧪 Тест
1. Отправьте `/start` боту
2. Нажмите "🚀 Запустить WebApp"
3. Проверьте работу!

## ⚠️ Важно
- Все URL должны быть HTTPS
- Проверьте все переменные окружения
- Убедитесь, что таблица `users` создана в Supabase 