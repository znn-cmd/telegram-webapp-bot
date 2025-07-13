-- Исправление политик RLS для таблицы users
-- Удаляем старые политики
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;
DROP POLICY IF EXISTS "Users can insert own data" ON users;

-- Создаем новые политики для публичного доступа (для демо)
-- В продакшене нужно будет настроить правильную аутентификацию

-- Политика для чтения (все пользователи могут читать)
CREATE POLICY "Enable read access for all users" ON users
    FOR SELECT USING (true);

-- Политика для вставки (все пользователи могут создавать записи)
CREATE POLICY "Enable insert access for all users" ON users
    FOR INSERT WITH CHECK (true);

-- Политика для обновления (все пользователи могут обновлять)
CREATE POLICY "Enable update access for all users" ON users
    FOR UPDATE USING (true);

-- Альтернативный вариант с ограничением по telegram_id (если нужно)
-- CREATE POLICY "Users can manage own data" ON users
--     FOR ALL USING (telegram_id = current_setting('app.telegram_id', true)::bigint); 