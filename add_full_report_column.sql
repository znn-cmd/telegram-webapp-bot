-- Добавляем колонку full_report в таблицу user_reports
ALTER TABLE user_reports 
ADD COLUMN IF NOT EXISTS full_report JSONB;

-- Добавляем комментарий к колонке
COMMENT ON COLUMN user_reports.full_report IS 'Полный отчет в формате JSON с детальным анализом'; 