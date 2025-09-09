-- SQL скрипт для добавления новых полей в таблицу users
-- Для профиля пользователя с расширенными данными

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS full_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS position VARCHAR(255),
ADD COLUMN IF NOT EXISTS company_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS website_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS about_me TEXT,
ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS whatsapp_link VARCHAR(500),
ADD COLUMN IF NOT EXISTS telegram_link VARCHAR(500),
ADD COLUMN IF NOT EXISTS facebook_link VARCHAR(500),
ADD COLUMN IF NOT EXISTS instagram_link VARCHAR(500),
ADD COLUMN IF NOT EXISTS avatar_filename VARCHAR(255);

-- Создание индексов для часто используемых полей
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_full_name ON users(full_name);
CREATE INDEX IF NOT EXISTS idx_users_company_name ON users(company_name);

-- Комментарии к новым полям
COMMENT ON COLUMN users.full_name IS 'Полное имя пользователя (Фамилия и имя)';
COMMENT ON COLUMN users.position IS 'Должность пользователя';
COMMENT ON COLUMN users.company_name IS 'Название компании';
COMMENT ON COLUMN users.website_url IS 'Ссылка на сайт';
COMMENT ON COLUMN users.about_me IS 'Информация о пользователе';
COMMENT ON COLUMN users.phone IS 'Номер телефона';
COMMENT ON COLUMN users.email IS 'Электронная почта';
COMMENT ON COLUMN users.whatsapp_link IS 'Ссылка на WhatsApp';
COMMENT ON COLUMN users.telegram_link IS 'Ссылка на Telegram';
COMMENT ON COLUMN users.facebook_link IS 'Ссылка на Facebook';
COMMENT ON COLUMN users.instagram_link IS 'Ссылка на Instagram';
COMMENT ON COLUMN users.avatar_filename IS 'Имя файла аватара пользователя';
