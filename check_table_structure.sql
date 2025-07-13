-- Проверяем структуру таблицы user_reports
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'user_reports' 
ORDER BY ordinal_position;

-- Проверяем, есть ли таблица вообще
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'user_reports'; 