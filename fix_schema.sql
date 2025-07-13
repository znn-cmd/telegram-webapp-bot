-- Добавление недостающих колонок в таблицы

-- Добавляем колонки в property_sales
ALTER TABLE property_sales 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

-- Добавляем колонки в long_term_rentals
ALTER TABLE long_term_rentals 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

-- Добавляем колонки в short_term_rentals
ALTER TABLE short_term_rentals 
ADD COLUMN IF NOT EXISTS agent_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS agent_rating DECIMAL(3,2),
ADD COLUMN IF NOT EXISTS agent_review_count INTEGER;

-- Обновляем политики RLS для новых колонок
DROP POLICY IF EXISTS "Enable read access for all users" ON property_sales;
CREATE POLICY "Enable read access for all users" ON property_sales FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable insert access for all users" ON property_sales;
CREATE POLICY "Enable insert access for all users" ON property_sales FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Enable update access for all users" ON property_sales;
CREATE POLICY "Enable update access for all users" ON property_sales FOR UPDATE USING (true);

-- Аналогично для других таблиц
DROP POLICY IF EXISTS "Enable read access for all users" ON long_term_rentals;
CREATE POLICY "Enable read access for all users" ON long_term_rentals FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable insert access for all users" ON long_term_rentals;
CREATE POLICY "Enable insert access for all users" ON long_term_rentals FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Enable update access for all users" ON long_term_rentals;
CREATE POLICY "Enable update access for all users" ON long_term_rentals FOR UPDATE USING (true);

DROP POLICY IF EXISTS "Enable read access for all users" ON short_term_rentals;
CREATE POLICY "Enable read access for all users" ON short_term_rentals FOR SELECT USING (true);

DROP POLICY IF EXISTS "Enable insert access for all users" ON short_term_rentals;
CREATE POLICY "Enable insert access for all users" ON short_term_rentals FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Enable update access for all users" ON short_term_rentals;
CREATE POLICY "Enable update access for all users" ON short_term_rentals FOR UPDATE USING (true); 