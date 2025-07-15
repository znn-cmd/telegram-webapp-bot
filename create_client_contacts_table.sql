-- Создаем таблицу client_contacts если её нет
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

-- Добавляем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_client_contacts_user_id ON client_contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_client_contacts_realtor_id ON client_contacts(realtor_telegram_id);
CREATE INDEX IF NOT EXISTS idx_client_contacts_created_at ON client_contacts(created_at);

-- Добавляем комментарии к таблице
COMMENT ON TABLE client_contacts IS 'Контакты клиентов риелторов';
COMMENT ON COLUMN client_contacts.user_id IS 'ID пользователя (риелтора)';
COMMENT ON COLUMN client_contacts.realtor_telegram_id IS 'Telegram ID риелтора';
COMMENT ON COLUMN client_contacts.client_name IS 'Имя клиента';
COMMENT ON COLUMN client_contacts.client_telegram IS 'Telegram username клиента';
COMMENT ON COLUMN client_contacts.client_username IS 'Username клиента'; 