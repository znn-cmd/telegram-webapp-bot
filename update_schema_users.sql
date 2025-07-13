-- Создание таблицы пользователей с балансом
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    balance DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance);

-- Включение RLS для таблицы users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Политики RLS для users
DROP POLICY IF EXISTS "Users can view own data" ON users;
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (telegram_id = current_setting('request.jwt.claims', true)::json->>'sub'::bigint);

DROP POLICY IF EXISTS "Users can update own data" ON users;
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (telegram_id = current_setting('request.jwt.claims', true)::json->>'sub'::bigint);

DROP POLICY IF EXISTS "Users can insert own data" ON users;
CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (telegram_id = current_setting('request.jwt.claims', true)::json->>'sub'::bigint);

-- Добавление недостающих колонок в существующие таблицы
ALTER TABLE short_term_rentals 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

ALTER TABLE long_term_rentals 
ADD COLUMN IF NOT EXISTS deposit_currency VARCHAR(10),
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

ALTER TABLE property_sales 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER,
ADD COLUMN IF NOT EXISTS construction_status VARCHAR(50),
ADD COLUMN IF NOT EXISTS ownership_type VARCHAR(50);

-- Создание функции для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 