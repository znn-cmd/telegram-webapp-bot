-- Добавляем недостающие колонки в таблицу user_reports

-- Добавляем колонку price если её нет
ALTER TABLE user_reports ADD COLUMN IF NOT EXISTS price NUMERIC;

-- Добавляем колонку full_report если её нет
ALTER TABLE user_reports ADD COLUMN IF NOT EXISTS full_report JSONB;

-- Добавляем колонку user_id если её нет
ALTER TABLE user_reports ADD COLUMN IF NOT EXISTS user_id INTEGER;

-- Показываем структуру таблицы после изменений
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user_reports' 
ORDER BY ordinal_position; 