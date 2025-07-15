-- Создаем таблицу saved_objects если её нет
CREATE TABLE IF NOT EXISTS saved_objects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    object_data JSONB NOT NULL,
    saved_at TIMESTAMP DEFAULT NOW()
);

-- Добавляем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_saved_objects_user_id ON saved_objects(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_objects_saved_at ON saved_objects(saved_at);

-- Добавляем комментарии к таблице
COMMENT ON TABLE saved_objects IS 'Сохраненные объекты пользователей';
COMMENT ON COLUMN saved_objects.user_id IS 'ID пользователя';
COMMENT ON COLUMN saved_objects.object_data IS 'Данные объекта в формате JSON'; 