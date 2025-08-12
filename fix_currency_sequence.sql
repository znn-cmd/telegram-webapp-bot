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

-- Проверяем текущую последовательность
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

-- Сбрасываем последовательность на максимальное значение + 1
-- Замените 'currency_id_seq' на реальное имя последовательности из предыдущего запроса
-- SELECT setval('currency_id_seq', (SELECT MAX(id) FROM currency) + 1);

-- Альтернативный способ: пересоздание последовательности
-- DROP SEQUENCE IF EXISTS currency_id_seq CASCADE;
-- CREATE SEQUENCE currency_id_seq START WITH 1 INCREMENT BY 1;
-- ALTER TABLE currency ALTER COLUMN id SET DEFAULT nextval('currency_id_seq');

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
