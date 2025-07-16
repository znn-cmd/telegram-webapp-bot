-- Создаем таблицу user_reports если её нет
CREATE TABLE IF NOT EXISTS user_reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    parameters JSONB,
    address VARCHAR(500),
    latitude NUMERIC,
    longitude NUMERIC,
    bedrooms INTEGER,
    price_range_min NUMERIC,
    price_range_max NUMERIC,
    full_report JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Добавляем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_created_at ON user_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_user_reports_report_type ON user_reports(report_type);

-- Добавляем комментарии к таблице
COMMENT ON TABLE user_reports IS 'Отчеты пользователей';
COMMENT ON COLUMN user_reports.user_id IS 'ID пользователя';
COMMENT ON COLUMN user_reports.report_type IS 'Тип отчета (market_analysis, full)';
COMMENT ON COLUMN user_reports.full_report IS 'Полный отчет в формате JSON'; 