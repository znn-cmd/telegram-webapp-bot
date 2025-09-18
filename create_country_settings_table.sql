-- SQL скрипт для создания таблицы настроек стран
-- Эта таблица будет хранить настройки доступности стран для обычных пользователей

CREATE TABLE IF NOT EXISTS country_settings (
    id SERIAL PRIMARY KEY,
    country_id INTEGER NOT NULL UNIQUE,
    country_name VARCHAR(255) NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_country_settings_country_id ON country_settings(country_id);
CREATE INDEX IF NOT EXISTS idx_country_settings_is_enabled ON country_settings(is_enabled);

-- Комментарии к полям
COMMENT ON TABLE country_settings IS 'Настройки доступности стран для пользователей';
COMMENT ON COLUMN country_settings.country_id IS 'ID страны из таблицы locations';
COMMENT ON COLUMN country_settings.country_name IS 'Название страны';
COMMENT ON COLUMN country_settings.is_enabled IS 'Доступна ли страна для обычных пользователей (true - доступна, false - недоступна)';
COMMENT ON COLUMN country_settings.created_at IS 'Дата создания записи';
COMMENT ON COLUMN country_settings.updated_at IS 'Дата последнего обновления записи';

-- Инициализация таблицы данными из locations
-- Вставляем все существующие страны как включенные по умолчанию
INSERT INTO country_settings (country_id, country_name, is_enabled)
SELECT DISTINCT country_id, country_name, true
FROM locations 
WHERE country_id IS NOT NULL AND country_name IS NOT NULL
ON CONFLICT (country_id) DO NOTHING;

-- Обновляем updated_at при изменении записи
CREATE OR REPLACE FUNCTION update_country_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_country_settings_updated_at
    BEFORE UPDATE ON country_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_country_settings_updated_at();
