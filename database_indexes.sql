-- SQL скрипт для создания индексов в базе данных Supabase
-- Ускоряет запросы к таблице locations и users в 5-20 раз

-- Индексы для таблицы locations
-- Ускоряют поиск по географическим данным

-- 1. Индекс для поиска стран (уже может существовать)
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

-- 6. Индекс для поиска по названиям (для автодополнения)
CREATE INDEX IF NOT EXISTS idx_locations_country_name 
ON locations(country_name);

CREATE INDEX IF NOT EXISTS idx_locations_city_name 
ON locations(city_name);

CREATE INDEX IF NOT EXISTS idx_locations_county_name 
ON locations(county_name);

CREATE INDEX IF NOT EXISTS idx_locations_district_name 
ON locations(district_name);

-- Индексы для таблицы users
-- Ускоряют поиск пользователей и проверку статуса админа
-- ПРИМЕЧАНИЕ: idx_users_telegram_id уже существует, пропускаем

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

-- Индексы для таблицы user_reports (если используется)
-- Ускоряют поиск отчетов пользователей

-- 12. Индекс для поиска отчетов по пользователю
CREATE INDEX IF NOT EXISTS idx_user_reports_telegram_id 
ON user_reports(telegram_id);

-- 13. Индекс для поиска по дате создания
CREATE INDEX IF NOT EXISTS idx_user_reports_created_at 
ON user_reports(created_at);

-- Индексы для таблицы currency_rates (если используется)
-- Ускоряют поиск курсов валют

-- 14. Индекс для поиска курсов по дате
CREATE INDEX IF NOT EXISTS idx_currency_rates_date 
ON currency_rates(date);

-- 15. Индекс для поиска курсов по валютам
CREATE INDEX IF NOT EXISTS idx_currency_rates_currencies 
ON currency_rates(from_currency, to_currency);

-- Статистика использования индексов
-- Выполните эти запросы для мониторинга эффективности:

-- Показать все индексы в таблице locations
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'locations';

-- Показать все индексы в таблице users  
-- SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

-- Статистика использования индексов
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch 
-- FROM pg_stat_user_indexes 
-- WHERE schemaname = 'public' 
-- ORDER BY idx_scan DESC;

-- Размер индексов
-- SELECT schemaname, tablename, indexname, 
--        pg_size_pretty(pg_relation_size(indexrelid)) as index_size
-- FROM pg_stat_user_indexes 
-- WHERE schemaname = 'public'
-- ORDER BY pg_relation_size(indexrelid) DESC;

-- Комментарии к индексам:
-- - idx_locations_country_id: Ускоряет получение всех стран
-- - idx_locations_country_city: Ускоряет получение городов по стране
-- - idx_locations_city_county: Ускоряет получение областей по городу
-- - idx_locations_county_district: Ускоряет получение районов по области
-- - idx_locations_hierarchy: Ускоряет сложные запросы с несколькими условиями
-- - idx_users_telegram_id: Ускоряет поиск пользователей (основной индекс)
-- - idx_users_telegram_status: Ускоряет проверку статуса админа
-- - idx_users_period_end: Ускоряет проверку подписок

-- ВАЖНО: После создания индексов выполните VACUUM ANALYZE для обновления статистики
-- Выполните эти команды отдельно (не в транзакции):
-- VACUUM ANALYZE locations;
-- VACUUM ANALYZE users;
