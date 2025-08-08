-- Проверка структуры таблицы users
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- Проверка существующих пользователей и их статусов
SELECT telegram_id, user_status, created_at
FROM users 
ORDER BY created_at DESC 
LIMIT 10;

-- Поиск пользователя по telegram_id (замените YOUR_TELEGRAM_ID на ваш ID)
-- SELECT telegram_id, user_status, name, tg_name
-- FROM users 
-- WHERE telegram_id = YOUR_TELEGRAM_ID;

-- Обновление статуса пользователя на администратора (замените YOUR_TELEGRAM_ID на ваш ID)
-- UPDATE users 
-- SET user_status = 'admin' 
-- WHERE telegram_id = YOUR_TELEGRAM_ID;

-- Проверка после обновления
-- SELECT telegram_id, user_status, name, tg_name
-- FROM users 
-- WHERE telegram_id = YOUR_TELEGRAM_ID; 