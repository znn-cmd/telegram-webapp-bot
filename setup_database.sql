-- Полная настройка базы данных для WebApp

-- 1. Создаем таблицу user_reports
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

-- 2. Создаем таблицу saved_objects
CREATE TABLE IF NOT EXISTS saved_objects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    object_data JSONB NOT NULL,
    saved_at TIMESTAMP DEFAULT NOW()
);

-- 3. Создаем таблицу client_contacts
CREATE TABLE IF NOT EXISTS client_contacts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    realtor_telegram_id INTEGER,
    client_name VARCHAR(255) NOT NULL,
    client_telegram VARCHAR(100),
    client_username VARCHAR(100),
    report_address VARCHAR(500),
    last_report_pdf_url TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Добавляем колонку full_report если её нет
ALTER TABLE user_reports 
ADD COLUMN IF NOT EXISTS full_report JSONB;

-- 5. Добавляем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_user_reports_user_id ON user_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_created_at ON user_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_user_reports_report_type ON user_reports(report_type);

CREATE INDEX IF NOT EXISTS idx_saved_objects_user_id ON saved_objects(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_objects_saved_at ON saved_objects(saved_at);

CREATE INDEX IF NOT EXISTS idx_client_contacts_user_id ON client_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_client_contacts_realtor_id ON client_contacts(realtor_telegram_id);
CREATE INDEX IF NOT EXISTS idx_client_contacts_created_at ON client_contacts(created_at);

-- 6. Добавляем комментарии
COMMENT ON TABLE user_reports IS 'Отчеты пользователей';
COMMENT ON COLUMN user_reports.full_report IS 'Полный отчет в формате JSON с детальным анализом';

COMMENT ON TABLE saved_objects IS 'Сохраненные объекты пользователей';
COMMENT ON COLUMN saved_objects.object_data IS 'Данные объекта в формате JSON';

COMMENT ON TABLE client_contacts IS 'Контакты клиентов риелторов';
COMMENT ON COLUMN client_contacts.client_telegram IS 'Telegram username клиента'; 