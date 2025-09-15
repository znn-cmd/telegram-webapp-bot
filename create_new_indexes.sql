-- Упрощенный SQL скрипт для создания только новых индексов
-- Учитывает существующую структуру таблицы users

-- Индексы для таблицы locations (если таблица существует)
-- Ускоряют поиск по географическим данным

-- 1. Индекс для поиска стран
CREATE INDEX IF NOT EXISTS idx_locations_country_id 
ON locations(country_id);

-- 2. Индекс для поиска городов по стране
CREATE INDEX IF NOT EXISTS idx_locations_country_city 
ON locations(country_id, city_id);

-- 3. Индекс для поиска областей по городу
CREATE INDEX IF NOT EXISTS idx_locations_city_county 
ON locations(city_id, county_id);

-- 4. Индекс для поиска районов по области
CREATE INDEX IF NOT EXISTS idx_locations_county_district 
ON locations(county_id, district_id);

-- 5. Составной индекс для полной иерархии локаций
CREATE INDEX IF NOT EXISTS idx_locations_hierarchy 
ON locations(country_id, city_id, county_id, district_id);

-- 6. Индексы для поиска по названиям (для автодополнения)
CREATE INDEX IF NOT EXISTS idx_locations_country_name 
ON locations(country_name);

CREATE INDEX IF NOT EXISTS idx_locations_city_name 
ON locations(city_name);

CREATE INDEX IF NOT EXISTS idx_locations_county_name 
ON locations(county_name);

CREATE INDEX IF NOT EXISTS idx_locations_district_name 
ON locations(district_name);

-- Индексы для таблицы users
-- ПРИМЕЧАНИЕ: idx_users_telegram_id уже существует, не создаем

-- 7. Индекс для поиска по user_status (админы)
CREATE INDEX IF NOT EXISTS idx_users_status 
ON users(user_status);

-- 8. Составной индекс для проверки админов
CREATE INDEX IF NOT EXISTS idx_users_telegram_status 
ON users(telegram_id, user_status);

-- 9. Индекс для поиска по периоду подписки
CREATE INDEX IF NOT EXISTS idx_users_period_end 
ON users(period_end);

-- 10. Индекс для поиска по языку пользователя
CREATE INDEX IF NOT EXISTS idx_users_language 
ON users(language);

-- 11. Индекс для поиска по балансу (для админов)
CREATE INDEX IF NOT EXISTS idx_users_balance 
ON users(balance);

-- 12. Индекс для поиска по дате регистрации
CREATE INDEX IF NOT EXISTS idx_users_registration_date 
ON users(registration_date);

-- Проверка существующих индексов
SELECT 'Existing indexes on users table:' as info;
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

SELECT 'Existing indexes on locations table:' as info;
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'locations';

-- Проверка успешного создания индексов
SELECT 'Indexes created successfully!' as result;

-- ПРИМЕЧАНИЕ: Для обновления статистики выполните отдельно:
-- VACUUM ANALYZE users;
-- VACUUM ANALYZE locations;
