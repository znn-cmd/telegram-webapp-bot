-- Скрипт для обновления статистики БД после создания индексов
-- Выполните этот скрипт ОТДЕЛЬНО после создания индексов

-- Обновление статистики для таблицы users
VACUUM ANALYZE users;

-- Обновление статистики для таблицы locations (если таблица существует)
VACUUM ANALYZE locations;

-- Проверка обновленной статистики
SELECT 'Statistics updated successfully!' as result;

-- Дополнительная информация о статистике
SELECT 
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables 
WHERE tablename IN ('users', 'locations')
ORDER BY tablename;
