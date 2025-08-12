-- Исправление автоинкремента для таблицы currency
-- Выполните этот скрипт в Supabase SQL Editor

-- Проверяем текущий статус последовательности
SELECT 
    schemaname,
    tablename,
    columnname,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'currency' AND column_name = 'id';

-- Проверяем текущую последовательность (для bigint identity)
SELECT 
    sequence_name,
    data_type,
    start_value,
    minimum_value,
    maximum_value,
    increment,
    last_value
FROM information_schema.sequences 
WHERE sequence_name LIKE '%currency%';

-- Проверяем максимальное значение ID в таблице
SELECT MAX(id) as max_id FROM currency;

-- Проверяем текущее значение последовательности
-- Для bigint identity используем специальный запрос
SELECT pg_get_serial_sequence('currency', 'id') as sequence_name;

-- Сбрасываем последовательность на максимальное значение + 1
-- Замените 'currency_id_seq' на реальное имя последовательности из предыдущего запроса
SELECT setval(pg_get_serial_sequence('currency', 'id'), (SELECT MAX(id) FROM currency) + 1);

-- Проверяем результат
SELECT 
    schemaname,
    tablename,
    columnname,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'currency' AND column_name = 'id';

-- Проверяем, что последовательность исправлена
SELECT 
    sequence_name,
    last_value
FROM information_schema.sequences 
WHERE sequence_name LIKE '%currency%';
