-- Исправление RLS политики для таблицы currency
-- Выполните этот скрипт в Supabase SQL Editor

-- Вариант 1: Отключить RLS для таблицы currency (если не нужна безопасность)
ALTER TABLE currency DISABLE ROW LEVEL SECURITY;

-- Вариант 2: Создать политику, разрешающую вставку (если RLS нужен)
-- Сначала включаем RLS
-- ALTER TABLE currency ENABLE ROW LEVEL SECURITY;

-- Создаем политику для вставки (разрешаем всем аутентифицированным пользователям)
-- CREATE POLICY "Enable insert for authenticated users" ON currency
--     FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Создаем политику для чтения (разрешаем всем)
-- CREATE POLICY "Enable read access for all users" ON currency
--     FOR SELECT USING (true);

-- Проверяем текущий статус RLS
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename = 'currency';

-- Проверяем существующие политики
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies 
WHERE tablename = 'currency';
