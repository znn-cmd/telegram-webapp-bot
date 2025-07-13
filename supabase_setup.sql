-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индекса для быстрого поиска по telegram_id
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

-- Создание функции для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггера для автоматического обновления updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Включение Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Создание политики для чтения (в данном случае разрешаем всем)
CREATE POLICY "Allow read access" ON users FOR SELECT USING (true);

-- Создание политики для вставки (в данном случае разрешаем всем)
CREATE POLICY "Allow insert access" ON users FOR INSERT WITH CHECK (true);

-- Создание политики для обновления (в данном случае разрешаем всем)
CREATE POLICY "Allow update access" ON users FOR UPDATE USING (true); 